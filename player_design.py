import pygame
import os
import math
from sprite_utils import Animation, load_sprite_sheet, load_image

class EnhancedPlayer(pygame.sprite.Sprite):
    def __init__(self, screen_height, ground_height):
        super().__init__()
        
        # Store reference values
        self.screen_height = screen_height
        self.ground_height = ground_height
        
        # Player stats
        self.velocity_y = 0
        self.jumping = False
        self.double_jump_available = True
        self.invincible = False
        self.invincible_timer = 0
        self.lives = 3
        self.coins = 0
        self.score = 0
        
        # Animation states
        self.state = "idle"  # idle, run, jump, fall, hurt
        self.facing_right = True
        
        # Load animations
        self.animations = self.load_player_animations()
        
        # Set initial image and rect
        self.image = self.animations["idle"].get_current_frame()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (100, screen_height - ground_height)
        
        # Particle effects for running
        self.dust_timer = 0
        self.dust_particles = []
        
        # Jump and hurt sound effects
        self.jump_sound = None
        self.hurt_sound = None
        try:
            self.jump_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'jump.wav'))
            self.hurt_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'hurt.wav'))
        except:
            print("Could not load player sound effects")
    
    def load_player_animations(self):
        """Load all player animations or create placeholders"""
        animations = {}
        
        # Try to load sprite sheets, otherwise create colored rectangles
        try:
            # Check if sprite sheets exist
            run_sheet_path = os.path.join('assets', 'images', 'player_run.png')
            idle_sheet_path = os.path.join('assets', 'images', 'player_idle.png')
            jump_sheet_path = os.path.join('assets', 'images', 'player_jump.png')
            
            if os.path.exists(run_sheet_path):
                # If real sprites exist, load them
                run_frames = load_sprite_sheet(run_sheet_path, 48, 48)
                idle_frames = load_sprite_sheet(idle_sheet_path, 48, 48)
                jump_frames = load_sprite_sheet(jump_sheet_path, 48, 48)
                
                animations["run"] = Animation(run_frames, 100)
                animations["idle"] = Animation(idle_frames, 150)
                animations["jump"] = Animation(jump_frames, 100, loop=False)
                animations["fall"] = Animation([jump_frames[-1]], 100)
                animations["hurt"] = Animation([run_frames[0]], 100)  # Use first run frame tinted red for hurt
            else:
                # Create placeholder animations with colored rectangles
                run_frames = self.create_placeholder_frames("run", 6)
                idle_frames = self.create_placeholder_frames("idle", 4)
                jump_frames = self.create_placeholder_frames("jump", 2)
                
                animations["run"] = Animation(run_frames, 100)
                animations["idle"] = Animation(idle_frames, 150)
                animations["jump"] = Animation(jump_frames, 100, loop=False)
                animations["fall"] = Animation([jump_frames[-1]], 100)
                animations["hurt"] = Animation([self.create_placeholder_frames("hurt", 1)[0]], 100)
        except Exception as e:
            print(f"Error loading player animations: {e}")
            # Create basic placeholder if everything fails
            basic_frame = pygame.Surface((40, 60))
            basic_frame.fill((0, 100, 255))
            animations["run"] = Animation([basic_frame], 100)
            animations["idle"] = Animation([basic_frame], 100)
            animations["jump"] = Animation([basic_frame], 100)
            animations["fall"] = Animation([basic_frame], 100)
            animations["hurt"] = Animation([basic_frame], 100)
            
        return animations
    
    def create_placeholder_frames(self, animation_type, num_frames):
        """Create placeholder animation frames with different colors based on type"""
        frames = []
        
        if animation_type == "run":
            # Blue running character with leg movement
            for i in range(num_frames):
                frame = pygame.Surface((40, 60), pygame.SRCALPHA)
                # Body
                pygame.draw.rect(frame, (0, 100, 255), (10, 0, 20, 40))
                # Head
                pygame.draw.circle(frame, (0, 100, 255), (20, 0), 10)
                # Legs - alternate positions
                leg_offset = 5 if i % 2 == 0 else -5
                pygame.draw.rect(frame, (0, 80, 200), (10, 40, 8, 20))
                pygame.draw.rect(frame, (0, 80, 200), (22, 40, 8, 20 - leg_offset))
                frames.append(frame)
                
        elif animation_type == "idle":
            # Blue standing character with slight movement
            for i in range(num_frames):
                frame = pygame.Surface((40, 60), pygame.SRCALPHA)
                # Body
                pygame.draw.rect(frame, (0, 100, 255), (10, 0 + (i % 2), 20, 40 - (i % 2)))
                # Head
                pygame.draw.circle(frame, (0, 100, 255), (20, 0 + (i % 2)), 10)
                # Legs
                pygame.draw.rect(frame, (0, 80, 200), (10, 40, 8, 20))
                pygame.draw.rect(frame, (0, 80, 200), (22, 40, 8, 20))
                frames.append(frame)
                
        elif animation_type == "jump":
            # Blue jumping character
            for i in range(num_frames):
                frame = pygame.Surface((40, 60), pygame.SRCALPHA)
                # Body - more compact when jumping
                pygame.draw.rect(frame, (0, 100, 255), (10, 5, 20, 35))
                # Head
                pygame.draw.circle(frame, (0, 100, 255), (20, 5), 10)
                # Legs - tucked up for jump
                leg_angle = 30 if i == 0 else 45
                pygame.draw.rect(frame, (0, 80, 200), (10, 40, 8, 15))
                pygame.draw.rect(frame, (0, 80, 200), (22, 40, 8, 15))
                frames.append(frame)
                
        elif animation_type == "hurt":
            # Red tinted character for hurt state
            frame = pygame.Surface((40, 60), pygame.SRCALPHA)
            # Body
            pygame.draw.rect(frame, (255, 100, 100), (10, 0, 20, 40))
            # Head
            pygame.draw.circle(frame, (255, 100, 100), (20, 0), 10)
            # Legs
            pygame.draw.rect(frame, (200, 80, 80), (10, 40, 8, 20))
            pygame.draw.rect(frame, (200, 80, 80), (22, 40, 8, 20))
            frames.append(frame)
            
        return frames
    
    def update(self):
        # Apply gravity
        self.velocity_y += 0.8
        self.rect.y += self.velocity_y
        
        # Check if on ground
        if self.rect.bottom >= self.screen_height - self.ground_height:
            self.rect.bottom = self.screen_height - self.ground_height
            self.velocity_y = 0
            self.jumping = False
            self.double_jump_available = True
            
            # Create dust particles when landing from a jump
            if self.state == "fall":
                self.create_dust_particles(5)
        
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Update animation state
        if self.invincible and self.invincible_timer > 0:
            new_state = "hurt"
        elif self.velocity_y < 0:
            new_state = "jump"
        elif self.velocity_y > 1:  # Small threshold to avoid flickering
            new_state = "fall"
        elif self.velocity_y == 0 and not self.jumping:
            # Only create dust while running on ground
            self.dust_timer += 1
            if self.dust_timer >= 10:  # Create dust every 10 frames
                self.create_dust_particles(1)
                self.dust_timer = 0
            new_state = "run"
        else:
            new_state = "idle"
            
        # Update animation if state changed
        if new_state != self.state:
            self.state = new_state
            if self.state == "jump" or self.state == "fall":
                self.animations[self.state].reset()
        
        # Update current animation
        self.animations[self.state].update()
        
        # Get current frame and flip if needed
        current_frame = self.animations[self.state].get_current_frame()
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        # Apply blinking effect when invincible
        if self.invincible and self.invincible_timer % 10 < 5:
            # Create a semi-transparent copy for blinking
            self.image = current_frame.copy()
            self.image.set_alpha(128)
        else:
            self.image = current_frame
            
        # Update dust particles
        self.update_dust_particles()
    
    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True
            self.state = "jump"
            self.animations[self.state].reset()
            self.create_dust_particles(3)
            
            # Play jump sound
            if self.jump_sound:
                self.jump_sound.play()
                
        elif self.double_jump_available:
            self.velocity_y = -13
            self.double_jump_available = False
            self.state = "jump"
            self.animations[self.state].reset()
            self.create_dust_particles(2)
            
            # Play jump sound at lower volume for double jump
            if self.jump_sound:
                self.jump_sound.set_volume(0.7)
                self.jump_sound.play()
                self.jump_sound.set_volume(1.0)
    
    def make_invincible(self, duration=180):
        self.invincible = True
        self.invincible_timer = duration
    
    def lose_life(self):
        if not self.invincible:
            self.lives -= 1
            self.make_invincible(120)
            
            # Play hurt sound
            if self.hurt_sound:
                self.hurt_sound.play()
                
            return self.lives <= 0
        return False
    
    def create_dust_particles(self, count):
        """Create dust particles at player's feet"""
        for _ in range(count):
            # Particle properties
            size = random.randint(3, 6)
            pos_x = self.rect.midbottom[0] + random.randint(-10, 10)
            pos_y = self.rect.midbottom[1] - random.randint(0, 5)
            velocity_x = random.uniform(-0.5, 0.5)
            velocity_y = random.uniform(-1.5, -0.5)
            lifetime = random.randint(20, 40)
            
            # Add to particle list
            self.dust_particles.append({
                'pos': [pos_x, pos_y],
                'vel': [velocity_x, velocity_y],
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': (200, 200, 200)
            })
    
    def update_dust_particles(self):
        """Update and remove expired dust particles"""
        for particle in self.dust_particles[:]:
            # Update position
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            
            # Update lifetime
            particle['lifetime'] -= 1
            
            # Remove if expired
            if particle['lifetime'] <= 0:
                self.dust_particles.remove(particle)
    
    def draw_particles(self, surface):
        """Draw all active dust particles"""
        for particle in self.dust_particles:
            # Calculate opacity based on remaining lifetime
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            
            # Draw particle
            pygame.draw.circle(
                surface,
                particle['color'] + (alpha,),  # Add alpha to color
                (int(particle['pos'][0]), int(particle['pos'][1])),
                particle['size']
            )
