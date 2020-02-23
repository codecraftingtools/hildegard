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

        self._block = block
        self.editing = False
        
        super().__init__(0, 0, 120, 200)
        self.setBrush(QBrush(Qt.gray))
        self.setPen(QPen(Qt.black))
        self.setFlag(self.ItemIsMovable)
        
        pad = 5
        self._pad = pad

        area = QGraphicsRectItem(self.rect())
        self._area = area
        area.setParentItem(self)
        area.setBrush(QBrush(Qt.NoBrush))
        #area.setBrush(QBrush(Qt.blue))
        area.setPen(QPen(Qt.NoPen))
        
        r_area = QGraphicsRectItem(self.rect())
        self._receptor_area = r_area
        r_area.setParentItem(self)
        r_area.setBrush(QBrush(Qt.NoBrush))
        #r_area.setBrush(QBrush(Qt.blue))
        r_area.setPen(QPen(Qt.NoPen))
        
        title = QGraphicsTextItem(self._block.name, parent=self)
        self._title = title
        title_br = title.boundingRect()
        title.setPos(2*pad, 2*pad)
        #title.setZValue(1)
        self._text_height = title_br.height()
        self._row_height = title_br.height() + 2*pad
        
        title_outline = QGraphicsRectItem(
            0, 0, title_br.width() + 4*pad, title_br.height() + 3*pad)
        self._title_outline = title_outline
        title_outline.setBrush(QBrush(Qt.darkGray))
        title_outline.setPen(QPen(Qt.black))
        title_outline.setParentItem(area)
        title.setParentItem(title_outline)
        
        self._p_rows = []
        self._r_rows = []
        
        self._resizers = resizer.add_resizers(self)
        self._update()
        
    def mouseDoubleClickEvent(self, event):
        self.editing = not self.editing
        self._update()
        
    def _update(self):
        r = self.rect()
        self._area.setRect(r)
        self._receptor_area.setRect(r)
        w = r.width()
        h = r.height()
        
        n_rows = int((h-2*self._pad) // self._row_height) - 1
        for i in range(n_rows):
            if i >= len(self._r_rows):
                new_r = QGraphicsRectItem(0,0,20,self._text_height)
                new_r.setParentItem(self._receptor_area)
                new_r.setPen(QPen(Qt.green));
                new_r.setBrush(QBrush(Qt.green));
                new_r.setOpacity(0.5)
                new_r.setPos(2*self._pad,2*self._pad+(i+1)*self._row_height)
                self._r_rows.append(new_r)
            if i >= len(self._p_rows):
                new_r = QGraphicsRectItem(0,0,30,self._row_height)
                new_r.setParentItem(self._area)
                new_r.setPen(QPen(Qt.black));
                new_r.setBrush(QBrush(Qt.NoBrush));
                new_r.setPos(self._pad,self._pad+(i+1)*self._row_height)
                self._p_rows.append(new_r)
        for i in range(len(self._r_rows)):
            rect1 = self._r_rows[i].rect()
            rect1.setWidth(w - 4*self._pad)
            self._r_rows[i].setRect(rect1)
            rect1 = self._p_rows[i].rect()
            rect1.setWidth(w - 2*self._pad)
            self._p_rows[i].setRect(rect1)
            if i >= n_rows:
                self._r_rows[i].hide()
                self._p_rows[i].hide()
            else:
                self._r_rows[i].show()
                self._p_rows[i].show()
                
        tw = self._title.boundingRect().width()
        self._title.setX((w - tw)/2.0)
        tor = self._title_outline.rect()
        tor.setWidth(w)
        self._title_outline.setRect(tor)
        
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
