import pygame
import os
from sprite_utils import load_image

class ParallaxLayer:
    """
    A single layer for parallax scrolling background
    """
    def __init__(self, image_path, scroll_speed, y_pos=0):
        self.image = load_image(image_path)
        if self.image.get_width() < 800:  # If image is smaller than screen width
            # Create a wider surface to allow for seamless scrolling
            wide_surface = pygame.Surface((self.image.get_width() * 3, self.image.get_height()), pygame.SRCALPHA)
            for i in range(3):
                wide_surface.blit(self.image, (i * self.image.get_width(), 0))
            self.image = wide_surface
            
        self.scroll_speed = scroll_speed
        self.x_pos = 0
        self.y_pos = y_pos
        
    def update(self, game_speed=1.0):
        # Move the layer based on its scroll speed
        self.x_pos -= self.scroll_speed * game_speed
        
        # Reset position for seamless scrolling
        if self.x_pos <= -self.image.get_width():
            self.x_pos = 0
            
    def draw(self, surface):
        # Draw the layer twice side by side for seamless scrolling
        surface.blit(self.image, (self.x_pos, self.y_pos))
        surface.blit(self.image, (self.x_pos + self.image.get_width(), self.y_pos))

class ParallaxBackground:
    """
    Manages multiple parallax layers
    """
    def __init__(self):
        self.layers = []
        
        # Define paths to background images
        sky_path = os.path.join('assets', 'images', 'sky.png')
        mountains_path = os.path.join('assets', 'images', 'mountains.png')
        trees_path = os.path.join('assets', 'images', 'trees.png')
        buildings_path = os.path.join('assets', 'images', 'buildings.png')
        
        # Add layers with different scroll speeds (slower for distant objects)
        self.add_layer(sky_path, 0.1, 0)  # Sky (very slow)
        self.add_layer(mountains_path, 0.3, 50)  # Mountains (slow)
        self.add_layer(buildings_path, 0.7, 100)  # Buildings (medium)
        self.add_layer(trees_path, 1.0, 150)  # Trees (fast)
        
    def add_layer(self, image_path, scroll_speed, y_pos=0):
        self.layers.append(ParallaxLayer(image_path, scroll_speed, y_pos))
        
    def update(self, game_speed=1.0):
        for layer in self.layers:
            layer.update(game_speed)
            
    def draw(self, surface):
        for layer in self.layers:
            layer.draw(surface)
