# Copyright (c) 2020 Jeffrey A. Webb

from . import resizer, scene_util
from ... diagram import Block

from qtpy.QtCore import QRectF, Qt
from qtpy.QtGui import QBrush, QPen
from qtpy.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
)

class Block_Item(QGraphicsRectItem):
    def __init__(self, block):

        self.block = block
        self.editing = False
        
        super().__init__(0, 0, 120, 200)
        self.setBrush(QBrush(Qt.gray))
        self.setPen(QPen(Qt.black))
        self.setFlag(self.ItemIsMovable)
        
        pad = 5
        
        title = QGraphicsTextItem(self.block.name, parent=self)
        self.title = title
        title_br = title.boundingRect()
        title.setPos(pad, pad)
        #title.setZValue(1)
        
        title_outline = QGraphicsRectItem(
            0, 0, title_br.width() + 2*pad, title_br.height() + 2*pad)
        self.title_outline = title_outline
        title_outline.setBrush(QBrush(Qt.darkGray))
        title_outline.setPen(QPen(Qt.black))
        title_outline.setParentItem(self)
        title.setParentItem(title_outline)
        
        self._resizers = resizer.add_resizers(self)
        self._update()
        
    def mouseDoubleClickEvent(self, event):
        self.editing = not self.editing
        self._update()
        
    def _update(self):
        w = self.rect().width()
        tw = self.title.boundingRect().width()
        self.title.setX((w - tw)/2.0)
        tor = self.title_outline.rect()
        tor.setWidth(w)
        self.title_outline.setRect(tor)
        for rs in self._resizers:
            rs._update()
        
    def setRect(self, r):
        super().setRect(r)
        self._update()
        
class Diagram_Item(QGraphicsItem):
    def __init__(self, view):
        super().__init__()
        
        self.view = view
        
        for i, (s_name, s) in enumerate(
                self.view.symbols.items()):
            s_ui = Block_Item(s)
            s_ui.moveBy(200*i,0)
            s_ui.setParentItem(self)

    # Implement pure virtual method
    def paint(self, *args, **kw):
        pass
    
    # Implement pure virtual method
    def boundingRect(self, *args, **kw):
        return QRectF(0,0,0,0)
    
class Diagram_Editor(scene_util.Scene_Window):
    def __init__(self, view):
        ui = Diagram_Item(view)
        super().__init__(ui)
        self.view = view
