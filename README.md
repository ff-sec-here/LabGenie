# LabGenie - Vulnerability Lab Generator

**Transform vulnerability write-ups into fully functional, runnable security labs**

LabGenie is a terminal-first, interactive CLI tool that takes a vulnerability write-up URL and produces a complete, testable lab environment ready for security research and education.

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- **Option A**: Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey)) - **Recommended**
- **Option B**: Google Cloud Project with Vertex AI enabled

### Installation

1. **Clone or navigate to this directory**

```bash
cd /path/to/LabGenie
```

2. **Run the setup script**

```bash
bash setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Check for required API keys
- Make the CLI executable

3. **Configure your AI provider**

**Option A: Gemini API (Recommended)**
```bash
export GOOGLE_API_KEY='your-gemini-api-key'
```

**Option B: Vertex AI (Enterprise)**
```bash
export GOOGLE_CLOUD_PROJECT='your-gcp-project-id'
gcloud auth application-default login
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Run LabGenie

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Interactive mode (default)
python labgenie.py

# Direct URL mode
python labgenie.py --url https://example.com/vuln-writeup

# Debug mode for detailed output
python labgenie.py --debug
```

---

## Usage

Simply run the CLI and provide a vulnerability write-up URL:

```bash
$ python labgenie.py

🔗 Write-up URL: https://example.com/blog/sqli-vulnerability
```

The CLI will then:

1. **🔮 Convert** the write-up to structured markdown
2. **🔍 Parse** vulnerability information and reproduction steps  
3. **📋 Plan** the lab architecture and components
4. **🛠️ Build** complete, runnable lab artifacts

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
```

The lab name is automatically extracted from the vulnerability write-up or generated with a timestamp.

---

## Architecture

LabGenie implements a four-stage AI agent workflow that converts a vulnerability write-up to a complete, runnable lab environment.

For detailed information about the system architecture, agent designs, and technical implementation, see:

**📖 [docs/Architecture.md](docs/Architecture.md)**

---

## Documentation

- **[Architecture](docs/Architecture.md)** - System design and agent workflow
- **[Troubleshooting](docs/Troubleshooting.md)** - Common issues and solutions

---

## Contributing

Contributions are welcome!

---

## License

This tool is provided for educational and research purposes. Use responsibly.

---

## Acknowledgments

---

**Made with 🧞 magic by LabGenie**
