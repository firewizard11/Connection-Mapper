from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QSplitter, QGroupBox, QHBoxLayout, QVBoxLayout

class ConnectionMapperGUI:

    def __init__(self):
        self.app = QApplication([])
        self.window = QWidget()

        main_layout = QHBoxLayout()
        pcap_layout = QVBoxLayout()
        
        pcap_control_group = QGroupBox()
        pcap_log_group = QGroupBox()
        node_vis_group = QGroupBox()

    def run(self):
        self.window.show()
        self.app.exec()

if __name__ == "__main__":
    app = ConnectionMapperGUI()
    app.run()