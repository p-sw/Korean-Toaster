import ctypes
import ctypes.wintypes

import src.constants as c

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("rcMonitor", ctypes.wintypes.RECT),
        ("rcWork", ctypes.wintypes.RECT),
        ("dwFlags", ctypes.wintypes.DWORD)
    ]

user32 = ctypes.windll.user32
imm32 = ctypes.windll.imm32

class LanguageDetector:
    key_state = 0
    def update(self):
        hWnd = user32.GetForegroundWindow()
        hIMEWnd = imm32.ImmGetDefaultIMEWnd(hWnd)
        conversion_status = user32.SendMessageW(hIMEWnd, c.WM_IME_CONTROL, c.IMC_GETCONVERSIONMODE, 0)
        self.key_state = conversion_status
    def is_hangul(self):
        return self.key_state == c.KOREAN_MODE
    def is_english(self):
        return self.key_state == c.ENGLISH_MODE
    def get_current_language(self):
        return "가" if self.is_hangul() else 'A' if self.is_english() else None
    def get_current_language_str(self):
        return result if (result := self.get_current_language()) is not None else '?'

def get_monitor_rect(by: c.E_MONITORCONF):
    if by == c.E_MONITORCONF.PRIMARY: return [0, 0, None, None]

    minfo = MONITORINFO()
    minfo.cbSize = ctypes.sizeof(MONITORINFO)

    hmonitor = None
    if by == c.E_MONITORCONF.CURSOR:
        cursor_pos = ctypes.wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(cursor_pos))
        hmonitor = user32.MonitorFromPoint(cursor_pos, c.MONITOR_DEFAULTTONEAREST)
    elif by == c.E_MONITORCONF.FOCUSED:
        hwnd = user32.GetForegroundWindow()
        hmonitor = user32.MonitorFromWindow(hwnd, c.MONITOR_DEFAULTTONEAREST)
    
    if hmonitor is None:
        # failed to get monitor handle
        return [0, 0, None, None]
    
    user32.GetMonitorInfoW(hmonitor, ctypes.byref(minfo))
    return [
        minfo.rcMonitor.left,
        minfo.rcMonitor.top,
        minfo.rcMonitor.right,
        minfo.rcMonitor.bottom,
    ]
