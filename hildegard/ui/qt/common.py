# Copyright (c) 2020 Jeffrey A. Webb

from .  import diagram, util
from ...diagram import Diagram
from ...common import Environment

from qtpy.QtWidgets import (
    QAction, QApplication, QMainWindow, QTabWidget, qApp
)

class Main_Window(QMainWindow):
    def __init__(self, env):
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
            lambda: env.export(self.tabs.currentWidget().view, format="svg"))
        export_menu.addAction(export_svg_action)
        toolbar.addAction(export_svg_action)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(
            lambda index: env.close(self.tabs.widget(index).view))
        self.setCentralWidget(self.tabs)
        
        self.statusBar()

    def _fit_in_view(self, widget_in_tab):
        if hasattr(widget_in_tab, "scene_view"):
            widget_in_tab.scene_view.fit_all_in_view()

class GUI_Environment(Environment):
    _viewers = {
        Diagram: diagram.Diagram_Editor,
    }
    
    def __init__(self, show=True):
        super().__init__(show=show)
        self._app = QApplication([])
        self._main_window = Main_Window(self)
        if show:
            self._main_window.show()
        
    def execute(self):
        return self._app.exec_()

    def _add_tab(self, view):
        if (not hasattr(view.widget, "tab_index") or
            view.widget.tab_index is None):
            view.widget.tab_index = self._main_window.tabs.addTab(
                view.widget, view.name)
        
    def _remove_tab(self, view):
        if (hasattr(view.widget, "tab_index") and
            view.widget.tab_index is not None):
            self._main_window.tabs.removeTab(view.widget.tab_index)
            view.widget.tab_index = None
            
    def open(self, view, show=True):
        super().open(view, show=show)
        self._add_tab(view)
        if show:
            view.widget.show()
    
    def close(self, view):
        self._remove_tab(view)
        if view.widget is not None:
            view.widget.close()
            view.widget = None
        super().close(view)
        if not self.viewing():
            self._app.quit()

    def export(self, view, format):
        if (view.widget is not None and
            format == "svg" and
            hasattr(view.widget, "scene")):
            util.export_scene_as_svg(
                view.widget.scene)