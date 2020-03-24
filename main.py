#!/usr/bin/env python3
from typing import List
import random
import socket
import pickle

HEADER_LENGTH = 10


class Board:
    """
    ■ is an unmarked space
    X is a miss (wrong guess)
    """

    def __init__(self):
        self.board = [["■" for _ in range(10)] for _ in range(10)]
        self.dot = (random.randint(0, 9), random.randint(0, 9))

    def print(self) -> None:
        for row in self.board:
            print(" ".join(row))

    def update_board(self, x: int, y: int, value: str) -> None:
        """
        0,0 is top left
        9,9 if bottom right
        """
        self.board[y][x] = value
        self.print()

    def send_bomb(self, x: int, y: int):
        self.update_board(x, y, "X")
        # TODO IPC
        pass

    def receive_bomb(self, x: int, y: int):
        if self.dot == (x, y):
            print("I WAS HIT")


# class Player(socketserver.StreamRequestHandler):
#    def handle(self):
#        print(f"Received request from {self.client_address}")
#        message = self.rfile.readline().strip()
#        print(f"Data received is {message}")


def create_client(destination: str, destination_port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((destination, destination_port))
    return s


def setup_client():
    destination = input(
        "Choose the destination address. If you were sitting at a table, this person would be on your right: "
    )
    destination_port = input("Choose the port for the destination: ")
    destination_port = int(destination_port)
    return create_client(destination, destination_port)


def setup_server(port=None):
    if port is None:
        port = input("Choose the port to run this application on: ")
        port = int(port)
    return create_server(port), port


def create_server(port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    s.listen()
    return s


def receive_message(client_socket):
    """
    For the server to receive a message
    """
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except Exception:
        return False


def send_message(server_socket, message: bytes):
    header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
    server_socket.send(header + message)

def rotate_list(l, pos: int):
    return l[pos:] + l[:pos]

def rotate_players(l):
    return rotate_list(l, len(l)-1)

def get_host_ip()->str:
    return socket.gethostbyname(socket.gethostname())


if __name__ == "__main__":

    PLAYERS = [] # index 0 is the process's own player info 
    BOARD = Board()
    GAME_STARTED = False

    print(
        "Welcome to BattleDot, an unpopular networked spinoff of the popular Battleship game."
    )

    first = input("Are you the first player? (y/n): ")
    first = first == "y"

    server, port = setup_server()

    if first:
        PLAYERS.append((get_host_ip(), port))

    client = None
    
    if not first:
        client= setup_client()
    
        player = (get_host_ip(), port)
        player = pickle.dumps(player)

        send_message(client, player)
#        print(receive_message(client))
        if player_list := receive_message(client):
            PLAYERS = pickle.loads(player_list['data'])
            print(f"Received player list {PLAYERS}")


    while True:
        client_socket, address = server.accept()
        print(f"Connection from {address}")
        if p := receive_message(client_socket):
            player = pickle.loads(p['data'])
            print(f"New player {player} wants to join")
            PLAYERS.append(player)
            message = pickle.dumps(rotate_players(PLAYERS))
            send_message(client_socket, message)
