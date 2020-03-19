# Copyright (c) 2020 Jeffrey A. Webb

from .common import View
from pidgen import component
from wumps import Attribute, elements

class Connector(View):
    _attributes = (
        Attribute("subject", component.Port, alias="port"),
        Attribute("row", int),
        Attribute("col", int, default=1),
    )

class Symbol(View):
    _attributes = (
        Attribute("subject", component.Instance, alias="instance"),
        Attribute("connectors", elements(Connector, "connector")),
    )

class Block(Symbol):
    _attributes = ()

class Connection(View):
    _attributes = (
        Attribute("subject", component.Channel, alias="channel"),
        Attribute("source", Connector, reference=True),
        Attribute("sink", Connector, reference=True),
    )

class Diagram(View):
    _attributes = (
        Attribute("subject", component.Hierarchy, alias="hierarchy"),
        Attribute("symbols", elements(Symbol, "symbol")),
        Attribute("connections",
                  elements(Connection, "connection", anonymous=True)),
    )
