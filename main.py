import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class HyprStatsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="HyprStats")
        self.set_decorated(False)
        self.set_default_size(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)

        self.label = Gtk.Label(label="HyprStats")
        self.fixed.put(self.label, 120, 80)


if __name__ == "__main__":
    win = HyprStatsWindow()
    win.show_all()
    Gtk.main()
