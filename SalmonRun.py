import sys
import sdl2.ext
import random
import time
import sdl2.sdlmixer
import os

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources")

### Begin Game Engine ###

# Declare globals:
running = True   # boolean for governing main event loop.
death = False    # death is used as a trigger to indicate that the player has collided with                 either an enemy or an obstacle.
home_lock = True # home_lock makes world.process() safe when rendering the home screen.                     It prevents certain inputs from crashing the game by attempting to                       influence sprites that do not currently exist.

class Inert(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
    def setDepth(self, depth):
        self.sprite.depth = depth
    
class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.size = Size(1)
        self.meals = Meals(0)
        self.energy = Energy(100)
    def setDepth(self, depth):
        self.sprite.depth = depth

class PlayerData(object):
    def __init__(self):
        super(PlayerData, self).__init__()
        self.ai = False

class Enemy(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0, ai=False):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.playerdata = PlayerData()
        self.playerdata.ai = ai
        self.size = Size()
    def setDepth(self, depth):
        self.sprite.depth = depth

class Size(object):
    def __init__(self, size=0):
        super(Size, self).__init__()
        self.size = size
    def increment(self):
        self.size += 1
    def decrement(self):
        self.size -= 1

class Meals(object):
    def __init__(self, meals=0):
        super(Meals, self).__init__()
        self.meals = meals
    def eat(self):
        self.meals += 1
    def reset(self):
        self.meals = 0

class Energy(object):
    def __init__(self, energy=0):
        super(Energy, self).__init__()
        self.energy = energy
    def boost(self, amount):
        self.energy += amount

class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            pmaxx = sprite.x + swidth
            pmaxy = sprite.y + sheight
            if pmaxx > self.maxx:
                sprite.x = self.maxx - swidth
            if pmaxy > self.maxy:
                sprite.y = self.maxy - sheight

class CollisionSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(CollisionSystem, self).__init__()
        self.componenttypes = Size, Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.salmon = None
    
    def _overlap(self, item):
        size, pos, sprite = item
        
        if sprite.depth != 3:
            return False
        
        left, top, right, bottom = sprite.area
        s_left, s_top, s_right, s_bottom = self.salmon.sprite.area
        
        coll = s_left < right and s_right > left and \
               s_top < bottom and s_bottom > top
        
        #if coll:
        #    coll = False
        #    # Calculate Collision Rect:
        #    x1 = max(left,s_left)
        #    y1 = max(top,s_top)
        #    x2 = min(right,s_right)
        #    y2 = min(bottom,s_bottom)
        #    w = x2 - x1
        #    h = y2 - y1
            # Pixel Perfect Collision:
        #    x=0
        #    y=0
        #    sprite_pix = sdl2.ext.PixelView(sprite) #sdl2.ext.pixels2d(sprite)
        #    salmon_pix = sdl2.ext.PixelView(self.salmon.sprite)
        #    while y < h:
        #        while x < w:
        #            if sprite_pix[y][x] != 0 and salmon_pix[y][x] != 0:
                        #print(sprite_pix[y][x])
                        #print(salmon_pix[y][x])
        #                coll = True
        #            x += 1
        #        y += 1
            
        return coll
    
    def process(self, world, componentsets):
        global death
        global home_lock
        # During game play, check for sprite collisions:
        if death == False and home_lock == False:
            collitems = [comp for comp in componentsets if self._overlap(comp)]
            if collitems:
                size, pos, sprite = collitems[0]
                if self.salmon.size.size > size.size:
                    entity = world.get_entities(sprite)[0]
                    entity.delete()                 # Delete eaten enemy
                    self.salmon.meals.eat()         # Increment meals counter
                    #print(self.salmon.meals.meals)
                else:
                    death = True

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)
        
    # Manage sprite rendering according to state of globals:
    def process(self, world, components):
        global death
        global home_lock
        # On death, render everyhing except player and enemy sprites,
        # then delete all player and enemy sprites:
        if death == True:
            valid = [sprite for sprite in components if sprite.depth not in [2,3]]
            delete = set(components) - set(valid)
            self.render(sorted(valid, key=self._sortfunc))
            for sprite in delete:
                entity = world.get_entities(sprite)[0]
                entity.delete()
        
        # During game play, render everything except enemies that have reached the,
        # bottom of the screen, then delete said enemy sprites from the world.
        elif home_lock == False:
            valid = [sprite for sprite in components if (sprite.depth==3 and sprite.area[3]==650)==False]
            delete = set(components) - set(valid)
            self.render(sorted(valid, key=self._sortfunc))
            for sprite in delete:
                entity = world.get_entities(sprite)[0]
                entity.delete()
        
        # While on the home screen, simply render everything:
        else:
            self.render(sorted(components, key=self._sortfunc))

class TrackingAIController(sdl2.ext.Applicator):
    def __init__(self, miny, maxy):
        super(TrackingAIController, self).__init__()
        self.componenttypes = PlayerData, Velocity, sdl2.ext.Sprite
        self.miny = miny
        self.maxy = maxy
        self.target = None

    def process(self, world, componentsets):
        for pdata, vel, sprite in componentsets:
            if not pdata.ai:        # Enemies with AI track salmon in x-axis
                continue
            # Calc homing sprite axis centres:
            centerx = sprite.x + sprite.size[0] // 2
            centery = sprite.y + sprite.size[1] // 2
            # Calc target sprite axis centres:
            s_centerx = self.target.sprite.x + self.target.sprite.size[0] // 2
            s_centery = self.target.sprite.y + self.target.sprite.size[1] // 2
            # If homing sprite is below target sprite, revert to standard velocity:
            if s_centery < centery:
                if vel.vx==0:
                    continue
                vel.vx = 0
                vel.vy = random.randint(1,10)
                continue
            # Otherwise, track target sprite in the x-axis:
            elif s_centerx < centerx:         # salmon is to the left
                if vel.vy > 6:
                    vel.vx = -2
                else:
                    vel.vx = -4
                #vel.vx = random.randint(1,10)*-1
            elif s_centerx > centerx:       # salmon is to the right
                if vel.vy > 6:
                    vel.vx = 2
                else:
                    vel.vx = 4
                #vel.vx = random.randint(1,10)
        
class Game(object):
    def __init__(self, name, winx=800, winy=600):
        sdl2.ext.init()
        # Init basics:
        self.window = sdl2.ext.Window(name, size=(winx, winy))
        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        self.world = sdl2.ext.World()
        # Init systems:
        self.movement = MovementSystem(90, 50, 710, winy) # Movement area hard-coded
        self.collision = CollisionSystem(0, 0, winx, winy)
        self.spriterenderer = SoftwareRenderer(self.window)
        self.aicontroller = TrackingAIController(0, winy)
        # Build world & show window:
        self.world.add_system(self.spriterenderer)
        self.world.add_system(self.movement)
        self.world.add_system(self.collision)
        self.world.add_system(self.aicontroller)
        self.window.show()
        
        self.start_t = time.time()
        self.old_t = 0
        
### End Game Engine ###
        
# Z-LAYERING DEPTHS:
#    0 - HIDE (HOME/GAMEOVER OFF)
#    1 - BACKGROUND
#    2 - SALMON
#    3 - ENEMIES
#    4 - HUD
#    5 - SHOW (HOME/GAMEOVER ON)

# Sizing Guide:
#   0 - greenEnemy / salmon0
#   1 - blueEnemy / salmon1
#   2 
#   3
#   4
#   5
#   6
#   7
#   8
#   9
#   10
#   11
#   12
#   13
#   14 - 
#   15 - redEnemy / salmon15

### Begin Custom Game Implementation ###

class SalmonRun(Game):
    def __init__(self, name, winx, winy):
        super(SalmonRun, self).__init__(name, winx, winy)
        # Init sprites:
        self.sp_homescreen = self.factory.from_image(RESOURCES.get_path('homescreen.bmp'))
        self.sp_gameover = self.factory.from_image(RESOURCES.get_path('gameover.bmp'))
        self.sp_background = self.factory.from_image(RESOURCES.get_path('background.bmp'))
        self.sp_dashboard = self.factory.from_image(RESOURCES.get_path('dashboard.bmp'))
        self.sp_salmon = self.factory.from_image(RESOURCES.get_path('salmon.bmp'))
        # Init sprite class instances: (except for the special salmon...)
        self.homescreen = Inert(self.world, self.sp_homescreen, 0, 0)
        self.gameover = Inert(self.world, self.sp_gameover, 0, 0)
        self.background = Inert(self.world, self.sp_background, 0, 50)
        self.dashboard = Inert(self.world, self.sp_dashboard,0, 0)
    
    def init_numbers(self):
        self.zero = self.factory.from_image(RESOURCES.get_path('s_numbers.bmp'))
        
    def init_salmon(self):
        self.salmon = Player(self.world, self.sp_salmon, 400, 550)
        self.salmon.setDepth(2)
        self.collision.salmon = self.salmon
        self.aicontroller.target = self.salmon
        
    def render_home(self):
        self.homescreen.setDepth(5)
        self.world.process()
        while home_lock == True:                # Wait for user-input
            events = sdl2.ext.get_events()
            for event in events:
                self.handleEvent(event)
            self.world.process()
        self.homescreen.setDepth(0)
                
    def render_game_over(self):
        self.gameover.setDepth(5)
        self.world.process()
        sdl2.SDL_Delay(2000)
        self.gameover.setDepth(0)
        
    def render_play(self):
        self.init_salmon()
        self.background.setDepth(1)
        self.dashboard.setDepth(4)
                
    def spawn(self, path, size, depth, tracking):
        v = random.randint(1,10)
        x = random.randint(90,610)
        sp_enemy = self.factory.from_image(RESOURCES.get_path(path))
        if tracking:
            self.enemy = Enemy(self.world, sp_enemy, x, 0, True)
        else:
            self.enemy = Enemy(self.world, sp_enemy, x, 0, False)
        self.enemy.velocity.vy = v
        self.enemy.size.size = size
        self.enemy.setDepth(depth)
    
    def music(self):
        mixformat = sdl2.sdlmixer.MIX_DEFAULT_FORMAT  # sets up the format for OpenAudio
        musicfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/sounds","Chiptune.wav")
        music_init = sdl2.sdlmixer.MIX_INIT_MP3
        sdl2.sdlmixer.Mix_Init(music_init)
        sdl2.sdlmixer.Mix_OpenAudio(22050, mixformat, 2, 4096)
        loadmusic = sdl2.sdlmixer.Mix_LoadMUS(musicfile.encode("utf-8")) # pre-Load Music
        sdl2.sdlmixer.Mix_PlayMusic(loadmusic, -1)  # play music
        #print(sdl2.sdlmixer.Mix_GetError())
    
    def run(self):
        global running
        global death
        global home_lock
        self.music()                            # Init music capabilities
        
        self.render_home()                      # Render home screen
        running = True
        while running:                          # Begin event loop
            delta_t = int(time.time()-self.start_t)
            # Spawn Enemies:
            if delta_t != self.old_t:
                num = random.randint(1,3)       # Give 1/3 of enemies ai
                ai_flag = True if num == 1 else False
                if delta_t % 2 == 0:
                    self.spawn('greenEnemy.bmp', 0, 3, ai_flag)
                elif delta_t % 3 == 0:
                    self.spawn('blueEnemy.bmp', 2, 3, ai_flag)
                elif delta_t % 5 == 0:
                    self.spawn('redEnemy.bmp', 3, 3, ai_flag)
                # Process SDL events:
            events = sdl2.ext.get_events()
            for event in events:
                self.handleEvent(event)
            # Death process:
            if death == True:
                self.render_game_over()         # Render Game Over screen & delete sprites
                death = False
                home_lock = True
                self.render_home()              # Render home screen
            sdl2.SDL_Delay(10)
            self.old_t = delta_t
            self.world.process()
        sdl2.ext.quit()
        return 0
    
    def handleEvent(self, event):
        global home_lock
        global running
        # Handle home screen events:
        if home_lock == True:
            if event.type == sdl2.SDL_QUIT:
                home_lock = False
                running = False
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_p:
                    home_lock = False
                    self.render_play()          # Render game play screen
        # Handle game play events:
        else:
            if event.type == sdl2.SDL_QUIT:
                running = False
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    self.salmon.velocity.vx = -6
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    self.salmon.velocity.vx = 6
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    self.salmon.velocity.vy = -3
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    self.salmon.velocity.vy = 3
                elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    running = False
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT, sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    self.salmon.velocity.vx -= 1
                    self.salmon.velocity.vy -= 1

def main():
    sr = SalmonRun("Salmon Run",800,650)
    sr.run()

if __name__ == "__main__":
    main()