# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtWidgets import QGraphicsItem, QGraphicsItemGroup, QGraphicsRectItem

def add_resizers(parent):
    return (
        Rect_Resizer(parent, vertical=False),
        Rect_Resizer(parent, vertical=True),
    )
    
class Rect_Resizer(QGraphicsRectItem):
    def __init__(self, parent, vertical=False):
        self._border = 10
        self._side = 40
        if vertical:
            super().__init__(self._side - self._border, 0,
                             self._border, self._side)
        else:
            super().__init__(0, self._side - self._border,
                             self._side, self._border)
        self.setParentItem(parent)
        self._update()
        self.setFlag(self.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
    def _update(self):
        parent = self.parentItem()
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPos(parent.rect().width() - self._side,
                    parent.rect().height() - self._side)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            min_pos = self._side*2
            if value.x() < min_pos:
                value.setX(min_pos)
            if value.y() < min_pos:
                value.setY(min_pos)
            delta = value - self.pos()
            pr = self.parentItem().rect()
            pr.setWidth(pr.width() + delta.x())
            pr.setHeight(pr.height() + delta.y())
            self.parentItem().setRect(pr)
        return value
