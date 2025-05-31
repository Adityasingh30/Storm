import pygame
import sys
import os
from menu_system import MenuSystem
from storm_runner_enhanced import Game

# Initialize pygame
pygame.init()
#pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Storm Runner")
clock = pygame.time.Clock()

# Create assets directories if they don't exist
os.makedirs(os.path.join('assets', 'images'), exist_ok=True)
os.makedirs(os.path.join('assets', 'sounds'), exist_ok=True)
os.makedirs(os.path.join('assets', 'music'), exist_ok=True)

# Game states
MENU = 0
PLAYING = 1

# Main function
def main():
    # Create menu system
    menu = MenuSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Create game
    game = Game()
    
    # Set initial state
    current_state = MENU
    
    # Main game loop
    running = True
    while running:
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
        # Update and draw based on current state
        if current_state == MENU:
            # Handle menu events
            action = menu.handle_events(events)
            
            if action == "play":
                current_state = PLAYING
                game.reset_game()
                # Apply menu settings to the game
                try:
                    pygame.mixer.music.set_volume(menu.get_volume())
                except:
                    pass  # In case mixer isn't initialized
            elif action == "quit":
                running = False
                
            # Draw menu
            menu.draw(screen)
            
        elif current_state == PLAYING:
            # Process events for the game
            game_over_escape = False
            
            # First pass events to the game's handler
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and game.game_state == "game_over":
                        game_over_escape = True
                    elif event.key == pygame.K_SPACE:
                        game.player.jump()
                    elif event.key == pygame.K_p:
                        if game.game_state == "playing":
                            game.game_state = "paused"
                        elif game.game_state == "paused":
                            game.game_state = "playing"
                    elif event.key == pygame.K_RETURN and game.game_state == "game_over":
                        game.reset_game()
            
            if game_over_escape:
                current_state = MENU
            
            # Update game (but don't call game.handle_events() again)
            game.update()
            
            # Draw game
            game.draw()
            
            # Check if game over to return to menu
            if game.game_state == "game_over":
                # Add a prompt to return to menu
                font = pygame.font.SysFont(None, 24)
                text = font.render("Press ESC to return to menu", True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT - 30))
                pygame.display.flip()
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
