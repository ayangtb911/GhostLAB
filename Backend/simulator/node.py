import random


class Node:

    def __init__(self, node_id, node_type):
        self.node_id = node_id
        self.node_type = node_type
        self.status = "OFFLINE"
        self.cpu_usage = 0
        self.memory_usage = 0

    def start(self):
        self.status = "ONLINE"

        self.cpu_usage = random.randint(10, 80)
        self.memory_usage = random.randint(20, 70)

    def stop(self):
        self.status = "OFFLINE"
        self.cpu_usage = 0
        self.memory_usage = 0

    def show_status(self):

        print(f"Node: {self.node_id}")
        print(f"Type: {self.node_type}")
        print(f"Status: {self.status}")
        print(f"CPU: {self.cpu_usage}%")
        print(f"Memory: {self.memory_usage}%")

        class ECU(Node):

            def __init__(self, node_id, ecu_type):
                super().__init__(node_id, "ECU")
                self.ecu_type = ecu_type

            def diagnostic_check(self):
                print(f"{self.node_id}: Running diagnostic check")