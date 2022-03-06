import math
from operator import attrgetter

import pygame

# initiate pygame
pygame.init()
# size of board
X = 800
# create new Window
screen = pygame.display.set_mode((X, X))

# set amount of rectangles that make up grid
recAmount = 20
recSize = int(X / recAmount)

# colors for later use
WHITE = (255, 255, 255)
LIGHT_BLUE = (150, 240, 255)
BLACK = (20, 20, 20)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Node:

    def __init__(self, x, y):
        if x > 0 or y > 0 or x < recAmount or y < recAmount:
            self.x = x
            self.y = y
        else:
            self.x = 0
            self.y = 0

        self.parent = any
        self.blocked = False
        self.fCost = 0
        self.gCost = 0
        self.hCost = 0

    def block(self):
        self.blocked = True

    def calculateF(self):
        self.fCost = self.hCost + self.gCost

    def calculateHeuristic(self, end):
        self.hCost = round(math.sqrt(abs(self.x - end.x)) + math.sqrt(abs(self.y - end.y)))

    def setParent(self, parent):
        self.parent = parent

    # colors rectangle at current position of node
    def drawColorOnBoard(self, color):
        pygame.draw.rect(screen, color, pygame.Rect(self.x * recSize, self.y * recSize, recSize, recSize))
        drawBoard(screen)
        pygame.display.update()

    def removeColorOnBoard(self):
        pygame.draw.rect(screen, WHITE, pygame.Rect(self.x * recSize, self.y * recSize, recSize, recSize))
        drawBoard(screen)
        pygame.display.update()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# place start and end
START = Node(0, int(recAmount / 2) - 1)
END = Node(recAmount - 1, int(recAmount / 2) - 1)

# TODO
remove = False
ready = True


def main():
    # set caption

    pygame.display.set_caption('A* Pathfinding')

    # internal representation of grid/board
    board = initBoard()
    setupBoard()

    global ready
    mouse_down = False
    global remove
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
                    setupBoard()
                    board = initBoard()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                if event.button == 3:
                    remove = True
                    mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                remove = False

            if mouse_down:
                drawCursor(pygame.mouse.get_pos(), board)
                pygame.time.Clock().tick(50)
            # update display
            drawBoard(screen)
            pygame.display.update()


def setupBoard():
    screen.fill(WHITE)

    # show start and end
    START.drawColorOnBoard(GREEN)
    END.drawColorOnBoard(RED)


# draw grids on display
def drawBoard(display):
    for i in range(1, recAmount):
        pygame.draw.line(display, (0, 0, 0), (0, i * recSize), (X, i * recSize), 1)
        pygame.draw.line(display, (0, 0, 0), (i * recSize, 0), (i * recSize, X), 1)


def initBoard():
    board = [[None] * recAmount for i in range(recAmount)]
    for i in range(len(board)):
        for j in range(len(board[i])):
            board[i][j] = Node(i, j)
    return board


def drawCursor(position, board):
    x = math.floor(position[0] / recSize)
    y = math.floor(position[1] / recSize)

    current = board[x][y]
    if current == START or current == END or not ready:
        return

    if current.blocked and remove:
        current.removeColorOnBoard()
        current.blocked = False
    elif not remove:
        current.drawColorOnBoard(BLACK)
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
                gCost = 14 + current.gCost
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

            if current != START and current != END:
                current.drawColorOnBoard(LIGHT_BLUE)
            pygame.time.wait(50)


#TODO RENAME
# prints path from end end to start
def printPath(start: Node, end: Node):
    if end == start:
        return
    if end != END:
        end.drawColorOnBoard(BLUE)
    printPath(start, end.parent)
    open_list.clear()


if __name__ == "__main__":
    main()
