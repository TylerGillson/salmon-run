# Declare globals:
running = True          # running governs the main event loop
pause = False           # pause, unsurprisingly, pauses the main event loop
death = False           # death is used as a trigger to indicate that the player has died
home_lock = True        # home_lock locks rendering on the home screen
game_over_lock = False  # game_over_lock locks rendering on the game over screen so the user can view top scores
grow_salmon = False     # grow_salmon indicates that the salmon has eaten five meals and must grow
clear_meals = False     # clear_meals indicates that the salmon has grown and the meal sprites must be reset
evil_fish = False
