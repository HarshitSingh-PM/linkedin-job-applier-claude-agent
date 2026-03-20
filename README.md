# LinkedIn Job Applier - Claude Code Agent

An autonomous AI agent that applies to LinkedIn jobs for you. Give it a LinkedIn jobs search URL and walk away - it reads every job description, tailors your resume for each one, uploads it, fills out the application form, and submits. Fully hands-free.

## What It Does

1. Opens your LinkedIn jobs search URL in Chrome
2. Scans all visible job listings
3. Reads each job description and filters out irrelevant ones
4. For each relevant job:
   - Tailors your resume to match the JD (keywords, skills, bullet rewriting)
   - Generates a professional 2-page PDF
   - Uploads the tailored resume to LinkedIn (automated file dialog handling)
   - Fills all Easy Apply form fields (contact, salary, experience questions, etc.)
   - Submits the application
5. Prints a summary of all applications

## Requirements

| Requirement | Details |
|-------------|---------|
| **OS** | macOS (file upload uses AppleScript + Chrome) |
| **Browser** | Google Chrome |
| **Claude Code** | [Install](https://docs.anthropic.com/en/docs/claude-code/overview) - Anthropic's CLI |
| **Kapture** | Chrome extension + MCP server for browser automation |
| **Python 3** | With `fpdf2` and `pyyaml` packages |
| **Accessibility** | Terminal app must have macOS Accessibility permission |

## Setup (5 minutes)

### Step 1: Clone and install

```bash
git clone https://github.com/HarshitSingh-PM/linkedin-job-applier-claude-agent.git
cd linkedin-job-applier-claude-agent
bash setup.sh
```

### Step 2: Fill in your profile

Edit `config/profile.yaml` with your details - name, experience, metrics, skills, education, and application defaults. This is what the agent uses to tailor resumes and fill forms.

```bash
nano config/profile.yaml
```

The file is heavily commented - just follow the template. Key sections:
- **Personal info**: name, email, phone, location
- **Application defaults**: salary expectations, notice period, sponsorship needs
- **Experience**: your roles with REAL metrics (the agent reframes these per JD)
- **Skills**: grouped by category (the agent picks relevant ones per JD)
- **Education & certifications**

### Step 3: Install the Kapture Chrome extension

1. Install [Kapture](https://chromewebstore.google.com/detail/kapture/gidnhmdkfgcaopfgiaenpdbmkjhmbijf) from Chrome Web Store
2. Pin it to your toolbar
3. Click the Kapture icon and ensure it shows "Connected"

### Step 4: Configure Kapture MCP in Claude Code

Add the Kapture MCP server to your Claude Code settings:

```bash
claude mcp add kapture npx -y @anthropic-ai/kapture-mcp@latest --chrome
```

Or manually add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "kapture": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/kapture-mcp@latest", "--chrome"]
    }
  }
}
```

### Step 5: Grant macOS Accessibility permission

The file upload automation needs to control Chrome via AppleScript:

1. Open **System Settings** > **Privacy & Security** > **Accessibility**
2. Add your terminal app (Terminal, iTerm2, Warp, etc.)
3. Toggle it ON

### Step 6: Log into LinkedIn

Open Chrome and make sure you're logged into LinkedIn. The agent uses your existing session.

## Usage

```bash
cd linkedin-job-applier-claude-agent
claude
```

Then just paste a LinkedIn jobs search URL:

```
https://www.linkedin.com/jobs/search/?keywords=product%20manager&f_AL=true&geoId=103644278&sortBy=R
```

The agent will start scanning and applying automatically. No further input needed.

### Tips for LinkedIn URLs

- Use **Easy Apply** filter (`f_AL=true`) - the agent only works with Easy Apply jobs
- Use **Past 24 hours** filter (`f_TPR=r86400`) to find fresh listings
- Set your preferred **location** and **experience level** filters
- The URL from your LinkedIn search bar works as-is

### Example

```
> https://www.linkedin.com/jobs/search/?keywords=senior%20product%20manager&f_AL=true&f_TPR=r86400&geoId=103644278

Scanning jobs...
[1/8] Applied: Senior PM - AI at TechCorp -- Resume: TechCorp_tailored.pdf
[2/8] Applied: Product Manager at StartupXYZ -- Resume: StartupXYZ_tailored.pdf
[3/8] SKIPPED: PM (German required) at Deutsche Bank -- Reason: Language mismatch
...

=== APPLICATION SUMMARY ===
Total jobs scanned: 12
Applications submitted: 8
Skipped: 4
```

## How It Works

### Architecture

```
You paste URL
    |
    v
Claude Code (CLAUDE.md)
    |
    v
job-applier agent (.claude/agents/job-applier.md)
    |
    |-- Reads: config/profile.yaml (your info)
    |-- Reads: skills/resume-tailor.md (tailoring rules)
    |-- Uses: Kapture MCP (browser automation)
    |-- Uses: resume/generate_pdf.py (PDF generation)
    +-- Uses: resume/upload_resume.sh (macOS file dialog automation)
```

### Resume Tailoring

For each job, the agent:
1. Reads the full job description from LinkedIn
2. Identifies key requirements, skills, and domain focus
3. Rewrites your resume bullets using your REAL metrics from `profile.yaml`
4. Matches skills section to JD requirements
5. Generates a clean 2-page PDF

The agent never fabricates metrics - it reframes your actual achievements to match each JD's domain and keywords.

### File Upload Automation

LinkedIn's file upload uses a native OS file dialog (not a web form), which can't be controlled via browser automation alone. The `upload_resume.sh` script solves this:

1. Waits for Chrome's file dialog to appear (via AppleScript polling)
2. Opens the "Go to Folder" sheet (Cmd+Shift+G)
3. Pastes the file path via clipboard
4. Presses Enter to select the file

This requires Chrome to be the frontmost app, which the agent handles automatically.

## Project Structure

```
linkedin-job-applier-claude-agent/
|-- CLAUDE.md                          # Entry point - tells Claude what to do
|-- setup.sh                           # One-time setup script
|-- config/
|   |-- profile.example.yaml           # Template (committed)
|   +-- profile.yaml                   # Your profile (gitignored)
|-- skills/
|   +-- resume-tailor.md               # Resume tailoring methodology
|-- resume/
|   |-- generate_pdf.py                # PDF resume generator
|   |-- upload_resume.sh               # macOS file dialog automation
|   +-- output/                        # Generated PDFs land here (gitignored)
+-- .claude/
    +-- agents/
        +-- job-applier.md             # The autonomous agent definition
```

## Customization

### Adjusting form defaults

Edit the `application_defaults` section in `config/profile.yaml`:

```yaml
application_defaults:
  salary_current: 120000
  salary_expected: 150000
  notice_period: "1 month"
  requires_sponsorship: true
  willing_to_relocate: false
```

### Changing resume style

Edit `resume/generate_pdf.py` to adjust fonts, margins, spacing, and layout. The `ResumePDF` class controls all formatting.

### Modifying tailoring rules

Edit `skills/resume-tailor.md` to change how the agent rewrites bullets, selects skills, and structures the resume.

## Limitations

- **macOS only** - The file upload automation uses AppleScript. PRs welcome for Linux/Windows support.
- **Chrome only** - Kapture currently supports Chrome (and Chromium-based browsers).
- **Easy Apply only** - External application links are not supported.
- **English UI** - LinkedIn must be in English for selectors to work.
- **Rate limits** - LinkedIn may flag accounts that apply too rapidly. Consider spacing out your job search URLs.

## Troubleshooting

### "No file dialog detected after 15 seconds"
- Chrome wasn't the active app. The agent retries automatically, but make sure no other app is stealing focus.
- Ensure Accessibility permissions are granted to your terminal.

### "Element not found" errors
- LinkedIn may have updated their CSS classes. Open an issue with the screenshot.
- The agent takes screenshots at each step for debugging.

### Profile not loading
- Make sure `config/profile.yaml` exists (not just the `.example` file)
- Check YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('config/profile.yaml'))"`

### Resume is more than 2 pages
- Reduce `bullet_count` for older roles in your profile
- Shorten metrics descriptions
- Reduce number of skills

## Contributing

PRs welcome! Key areas that need help:
- **Linux/Windows support** for file upload automation
- **Additional browser support** beyond Chrome
- **Form field handling** for new question types LinkedIn adds
- **Multi-language support** for non-English LinkedIn UIs

## License

MIT

## Credits

Built with:
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) by Anthropic
- [Kapture MCP](https://www.npmjs.com/package/@anthropic-ai/kapture-mcp) for browser automation
- [fpdf2](https://py-pdf.github.io/fpdf2/) for PDF generation
