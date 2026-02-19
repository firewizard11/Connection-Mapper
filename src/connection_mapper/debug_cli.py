from connection_mapper.connection_mapper import ConnectionMapper
import matplotlib.pyplot as plt
import networkx as nx


def debug_repl():
    cm = ConnectionMapper()

    while (True):
        cmd = input("> ").strip().lower()

        match cmd:
            case "start":
                print("Starting Capture...")
                cm.start_capture()

            case "stop":
                print("Stopping Capture...")
                cm.stop_capture()

            case "map":
                print("Outputting Map...")
                map = cm.get_map()
                
                colors = []
                labels = {}
                with_labels = map.number_of_nodes() < 10

                for node, data in map.nodes.items():
                    colors.append(data["color"])
                    labels[node] = data["label"]

                positions = nx.spring_layout(map)
                nx.draw(map, positions, node_color=colors)

                if with_labels:
                    nx.draw_networkx_labels(map, positions, labels)

                plt.show()

            case "status":
                status = cm.get_status()
                print(f"Capture Status: {status.is_capturing}")
                print(f"Packets Processed: {status.packets_processed}")
                print(f"Nodes Found: {status.nodes_found}")

            case "commands":
                print("Commands:")
                print("- start")
                print("- stop")
                print("- map")
                print("- status")
                print("- commands")
                print("- quit")

            case "quit":
                print("Exiting Program...")
                break

            case _:
                print("Run 'commands' to see commands")
                continue