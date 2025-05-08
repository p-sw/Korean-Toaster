from pystray import MenuItem, Menu, Icon
from PIL import Image
import threading

from src.conf import Configuration
from src.utils import build_resource
import src.constants as c

class AppTray:
    def __init__(self, config: Configuration, global_quit):
        self.conf = config
        self.global_quit = global_quit
        self.setup_tray_icon()
    
    def set_fadeout_speed(self, speed):
        def _():
            self.conf.fade_duration = speed
        return _
    
    def set_window_size(self, size):
        def _():
            self.conf.window_size_ratio = size
        return _
    
    def set_monitor_conf(self, val):
        def _():
            self.conf.monitor_conf = val
        return _

    def set_window_lifetime(self, time):
        def _():
            self.conf.window_lifetime = time
        return _

    def setup_tray_icon(self):
        image = Image.open(build_resource("icon.png"))
        menu = (
            MenuItem(
                '창 유지 시간',
                Menu(
                    MenuItem('0초', self.set_window_lifetime(0), radio=True, checked=lambda x: self.conf.window_lifetime == 0),
                    MenuItem('0.5초', self.set_window_lifetime(0.5), radio=True, checked=lambda x: self.conf.window_lifetime == 0.5, default=True),
                    MenuItem('1초', self.set_window_lifetime(1), radio=True, checked=lambda x: self.conf.window_lifetime == 1),
                    MenuItem('2초', self.set_window_lifetime(2), radio=True, checked=lambda x: self.conf.window_lifetime == 2),
                    MenuItem('3초', self.set_window_lifetime(3), radio=True, checked=lambda x: self.conf.window_lifetime == 3),
                )
            ),
            MenuItem(
                '창 애니메이션 속도',
                Menu(
                    MenuItem('끄기', self.set_fadeout_speed(0), radio=True, checked=lambda x: self.conf.fade_duration == 0),
                    MenuItem('0.5초', self.set_fadeout_speed(0.5), radio=True, checked=lambda x: self.conf.fade_duration == 0.5, default=True),
                    MenuItem('1초', self.set_fadeout_speed(1), radio=True, checked=lambda x: self.conf.fade_duration == 1),
                    MenuItem('2초', self.set_fadeout_speed(2), radio=True, checked=lambda x: self.conf.fade_duration == 2),
                    MenuItem('3초', self.set_fadeout_speed(3), radio=True, checked=lambda x: self.conf.fade_duration == 3),
                )
            ),
            MenuItem(
                '창 크기',
                Menu(
                    MenuItem('1/4', self.set_window_size(1/4), radio=True, checked=lambda x: self.conf.window_size_ratio == 1/4),
                    MenuItem('1/6', self.set_window_size(1/6), radio=True, checked=lambda x: self.conf.window_size_ratio == 1/6),
                    MenuItem('1/8', self.set_window_size(1/8), radio=True, default=True, checked=lambda x: self.conf.window_size_ratio == 1/8),
                )
            ),
            MenuItem(
                '다중 모니터 설정',
                Menu(
                    MenuItem('항상 주 모니터에 표시', self.set_monitor_conf(c.E_MONITORCONF.PRIMARY), radio=True, checked=lambda x: self.conf.monitor_conf == c.E_MONITORCONF.PRIMARY, default=True),
                    MenuItem('커서가 있는 모니터에 표시', self.set_monitor_conf(c.E_MONITORCONF.CURSOR), radio=True, checked=lambda x: self.conf.monitor_conf == c.E_MONITORCONF.CURSOR),
                    MenuItem('활성 윈도우가 있는 모니터에 표시', self.set_monitor_conf(c.E_MONITORCONF.FOCUSED), radio=True, checked=lambda x: self.conf.monitor_conf == c.E_MONITORCONF.FOCUSED),
                )
            ),
            MenuItem('설정 다시 불러오기', self.conf.load_from_json),
            MenuItem('종료', self.global_quit),
        )

        self.icon = Icon("Korean Toaster", image, "KRT", menu)
    
    def run(self):
        self.tray_thread = threading.Thread(target=self.icon.run)
        self.tray_thread.daemon = True
        self.tray_thread.start()
    
    def quit(self):
        self.icon.stop()
