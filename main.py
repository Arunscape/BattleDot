#!/usr/bin/env python3
from typing import List
import random
import socket
import socketserver

class Board:
    """
    ■ is an unmarked space
    X is a miss (wrong guess)
    """
    def __init__(self):
        self.board = [["■" for _ in range(10)] for _ in range(10)]
        self.dot = (random.randint(0, 9), random.randint(0,9))

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
        if self.dot == (x,y):
            print("I WAS HIT")

class Player(socketserver.StreamRequestHandler):
    def handle(self):
        print(f"Received request from {self.client_address}")
        message = self.rfile.readline().strip()
        print(f"Data received is {message}")


if __name__ == "__main__":

    PLAYERS = []
    BOARD = Board()

    print("Welcome to BattleDot, an unpopular networked spinoff of the popular Battleship game.")

    first = input("Are you the first player? (y/n): ")
    if first == "y":
        first = True
        PLAYERS.append(1)
    else:
        first = False

    if not first:
        destination = input("Choose the destination address. If you were sitting at a table, this person would be on your right: ")
        destination_port = input("Choose the port for the destination: ")
        destination_port = int(destination_port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((destination, destination_port))
        s.sendto("HELLO".encode(), (destination, destination_port))
        s.recv(1024)
        s.close()

    port = input("Choose the port to run this application on: ")
    port = int(port)
    server = socketserver.TCPServer(("127.0.0.1", port), Player)
    server.serve_forever()
