# Copyright (c) 2020 Jeffrey A. Webb

from . import receptor
from . import scene
from . import resizer
from ... import diagram

import adaptagrams as avoid

from qtpy.QtCore import QPointF, QRectF, Qt
from qtpy.QtGui import (
    QBrush, QColor, QPainterPath, QPainterPathStroker, QPen, QPolygonF)
from qtpy.QtWidgets import (
    QGraphicsItem, QGraphicsLineItem, QGraphicsPathItem, QGraphicsPolygonItem,
    QGraphicsRectItem, QGraphicsTextItem)

from math import sqrt

class Title(QGraphicsTextItem):
    def start_editing(self):
        self.setTextInteractionFlags(Qt.TextEditable)
        self.setFocus()
        cursor = self.textCursor()
        cursor.select(cursor.LineUnderCursor)
        self.setTextCursor(cursor)

    def _stop_editing(self):
        pass

    def _set_text(self, name):
        pass
    
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
            self._stop_editing()
        else:
            self._set_text(self.toPlainText())
        super().keyPressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        self._stop_editing()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self._set_text(self.toPlainText())
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

class Connector_Title(Title):
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if not self.toPlainText():
            connector_item = self.parentItem()
            self.setParentItem(None)
            connector_item.parentItem().parentItem().remove_connector(
                connector_item)
        
    def _stop_editing(self):
        self.parentItem().setFocus()

    def _set_text(self, name):
        self.parentItem()._connector.name = name
        r = self.parentItem().rect()
        r.setWidth(self.boundingRect().width())
        self.parentItem().setRect(r)
        self.parentItem().parentItem().parentItem()._ensure_minimum_size()
    
class Block_Title(Title):
    def _stop_editing(self):
        self.parentItem().parentItem().setFocus()

    def _set_text(self, name):
        self.parentItem().parentItem()._block.name = name
        self.parentItem().parentItem()._ensure_minimum_size()
        
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
        self.setPen(QPen(Qt.red))
        self.setBrush(QBrush(
            self.parentItem().parentItem().highlight_background_color))
        super().focusInEvent(event)
        
    def focusOutEvent(self, event):
        self._set_default_appearance()
        super().focusOutEvent(event)
        
    def keyPressEvent(self, event):
        key = event.key()
        if (key == Qt.Key_Delete):
            self.parentItem().parentItem().remove_connector(self)
        elif (key == key == Qt.Key_E):
            self._title.start_editing()
        elif (key == key == Qt.Key_N):
            self.parentItem().parentItem().append_new_connector(
                after=self, edit=True)
            return
        super().keyPressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        if ((self.flags() & self.ItemIsMovable) and
            event.button() == Qt.LeftButton):
            self._title.start_editing()
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

    def get_connection_point(self):
        if self.parentItem() is None:
            return None, None
        x = self.x()
        if self._connector.col == 2:
            x = x + self.rect().width()
        elif self._connector.col == 1:
            x = x + self.rect().width() / 2.0
        y = self.y() + self.rect().height() / 2.0
        return x, y
        
class Block_Item(QGraphicsRectItem):
    def __init__(self, block, debug=False):
        self._block = block
        self._debug = debug
        self.modified = False
        
        self._base_zvalue = None
        self._top_zvalue = 1
        self._vpad = 5
        self._footer_height = self._vpad
        self._editing = False
        self._start_move_connector_row = None
        self.highlight_background_color = QColor(255,127,127,255)
        
        super().__init__(0, 0, 120, 200)
        self.setBrush(QBrush(Qt.gray))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsFocusable)
        self.setFlag(self.ItemSendsGeometryChanges)

        t = self._title = Block_Title(self._block.name)
        t.setParentItem(self)
        t.setPos(0, self._vpad)
        text_height = t.boundingRect().height()
        
        self._row_height = text_height
        self._insert_receptor_height = text_height/2.0
        self._header_height = text_height + 2*self._vpad
        self._grid_size = self._row_height / 2.0
        
        tr = self._title_rect = QGraphicsRectItem(
            0, 0, 10, self._header_height) # width set later
        tr.setParentItem(self)
        self._title.setParentItem(tr)
        
        cl = self._connector_layer = QGraphicsRectItem(self.rect())
        cl.setParentItem(self)
        cl.setBrush(QBrush(Qt.NoBrush))
        #cl.setBrush(QBrush(Qt.blue))
        cl.setPen(QPen(Qt.NoPen))

        self._connectors = []
        for i, c in enumerate(block.connectors):
            self.add_connector(c, quick=True)
            
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

        self._header_avoid_shape = None
        self._row_avoid_shapes = []
        self._row_divider_avoid_shapes = []
        self._footer_avoid_shape = None
        self._avoid_shape = None
        
        self._ensure_minimum_size()
        self._set_default_appearance()
        self.set_editing_mode(self._editing)
        self.modified = False

    def handle_connector_start_move(self, connector):
        self._start_move_connector_row = connector._connector.row
        connector._connector.row = None
        self._update_receptor_sensitivities()
        
    def handle_connector_move(self, connector):
        pos = connector.rect().center() + connector.pos()
        r, c = self._insert_receptors.get_cell_at(
            pos=pos, sensitive=True, highlight=True)
        if r is None:
            self._receptors.get_cell_at(
                pos=pos, sensitive=True, highlight=True)
        else:
            # Reset the appearance of the selected standard receptor,
            # if a sensitive insert receptor is highlighted.
            self._receptors.reset_appearance()

    def handle_connector_end_move(self, connector, disregard=False):
        action = None
        prev_r = self._start_move_connector_row
        prev_c = connector._connector.col
        pos = connector.rect().center() + connector.pos()
        r, c = self._insert_receptors.get_cell_at(pos=pos, sensitive=True)
        if disregard:
            connector._connector.row = self._start_move_connector_row
            action = f"no movement"
        else:
            if r is not None: # Insert extra row
                action = f"insert at {r} {c}"
                self._insert_connector_at(connector, r, c)
            else:
                r, c = self._receptors.get_cell_at(pos=pos, sensitive=True)
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
                r, c = self._receptors.get_cell_at(mouse=True, sensitive=True)
                if r is not None:
                    new_c = self.add_new_connector_at(r, c, edit=True)
                elif self._title.boundingRect().contains(
                        self._title.mapFromParent(event.pos())):
                    self._title.start_editing()
                elif self._title_rect.contains(event.pos()):
                    if not self._title.toPlainText():
                        self._title.start_editing()
            else:
                in_existing_connector = None
                for c in self._connectors:
                    if c.contains(c.mapFromParent(event.pos())):
                        in_existing_connector = c
                        break
                if in_existing_connector:
                    if self.parentItem():
                        start_c = self.parentItem(
                            ).connection_in_progress_from
                        if not start_c:
                            if self.parentItem().connect_on_double_click:
                                self.parentItem().start_connecting(c, event)
                                return
                else:
                    self.set_editing_mode(True)
        super().mouseDoubleClickEvent(event)
        
    def mousePressEvent(self, event):
        parent_item = self.parentItem()
        if parent_item:
            parent_item.connect_on_double_click = True
        if event.button() == Qt.LeftButton and parent_item:
           in_existing_connector = None
           for c in self._connectors:
               if c.contains(c.mapFromParent(event.pos())):
                   in_existing_connector = c
                   break
           if in_existing_connector:
               start_c = self.parentItem(
                   ).connection_in_progress_from
               if start_c:
                   self.parentItem().finish_connecting(c)
                   self.parentItem().connect_on_double_click = False
                   self.clearFocus()
        if parent_item:
            parent_item.mouse_pressed_in(self)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if (key == Qt.Key_Delete):
            parent_item = self.parentItem()
            if parent_item:
                parent_item.remove_block(self)
        elif (key == key == Qt.Key_N):
            self.append_new_connector(edit=True)
        super().keyPressEvent(event)
        
    def mouse_pressed_in(self, source_item):
        self.set_editing_mode(False)

    def remove_all_connectors(self):
        for c in list(self._connectors):
            self.remove_connector(c)
            
    def remove_connector(self, connector):
        self._connectors.remove(connector)
        connector.setParentItem(None)
        self._update_geometry()
        self._block.connectors.remove(connector._connector)
        
    def add_connector(self, connector, quick=False):
        new_item = Connector_Item(
            connector, parent_item=self._connector_layer, debug=self._debug)
        if self._editing:
            new_item.setFlag(self.ItemIsMovable)
            new_item.setFlag(self.ItemIsFocusable)
        if not quick:
            self._ensure_minimum_size()
        self._connectors.append(new_item)
        if not connector in self._block.connectors:
            self._block.connectors.append(connector)
        return new_item
    
    def add_new_connector_at(self, r, c, quick=False, edit=True):
        # Note that this connector should really be associated
        # with some port on this block's component, but that
        # is not required at this time.
        new_c = diagram.Connector(name="Untitled",row=r, col=c)
        new_c.row = None
        new_item = self.add_connector(new_c, quick=quick)
        self._move_connector_to(new_item, r, c)
        if not quick:
            self._ensure_minimum_size()
        if edit:
            new_item._title.start_editing()
        return new_item
    
    def append_new_connector(self, after=None, edit=True):
        if after is None:
            row = 0
            col = 1
        else:
            row = after._connector.row
            col = after._connector.col
            
        occupied_cols = self._get_occupied_cols()
        while True:
            if not row in occupied_cols:
                break
            else:
                taken_cols = occupied_cols[row]
                if not col in taken_cols and len(taken_cols) < 2:
                    break
                row = row + 1
        self.add_new_connector_at(row, col, edit=True)
        
    def focusInEvent(self, event):
        self.setPen(QPen(Qt.red,2))
        self._title_rect.setPen(QPen(Qt.red,2))
        super().focusInEvent(event)
        
    def focusOutEvent(self, event):
        self._set_default_appearance()
        super().focusOutEvent(event)

    def _set_default_appearance(self):
        self.setPen(QPen(Qt.black,2))
        self._title_rect.setPen(QPen(Qt.black,2))
        
    def set_editing_mode(self, editing, edit_title=False):
        self._editing = editing
        self._resizer.set_resizable(self._editing)
        if self._editing:
            self.setFocus()
            self._title_rect.setBrush(QBrush(self.highlight_background_color))
            self.setBrush(QBrush(QColor(255,127,127,255)))
            self._base_zvalue = self.zValue()
            self.setZValue(self._top_zvalue)
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable)
                c.setFlag(self.ItemIsFocusable)
        else:
            self._title_rect.setBrush(QBrush(Qt.darkGray))
            self.setBrush(QBrush(Qt.lightGray))
            if self._base_zvalue is not None:
                self.setZValue(self._base_zvalue)
            for c in self._connectors:
                c.setFlag(self.ItemIsMovable, False)
                c.setFlag(self.ItemIsFocusable, False)
        if edit_title:
            self._title.start_editing()

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
                self._receptors.set_cell_sensitivity_at(ri, ci, False)
            # Moving to a cell in a row with two connectors is not permitted
            if len(occupied_cols[ri]) > 1:
                self._receptors.set_cell_sensitivity_at(ri, 1, False)
            # If there is a gap between two consecutive rows
            if ri == last_ri + 1:
                # Add insert receptors between the rows
                for cii in range(3):
                    self._insert_receptors.set_cell_sensitivity_at(ri, cii, True)
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
                    self._insert_receptors.set_cell_sensitivity_at(
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

        self._update_avoid()

        self._block.width = r.width()
        self._block.height = r.height()
        
    def setRect(self, r):
        # Snap size to grid
        w = r.width()
        extra_w = w % self._grid_size
        if extra_w > 0.25:
            w = (1 + (w // self._grid_size)) * self._grid_size
        r.setWidth(w)
        h = r.height()
        extra_h = h % self._grid_size
        if extra_h > 0.25:
            h = (1 + (h // self._grid_size)) * self._grid_size
        r.setHeight(h)
                
        super().setRect(r)
        self._update_geometry()

    def _update_avoid(self):
        self.modified = True
        if self.parentItem():
            avoid_router = self.parentItem().avoid_router
            r = self.rect()

            # Header area
            avoid_rect = avoid.AvoidRectangle(
                avoid.Point(self.x(), self.y()),
                avoid.Point(self.x() + r.width(),
                            self.y() + self._header_height))
            if self._header_avoid_shape is None:
                self._header_avoid_shape = avoid.ShapeRef(
                    avoid_router, avoid_rect)
            else:
                avoid_router.moveShape(self._header_avoid_shape, avoid_rect)

            # Row areas
            occupied_cols = self._get_occupied_cols()
            n_avoid_rows = len(self._row_avoid_shapes)
            n_visible_rows = self._receptors.get_num_visible_rows()
            for ri in range(n_visible_rows):
                if (not ri in occupied_cols or
                    len(occupied_cols[ri]) == 0 or
                    1 in occupied_cols[ri]):
                    x = self.x()
                    w = r.width()
                elif len(occupied_cols[ri]) > 1:
                    w = r.width() / 2.0
                    x = self.x() + w/2.0
                elif 2 in occupied_cols[ri]:
                    x = self.x()
                    w = r.width() / 2.0
                elif 0 in occupied_cols[ri]:
                    w = r.width() / 2.0
                    x = self.x() + w
                avoid_rect = avoid.AvoidRectangle(
                    avoid.Point(
                        x,
                        self.y() + self._header_height + ri*self._row_height),
                    avoid.Point(
                        x + w,
                        self.y() + self._header_height+(ri+1)*self._row_height))
                divider_avoid_rect = avoid.AvoidRectangle(
                    avoid.Point(
                        self.x() - self.parentItem().pin_length,
                        self.y() + self._header_height + ri*self._row_height),
                    avoid.Point(
                        self.x() + r.width() + self.parentItem().pin_length,
                        self.y() + self._header_height+ri*self._row_height+2))
                if ri >= n_avoid_rows:
                    self._row_avoid_shapes.append(
                        avoid.ShapeRef(avoid_router, avoid_rect))
                    self._row_divider_avoid_shapes.append(
                        avoid.ShapeRef(avoid_router, divider_avoid_rect))
                else:
                    avoid_router.moveShape(
                        self._row_avoid_shapes[ri], avoid_rect)
                    avoid_router.moveShape(
                        self._row_divider_avoid_shapes[ri], divider_avoid_rect)
            for ri in range(n_avoid_rows):
                if ri >= n_visible_rows:
                    avoid_rect = avoid.AvoidRectangle(
                        avoid.Point(self.x(), self.y()),
                        avoid.Point(self.x(), self.y()))
                    avoid_router.moveShape(
                        self._row_avoid_shapes[ri], avoid_rect)
                    avoid_router.moveShape(
                        self._row_divider_avoid_shapes[ri], avoid_rect)
                
            # Footer area
            avoid_rect = avoid.AvoidRectangle(
                avoid.Point(self.x() - self.parentItem().pin_length,
                            self.y() + r.height() - self._footer_height),
                avoid.Point(self.x() + r.width() + self.parentItem().pin_length,
                            self.y() + r.height()))
            if self._footer_avoid_shape is None:
                self._footer_avoid_shape = avoid.ShapeRef(
                    avoid_router, avoid_rect)
            else:
                avoid_router.moveShape(self._footer_avoid_shape, avoid_rect)

            # Full block
            avoid_rect = avoid.AvoidRectangle(
                avoid.Point(self.x(), self.y()),
                avoid.Point(self.x() + r.width(),
                            self.y() + r.height()))
            if self._avoid_shape is None:
                self._avoid_shape = avoid.ShapeRef(avoid_router, avoid_rect)
            else:
                avoid_router.moveShape(self._avoid_shape, avoid_rect)
            self.parentItem().process_avoid_updates()
            
    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            # Snap position to grid
            x = value.x()
            extra_x = x % self._grid_size
            if extra_x > 0.25:
                x = (1 + (x // self._grid_size)) * self._grid_size
            value.setX(x)
            y = value.y()
            extra_y = y % self._grid_size
            if extra_y > 0.25:
                y = (1 + (y // self._grid_size)) * self._grid_size
            value.setY(y)
            return value
        elif change == self.ItemPositionHasChanged:
            self._update_avoid()
            self._block.x = self.x()
            self._block.y = self.y()
        return super().itemChange(change, value)
        
    def setParentItem(self, parent_item):
        super().setParentItem(parent_item)
        self._update_avoid()
        
class Connection_Item(QGraphicsPathItem):
    def __init__(self, connection, parent):
        super().__init__()
        self._connection = connection
        self._source_ui = self._find_ui(parent, connection.source)
        self._sink_ui = self._find_ui(parent, connection.sink)
        self.avoid_conn = None
        self._duplicate_is = None
        self._duplicate_of = None
        self._switch_direction_count = 1
        self.path = QPainterPath()
        self.stroker_path = QPainterPath()
        self.stroker = QPainterPathStroker()
        self.stroker.setWidth(8)
        self.update_endpoints()
        self.setZValue(-10)
        self.arrow = QGraphicsPolygonItem()
        self._set_default_appearance()
        self.setFlag(self.ItemIsFocusable)

    def shape(self):
        return self.stroker_path
    
    def setPath(self, path):
        super().setPath(path)
        self.stroker_path = self.stroker.createStroke(path)
        
    def _set_default_appearance(self):
        self.setPen(QPen(Qt.black,2))
        self.arrow.setPen(QPen(Qt.black))
        self.arrow.setBrush(QBrush(Qt.black))
        
    def focusInEvent(self, event):
        self.setPen(QPen(Qt.red,2))
        self.arrow.setPen(QPen(Qt.red))
        self.arrow.setBrush(QBrush(Qt.red))
        super().focusInEvent(event)
        
    def focusOutEvent(self, event):
        self._set_default_appearance()
        super().focusOutEvent(event)
        
    def keyPressEvent(self, event):
        key = event.key()
        if (key == Qt.Key_Delete):
            self.parentItem().remove_connection(self)
            return
        elif (key == Qt.Key_D):
            self._switch_direction()
            return
        super().keyPressEvent(event)

    def _switch_direction(self):
        if self._duplicate_is:
            self.parentItem().remove_connection(self._duplicate_is)
            self._switch_direction_count = 0
        elif self._switch_direction_count < 2:
            sink = self._connection.sink
            self._connection.sink = self._connection.source
            self._connection.source = sink
            self._source_ui = self._find_ui(
                self.parentItem(), self._connection.source)
            self._sink_ui = self._find_ui(
                self.parentItem(), self._connection.sink)
            self._switch_direction_count += 1
        else:
            conn = diagram.Connection(
                source=self._connection.sink,
                sink=self._connection.source,
            )
            self.parentItem().add_connection(conn)
            self._switch_direction_count = 3
        self.update_endpoints()
        self.parentItem()._hide_duplicate_connections()
        if self._switch_direction_count == 0:
            self._switch_direction()
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._switch_direction()
            return # Do not call mousePressEvent, will pass on to diagram
        super().mouseDoubleClickEvent(event)
        
    def _find_ui(self, parent, c):
        result = None
        for b_ui in parent._block_items:
            for c_ui in b_ui._connectors:
                if c_ui._connector == c:
                    return c_ui
        return result

    def _get_endpoint(self, c_ui):
        x, y = c_ui.get_connection_point()
        if x is None:
            return None, None
        p = self.mapToParent(
            self.mapFromScene(c_ui.parentItem().mapToScene(x, y)))
        return p.x(), p.y()
    
    def update_endpoints(self):
        self.x1, self.y1 = self._get_endpoint(self._source_ui)
        self.x2, self.y2 = self._get_endpoint(self._sink_ui)
        if self.x1 is None or self.x2 is None:
            return False
        self.path = QPainterPath()
        self.path.moveTo(self.x1, self.y1)
        self.path.lineTo(self.x2, self.y2)
        self.setPath(self.path)
        self._update_avoid()
        return True
    
    def _update_avoid(self):
        if self.parentItem():
            avoid_router = self.parentItem().avoid_router
            src = avoid.ConnEnd(avoid.Point(self.x1, self.y1))
            if self.isVisible():
                dest = avoid.ConnEnd(avoid.Point(self.x2, self.y2))
            else:
                dest = src # Don't route duplicate connection
            if self.avoid_conn is None:
                self.avoid_conn = avoid.ConnRef(avoid_router, src, dest)
            else:
                self.avoid_conn.setEndpoints(src, dest)

    def update_from_avoid_router(self):
        if self.avoid_conn is not None and self.avoid_conn.needsRepaint():
            radius = self.parentItem().route_radius
            route = self.avoid_conn.displayRoute()
            self.path = QPainterPath()
            last_i = route.size() - 1
            for i in range(0, route.size()):
                point = route.at(i)
                if i > 0:
                    last_point = route.at(i-1)
                    last_path_point = self.path.currentPosition()
                    if point.y == last_point.y: # horizontal line
                        if point.x > last_point.x: # right
                            sign = 1
                        else: # left
                            sign = -1
                        self.path.quadTo(
                            last_point.x,last_point.y,
                            last_point.x+sign*radius, point.y)
                        if i == last_i:
                            my_x = point.x
                        else:
                            my_x = point.x-sign*radius
                        self.path.lineTo(my_x, point.y)
                    elif point.x == last_point.x: # vertical line
                        if point.y > last_point.y: # down
                            sign = 1
                        else: # up
                            sign = -1
                        self.path.quadTo(
                            last_point.x,last_point.y,
                            point.x, last_point.y+sign*radius)
                        if i == last_i:
                            my_y = point.y
                        else:
                            my_y = point.y-sign*radius
                        self.path.lineTo(point.x, my_y)
                    else:
                        self.path.lineTo(point.x, point.y)
                else:
                    self.path.moveTo(point.x, point.y)
            self.setPath(self.path)

            sink = self._sink_ui
            entry_from = "L"
            x = 0
            if route.at(route.size()-1).x < route.at(route.size()-2).x:
                entry_from = "R"
                x = sink.parentItem().rect().width()
            if self._duplicate_of:
                route = self._duplicate_of.avoid_conn.displayRoute()
                if route.at(0).x < route.at(1).x:
                    entry_from = "R"
                    x = sink.parentItem().rect().width()
            y = sink.y() + sink.rect().height() / 2.0            
            p = self.mapToParent(
                self.mapFromScene(sink.parentItem().mapToScene(x, y)))
            xc, yc = p.x(), p.y()
            arrow_h = 8
            arrow_y = arrow_h/2.0
            arrow_x = sqrt(arrow_h*arrow_h - arrow_y*arrow_y)
            poly = QPolygonF()
            if entry_from == "L":
                poly << QPointF(xc-arrow_x,yc)
                poly << QPointF(xc-arrow_x, yc+arrow_y)
                poly << QPointF(xc, yc)
                poly << QPointF(xc-arrow_x, yc-arrow_y)
                poly << QPointF(xc-arrow_x,yc)
            else:
                poly << QPointF(xc+arrow_x,yc)
                poly << QPointF(xc+arrow_x, yc+arrow_y)
                poly << QPointF(xc, yc)
                poly << QPointF(xc+arrow_x, yc-arrow_y)
                poly << QPointF(xc+arrow_x,yc)
            self.arrow.setPolygon(poly)
            
    def setParentItem(self, parent_item):
        super().setParentItem(parent_item)
        self._update_avoid()

class Diagram_Item(QGraphicsItem):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.modified = False
        self.connection_in_progress_from = None
        self.connection_in_progress_line = None
        self.connect_on_double_click = True
        self.avoid_router = avoid.Router(
            #avoid.PolyLineRouting)
            avoid.OrthogonalRouting)
        self.avoid_router.setRoutingParameter(
            avoid.shapeBufferDistance, 10.0)
        self.avoid_router.setRoutingParameter(
            avoid.idealNudgingDistance, 10.0)
        self.avoid_router.setRoutingParameter(
            avoid.crossingPenalty, 50000000)
        self.route_radius = 6.0
        self.pin_length = 10.0
        self._connection_items = []
        self._block_items = []
        for i, s in enumerate(self.view.symbols):
            w = s.width
            h = s.height
            s_ui = self.add_block(s, debug=False)
            s_ui.moveBy(s.x, s.y)
            r = s_ui.rect()
            r.setWidth(w)
            r.setHeight(h)
            s_ui.setRect(r)
            s_ui._ensure_minimum_size()
        for c in self.view.connections:
            self.add_connection(c)
        self.process_avoid_updates()
        self.modified = False

    def double_clicked_in_background(self, scene_pos):
        # Note that this block should really be associated with
        # some component, but that is not required at this time.
        b = diagram.Block(name="Untitled")
        b_item = self.add_block(b, debug=False)
        b_item.setPos(b_item.mapFromScene(scene_pos))
        b_item.set_editing_mode(True, edit_title=True)
        return True # Do not call mouseDoubleClickEvent, will stop editing
    
    def mouse_moved_in_scene(self, scene_pos):
        diagram = self
        if diagram.connection_in_progress_from:
            diagram_pos = diagram.mapFromScene(scene_pos)
            x1 = diagram.connection_in_progress_line.line().x1()
            y1 = diagram.connection_in_progress_line.line().y1()
            diagram.connection_in_progress_line.setLine(
                x1, y1, diagram_pos.x(), diagram_pos.y())
        
    def start_connecting(self, c, event):
        self.connection_in_progress_from = c
        x, y = c.get_connection_point()
        p1 = self.mapToParent(
            self.mapFromScene(c.parentItem().mapToScene(x, y)))
        x1 = p1.x()
        y1 = p1.y()
        p2 = self.mapFromScene(event.scenePos())
        self.connection_in_progress_line = QGraphicsLineItem(
            x1, y1, p2.x(), p2.y())
        self.connection_in_progress_line.setParentItem(self)
        c._title.setDefaultTextColor(Qt.red)
        
    def finish_connecting(self, c):
        start_c = self.connection_in_progress_from
        if c != start_c:
            conn = diagram.Connection(
                source=start_c._connector,
                sink=c._connector,
            )
            self._stop_connecting()
            self.add_connection(conn)
            self.process_avoid_updates()
        else:
            self.abort_connecting(c)

    def abort_connecting(self, source_item=None):
        if source_item:
            if self.connection_in_progress_from:
                source_item.clearFocus()
        self._stop_connecting()
        
    def _stop_connecting(self):
        start_c = self.connection_in_progress_from
        if start_c:
            start_c._title.setDefaultTextColor(Qt.black)
            self.connection_in_progress_from = None
            self.connection_in_progress_line.setParentItem(None)
            self.connection_in_progress_line = None
        
    def add_connection(self, connection):
        c_ui = Connection_Item(connection, self)
        c_ui.setParentItem(self)
        c_ui.arrow.setParentItem(self)
        self._connection_items.append(c_ui)
        self._hide_duplicate_connections()
        if not connection in self.view.connections:
            self.view.connections.append(connection)
        return c_ui

    def remove_connection(self, c_ui):
        self.avoid_router.deleteConnector(c_ui.avoid_conn)
        self._connection_items.remove(c_ui)
        c_ui.setParentItem(None)
        c_ui.arrow.setParentItem(None)
        self._hide_duplicate_connections()
        self.view.connections.remove(c_ui._connection)

    def add_block(self, block, debug=False):
        s_ui = Block_Item(block, debug=debug)
        s_ui.setParentItem(self)
        self._block_items.append(s_ui)
        if not block in self.view.symbols:
            self.view.symbols.append(block)
        return s_ui
    
    def remove_block(self, block):
        self._block_items.remove(block)
        block.remove_all_connectors()
        block.setParentItem(None)
        self.view.symbols.remove(block._block)
        
    def mouse_pressed_in(self, source_item):
        # Allow diagram elements to know that the mouse was pressed
        # outside of the element.
        for item in self._block_items:
            if source_item != item:
                item.mouse_pressed_in(source_item)
        self.abort_connecting(source_item)
        
    def paint(self, *args, **kw):
        # Implement pure virtual method
        pass
    
    def boundingRect(self, *args, **kw):
        # Implement pure virtual method
        return QRectF(0,0,0,0)

    def process_avoid_updates(self):
        for c_ui in list(self._connection_items):
            success = c_ui.update_endpoints()
            if not success:
                self.remove_connection(c_ui)
        self.avoid_router.processTransaction()
        for c_ui in self._connection_items:
            c_ui.update_from_avoid_router()
        self.modified = True

    def _hide_duplicate_connections(self):
        processed_connections = []
        for c in self._connection_items:
            c._duplicate_is = None
            c._duplicate_of = None
            c.show()
            for p in processed_connections:
                if (c._sink_ui == p._source_ui and
                    c._source_ui == p._sink_ui):
                    c.hide()
                    p._duplicate_is = c
                    c._duplicate_of = p
            processed_connections.append(c)
        self.process_avoid_updates()
        
class Diagram_Editor(scene.Item_Viewer):
    def __init__(self, view):
        super().__init__(Diagram_Item(view))
        self.view = view
