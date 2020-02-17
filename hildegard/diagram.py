# Copyright (c) 2020 Jeffrey A. Webb

from .common import View
from pidgen import component
from wumps import Attribute, elements

class Connector(View):
    _attributes = (
        Attribute("port", component.Port),
    )

class Symbol(View):
    _attributes = (
        Attribute("instance", component.Instance),
        Attribute("connectors", elements(Connector, "connector")),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name:
            self.name = self.instance.name
        for c_name, c in self.connectors.items():
            c.name = c_name

class Block(Symbol):
    _attributes = ()

class Diagram(View):
    _attributes = (
        Attribute("hierarchy", component.Hierarchy),
        Attribute("symbols", elements(Symbol, "symbol")),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name:
            self.name = self.hierarchy.name
        for s_name, s in self.symbols.items():
            s.name = s_name
