import pygame
import os
import random
import math
from sprite_utils import load_image

class ParallaxBackground:
    """Enhanced parallax background with multiple layers"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layers = []
        
        # Define background layers with their scroll speeds
        # Format: (image_path, scroll_speed, y_position)
        bg_layers = [
            ('sky.png', 0.1, 0),                  # Sky (slowest)
            ('clouds.png', 0.2, 50),              # Distant clouds
            ('mountains.png', 0.3, 100),          # Mountains
            ('distant_trees.png', 0.5, 150),      # Far trees
            ('trees.png', 0.7, 200),              # Trees
            ('bushes.png', 0.9, screen_height - 150)  # Bushes (fastest)
        ]
        
        # Load each layer
        for image_name, speed, y_pos in bg_layers:
            self.add_layer(os.path.join('assets', 'images', image_name), speed, y_pos)
    
    def add_layer(self, image_path, scroll_speed, y_pos=0):
        """Add a new parallax layer"""
        # Try to load the image, or create a placeholder
        try:
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
            else:
                # Create a placeholder with a gradient
                image = self.create_placeholder_layer(scroll_speed)
        except:
            # Fallback to placeholder on error
            image = self.create_placeholder_layer(scroll_speed)
        
        # Make sure the image is wide enough for seamless scrolling
        if image.get_width() < self.screen_width:
            # Create a wider surface
            wide_surface = pygame.Surface((image.get_width() * 3, image.get_height()), pygame.SRCALPHA)
            for i in range(3):
                wide_surface.blit(image, (i * image.get_width(), 0))
            image = wide_surface
        
        # Add the layer
        self.layers.append({
            'image': image,
            'scroll_speed': scroll_speed,
            'x_pos': 0,
            'y_pos': y_pos
        })
    
    def create_placeholder_layer(self, scroll_speed):
        """Create a placeholder background layer with appropriate colors"""
        layer_height = 100
        
        # Choose color based on scroll speed (far = light, near = dark)
        if scroll_speed < 0.3:
            # Sky colors
            color1 = (135, 206, 235)  # Sky blue
            color2 = (200, 230, 255)  # Light blue
        elif scroll_speed < 0.6:
            # Mountain/hill colors
            color1 = (100, 120, 150)  # Bluish gray
            color2 = (70, 90, 110)    # Darker blue-gray
        else:
            # Foreground colors
            color1 = (50, 120, 50)    # Dark green
            color2 = (70, 150, 70)    # Medium green
        
        # Create gradient surface
        surface = pygame.Surface((self.screen_width * 2, layer_height), pygame.SRCALPHA)
        
        # Fill with base color
        surface.fill(color1)
        
        # Add some random shapes for texture
        for _ in range(50):
            shape_x = random.randint(0, surface.get_width() - 1)
            shape_y = random.randint(0, surface.get_height() - 1)
            shape_size = random.randint(5, 20)
            
            if scroll_speed < 0.3:
                # Cloud-like shapes for sky
                pygame.draw.ellipse(surface, color2, (shape_x, shape_y, shape_size * 2, shape_size))
            elif scroll_speed < 0.6:
                # Mountain-like triangles
                points = [
                    (shape_x, shape_y + shape_size),
                    (shape_x + shape_size, shape_y + shape_size),
                    (shape_x + shape_size // 2, shape_y)
                ]
                pygame.draw.polygon(surface, color2, points)
            else:
                # Bush/tree-like shapes
                pygame.draw.circle(surface, color2, (shape_x, shape_y), shape_size // 2)
        
        return surface
    
    def update(self, game_speed=1.0):
        """Update all layers based on their scroll speed"""
        for layer in self.layers:
            # Move the layer based on its scroll speed
            layer['x_pos'] -= layer['scroll_speed'] * game_speed
            
            # Reset position for seamless scrolling
            if layer['x_pos'] <= -layer['image'].get_width() // 2:
                layer['x_pos'] = 0
    
    def draw(self, surface):
        """Draw all background layers"""
        for layer in self.layers:
            # Draw the layer twice side by side for seamless scrolling
            surface.blit(layer['image'], (layer['x_pos'], layer['y_pos']))
            surface.blit(layer['image'], 
                        (layer['x_pos'] + layer['image'].get_width(), layer['y_pos']))

class Ground:
    """Enhanced ground with texture and details"""
    def __init__(self, screen_width, screen_height, ground_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ground_height = ground_height
        
        # Try to load ground texture
        ground_path = os.path.join('assets', 'images', 'ground.png')
        try:
            if os.path.exists(ground_path):
                self.texture = pygame.image.load(ground_path).convert()
                # Tile the texture if needed
                if self.texture.get_width() < screen_width:
                    wide_texture = pygame.Surface((screen_width * 2, ground_height))
                    for x in range(0, screen_width * 2, self.texture.get_width()):
                        wide_texture.blit(self.texture, (x, 0))
                    self.texture = wide_texture
            else:
                self.texture = self.create_ground_texture()
        except:
            self.texture = self.create_ground_texture()
            
        # Scroll position
        self.scroll_pos = 0
        
        # Ground details (small rocks, grass tufts)
        self.details = []
        self.generate_details()
    
    def create_ground_texture(self):
        """Create a textured ground surface"""
        texture = pygame.Surface((self.screen_width * 2, self.ground_height))
        
        # Base color
        base_color = (110, 80, 50)  # Brown
        texture.fill(base_color)
        
        # Add noise for texture
        for x in range(texture.get_width()):
            for y in range(texture.get_height()):
                noise = random.randint(-10, 10)
                color = (
                    max(0, min(255, base_color[0] + noise)),
                    max(0, min(255, base_color[1] + noise)),
                    max(0, min(255, base_color[2] + noise))
                )
                texture.set_at((x, y), color)
        
        # Add a darker top line
        pygame.draw.line(texture, (80, 60, 40), 
                        (0, 0), (texture.get_width(), 0), 3)
        
        # Add some horizontal lines for layers
        for y in range(10, texture.get_height(), 15):
            line_color = (100, 70, 40)
            pygame.draw.line(texture, line_color, 
                            (0, y), (texture.get_width(), y), 1)
        
        return texture
    
    def generate_details(self):
        """Generate ground details like rocks and grass"""
        for _ in range(30):
            detail_type = random.choice(['rock', 'grass', 'pebble'])
            x_pos = random.randint(0, self.screen_width * 2)
            
            if detail_type == 'rock':
                size = random.randint(5, 10)
                y_pos = self.screen_height - self.ground_height + 5
                color = (80, 80, 80)
            elif detail_type == 'grass':
                size = random.randint(3, 8)
                y_pos = self.screen_height - self.ground_height + 2
                color = (70, 140, 50)
            else:  # pebble
                size = random.randint(2, 4)
                y_pos = self.screen_height - self.ground_height + 10
                color = (120, 100, 80)
                
            self.details.append({
                'type': detail_type,
                'x': x_pos,
                'y': y_pos,
                'size': size,
                'color': color
            })
    
    def update(self, game_speed):
        """Update ground scroll position"""
        self.scroll_pos -= game_speed
        if self.scroll_pos <= -self.texture.get_width() // 2:
            self.scroll_pos = 0
            
        # Update details
        for detail in self.details:
            detail['x'] -= game_speed
            if detail['x'] < -20:
                detail['x'] = self.screen_width + random.randint(0, 100)
    
    def draw(self, surface):
        """Draw the ground with texture and details"""
        # Draw the ground texture
        surface.blit(self.texture, (self.scroll_pos, self.screen_height - self.ground_height))
        surface.blit(self.texture, 
                    (self.scroll_pos + self.texture.get_width(), 
                     self.screen_height - self.ground_height))
        
        # Draw details
        for detail in self.details:
            if detail['type'] == 'rock':
                pygame.draw.circle(surface, detail['color'], 
                                 (int(detail['x']), int(detail['y'])), 
                                 detail['size'])
            elif detail['type'] == 'grass':
                # Draw a few blades of grass
                for i in range(3):
                    offset = random.randint(-2, 2)
                    pygame.draw.line(surface, detail['color'],
                                   (detail['x'] + offset, detail['y']),
                                   (detail['x'] + offset, detail['y'] - detail['size']),
                                   1)
            else:  # pebble
                pygame.draw.circle(surface, detail['color'], 
                                 (int(detail['x']), int(detail['y'])), 
                                 detail['size'])

class WeatherSystem:
    """Weather effects including rain, lightning, and fog"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Rain properties
        self.raindrops = []
        self.rain_intensity = 0  # 0-100
        
        # Lightning properties
        self.lightning_active = False
        self.lightning_timer = 0
        self.lightning_duration = 0
        self.lightning_alpha = 0
        self.next_lightning = random.randint(300, 600)
        
        # Fog properties
        self.fog_surfaces = self.create_fog_surfaces()
        self.fog_positions = [
            {'x': 0, 'y': screen_height - 200, 'speed': 0.3},
            {'x': -400, 'y': screen_height - 150, 'speed': 0.5},
            {'x': -800, 'y': screen_height - 100, 'speed': 0.7}
        ]
        self.fog_alpha = 0
    
    def create_fog_surfaces(self):
        """Create fog cloud surfaces with different sizes"""
        fog_surfaces = []
        
        for size in [(300, 100), (400, 150), (500, 120)]:
            # Create a surface for the fog
            fog = pygame.Surface(size, pygame.SRCALPHA)
            
            # Create a cloudy pattern
            for _ in range(100):
                x = random.randint(0, size[0] - 1)
                y = random.randint(0, size[1] - 1)
                radius = random.randint(20, 40)
                
                # Draw a semi-transparent white circle
                pygame.draw.circle(fog, (255, 255, 255, 30), (x, y), radius)
            
            fog_surfaces.append(fog)
        
        return fog_surfaces
    
    def set_storm_intensity(self, intensity):
        """Set the intensity of the storm (0-100)"""
        self.rain_intensity = intensity
        
        # Adjust number of raindrops
        target_drops = int(intensity * 2)
        
        # Add or remove raindrops as needed
        while len(self.raindrops) < target_drops:
            self.add_raindrop()
        
        while len(self.raindrops) > target_drops:
            self.raindrops.pop()
            
        # Set fog opacity based on intensity
        self.fog_alpha = min(150, intensity * 1.5)
    
    def add_raindrop(self):
        """Add a new raindrop"""
        self.raindrops.append({
            'x': random.randint(0, self.screen_width),
            'y': random.randint(-100, 0),
            'speed': random.randint(10, 20),
            'length': random.randint(10, 20),
            'thickness': random.randint(1, 2)
        })
    
    def update(self, game_speed=1.0):
        """Update all weather effects"""
        # Update raindrops
        for drop in self.raindrops:
            drop['y'] += drop['speed'] * game_speed
            drop['x'] -= 3 * game_speed  # Angle the rain
            
            if drop['y'] > self.screen_height:
                drop['y'] = random.randint(-100, -10)
                drop['x'] = random.randint(0, self.screen_width)
        
        # Update lightning
        if self.rain_intensity > 60:  # Only show lightning in heavy rain
            if not self.lightning_active:
                self.lightning_timer -= 1
                if self.lightning_timer <= 0:
                    self.trigger_lightning()
            else:
                self.lightning_duration -= 1
                if self.lightning_duration <= 0:
                    self.lightning_active = False
                    self.lightning_timer = random.randint(100, 300)
                    
                # Flash effect fading
                if self.lightning_duration < 5:
                    self.lightning_alpha = max(0, self.lightning_alpha - 51)
        
        # Update fog
        for fog in self.fog_positions:
            fog['x'] -= fog['speed'] * game_speed
            if fog['x'] < -self.fog_surfaces[0].get_width():
                fog['x'] = self.screen_width
    
    def trigger_lightning(self):
        """Trigger a lightning flash"""
        self.lightning_active = True
        self.lightning_duration = random.randint(5, 10)
        self.lightning_alpha = 100
    
    def draw(self, surface):
        """Draw all weather effects"""
        # Draw fog
        if self.fog_alpha > 0:
            for i, fog in enumerate(self.fog_positions):
                # Use modulo to cycle through available fog surfaces
                fog_surface = self.fog_surfaces[i % len(self.fog_surfaces)].copy()
                fog_surface.set_alpha(self.fog_alpha)
                surface.blit(fog_surface, (fog['x'], fog['y']))
        
        # Draw raindrops
        for drop in self.raindrops:
            end_x = drop['x'] - drop['length']
            end_y = drop['y'] + drop['length']
            pygame.draw.line(surface, (200, 230, 255), 
                           (drop['x'], drop['y']), 
                           (end_x, end_y), 
                           drop['thickness'])
        
        # Draw lightning flash
        if self.lightning_active and self.lightning_alpha > 0:
            flash = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            flash.fill((255, 255, 255, self.lightning_alpha))
            surface.blit(flash, (0, 0))

class EnhancedObstacle(pygame.sprite.Sprite):
    """Enhanced obstacle with better visuals and animations"""
    def __init__(self, screen_width, screen_height, ground_height, speed, game_speed, obstacle_type="standard"):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ground_height = ground_height
        self.obstacle_type = obstacle_type
        self.speed = speed + game_speed
        self.rotation = 0
        
        # Create the obstacle based on type - all as triangles
        if obstacle_type == "standard":
            self.create_standard_triangle()
        elif obstacle_type == "flying":
            self.create_flying_triangle()
        elif obstacle_type == "boulder":
            self.create_boulder_triangle()
        else:
            # Default fallback
            self.create_standard_triangle()
    
    def create_standard_triangle(self):
        """Create a standard ground triangle obstacle"""
        # Create a triangular shape
        height = random.randint(30, 60)
        width = random.randint(30, 50)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw a triangle
        pygame.draw.polygon(self.image, (200, 50, 50), [
            (width // 2, 0),  # Top point
            (0, height),      # Bottom left
            (width, height)   # Bottom right
        ])
        
        # Add some texture/detail
        for _ in range(3):
            y = random.randint(height // 3, height - 5)
            pygame.draw.line(self.image, (150, 30, 30),
                           (5, y), (width - 5, y), 2)
        
        self.rect = self.image.get_rect()
        
        # Position at ground level
        self.rect.bottomleft = (self.screen_width, self.screen_height - self.ground_height)
    
    def create_flying_triangle(self):
        """Create a flying triangle obstacle"""
        # Create a flying triangular shape
        height = random.randint(20, 40)
        width = random.randint(40, 60)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw a triangle pointing right (like an arrow)
        pygame.draw.polygon(self.image, (255, 140, 0), [
            (0, 0),           # Top left
            (0, height),      # Bottom left
            (width, height//2) # Right middle
        ])
        
        # Add some detail
        pygame.draw.line(self.image, (200, 100, 0),
                       (width//4, height//4), (width//2, height//2), 2)
        pygame.draw.line(self.image, (200, 100, 0),
                       (width//4, height*3//4), (width//2, height//2), 2)
        
        self.rect = self.image.get_rect()
        
        # Position in air
        height_offset = random.randint(70, 200)
        self.rect.bottomleft = (self.screen_width, self.screen_height - self.ground_height - height_offset)
        
        # Movement pattern
        self.y_movement = random.choice([-1, 1])
        self.y_range = random.randint(20, 40)
        self.original_y = self.rect.y
        self.movement_speed = random.uniform(0.05, 0.1)
    
    def create_boulder_triangle(self):
        """Create a rolling triangle obstacle"""
        # Create a triangular boulder (pyramid)
        size = random.randint(40, 60)
        self.original_image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw a triangle
        pygame.draw.polygon(self.original_image, (150, 50, 150), [
            (size // 2, 0),   # Top point
            (0, size),        # Bottom left
            (size, size)      # Bottom right
        ])
        
        # Add some texture/cracks
        for _ in range(3):
            start_x = random.randint(size//4, size//4 * 3)
            start_y = random.randint(size//4, size//4 * 3)
            end_x = start_x + random.randint(-size//4, size//4)
            end_y = start_y + random.randint(-size//4, size//4)
            
            pygame.draw.line(self.original_image, (100, 30, 100),
                           (start_x, start_y), (end_x, end_y), 2)
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        
        # Position at ground level
        self.rect.bottomleft = (self.screen_width, self.screen_height - self.ground_height)
        
        # Rotation properties
        self.rotation = 0
        self.rotation_speed = random.uniform(3, 7)
    
    def update(self):
        """Update obstacle position and animation"""
        # Move left
        self.rect.x -= self.speed
        
        # Type-specific updates
        if self.obstacle_type == "flying":
            # Oscillating up and down movement
            self.rect.y = self.original_y + self.y_range * math.sin(pygame.time.get_ticks() * self.movement_speed)
        
        elif self.obstacle_type == "boulder":
            # Rotate the boulder
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation = 0
                
            # Apply rotation
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            
            # Keep the same position after rotation (which changes rect size)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()
