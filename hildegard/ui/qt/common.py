# Copyright (c) 2020 Jeffrey A. Webb

from .  import diagram, scene
from ...diagram import Block, Diagram
from ...common import Environment
import wumps

from qtpy.QtWidgets import (
    QAction, QApplication, QFileDialog,  QGraphicsItem, QMainWindow,
    QTabWidget, qApp
)

import os.path

class Main_Window(QMainWindow):
    def __init__(self, env):
        super().__init__()

        self._env = env
        
        self._set_title()
        
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
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save")
        save_action.triggered.connect(
            lambda: env.save(self.tabs.currentWidget().view))
        file_menu.addAction(save_action)
        toolbar.addAction(save_action)

        save_as_action = QAction("&Save As...", self)
        save_as_action.setStatusTip("Save As...")
        save_as_action.triggered.connect(
            lambda: env.save_as(self.tabs.currentWidget().view))
        file_menu.addAction(save_as_action)

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

    def _set_title(self):
        if self._env._file_name:
            base_name = os.path.basename(self._env._file_name)
        else:
            base_name = "Unsaved"
        self.setWindowTitle(f"Hildegard: {base_name}")
        
    def _fit_in_view(self, widget_in_tab):
        if hasattr(widget_in_tab, "scene_view"):
            widget_in_tab.scene_view.fit_all_in_view()

class GUI_Environment(Environment):
    _viewers = {
        Diagram: diagram.Diagram_Editor,
        Block: diagram.Block_Item,
    }
    
    def __init__(self, entities, file_name=None, show=True):
        super().__init__(entities, file_name, show=show)
        self._app = QApplication([])
        self._main_window = Main_Window(self)
        if show:
            self._main_window.show()
        
    def execute(self):
        return self._app.exec_()

    def _add_tab(self, view):
        self._main_window.tabs.addTab(view.widget, view.name)
        
    def _remove_tab(self, view):
        self._main_window.tabs.removeTab(
            self._main_window.tabs.indexOf(view.widget))
        
    def open(self, view, show=True):
        added = super().open(view, show=show)
        if not added:
            return False
        if isinstance(view.widget, QGraphicsItem):
            view.widget = scene.Window(view.widget)
            view.widget.view = view
        self._add_tab(view)
        if show:
            view.widget.show()
        return True
    
    def close(self, view):
        if not self.viewing(view):
            return
        self._remove_tab(view)
        view.widget.close()
        super().close(view)
        if not self.viewing():
            self._app.quit()

    def _set_new_file_name(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self._main_window, caption="Save Environment",
            filter="YAML Block Diagram (YBD) Files (*.ybd)")
        if file_name:
            self._file_name = file_name
            self._main_window._set_title()
    
    def save_as(self, view):
        self._set_new_file_name()
        if self._file_name:
            self.save(view)
            
    def save(self, view):
        if not self._file_name:
            self._set_new_file_name()
        if self._file_name:
            wumps.save(self._entities, file_name=self._file_name)
            
    def export(self, view, format):
        if (view.widget is not None and
            format == "svg" and
            hasattr(view.widget, "scene")):
            file_name, selected_filter = QFileDialog.getSaveFileName(
                self._main_window, caption="Export to SVG",
                filter="SVG Files (*.svg)")
            if file_name:
                scene.export_as_svg(view.widget.scene, file_name)
