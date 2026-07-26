"""Config loading for HyprStats.

Reads ~/.config/hyprstats/config.json. If it doesn't exist yet, a default
one is created automatically on first run so the user has something to edit.
"""

import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/hyprstats")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "position": {
        # any combination of: top, bottom, left, right
        "anchor": ["top", "right"],
        "margin_top": 50,
        "margin_right": 12,
        "margin_left": 12,
        "margin_bottom": 12,
    },
    # which metrics to show, and in what order.
    # remove an entry to hide that row entirely.
    "rows": ["ram", "cpu", "gpu", "disk", "network"],
    "colors": {
        "ram": "#a78bfa",
        "cpu": "#c084fc",
        "gpu": "#d8b4fe",
        "disk": "#e2ccff",
        "network": "#c084fc",
        "background_start": "rgba(60, 30, 90, 0.45)",
        "background_end": "rgba(30, 15, 45, 0.35)",
        "border": "rgba(200, 160, 255, 0.35)",
    },
    "graph": {
        "history_length": 30,
        "width": 60,
        "height": 22,
    },
    "window": {
        "min_width": 460,
        "font_size": 18,
    },
    "mewline": {
        # icon shown for the HyprStats hover button in the Mewline status bar
        # pick one from https://www.nerdfonts.com/cheat-sheet and paste its code here
        "icon": "\ued2f",
    },
}


def _deep_merge(base, override):
    """Merge override into base, recursively for nested dicts."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except Exception:
            pass
        return dict(DEFAULT_CONFIG)

    try:
        with open(CONFIG_PATH) as f:
            user_config = json.load(f)
        return _deep_merge(DEFAULT_CONFIG, user_config)
    except Exception:
        # broken config.json shouldn't crash the widget — fall back to defaults
        return dict(DEFAULT_CONFIG)