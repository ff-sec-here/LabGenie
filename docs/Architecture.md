# LabGenie Architecture

## Overview

LabGenie is a terminal-first CLI tool that transforms vulnerability write-ups into fully functional, runnable security labs. It implements a four-stage AI agent workflow that converts a vulnerability write-up URL to a complete, testable lab environment.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LabGenie CLI                            │
│                    (labgenie.py)                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Workflow Orchestrator                          │  │
│  │        (LabGenieWorkflow class)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Provider Layer                            │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   Gemini API     │      OR      │   Vertex AI      │        │
│  │  (google.genai)  │              │  (google-cloud)  │        │
│  └──────────────────┘              └──────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Pipeline (4 Stages)                    │
│                                                                 │
│  Stage 1: WriteUpToMarkdown                                    │
│  ├─ Model: gemini-2.5-flash                                    │
│  ├─ Input: URL                                                 │
│  ├─ Process: Fetch via Jina.ai, validate content              │
│  └─ Output: Markdown content + metadata                       │
│                              │                                  │
│                              ▼                                  │
│  Stage 2: WriteupParser                                        │
│  ├─ Model: gemini-2.5-pro                                      │
│  ├─ Input: Markdown content                                    │
│  ├─ Process: Extract vulnerability details                    │
│  └─ Output: Structured vulnerability data                     │
│                              │                                  │
│                              ▼                                  │
│  Stage 3: LabCorePlanner                                       │
│  ├─ Model: gemini-2.5-pro                                      │
│  ├─ Input: Vulnerability data                                  │
│  ├─ Process: Design lab architecture                          │
│  └─ Output: Complete lab plan                                 │
│                              │                                  │
│                              ▼                                  │
│  Stage 4: LabBuilder                                           │
│  ├─ Model: gemini-2.5-pro                                      │
│  ├─ Input: Lab plan                                            │
│  ├─ Process: Generate code, configs, tests                    │
│  └─ Output: Runnable lab artifacts                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output Layer                                 │
│                                                                 │
│  output/{lab_name}/                                            │
│  ├── lab_manifest.json                                         │
│  ├── README.md                                                 │
│  ├── docker-compose.yml                                        │
│  ├── src/                                                      │
│  ├── tests/                                                    │
│  └── exploits/                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Details

### 1. WriteUpToMarkdown Agent

**Purpose**: Convert vulnerability write-up URLs to markdown and validate content type.

**Location**: `agents/WriteUpToMarkdown/agent.py`

**Model**: `gemini-2.5-flash` (lightweight, fast for content validation)

**Configuration**:
- Temperature: 0.4 (consistent validation decisions)
- Max Output Tokens: 15,000
- Top P: 0.9
- Top K: 40

**Process**:
1. Receives a URL as input
2. Fetches content via Jina.ai (`https://r.jina.ai/{url}`)
3. Validates if content is a vulnerability write-up
4. Returns structured JSON with:
   - `status`: "ok" or "error"
   - `markdown`: Full markdown content
   - `input`: URL and fetch metadata
   - `error`: Error details if applicable


---

### 2. WriteupParser Agent

**Purpose**: Extract structured vulnerability information from markdown content.

**Location**: `agents/WriteupParser/agent.py`

**Model**: `gemini-2.5-pro` (precise information extraction)

**Configuration**:
- Temperature: 0.2 (high precision for extraction)
- Max Output Tokens: 8,192
- Top P: 0.9
- Top K: 20

**Process**:
1. Receives markdown content
2. Extracts vulnerability details:
   - Title and description
   - CVE identifiers
   - Affected software/versions
   - Vulnerability type
   - Attack vectors
   - Severity
   - References
3. Returns structured vulnerability data


---

### 3. LabCorePlanner Agent

**Purpose**: Design complete lab architecture from vulnerability data.

**Location**: `agents/LabCorePlanner/agent.py`

**Model**: `gemini-2.5-pro` (complex planning and architecture)

**Configuration**:
- Temperature: 0.5 (balanced creativity and precision)
- Max Output Tokens: 16,384
- Top P: 0.92
- Top K: 40

**Process**:
1. Receives structured vulnerability data
2. Designs lab components:
   - Application architecture
   - Database schema
   - Docker configuration
   - Network topology
   - Test scenarios
   - Exploit strategies
3. Returns comprehensive lab plan with:
   - File structure
   - Technology stack
   - Setup instructions
   - Test cases


---

### 4. LabBuilder Agent

**Purpose**: Generate complete, runnable lab artifacts from the plan.

**Location**: `agents/LabBuilder/agent.py`

**Model**: `gemini-2.5-pro` (code generation)

**Configuration**:
- Temperature: 0.3 (precise code generation)
- Max Output Tokens: 65,536 (maximum for complete labs)
- Top P: 0.9
- Top K: 30

**Process**:
1. Receives lab plan
2. Generates all required files:
   - Application source code
   - Docker configurations
   - Database schemas
   - Test scripts
   - Exploit PoCs
   - Documentation
3. Returns structured file list with:
   - `path`: File path
   - `content`: Full file content
   - `type`: File type
   - `description`: File purpose


---

## Base Agent Class

**Location**: `agents/base_agent.py`

**Purpose**: Provides common functionality for all agents.

**Key Features**:

1. **Multi-Provider Support**:
   - Gemini API (via `google-generativeai`)
   - Vertex AI (via `google-cloud-aiplatform`)
   - Auto-detection based on environment variables

2. **Lazy Loading**:
   - SDKs are imported only when needed
   - Reduces startup time and dependencies

3. **Prompt Management**:
   - Loads system instructions from markdown files
   - Each agent has its own prompt template
   - Supports dynamic prompt composition

4. **JSON Generation**:
   - `generate_json()` method with retry logic
   - Automatic JSON cleaning and repair
   - Handles markdown code fences
   - Repairs common JSON errors (trailing commas, unquoted keys)

5. **Error Handling**:
   - Detailed error logging to `logs/agent_errors/`
   - Retry mechanism (up to 3 attempts)
   - Context-aware error messages

6. **Response Parsing**:
   - Cleans markdown code blocks
   - Repairs malformed JSON
   - Extracts JSON from mixed content
   - Detailed error reporting with context

---

## Configuration System

**Location**: `config.json`

**Purpose**: Centralized model configuration for all agents.

**Structure**:
```json
{
  "models": {
    "WriteUpToMarkdown": "gemini-2.5-flash",
    "WriteupParser": "models/gemini-2.5-pro",
    "LabCorePlanner": "models/gemini-2.5-pro",
    "LabBuilder": "models/gemini-2.5-pro"
  }
}
```

**Features**:
- Easy model switching without code changes
- Supports both Gemini API and Vertex AI model names
- Override via CLI arguments

---

## Environment Configuration

### Required Variables

**For Gemini API** (Recommended):
```bash
export GOOGLE_API_KEY='your-api-key'
```

**For Vertex AI** (Enterprise):
```bash
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'  # Optional
```

### Optional Variables

```bash
# Explicitly set provider (auto-detected by default)
export LABGENIE_PROVIDER='gemini'  # or 'vertex'
```

---

## Workflow Execution

### Interactive Mode

```bash
python labgenie.py
```

**Flow**:
1. Display banner with provider info
2. Prompt for vulnerability write-up URL
3. Execute 4-stage pipeline with animations
4. Save artifacts to `output/{lab_name}/`
5. Display summary with file count and timing


---

## Logging System

### File Logger

**Location**: `logs/{run_id}/`

**Files**:
- `step_1_markdown_conversion.json`
- `step_2_vulnerability_parsing.json`
- `step_3_lab_planning.json`
- `step_4_lab_building.json`

**Purpose**: Debug and audit trail for each run.

### Debug Logger

**Purpose**: Real-time action tracking during execution.

**Features**:
- Step timing
- Action status (info, success, error, warning)
- Elapsed time tracking
- Rich terminal output

### Error Logger

**Location**: `logs/agent_errors/error_{timestamp}.log`

**Content**:
- Timestamp
- Agent name
- Model used
- Error message
- Full context

---

## Performance Characteristics

### Model Selection Strategy

- **gemini-2.5-flash**: Fast, lightweight tasks (URL validation)
- **gemini-2.5-pro**: Complex tasks (parsing, planning, building)

---

## Extension Points

### Adding New Agents

1. Create agent directory in `agents/`
2. Add `prompt.md` with system instructions
3. Create `agent.py` inheriting from `BaseAgent`
4. Update workflow in `labgenie.py`
5. Add model to `config.json`

### Custom Models

1. Update `config.json` with new model names
2. Adjust generation configs in agent `__init__`
3. Test with various inputs
### New Providers

1. Add SDK import in `base_agent.py`
2. Implement provider logic in `BaseAgent.__init__`
3. Add environment variable checks
4. Update documentation

---

## Development Workflow

1. **Clone Repository**: Get the LabGenie codebase
2. **Setup Environment**: Run `setup.sh` to create venv
3. **Configure API**: Set `GOOGLE_API_KEY` or Vertex credentials
4. **Test Agents**: Use debug mode to verify functionality
5. **Iterate**: Modify prompts and configs as needed
6. **Validate**: Test with real vulnerability write-ups

---

## Best Practices

1. **Prompt Engineering**: Keep prompts in separate `.md` files
2. **Model Selection**: Use flash for speed, pro for quality
3. **Error Logging**: Always log to files for debugging
4. **Configuration**: Use `config.json` for easy updates
5. **Testing**: Run with `--debug` to verify behavior
6. **Version Control**: Track changes to prompts and configs

---

## Future Enhancements

- Support for additional AI providers (Claude, GPT-4)
- Web interface for lab generation
- Lab testing automation
- Lab library and sharing
- Custom lab templates
- Multi-language support
- CI/CD integration