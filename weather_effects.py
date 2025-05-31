import pygame
import random
import math

class RainDrop:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, self.screen_width)
        self.y = random.randint(-100, -10)
        self.speed = random.randint(5, 15)
        self.length = random.randint(5, 15)
        self.thickness = random.randint(1, 2)
        self.color = (200, 230, 255)  # Light blue
        
    def update(self, game_speed=1.0):
        self.y += self.speed * game_speed
        self.x -= 2 * game_speed  # Slight horizontal movement to simulate wind
        
        if self.y > self.screen_height:
            self.reset()
            
    def draw(self, surface):
        end_x = self.x - self.length * 0.5  # Angle the rain slightly
        end_y = self.y + self.length
        pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), self.thickness)

class Lightning:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.duration = 0
        self.flash_alpha = 0
        self.branches = []
        self.next_strike = random.randint(300, 1000)  # Frames until next lightning
        
    def update(self):
        if not self.active:
            self.next_strike -= 1
            if self.next_strike <= 0:
                self.trigger()
        else:
            self.duration -= 1
            if self.duration <= 0:
                self.active = False
                self.next_strike = random.randint(300, 1000)
                
            # Flash effect fading
            if self.duration < 5:
                self.flash_alpha = max(0, self.flash_alpha - 51)  # Fade out
                
    def trigger(self):
        self.active = True
        self.duration = random.randint(10, 20)
        self.flash_alpha = 100
        
        # Create lightning branches
        self.branches = []
        start_x = random.randint(0, self.screen_width)
        
        # Main branch
        points = [(start_x, 0)]
        x, y = start_x, 0
        
        while y < self.screen_height * 0.7:
            x += random.randint(-15, 15)
            y += random.randint(10, 30)
            points.append((x, y))
            
        self.branches.append(points)
        
        # Add some smaller branches
        for _ in range(random.randint(1, 3)):
            if len(points) > 2:
                # Start from a random point on the main branch
                branch_start = random.randint(1, len(points) - 2)
                branch_points = [points[branch_start]]
                
                bx, by = points[branch_start]
                for _ in range(random.randint(2, 5)):
                    bx += random.randint(-20, 20)
                    by += random.randint(10, 20)
                    branch_points.append((bx, by))
                    
                self.branches.append(branch_points)
                
    def draw(self, surface):
        if not self.active:
            return
            
        # Draw flash overlay
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, self.flash_alpha))
            surface.blit(flash_surface, (0, 0))
            
        # Draw lightning branches
        for branch in self.branches:
            if len(branch) > 1:
                pygame.draw.lines(surface, (255, 255, 255), False, branch, 2)

class WeatherSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rain_intensity = 0  # 0 to 100
        self.raindrops = []
        self.lightning = Lightning(screen_width, screen_height)
        
    def set_intensity(self, intensity):
        """Set storm intensity from 0 (none) to 100 (maximum)"""
        self.rain_intensity = max(0, min(100, intensity))
        
        # Adjust number of raindrops based on intensity
        target_drops = int(self.rain_intensity * 1.5)
        
        # Add more drops if needed
        while len(self.raindrops) < target_drops:
            self.raindrops.append(RainDrop(self.screen_width, self.screen_height))
            
        # Remove drops if too many
        while len(self.raindrops) > target_drops:
            self.raindrops.pop()
            
    def update(self, game_speed=1.0):
        for drop in self.raindrops:
            drop.update(game_speed)
            
        if self.rain_intensity > 50:  # Only show lightning in heavy rain
            self.lightning.update()
            
    def draw(self, surface):
        for drop in self.raindrops:
            drop.draw(surface)
            
        if self.rain_intensity > 50:
            self.lightning.draw(surface)
