# Copyright (c) 2020 Jeffrey A. Webb

from .common import View
from pidgen import component
from wumps import Attribute

class Diagram(View):
    _attributes = (
        Attribute("hierarchy", component.Hierarchy),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name:
            self.name = self.hierarchy.name

class Block(View):
    _attributes = (
        Attribute("instance", component.Instance),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name:
            self.name = self.instance.name
