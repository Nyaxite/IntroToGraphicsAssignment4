# Source File Name: CoinCollector.py
# Author's Name: Michael Burnie
# Last Modified By: Michael Burnie
# Date Last Modified: June 28, 2013
""" 
  Program Description:  This program is built from MailPilot.py. It uses the horizontal axis as a backdrop for 
  a mouse-driven game. The objective is to steer the car into the coins while avoiding obstacles, such as oncoming
  cars.

  Version: 1 - Initial Commit
- Modified MailPilot.py
- Changed Background
- Controls based on Y-axis, using a car
- Enemies move via x-axis, within 4 defined lanes
    - oncoming enemies move at speed + speed of background, to produce oncoming effect
- Player has 10 health, to be modified later
- Intro to be changed in future patch
  
"""

import pygame, random
pygame.init()

screen = pygame.display.set_mode((640, 480))

HEALTH = 10
SCROLL_SPEED = 20
LANE_1 = 90
LANE_2 = 190
LANE_3 = 290
LANE_4 = 390

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("playerCar.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        
        if not pygame.mixer:
            print("problem with sound")
        else:
            pygame.mixer.init()
            self.sndYay = pygame.mixer.Sound("yay.ogg")
            self.sndThunder = pygame.mixer.Sound("thunder.ogg")
            self.sndEngine = pygame.mixer.Sound("engine.ogg")
            self.sndEngine.play(-1)
        
    def update(self):
        mousex, mousey = pygame.mouse.get_pos()
        self.rect.center = (50, mousey)
                
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("coin.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()
        
        self.dx = SCROLL_SPEED
    
    def update(self):
        self.rect.centerx -= self.dx
        if self.rect.centerx < -50:
            self.reset()
    
    def reset(self):
        self.rect.top = 0
        self.rect.centerx = 800
        self.rect.centery = random.randrange(0, screen.get_height())
      
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("enemyCar.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()

    def update(self):
        self.rect.centerx = self.rect.centerx - self.dx
        if self.rect.centerx < -50:
            self.reset()
    
    def reset(self):
        lane = random.randrange(1, 5)
        self.dx = random.randrange(13, 15)
        self.rect.centerx = 750
        if(lane == 1): #Oncoming lane
            self.rect.centery = LANE_1
            self.dx = self.dx + SCROLL_SPEED
            self.image = pygame.image.load("enemyCar2.gif")
        elif(lane == 2): #Oncoming lane            
            self.rect.centery = LANE_2
            self.dx = self.dx + SCROLL_SPEED
            self.image = pygame.image.load("enemyCar2.gif")
        elif(lane == 3):
            self.rect.centery = LANE_3
            self.image = pygame.image.load("enemyCar.gif")
        elif(lane == 4):
            self.rect.centery = LANE_4
            self.image = pygame.image.load("enemyCar.gif") 
    
class Road(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("background.png")
        self.rect = self.image.get_rect()
        self.dx = 5
        self.reset()
        
    def update(self):
        self.rect.centerx -= SCROLL_SPEED
        if self.rect.centerx <= -3400:
            self.reset() 
    
    def reset(self):
        self.rect.centerx = 4000

class Scoreboard(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.lives = HEALTH
        self.score = 0
        self.font = pygame.font.SysFont("None", 50)
        
    def update(self):
        self.text = "Health: %d, score: %d" % (self.lives, self.score)
        self.image = self.font.render(self.text, 1, (255, 255, 0))
        self.rect = self.image.get_rect()
    
def game():
    pygame.display.set_caption("Coin Collector!")

    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    player = Player()
    coin = Coin()
    enemy1 = Enemy()
    enemy2 = Enemy()
    enemy3 = Enemy()
    road = Road()
    scoreboard = Scoreboard()


    friendSprites = pygame.sprite.OrderedUpdates(road, coin, player)
    cloudSprites = pygame.sprite.Group(enemy1, enemy2, enemy3)
    scoreSprite = pygame.sprite.Group(scoreboard)

    clock = pygame.time.Clock()
    keepGoing = True
    while keepGoing:
        clock.tick(30)
        pygame.mouse.set_visible(False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

        
        #check collisions
        
        if pygame.sprite.collide_rect(player, coin):
            player.sndYay.play()
            coin.reset()
            scoreboard.score += 100

        hitClouds1 = pygame.sprite.collide_rect(player, enemy1)
        hitClouds2 = pygame.sprite.collide_rect(player, enemy2)
        hitClouds3 = pygame.sprite.collide_rect(player, enemy3)
        if hitClouds1 or hitClouds2 or hitClouds3:
            player.sndThunder.play()
            scoreboard.lives -= 1
            if scoreboard.lives <= 0:
                keepGoing = False
            if hitClouds1:
                enemy1.reset()
            if hitClouds2:
                enemy2.reset()
            if hitClouds3:
                enemy3.reset()
        
        friendSprites.update()
        cloudSprites.update()
        scoreSprite.update()
        
        friendSprites.draw(screen)
        cloudSprites.draw(screen)
        scoreSprite.draw(screen)
        
        pygame.display.flip()
    
    player.sndEngine.stop()
    #return mouse cursor
    pygame.mouse.set_visible(True) 
    return scoreboard.score
    
def instructions(score):
    pygame.display.set_caption("Mail Pilot!")

    player = Player()
    road = Road()
    
    allSprites = pygame.sprite.OrderedUpdates(road, player)
    insFont = pygame.font.SysFont(None, 50)
    insLabels = []
    instructions = (
    "Mail Pilot.     Last score: %d" % score ,
    "Instructions:  You are a mail pilot,",
    "delivering mail to the islands.",
    "",
    "Fly over an island to drop the mail,",
    "but be careful not to fly too close",    
    "to the clouds. Your plane will fall ",
    "apart if it is hit by lightning too",
    "many times. Steer with the mouse.",
    "",
    "good luck!",
    "",
    "click to start, escape to quit..."
    )
    
    for line in instructions:
        tempLabel = insFont.render(line, 1, (255, 255, 0))
        insLabels.append(tempLabel)
 
    keepGoing = True
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
                donePlaying = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                keepGoing = False
                donePlaying = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
                    donePlaying = True
    
        allSprites.update()
        allSprites.draw(screen)

        for i in range(len(insLabels)):
            screen.blit(insLabels[i], (50, 30*i))

        pygame.display.flip()
        
    player.sndEngine.stop()    
    pygame.mouse.set_visible(True)
    return donePlaying
        
def main():
    donePlaying = False
    score = 0
    while not donePlaying:
        donePlaying = instructions(score)
        if not donePlaying:
            score = game()


if __name__ == "__main__":
    main()
    
    

