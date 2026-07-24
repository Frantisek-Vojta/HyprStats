import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf, Gio
import psutil
import subprocess
import glob
import os


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


def _load_icon(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        return None

    target_size = 22

    if filename.endswith(".svg"):
        import cairosvg
        png_bytes = cairosvg.svg2png(url=path, output_width=target_size, output_height=target_size)
        input_stream = Gio.MemoryInputStream.new_from_data(png_bytes)
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
    elif filename.endswith(".png"):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, target_size, target_size)
    else:
        return None

    return Gtk.Image.new_from_pixbuf(pixbuf)


class HyprStatsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="HyprStats")
        self.set_decorated(False)
        self.set_default_size(500, 520)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)

        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        css_provider = Gtk.CssProvider()
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        css_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_start(25)
        vbox.set_margin_top(15)
        self.add(vbox)

        self.clock_label = Gtk.Label(label="")
        self.clock_label.set_name("clock")
        self.clock_label.set_halign(Gtk.Align.START)
        vbox.pack_start(self.clock_label, False, False, 0)

        self.rows = []
        row_data = [
            ("ram", "ram.svg"),
            ("cpu", "cpu.svg"),
            ("gpu", "gpu.svg"),
            ("disk", "disk.svg"),
            ("temp", None),
        ]
        for name, icon_file in row_data:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            if icon_file:
                image = _load_icon(icon_file)
                if image:
                    hbox.pack_start(image, False, False, 0)
            label = Gtk.Label(label="")
            label.set_name(name)
            label.set_halign(Gtk.Align.START)
            hbox.pack_start(label, False, False, 0)
            vbox.pack_start(hbox, False, False, 0)
            self.rows.append((name, label))

        GLib.timeout_add_seconds(2, self.update_stats)

    def update_stats(self):
        now = __import__("datetime").datetime.now()
        self.clock_label.set_text(now.strftime("%H:%M:%S"))

        mem = psutil.virtual_memory()
        used_gb = mem.used / 1024**3
        total_gb = mem.total / 1024**3
        percent = mem.percent
        self._set_row("ram", f"RAM  {used_gb:.2f} GB / {total_gb:.2f} GB  ({percent}%)")

        cpu_percent = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq()
        freq_text = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        self._set_row("cpu", f"CPU  {cpu_percent}%  ({freq_text})")

        gpu_text = self.get_gpu_info()
        self._set_row("gpu", gpu_text)

        disk = psutil.disk_usage("/")
        disk_used = disk.used / 1024**3
        disk_total = disk.total / 1024**3
        disk_percent = disk.percent
        self._set_row("disk", f"DISK  {disk_used:.1f} GB / {disk_total:.1f} GB  ({disk_percent}%)")

        temp_text = self.get_temperature_info()
        self._set_row("temp", temp_text)

        return True

    def _set_row(self, name, text):
        for n, label in self.rows:
            if n == name:
                label.set_text(text)
                break

    def get_gpu_info(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(", ")
                if len(parts) >= 3:
                    return f"GPU  {parts[0]}%  (VRAM: {parts[1]} MB / {parts[2]} MB)"
        except Exception:
            pass

        for card_path in glob.glob("/sys/class/drm/card*/device"):
            try:
                with open(f"{card_path}/gpu_busy_percent") as f:
                    gpu_percent = f.read().strip()
                with open(f"{card_path}/mem_info_vram_used") as f:
                    vram_used = int(f.read().strip()) / 1024**2
                with open(f"{card_path}/mem_info_vram_total") as f:
                    vram_total = int(f.read().strip()) / 1024**2
                return f"GPU  {gpu_percent}%  (VRAM: {vram_used:.0f} MB / {vram_total:.0f} MB)"
            except Exception:
                continue

        return "GPU: N/A"

    def get_temperature_info(self):
        temps = []

        sensors = psutil.sensors_temperatures()
        if "coretemp" in sensors:
            for entry in sensors["coretemp"]:
                temps.append(f"CPU: {entry.current:.0f}°C")
                break
        elif "k10temp" in sensors:
            for entry in sensors["k10temp"]:
                temps.append(f"CPU: {entry.current:.0f}°C")
                break
        else:
            for path in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
                try:
                    with open(path) as f:
                        raw = f.read().strip()
                        temp_c = int(raw) / 1000
                        if temp_c > 0 and temp_c < 120:
                            temps.append(f"CPU: {temp_c:.0f}°C")
                            break
                except Exception:
                    continue

        for card_path in glob.glob("/sys/class/drm/card*/device/hwmon/hwmon*/temp1_input"):
            try:
                with open(card_path) as f:
                    raw = f.read().strip()
                    temp_c = int(raw) / 1000
                    if temp_c > 0 and temp_c < 120:
                        temps.append(f"GPU: {temp_c:.0f}°C")
                        break
            except Exception:
                continue

        if not temps:
            return "TEMP  N/A"

        return "TEMP  " + " | ".join(temps)


if __name__ == "__main__":
    win = HyprStatsWindow()
    win.show_all()
    Gtk.main()
