import math
import networkx as nx

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor


class QNode(QGraphicsItem):

    def __init__(self, label: str, color: str, parent = None):
        super().__init__()
        self._label = label
        self._color = QColor(color)
        self._radius = 40
        self._diameter = self._radius * 2

        self._rect = QRectF(0, 0, self._diameter, self._diameter)

    def boundingRect(self):
        return self._rect
    
    def paint(self, painter, option, widget = ...):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        text_pen = QPen(QColor("white"))
        outline_pen = QPen(
            self._color.darker(),
            2,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        )
        painter.setPen(outline_pen)

        brush = QBrush(
            self._color,
            Qt.BrushStyle.SolidPattern
        )
        painter.setBrush(brush)

        painter.drawEllipse(self.boundingRect())
        painter.setPen(text_pen)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self._label)


class QEdge(QGraphicsItem):

    def __init__(self, src: QNode, dst: QNode, parent = None):
        super().__init__()
        self._src = src
        self._dst = dst

        self._color = QColor("black")
        self._arrow_size = self._src._radius / 2
        self._line_thickness = 1

        self._line = QLineF()
        self.setZValue(-1)
        self._derive_pos()

    def boundingRect(self):
        return QRectF(self._line.p1(), self._line.p2())

    def _derive_pos(self):
        self._line.setP1(self._src.pos() + self._src.boundingRect().center())
        self._line.setP2(self._dst.pos() + self._dst.boundingRect().center())

    def _draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF):
        head_length = 10
        head_angle = math.pi / 7

        pen = QPen(self._color, self._line_thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawLine(start, end)

        line = QLineF(start, end)
        angle = math.atan2(line.dy(), line.dx())

        p1 = QPointF(end.x() - head_length * math.cos(angle - head_angle), end.y() - head_length * math.sin(angle - head_angle))
        p2 = QPointF(end.x() - head_length * math.cos(angle + head_angle), end.y() - head_length * math.sin(angle + head_angle))

        painter.drawLine(end, p1)
        painter.drawLine(end, p2)

    def _arrow_target(self) -> QPointF:
        target = self._line.p1()
        center = self._line.p2()
        radius = self._dst._radius
        vector = target - center
        length = math.sqrt(vector.x() ** 2 + vector.y() ** 2)
        if length == 0:
            return target
        normal = vector / length
        target = QPointF(center.x() + (normal.x() * radius), center.y() + (normal.y() * radius))

        return target

    def paint(self, painter, option, widget = ...):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self._color, self._line_thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self._line)
        self._draw_arrow(painter, self._line.p1(), self._arrow_target())


class QDiGraphView(QGraphicsView):
    
    def __init__(self, graph: nx.DiGraph):
        super().__init__()
        self.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        self.setBackgroundBrush(QColor("white"))
        self.setDragMode(self.DragMode.ScrollHandDrag)

        self._internal_graph = QGraphicsScene()
        self.setScene(self._internal_graph)
        
        self._nx_graph = graph
        self._scale = 500
        self._radius = 30
        self._diameter = self._radius * 2
        
        self._position_map = None
        self._node_map = {}

        self.load_graph()

    def load_graph(self):
        self._internal_graph.clear()
        self._node_map.clear()

        if not self._position_map:
            self._position_map = nx.spring_layout(self._nx_graph)
        else:
            self._position_map = nx.spring_layout(self._nx_graph, pos=self._position_map, fixed=self._position_map.keys(), iterations=10)

        self.add_nodes()
        self.add_edges()

        self._internal_graph.setSceneRect(self._internal_graph.itemsBoundingRect())

    def add_nodes(self):
        for node, data in self._nx_graph.nodes.items():

            item = QNode(data["label"], data["color"])

            self._internal_graph.addItem(item)

            item.setPos(self.get_node_position(node))
            item.setZValue(1)

            self._node_map[node] = item

    def get_node_position(self, node) -> QPointF:
        item_position = QPointF()
        item_position.setX(self._position_map[node][0] * self._scale)
        item_position.setY(self._position_map[node][1] * self._scale)
        return item_position

    def add_edges(self):
        for u, v in self._nx_graph.edges:
            self._internal_graph.addItem(QEdge(
                self._node_map[u],
                self._node_map[v]
            ))

    def update_graph(self, new_graph: nx.DiGraph):
        self._nx_graph = new_graph
        self.load_graph()