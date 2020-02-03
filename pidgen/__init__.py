# Copyright (c) 2020 Jeffrey A. Webb

from collections import OrderedDict

class Component:
    def __init__(self):
        self.title = "Component 1"
        self.ports = OrderedDict()

class Connection:
    def __init__(self, from_port, to_port):
        self.from_port = from_port
        self.to_port = to_port
        
class Hierarchic_Component(Component):
    def __init__(self):
        Component.__init__(self)
        self.subcomponents = OrderedDict()
        self.connections = []
