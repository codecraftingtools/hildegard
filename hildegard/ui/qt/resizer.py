# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGraphicsItem, QGraphicsItemGroup, QGraphicsRectItem

def add_resizers(parent):
    return (
        Rect_Resizer(parent, anchor="BR", vertical=False),
        Rect_Resizer(parent, anchor="BR", vertical=True),
        Rect_Resizer(parent, anchor="TR", vertical=False),
        Rect_Resizer(parent, anchor="TR", vertical=True),
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
        x = self._side - w
        if anchor == "BR":
            y = self._side - h
        elif anchor == "TR":
            y = 0
        super().__init__(x, y, w, h)
        self.setParentItem(parent)
        self._update()
        self.setFlag(self.ItemIsMovable)
        
    def _update(self):
        parent = self.parentItem()
        x = parent.rect().width() - self._side
        if self._anchor == "BR":
            y = parent.rect().height() - self._side
        elif self._anchor == "TR":
            y = 0    
        self.setPos(x, y)
        
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

        if self._anchor == "BR":
            min_delta_p_y = -(self._last_parent_rect.height() - 3*self._side)
        elif self._anchor == "TR":
            max_delta_p_y = self._last_parent_rect.height() - 3*self._side
        min_delta_p_x = -(self._last_parent_rect.width() - 3*self._side)

        if min_delta_p_x is not None and delta_p.x() < min_delta_p_x:
            delta_p.setX(min_delta_p_x)
        if max_delta_p_x is not None and delta_p.x() > max_delta_p_x:
            delta_p.setX(max_delta_p_x)
        if min_delta_p_y is not None and delta_p.y() < min_delta_p_y:
            delta_p.setY(min_delta_p_y)
        if max_delta_p_y is not None and delta_p.y() > max_delta_p_y:
            delta_p.setY(max_delta_p_y)

        move_x = 0
        resize_x = delta_p.x()
        if self._anchor == "BR":
            move_y = 0
            resize_y = delta_p.y()
        elif self._anchor == "TR":
            move_y = delta_p.y()
            resize_y = -delta_p.y()
        
        self.parentItem().setPos(
            self._last_parent_pos.x() + move_x,
            self._last_parent_pos.y() + move_y)
        pr = self.parentItem().rect()
        pr.setWidth(self._last_parent_rect.width() + resize_x)
        pr.setHeight(self._last_parent_rect.height() + resize_y)
        self.parentItem().setRect(pr)
