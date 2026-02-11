from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt6.QtCore import QTimer
from connection_mapper import ConnectionMapper


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

        self._configure_widgets()
        self._configure_layout()

    def run(self):
        self.timer.start(2000)
        self.window.show()
        self.app.exec()

    def _configure_widgets(self):
        self.window.setWindowTitle("Connection Mapper")
        self.timer.timeout.connect(self._update_status)
        
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

        main_layout = QGridLayout()
        main_layout.addWidget(self.ctrl_grp, 0, 1)

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

        self.status_lbl.setText(f"Capture Status: {"Running" if capture_status["capturing"] else "Not Running"}")
        self.pkt_cnt_lbl.setText(f"Packet Count: {capture_status["cap_count"]}")
        self.node_cnt_lbl.setText(f"Node Count: {capture_status["node_count"]}")


if __name__ == "__main__":
    gui = ConnectionMapperGUI()
    gui.run()