import pygame
import math
import random


running = True
drawPaths = True
screenX = 2500
screenY = 1300

speedMod = 1

tickCount = 0

u = []
original = []

controlsString = """Space: reset current sim
R:     New simulation
Num +: Increase sim speed
Num -: Decrease sim speed
P:     Hide path
Mouse 1: Add body
"""


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Body:
    def __init__(self, mass, x, y, vX, vY):
        self.x = x
        self.y = y
        self.iX = x
        self.iY = y
        
        self.vX = vX
        self.vY = vY
        self.fX = 0
        self.fY = 0
        self.mass = mass
        
        self.radius = mass / 16000
        
        self.color = (random.randrange(50, 255), random.randrange(50, 255), random.randrange(50, 255))
        self.path = [] # Stores former coordinates to render body's path
        
    def startTick(self):
        self.fX = 0
        self.fY = 0

    def addForceVector(self, b):
        radius = self.distanceTo(b)
        unitVector = self.unitVectorTo(b)

        force = getF(self, b, radius)
        
        forceX = force * unitVector[0]
        forceY = force * unitVector[1]
        
        self.fX += forceX
        self.fY += forceY
        
    def updateCoords(self):
        self.x += self.vX
        self.y += self.vY
        
        global tickCount
        if tickCount % 20 == 0:
            self.path.append(Point(self.x, self.y))
            if len(self.path) > 400:
                self.path.pop(0)
            

    def updateVelocity(self):
        aX = self.fX / self.mass
        aY = self.fY / self.mass

        
        self.vX += aX
        self.vY += aY

    def finishTick(self):
        self.fX = 0.0
        self.fY = 0.0


    def distanceTo(self, b):
        dX = self.x - b.x
        dY = self.y - b.y

        return math.sqrt( dX ** 2 + dY ** 2)
        
    def unitVectorTo(self, b):
        radius = self.distanceTo(b)
        
        if radius == 0:
            return (0, 0)
        
        return ( ((self.x - b.x) / radius), ((self.y - b.y) / radius))

def getF(b1, b2, r):
    global speedMod
    if r == 0:
        return 0
        
    # Assume bodies aren't actually clipping through each other for calculating gravitational force
    if r < b1.radius or r < b2.radius:
        r = max(b1.radius, b2.radius)
    return (-6.67 * pow(10, -11)) * ((b1.mass * b2.mass) / r) * 100000 * speedMod

def tick(u):
    global tickCount
    tickCount += 1
    
    for b1 in u:
        b1.startTick()
    
    for b1 in u:
        for b2 in u:
            if b1 is b2:
                continue
            b1.addForceVector(b2)
            b2.addForceVector(b1)

    for b in u:
        b.updateVelocity()
        b.updateCoords()
        b.finishTick()


def handleInput(u):
    global running
    global speedMod
    global drawPaths
    global original
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                u.append(Body(100000, event.pos[0], event.pos[1], 0, 0))
        elif event.type == pygame.KEYUP:
            
            if event.key == pygame.K_SPACE:
                reset(u)
            elif event.key == pygame.K_n:
                randomize()
            elif event.key == pygame.K_p:
                drawPaths = not drawPaths
            elif event.key == pygame.K_KP_PLUS:
                if speedMod < 10000:
                    speedMod *= 10
                if speedMod > 10000:
                    speedMod = 10000
            elif event.key == pygame.K_KP_MINUS:
                if speedMod > 1:
                    speedMod /= 10
                if speedMod < 1:
                    speedMod = 1

def initScreen():
    pygame.init()

    global screenX
    global screenY

    screen = pygame.display.set_mode((screenX, screenY))
    pygame.display.set_caption("3Body")
    
    return screen
    
def initFont():
    pygame.font.init()
    return pygame.font.SysFont("Arial", 20)

def refresh(screen, font, u):
    global screenX
    global screenY
    
    screen.fill((0, 0, 0))
    
    textSurface = font.render(f"Speed: x{speedMod}", True, (255, 255, 255))
    screen.blit(textSurface, (30, 30))
    
    offset = 0
    for line in controlsString.split("\n"):
        
        controlsSurface = font.render(line, True, (255, 255, 255))
        screen.blit(controlsSurface, (screenX - 300, screenY + offset - 200))
        offset += 20#font.get_height()
    
    
    for b in u:
        pygame.draw.circle(screen, b.color, (b.x, b.y), b.radius)
        
        if drawPaths:
            i = 0
            for point in b.path:
                
                pygame.draw.circle(screen, 
                    (b.color[0], b.color[1], b.color[2], 255),#255 * (400 / (400 + (i * 80)))),
                    (point.x, point.y),
                    2)
                i += 1
    
    pygame.display.flip()
    
def reset(u):
    for b in u:
        b.x = b.iX
        b.y = b.iY
        b.vX = 0
        b.vY = 0
        b.aX = 0
        b.aY = 0
        b.fX = 0
        b.fY = 0
        
        b.path.clear()
        
def randomize():
    global u
    reset(u)
    u = original.copy()
    
    global screenX
    global screenY
    for b in u:
        b.iX = random.randrange(500, screenX - 500)
        b.x = b.iX
        b.iY = random.randrange(500, screenY - 500)
        b.y = b.iY


def threeBodyWorld():
    u = []
    u.append(Body(100000, 400, 500, 0.0, -0.0))
    u.append(Body(100000, 600, 500, 0.0, -0.07))
    u.append(Body(100000, 1000, 900, 0.0, 0.0))
    return u
    
def coorbit():
    u = []
    u.append(Body(100000, 400, 500, 0.0, 0.6))
    u.append(Body(100000, 700, 500, 0.0, -0.6))
    return u
    
def trisolaris():
    u = []
    u.append(Body(100000, 400, 500, 0.0, -0.0))
    u.append(Body(100000, 600, 500, 0.0, -0.07))
    u.append(Body(100000, 1000, 900, 0.0, 0.0))
    u.append(Body(100, 500, 700, 0.0, 0.0))
    u[3].radius = 4
    return u
    
def rings():
    global drawPaths
    
    drawPaths = False
    u = []
    u.append(Body(100000, 800, 500, 0, 0))
    
    deg = 0.0
    for i in range(0, 36):
        b = Body(1, 800 + math.cos(math.radians(deg)) * 200, 500 + math.sin(math.radians(deg)) * 200, math.sin(math.radians(deg)), -math.cos(math.radians(deg)))
        deg += 10
        b.radius = 2
        u.append(b)
    return u

def earthAndSunWorld():
    b1 = Body(1000, 400, 500, 0.0, -0.0)
    b2 = Body(1, 600, 500, 0.0, -1.2)
    
    global speedMod
    speedMod = 100
    
    b1.radius = 15
    b2.radius = 5
    
    return [b1, b2]

#u = threeBodyWorld()
#u = earthAndSunWorld()
u = trisolaris()
#u = coorbit()
#u = rings()
original = u.copy()


screen = initScreen()
font = initFont()

while(running):
    handleInput(u)
    tick(u)
    refresh(screen, font, u)
    pygame.time.delay((10))


