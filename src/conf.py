import json
from typing import Literal, Callable

import src.constants as c

class Configuration:
    type FieldType = Literal["fade_duration"] | Literal["window_size_ratio"] | Literal["monitor_conf"]
    type ValueType = int
    type Listener = Callable[[ValueType], None]
    
    __listeners_id: int = 0
    __listeners: dict[FieldType, list[tuple[str, Listener]]] = {}
    _fields_: list[tuple[FieldType, ValueType]] = [
        ("fade_duration", 0.5),
        ("window_size_ratio", 1/8),
        ("monitor_conf", c.E_MONITORCONF.PRIMARY)
    ]

    def __init__(self):
        self.load_from_json()

    def setproperty(self, **kwargs):
        for field_name, default_value in self._fields_:
            setattr(self, field_name, kwargs[field_name] if field_name in kwargs else default_value)

    def getproperty(self):
        return { k: getattr(self, k) if hasattr(self, k) else v for k, v in self._fields_ }

    def load_from_json(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                self.setproperty(**data)
        except FileNotFoundError:
            self.save_to_json()
            self.load_from_json()
    
    def save_to_json(self):
        with open("config.json", "w") as f:
            json.dump(self.getproperty(), f)
    
    def __setattr__(self, name: FieldType, value: ValueType) -> None:
        object.__setattr__(self, name, value)
        self.save_to_json()
    
    def listen(self, name: FieldType, listener: Listener):
        if name not in self.__listeners: self.__listeners[name] = []
        listener_id = f"{name}_{self.__listeners_id}"
        self.__listeners_id += 1
        self.__listeners[name].append((listener_id, listener))
        return listener_id
    
    def forget(self, _id: str):
        attrname = '_'.join(_id.split('_')[:-1])
        self._listeners[attrname] = list(filter(lambda lid, _: lid != _id, self.__listeners[attrname]))
