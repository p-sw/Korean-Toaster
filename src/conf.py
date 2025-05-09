import json
from typing import Literal, Callable, cast

import src.constants as c
from src.logger import get_logger

class Configuration:
    type FieldType = \
        Literal["fade_duration"] | \
        Literal["window_lifetime"] | \
        Literal["window_size_ratio"] | \
        Literal["monitor_conf"]
    type ValueType = int | float
    type Listener = Callable[[ValueType], None]
    
    __listeners_id: int = 0
    __listeners: dict[FieldType, list[tuple[str, Listener]]] = {}
    _fields_: list[tuple[FieldType, ValueType]] = [
        ("fade_duration", 0.5),
        ("window_lifetime", 0.5),
        ("window_size_ratio", 1/8),
        ("monitor_conf", c.E_MONITORCONF.PRIMARY)
    ]

    fade_duration: float
    window_lifetime: float
    window_size_ratio: float
    monitor_conf: c.E_MONITORCONF

    def __init__(self):
        self.logger = get_logger("Configuration")
        self.load_from_json()
        self.logger.info("Configuration initialized")

    def setproperty(self, **kwargs):
        for field_name, default_value in self._fields_:
            setattr(self, field_name, kwargs[field_name] if field_name in kwargs else default_value)

    def getproperty(self):
        return { k: getattr(self, k) if hasattr(self, k) else v for k, v in self._fields_ }

    def load_from_json(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                self.logger.info(f"Loaded configuration from {f.name}")
                self.setproperty(**data)
        except FileNotFoundError:
            self.save_to_json()
            self.load_from_json()
    
    def save_to_json(self):
        with open("config.json", "w") as f:
            json.dump(self.getproperty(), f)
            self.logger.info(f"Saved configuration to {f.name}")

    def __setattr__(self, name: str, value: ValueType) -> None:
        object.__setattr__(self, name, value)
        self.save_to_json()
    
    def listen(self, name: FieldType, listener: Listener):
        if name not in self.__listeners: self.__listeners[name] = []
        listener_id = f"{name}_{self.__listeners_id}"
        self.__listeners_id += 1
        self.__listeners[name].append((listener_id, listener))
        self.logger.info(f"Listener {listener_id} added to {name}")
        return listener_id
    
    def forget(self, _id: str):
        attrname = cast(Configuration.FieldType, '_'.join(_id.split('_')[:-1]))
        self.__listeners[attrname] = list(filter(lambda lid: lid[0] != _id, self.__listeners[attrname]))
        self.logger.info(f"Listener {_id} removed from {attrname}")
