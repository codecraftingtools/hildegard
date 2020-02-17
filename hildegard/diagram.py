# Copyright (c) 2020 Jeffrey A. Webb

from .common import View
from pidgen import component
from wumps import Attribute

from collections import OrderedDict

class Diagram(View):
    _attributes = (
        Attribute("hierarchy", component.Hierarchy),
        Attribute("symbols", OrderedDict, element="symbol"),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name:
            self.name = self.hierarchy.name
        for s_name, s in self.symbols.items():
            s.name = s_name

class Symbol(View):
    _attributes = (
        Attribute("instance", component.Instance),
        Attribute("connectors", OrderedDict, element="connector"),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name:
            self.name = self.instance.name
        for c_name, c in self.connectors.items():
            c.name = c_name

class Block(Symbol):
    _attributes = ()
