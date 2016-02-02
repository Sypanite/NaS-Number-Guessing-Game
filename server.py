# server.py
# The server side of my basic number guessing game implementation.
# Originally used threading, modified to use select.
# Author: Carl Linley (100298658) | c.linley1@unimail.derby.ac.uk

import select, socket, ssl
import random
import math

serverRunning = True

addresses = {} # Socket : String
activeGames = {} # Socket : Game
inSockets = {} # Socket : SocketType

# SSL Constants
CERT_FILE = "ssl/server/5cc515_server.crt"
KEY_FILE = "ssl/server/5cc515_server.key"
CA_CERTS = "ssl/5cc515-root-ca.cer"

# Used to identify socket types- basically an enum
class SocketType:
    PLAYER_LISTENER, ADMIN_LISTENER, PLAYER_CLIENT, ADMIN_CLIENT = range(4)


# Handles the gameplay for each client.
class Game:
    secretNumber = -1

    def __init__(self):
        self.secretNumber = random.randint(1, 20)

    def difference(self, value):
        return abs(value - self.secretNumber)

    def guess(self, value):
        if value == self.secretNumber:
            return "Correct"

        elif self.difference(value) <= 3:
            return "Close"

        return "Far"


# Sends a packet to the specified client.
def send(clientSocket, data):
    try:
        clientSocket.send((data + "\r\n").encode())

    except ConnectionResetError:
        pass


# Receives the next packet from the specified client.
# Due to the nature of the data it receives, the server does not use a buffer.
def receive(clientSocket):
    return clientSocket.recv(32).decode()[0:-2]


# Creates a new TCP/IPv4 socket using the given port and adds it to the serverSockets list.
def listen(port):
    listener = None

    try:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", port))
        listener.listen(5)

        inSockets[listener] = SocketType.PLAYER_LISTENER if port == 4000 else SocketType.ADMIN_LISTENER

    except OSError: # Failed to start server - port already in use?
        return


# Disconnects the specified client
def disconnect(client):
    if inSockets[client] == SocketType.PLAYER_CLIENT:
        del activeGames[client]
        del addresses[client]

    client.close()
    del inSockets[client]


# Handles data from player clients.
def processPlayerPacket(client):
    if message == "Hello":
        # Return the handshake
        send(client, "Greetings")

        # Start a new game for this client
        activeGames[client] = Game()

    elif message[0:5] == "Guess":
        # Process the guess
        guessType = activeGames[client].guess(int(message[7:]));
        send(client, guessType)

    else:
        disconnect(client)


# Handles data from admin clients.
def processAdminPacket(client):
    if message == "Hello":
        # Return the handshake
        send(secureClient, "Admin-Greetings")

    elif message == "Who":
        for add in list(addresses.values()):
            send(secureClient, str(add[0]) + " " + str(add[1]))

        disconnect(client)
        return

    else:
        pass
        # break


# Entry point
listen(4000)
listen(4001)

message = ""

while serverRunning:
    (inputSockets, outputSockets, exceptions) = select.select(inSockets, [], [])

    # Accept incoming connections
    for iSocket in inputSockets:
        if inSockets[iSocket] == SocketType.PLAYER_LISTENER:
            (client, address) = iSocket.accept()

            inSockets[client] = SocketType.PLAYER_CLIENT
            addresses[client] = address
  
        elif inSockets[iSocket] == SocketType.ADMIN_LISTENER:
            (client, address) = iSocket.accept()

            secureClient = ssl.wrap_socket(client, certfile=CERT_FILE, keyfile=KEY_FILE,
                                           server_side=True, cert_reqs=ssl.CERT_REQUIRED, ca_certs=CA_CERTS)

            inSockets[secureClient] = SocketType.ADMIN_CLIENT

        else:
            try:
                message = receive(iSocket)
                
                if message == "":
                    disconnect(iSocket)
                    break

            except ConnectionResetError:
                disconnect(iSocket)
                break

            if inSockets[iSocket] == SocketType.PLAYER_CLIENT:
                processPlayerPacket(iSocket)

            elif inSockets[iSocket] == SocketType.ADMIN_CLIENT:
                processAdminPacket(iSocket)
