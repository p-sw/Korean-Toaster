from pystray import MenuItem, Menu, Icon
from PIL import Image
import threading

from src.conf import Configuration
from src.utils import build_resource
from src.logger import get_logger
import src.constants as c

class AppTray:
    def __init__(self, config: Configuration, global_quit):
        self.logger = get_logger("AppTray")
        self.logger.info("Initializing AppTray")

        self.conf = config
        self.global_quit = global_quit
        self.setup_tray_icon()
    
    def set_fadeout_speed(self, speed):
        def _():
            self.logger.info(f"fade_duration to {speed}")
            self.conf.fade_duration = speed
        return _
    
    def set_window_size(self, size):
        def _():
            self.logger.info(f"window_size_ratio to {size}")
            self.conf.window_size_ratio = size
        return _
    
    def set_monitor_conf(self, val):
        def _():
            self.logger.info(f"monitor_conf to {val}")
            self.conf.monitor_conf = val
        return _

    def set_window_lifetime(self, time):
        def _():
            self.logger.info(f"window_lifetime to {time}")
            self.conf.window_lifetime = time
        return _

    def set_initial_alpha(self, alpha):
        def _():
            self.logger.info(f"initial_alpha to {alpha}")
            self.conf.initial_alpha = alpha
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
                '창 시작 투명도',
                Menu(
                    MenuItem('30%', self.set_initial_alpha(0.3), radio=True, checked=lambda x: self.conf.initial_alpha == 0.3),
                    MenuItem('50%', self.set_initial_alpha(0.5), radio=True, checked=lambda x: self.conf.initial_alpha == 0.5),
                    MenuItem('70%', self.set_initial_alpha(0.7), radio=True, checked=lambda x: self.conf.initial_alpha == 0.7),
                    MenuItem('90%', self.set_initial_alpha(0.9), radio=True, checked=lambda x: self.conf.initial_alpha == 0.9),
                    MenuItem('100% (불투명)', self.set_initial_alpha(1.0), radio=True, checked=lambda x: self.conf.initial_alpha == 1.0, default=True),
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
        self.logger.info("AppTray initialized")

    def run(self):
        self.logger.info("Running AppTray")
        self.tray_thread = threading.Thread(target=self.icon.run)
        self.tray_thread.daemon = True
        self.tray_thread.start()
    
    def quit(self):
        self.logger.info("Quitting AppTray")
        self.icon.stop()
