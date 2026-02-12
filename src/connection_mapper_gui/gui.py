from connection_mapper.connection_mapper import ConnectionMapper
from connection_mapper_gui.custom_widgets import QDiGraphView

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGroupBox, QHBoxLayout, QGridLayout
from PyQt6.QtCore import QTimer, Qt


class ConnectionMapperGUI:

    def __init__(self):
        self.mapper = ConnectionMapper()
        self.timer = QTimer()
        self.app = QApplication([])
        self.window = QWidget()

        self.ctrl_grp = QGroupBox()
        self.ctrl_btn = QPushButton()
        self.status_lbl = QLabel()
        self.pkt_cnt_lbl = QLabel()
        self.node_cnt_lbl = QLabel()

        self.map_grp = QGroupBox()
        self.map_view = QDiGraphView(self.mapper.get_map())    

        self._configure_widgets()
        self._configure_layout()

    def run(self):
        self.timer.start(2000)
        self.window.show()
        self.app.exec()

    def _configure_widgets(self):
        self.window.setWindowTitle("Connection Mapper")
        self.window.setWindowState(Qt.WindowState.WindowMaximized)

        self.timer.timeout.connect(self._update_status)
        self.timer.timeout.connect(self._update_map)
        
        self.ctrl_grp.setTitle("Capture Control")
        self.ctrl_btn.setText("Start")
        self.ctrl_btn.clicked.connect(self._click_handler)
        self._update_status()

    def _configure_layout(self):
        ctrl_grp_layout = QGridLayout()
        ctrl_grp_layout.addWidget(self.status_lbl, 0, 0)
        ctrl_grp_layout.addWidget(self.pkt_cnt_lbl, 1, 0)
        ctrl_grp_layout.addWidget(self.node_cnt_lbl, 2, 0)
        ctrl_grp_layout.addWidget(self.ctrl_btn, 1, 1)
        self.ctrl_grp.setLayout(ctrl_grp_layout)

        map_grp_layout = QHBoxLayout()
        map_grp_layout.addWidget(self.map_view)
        self.map_grp.setLayout(map_grp_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(self.ctrl_grp, 0, 1)
        main_layout.addWidget(self.map_grp, 2, 1)

        self.window.setLayout(main_layout)

    def _click_handler(self):
        if self.ctrl_btn.text() == "Start":
            self.ctrl_btn.setText("Stop")
            self.mapper.start_capture()
        else:
            self.ctrl_btn.setText("Start")
            self.mapper.stop_capture()

        self._update_status()

    def _update_status(self):
        capture_status = self.mapper.get_status()

        self.status_lbl.setText(f"Capture Status: {"Running" if capture_status.is_capturing else "Not Running"}")
        self.pkt_cnt_lbl.setText(f"Packet Count: {capture_status.packet_cnt}")
        self.node_cnt_lbl.setText(f"Node Count: {capture_status.node_cnt}")
    
    def _update_map(self):
        new_map = self.mapper.get_map()
        self.map_view.update_graph(new_map)


def gui_entry():
    gui = ConnectionMapperGUI()
    gui.run()
