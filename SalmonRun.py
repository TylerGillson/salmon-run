# We'll use sys to properly exit with an error code.
import sys
import sdl2.ext

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources")

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

class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

class Inert(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy

class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()

class Enemy(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("Salmon Run", size=(800, 600))
    window.show()
    
    world = sdl2.ext.World()
    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)
    
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    
    movement = MovementSystem(0, 0, 800, 600)
    world.add_system(movement)
    
    sp_background = factory.from_image(RESOURCES.get_path('background.bmp'))
    background = Inert(world, sp_background, 0, 0)
    
    sp_salmon = factory.from_image(RESOURCES.get_path('salmon.bmp'))
    salmon = Player(world, sp_salmon, 400, 550)
    
    sp_renemy = factory.from_image(RESOURCES.get_path('redEnemy.bmp'))
    enemy = Enemy(world, sp_renemy, 400, 100)

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    salmon.velocity.vx = -3
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    salmon.velocity.vx = 3
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    salmon.velocity.vy = -3
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    salmon.velocity.vy = 3
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT, sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    salmon.velocity.vx -= 1
                    salmon.velocity.vy -= 1
                    
        sdl2.SDL_Delay(10)
        world.process()
    
    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())
