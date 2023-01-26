"""Function class to describe ranged integer settings"""
from hubspaceng.models.functions.base import BaseFunction

class RangeFunction(BaseFunction):
    """Function class to describe ranged integer settings, like 1-100 for brightness"""
    min_value: int
    max_value: int
    step: int
    value: int

    def __init__(self, title: str, account: "HubspaceAccount", raw_fragment: dict):
        super().__init__(title, account, raw_fragment)
        range_desc = raw_fragment['values'][0]['range']
        self.min_value = range_desc['min']
        self.max_value = range_desc['max']
        self.step = range_desc['step']

    def validate_state(self, new_value):
        new_value = int(new_value)

        if new_value < self.min_value:
            # print("too low")
            return False
        if new_value > self.max_value:
            # print("too high")
            return False
        if (new_value - self.min_value) % self.step > 0:
            # print("invalid step")
            return False
        return True
