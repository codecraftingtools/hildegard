# Copyright (c) 2020 Jeffrey A. Webb

from wumps import Attribute, Entity

class View(Entity):
    _attributes = (
        # Derived entities should add "subject" alias
        Attribute("widget", save=False),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name and self.subject:
            self.name = self.subject.name
     
class Environment:
    _viewers = {}
    
    def __init__(self, show=True):
        self._open_views = []

    def viewing(self, view=None):
        if view is None:
            return True if self._open_views else False
        else:
            return True if view in self._open_views else False
    
    def execute(self):
        return 0

    def open(self, view, show=True):
        if view.widget:
            return False
        if view in self._open_views:
            return False
        view.widget = self._viewers[type(view)](view)
        self._open_views.append(view)
        return True
    
    def close(self, view):
        self._open_views.remove(view)
        view.widget = None
        
    def export(self, view, format):
        pass
