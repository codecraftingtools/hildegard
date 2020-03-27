# Copyright (c) 2020 Jeffrey A. Webb

import wumps
from wumps import Attribute, Entity

class View(Entity):
    _attributes = (
        Attribute("subject", save=False), # Remove save=False later
        Attribute("widget", save=False),
    )
    def __init__(self, *args, **kw):
        super().__init__(self, *args, **kw)
        if not self.name and self.subject:
            self.name = self.subject.name
     
class Environment:
    _viewers = {}
    
    def __init__(self, source, show=True):
        self._entities = []
        self._file_name = None
        self._open_views = []
        if isinstance(source, str):
            self._open(source)
        else:
            self._entities = list(source)

    def entities(self):
        return list(self._entities)
    
    def viewing(self, view=None):
        if view is None:
            return True if self._open_views else False
        else:
            return True if view in self._open_views else False
    
    def execute(self):
        return 0

    def new(self):
        from hildegard.diagram import Diagram
        ret = self.close_all()
        if not ret:
            return
        self._file_name = None
        d = Diagram(name="Untitled")
        self._entities = [d]
        self.view(d)
        
    def open(self, file_name):
        ret = self._open(file_name)
        for entity in self._entities:
            self.view(entity)
        return ret
    
    def _open(self, file_name): # Not overloaded
        from hildegard import diagram
        ret = self.close_all()
        if not ret:
            return
        print(f"opening: {file_name}")
        self._file_name = file_name
        self._entities = wumps.load(
            file_name,
            map={
                "Diagram": diagram.Diagram,
                "Block": diagram.Block,
                "Connector": diagram.Connector,
                "Connection": diagram.Connection,
            }
        )
        
    def view(self, view, show=True):
        if not view in self._entities:
            print("error: tried to view external entitiy")
            return False
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
        return True
    
    def close_all(self):
        for view in list(self._open_views):
            ret = self.close(view)
            if not ret:
                return False
        return True
    
    def export(self, view, format):
        pass
