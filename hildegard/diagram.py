# Copyright (c) 2020 Jeffrey A. Webb

from .common import View
from pidgen import component
from wumps import Attribute, elements

class Connector(View):
    _attributes = (
        Attribute("port", component.Port, alias="subject"),
    )

class Symbol(View):
    _attributes = (
        Attribute("instance", component.Instance, alias="subject"),
        Attribute("connectors", elements(Connector, "connector")),
    )

class Block(Symbol):
    _attributes = ()

class Diagram(View):
    _attributes = (
        Attribute("hierarchy", component.Hierarchy, alias="subject"),
        Attribute("symbols", elements(Symbol, "symbol")),
    )
