import sys
import os
import sdl2.ext
import sdl2.sdlmixer
import random
import time
# Custom Modules:
import globals
import sprite_classes
import collision
import renderers
import movement

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources")

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
        self.texspriterenderer = renderers.TextureRenderer(self.window)
        self.aicontroller = movement.TrackingAIController(0, winy)
        # Build world & show window:
        self.world.add_system(self.spriterenderer)
        self.world.add_system(self.texspriterenderer)
        self.world.add_system(self.movement)
        self.world.add_system(self.collision)
        self.world.add_system(self.aicontroller)
        self.window.show()
        # Init time variables:
        self.start_t = time.time()
        self.old_t = 0

# Z-LAYERING DEPTHS:
#    0 - HIDE (HOME/GAMEOVER OFF)
#    1 - BACKGROUND
#    2 - SALMON
#    3 - ENEMIES
#    4 - HUD
#    5 - SHOW (HOME/GAMEOVER ON)

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
        self.homescreen = sprite_classes.Inert(self.world, self.sp_homescreen, 0, 0)
        self.gameover = sprite_classes.Inert(self.world, self.sp_gameover, 0, 0)
        self.background = sprite_classes.Inert(self.world, self.sp_background, 0, 50)
        self.dashboard = sprite_classes.Inert(self.world, self.sp_dashboard,0, 0)

    def init_numbers(self):
        self.zero = self.factory.from_image(RESOURCES.get_path('s_numbers.bmp'))

    def init_salmon(self):
        self.salmon = sprite_classes.Player(self.world, self.sp_salmon, 400, 550)
        self.salmon.setDepth(2)
        self.collision.salmon = self.salmon
        self.aicontroller.target = self.salmon

    def render_home(self):
        self.homescreen.setDepth(5)
        self.world.process()
        while globals.home_lock == True:                # Wait for user-input
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
            self.enemy = sprite_classes.Enemy(self.world, sp_enemy, x, 0, True)
        else:
            self.enemy = sprite_classes.Enemy(self.world, sp_enemy, x, 0, False)
        self.enemy.velocity.vy = v
        self.enemy.size.size = size
        self.enemy.setDepth(depth)

    def manage_spawn(self, delta_t, ai_flag):
        if delta_t % 1 == 0:
            self.spawn('enemy0.bmp', 0, 3, ai_flag)
        if delta_t % 2 == 0:
            self.spawn('enemy1.bmp', 1, 3, ai_flag)
        if delta_t % 3 == 0:
            self.spawn('enemy2.bmp', 2, 3, ai_flag)
        if delta_t % 4 == 0:
            self.spawn('enemy3.bmp', 3, 3, ai_flag)
        if delta_t % 5 == 0:
            self.spawn('enemy4.bmp', 4, 3, ai_flag)
        if delta_t % 8 == 0:
            self.spawn('enemy5.bmp', 5, 3, ai_flag)
        if delta_t % 10 == 0:
            self.spawn('enemy6.bmp', 6, 3, ai_flag)
        if delta_t % 12 == 0:
            self.spawn('enemy7.bmp', 7, 3, ai_flag)
        if delta_t % 14 == 0:
            self.spawn('enemy8.bmp', 8, 3, ai_flag)
        if delta_t % 16 == 0:
            self.spawn('enemy9.bmp', 9, 3, ai_flag)
        if delta_t % 18 == 0:
            self.spawn('enemy10.bmp', 10, 3, ai_flag)
        if delta_t % 20 == 0:
            self.spawn('enemy11.bmp', 11, 3, ai_flag)
        if delta_t % 22 == 0:
            self.spawn('enemy12.bmp', 12, 3, ai_flag)
        if delta_t % 24 == 0:
            self.spawn('enemy13.bmp', 13, 3, ai_flag)
        if delta_t % 26 == 0:
            self.spawn('enemy14.bmp', 14, 3, ai_flag)

    def music(self):
        mixformat = sdl2.sdlmixer.MIX_DEFAULT_FORMAT  # sets up the format for OpenAudio
        musicfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/sounds","Chiptune.wav")
        music_init = sdl2.sdlmixer.MIX_INIT_MP3
        sdl2.sdlmixer.Mix_Init(music_init)
        sdl2.sdlmixer.Mix_OpenAudio(22050, mixformat, 2, 4096)
        loadmusic = sdl2.sdlmixer.Mix_LoadMUS(musicfile.encode("utf-8")) # pre-Load Music
        sdl2.sdlmixer.Mix_PlayMusic(loadmusic, -1)  # play music

    def handleEvent(self, event):
        # Handle home screen events:
        if globals.home_lock == True:
            if event.type == sdl2.SDL_QUIT:
                globals.home_lock = False
                globals.running = False
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_p:
                    globals.home_lock = False
                    self.render_play()          # Render game play screen
        # Handle game play events:
        else:
            if event.type == sdl2.SDL_QUIT:
                globals.running = False
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
                    globals.running = False
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT, sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    self.salmon.velocity.vx -= 1
                    self.salmon.velocity.vy -= 1

    def run(self):
        self.music()                            # Init music capabilities
        self.render_home()                      # Render home screen
        globals.running = True
        while globals.running:                          # Begin event loop
            delta_t = int(time.time()-self.start_t)
            # Spawn Enemies:
            if delta_t != self.old_t:
                num = random.randint(1,6)       # Give 1/6 of enemies ai
                ai_flag = True if num == 1 else False
                self.manage_spawn(delta_t, ai_flag)  # Spawn enemies
            # Process SDL events:
            events = sdl2.ext.get_events()
            for event in events:
                self.handleEvent(event)
            # Death process:
            if globals.death == True:
                self.render_game_over()         # Render Game Over screen & delete sprites
                globals.death = False
                globals.home_lock = True
                self.render_home()              # Render home screen
            sdl2.SDL_Delay(10)
            self.old_t = delta_t
            self.world.process()
        sdl2.ext.quit()
        return 0

def main():
    sr = SalmonRun("Salmon Run",800,650)
    sr.run()

if __name__ == "__main__":
    main()
