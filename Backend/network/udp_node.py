import socket

from Backend.simulator.node import Node


HOST = "127.0.0.1"
PORT = 5001


node = Node("ECU_02", "Brake")


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

server.bind((HOST, PORT))

print("UDP Node waiting for message...")


while True:

    message, address = server.recvfrom(1024)

    message = message.decode()

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

    server.sendto(
        response.encode(),
        address
    )