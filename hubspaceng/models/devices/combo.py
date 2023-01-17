from .base import BaseDevice

class ComboDevice(BaseDevice):
    children: dict[BaseDevice] = dict()
    
    def __init__(self, id: str, title: str, raw_fragment: dict):
        super().__init__(id, title, raw_fragment)

    def add_child(child: BaseDevice):
        children[child.id] = child