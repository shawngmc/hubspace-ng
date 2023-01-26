"""A device implementation for devices with subdevices, like CeilingFan + Light"""
from hubspaceng.models.devices.base import BaseDevice

class ComboDevice(BaseDevice):
    """A device implementation for devices with subdevices, like CeilingFan + Light"""
    _children: dict[BaseDevice] = dict()

    def add_child(self, child: BaseDevice):
        """Add a child device for this ComboDevice"""
        self._children[child.id] = child

    @property
    def children(self):
        """Return the list of child devices"""
        return self._children

    def get_unlinked_children(self):
        """Return a list of children that are in the JSON, but no object is linked"""
        all_children = self.device_json['children']
        known_children = self._children.keys()
        missing_children = [i for i in all_children if i not in known_children]
        return missing_children
