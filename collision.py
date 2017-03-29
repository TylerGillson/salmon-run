import sdl2.ext
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

        coll = s_left < right and s_right > left and \
               s_top < bottom and s_bottom > top

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
            eox = x1-left if x1 > left else 0       # enemy sprite x
            sox = x1-s_left if x1 > s_left else 0   # salmon sprite x
            eoy = y1-top if y1 > top else 0         # enemy sprite y
            soy = y1-s_top if y1 > s_top else 0     # salmon sprite y

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

    def process(self, world, componentsets):
        # During game play, check for sprite collisions:
        if globals.death == False and globals.home_lock == False:
            collitems = [comp for comp in componentsets if self._overlap(comp)]
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
                    music.play_sample('SplitSplat.wav')
                    music.kill()
                    globals.death = True
