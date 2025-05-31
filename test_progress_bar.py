import pygame
import sys
from ui_elements import ProgressBar

# Initialize pygame
pygame.init()

# Set up display
screen_width, screen_height = 800, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Storm Progress Bar Test")
clock = pygame.time.Clock()

# Create a progress bar
storm_progress = ProgressBar(50, 50, 700, 30, max_value=100, color=(100, 100, 255))

# Main game loop
running = True
progress_value = 0
direction = 1  # 1 for increasing, -1 for decreasing

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Update progress bar value
    progress_value += 0.5 * direction
    if progress_value >= 100:
        direction = -1
    elif progress_value <= 0:
        direction = 1
    
    storm_progress.set_value(progress_value)
    
    # Draw
    screen.fill((0, 0, 0))
    storm_progress.draw(screen)
    
    # Display instructions
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Storm Progress: {int(progress_value)}%", True, (255, 255, 255))
    screen.blit(text, (50, 100))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
