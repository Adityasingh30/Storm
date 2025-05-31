import pygame
import sys
import os
from ui_elements import Button, Slider

class MenuSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_menu = "main"  # main, how_to_play, settings
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (100, 100, 100)
        self.BLUE = (0, 100, 255)
        
        # Create buttons
        button_width = 250
        button_height = 60
        button_x = screen_width // 2 - button_width // 2
        
        # Main menu buttons
        self.play_button = Button(button_x, 180, button_width, button_height, 
                                 "Play", self.font)
        self.how_to_button = Button(button_x, 260, button_width, button_height, 
                                   "How to Play", self.font)
        self.settings_button = Button(button_x, 340, button_width, button_height, 
                                     "Settings", self.font)
        self.exit_button = Button(button_x, 420, button_width, button_height, 
                                 "Exit", self.font)
        
        # Back buttons for sub-menus
        self.back_button = Button(50, screen_height - 90, 120, 50, 
                                 "Back", self.font)
        
        # Settings menu elements
        self.volume_slider = Slider(button_x, 250, button_width, 25, 
                                   min_val=0, max_val=100, initial_val=50, 
                                   label="Volume", font=self.font)
        
        # Game settings
        self.volume = 50
        
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_menu == "main":
                        return "quit"
                    else:
                        self.current_menu = "main"
        
        # Update buttons based on current menu
        if self.current_menu == "main":
            self.play_button.update(mouse_pos, mouse_clicked)
            self.how_to_button.update(mouse_pos, mouse_clicked)
            self.settings_button.update(mouse_pos, mouse_clicked)
            self.exit_button.update(mouse_pos, mouse_clicked)
            
            if self.play_button.is_clicked():
                return "play"
            elif self.how_to_button.is_clicked():
                self.current_menu = "how_to_play"
            elif self.settings_button.is_clicked():
                self.current_menu = "settings"
            elif self.exit_button.is_clicked():
                return "quit"
                
        elif self.current_menu in ["how_to_play", "settings"]:
            self.back_button.update(mouse_pos, mouse_clicked)
            
            if self.back_button.is_clicked():
                self.current_menu = "main"
                
            # Settings specific controls
            if self.current_menu == "settings":
                self.volume_slider.update(mouse_pos, mouse_clicked)
                self.volume = self.volume_slider.get_value()
                # Apply volume setting immediately
                try:
                    pygame.mixer.music.set_volume(self.volume / 100.0)
                except:
                    pass  # In case mixer isn't initialized
        
        return None  # No action to take
        
    def draw(self, surface):
        # Clear screen
        surface.fill(self.BLACK)
        
        # Draw title
        title_text = self.title_font.render("STORM RUNNER", True, self.WHITE)
        surface.blit(title_text, (self.screen_width//2 - title_text.get_width()//2, 80))
        
        # Draw menu elements based on current menu
        if self.current_menu == "main":
            self.play_button.draw(surface)
            self.how_to_button.draw(surface)
            self.settings_button.draw(surface)
            self.exit_button.draw(surface)
            
        elif self.current_menu == "how_to_play":
            # Draw instructions
            instructions = [
                "How to Play:",
                "",
                "- Use SPACE to jump",
                "- Double-jump by pressing SPACE again while in the air",
                "- Collect coins for bonus points",
                "- Avoid obstacles or lose a life",
                "- Collect power-ups for special abilities",
                "- Press P to pause the game",
                "- Outrun the storm to survive!"
            ]
            
            for i, line in enumerate(instructions):
                text = self.font.render(line, True, self.WHITE)
                surface.blit(text, (self.screen_width//2 - text.get_width()//2, 180 + i * 35))
                
            self.back_button.draw(surface)
            
        elif self.current_menu == "settings":
            # Draw settings
            settings_title = self.font.render("Settings", True, self.WHITE)
            surface.blit(settings_title, (self.screen_width//2 - settings_title.get_width()//2, 180))
            
            self.volume_slider.draw(surface)
            
            # Draw current volume
            vol_text = self.font.render(f"Volume: {int(self.volume)}%", True, self.WHITE)
            surface.blit(vol_text, (self.screen_width//2 - vol_text.get_width()//2, 320))
            
            self.back_button.draw(surface)
            
    def get_volume(self):
        return self.volume / 100.0  # Convert to 0.0-1.0 range
