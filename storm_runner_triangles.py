import pygame
import random
import sys
import os
import math
from pygame import mixer

# Initialize pygame
pygame.init()
#mixer.init()

# Game constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 60
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Storm Runner - Triangles & Circles")
clock = pygame.time.Clock()

# Storm progress bar
class StormProgressBar:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = 0  # 0 to 100
        self.danger_zone = 85  # Changed from 80 to 85 for more warning time
        
    def update(self, player_speed, storm_speed):
        # Calculate progress based on player vs storm speed
        speed_diff = storm_speed - player_speed
        
        # Increase progress if storm is faster, decrease if player is faster
        if speed_diff > 0:
            self.progress += speed_diff * 0.08  # Changed from 0.1 to 0.08 for slower storm progress
        else:
            self.progress = max(0, self.progress + speed_diff * 0.06)  # Changed from 0.05 to 0.06 for faster recovery
            
        # Cap progress at 100
        self.progress = min(100, self.progress)
        
    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        
        # Draw progress
        if self.progress > 0:
            fill_width = int((self.progress / 100) * self.rect.width)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            
            # Color changes based on progress
            if self.progress < 50:
                color = GREEN
            elif self.progress < self.danger_zone:
                color = YELLOW
            else:
                color = RED
                
            pygame.draw.rect(surface, color, fill_rect)
            
        # Draw border
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        # Draw "STORM" label
        font = pygame.font.SysFont(None, 24)
        text = font.render("STORM", True, WHITE)
        text_rect = text.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text, text_rect)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (100, SCREEN_HEIGHT - GROUND_HEIGHT)
        self.velocity_y = 0
        self.jumping = False
        self.double_jump_available = True
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        self.lives = 3
        self.coins = 0
        
    def update(self):
        # Gravity
        self.velocity_y += 0.8
        self.rect.y += self.velocity_y
        
        # Check if on ground
        if self.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
            self.velocity_y = 0
            self.jumping = False
            self.double_jump_available = True
            
        # Invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def jump(self):
        if not self.jumping:
            self.velocity_y = -18  # Changed from -15 to -18 for higher jumps
            self.jumping = True
        elif self.double_jump_available:
            self.velocity_y = -16  # Changed from -13 to -16 for higher double jumps
            self.double_jump_available = False
            
    def make_invincible(self, duration=240):  # Changed from 180 to 240 for longer invincibility
        self.invincible = True
        self.invincible_timer = duration
        
    def lose_life(self):
        if not self.invincible:
            self.lives -= 1
            self.make_invincible(180)  # Changed from 120 to 180 for longer invincibility after hit
            return self.lives <= 0
        return False

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed, game_speed, obstacle_type="standard"):
        super().__init__()
        self.obstacle_type = obstacle_type
        self.speed = speed + game_speed
        
        if obstacle_type == "standard":
            # Create a triangular obstacle
            height = random.randint(30, 60)
            width = random.randint(30, 50)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Draw a triangle
            pygame.draw.polygon(self.image, RED, [
                (width // 2, 0),  # Top point
                (0, height),      # Bottom left
                (width, height)   # Bottom right
            ])
            
            self.rect = self.image.get_rect()
            self.rect.bottomleft = (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT)
        
        elif obstacle_type == "flying":
            # Create a flying triangular obstacle
            height = random.randint(20, 40)
            width = random.randint(40, 60)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Draw a triangle pointing right (like an arrow)
            pygame.draw.polygon(self.image, ORANGE, [
                (0, 0),           # Top left
                (0, height),      # Bottom left
                (width, height//2) # Right middle
            ])
            
            self.rect = self.image.get_rect()
            height_offset = random.randint(50, 150)
            self.rect.bottomleft = (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - height_offset)
            self.y_movement = random.choice([-1, 1])
            self.y_range = random.randint(10, 30)
            self.original_y = self.rect.y
        
        elif obstacle_type == "boulder":
            # Create a triangular boulder (pyramid)
            size = random.randint(40, 60)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw a triangle
            pygame.draw.polygon(self.image, PURPLE, [
                (size // 2, 0),   # Top point
                (0, size),        # Bottom left
                (size, size)      # Bottom right
            ])
            
            self.rect = self.image.get_rect()
            self.rect.bottomleft = (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT)
            self.rotation = 0
            self.rotation_speed = random.uniform(2, 5)
            self.original_image = self.image.copy()
        
    def update(self):
        self.rect.x -= self.speed
        
        # Special movement patterns based on obstacle type
        if self.obstacle_type == "flying":
            # Oscillating up and down movement
            self.rect.y = self.original_y + self.y_range * math.sin(pygame.time.get_ticks() * 0.005)
        
        elif self.obstacle_type == "boulder":
            # Rotating triangle
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation = 0
                
            # Rotate the image
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            self.rect = self.image.get_rect(center=old_center)
        
        if self.rect.right < 0:
            self.kill()

# PowerUp class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed, game_speed):
        super().__init__()
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - random.randint(0, 100))
        self.speed = speed + game_speed
        self.type = random.choice(['invincibility', 'score_boost', 'extra_life'])
        
        # Draw a circular powerup with different colors based on type
        if self.type == 'invincibility':
            color = (0, 200, 255)  # Light blue for invincibility
        elif self.type == 'score_boost':
            color = (255, 215, 0)  # Gold for score boost
        else:  # extra_life
            color = (255, 100, 100)  # Light red for extra life
            
        # Draw the circular powerup
        pygame.draw.circle(self.image, color, (12, 12), 12)
        
        # Add a symbol inside based on type
        if self.type == 'invincibility':
            # Shield symbol
            pygame.draw.arc(self.image, WHITE, (5, 5, 15, 15), 0, math.pi, 2)
            pygame.draw.line(self.image, WHITE, (5, 12), (20, 12), 2)
        elif self.type == 'score_boost':
            # Plus symbol
            pygame.draw.line(self.image, WHITE, (12, 6), (12, 18), 2)
            pygame.draw.line(self.image, WHITE, (6, 12), (18, 12), 2)
        else:  # extra_life
            # Heart symbol (simplified)
            pygame.draw.circle(self.image, WHITE, (8, 8), 4)
            pygame.draw.circle(self.image, WHITE, (16, 8), 4)
            pygame.draw.polygon(self.image, WHITE, [(4, 10), (12, 20), (20, 10)])
        
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, speed, game_speed):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - random.randint(20, 120))
        self.speed = speed + game_speed
        self.value = 1
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        
        # Create a circular coin
        pygame.draw.circle(self.image, YELLOW, (7, 7), 7)
        
        # Draw a simple star/shine effect
        pygame.draw.line(self.image, WHITE, (7, 2), (7, 12), 1)
        pygame.draw.line(self.image, WHITE, (2, 7), (12, 7), 1)
        
    def update(self):
        self.rect.x -= self.speed
        
        # Simple animation - make the coin "pulse"
        self.animation_frame += self.animation_speed
        scale_factor = 1.0 + 0.1 * math.sin(self.animation_frame)
        
        # We don't actually scale the image here to keep it simple,
        # but in a full implementation we would resize the coin slightly
        
        if self.rect.right < 0:
            self.kill()

# Game class
class Game:
    def __init__(self):
        self.running = True
        self.game_state = "title"  # title, playing, game_over, paused
        self.score = 0
        self.high_score = 0
        self.coins_collected = 0
        self.high_coins = 0
        self.game_speed = 1
        self.obstacle_timer = 0
        self.powerup_timer = 0
        self.coin_timer = 0
        self.difficulty_level = 1
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.player.lives = 5  # Changed from 3 to 5 for more lives
        self.all_sprites.add(self.player)
        
        # Create storm progress bar
        self.storm_progress = StormProgressBar(SCREEN_WIDTH - 260, 10, 250, 25)
        
        # Heart image for lives
        self.heart_img = pygame.Surface((25, 25), pygame.SRCALPHA)
        # Draw a heart shape
        pygame.draw.polygon(self.heart_img, RED, [
            (12, 20), (5, 13), (5, 8), (8, 5), (12, 8),
            (16, 5), (19, 8), (19, 13)
        ])
        pygame.draw.circle(self.heart_img, RED, (8, 8), 4)
        pygame.draw.circle(self.heart_img, RED, (16, 8), 4)
        
        # Try to load background music
        try:
            mixer.music.load(os.path.join('assets', 'music', 'background.mp3'))
            mixer.music.set_volume(0.5)
            mixer.music.play(-1)  # Loop indefinitely
        except:
            print("Could not load background music")
    
    def reset_game(self):
        self.all_sprites.empty()
        self.obstacles.empty()
        self.powerups.empty()
        self.coins.empty()
        
        self.player = Player()
        self.player.lives = 5  # Changed from 3 to 5 for more lives
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.coins_collected = 0
        self.game_speed = 1
        self.obstacle_timer = 0
        self.powerup_timer = 0
        self.coin_timer = 0
        self.difficulty_level = 1
        self.game_state = "playing"
        
        # Reset storm progress
        self.storm_progress = StormProgressBar(SCREEN_WIDTH - 260, 10, 250, 25)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
                if self.game_state == "title":
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        
                elif self.game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_p:
                        self.game_state = "paused"
                        
                elif self.game_state == "paused":
                    if event.key == pygame.K_p:
                        self.game_state = "playing"
                        
                elif self.game_state == "game_over":
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
    
    def update(self):
        if self.game_state == "playing":
            # Update all sprites
            self.all_sprites.update()
            
            # Check for difficulty increase
            new_level = 1 + self.score // 700  # Changed from 500 to 700 for slower difficulty progression
            if new_level > self.difficulty_level:
                self.difficulty_level = new_level
                self.game_speed += 0.3  # Changed from 0.5 to 0.3 for smaller speed jumps
            else:
                # Smaller continuous speed increase
                self.game_speed += 0.0002  # Changed from 0.0005 to 0.0002 for slower progression
            
            # Update storm progress
            storm_speed = self.game_speed * 1.1  # Changed from 1.2 to 1.1 for slower storm
            player_speed = self.game_speed
            if not self.player.jumping:  # Player is slower when not jumping
                player_speed *= 0.9
            self.storm_progress.update(player_speed, storm_speed)
            
            # Check if storm caught up with player
            if self.storm_progress.progress >= 100:
                game_over = self.player.lose_life()
                if game_over:
                    self.game_state = "game_over"
                    if self.score > self.high_score:
                        self.high_score = self.score
                    if self.coins_collected > self.high_coins:
                        self.high_coins = self.coins_collected
                else:
                    # Reset storm progress after taking damage
                    self.storm_progress.progress = 40  # Changed from 50 to 40 for more recovery time
            
            # Spawn obstacles - rate increases with difficulty
            self.obstacle_timer += 1
            spawn_rate = max(15, 80 // (self.game_speed * (1 + (self.difficulty_level * 0.08))))  # Increased base rate for fewer obstacles
            if self.obstacle_timer >= spawn_rate:
                if random.random() < 0.6:  # Changed from 0.7 to 0.6 for fewer obstacles
                    # Choose obstacle type based on difficulty
                    obstacle_types = ["standard"]
                    if self.difficulty_level >= 2:
                        obstacle_types.append("flying")
                    if self.difficulty_level >= 3:
                        obstacle_types.append("boulder")
                    
                    obstacle_type = random.choice(obstacle_types)
                    obstacle = Obstacle(5, self.game_speed, obstacle_type)
                    self.obstacles.add(obstacle)
                    self.all_sprites.add(obstacle)
                self.obstacle_timer = 0
                
            # Spawn powerups (more frequently)
            self.powerup_timer += 1
            if self.powerup_timer >= 120 // self.game_speed:  # Changed from 180 to 120 for more powerups
                if random.random() < 0.4:  # Changed from 0.3 to 0.4 for more powerups
                    powerup = PowerUp(5, self.game_speed)
                    self.powerups.add(powerup)
                    self.all_sprites.add(powerup)
                self.powerup_timer = 0
                
            # Spawn coins
            self.coin_timer += 1
            if self.coin_timer >= 70 // self.game_speed:  # Changed from 90 to 70 for more coins
                if random.random() < 0.6:  # Changed from 0.5 to 0.6 for more coins
                    coin = Coin(5, self.game_speed)
                    self.coins.add(coin)
                    self.all_sprites.add(coin)
                self.coin_timer = 0
                
            # Check for collisions with obstacles
            if not self.player.invincible:
                hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
                if hits:
                    game_over = self.player.lose_life()
                    if game_over:
                        self.game_state = "game_over"
                        if self.score > self.high_score:
                            self.high_score = self.score
                        if self.coins_collected > self.high_coins:
                            self.high_coins = self.coins_collected
            
            # Check for collisions with powerups
            powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in powerup_hits:
                if powerup.type == 'invincibility':
                    self.player.make_invincible()
                elif powerup.type == 'score_boost':
                    self.score += 100
                elif powerup.type == 'extra_life' and self.player.lives < 5:
                    self.player.lives += 1
            
            # Check for collisions with coins
            coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
            for coin in coin_hits:
                self.coins_collected += coin.value
                self.score += 10 * coin.value
            
            # Update score
            self.score += 1
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw ground
        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        if self.game_state == "title":
            title_text = self.title_font.render("STORM RUNNER", True, BLACK)
            start_text = self.font.render("Press ENTER to start", True, BLACK)
            controls_text = self.font.render("SPACE to jump (double-jump available!)", True, BLACK)
            pause_text = self.font.render("P to pause", True, BLACK)
            
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//3))
            screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 + 90))
            
        elif self.game_state == "playing" or self.game_state == "paused":
            # Draw all sprites
            self.all_sprites.draw(screen)
            
            # Draw player with blinking effect when invincible
            if self.player.invincible and self.player.invincible_timer % 10 < 5:
                pass  # Skip drawing player every few frames for blinking effect
            else:
                screen.blit(self.player.image, self.player.rect)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, BLACK)
            screen.blit(score_text, (10, 10))
            
            # Draw coins
            coin_text = self.font.render(f"Coins: {self.coins_collected}", True, BLACK)
            screen.blit(coin_text, (10, 50))
            
            # Draw speed and level
            speed_text = self.small_font.render(f"Speed: {self.game_speed:.1f}x | Level: {self.difficulty_level}", True, BLACK)
            screen.blit(speed_text, (10, 90))
            
            # Draw storm progress bar
            self.storm_progress.draw(screen)
            
            # Draw lives (hearts)
            for i in range(self.player.lives):
                screen.blit(self.heart_img, (SCREEN_WIDTH - 40 - (i * 30), 45))
            
            # Draw pause overlay
            if self.game_state == "paused":
                # Semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill(BLACK)
                overlay.set_alpha(150)
                screen.blit(overlay, (0, 0))
                
                # Pause text
                pause_text = self.title_font.render("PAUSED", True, WHITE)
                resume_text = self.font.render("Press P to resume", True, WHITE)
                
                screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//3))
                screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2))
            
        elif self.game_state == "game_over":
            game_over_text = self.title_font.render("GAME OVER", True, BLACK)
            score_text = self.font.render(f"Score: {self.score}", True, BLACK)
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, BLACK)
            coins_text = self.font.render(f"Coins: {self.coins_collected} | Best: {self.high_coins}", True, BLACK)
            restart_text = self.font.render("Press ENTER to restart", True, BLACK)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//3))
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
            screen.blit(coins_text, (SCREEN_WIDTH//2 - coins_text.get_width()//2, SCREEN_HEIGHT//2 + 80))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 120))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# Create and run the game
if __name__ == "__main__":
    # Create assets directories if they don't exist
    os.makedirs(os.path.join('assets', 'images'), exist_ok=True)
    os.makedirs(os.path.join('assets', 'sounds'), exist_ok=True)
    os.makedirs(os.path.join('assets', 'music'), exist_ok=True)
    
    game = Game()
    game.run()
    
    pygame.quit()
    sys.exit()
