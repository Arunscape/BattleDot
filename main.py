#!/usr/bin/env python3
from typing import List, Tuple
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
    s.bind(("0.0.0.0", port))
    s.listen()
    return s


def receive_message(client_socket):
    """
    For the server to receive a message
    """
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        print(f"header: {message_header}")

        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except Exception as e:
        print(f"Uhh {e}")
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

#def send_setup_left():



if __name__ == "__main__":

    LEFT = []
    RIGHT = []

    BOARD = Board()
    CURRENT_TURN = None

    print(
        "Welcome to BattleDot, an unpopular networked spinoff of the popular Battleship game."
    )

    first = input("Are you the first player? (y/n): ")
    first = first == "y"
    
    second = None
    if not first:
        second = input("Are you the second player? (y/n): ")
    second = second == "y"

    server, port = setup_server()
    node_info = (get_host_ip(), port)

    if first:
        CURRENT_TURN = node_info

    if not first:
        LEFT.append(setup_client("LEFT"))
        RIGHT.append(setup_client("RIGHT"))
    

        message = pickle.dumps({'setup_left': node_info})
        send_message(LEFT[-1], message)
        
        message = pickle.dumps({'setup_right': node_info})
        send_message(RIGHT[-1], message)
        
        if second:
            # start the game!
            message = pickle.dumps({'announce_turn': RIGHT[-1].getpeername()})
            send_message(RIGHT[-1], message)

        # if the server sends data back
        #if response := receive_message(client):
        #    data = pickle.loads(response['data'])
        #    print(f"Received: {data}")


    while True:
        client_socket, address = server.accept()
        print(f"Connection from {address}")
        m = receive_message(client_socket)
        print(pickle.loads(m['data']))
        if m:
        #if m := receive_message(client_socket):
            data = pickle.loads(m['data'])

            if left := data.get('setup_left'):
                print(f"Left is now {left}")
                left = create_client(*left)
                LEFT.append(left)
            elif right := data.get('setup_right'):
                print(f"Right is now {right}")
                right = create_client(*right)
                RIGHT.append(right)
                BOARD.reset_markers() # the person you're trying to kill has changed
            elif  n := data.get('announce_turn'):
                print(f"turn announce: {n}")
                if n != node_info:
                    send_message(RIGHT[-1], m[data])
                else:
                    x, y = BOARD.user_input()
                    message = pickle.dumps({'make_move': (x,y)})
            elif m := data.get('make_move'):
                print(f"incoming move: {m}")
                if BOARD.receive_bomb(*m):
                    message = pickle.dumps({'setup_left': LEFT[-1].getpeername()})
                    send_message(RIGHT[-1], message)
        
                    message = pickle.dumps({'setup_right': RIGHT[-1].getpeername()})
                    send_message(LEFT[-1], message)
                else:
                    message = pickle.dumps({'announce_turn': node_info})
                    send_message(RIGHT[-1], message)
                    
            else:
                print("🤷")
