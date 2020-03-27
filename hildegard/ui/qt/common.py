# Copyright (c) 2020 Jeffrey A. Webb

from .  import diagram, scene
from ...diagram import Block, Diagram
from ...common import Environment
import wumps

from qtpy.QtWidgets import (
    QAction, QApplication, QFileDialog,  QGraphicsItem, QMainWindow,
    QMessageBox, QTabWidget, qApp
)

import os.path

class Main_Window(QMainWindow):
    def __init__(self, env):
        super().__init__()

        self._env = env
        
        self.update_title()
        
        main_menu = self.menuBar()
        project_menu = main_menu.addMenu("&Project")
        view_menu = main_menu.addMenu("&View")
        export_menu = main_menu.addMenu("&Export")

        toolbar = self.addToolBar("Top")
        #toolbar.hide()
        
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new empty project")
        new_action.triggered.connect(env.new)
        project_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open an existing project")
        open_action.triggered.connect(env.open)
        project_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save project")
        save_action.triggered.connect(
            lambda: env.save(self.tabs.currentWidget().view))
        project_menu.addAction(save_action)
        toolbar.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setStatusTip("Save project under a new name")
        save_as_action.triggered.connect(
            lambda: env.save_as(self.tabs.currentWidget().view))
        project_menu.addAction(save_as_action)

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setStatusTip("Quit Hildegard")
        quit_action.triggered.connect(self.handle_quit)
        project_menu.addAction(quit_action)
        
        fit_action = QAction("&Fit", self)
        fit_action.setStatusTip("Fit the entire scene to the viewport")
        fit_action.triggered.connect(
            lambda: self._fit_in_view(self.tabs.currentWidget()))
        view_menu.addAction(fit_action)
        toolbar.addAction(fit_action)
        
        export_svg_action = QAction("Export &SVG...", self)
        export_svg_action.setStatusTip("Export the current tab as an SVG file")
        export_svg_action.triggered.connect(
            lambda: env.export(self.tabs.currentWidget().view, format="svg"))
        export_menu.addAction(export_svg_action)
        toolbar.addAction(export_svg_action)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(
            lambda index: env.close(self.tabs.widget(index).view, quit=True))
        self.setCentralWidget(self.tabs)
        
        self.statusBar()

    def handle_quit(self):
        if self._env._ok_to_quit():
            qApp.quit()
            
    def closeEvent(self, event):
        if not self._env._ok_to_quit():
            event.ignore()
        
    def update_title(self):
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
    
    def __init__(self, source, show=True):
        super().__init__(source, show=show)
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

    def _ok_to_quit(self, view=None):
        if view:
            is_modified = view.widget.scene_item.modified
        else:
            is_modified = False
            for i in range(self._main_window.tabs.count()):
                if self._main_window.tabs.widget(i).scene_item.modified:
                    is_modified = True
                    break
        if is_modified:
            mb = QMessageBox()
            mb.setText("The project may have been modified.")
            mb.setInformativeText("Do you want to save your changes?")
            mb.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            mb.setDefaultButton(QMessageBox.Save)
            ans = mb.exec()
            if ans == QMessageBox.Cancel:
                return False
            elif ans == QMessageBox.Save:
                saved = self.save(None)
                if not saved:
                    return False
        return True

    def new(self):
        ret = self.close_all()
        if not ret:
            return
        super().new()
        
    def open(self, file_name=None):
        ret = self.close_all()
        if not ret:
            return
        if not file_name:
            file_name, selected_filter = QFileDialog.getOpenFileName(
                self._main_window, caption="Open File",
                filter="YAML Block Diagram (YBD) Files (*.ybd)")
            if file_name:
                self._file_name = file_name
                self._main_window.update_title()
                super().open(file_name)
            
    def view(self, view, show=True):
        added = super().view(view, show=show)
        if not added:
            return False
        if isinstance(view.widget, QGraphicsItem):
            view.widget = scene.Window(view.widget)
            view.widget.view = view
        self._add_tab(view)
        if show:
            view.widget.show()
        return True
    
    def close(self, view, quit=False):
        if not self.viewing(view):
            return True
        if not self._ok_to_quit(view):
            return False
        self._remove_tab(view)
        view.widget.close()
        ret = super().close(view)
        if not self.viewing() and quit:
            self._app.quit()
        return ret
    
    def close_all(self, quit=False):
        ret = super().close_all()
        if not self.viewing() and quit:
            self._app.quit()
        return ret
    
    def _set_new_file_name(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self._main_window, caption="Save Environment",
            filter="YAML Block Diagram (YBD) Files (*.ybd)")
        if file_name:
            self._file_name = file_name
            self._main_window.update_title()

    def save_as(self, view):
        self._set_new_file_name()
        if self._file_name:
            self.save(view)
            
    def save(self, view):
        if not self._file_name:
            self._set_new_file_name()
        if self._file_name:
            wumps.save(self._entities, file_name=self._file_name)
        return True if self._file_name else False
    
    def export(self, view, format):
        if (view.widget is not None and
            format == "svg" and
            hasattr(view.widget, "scene")):
            file_name, selected_filter = QFileDialog.getSaveFileName(
                self._main_window, caption="Export to SVG",
                filter="SVG Files (*.svg)")
            if file_name:
                scene.export_as_svg(view.widget.scene, file_name)
