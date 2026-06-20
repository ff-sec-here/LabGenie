# Troubleshooting Guide

## Common Issues

### No AI Provider Configured

**Error:**
```
❌ Error: No AI provider configured
```

**Solution:** Set up one of the following providers:

```bash
# Option 1 — Claude Code subscription (no API costs)
claude login   # after installing from https://claude.ai/download

# Option 2 — Claude API
export ANTHROPIC_API_KEY='your-key'

# Option 3 — Gemini API
export GOOGLE_API_KEY='your-key'

# Option 4 — Vertex AI
export GOOGLE_CLOUD_PROJECT='your-project-id'
gcloud auth application-default login
```

---

### Claude Code CLI Not Found

**Error:**
```
❌ Error: claude-code provider not configured
Claude Code CLI not found.
```

**Solution:** Install Claude Code and log in:
```bash
# Download from https://claude.ai/download, then:
claude login
```

---

### Anthropic API Key Missing

**Error:**
```
❌ Error: Claude provider not configured
ANTHROPIC_API_KEY environment variable not set.
```

**Solution:**
```bash
export ANTHROPIC_API_KEY='your-key'
```

> **Note:** `ANTHROPIC_API_KEY` is a **separate pay-per-use key** from [console.anthropic.com](https://console.anthropic.com/). It is not your Claude.ai or Claude Code subscription. If you have a Claude Code subscription, use `--provider claude-code` instead.

---

### Vertex AI Project Not Set

**Error:**
```
❌ Error: Vertex provider not configured
GOOGLE_CLOUD_PROJECT environment variable not set
```

**Solution:**
```bash
export GOOGLE_CLOUD_PROJECT='your-project-id'
gcloud auth application-default login
```

---

### Gemini GenerationConfig Conflict

**Error:**
```
Invalid input type. Expected a dict or GenerationConfig for generation_config.
However, received an object of type: vertexai.generative_models...
```

**Solution:** Both `google-cloud-aiplatform` and `google-generativeai` are installed and conflicting. This is fixed in the latest version — pull the latest code and reinstall:
```bash
git pull
pip install -r requirements.txt
```

---

### Rate Limiting

**Error:**
```
❌ Error: Resource exhausted (quota exceeded)
```

**Solution:**
- **Claude Code**: Rate limits are per-session; wait a moment or use `--provider claude` with an API key for higher throughput.
- **Claude API**: Check usage limits at [console.anthropic.com](https://console.anthropic.com/).
- **Gemini API**: Get additional API keys or request quota increase.
- **Vertex AI**: Request quota increase in GCP Console.

---

### URL Fetch Failed

**Error:**
```
❌ Error: Failed to fetch URL: Connection timeout
```

**Solution:**
- Check your internet connection
- Verify the URL is accessible
- Try a different network if behind a firewall

---

### Invalid Write-up

**Error:**
```
⚠️ The provided URL is not a blog post or vulnerability write-up
```

**Solution:**
- Ensure the URL points to a security blog or advisory
- The content should describe a vulnerability, not a general article
- Try a different URL that clearly describes a security vulnerability

---

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'output/...'
```

**Solution:**
- Ensure you have write permissions in the current directory
- Run with appropriate permissions or change to a writable directory

---

### Python Version Error

**Error:**
```
❌ Error: Python 3.10+ required, found 3.8
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3.10

# macOS (Homebrew)
brew install python@3.10

python3 --version
```

---

## Debug Mode

Enable debug mode for detailed logging:

```bash
python labgenie.py --debug
```

This shows real-time action tracking, agent response details, timing information, and error stack traces. Debug logs are also saved to `logs/{run_id}/`.

---

## Getting Help

1. **Check the logs**: `logs/` and `logs/agent_errors/` for detailed error messages
2. **Review the docs**: See `docs/Architecture.md` for system details
3. **Check your configuration**: Verify API keys and environment variables

**Or** raise an issue in this repo — every problem has a fix!
