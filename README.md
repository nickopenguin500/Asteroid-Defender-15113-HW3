

Model: Gemini Pro
Important Prompts: 
(Many prompts prior about brainstorming and logistics)
1. "I need a Python script using requests to fetch data from the NASA NeoWs (Near Earth Object) API.

Load API key from .env.

Fetch the 'Feed' for 'today'.

Parse the JSON to return a list of dictionaries. Each dictionary must contain:

id (string)

name (string)

diameter (average of min/max estimated diameter in meters)

velocity (kilometers per hour, as a float)

is_hazardous (boolean)

Handle errors (e.g., if the API fails, return a hardcoded 'dummy' list so I can test the game offline)." (Given by and fed to Gemini)

2. "I have a file named asteroid_data.py with a function fetch_asteroid_data() that returns a list of asteroid dictionaries.

Now, write a main.py script using pygame to create the game.

Requirements:

Setup: Initialize Pygame with an 800x600 window. Set a caption 'NASA Asteroid Defender'.

Data: Call fetch_asteroid_data() at the start to get the enemy list.

The Player: A simple white triangle at the bottom center. It moves Left/Right with Arrow keys. Spacebar shoots a yellow bullet upwards.

The Enemies (Asteroids):

Create a class Asteroid.

Spawn them at random X positions at the top, falling down.

Size: Use the diameter from the data. Map it: 10m -> 10px radius, 100m -> 50px radius (clamp it so they aren't too huge).

Speed: Use velocity from the data. Map it: 20,000kph -> 2px/frame, 80,000kph -> 7px/frame.

Color: Draw them as Grey circles. If is_hazardous is True, draw them Red.

Text: (Optional) If possible, render the asteroid's name in small text above it.

Gameplay:

If a bullet hits an asteroid: Remove asteroid, add +100 score, play a standard beep sound (if easy) or just print 'Hit!' to console.

If an asteroid hits the player: Game Over.

If an asteroid goes off screen: Respawn it at the top (infinite loop of the same daily asteroids).

UI: Display the Score in the top left.

Please write the complete, run-able code." (Given and fed to Gemini)

(Accidentally pushed my api key, so I deleted and remade the entire repo)

3. ok can you redo the game concept tho, keep all the asteroids speeds relative, but far slower. make the goal to reach the end of a topdown scrolling game, far less ammo, but keep ammo there that can break 1 asteroid. this game should be more about dodging asteroids than breaking them.
