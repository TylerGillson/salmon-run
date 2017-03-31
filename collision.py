import sdl2.ext
import random
import copy
# Custom Modules:
import sprite_classes
import music
import globals

class CollisionSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(CollisionSystem, self).__init__()
        self.componenttypes = sprite_classes.Size, sprite_classes.Velocity, sdl2.ext.Sprite
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
        coll = s_left < right and s_right > left and s_top < bottom and s_bottom > top

        if coll:
            coll = False
            # Calculate Collision Rect:
            x1 = max(left,s_left)
            y1 = max(top,s_top)
            x2 = min(right,s_right)
            y2 = min(bottom,s_bottom)
            w = x2 - x1
            h = y2 - y1
            # Calculate screen-to-sprite offsets:
            eox = x1-left if x1 > left else left-x1         # x pixel offset into enemy sprite bitmap
            sox = x1-s_left if x1 > s_left else s_left-x1   # x pixel offset into salmon sprite bitmap
            eoy = y1-top if y1 > top else top-y1            # y pixel offset into enemy sprite bitmap
            soy = y1-s_top if y1 > s_top else s_top-y1      # y pixel offset into salmon sprite bitmap

            # Pixel Perfect Collision:
            x=0
            y=0
            sprite_pix = sdl2.ext.PixelView(sprite)
            salmon_pix = sdl2.ext.PixelView(self.salmon.sprite)
            while y < h:
                while x < w:
                    if sprite_pix[y+eoy][x+eox] != 0 and salmon_pix[y+soy][x+sox] != 0:
                        coll = True
                        break
                    x += 1
                y += 1
        return coll

    def _enemy_obstacle_overlap(self, item, obstacles):
        size, pos, sprite = item
        if sprite.depth != 3 or ((sprite.area[2]-sprite.area[0]) * (sprite.area[3]-sprite.area[1]) in [1628,2450]):
            return (False, None)
        left, top, right, bottom = sprite.area
        coll = False
        o_type = None

        for obstacle in obstacles:
            o_type = 'rock' if (obstacle[2]-obstacle[0]) * (obstacle[3]-obstacle[1]) == 1628 else 'whirlpool'
            o_left, o_top, o_right, o_bottom = obstacle
            coll = o_left < right and o_right > left and o_top < bottom and o_bottom > top
            if coll:
                break
        return coll, o_type

    def process(self, world, componentsets):
        # During game play, check for sprite collisions:
        if globals.death == False and globals.home_lock == False:
            comp_list = [comp for comp in componentsets]
            collitems = [comp for comp in comp_list if self._overlap(comp)]
            obstacles = [comp[2].area for comp in comp_list if
                (comp[2].area[2]-comp[2].area[0]) * (comp[2].area[3]-comp[2].area[1]) in [1628,2450]]

            # Determine enemy-obstacle collisions:
            enemies_on_obstacles = []
            for comp in comp_list:
                coll, o_type = self._enemy_obstacle_overlap(comp, obstacles)
                if coll:
                    enemies_on_obstacles.append((comp,o_type))

            if collitems:
                size, pos, sprite = collitems[0]
                if self.salmon.size.size > size.size:
                    entity = world.get_entities(sprite)[0]
                    entity.delete()                 # Delete eaten enemy
                    self.salmon.meals.eat()         # Increment meals counter
                    self.salmon.energy.boost(20)    # Boost salmon energy
                    music.play_sample('Bite.wav')
                    globals.clear_meals = False
                    if self.salmon.meals.meals == 5:
                        self.salmon.meals.reset()
                        self.salmon.size.increment()
                        globals.grow_salmon = True
                        globals.clear_meals = True
                else:
                    # Whirlpool collision:
                    if size.size == 50:
                        self.salmon.velocity.vy = random.randint(-30,30)
                        self.salmon.velocity.vx = random.randint(-30,30)
                    else:
                        music.play_sample('SplitSplat.wav')
                        music.kill()
                        globals.death = True

            if enemies_on_obstacles:
                for enemy in enemies_on_obstacles:
                    if enemy[1] == 'rock':
                        entity = world.get_entities(enemy[0][2])[0]
                        entity.delete()
                    elif enemy[1] == 'whirlpool':
                        enemy[0][1].vx = random.randint(-30,30)
                        enemy[0][1].vy = random.randint(1,30)
