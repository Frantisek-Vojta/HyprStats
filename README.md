<div align="center">

# HyprStats

Custom Linux desktop system monitor widget for Hyprland on Arch Linux.



![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![GTK3](https://img.shields.io/badge/GTK3-3.24-7FE719?style=flat&logo=gtk&logoColor=white)
![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=arch-linux&logoColor=white)
![Hyprland](https://img.shields.io/badge/Hyprland-58E1FF?style=flat&logo=hyprland&logoColor=black)


![HyprStats screenshot](assets/image.png)

*more screenshots coming soon.*
</div>

---

## Features

- Real-time RAM, CPU, GPU, and DISK usage monitoring
- Live CPU and GPU temperature readouts
- Transparent purple-themed UI with GTK3 CSS styling
- High-load notifications via notify-send
- Embedded Font Awesome icons rendered with cairosvg

## Status

This project is in early development. 

<div align="center">

![50%](https://progress-bar.xyz/18)

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

## Usage

Run the widget:

```bash
python main.py
```

## Contributing

Pull requests, bug reports, and feature requests are welcome. Feel free to open an issue.

## License

This project is licensed under the MIT License.
