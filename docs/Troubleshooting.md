# Troubleshooting Guide

## Common Issues

### No Provider Configured

**Error:**
```
❌ Error: No AI provider configured
```

**Solution:** Set credentials for either provider
```bash
# For Gemini (easier)
export GOOGLE_API_KEY='your-key'

# OR for Vertex (enterprise)
export GOOGLE_CLOUD_PROJECT='your-project-id'
gcloud auth application-default login
```

---

### Vertex AI Project Not Set

**Error:**
```
❌ Error: Vertex provider not configured
GOOGLE_CLOUD_PROJECT environment variable not set
```

**Solution:** Configure Vertex AI
```bash
export LABGENIE_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT='your-project-id'
gcloud auth application-default login
```

---

### Rate Limiting Issues

**Error:**
```
❌ Error: Resource exhausted (quota exceeded)
```

**Solution:**
- **For Gemini API**: Get additional API keys and rotate them
- **For Vertex AI**: Request quota increase in GCP Console

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
ModuleNotFoundError: No module named 'google.generativeai'
```

**Solution:** Install dependencies
```bash
# Activate virtual environment if using one
source venv/bin/activate

# Install all dependencies
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

**Solution:** Upgrade Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10

# macOS (with Homebrew)
brew install python@3.10

# Verify version
python3 --version
```

---

## Debug Mode

If you encounter issues, enable debug mode for detailed logging:

```bash
python labgenie.py --debug
```

This will show:
- Real-time action tracking
- Agent response details
- Timing information
- Error stack traces

Debug logs are also saved to `logs/{run_id}/` for later analysis.

---

## Getting Help

If you encounter an issue not listed here:

1. **Check the logs**: Look in `logs/` and `logs/agent_errors/` for detailed error messages
2. **Review the documentation**: See `docs/Architecture.md` for system details
3. **Check your configuration**: Verify API keys and environment variables
4. **Test with a known URL**: Try a simple, public vulnerability write-up first

---

## Common Tips

- **First time setup**: Always run `setup.sh` first
- **API Keys**: Store them in `.env` file instead of exporting each time
- **Virtual Environment**: Use `venv` to avoid dependency conflicts
- **Provider Selection**: Gemini API is easier for beginners, Vertex AI for enterprise
- **Network Issues**: Some corporate networks block AI APIs - try from a different network
