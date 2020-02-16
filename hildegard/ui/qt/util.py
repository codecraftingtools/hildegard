# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt, QSize, QRect, QRectF, QPoint
from qtpy.QtGui import QPainter
from qtpy.QtSvg import QSvgGenerator
from qtpy.QtWidgets import QBoxLayout, QGraphicsScene, QGraphicsView, QWidget

class Scene_Window(QWidget):
    def __init__(self, ui):
        super().__init__()
        
        layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        scene = QGraphicsScene()
        self.scene = scene
        
        scene_view = Scene_View(self)
        self.scene_view = scene_view
        scene_view.setScene(scene)
        scene_view.setMinimumSize(350, 350)
        scene_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(scene_view)

        scene.addItem(ui)
            
        self.resize(800, 600)

class Scene_View(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)

        #self.pan_button = Qt.MiddleButton
        self.pan_button = Qt.RightButton # for testing w/ touchpad
        self.pan_modifier = Qt.ShiftModifier
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

    def fit_all_in_view(self):
        self._expand_scene_rect()
        br = self.scene().itemsBoundingRect()
        self.fitInView(br, Qt.KeepAspectRatio)
        delta = self.mapToScene(self._get_viewport_center()) - br.center()
        self.translate(delta.x(), delta.y())

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
        pos = self._get_viewport_center()
        if key == Qt.Key_Plus or key == Qt.Key_Equal:
            self._zoom(1 + self.key_zoom_increment, pos)
        elif key == Qt.Key_Minus:
            self._zoom(1 - self.key_zoom_increment, pos)
        elif key == Qt.Key_0:
            self.fit_all_in_view()
        super().keyPressEvent(event)

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
    
def export_scene_as_svg(scene, file_name=None):
    if file_name is None:
        file_name = "out.svg"
    
    print(f"exporting SVG to file: {file_name}")
    
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(file_name)
    svg_gen.setSize(QSize(scene.width(), scene.height()))
    svg_gen.setViewBox(QRect(0, 0, scene.width(), scene.height()))
    svg_gen.setTitle("Hierarchic Component Drawing")
    svg_gen.setDescription("A Hierarchic Component Drawing created by "
                          "Hildegard.")
    
    painter = QPainter()
    painter.begin(svg_gen)
    scene.render(painter)
    painter.end()
