import random
# Custom Modules:
import sdl2.ext
import sprite_classes
import globals

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = sprite_classes.Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.salmon = None

    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            # Reset riverbanks:
            if sprite.x < 90 and (sprite.area[2]-sprite.area[0] > 50):
                if sprite.y > 0:
                    sprite.y = -550
                sprite.y += -self.salmon.velocity.vy if self.salmon.velocity.vy < 0 else 0
                continue
            # Have trees track upwards salmon velocity:
            if sprite.x < 90 or sprite.x > 710:
                sprite.y += -self.salmon.velocity.vy if self.salmon.velocity.vy < 0 else 0
                continue
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

class TrackingAIController(sdl2.ext.Applicator):
    def __init__(self, miny, maxy):
        super(TrackingAIController, self).__init__()
        self.componenttypes = sprite_classes.PlayerData, sprite_classes.Velocity, sdl2.ext.Sprite
        self.miny = miny
        self.maxy = maxy
        self.target = None

    def process(self, world, componentsets):
        for pdata, vel, sprite in componentsets:
            if not pdata.ai:        # Enemies with AI track salmon in x-axis
                continue
            if sprite.depth != 3:
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
            elif s_centerx > centerx:       # salmon is to the right
                if vel.vy > 6:
                    vel.vx = 2
                else:
                    vel.vx = 4
