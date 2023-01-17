from .devices.base import BaseDevice

class Room:
    id: str
    title: str
    devices: dict[BaseDevice]
    raw_fragment: dict

    def __init__(self, id: str, title: str, raw_fragment: dict):
        self.id = id
        self.title = title
        self.devices = dict()
        self.raw_fragment = raw_fragment

    def add_device(device: BaseDevice):
        devices[device.id] = device