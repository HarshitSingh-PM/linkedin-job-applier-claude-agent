# LinkedIn Job Applier - Claude Code Agent

When the user provides a LinkedIn jobs search URL (any URL containing `linkedin.com/jobs`), spawn the `job-applier` agent with the URL. The agent handles everything autonomously.

## Quick Reference

```
# User pastes a URL like:
https://www.linkedin.com/jobs/search/?keywords=product%20manager&f_AL=true&...

# You spawn:
Agent(subagent_type="job-applier", prompt="Apply to jobs from: <URL>")
```

## Setup Check
Before spawning the agent, verify `config/profile.yaml` exists. If not, tell the user to run setup first.

## Requirements
- macOS (for file upload automation)
- Google Chrome with [Kapture extension](https://chromewebstore.google.com/detail/kapture/gidnhmdkfgcaopfgiaenpdbmkjhmbijf)
- Claude Code with Kapture MCP server configured
- Python 3 with `fpdf2` and `pyyaml` packages
