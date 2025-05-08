import time
import pyglet

from src.ui import AppUI
from src.tray import AppTray
from src.utils import build_resource
from src.conf import Configuration
from src.cpp import LanguageDetector
from src.keyboard import KeyboardMonitor

import src.constants as c

pyglet.font.add_file(build_resource("Pretendard-Regular.otf"))

class AppConductor:
    def __init__(self):
        self.conf = Configuration()
        self.language_detector = LanguageDetector()

        self.ui = AppUI(self.conf, initial=self.language_detector.get_current_language_str())
        self.tray = AppTray(self.conf, global_quit=self.quit)
        self.keyboard = KeyboardMonitor()

        self.keyboard.register_hooks(
            (c.K_ALT, self.hangeul_handler),
            (c.K_HANGEUL, self.hangeul_handler),
        )
    
    def quit(self):
        self.tray.quit()
        self.ui.quit()
        self.keyboard.unregister_all()
    
    def hangeul_handler(self, e: KeyboardMonitor.Event):
        if e.name in ['alt', 'left alt']: return # ignoring left alt
        if e.event_type == 'down':
            time.sleep(0.05) # make sure ime mode is updated before calling SendMessage
            self.language_detector.update()
            if (key := self.language_detector.get_current_language()) is None:
                return
            self.ui.show_popup(key)

    def run(self):
        self.tray.run()
        self.ui.run()

app = AppConductor()
app.run()
