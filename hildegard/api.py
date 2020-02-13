# Copyright (c) 2020 Jeffrey A. Webb

class View:
    def __init__(self, entity=None):
        self.entity = entity
        self.widget = None
            
class Application:
    _viewers = {}
    
    def __init__(self, show=True):
        self._open_views = []

    def viewing(self):
        return True if self._open_views else False
    
    def execute(self):
        return 0

    def open(self, entity, show=True):
        view = View(entity)
        view.widget = self._viewers[type(entity)](entity, view)
        self._open_views.append(view)
        return view
    
    def close(self, view):
        self._open_views.remove(view)

    def export(self, view, format):
        pass
