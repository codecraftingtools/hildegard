# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt, QSize, QRect, QRectF, QPoint
from qtpy.QtGui import QPainter
from qtpy.QtSvg import QSvgGenerator
from qtpy.QtWidgets import QGraphicsView

class Scene_View(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)

        #self.pan_button = Qt.MiddleButton
        self.pan_button = Qt.RightButton # for testing w/ touchpad
        self.pan_modifier = Qt.ShiftModifier
        self._panning = False
        #self._button_panning = False
        #self._modifier_panning = False
        self._starting_mouse_pos = None
        self._last_mouse_pos = None
        self._scale = 1.0
        self._shown = False
        
        self.verticalScrollBar().disconnect()
        self.horizontalScrollBar().disconnect()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        
        #self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        #self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)
        #self.setDragMode(QGraphicsView.NoDrag)
        #self.setStyleSheet("border: 0px")

    def showEvent(self,event):
        if not self._shown:
            self._shown = 1
            self._set_scene_rect()

    def fitInView(self,event,aspect):
        pos = QPoint(self.viewport().width()/2,
                     self.viewport().height()/2)        
        scene_pos1 = self.mapToScene(pos)
        self._set_scene_rect()
        scene_pos2 = self.mapToScene(pos)
        delta = scene_pos2 - scene_pos1
        self.translate(delta.x(), delta.y())
        super().fitInView(event,aspect)

    def resizeEvent(self,event):
        br = self.scene().itemsBoundingRect()
        self.fitInView(br, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        mouse_pos = event.pos()
        if event.angleDelta().y() > 0:
            self._zoom(1.1, mouse_pos)
        else:
            self._zoom(0.97, mouse_pos)
                       
    def calc_offset(self, x, y):
        offset_x = x - int(self.viewport().width()/2)
        offset_y = y - int(self.viewport().height()/2)
        return offset_x, offset_y

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos()
        
        #if event.modifiers() == self.pan_modifier:
        #    if not self._modifier_panning:
        #        self._modifier_panning = True
        #        self._starting_mouse_pos = mouse_pos
        #else:
        #    self._modifier_panning = False
            
        #if (self._button_panning or self._modifier_panning):
        if self._panning:

            #delta = mouse_pos - self._starting_mouse_pos
            delta = mouse_pos - self._last_mouse_pos
            
            # Move using scroll bars
            #v = self.verticalScrollBar()
            #h = self.horizontalScrollBar()
            #h.setValue(h.value() - delta.x())
            #v.setValue(v.value() - delta.y())

            # Move using translate (scroll bars must be disconnected)
            if 1:
                #delta = delta / self._scale
                #self.translate(delta.x(), delta.y())
                delta_scene = self.mapToScene(mouse_pos) - self.mapToScene(
                    self._last_mouse_pos)
                self.translate(delta_scene.x(), delta_scene.y())
                
            # Move using scroll
            if 0:
                offset_x, offset_y = self.calc_offset(
                    event.pos().x(), event.pos().y())
                #self.scroll(offset_x,offset_y)
                f_offset_x, f_offset_y = self.calc_offset(
                    self._starting_mouse_pos.x(), self._starting_mouse_pos.y())
                self.scroll(offset_x - f_offset_x,
                            offset_y - f_offset_y)
                #print(delta.x(), delta.y(), offset_x, offset_y)
            
            self._last_mouse_pos = mouse_pos
            
        super().mouseMoveEvent(event)

    def _set_scene_rect(self):
            vp_max_old = self.mapToScene(
                self.viewport().width(), self.viewport().height())
            vp_min_old = self.mapToScene(0, 0)
            vp_max = vp_max_old*2
            vp_min = vp_min_old - vp_max_old
            s = self.scene().sceneRect()
            #print("start", s)
            s_min = s.topLeft()
            s_max = s.bottomRight()
            new_min_x = min(vp_min.x(), s_min.x())
            new_min_y = min(vp_min.y(), s_min.y())
            new_max_x = max(vp_max.x(), s_max.x())
            new_max_y = max(vp_max.y(), s_max.y())
            #print(vp_min, vp_max, s_min, s_max)
            new_rect = QRectF(
                new_min_x, new_min_y, new_max_x-new_min_x, new_max_y - new_min_y)
            #print("end", new_rect)
            t = self.transform()
            #print(t.dx(), t.dy())
            #self.scene().setSceneRect(new_rect)
            self.setSceneRect(new_rect)
            t = self.transform()
            #print(t.dx(), t.dy())
            #self.setTransform(t)
            #self.translate(new_min_x - s_min.x(), new_min_y - s_min.y())
            t = self.transform()
            #print(t.dx(), t.dy())
            #self.setSceneRect(new_rect)
        
    def mousePressEvent(self, event):
        mouse_pos = event.pos()
        if (event.button() == self.pan_button or
            (event.button() == Qt.LeftButton and
             event.modifiers() == self.pan_modifier)):
            #self._button_panning = True
            self._panning = True
            self._starting_mouse_pos = mouse_pos
            self._last_mouse_pos = mouse_pos

            self._set_scene_rect()
            
            #print(dir(s))
            #s1 = self.mapFromScene(s.topLeft())
            #y = self.mapToScene(s.y())
            #print(s.x(), s.y(), s.width(), s.height())
            #print(" ", s1.x(), s1.y())
            #print(dir(self.viewport()))
            #print(" zzz ", self.viewport().x(), self.viewport().y())
            #self.scene().setSceneRect(s)
            

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (event.button() == self.pan_button or
            event.button() == Qt.LeftButton):
            #self._button_panning = False
            self._panning = False
            
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        pos = QPoint(self.viewport().width()/2,
                     self.viewport().height()/2)
        if key == Qt.Key_Plus or key == Qt.Key_Equal:
            self._zoom(1.1, pos)
        elif key == Qt.Key_Minus:
            self._zoom(0.9, pos)
        else:
            super().keyPressEvent(event)

    def _zoom(self, factor, pos=None):
        if pos is not None:
            scene_pos1 = self.mapToScene(pos)
        self.scale(factor, factor)
        self._scale = self._scale * factor
        self._set_scene_rect()
        if pos is not None:
            scene_pos2 = self.mapToScene(pos)
            delta = scene_pos2 - scene_pos1
            self.translate(delta.x(), delta.y())
        
def export_scene_as_svg(scene, file_name=None):
    if file_name is None:
        file_name = "out.svg"
    
    print(f"export SVG to file: {file_name}")
    
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
