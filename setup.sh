#!/bin/bash

# LabGenie Setup Script
# Quick installation and configuration

set -e

echo "🧞 LabGenie Setup"
echo "=================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10+ required, found $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# ─── Provider detection ──────────────────────────────────────────────────────

PROVIDER_FOUND=""

# Option 1: Claude Code CLI (subscription — no API key needed)
if command -v claude &> /dev/null; then
    echo "✅ Claude Code CLI detected — using subscription (no API key needed)"
    PROVIDER_FOUND="claude-code"

# Option 2: Claude API key
elif [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY detected — using Claude API"
    PROVIDER_FOUND="claude"

# Option 3: Gemini API key
elif [ -n "$GOOGLE_API_KEY" ]; then
    echo "✅ GOOGLE_API_KEY detected — using Gemini API"
    PROVIDER_FOUND="gemini"

# Option 4: Vertex AI
elif [ -n "$GOOGLE_CLOUD_PROJECT" ] || [ -n "$GCP_PROJECT" ]; then
    echo "✅ GCP project detected — using Vertex AI"
    PROVIDER_FOUND="vertex"

else
    echo "⚠️  No AI provider configured"
    echo ""
    echo "Please set up one of the following:"
    echo ""
    echo "  Option 1 — Claude Code subscription (Recommended, no API costs):"
    echo "    Install: https://claude.ai/download"
    echo "    Login:   claude login"
    echo ""
    echo "  Option 2 — Claude API:"
    echo "    export ANTHROPIC_API_KEY='your-key'"
    echo "    Get key: https://console.anthropic.com/"
    echo ""
    echo "  Option 3 — Gemini API:"
    echo "    export GOOGLE_API_KEY='your-key'"
    echo "    Get key: https://makersuite.google.com/app/apikey"
    echo ""
    echo "  Option 4 — Vertex AI (Enterprise):"
    echo "    export GOOGLE_CLOUD_PROJECT='your-project-id'"
    echo "    gcloud auth application-default login"
    echo ""
fi

# Make CLI executable
chmod +x labgenie.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "  # Activate virtual environment (if not already active)"
echo "  source venv/bin/activate"
echo ""
echo "  # Run LabGenie (auto-detects provider)"
echo "  python labgenie.py"
echo ""
echo "  # Or direct URL mode"
echo "  python labgenie.py --url https://example.com/vuln-writeup"
echo ""

if [ "$PROVIDER_FOUND" = "claude-code" ]; then
    echo "  # Using Claude Code subscription (--provider claude-code)"
    echo "  python labgenie.py --url https://example.com/vuln --provider claude-code"
    echo ""
fi

echo "📚 Documentation:"
echo "  README.md          — Usage instructions"
echo "  docs/Architecture.md — System architecture"
echo "  docs/Troubleshooting.md — Common issues"
echo ""
echo "💡 Tip: The virtual environment must be activated before running LabGenie"
echo ""
