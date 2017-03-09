import sdl2.ext
# Custom Modules:
import sprite_classes
import globals

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    # Manage sprite rendering according to game state (state of globals):
    def process(self, world, components):
        # Game Over Rendering:
        if globals.death == True:
            # Render everyhing except player and enemy sprites:
            valid = [sprite for sprite in components if sprite.depth not in [2,3]]
            # Delete all player and enemy sprites:
            delete = set(components) - set(valid)
            self.render(sorted(valid, key=self._sortfunc))
            for sprite in delete:
                entity = world.get_entities(sprite)[0]
                entity.delete()
        # Game Play Rendering:
        elif globals.home_lock == False:
            # Render everything except enemies that have reached the bottom of the screen:
            valid = [sprite for sprite in components if (sprite.depth==3 and sprite.area[3]==650)==False]
            self.render(sorted(valid, key=self._sortfunc))
            # Delete the score sprite:
            hud_sprites = [sprite for sprite in components if sprite.depth==5]
            for sprite in hud_sprites:
                if sprite.depth==5 and sprite.x==84:
                    entity = world.get_entities(sprite)[0]
                    entity.delete()
            # Delete enemy sprites that have reached the bottom from the world:
            delete = set(components) - set(valid)
            for sprite in delete:
                entity = world.get_entities(sprite)[0]
                entity.delete()
        # Home Screen Rendering:
        else:
            # Simply render everything according to z-layering depths:
            self.render(sorted(components, key=self._sortfunc))
