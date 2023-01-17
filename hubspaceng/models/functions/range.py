class RangeFunction:
    """Function class to describe ranged integer settings, like 1-100 for brightness"""
    min_value: int
    max_value: int
    step: int
    value: int

    def __init__(self, id: str, title: str, raw_fragment: dict):
        self.id = id
        self.title = title
        self.raw_fragment = raw_fragment
        self.values = dict()
        range_desc = raw_fragment['values'][0]['range']
        self.min_value = range_desc['min']
        self.max_value = range_desc['max']
        self.step = range_desc['step']

    def update_value(new_value):
        if new_value < self.min and new_value > self.max and (new_value - self.min) % step == 0:
            value = new_value
            print(new_value)
        else:
            raise ValueError(f"{new_value} is not a valid value for {title} ({id})")

    def modify_value(value):
        raise NotImplementedError()

    def get_value():
        return value