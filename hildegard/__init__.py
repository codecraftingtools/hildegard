# Copyright (c) 2020 Jeffrey A. Webb

from . import qt_ui as ui
import pidgen

from qtpy.QtWidgets import QApplication

class Editor_Handle:
    def __init__(self, app=None, entity=None, editor=None, tab_index=None):
        self.app = app
        self.entity = entity
        self.editor = editor
        self.tab_index = tab_index
        
    def close(self):
        self.app.close_editor(self)
            
class Application:
    _editors = {
        pidgen.Hierarchic_Component: ui.Hierarchic_Component_Editor,
    }
    
    def __init__(self, show=True):
        self._handles = []
        self._app = QApplication([])
        self._main_window = ui.Main_Window(self)
        if show:
            self._main_window.show()
        
    def execute(self):
        return self._app.exec_()

    def _add_tab(self, handle):
        if handle.tab_index is None:
            handle.tab_index = self._main_window.tabs.addTab(
                handle.editor, handle.entity.title)
        
    def _remove_tab(self, handle):
        if handle.tab_index is not None:
            self._main_window.tabs.removeTab(handle.tab_index)
            handle.tab_index = None
            
    def edit(self, entity, show=True):
        handle = Editor_Handle(self, entity)
        handle.editor = self._editors[type(entity)](entity, handle)
        self._add_tab(handle)
        if show:
            handle.editor.show()
        self._handles.append(handle)
        return handle
    
    def close_editor(self, handle):
        self._remove_tab(handle)
        if handle.editor is not None:
            handle.editor.close()
            del handle.editor
        self._handles.remove(handle)
        if not self._handles:
            self._app.quit()

    def export_as_svg(self, handle):
        if (handle.editor is not None and
            hasattr(handle.editor, "scene")):
            qt_util.export_scene_as_svg(
                handle.editor.scene)
