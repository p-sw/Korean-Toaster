import keyboard as k
from typing import Callable

class KeyboardMonitor:
    type Event = k.KeyboardEvent
    type Hook = Callable[[k.KeyboardEvent], None]

    hook_removers: list[Callable[[], None]] = []

    def __init__(self):
        self.register_hooks()
    
    def register_hooks(self, *hooks: tuple[int, Hook]):
        for key, callback in hooks:
            hook_remover = k.hook_key(key, callback)
            self.hook_removers.append(hook_remover)
    
    def unregister_hooks(self, *hooks: list[int]):
        for hook_remover in [i for i in hooks if i in self.hook_removers]:
            hook_remover()
            self.hook_removers.remove(hook_remover)
    
    def unregister_all(self):
        for hook in self.hooks:
            k.unhook(hook)
        
        self.hooks = []

    def quit(self):
        self.unregister_all()
