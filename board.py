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
LIGHT_BLUE = (100, 230, 255)
LIGHT_GREEN = (150, 255, 180)
BLACK = (30, 30, 30)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (50, 50, 255)

group = pygame.sprite.Group()


class Rec(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
        super().__init__()

        self.image = pygame.Surface([width, height])
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))
        self.rect = self.image.get_rect()
        self.color = color


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
        # self.hCost = abs(self.x - end.x) + abs(self.y - end.y)

        self.hCost = 10 * max(abs(end.x - self.x), abs(end.y - self.y)) + 4*min(abs(end.x - self.x), abs(end.y - self.y))

    def setParent(self, parent):
        self.parent = parent

    # colors rectangle at current position of node
    def drawColorOnBoard(self, color):
        # pygame.draw.rect(screen, color, pygame.Rect(self.x * recSize, self.y * recSize, recSize, recSize))
        # drawBoard(screen)
        # pygame.display.update()
        r = Rec(color, recSize, recSize)
        r.rect.x = self.x * recSize
        r.rect.y = self.y * recSize
        group.add(r)
        group.update()
        group.draw(screen)
        drawBoard(screen)
        pygame.display.flip()

    def removeColorOnBoard(self):
        # pygame.draw.rect(screen, WHITE, pygame.Rect(self.x * recSize, self.y * recSize, recSize, recSize))
        # drawBoard(screen)
        # pygame.display.update()
        r = Rec(WHITE, recSize, recSize)
        r.rect.x = self.x * recSize
        r.rect.y = self.y * recSize
        group.add(r)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# place start and end
START = Node(0, int(recAmount / 2) - 1)
END = Node(recAmount - 1, int(recAmount / 2) - 1)

# TODO
remove = False
ready = True
rectangle = pygame.sprite.Group()


def main():
    # set caption

    pygame.display.set_caption('A* Pathfinding')

    # internal representation of grid/board
    board = initBoard()
    setupBoard()

    global ready
    mouse_down = False
    global remove
    dragAndDrop = False

    rec = Rec(WHITE, 0, 0)

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
                    START.x = 0
                    START.y = int(recAmount / 2) - 1
                    END.x = recAmount - 1
                    END.y = int(recAmount / 2) - 1
                    START.drawColorOnBoard(GREEN)
                    END.drawColorOnBoard(RED)
                    for e in group:
                        if (math.floor(e.rect.x / recSize) != START.x or (math.floor(e.rect.y / recSize) != START.y)) \
                                and (
                                math.floor(e.rect.x / recSize) != END.x or (math.floor(e.rect.y / recSize) != END.y)):
                            group.remove(e)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

                x = math.floor(pygame.mouse.get_pos()[0] / recSize)
                y = math.floor(pygame.mouse.get_pos()[1] / recSize)
                if START.x == x and START.y == y:
                    dragAndDrop = True
                    rec = Rec(GREEN, recSize, recSize)
                    rec.rect.x = START.x * recSize
                    rec.rect.y = START.y * recSize
                    START.removeColorOnBoard()

                elif END.x == x and END.y == y:
                    dragAndDrop = True
                    rec = Rec(RED, recSize, recSize)
                    rec.rect.x = END.x * recSize
                    rec.rect.y = END.y * recSize
                    END.removeColorOnBoard()

                if event.button == 3:
                    remove = True
                    mouse_down = True

            if event.type == pygame.MOUSEBUTTONUP:
                x = math.floor(pygame.mouse.get_pos()[0] / recSize)
                y = math.floor(pygame.mouse.get_pos()[1] / recSize)
                if x == END.x and y == END.y or x == START.x and y == START.y:
                    rec = Rec(WHITE, 0, 0)
                    START.drawColorOnBoard(GREEN)
                    END.drawColorOnBoard(RED)

                elif dragAndDrop:
                    if rec.color == GREEN:
                        START.x = x
                        START.y = y
                        START.drawColorOnBoard(GREEN)
                        rec = Rec(WHITE, 0, 0)
                    elif rec.color == RED:
                        END.x = x
                        END.y = y
                        END.drawColorOnBoard(RED)
                        rec = Rec(WHITE, 0, 0)
                    if board[x][y] is not None:
                        board[x][y].blocked = False

                mouse_down = False
                dragAndDrop = False
                remove = False

            if event.type == pygame.MOUSEMOTION:
                if dragAndDrop:
                    x = math.floor(pygame.mouse.get_pos()[0])
                    y = math.floor(pygame.mouse.get_pos()[1])
                    rec.rect.x = x
                    rec.rect.y = y

            if mouse_down:
                if not dragAndDrop:
                    drawCursor(pygame.mouse.get_pos(), board)
                    pygame.time.Clock().tick(50)
            # update display

            screen.fill(WHITE)
            group.update()
            group.draw(screen)
            pygame.draw.rect(screen, rec.color, rec)
            drawBoard(screen)
            pygame.display.flip()


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

    while len(open_list) > 0:
        current = min(open_list, key=attrgetter('fCost'))
        open_list.remove(current)
        current.block()

        if current == end:
            printPath(start, current)
            open_list.clear()
            return

        if current != START and current != END:
            current.drawColorOnBoard(LIGHT_BLUE)

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
            if abs(i) == abs(j):
                gCost = 14 + parent.gCost
            else:
                gCost = 10 + parent.gCost

            # if current is already in open list and gCost is smaller change parent
            if current in open_list and gCost >= current.gCost:
                continue

            open_list.append(current)

            # update fCost
            current.setParent(parent)
            current.gCost = gCost
            current.calculateHeuristic(end)
            current.calculateF()

            if current != START and current != END:
                current.drawColorOnBoard(LIGHT_GREEN)
            pygame.time.wait(20)


# prints path from end end to start
def printPath(start: Node, end: Node):
    if end == start:
        return
    if end != END:
        end.drawColorOnBoard(BLUE)
    printPath(start, end.parent)


if __name__ == "__main__":
    main()
