#!/bin/bash
# LinkedIn Job Applier - Quick Setup Script
# Run this once to get started.

set -e

echo "=========================================="
echo "  LinkedIn Job Applier - Setup"
echo "=========================================="
echo ""

# Check OS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "WARNING: This tool currently only works on macOS."
    echo "The file upload automation uses AppleScript + Chrome."
    echo ""
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found."
    echo "Install: brew install python3"
    exit 1
fi

# Install Python dependencies
echo "[1/4] Installing Python dependencies..."
pip3 install fpdf2 pyyaml --quiet 2>/dev/null || pip install fpdf2 pyyaml --quiet
echo "  Done."

# Check Claude Code
if ! command -v claude &> /dev/null; then
    echo ""
    echo "WARNING: Claude Code CLI not found."
    echo "Install: npm install -g @anthropic-ai/claude-code"
    echo ""
fi

# Check for Kapture MCP configuration
echo ""
echo "[2/4] Checking Kapture MCP server..."
if [ -f "$HOME/.claude/settings.json" ]; then
    if grep -q "kapture" "$HOME/.claude/settings.json" 2>/dev/null; then
        echo "  Kapture MCP found in settings."
    else
        echo "  WARNING: Kapture MCP not found in Claude Code settings."
        echo "  You need to add it. See README.md for instructions."
    fi
else
    echo "  WARNING: No Claude Code settings found."
    echo "  You need to configure Kapture MCP. See README.md for instructions."
fi

# Create profile from template
echo ""
echo "[3/4] Setting up profile..."
if [ -f "config/profile.yaml" ]; then
    echo "  config/profile.yaml already exists. Skipping."
else
    cp config/profile.example.yaml config/profile.yaml
    echo "  Created config/profile.yaml from template."
    echo ""
    echo "  IMPORTANT: Edit config/profile.yaml with your details!"
    echo "  Run: nano config/profile.yaml"
fi

# Make scripts executable
echo ""
echo "[4/4] Setting permissions..."
chmod +x resume/upload_resume.sh
echo "  Done."

# macOS accessibility check
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit config/profile.yaml with your details"
echo "  2. Install Kapture Chrome extension"
echo "  3. Configure Kapture MCP in Claude Code (see README)"
echo "  4. Grant Accessibility permissions (System Settings > Privacy > Accessibility)"
echo "     Add: Terminal / iTerm / your terminal app"
echo ""
echo "Then run:"
echo "  claude"
echo "  > Paste any LinkedIn jobs URL"
echo ""
