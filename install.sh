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

# 3. Patch the live Mewline status bar in-place (no bundled copy needed)
if [ -f "$MEWLINE_TARGET" ]; then
    echo -e "${BLUE}--> Mewline detected at $MEWLINE_TARGET.${NC}"

    if grep -q "HyprStatsButton" "$MEWLINE_TARGET"; then
        echo -e "${YELLOW}[!] Mewline status bar already patched, skipping.${NC}"
    else
        if [ ! -f "${MEWLINE_TARGET}.bak" ]; then
            echo -e "${BLUE}--> Creating backup of original status_bar.py...${NC}"
            sudo cp "$MEWLINE_TARGET" "${MEWLINE_TARGET}.bak"
        fi

        echo -e "${BLUE}--> Injecting HyprStats button into Mewline status bar...${NC}"
        sudo python3 - "$MEWLINE_TARGET" <<'PYEOF'
import sys

path = sys.argv[1]
with open(path, "r") as f:
    src = f.read()

if "HyprStatsButton" in src:
    sys.exit(0)

# 1. add imports right after the original cairo import
imports_anchor = "import cairo\n"
extra_imports = (
    "import os\n"
    "import subprocess\n"
    "import cairo\n"
    "from fabric.widgets.button import Button\n"
)
src = src.replace(imports_anchor, extra_imports, 1)

# 2. add the launcher function + button class right before StatusBarBase
class_anchor = "class StatusBarBase:"
injected = '''HYPRSTATS_PATH = os.path.expanduser("~/.config/hyprstats/main.py")


def launch_hyprstats(*_args):
    """Launch the HyprStats widget as a detached process."""
    if not os.path.exists(HYPRSTATS_PATH):
        logger.warning(f"HyprStats not found at {HYPRSTATS_PATH}")
        return
    try:
        subprocess.Popen(["python3", HYPRSTATS_PATH], start_new_session=True)
    except Exception as e:
        logger.error(f"Failed to launch HyprStats: {e}")


class HyprStatsButton(Button):
    """Status bar button that opens the HyprStats widget."""

    def __init__(self, **kwargs):
        super().__init__(
            name="hyprstats-button",
            label="\uf2db",
            tooltip_text="HyprStats",
            on_clicked=launch_hyprstats,
            **kwargs,
        )


''' + class_anchor
src = src.replace(class_anchor, injected, 1)

# 3. add the button into the end_children list, right before PowerButton()
button_anchor = "                    PowerButton(),"
src = src.replace(button_anchor, "                    HyprStatsButton(),\n" + button_anchor, 1)

with open(path, "w") as f:
    f.write(src)

print("patched")
PYEOF
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