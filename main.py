import glob
import os
import subprocess
import time
from collections import deque
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import GdkPixbuf, Gio, GLib, Gtk, GtkLayerShell
import psutil

ICONS = {
    "ram": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path fill="#a78bfa" d="M128 128C92.7 128 64 156.7 64 192L64 199.4C64 206.2 68.4 212 74.1 215.7C87.3 224.3 96 239.1 96 256C96 272.9 87.3 287.7 74.1 296.3C68.4 300 64 305.8 64 312.6L64 368L576 368L576 312.6C576 305.8 571.6 300 565.9 296.3C552.7 287.7 544 272.9 544 256C544 239.1 552.7 224.3 565.9 215.7C571.6 212 576 206.2 576 199.4L576 192C576 156.7 547.3 128 512 128L128 128zM576 480L576 416L64 416L64 480C64 497.7 78.3 512 96 512L160 512L160 488C160 474.7 170.7 464 184 464C197.3 464 208 474.7 208 488L208 512L296 512L296 488C296 474.7 306.7 464 320 464C333.3 464 344 474.7 344 488L344 512L432 512L432 488C432 474.7 442.7 464 456 464C469.3 464 480 474.7 480 488L480 512L544 512C561.7 512 576 497.7 576 480zM224 224L224 288C224 305.7 209.7 320 192 320C174.3 320 160 305.7 160 288L160 224C160 206.3 174.3 192 192 192C209.7 192 224 206.3 224 224zM352 224L352 288C352 305.7 337.7 320 320 320C302.3 320 288 305.7 288 288L288 224C288 206.3 302.3 192 320 192C337.7 192 352 206.3 352 224zM480 224L480 288C480 305.7 465.7 320 448 320C430.3 320 416 305.7 416 288L416 224C416 206.3 430.3 192 448 192C465.7 192 480 206.3 480 224z"/></svg>',
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path fill="#c084fc" d="M240 88C240 74.7 229.3 64 216 64C202.7 64 192 74.7 192 88L192 128C156.7 128 128 156.7 128 192L88 192C74.7 192 64 202.7 64 216C64 229.3 74.7 240 88 240L128 240L128 296L88 296C74.7 296 64 306.7 64 320C64 333.3 74.7 344 88 344L128 344L128 400L88 400C74.7 400 64 410.7 64 424C64 437.3 74.7 448 88 448L128 448C128 483.3 156.7 512 192 512L192 552C192 565.3 202.7 576 216 576C229.3 576 240 565.3 240 552L240 512L296 512L296 552C296 565.3 306.7 576 320 576C333.3 576 344 565.3 344 552L344 512L400 512L400 552C400 565.3 410.7 576 424 576C437.3 576 448 565.3 448 552L448 512C483.3 512 512 483.3 512 448L552 448C565.3 448 576 437.3 576 424C576 410.7 565.3 400 552 400L512 400L512 344L552 344C565.3 344 576 333.3 576 320C576 306.7 565.3 296 552 296L512 296L512 240L552 240C565.3 240 576 229.3 576 216C576 202.7 565.3 192 552 192L512 192C512 156.7 483.3 128 448 128L448 88C448 74.7 437.3 64 424 64C410.7 64 400 74.7 400 88L400 128L344 128L344 88C344 74.7 333.3 64 320 64C306.7 64 296 74.7 296 88L296 128L240 128L240 88zM224 192L416 192C433.7 192 448 206.3 448 224L448 416C448 433.7 433.7 448 416 448L224 448C206.3 448 192 433.7 192 416L192 224C192 206.3 206.3 192 224 192zM240 240L240 400L400 400L400 240L240 240z"/></svg>',
    "gpu": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#d8b4fe" viewBox="0 0 16 16"><path d="M4 8a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0m7.5-1.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3"/><path d="M0 1.5A.5.5 0 0 1 .5 1h1a.5.5 0 0 1 .5.5V4h13.5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-.5.5H2v2.5a.5.5 0 0 1-1 0V2H.5a.5.5 0 0 1-.5-.5m5.5 4a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M9 8a2.5 2.5 0 1 0 5 0 2.5 2.5 0 0 0 5 0"/><path d="M3 12.5h3.5v1a.5.5 0 0 1-.5.5H3.5a.5.5 0 0 1-.5-.5zm4 1v-1h4v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5"/></svg>',
    "disk": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path fill="#e2ccff" d="M160 144C151.2 144 144 151.2 144 160L144 322C149.1 320.7 154.5 320 160 320L480 320C485.5 320 490.9 320.7 496 322L496 160C496 151.2 488.8 144 480 144L160 144zM144 384L144 480C144 488.8 151.2 496 160 496L480 496C488.8 496 496 488.8 496 480L496 384C496 375.2 488.8 368 480 368L160 368C151.2 368 144 375.2 144 384zM96 384L96 160C96 124.7 124.7 96 160 96L480 96C515.3 96 544 124.7 544 160L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 384zM312 432C312 418.7 322.7 408 336 408C349.3 408 360 418.7 360 432C360 445.3 349.3 456 336 456C322.7 456 312 445.3 312 432zM432 408C445.3 408 456 418.7 456 432C456 445.3 445.3 456 432 456C418.7 456 408 445.3 408 432C408 418.7 418.7 408 432 408z"/></svg>',
    "network": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#c084fc" viewBox="0 0 16 16"><path d="M0 11.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5zm4-3a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5v5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5zm4-3a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5v8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5zm4-3a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5v11a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5z"/></svg>',
}


GRAPH_COLORS = {
    "ram": (0.655, 0.545, 0.980),
    "cpu": (0.753, 0.518, 0.988),
    "gpu": (0.847, 0.706, 0.996),
    "disk": (0.886, 0.800, 1.000),
    "network": (0.753, 0.518, 0.988),
}

GRAPH_HISTORY_LEN = 30


def _load_icon(name):
    svg_data = ICONS.get(name)
    if not svg_data:
        return None
    target_size = 18
    try:
        import cairosvg

        png_bytes = cairosvg.svg2png(
            bytestring=svg_data.encode(),
            output_width=target_size,
            output_height=target_size,
        )
        input_stream = Gio.MemoryInputStream.new_from_data(png_bytes)
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
        return Gtk.Image.new_from_pixbuf(pixbuf)
    except Exception:
        return None


def get_cpu_temperature():
    sensors = psutil.sensors_temperatures()
    if "coretemp" in sensors:
        for entry in sensors["coretemp"]:
            return f"{entry.current:.0f}°C"
    elif "k10temp" in sensors:
        for entry in sensors["k10temp"]:
            return f"{entry.current:.0f}°C"
    else:
        for path in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
            try:
                with open(path) as f:
                    raw = f.read().strip()
                    temp_c = int(raw) / 1000
                    if 0 < temp_c < 120:
                        return f"{temp_c:.0f}°C"
            except Exception:
                continue
    return ""


def get_gpu_temperature():
    for card_path in glob.glob(
        "/sys/class/drm/card*/device/hwmon/hwmon*/temp1_input"
    ):
        try:
            with open(card_path) as f:
                raw = f.read().strip()
                temp_c = int(raw) / 1000
                if 0 < temp_c < 120:
                    return f"{temp_c:.0f}°C"
        except Exception:
            continue
    return ""


class HyprStatsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="HyprStats")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "hyprstats")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_exclusive_zone(self, -1)

        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 50)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 12)

        self.connect("focus-out-event", lambda w, e: Gtk.main_quit())

        self.set_decorated(False)
        self.set_default_size(360, 220)

        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        css_provider = Gtk.CssProvider()
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        if os.path.exists(css_path):
            css_provider.load_from_path(css_path)

        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_name("hyprstats-container")
        vbox.set_margin_start(28)
        vbox.set_margin_end(28)
        vbox.set_margin_top(24)
        vbox.set_margin_bottom(24)
        self.add(vbox)

        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(28)
        self.grid.set_row_spacing(18)
        vbox.pack_start(self.grid, False, False, 0)

        self.cells = {}
        rows = [
            ("ram", "RAM"),
            ("cpu", "CPU"),
            ("gpu", "GPU"),
            ("disk", "DISK"),
            ("network", "NET"),
        ]

        for i, (key, title) in enumerate(rows):
            image = _load_icon(key)
            if image:
                self.grid.attach(image, 0, i, 1, 1)

            lbl_title = Gtk.Label(label=title)
            lbl_title.set_name(key)
            lbl_title.set_halign(Gtk.Align.START)
            self.grid.attach(lbl_title, 1, i, 1, 1)

            lbl_usage = Gtk.Label(label="")
            lbl_usage.set_name(key)
            lbl_usage.set_halign(Gtk.Align.START)
            self.grid.attach(lbl_usage, 2, i, 1, 1)

            lbl_detail = Gtk.Label(label="")
            lbl_detail.set_name(key)
            lbl_detail.set_halign(Gtk.Align.START)
            self.grid.attach(lbl_detail, 3, i, 1, 1)

            lbl_temp = Gtk.Label(label="")
            lbl_temp.set_name(key)
            lbl_temp.set_halign(Gtk.Align.START)
            self.grid.attach(lbl_temp, 4, i, 1, 1)

            graph = Gtk.DrawingArea()
            graph.set_size_request(60, 22)
            graph.set_valign(Gtk.Align.CENTER)
            graph.connect("draw", self._on_draw_graph, key)
            self.grid.attach(graph, 5, i, 1, 1)

            self.cells[key] = {
                "usage": lbl_usage,
                "detail": lbl_detail,
                "temp": lbl_temp,
                "graph": graph,
            }

        self.history = {key: deque([0] * GRAPH_HISTORY_LEN, maxlen=GRAPH_HISTORY_LEN) for key, _ in rows}

        self.prev_net = psutil.net_io_counters()
        self.prev_net_time = time.time()

        self.update_stats()
        GLib.timeout_add_seconds(1, self.update_stats)

    def _on_draw_graph(self, widget, cr, key):
        values = list(self.history[key])
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        if not values or width <= 0 or height <= 0:
            return False

        max_val = max(max(values), 1)
        n = len(values)
        padding = 2
        r, g, b = GRAPH_COLORS.get(key, (0.75, 0.52, 0.99))

        # filled area under the line
        cr.move_to(padding, height - padding)
        for i, v in enumerate(values):
            x = padding + (width - 2 * padding) * i / max(n - 1, 1)
            y = height - padding - (v / max_val) * (height - 2 * padding)
            cr.line_to(x, y)
        cr.line_to(width - padding, height - padding)
        cr.close_path()
        cr.set_source_rgba(r, g, b, 0.18)
        cr.fill()

        # the line itself
        cr.set_line_width(1.6)
        cr.set_source_rgba(r, g, b, 0.9)
        for i, v in enumerate(values):
            x = padding + (width - 2 * padding) * i / max(n - 1, 1)
            y = height - padding - (v / max_val) * (height - 2 * padding)
            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.stroke()

        return False

    def update_stats(self):
        mem = psutil.virtual_memory()
        used_gb = mem.used / 1024**3
        total_gb = mem.total / 1024**3
        self.cells["ram"]["usage"].set_text(f"{mem.percent:.1f}%")
        self.cells["ram"]["detail"].set_text(f"{used_gb:.1f}/{total_gb:.1f}GB")
        self.cells["ram"]["temp"].set_text("")
        self.history["ram"].append(mem.percent)
        self.cells["ram"]["graph"].queue_draw()

        cpu_percent = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq()
        freq_text = f"{cpu_freq.current:.0f}MHz" if cpu_freq else "N/A"
        self.cells["cpu"]["usage"].set_text(f"{cpu_percent:.1f}%")
        self.cells["cpu"]["detail"].set_text(freq_text)
        self.cells["cpu"]["temp"].set_text(get_cpu_temperature())
        self.history["cpu"].append(cpu_percent)
        self.cells["cpu"]["graph"].queue_draw()

        gpu_usage, gpu_vram = self.get_gpu_info()
        self.cells["gpu"]["usage"].set_text(gpu_usage)
        self.cells["gpu"]["detail"].set_text(gpu_vram)
        self.cells["gpu"]["temp"].set_text(get_gpu_temperature())
        try:
            gpu_percent_val = float(gpu_usage.rstrip("%"))
        except ValueError:
            gpu_percent_val = 0
        self.history["gpu"].append(gpu_percent_val)
        self.cells["gpu"]["graph"].queue_draw()

        disk = psutil.disk_usage("/")
        disk_used = disk.used / 1024**3
        disk_total = disk.total / 1024**3
        self.cells["disk"]["usage"].set_text(f"{disk.percent:.1f}%")
        self.cells["disk"]["detail"].set_text(f"{disk_used:.0f}/{disk_total:.0f}GB")
        self.cells["disk"]["temp"].set_text("")
        self.history["disk"].append(disk.percent)
        self.cells["disk"]["graph"].queue_draw()

        curr_net = psutil.net_io_counters()
        curr_time = time.time()
        elapsed = curr_time - self.prev_net_time
        if elapsed > 0:
            down_speed = (curr_net.bytes_recv - self.prev_net.bytes_recv) / elapsed
            up_speed = (curr_net.bytes_sent - self.prev_net.bytes_sent) / elapsed
        else:
            down_speed = 0
            up_speed = 0
        self.prev_net = curr_net
        self.prev_net_time = curr_time

        def fmt_speed(bps):
            if bps >= 1024 * 1024:
                return f"{bps / (1024*1024):.1f}M"
            elif bps >= 1024:
                return f"{bps / 1024:.0f}K"
            else:
                return f"{bps:.0f}B"

        self.cells["network"]["usage"].set_text("")
        self.cells["network"]["detail"].set_text(
            f"↓{fmt_speed(down_speed)} ↑{fmt_speed(up_speed)}"
        )
        self.cells["network"]["temp"].set_text("")
        self.history["network"].append(down_speed)
        self.cells["network"]["graph"].queue_draw()

        return True

    def get_gpu_info(self):
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(", ")
                if len(parts) >= 3:
                    return f"{parts[0]}%", f"{parts[1]}MB"
        except Exception:
            pass

        for card_path in glob.glob("/sys/class/drm/card*/device"):
            try:
                with open(f"{card_path}/gpu_busy_percent") as f:
                    gpu_percent = f.read().strip()
                with open(f"{card_path}/mem_info_vram_used") as f:
                    vram_used = int(f.read().strip()) / 1024**2
                return f"{gpu_percent}%", f"{vram_used:.0f}MB"
            except Exception:
                continue

        return "N/A", ""


if __name__ == "__main__":
    win = HyprStatsWindow()
    win.show_all()
    Gtk.main()