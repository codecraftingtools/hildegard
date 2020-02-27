# Copyright (c) 2020 Jeffrey A. Webb

from . import receptor
from . import scene
from .resizer import Rect_Resizer
from ...diagram import Block

from qtpy.QtCore import QRectF, Qt
from qtpy.QtGui import QBrush, QPen
from qtpy.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
)

class Connector_Item(QGraphicsRectItem):
    def __init__(self, connector, parent_item=None):
        self._connector = connector
        self._title = QGraphicsTextItem(self._connector.name)
        title_br = self._title.boundingRect()
        super().__init__(0, 0, title_br.width(), title_br.height())
        self._title.setParentItem(self)
        if parent_item:
            self.setParentItem(parent_item)
        self.setPen(QPen(Qt.black));
        self.setBrush(QBrush(Qt.gray));
        
    def mouseMoveEvent(self, event):
        self.parentItem().parentItem().handle_connector_move(self, event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.parentItem().parentItem().handle_connector_release(self, event)
        super().mouseReleaseEvent(event)
        
class Block_Item(QGraphicsRectItem):
    def __init__(self, block, debug=False):
        self._block = block
        self._debug = debug
        
        pad = self._pad = 5
        self._editing = False

        super().__init__(0, 0, 120, 200)
        self.setBrush(QBrush(Qt.gray))
        self.setFlag(self.ItemIsMovable)
        
        t = self._title = QGraphicsTextItem(self._block.name)
        t.setParentItem(self)
        t.setPos(2*pad, 2*pad)
        #t.setZValue(1)
        title_br = t.boundingRect()
        text_height = title_br.height()
        self._row_height = text_height + 2*pad
        
        tr = self._title_rect = QGraphicsRectItem(
            0, 0, title_br.width() + 4*pad, title_br.height() + 3*pad)
        tr.setBrush(QBrush(Qt.darkGray))
        tr.setParentItem(self)
        self._title.setParentItem(tr)
        
        cl = self._connector_layer = QGraphicsRectItem(self.rect())
        cl.setParentItem(self)
        cl.setBrush(QBrush(Qt.NoBrush))
        #cl.setBrush(QBrush(Qt.blue))
        cl.setPen(QPen(Qt.NoPen))

        self._connectors = []
        for i, (c_name, c) in enumerate(block.connectors.items()):
            new_item = Connector_Item(c, parent_item=self._connector_layer)
            self._connectors.append(new_item)
            
        rl = self._receptor_layer = QGraphicsRectItem(self.rect())
        rl.setParentItem(self)
        rl.setBrush(QBrush(Qt.NoBrush))
        #rl.setBrush(QBrush(Qt.blue))
        rl.setPen(QPen(Qt.NoPen))
        
        self._receptors = receptor.Grid(
            parent_item=self._receptor_layer, n_cols=3,
            cell_height=text_height, row_spacing=2*self._pad,
            top_border=4*self._pad+text_height,
            bottom_border=2*self._pad,
            debug_color=Qt.cyan,
            debug=self._debug,
        )

        irl = self._insert_receptor_layer = QGraphicsRectItem(self.rect())
        irl.setParentItem(self)
        irl.setBrush(QBrush(Qt.NoBrush))
        #irl.setBrush(QBrush(Qt.blue))
        irl.setPen(QPen(Qt.NoPen))
        
        self._insert_receptors = receptor.Grid(
            parent_item=self._insert_receptor_layer, n_cols=3,
            cell_height=self._pad*2, row_spacing=text_height,
            top_border=2*self._pad+text_height,
            stretch_last_row=True,
            sensitive=False,
            debug_color=Qt.yellow,
            debug=self._debug,
        )
        for c in range(3):
            self._insert_receptors.set_cell_sensitivity(0, c, True)
        
        self._resizer = Rect_Resizer(self, debug=self._debug)

        self._do_update()

    def handle_connector_move(self, connector, event):
        self._receptors.highlight_sensitive_cell_under_mouse()
        self._insert_receptors.highlight_sensitive_cell_under_mouse()

    def handle_connector_release(self, connector, event):
        action = None
        r, c = self._receptors.highlight_sensitive_cell_under_mouse()
        if r is not None:
            action = f"move to {r} {c}"
            connector._connector.row = r
        else:
            r, c = self._insert_receptors.highlight_sensitive_cell_under_mouse()
            action = f"insert at {r} {c}"
        print(f"released {connector._connector.name} "
              f"({connector._connector.row}): action: {action}")
        self._do_update()
        
    def mouseDoubleClickEvent(self, event):
        self._editing = not self._editing
        self._resizer.resizing = self._editing
        if self._editing:
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable)
        else:
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable, False)
        self._do_update()
        
    def _do_update(self):
        if self._editing:
            self.setPen(QPen(Qt.red,2))
            self._title_rect.setPen(QPen(Qt.red,2))
        else:
            self.setPen(QPen(Qt.black,2))
            self._title_rect.setPen(QPen(Qt.black,2))
        
        r = self.rect()
        self._connector_layer.setRect(r)
        self._receptor_layer.setRect(r)
        self._insert_receptor_layer.setRect(r)
        w = r.width()

        tw = self._title.boundingRect().width()
        self._title.setX((w - tw)/2.0)
        tor = self._title_rect.rect()
        tor.setWidth(w)
        self._title_rect.setRect(tor)

        for c in self._connectors:
            i = c._connector.row
            c.setPos(self._pad,self._pad+(i+1)*self._row_height)
            
        self._receptors.update_cells()
        self._insert_receptors.update_cells()
        
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
            s_ui = Block_Item(s, debug=False)
            s_ui.moveBy(200*i,0)
            s_ui.setParentItem(self)

    # Implement pure virtual method
    def paint(self, *args, **kw):
        pass
    
    # Implement pure virtual method
    def boundingRect(self, *args, **kw):
        return QRectF(0,0,0,0)
    
class Diagram_Editor(scene.Window):
    def __init__(self, view):
        ui = Diagram_Item(view)
        super().__init__(ui)
        self.view = view
