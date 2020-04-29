# Copyright (c) 2020 Jeffrey A. Webb

from .common import View
from pidgen import component
from wumps import Attribute, Entity, elements

class Connector(View):
    _attributes = (
        Attribute("subject", component.Port, alias="port"),
        Attribute("row", int),
        Attribute("col", int, default=1),
    )

class Endpoint(Entity):
    _attributes = (
        Attribute("connector", Connector, reference=True),
        Attribute("ports",
                  elements(component.Port, "port", anonymous=True)),
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
        Attribute("source", Endpoint),
        Attribute("sink", Endpoint),
    )

class Diagram(View):
    _attributes = (
        Attribute("subject", component.Hierarchy, alias="hierarchy"),
        Attribute("symbols", elements(Symbol, "symbol", anonymous=True)),
        Attribute("connections",
                  elements(Connection, "connection", anonymous=True)),
    )
