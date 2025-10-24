# LabGenie - Vulnerability Lab Generator

**Transform vulnerability write-ups into fully functional, runnable security labs**

LabGenie is a terminal-first, interactive CLI tool that implements the Lab Core Planner workflow. It takes a vulnerability write-up URL and produces a complete, testable lab environment ready for security research and education.

---

## Features

- **Automated Lab Generation** - From URL to working lab in minutes
- **Animated Genie Mascot** - Colorful terminal animations during processing
- **Real-Time Debug Mode** - Track agent actions, timing, and correctness indicators
- **Safety First** - All exploits target localhost only, with authorization checks
- **Beautiful CLI** - Rich terminal UI with progress bars and panels
- **Dual AI Providers** - Choose between Gemini API or Vertex AI
- **Complete Artifacts** - Generates code, configs, tests, and documentation
- **Cross-Platform** - Works on Linux, macOS, and Windows (WSL)
- **Performance Tracking** - Monitor step duration and overall workflow progress
- **Production Ready** - Clean, optimized, and well-documented

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- **Option A**: Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey)) - **Recommended for ease of use**
- **Option B**: Google Cloud Project with Vertex AI enabled

### Installation

1. **Clone or navigate to this directory**

```bash
cd /path/to/LabGenie
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure your AI provider**

**LabGenie auto-detects which provider you have configured!** Just set the credentials:

**Option A: Gemini API (Recommended - Easiest)**
```bash
export GOOGLE_API_KEY='your-gemini-api-key'
# LabGenie will auto-detect and use Gemini
```

**Option B: Vertex AI (Enterprise)**
```bash
export GOOGLE_CLOUD_PROJECT='your-gcp-project-id'
gcloud auth application-default login
# LabGenie will auto-detect and use Vertex
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your configuration
# No need to set LABGENIE_PROVIDER - it auto-detects!
```

### Run LabGenie

```bash
# Interactive mode (default)
python labgenie.py

# Direct URL mode
python labgenie.py --url https://example.com/vuln-writeup

# Specify provider explicitly
python labgenie.py --provider gemini --api-key YOUR_KEY --url https://example.com/vuln
```

### Demo Debug Features (Optional)

Want to see the debug features in action without making API calls?

```bash
python demo_debug_features.py
```

This will run a simulation showing:
- Real-time action tracking
- Timing information
- Correctness indicators
- Debug summary reports

---

## Usage

### Interactive Mode

Simply run the CLI and follow the prompts:

```bash
$ python labgenie.py

╔═══════════════════════════════════════════════════════════╗
║  🧞 LabGenie - Vulnerability Lab Generator              ║
║  Transform vulnerability write-ups into working labs    ║
╚═══════════════════════════════════════════════════════════╝

Please provide a vulnerability write-up URL:
(The URL should point to a blog post or security advisory)

🔗 Write-up URL: https://example.com/blog/sqli-vulnerability
```

The CLI will then:

1. **🔮 Convert** the write-up to structured markdown
2. **🔍 Parse** vulnerability information and reproduction steps  
3. **📋 Plan** the lab architecture and components
4. **🛠️ Build** complete, runnable lab artifacts

### Debug Mode

Debug mode is **enabled by default** and provides real-time visibility into agent actions:

```
🔍 Debug Mode: ENABLED
Real-time action tracking and timing information will be displayed

🔮 WriteUp to Markdown Conversion
Fetching and converting the vulnerability write-up to structured markdown...
⏱️  Total elapsed: 00:00:05

⚙️ Calling agent: WriteUp to Markdown Conversion
✅ Agent response received: Keys: ['markdown', 'metadata', 'url']

✅ WriteUp to Markdown Conversion completed successfully!
⏱️  Step duration: 8.45s
```

At the end of the workflow, you'll see a comprehensive debug summary with:
- **Action Log**: All agent actions with timestamps
- **Timing Summary**: Duration for each step
- **Performance Metrics**: Success rate and total duration

See [DEBUG_FEATURES.md](DEBUG_FEATURES.md) for complete documentation.

### Output

All generated files are saved to `./output/{labname}/`:

```
output/
└── sqli_vulnerability_lab/      # Lab name extracted from vulnerability
    ├── lab_manifest.json         # Complete lab metadata
    ├── README.md                 # Lab setup instructions
    ├── docker-compose.yml        # Container orchestration
    ├── src/                      # Application source code
    ├── tests/                    # Verification scripts
    └── exploits/                 # PoC scripts (localhost only)

The lab name is automatically extracted from the vulnerability write-up or generated with a timestamp.

---

## Architecture

LabGenie implements a four-stage AI agent workflow that converts a vulnerability write-up to a complete, runnable lab environment.

### 1. WriteUpToMarkdown Agent
- **Model**: Gemini Pro (default)
{{ ... }}
- Planning lab architecture
- Generating code artifacts

---

## AI Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
{{ ... }}
### Complete Documentation

See [DEBUG_FEATURES.md](DEBUG_FEATURES.md) for:
- Full feature documentation
- Status icon reference
- ## Example Outputs
- Use cases and best practices

### Try the Demo

Run the demo to see debug features without API calls:
{{ ... }}
python demo_debug_features.py
```

---

## 🧪 Development Mode

**Test individual agents for debugging and development**

LabGenie includes a development mode that allows you to run individual agents in isolation:

```bash
python labgenie_dev.py
```

This is useful for:
- 🐛 **Debugging**: Test specific agents with custom inputs
- 🔬 **Development**: Iterate on agent prompts quickly
- 📊 **Analysis**: Inspect outputs at each pipeline stage
- 🧪 **Testing**: Test edge cases without running full workflow

### Quick Examples

```bash
# Interactive mode - select agent from menu
python labgenie_dev.py

# Run WriteUpToMarkdown agent
python labgenie_dev.py --agent 1 --url https://example.com/vuln

# Run LabBuilder agent with custom plan
python labgenie_dev.py --agent 4 --input dev_output/03_plan.json
```

### Available Agents

| # | Agent | Description |
|---|-------|-------------|
| 1 | WriteUpToMarkdown | Convert URL to markdown |
| 2 | WriteupParser | Parse vulnerability information |
| 3 | LabCorePlanner | Create lab plan (no code) |
| 4 | LabBuilder | Generate complete lab code |

**Full Documentation**: See [DEV_MODE.md](DEV_MODE.md) for complete usage guide.

---

## 🐛 Troubleshooting

### Common Issues

**No Provider Configured**
```
❌ Error: No AI provider configured
```
**Solution**: Set credentials for either provider
```bash
# For Gemini (easier)
export GOOGLE_API_KEY='your-key'

# OR for Vertex (enterprise)
export GOOGLE_CLOUD_PROJECT='your-project-id'
gcloud auth application-default login
```

**Vertex AI Project Not Set**
```
❌ Error: Vertex provider not configured
GOOGLE_CLOUD_PROJECT environment variable not set
```
**Solution**: Configure Vertex AI
```bash
export LABGENIE_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT='your-project-id'
gcloud auth application-default login
```

**Rate Limiting Issues**
```
❌ Error: Resource exhausted (quota exceeded)
```
**Solution**: 
- For Gemini API: Get additional API keys and rotate them
- For Vertex AI: Request quota increase in GCP Console

**URL Fetch Failed**
```
❌ Error: Failed to fetch URL: Connection timeout
```
**Solution**: Check internet connection and URL validity

**Invalid Write-up**
```
⚠️ The provided URL is not a blog post or vulnerability write-up
```
**Solution**: Ensure the URL points to a security blog or advisory

---

## Contributing

Contributions are welcome!

---

## License

This tool is provided for educational and research purposes. Use responsibly.

---

## Acknowledgments

- Built on the n8n Lab Core Planner workflow
- Powered by Google Gemini AI
- Terminal UI by Rich library
- Markdown conversion via Jina.ai

---

**Made with 🧞 magic by LabGenie**
