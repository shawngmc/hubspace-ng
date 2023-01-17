from .base import BaseDevice
from ..functions.base import BaseFunction
from ..functions.category import CategoryFunction

class FanDevice(BaseDevice):
    power: CategoryFunction = None
    comfort_breeze: CategoryFunction = None
    fan_speed: CategoryFunction = None

    def __init__(self, id: str, title: str, raw_fragment: dict):
        super().__init__(id, title, raw_fragment)
        raw_functions = raw_fragment['description']['functions']
        for raw_function in raw_functions:
            if raw_function["functionClass"] == "power" and raw_function["type"] == "category":
                power = CategoryFunction(raw_function['id'], "Power", raw_function)
            elif raw_function["functionClass"] == "comfort-breeze" and raw_function["type"] == "category":
                comfort_breeze = CategoryFunction(raw_function['id'], "Comfort Breeze", raw_function)
            elif raw_function["functionClass"] == "fan-speed" and raw_function["type"] == "category":
                fan_speed = CategoryFunction(raw_function['id'], "Fan Speed", raw_function)

    def turn_on(self):
        self.set_state(power, 'on')

    def turn_off(self):
        self.set_state(power, 'off')

    def is_on(self):
        return self.get_state(power)

    def set_comfort_breeze(self, new_comfort_breeze: str):
        self.set_state(comfort_breeze, new_comfort_breeze)

    def get_comfort_breeze(self):
        return self.get_state(comfort_breeze)

    def set_fan_speed(self, new_fan_speed: str):
        self.set_state(fan_speed, new_fan_speed)

    def get_fan_speed(self):
        return self.get_state(fan_speed)

    def get_state(self, function: BaseFunction):
        if function is None:
            raise NotImplementedError(f"Function is not implemented for device {self.id}")
        else:
            return function.get_state()

    def set_state(self, function: BaseFunction, new_value):
        if function is None:
            raise NotImplementedError(f"Function is not implemented for device {self.id}")
        else:
            function.set_state(new_value)
