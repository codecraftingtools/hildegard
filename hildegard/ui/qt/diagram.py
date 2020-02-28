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
    def __init__(self, connector, parent_item=None, debug=False):
        self._connector = connector
        self._debug = debug
        self._title = QGraphicsTextItem(self._connector.name)
        title_br = self._title.boundingRect()
        super().__init__(0, 0, title_br.width(), title_br.height())
        self._title.setParentItem(self)
        if parent_item:
            self.setParentItem(parent_item)
        self._set_default_appearance()
 
    def _set_default_appearance(self):
        if self._debug:
            self.setPen(QPen(Qt.black))
        else:
            self.setPen(QPen(Qt.NoPen))
        self.setBrush(QBrush(Qt.NoBrush))

    def mousePressEvent(self, event):
        if self.flags() & self.ItemIsMovable:
            self.setPen(QPen(Qt.black))
            self.setBrush(QBrush(Qt.gray))
            self.parentItem().parentItem().handle_connector_start_move(
                self, event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.parentItem().parentItem().handle_connector_move(self, event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._set_default_appearance()
        self.parentItem().parentItem().handle_connector_end_move(self, event)
        super().mouseReleaseEvent(event)
        
class Block_Item(QGraphicsRectItem):
    def __init__(self, block, debug=False):
        self._block = block
        self._debug = debug
        
        self._vpad = 5
        self._editing = False
        self._start_move_connector_row = None
        
        super().__init__(0, 0, 120, 200)
        self.setBrush(QBrush(Qt.gray))
        self.setFlag(self.ItemIsMovable)
        
        t = self._title = QGraphicsTextItem(self._block.name)
        t.setParentItem(self)
        t.setPos(0, self._vpad)
        #t.setZValue(1)
        text_height = t.boundingRect().height()
        
        self._row_height = text_height
        self._insert_receptor_height = text_height/2.0
        self._header_height = text_height + 2*self._vpad
        
        tr = self._title_rect = QGraphicsRectItem(
            0, 0, 10, self._header_height) # width set later
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
            new_item = Connector_Item(
                c, parent_item=self._connector_layer, debug=self._debug)
            self._connectors.append(new_item)
            
        rl = self._receptor_layer = QGraphicsRectItem(self.rect())
        rl.setParentItem(self)
        rl.setBrush(QBrush(Qt.NoBrush))
        #rl.setBrush(QBrush(Qt.blue))
        rl.setPen(QPen(Qt.NoPen))
        
        self._receptors = receptor.Grid(
            parent_item=self._receptor_layer, n_cols=3,
            cell_height=self._row_height,
            top_border=self._header_height,
            bottom_border=self._vpad,
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
            cell_height=self._insert_receptor_height,
            row_spacing=self._row_height - self._insert_receptor_height,
            top_border=self._header_height - self._insert_receptor_height/2.0,
            stretch_last_row=True,
            sensitive=False,
            debug_color=Qt.yellow,
            debug=self._debug,
        )
        
        self._resizer = Rect_Resizer(self, debug=self._debug)

        self._do_update()

    def handle_connector_start_move(self, connector, event):
        self._start_move_connector_row = connector._connector.row
        connector._connector.row = None
        self._update_sensitivity()
        
    def handle_connector_move(self, connector, event):
        r, c = self._insert_receptors.highlight_sensitive_cell_under_mouse()
        if r is None:
            self._receptors.highlight_sensitive_cell_under_mouse()
        else:
            self._receptors.update_cells()

    def handle_connector_end_move(self, connector, event):
        action = None
        r, c = self._insert_receptors.highlight_sensitive_cell_under_mouse()
        if r is not None:
            action = f"insert at {r} {c}"
            self._insert_connector_at(connector, r)
        else:
            r, c = self._receptors.highlight_sensitive_cell_under_mouse()
            if r is not None:
                action = f"move to {r} {c}"
                connector._connector.row = r
            else:
                connector._connector.row = self._start_move_connector_row
                action = f"aborted move"
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

    def _get_sorted_connectors(self):
        return sorted(
            self._connectors, key=lambda x:
            x._connector.row if x._connector.row is not None
            else -10)

    def _insert_connector_at(self, connector, index):
        sorted_connectors = self._get_sorted_connectors()
        last_r = -1
        for c in sorted_connectors:
            r = c._connector.row
            if r is None:
                # This connector is being moved, so disregard it
                continue
            # For existing rows on or after the insert index
            if r >= index:
                # If there is a gap
                if r - last_r > 1:
                    # Stop shifting the rows down
                    break
                # Shift the row down
                c._connector.row = r + 1
            last_r = r
        connector._connector.row = index
        
    def _update_sensitivity(self):
        self._insert_receptors.set_all_cell_sensitivity(False)
        self._receptors.set_all_cell_sensitivity(True)

        # Search through the connectors in order of the row position
        sorted_connectors = self._get_sorted_connectors()
        last_r = -1
        for c in sorted_connectors:
            r = c._connector.row
            if r is None:
                # This connector is being moved, so disregard it
                continue
            # Moving to populated rows is not permitted
            for c in range(3):
                self._receptors.set_cell_sensitivity(r, c, False)
            # If there is a gap between two consecutive rows
            if r == last_r + 1:
                # Add insert receptors between the rows
                for c in range(3):
                    self._insert_receptors.set_cell_sensitivity(r, c, True)
            last_r = r
    
    def _do_update(self):
        self._update_sensitivity()
        
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
            if i is not None:
                c.setPos(0, self._header_height + i*self._row_height)
            
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
