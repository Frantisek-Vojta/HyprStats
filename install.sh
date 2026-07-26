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

# --restore: put back the original, unpatched Mewline status bar and exit
if [ "$1" = "--restore" ] || [ "$1" = "-r" ]; then
    echo -e "${BLUE}==> Restoring original Mewline status bar...${NC}"
    if [ -f "${MEWLINE_TARGET}.bak" ]; then
        sudo cp "${MEWLINE_TARGET}.bak" "$MEWLINE_TARGET"
        echo -e "${GREEN}[✓] Original status_bar.py restored from backup.${NC}"

        if pgrep -x "mewline" > /dev/null; then
            echo -e "${BLUE}--> Restarting Mewline...${NC}"
            pkill mewline || true
            sleep 0.5
            hyprctl dispatch exec mewline > /dev/null 2>&1 &
            echo -e "${GREEN}[✓] Mewline restarted successfully.${NC}"
        fi
    else
        echo -e "${RED}[✗] No backup found at ${MEWLINE_TARGET}.bak — nothing to restore.${NC}"
        exit 1
    fi
    exit 0
fi

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

    if [ ! -f "${MEWLINE_TARGET}.bak" ]; then
        echo -e "${BLUE}--> Creating backup of original status_bar.py...${NC}"
        sudo cp "$MEWLINE_TARGET" "${MEWLINE_TARGET}.bak"
    fi

    echo -e "${BLUE}--> Restoring pristine status_bar.py before patching...${NC}"
    sudo cp "${MEWLINE_TARGET}.bak" "$MEWLINE_TARGET"

    echo -e "${BLUE}--> Injecting HyprStats button into Mewline status bar...${NC}"
    sudo python3 - "$MEWLINE_TARGET" <<'PYEOF'
import sys

path = sys.argv[1]
with open(path, "r") as f:
    src = f.read()

# 1. add imports right after the original cairo import
imports_anchor = "import cairo\n"
extra_imports = (
    "import os\n"
    "import sys\n"
    "import subprocess\n"
    "import cairo\n"
    "from fabric.widgets.button import Button\n"
)
src = src.replace(imports_anchor, extra_imports, 1)

# 2. add the launcher/stopper functions + button class right before StatusBarBase
class_anchor = "class StatusBarBase:"
injected = '''HYPRSTATS_DIR = os.path.expanduser("~/.config/hyprstats")
HYPRSTATS_PATH = os.path.join(HYPRSTATS_DIR, "main.py")
_hyprstats_proc = None


def _get_hyprstats_icon():
    """Read the mewline button icon from HyprStats' own config.json, live."""
    default_icon = "\\ued2f"
    try:
        sys.path.insert(0, HYPRSTATS_DIR)
        from config import load_config

        cfg = load_config()
        return cfg.get("mewline", {}).get("icon", default_icon)
    except Exception:
        return default_icon


def _start_hyprstats(*_args):
    global _hyprstats_proc
    if not os.path.exists(HYPRSTATS_PATH):
        logger.warning(f"HyprStats not found at {HYPRSTATS_PATH}")
        return
    if _hyprstats_proc is not None and _hyprstats_proc.poll() is None:
        return
    try:
        _hyprstats_proc = subprocess.Popen(
            ["python3", HYPRSTATS_PATH], start_new_session=True
        )
    except Exception as e:
        logger.error(f"Failed to launch HyprStats: {e}")


def _stop_hyprstats(*_args):
    global _hyprstats_proc
    if _hyprstats_proc is not None and _hyprstats_proc.poll() is None:
        try:
            _hyprstats_proc.terminate()
        except Exception as e:
            logger.error(f"Failed to stop HyprStats: {e}")
    _hyprstats_proc = None


class HyprStatsButton(Button):
    """Status bar button that shows the HyprStats widget on hover."""

    def __init__(self, **kwargs):
        super().__init__(
            name="hyprstats-button",
            label=_get_hyprstats_icon(),
            tooltip_text="HyprStats",
            **kwargs,
        )
        self.connect("enter-notify-event", lambda *_a: _start_hyprstats())
        self.connect("leave-notify-event", lambda *_a: _stop_hyprstats())


''' + class_anchor
src = src.replace(class_anchor, injected, 1)

# 3. place the button right after Battery(), before combined_controls
battery_anchor = "                    Battery(),"
src = src.replace(
    battery_anchor,
    battery_anchor + "\n                    HyprStatsButton(),",
    1,
)

with open(path, "w") as f:
    f.write(src)

print("patched")
PYEOF
    echo -e "${GREEN}[✓] Mewline patched successfully.${NC}"
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