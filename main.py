#!/usr/bin/env python3
from typing import List
import random

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


if __name__ == "__main__":
    b = Board()
    b.print()
    print()
