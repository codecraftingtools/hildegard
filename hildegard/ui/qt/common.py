# Copyright (c) 2020 Jeffrey A. Webb

from .  import diagram, scene
from ...diagram import Block, Diagram
from ...common import Environment
import wumps

from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QAction, QApplication, QFileDialog,  QGraphicsItem, QMainWindow,
    QMessageBox, QTabWidget, qApp
)

import os.path

class Main_Window(QMainWindow):
    def __init__(self, env):
        super().__init__()

        self._env = env
        self._extra_menu_actions = []
        self._extra_toolbar_actions = []
        
        self.update_title()
        
        main_menu = self.menuBar()
        self.main_menu = main_menu
        project_menu = main_menu.addMenu("&Project")

        toolbar = self.addToolBar("Top")
        self.toolbar = toolbar
        
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new empty project")
        new_action.triggered.connect(lambda: env.new())
        project_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open an existing project")
        open_action.triggered.connect(lambda: env.open())
        project_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        self.save_action = save_action
        save_action.setShortcut("Ctrl+S")
        save_action.setIcon(QIcon.fromTheme("document-save"))
        #save_action.setIcon(self.style().standardIcon(
        #    self.style().SP_DialogSaveButton))
        save_action.setStatusTip("Save project")
        save_action.setEnabled(False)
        save_action.triggered.connect(lambda: env.save())
        project_menu.addAction(save_action)
        toolbar.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setStatusTip("Save project under a new name")
        save_as_action.triggered.connect(lambda: env.save_as())
        project_menu.addAction(save_as_action)

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setStatusTip("Quit Hildegard")
        quit_action.triggered.connect(self.handle_quit)
        project_menu.addAction(quit_action)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(
            lambda index: env.close(self.tabs.widget(index).entity, quit=True))
        self.tabs.currentChanged.connect(self._handle_switch_to_tab)
        self.setCentralWidget(self.tabs)
        
        self.statusBar()

    def _handle_switch_to_tab(self, index):
        for a in self._extra_menu_actions:
            self.main_menu.removeAction(a)
        for t in self._extra_toolbar_actions:
            self.toolbar.removeAction(t)
        if index >= 0:
            widget = self.tabs.widget(index)
            if hasattr(widget, "menus"):
                for m in widget.menus:
                    a = self.main_menu.addMenu(m)
                    self._extra_menu_actions.append(a)
            if hasattr(widget, "tools"):
                for t in widget.tools:
                    self.toolbar.addAction(t)
                    self._extra_toolbar_actions.append(t)
                    
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
        modified_str = ""
        if self._env.modified:
            modified_str = "*"
        self.setWindowTitle(f"Hildegard: {base_name}{modified_str}")

    def update_tab_title(self, index):
        modified_str = ""
        widget = self.tabs.widget(index)
        if widget in self._env.modified_widgets:
            modified_str = "*"
        self.tabs.setTabText(
            index, f"{widget.entity.name}{modified_str}")
        
class GUI_Environment(Environment):
    _viewers = {
        Diagram: diagram.Diagram_Editor,
        Block: diagram.Block_Editor,
    }
    
    def __init__(self, source, show=True):
        super().__init__(source, show=show)
        self.modified = False
        self.modified_widgets = set()
        self._app = QApplication([])
        self._app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
        self._main_window = Main_Window(self)
        if show:
            self._main_window.show()
        
    def execute(self):
        return self._app.exec_()

    def _add_tab(self, entity):
        self._main_window.tabs.addTab(entity.widget, entity.name)
        self._main_window.update_tab_title(
            self._main_window.tabs.indexOf(entity.widget))
        
    def _remove_tab(self, entity):
        self._main_window.tabs.removeTab(
            self._main_window.tabs.indexOf(entity.widget))

    def _ok_to_close(self, entity):
        if entity.widget in self.modified_widgets:
            mb = QMessageBox()
            mb.setText("The tab contents may have been modified.")
            mb.setInformativeText("Do you want to save your changes?")
            mb.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            mb.setDefaultButton(QMessageBox.Save)
            ans = mb.exec()
            if ans == QMessageBox.Cancel:
                return False
            elif ans == QMessageBox.Save:
                saved = self.save()
                if not saved:
                    return False
        return True
        
    def _ok_to_quit(self):
        if not hasattr(self, "_main_window"):
            return True
        if self.modified:
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
                saved = self.save()
                if not saved:
                    return False
        return True

    def new(self):
        if not self._ok_to_quit():
            return
        self.clear_modified()
        ret = self.close_all()
        if not ret:
            return
        super().new()
        
    def open(self, file_name=None):
        if not self._ok_to_quit():
            return
        if not file_name:
            file_name, selected_filter = QFileDialog.getOpenFileName(
                self._main_window, caption="Open File",
                filter="Hildegard Project Files (*.hpy)")
            if file_name:
                self.clear_modified()
                ret = self.close_all()
                if not ret:
                    return
                self._file_name = file_name
                self._main_window.update_title()
                super().open(file_name)
            
    def view(self, entity, show=True):
        added = super().view(entity, show=show)
        if not added:
            return False
        self._add_tab(entity)
        if show:
            entity.widget.show()
        return True
    
    def close(self, entity, quit=False):
        if not self.viewing(entity):
            return True
        if not self._ok_to_close(entity):
            return False
        self._remove_tab(entity)
        entity.widget.close()
        ret = super().close(entity)
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
            filter="Hildegard Project Files (*.hpy)")
        if file_name:
            self._file_name = file_name
            self._main_window.update_title()

    def save_as(self):
        self._set_new_file_name()
        if self._file_name:
            self.save()
            
    def save(self):
        if not self._file_name:
            self._set_new_file_name()
        if self._file_name:
            wumps.save(self._entities, file_name=self._file_name)
            self._main_window.save_action.setEnabled(False)
            self.clear_modified()
        return True if self._file_name else False
        
    def set_modified(self, subitem=None):
        if subitem is not None:
            self.modified_widgets.add(subitem)
            try:
                i = self._main_window.tabs.indexOf(subitem)
                self._main_window.update_tab_title(i)
            except:
                pass
        self.modified = True
        self._main_window.update_title()
        self._main_window.save_action.setEnabled(True)
        
    def clear_modified(self):
        self.modified = False
        self._main_window.update_title()
        widgets_to_update = self.modified_widgets
        self.modified_widgets = set()
        for widget in widgets_to_update:
            try:
                i = self._main_window.tabs.indexOf(widget)
                self._main_window.update_tab_title(i)
            except:
                pass
