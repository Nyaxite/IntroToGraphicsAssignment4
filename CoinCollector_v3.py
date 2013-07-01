# Source File Name: CoinCollector.py
# Author's Name: Michael Burnie
# Last Modified By: Michael Burnie
# Date Last Modified: June 30, 2013
""" 
  Program Description:  This program is built from MailPilot.py. It uses the horizontal axis as a backdrop for 
  a mouse-driven game. The objective is to steer the car into the coins while avoiding obstacles, such as oncoming
  cars, to achieve the highest score possible.

    Version: 3
    - Added invulnerability state
        - After hitting an object, the player becomes invulnerable for 1 second
        - The player cannot collide with cars/flotsam in this state, thus won't lose health
        - The player car flashes to indicate invulnerability
        - Star power-up added, allows player to stay invulnerable for 7 seconds, spawns infrequently
    - Added status, which displays information about hits and other states
    - Added additional environment details/sprites
    - Reduced mouse sensitivity slightly
    - Added music (menu and in-game)
    - Added sound effects for each collision, plus engine sound
    - Changed collisions to mask from rect to reduce false collisions
    - Adjusted volumes for sounds/music; uses constants
    - Some commenting done
    
"""

import pygame, random
pygame.init()

screen = pygame.display.set_mode((640, 480))

FRAMES_PER_SECOND = 30 
HEALTH = 100 #player's health
SCROLL_SPEED = 20 #movement speed of the background

#y-coordinate of Lanes 1, 2, 3, and 4
LANE_1 = 90 
LANE_2 = 190
LANE_3 = 290
LANE_4 = 390

STAR_DURATION = 210 #in frames, the duration of the star invulnerability state

#game volume
MUSIC_VOLUME = 0.6
SOUND_VOLUME = 0.5

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("playerCar.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.invulnerable = False
        self.invulnerableDuration = 30
        self.invulnerableElapsed = 0
        
        #setup in-game sounds
        if not pygame.mixer:
            print("problem with sound")
        else:
            pygame.mixer.init()
            
            self.sndEngine = pygame.mixer.Sound("engine.ogg")
            self.sndEngine.play(-1)
            self.sndCrash = pygame.mixer.Sound("crash.ogg")
            self.sndHit = pygame.mixer.Sound("hit1.ogg")
            self.sndFix = pygame.mixer.Sound("fix.ogg")
            self.sndCoin = pygame.mixer.Sound("coin.ogg")
            self.sndInvulnerable = pygame.mixer.Sound("Invulnerable.ogg")
            
            self.sndEngine.set_volume(SOUND_VOLUME)
            self.sndCrash.set_volume(SOUND_VOLUME + 0.5)
            self.sndHit.set_volume(SOUND_VOLUME)
            self.sndFix.set_volume(SOUND_VOLUME)
            self.sndCoin.set_volume(SOUND_VOLUME)
            self.sndInvulnerable.set_volume(SOUND_VOLUME)
        
    def update(self):
        mousex, mousey = pygame.mouse.get_pos() #get the mouse position and translte it to the screen
        
        #reduce the sensitivity by 10%
        mousex = mousex / 1.1
        mousey = mousey / 1.1
        
        #the mouse only affects the car's y-axis; x is fixed to position 60
        self.rect.center = (60, mousey)
        
        #do not allow the car to move onto the grass at the sides of the road by restricting mousex, mousey
        if(mousey < 50):
            self.rect.center = (60, 70)
        if(mousey > 400):
            self.rect.center = (60, 410)
        
    #the following two methods are can to display and hide the car image;
    #primarily used for the invulnerability state to show the player that they are currently invulnerable
    def flashOn(self):
        self.image = pygame.image.load("playerCar.gif")
    def flashOff(self):
        self.image = pygame.image.load("blankCar.gif")
                
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
        self.rect.centerx = random.randrange(15000, 20000) #rare occurrence
        self.rect.centery = random.randrange(50, screen.get_height() - 50)
        
class Star(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("star.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()
        
        self.dx = SCROLL_SPEED
    
    def update(self):
        self.rect.centerx -= self.dx
        if self.rect.centerx < -50:
            self.reset()
    
    def reset(self):
        self.image = pygame.image.load("star.gif")
        self.rect.centerx = random.randrange(20000, 30000) # rare occurrence
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
        if self.rect.centerx < -250:
            self.reset()
    
    def reset(self):
        image = random.randrange(1,12)
        if(image == 1):
            self.image = pygame.image.load("crack1.gif")
        elif(image == 2):
            self.image = pygame.image.load("crack2.gif")
        elif(image == 3):
            self.image = pygame.image.load("crack3.gif")
        elif(image == 4):
            self.image = pygame.image.load("tiremarks.gif")
        elif(image == 5):
            self.image = pygame.image.load("crack4.gif")
        elif(image == 6):
            self.image = pygame.image.load("crack5.gif")
        elif(image == 7):
            self.image = pygame.image.load("crack6.gif")
        elif(image == 8):
            self.image = pygame.image.load("crack7.gif")
        elif(image == 9):
            self.image = pygame.image.load("grass1.gif")
        elif(image == 10):
            self.image = pygame.image.load("leaf1.gif")
        elif(image == 11):
            self.image = pygame.image.load("leaf2.gif")
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
        self.font = pygame.font.SysFont("Arial", 30, 0, 1)
        self.status = ""
        
    def update(self):
        self.text = "Health: %d   Score: %d    %s" % (self.health, self.score, self.status)
        self.image = self.font.render(self.text, 1, (0, 0, 255))
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
    star = Star()
    environment1 = Environment()
    environment2 = Environment()
    road = Road()
    scoreboard = Scoreboard()

    #setup the in-game music
    pygame.mixer.music.load('TopGear1-2.mp3')
    pygame.mixer.music.play(-1, 0.0)#repeat
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    
    friendSprites = pygame.sprite.OrderedUpdates(road, environment1, environment2, repair, star, coin, player)
    enemySprites = pygame.sprite.OrderedUpdates(flotsam1, flotsam2, enemy1, enemy2)
    scoreSprite = pygame.sprite.Group(scoreboard)

    clock = pygame.time.Clock()
    keepGoing = True
    while keepGoing:
        clock.tick(FRAMES_PER_SECOND)
        pygame.mouse.set_visible(False)
        scoreboard.score += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
        
        #check collisions
        
        if pygame.sprite.collide_mask(player, coin):
            player.sndCoin.play()
            coin.reset()
            scoreboard.score += 500

        hitEnemy1 = pygame.sprite.collide_mask(player, enemy1)
        hitEnemy2 = pygame.sprite.collide_mask(player, enemy2)
        hitFlotsam1 = pygame.sprite.collide_mask(player, flotsam1)
        hitFlotsam2 = pygame.sprite.collide_mask(player, flotsam2)
        hitRepair = pygame.sprite.collide_mask(player, repair)
        hitStar = pygame.sprite.collide_mask(player, star)
        enemyCollision = pygame.sprite.collide_mask(enemy1, enemy2)

        if((hitEnemy1 or hitEnemy2 or hitFlotsam1 or hitFlotsam2) and not player.invulnerable):
            player.invulnerable = True
            if hitEnemy1 or hitEnemy2:
                player.sndCrash.play()
                scoreboard.health -= 20
                scoreboard.status = "Hit car (-20 HP)"
                if hitEnemy1:
                    enemy1.reset()
                if hitEnemy2:
                    enemy2.reset()
            if hitFlotsam1 or hitFlotsam2:
                player.sndHit.play()
                scoreboard.health -= 10
                scoreboard.status = "Hit object (-10 HP)"
                if hitFlotsam1:
                    flotsam1.reset()
                if hitFlotsam2:
                    flotsam2.reset()
            if scoreboard.health <= 0: #if the player has no health left
                keepGoing = False #end the game
                
        if(player.invulnerable and player.invulnerableElapsed < player.invulnerableDuration):
            player.invulnerableElapsed += 1
            if(player.invulnerableElapsed % 2 == 0):
                player.flashOff()
            else:
                player.flashOn()
            if(player.invulnerableDuration == STAR_DURATION):
                scoreboard.status = "Star! (%d sec) " % (((STAR_DURATION - player.invulnerableElapsed)/FRAMES_PER_SECOND) + 1)
                
        elif(player.invulnerable and player.invulnerableElapsed >= player.invulnerableDuration):
            #revert to default values after player has been invulnerable for the complete duration
            player.flashOn()
            player.invulnerableElapsed = 0
            player.invulnerableDuration = 30 
            player.invulnerable = False
            scoreboard.status = ""
        
        if hitRepair: #if the player hit a repair power-up
            player.sndFix.play()
            repair.reset()
            #add 50 to the player health, up to a maximum of 100
            if(scoreboard.health <= 100):
                scoreboard.health += 50
                if(scoreboard.health > 100):
                    scoreboard.health = 100
                    
        if hitStar: #if the player hit a star power-up
            player.sndInvulnerable.play()
            star.reset()
            player.invulnerable = True
            player.invulnerableDuration = STAR_DURATION #make player invulnerable for given seconds (default 7)
            
        if enemyCollision: #if the two enemy cars collide, reset one to avoid overlap
            enemy2.reset()
        friendSprites.update()
        enemySprites.update()
        scoreSprite.update()
        
        friendSprites.draw(screen)
        enemySprites.draw(screen)
        scoreSprite.draw(screen)
        
        pygame.display.flip()
    
    
    player.sndEngine.stop()
    pygame.mixer.stop()
    #return mouse cursor
    pygame.mouse.set_visible(True) 
    return scoreboard.score
    
def instructions(score):
    pygame.display.set_caption("Coin Collector!")
    
    #setup the game's menu music
    pygame.mixer.music.load('TopGear1-1.mp3')
    pygame.mixer.music.play(-1, 0.0)#repeat
    pygame.mixer.music.set_volume(MUSIC_VOLUME)

    player = Player()
    player.sndEngine.set_volume(0.3)
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
        tempLabel = insFont.render(line, 1, (255, 255, 255))
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
        
    #player.sndEngine.stop()    
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
    
    

