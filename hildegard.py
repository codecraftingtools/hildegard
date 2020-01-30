#!/usr/bin/python3

import sys
from collections import OrderedDict

from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtSvg import *

class Component:
    def __init__(self):
        self.ports = OrderedDict()

class Connection:
    def __init__(self, from_port, to_port):
        self.from_port = from_port
        self.to_port = to_port
        
class Hierarchic_Component(Component):
    def __init__(self):
        Component.__init__(self)
        self.subcomponents = OrderedDict()
        self.connections = []

class Component_Qt_View(QGraphicsItemGroup):
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

    def __init__(self, top_component):
        QWidget.__init__(self)

        self.top_component = top_component
        
        #scene.addLine(-100, -100, 100, 100)
        #scene.addLine(0, 0, 0, 100)

        self.setWindowTitle('Hierarchic Component Editor')
        layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        scene = QGraphicsScene()
        self.scene = scene
        
        view = QGraphicsView(self)
        self.view = view
        view.setScene(scene)
        view.setMinimumSize(350, 350)
        #view.setDragMode(QGraphicsView.ScrollHandDrag)
        view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(view)

        quit_button = QPushButton('Close')
        quit_button.clicked.connect(qApp.quit)
        layout.addWidget(quit_button, False, Qt.AlignHCenter)

        for c_name, c in self.top_component.subcomponents.items():
            scene.addItem(Component_Qt_View(c_name, c))
        
        self.resize(800, 600)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    c = Hierarchic_Component()
    c.subcomponents["C1"] = Component()
    
    e = Hierarchic_Component_Editor(c)
    e.show()

    svgGen = QSvgGenerator()
    svgGen.setFileName( "out.svg" )
    svgGen.setSize(QSize(e.scene.width(), e.scene.height()))
    svgGen.setViewBox(QRect(0, 0, e.scene.width(), e.scene.height()))
    svgGen.setTitle("Hierarchic Component Drawing")
    svgGen.setDescription("A Hierarchic Component Drawing created by gsd.")
    painter = QPainter()
    painter.begin(svgGen)
    e.scene.render(painter)
    painter.end()
    
    sys.exit(app.exec_())
