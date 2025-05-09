import logging
import os
import keyboard

LOGS_DIR = os.path.abspath("logs")

LOGGER_INITIALIZED = False
def initialize():
    global LOGGER_INITIALIZED
    os.makedirs(LOGS_DIR, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(LOGS_DIR, "app.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    LOGGER_INITIALIZED = True

def get_logger(name: str):
    if not LOGGER_INITIALIZED:
        initialize()
    return logging.getLogger(name)

class KeyPressLogger:
    def __init__(self):
        self.logger = get_logger("KeyPressLogger")
        keyboard.hook(self.callback)

        self.logger.info("KeyPressLogger initialized")

    def callback(self, e: keyboard.KeyboardEvent):
        self.logger.info(f"{e.event_type} {e.name} ({e.scan_code})")
