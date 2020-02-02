# Copyright (c) 2020 Jeffrey A. Webb

from qtpy.QtCore import Qt
#from qtpy.QtSvg import QSvgGenerator
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

# 
#    svgGen = QSvgGenerator()
#    svgGen.setFileName( "out.svg" )
#    svgGen.setSize(QSize(e.scene.width(), e.scene.height()))
#    svgGen.setViewBox(QRect(0, 0, e.scene.width(), e.scene.height()))
#    svgGen.setTitle("Hierarchic Component Drawing")
#    svgGen.setDescription("A Hierarchic Component Drawing created by gsd.")
#    painter = QPainter()
#    painter.begin(svgGen)
#    e.scene.render(painter)
#    painter.end()
