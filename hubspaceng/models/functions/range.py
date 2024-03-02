"""Function class to describe ranged integer settings"""
import logging

from hubspaceng.models.functions.base import BaseFunction

_LOGGER = logging.getLogger(__name__)
class RangeFunction(BaseFunction):
    """Function class to describe ranged integer settings, like 1-100 for brightness"""
    min_value: int
    max_value: int
    step: int

    def __init__(self, title: str, account: "HubspaceAccount", raw_fragment: dict):
        super().__init__(title, account, raw_fragment)
        range_desc = raw_fragment['values'][0]['range']
        self.min_value = range_desc['min']
        self.max_value = range_desc['max']
        self.step = range_desc['step']

    def validate_state(self, new_value) -> bool:
        new_value = int(new_value)

        if new_value < self.min_value:
            _LOGGER.debug(f"Value of {new_value} is lower than min value {self.min_value}")
            return False
        if new_value > self.max_value:
            _LOGGER.debug(f"Value of {new_value} is higher than max value {self.max_value}")
            return False
        if (new_value - self.min_value) % self.step > 0:
            _LOGGER.debug(f"Value of {new_value} is not a step {self.step} from min value {self.min_value}")
            return False
        return True
