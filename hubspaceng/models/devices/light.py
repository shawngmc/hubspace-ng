from .base import BaseDevice
from ..functions.base import BaseFunction
from ..functions.category import CategoryFunction
from ..functions.range import RangeFunction

class LightDevice(BaseDevice):
    brightness: RangeFunction = None
    power: CategoryFunction = None
    color_temp: CategoryFunction = None
    
    def __init__(self, id: str, title: str, raw_fragment: dict):
        super().__init__(id, title, raw_fragment)
        raw_functions = raw_fragment['description']['functions']
        for raw_function in raw_functions:
            if raw_function["functionClass"] == "color-temperature" and raw_function["type"] == "category":
                color_temp = CategoryFunction(raw_function['id'], "Color Temperature", raw_function)
            elif raw_function["functionClass"] == "power" and raw_function["type"] == "category":
                power = CategoryFunction(raw_function['id'], "Power", raw_function)
            elif raw_function["functionClass"] == "brightness" and raw_function["type"] == "numeric":
                brightness = RangeFunction(raw_function['id'], "Brightness", raw_function)

    def turn_on(self):
        self.set_state(power, 'on')

    def turn_off(self):
        self.set_state(power, 'off')

    def is_on(self):
        return self.get_state(power)

    def set_brightness(self, new_brightness: int):
        self.set_state(brightness, new_brightness)

    def get_brightness(self):
        return self.get_state(brightness)

    def set_color_temp(self, new_color_temp: str):
        self.set_state(color_temp, new_color_temp)

    def get_color_temp(self):
        return self.get_state(color_temp)

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