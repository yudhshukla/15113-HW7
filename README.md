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

Challenges:
- Figuring out what was limiting the smooth movement 

To do next:
- Add more maps, easy/medium/hard game modes, perhaps dynamic and moveable maps where the user can explore
