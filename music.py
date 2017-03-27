import os
import sdl2.sdlmixer
from sdl2.ext.compat import byteify

# Create a resource container:
RESOURCES = sdl2.ext.Resources(__file__, "resources/sounds")

def init_audio():
    mix_format = sdl2.sdlmixer.MIX_DEFAULT_FORMAT
    sdl2.sdlmixer.Mix_OpenAudio(22050, mix_format, 2, 4096)

def play_music(filepath, duration):
    music_file = RESOURCES.get_path(filepath)
    music = sdl2.sdlmixer.Mix_LoadMUS(music_file.encode("utf-8"))
    sdl2.sdlmixer.Mix_PlayMusic(music, duration)

def play_sample(filepath, quiet=False):
    sample_file = RESOURCES.get_path(filepath)
    sample = sdl2.sdlmixer.Mix_LoadWAV(byteify(sample_file, "utf-8"))
    if quiet:
        channel = sdl2.sdlmixer.Mix_PlayChannel(2, sample, -1)
        sdl2.sdlmixer.Mix_Volume(2,5)
    else:
        channel = sdl2.sdlmixer.Mix_PlayChannel(1, sample, 0)

def kill():
    sdl2.sdlmixer.Mix_HaltMusic()
