import sdl2.ext
# Custom Modules:
import sprite_classes
import globals

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def delete(self, object, world):
        entity = world.get_entities(object)[0]
        entity.delete()

    # Manage sprite rendering according to game state (state of globals):
    def process(self, world, components):
        # Game Over Rendering:
        if globals.death == True:
            # Render everyhing except player and enemy sprites:
            valid = [sprite for sprite in components if sprite.depth not in [1,2,3,5]]
            # Delete all player and enemy sprites:
            delete = set(components) - set(valid)
            self.render(sorted(valid, key=self._sortfunc))
            for sprite in delete:
                self.delete(sprite, world)

        # Game Play Rendering:
        elif globals.home_lock == False:
            # Render everything except enemies that have reached the bottom of the screen:
            valid = [sprite for sprite in components if
                (sprite.depth==3 and (sprite.area[3]==650 or sprite.area[3]>650))==False]
            self.render(sorted(valid, key=self._sortfunc))
            # Delete the score sprite on each process loop:
            hud_sprites = [sprite for sprite in components if sprite.depth==5]
            for sprite in hud_sprites:
                if sprite.x==84:
                    self.delete(sprite, world)
                if globals.clear_meals == True:
                    if sprite.x not in [84,623,625]:
                        self.delete(sprite, world)
            # Delete enemy sprites that have reached the bottom from the world:
            delete = set(components) - set(valid)
            for sprite in delete:
                self.delete(sprite, world)
            # Delete the energy bar:
            energy_bar = [sprite for sprite in components if sprite.depth == 5 and sprite.x==625]
            for sprite in energy_bar:
                self.delete(sprite, world)
            # Delete pause bars:
            pause_bars = [sprite for sprite in components if sprite.depth == 5 and (sprite.x,sprite.y) in [(300,300),(370,300)]]
            if pause_bars:
                for bar in pause_bars:
                    self.delete(bar, world)

        # Home Screen Rendering:
        else:
            # Simply render everything according to z-layering depths:
            self.render(sorted(components, key=self._sortfunc))
