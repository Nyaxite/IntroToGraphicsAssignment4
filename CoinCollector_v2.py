# Source File Name: CoinCollector.py
# Author's Name: Michael Burnie
# Last Modified By: Michael Burnie
# Date Last Modified: June 29, 2013
""" 
  Program Description:  This program is built from MailPilot.py. It uses the horizontal axis as a backdrop for 
  a mouse-driven game. The objective is to steer the car into the coins while avoiding obstacles, such as oncoming
  cars, to achieve the highest score possible.

    Version: 2
    - Player health changed to 100
    - Player's score accumulates over time (+1 per frame)
    - Coins are now worth 500 points
    - Player bounds are now restricted within road area, cannot drive on grass sections
    - Updated Instructions screen and scoreboard
    - Reduced number of enemy cars to 2 from 3
        - Hitting an enemy car results in a loss of 20 health
    - Added Flotsam
        - Hitting flotsam results in a loss of 10 health
    - Added Environmental details such as cracks and tire marks
    - Added repair power-up, appears infrequently
        - Heals player's health by 50 points instantly
  
"""

import pygame, random
pygame.init()

screen = pygame.display.set_mode((640, 480))

HEALTH = 100
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
        self.rect.center = (60, mousey)
        if(mousey < 50):
            self.rect.center = (60, 70)
        if(mousey > 400):
            self.rect.center = (60, 410)
                
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
        self.rect.centerx = 800
        self.rect.centery = random.randrange(50, screen.get_height() - 50)
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("enemyCar1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()

    def update(self):
        self.rect.centerx = self.rect.centerx - self.dx
        if self.rect.centerx < -50:
            self.reset()
    
    def reset(self):
        lane = random.randrange(1, 5)
        image = random.randrange(1, 3)
        self.dx = random.randrange(13, 15)
        self.rect.centerx = 750
        if(lane == 1 or lane == 2): #Oncoming lanes
            self.dx += SCROLL_SPEED    
            if(lane == 1):
                self.rect.centery = LANE_1
            elif(lane == 2):          
                self.rect.centery = LANE_2
                
            if(image == 1):
                self.image = pygame.image.load("oncomingEnemyCar1.gif")
            elif(image == 2):
                self.image = pygame.image.load("oncomingEnemyCar2.gif")
                
        if(lane == 3 or lane == 4):  
            if(lane == 3):
                self.rect.centery = LANE_3
            elif(lane == 4):          
                self.rect.centery = LANE_4
                
            if(image == 1):
                self.image = pygame.image.load("enemyCar1.gif")
            elif(image == 2):
                self.image = pygame.image.load("enemyCar2.gif")

class Flotsam(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("barrel.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()
        
        self.dx = SCROLL_SPEED
    
    def update(self):
        self.rect.centerx -= self.dx
        if self.rect.centerx < -50:
            self.reset()
    
    def reset(self):
        image = random.randrange(1,6)
        if(image == 1):
            self.image = pygame.image.load("barrel.gif")
        elif(image == 2):
            self.image = pygame.image.load("crate.gif")
        elif(image == 3):
            self.image = pygame.image.load("muffler.gif")
        elif(image == 4):
            self.image = pygame.image.load("tire.gif")
        elif(image == 5):
            self.image = pygame.image.load("pylon.gif")
        self.rect.centerx = random.randrange(850, 1600)
        self.rect.centery = random.randrange(50, screen.get_height() - 50)

class Repair(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("fix.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()
        
        self.dx = SCROLL_SPEED
    
    def update(self):
        self.rect.centerx -= self.dx
        if self.rect.centerx < -50:
            self.reset()
    
    def reset(self):
        self.image = pygame.image.load("fix.gif")
        self.rect.centerx = random.randrange(15000, 25000) #rare occurrence
        self.rect.centery = random.randrange(50, screen.get_height() - 50)

class Environment(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("crack1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()
        
        self.dx = SCROLL_SPEED
    
    def update(self):
        self.rect.centerx -= self.dx
        if self.rect.centerx < -50:
            self.reset()
    
    def reset(self):
        image = random.randrange(1,5)
        if(image == 1):
            self.image = pygame.image.load("crack1.gif")
        elif(image == 2):
            self.image = pygame.image.load("crack2.gif")
        elif(image == 3):
            self.image = pygame.image.load("crack3.gif")
        elif(image == 4):
            self.image = pygame.image.load("tiremarks.gif")
        self.rect.centerx = random.randrange(850, 1600)
        self.rect.centery = self.rect.centery = random.randrange(75, screen.get_height() - 75)
        
class Road(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("background.png")
        self.rect = self.image.get_rect()
        self.dx = 5
        self.reset()
        
    def update(self):
        self.rect.centerx -= SCROLL_SPEED
        if self.rect.centerx <= -3420:
            self.reset() 
    
    def reset(self):
        self.rect.centerx = 4000

class Scoreboard(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.health = HEALTH
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 40, 0, 1)
        
    def update(self):
        self.text = "Health: %d     Score: %d" % (self.health, self.score)
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
    flotsam1 = Flotsam()
    flotsam2 = Flotsam()
    repair = Repair()
    environment1 = Environment()
    environment2 = Environment()
    road = Road()
    scoreboard = Scoreboard()


    friendSprites = pygame.sprite.OrderedUpdates(road, environment1, environment2, repair, coin, player)
    enemySprites = pygame.sprite.OrderedUpdates(flotsam1, flotsam2, enemy1, enemy2)
    scoreSprite = pygame.sprite.Group(scoreboard)

    clock = pygame.time.Clock()
    keepGoing = True
    while keepGoing:
        clock.tick(30)
        pygame.mouse.set_visible(False)
        scoreboard.score += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

        
        #check collisions
        
        if pygame.sprite.collide_rect(player, coin):
            player.sndYay.play()
            coin.reset()
            scoreboard.score += 500

        hitEnemy1 = pygame.sprite.collide_rect(player, enemy1)
        hitEnemy2 = pygame.sprite.collide_rect(player, enemy2)
        hitFlotsam1 = pygame.sprite.collide_rect(player, flotsam1)
        hitFlotsam2 = pygame.sprite.collide_rect(player, flotsam2)
        hitRepair = pygame.sprite.collide_rect(player, repair)
        enemyCollision = pygame.sprite.collide_rect(enemy1, enemy2)
        
        if hitEnemy1 or hitEnemy2 or hitFlotsam1 or hitFlotsam2:
            player.sndThunder.play()
            if hitEnemy1:
                scoreboard.health -= 20
                enemy1.reset()
            if hitEnemy2:
                scoreboard.health -= 20
                enemy2.reset()
            if hitFlotsam1:
                scoreboard.health -= 10
                flotsam1.reset()
            if hitFlotsam2:
                scoreboard.health -= 10
                flotsam2.reset()
            if scoreboard.health <= 0:
                keepGoing = False
        if hitRepair:
            repair.reset()
            if(scoreboard.health <= 100):
                scoreboard.health += 50
                if(scoreboard.health > 100):
                    scoreboard.health = 100
        if enemyCollision:
            enemy2.reset()
        friendSprites.update()
        enemySprites.update()
        scoreSprite.update()
        
        friendSprites.draw(screen)
        enemySprites.draw(screen)
        scoreSprite.draw(screen)
        
        pygame.display.flip()
    
    player.sndEngine.stop()
    #return mouse cursor
    pygame.mouse.set_visible(True) 
    return scoreboard.score
    
def instructions(score):
    pygame.display.set_caption("Coin Collector!")

    player = Player()
    road = Road()
    
    allSprites = pygame.sprite.OrderedUpdates(road, player)
    insFont = pygame.font.SysFont(None, 35)

    insLabels = []
    instructions = (
    "Coin Collector!     Last score: %d" % score ,
    "Instructions:  You are a coin collector,",
    "gathering coins as fast as possible.",
    "",
    "Drive over coins to accumulate score quickly,",
    "but be careful not to run into other cars",    
    "or other obstacles. Your car will be totaled ",
    "if you run into too many objects",
    "Steer with the mouse.",
    "",
    "Good luck, and have fun!",
    "",
    "Click to start or press Escape to quit."
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
    
    

