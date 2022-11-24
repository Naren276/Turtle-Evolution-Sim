# Dependacices
import pygame
import math
import random
import time
import os
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab


#Global Consts

img_folder = os.path.dirname(__file__ )
img_folder += "/imgs"
turtles = []
food = []
SURFACE_COLOR = (200, 200, 200)
WHITE = (255,255,255)
fturtles = 350
Seed = None#int(time.time()) #########SEED TO COPY DOES NOT WORK FOR EDIT GENES#######
updatespermove= 15 #base 30

# GLOBALS
turtlecount = 100
foodcount = 200
maxfoodcount = 300
minfoodcount = 0
maxturtlecount = 200
startingenergy = 499
energyinfood = 200
energyinturtle = 400
chasethreshold = 200
runawaythreshold = 100
Attackspeedmod = 0
movesbeforenewgen = 700
foodgrowthmod = 2
turtlegrowthmod = 2
speedmod = 100
fooddepletionrate = 2
mutationrate = 100
blank = "TES"

varibles = ["turtlecount",
"foodcount","maxfoodcount","minfoodcount","maxturtlecount","startingenergy","energyinfood",
"energyinturtle","chasethreshold","runawaythreshold","Attackspeedmod","movesbeforenewgen","foodgrowthmod","turtlegrowthmod",
"speedmod","fooddepletionrate","mutationrate", "Seed","blank"]
vardata = []
[exec("vardata.append({})".format(i)) for i in varibles]

moves = 0
gen = 1
exit = True

pygame.font.init() 
my_font = pygame.font.SysFont('Aerial', 20) 
captionfont = pygame.font.SysFont('Aerial', 25) 
Titelfont =  pygame.font.SysFont('Aerial', 30, bold= True) 
pygame.init()


#starimage = pygame.image.load("foodpellet.png")
predatorturtlescount = []
turtlescountovertime = []
foodcountovertime = []
inputfromtext = None

colors = {"redturtles.png": "red",
        "blueturtles.png": "blue",
        "greenturtles.png": "green",
        "purpleturtles.png": "purple",
        "blackturtles.png": "black", 
        "greyturtles.png": "grey" }
winsize = (1300,700)
size = ((50,900),(50, 575))

Tgroup = pygame.sprite.Group()
Fgroup = pygame.sprite.Group()

class Sprite(pygame.sprite.Sprite):
    def __init__(self, color, tofood, toturtle, strength, speed, eysight, health):
        super().__init__()

        self.target = (random.randint(size[0][0],size[0][1]),random.randint(size[1][0],size[1][1]))

        self.color = color
        self.tofood = tofood
        self.toturtle = toturtle
        self.strength = strength
        self.speed = speed
        self.eyesight = eysight
        self.health = health
        self.oghealth = health
        self.energy = startingenergy

        #Calculate Choices.
        self.reverseangle = False

        self.choice = ""
        self.runaway = False
        self.ispredator = False
        if self.toturtle > self.tofood:
            self.ispredator = True
        if self.toturtle * 2 <= self.tofood:
            self.runaway = True 
        

        self.floatx = 0
        self.floaty = 0 
        self.rotation = 0
        
        self.image = pygame.image.load(os.path.join(img_folder, color[0]))
        self.orig_image =self.image
        self.rect = self.image.get_rect()
    
    def rotate(self):

        self.image = pygame.transform.rotozoom(self.orig_image, self.rotation * -1,1)
        self.rect = self.image.get_rect(center=self.rect.center)
        
    def getgene(self):
        return [self.color[1], self.tofood,self.toturtle,self.strength,self.speed, self.eyesight,self.oghealth ]
    def update(self):
        if selectedturtle == self:
            pygame.draw.rect(screen, (212,175,55), self.rect)
        screen.blit(self.image, self.rect)
        
    def getangle(self, x2,y2):
        myradians = math.atan2(y2 - self.floaty, x2 - self.floatx)
        mydegrees = math.degrees(myradians)
        return mydegrees


    def findclose(self, list, distance):
        
        min = distance
        for i in list:
            if abs(self.rect.x - i.rect.x)+ abs(self.rect.y - i.rect.y) < min:
                if list == food: 
                    min = abs(self.rect.x - i.rect.x) + abs(self.rect.y - i.rect.y)
                    self.target = (i.rect.x,i.rect.y)
                elif i.getgene() != self.getgene():
                    
                    min = abs(self.rect.x - i.rect.x) + abs(self.rect.y - i.rect.y)
                    self.target= (i.rect.x, i.rect.y)
        
        if min == distance: return False
        else: return True  


    def getchoice(self):
        
        if not self.ispredator and not self.runaway:
            if food: self.findclose(food, self.eyesight) 
            self.choice = "Food"
            return "food"
        elif self.ispredator:
            if self.eyesight > chasethreshold:
                if not self.findclose([i for i in turtles if not i.ispredator], chasethreshold):
                    self.findclose(turtles,self.eyesight)
                self.choice = "Turtle"
                return "turtle"
            else:
                if not self.findclose([i for i in turtles if not i.ispredator], self.eyesight):
                    self.findclose(turtles,self.eyesight)
                self.choice = "Turtle"
                return "turtle"
        else: 
            if not self.findclose([i for i in turtles if i.ispredator], runawaythreshold ):
                if food: self.findclose(food, self.eyesight) 
                self.choice = "Food"
                return "food"
            else:
                
                self.reverseangle = True
                self.choice = "Run"
                return "run"

class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image =  pygame.image.load(os.path.join(img_folder,"foodpellet.png"))
        self.rect= self.image.get_rect()
    def update(self):
        screen.blit(self.image, self.rect)

class TextInput():
    def __init__(self,x1,x2,y1,y2, Acolor,Ucolor):
        self.inactivecolor = Ucolor
        self.activecolor = Acolor
        self.color = self.inactivecolor
        self.caption = ""
        self.text = ""
        self.rect = pygame.Rect(x1, x2, y1, y2)
        self.image = captionfont.render(self.text, True, (0,0,0))
        self.captionimage = captionfont.render(self.caption, True,(0,0,0))



    def getinput(self, caption = "Input:"):
        self.caption = caption
        self.captionimage = captionfont.render(self.caption, True,(0,0,0))

    def update(self):
        #self.captionimage = captionfont.render(self.caption, True,(0,0,0))

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            temp = self.text
            self.text = ""
            self.caption  = ""
            self.captionimage = captionfont.render(self.caption, True,(0,0,0))
            
            return temp
        
        self.image = captionfont.render(self.text, True, (0,0,0))
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.captionimage, (self.rect.x  + self.rect.w/2 - self.captionimage.get_rect().w/2, self.rect.y - 20))
        screen.blit(self.image, self.rect)

class Button:
    def __init__(self, text, pos, tcolor = (255,255,255),bcolor = (0,0,0), Generaterect = False):

        self.text = my_font.render(text,True,tcolor)
        self.bcolor = bcolor
        if not Generaterect:
            self.rect = pygame.Rect(pos)
        else:
            self.rect = self.text.get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]
        self.show = False
    def update(self):
        if self.show:
            pygame.draw.rect(screen,self.bcolor, self.rect)
            screen.blit(self.text, self.rect)

class pygraph():
    def __init__(self, inches, dpi = 50):
        self.fig = pylab.figure(figsize=inches, dpi= dpi)
        self.graph = self.fig.gca()
    def plotline(self, x,y, name = None):
        if x != None:
            self.graph.plot(x, y, label = name)
            self.graph.legend()
        else:
            self.graph.plot(list(range(len(y))), y, label = name)
            self.graph.legend()
    def kill(self):
        plt.clf()

    def get_size(self):
        self.canvas = agg.FigureCanvasAgg(self.fig)
        self.canvas.draw()
        return self.canvas.get_width_height()
    def get_data(self):
        self.canvas = agg.FigureCanvasAgg(self.fig)
        self.canvas.draw()
        self.renderer = self.canvas.get_renderer()
        self.raw_data = self.renderer.buffer_rgba ()
        return self.raw_data

class fallingturtle():
    def __init__(self):
        self.orig_image = pygame.image.load(os.path.join(img_folder,random.choice(list(colors.keys()))))
        self.speed = random.randint(30,60)       
        self.orig_image = pygame.transform.scale(self.orig_image,(self.speed/4,self.speed/4))
        self.image = self.orig_image
        self.rect = self.image.get_rect()
        self.rotation = 0
        self.target = (None,None)
        self.rotationspeed = random.random()
        self.rect.x = random.randint(0,winsize[0])
        self.rect.y = random.randint(0,winsize[1])

    def rotate(self):

        self.image = pygame.transform.rotozoom(self.orig_image, self.rotation * -1,1)
        self.rect = self.image.get_rect(center=self.rect.center)
    def getangle(self, x2,y2):
        myradians = math.atan2(y2 - self.rect.y, x2 - self.rect.x)
        mydegrees = math.degrees(myradians)
        return mydegrees
    def update(self):
        if self.target == (None,None):
            self.rect.y += self.speed/12
            if self.rect.y > winsize[1]:
                self.rect.y = -10
                self.rect.x = random.randint(0,winsize[0])
        else:
            direction = self.getangle(self.target[0],self.target[1])
            self.rect.x += self.speed/6*math.cos(math.radians(direction))
            self.rect.y += self.speed/6*math.sin(math.radians(direction)) 
        self.rotation += self.rotationspeed
        self.rotate()
        self.image.set_alpha(self.speed*4.25)
        screen.blit(self.image,self.rect)

editbuttons = {}

atribbutes= [".tofood", ".toturtle", ".strength", ".speed", ".eyesight", ".health",".energy"]
for i in range(7): 
    editbuttons.update({Button("edit",(size[0][1] + size[0][0] + 240, size[1][0] + size[1][1] - 255 + (16* i), 25,15), tcolor = (0,0,0),bcolor = (150,150,150)): atribbutes[i]})


screen = pygame.display.set_mode(winsize)
pygame.display.set_caption("Naren's turtle evolution simulator version 2.0")
clock = pygame.time.Clock()
screen.fill(SURFACE_COLOR)



textbox = TextInput(winsize[0]//2 - 75, winsize[1]//2, 150, 25, (255,0,0), (0,255,0))
Startbutton = Button("-Start-", (winsize[0]//2 - 20, winsize[1]//2 + 50, 38,20),bcolor = (100,100,100), Generaterect= True)

spawnbuttons = [Button("ADD FOOD", (size[0][1] + size[0][0] + 15, 300,20,20),bcolor = (100,100,100), Generaterect= True)
,Button("ADD TURTLE", (size[0][1] + size[0][0] + 100, 300,20,20),bcolor = (100,100,100), Generaterect= True)]

for i in spawnbuttons:
    i.show = True

Startbutton.show = True

################################START SCREEN###########################################
elapsedtime = 0
fallingturtles = []
varptr = 0
textbox.getinput(varibles[varptr])
Title = Titelfont.render("Turtle Evolution Simulator Version 2", True, (0,0,0))
for i in range(fturtles):
    fallingturtles.append(fallingturtle())
while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if textbox.rect.collidepoint(event.pos): 
                textbox.color = textbox.activecolor
            else: textbox.color = textbox.inactivecolor
            if Startbutton.rect.collidepoint(event.pos):
                exit = False
        if textbox.color == textbox.activecolor and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                textbox.text = textbox.text[:-1]
            else:
                textbox.text += event.unicode
            textbox.rect.w = max(150, textbox.image.get_width()+25)

    screen.fill(SURFACE_COLOR)
    [i.update() for i in fallingturtles]

    intext = varibles[varptr] + ": (" + str(vardata[varptr]) + ")"
    textbox.getinput(intext)
    inputfromtext =  textbox.update()

    rotatedtitle = pygame.transform.rotozoom(Title, math.sin(elapsedtime/10) *2, 1 )
    screen.blit(rotatedtitle, (winsize[0]//2 - Title.get_rect().w/2 ,250,1,1))
    Startbutton.update()
    if inputfromtext!= None:
        try: 
            if inputfromtext != "": 
                
                exec("{} = {}".format(varibles[varptr], float(inputfromtext)))
                varptr += 1

        except ValueError: 
            varptr += 1

            inputfromtext = None


    if varptr == len(varibles) - 1:
        exit = False
    
    elapsedtime += 1
    pygame.display.flip()
    clock.tick(60)
    
exit = True

##################################END OF START SCREEN#########################################

'''
for i in range(winsize[0]//25):
    screen.fill(SURFACE_COLOR)
    pygame.draw.rect(screen,(0,0,0), ((winsize[0] * -1) + i*25, 0, winsize[0], winsize[1]))
    pygame.display.flip()
    clock.tick(60)
'''


def makefood(amount):
    for i in range(int(amount)):
        food.append(Food(
        
        ))
        food[-1].rect.x = random.randint(size[0][0],size[0][1])
        food[-1].rect.y = random.randint(size[1][0],size[1][1])
makefood(foodcount)

prompts = ["Amount of Gene:", "Color: red: 1 blue: 2 green: 3 purple: 4 black: 5 grey: 6 ", "Tendacy to Food:", "Tendancy to Turtle:", "Strength (0-100)", "Speed (0-100)", "Sight Range (300)", "Health (1000)"]

################################GENE SCREEN###########################################

Title = Titelfont.render("Edit Genes ?", True, (0,0,0))
aptr = 0
elapsedtime = 0
editingGene = [0,1,50,50,50,50,300,1000]
while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if textbox.rect.collidepoint(event.pos): 
                textbox.color = textbox.activecolor
            else: textbox.color = textbox.inactivecolor
            if Startbutton.rect.collidepoint(event.pos):
                exit = False
        if textbox.color == textbox.activecolor and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                textbox.text = textbox.text[:-1]
            else:
                textbox.text += event.unicode
            textbox.rect.w = max(150, textbox.image.get_width()+25)

    screen.fill(SURFACE_COLOR)
    [i.update() for i in fallingturtles]

    try: textbox.getinput(prompts[aptr])
    except IndexError: textbox.getinput('Press Enter to finalize or Countinue Editing')

    inputfromtext =  textbox.update()
    rotatedtitle = pygame.transform.rotozoom(Title, math.sin(elapsedtime/10) *2, 1 )
    
    screen.blit(rotatedtitle, (winsize[0]//2 - Title.get_rect().w/2 ,250,1,1))
    Startbutton.update()
    
    if inputfromtext!= None:
        try: 
            if inputfromtext != "":  
                if aptr != len(prompts):
                    editingGene[aptr] = int(inputfromtext)
                    aptr +=1
                else:
                    aptr = 0
                    for i in range(editingGene[0]):
                        if len(turtles) < turtlecount:
                            exec('''turtles.append(Sprite(
                            list(colors.items())[{} - 1],
                            {},
                            {},
                            {},
                            {},
                            {},
                            {}
                            ))'''.format(editingGene[1],editingGene[2],editingGene[3],editingGene[4],editingGene[5],editingGene[6],editingGene[7]))
                        

                    editingGene = [0,1,50,50,50,50,300,1000]
        except ValueError:
            if "-" in inputfromtext:
                inputfromtext = inputfromtext.split("-")
                editingGene[aptr] = "random.randint({},{})".format(inputfromtext[0], inputfromtext[1])
                aptr +=1
            else:
                inputfromtext = None
    elapsedtime += 1
    pygame.display.flip()
    clock.tick(60)
    
exit = True

##################################END OF GENE SCREEN#########################################
elapsedtime = 0
blackhole = 3
for i in fallingturtles:
    i.target = (winsize[0]//2, winsize[1]//2)
while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False
    
    screen.fill(SURFACE_COLOR)
    [i.update() for i in fallingturtles]  
    pygame.draw.circle(screen, (0, 0, 0),[winsize[0]//2 + 10, winsize[1]//2 + 10] , blackhole )
    blackhole += 1/2
    for i in fallingturtles:
        if abs(i.rect.x - i.target[0]) <= 5 and abs(i.rect.y - i.target[1]) <= 5 :
            fallingturtles.remove(i)
            #blackhole += 2
    if fallingturtles == []:
        blackhole += 20
    if blackhole > 800:
        exit = False
    elapsedtime += 1
    pygame.display.flip()
    clock.tick(60)
    
exit = True

######################################END OF START ANIMATION######################################################

vardata = []
[exec("vardata.append({})".format(i)) for i in varibles]

def assignrandom(amount ):
    if Seed != None:
        random.seed(int(Seed))

    for i in range(int(amount)):
        turtles.append(Sprite(
        random.choice(list(colors.items())),
        random.randint(0,100),
        random.randint(0,100),
        random.randint(10,100), 
        random.randint(10,100),
        random.randint(300,500), 
        random.randint(500,1500)

        ))
        vx = random.randint(size[0][0],size[0][1])
        turtles[-1].floatx = vx
        turtles[-1].rect.x = vx
        vx = random.randint(size[1][0],size[1][1])
        turtles[-1].floaty = vx
        turtles[-1].rect.y = vx
assignrandom(turtlecount - len(turtles))


def spawn():
    for i in food:
        i.rect.x = random.randint(size[0][0],size[0][1])
        i.rect.y = random.randint(size[1][0],size[1][1])
        Fgroup.add(i)

    for i in turtles:
        vx = random.randint(size[0][0],size[0][1])
        i.floatx = vx
        i.rect.x = vx
        vx = random.randint(size[1][0],size[1][1])
        i.floaty = vx
        i.rect.y = vx
        Tgroup.add(i)

spawn()

def eatfood(turtle, f):
    if f :
        if random.randint(0,fooddepletionrate) == 0:
            food.remove(f[0])
            pygame.sprite.Sprite.kill(f[0])
        else:
            f[0].rect.x = random.randint(size[0][0],size[0][1])
            f[0].rect.y = random.randint(size[1][0],size[1][1])
            
        turtle.energy += energyinfood

def eaturtle(turtle, turt):
    for t in  turt:
        if t.getgene() != turtle.getgene():
            damage = (turtle.strength + random.randint(0,25) - t.strength)
            damage += 5
            t.health -= damage
            if t.health <= 0:
                turtle.energy += energyinturtle
                turtles.remove(t)
                pygame.sprite.Sprite.kill(t)
            #else:
                #turtle.rect.x += random.randint(-20,20) #brawling turtles
                #turtle.rect.y += random.randint(-20,20)

def findbest():
        genes = [i.getgene() for i in turtles]
        uniquegenes = []
        [uniquegenes.append(i) for i in genes if i not in uniquegenes]
        List = [genes.count(i) for i in uniquegenes]
        best = sorted(List, reverse= True)
        nboard = []
        for t in best[:5]:
            bgene = [i for i in genes if genes.count(i) == t]
            if bgene:
                bgene = bgene[0]
                nboard.append(bgene)
                genes = [i for i in genes if i != bgene]
        return nboard



def blitboard(btext, xdif , ydif):
    pygame.draw.rect(screen, SURFACE_COLOR, (size[0][1] + size[0][0] + 5, size[1][0] + size[1][1] - ydif, 400, len(btext.splitlines() * 15)))
    for place, i in enumerate(btext.splitlines()):
        text = my_font.render(i, True, (0,0,0))
        screen.blit(text,(size[0][1] + size[0][0] - xdif, size[1][0] + size[1][1] - ydif + (15 * (place + 1))))
        

textbox = TextInput(size[0][1] + 70, size[1][1]+ 25, 150, 25, (255,0,0), (0,255,0))

selectedturtle = None
selectedbutton = None
inputfromtext = None
paused = False

top5 = findbest()
while len(top5) != 5:
    top5.append(None)
genes = [i.getgene() for i in turtles]


countgraph = pygraph([5,4], 60)


predatorturtlescount.append(len([i for i in turtles if i.ispredator]))
turtlescountovertime.append(len(turtles))
foodcountovertime.append(len(food))

countgraph.plotline( None, turtlescountovertime,"Turtle Count")
countgraph.plotline( None,predatorturtlescount, "Predator Turtle Count")
countgraph.plotline(None,foodcountovertime, "Food Count")

gsize = countgraph.get_size()
countgraphsurf = pygame.image.frombuffer(countgraph.get_data(), gsize, "RGBA")


while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            found = False
            if textbox.rect.collidepoint(event.pos): 
                found = True
                textbox.color = textbox.activecolor
            else: textbox.color = textbox.inactivecolor

            for i in editbuttons.items():
                if i[0].rect.collidepoint(event.pos):
                    selectedbutton = i[1]
                    textbox.getinput("Set %s To:" % i[1])
                    found = True
            for i in spawnbuttons:
                if i.rect.collidepoint(event.pos):
                    if spawnbuttons.index(i) == 0: 
                        makefood(1)
                        Fgroup.add(food[-1])
                    else: 
                        assignrandom(1)
                        Tgroup.add(turtles[-1])

            if not found:
                selectedbutton = None
                for i in turtles:
                    selectedturtle = None
                    for button in editbuttons:
                        button.show = False
                    if i.rect.collidepoint(event.pos):                    
                        for button in editbuttons:
                            button.show = True
                        selectedturtle = i
                        break         
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if paused: paused = False
            else: paused = True

        if textbox.color == textbox.activecolor and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                textbox.text = textbox.text[:-1]
            else:
                textbox.text += event.unicode
            textbox.rect.w = max(100, textbox.image.get_width()+25)
        

    if moves == movesbeforenewgen : #end generation code
        gen += 1
        moves = 0
        
        foodcount = round(len(food) * foodgrowthmod)
        if  foodcount < maxfoodcount: 
            if foodcount > minfoodcount: makefood(abs(len(food) - foodcount))
            else:
                foodcount = minfoodcount 
                makefood(minfoodcount - len(food))
        else: 
            foodcount = maxfoodcount
            makefood(abs(len(food) - foodcount))
        
        newturtles = []
        turtlecount= round(len(turtles) * turtlegrowthmod)

        turtles.sort(key= lambda x: x.energy, reverse= True) # Sort Turtle list so that turtles with greater energy get duplicated first 


        turtlecount = round(len(turtles) * turtlegrowthmod)

        if turtlecount > maxturtlecount: turtlecount = maxturtlecount
        for place in range(turtlecount): 
            i = turtles[place%len(turtles)]
            
            if random.randint(0,mutationrate) == 0:

                geneswitch = random.randint(0,6)     
                if geneswitch == 0: i.color = random.choice(list(colors.items()))
                if geneswitch == 1: i.tofood = random.randint(0,100)
                if geneswitch == 2: i.toturtle = random.randint(0,100)
                if geneswitch == 3: i.strength = random.randint(10,100)
                if geneswitch == 4: i.speed = random.randint(10,100)
                if geneswitch == 5: i.eyesight = random.randint(300,500)
                if geneswitch == 6: i.oghealth = random.randint(500,1500)
                i.color = random.choice(list(colors.items()))

            newturtles.append(Sprite(i.color,i.tofood,i.toturtle,i.strength,i.speed,i.eyesight,i.oghealth))

        for i in turtles:
            pygame.sprite.Sprite.kill(i)
        turtles = newturtles
        
        predatorturtlescount.append(len([i for i in turtles if i.ispredator]))
        turtlescountovertime.append(len(turtles))
        foodcountovertime.append(len(food))

        countgraph.kill()
        countgraph = pygraph([5,4], 60)
        
        countgraph.plotline(None,turtlescountovertime,"Turtle Count")
        countgraph.plotline(None,predatorturtlescount, "Predator Turtle Count")
        countgraph.plotline(None,foodcountovertime, "Food Count")

        gsize = countgraph.get_size()
        countgraphsurf = pygame.image.frombuffer(countgraph.get_data(), gsize, "RGBA")

        top5 = findbest()

        while len(top5) != 5:
            top5.append(None)
        genes = [i.getgene() for i in turtles]
        spawn()


    screen.fill(SURFACE_COLOR)
    pygame.draw.rect(screen,(WHITE), pygame.Rect(size[0][0], size[1][0], size[0][1], size[1][1]))
    if not paused:


        if moves%updatespermove == 0:
            for i in turtles:
                if i.energy:
                    #Manage direction 50 sould be a changable varible
                    direction = i.getangle(i.target[0],i.target[1])
                    if i.reverseangle:
                        direction = (direction + 180)%360
                        i.reverseangle = False

                    i.getchoice()

                    i.rotation = direction + 90
                    i.rotate()
            
        for i in turtles:
            
            if i.energy > 0:
                #Manage direction 50 sould be a changable varible

                direction = i.getangle(i.target[0],i.target[1])
                if i.reverseangle:
                    direction = (direction + 180)%360

                if abs(i.rect.x - i.target[0]) < 3 and abs(i.rect.y - i.target[1]) < 3:
                    i.target = (random.randint(size[0][0],size[0][1]),random.randint(size[1][0],size[1][1]))

                #Dont go off the screen turtles!

                i.rotation = direction + 90
                i.rotate()

                movespeed = i.speed
                if i.ispredator == True:
                    movespeed += Attackspeedmod

                fx = movespeed/speedmod*math.cos(math.radians(direction))
                fy = movespeed/speedmod*math.sin(math.radians(direction)) 
                i.floatx += fx
                i.floaty += fy

                if i.floatx < size[0][0]: i.floatx = size[0][0]
                elif i.floatx > size[0][0] + size[0][1] - 20: i.floatx = size[0][0] + size[0][1] - 20
                if i.floaty < size[1][0]: i.floaty =  size[1][0]
                elif i.floaty > size[1][0] + size[1][1] - 20: i.floaty = size[1][0] + size[1][1] -20 

                #Move to new location.
                i.rect.x = round(i.floatx)
                i.rect.y = round(i.floaty)
                #collison code:

                if not i.ispredator: eatfood(i,pygame.sprite.spritecollide(i, Fgroup, False, collided = pygame.sprite.collide_rect_ratio(0.5)))
                if i.ispredator: eaturtle(i,pygame.sprite.spritecollide(i, Tgroup, False, collided = pygame.sprite.collide_rect_ratio(0.5)))
            else: 
                
                turtles.remove(i)
                pygame.sprite.Sprite.kill(i)

            i.energy -= 1
        moves += 1
        

        #screen.fill(SURFACE_COLOR)
        #pygame.draw.rect(screen,(WHITE), pygame.Rect(size[0][0], size[1][0], size[0][1], size[1][1]))
        pygame.draw.rect(screen,(150,150,150), pygame.Rect(size[0][0], size[1][0], size[0][1], size[1][1]),2)

    Fgroup.update()
    Tgroup.update()

            
    board = """
            Generation Number: {} Percent Completed: {}%
            FPS: {}
            Turtles left: {}/{}
            Food left: {}/{}
            Predator Turtles: {}
            Seed: {}

            Top Four Turtles:
            [ColorFood,Turtle,Strength,Speed,Sight,Health]
            1: {} Count: {}
            2: {} Count: {}
            3: {} Count: {}
            4: {} Count: {}

            Click On a Turtle to Inspect and Edit


    """.format(gen,round((moves/movesbeforenewgen) * 100), int(clock.get_fps()), len(turtles),turtlecount,len(food),foodcount, predatorturtlescount[-1], Seed,
    
    top5[0], genes.count(top5[0]),
    top5[1], genes.count(top5[1]),
    top5[2], genes.count(top5[2]),
    top5[3], genes.count(top5[3]),
    )

    blitboard("".join([str(i)+"." for i in vardata]),size[0][1],10) #BLits code

    blitboard(board,35,600)
    for i in spawnbuttons:
        i.update()
        
    if selectedturtle:

        board = """
            Turtle Color: {}    Turtle's Choice: {}
            Turtle's Tendancy To Food: {}
            Turtle's Tendancy To Turtle: {}
            Turtle's Strength: {}
            Turtle's Speed: {}
            Turtle's Eyesight: {}
            Turtles's Current Health: {}
            Turtle's Current Energy: {}  

        """.format(selectedturtle.color[1],selectedturtle.choice, selectedturtle.tofood,selectedturtle.toturtle,selectedturtle.strength,selectedturtle.speed,selectedturtle.eyesight,selectedturtle.health,selectedturtle.energy)
        blitboard(board,35,300)
        popup = pygame.transform.scale(selectedturtle.image, (40,40))
        screen.blit(popup, (size[0][1] + size[0][0] + 270, size[1][0] + size[1][1] - 235 ) )
    else:
        screen.blit(countgraphsurf, (size[0][1] + size[0][0] + 15, size[1][0] + 280))
        

    for i in editbuttons:
        i.update()
    inputfromtext =  textbox.update()
    if inputfromtext!= None:
        try: int(inputfromtext)
        except ValueError: inputfromtext = None
        
    
    if inputfromtext != None and selectedbutton: 
        exec("selectedturtle{} = {}".format(selectedbutton, int(inputfromtext)))
        selectedturtle.runaway = False
        selectedturtle.ispredator = False
        if selectedturtle.toturtle > selectedturtle.tofood:
            selectedturtle.ispredator = True
        if selectedturtle.toturtle * 2 <= selectedturtle.tofood:
            selectedturtle.runaway = True 


    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()