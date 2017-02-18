# We'll use sys to properly exit with an error code.
import sys
import sdl2.ext
import random

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources")

### Begin Game Engine ###

# Declare globals:
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
    def setDepth(self, depth):
        self.sprite.depth = depth

class Enemy(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
    def setDepth(self, depth):
        self.sprite.depth = depth

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
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.salmon = None
    
    def _overlap(self, item):
        pos, sprite = item
        if sprite == self.salmon.sprite:
            return False
        left, top, right, bottom = sprite.area
        s_left, s_top, s_right, s_bottom = self.salmon.sprite.area
        return (s_left < right and 
                s_right > left and 
                s_top < bottom and 
                s_bottom > top)
    
    def process(self, world, componentsets):
        global death
        global home_lock
        # During game play, check for sprite collisions:
        if death == False and home_lock == False:
            collitems = [comp for comp in componentsets if self._overlap(comp)]
            if collitems:
                # PIXEL-PERFECT COLLISION ... ANALYZE ALPHA CHANNEL PIXELS
                #print(collitems)
                #print(collitems[0][1])
                #print(collitems[0][1].area)
                #
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
            valid = [sprite for sprite in components if (sprite.depth==3 and sprite.area[1]==550)==False]
            delete = set(components) - set(valid)
            self.render(sorted(valid, key=self._sortfunc))
            for sprite in delete:
                entity = world.get_entities(sprite)[0]
                entity.delete()
        
        # While on the home screen, simply render everything:
        else:
            self.render(sorted(components, key=self._sortfunc))
        
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
        # Build world & show window:
        self.world.add_system(self.spriterenderer)
        self.world.add_system(self.movement)
        self.world.add_system(self.collision)
        self.window.show()

### End Game Engine ###
        
# Z-LAYERING DEPTHS:
#    0 - HIDE (HOME/GAMEOVER OFF)
#    1 - BACKGROUND
#    2 - SALMON
#    3 - ENEMIES
#    4 - HUD
#    5 - SHOW (HOME/GAMEOVER ON)
        
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
    
    def init_salmon(self):
        self.salmon = Player(self.world, self.sp_salmon, 400, 550)
        self.salmon.setDepth(2)
        self.collision.salmon = self.salmon
        
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
        
    def spawn(self, path, depth):
        v = random.randint(1,10)
        x = random.randint(90,610)
        sp_enemy = self.factory.from_image(RESOURCES.get_path(path))
        self.enemy = Enemy(self.world, sp_enemy, x, 0)
        self.enemy.velocity.vy = v
        self.enemy.setDepth(depth)
    
    def run(self):
        self.render_home()                      # Render home screen
        running = True
        while running:                          # Begin event loop
            ticks = sdl2.timer.SDL_GetTicks()
            # Spawn Enemies:
            if ticks % 15 in range(1):
                self.spawn('redEnemy.bmp', 3)
            # Process SDL events:
            events = sdl2.ext.get_events()
            for event in events:
                self.handleEvent(event)
            
            global death
            global home_lock
            # Death process:
            if death == True:
                self.render_game_over()         # Render Game Over screen & delete sprites
                death = False
                home_lock = True
                self.render_home()              # Render home screen
            sdl2.SDL_Delay(10)
            self.world.process()
        sdl2.ext.quit()
    
    def handleEvent(self, event):
        global home_lock
        if home_lock == True:
            if event.key.keysym.sym == sdl2.SDLK_p:
                home_lock = False
                self.render_play()              # Render game play screen
        else:
            if event.type == sdl2.SDL_QUIT:
                running = False
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    self.salmon.velocity.vx = -3
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    self.salmon.velocity.vx = 3
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    self.salmon.velocity.vy = -3
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    self.salmon.velocity.vy = 3
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT, sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    self.salmon.velocity.vx -= 1
                    self.salmon.velocity.vy -= 1

def main():
    sr = SalmonRun("Salmon Run",800,650)
    sr.run()

if __name__ == "__main__":
    main()