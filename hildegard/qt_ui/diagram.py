# Copyright (c) 2020 Jeffrey A. Webb

from . import util

from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter, QBrush, QPen
from qtpy.QtWidgets import (
    QGraphicsItemGroup, QWidget, QBoxLayout, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem
)

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

        self.setWindowTitle("Hierarchic Component Editor")
        layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        scene = QGraphicsScene()
        self.scene = scene
        
        view = util.Scene_View(self)
        self.view = view
        view.setScene(scene)
        view.setMinimumSize(350, 350)
        view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(view)

        for c_name, c in self.top_component["subcomponents"].items():
            scene.addItem(Component_UI(c_name, c))
        
        self.resize(800, 600)