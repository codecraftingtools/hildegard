# Copyright (c) 2020 Jeffrey A. Webb

from .entity import *

from collections import OrderedDict

class Component(Entity):
    _attributes = (
        Attribute("title", str, default="untitled"),
        Attribute("ports", OrderedDict, alias="port"),
    )    

class Connection:
    _attributes = (
        Attribute("from_port"),
        Attribute("to_port"),
    )
        
class Hierarchic_Component(Component):
    _attributes = (
        Attribute("subcomponents", OrderedDict, alias="subcomponent"),
        Attribute("connections", list, alias="connection"),
    )    
