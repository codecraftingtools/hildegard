# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush, QPen
from qtpy.QtWidgets import QGraphicsItem, QGraphicsItemGroup, QGraphicsRectItem

def add_resizers(parent):
    return (
        Rect_Resizer(parent, anchor="BR", vertical=False),
        Rect_Resizer(parent, anchor="BR", vertical=True),
        Rect_Resizer(parent, anchor="TR", vertical=False),
        Rect_Resizer(parent, anchor="TR", vertical=True),
        Rect_Resizer(parent, anchor="BL", vertical=False),
        Rect_Resizer(parent, anchor="BL", vertical=True),
        Rect_Resizer(parent, anchor="TL", vertical=False),
        Rect_Resizer(parent, anchor="TL", vertical=True),
        Rect_Resizer(parent, anchor="B",  vertical=False),
        Rect_Resizer(parent, anchor="T",  vertical=False),
    )
    
class Rect_Resizer(QGraphicsRectItem):
    def __init__(self, parent, anchor="BR", vertical=False):
        self._border = 10
        self._side = 40
        self._anchor = anchor
        self._last_mouse_scene_pos = None
        self._last_parent_rect = None
        self._last_parent_pos = None
        if vertical:
            w = self._border
            h = self._side
        else:
            w = self._side
            h = self._border
        if anchor in ["BR", "TR"]:
            x = self._side - w
        elif anchor in ["BL", "TL", "B", "T"]:
            x = 0
        if anchor in ["BR", "BL", "B"]:
            y = self._side - h
        elif anchor in ["TR", "TL", "T"]:
            y = 0
        super().__init__(x, y, w, h)
        self.setParentItem(parent)
        self._update()
        
    def _update(self):
        parent = self.parentItem()
        if self._anchor in ["BR", "TR"]:
            x = parent.rect().width() - self._side
        elif self._anchor in ["BL", "TL"]:
            x = 0
        elif self._anchor in ["B", "T"]:
            x = self._side
        if self._anchor in ["BR", "BL", "B"]:
            y = parent.rect().height() - self._side
        elif self._anchor in ["TR", "TL", "T"]:
            y = 0
        self.setPos(x, y)
        if self._anchor in ["B", "T"]:
            r = self.rect()
            r.setWidth(parent.rect().width() - 2*self._side)
            self.setRect(r)
        if parent.editing:
            if self._anchor in ["B", "T"]:
                self.setBrush(QBrush(Qt.NoBrush))
            else:
                self.setBrush(QBrush(Qt.red))
            self.setPen(QPen(Qt.red))
            self.setFlag(self.ItemIsMovable)
        else:
            self.setBrush(QBrush(Qt.NoBrush))
            self.setPen(QPen(Qt.NoPen))
            self.setFlag(self.ItemIsMovable, False)
        
    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton):
            self._last_mouse_scene_pos = event.scenePos()
            self._last_parent_rect = self.parentItem().rect()
            self._last_parent_pos = self.parentItem().pos()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        old_p = self.parentItem().mapFromScene(self._last_mouse_scene_pos)
        p = self.parentItem().mapFromScene(event.scenePos())
        delta_p = p - old_p
        
        min_delta_p_x = None
        max_delta_p_x = None
        min_delta_p_y = None
        max_delta_p_y = None        

        if self._anchor in ["BR", "TR"]:
            min_delta_p_x = -(self._last_parent_rect.width() - 3*self._side)
        elif self._anchor in ["BL", "TL"]:
            max_delta_p_x = self._last_parent_rect.width() - 3*self._side
        elif self._anchor in ["B", "T"]:
            min_delta_p_x = 0
            max_delta_p_x = 0
        if self._anchor in ["BR", "BL", "B"]:
            min_delta_p_y = -(self._last_parent_rect.height() - 3*self._side)
        elif self._anchor in ["TR", "TL", "T"]:
            max_delta_p_y = self._last_parent_rect.height() - 3*self._side

        if min_delta_p_x is not None and delta_p.x() < min_delta_p_x:
            delta_p.setX(min_delta_p_x)
        if max_delta_p_x is not None and delta_p.x() > max_delta_p_x:
            delta_p.setX(max_delta_p_x)
        if min_delta_p_y is not None and delta_p.y() < min_delta_p_y:
            delta_p.setY(min_delta_p_y)
        if max_delta_p_y is not None and delta_p.y() > max_delta_p_y:
            delta_p.setY(max_delta_p_y)

        if self._anchor in ["BR", "TR"]:
            move_x = 0
            resize_x = delta_p.x()
        elif self._anchor in ["BL", "TL"]:
            move_x = delta_p.x()
            resize_x = -delta_p.x()
        elif self._anchor in ["B", "T"]:
            move_x = 0
            resize_x = 0
        if self._anchor in ["BR", "BL", "B"]:
            move_y = 0
            resize_y = delta_p.y()
        elif self._anchor in ["TR", "TL", "T"]:
            move_y = delta_p.y()
            resize_y = -delta_p.y()
        
        self.parentItem().setPos(
            self._last_parent_pos.x() + move_x,
            self._last_parent_pos.y() + move_y)
        pr = self.parentItem().rect()
        pr.setWidth(self._last_parent_rect.width() + resize_x)
        pr.setHeight(self._last_parent_rect.height() + resize_y)
        self.parentItem().setRect(pr)
