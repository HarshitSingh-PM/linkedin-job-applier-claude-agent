#!/bin/bash
# Auto-select a file in macOS file dialog via clipboard paste
# Usage: ./upload_resume.sh "/path/to/resume.pdf"
#
# This script waits for a file dialog to appear in Chrome, then uses
# Cmd+Shift+G > paste path > Enter to navigate and select the file.
# Handles paths with spaces correctly by using clipboard instead of keystroke.
#
# Requirements: macOS, Google Chrome, Accessibility permissions for Terminal/iTerm

FILE_PATH="$1"

if [ -z "$FILE_PATH" ]; then
    echo "Usage: $0 <path-to-file>"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

echo "Waiting for file dialog..."
echo "Will select: $FILE_PATH"

# Wait for the Open/upload dialog to appear (up to 15 seconds)
DIALOG_FOUND=false
for i in $(seq 1 30); do
    DIALOG_EXISTS=$(osascript -e '
        tell application "System Events"
            tell process "Google Chrome"
                try
                    if exists sheet 1 of window 1 then
                        return "true"
                    end if
                end try
                return "false"
            end tell
        end tell
    ' 2>/dev/null)

    if [ "$DIALOG_EXISTS" = "true" ]; then
        echo "File dialog detected!"
        DIALOG_FOUND=true
        break
    fi
    sleep 0.5
done

if [ "$DIALOG_FOUND" != "true" ]; then
    echo "ERROR: No file dialog detected after 15 seconds."
    exit 1
fi

# Save current clipboard, set file path to clipboard, paste it
OLD_CLIPBOARD=$(pbpaste 2>/dev/null)

# Use Cmd+Shift+G to open "Go to Folder" and paste the FULL file path
echo "$FILE_PATH" | tr -d '\n' | pbcopy

osascript <<'APPLESCRIPT'
    delay 0.3
    tell application "System Events"
        tell process "Google Chrome"
            -- Open "Go to Folder" sheet
            keystroke "g" using {command down, shift down}
            delay 1.0

            -- Select all existing text in the path field and paste our path
            keystroke "a" using {command down}
            delay 0.2
            keystroke "v" using {command down}
            delay 0.5

            -- Press Go/Enter to navigate
            keystroke return
            delay 1.5

            -- The file should now be selected, press Enter/Open
            keystroke return
            delay 0.3
        end tell
    end tell
APPLESCRIPT

# Restore clipboard
echo "$OLD_CLIPBOARD" | pbcopy 2>/dev/null

echo "Done! File uploaded: $(basename "$FILE_PATH")"
