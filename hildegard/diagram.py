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
        if self.name == "anonymous":
            self.name = self.hierarchy.name
