from connection_mapper.connection_mapper import ConnectionMapper

def debug_cli():
    cm = ConnectionMapper()

    while (True):
        cmd = input("> ")
        
        match cmd.strip().lower():
            case "help":
                print("Commands:")
                print("-- start: start packet capture")
                print("-- stop: stop packet capture")
                print("-- draw: displays the map")
                print("-- status: displays if the capture is running and the number of packets captured")
                print("-- quit: close program")
            case "start":
                cm.start_capture()
            case "stop":
                cm.stop_capture()
            case "draw":
                cm.draw_map()
            case "quit":
                cm.stop_capture()
                print("Exiting")
                break
            case "status":
                status = cm.get_status()
                if status["capturing"]:
                    print("[INFO] Capture is running")
                else:
                    print("[INFO] Capture is not running")

                print(f"[INFO] Captured {status["cap_count"]} Packets")
                print(f"[INFO] Found {status["node_count"]} Nodes")
            case _:
                print("[INFO] Enter 'help' to see commands")