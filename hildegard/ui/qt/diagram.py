# Copyright (c) 2020 Jeffrey A. Webb

from . import receptor
from . import scene
from . import resizer
from ...diagram import Block, Connector

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
        elif key == Qt.Key_Escape:
            self.parentItem().setFocus()
        super().keyPressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.parentItem()._connector.name = self.toPlainText()
        r = self.parentItem().rect()
        r.setWidth(self.boundingRect().width())
        self.parentItem().setRect(r)
        self.parentItem().parentItem().parentItem()._ensure_minimum_size()
        super().focusOutEvent(event)
        
class Connector_Item(QGraphicsRectItem):
    def __init__(self, connector, parent_item=None, debug=False):
        self._connector = connector
        self._debug = debug
        self._title = Connector_Title(self._connector.name)
        self._moved_since_click = False
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

    def focusInEvent(self, event):
        self.setPen(QPen(Qt.black))
        self.setBrush(QBrush(Qt.gray))
        super().focusOutEvent(event)
        
    def focusOutEvent(self, event):
        self._set_default_appearance()
        super().focusOutEvent(event)
        
    def keyPressEvent(self, event):
        key = event.key()
        if (key == Qt.Key_Delete or key == Qt.Key_D):
            self.parentItem().parentItem().remove_connector(self)
        super().keyPressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        if ((self.flags() & self.ItemIsMovable) and
            event.button() == Qt.LeftButton):
            self._title.setTextInteractionFlags(Qt.TextEditable)
            self._title.setFocus()
            cursor = self._title.textCursor()
            cursor.select(cursor.LineUnderCursor)
            self._title.setTextCursor(cursor)
        super().mouseDoubleClickEvent(event)
            
    def mousePressEvent(self, event):
        if ((self.flags() & self.ItemIsMovable) and
            event.button() == Qt.LeftButton):
            self._moved_since_click = False
            self.parentItem().parentItem().handle_connector_start_move(self)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.flags() & self.ItemIsMovable:
            self._moved_since_click = True
            self.parentItem().parentItem().handle_connector_move(self)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if ((self.flags() & self.ItemIsMovable) and
            event.button() == Qt.LeftButton):
            if self._moved_since_click:
                disregard = False
            else:
                disregard = True
            self.parentItem().parentItem().handle_connector_end_move(
                self, disregard=disregard)
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
        self.setFlag(self.ItemIsFocusable)
        
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
            sensitive=False,
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
        
        self._resizer = resizer.Frame(self, debug=self._debug)

        self._ensure_minimum_size()
        self._set_editing_mode(self._editing)

    def handle_connector_start_move(self, connector):
        self._start_move_connector_row = connector._connector.row
        connector._connector.row = None
        self._update_receptor_sensitivities()
        
    def handle_connector_move(self, connector):
        pos = connector.rect().center() + connector.pos()
        r, c = self._insert_receptors.highlight_sensitive_cell_at(pos)
        if r is None:
            self._receptors.highlight_sensitive_cell_at(pos)
        else:
            # Reset the appearance of the selected standard receptor,
            # if a sensitive insert receptor is highlighted.
            self._receptors.reset_appearance()

    def handle_connector_end_move(self, connector, disregard=False):
        action = None
        prev_r = self._start_move_connector_row
        prev_c = connector._connector.col
        pos = connector.rect().center() + connector.pos()
        r, c = self._insert_receptors.get_sensitive_cell_at(pos)
        if disregard:
            connector._connector.row = self._start_move_connector_row
            action = f"no movement"
        else:
            if r is not None: # Insert extra row
                action = f"insert at {r} {c}"
                self._insert_connector_at(connector, r, c)
            else:
                r, c = self._receptors.get_sensitive_cell_at(pos)
                if r is not None: # Move to open row
                    action = f"move to {r} {c}"
                    self._move_connector_to(connector, r, c)
                else: # Aborted move
                    connector._connector.row = self._start_move_connector_row
                    action = f"aborted move"
        #print(f"released {connector._connector.name} "
        #      f"({prev_r} {prev_c}): action: {action}")
        self._receptors.reset_appearance()
        self._insert_receptors.reset_appearance()        
        self._ensure_minimum_size()
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._editing:
                # See if we are at an open location for a connector
                self._update_receptor_sensitivities()
                r, c = self._receptors.get_sensitive_cell_under_mouse()
                if r is not None:
                    # Note that this connector should really be associated
                    # with some port on this block's component, but that
                    # is not required at this time.
                    new_c = Connector(name="Untitled",row=r, col=c)
                    new_item = Connector_Item(
                        new_c, parent_item=self._connector_layer,
                        debug=self._debug)
                    new_item.setFlag(self.ItemIsMovable)
                    new_item.setFlag(self.ItemIsFocusable)
                    new_c.row = None
                    self._connectors.append(new_item)
                    self._move_connector_to(new_item, r, c)
                    self._ensure_minimum_size()
                    # Start editing connector title immediately
                    new_item._title.setTextInteractionFlags(Qt.TextEditable)
                    new_item._title.setFocus()
                    cursor = new_item._title.textCursor()
                    cursor.select(cursor.LineUnderCursor)
                    new_item._title.setTextCursor(cursor)
            else:
                if self._title_rect.contains(event.pos()):
                    self._set_editing_mode(True)
                else:
                    self._set_editing_mode(True)
        super().mouseDoubleClickEvent(event)
        
    def mousePressEvent(self, event):
        self.parentItem().mouse_pressed_in(self)
        super().mousePressEvent(event)

    def mouse_pressed_outside_item(self):
        self._set_editing_mode(False)

    def remove_connector(self, connector):
        self._connectors.remove(connector)
        connector.setParentItem(None)
        self._update_geometry()
        
    def _set_editing_mode(self, editing):
        self._editing = editing
        self._resizer.set_resizing_mode(self._editing)
        if self._editing:
            self.setFocus()
            self.setPen(QPen(Qt.red,2))
            self._title_rect.setPen(QPen(Qt.red,2))
            self._base_zvalue = self.zValue()
            self.setZValue(self._top_zvalue)
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable)
                c.setFlag(self.ItemIsFocusable)
        else:
            self.setPen(QPen(Qt.black,2))
            self._title_rect.setPen(QPen(Qt.black,2))
            if self._base_zvalue is not None:
                self.setZValue(self._base_zvalue)
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable, False)
                c.setFlag(self.ItemIsFocusable, False)
        
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
            
        # Add extra height to always allow inserting after last row
        min_height = min_height + 4
        
        self._resizer.min_width = min_width
        self._resizer.min_height = min_height
        
        r = self.rect()
        r.setWidth(max(min_width,r.width()))
        r.setHeight(max(min_height,r.height()))
        self.setRect(r) # note that this calls self._update_geometry()
        
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
        
    def _update_receptor_sensitivities(self):
        self._insert_receptors.set_all_cell_sensitivities(False)
        self._receptors.set_all_cell_sensitivities(True)

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

        # If the last visible receptor row is occupied
        last_visible_receptor_row_i = self._receptors.get_num_visible_rows() - 1
        if last_visible_receptor_row_i == last_ri:
            # If the following insert receptor is visible
            last_visible_irow_i = \
                self._insert_receptors.get_num_visible_rows() - 1
            if last_visible_irow_i == last_ri + 1:
                # Add insert receptors after the last row
                for cii in range(3):
                    self._insert_receptors.set_cell_sensitivity(
                        last_ri + 1, cii, True)
        
    def _update_geometry(self):
                
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
            
        self._receptors.update_geometry()
        self._insert_receptors.update_geometry()
        self._resizer.update_geometry()

    def setRect(self, r):
        super().setRect(r)
        self._update_geometry()
        
class Diagram_Item(QGraphicsItem):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.view_items = []
        for i, (s_name, s) in enumerate(
                self.view.symbols.items()):
            s_ui = Block_Item(s, debug=False)
            s_ui.moveBy(200*i,0)
            s_ui.setParentItem(self)
            self.view_items.append(s_ui)

    # Allow diagram elements to know that the mouse was pressed
    # outside of the element
    def mouse_pressed_in(self, source_item):
        for item in self.view_items:
            if source_item != item:
                item.mouse_pressed_outside_item()
                
    # Implement pure virtual method
    def paint(self, *args, **kw):
        pass
    
    # Implement pure virtual method
    def boundingRect(self, *args, **kw):
        return QRectF(0,0,0,0)
    
class Diagram_Editor(scene.Window):
    def __init__(self, view):
        self.view_item = Diagram_Item(view)
        super().__init__(self.view_item)
        self.view = view
        
    def mousePressEvent(self, event):
        # Allow diagram elements to know that the mouse was pressed
        # outside of the element
        self.view_item.mouse_pressed_in(None)
        super().mousePressEvent(event)
