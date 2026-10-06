import socket

from Backend.simulator.node import Node


HOST = "127.0.0.1"
PORT = 5000


node = Node("ECU_01", "Engine")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print("TCP Node waiting for connection...")


while True:

    connection, address = server.accept()

    print("Connected to:", address)

    message = connection.recv(1024).decode()

    print("Received:", message)

    if message == "START":
        node.start()
        response = "Node started"

    elif message == "STOP":
        node.stop()
        response = "Node stopped"

    elif message == "STATUS":
        response = (
            f"Status: {node.status}, "
            f"CPU: {node.cpu_usage}%, "
            f"Memory: {node.memory_usage}%"
        )

    else:
        response = "Unknown command"

    connection.send(response.encode())

    connection.close()