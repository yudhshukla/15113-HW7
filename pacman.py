import pygame
import sys
import os
import random

# --- 1. CONSTANTS ---
TILE_SIZE = 32
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 81)
DARK_BLUE = (0, 0, 139)

# --- 2. LEVEL DESIGN ---
# Easily editable grid. W=Wall, .=Pellet, P=Player, G=Ghost, Space=Empty, O=Powerup
# --- 2. LEVEL DESIGN ---
# We've wrapped your original map into a list, and added a second map layout.
# --- 2. LEVEL DESIGN ---
LEVELS = [
    [ # Level 1 (Your original map)
        "WWWWWWWWWWWWWWWWWWW",
        "W.O.............O.W",
        "W.WW.WWW.W.WWW.WW.W",
        "W.WW.WWW.W.WWW.WW.W",
        "W.................W",
        "W.WW.W.WWWWW.W.WW.W",
        "W....W...W...W....W",
        "WWWW.WWW W WWW.WWWW",
        "   W.W       W.W   ",
        "WWWW.W WW-WW W.WWWW", 
        "    .  W1234 W  .  ", 
        "WWWW.W WWWWW W.WWWW",
        "   W.W       W.W   ",
        "WWWW.W WWWWW W.WWWW",
        "W........W........W",
        "W.WW.WWW.W.WWW.WW.W",
        "W..W.O...P...O.W..W",
        "WW.W.W.WWWWW.W.W.WW",
        "W....W...W...W....W",
        "WWWWWWWWWWWWWWWWWWW"
    ],
    [ # Level 2 (Expanded to 20 rows for full screen!)
        "WWWWWWWWWWWWWWWWWWW",
        "W........O........W",
        "W.WWWWW.WWW.WWWWW.W",
        "W.WWWWW.WWW.WWWWW.W",
        "W.................W",
        "WWWW.WWW W WWW.WWWW",
        "   W.W       W.W   ",
        "WWWW.W WW-WW W.WWWW", 
        "    .  W1234 W  .  ", 
        "WWWW.W WWWWW W.WWWW",
        "   W.W       W.W   ",
        "WWWW.W WWWWW W.WWWW",
        "W.................W",
        "W.WWWWW.WWW.WWWWW.W",
        "W........P........W",
        "W.WW.WWWWWWWWW.WW.W",
        "W..W.....W.....W..W",
        "WW.WWWWW.W.WWWWW.WW",
        "W.O.............O.W",
        "WWWWWWWWWWWWWWWWWWW"
    ]
]

WIDTH = len(LEVELS[0][0]) * TILE_SIZE
HEIGHT = len(LEVELS[0]) * TILE_SIZE

# --- 3. PLAYER CLASS ---
class Player:
    def __init__(self, x, y):
        # THE FIX: Make the hitbox EXACTLY 32x32 to match the corridors.
        # Your Game class passes in x+2, y+2, so we subtract 2 to snap it perfectly back to the grid.
        self.rect = pygame.Rect(x - 2, y - 2, TILE_SIZE, TILE_SIZE)
        self.speed = 2 
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

    def handle_keys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.next_dx = -self.speed
                self.next_dy = 0
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.next_dx = self.speed
                self.next_dy = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.next_dx = 0
                self.next_dy = -self.speed
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.next_dx = 0
                self.next_dy = self.speed

    def update(self, walls):
        # 1. Input Buffering & Turning
        # Because the rect is exactly 32x32, a turn will ONLY be valid (no collisions) 
        # when perfectly aligned with an intersecting 32x32 corridor.
        projected_rect = self.rect.move(self.next_dx, self.next_dy)
        if not self.check_collision(projected_rect, walls):
            self.dx, self.dy = self.next_dx, self.next_dy

        # 2. Move horizontally
        self.rect.x += self.dx
        if self.check_collision(self.rect, walls):
            self.rect.x -= self.dx
            self.dx = 0 

        # 3. Move vertically
        self.rect.y += self.dy
        if self.check_collision(self.rect, walls):
            self.rect.y -= self.dy
            self.dy = 0 

        # 4. Screen Wrap 
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0
            
    def check_collision(self, rect, walls):
        # Checks if a given rectangle overlaps with any wall rectangle
        for wall in walls:
            if rect.colliderect(wall):
                return True
        return False

    def draw(self, surface):
        # We still draw the yellow circle slightly smaller (-2 radius)
        # so it visually looks nice and doesn't visually touch the walls!
        pygame.draw.circle(surface, YELLOW, self.rect.center, (TILE_SIZE // 2) - 2)

# --- 4. GHOST CLASS ---
class Ghost:
    def __init__(self, x, y, ghost_type):
        # THE FIX: Snap the mathematical hitbox perfectly to the 32x32 grid
        self.rect = pygame.Rect(x - 2, y - 2, TILE_SIZE, TILE_SIZE)
        self.speed = 2 
        self.ghost_type = ghost_type
        
        # Save starting coordinates for respawning
        self.start_x = self.rect.x
        self.start_y = self.rect.y
        
        if self.ghost_type == 1: self.color = RED        
        elif self.ghost_type == 2: self.color = PINK     
        elif self.ghost_type == 3: self.color = CYAN     
        else: self.color = ORANGE                        

        self.directions = [(self.speed, 0), (-self.speed, 0), (0, self.speed), (0, -self.speed)]
        self.dx, self.dy = self.speed, 0 

    def respawn(self):
        # Send ghost back to its starting position
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.dx, self.dy = self.speed, 0

    def get_target(self, player, is_frightened):
        if is_frightened:
            return random.randint(0, WIDTH), random.randint(0, HEIGHT)

        target_x = player.rect.x
        target_y = player.rect.y

        if self.ghost_type == 1:
            pass 
        elif self.ghost_type == 2:
            target_x += player.dx * 64
            target_y += player.dy * 64
        elif self.ghost_type == 3:
            target_x -= player.dx * 32
            target_y -= player.dy * 32
        else:
            dist = abs(self.rect.x - player.rect.x) + abs(self.rect.y - player.rect.y)
            if dist < TILE_SIZE * 5:
                target_x, target_y = 0, HEIGHT 

        target_x = max(0, min(WIDTH - TILE_SIZE, target_x))
        target_y = max(0, min(HEIGHT - TILE_SIZE, target_y))

        return target_x, target_y

    def update(self, walls, player, is_frightened):
        self.rect.x += self.dx
        self.rect.y += self.dy

        hit_wall = self.check_collision(self.rect, walls)
        
        # CLEANER MATH: Because the rect is exactly 32x32, we don't need the "- 2" 
        # offset anymore. Intersections are perfect multiples of the TILE_SIZE!
        at_intersection = self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0

        if hit_wall or at_intersection:
            if hit_wall:
                self.rect.x -= self.dx
                self.rect.y -= self.dy

            target_x, target_y = self.get_target(player, is_frightened)
            valid_directions = []

            for test_dx, test_dy in self.directions:
                if (test_dx, test_dy) == (-self.dx, -self.dy) and not hit_wall:
                    continue

                test_rect = self.rect.move(test_dx, test_dy)
                if not self.check_collision(test_rect, walls):
                    proj_x = self.rect.x + test_dx * (TILE_SIZE // self.speed)
                    proj_y = self.rect.y + test_dy * (TILE_SIZE // self.speed)
                    
                    distance = abs(proj_x - target_x) + abs(proj_y - target_y)
                    valid_directions.append((distance, test_dx, test_dy))

            if valid_directions:
                valid_directions.sort(key=lambda item: item[0])
                best_move = valid_directions[0]
                self.dx, self.dy = best_move[1], best_move[2]
            elif hit_wall:
                self.dx, self.dy = -self.dx, -self.dy

    def check_collision(self, rect, walls):
        for wall in walls:
            if rect.colliderect(wall): return True
        return False

    def draw(self, surface, is_frightened):
        current_color = DARK_BLUE if is_frightened else self.color
        
        # THE VISUAL FIX: We draw the colored square slightly smaller (24x24) 
        # and offset it by 4 pixels so it sits dead center in the 32x32 invisible hitbox.
        draw_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
        pygame.draw.rect(surface, current_color, draw_rect, border_radius=8)

# --- 5. GAME MANAGER ---
class Game:
    # Inside the Game class...

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man Foundation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 36)
        
        self.running = True
        self.state = "PLAYING" 
        
        # NEW: Track the player's current level index
        self.current_level_idx = 1
        self.score = 0 # Move score here so it doesn't reset on new levels
        
        self.reset_game() 

    def reset_game(self):
        # Clears out all entities so we can spawn them fresh for the new level
        self.walls = []
        self.gates = [] 
        self.pellets = []
        self.power_pellets = [] 
        self.ghosts = []
        self.state = "PLAYING"
        
        self.frightened_timer = 0          
        self.frightened_duration = FPS * 7 
        
        self.load_level()

    def load_level(self):
        # NEW: Fetch the specific map layout for our current level
        current_map = LEVELS[self.current_level_idx]
        
        # Parse the map grid just like before
        for row_idx, row in enumerate(current_map):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                # ... (Keep all the if/elif conditions exactly the same here) ...
                if char == 'W':
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == '-': # NEW: Parse the gate
                    self.gates.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == '.':
                    pellet_rect = pygame.Rect(x + TILE_SIZE//2 - 2, y + TILE_SIZE//2 - 2, 4, 4)
                    self.pellets.append(pellet_rect)
                elif char == 'O': # Add Power Pellet parsing
                    power_rect = pygame.Rect(x + TILE_SIZE//2 - 6, y + TILE_SIZE//2 - 6, 12, 12)
                    self.power_pellets.append(power_rect)
                elif char == 'P':
                    self.player = Player(x + 2, y + 2)
                elif char in ['1', '2', '3', '4']:
                    self.ghosts.append(Ghost(x + 2, y + 2, int(char)))

    def run(self):
        while self.running:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.state == "PLAYING" and self.player:
                    self.player.handle_keys(event)
                elif self.state == "GAME_OVER" and event.type == pygame.KEYDOWN:
                    self.reset_game()

            # NEW: If the user hit the X, break the loop immediately!
            # This skips display.flip() and goes straight to the exit code.
            if not self.running:
                break

            # 2. Logic Updates
            if self.state == "PLAYING":
                if self.frightened_timer > 0:
                    self.frightened_timer -= 1

                if self.player:
                    self.player.update(self.walls + self.gates) 
                    self.check_pellet_collisions()
                    self.check_ghost_collisions()

                for ghost in self.ghosts:
                    is_scared = self.frightened_timer > 0
                    ghost.update(self.walls, self.player, is_scared) 

            # 3. Rendering
            self.screen.fill(BLACK)
            self.draw_environment()
            
            if self.player:
                self.player.draw(self.screen)
            for ghost in self.ghosts:
                is_scared = self.frightened_timer > 0
                ghost.draw(self.screen, is_scared)

            if self.state == "GAME_OVER":
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        # 4. Clean Exit - ONLY place these should exist!
        pygame.quit()
        os._exit(0)

    def check_pellet_collisions(self):
        # Standard Pellets
        for i in range(len(self.pellets) - 1, -1, -1):
            if self.player.rect.colliderect(self.pellets[i]):
                del self.pellets[i]
                self.score += 10
                pygame.display.set_caption(f"Score: {self.score}")
                
        # Power Pellets
        for i in range(len(self.power_pellets) - 1, -1, -1):
            if self.player.rect.colliderect(self.power_pellets[i]):
                del self.power_pellets[i]
                self.score += 50
                self.frightened_timer = self.frightened_duration # Start/Reset the timer!
                pygame.display.set_caption(f"Score: {self.score}")
        
        if len(self.pellets) == 0 and len(self.power_pellets) == 0:
            self.current_level_idx += 1 # Advance the level index
            
            # Check if we beat the last level
            if self.current_level_idx >= len(LEVELS):
                self.state = "VICTORY" # You'll need to draw a victory screen similar to game over!
            else:
                self.reset_game() # Automatically builds the next map!

    def check_ghost_collisions(self):
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if self.frightened_timer > 0:
                    self.score += 200
                    ghost.respawn()
                    pygame.display.set_caption(f"Score: {self.score}")
                else:
                    # Just change the state! Do NOT call pygame.quit() here.
                    self.state = "GAME_OVER"

    def draw_environment(self):
        for wall in self.walls:
            pygame.draw.rect(self.screen, BLUE, wall, 2)
            
        # NEW: Draw the one-way gate
        for gate in self.gates:
            # Draws a thin pink line across the middle of the tile
            pygame.draw.rect(self.screen, PINK, (gate.x, gate.y + TILE_SIZE // 2 - 2, TILE_SIZE, 4))
            
        for pellet in self.pellets:
            pygame.draw.rect(self.screen, WHITE, pellet)
        for power in self.power_pellets:
            radius = 6 if self.frightened_timer % 30 < 15 else 8
            pygame.draw.circle(self.screen, WHITE, power.center, radius)
            
    def draw_game_over(self):
        # Creates a semi-transparent black overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw the text
        text = self.font.render("GAME OVER - Press any key to restart", True, RED)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        self.screen.blit(text, text_rect)

# --- 6. EXECUTION ---
if __name__ == "__main__":
    game = Game()
    game.run()