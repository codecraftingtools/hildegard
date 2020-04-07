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
        self._open_entities = []
        if isinstance(source, str):
            self._open(source)
        else:
            self._entities = list(source)

    def entities(self):
        return list(self._entities)
    
    def viewing(self, entity=None):
        if entity is None:
            return True if self._open_entities else False
        else:
            return True if entity in self._open_entities else False
    
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
        
    def view(self, entity, show=True):
        if not entity in self._entities:
            print("error: tried to view external entitiy")
            return False
        if entity.widget:
            return False
        if entity in self._open_entities:
            return False
        entity.widget = self._viewers[type(entity)](entity, self)
        self._open_entities.append(entity)
        return True
    
    def close(self, entity):
        self._open_entities.remove(entity)
        entity.widget = None
        return True
    
    def close_all(self):
        for entity in list(self._open_entities):
            ret = self.close(entity)
            if not ret:
                return False
        return True
