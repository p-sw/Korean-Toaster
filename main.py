import tkinter as tk
from tkinter import ttk
import keyboard
import time
import threading
from PIL import Image
from pystray import MenuItem, Menu, Icon
import ctypes
import ctypes.wintypes
import json

TRANSPARENT_COLOR = "#123456"
BACKGROUND_COLOR = "#333333"

class E_MONITORCONF:
    PRIMARY = 1
    CURSOR = 2
    FOCUSED = 3

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("rcMonitor", ctypes.wintypes.RECT),
        ("rcWork", ctypes.wintypes.RECT),
        ("dwFlags", ctypes.wintypes.DWORD)
    ]

hllDll = ctypes.windll.user32
immDll = ctypes.windll.imm32
IMC_GETCONVERSIONMODE = 0x0001
MONITOR_DEFAULTTONEAREST = 0x00000002
WM_IME_CONTROL = 643
VK_HANGUEL = 0x15
KOREAN_MODE = 1
ENGLISH_MODE = 0
class LanguageDetector:
    key_state = 0
    def update(self):
        hWnd = hllDll.GetForegroundWindow()
        hIMEWnd = immDll.ImmGetDefaultIMEWnd(hWnd)
        conversion_status = hllDll.SendMessageW(hIMEWnd, WM_IME_CONTROL, IMC_GETCONVERSIONMODE, 0)
        self.key_state = conversion_status
    def is_hangul(self):
        return self.key_state == KOREAN_MODE
    def is_english(self):
        return self.key_state == ENGLISH_MODE
    def get_current_language(self):
        return "한" if self.is_hangul() else 'En' if self.is_english() else None
    def get_current_language_str(self):
        return result if (result := self.get_current_language()) is not None else '?'

class RoundFrame(tk.Canvas):
    def __init__(self, parent, radius=20, bg=BACKGROUND_COLOR, **kwargs):
        super().__init__(parent, **kwargs)
        self.radius = radius
        self.bg = bg
        self.configure(bg=TRANSPARENT_COLOR, highlightthickness=0, bd=0)
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

class Configuration:
    fade_duration = 0.5
    window_size_ratio = 1/8
    monitor_conf = E_MONITORCONF.PRIMARY

    @property
    def data(self):
        return {
            "fade_duration": self.fade_duration,
            "window_size_ratio": self.window_size_ratio,
            "monitor_conf": self.monitor_conf,
        }

    def load_from_json(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                self.fade_duration = data.get("fade_duration", self.fade_duration)
                self.window_size_ratio = data.get("window_size_ratio", self.window_size_ratio)
                self.monitor_conf = data.get("monitor_conf", self.monitor_conf)
        except FileNotFoundError:
            self.save_to_json()
    
    def save_to_json(self):
        with open("config.json", "w") as f:
            json.dump(self.data, f)

class App:
    fade_step = 0.02
    fade_timer = None
    fading = False

    hooks = []

    def __init__(self):
        self.conf = Configuration()
        self.conf.load_from_json()

        self.language_detector = LanguageDetector()

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes('-alpha', 0.0)
        self.root.configure(bg=TRANSPARENT_COLOR)
        self.root.attributes('-transparentcolor', TRANSPARENT_COLOR)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.set_root_geometry()

        self.width, self.height = self.screen_width // 8, self.screen_height // 8

        self.frame = RoundFrame(self.root, radius=20, bg=BACKGROUND_COLOR, width=self.width, height=self.height)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.style = ttk.Style()
        self.style.configure("Language.TLabel", font=('Arial', 24, 'bold'), padding=20, foreground='white', background=BACKGROUND_COLOR)
        
        self.label = ttk.Label(self.frame, text=self.language_detector.get_current_language_str(), style="Language.TLabel")
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.register_keyboard_monitor()

        self.setup_tray_icon()
    
    def set_fadeout_speed(self, speed):
        self.conf.fade_duration = speed
        self.conf.save_to_json()
    
    def set_root_geometry(self, screen_x=0, screen_y=0, screen_width=None, screen_height=None):
        if screen_width is None: screen_width = self.screen_width
        if screen_height is None: screen_height = self.screen_height

        y_padding = 50

        width = int(screen_width * self.conf.window_size_ratio)
        height = int(screen_height * self.conf.window_size_ratio)
        x = int(screen_width // 2 - width // 2) + screen_x
        y = int(screen_height - height - y_padding) + screen_y
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def set_window_size(self, size):
        self.conf.window_size_ratio = size
        self.set_root_geometry()
        self.conf.save_to_json()
    
    def set_monitor_conf(self, val):
        self.conf.monitor_conf = val
        self.set_root_geometry()
        self.conf.save_to_json()

    def setup_tray_icon(self):
        image = Image.open("_internal/icon.png")
        menu = (
            MenuItem(
                '창 애니메이션 속도',
                Menu(
                    MenuItem('끄기', lambda: self.set_fadeout_speed(0), radio=True, checked=lambda x: self.conf.fade_duration == 0),
                    MenuItem('0.5초(기본)', lambda: self.set_fadeout_speed(0.5), radio=True, checked=lambda x: self.conf.fade_duration == 0.5, default=True),
                    MenuItem('1초', lambda: self.set_fadeout_speed(1), radio=True, checked=lambda x: self.conf.fade_duration == 1),
                    MenuItem('2초', lambda: self.set_fadeout_speed(2), radio=True, checked=lambda x: self.conf.fade_duration == 2),
                    MenuItem('3초', lambda: self.set_fadeout_speed(3), radio=True, checked=lambda x: self.conf.fade_duration == 3),
                )
            ),
            MenuItem(
                '창 크기',
                Menu(
                    MenuItem('1/4', lambda: self.set_window_size(1/4), radio=True, checked=lambda x: self.conf.window_size_ratio == 1/4),
                    MenuItem('1/6', lambda: self.set_window_size(1/6), radio=True, checked=lambda x: self.conf.window_size_ratio == 1/6),
                    MenuItem('1/8(기본)', lambda: self.set_window_size(1/8), radio=True, default=True, checked=lambda x: self.conf.window_size_ratio == 1/8),
                )
            ),
            MenuItem(
                '다중 모니터 설정',
                Menu(
                    MenuItem('항상 주 모니터에 표시', lambda: self.set_monitor_conf(E_MONITORCONF.PRIMARY), radio=True, checked=lambda x: self.conf.monitor_conf == E_MONITORCONF.PRIMARY, default=True),
                    MenuItem('커서가 있는 모니터에 표시', lambda: self.set_monitor_conf(E_MONITORCONF.CURSOR), radio=True, checked=lambda x: self.conf.monitor_conf == E_MONITORCONF.CURSOR),
                    MenuItem('활성 윈도우가 있는 모니터에 표시', lambda: self.set_monitor_conf(E_MONITORCONF.FOCUSED), radio=True, checked=lambda x: self.conf.monitor_conf == E_MONITORCONF.FOCUSED),
                )
            ),
            MenuItem('설정 다시 불러오기', self.conf.load_from_json),
            MenuItem('종료', self.quit),
        )

        self.icon = Icon("Korean Toaster", image, "KRT", menu)
        self.tray_thread = threading.Thread(target=self.icon.run)
        self.tray_thread.daemon = True
        self.tray_thread.start()
    
    def quit(self):
        self.icon.stop()
        self.root.destroy()
        self.unregister_keyboard_monitor()
    
    def show_popup(self, text):
        if self.fade_timer:
            self.root.after_cancel(self.fade_timer)
        if self.fading:
            self.fading = False
        
        if self.conf.monitor_conf in [E_MONITORCONF.CURSOR, E_MONITORCONF.FOCUSED]:
            minfo = MONITORINFO()
            minfo.cbSize = ctypes.sizeof(MONITORINFO)
            if self.conf.monitor_conf == E_MONITORCONF.CURSOR:
                cursor_pos = ctypes.wintypes.POINT()
                hllDll.GetCursorPos(ctypes.byref(cursor_pos))
                hmonitor = hllDll.MonitorFromPoint(cursor_pos, MONITOR_DEFAULTTONEAREST)
            elif self.conf.monitor_conf == E_MONITORCONF.FOCUSED:
                hwnd = hllDll.GetForegroundWindow()
                hmonitor = hllDll.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
            hllDll.GetMonitorInfoW(hmonitor, ctypes.byref(minfo))
            self.set_root_geometry(
                minfo.rcMonitor.left,
                minfo.rcMonitor.top,
                minfo.rcMonitor.right,
                minfo.rcMonitor.bottom
            )

        self.label.config(text=text)
        self.root.attributes('-alpha', 1.0)

        self.fade_timer = self.root.after(500, self.fade_out)

    def fade_out(self):
        self.fading = True
        steps = int(self.conf.fade_duration / self.fade_step)
        for i in range(steps, -1, -1):
            if not self.fading:
                return
            alpha = i / steps
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(self.fade_step)
    
    def register_keyboard_monitor(self):
        def callback(e: keyboard.KeyboardEvent):
            if e.event_type == 'down':
                time.sleep(0.05) # make sure ime mode is updated before calling SendMessage
                self.language_detector.update()
                if (key := self.language_detector.get_current_language()) is None:
                    return
                self.show_popup(key)

        self.hooks.append(keyboard.hook_key(56, callback)) # right alt
        self.hooks.append(keyboard.hook_key(242, callback)) # hangeul
    
    def unregister_keyboard_monitor(self):
        for hook in self.hooks:
            keyboard.unhook(hook)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()
