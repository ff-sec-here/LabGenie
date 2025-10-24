#!/usr/bin/env python3
"""
LabGenie - Vulnerability Lab Generator
Transforms security write-ups into production-ready vulnerable labs
"""

import os
import sys
import json
import re
import time
import asyncio
import argparse
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from rich.live import Live
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
)

from agents.WriteUpToMarkdown.agent import WriteUpToMarkdownAgent
from agents.WriteupParser.agent import WriteupParserAgent
from agents.LabCorePlanner.agent import LabCorePlannerAgent
from agents.LabBuilder.agent import LabBuilderAgent

# Import ULTRA animations
from helpers.genie_animation_ultra import (
    create_epic_startup_banner,
    create_step_animation,
    create_success_banner
)

console = Console()


class FileLogger:
    """Logs agent responses to files for debugging"""

    def __init__(self, run_id: str, log_dir: Path = None):
        self.run_id = run_id
        self.log_dir = (log_dir or Path("logs")) / run_id
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create run info file
        info_file = self.log_dir / "run_info.json"
        with open(info_file, "w") as f:
            json.dump({
                "run_id": run_id,
                "start_time": datetime.now().isoformat(),
                "status": "running"
            }, f, indent=2)

    def log_agent_response(
            self,
            agent_name: str,
            response: Any,
            input_data: Any = None):
        """Log agent response to file"""
        log_file = self.log_dir / f"{agent_name}.log"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "input_summary": self._summarize(input_data),
            "response": response,
            "response_type": str(type(response)),
        }

        if isinstance(response, dict):
            log_entry["response_keys"] = list(response.keys())
            log_entry["has_error"] = response.get("error", False)
            log_entry["status"] = response.get("status", "unknown")

            if "files" in response:
                log_entry["files_count"] = len(response["files"])
                log_entry["files_list"] = [
                    f.get("path", "no-path") for f in response.get("files", [])[:10]]

        with open(log_file, "a") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(json.dumps(log_entry, indent=2, default=str))
            f.write("\n")

    def _summarize(self, data: Any) -> str:
        """Create a brief summary of input data"""
        if data is None:
            return "None"
        if isinstance(data, str):
            return f"String({len(data)} chars)"
        if isinstance(data, dict):
            return f"Dict(keys={list(data.keys())[:5]})"
        if isinstance(data, list):
            return f"List({len(data)} items)"
        return str(type(data))

    def finalize(self, status: str):
        """Mark run as complete"""
        info_file = self.log_dir / "run_info.json"
        with open(info_file, "r") as f:
            info = json.load(f)

        info["status"] = status
        info["end_time"] = datetime.now().isoformat()

        with open(info_file, "w") as f:
            json.dump(info, f, indent=2)


class DebugLogger:
    """Real-time debug logger for agent actions"""

    def __init__(self):
        self.actions: List[Dict[str, Any]] = []
        self.start_time = None
        self.current_step = None
        self.step_start_time = None

    def start_workflow(self):
        """Start workflow timer"""
        self.start_time = time.time()
        self.actions = []

    def start_step(self, step_name: str, description: str):
        """Log step start"""
        self.current_step = step_name
        self.step_start_time = time.time()
        self.actions.append({
            "type": "step_start",
            "step": step_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._get_elapsed()
        })

    def log_action(self, action: str, details: str = "", status: str = "info"):
        """Log an action with status"""
        self.actions.append({
            "type": "action",
            "step": self.current_step,
            "action": action,
            "details": details,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._get_elapsed()
        })

    def end_step(self, success: bool, result_summary: str = ""):
        """Log step completion"""
        duration = time.time() - self.step_start_time if self.step_start_time else 0
        self.actions.append({
            "type": "step_end",
            "step": self.current_step,
            "success": success,
            "duration": duration,
            "result_summary": result_summary,
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._get_elapsed()
        })

    def _get_elapsed(self) -> float:
        """Get elapsed time since workflow start"""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0

    def get_total_elapsed(self) -> str:
        """Get formatted total elapsed time"""
        if not self.start_time:
            return "00:00:00"
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def format_action_log(self) -> Table:
        """Format actions as a rich table"""
        table = Table(
            title="🔍 Debug Log - Agent Actions",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan")
        table.add_column("Time", style="dim", width=8)
        table.add_column("Step", style="cyan", width=20)
        table.add_column("Action", style="white", width=30)
        table.add_column("Status", width=10)
        table.add_column("Duration", style="yellow", width=10)

        for action in self.actions[-20:]:  # Show last 20 actions
            elapsed = action.get("elapsed", 0)
            time_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"

            if action["type"] == "step_start":
                step = action["step"]
                desc = action["description"][:30]
                table.add_row(time_str, step, desc, "▶️ START", "-")

            elif action["type"] == "action":
                step = action.get("step", "")
                act = action["action"]
                status = action["status"]
                status_icon = self._get_status_icon(status)
                table.add_row(time_str, step, act, status_icon, "-")

            elif action["type"] == "step_end":
                step = action["step"]
                success = action["success"]
                duration = action.get("duration", 0)
                status_icon = "✅ DONE" if success else "❌ FAIL"
                duration_str = f"{duration:.2f}s"
                table.add_row(
                    time_str,
                    step,
                    "Completed",
                    status_icon,
                    duration_str,
                    style="bold green" if success else "bold red")

        return table

    def _get_status_icon(self, status: str) -> str:
        """Get status icon for action"""
        icons = {
            "info": "ℹ️ INFO",
            "success": "✅ OK",
            "warning": "⚠️ WARN",
            "error": "❌ ERR",
            "processing": "⚙️ PROC"
        }
        return icons.get(status, "ℹ️ INFO")


def auto_detect_provider() -> Optional[str]:
    """Auto-detect which provider is configured.

    Priority:
    1. Vertex AI (if GOOGLE_CLOUD_PROJECT is set)
    2. Gemini API (if GOOGLE_API_KEY is set)
    3. None (if neither is configured)
    """
    # Check Vertex first (enterprise priority)
    if os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"):
        return "vertex"

    # Check Gemini
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini"

    return None


def check_provider_config(provider: str, api_key: Optional[str] = None):
    """Check configuration for selected provider.

    Returns (ok, error_msg).
    """
    provider = provider.lower()
    if provider == "vertex":
        project_id = os.getenv(
            "GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
        if not project_id:
            return False, (
                "GOOGLE_CLOUD_PROJECT environment variable not set.\n"
                "Vertex AI requires a GCP project ID to function."
            )
        return True, None
    # gemini
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        return False, (
            "GOOGLE_API_KEY environment variable not set.\n"
            "Gemini API requires an API key."
        )
    return True, None


class LabGenieWorkflow:
    """Main workflow orchestrator for LabGenie CLI"""

    def __init__(
            self,
            output_dir: Optional[Path] = None,
            log_dir: Optional[Path] = None,
            debug_mode: bool = False,
            verbose: bool = True,
            provider: Optional[str] = None,
            api_key: Optional[str] = None,
            config_path: Optional[Path] = None):
        """Initialize the workflow with Vertex AI configuration.

        Args:
            output_dir: Custom output directory for generated labs
            log_dir: Custom logs directory
            debug_mode: Enable detailed debug logging
            verbose: Enable verbose console output
            provider: AI provider to use
            api_key: API key for Gemini API
            config_path: Path to config.json file (default: ./config.json)
        """
        self.verbose = verbose

        # Load configuration
        self.config = self._load_config(config_path or Path("config.json"))

        # Smart provider detection: explicit > env > auto-detect
        if provider:
            self.provider = provider.lower()
        elif os.getenv("LABGENIE_PROVIDER"):
            self.provider = os.getenv("LABGENIE_PROVIDER").lower()
        else:
            # Auto-detect based on what's configured
            detected = auto_detect_provider()
            if detected:
                self.provider = detected
            else:
                # No provider configured
                console.print("[red]❌ Error: No AI provider configured[/red]")
                console.print(
                    "\n[yellow]Please configure one of the following:[/yellow]\n")
                console.print(
                    "[bold]Option 1: Gemini API (Recommended)[/bold]")
                console.print("  export GOOGLE_API_KEY='your-api-key'")
                console.print(
                    "  Get key: https://makersuite.google.com/app/apikey\n")
                console.print("[bold]Option 2: Vertex AI (Enterprise)[/bold]")
                console.print(
                    "  export GOOGLE_CLOUD_PROJECT='your-project-id'")
                console.print("  gcloud auth application-default login\n")
                sys.exit(1)

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        ok, error_msg = check_provider_config(self.provider, self.api_key)
        if not ok:
            console.print(
                f"[red]❌ Error: {
                    self.provider.title()} provider not configured[/red]")
            console.print(f"[yellow]{error_msg}[/yellow]")
            sys.exit(1)

        # Initialize agents silently with models from config
        models = self.config.get("models", {})

        agents_list = [
            ("WriteUpToMarkdown", WriteUpToMarkdownAgent, models.get("WriteUpToMarkdown")),
            ("WriteupParser", WriteupParserAgent, models.get("WriteupParser")),
            ("LabCorePlanner", LabCorePlannerAgent, models.get("LabCorePlanner")),
            ("LabBuilder", LabBuilderAgent, models.get("LabBuilder"))
        ]

        for idx, (_, AgentClass, model) in enumerate(agents_list):
            agent_instance = AgentClass(
                api_key=self.api_key,
                provider=self.provider,
                model=model)

            if idx == 0:
                self.writeup_to_markdown = agent_instance
            elif idx == 1:
                self.writeup_parser = agent_instance
            elif idx == 2:
                self.lab_core_planner = agent_instance
            elif idx == 3:
                self.lab_builder = agent_instance

        self.output_base = output_dir or Path("./output")
        self.output_base.mkdir(exist_ok=True)
        self.output_dir = None
        self._custom_output = output_dir is not None

        self.debug_mode = debug_mode
        # Always initialize logger for duration tracking
        self.logger = DebugLogger()

        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + \
            "_" + str(uuid.uuid4())[:8]
        self.file_logger = FileLogger(self.run_id, log_dir)

        # Store info for later display
        self.provider_info = {
            "provider": self.provider,
            "run_id": self.run_id,
            "log_path": str(log_dir or Path("logs"))
        }
        if self.provider == "vertex":
            self.provider_info["project"] = os.getenv(
                "GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
            self.provider_info["location"] = os.getenv(
                "GOOGLE_CLOUD_LOCATION", "us-central1")

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from config.json file.

        Args:
            config_path: Path to config.json file

        Returns:
            Configuration dictionary with model settings
        """
        default_config = {
            "models": {
                "WriteUpToMarkdown": "gemini-2.5-flash",
                "WriteupParser": "models/gemini-2.5-pro",
                "LabCorePlanner": "models/gemini-2.5-pro",
                "LabBuilder": "models/gemini-2.5-pro"
            }
        }

        if not config_path.exists():
            if self.verbose:
                console.print(
                    f"[yellow]⚠️  Config file not found at {config_path}, "
                    f"using default models[/yellow]")
            return default_config

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing values
                if "models" not in config:
                    config["models"] = default_config["models"]
                else:
                    # Fill in any missing model configurations
                    for agent, model in default_config["models"].items():
                        if agent not in config["models"]:
                            config["models"][agent] = model
                return config
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error parsing config.json: {e}[/red]")
            console.print(f"[yellow]Using default models[/yellow]")
            return default_config
        except Exception as e:
            console.print(f"[red]❌ Error loading config.json: {e}[/red]")
            console.print(f"[yellow]Using default models[/yellow]")
            return default_config

    def display_banner(self):
        """Display the EPIC LabGenie welcome banner with animation"""
        # Epic banner (left-aligned, compact)
        console.print()
        console.print(create_epic_startup_banner())

        # Show provider info compactly if verbose
        if self.verbose:
            provider_name = "Vertex AI" if self.provider == "vertex" else "Gemini API"
            # Show custom output path if provided, otherwise show default pattern
            if self._custom_output:
                output_display = str(self.output_base)
            else:
                output_display = f"/output/{self.run_id}"
            
            info_text = (
                f"[dim]Provider: {provider_name} | "
                f"Run: {self.run_id} | "
                f"Output: {output_display}[/dim]"
            )
            console.print(info_text)
        console.print()

    async def run_step_with_genie(
            self,
            step_name: str,
            coro,
            description: str,
            agent_input: Any = None):
        """Run a workflow step with ANIMATED loading screen and timer"""
        # Always log step for timer tracking
        if self.logger:
            self.logger.start_step(step_name, description)

        result = None
        error = None
        step_start = time.time()

        async def run_task():
            nonlocal result, error
            try:
                if self.debug_mode:
                    self.logger.log_action(
                        f"Calling agent: {step_name}",
                        "Sending request to LLM",
                        "processing")

                result = await coro

                if self.debug_mode:
                    if isinstance(result, dict):
                        if result.get("error"):
                            self.logger.log_action(
                                "Agent returned error", result.get(
                                    "reason", ""), "error")
                        else:
                            result_keys = list(result.keys())[:5]
                            self.logger.log_action(
                                "Agent response received", f"Keys: {result_keys}", "success")
                    else:
                        self.logger.log_action(
                            "Agent response received", f"Type: {
                                type(result)}", "success")
            except Exception as e:
                error = e
                if self.debug_mode:
                    self.logger.log_action(
                        "Exception occurred", str(e), "error")

        def make_display():
            elapsed = time.time() - step_start
            total_elapsed = self.logger.get_total_elapsed() if self.logger else "00:00:00"

            # Format elapsed time consistently in HH:MM:SS
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Simulate progress (based on time, capped at 90%)
            progress = min(90, (elapsed / 30) * 100)  # Assume 30s average

            # Use ultra animation function with clear time labels
            panel = create_step_animation(
                step_name=step_name,
                description=description,
                progress=progress,
                elapsed_time=f"Step: {elapsed_str} | Workflow: {total_elapsed}"
            )
            return panel

        task = asyncio.create_task(run_task())

        with Live(make_display(), refresh_per_second=4, console=console, transient=True) as live:
            while not task.done():
                live.update(make_display())
                await asyncio.sleep(0.33)

        step_duration = time.time() - step_start

        if error:
            if self.logger:
                self.logger.end_step(False, str(error))
            console.print(
                f"[bold red]❌ {step_name} failed: {error}[/bold red]")
            if self.verbose:
                console.print(f"[dim]Duration: {step_duration:.2f}s[/dim]\n")
            raise error  # type: ignore

        # Log completion
        result_summary = "Success"
        if result and isinstance(result, dict):
            if "files" in result:  # type: ignore
                result_summary = f"Generated {len(result['files'])} files"  # type: ignore
            elif "markdown" in result:  # type: ignore
                markdown_len = len(result['markdown'])  # type: ignore
                result_summary = f"Markdown length: {markdown_len} chars"
        if self.logger:
            self.logger.end_step(True, result_summary)

        agent_name = step_name.replace(" ", "_")
        self.file_logger.log_agent_response(agent_name, result, agent_input)

        # Success message
        success_msg = Panel(
            f"[bold green]✅ {step_name} Complete![/bold green]\n"
            f"[dim]⏱️  {step_duration:.1f}s[/dim]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
            width=60
            
        )
        console.print(success_msg)
        return result

    async def step_1_markdown_conversion(self, url: str) -> Dict[str, Any]:
        """Step 1: Convert write-up URL to markdown"""
        return await self.run_step_with_genie(
            "WriteUp to Markdown Conversion",
            self.writeup_to_markdown.convert(url),
            "Fetching and converting the vulnerability write-up to structured markdown...",
            agent_input=url
        )

    async def step_2_vulnerability_parsing(
            self, markdown_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Parse vulnerability information"""
        return await self.run_step_with_genie(
            "Vulnerability Information Parsing",
            self.writeup_parser.parse(markdown_data),
            "Extracting reproduction steps, root cause analysis, and technical details...",
            agent_input=markdown_data
        )

    async def step_3_lab_planning(
            self, vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Generate lab core plan"""
        return await self.run_step_with_genie(
            "Lab Core Planning",
            self.lab_core_planner.plan(vulnerability_data),
            "Creating deterministic lab plan with UI flows and component architecture...",
            agent_input=vulnerability_data
        )

    async def step_4_lab_building(
            self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Build complete lab artifacts"""
        return await self.run_step_with_genie(
            "Lab Building",
            self.lab_builder.build(plan_data),
            "Generating complete, runnable lab repository with code, configs, and tests...",
            agent_input=plan_data
        )

    def _extract_lab_name(
            self, lab_data: Dict[str, Any], plan_data: Dict[str, Any]) -> str:
        """Extract lab name from generated data"""
        # Try to get lab name from various sources
        lab_name = None

        # Check lab_data for lab_name field
        if isinstance(lab_data, dict):
            lab_name = lab_data.get("lab_name") or lab_data.get("name")

        # Check plan_data for plan_metadata.lab_name
        if not lab_name and isinstance(plan_data, dict):
            plan_meta = plan_data.get("plan_metadata", {})
            if isinstance(plan_meta, dict):
                lab_name = plan_meta.get("lab_name") or plan_meta.get("name")

        # Generate default name with timestamp if not found
        if not lab_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lab_name = f"vulnerability_lab_{timestamp}"

        # Sanitize lab name (remove invalid characters)
        lab_name = re.sub(r'[^\w\-_]', '_', lab_name)

        return lab_name

    def save_artifacts(
            self, lab_data: Dict[str, Any], plan_data: Dict[str, Any]) -> Path:
        """Save lab artifacts to output/{labname} directory"""
        header = Panel(
            "[bold white]💾 Saving Lab Artifacts[/bold white]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
            width=60
            
        )
        console.print(header)

        files_list = lab_data.get("files", [])

        if not files_list:
            console.print(
                "[yellow]⚠️  No files to save - LabBuilder returned empty files array[/yellow]")
            console.print(f"[yellow]Check logs for details[/yellow]")
            lab_name = self._extract_lab_name(lab_data, plan_data)
            self.output_dir = self.output_base / lab_name
            self.output_dir.mkdir(parents=True, exist_ok=True)

            debug_file = self.output_dir / "debug_lab_data.json"
            with open(debug_file, "w") as f:
                json.dump(lab_data, f, indent=2)

            return self.output_dir

        lab_name = self._extract_lab_name(lab_data, plan_data)
        self.output_dir = self.output_base / lab_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            console.print(f"[dim]Lab name: {lab_name}[/dim]")
            console.print(
                f"[dim]Output directory: {
                    self.output_dir.absolute()}[/dim]\n")

        # Calculate total tasks (files + Docker configs)
        total_tasks = len(files_list)
        docker_config = lab_data.get("docker_config", {})
        if docker_config.get("dockerfile", {}).get("content"):
            total_tasks += 1
        if docker_config.get("docker_compose", {}).get("content"):
            total_tasks += 1

        progress_panel = Panel(
            "[bold cyan]⏳ Writing files to disk...[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            width=60
        )
        console.print(progress_panel)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=30),
            TaskProgressColumn(),
            console=console,
            expand=False
        ) as progress:

            task = progress.add_task(
                "[cyan]Writing files...", total=total_tasks)

            # Write application files
            for file_info in files_list:
                file_path = self.output_dir / file_info["path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_info.get("content", ""))

                progress.update(task, advance=1)

            # Write Docker configuration files
            if docker_config:
                # Write Dockerfile (always required)
                dockerfile = docker_config.get("dockerfile", {})
                if dockerfile.get("content"):
                    dockerfile_path = self.output_dir / "Dockerfile"
                    with open(dockerfile_path, "w", encoding="utf-8") as f:
                        f.write(dockerfile["content"])
                    progress.update(task, advance=1)

                docker_compose = docker_config.get("docker_compose", {})
                if docker_compose.get("content") and docker_compose["content"] not in [
                        None, "null", ""]:
                    compose_path = self.output_dir / "docker-compose.yml"
                    with open(compose_path, "w", encoding="utf-8") as f:
                        f.write(docker_compose["content"])
                    progress.update(task, advance=1)

        # Save complete JSON output
        output_json = self.output_dir / "lab_manifest.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(lab_data, f, indent=2)

        success_msg = Panel(
            f"[bold green]✅ All artifacts saved![/bold green]\n"
            f"[dim]{self.output_dir.absolute()}[/dim]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
            width=60
            
        )
        console.print(success_msg)
        return self.output_dir

    def display_summary(self, lab_data: Dict[str, Any], output_path: Path):
        """Display EPIC workflow completion summary"""

        # Lab details
        lab_name = lab_data.get("lab_name", "vulnerability-lab")
        file_count = len(lab_data.get("files", []))

        # Get total time
        total_time = self.logger.get_total_elapsed() if self.logger else "00:00:00"

        # Epic success banner with total time
        console.print()
        console.print(create_success_banner(lab_name, file_count, total_time))

        # Compact summary table
        table = Table(
            show_header=False,
            box=box.ROUNDED,
            padding=(0, 1),
            border_style="cyan"
        )
        table.add_column("Item", style="bold cyan", justify="right", width=20)
        table.add_column("Value", style="white", width=36)

        table.add_row("📦 Lab", lab_name[:30])
        table.add_row("📄 Files", f"[bold green]{file_count}[/bold green]")
        table.add_row(
            "⏱ Duration",
            f"[bold magenta]{total_time}[/bold magenta]")
        table.add_row("📁 Output", output_path.name)

        # Docker configuration info (compact)
        docker_config = lab_data.get("docker_config", {})
        if docker_config.get("dockerfile", {}).get("content"):
            table.add_row("🐳 Docker", "✅ Dockerfile")

        if docker_config.get("docker_compose", {}).get("content"):
            if docker_config["docker_compose"]["content"] not in [
                    None, "null", ""]:
                table.add_row("🐳 Compose", "✅ docker-compose.yml")

        console.print(table)

        # Next steps - compact version
        has_compose = docker_config.get("docker_compose", {}).get(
            "content") not in [None, "null", ""]

        steps = "[bold white]Next Steps:[/bold white]\n\n"
        steps += f"1. [cyan]cd {output_path.name}[/cyan]\n"
        steps += "2. Review lab_manifest.json\n"

        if has_compose:
            steps += "3. [cyan]docker-compose up --build[/cyan]\n"
        elif docker_config.get("dockerfile", {}).get("content"):
            steps += "3. [cyan]docker build -t lab .[/cyan]\n"
            steps += "   [cyan]docker run -p 8080:8080 lab[/cyan]\n"

        steps += "\n[yellow]⚠️  Target localhost only![/yellow]"

        next_steps = Panel(
            steps,
            title="[bold magenta]🚀 Get Started[/bold magenta]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
            width=60
            
        )
        console.print(next_steps)

    async def run_interactive(self):
        """Run the interactive CLI workflow"""
        self.display_banner()

        if self.debug_mode:
            console.print(Panel(
                "[bold green]🔍 Debug Mode: ENABLED[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1),
                width=60
                
            ))

        # Input prompt panel
        console.print(
            Panel(
                "[bold white]Vulnerability Write-up URL[/bold white]\n"
                "[dim](Provide a URL to a blog post or security advisory)[/dim]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(0, 1),
                width=60
            ))

        url = Prompt.ask("🔗 [cyan]URL[/cyan]")

        if not url:
            error_panel = Panel(
                "[red]❌ URL is required[/red]",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1),
                width=60
                
            )
            console.print(error_panel)
            return

        if self.verbose:
            info_panel = Panel(
                f"[dim]Processing: {url}[/dim]",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 1), 
                width=60
            )
            console.print(info_panel)

        # Always start workflow timer (needed for duration tracking)
        if self.logger:
            self.logger.start_workflow()

        try:
            markdown_data = await self.step_1_markdown_conversion(url)

            if markdown_data.get("error"):
                console.print(
                    f"[bold red]❌ Error: {
                        markdown_data.get(
                            'reason',
                            'Invalid URL')}[/bold red]")
                if self.debug_mode and self.logger:
                    self._display_debug_summary()
                return

            vulnerability_data = await self.step_2_vulnerability_parsing(markdown_data)
            plan_data = await self.step_3_lab_planning(vulnerability_data)
            lab_data = await self.step_4_lab_building(plan_data)

            output_path = self.save_artifacts(lab_data, plan_data)
            self.file_logger.finalize("success")

            if self.debug_mode and self.logger:
                self._display_debug_summary()

            self.display_summary(lab_data, output_path)

        except KeyboardInterrupt:
            self.file_logger.finalize("interrupted")
            console.print(
                "\n[yellow]⚠️  Workflow interrupted by user[/yellow]")
            if self.debug_mode and self.logger:
                self._display_debug_summary()
            sys.exit(0)
        except Exception as e:
            self.file_logger.finalize("failed")
            console.print(f"\n[bold red]❌ Workflow failed: {e}[/bold red]")
            if self.debug_mode:
                console.print(traceback.format_exc())
            sys.exit(1)

    def _display_debug_summary(self):
        """Display comprehensive debug summary"""
        if not self.logger:
            return

        console.print("\n" + "=" * 70)
        console.print(
            "[bold cyan]📊 Debug Summary - Workflow Analysis[/bold cyan]")
        console.print("=" * 70 + "\n")

        # Display action log table
        console.print(self.logger.format_action_log())
        console.print()

        # Display timing summary
        timing_table = Table(
            title="⏱️  Timing Summary",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold yellow")
        timing_table.add_column("Step", style="cyan")
        timing_table.add_column("Duration", style="yellow", justify="right")
        timing_table.add_column("Status", justify="center")

        step_timings = {}
        for action in self.logger.actions:
            if action["type"] == "step_end":
                step = action["step"]
                duration = action.get("duration", 0)
                success = action.get("success", False)
                step_timings[step] = {"duration": duration, "success": success}

        total_time = 0
        for step, data in step_timings.items():
            duration = data["duration"]
            success = data["success"]
            status = "✅" if success else "❌"
            timing_table.add_row(step, f"{duration:.2f}s", status)
            total_time += duration

        timing_table.add_row("[bold]TOTAL", f"[bold]{total_time:.2f}s", "")
        console.print(timing_table)
        console.print()

        # Display correctness metrics
        total_steps = len(step_timings)
        successful_steps = sum(
            1 for data in step_timings.values() if data["success"])
        success_rate = (
            successful_steps /
            total_steps *
            100) if total_steps > 0 else 0

        metrics_panel = Panel(
            f"[bold]Workflow Metrics:[/bold]\n\n"
            f"✅ Successful Steps: {successful_steps}/{total_steps}\n"
            f"📊 Success Rate: {success_rate:.1f}%\n"
            f"⏱️  Total Duration: {self.logger.get_total_elapsed()}\n"
            f"🔄 Total Actions Logged: {len(self.logger.actions)}",
            title="📈 Performance Metrics",
            border_style="green" if success_rate == 100 else "yellow",
            width=60
        )
        console.print(metrics_panel)
        console.print()


def run_wizard():
    """Run interactive configuration wizard"""
    # Wizard header
    wizard_header = Panel(
        "[bold cyan]🧙 LabGenie Configuration Wizard[/bold cyan]",
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 1),
        width=60
        
    )
    console.print(wizard_header)
    console.print()

    # Get URL
    step1_panel = Panel(
        "[bold white]Step 1: Vulnerability Write-up[/bold white]",
        border_style="cyan",
        box=box.ROUNDED,
        width=60
    )
    console.print(step1_panel)
    url = Prompt.ask("🔗 [cyan]Enter the write-up URL[/cyan]")

    # Output directory
    console.print()
    step2_panel = Panel(
        "[bold white]Step 2: Output Configuration[/bold white]",
        border_style="cyan",
        box=box.ROUNDED,
        width=60
    )
    console.print(step2_panel)
    use_custom_output = Confirm.ask(
        "📁 Use custom output directory?", default=False)
    output_dir = None
    if use_custom_output:
        output_dir = Path(Prompt.ask("Output directory", default="./output"))

    # Logs directory
    use_custom_logs = Confirm.ask(
        "📄 Use custom logs directory?",
        default=False)
    log_dir = None
    if use_custom_logs:
        log_dir = Path(Prompt.ask("Logs directory", default="./logs"))

    # Debug mode
    console.print()
    step3_panel = Panel(
        "[bold white]Step 3: Runtime Options[/bold white]",
        border_style="cyan",
        box=box.ROUNDED,
        width=60
        
    )
    console.print(step3_panel)
    debug_mode = Confirm.ask("🔍 Enable debug mode?", default=False)
    verbose = Confirm.ask("📝 Enable verbose output?", default=True)

    console.print()
    complete_panel = Panel(
        "[bold green]✓ Configuration complete![/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 1),
        width=60
        
    )
    console.print(complete_panel)
    console.print()

    return {
        'url': url,
        'output_dir': output_dir,
        'log_dir': log_dir,
        'debug_mode': debug_mode,
        'verbose': verbose
    }


async def main():
    """Main entry point for LabGenie CLI"""
    parser = argparse.ArgumentParser(
        prog='labgenie',
        description='LabGenie - Automated Vulnerability Lab Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive wizard mode
  labgenie --wizard

  # Generate lab from URL with default settings
  labgenie --url https://example.com/vuln-writeup

  # Custom output and logs directories
  labgenie --url https://example.com/vuln --output ./my-labs --logs ./my-logs

  # Enable debug mode for detailed logging
  labgenie --url https://example.com/vuln --debug

  # Quiet mode (minimal output)
  labgenie --url https://example.com/vuln --quiet

For more information, visit: https://github.com/yourusername/LabGenie
        """
    )

    parser.add_argument(
        '--url', '-u',
        type=str,
        help='Vulnerability write-up URL to process'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for generated labs (default: ./output)'
    )

    parser.add_argument(
        '--logs', '-l',
        type=str,
        help='Logs directory (default: ./logs)'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode with detailed logging'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - minimal console output'
    )

    parser.add_argument(
        '--provider',
        type=str,
        choices=['gemini', 'vertex'],
        help='AI provider backend (default: auto-detect from environment)'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        help='Gemini API key (overrides GOOGLE_API_KEY env)'
    )

    parser.add_argument(
        '--wizard', '-w',
        action='store_true',
        help='Run interactive configuration wizard'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='LabGenie v1.0.0'
    )

    args = parser.parse_args()

    # Wizard mode
    if args.wizard:
        config = run_wizard()
        workflow = LabGenieWorkflow(
            output_dir=config['output_dir'],
            log_dir=config['log_dir'],
            debug_mode=config['debug_mode'],
            verbose=config['verbose'],
            provider=None,  # Auto-detect
            api_key=None
        )

        workflow.display_banner()

        processing_panel = Panel(
            f"[dim]Processing URL: {config['url']}[/dim]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=60
            
        )
        console.print(processing_panel)
        console.print()

        # Always start workflow timer
        if workflow.logger:
            workflow.logger.start_workflow()

        try:
            markdown_data = await workflow.step_1_markdown_conversion(config['url'])

            if markdown_data.get("error"):
                console.print(
                    f"[bold red]❌ Error: {
                        markdown_data.get(
                            'reason',
                            'Invalid URL')}[/bold red]")
                return

            vulnerability_data = await workflow.step_2_vulnerability_parsing(markdown_data)
            plan_data = await workflow.step_3_lab_planning(vulnerability_data)
            lab_data = await workflow.step_4_lab_building(plan_data)

            output_path = workflow.save_artifacts(lab_data, plan_data)
            workflow.file_logger.finalize("success")

            if workflow.debug_mode and workflow.logger:
                workflow._display_debug_summary()

            workflow.display_summary(lab_data, output_path)

        except Exception as e:
            workflow.file_logger.finalize("failed")
            console.print(f"\n[bold red]❌ Workflow failed: {e}[/bold red]")
            sys.exit(1)

        return

    # CLI mode with arguments
    if args.url:
        output_dir = Path(args.output) if args.output else None
        log_dir = Path(args.logs) if args.logs else None
        verbose = not args.quiet

        workflow = LabGenieWorkflow(
            output_dir=output_dir,
            log_dir=log_dir,
            debug_mode=args.debug,
            verbose=verbose,
            provider=args.provider,  # None = auto-detect
            api_key=args.api_key
        )

        workflow.display_banner()

        if workflow.debug_mode:
            debug_panel = Panel(
                "[bold green]🔍 Debug Mode: ENABLED[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1),
                width=60
                
            )
            console.print(debug_panel)
            console.print()

        # Processing message
        processing_panel = Panel(
            f"[dim]Processing URL: {args.url}[/dim]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=60
            
        )
        console.print(processing_panel)
        console.print()

        # Always start workflow timer
        if workflow.logger:
            workflow.logger.start_workflow()

        try:
            markdown_data = await workflow.step_1_markdown_conversion(args.url)

            if markdown_data.get("error"):
                console.print(
                    f"[bold red]❌ Error: {
                        markdown_data.get(
                            'reason',
                            'Invalid URL')}[/bold red]")
                return

            vulnerability_data = await workflow.step_2_vulnerability_parsing(markdown_data)
            plan_data = await workflow.step_3_lab_planning(vulnerability_data)
            lab_data = await workflow.step_4_lab_building(plan_data)

            output_path = workflow.save_artifacts(lab_data, plan_data)
            workflow.file_logger.finalize("success")

            if workflow.debug_mode and workflow.logger:
                workflow._display_debug_summary()

            workflow.display_summary(lab_data, output_path)

        except Exception as e:
            workflow.file_logger.finalize("failed")
            console.print(f"\n[bold red]❌ Workflow failed: {e}[/bold red]")
            if args.debug:
                console.print(traceback.format_exc())
            sys.exit(1)

    else:
        # Interactive mode (default)
        workflow = LabGenieWorkflow()
        await workflow.run_interactive()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
        sys.exit(0)
