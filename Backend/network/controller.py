import socket


HOST = "127.0.0.1"

TCP_PORT = 5000
UDP_PORT = 5001


# ---------------- TCP ----------------

tcp_client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

tcp_client.connect((HOST, TCP_PORT))

tcp_client.send("STATUS".encode())

response = tcp_client.recv(1024).decode()

print("\n--- TCP NODE ---")
print("Response:", response)

tcp_client.close()


# ---------------- UDP ----------------

udp_client = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

udp_client.sendto(
    "STATUS".encode(),
    (HOST, UDP_PORT)
)

response, address = udp_client.recvfrom(1024)

print("\n--- UDP NODE ---")
print("Response:", response.decode())

udp_client.close()