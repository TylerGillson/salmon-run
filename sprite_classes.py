import sdl2.ext

class Inert(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
    def setPos(self, x,y):
        self.sprite.position = x, y
    def setDepth(self, depth):
        self.sprite.depth = depth

class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx, posy, size, meals, velocity, energy):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity(velocity)
        self.size = Size(size)
        self.meals = Meals(meals)
        self.energy = Energy(energy)
    def setDepth(self, depth):
        self.sprite.depth = depth

class PlayerData(object):
    def __init__(self, ai):
        super(PlayerData, self).__init__()
        self.ai = ai

class Enemy(sdl2.ext.Entity):
    def __init__(self, world, sprite, velocity, posx=0, posy=0, ai=False):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity(velocity)
        self.playerdata = PlayerData(ai)
        self.size = Size()
    def setDepth(self, depth):
        self.sprite.depth = depth

class Size(object):
    def __init__(self, size=0):
        super(Size, self).__init__()
        self.size = size
    def increment(self):
        if self.size < 16:
            self.size += 1
    def decrement(self):
        self.size -= 1

class Meals(object):
    def __init__(self, meals=0):
        super(Meals, self).__init__()
        self.meals = meals
    def eat(self):
        self.meals += 1
    def reset(self):
        self.meals = 0

class Energy(object):
    def __init__(self, energy=0):
        super(Energy, self).__init__()
        self.energy = energy
    def boost(self, amount):
        self.energy += amount

class Velocity(object):
    def __init__(self, velocity):
        super(Velocity, self).__init__()
        self.vx = velocity[0]
        self.vy = velocity[1]
    def get_velocity(self):
        return (self.vx, self.vy)
