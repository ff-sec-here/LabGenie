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

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo "✅ Dependencies installed"
echo ""

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not set"
    echo ""
    echo "To set your API key:"
    echo "  1. Get an API key from: https://makersuite.google.com/app/apikey"
    echo "  2. Run: export GOOGLE_API_KEY='your-api-key'"
    echo "  3. Or create a .env file with: GOOGLE_API_KEY=your-api-key"
    echo ""
else
    echo "✅ GOOGLE_API_KEY detected"
    echo ""
fi

# Make CLI executable
chmod +x labgenie.py

echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "  # Activate virtual environment (if not already active)"
echo "  source venv/bin/activate"
echo ""
echo "  # Run LabGenie"
echo "  python labgenie.py"
echo ""
echo "  # Or use direct URL mode"
echo "  python labgenie.py --url https://example.com/vuln-writeup"
echo ""
echo "📚 Documentation:"
echo "  README.md - Usage instructions"
echo "  docs/Architecture.md - System architecture"
echo ""
echo "💡 Tip: The virtual environment must be activated before running LabGenie"
echo ""
