# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import QBuffer, QMimeData, QPoint, QRect, QRectF, QSize, Qt
from qtpy.QtGui import QClipboard, QIcon, QImage, QPainter
from qtpy.QtSvg import QSvgGenerator
from qtpy.QtWidgets import (
    QAction, QBoxLayout, QFileDialog, QGraphicsScene, QGraphicsView, QMenu,
    QWidget, qApp)
from qtpy.QtPrintSupport import QPrinter

class Window(QWidget):
    def __init__(self, item):
        super().__init__()
        
        self._shown = False
        
        scene = QGraphicsScene()
        self.scene = scene
        
        self.scene_item = item
        scene.addItem(item)

        layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        scene_view = View(self)
        self.scene_view = scene_view
        scene_view.setScene(scene)
        scene_view.setMinimumSize(350, 350)
        scene_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(scene_view)

        self.menus = []
        view_menu = QMenu("&View")
        self.menus.append(view_menu)
        export_menu = QMenu("&Export")
        self.menus.append(export_menu)

        self.tools = []
        
        fit_action = QAction("&Fit", self)
        fit_action.setShortcut("0")
        fit_action.setIcon(QIcon.fromTheme("zoom-fit-best"))
        fit_action.setStatusTip("Fit the entire scene to the viewport")
        fit_action.triggered.connect(self.scene_view.fit_all_in_view)
        view_menu.addAction(fit_action)
        self.tools.append(fit_action)
        
        reset_action = QAction("&Reset (1:1)", self)
        reset_action.setShortcut("9")
        reset_action.setIcon(QIcon.fromTheme("zoom-original"))
        reset_action.setStatusTip("Reset the view to 100% scale")
        reset_action.triggered.connect(self.scene_view.reset_scale)
        view_menu.addAction(reset_action)
        self.tools.append(reset_action)
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcuts(["+", "="])
        zoom_in_action.setStatusTip("Zoom in")
        zoom_in_action.triggered.connect(
            lambda: self.scene_view.zoom_in())
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcuts(["-","_"])
        zoom_out_action.setStatusTip("Zoom out")
        zoom_out_action.triggered.connect(
            lambda: self.scene_view.zoom_out())
        view_menu.addAction(zoom_out_action)
        
        export_svg_action = QAction("As &SVG...", self)
        export_svg_action.setStatusTip("Export the current tab as an SVG file")
        export_svg_action.triggered.connect(
            lambda: export_as_svg(self.scene))
        export_menu.addAction(export_svg_action)

        export_png_action = QAction("As PN&G...", self)
        export_png_action.setStatusTip("Export the current tab as an PNG file")
        export_png_action.triggered.connect(
            lambda: export_as_png(self.scene))
        export_menu.addAction(export_png_action)

        export_pdf_action = QAction("As &PDF...", self)
        export_pdf_action.setStatusTip("Export the current tab as an PDF file")
        export_pdf_action.triggered.connect(
            lambda: export_as_pdf(self.scene))
        export_menu.addAction(export_pdf_action)

        export_svg_clip_action = QAction("To Clipboard as SVG", self)
        export_svg_clip_action.setStatusTip(
            "Export the current tab to the clipoard in SVG format")
        export_svg_clip_action.triggered.connect(
            lambda: export_to_clipboard_as_svg(self.scene))
        export_menu.addAction(export_svg_clip_action)

        export_image_clip_action = QAction("To &Clipboard as Image", self)
        export_image_clip_action.setStatusTip(
            "Export the current tab to the clipoard as an image")
        export_image_clip_action.triggered.connect(
            lambda: export_to_clipboard_as_image(self.scene))
        export_menu.addAction(export_image_clip_action)

        self.resize(800, 600)

    def showEvent(self, event):
        if not self._shown:
            # Shift view to top-left corner when first shown
            self.scene_view.reset_scale()
            self._shown = True
        
    def mousePressEvent(self, event):
        # Allow scene item to know that the mouse was pressed outside
        # of any item.
        if hasattr(self.scene_item, "mouse_pressed_in"):
            self.scene_item.mouse_pressed_in(None)
        super().mousePressEvent(event)

class View(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)

        #self.pan_button = Qt.MiddleButton
        self.pan_button = Qt.RightButton # for testing w/ touchpad
        self.pan_modifier = Qt.ControlModifier
        self.key_zoom_increment = 0.1
        self.wheel_zoom_increment = 0.1
        self.wheel_zoom_in_factor = None # Override wheel_zoom_increment
        #self.wheel_zoom_out_factor = None # Override wheel_zoom_increment
        self.wheel_zoom_out_factor = 0.97 # Touch pad
        
        self._panning = False
        self._last_mouse_pos = None
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        
        self.verticalScrollBar().disconnect()
        self.horizontalScrollBar().disconnect()

    def resizeEvent(self,event):
        self._expand_scene_rect()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if (event.button() == self.pan_button or
            event.button() == Qt.LeftButton and
            event.modifiers() == self.pan_modifier):
            self._panning = True
            self._last_mouse_pos = event.pos()
            self._expand_scene_rect() # Allows panning when zoomed out
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (event.button() == self.pan_button or
            event.button() == Qt.LeftButton):
            self._panning = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos()
        if self._panning:
            delta_scene = self.mapToScene(mouse_pos) - self.mapToScene(
                self._last_mouse_pos)
            self.translate(delta_scene.x(), delta_scene.y())                
            self._last_mouse_pos = mouse_pos
        else:
            if hasattr(self.parent(), "mouse_move"):
                self.parent().mouse_move(event)
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            zoom_factor = (1 + self.wheel_zoom_increment
                           if self.wheel_zoom_in_factor is None else
                           self.wheel_zoom_in_factor)
        else:
            zoom_factor = (1 - self.wheel_zoom_increment
                           if self.wheel_zoom_out_factor is None else
                           self.wheel_zoom_out_factor)
        self._zoom(zoom_factor, event.pos())

    def keyPressEvent(self, event):
        key = event.key()
        if event.modifiers() & Qt.ControlModifier:
            if key == Qt.Key_Plus or key == Qt.Key_Equal:
                self.zoom_in()
            elif key == Qt.Key_Minus:
                self.zoom_out()
            elif key == Qt.Key_0:
                self.fit_all_in_view()
        super().keyPressEvent(event)

    def zoom_in(self, pos=None):
        if pos is None:
            pos = self._get_viewport_center()
        self._zoom(1 + self.key_zoom_increment, pos)
        
    def zoom_out(self, pos=None):
        if pos is None:
            pos = self._get_viewport_center()
        self._zoom(1 - self.key_zoom_increment, pos)
        
    def _zoom(self, factor, pos=None):
        if pos is not None:
            orig_scene_pos = self.mapToScene(pos)
        self.scale(factor, factor)
        self._expand_scene_rect()
        if pos is not None:
            # Keep the reference scene point in the same position while zooming
            new_scene_pos = self.mapToScene(pos)
            delta = new_scene_pos - orig_scene_pos
            self.translate(delta.x(), delta.y())
        
    def reset_scale(self):
        # Reset to native size and shift view to top-left corner
        self.resetTransform()
        br = self.scene().itemsBoundingRect()
        p = self.mapToScene(0,0)
        self.translate(p.x() - br.x(), p.y() - br.y())
        
    def fit_all_in_view(self):
        self._expand_scene_rect()
        br = self.scene().itemsBoundingRect()
        self.fitInView(br, Qt.KeepAspectRatio)
        delta = self.mapToScene(self._get_viewport_center()) - br.center()
        self.translate(delta.x(), delta.y())

    def _expand_scene_rect(self):
        vpc_pos = self._get_viewport_center()
        orig_vpc_scene_pos = self.mapToScene(vpc_pos)
        
        vpr_top_left = self.mapToScene(0, 0)
        vpr_bottom_right = self.mapToScene(
            self.viewport().width(), self.viewport().height())
        vpr_size = vpr_bottom_right - vpr_top_left
        
        # Make sure we have extra space in the scene to pan
        vsr_top_left = vpr_top_left - vpr_size
        vsr_bottom_right = vpr_bottom_right + vpr_size
        
        sr = self.scene().sceneRect()
        sr_top_left = sr.topLeft()
        sr_bottom_right = sr.bottomRight()

        vsr_top_left_x = min(vsr_top_left.x(), sr_top_left.x())
        vsr_top_left_y = min(vsr_top_left.y(), sr_top_left.y())
        vsr_bottom_right_x = max(vsr_bottom_right.x(), sr_bottom_right.x())
        vsr_bottom_right_y = max(vsr_bottom_right.y(), sr_bottom_right.y())
            
        vsr = QRectF(
            vsr_top_left_x, vsr_top_left_y,
            vsr_bottom_right_x - vsr_top_left_x,
            vsr_bottom_right_y - vsr_top_left_y)
        self.setSceneRect(vsr)

        # Make sure expanding scene doesn't shift the view area
        new_vpc_scene_pos = self.mapToScene(vpc_pos)
        delta = new_vpc_scene_pos - orig_vpc_scene_pos
        self.translate(delta.x(), delta.y())
        
    def _get_viewport_center(self):
        return QPoint(self.viewport().width() // 2,
                      self.viewport().height() // 2)

def export_as_svg(scene, file_name=None):
    if file_name is None:
        file_name, selected_filter = QFileDialog.getSaveFileName(
            None, caption="Export to SVG",
            filter="SVG Files (*.svg)")
        if not file_name:
            return
    
    print(f"exporting SVG to file: {file_name}")    
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(file_name)
    render_to_svggen(scene, svg_gen)

def export_to_clipboard_as_svg(scene):
    print(f"exporting SVG to clipboard")
    buffer = QBuffer()
    svg_gen = QSvgGenerator()
    svg_gen.setOutputDevice(buffer)
    render_to_svggen(scene, svg_gen)
    data = QMimeData()
    data.setData("image/svg+xml", buffer.buffer())
    qApp.clipboard().setMimeData(data, QClipboard.Clipboard)

def render_to_svggen(scene, svg_gen):
    svg_gen.setSize(QSize(scene.width(), scene.height()))
    svg_gen.setViewBox(QRect(0, 0, scene.width(), scene.height()))
    svg_gen.setTitle("Hierarchic Component Drawing")
    svg_gen.setDescription("A Hierarchic Component Drawing created by "
                          "Hildegard.")
    painter = QPainter()
    painter.begin(svg_gen)
    painter.setRenderHint(QPainter.Antialiasing)
    scene.render(painter)
    painter.end()
    
def export_as_png(scene, file_name=None):
    if file_name is None:
        file_name, selected_filter = QFileDialog.getSaveFileName(
            None, caption="Export to PNG",
            filter="PNG Files (*.png)")
        if not file_name:
            return
    
    print(f"exporting PNG to file: {file_name}")
    image = render_image(scene)
    image.save(file_name)
    qApp.clipboard().setImage(image, QClipboard.Clipboard)

def export_to_clipboard_as_image(scene):
    print(f"exporting PNG to clipboard")
    image = render_image(scene)
    qApp.clipboard().setImage(image, QClipboard.Clipboard)

def render_image(scene):
    image = QImage(scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    scene.render(painter)
    painter.end()
    return image

def export_as_pdf(scene, file_name=None):
    if file_name is None:
        file_name, selected_filter = QFileDialog.getSaveFileName(
            None, caption="Export to PDF",
            filter="PNG Files (*.pdf)")
        if not file_name:
            return
    
    print(f"exporting scene to PDF: {file_name}")
    printer = QPrinter (QPrinter.HighResolution)
    printer.setPageSize(QPrinter.Letter)
    r = scene.sceneRect()
    if r.width() < r.height():
        printer.setOrientation(QPrinter.Portrait)
    else:
        printer.setOrientation(QPrinter.Landscape)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(file_name)
    painter = QPainter(printer)
    scene.render(painter)
    painter.end()
