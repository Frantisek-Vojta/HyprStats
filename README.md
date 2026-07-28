<div align="center">

# HyprStats ✨

Custom Linux desktop system monitor widget for Hyprland on Arch Linux.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![GTK3](https://img.shields.io/badge/GTK3-3.24-7FE719?style=flat&logo=gtk&logoColor=white)
![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=arch-linux&logoColor=white)
![Hyprland](https://img.shields.io/badge/Hyprland-58E1FF?style=flat&logo=hyprland&logoColor=black)
![Wayland](https://img.shields.io/badge/Wayland-FFBC00?style=flat&logo=wayland&logoColor=black)
![Meowrch](https://img.shields.io/badge/Meowrch-FCA2A2?style=flat&logo=cat&logoColor=black)

![HyprStats demo](assets/demo.gif)

</div>

---

## Features

- Real-time RAM, CPU, GPU, NET speed and DISK usage monitoring
- Live CPU and GPU temperature readouts
- Small live sparkline graph next to every metric (last ~30 samples)
- Transparent purple-themed UI with GTK3 CSS styling, fully customizable via `config.json`
- Cool icons
- Optional one-click integration into the [Mewline](https://github.com/meowrch/mewline) status bar (hover to open, move away to close)

## Status

This project is in early development.

<div align="center">

![50%](https://progress-bar.xyz/43)

</div>

## Requirements

- Python 3.9+
- GTK3 (PyGObject)
- psutil
- cairosvg
- Nerd Font (for icons)

## Why

Checking system stats on Hyprland usually means opening a terminal and running `htop`, `nvidia-smi`, or `df -h` just to glance at RAM, temps, or disk space — a small but constant interruption. HyprStats removes that friction by putting live stats one hover away, right in your status bar.

**3 main QoL improvements:**

1. **No more terminal round-trips** — RAM, CPU, GPU, disk, and network stats (plus live temps and mini graphs) are visible instantly, without alt-tabbing to a terminal and typing a command.
2. **Zero-click, hover-to-open access** — integrated directly into the [Mewline](https://github.com/meowrch/mewline) status bar: hover the icon to open, move away to close. No extra window to manage or close manually.
3. **Fully configurable without touching code** — colors, position, which metrics show, graph size, and font size are all editable in a plain `config.json`, generated automatically on first run.

## Installation

Install system dependencies (Arch Linux):

```bash
sudo pacman -S python-gobject python-psutil python-cairosvg
```

Clone the repository:

```bash
git clone https://github.com/Frantisek-Vojta/HyprStats.git
cd HyprStats
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Automatic install (`install.sh`)

The repo includes `install.sh`, which copies the widget to `~/.config/hyprstats`, installs Python dependencies, and — **if [Mewline](https://github.com/meowrch/mewline) by meowrch is detected** — adds a hover button for it directly into Mewline's status bar.

```bash
chmod +x install.sh
./install.sh
```

> ⚠️ **Mewline integration only works with [meowrch/mewline](https://github.com/meowrch/mewline).** The script patches Mewline's own `status_bar.py` in place, so it depends on Mewline's internal file structure — it will not work with other status bars (Waybar, HyDePanel, eww, etc.). If Mewline isn't detected, `install.sh` still installs HyprStats standalone; you can then launch it manually (see [Usage](#usage)).

To undo the Mewline integration and restore the original, unpatched `status_bar.py`:

```bash
./install.sh --restore
```

## Usage

Run the widget manually (either from the repo, or from the installed copy):

```bash
python3 ~/.config/hyprstats/main.py
```

If you're using the Mewline integration, just hover over the HyprStats icon in the status bar instead — no manual launch needed.

## Configuration

On first launch, HyprStats automatically creates `~/.config/hyprstats/config.json` with sensible defaults. Edit that file (not anything in the cloned repo) and restart the widget — or Mewline, if integrated — to apply changes. No code editing required.

You can customize:

- **`position`** — which screen edges the widget anchors to (`top`/`bottom`/`left`/`right`) and the margin from each
- **`rows`** — which metrics to show and in what order (remove one, e.g. `"gpu"`, to hide that row entirely)
- **`colors`** — accent color per metric (affects both the text and its graph), plus background and border colors
- **`graph`** — sparkline size and how many samples of history to keep
- **`window`** — overall width and font size
- **`mewline`** — the icon shown for the HyprStats hover button in the Mewline status bar (grab a code from the [Nerd Fonts cheat sheet](https://www.nerdfonts.com/cheat-sheet))

Example:

```json
{
    "position": { "anchor": ["top", "right"], "margin_top": 50, "margin_right": 12 },
    "rows": ["ram", "cpu", "gpu", "disk", "network"],
    "colors": { "ram": "#a78bfa", "cpu": "#c084fc" },
    "graph": { "history_length": 30, "width": 60, "height": 22 },
    "window": { "min_width": 460, "font_size": 18 },
    "mewline": { "icon": "\ued2f" }
}
```

## Screenshots

#### old version:
![HyprStats screenshot](assets/image.png)

*more screenshots coming soon.*

## Contributing

Pull requests, bug reports, and feature requests are welcome. Feel free to open an issue.

## License

This project is licensed under the MIT License.