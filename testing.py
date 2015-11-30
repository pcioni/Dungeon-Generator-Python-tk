from Tkinter import *
import random

class MapDraw:
    Colors = {
        "White": "#FFFFFF",
        "DarkBlue": "#081E38",
        "LightBlue": "#0D5EBA",
        "LightGreen": "#9BF04D",
        "DarkGreen": "#54822A",
        "LightRed": "#F72D2D",
        "DarkRed": "#850B0B",
        "Black": "#000000"
    }

    borderColors = {0: "White", 1: "DarkBlue", 2: "DarkGreen", 3: "DarkRed"}
    fillColors = {0: "White", 1: "LightBlue", 2: "LightGreen", 3: "LightRed"}

    def __init__(self, screenWidth, screenHeight, cellX, cellY):
        self.width = screenWidth
        self.height = screenHeight
        self.cell_x = cellX
        self.cell_y = cellY
        self.cell_width = screenWidth / cellX
        self.cell_height = screenHeight / cellY

        self.master = Tk()
        self.canvas = Canvas(self.master, width = self.width, height = self.height)
        self.canvas.pack()

    def drawTile(self, tileType, x, y):
        xPos = x * self.cell_width
        yPos = y * self.cell_height

        borderColor = self.borderColors[tileType]
        fillColor = self.fillColors[tileType]

        self.canvas.create_rectangle(xPos, yPos ,xPos+self.cell_width, yPos+self.cell_height, fill = self.Colors[borderColor], width = 0)
        self.canvas.create_rectangle(xPos + 1, yPos + 1 ,(xPos+self.cell_width) - 1 , (yPos+self.cell_height) - 1, fill = self.Colors[fillColor], width = 0)
        self.canvas.pack()

    def DrawMap(self, cellMap):
        self.canvas.delete("all")
        for x in range(0, self.cell_x):
            for y in range(0, self.cell_y):
                self.drawTile(cellMap[x][y], x, y)

        self.update()

    def update(self):
        self.master.update()

    def lock(self):
        self.master.mainloop()

class generateDungeon:
    def __init__(self, sizeX, sizeY):
        self.cell_x = sizeX
        self.cell_y = sizeY
        self.cellMap = [[0 for i in range(self.cell_y)] for j in range(self.cell_x)]
        #self.cellMap =  [ [0] * self.cell_y] * self.cell_x
        self.Drawupdates = False

    def createMapDraw(self, handler):
        self.GFX = handler
        self.Drawupdates = True

    def setTile(self, x, y, value):
        self.cellMap[x][y] = value

    def roomFits(self, x, y, width, height):
        if x < 1 or y < 1:
            return False
        if x + width > self.cell_x - 1 or y + height > self.cell_y - 1:
            return False

        for xP in range(0, width):
            for yP in range(0, height):
                if self.cellMap[xP+x][yP+y] != 0:
                    return False
        return True

    def fillRoom(self, x, y, width, height, value):
        for xP in range(0, width):
            for yP in range(0, height):
                self.setTile(xP+x, yP+y, value)

    def generateRooms(self, maxFailures, minWidth, minHeight, maxWidth, maxHeight):
        currentFailures = 0
        while currentFailures < maxFailures:
            w = random.randrange(minWidth, maxWidth)
            if w % 2 == 0:
                w -= 1

            h = random.randrange(minHeight, maxHeight)
            if h % 2 == 0:
                h -= 1

            xP = random.randrange(1, self.cell_x - w)
            if xP % 2 == 0:
                xP -= 1

            yP = random.randrange(1, self.cell_y - h)
            if yP % 2 == 0:
                yP -= 1

            if self.roomFits(xP, yP, w, h):
                self.fillRoom(xP, yP, w, h, 1)
            else:
                currentFailures += 1

    def generateMaze(self):
        regions = []
        for x in range(0, self.cell_x):
            for y in range(0,self.cell_y):
                cells = self.getAdjacentCells(x, y)
                if not ((1 in cells) or (2 in cells)):
                    region = self.buildRegion(x, y, [0])
                    prunedRegion = []
                    for cell in region:
                        if not 1 in self.getAdjacentCells(cell[0], cell[1]):
                            prunedRegion.append(cell)
                        else:
                            self.setTile(cell[0], cell[1], 2)
                    regions.append(prunedRegion)
                    self.createMazeInRegion(prunedRegion)

        """
        for x in range(0, self.cell_x):
            for y in range(0,self.cell_y):
                if self.cellMap[x][y] == 2:
                    self.setTile(x, y, 0)
                if self.cellMap[x][y] == 3:
                    self.setTile(x, y, 2)
        """

        self.cellMap = [ [ 0 if x == 2 else 2 if x == 3 else x for x in self.cellMap[j] ] for j in range(len(self.cellMap)) ]

    def pointInRegion(self, x, y, regions):
        for region in regions:
            if [x,y] in region:
                return True
        return False

    def buildRegion(self, x, y, acceptedValues):
        region, queue = [], [ [x, y] ]

        while len(queue) > 0:
            nextRegion = queue.pop()
            region.append(nextRegion)
            nX = nextRegion[0]
            nY = nextRegion[1]

            if nX > 0 and self.cellMap[nX-1][nY] in acceptedValues and not [nX-1, nY] in region:
                queue.append([nX - 1, nY])
            if nX < self.cell_x - 1 and self.cellMap[nX+1][nY] in acceptedValues and not [nX+1, nY] in region:
                queue.append([nX + 1, nY])
            if nY > 0 and self.cellMap[nX][nY-1] in acceptedValues and not [nX, nY-1] in region:
                queue.append([nX, nY - 1])
            if nY < self.cell_y - 1 and self.cellMap[nX][nY+1] in acceptedValues and not [nX, nY+1] in region:
                queue.append([nX, nY + 1])

        return region

    def regionTouchesConnector(self, region):
        for cell in region:
            if self.getCardinalCells(cell[0], cell[1]).count(3) > 1: return True
        return False

    def regionTouchesPoint(self, region, x, y):
        for cell in region:
            if abs(cell[0] - x) <= 1 and abs(cell[1] - y) <= 1 and abs(cell[0] - x) + abs(cell[1] - y) != 2 : return True
        return False

    def connectregions(self):
        prunedConnectors, regions = [], []

        for x in range(0, self.cell_x):
            for y in range(0, self.cell_y):
                if self.cellMap[x][y] == 0:
                    card = self.getCardinalCells(x, y)
                    if card.count(1) > 0 and card.count(2) > 0 or card.count(1) == 2:
                        self.setTile(x, y, 3)
                        prunedConnectors.append([x,y])
                if self.cellMap[x][y] in range(1, 3) and not self.pointInRegion(x, y, regions):
                    regions.append(self.buildRegion(x,y,[1,2]))


        prunedRegions = []
        for region in regions:
            if not self.regionTouchesConnector(region):
                for cell in region:
                    self.setTile(cell[0], cell[1], 0)
            else:
                prunedRegions.append(region)


        while len(prunedConnectors) > 0:
            if self.Drawupdates:
                self.GFX.DrawMap(self.cellMap)
            candidateConnector = prunedConnectors[random.randrange(0, len(prunedConnectors))]
            prunedConnectors.remove(candidateConnector)
            card = self.getCardinalCells(candidateConnector[0], candidateConnector[1])
            self.setTile(candidateConnector[0], candidateConnector[1], 1)

            if (card.count(2) > 0 and card.count(1) > 0) or card.count(1) == 2:
                self.setTile(candidateConnector[0], candidateConnector[1], 2)

                connectedRegions = [region for region in prunedRegions if
                                    self.regionTouchesPoint(region, candidateConnector[0], candidateConnector[1])]
                newRegion = []
                for region in connectedRegions:
                    newRegion = newRegion + region
                    prunedRegions.remove(region)
                prunedRegions.append(newRegion)

                newPrunedConnectors = []
                for connector in prunedConnectors:
                    regionCount = 0
                    for region in prunedRegions:
                        if self.regionTouchesPoint(region, connector[0], connector[1]):
                            regionCount += 1
                            if regionCount == 2:
                                newPrunedConnectors.append(connector)
                                break
                    if regionCount < 2:
                        self.setTile(connector[0], connector[1], 0)
                    prunedConnectors = newPrunedConnectors[:]
            else:
                self.setTile(candidateConnector[0], candidateConnector[1], 0)

    def createMazeInRegion(self, region):
        while len(region) > 0:
            eligible = []

            start = region.pop(random.randrange( 0, len(region) ) )

            if self.getCardinalCells(start[0], start[1]).count(3) <= 1:
                self.setTile(start[0], start[1], 3)
                for i in range(-1, 2, 2):
                    if [start[0]+i, start[1]] in region:
                            eligible.append( [start[0]+i, start[1]] )
                    if [start[0], start[1]+i] in region:
                            eligible.append( [start[0], start[1]+i] )



                while len(eligible) > 0:
                    candidate = eligible.pop(random.randrange(0, len(eligible) ) )

                    if self.getCardinalCells(candidate[0], candidate[1]).count(3) == 1:
                        self.setTile(candidate[0], candidate[1], 3)
                        for i in range(-1, 2, 2):
                            if ( [candidate[0]+i,candidate[1]] in region
                                    and self.cellMap[candidate[0]+i][candidate[1]] == 2
                                    and self.getCardinalCells(candidate[0]+i, candidate[1]).count(3) == 1 ):
                                eligible.append([candidate[0]+i,candidate[1]])

                            if ( [candidate[0],candidate[1]+i] in region
                                    and self.cellMap[candidate[0]][candidate[1]+i] == 2
                                    and self.getCardinalCells(candidate[0],candidate[1]+i).count(3) == 1 ):
                                eligible.append( [start[0], start[1]+i] )

                    region.remove(candidate)

    def pruneDeadEnds(self):
        tileRemoved = True
        while tileRemoved:
            tileRemoved = False
            for x in range(0, self.cell_x):
                for y in range(0, self.cell_y):
                    if self.cellMap[x][y] == 2:
                        threshold = 3
                        if x == 0:
                             threshold -= 1

                        if x == self.cell_x - 1:
                            threshold -= 1

                        if y == 0:
                            threshold -= 1

                        if y == self.cell_y - 1:
                            threshold -= 1
                        if self.getCardinalCells(x,y).count(0) == threshold:
                            self.setTile(x, y, 0)
                            tileRemoved = True
                            if self.Drawupdates:
                                self.GFX.DrawMap(self.cellMap)


    def pointTouchesTwoRegions(self, regions, point):
        connectedRegions = []

        for region in regions:
            if point[0] > 0:
                if not region in connectedRegions and [point[0]-1,point[1]] in region:
                    connectedRegions.append(region)
            if point[0] < self.cell_x - 1:
                if not region in connectedRegions and [point[0]+1,point[1]] in region:
                    connectedRegions.append(region)
            if point[1] > 0:
                if not region in connectedRegions and [point[0],point[1]-1] in region:
                    connectedRegions.append(region)
            if point[1] < self.cell_y - 1:
                if not region in connectedRegions and [point[0],point[1]+1] in region:
                    connectedRegions.append(region)

        return len(connectedRegions) >= 2

    def getCardinalCells(self, x, y):
        cells = []

        if x > 0:
            cells.append(self.cellMap[x-1][y])

        if x < self.cell_x - 1:
            cells.append(self.cellMap[x+1][y])

        if y > 0:
            cells.append(self.cellMap[x][y-1])

        if y < self.cell_y - 1:
            cells.append(self.cellMap[x][y+1])

        return cells

    def getAdjacentCells(self, x, y):
        cells = []
        if x > 0:
            cells.append(self.cellMap[x-1][y])

        if x < self.cell_x - 1:
            cells.append(self.cellMap[x+1][y])

        if y > 0:
            cells.append(self.cellMap[x][y-1])

        if y < self.cell_y - 1:
            cells.append(self.cellMap[x][y+1])

        if x > 0 and y > 0:
            cells.append(self.cellMap[x-1][y-1])

        if x > 0 and y < self.cell_y - 1:
         cells.append(self.cellMap[x-1][y+1])

        if x < self.cell_x - 1 and y > 0:
            cells.append(self.cellMap[x+1][y-1])

        if x < self.cell_x - 1 and y < self.cell_y - 1:
            cells.append(self.cellMap[x+1][y+1])

        return cells

GFX = MapDraw(800,600,80,60)
MG = generateDungeon(80,60)
MG.createMapDraw(GFX)
MG.generateRooms(5000, 3, 3, 11, 11)
MG.generateMaze()
MG.connectregions()
MG.pruneDeadEnds()
GFX.DrawMap(MG.cellMap)
GFX.lock()
