import tkinter
import tkinter.font
import tkinter.ttk
import time

from src.conf import Configuration
from src.cpp import get_monitor_rect
from src.logger import get_logger
import src.constants as c

class RoundFrame(tkinter.Canvas):
    def __init__(self, parent, radius=20, bg=c.BACKGROUND_COLOR, **kwargs):
        super().__init__(parent, **kwargs)
        self.radius = radius
        self.bg = bg
        self.configure(bg=c.TRANSPARENT_COLOR, highlightthickness=0, bd=0)
        self.bind("<Configure>", self._draw_rounded_rect)

    def _draw_rounded_rect(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        self.create_rounded_rect(0, 0, width, height, self.radius, fill=self.bg)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

class AppUI:
    fade_step = 0.02
    fade_timer = None
    fading = False

    conf_listeners = []

    def __init__(self, config: Configuration, initial: str):
        self.logger = get_logger("AppUI")
        self.logger.info("Initializing AppUI")

        self.conf = config
        self.conf_listeners.append(self.conf.listen("window_size_ratio", lambda _: self.update_geometry()))
        self.conf_listeners.append(self.conf.listen("monitor_conf", lambda _: self.update_geometry()))

        self.root = tkinter.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0)
        self.root.configure(bg=c.TRANSPARENT_COLOR)
        self.root.attributes('-transparentcolor', c.TRANSPARENT_COLOR)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.logger.info(f"Screen size: {self.screen_width}x{self.screen_height}")

        self.update_geometry()

        self.width, self.height = int(self.screen_width * self.conf.window_size_ratio), int(self.screen_height * self.conf.window_size_ratio)

        self.frame = RoundFrame(self.root, radius=40, bg=c.BACKGROUND_COLOR, width=self.width, height=self.height)
        self.frame.pack(expand=True, fill=tkinter.BOTH)

        pretendard = tkinter.font.Font(family='Pretendard', size=24, weight='normal')

        self.style = tkinter.ttk.Style()
        self.style.configure("Language.TLabel", font=pretendard, padding=20, foreground='white', background=c.BACKGROUND_COLOR)
        
        self.label = tkinter.ttk.Label(self.frame, text=initial, style="Language.TLabel")
        self.label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.logger.info("AppUI initialized")

    def update_geometry(self, screen_x=0, screen_y=0, screen_rx=None, screen_ry=None):
        if screen_rx is None: screen_width = self.screen_width
        else: screen_width = screen_rx - screen_x
        if screen_ry is None: screen_height = self.screen_height
        else: screen_height = screen_ry - screen_y

        y_padding = 50

        width = int(screen_width * self.conf.window_size_ratio)
        height = int(screen_height * self.conf.window_size_ratio)
        x = int(screen_width // 2 - width // 2) + screen_x
        y = int(screen_height - height - y_padding) + screen_y
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.logger.info(f"Updated geometry: {width}x{height}+{x}+{y}, screen_anchor: [{screen_x}, {screen_y}]")

    def show_popup(self, text):
        if self.fade_timer:
            self.root.after_cancel(self.fade_timer)
        if self.fading:
            self.fading = False
        
        self.update_geometry(*get_monitor_rect(self.conf.monitor_conf))

        self.label.config(text=text)
        self.root.attributes('-alpha', 1.0)

        self.fade_timer = self.root.after(int(self.conf.window_lifetime * 1000), self.fade_out)

    def fade_out(self):
        if self.conf.fade_duration == 0:
            self.root.attributes('-alpha', 0)
            self.root.update()
            return

        self.fading = True
        steps = int(self.conf.fade_duration / self.fade_step)
        for i in range(steps, -1, -1):
            if not self.fading:
                return
            alpha = i / steps
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(self.fade_step)
        self.fading = False

    def run(self):
        self.logger.info("Running AppUI")
        self.root.mainloop()
    
    def quit(self):
        self.logger.info("Quitting AppUI")
        self.root.destroy()
