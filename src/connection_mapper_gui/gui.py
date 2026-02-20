from connection_mapper.connection_mapper import ConnectionMapper
from connection_mapper_gui.graph_view import QDiGraphView

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGroupBox, QVBoxLayout, QGridLayout
from PyQt6.QtCore import QTimer, Qt


class ConnectionMapperGUI:

    def __init__(self):
        self._mapper = ConnectionMapper()
        self._timer = QTimer()
        self._app = QApplication([])

        self._create_main_window()

    def run(self):
        self._timer.start(2000)
        self._window.show()
        self._app.exec()

    def _create_main_window(self):
        self._window = QWidget()
        self._window.setWindowTitle("Connection Mapper")
        self._window.setWindowState(Qt.WindowState.WindowMaximized)

        self._create_ctrl_section()
        self._create_map_section()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._ctrl_grp)
        main_layout.addWidget(self._map_grp)

        self._window.setLayout(main_layout)

    def _create_ctrl_section(self):
        self._ctrl_grp = QGroupBox()
        self._ctrl_grp.setTitle("Packet Capture Control")

        self._ctrl_btn = QPushButton()
        self._ctrl_btn.setText("Start Capture")
        self._ctrl_btn.clicked.connect(self._click_handler)

        self._status_lbl = QLabel()
        self._pkt_cnt_lbl = QLabel()
        self._node_cnt_lbl = QLabel()
        self._update_status_lbls()
        self._timer.timeout.connect(self._update_status_lbls)

        ctrl_layout = QGridLayout()
        ctrl_layout.addWidget(self._status_lbl, 0, 0)
        ctrl_layout.addWidget(self._pkt_cnt_lbl, 1, 0)
        ctrl_layout.addWidget(self._node_cnt_lbl, 2, 0)
        ctrl_layout.addWidget(self._ctrl_btn, 1, 1)

        self._ctrl_grp.setLayout(ctrl_layout)

    def _create_map_section(self):
        self._map_grp = QGroupBox()
        self._map_grp.setTitle("Connection Map")

        self._map_view = QDiGraphView(self._mapper.get_map())
        
        map_layout = QVBoxLayout()
        map_layout.addWidget(self._map_view)
        self._map_grp.setLayout(map_layout)

        self._timer.timeout.connect(self._update_map)

    def _click_handler(self):
        if self._mapper.get_status().is_capturing:
            self._mapper.stop_capture()
            self._ctrl_btn.setText("Start Capture")
        else:
            self._mapper.start_capture()
            self._ctrl_btn.setText("Stop Capture")
        
        self._update_status_lbls()

    def _update_status_lbls(self):
        capture_status = self._mapper.get_status()

        self._status_lbl.setText(f"Capture Status: {"Running" if capture_status.is_capturing else "Not Running"}")
        self._pkt_cnt_lbl.setText(f"Packet Count: {capture_status.packets_processed}")
        self._node_cnt_lbl.setText(f"Node Count: {capture_status.nodes_found}")

    def _update_map(self):
        new_map = self._mapper.get_map()
        self._map_view.update_graph(new_map)

def gui_entry():
    gui = ConnectionMapperGUI()
    gui.run()
