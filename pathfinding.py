import math
from operator import attrgetter
import random

import pygame

pygame.init()
# height and width of window
X = 800
# create new Window
screen = pygame.display.set_mode((X, X))

# set amount of squares that make up grid and calculate their size
recAmount = 40
recSize = int(X / recAmount)

WHITE = (255, 255, 255)
LIGHT_BLUE = (100, 255, 255)
LIGHTER_BLUE = (180, 255, 255)
BLACK = (40, 40, 40)
RED = (255, 102, 102)
GREEN = (102, 255, 102)
PURPLE = (102, 102, 255)

# group of all colored squares
colored = pygame.sprite.Group()


# Rectangle class only used to drag and drop start and end
class Rec(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
        super().__init__()
        self.image = pygame.Surface([width, height])
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))
        self.rect = self.image.get_rect()
        self.color = color


# every square on the grid is represented by a Node object
class Node:
    def __init__(self, x, y):
        # make sure x and y lie within grid
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
        # used for maze generation
        self.visited = False

    def block(self):
        self.blocked = True

    def calculateF(self):
        self.fCost = self.hCost + self.gCost

    # using octile distance (Chebyshev distance with diagonal distance of sqrt(2))
    def calculateHeuristic(self, end):
        self.hCost = 10 * max(abs(end.x - self.x), abs(end.y - self.y)) \
                     + 4 * min(abs(end.x - self.x), abs(end.y - self.y))

    def setParent(self, parent):
        self.parent = parent

    # colors square at current position of node
    def drawColorOnBoard(self, color):
        r = Rec(color, recSize, recSize)
        r.rect.x = self.x * recSize
        r.rect.y = self.y * recSize
        colored.add(r)
        colored.draw(screen)
        drawBoard(screen)
        pygame.display.flip()

    def removeColorOnBoard(self):
        r = Rec(WHITE, recSize, recSize)
        r.rect.x = self.x * recSize
        r.rect.y = self.y * recSize
        colored.add(r)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# place start and end
START = Node(1, int(recAmount / 2) - 1)
END = Node(recAmount - 2, int(recAmount / 2) - 1)

# used to remove walls on grid
remove = False
# used so board can only be edited at beginning or after board has been reset
ready = True


def main():
    pygame.display.set_caption('A* Pathfinding')

    # internal representation of grid/board
    board = initBoard()
    setupBoard()

    # see above
    global ready
    global remove
    # used to draw walls
    mouse_down = False
    # used to drag and drop start and end to new location
    dragAndDrop = False
    # initiate rectangle which will be used to drag start and end
    drag = Rec(WHITE, 0, 0)

    # main event loop
    while True:
        for event in pygame.event.get():
            # quit program
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # press space to start pathfinding
                if event.key == pygame.K_SPACE and ready:
                    ready = False
                    aStar(board, START, END)

                # press backspace to reset board
                if event.key == pygame.K_BACKSPACE:
                    ready = True
                    setupBoard()
                    board = initBoard()
                    # remove everything from board
                    for square in colored:
                        colored.remove(square)
                    # reset start and end
                    START.x = 1
                    START.y = int(recAmount / 2) - 1
                    END.x = recAmount - 2
                    END.y = int(recAmount / 2) - 1
                    START.drawColorOnBoard(GREEN)
                    END.drawColorOnBoard(RED)

                # create random maze
                if event.key == pygame.K_m and ready:
                    blockAll(board)
                    generateMaze(Node(0, 0), board)

                    # place start and end
                    START.x = 0
                    START.y = 0
                    END.x = recAmount - 2
                    END.y = recAmount - 2
                    START.drawColorOnBoard(GREEN)
                    END.drawColorOnBoard(RED)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # left mouse-button to draw walls
                if event.button == 1:
                    mouse_down = True
                # right mouse-button to remove walls
                if event.button == 3:
                    remove = True
                    mouse_down = True

                x = math.floor(pygame.mouse.get_pos()[0] / recSize)
                y = math.floor(pygame.mouse.get_pos()[1] / recSize)
                # mouse currently over start => drag start
                if START.x == x and START.y == y and ready:
                    dragAndDrop = True
                    drag = Rec(GREEN, recSize, recSize)
                    drag.rect.x = START.x * recSize
                    drag.rect.y = START.y * recSize
                    START.removeColorOnBoard()
                # mouse currently over end => drag start
                elif END.x == x and END.y == y and ready:
                    dragAndDrop = True
                    drag = Rec(RED, recSize, recSize)
                    drag.rect.x = END.x * recSize
                    drag.rect.y = END.y * recSize
                    END.removeColorOnBoard()

            if event.type == pygame.MOUSEBUTTONUP:
                x = math.floor(pygame.mouse.get_pos()[0] / recSize)
                y = math.floor(pygame.mouse.get_pos()[1] / recSize)
                # end should not be placed on start and same for the other way around
                if x == END.x and y == END.y or x == START.x and y == START.y:
                    drag = Rec(WHITE, 0, 0)
                    START.drawColorOnBoard(GREEN)
                    END.drawColorOnBoard(RED)

                # place start (end) on square mouse is currently over
                elif dragAndDrop:
                    if drag.color == GREEN:
                        START.x = x
                        START.y = y
                        START.drawColorOnBoard(GREEN)
                        drag = Rec(WHITE, 0, 0)
                    elif drag.color == RED:
                        END.x = x
                        END.y = y
                        END.drawColorOnBoard(RED)
                        drag = Rec(WHITE, 0, 0)
                    # if end/start is placed on a wall remove blocked status in board
                    if board[x][y] is not None:
                        board[x][y].blocked = False

                mouse_down = False
                dragAndDrop = False
                remove = False

            if event.type == pygame.MOUSEMOTION:
                # draw rec to current mouse position to drag start/end
                if dragAndDrop:
                    x = pygame.mouse.get_pos()[0]
                    y = pygame.mouse.get_pos()[1]
                    drag.rect.x = x
                    drag.rect.y = y

            # continually draw walls while left mouse-button is held down
            if mouse_down:
                if not dragAndDrop:
                    setWall(pygame.mouse.get_pos(), board)
                    #pygame.time.Clock().tick(50)

            # update display
            screen.fill(WHITE)
            colored.update()
            colored.draw(screen)
            pygame.draw.rect(screen, drag.color, drag)
            drawBoard(screen)
            pygame.display.flip()


def setupBoard():
    screen.fill(WHITE)
    START.drawColorOnBoard(GREEN)
    END.drawColorOnBoard(RED)


# draw grids on display
def drawBoard(display):
    for i in range(1, recAmount):
        pygame.draw.line(display, (0, 0, 0), (0, i * recSize), (X, i * recSize), 1)
        pygame.draw.line(display, (0, 0, 0), (i * recSize, 0), (i * recSize, X), 1)


# initiate 2-dimensional array to internally represent grid
def initBoard():
    board = [[None] * recAmount for _ in range(recAmount)]
    for i in range(len(board)):
        for j in range(len(board[i])):
            board[i][j] = Node(i, j)
    return board


# place wall at current mouse position
def setWall(position, board):
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


# contains all known Nodes
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

        # color current square except start and end
        if current != start and current != end:
            current.drawColorOnBoard(LIGHTER_BLUE)

        expandNeighbors(board, current, end)


# add all viable neighbors of parent to open list
# and calculate their g-,h-,fCost and set their parents
def expandNeighbors(board, parent, end):
    x = parent.x
    y = parent.y

    # loop over all 8 neighbors of parent
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
            if abs(i) == abs(j):
                # neighbor lies diagonally
                gCost = 14 + parent.gCost
            else:
                gCost = 10 + parent.gCost

            # if current is already in open list and gCost (=distance of path to current) would be bigger continue
            if current in open_list and gCost >= current.gCost:
                continue

            open_list.append(current)

            current.setParent(parent)
            current.gCost = gCost
            current.calculateHeuristic(end)
            current.calculateF()

            if current != START and current != END:
                current.drawColorOnBoard(LIGHT_BLUE)
            pygame.time.wait(50)


# recursively prints path from end to start
def printPath(start: Node, end: Node):
    if end == start:
        return
    if end != END:
        end.drawColorOnBoard(PURPLE)
    printPath(start, end.parent)


# generate random maze with recursive backtracking
# http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking
def generateMaze(current: Node, board):

    current.drawColorOnBoard(WHITE)
    current.blocked = False
    current.visited = True

    neighbors = getNeighbors(current.y, current.x, board)

    while len(neighbors) > 0:

        n = neighbors.pop(random.randrange(0, len(neighbors)))

        if n.visited:
            continue

        middleX = int((n.x - current.x)/2) + current.x
        middleY = int((n.y - current.y)/2) + current.y
        board[middleX][middleY].drawColorOnBoard(WHITE)
        board[middleX][middleY].blocked = False

        generateMaze(n, board)


# TODO add comment
def getNeighbors(x, y, board):
    neighbors = []
    for i in range(-2, 3, 2):
        for j in range(-2, 3, 2):
            if (x + i) >= recAmount or (x + i) < 0 or (y + j) >= recAmount or (y + j) < 0 or (i == 0 and j == 0):
                continue
            if abs(i) == abs(j):
                continue

            neighbor = board[y + j][x + i]
            if neighbor.visited:
                continue

            neighbors.append(neighbor)
    return neighbors


def blockAll(board: []):
    START.drawColorOnBoard(BLACK)
    END.drawColorOnBoard(BLACK)
    for i in board:
        for j in i:
            j.block()
            j.visited = False
            r = Rec(BLACK, recSize, recSize)
            r.rect.x = j.x * recSize
            r.rect.y = j.y * recSize
            colored.add(r)

if __name__ == "__main__":
    main()
