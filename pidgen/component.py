# Copyright (c) 2020 Jeffrey A. Webb

from wumps import Attribute, Entity, elements

# Should be in Tydl module
class Type(Entity):
    _attributes = ()
    
class Port(Entity):
    _attributes = (
        Attribute("type", Type),
        Attribute("input", bool, default=False),
        Attribute("output", bool, default=False),
    )
    
class Interface(Entity):
    _attributes = (
        Attribute("ports", elements(Port, "port")),
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
        Attribute("source", Port),
        Attribute("sink", Port),
    )
        
class Hierarchy(Implementation):
    _attributes = (
        Attribute("subcomponents", elements(Instance, "subcomponent")),
        Attribute("connections", elements(Connection, "connection",
                                          anonymous=True)),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        for c_name, c in self.subcomponents.items():
            c.name = c_name
