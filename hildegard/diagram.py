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
        Attribute("connectors",
                  elements(Connector, "connector", anonymous=True)),
        Attribute("x", float),
        Attribute("y", float),
    )

class Block(Symbol):
    _attributes = (
        Attribute("width", float),
        Attribute("height", float),
    )

class Connection(View):
    _attributes = (
        Attribute("subject", component.Channel, alias="channel"),
        Attribute("source", Connector, reference=True),
        Attribute("sink", Connector, reference=True),
        Attribute("source_ports",
                  elements(component.Port, "source_port", anonymous=True)),
        Attribute("dest_ports",
                  elements(component.Port, "dest_port", anonymous=True)),
    )

class Diagram(View):
    _attributes = (
        Attribute("subject", component.Hierarchy, alias="hierarchy"),
        Attribute("symbols", elements(Symbol, "symbol", anonymous=True)),
        Attribute("connections",
                  elements(Connection, "connection", anonymous=True)),
    )
