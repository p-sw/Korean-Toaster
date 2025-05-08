import keyboard as k
from typing import Callable

class KeyboardMonitor:
    type Event = k.KeyboardEvent
    type Hook = Callable[[k.KeyboardEvent], None]

    hooks = []

    def __init__(self):
        self.register_hooks()
    
    def register_hooks(self, *hooks: tuple[int, Hook]):
        registered = []
        for key, callback in hooks:
            hook_id = k.hook_key(key, callback)
            self.hooks.append(hook_id)
            registered.append(hook_id)
        return registered
    
    def unregister_hooks(self, *hooks: list[int]):
        for hook in [i for i in hooks if i in self.hooks]:
            k.unhook(hook)
            self.hooks.remove(hook)
    
    def unregister_all(self):
        for hook in self.hooks:
            k.unhook(hook)
        
        self.hooks = []

    def quit(self):
        self.unregister_all()
