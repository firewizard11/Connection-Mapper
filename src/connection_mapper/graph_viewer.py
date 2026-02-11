import networkx as nx
from PyQt6.QtWidgets import QGraphicsView, QApplication, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor
from connection_mapper import ConnectionMapper
import time

class DiGraphViewer(QGraphicsView):
    
    def __init__(self, graph: nx.DiGraph):
        super().__init__()
        self.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        self.setBackgroundBrush(QColor("white"))

        self._graph = graph
        self._scene = QGraphicsScene()
        self._scale = 300
        self._radius = 15
        self._diameter = self._radius * 2
        self._position_table = nx.spring_layout(self._graph, scale=self._scale)

        self.draw_graph()
        self.setScene(self._scene)

    def draw_graph(self):
        self.add_nodes()
        self.add_edges()

    def add_nodes(self):
        for node, data in self._graph.nodes.items():
            node_color = QColor(data["color"])
            brush = QBrush(node_color)
            brush.setStyle(Qt.BrushStyle.SolidPattern)

            item = self._scene.addEllipse(
                0,
                0,
                self._diameter,
                self._diameter,
                node_color.darker(),
                brush
            )

            item.setPos(self.get_node_position(node))

    def get_node_position(self, node) -> QPointF:
        item_position = QPointF()
        item_position.setX(self._position_table[node][0])
        item_position.setY(self._position_table[node][1])
        return item_position

    def add_edges(self):
        for u, v in self._graph.edges:
            line = QLineF(self.get_node_position(u), self.get_node_position(v))

            self._scene.addLine(line, QColor("black"))

    def update_graph(self):
        pass

if __name__ == "__main__":
    app = QApplication([])
    cm = ConnectionMapper(is_verbose=True)
    cm.start_capture()
    time.sleep(5)
    cm.stop_capture()

    view = DiGraphViewer(cm.get_map())
    view.show()
    app.exec()