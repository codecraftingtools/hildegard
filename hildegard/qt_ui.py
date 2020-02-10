# Copyright (c) 2020 Jeffrey A. Webb

from . import qt_util

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class Component_UI(QGraphicsItemGroup):
    def __init__(self, component_name, component):
        super().__init__()

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
    def __init__(self, top_component, handle):
        super().__init__()
        
        self.top_component = top_component
        self.handle = handle
        
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

        for c_name, c in self.top_component.subcomponents.items():
            scene.addItem(Component_UI(c_name, c))
        
        self.resize(800, 600)

class Main_Window(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.setWindowTitle('Hildegard')
        
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')
        view_menu = main_menu.addMenu('&View')
        export_menu = main_menu.addMenu('&Export')

        toolbar = self.addToolBar('Top')
        #toolbar.hide()
        
        exit_action = QAction("E&xit Hildegard", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip('Exit Hildegard')
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        fit_action = QAction("Fit", self)
        fit_action.setStatusTip('Fit in view')
        fit_action.triggered.connect(
            lambda: self._fit_in_view(self.tabs.currentWidget()))
        view_menu.addAction(fit_action)
        toolbar.addAction(fit_action)
        
        export_svg_action = QAction("Export as SVG", self)
        export_svg_action.setStatusTip('Export current tab as an SVG file')
        export_svg_action.triggered.connect(
            lambda: app.export_as_svg(self.tabs.currentWidget().handle))
        export_menu.addAction(export_svg_action)
        toolbar.addAction(export_svg_action)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(
            lambda index: app.close_editor(self.tabs.widget(index).handle))
        self.setCentralWidget(self.tabs)
        
        self.statusBar()

    def _fit_in_view(self, editor):
        if hasattr(editor, "view"):
            editor.view.fit_all_in_view()
