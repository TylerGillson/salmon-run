# We'll use sys to properly exit with an error code.
import sys
import sdl2.ext

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources")

WHITE = sdl2.ext.Color(255, 255, 255)

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("Salmon Run", size=(592, 460))
    window.show()
    
    world = sdl2.ext.World()
    
    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)
    
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    
    sp_salmon = factory.from_color(WHITE, size=(20, 100))
    player = Player(world, sp_salmon, 0, 250)
    
    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        world.process()
    
    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())
