# Copyright (c) 2020 Jeffrey A. Webb

class Editor_Handle:
    def __init__(self, app=None, entity=None, editor=None, tab_index=None):
        self.app = app
        self.entity = entity
        self.editor = editor
        self.tab_index = tab_index
        
    def close(self):
        self.app.close(self)
            
class Application:
    _editors = {}
    
    def __init__(self, show=True):
        self._handles = []
        
    def execute(self):
        return 0

    def open(self, entity, show=True):
        handle = Editor_Handle(self, entity)
        handle.editor = self._editors[type(entity)](entity, handle)
        self._handles.append(handle)
        return handle
    
    def close(self, handle):
        self._handles.remove(handle)

    def export(self, handle, format):
        pass
