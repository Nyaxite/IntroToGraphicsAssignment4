# Source File Name: CoinCollector.py
# Author's Name: Michael Burnie
# Last Modified By: Michael Burnie
# Date Last Modified: July 07, 2013
""" 
  Program Description:  This program is built from MailPilot.py. It uses the horizontal axis as a backdrop for 
  a mouse-driven game. The objective is to steer the car into the coins while avoiding obstacles, such as oncoming
  cars, to achieve the highest score possible.

    Version: 4
    - Added simple game-end screen
        - Includes score and tips
    - Got rid of many redundant classes & optimized code better
    - Changed repair to heal only 30 points, from 50
    - Added comments
    - Includes external documentation
    
"""

import pygame, random
pygame.init()

screen = pygame.display.set_mode((640, 480))#640x480 resolution

FRAMES_PER_SECOND = 30
HEALTH = 100 #player's health
SCROLL_SPEED = 20 #movement speed of the background

#y-coordinate of Lanes 1, 2, 3, and 4
LANE_1 = 90 
LANE_2 = 190
LANE_3 = 290
LANE_4 = 390

RESET_POINT = -50 #the point at which objects will reset, must be negative

COIN_SCORE = 500 #the number of points a coin awards the player

#The start and end x values for in-game objects. A random value will be chosen between the start and end x
#values to determine how frequently objects appear
ENVIRONMENT_START_X = 850
ENVIRONMENT_END_X = 1500
REPAIR_START_X = 15000
REPAIR_END_X = 20000
STAR_START_X = 20000
STAR_END_X = 30000

REPAIR_HEALTH = 30 #the amount of health the repair powerup heals

STAR_DURATION = 210 #in frames, the duration of the star invulnerability state

#game volume
MUSIC_VOLUME = 0.6
SOUND_VOLUME = 0.5

"""
The Player class defines all of the properties of the player, such as the image, sounds, etc.
This is the sprite the player will move to avoid obstacles and collect the objectives.
"""
class Player(pygame.sprite.Sprite):
    """
    Constructor for Player Class   
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #set the sprite's image to the playerCar.gif file
        self.image = pygame.image.load("playerCar.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        
        #the following is for the invulnerability state which occurs when the player hits a car/object or collects as a star
        self.invulnerable = False #default, not invulnerable
        self.invulnerableDuration = FRAMES_PER_SECOND * 1#default, 30 frames or 1 second at 30 FPS
        self.invulnerableElapsed = 0 #current time invulnerable, increments when invulnerable is active
        
        #keep track of how many collisions there are for the player
        self.hitCar = 0
        self.hitFlotsam = 0
        self.hitPowerup = 0
        
        #setup in-game sound setup
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
            
            #set the volume and make adjustments from default for given sounds if required
            self.sndEngine.set_volume(SOUND_VOLUME)
            self.sndCrash.set_volume(SOUND_VOLUME + 0.5)
            self.sndHit.set_volume(SOUND_VOLUME)
            self.sndFix.set_volume(SOUND_VOLUME)
            self.sndCoin.set_volume(SOUND_VOLUME)
            self.sndInvulnerable.set_volume(SOUND_VOLUME)
   
    """
    The update method is called once per frame, which updates the position and sprite of the player object        
    """
    def update(self):
        mousex, mousey = pygame.mouse.get_pos() #get the mouse position and translte it to the screen
        
        #reduce the sensitivity by 10%
        mousex = mousex / 1.1
        mousey = mousey / 1.1
        
        #the mouse only affects the car's y-axis; x is fixed to position 60
        self.rect.center = (60, mousey)
        
        #do not allow the car to move onto the grass at the sides of the road by restricting mousex, mousey
        if(mousey < 50):
            self.rect.center = (60, 60)
        if(mousey > 400):
            self.rect.center = (60, 410)

        #if the player is invulnerable, flash the car image to show this and increased time elapsed as invulnerable
        if(self.invulnerable and self.invulnerableElapsed < self.invulnerableDuration):
            self.invulnerableElapsed += 1
            if(self.invulnerableElapsed % 2 == 0):
                self.image = pygame.image.load("playerCar.gif")
            else:
                self.image = pygame.image.load("blankCar.gif")

        #if the invulnerability state has ended (comparing elapsed = duration
        elif(self.invulnerable and self.invulnerableElapsed >= self.invulnerableDuration):
            #revert to default values after player has been invulnerable for the complete duration
            self.image = pygame.image.load("playerCar.gif")
            self.invulnerableElapsed = 0
            self.invulnerableDuration = 30 
            self.invulnerable = False

"""
The Environment class defines the sprites that are, to the player's eye, stationary on the road. This includes
flotsam such as mufflers and pylons, and non-collision objects such as cracks on the road and tiremarks.
"""
class Environment(pygame.sprite.Sprite):
    """
    Constructor for Environment
    """
    def __init__(self, startx, endx, imageStr):
        pygame.sprite.Sprite.__init__(self)
        self.imageStr = imageStr #set the imageStr variable from the parameters list and hold it for later use
        self.image = pygame.image.load("barrel.gif")#instantiate the image
        #if the image of the object requires randomization, check for those specific strings
        if(self.imageStr == "flotsam" or self.imageStr == "nonCollide"):
            self.randomEnvironmentImages()
        else:
            #if the string is looking for one specific image, convert to an image
            self.image = pygame.image.load(imageStr)
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        
        #set the speed of the objects crossing the screen equal to the scroll speed. These items do not move in the eye's of the player
        self.dx = SCROLL_SPEED
        
        #set the start and end positions as the parameters given
        self.startx = startx
        self.endx = endx

        self.reset()
    
    """
    The update method is called once per frame, which updates the position and sprite of the environment objects        
    """
    def update(self):
        self.rect.centerx -= self.dx#update the position through subtracting by the speed variable
        #if the image has gone beyond the reset point (beyond the edge of the screen), reset
        if self.rect.centerx < RESET_POINT:
            self.reset()
    
    """
    The reset method will reset the position of the sprite, as well as the image if it needs to be randomized
    """
    def reset(self):
        #reset the position
        self.rect.centerx = random.randrange(self.startx, self.endx)
        self.rect.centery = random.randrange(75, screen.get_height() - 75)
        #randomize the image for environment objects that require it
        if(self.imageStr == "flotsam" or self.imageStr == "nonCollide"):
            self.randomEnvironmentImages()
                    
    """
    The following method will randomize between images for objects that require image randomization
    by checking the imageStr for a specific string that represents image randomizations
    """
    def randomEnvironmentImages(self):
        if(self.imageStr == "flotsam"):
            images = ["barrel.gif", "crate.gif", "muffler.gif", "tire.gif", "pylon.gif"]
        elif(self.imageStr == "nonCollide"):
            images = ["crack1.gif", "crack2.gif", "crack3.gif", "crack4.gif", "crack5.gif", "crack6.gif", "crack7.gif", "leaf1.gif", "grass1.gif", "leaf2.gif", "tiremarks.gif"]            
        image = random.randrange(0, len(images))
        self.image = pygame.image.load(images[image])
        
 
"""
The Enemy class defines the enemy sprites. In this game, it is jst the cars that move at various speeds
across the screen. There are 4 fixed lanes defined that they will appear on and follow x-directionally, as per the background. 
"""       
class Enemy(pygame.sprite.Sprite):
    """
    Constructor for Enemy
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("enemyCar1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.reset()

    """
    The update method is called once per frame, which updates the position and sprite of the enemy objects        
    """
    def update(self):
        self.rect.centerx = self.rect.centerx - self.dx
        if self.rect.centerx < -50:#if the enemy is off the screen, reset the image
            self.reset()
    
    """
    The reset method will reset the position of the sprite as well as randomizing the lanes
    and colours of the cars. Oncoming cars must be defined differently than other cars as there are different
    speeds and images used.
    """
    def reset(self):
        #randomize a lane
        lane = random.randrange(1, 5)
        #randomize an image
        image = random.randrange(1, 3)
        self.dx = random.randrange(13, 15)
        self.rect.centerx = 750
        if(lane == 1 or lane == 2): #Oncoming lanes
            self.dx += SCROLL_SPEED    
            if(lane == 1):
                self.rect.centery = LANE_1
            elif(lane == 2):          
                self.rect.centery = LANE_2
            #set image to an oncoming car image
            if(image == 1):
                self.image = pygame.image.load("oncomingEnemyCar1.gif")
            elif(image == 2):
                self.image = pygame.image.load("oncomingEnemyCar2.gif")
                
        if(lane == 3 or lane == 4):#with lanes  
            if(lane == 3):
                self.rect.centery = LANE_3
            elif(lane == 4):          
                self.rect.centery = LANE_4
            #set image to a with car image
            if(image == 1):
                self.image = pygame.image.load("enemyCar1.gif")
            elif(image == 2):
                self.image = pygame.image.load("enemyCar2.gif")

"""
The Road class defines the background image (the road).
"""       
class Road(pygame.sprite.Sprite):
    """
    Constructor for Road
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("background.png")
        self.rect = self.image.get_rect()
        self.dx = 5#scroll at speed/frame
        self.reset()
        
    """
    Called once per frame, the update method just moves along at the scroll speed, and checks for the reset position
    """
    def update(self):
        self.rect.centerx -= SCROLL_SPEED
        if self.rect.centerx <= -3420:
            self.reset() 
    
    """
    Reset the image position
    """
    def reset(self):
        self.rect.centerx = 4000

"""
The scoreboard class defines the text sprite at the top of the game, displaying game information such as score and health
"""
class Scoreboard(pygame.sprite.Sprite):
    """
    Constructor for Scoreboard
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.health = HEALTH
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30, 0, 1)
        self.status = ""
        self.messageElapsed = 0#time status has been on screen
        self.messageLength = FRAMES_PER_SECOND * 1#Current length of the status
        
    """
    Called once per frame, the update method updates the score, health and status of the player
    """
    def update(self):
        #if the message time elapsed is less than the maximum length, add to time elapsed. Otherwise, reset the time elapsed and remove the status
        if(self.messageElapsed <= self.messageLength and self.status is not ""):
            self.messageElapsed += 1
        else:
            self.messageElapsed = 0
            self.status = ""
    
        #show the current status on the screen
        self.text = "Health: %d   Score: %d    %s" % (self.health, self.score, self.status)
        self.image = self.font.render(self.text, 1, (0, 0, 255))
        self.rect = self.image.get_rect()

"""
This is the game method, where all of the in-game is managed. Objects are created and updates are made to
the screen. This is the primary method of gameplay as it makes all of the necessary calls during the game.
"""   
def game():
    pygame.display.set_caption("Coin Collector!")
    
    #create player, environment, enemy, scoreboard, and road objects
    player = Player()
    enemy1 = Enemy()
    enemy2 = Enemy()
    coin = Environment(ENVIRONMENT_START_X, ENVIRONMENT_END_X, "coin.gif")
    flotsam1 = Environment(ENVIRONMENT_START_X, ENVIRONMENT_END_X, "flotsam")
    flotsam2 = Environment(ENVIRONMENT_START_X, ENVIRONMENT_END_X, "flotsam")
    flotsam3 = Environment(ENVIRONMENT_START_X, ENVIRONMENT_END_X, "flotsam")
    nonCollide1 = Environment(ENVIRONMENT_START_X, ENVIRONMENT_END_X, "nonCollide")
    nonCollide2 = Environment(ENVIRONMENT_START_X, ENVIRONMENT_END_X, "nonCollide")
    repair = Environment(REPAIR_START_X, REPAIR_END_X, "fix.gif")
    star = Environment(STAR_START_X, STAR_END_X, "star.gif")
    road = Road()
    scoreboard = Scoreboard()

    #setup the in-game music
    pygame.mixer.music.load('TopGear1-2.mp3')
    pygame.mixer.music.play(-1, 0.0)#repeat
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    
    #group each of the sprites into: friend, enemy, or score
    friendSprites = pygame.sprite.OrderedUpdates(road, nonCollide1, nonCollide2, repair, star, coin, player)
    enemySprites = pygame.sprite.OrderedUpdates(flotsam1, flotsam2, flotsam3, enemy1, enemy2)
    scoreSprite = pygame.sprite.Group(scoreboard)

    #instantiate the clock
    clock = pygame.time.Clock()
    
    #the following is the primary game loop. The in-game happens within this loop
    keepGoing = True
    while keepGoing:
        clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
        pygame.mouse.set_visible(False)#hide the mouse
        scoreboard.score += 1#add 1 to the score for each frame
        
        #if the player clicks a quit event, stop the game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
        
        #check collisions
        hitEnemy1 = pygame.sprite.collide_mask(player, enemy1)
        hitEnemy2 = pygame.sprite.collide_mask(player, enemy2)
        hitFlotsam1 = pygame.sprite.collide_mask(player, flotsam1)
        hitFlotsam2 = pygame.sprite.collide_mask(player, flotsam2)
        hitFlotsam3 = pygame.sprite.collide_mask(player, flotsam3)
        hitRepair = pygame.sprite.collide_mask(player, repair)
        hitStar = pygame.sprite.collide_mask(player, star)
        enemyCollision = pygame.sprite.collide_mask(enemy1, enemy2)
        
        #if the player collects a coin, play a sound, reset the coin, add to the player's score, and update the status
        if pygame.sprite.collide_mask(player, coin):
            player.sndCoin.play()
            coin.reset()
            scoreboard.score += COIN_SCORE
            scoreboard.status = "Coin! (+%d Score)" % (COIN_SCORE)
            
        #if the player collides with an enemy of flotsam, play the crash sound, take away health, make the player temporarily invulnerable
        #and reset the sprites
        if((hitEnemy1 or hitEnemy2 or hitFlotsam1 or hitFlotsam2 or hitFlotsam3) and not player.invulnerable):
            player.invulnerable = True#make the player invulnerable after a hit
            if hitEnemy1 or hitEnemy2:#if the player hit an enemy car
                player.sndCrash.play()#play crash sound
                scoreboard.health -= 20#take health away
                scoreboard.status = "Hit car (-20 HP)"#update status
                player.hitCar += 1
                
                #reset the enemies
                if hitEnemy1:
                    enemy1.reset()
                if hitEnemy2:
                    enemy2.reset()
            if hitFlotsam1 or hitFlotsam2 or hitFlotsam3:#if the player hit flotsam (environmental collisions)
                player.sndHit.play()#play hit sound
                scoreboard.health -= 10#take health away
                scoreboard.status = "Hit object (-10 HP)"#update status
                player.hitFlotsam += 1
                
                #reset the flotsam
                if hitFlotsam1:
                    flotsam1.reset()
                if hitFlotsam2:
                    flotsam2.reset()
                if hitFlotsam3:
                    flotsam3.reset()
            if scoreboard.health <= 0: #if the player has no health left
                keepGoing = False #end the game
            
        
        if hitRepair: #if the player hit a repair power-up
            player.sndFix.play()
            repair.reset()
            #add to the player health, up to a maximum of 100
            scoreboard.status = "Repair! (+%d HP)" % (REPAIR_HEALTH)
            player.hitPowerup += 1
            if(scoreboard.health <= 100):
                scoreboard.health += REPAIR_HEALTH
                if(scoreboard.health > 100):
                    scoreboard.health = 100
                    
        if hitStar: #if the player hit a star power-up
            player.sndInvulnerable.play()
            star.reset()#reset the star sprite
            player.hitPowerup += 1
            player.invulnerable = True#make the player invulnerable
            player.invulnerableDuration = STAR_DURATION #make player invulnerable for given seconds
            scoreboard.status = "Star! (%d sec) " % ((STAR_DURATION - player.invulnerableElapsed)/FRAMES_PER_SECOND)
                
        if enemyCollision: #if the two enemy cars collide, reset one to avoid overlap
            enemy2.reset()
            
        #update each sprite
        friendSprites.update()
        enemySprites.update()
        scoreSprite.update()
        
        #draw the sprites on the screen
        friendSprites.draw(screen)
        enemySprites.draw(screen)
        scoreSprite.draw(screen)
        
        #flip the display
        pygame.display.flip()
    
    #stop the engine sound if the game is over
    player.sndEngine.stop()
    pygame.mixer.stop()
    #return mouse cursor
    pygame.mouse.set_visible(True) 
    return scoreboard.score

"""
The instructions method defines the intro screen for the game. This is the first screen the player sees,
and it includes instructions for the game. 
"""  
def instructions(score):
    pygame.display.set_caption("Coin Collector!")
    
    #setup the game's menu music
    pygame.mixer.music.load('TopGear1-1.mp3')
    pygame.mixer.music.play(-1, 0.0)#repeat 
    pygame.mixer.music.set_volume(MUSIC_VOLUME)

    player = Player()#create the player object
    player.sndEngine.set_volume(0.3)
    
    road = Road()#create the road object
    
    #create a translucent surface on the title screen
    transSurface = pygame.Surface(screen.get_size())
    transSurface.fill((0, 0, 20))
    transSurface.set_alpha(150, 0)
    
    #group the sprites
    allSprites = pygame.sprite.OrderedUpdates(road, player)
    
    insFont = pygame.font.SysFont(None, 35)#set font

    #display instructions
    insLabels = []
    instructions = (
    "Coin Collector! ",
    "Previous score:  %d" % score,
    "",
    "Instructions:  You are a coin collector,",
    "gathering coins as fast as possible.",
    "",
    "Drive over coins to accumulate score quickly,",
    "but be careful not to run into other cars",    
    "or other obstacles. Your car will be destroyed ",
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
 
    #define the intro keepGoing loop
    keepGoing = True
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while keepGoing:
        clock.tick(FRAMES_PER_SECOND)
        
        #listen for events. If the player clicks, start the game. If they wish to quit,
        #the user can hit the X button at the top of the screen or press ESC.
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
    
        #update and draw the sprites on the instructions screen
        allSprites.update()
        allSprites.draw(screen)
        screen.blit(transSurface, (0, 0))
    
        for i in range(len(insLabels)):
            screen.blit(insLabels[i], (50, 30*i))

        pygame.display.flip()#flip the display
        
    player.sndEngine.stop()    
    pygame.mouse.set_visible(True)
    return donePlaying

"""
The gameEnd method manages the game end screen, displaying the player's score and a relevant background.
"""
def gameEnd(score):
    #display the background for the game end screen
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 40))
    background = pygame.image.load("endGame.png")
    screen.blit(background, (0, 0))
    
    #create a translucent surface on the title screen
    transSurface = pygame.Surface(screen.get_size())
    transSurface.fill((0, 0, 0))
    transSurface.set_alpha(200, 0)
    screen.blit(transSurface, (0, 0))
    
    #display game over messages
    gameOverMessage = "GAME OVER!"
    scoreMessage = "Score: %d" % score
    instructionsMessage = "Click to return to the main screen and play again!"
    
    tip1 = "Don't try to get every coin. It's not worth the risk."
    tip2 = "Always anticipate oncoming cars."
    tip3 = "Only two cars will appear at any given time."
    tip4 = "If you have to hit something, avoid cars and hit an object."
    tip5 = "Having a higher score doesn't make you a better person."
    tip6 = "It's dangerous to go alone! Take this."
    tip7 = "Don't eat yellow snow."
    tip8 = "Stay out of the oncoming lanes when possible."
    tip9 = "Don't drink and drive."
    tip10 = "This game is like Tetris. You never REALLY beat it."
    tips = [tip1, tip2, tip3, tip4, tip5, tip6, tip7, tip8, tip9, tip10]
    tip = random.randrange(0, len(tips))
    
    insBigFont = pygame.font.SysFont(None, 36)
    insSmallFont = pygame.font.SysFont(None, 26)
    
    screen.blit(insBigFont.render(gameOverMessage, True, (255,255,255)),(25, 50))
    screen.blit(insBigFont.render(scoreMessage, True, (255,255,255)),(25, 100))
    screen.blit(insBigFont.render(instructionsMessage, True, (255,255,255)),(25, 150))
    screen.blit(insSmallFont.render("TIP: " + tips[tip], True, (255,255,255)),(25, 200))
        
    pygame.display.flip()#flip the display
    
    #define the intro keepGoing loop
    keepGoing = True
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while keepGoing:
        clock.tick(FRAMES_PER_SECOND)
        
        #listen for events. Similar to instructions method
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
                    
    pygame.mouse.set_visible(True)
    return donePlaying
    
"""
The main loop starts the gaming process by calling the instructions method, followed by the game method if the 
player is not done playing.
"""
def main():
    donePlaying = False
    score = 0#instantiate score
    while not donePlaying:
        donePlaying = instructions(score)#get the score when the player is done playing
        if not donePlaying:
            score = game()#get the score from the player's game
            donePlaying = gameEnd(score)

if __name__ == "__main__":
    main()