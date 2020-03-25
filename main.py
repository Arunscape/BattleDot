#!/usr/bin/env python3
from typing import List, Tuple
import random
import socket
import pickle
import threading
import sys

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
        print()
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

    def receive_bomb(self, x: int, y: int) -> bool:
        if self.dot == (x, y):
            print("I WAS HIT")
            return True
        return False

    def reset_markers(self) -> None:
        self.board = [["■" for _ in range(10)] for _ in range(10)]

    def user_input(self) -> Tuple[int, int]:
        print("It's your turn!")
        self.print()
        x = int(input("Enter the x coordinate: "))
        y = int(input("Enter the y coordinate: "))
        self.send_bomb(x, y)
        return x, y

def create_client(destination: str, destination_port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((destination, destination_port))
    #print(f'created client on {s.getsockname()} to {s.getpeername()}')
    return s

def setup_client(direction: str):
    destination = input(
            f"Choose the destination address. This person is on your {direction}: "
    )
    destination_port = input("Port: ")
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
    s.bind(("127.0.0.1", port))
    s.listen()
    return s


def receive_message(client_socket):
    """
    For the server to receive a message
    """
    try:
        #print(f"expecting message from {client_socket.getpeername()}")
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            print("Received empty header")
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except Exception as e:
        print(f"Uhh {e}")
        return False


def send_message(socket, message: bytes, server=False):
    header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
    socket.send(header + message)
    print(f"sending to {socket.getpeername()} {pickle.loads(message)} from {socket.getsockname()}")

def rotate_list(l, pos: int):
    return l[pos:] + l[:pos]

def rotate_players(l):
    return rotate_list(l, len(l)-1)

def get_host_ip()->str:
    return socket.gethostbyname(socket.gethostname())

def send_setup_left(client, node: Tuple[str, int]):
    send_message_pickle(client, 'setup_left', node)
    if response := receive_message(client):
        data = pickle.loads(response['data'])
        print(f"Setup left complete: {data}")
        return data

def send_setup_right(client, node: Tuple[str, int]):
    send_message_pickle(client, 'setup_right', node)
    if response := receive_message(client):
        data = pickle.loads(response['data'])
        print(f"Setup right complete: {data}")
        return data

def send_message_pickle(client, key: str, val:any):
    message = pickle.dumps({key: val})
    send_message(client, message)

if __name__ == "__main__":

    LEFT = None # clients
    RIGHT = None
    PLAYERS = {} # keeps track of who is attacking who

    BOARD = Board()
    print(f"your dot is {BOARD.dot}")

    print(
        "Welcome to BattleDot, an unpopular networked spinoff of the popular Battleship game."
    )

    first = input("Are you the first player? (y/n): ")
    first = first == "y"
    
    server, port = setup_server()
    node_info = server.getsockname()
    #print(f"nodeinfo: {node_info}")

    if not first:
        LEFT = setup_client("LEFT")
        RIGHT = setup_client("RIGHT")
    
        send_setup_left(RIGHT, node_info)
        data = send_setup_right(LEFT, node_info)
        PLAYERS = data.get('setup_right_complete')

        if LEFT.getpeername() == RIGHT.getpeername():
            # 2nd player
            # start the game!
            player1 = RIGHT.getpeername()
            message = pickle.dumps({'announce_turn': player1, 'share_player_list': PLAYERS})
            #send_message_pickle(RIGHT, 'announce_turn', player1)
            send_message(RIGHT, message)
        LEFT.close()

    def new_client(client_socket, address):
        global PLAYERS, LEFT, RIGHT
        while True:
            if m := receive_message(client_socket):
                data = pickle.loads(m['data'])
                #print(f"Received data: {data}")
    
                if left := data.get('setup_left'):
                    #print(f"Left is now {left}")
                    left = create_client(*left)
                    LEFT = left
                    LEFT.close()
                    send_message_pickle(client_socket, 'setup_left_complete', 'setup left complete')
                    
    
                elif right := data.get('setup_right'):
                    #print(f"Right is now {right}")
                    #RIGHT.close()
                    right = create_client(*right)
                    RIGHT = right
                    BOARD.reset_markers() # the person you're trying to kill has changed
                    PLAYERS[node_info] = RIGHT.getpeername()
                    send_message_pickle(client_socket, 'setup_right_complete', PLAYERS)
                    print(f"PLAYERS setup: {PLAYERS}")
    
                elif  n := data.get('announce_turn'):
                    #print(f"turn announce: {n}")
                    if n != node_info:
                        print(f"PLAYERS announce: {PLAYERS}")
                        message = pickle.dumps({'announce_turn': n, 'share_player_list': PLAYERS})
                        send_message(RIGHT, message)
                    else:
                        x,y = BOARD.user_input()
                        send_message_pickle(RIGHT, 'make_move', (x, y))

                elif m := data.get('make_move'):
                    #print(f"incoming move: {m}")
                    if BOARD.receive_bomb(*m):
                        message = pickle.dumps({'setup_left': LEFT.getpeername()})
                        send_message(RIGHT, message)

                        message = pickle.dumps({'setup_right': RIGHT.getpeername()})
                        send_message(RIGHT, message)
                    else:
                        message = pickle.dumps({'announce_turn': node_info})
                        send_message(RIGHT, message)
                else:
                    print("Did not handle this yet")

            else:
                # connection lost

                if len(PLAYERS) < 2:
                    print("You win!")
                    sys.exit()

                # a node has lost of forfeited



    threads = []
    while True:
        client_socket, address = server.accept()
        #print(f"Connection from {address}")
        x = threading.Thread(target=new_client, args=(client_socket, address))
        threads.append(x)
        x.start()

