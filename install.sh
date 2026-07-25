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
MEWLINE_TARGET="/opt/mewline/src/mewline/widgets/status_bar.py"

echo -e "${BLUE}==> Installing HyprStats...${NC}"

# 1. Deploy project files to ~/.config/hyprstats
echo -e "${BLUE}--> Copying project files to $INSTALL_DIR...${NC}"
mkdir -p "$INSTALL_DIR"
cp -r "$REPO_DIR/"* "$INSTALL_DIR/"
echo -e "${GREEN}[✓] Files successfully deployed to $INSTALL_DIR${NC}"

# 2. Install Python dependencies
if [ -f "$REPO_DIR/requirements.txt" ]; then
    echo -e "${BLUE}--> Installing Python dependencies...${NC}"
    if command -v pip &> /dev/null; then
        pip install -r "$REPO_DIR/requirements.txt" --break-system-packages 2>/dev/null \
            || pip install -r "$REPO_DIR/requirements.txt"
        echo -e "${GREEN}[✓] Python dependencies installed.${NC}"
    else
        echo -e "${YELLOW}[!] pip not found, skipping dependency install. Install requirements.txt manually.${NC}"
    fi
fi

# 3. Patch Mewline status bar if installed
if [ -f "$MEWLINE_TARGET" ]; then
    echo -e "${BLUE}--> Mewline detected at $MEWLINE_TARGET.${NC}"

    if [ ! -f "$REPO_DIR/status_bar.py" ]; then
        echo -e "${RED}[✗] status_bar.py not found in repo, cannot patch Mewline.${NC}"
        echo -e "${YELLOW}    HyprStats was still installed to $INSTALL_DIR — run it manually with:${NC}"
        echo -e "${YELLOW}    python3 $INSTALL_DIR/main.py${NC}"
    else
        # Create a backup of the original status_bar.py if it doesn't exist yet
        if [ ! -f "${MEWLINE_TARGET}.bak" ]; then
            echo -e "${BLUE}--> Creating backup of original status_bar.py...${NC}"
            sudo cp "$MEWLINE_TARGET" "${MEWLINE_TARGET}.bak"
        else
            echo -e "${YELLOW}[!] Backup already exists at ${MEWLINE_TARGET}.bak, skipping backup.${NC}"
        fi

        echo -e "${BLUE}--> Applying HyprStats patch to Mewline status bar...${NC}"
        sudo cp "$REPO_DIR/status_bar.py" "$MEWLINE_TARGET"
        echo -e "${GREEN}[✓] Mewline patched successfully.${NC}"
    fi
else
    echo -e "${YELLOW}[!] Mewline status bar not found at $MEWLINE_TARGET.${NC}"
    echo -e "${YELLOW}    If you're not using Mewline, you can run HyprStats manually via:${NC}"
    echo -e "${YELLOW}    python3 $INSTALL_DIR/main.py${NC}"
fi

# 4. Restart Mewline if running
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