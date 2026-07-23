import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import psutil


class HyprStatsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="HyprStats")
        self.set_decorated(False)
        self.set_default_size(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)

        self.ram_label = Gtk.Label(label="RAM: loading...")
        self.fixed.put(self.ram_label, 20, 20)

        GLib.timeout_add_seconds(2, self.update_stats)

    def update_stats(self):
        mem = psutil.virtual_memory()
        used_gb = mem.used / 1024**3
        total_gb = mem.total / 1024**3
        percent = mem.percent
        self.ram_label.set_text(f"RAM: {used_gb:.2f} GB / {total_gb:.2f} GB ({percent}%)")
        return True


if __name__ == "__main__":
    win = HyprStatsWindow()
    win.show_all()
    Gtk.main()
