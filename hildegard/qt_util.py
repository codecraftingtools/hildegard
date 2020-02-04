# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt, QSize, QRect
from qtpy.QtGui import QPainter
from qtpy.QtSvg import QSvgGenerator
from qtpy.QtWidgets import QGraphicsView

class Scene_View(QGraphicsView):
    def __init__(self, parent):
        super(Scene_View, self).__init__(parent)
        #self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)
        #self.setDragMode(QGraphicsView.NoDrag)
        
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.1
            self.scale(factor, factor)
        else:
            factor = 0.97
            self.scale(factor, factor)

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
