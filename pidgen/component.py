# Copyright (c) 2020 Jeffrey A. Webb

from .base import Entity, Attribute

from collections import OrderedDict

class Interface(Entity):
    _attributes = (
        Attribute("ports", OrderedDict, element="port"),
    )

class Implementation(Entity):
    _attributes = (
        Attribute("interface", Interface),
    )

class Instance(Entity):
    _attributes = (
        Attribute("interface", Interface),
    )

class Connection(Entity):
    _attributes = (
        Attribute("source"),
        Attribute("sink"),
    )
        
class Hierarchic_Implementation(Implementation):
    _attributes = (
        Attribute("subcomponents", OrderedDict, element="subcomponent"),
        Attribute("connections", list, element="connection"),
    )
