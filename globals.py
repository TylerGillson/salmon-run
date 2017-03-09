# Declare globals:
running = True   # boolean for governing main event loop.
death = False    # death is used as a trigger to indicate that the player has
                 # collided with either an enemy or an obstacle.
home_lock = True # home_lock makes world.process() safe when rendering the home screen.
                 # It prevents certain inputs from crashing the game by attempting to influence sprites that do not currently exist.
clear_meals = False
grow_salmon = False
