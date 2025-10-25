"""
🧞 ULTRA ENHANCED GENIE ANIMATION 🧞
Maximum Visual Impact - Production Ready Awesomeness
"""
import asyncio
import time
import random
from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.live import Live


def create_particle_field(width: int = 60, height: int = 5) -> str:
    """Create a random particle field effect"""
    particles = ["✨", "⭐", "💫", "🌟", "✦", "★", "◆", "◇", " ", " ", " "]
    field = []
    for _ in range(height):
        row = "".join(random.choice(particles) for _ in range(width))
        field.append(row)
    return "\n".join(field)


def get_gradient_text(text: str, colors: list) -> Text:
    """Create gradient text effect"""
    result = Text()
    for i, char in enumerate(text):
        color = colors[i % len(colors)] if colors else "white"
        result.append(char, style=color)
    return result


def create_epic_startup_banner() -> Panel:
    """Create startup banner"""
    banner = Text()

    # Title with gradient
    title_colors = [
        "bold cyan",
        "bold blue",
        "bold magenta",
        "bold yellow",
        "bold green"]

    banner.append("     ", style="bold")  # Center alignment
    for i, char in enumerate("⚡ LAB GENIE ⚡"):
        banner.append(char, style=title_colors[i % len(title_colors)])
    banner.append("\n", style="bold")

    # Subtitle
    banner.append("     ━━━━━━━━━━━━━━━\n", style="cyan")
    banner.append("     Vulnerabilities → Labs\n", style="bold white")
    banner.append("     ━━━━━━━━━━━━━━━\n", style="cyan")

    banner.append("     🧞 ✨ 🔮 ⚡ 💫 🌟\n", style="")

    return Panel(
        banner,
        box=box.DOUBLE_EDGE,
        border_style="bold magenta",
        padding=(0, 1),
        width=38
    )


def create_loading_frame(
        step: int,
        total: int = 4,
        message: str = "Processing") -> Panel:
    """Create a fancy loading frame with progress"""

    # Genie states based on progress
    genie_states = [
        r"""
    ___
   /   \
  | 🧞  |
   \___/
    | |
  ∼∼∼∼∼
""",
        r"""
    ___
   / ✨ \
  | 🧞  |
   \___/
    | |
  ∼∼∼∼∼
""",
        r"""
    ___
   /⚡ ⚡\
  |✨🧞✨|
   \___/
  💫| |💫
  ∼∼∼∼∼
""",
        r"""
  ⭐ ___  ⭐
   /💫💫\
  |⚡🧞⚡|
   \___/
  ✨ | | ✨
  ∼∼∼∼∼∼
""",
        r"""
 💫⭐___⭐💫
  /✨✨✨\
 ⚡|🧞💫|⚡
  \___/
 🌟 | | 🌟
  ∼∼∼∼∼∼
""",
    ]

    genie = genie_states[min(step, len(genie_states) - 1)]

    # Progress bar
    filled = "▰" * step
    empty = "▱" * (total - step)
    progress_colors = ["cyan", "magenta", "yellow", "green", "bold green"]
    progress_color = progress_colors[min(step, len(progress_colors) - 1)]

    progress_bar = f"[{progress_color}]{filled}[/][dim]{empty}[/dim] {step * 20}%"

    # Particle effect
    particles = random.choice(["✨ 💫 ⭐", "⚡ 🌟 ✨", "💫 ⭐ 🔮", "✨ ⚡ 💫"])

    content = Text()
    content.append(genie, style="bold magenta")
    content.append("\n")
    content.append(f"     {message}\n", style="bold cyan")
    content.append(f"     {particles}\n\n", style="")
    content.append(f"     {progress_bar}\n", style="")

    border_colors = ["blue", "magenta", "cyan", "yellow", "green"]
    border_color = border_colors[min(step, len(border_colors) - 1)]

    return Panel(
        content,
        box=box.DOUBLE,
        border_style=f"bold {border_color}",
        title="[bold white]✨ GENIE LAB MAGIC ✨[/bold white]",
        padding=(1, 2)
    )


def animate_startup(console: Console, duration: float = 1.5):
    """Animate an epic startup sequence"""
    steps = [
        "Initializing Magic",
        "Loading Spells",
        "Charging Energy",
        "Ready to Create"
    ]

    with Live(console=console, refresh_per_second=10, transient=True) as live:
        for i, step in enumerate(steps):
            frame = create_loading_frame(i, len(steps), step)
            live.update(frame)
            time.sleep(duration / len(steps))


def create_step_animation(
        step_name: str,
        description: str,
        progress: float = 0.0,
        elapsed_time: str = "00:00") -> Panel:
    """Create animated panel for workflow step with timer"""

    # Rotating spinner symbols
    spinners = ["🔮", "✨", "💫", "⚡", "🌟", "⭐"]
    spinner = spinners[int(time.time() * 3) % len(spinners)]

    # Progress visualization (compact for half-screen)
    bar_width = 20
    filled_width = int(bar_width * (progress / 100))
    bar = "▰" * filled_width + "▱" * (bar_width - filled_width)

    # Color based on progress
    if progress < 30:
        color = "cyan"
    elif progress < 70:
        color = "yellow"
    else:
        color = "green"

    content = Text()
    content.append(f"{spinner} ", style="bold magenta")
    content.append(step_name, style="bold white")
    content.append("\n")
    content.append(f"{description}\n", style="dim")
    content.append(f"\n{bar} {progress:.0f}%", style=color)
    content.append(f"  ⏱ {elapsed_time}", style=color)

    return Panel(
        content,
        box=box.ROUNDED,
        border_style=f"bold {color}",
        padding=(0, 1),
        width=38
    )


def create_success_banner(
        lab_name: str,
        file_count: int,
        total_time: str = "00:00") -> Panel:
    """Create epic success banner with total time"""

    success_art = r"""
    ⭐ ✨ 💫 🌟 ⚡ 💫 ✨ ⭐

       🎉 SUCCESS! 🎉

      🧞 Lab Created! 🧞

    ⭐ ✨ 💫 🌟 ⚡ 💫 ✨ ⭐
    """

    content = Text()
    content.append(success_art, style="bold green")
    content.append("\n")
    content.append(f"  Lab: {lab_name}\n", style="bold cyan")
    content.append(f"  Files: {file_count}\n", style="bold yellow")
    content.append(f"  Time: {total_time}\n", style="bold magenta")
    content.append("\n  ✨ Ready to Deploy! ✨\n", style="bold white")

    return Panel(
        content,
        box=box.DOUBLE_EDGE,
        border_style="bold green",
        title="[bold white]🏆 COMPLETE 🏆[/bold white]",
        padding=(1, 1)
    )


def create_matrix_rain(console: Console, duration: float = 1.5):
    """Create Matrix-style particle rain effect"""
    particles = ["✨", "⭐", "💫", "🌟", "✦", "★"]

    with Live(console=console, refresh_per_second=20, transient=True) as live:
        start_time = time.time()
        while time.time() - start_time < duration:
            lines = []
            for _ in range(3):
                line = " ".join(random.choice(particles) for _ in range(20))
                lines.append(line)

            panel = Panel(
                "\n".join(lines),
                border_style="bold cyan",
                box=box.MINIMAL
            )
            live.update(panel)
            time.sleep(0.05)


def create_power_meter(power_level: int = 100) -> Table:
    """Create a power meter display"""
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))

    table.add_column(justify="right")
    table.add_column(justify="left")

    # Power bars
    meters = [
        ("⚡ Magic", power_level),
        ("🔮 Energy", power_level - 10),
        ("✨ Creativity", power_level - 5),
        ("💫 Precision", power_level - 15),
    ]

    for label, level in meters:
        bar_width = 20
        filled = int(bar_width * (level / 100))
        bar = "█" * filled + "░" * (bar_width - filled)

        if level >= 80:
            color = "bold green"
        elif level >= 50:
            color = "bold yellow"
        else:
            color = "bold red"

        table.add_row(label, f"[{color}]{bar}[/] {level}%")

    return Panel(
        table,
        title="[bold magenta]⚡ GENIE POWER LEVELS ⚡[/bold magenta]",
        border_style="bold cyan",
        box=box.DOUBLE
    )


def display_workflow_banner(
        console: Console,
        provider: Optional[str],
        run_id: str,
        output_display: str,
        verbose: bool = False) -> None:
    """Render the startup banner and optional provider info."""

    console.print()
    console.print(create_epic_startup_banner())

    if verbose:
        provider_name = "Vertex AI" if provider == "vertex" else "Gemini API"
        info_text = (
            f"[dim]Provider: {provider_name} | "
            f"Run: {run_id} | "
            f"Output: {output_display}[/dim]"
        )
        console.print(info_text)

    console.print()


async def execute_step_with_animation(
        step_name: str,
        coro,
        description: str,
        console: Console,
        logger: Optional[Any] = None,
        file_logger: Optional[Any] = None,
        debug_mode: bool = False,
        verbose: bool = False,
        agent_input: Any = None) -> Any:
    """Run a workflow coroutine while rendering live step animations."""

    if logger:
        logger.start_step(step_name, description)

    result: Any = None
    error: Optional[Exception] = None
    step_start = time.time()

    async def run_task():
        nonlocal result, error
        try:
            if debug_mode and logger:
                logger.log_action(
                    f"Calling agent: {step_name}",
                    "Sending request to LLM",
                    "processing"
                )

            result = await coro

            if debug_mode and logger:
                if isinstance(result, dict):
                    if result.get("error"):
                        logger.log_action(
                            "Agent returned error",
                            result.get("reason", ""),
                            "error"
                        )
                    else:
                        result_keys = list(result.keys())[:5]
                        logger.log_action(
                            "Agent response received",
                            f"Keys: {result_keys}",
                            "success"
                        )
                else:
                    logger.log_action(
                        "Agent response received",
                        f"Type: {type(result)}",
                        "success"
                    )
        except Exception as exc:  # pylint: disable=broad-except
            error = exc
            if debug_mode and logger:
                logger.log_action("Exception occurred", str(exc), "error")

    async def make_display_panel() -> Panel:
        elapsed = time.time() - step_start
        total_elapsed = logger.get_total_elapsed() if logger else "00:00:00"

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        progress = min(90, (elapsed / 30) * 100)

        return create_step_animation(
            step_name=step_name,
            description=description,
            progress=progress,
            elapsed_time=f"Step: {elapsed_str} | Workflow: {total_elapsed}"
        )

    task = asyncio.create_task(run_task())

    with Live(
            await make_display_panel(),
            refresh_per_second=4,
            console=console,
            transient=True) as live:
        while not task.done():
            await asyncio.sleep(0.33)
            live.update(await make_display_panel())

    await task

    step_duration = time.time() - step_start

    if error:
        if logger:
            logger.end_step(False, str(error))
        console.print(f"[bold red]❌ {step_name} failed: {error}[/bold red]")
        if verbose:
            console.print(f"[dim]Duration: {step_duration:.2f}s[/dim]\n")
        raise error

    result_summary = "Success"
    if isinstance(result, dict):
        if "files" in result:
            result_summary = f"Generated {len(result['files'])} files"
        elif "markdown" in result:
            markdown_len = len(result['markdown'])
            result_summary = f"Markdown length: {markdown_len} chars"

    if logger:
        logger.end_step(True, result_summary)

    if file_logger:
        file_logger.log_agent_response(
            step_name.replace(" ", "_"),
            result,
            agent_input
        )

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


def display_success_banner(
        console: Console,
        lab_name: str,
        file_count: int,
        total_time: str = "00:00") -> None:
    """Print the final success banner for a completed lab."""

    console.print()
    console.print(create_success_banner(lab_name, file_count, total_time))


# Export main functions
__all__ = [
    'create_epic_startup_banner',
    'animate_startup',
    'create_step_animation',
    'create_success_banner',
    'create_matrix_rain',
    'create_power_meter',
    'create_loading_frame',
    'display_workflow_banner',
    'execute_step_with_animation',
    'display_success_banner',
]
