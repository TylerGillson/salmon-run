import os
import sdl2.sdlmixer

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources")

def play_music():
    mixformat = sdl2.sdlmixer.MIX_DEFAULT_FORMAT  # sets up the format for OpenAudio
    musicfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/sounds","Chiptune.wav")
    music_init = sdl2.sdlmixer.MIX_INIT_MP3
    sdl2.sdlmixer.Mix_Init(music_init)
    sdl2.sdlmixer.Mix_OpenAudio(22050, mixformat, 2, 4096)
    loadmusic = sdl2.sdlmixer.Mix_LoadMUS(musicfile.encode("utf-8"))
    sdl2.sdlmixer.Mix_PlayMusic(loadmusic, -1)
