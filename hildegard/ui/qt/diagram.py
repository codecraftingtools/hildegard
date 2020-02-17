# Copyright (c) 2020 Jeffrey A. Webb

from . import util
from ... diagram import Block

from qtpy.QtCore import Qt, QRectF
from qtpy.QtGui import QBrush, QPen
from qtpy.QtWidgets import (
    QGraphicsItemGroup, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
)

class Block_Item(QGraphicsItemGroup):
    def __init__(self, block):
        super().__init__()

        self.block = block
        
        outline = QGraphicsRectItem(0, 0, 100, 200, parent=self)
        self.outline = outline
        outline_br = outline.boundingRect()
        outline.setPos(-outline_br.width()/2.0, -outline_br.height()/2.0)
        outline.setBrush(QBrush(Qt.gray))
        outline.setPen(QPen(Qt.green))
        #outline.setPen(QPen(Qt.green, 3, Qt.DashDotLine,
        #               Qt.RoundCap, Qt.RoundJoin))

        title = QGraphicsTextItem(self.block.name, parent=self)
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
        
class Diagram_Item(QGraphicsItem):
    def __init__(self, view):
        super().__init__()
        
        self.view = view
        
        for i, (s_name, s) in enumerate(
                self.view.symbols.items()):
            s_ui = Block_Item(s)
            s_ui.moveBy(200*i,0)
            s_ui.setParentItem(self)
            
    def paint(self, *args, **kw):
        pass
    
    def boundingRect(self, *args, **kw):
        return QRectF(0,0,0,0)
    
class Diagram_Editor(util.Scene_Window):
    def __init__(self, view):
        ui = Diagram_Item(view)
        super().__init__(ui)
        self.view = view
