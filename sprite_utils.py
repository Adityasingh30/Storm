import pygame
import os

def load_sprite_sheet(filename, width, height, scale=1):
    """
    Load a sprite sheet and split it into individual frames
    """
    try:
        # Check if file exists, if not use placeholder
        if not os.path.isfile(filename):
            # Create a placeholder surface
            placeholder = pygame.Surface((width, height))
            placeholder.fill((128, 128, 255))  # Light blue placeholder
            return [placeholder]
            
        sheet = pygame.image.load(filename).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        
        frames = []
        for y in range(0, sheet_height, height):
            for x in range(0, sheet_width, width):
                # Extract each frame
                frame = pygame.Surface((width, height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x, y, width, height))
                
                # Scale if needed
                if scale != 1:
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = pygame.transform.scale(frame, (new_width, new_height))
                
                frames.append(frame)
        
        return frames
    except Exception as e:
        print(f"Error loading sprite sheet {filename}: {e}")
        # Return a placeholder
        placeholder = pygame.Surface((width, height))
        placeholder.fill((128, 128, 255))  # Light blue placeholder
        return [placeholder]

def load_image(filename, scale=1):
    """
    Load a single image with error handling
    """
    try:
        # Check if file exists, if not use placeholder
        if not os.path.isfile(filename):
            # Create a placeholder surface
            placeholder = pygame.Surface((50, 50))
            placeholder.fill((128, 128, 255))  # Light blue placeholder
            return placeholder
            
        image = pygame.image.load(filename).convert_alpha()
        
        # Scale if needed
        if scale != 1:
            width, height = image.get_size()
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = pygame.transform.scale(image, (new_width, new_height))
            
        return image
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        # Return a placeholder
        placeholder = pygame.Surface((50, 50))
        placeholder.fill((128, 128, 255))  # Light blue placeholder
        return placeholder

class Animation:
    """
    Handles sprite animations
    """
    def __init__(self, frames, frame_duration=100, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.finished = False
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self):
        return self.frames[self.current_frame]
        
    def reset(self):
        self.current_frame = 0
        self.finished = False
