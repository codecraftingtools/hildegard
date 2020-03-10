# Copyright (c) 2020 Jeffrey A. Webb

from wumps import Attribute, Entity, elements

# Should be in Tydl module
class Type(Entity):
    _attributes = ()
    
class Port(Entity):
    _attributes = (
        Attribute("type", Type),
        Attribute("input", bool),
        Attribute("output", bool),
    )
    
class Interface(Entity):
    _attributes = (
        Attribute("ports", elements(Port, "port")),
    )

class Implementation(Entity):
    _attributes = (
        Attribute("interface", Interface),
    )

class Instance(Entity):
    _attributes = (
        Attribute("interface", Interface),
        Attribute("implementation", Implementation),
    )

class Channel(Entity):
    _attributes = (
        Attribute("source", Port),
        Attribute("sink", Port),
    )
        
class Hierarchy(Implementation):
    _attributes = (
        Attribute("subcomponents", elements(Instance, "subcomponent")),
        Attribute("channels", elements(Channel, "channel", anonymous=True)),
    )
