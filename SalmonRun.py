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
#    3 - ENEMIES, TREES
#    4 - HUD PANE
#    5 - HUD ELEMENTS (SCORE, SKULLS, ENERGY)
#    6 - SHOW (HOME/GAMEOVER ON)
#    7 - HOME/GAMEOVER TTF'S

class SalmonRun(game.Game):
    def __init__(self, name, winx, winy):
        super(SalmonRun, self).__init__(name, winx, winy)
        # Init sprites:
        self.sp_blank = self.factory.from_image(RESOURCES.get_path('blank.bmp'))
        self.sp_dashboard = self.factory.from_image(RESOURCES.get_path('dashboard.bmp'))
        # Init HUD sprites:
        self.sp_energy = self.factory.from_color((0,255,0,0),(155,30))
        self.energy = sprite_classes.Inert(self.world, self.sp_energy,625,10)
        self.energy.setDepth(5)
        # Init sprite class instances: (except for the special salmon...)
        self.blank = sprite_classes.Inert(self.world, self.sp_blank, 0, 0)
        self.dashboard = sprite_classes.Inert(self.world, self.sp_dashboard,0, 0)
        # Init enemy sizes array:
        self.esizes = [x for x in range(0,15)]

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
        music.play_sample('Bubbles.wav', True)
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
        self.blank.setDepth(6)
        self.sp_gameover = self.factory.from_text('GAME OVER',fontmanager=fonts.make_font('GameOver'))
        self.gameover = sprite_classes.Inert(self.world, self.sp_gameover,112,110)
        self.gameover.setDepth(7)
        # Print scores to screen:
        self.sp_your_score = self.factory.from_text('Your Score: '+str(self.score),fontmanager=fonts.make_font('GameOverScore'))
        self.your_score = sprite_classes.Inert(self.world, self.sp_your_score,300,240)
        self.your_score.setDepth(7)
        self.sp_top_scores = self.factory.from_text('Top Scores:',fontmanager=fonts.make_font('GameOverScore'))
        self.top_scores = sprite_classes.Inert(self.world, self.sp_top_scores,300,300)
        self.top_scores.setDepth(7)
        top_scores_f = open('top_scores.txt', 'r')
        top_scores = top_scores_f.readlines()
        to_print = len(top_scores)
        while True:
            self.sp_a_score = self.factory.from_text('1: '+top_scores[0][:-1:],fontmanager=fonts.make_font('GameOverScore'))
            self.score_1 = sprite_classes.Inert(self.world, self.sp_a_score,350,360)
            self.score_1.setDepth(7)
            if to_print == 1:
                break
            self.sp_a_score = self.factory.from_text('2: '+top_scores[1][:-1:],fontmanager=fonts.make_font('GameOverScore'))
            self.score_2 = sprite_classes.Inert(self.world, self.sp_a_score,350,400)
            self.score_2.setDepth(7)
            if to_print == 2:
                break
            self.sp_a_score = self.factory.from_text('3: '+top_scores[2][:-1:],fontmanager=fonts.make_font('GameOverScore'))
            self.score_3 = sprite_classes.Inert(self.world, self.sp_a_score,350,440)
            self.score_3.setDepth(7)
            if to_print == 3:
                break
            self.sp_a_score = self.factory.from_text('4: '+top_scores[3][:-1:],fontmanager=fonts.make_font('GameOverScore'))
            self.score_4 = sprite_classes.Inert(self.world, self.sp_a_score,350,480)
            self.score_4.setDepth(7)
            if to_print == 4:
                break
            self.sp_a_score = self.factory.from_text('5: '+top_scores[4][:-1:],fontmanager=fonts.make_font('GameOverScore'))
            self.score_5 = sprite_classes.Inert(self.world, self.sp_a_score,350,520)
            self.score_5.setDepth(7)
            break
        self.sp_retry = self.factory.from_text('Press "p" to retry...',fontmanager=fonts.make_font('GameOverScore'))
        self.retry = sprite_classes.Inert(self.world, self.sp_retry,300,580)
        self.retry.setDepth(7)
        while globals.game_over_lock == True:                # Wait for user-input
            events = sdl2.ext.get_events()
            for event in events:
                self.handleEvent(event)
            self.world.process()

        self.score = 0                  # Reset the score
        entity = self.world.get_entities(self.gameover.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.your_score.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.top_scores.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.score_1.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.score_2.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.score_3.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.score_4.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.score_5.sprite)[0]
        entity.delete()
        entity = self.world.get_entities(self.retry.sprite)[0]
        entity.delete()
        self.blank.setDepth(0)
        globals.clear_meals = False
        globals.grow_salmon = False

    def init_energy_bar(self):
        self.render_energy(155)
        self.sp_energybar_border = self.factory.from_image(RESOURCES.get_path('energy_bar_border.bmp'))
        self.energybar_border = sprite_classes.Inert(self.world, self.sp_energybar_border,623,8)
        self.energybar_border.setDepth(5)

    def render_play(self):
        music.play_music('Chiptune.wav',-1)     # Play background music
        music.play_sample('Bubbles.wav', True)
        self.init_salmon(450,550)
        self.init_energy_bar()
        # Init river & riverbanks then bring up the HUD:
        self.sp_river = self.factory.from_image(RESOURCES.get_path('river.bmp'))
        self.river = sprite_classes.Inert(self.world, self.sp_river, 0, 50)
        self.river.setDepth(1)
        self.sp_river_top = self.factory.from_image(RESOURCES.get_path('top.bmp'))
        self.sp_river_bottom = self.factory.from_image(RESOURCES.get_path('bottom.bmp'))
        self.river_top = sprite_classes.Enemy(self.world, self.sp_river_top, (0,1), 0, -550, False)
        self.river_bottom = sprite_classes.Enemy(self.world, self.sp_river_bottom, (0,1), 0, 50, False)
        self.river_top.setDepth(2)
        self.river_bottom.setDepth(2)
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
        num = random.randint(1,3)
        ai_flag = True if num == 1 else False       # Give 1/3 of enemies ai
        esize_lbound = self.salmon.size.size - 2 if self.salmon.size.size - 2 > 0 else 0
        esize_ubound = self.salmon.size.size + 3 if self.salmon.size.size + 3 <= 14 else 14
        if self.salmon.energy.energy < 52:          # If energy in red zone, spawn smaller enemies
            esize_index = random.randint(esize_lbound,esize_ubound-1)
        else:
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

    def spawn_rock(self):
        x = random.randint(90,610)
        sp_rock = self.factory.from_image(RESOURCES.get_path('small_rock.bmp'))
        self.rock = sprite_classes.Enemy(self.world, sp_rock, (0,1), x, 50, False)
        self.rock.setDepth(3)
        self.rock.size.size = 99

    def spawn_whirlpool(self):
        x = random.randint(90,610)
        sp_whirlpool = self.factory.from_image(RESOURCES.get_path('whirlpool.bmp'))
        self.whirlpool = sprite_classes.Enemy(self.world, sp_whirlpool, (0,1), x, 50, False)
        self.whirlpool.setDepth(3)
        self.whirlpool.size.size = 50

    def decrement_energy(self):
        self.salmon.energy.energy -= 4
        if self.salmon.energy.energy <= 0:
            globals.death = True

    def render_energy(self,w):
        if self.salmon.energy.energy > 103:
            color = (0,255,0,0)
        elif self.salmon.energy.energy > 51:
            color = (237,239,0,0)
        else:
            color = (255,0,0,0)
        if w > 155:
            w = 155
        self.sp_energy = self.factory.from_color(color,(w,30))
        self.energy_bar = sprite_classes.Inert(self.world,self.sp_energy,625,10)
        self.energy_bar.setDepth(5)

    def save_score(self,score):
        top_scores = open('top_scores.txt', 'a+')
        top_scores.seek(0,0)
        lines = top_scores.readlines()
        if not lines:
            lines.append(str(score))
        else:
            counter = 0
            for line in lines:
                if score > int(line.strip()):
                    break
                counter += 1
            lines.insert(counter,str(score))

        if len(lines) > 5:
            del lines[-1]
        top_scores.seek(0,0)
        top_scores.truncate()
        for line in lines:
            top_scores.write(line.strip()+'\n')
        top_scores.close()

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
        elif globals.game_over_lock == True:
            if event.type == sdl2.SDL_QUIT:
                globals.game_over_lock = False
                globals.running = False
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_p:
                    globals.game_over_lock = False
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
                elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                   if globals.pause == False:
                       globals.pause = True
                       self.sp_pauseL = self.factory.from_color((255, 255, 255, 0), (50, 100))
                       self.pause_barL = sprite_classes.Inert(self.world, self.sp_pauseL, 300, 300)
                       self.pause_barL.setDepth(5)
                       self.sp_pauseR = self.factory.from_color((255, 255, 255, 0), (50, 100))
                       self.pause_barR = sprite_classes.Inert(self.world, self.sp_pauseR, 370, 300)
                       self.pause_barR.setDepth(5)
                   elif globals.pause == True:
                       globals.pause = False
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT, sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    self.salmon.velocity.vx -= 1
                    self.salmon.velocity.vy -= 1

    def run(self):
        music.init_audio()
        self.render_home()                      # Render home screen
        globals.running = True
        while globals.running:                  # Begin event loop
            if globals.pause == False:
                self.render_score()                 # Display the score
                self.render_meals()                 # Display meals
                delta_t = int(time.time()-self.start_t)
                # Spawn Enemies:
                if delta_t != self.old_t:
                    self.manage_spawn(delta_t)      # Spawn enemies
                    self.decrement_energy()
                    if self.old_t % 3 == 0:
                        if self.salmon.velocity.vy < 0:
                            self.spawn_tree('left')
                    elif self.old_t % 3 == 1:
                        if self.salmon.velocity.vy < 0:
                            self.spawn_tree('right')
                    elif self.old_t % 4 == 0:       # Spawn rocks
                        self.spawn_rock()
                    if self.old_t % 12 == 0:        # Spawn whirlpools
                        self.spawn_whirlpool()
                # Process SDL events:
                events = sdl2.ext.get_events()
                for event in events:
                    self.handleEvent(event)
                # Grow salmon sprite every five meals:
                if globals.grow_salmon:
                    self.grow_salmon()
                # Death process:
                if globals.death == True:
                    self.save_score(self.score)
                    globals.game_over_lock = True
                    self.render_game_over()         # Render Game Over screen & delete sprites
                    globals.death = False
                    globals.home_lock = True
                    self.render_home()              # Render home screen
                self.old_t = delta_t
                sdl2.SDL_Delay(15)
                self.world.process()
                self.render_energy(self.salmon.energy.energy)
            while globals.pause:
                events = sdl2.ext.get_events()
                for event in events:
                    self.handleEvent(event)
        sdl2.ext.quit()
        return 0

def main():
    sr = SalmonRun("Salmon Run",800,650)
    sr.run()

if __name__ == "__main__":
    main()
