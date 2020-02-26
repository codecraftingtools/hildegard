# Copyright (c) 2020 Jeffrey A. Webb

from .common import View
from pidgen import component
from wumps import Attribute, elements

class Connector(View):
    _attributes = (
        Attribute("subject", component.Port, alias="port"),
        Attribute("row", int),
    )

class Symbol(View):
    _attributes = (
        Attribute("subject", component.Instance, alias="instance"),
        Attribute("connectors", elements(Connector, "connector")),
    )

class Block(Symbol):
    _attributes = ()

class Diagram(View):
    _attributes = (
        Attribute("subject", component.Hierarchy, alias="hierarchy"),
        Attribute("symbols", elements(Symbol, "symbol")),
    )
