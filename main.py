#!/usr/bin/env python3

class Board:
    """
    O is the player's dot
    ■ is an empty space
    X is a miss (wrong guess)
    """
    def __init__(self):
        self.board = [["■" for _ in range(10)] for _ in range(10)]

    def print(self) -> None:
        for row in self.board:
            print(" ".join(row))

    def update(self, x: int, y: int, value: str) -> None:
        """
        0,0 is top left
        9,9 if bottom right
        """
        self.board[y][x] = value



if __name__ == "__main__":
    b = Board()
    b.print()
    print()
    b.update(0,0,"X")
    b.print()
    print()
    b.update(9,9,"X")
    b.print()
    print()
    b.update(7,2,"X")
    b.print()
