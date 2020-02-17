# Copyright (c) 2020 Jeffrey A. Webb

from wumps import Attribute, Entity

from collections import OrderedDict

class Interface(Entity):
    _attributes = (
        Attribute("ports", OrderedDict, element="port"),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        for p_name, p in self.ports.items():
            p.name = p_name

class Implementation(Entity):
    _attributes = (
        Attribute("interface", Interface),
    )

class Instance(Entity):
    _attributes = (
        Attribute("interface", Interface),
        Attribute("implementation", Implementation),
    )

class Connection(Entity):
    _attributes = (
        Attribute("source"),
        Attribute("sink"),
    )
        
class Hierarchy(Implementation):
    _attributes = (
        Attribute("subcomponents", OrderedDict, element="subcomponent"),
        Attribute("connections", list, element="connection"),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        for c_name, c in self.subcomponents.items():
            c.name = c_name
