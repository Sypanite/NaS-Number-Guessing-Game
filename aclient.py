# The Admin client
# Author: Carl Linley (100298658) | c.linley1@unimail.derby.ac.uk

import socket, ssl

serverSocket = None
secureServer = None
whoIs = 0

# SSL Constants
CERT_FILE = "ssl/client/100298658.crt"
KEY_FILE = "ssl/client/100298658.key"
CA_CERTS = "ssl/5cc515-root-ca.cer"

receiveBuffer = ""

# Sends a packet to the server.
def send(data):
    secureSocket.send((data + "\r\n").encode())


# Receives the next packet from the server. Any extra data is stored in 'receiveBuffer'.
def receive():
    global receiveBuffer

    packetStream = receiveBuffer + secureSocket.recv(32).decode()
    packets = packetStream.split("\r\n")

    if len(packets) > 1:
        receiveBuffer = ""

        for i in packets[1:]:
            receiveBuffer += i # Add the extra stuff to the buffer

    else:
        receiveBuffer = ""

    return packets[0]


def processMessage(message):
    if message == "Admin-Greetings":
        print("Connected to server.\nWelcome, Admin!\n");

        # Ask for a player list
        print("Players online:")
        send("Who")

    else: # "IP port"
        global whoIs

        playerData = message.split();
        whoIs += 1

        print("\t", str(whoIs) + ")", "IP:", playerData[0], "/", "Port:", playerData[1]);

# Entry point

# Create a socket and connect to the server
try:
    clientSocket = socket.socket()
    clientSocket.connect(("127.0.0.1", 4001))

    try:
        secureSocket = ssl.wrap_socket(clientSocket, certfile=CERT_FILE, keyfile=KEY_FILE, server_side=False, ca_certs=CA_CERTS)

    except ssl.SSLError as error:
        print("Failed to create a secure connection to the server:", error)
        quit(-1)

except ConnectionRefusedError:
    print("Error connecting to server.")
    quit(-1)

# Send a handshake
send("Hello")

# Main loop
while True:
    message = receive()

    # print("Server: '" + message + "'")

    if message != "":
        processMessage(message)

    else:
        break

if whoIs == 0:
    print("\tAbsolutely none!") # Nicer than no output

# Close the socket
clientSocket.close()
print("\nDisconnected from server.")

input()
