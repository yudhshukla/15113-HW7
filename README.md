Recreation of Pac-Man

Requirements: (at least for mac)
pip3 install pygame

Known issues / things to add:
The ghost AIs aren't very smart
Player lives
Player movement needs to be limited (you can currently just run into the wall to stop moving)
Closing the game is sometimes buggy

Update: 
- Changed movement to keep player aligned with the corners by modifying player speed and changed collision logic to stop momentum when hitting walls.
- Upgraded the single-map string into a LEVELS list array, as well as restarting logic
- Improved ghost AI logic by changing multipliers to change how the different ghosts catch you
- Updated ghost movements by modifying collision logic
- Added a map

Challenges:
- Figuring out what was limiting the smooth movement, tried several solutions that introduced more bugs/didn't fix the problem at first
- Understanding how to improve the ghost AI without making them all do the same thing

To do next:
- Add more maps, easy/medium/hard game modes, perhaps dynamic and moveable maps where the user can explore
