import math
from operator import attrgetter

import pygame

# initiate pygame
pygame.init()
# size of board
X = 800
# create new Window
screen = pygame.display.set_mode((X, X))

# set amount of rectangles
recAmount = 20
recSize = int(X / recAmount)

# colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# fill window with white
screen.fill(WHITE)


class Node:
    x = 0
    y = 0

    blocked = False
    fCost = 0
    gCost = 0
    hCost = 0
    parent = any

    def __init__(self, x, y):
        if x > 0 or y > 0 or x < recAmount or y < recAmount:
            self.x = x
            self.y = y

    def block(self):
        self.blocked = True

    def calculateF(self):
        self.fCost = self.hCost + self.gCost

    def calculateHeuristic(self, end):
        self.hCost = abs(self.x - end.x) + abs(self.y - end.y)

    def setParent(self, parent):
        self.parent = parent

    # colors rectangle at current position of node
    def drawColorOnBoard(self, color):
        pygame.draw.rect(screen, color, pygame.Rect(self.x * recSize, self.y * recSize, recSize, recSize))
        pygame.display.update()

    def removeColorOnBoard(self):
        pygame.draw.rect(screen, WHITE, pygame.Rect(self.x * recSize, self.y * recSize, recSize, recSize))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# TODO TEMP START AND END
START = Node(2, 3)
START.drawColorOnBoard((255, 0, 0))
END = Node(12, 16)
END.drawColorOnBoard((0, 255, 0))


def main():
    # set caption
    pygame.display.set_caption('A* Pathfinding')

    # initialize internal array to represent array
    board = initBoard()

    ready = True

    while True:

        for event in pygame.event.get():

            # quit program
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and ready:
                    ready = False
                    aStar(board, START, END)

                # reset board
                if event.key == pygame.K_BACKSPACE:
                    ready = True
                    resetBoard()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawCursor(pygame.mouse.get_pos(), board)

            # update display
            drawBoard(screen)
            pygame.display.update()


def resetBoard():
    screen.fill(WHITE)
    initBoard()


# draw grids on display
def drawBoard(display):
    for i in range(1, recAmount):
        pygame.draw.line(display, (0, 0, 0), (0, i * recSize), (X, i * recSize), 1)
        pygame.draw.line(display, (0, 0, 0), (i * recSize, 0), (i * recSize, X), 1)


def initBoard():
    board = [[0] * recAmount for i in range(recAmount)]
    for i in range(len(board)):
        for j in range(len(board[i])):
            board[i][j] = Node(i, j)
    return board


def drawCursor(position, board):
    x = math.floor(position[0] / recSize)
    y = math.floor(position[1] / recSize)

    current = board[x][y]
    if current.blocked:
        current.removeColorOnBoard()
        current.blocked = False
    else:
        current.drawColorOnBoard((0, 0, 0))
        current.block()


# open list
open_list = []


def aStar(board, start, end):
    if start == end:
        return

    open_list.append(start)
    start.block()
    while len(open_list) > 0:
        current = min(open_list, key=attrgetter('fCost'))
        # current = min(open_list)
        open_list.remove(current)

        if current == end:
            printPath(start, current)
            return

        current.block()

        getNeighbors(board, current, end)


def getNeighbors(board, parent, end):
    x = parent.x
    y = parent.y

    for i in range(-1, 2):
        for j in range(-1, 2):
            # continue if current is parent
            if i == 0 and j == 0:
                continue
            # continue if outside of board
            if (x + i) >= recAmount or (x + i) < 0 or (y + j) >= recAmount or (y + j) < 0:
                continue

            current = board[x + i][y + j]

            if current.blocked:
                continue

            # update gCost
            # TODO
            if i == j:
                gCost = 10 + current.gCost
            else:
                gCost = 10 + current.gCost

            # if current is already in open list and gCost would be bigger continue
            if current in open_list and gCost >= current.gCost:
                continue
            current.gCost = gCost

            # set parent of current
            current.setParent(parent)

            # update fCost
            current.calculateHeuristic(end)
            current.calculateF()

            open_list.append(current)

            # TODO remove
            current.drawColorOnBoard(YELLOW)
            pygame.time.wait(100)


# prints path from end end to start
def printPath(start: Node, end: Node):
    if end == start:
        return
    end.drawColorOnBoard(BLUE)
    printPath(start, end.parent)


if __name__ == "__main__":
    main()
