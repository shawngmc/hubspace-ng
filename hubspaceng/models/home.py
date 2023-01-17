from .room import Room

class Home:
    id: str
    title: str
    rooms: dict[Room]
    raw_fragment: dict

    def __init__(self, id: str, title: str, raw_fragment: dict):
        self.id = id
        self.title = title
        self.rooms = dict()
        self.raw_fragment = raw_fragment

    def add_room(room: Room):
        rooms[room.id] = room