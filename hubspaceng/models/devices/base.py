class BaseDevice:
    id: str
    title: str
    raw_fragment: dict

    def __init__(self, id: str, title: str, raw_fragment: dict):
        self.id = id
        self.title = title
        self.raw_fragment = raw_fragment
