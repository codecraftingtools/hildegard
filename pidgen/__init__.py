# Copyright (c) 2020 Jeffrey A. Webb

from .entity import *

from collections import OrderedDict

class Component(Entity):
    _attributes = (
        Attribute("title", str, default="untitled"),
        Attribute("ports", OrderedDict, alias="port"),
    )    
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

class Connection:
    _attributes = (
        Attribute("from_port"),
        Attribute("to_port"),
    )
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        
class Hierarchic_Component(Component):
    _attributes = (
        Attribute("subcomponents", OrderedDict, alias="subcomponent"),
        Attribute("connections", list, alias="connection"),
    )    
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
