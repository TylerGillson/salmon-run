import sdl2.ext
import sdl2.sdlttf

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources/fonts")

def make_font():
    font = sdl2.ext.font.FontManager(RESOURCES.get_path('PixelGameFont.ttf'),size=20,color=(255,255,0))
    return font
