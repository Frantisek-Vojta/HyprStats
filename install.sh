#!/usr/bin/env bash

set -e

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paths
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.config/hyprstats"
MEWLINE_STATUS_BAR="/opt/mewline/src/mewline/widgets/status_bar.py"

echo -e "${BLUE}==> Installing HyprStats...${NC}"

# 1. Deploy project files to ~/.config/hyprstats
echo -e "${BLUE}--> Copying project files to $INSTALL_DIR...${NC}"
mkdir -p "$INSTALL_DIR"
cp -r "$REPO_DIR/"* "$INSTALL_DIR/"
echo -e "${GREEN}[✓] Files successfully deployed to $INSTALL_DIR${NC}"

# 2. Patch Mewline status bar if installed
if [ -f "$MEWLINE_STATUS_BAR" ]; then
    echo -e "${BLUE}--> Mewline detected at $MEWLINE_STATUS_BAR.${NC}"
    
    # Create a backup of the original status_bar.py if it doesn't exist yet
    if [ ! -f "${MEWLINE_STATUS_BAR}.bak" ]; then
        echo -e "${BLUE}--> Creating backup of original status_bar.py...${NC}"
        sudo cp "$MEWLINE_STATUS_BAR" "${MEWLINE_STATUS_BAR}.bak"
    fi

    echo -e "${BLUE}--> Applying HyprStats patch to Mewline status bar...${NC}"
    sudo cp "$REPO_DIR/status_bar.py" "$MEWLINE_STATUS_BAR"
    echo -e "${GREEN}[✓] Mewline patched successfully.${NC}"
else
    echo -e "${YELLOW}[!] Mewline status bar not found at $MEWLINE_STATUS_BAR.${NC}"
    echo -e "${YELLOW}    If you're not using Mewline, you can run HyprStats manually via:${NC}"
    echo -e "${YELLOW}    python3 ~/.config/hyprstats/main.py${NC}"
fi

# 3. Restart Mewline if running
if pgrep -x "mewline" > /dev/null; then
    echo -e "${BLUE}--> Restarting Mewline...${NC}"
    pkill mewline || true
    sleep 0.5
    hyprctl dispatch exec mewline > /dev/null 2>&1 &
    echo -e "${GREEN}[✓] Mewline restarted successfully.${NC}"
else
    echo -e "${YELLOW}[!] Mewline is not currently running.${NC}"
fi

echo -e "\n${GREEN}✨ HyprStats installation complete!${NC}"