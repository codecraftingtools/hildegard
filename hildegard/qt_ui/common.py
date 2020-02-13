# Copyright (c) 2020 Jeffrey A. Webb

from .. import api
from .  import diagram, util

from pidgen import component

from qtpy.QtWidgets import (
    QApplication, QMainWindow, QAction, qApp, QTabWidget
)

class Main_Window(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.setWindowTitle("Hildegard")
        
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("&File")
        view_menu = main_menu.addMenu("&View")
        export_menu = main_menu.addMenu("&Export")

        toolbar = self.addToolBar("Top")
        #toolbar.hide()
        
        exit_action = QAction("E&xit Hildegard", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit Hildegard")
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        fit_action = QAction("Fit", self)
        fit_action.setStatusTip("Fit in view")
        fit_action.triggered.connect(
            lambda: self._fit_in_view(self.tabs.currentWidget()))
        view_menu.addAction(fit_action)
        toolbar.addAction(fit_action)
        
        export_svg_action = QAction("Export as SVG", self)
        export_svg_action.setStatusTip("Export current tab as an SVG file")
        export_svg_action.triggered.connect(
            lambda: app.export(self.tabs.currentWidget().handle, format="svg"))
        export_menu.addAction(export_svg_action)
        toolbar.addAction(export_svg_action)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(
            lambda index: app.close(self.tabs.widget(index).handle))
        self.setCentralWidget(self.tabs)
        
        self.statusBar()

    def _fit_in_view(self, editor):
        if hasattr(editor, "view"):
            editor.view.fit_all_in_view()

class Application(api.Application):
    _editors = {
        component.Hierarchic_Implementation:
          diagram.Hierarchic_Component_Editor,
    }
    
    def __init__(self, show=True):
        super().__init__(show=show)
        self._qapp = QApplication([])
        self._main_window = Main_Window(self)
        if show:
            self._main_window.show()
        
    def execute(self):
        return self._qapp.exec_()

    def _add_tab(self, handle):
        if handle.tab_index is None:
            handle.tab_index = self._main_window.tabs.addTab(
                handle.editor, handle.entity["name"])
        
    def _remove_tab(self, handle):
        if handle.tab_index is not None:
            self._main_window.tabs.removeTab(handle.tab_index)
            handle.tab_index = None
            
    def open(self, entity, show=True):
        handle = super().open(entity, show=show)
        self._add_tab(handle)
        if show:
            handle.editor.show()
        return handle
    
    def close(self, handle):
        self._remove_tab(handle)
        if handle.editor is not None:
            handle.editor.close()
            del handle.editor
        super().close(handle)
        if not self._handles:
            self._qapp.quit()

    def export(self, handle, format):
        if (handle.editor is not None and
            format == "svg" and
            hasattr(handle.editor, "scene")):
            util.export_scene_as_svg(
                handle.editor.scene)
