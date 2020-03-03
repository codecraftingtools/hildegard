# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush, QPen
from qtpy.QtWidgets import QGraphicsRectItem

class Frame:
    def __init__(self, parent_item, resizing=False, debug=False):
        self.min_width = 0
        self.min_height = 0
        self._handles = [
            Handle(self, parent_item, "BR", False, debug),
            Handle(self, parent_item, "BR", True,  debug),
            Handle(self, parent_item, "TR", False, debug),
            Handle(self, parent_item, "TR", True,  debug),
            Handle(self, parent_item, "BL", False, debug),
            Handle(self, parent_item, "BL", True,  debug),
            Handle(self, parent_item, "TL", False, debug),
            Handle(self, parent_item, "TL", True,  debug),
            Handle(self, parent_item, "B",  False, debug),
            Handle(self, parent_item, "T",  False, debug),
            Handle(self, parent_item, "L",  True,  debug),
            Handle(self, parent_item, "R",  True,  debug),
        ]
        self.set_resizable(resizing)
        
    def update_geometry(self):
        # Update the resizer handle positions and sizes based on the
        # geometry of the parent QGraphicsRectItem. This method should
        # be called whenever the parent item is resized.
        for h in self._handles:
            h.update_geometry()
            
    def set_resizable(self, resizing):
        # Update the resizer handle appearance and movability based on
        # the specified resizing state.
        for h in self._handles:
            h.set_resizable(resizing)
            
class Handle(QGraphicsRectItem):
    def __init__(self, frame, parent, anchor, vertical=False, debug=False):
        self._frame = frame
        self._anchor = anchor
        self._debug = debug
        
        self._border = 10
        self._side = 30
        self._last_mouse_scene_pos = None
        self._last_parent_rect = None
        self._last_parent_pos = None

        if vertical:
            w = self._border
            h = self._side
        else:
            w = self._side
            h = self._border
        if anchor in ["BR", "TR", "R"]:
            x = self._side - w
        elif anchor in ["BL", "TL", "B", "T", "L"]:
            x = 0
        if anchor in ["BR", "BL", "B"]:
            y = self._side - h
        elif anchor in ["TR", "TL", "T", "R", "L"]:
            y = 0
        super().__init__(x, y, w, h)
        
        self.setParentItem(parent)
        self.update_geometry()
        self.set_resizable(False)
        
    def update_geometry(self):
        # Update the resizer handle positions and sizes based on the
        # geometry of the parent QGraphicsRectItem. This method should
        # be called whenever the parent item is resized.
        parent = self.parentItem()

        if self._anchor in ["BR", "TR", "R"]:
            x = parent.rect().width() - self._side
        elif self._anchor in ["BL", "TL", "L"]:
            x = 0
        elif self._anchor in ["B", "T"]:
            x = self._side
        if self._anchor in ["BR", "BL", "B"]:
            y = parent.rect().height() - self._side
        elif self._anchor in ["TR", "TL", "T"]:
            y = 0
        elif self._anchor in ["R", "L"]:
            y = self._side
        self.setPos(x, y)
        
        if self._anchor in ["B", "T"]:
            r = self.rect()
            r.setWidth(parent.rect().width() - 2*self._side)
            self.setRect(r)
        if self._anchor in ["R", "L"]:
            r = self.rect()
            r.setHeight(parent.rect().height() - 2*self._side)
            self.setRect(r)
            
    def set_resizable(self, resizing):
        # Update the resizer handle appearance and movability based on
        # the specified resizing state.
        if resizing:
            if self._debug:
                if self._anchor in ["B", "T", "R", "L"]:
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

        min_width = max(self._frame.min_width, 2*self._side)
        min_height = max(self._frame.min_height, 2*self._side)
        
        if self._anchor in ["BR", "TR", "R"]:
            min_delta_p_x = -(self._last_parent_rect.width() - min_width)
        elif self._anchor in ["BL", "TL", "L"]:
            max_delta_p_x = self._last_parent_rect.width() - min_width
        elif self._anchor in ["B", "T"]:
            min_delta_p_x = 0
            max_delta_p_x = 0
        if self._anchor in ["BR", "BL", "B"]:
            min_delta_p_y = -(self._last_parent_rect.height() - min_height)
        elif self._anchor in ["TR", "TL", "T"]:
            max_delta_p_y = self._last_parent_rect.height() - min_height
        elif self._anchor in ["R", "L"]:
            min_delta_p_y = 0
            max_delta_p_y = 0

        if min_delta_p_x is not None and delta_p.x() < min_delta_p_x:
            delta_p.setX(min_delta_p_x)
        if max_delta_p_x is not None and delta_p.x() > max_delta_p_x:
            delta_p.setX(max_delta_p_x)
        if min_delta_p_y is not None and delta_p.y() < min_delta_p_y:
            delta_p.setY(min_delta_p_y)
        if max_delta_p_y is not None and delta_p.y() > max_delta_p_y:
            delta_p.setY(max_delta_p_y)

        if self._anchor in ["BR", "TR", "R"]:
            move_x = 0
            resize_x = delta_p.x()
        elif self._anchor in ["BL", "TL", "L"]:
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
        elif self._anchor in ["R", "L"]:
            move_y = 0
            resize_y = 0
        
        self.parentItem().setPos(
            self._last_parent_pos.x() + move_x,
            self._last_parent_pos.y() + move_y)
        pr = self.parentItem().rect()
        pr.setWidth(self._last_parent_rect.width() + resize_x)
        pr.setHeight(self._last_parent_rect.height() + resize_y)
        self.parentItem().setRect(pr)
