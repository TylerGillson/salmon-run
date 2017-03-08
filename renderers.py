import sdl2.ext
# Custom Modules:
import sprite_classes
import globals

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    # Manage sprite rendering according to state of globals:
    def process(self, world, components):
        # On death, render everyhing except player and enemy sprites,
        # then delete all player and enemy sprites:
        if globals.death == True:
            valid = [sprite for sprite in components if sprite.depth not in [2,3]]
            delete = set(components) - set(valid)
            self.render(sorted(valid, key=self._sortfunc))
            for sprite in delete:
                entity = world.get_entities(sprite)[0]
                entity.delete()
        # During game play, render everything except enemies that have reached the,
        # bottom of the screen, then delete said enemy sprites from the world.
        elif globals.home_lock == False:
            valid = [sprite for sprite in components if (sprite.depth==3 and sprite.area[3]==650)==False]
            delete = set(components) - set(valid)
            self.render(sorted(valid, key=self._sortfunc))
            for sprite in delete:
                entity = world.get_entities(sprite)[0]
                entity.delete()
        # While on the home screen, simply render everything:
        else:
            self.render(sorted(components, key=self._sortfunc))
