# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush, QPen
from qtpy.QtWidgets import QGraphicsRectItem

class Receptor(QGraphicsRectItem):
    def __init__(self, *args, active=True, **kw):
        super().__init__(*args, **kw)
        self.active = active
        
class Receptor_Grid:
    def __init__(
            self, parent_item, n_rows=None, n_cols=None,
            cell_size=None, cell_width=None, cell_height=None,
            spacing=0, row_spacing=None, col_spacing=None,
            border=0, top_border=None, bottom_border=None,
            left_border=None, right_border=None,
            stretch_last_row=False, stretch_last_col=False,
            debug_color=None, active=True):
        self._parent_item = parent_item
        self._n_rows = n_rows
        self._n_cols = n_cols
        self._cell_width = cell_width if cell_width is not None else cell_size
        self._cell_height = cell_height if cell_height is not None else cell_size
        self._row_spacing = (row_spacing if row_spacing is not None else
                             spacing)
        self._col_spacing = (col_spacing if col_spacing is not None else
                             spacing)
        self._top_border = top_border if top_border is not None else border
        self._bottom_border = (bottom_border if bottom_border is not None else
                               border)
        self._left_border = left_border if left_border is not None else border
        self._right_border = (right_border if right_border is not None else
                              border)
        self._stretch_last_row = stretch_last_row
        self._stretch_last_col = stretch_last_col
        self._debug_color = debug_color
        self._active = active
        self._cells = []
        self.update_cells()

    def _reset_cell(self, cell):
        if self._debug_color:
            cell.setPen(QPen(Qt.black));
            cell.setBrush(QBrush(self._debug_color));
        else:
            cell.setPen(QPen(Qt.NoPen));
            cell.setBrush(QBrush(Qt.NoBrush));

    def set_active(self, r, c, active):
        self._cells[r][c].active = active
        
    def highlight_cell_under_mouse(self):
        r, c = None, None
        for ri, row in enumerate(self._cells):
            for ci, cell in enumerate(row):
                if cell.isVisible() and cell.isUnderMouse() and cell.active:
                    cell.setBrush(QBrush(Qt.green));
                    r, c = ri, ci
                else:
                    self._reset_cell(cell)
        return r, c
    
    def update_cells(self):
        parent_r = self._parent_item.rect()
        h = parent_r.height() - self._top_border - self._bottom_border
        w = parent_r.width() - self._left_border - self._right_border

        if self._n_rows is None:
            v_interval = self._cell_height + self._row_spacing
            max_rows = int(h // v_interval)
            h_remaining = h - max_rows*v_interval
            if h_remaining >= self._cell_height:
                max_rows = max_rows + 1
            n_rows = max_rows
            cell_h = self._cell_height
            if self._stretch_last_row:
                last_cell_h = h - (n_rows - 1)*v_interval
            else:
                last_cell_h = cell_h
        else:
            n_rows = self._n_rows
            space = (n_rows - 1) * self._row_spacing
            cell_h = (h - space) / n_rows
            last_cell_h = cell_h
            
        if self._n_cols is None:
            h_interval = self._cell_width + self._col_spacing
            max_cols = int(w // h_interval)
            w_remaining = w - max_cols*h_interval
            if w_remaining >= self._cell_width:
                max_cols = max_cols + 1
            n_cols = max_cols
            cell_w = self._cell_width
            if self._stretch_last_col:
                last_cell_w = w - (n_cols - 1)*h_interval
            else:
                last_cell_w = cell_w
        else:
            n_cols = self._n_cols
            space = (n_cols - 1) * self._col_spacing
            cell_w = (w - space) / n_cols
            last_cell_w = cell_w
            
        for ri in range(n_rows):
            if ri >= len(self._cells):
                self._cells.append([])
            row = self._cells[ri]
            for ci in range(n_cols):
                if ci >= len(row):
                    r = Receptor(0, 0, cell_w, cell_h, active=self._active)
                    r.setParentItem(self._parent_item)
                    r.setOpacity(0.5)
                    row.append(r)
                cell = row[ci]
                cell_r = cell.rect()
                if ci == n_cols - 1:
                    cell_r.setWidth(last_cell_w)
                else:
                    cell_r.setWidth(cell_w)
                if ri == n_rows - 1:
                    cell_r.setHeight(last_cell_h)
                else:
                    cell_r.setHeight(cell_h)
                cell.setRect(cell_r)
                cell_x = self._left_border + ci*(cell_w+self._col_spacing)
                cell_y = self._top_border + ri*(cell_h+self._row_spacing)
                cell.setX(cell_x)
                cell.setY(cell_y)
                
        for ri, row in enumerate(self._cells):
            for ci, cell in enumerate(row):
                if ri >= n_rows or ci >= n_cols :
                    cell.hide()
                else:
                    self._reset_cell(cell)
                    cell.show()
