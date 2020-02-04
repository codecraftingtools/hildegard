# Copyright (c) 2020 Jeffrey A. Webb

from . import qt_util
import pidgen

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class Component_UI(QGraphicsItemGroup):
    def __init__(self, component_name, component):
        QGraphicsItemGroup.__init__(self)

        self.component_name = component_name
        self.component = component
        
        outline = QGraphicsRectItem(0, 0, 100, 200, parent=self)
        self.outline = outline
        outline_br = outline.boundingRect()
        outline.setPos(-outline_br.width()/2.0, -outline_br.height()/2.0)
        outline.setBrush(QBrush(Qt.gray))
        outline.setPen(QPen(Qt.green))
        #outline.setPen(QPen(Qt.green, 3, Qt.DashDotLine,
        #               Qt.RoundCap, Qt.RoundJoin))

        title = QGraphicsTextItem(component_name, parent=self)
        self.title = title
        title_br = title.boundingRect()
        #title.setPos(-title_br.width()/2.0, -title_br.height()/2.0)
        title.setZValue(1)

        pad = 5
        title_outline = QGraphicsRectItem(
            title_br.x() - pad, title_br.y() - pad,
            title_br.width() + 2*pad, title_br.height() + 2*pad,
            parent=self)
        title_outline.setBrush(QBrush(Qt.red))
        #title_outline.setPos(title.x(), title.y())
        #title_outline.update(title.x(), title.y(),
        #                     title_br.width() + 20, title_br.height() + 20)
        
        self.setFlag(self.ItemIsMovable)
        
class Hierarchic_Component_Editor(QWidget):
    def __init__(self, top_component, app):
        QWidget.__init__(self)

        self.top_component = top_component
        
        #scene.addLine(-100, -100, 100, 100)
        #scene.addLine(0, 0, 0, 100)

        self.setWindowTitle('Hierarchic Component Editor')
        layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        scene = QGraphicsScene()
        self.scene = scene
        
        view = qt_util.Scene_View(self)
        self.view = view
        view.setScene(scene)
        view.setMinimumSize(350, 350)
        view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(view)

        #quit_button = QPushButton('Close')
        #quit_button.clicked.connect(lambda: app.close_editor(self))
        #layout.addWidget(quit_button, False, Qt.AlignHCenter)

        for c_name, c in self.top_component.subcomponents.items():
            scene.addItem(Component_UI(c_name, c))
        
        self.resize(800, 600)

class Main_Window(QMainWindow):
    def __init__(self, app):
        QMainWindow.__init__(self)

        self._app = app
        
        self.setWindowTitle('Hildegard')
        
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')
        export_menu = main_menu.addMenu('&Export')

        toolbar = self.addToolBar('Top')
        #toolbar.hide()
        
        close_action = QAction("Close Tab", self)
        close_action.setStatusTip('Close active tab')
        close_action.triggered.connect(
            lambda: app.close_editor(self.tabs.currentWidget()))
        file_menu.addAction(close_action)
        toolbar.addAction(close_action)

        exit_action = QAction("E&xit Hildegard", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip('Exit Hildegard')
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab_with_index)
        self.setCentralWidget(self.tabs)
        
        export_svg_action = QAction("Export as SVG", self)
        export_svg_action.setStatusTip('Export current tab as an SVG file')
        export_svg_action.triggered.connect(
            lambda: app.export_as_svg(self.tabs.currentWidget()))
        export_menu.addAction(export_svg_action)
        toolbar.addAction(export_svg_action)

        self.statusBar()

    def _close_tab_with_index(self, index):
        self._app.close_editor(self.tabs.widget(index))
        
class Application:
    _editors = {
        pidgen.Hierarchic_Component: Hierarchic_Component_Editor,
    }
    
    def __init__(self):
        self._app = QApplication([])
        self._tab_contents = {}
        self._main_window = Main_Window(self)
        self._main_window.show()
        
    def execute(self):
        return self._app.exec_()

    def _add_tab(self, item, name):
        index = self._main_window.tabs.addTab(item, name)
        self._tab_contents[index] = item
        
    def _remove_tab(self, item):
        index = None
        for index, content in self._tab_contents.items():
            if content == item:
                self._main_window.tabs.removeTab(index)
                break
        if index is not None:
            del self._tab_contents[index]
            
    def edit(self, item):
        e = self._editors[type(item)](item, self)
        e.show()
        self._add_tab(e, item.title)

    def close_editor(self, item):
        self._remove_tab(item)
        item.close()
        if not self._tab_contents:
            qApp.quit()

    def export_as_svg(self, item):
        if hasattr(item, "scene"):
            qt_util.export_scene_as_svg(
                item.scene)
