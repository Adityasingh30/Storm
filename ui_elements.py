import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, text_color=(255, 255, 255), 
                 bg_color=(50, 50, 50), hover_color=(70, 70, 70)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.hovered = False
        self.clicked = False
        
    def update(self, mouse_pos, mouse_clicked):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.clicked = False
        
        if self.hovered and mouse_clicked:
            self.clicked = True
            
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)  # Border
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self):
        return self.clicked

class Slider:
    def __init__(self, x, y, width, height, min_val=0, max_val=100, initial_val=50, 
                 label="", font=None, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.label = label
        self.font = font
        self.text_color = text_color
        
        # Calculate handle position
        self.handle_width = height * 2
        self.handle_rect = pygame.Rect(0, 0, self.handle_width, height * 1.5)
        self.update_handle_pos()
        
    def update_handle_pos(self):
        # Convert value to position
        val_range = self.max_val - self.min_val
        pos_range = self.rect.width - self.handle_width
        rel_val = self.value - self.min_val
        pos = int((rel_val / val_range) * pos_range) if val_range > 0 else 0
        
        self.handle_rect.x = self.rect.x + pos
        self.handle_rect.centery = self.rect.centery
        
    def update(self, mouse_pos, mouse_pressed):
        mouse_x, mouse_y = mouse_pos
        
        # Check if mouse is pressed on the handle
        if mouse_pressed:  # Changed from mouse_pressed[0] to just mouse_pressed
            if self.handle_rect.collidepoint(mouse_pos):
                self.dragging = True
            elif self.dragging:
                # Update position while dragging
                rel_x = mouse_x - self.rect.x
                # Constrain to slider width
                rel_x = max(0, min(rel_x, self.rect.width - self.handle_width))
                
                # Convert position to value
                val_range = self.max_val - self.min_val
                pos_range = self.rect.width - self.handle_width
                self.value = self.min_val + (rel_x / pos_range) * val_range if pos_range > 0 else self.min_val
                
                # Update handle position
                self.handle_rect.x = self.rect.x + rel_x
        else:
            self.dragging = False
            
    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        pygame.draw.rect(surface, (150, 150, 150), self.rect, 2)
        
        # Draw handle
        pygame.draw.rect(surface, (200, 200, 200), self.handle_rect)
        pygame.draw.rect(surface, (255, 255, 255), self.handle_rect, 2)
        
        # Draw label and value if font is provided
        if self.font:
            # Label
            if self.label:
                label_surf = self.font.render(self.label, True, self.text_color)
                label_rect = label_surf.get_rect(bottomleft=(self.rect.x, self.rect.y - 5))
                surface.blit(label_surf, label_rect)
            
            # Value
            value_text = f"{int(self.value)}"
            value_surf = self.font.render(value_text, True, self.text_color)
            value_rect = value_surf.get_rect(bottomright=(self.rect.right, self.rect.y - 5))
            surface.blit(value_surf, value_rect)
            
    def get_value(self):
        return self.value

class ProgressBar:
    def __init__(self, x, y, width, height, max_value=100, color=(0, 200, 0), 
                 bg_color=(50, 50, 50), border_color=(200, 200, 200)):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.value = 0
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        
    def set_value(self, value):
        self.value = max(0, min(value, self.max_value))
        
    def get_percentage(self):
        return (self.value / self.max_value) * 100 if self.max_value > 0 else 0
        
    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Draw progress
        if self.value > 0:
            fill_width = int((self.value / self.max_value) * self.rect.width)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.color, fill_rect)
            
        # Draw border
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
