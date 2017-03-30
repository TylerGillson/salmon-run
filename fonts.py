import sdl2.ext
import sdl2.sdlttf

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources/fonts")

def make_font(font_type):
    if font_type == 'Score':
        font = sdl2.ext.font.FontManager(RESOURCES.get_path('PixelGameFont.ttf'),size=20,color=(255,255,0))
    elif font_type == 'Title':
        font = sdl2.ext.font.FontManager(RESOURCES.get_path('PixelGameFont.ttf'),size=100,color=(255,100,148))
    elif font_type == 'Play':
        font = sdl2.ext.font.FontManager(RESOURCES.get_path('PixelGameFont.ttf'),size=50,color=(255,100,148))
    elif font_type == 'GameOver':
        font = sdl2.ext.font.FontManager(RESOURCES.get_path('PixelGameFont.ttf'),size=100,color=(0,0,0))
    elif font_type == 'GameOverScore':
        font = sdl2.ext.font.FontManager(RESOURCES.get_path('PixelGameFont.ttf'),size=30,color=(0,0,0))
    return font
