# Player client
# Author: Carl Linley (100298658) | c.linley1@unimail.derby.ac.uk

import socket
import random
import json
from enum import Enum

# An enum value for each supported language.
class Language(Enum):
    ENGLISH = 0
    FRENCH = 1
    GERMAN = 2
    # BINARY = 3

# Stores language data.
class Lang:
    # Fixed messages
    NAME = None
    INTRO = None
    GUESS = None
    NAN = None
    END = None
    ERR_CON = None
    DIS_CON = None
    OUT_OF_RANGE = None

    # Pseudorandom messages, less monotonous.
    CLOSE = []
    FAR = []
    CORRECT = []
    CORRECT_SUFFIX = []

    def __init__(self, language):
        langFile = open('LANG.json', 'r')
        rawString = langFile.read()
        
        lang = str(language)[9:]

        with open('LANG.json') as jsonFile:    
            data = json.load(jsonFile)

            self.NAME = data[lang]["NAME"]
            self.INTRO = data[lang]["INTRO"]
            self.ERR_CONN = data[lang]["ERR_CON"]
            self.DIS_CON = data[lang]["DIS_CON"]
            self.GUESS = data[lang]["GUESS"]
            self.NAN = data[lang]["NAN"]
            self.END = data[lang]["END"]
            self.OUT_OF_RANGE = data[lang]["OUT_OF_RANGE"]

            self.CLOSE = data[lang]["CLOSE"]
            self.FAR = data[lang]["FAR"]
            self.CORRECT = data[lang]["CORRECT"]
            self.CORRECT_SUFFIX = data[lang]["CORRECT_SUFFIX"]


    def close(self):
        return random.choice(self.CLOSE) + "!"


    def far(self):
        return random.choice(self.FAR) + "!"


    def correct(self):
        return random.choice(self.CORRECT) + ", " + random.choice(self.CORRECT_SUFFIX) + "!"


lang = None
connected = False
gameRunning = True

guessCount = 0
serverSocket = None
receiveBuffer = ""

def setLanguage(language):
    global lang
    lang = Lang(language)


# Sends a packet to the server.
def send(data):
    serverSocket.send((data + "\r\n").encode())


# Receives the next packet from the server. Any extra data is stored in 'receiveBuffer'.
def receive():
    global receiveBuffer

    packetStream = receiveBuffer + serverSocket.recv(32).decode()
    packets = packetStream.split("\r\n")

    if len(packets) > 1:
        receiveBuffer = ""

        for i in packets[1:0]:
            receiveBuffer += i # Add the extra stuff to the buffer

    else:
        receiveBuffer = ""

    return packets[0]


def processMessage(message):
    if message == "Greetings":
        print(lang.INTRO)

    elif message == "Close":
        print(lang.close())

    elif message == "Far":
        print(lang.far())

    elif message == "Correct":
        print(lang.correct())
        return False

    return True


def processGuess(inputString):
    if inputString == "":
        return -1

    try:
        guess = int(inputString)

        if guess < 1 or guess > 20:
            print(lang.OUT_OF_RANGE)
            return -1

        return guess

    except ValueError:
        print(lang.NAN)
        return -1


# Entry point

while lang == None:
    print("\nThis game supports three languages - English, French, and German.")
    language = input("Which would you prefer? ").lower()
    
    if language[0:3] == "eng":
        setLanguage(Language.ENGLISH)
    
    elif language[0:3] == "fre" or language[0:3] == "fra":
        setLanguage(Language.FRENCH)
        
    elif language[0:3] == "ger" or language[0:3] == "deu":
        setLanguage(Language.GERMAN)

    else:
        print("Sorry - that language isn't supported.")

# Create a socket and connect to the server
try:
    serverSocket = socket.socket()
    serverSocket.connect(("127.0.0.1", 4000))
    connected = True

except:
    print(lang.ERR_CONN)

if connected:
    # Send a handshake
    send("Hello")

    # Main loop
    while gameRunning:
        message = receive()

        if message == "":
            print(lang.DIS_CON)
            break

        gameRunning = processMessage(message)

        if gameRunning: # Check required, it may have ended
            guess = -1

            while guess == -1:
                guess = processGuess(input("\n" + lang.GUESS))
                guessCount += 1

            send("Guess: " + str(guess))

    # Close the socket
    serverSocket.close()
    print("\n" + lang.END, guessCount)

# Prevent the window closing immediately
input()
