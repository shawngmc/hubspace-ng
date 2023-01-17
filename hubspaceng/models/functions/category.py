class CategoryFunction:
    """Function class to describe discretely named settings, like on/off for power or 3000K/4000K/5700K for color temp"""
    values: dict
    value: str

    def __init__(self, id: str, title: str, raw_fragment: dict):
        self.id = id
        self.title = title
        self.raw_fragment = raw_fragment
        self.values = dict()
        for value_option in raw_fragment['values']:
            name = value_option['name']
            value = value_option['deviceValues'][0]['value']
            self.values[name] = value

    def update_value(new_value):
        if new_value in values.keys():
            value = new_value
            print(new_value)
        else:
            raise ValueError(f"{new_value} is not a valid state for {title} ({id})")

    def modify_value(new_value):
        raise NotImplementedError()

    def get_value():
        return state
