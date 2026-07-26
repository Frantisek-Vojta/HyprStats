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
- Transparent purple-themed UI with GTK3 CSS styling
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
- Nerd Font (for terminal icons, optional)

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

The repo includes `install.sh`, which copies the widget to `~/.config/hyprstats`, installs Python dependencies, and - **if [Mewline](https://github.com/meowrch/mewline) by meowrch is detected** - adds a hover button for it directly into Mewline's status bar.

```bash
chmod +x install.sh
./install.sh
```

> ⚠️ **Mewline integration only works with [meowrch/mewline](https://github.com/meowrch/mewline).** The script patches Mewline's own `status_bar.py` in place, so it depends on Mewline's internal file structure - it will not work with other status bars (Waybar, HyDePanel, eww, etc.). If Mewline isn't detected, `install.sh` still installs HyprStats standalone; you can then launch it manually (see [Usage](#usage)).

To undo the Mewline integration and restore the original, unpatched `status_bar.py`:

```bash
./install.sh --restore
```

## Usage

Run the widget manually:

```bash
python main.py
```
---

## Screenshots
#### old version:
![HyprStats screenshot](assets/image.png)

*more screenshots coming soon.*

## Contributing

Pull requests, bug reports, and feature requests are welcome. Feel free to open an issue.

## License

This project is licensed under the MIT License.
