# Copyright (c) 2020 Jeffrey A. Webb

from .receptor import Receptor_Grid
from .resizer import Rect_Resizer
from .scene_util import Scene_Window
from ...diagram import Block

from qtpy.QtCore import QRectF, Qt
from qtpy.QtGui import QBrush, QPen
from qtpy.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
)

class Connector_Item(QGraphicsRectItem):
    def __init__(self, connector, *args, **kw):
        self._connector = connector
        super().__init__(*args, **kw)
        
    def mouseMoveEvent(self, event):
        self.parentItem().parentItem().connector_move(self, event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.parentItem().parentItem().connector_release(self, event)
        super().mouseReleaseEvent(event)
        
class Block_Item(QGraphicsRectItem):
    def __init__(self, block):
        self._block = block
        self._editing = False

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
        
        title = QGraphicsTextItem(self._block.name)
        self._title = title
        title.setParentItem(self)
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
        
        self._receptors = Receptor_Grid(
            parent_item=self._receptor_area, n_cols=3,
            cell_height=self._text_height, row_spacing=2*self._pad,
            top_border=4*self._pad+self._text_height,
            #debug_color=Qt.cyan,
            bottom_border=2*self._pad,
        )
        self._ireceptors = Receptor_Grid(
            parent_item=self._receptor_area, n_cols=3,
            cell_height=self._pad*2, row_spacing=self._text_height,
            top_border=2*self._pad+self._text_height,
            #debug_color=Qt.yellow,
            stretch_last_row=True,
            active=False,
        )
        for c in range(3):
            self._ireceptors.set_active(0, c, True)
        
        self._connectors = []
        for i, (c_name, c) in enumerate(block.connectors.items()):
            new_r = Connector_Item(c, 0,0,30,self._row_height)
            new_r.setFlag(self.ItemIsMovable)
            new_r.setParentItem(self._area)
            new_r.setPen(QPen(Qt.black));
            new_r.setBrush(QBrush(Qt.NoBrush));
            new_r.setPos(self._pad,self._pad+(i+1)*self._row_height)
            self._connectors.append(new_r)
            
        self._resizer = Rect_Resizer(self, debug=False)
        self._do_update()

    def connector_move(self, connector, event):
        self._receptors.highlight_cell_under_mouse()
        self._ireceptors.highlight_cell_under_mouse()

    def connector_release(self, connector, event):
        print("release", connector._connector.name, connector._connector.row)
        self._receptors.update_cells()
        self._ireceptors.update_cells()
        
    def mouseDoubleClickEvent(self, event):
        self._editing = not self._editing
        self._resizer.resizing = self._editing
        if self._editing:
            self.setPen(QPen(Qt.red))
        else:
            self.setPen(QPen(Qt.black))
        self._do_update()
        
    def _do_update(self):
        r = self.rect()
        self._area.setRect(r)
        self._receptor_area.setRect(r)
        w = r.width()
        h = r.height()

        self._receptors.update_cells()
        self._ireceptors.update_cells()
        
        tw = self._title.boundingRect().width()
        self._title.setX((w - tw)/2.0)
        tor = self._title_outline.rect()
        tor.setWidth(w)
        self._title_outline.setRect(tor)

        self._resizer.update_handles()
        
    def setRect(self, r):
        super().setRect(r)
        self._do_update()
        
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
    
class Diagram_Editor(Scene_Window):
    def __init__(self, view):
        ui = Diagram_Item(view)
        super().__init__(ui)
        self.view = view
