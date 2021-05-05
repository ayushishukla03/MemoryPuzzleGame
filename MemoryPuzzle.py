import random, pygame, sys
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program
SCREENWIDTH = 660 # screen's width in pixels
SCREENHEIGHT = 460 # screen's height in pixels
REVEALSPEED = 6 # speed of boxes' sliding reveals and covers
BOXSIZE = 40 # box height & width
GAPSIZE = 20 # gap between boxes
BOARDWIDTH = 8 # number of columns of icons
BOARDHEIGHT = 6 # number of rows of icons
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
XMARGIN = int((SCREENWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((SCREENHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
BLACK    = ( 0,   0,    0)
NEON     = (22.4, 100, 7.8)

BGCOLOR = BLACK
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = NEON

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'
CIRCLE = 'circle'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL, CIRCLE)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."

def main():
    global FPSCLOCK, DISPLAYSCREEN
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Puzzle Game')

    mainBoard = getRandomizedBoard()
    revealedBox = generateRevealedBoxData(False)

    firstSelection = None # stores the (x, y) of the first box clicked.

    DISPLAYSCREEN.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True: # main game loop
        mouseClicked = False

        DISPLAYSCREEN.fill(BGCOLOR) # drawing the window
        drawBoard(mainBoard, revealedBox)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        box_x, box_y = getBoxAtPixel(mousex, mousey)
        if box_x != None and box_y != None:
            # The mouse is currently over a box.
            if not revealedBox[box_x][box_y]:
                drawHighlightBox(box_x, box_y)
            if not revealedBox[box_x][box_y] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(box_x, box_y)])
                revealedBox[box_x][box_y] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (box_x, box_y)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, box_x, box_y)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (box_x, box_y)])
                        revealedBox[firstSelection[0]][firstSelection[1]] = False
                        revealedBox[box_x][box_y] = False
                    elif hasWon(revealedBox): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # Reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBox = generateRevealedBoxData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBox)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstSelection = None # reset firstSelection variable

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRevealedBoxData(val):
    revealedBox = []
    for i in range(BOARDWIDTH):
        revealedBox.append([val] * BOARDHEIGHT)
    return revealedBox


def getRandomizedBoard():
    # Get a list of every possible shape in every possible color.
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append( (shape, color) )

    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2) # calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 # make two of each
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board


def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(box_x, box_y):
    # Convert board coordinates to pixel coordinates
    left = box_x * (BOXSIZE + GAPSIZE) + XMARGIN
    top = box_y * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(box_x, box_y)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (box_x, box_y)
    return (None, None)


def drawIcon(shape, color, box_x, box_y):
    quarter = int(BOXSIZE * 0.25) # syntactic sugar
    half =    int(BOXSIZE * 0.5)  # syntactic sugar

    left, top = leftTopCoordsOfBox(box_x, box_y) # get pixel coords from board coords
    # Draw the shapes
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSCREEN, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSCREEN, BGCOLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSCREEN, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSCREEN, color, ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSCREEN, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSCREEN, color, (left + i, top + BOXSIZE - 1), (left + BOXSIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSCREEN, color, (left, top + quarter, BOXSIZE, half))


def getShapeAndColor(board, box_x, box_y):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[box_x][box_y][0], board[box_x][box_y][1]


def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSCREEN, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSCREEN, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    #  "box reveal" animation.
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    #  "box cover" animation.
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in  covered or revealed state.
    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(box_x, box_y)
            if not revealed[box_x][box_y]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSCREEN, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the revealed icon.
                shape, color = getShapeAndColor(board, box_x, box_y)
                drawIcon(shape, color, box_x, box_y)


def drawHighlightBox(box_x, box_y):
    left, top = leftTopCoordsOfBox(box_x, box_y)
    pygame.draw.rect(DISPLAYSCREEN, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)


def startGameAnimation(board):
    # Randomly reveal 8 boxes at a time when game starts.
    coveredBoxes = generateRevealedBoxData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    # when the player has won flash the background color
    coveredBoxes = generateRevealedBoxData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        DISPLAYSCREEN.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBox):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBox:
        if False in i:
            return False # return False if any boxes are covered.
    return True


if __name__ == '__main__':
    main()
