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

class Connector_Title(QGraphicsTextItem):
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            cursor = self.textCursor()
            cursor.movePosition(cursor.Left)
            self.setTextCursor(cursor)
        elif key == Qt.Key_Right:
            cursor = self.textCursor()
            cursor.movePosition(cursor.Right)
            self.setTextCursor(cursor)
        super().keyPressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.parentItem()._connector.name = self.toPlainText()
        super().focusOutEvent(event)
        
class Connector_Item(QGraphicsRectItem):
    def __init__(self, connector, parent_item=None, debug=False):
        self._connector = connector
        self._debug = debug
        self._title = Connector_Title(self._connector.name)
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

    def mouseDoubleClickEvent(self, event):
        if self.flags() & self.ItemIsMovable:
            self._title.setTextInteractionFlags(Qt.TextEditable)
            self._title.setFocus()
        super().mouseDoubleClickEvent(event)
            
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

        self._base_zvalue = None
        self._top_zvalue = 1
        self._vpad = 5
        self._footer_height = self._vpad
        self._editing = False
        self._start_move_connector_row = None
        
        super().__init__(0, 0, 120, 200)
        self.setBrush(QBrush(Qt.gray))
        self.setFlag(self.ItemIsMovable)
        
        t = self._title = QGraphicsTextItem(self._block.name)
        t.setParentItem(self)
        t.setPos(0, self._vpad)
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
            bottom_border=self._footer_height,
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

        self._ensure_minimum_size()
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
        prev_r = self._start_move_connector_row
        prev_c = connector._connector.col
        r, c = self._insert_receptors.highlight_sensitive_cell_under_mouse()
        if r is not None: # Insert extra row
            action = f"insert at {r} {c}"
            self._insert_connector_at(connector, r, c)
        else:
            r, c = self._receptors.highlight_sensitive_cell_under_mouse()
            if r is not None: # Move to open row
                action = f"move to {r} {c}"
                self._move_connector_to(connector, r, c)
            else: # Aborted move
                connector._connector.row = self._start_move_connector_row
                action = f"aborted move"
        #print(f"released {connector._connector.name} "
        #      f"({prev_r} {prev_c}): action: {action}")
        self._ensure_minimum_size()
        self._do_update()
        
    def mouseDoubleClickEvent(self, event):
        self._editing = not self._editing
        self._resizer.resizing = self._editing
        if self._editing:
            self._base_zvalue = self.zValue()
            self.setZValue(self._top_zvalue)
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable)
        else:
            self.setZValue(self._base_zvalue)
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable, False)
        self._do_update()

    def _ensure_minimum_size(self):
        min_width = self._title.boundingRect().width()
        min_height = self._header_height + self._footer_height

        occupied_cols = self._get_occupied_cols()
        occupied_rows = sorted(occupied_cols.keys())
        for ri in occupied_rows:
            min_row_w = 0
            for ci in occupied_cols[ri]:
                con = self._find_connector_at(ri, ci)
                min_row_w = min_row_w + con.rect().width()
            min_width = max(min_width, min_row_w)
        if occupied_rows:
            min_height = min_height + (max(occupied_rows) + 1)*self._row_height
            
        self._resizer.min_width = min_width
        self._resizer.min_height = min_height
        
        r = self.rect()
        r.setWidth(max(min_width,r.width()))
        r.setHeight(max(min_height,r.height()))
        self.setRect(r)
        
    def _get_sorted_connectors(self):
        return sorted(
            self._connectors, key=lambda x:
            x._connector.row if x._connector.row is not None
            else -10)

    def _get_occupied_cols(self):
        # Search through the connectors in order of the row position
        occupied_cols = {}
        for c in self._connectors:
            ri = c._connector.row
            if not ri in occupied_cols:
                occupied_cols[ri] = []
            occupied_cols[ri].append(c._connector.col)
        return occupied_cols
    
    def _find_connector_at(self, row, col):
        for c in self._connectors:
            ri = c._connector.row
            ci = c._connector.col
            if ri == row and ci == col:
                return c
        return None
        
    def _move_connector_to(self, connector, row, col):
        occupied_cols = self._get_occupied_cols()
        # If we are inserting into a row with another cell
        if row in occupied_cols:
            # If we are inserting on the left
            if col == 0:
                center_c = self._find_connector_at(row, 1)
                # Move any existing centered port to the right
                if center_c is not None:
                    center_c._connector.col = 2
            # If we are inserting in the center
            elif col == 1:
                left_c = self._find_connector_at(row, 0)
                # Insert to the right of the existing left connector
                if left_c is not None:
                    col = 2
                right_c = self._find_connector_at(row, 2)
                # Insert to the left of the existing right connector
                if right_c is not None:
                    col = 0
            # If we are inserting on the right
            elif col == 2:
                center_c = self._find_connector_at(row, 1)
                # Move any existing centered port to the left
                if center_c is not None:
                    center_c._connector.col = 0
        connector._connector.row = row
        connector._connector.col = col
        
    def _insert_connector_at(self, connector, row, col):
        sorted_connectors = self._get_sorted_connectors()
        last_r = -1
        for c in sorted_connectors:
            r = c._connector.row
            if r is None:
                # This connector is being moved, so disregard it
                continue
            # For existing rows on or after the insert row index
            if r >= row:
                # If there is a gap
                if r - last_r > 1:
                    # Stop shifting the rows down
                    break
                # Shift the row down
                c._connector.row = r + 1
            last_r = r
        connector._connector.row = row
        connector._connector.col = col
        
    def _update_sensitivity(self):
        self._insert_receptors.set_all_cell_sensitivity(False)
        self._receptors.set_all_cell_sensitivity(True)

        occupied_cols = self._get_occupied_cols()
            
        # Search through the connectors in order of the row position
        sorted_connectors = self._get_sorted_connectors()
        last_ri = -1
        for c in sorted_connectors:
            ri = c._connector.row
            ci = c._connector.col
            if ri is None:
                # This connector is being moved, so disregard it
                continue
            # Moving to populated locations is not permitted
            if ci in occupied_cols[ri]:
                self._receptors.set_cell_sensitivity(ri, ci, False)
            # Moving to a cell in a row with two connectors is not permitted
            if len(occupied_cols[ri]) > 1:
                self._receptors.set_cell_sensitivity(ri, 1, False)
            # If there is a gap between two consecutive rows
            if ri == last_ri + 1:
                # Add insert receptors between the rows
                for cii in range(3):
                    self._insert_receptors.set_cell_sensitivity(ri, cii, True)
            last_ri = ri
    
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
            ri = c._connector.row
            ci = c._connector.col
            if ri is not None:
                if ci == 0:
                    x = 0
                elif ci == 2:
                    x = w - c.rect().width()
                else:
                    x = (w - c.rect().width())/2.0
                c.setPos(x, self._header_height + ri*self._row_height)
            
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
