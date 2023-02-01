"""Function class to describe ranged integer settings"""
from dataclasses import dataclass
import json
from typing import Any
import logging

from hubspaceng.models.functions.base import BaseFunction

_LOGGER = logging.getLogger(__name__)
class ColorFunction(BaseFunction):
    """Function class to describe ranged integer settings, like 1-100 for brightness"""
    min_value: int
    max_value: int
    step: int

    def __init__(self, title: str, account: "HubspaceAccount", raw_fragment: dict):
        super().__init__(title, account, raw_fragment)

    def parse_state(self, new_value: Any) -> Any:
        """Parse a new value for this function from the server"""
        if isinstance(new_value, dict):
            color_def = new_value.get('color-rgb')
            red = color_def.get('r')
            green = color_def.get('g')
            blue = color_def.get('b')
            color = ColorValue(red, green, blue)
            return color
        else:
            raise ValueError(f"Received an invalid color def from the server: {new_value}")

    def validate_state(self, new_value: Any) -> bool:
        return new_value is not None and isinstance(new_value, ColorValue)

@dataclass(frozen=True)
class ColorValue:
    """An immutable RGB color object"""
    red: int
    green: int
    blue: int

    def __init__(self, red: int, green: int, blue: int):
        if red < 0 or red > 255:
            raise ValueError(f"Red value {red} out of range 0-255.")
        if green < 0 or green > 255:
            raise ValueError(f"Green value {red} out of range 0-255.")
        if blue < 0 or blue > 255:
            raise ValueError(f"Blue value {red} out of range 0-255.")

        # Use object.__setattr__(self, name, value) since this is a frozen object
        object.__setattr__(self, 'red', red)
        object.__setattr__(self, 'green', green)
        object.__setattr__(self, 'blue', blue)

    def __repr__(self):
        color_dict = dict()
        color_dict["r"] = self.red
        color_dict["g"] = self.green
        color_dict["b"] = self.blue
        parent_dict = dict()
        parent_dict['color-rgb'] = color_dict
        json_str = json.dumps(parent_dict)
        return json_str
