import pygame
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Storm Runner")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (100, SCREEN_HEIGHT - 60)
        self.velocity_y = 0
        self.jumping = False
        self.double_jump_available = True
        
    def update(self):
        # Gravity
        self.velocity_y += 0.8
        self.rect.y += self.velocity_y
        
        # Check if on ground
        if self.rect.bottom >= SCREEN_HEIGHT - 60:
            self.rect.bottom = SCREEN_HEIGHT - 60
            self.velocity_y = 0
            self.jumping = False
            self.double_jump_available = True
    
    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True
        elif self.double_jump_available:
            self.velocity_y = -13
            self.double_jump_available = False

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (SCREEN_WIDTH, SCREEN_HEIGHT - 60)
        self.speed = 5
        
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Game class
class Game:
    def __init__(self):
        self.running = True
        self.score = 0
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Obstacle timer
        self.obstacle_timer = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.player.jump()
    
    def update(self):
        # Update all sprites
        self.all_sprites.update()
        
        # Spawn obstacles
        self.obstacle_timer += 1
        if self.obstacle_timer >= 60:
            obstacle = Obstacle()
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)
            self.obstacle_timer = 0
            
        # Check for collisions
        hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        if hits:
            print("Collision detected!")
            
        # Update score
        self.score += 1
    
    def draw(self):
        # Clear screen
        screen.fill(WHITE)
        
        # Draw ground
        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60))
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        
        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        # Draw controls info
        controls_text = font.render("SPACE to jump (double-jump available!)", True, BLACK)
        screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, 10))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# Create and run the game
if __name__ == "__main__":
    game = Game()
    game.run()
    
    pygame.quit()
    sys.exit()
