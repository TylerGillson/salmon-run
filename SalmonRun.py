import sys
import sdl2.ext
import random
import time
# Custom Modules:
import game
import globals
import sprite_classes
import music
import fonts

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources")

# Z-LAYERING DEPTHS:
#    0 - HIDE (HOME/GAMEOVER OFF)
#    1 - RIVER, RIVERBANKS
#    2 - SALMON
#    3 - ENEMIES
#    4 - HUD PANE
#    5 - HUD ELEMENTS (SCORE, SKULLS, ENERGY)
#    6 - SHOW (HOME/GAMEOVER ON)

class SalmonRun(game.Game):
    def __init__(self, name, winx, winy):
        super(SalmonRun, self).__init__(name, winx, winy)
        # Init sprites:
        self.sp_blank = self.factory.from_image(RESOURCES.get_path('blank.bmp'))
        self.sp_dashboard = self.factory.from_image(RESOURCES.get_path('dashboard.bmp'))
        self.sp_background = self.factory.from_image(RESOURCES.get_path('river.bmp'))
        # Init HUD sprites:
        self.sp_energy = self.factory.from_color((0,255,0,0),(155,30))
        self.energy = sprite_classes.Inert(self.world, self.sp_energy,625,10)
        self.energy.setDepth(5)
        # Init sprite class instances: (except for the special salmon...)
        self.blank = sprite_classes.Inert(self.world, self.sp_blank, 0, 0)
        self.dashboard = sprite_classes.Inert(self.world, self.sp_dashboard,0, 0)
        self.background = sprite_classes.Inert(self.world, self.sp_background,0, 50)
        # Init enemy sizes array:
        self.esizes = [x for x in range(0,15)]
        # Init energy bar:
        self.render_energy(155)

    def render_meals(self):
        self.sp_skull = self.factory.from_image(RESOURCES.get_path('skull.bmp'))
        self.skulls = [sprite_classes.Inert(self.world, self.sp_skull)] * self.salmon.meals.meals
        x = 340
        y = 15
        for skull in self.skulls:
            skull.setPos(x,y)
            skull.setDepth(5)
            x += 30

    def render_score(self):
        self.sp_score = self.factory.from_text(str(self.score),fontmanager=fonts.make_font('Score'))
        self.score_obj = sprite_classes.Inert(self.world, self.sp_score,84,18)
        self.score_obj.setDepth(5)
        self.score += 1

    def init_salmon(self, x, y, size=0, meals=0, velocity=(0,0), energy=155):
        self.sp_salmon = self.factory.from_image(RESOURCES.get_path('salmon' + str(size) + '.bmp'))
        self.salmon = sprite_classes.Player(self.world, self.sp_salmon, x, y, size+1, meals, velocity, energy)
        self.salmon.setDepth(2)
        self.collision.salmon = self.salmon
        self.movement.salmon = self.salmon
        self.aicontroller.target = self.salmon

    def grow_salmon(self):
        x,y = self.salmon.sprite.position
        size = self.salmon.size.size
        if size < 14:
            meals = self.salmon.meals.meals
            velocity = self.salmon.velocity.get_velocity()
            energy = self.salmon.energy.energy
            entity = self.world.get_entities(self.salmon.sprite)[0] # Delete old salmon:
            entity.delete()
            self.init_salmon(x,y,size-1,meals,velocity,energy)      # Init new salmon:
            globals.grow_salmon = False

    def render_home(self):
        self.sp_title = self.factory.from_text('SALMON RUN',fontmanager=fonts.make_font('Title'))
        self.title = sprite_classes.Inert(self.world, self.sp_title,66,110)
        self.title.setDepth(7)
        self.sp_play = self.factory.from_text('PRESS "P" TO PLAY',fontmanager=fonts.make_font('Play'))
        self.play = sprite_classes.Inert(self.world, self.sp_play,150,330)
        self.play.setDepth(7)
        self.blank.setDepth(6)
        while globals.home_lock == True:                # Wait for user-input
            events = sdl2.ext.get_events()
            for event in events:
                self.handleEvent(event)
            self.world.process()
        self.blank.setDepth(0)
        self.title.setDepth(0)
        self.play.setDepth(0)

    def render_game_over(self):
        self.sp_gameover = self.factory.from_text('GAME OVER',fontmanager=fonts.make_font('GameOver'))
        self.gameover = sprite_classes.Inert(self.world, self.sp_gameover,112,200)
        self.gameover.setDepth(7)
        self.blank.setDepth(6)
        self.world.process()
        sdl2.SDL_Delay(2000)
        self.blank.setDepth(0)
        self.gameover.setDepth(0)
        globals.clear_meals = False
        globals.grow_salmon = False

    def render_play(self):
        self.init_salmon(450,550)
        self.background.setDepth(1)
        #......
        self.sp_river = self.factory.from_image(RESOURCES.get_path('river.bmp'))
        self.sp_riverbanks = self.factory.from_image(RESOURCES.get_path('riverbanks2.bmp'))
        self.river = sprite_classes.Inert(self.world, self.sp_river, 0, 50)
        self.riverbanks = sprite_classes.Enemy(self.world, self.sp_riverbanks, (0,1), 0, -550, False)
        self.river.setDepth(1)
        self.riverbanks.setDepth(2)     # If this is less than 2 everything crashes on death!!!
        self.dashboard.setDepth(4)
        self.world.process()

    def spawn(self, path, size, depth, ai_flag):
        v = random.randint(1,10)
        x = random.randint(90,610)
        sp_enemy = self.factory.from_image(RESOURCES.get_path(path))
        self.enemy = sprite_classes.Enemy(self.world, sp_enemy, (0,v), x, 0, ai_flag)
        self.enemy.size.size = size
        self.enemy.setDepth(depth)

    def manage_spawn(self, delta_t):
        num = random.randint(1,3)                   # Give 1/3 of enemies ai
        ai_flag = True if num == 1 else False
        esize_lbound = self.salmon.size.size - 2 if self.salmon.size.size - 2 > 0 else 0
        esize_ubound = self.salmon.size.size + 3 if self.salmon.size.size + 3 <= 14 else 14
        esize_index = random.randint(esize_lbound,esize_ubound)
        esize = self.esizes[esize_index]
        if esize < self.salmon.size.size:
            ai_flag = False
        enemy_str = 'enemy' + str(esize) + '.bmp'
        self.spawn(enemy_str, esize, 3, ai_flag)

    def spawn_tree(self,side):
        if side == 'left':
            xL = random.randint(5,70)
            sp_treeL = self.factory.from_image(RESOURCES.get_path('tree.bmp'))
            self.treeL = sprite_classes.Enemy(self.world, sp_treeL, (0,1), xL, 50, False)
            self.treeL.setDepth(3)
        elif side == 'right':
            xR = random.randint(715,775)
            sp_treeR = self.factory.from_image(RESOURCES.get_path('tree.bmp'))
            self.treeR = sprite_classes.Enemy(self.world, sp_treeR, (0,1), xR, 70, False)
            self.treeR.setDepth(3)

    def decrement_energy(self):
        self.salmon.energy.energy -= 5

    def render_energy(self,w,): #Main
        self.sp_energy = self.factory.from_color((0,255,0,0),(w,30))
        # Yellow r 237 g 239 b0 Red 255 g0 b0
        self.energy_bar = sprite_classes.Inert(self.world,self.sp_energy,625,10)
        self.energy_bar.setDepth(5)

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
                    self.salmon.velocity.vy = 6
                elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    globals.running = False
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT, sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    self.salmon.velocity.vx -= 1
                    self.salmon.velocity.vy -= 1

    def run(self):
        #music.play_music()                      # Play background music
        self.render_home()                      # Render home screen
        globals.running = True
        while globals.running:                  # Begin event loop
            self.render_score()                 # Display the score
            self.render_meals()                 # Display meals
            delta_t = int(time.time()-self.start_t)
            # Spawn Enemies:
            if delta_t != self.old_t:
                self.manage_spawn(delta_t)      # Spawn enemies
                self.decrement_energy()
                if self.old_t % 3 == 0:
                    self.spawn_tree('left')
                elif self.old_t % 3 == 1:
                    self.spawn_tree('right')
            # Process SDL events:
            events = sdl2.ext.get_events()
            for event in events:
                self.handleEvent(event)
            # Grow salmon sprite every five meals:
            if globals.grow_salmon:
                self.grow_salmon()
            # Death process:
            if globals.death == True:
                self.score = 0                  # Reset the score
                self.render_game_over()         # Render Game Over screen & delete sprites
                globals.death = False
                globals.home_lock = True
                self.render_home()              # Render home screen
            self.old_t = delta_t
            sdl2.SDL_Delay(15)
            self.world.process()
            self.render_energy(self.salmon.energy.energy)
        sdl2.ext.quit()
        return 0

def main():
    sr = SalmonRun("Salmon Run",800,650)
    sr.run()

if __name__ == "__main__":
    main()
