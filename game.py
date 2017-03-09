import sdl2.ext
import time
# Custom Modules:
import movement
import collision
import renderers

class Game(object):
    def __init__(self, name, winx=800, winy=600):
        sdl2.ext.init()
        # Init basics:
        self.window = sdl2.ext.Window(name, size=(winx, winy))
        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        self.world = sdl2.ext.World()
        # Init systems:
        self.movement = movement.MovementSystem(90, 50, 710, winy) # Movement area hard-coded
        self.collision = collision.CollisionSystem(0, 0, winx, winy)
        self.spriterenderer = renderers.SoftwareRenderer(self.window)
        self.aicontroller = movement.TrackingAIController(0, winy)
        # Build world & show window:
        self.world.add_system(self.spriterenderer)
        self.world.add_system(self.movement)
        self.world.add_system(self.collision)
        self.world.add_system(self.aicontroller)
        self.window.show()
        # Init time variables:
        self.start_t = time.time()
        self.old_t = 0
        # Init score:
        self.score = 0
