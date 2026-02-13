#!/bin/bash
# Universal macOS Script - Adds CDP Port to Antigravity

echo "=== Antigravity CDP Setup ==="
echo ""

IDE_NAME="Antigravity"

# Search for the app
APP_LOCATIONS=(
    "/Applications"
    "$HOME/Applications"
    "/Applications/Utilities"
)

app_path=""
for location in "${APP_LOCATIONS[@]}"; do
    if [ -d "$location" ]; then
        echo "Searching: $location"
        found=$(find "$location" -maxdepth 2 -name "*${IDE_NAME}*.app" -type d 2>/dev/null | head -n1)
        if [ -n "$found" ]; then
            app_path="$found"
            echo "Found: $app_path"
            break
        fi
    fi
done

if [ -z "$app_path" ]; then
    echo ""
    echo "ERROR: Antigravity.app not found in standard locations."
    echo "Please install Antigravity first."
    exit 1
fi

info_plist="$app_path/Contents/Info.plist"

if [ ! -f "$info_plist" ]; then
    echo "ERROR: Info.plist not found at expected location."
    exit 1
fi

echo ""
echo "Checking Info.plist: $info_plist"

# Check if CDP port already exists
if grep -q "remote-debugging-port" "$info_plist"; then
    echo "CDP port already configured in Info.plist"
else
    # Create backup
    backup_plist="${info_plist}.bak"
    cp "$info_plist" "$backup_plist"
    echo "Backup created: $backup_plist"

    # Add CDP port configuration
    # Insert before closing </dict> tag
    sed -i '' '/<\/dict>/i\
    <key>LSArguments<\/key>\
    <array>\
        <string>--remote-debugging-port=9000<\/string>\
    <\/array>
' "$info_plist"

    echo "CDP port added to Info.plist"
fi

echo ""
echo "=== Setup Complete ==="
echo "Please quit and restart Antigravity completely for changes to take effect."
echo ""
echo "To launch with CDP flag temporarily, you can also use:"
echo "  open -n -a \"Antigravity\" --args --remote-debugging-port=9000"
