import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import psutil
import subprocess
import glob


class HyprStatsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="HyprStats")
        self.set_decorated(False)
        self.set_default_size(300, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)

        self.ram_label = Gtk.Label(label="RAM: loading...")
        self.fixed.put(self.ram_label, 20, 20)

        self.cpu_label = Gtk.Label(label="CPU: loading...")
        self.fixed.put(self.cpu_label, 20, 50)

        self.gpu_label = Gtk.Label(label="GPU: loading...")
        self.fixed.put(self.gpu_label, 20, 80)

        self.disk_label = Gtk.Label(label="Disk: loading...")
        self.fixed.put(self.disk_label, 20, 110)

        GLib.timeout_add_seconds(2, self.update_stats)

    def update_stats(self):
        mem = psutil.virtual_memory()
        used_gb = mem.used / 1024**3
        total_gb = mem.total / 1024**3
        percent = mem.percent
        self.ram_label.set_text(f"RAM: {used_gb:.2f} GB / {total_gb:.2f} GB ({percent}%)")

        cpu_percent = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq()
        freq_text = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        self.cpu_label.set_text(f"CPU: {cpu_percent}% ({freq_text})")

        gpu_text = self.get_gpu_info()
        self.gpu_label.set_text(gpu_text)

        disk = psutil.disk_usage("/")
        disk_used = disk.used / 1024**3
        disk_total = disk.total / 1024**3
        disk_percent = disk.percent
        self.disk_label.set_text(f"Disk: {disk_used:.1f} GB / {disk_total:.1f} GB ({disk_percent}%)")

        return True

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
                    return f"GPU: {parts[0]}% (VRAM: {parts[1]} MB / {parts[2]} MB)"
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
                return f"GPU: {gpu_percent}% (VRAM: {vram_used:.0f} MB / {vram_total:.0f} MB)"
            except Exception:
                continue

        return "GPU: N/A"


if __name__ == "__main__":
    win = HyprStatsWindow()
    win.show_all()
    Gtk.main()
