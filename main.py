"""
Belgian Bingo Game
-----------------
A digital bingo game that works with Arduino-controlled physical components.
This game displays a 5x5 bingo card and interfaces with Arduino Uno as a bridge
to control physical components through Arduino Mega.
"""

import os
import sys
import json
import random
import time
import pygame
import serial
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Directory paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Global variables
settings = {}
serial_conn = None
game_active = False
balls_drawn = []
current_ball = None
player_cards = []
score = 0
wins = 0
games_played = 0


class Ball:
    """Represents a bingo ball with letter, number, and color attributes."""
    
    def __init__(self, number: int):
        self.number = number
        
        # Determine the letter based on the number range
        if 1 <= number <= 15:
            self.letter = 'B'
        elif 16 <= number <= 30:
            self.letter = 'I'
        elif 31 <= number <= 45:
            self.letter = 'N'
        elif 46 <= number <= 60:
            self.letter = 'G'
        elif 61 <= number <= 75:
            self.letter = 'O'
        else:
            self.letter = '?'
            
        # Get color from settings
        if self.letter in settings['colors']['ball_colors']:
            self.color = settings['colors']['ball_colors'][self.letter]
        else:
            self.color = (255, 255, 255)
        
        self.drawn = False
        self.image = None
        self._create_image()
        
    def _create_image(self):
        """Create an image representation of the ball."""
        try:
            # Create a reliable basic colored circle first
            self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
            
            if self.letter == 'B':
                ball_color = (65, 105, 225)  # Blue
            elif self.letter == 'I':
                ball_color = (34, 139, 34)  # Green
            elif self.letter == 'N':
                ball_color = (255, 0, 0)  # Red
            elif self.letter == 'G':
                ball_color = (255, 215, 0)  # Yellow
            elif self.letter == 'O':
                ball_color = (138, 43, 226)  # Purple
            else:
                ball_color = (255, 255, 255)  # White
                
            # Draw the circle with the appropriate color
            pygame.draw.circle(self.image, ball_color, (60, 60), 57)
            pygame.draw.circle(self.image, (255, 255, 255), (60, 60), 50)
            
            # Add text to the circle - use built-in font which is reliable
            font = pygame.font.Font(None, 48) 
            ball_text = font.render(f"{self.letter}{self.number}", True, (0, 0, 0))
            text_rect = ball_text.get_rect(center=(60, 60))
            self.image.blit(ball_text, text_rect)
            
            # Try loading prettier ball image 
            try:
                # Choose appropriate ball image based on the letter
                if self.letter == 'B':
                    ball_img_path = os.path.join(IMAGES_DIR, "ball_blue.png")
                elif self.letter == 'I':
                    ball_img_path = os.path.join(IMAGES_DIR, "ball_green.png")
                elif self.letter == 'N':
                    ball_img_path = os.path.join(IMAGES_DIR, "ball_red.png")
                elif self.letter == 'G':
                    ball_img_path = os.path.join(IMAGES_DIR, "ball_yellow.png")
                elif self.letter == 'O':
                    ball_img_path = os.path.join(IMAGES_DIR, "ball_white.png")
                else:
                    ball_img_path = os.path.join(IMAGES_DIR, "ball_white.png")
                
                if os.path.exists(ball_img_path):
                    img = pygame.image.load(ball_img_path)
                    # Resize the image to a suitable size for display
                    fancy_img = pygame.transform.scale(img, (120, 120))
                    
                    # Add number text to the fancy ball image
                    fancy_img.blit(ball_text, text_rect)
                    self.image = fancy_img
            except Exception as e:
                print(f"Couldn't load fancy ball image, using basic circle: {e}")
                # Keep using the basic circle we created earlier
                pass
            
        except Exception as e:
            # Final fallback if everything else fails
            print(f"Error creating ball image: {e}")
            self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 150, 150), (60, 60), 60)  # Gray circle


class BingoCell:
    """Represents a single cell in a bingo card."""
    
    def __init__(self, number: int, column: int):
        self.number = number
        self.column = column  # 0=B, 1=I, 2=N, 3=G, 4=O
        self.marked = False
        
        # Get the letter for the column
        letters = ['B', 'I', 'N', 'G', 'O']
        self.letter = letters[column]
        
    def mark(self):
        """Mark this cell as drawn."""
        self.marked = True
        
    def is_marked(self) -> bool:
        """Check if this cell has been marked."""
        return self.marked


class BingoCard:
    """Represents a 5x5 bingo card with cells arranged in a grid."""
    
    def __init__(self):
        self.grid = []
        self._generate_card()
        self.winner = False
        self.winning_pattern = None
        
    def _generate_card(self):
        """Generate a random 5x5 bingo card following Belgian bingo rules."""
        # Belgian bingo uses 1-75 numbers
        # B: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75
        
        self.grid = []
        
        # For each column, select 5 unique random numbers from the column's range
        for col in range(5):
            start = col * 15 + 1
            end = start + 14
            
            # For the N column (middle), make the center spot free
            if col == 2:
                # Select 4 numbers for the N column (leaving middle space for FREE)
                column_numbers = random.sample(range(start, end + 1), 5)
                # Replace the middle spot with 0 to represent FREE
                column_numbers[2] = 0
            else:
                column_numbers = random.sample(range(start, end + 1), 5)
                
            # Create the cells for this column
            column = [BingoCell(num, col) for num in column_numbers]
            self.grid.append(column)
        
        # If the center cell is 0, mark it as already selected (FREE space)
        if self.grid[2][2].number == 0:
            self.grid[2][2].mark()
    
    def mark_number(self, number: int) -> bool:
        """Mark a number on the card if it exists. Return True if marked."""
        for col in range(5):
            for row in range(5):
                if self.grid[col][row].number == number:
                    self.grid[col][row].mark()
                    return True
        return False
    
    def check_for_win(self, pattern: str) -> bool:
        """Check if the card has a winning pattern."""
        if pattern == "horizontal":
            # Check rows
            for row in range(5):
                if all(self.grid[col][row].is_marked() for col in range(5)):
                    self.winner = True
                    self.winning_pattern = "horizontal"
                    return True
                    
        elif pattern == "vertical":
            # Check columns
            for col in range(5):
                if all(self.grid[col][row].is_marked() for row in range(5)):
                    self.winner = True
                    self.winning_pattern = "vertical"
                    return True
                    
        elif pattern == "diagonal":
            # Check diagonals
            if all(self.grid[i][i].is_marked() for i in range(5)) or \
               all(self.grid[i][4-i].is_marked() for i in range(5)):
                self.winner = True
                self.winning_pattern = "diagonal"
                return True
                
        elif pattern == "four_corners":
            # Check four corners
            if (self.grid[0][0].is_marked() and 
                self.grid[0][4].is_marked() and 
                self.grid[4][0].is_marked() and 
                self.grid[4][4].is_marked()):
                self.winner = True
                self.winning_pattern = "four_corners"
                return True
                
        elif pattern == "full_card":
            # Check full card
            for col in range(5):
                for row in range(5):
                    if not self.grid[col][row].is_marked():
                        return False
            self.winner = True
            self.winning_pattern = "full_card"
            return True
        
        # Check all patterns if not specified
        elif pattern == "any":
            # Try all patterns
            for p in ["horizontal", "vertical", "diagonal", "four_corners"]:
                if self.check_for_win(p):
                    return True
            
        return False


class ArduinoBridge:
    """Handles communication with Arduino Uno bridge."""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.1):
        self.connection = None
        self.connected = False
        self.fallback_mode = False
        self.auto_detect = settings['serial'].get('auto_detect', False)
        
        if self.auto_detect:
            self.detect_and_connect(baudrate, timeout)
        else:
            self.connect(port, baudrate, timeout)
    
    def detect_and_connect(self, baudrate: int = 9600, timeout: float = 0.1) -> bool:
        """Auto-detect and connect to Arduino."""
        print("Auto-detecting Arduino port...")
        available_ports = self.list_serial_ports()
        
        if not available_ports:
            print("No serial ports found. Running in fallback mode.")
            self.fallback_mode = True
            return False
            
        # Try each port until we find the Arduino
        for port in available_ports:
            print(f"Trying port: {port}")
            if self.connect(port, baudrate, timeout):
                print(f"Successfully connected to Arduino on port {port}")
                return True
                
        print("Could not find Arduino on any available port. Running in fallback mode.")
        self.fallback_mode = True
        return False
    
    def list_serial_ports(self) -> List[str]:
        """List available serial ports based on the operating system."""
        if sys.platform.startswith('win'):  # Windows
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):  # Linux
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):  # macOS
            # Only include known Arduino port patterns on macOS
            ports = []
            # Add common macOS Arduino ports
            ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
            # Exclude known non-Arduino ports
            ports = [p for p in ports if not any(invalid in p for invalid in [
                'debug-console', 'Bluetooth', 'iPhone', 'iPad'])]
        else:
            return []
            
        result = []
        # Test if ports are valid and accessible
        for port in ports:
            try:
                # Attempt to open port briefly to verify it's valid
                s = serial.Serial(port)
                s.close()
                print(f"Found valid port: {port}")
                result.append(port)
            except (OSError, serial.SerialException):
                pass
                
        return result
        
    def connect(self, port: str, baudrate: int = 9600, timeout: float = 0.1) -> bool:
        """Try to establish a connection with the Arduino."""
        try:
            self.connection = serial.Serial(port, baudrate, timeout=timeout)
            self.connected = True
            print(f"Connected to Arduino on port {port}")
            # Save the successful port to settings if we're auto-detecting
            if self.auto_detect and settings['serial']['port'] != port:
                settings['serial']['port'] = port
                try:
                    with open(os.path.join(SCRIPT_DIR, "settings.json"), 'w') as f:
                        json.dump(settings, f, indent=4)
                    print(f"Saved detected port {port} to settings")
                except Exception as e:
                    print(f"Could not save port to settings: {e}")
            return True
        except (serial.SerialException, OSError) as e:
            print(f"Failed to connect to Arduino on port {port}: {e}")
            if not self.auto_detect:
                print("Running in fallback mode (simulation only)")
                self.fallback_mode = True
            self.connection = None
            self.connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if the serial connection is open and working."""
        return self.connected and self.connection and self.connection.is_open
    
    def send_command(self, command: str) -> None:
        """Send a command to Arduino."""
        if self.is_connected():
            try:
                self.connection.write(command.encode('utf-8'))
            except Exception as e:
                print(f"Error sending command to Arduino: {e}")
                self.connected = False
                self.fallback_mode = True
        elif self.fallback_mode:
            # In fallback mode, simulate Arduino responses
            self._process_fallback_command(command)
    
    def _process_fallback_command(self, command: str) -> None:
        """Process commands in fallback mode (Arduino not connected)."""
        print(f"FALLBACK MODE - Processing command: {command}")
        # Simulate Arduino behavior
        if command == "N":
            # Simulate new game confirmation
            global game_active
            game_active = True
            print("FALLBACK MODE - Game started")
        elif command == "E":
            # Simulate end game
            game_active = False
            print("FALLBACK MODE - Game ended")
        elif command == "D":
            # Simulate ball draw
            global balls_drawn, current_ball
            if game_active:
                # Draw a random ball that hasn't been drawn yet
                available_numbers = list(set(range(1, 76)) - set(b.number for b in balls_drawn))
                if available_numbers:
                    new_ball_num = random.choice(available_numbers)
                    new_ball = Ball(new_ball_num)
                    current_ball = new_ball
                    balls_drawn.append(new_ball)
                    
                    # Mark the ball on player cards
                    for card in player_cards:
                        card.mark_number(new_ball_num)
                    
                    # Play sound
                    sound_manager.play_sound("ball_draw")
                    print(f"FALLBACK MODE - Drew ball {new_ball.letter}{new_ball.number}")
    
    def read_message(self) -> str:
        """Read a message from Arduino if available."""
        if self.is_connected() and self.connection.in_waiting > 0:
            try:
                msg = self.connection.read(self.connection.in_waiting).decode('utf-8')
                return msg
            except Exception as e:
                print(f"Error reading from Arduino: {e}")
                self.connected = False
                self.fallback_mode = True
        return ""
    
    def start_game(self) -> None:
        """Send command to start a new game."""
        self.send_command("N")  # New game command
    
    def end_game(self) -> None:
        """Send command to end the current game."""
        self.send_command("E")  # End game command
    
    def close(self) -> None:
        """Close the serial connection."""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connected = False


class SoundManager:
    """Handles loading and playing sound effects and music."""
    
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.load_sounds()
    
    def load_sounds(self) -> None:
        """Load all sound effects from the sounds directory."""
        sound_files = {
            "ball_draw": "ball_draw.wav",
            "bingo": "bingo.wav",
            "button_click": "button_click.wav",
            "win": "win.wav",
            "lose": "lose.wav"
        }
        
        for sound_name, file_name in sound_files.items():
            try:
                self.sounds[sound_name] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, file_name))
            except pygame.error as e:
                print(f"Error loading sound '{file_name}': {e}")
    
    def play_sound(self, sound_name: str) -> None:
        """Play a sound effect by name."""
        if settings['audio']['enabled'] and sound_name in self.sounds:
            self.sounds[sound_name].set_volume(settings['audio']['sfx_volume'])
            self.sounds[sound_name].play()
    
    def play_music(self) -> None:
        """Start playing background music."""
        if settings['audio']['enabled'] and not self.music_playing:
            try:
                # Try WAV first, fall back to MP3 if it fails
                try:
                    pygame.mixer.music.load(os.path.join(SOUNDS_DIR, "background_music.wav"))
                except:
                    pygame.mixer.music.load(os.path.join(SOUNDS_DIR, "background_music.mp3"))
                    
                pygame.mixer.music.set_volume(settings['audio']['music_volume'])
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.music_playing = True
            except pygame.error as e:
                print(f"Error playing background music: {e}")
    
    def stop_music(self) -> None:
        """Stop the current background music."""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False


class GameUI:
    """Handles game rendering and UI interactions."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Calculate scale factors for responsive design
        self.scale_x = self.width / 1080  # Base width reference
        self.scale_y = self.height / 1920  # Base height reference
        self.scale = min(self.scale_x, self.scale_y)  # Use the smaller scale to maintain proportions
        
        # Dynamically size fonts based on screen dimensions
        base_large_size = int(48 * self.scale)
        base_medium_size = int(36 * self.scale)
        base_small_size = int(24 * self.scale)
        
        # Use pygame's default font which is guaranteed to work
        self.font_large = pygame.font.Font(None, max(24, base_large_size))
        self.font_medium = pygame.font.Font(None, max(18, base_medium_size))
        self.font_small = pygame.font.Font(None, max(12, base_small_size))

        # Load background (single color fallback if image loading fails)
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((20, 20, 40))  # Dark blue background
        
        # Try to load image background
        try:
            bg_path = os.path.join(IMAGES_DIR, "background.jpg")
            if os.path.exists(bg_path):
                bg = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(bg, (self.width, self.height))
        except Exception as e:
            print(f"Error loading background: {e}")
            
        # Try to load logo
        self.logo = None
        try:
            logo_path = os.path.join(IMAGES_DIR, "logo.png")
            if os.path.exists(logo_path):
                logo = pygame.image.load(logo_path)
                logo_width = int(self.width * 0.5)
                logo_height = int(logo_width / 4)  # Maintain aspect ratio
                self.logo = pygame.transform.scale(logo, (logo_width, logo_height))
        except Exception as e:
            print(f"Error loading logo: {e}")
            
        # Try to load custom fonts only after everything else is set up
        try:
            font_path = os.path.join(FONTS_DIR, "RobotoCondensed-Regular.ttf")
            if os.path.exists(font_path):
                # Test with small text first to avoid crashes
                test_font = pygame.font.Font(font_path, 12)
                test = test_font.render("Test", True, (255, 255, 255))
                
                # If we reach here, the font works - load the real sizes with proper scaling
                self.font_large = pygame.font.Font(font_path, max(24, base_large_size))
                self.font_medium = pygame.font.Font(font_path, max(18, base_medium_size))
                self.font_small = pygame.font.Font(font_path, max(12, base_small_size))
                print("Custom fonts loaded successfully")
        except Exception as e:
            print(f"Using system fonts - custom font error: {e}")
    
    def render_text(self, font, text, color):
        """Safely render text with fallbacks in case of font issues."""
        try:
            return font.render(text, True, color)
        except Exception as e:
            print(f"Font render error: {e} - using fallback")
            # Use the default pygame font as a fallback
            fallback = pygame.font.Font(None, 24)
            try:
                return fallback.render(text, True, color)
            except:
                # Last resort: create an empty surface with the text dimensions
                surf = pygame.Surface((len(text) * 10, 30), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0))
                return surf
    
    def draw_background(self):
        """Draw the background on the screen."""
        self.screen.blit(self.background, (0, 0))
    
    def draw_header(self):
        """Draw the game header including logo and title."""
        # Calculate responsive header position
        header_y = int(self.height * 0.01)  # 1% from the top
        
        # Draw the logo if available
        if self.logo:
            logo_rect = self.logo.get_rect(midtop=(self.width // 2, header_y))
            self.screen.blit(self.logo, logo_rect)
        else:
            # Draw text title if no logo
            title = self.render_text(self.font_large, "BELGIAN BINGO", settings['colors']['text'])
            title_rect = title.get_rect(midtop=(self.width // 2, header_y))
            self.screen.blit(title, title_rect)
            
        # Add hardware connection status with safe rendering
        status_padding = int(15 * self.scale)  # Scale padding with screen size
        if arduino_bridge and arduino_bridge.fallback_mode:
            status_text = self.render_text(self.font_small, "SIMULATION MODE (No Hardware)", (255, 100, 100))
            status_rect = status_text.get_rect(topright=(self.width - status_padding, status_padding))
            self.screen.blit(status_text, status_rect)
        elif arduino_bridge and arduino_bridge.is_connected():
            status_text = self.render_text(self.font_small, "Hardware Connected", (100, 255, 100))
            status_rect = status_text.get_rect(topright=(self.width - status_padding, status_padding))
            self.screen.blit(status_text, status_rect)
        else:
            status_text = self.render_text(self.font_small, "Hardware Disconnected", (255, 100, 100))
            status_rect = status_text.get_rect(topright=(self.width - status_padding, status_padding))
            self.screen.blit(status_text, status_rect)
    
    def draw_current_ball(self, ball: Ball) -> None:
        """Draw the current drawn ball."""
        if ball:
            # Calculate responsive positioning
            ball_size = int(120 * self.scale)  # Scale ball size
            ball_y = int(self.height * 0.12)  # 12% from the top
            
            # Scale the ball image to the appropriate size
            scaled_ball = pygame.transform.scale(ball.image, (ball_size, ball_size))
            ball_rect = scaled_ball.get_rect(center=(self.width // 2, ball_y))
            self.screen.blit(scaled_ball, ball_rect)
            
            # Draw ball info text
            ball_text = self.render_text(self.font_medium, f"Current Ball: {ball.letter}{ball.number}", settings['colors']['text'])
            text_rect = ball_text.get_rect(midtop=(self.width // 2, ball_y + ball_size // 2 + int(10 * self.scale)))
            self.screen.blit(ball_text, text_rect)
    
    def draw_recently_drawn_balls(self, balls: List[Ball]) -> None:
        """Draw the list of recently drawn balls."""
        if not balls:
            return
            
        # Show the last 10 balls (or fewer if less have been drawn)
        recent_balls = balls[-10:] if len(balls) > 10 else balls
        
        # Scale ball size based on screen dimensions
        ball_size = int(50 * self.scale)
        spacing = int(10 * self.scale)
        
        # Calculate responsive positioning
        total_width = len(recent_balls) * (ball_size + spacing) - spacing
        start_x = (self.width - total_width) // 2
        ball_y = int(self.height * 0.24)  # 24% from the top
        
        # Draw title
        title = self.render_text(self.font_small, "Recently Drawn:", settings['colors']['text'])
        title_rect = title.get_rect(midtop=(self.width // 2, ball_y - int(40 * self.scale)))
        self.screen.blit(title, title_rect)
        
        # Draw each recent ball
        for i, ball in enumerate(recent_balls):
            # Create a scaled-down version of the ball image
            scaled_img = pygame.transform.scale(ball.image, (ball_size, ball_size))
            x_pos = start_x + i * (ball_size + spacing)
            self.screen.blit(scaled_img, (x_pos, ball_y))
            
    def draw_player_card(self, card: BingoCard, index: int = 0) -> None:
        """Draw a player's bingo card."""
        # Calculate responsive card size based on screen width
        # Card should be square but not larger than 80% of screen width
        card_width = min(self.width * 0.8, self.height * 0.5)
        card_height = card_width  # Square aspect ratio for the grid itself
        
        # Position card centered horizontally and at proper vertical position
        card_x = (self.width - card_width) // 2
        card_y = int(self.height * 0.35)  # 35% from the top
        
        # Draw card background
        pygame.draw.rect(self.screen, settings['colors']['card_background'], 
                        (card_x, card_y, card_width, card_height))
        pygame.draw.rect(self.screen, settings['colors']['text'], 
                        (card_x, card_y, card_width, card_height), 3)
        
        # Draw BINGO letters at the top
        letters = ['B', 'I', 'N', 'G', 'O']
        cell_width = card_width / 5
        cell_height = card_height / 5
        
        # Draw the cell grid
        for col in range(5):
            for row in range(5):
                cell = card.grid[col][row]
                cell_rect = pygame.Rect(
                    card_x + col * cell_width, 
                    card_y + row * cell_height,
                    cell_width, 
                    cell_height
                )
                
                # Draw the cell border and background
                if col == 0:  # B column header
                    letter_color = (65, 105, 225)  # Blue
                elif col == 1:  # I column header
                    letter_color = (34, 139, 34)  # Green
                elif col == 2:  # N column header
                    letter_color = (255, 0, 0)  # Red
                elif col == 3:  # G column header
                    letter_color = (255, 215, 0)  # Yellow
                elif col == 4:  # O column header
                    letter_color = (138, 43, 226)  # Purple
                
                # Draw column header
                if row == 0:
                    # Draw stronger colored header background
                    header_color = [max(0, min(255, c * 0.8)) for c in letter_color]
                    pygame.draw.rect(self.screen, header_color, cell_rect)
                    letter_surf = self.render_text(self.font_medium, letters[col], (255, 255, 255))
                    letter_rect = letter_surf.get_rect(center=cell_rect.center)
                    self.screen.blit(letter_surf, letter_rect)
                    pygame.draw.rect(self.screen, settings['colors']['text'], cell_rect, 1)
                    continue
                
                # Offset row due to headers
                actual_row = row - 1
                cell = card.grid[col][actual_row]
                    
                # Draw highlighted background if marked
                if cell.is_marked():
                    pygame.draw.rect(self.screen, settings['colors']['ball_colors'][cell.letter], cell_rect)
                    pygame.draw.rect(self.screen, settings['colors']['text'], cell_rect, 1)
                else:
                    pygame.draw.rect(self.screen, settings['colors']['card_background'], cell_rect)
                    pygame.draw.rect(self.screen, settings['colors']['text'], cell_rect, 1)
                
                # Draw number (or FREE for the center space)
                if cell.number == 0:
                    text = self.render_text(self.font_small, "FREE", settings['colors']['text'])
                else:
                    text = self.render_text(self.font_small, str(cell.number), settings['colors']['text'])
                    
                text_rect = text.get_rect(center=cell_rect.center)
                self.screen.blit(text, text_rect)
    
    def draw_score_panel(self) -> None:
        """Draw the score and game statistics panel."""
        # Calculate responsive panel size and position
        panel_width = self.width * 0.9
        panel_height = int(self.height * 0.15)
        panel_x = (self.width - panel_width) // 2
        panel_y = self.height - panel_height - int(20 * self.scale)
        
        # Draw panel background
        pygame.draw.rect(self.screen, settings['colors']['card_background'], 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, settings['colors']['text'], 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw scores and stats
        score_text = self.render_text(self.font_medium, f"Score: {score}", settings['colors']['text'])
        wins_text = self.render_text(self.font_medium, f"Wins: {wins}", settings['colors']['text'])
        games_text = self.render_text(self.font_medium, f"Games: {games_played}", settings['colors']['text'])
        
        # Draw the texts in a row
        section_width = panel_width / 3
        
        score_rect = score_text.get_rect(center=(
            panel_x + section_width * 0.5, 
            panel_y + panel_height / 2
        ))
        wins_rect = wins_text.get_rect(center=(
            panel_x + section_width * 1.5, 
            panel_y + panel_height / 2
        ))
        games_rect = games_text.get_rect(center=(
            panel_x + section_width * 2.5, 
            panel_y + panel_height / 2
        ))
        
        self.screen.blit(score_text, score_rect)
        self.screen.blit(wins_text, wins_rect)
        self.screen.blit(games_text, games_rect)
        
    def draw_game_status(self, status: str) -> None:
        """Draw game status or announcements."""
        # Position in upper part of the card
        status_y = int(self.height * 0.3)
        
        status_text = self.render_text(self.font_medium, status, settings['colors']['text'])
        status_rect = status_text.get_rect(center=(self.width // 2, status_y))
        
        # Draw subtle background behind text
        bg_rect = status_rect.copy()
        bg_rect.inflate_ip(int(20 * self.scale), int(10 * self.scale))
        pygame.draw.rect(self.screen, settings['colors']['card_background'], bg_rect)
        pygame.draw.rect(self.screen, settings['colors']['text'], bg_rect, 1)
        
        self.screen.blit(status_text, status_rect)
        
    def draw_menu(self, options: List[str], selected: int) -> None:
        """Draw a menu with options and highlighted selection."""
        # Calculate responsive spacing
        option_height = int(60 * self.scale)
        menu_height = len(options) * option_height
        menu_y = (self.height - menu_height) // 2
        
        for i, option in enumerate(options):
            if i == selected:
                color = (255, 255, 0)  # Yellow for selected
            else:
                color = settings['colors']['text']
                
            text = self.render_text(self.font_medium, option, color)
            text_rect = text.get_rect(center=(self.width // 2, menu_y + i * option_height))
            
            # Draw background for selected item
            if i == selected:
                bg_rect = text_rect.copy()
                bg_rect.inflate_ip(int(20 * self.scale), int(10 * self.scale))
                pygame.draw.rect(self.screen, settings['colors']['card_highlight'], bg_rect)
                pygame.draw.rect(self.screen, color, bg_rect, 2)
            
            self.screen.blit(text, text_rect)


class SettingsScreen:
    """Handles the settings menu and configuration."""
    
    def __init__(self, screen: pygame.Surface, ui: GameUI):
        self.screen = screen
        self.ui = ui
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Settings categories and options
        self.categories = ["Serial", "Display", "Audio", "Game", "Back to Main Menu"]
        self.current_category = 0
        
        # Serial settings
        self.serial_settings = [
            {"name": "Auto-detect Arduino", "type": "toggle", "value": settings['serial'].get('auto_detect', False)},
            {"name": "Port", "type": "text", "value": settings['serial']['port']}
        ]
        
        # Display settings
        self.display_settings = [
            {"name": "Fullscreen", "type": "toggle", "value": settings['display']['fullscreen']},
            {"name": "FPS", "type": "value", "value": settings['display']['fps'], "min": 30, "max": 120, "step": 10}
        ]
        
        # Audio settings
        self.audio_settings = [
            {"name": "Enable Audio", "type": "toggle", "value": settings['audio']['enabled']},
            {"name": "Music Volume", "type": "slider", "value": settings['audio']['music_volume'], "min": 0.0, "max": 1.0, "step": 0.1},
            {"name": "SFX Volume", "type": "slider", "value": settings['audio']['sfx_volume'], "min": 0.0, "max": 1.0, "step": 0.1}
        ]
        
        # Game settings
        self.game_settings = [
            {"name": "Ball Draw Delay (ms)", "type": "value", "value": settings['game']['ball_draw_delay'], "min": 500, "max": 10000, "step": 500},
            {"name": "Winning Pattern", "type": "option", "value": settings['game']['default_pattern'], 
             "options": ["horizontal", "vertical", "diagonal", "four_corners", "full_card", "any"]}
        ]
        
        self.current_options = self.categories
        self.selected_index = 0
        self.in_submenu = False
        self.current_submenu = None
        self.edit_mode = False
        self.need_reconnect = False
    
    def handle_input(self, event) -> bool:
        """Handle input events. Returns True if settings screen should close."""
        if event.type == pygame.KEYDOWN:
            if self.edit_mode:
                # In edit mode for a specific setting
                if event.key == pygame.K_LEFT:
                    self._adjust_value(-1)
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_RIGHT:
                    self._adjust_value(1)
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    self.edit_mode = False
                    self._save_settings()
                    sound_manager.play_sound("button_click")
            elif self.in_submenu:
                # In a submenu (Display, Audio, Game)
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.current_options)
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.current_options)
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_RETURN:
                    if self.selected_index == len(self.current_options) - 1:  # Back option
                        self.in_submenu = False
                        self.current_submenu = None
                        self.current_options = self.categories
                        self.selected_index = self.current_category
                        
                        # Reconnect Arduino if needed
                        if self.need_reconnect:
                            global arduino_bridge_port
                            arduino_bridge.close()
                            arduino_bridge = ArduinoBridge(
                                settings['serial']['port'],
                                settings['serial']['baudrate'],
                                settings['serial']['timeout']
                            )
                            self.need_reconnect = False
                    else:
                        # Edit the selected setting
                        self.edit_mode = True
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_ESCAPE:
                    self.in_submenu = False
                    self.current_submenu = None
                    self.current_options = self.categories
                    self.selected_index = self.current_category
                    sound_manager.play_sound("button_click")
                    
                    # Reconnect Arduino if needed
                    if self.need_reconnect:
                        global arduino_bridge_port
                        arduino_bridge.close()
                        arduino_bridge = ArduinoBridge(
                            settings['serial']['port'],
                            settings['serial']['baudrate'],
                            settings['serial']['timeout']
                        )
                        self.need_reconnect = False
            else:
                # Main settings menu
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.categories)
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.categories)
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_RETURN:
                    if self.selected_index == len(self.categories) - 1:  # Back to Main Menu
                        return True  # Signal to close settings screen
                    else:
                        self.current_category = self.selected_index
                        self.in_submenu = True
                        self.selected_index = 0
                        
                        # Set current options based on selected category
                        if self.current_category == 0:  # Serial
                            self.current_submenu = "serial"
                            self.current_options = self.serial_settings + [{"name": "Back", "type": "back"}]
                        elif self.current_category == 1:  # Display
                            self.current_submenu = "display"
                            self.current_options = self.display_settings + [{"name": "Back", "type": "back"}]
                        elif self.current_category == 2:  # Audio
                            self.current_submenu = "audio"
                            self.current_options = self.audio_settings + [{"name": "Back", "type": "back"}]
                        elif self.current_category == 3:  # Game
                            self.current_submenu = "game"
                            self.current_options = self.game_settings + [{"name": "Back", "type": "back"}]
                    sound_manager.play_sound("button_click")
                elif event.key == pygame.K_ESCAPE:
                    return True  # Signal to close settings screen
                    
        return False  # Don't close settings screen
    
    def _adjust_value(self, direction: int) -> None:
        """Adjust the value of the currently selected setting."""
        setting = self.current_options[self.selected_index]
        
        if setting["type"] == "toggle":
            setting["value"] = not setting["value"]
            
        elif setting["type"] == "value" or setting["type"] == "slider":
            new_value = setting["value"] + (setting["step"] * direction)
            setting["value"] = max(setting["min"], min(setting["max"], new_value))
            
        elif setting["type"] == "option":
            options = setting["options"]
            current_index = options.index(setting["value"])
            new_index = (current_index + direction) % len(options)
            setting["value"] = options[new_index]
    
    def _save_settings(self) -> None:
        """Save current settings to the global settings dictionary."""
        # Serial settings
        for setting in self.serial_settings:
            if setting["name"] == "Auto-detect Arduino":
                if settings['serial'].get('auto_detect', False) != setting["value"]:
                    settings['serial']['auto_detect'] = setting["value"]
                    self.need_reconnect = True
            elif setting["name"] == "Port":
                if settings['serial']['port'] != setting["value"]:
                    settings['serial']['port'] = setting["value"]
                    self.need_reconnect = True
                
        # Display settings
        for setting in self.display_settings:
            if setting["name"] == "Fullscreen":
                settings['display']['fullscreen'] = setting["value"]
            elif setting["name"] == "FPS":
                settings['display']['fps'] = setting["value"]
                
        # Audio settings
        for setting in self.audio_settings:
            if setting["name"] == "Enable Audio":
                settings['audio']['enabled'] = setting["value"]
            elif setting["name"] == "Music Volume":
                settings['audio']['music_volume'] = setting["value"]
                pygame.mixer.music.set_volume(setting["value"])
            elif setting["name"] == "SFX Volume":
                settings['audio']['sfx_volume'] = setting["value"]
                
        # Game settings
        for setting in self.game_settings:
            if setting["name"] == "Ball Draw Delay (ms)":
                settings['game']['ball_draw_delay'] = setting["value"]
            elif setting["name"] == "Winning Pattern":
                settings['game']['default_pattern'] = setting["value"]
        
        # Save settings to file
        try:
            with open(os.path.join(SCRIPT_DIR, "settings.json"), 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def draw(self) -> None:
        """Draw the settings screen."""
        # Draw background
        self.ui.draw_background()
        
        # Draw title
        title = self.ui.render_text(self.ui.font_large, "Settings", settings['colors']['text'])
        title_rect = title.get_rect(midtop=(self.width // 2, int(self.ui.height * 0.05)))
        self.screen.blit(title, title_rect)
        
        if self.in_submenu:
            # Draw submenu title
            submenu_title = ""
            if self.current_submenu == "serial":
                submenu_title = "Serial Settings"
            elif self.current_submenu == "display":
                submenu_title = "Display Settings"
            elif self.current_submenu == "audio":
                submenu_title = "Audio Settings"
            elif self.current_submenu == "game":
                submenu_title = "Game Settings"
                
            subtitle = self.ui.render_text(self.ui.font_medium, submenu_title, settings['colors']['text'])
            subtitle_rect = subtitle.get_rect(midtop=(self.width // 2, int(self.ui.height * 0.15)))
            self.screen.blit(subtitle, subtitle_rect)
            
            option_height = int(50 * self.ui.scale)
            menu_y = int(self.ui.height * 0.25)
            
            for i, option in enumerate(self.current_options):
                # Option name
                if i == self.selected_index and self.edit_mode:
                    name_color = (255, 255, 0)  # Yellow when editing
                elif i == self.selected_index:
                    name_color = (100, 200, 255)  # Highlight blue
                else:
                    name_color = settings['colors']['text']
                    
                name_text = self.ui.render_text(self.ui.font_medium, option["name"], name_color)
                name_rect = name_text.get_rect(midright=(self.width // 2 - 20, menu_y + i * option_height))
                self.screen.blit(name_text, name_rect)
                
                # Option value (if applicable)
                if option["type"] != "back":
                    if option["type"] == "toggle":
                        value_text = "On" if option["value"] else "Off"
                    elif option["type"] == "slider":
                        value_text = f"{int(option['value'] * 100)}%"
                    elif option["type"] == "option":
                        value_text = option["value"].capitalize()
                    elif option["type"] == "text":
                        value_text = option["value"]
                    else:
                        value_text = str(option["value"])
                        
                    value_color = name_color if i == self.selected_index else settings['colors']['text']
                    value_rendered = self.ui.render_text(self.ui.font_medium, value_text, value_color)
                    value_rect = value_rendered.get_rect(midleft=(self.width // 2 + 20, menu_y + i * option_height))
                    self.screen.blit(value_rendered, value_rect)
                    
                    # Draw slider bar for slider type
                    if option["type"] == "slider" and i == self.selected_index:
                        slider_width = 200 * self.ui.scale
                        slider_height = 10 * self.ui.scale
                        slider_x = self.width // 2 + 20
                        slider_y = menu_y + i * option_height + 20
                        
                        # Background bar
                        pygame.draw.rect(self.screen, (60, 60, 60), 
                                        (slider_x, slider_y, slider_width, slider_height))
                        
                        # Filled portion
                        fill_width = int(slider_width * option["value"])
                        pygame.draw.rect(self.screen, (100, 200, 255), 
                                        (slider_x, slider_y, fill_width, slider_height))
                
                # Draw selection box
                if i == self.selected_index:
                    box_rect = pygame.Rect(
                        self.width // 2 - 250 * self.ui.scale, 
                        menu_y + i * option_height - 15 * self.ui.scale,
                        500 * self.ui.scale, 
                        30 * self.ui.scale
                    )
                    pygame.draw.rect(self.screen, settings['colors']['card_highlight'], box_rect, 2)
                
        else:
            # Draw main menu categories
            option_height = int(70 * self.ui.scale)
            menu_y = int(self.ui.height * 0.3)
            
            for i, category in enumerate(self.categories):
                if i == self.selected_index:
                    color = (255, 255, 0)  # Yellow for selected
                else:
                    color = settings['colors']['text']
                    
                text = self.ui.render_text(self.ui.font_medium, category, color)
                text_rect = text.get_rect(center=(self.width // 2, menu_y + i * option_height))
                
                # Draw background for selected item
                if i == self.selected_index:
                    bg_rect = text_rect.copy()
                    bg_rect.inflate_ip(int(40 * self.ui.scale), int(20 * self.ui.scale))
                    pygame.draw.rect(self.screen, settings['colors']['card_highlight'], bg_rect)
                    pygame.draw.rect(self.screen, color, bg_rect, 2)
                
                self.screen.blit(text, text_rect)
        
        # Draw navigation help
        help_text1 = self.ui.render_text(self.ui.font_small, 
                                         "Arrow Keys: Navigate | Enter: Select | Escape: Back", 
                                         settings['colors']['text'])
        help_rect1 = help_text1.get_rect(midbottom=(self.width // 2, self.height - 30))
        self.screen.blit(help_text1, help_rect1)
        
        if self.edit_mode:
            help_text2 = self.ui.render_text(self.ui.font_small, 
                                            "Left/Right: Adjust Value | Enter: Confirm", 
                                            settings['colors']['text'])
            help_rect2 = help_text2.get_rect(midbottom=(self.width // 2, self.height - 60))
            self.screen.blit(help_text2, help_rect2)


def load_settings() -> Dict:
    """Load game settings from settings.json."""
    try:
        with open(os.path.join(SCRIPT_DIR, "settings.json")) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading settings: {e}")
        # Return default settings
        return {
            "serial": {"port": "/dev/ttyACM0", "baudrate": 9600, "timeout": 0.1, "auto_detect": False},
            "display": {"width": 1080, "height": 1920, "fullscreen": True, "fps": 60},
            "audio": {"enabled": True, "music_volume": 0.5, "sfx_volume": 0.8},
            "game": {
                "max_balls": 75,
                "ball_draw_delay": 3000,
                "winning_patterns": ["horizontal", "vertical", "diagonal", "four_corners", "full_card"],
                "default_pattern": "horizontal"
            },
            "colors": {
                "background": [20, 20, 40],
                "text": [255, 255, 255],
                "card_background": [30, 30, 60],
                "card_highlight": [60, 60, 100],
                "ball_colors": {
                    "B": [65, 105, 225],
                    "I": [34, 139, 34],
                    "N": [255, 0, 0],
                    "G": [255, 215, 0],
                    "O": [138, 43, 226]
                }
            }
        }


def process_arduino_message(message: str):
    """Process messages received from the Arduino."""
    global current_ball
    
    lines = message.strip().split('\n')
    
    for line in lines:
        if not line:
            continue
            
        if line.startswith("BALL:"):
            # Ball has been drawn
            ball_code = line[5:].strip()
            
            # Convert Arduino ball code (A-Y) to number (1-25)
            if 'A' <= ball_code <= 'Y':
                ball_num = ord(ball_code) - ord('A') + 1
                
                # Create a new Ball object
                current_ball = Ball(ball_num)
                balls_drawn.append(current_ball)
                
                # Mark the ball on player cards
                for card in player_cards:
                    card.mark_number(ball_num)
                
                # Play sound
                sound_manager.play_sound("ball_draw")
                
        elif line == "BALL_RELEASED":
            # Ball has been physically released
            print("Ball released through gate")
            
        elif line == "BALL_RETURNED":
            # Ball has been returned
            print("Ball returned to the tray")
            
        elif line == "GAME_STARTED":
            # Game has started confirmation
            global game_active
            game_active = True
            
        elif line == "GAME_ENDED":
            # Game has ended confirmation
            game_active = False


def check_for_bingo() -> bool:
    """Check all player cards for bingo according to the winning pattern."""
    pattern = settings['game']['default_pattern']
    
    for card in player_cards:
        if card.check_for_win(pattern):
            return True
    
    return False


def new_game() -> None:
    """Start a new bingo game."""
    global balls_drawn, current_ball, player_cards, game_active, games_played
    
    # Reset game state
    balls_drawn = []
    current_ball = None
    
    # Create a new bingo card for the player
    player_cards = [BingoCard()]
    
    # Connect to Arduino and start the game
    if arduino_bridge.is_connected():
        arduino_bridge.start_game()
    
    # Play start sound
    sound_manager.play_sound("button_click")
    
    # Update game stats
    games_played += 1
    game_active = True


def end_game(is_winner: bool) -> None:
    """End the current game."""
    global game_active, score, wins
    
    if is_winner:
        sound_manager.play_sound("win")
        score += 100
        wins += 1
    else:
        sound_manager.play_sound("lose")
    
    if arduino_bridge.is_connected():
        arduino_bridge.end_game()
    
    game_active = False


def draw_ball() -> None:
    """Draw a new bingo ball."""
    if not game_active or arduino_bridge is None:
        return
        
    # Request a new ball from the Arduino system
    arduino_bridge.send_command("D")  # D for draw ball
    
    # The ball will be processed when Arduino sends back the ball code


def main() -> None:
    """Main game function."""
    global settings, serial_conn, arduino_bridge, sound_manager, game_active
    
    # Load settings
    settings = load_settings()
    
    # Set up display
    if settings['display']['fullscreen']:
        screen = pygame.display.set_mode(
            (settings['display']['width'], settings['display']['height']), 
            pygame.FULLSCREEN
        )
    else:
        screen = pygame.display.set_mode(
            (settings['display']['width'], settings['display']['height'])
        )
    
    pygame.display.set_caption("Belgian Bingo")
    
    # Set up Arduino connection
    arduino_bridge = ArduinoBridge(
        settings['serial']['port'],
        settings['serial']['baudrate'],
        settings['serial']['timeout']
    )
    
    # Initialize sound manager
    sound_manager = SoundManager()
    sound_manager.play_music()
    
    # Initialize UI
    ui = GameUI(screen)
    
    # Initialize settings screen
    settings_screen = SettingsScreen(screen, ui)
    
    # Game state
    in_menu = True
    in_settings = False
    menu_options = ["New Game", "Settings", "Quit"]
    selected_option = 0
    
    # Main game loop
    clock = pygame.time.Clock()
    last_ball_draw_time = pygame.time.get_ticks()
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle keyboard input
            if in_settings:
                if settings_screen.handle_input(event):
                    in_settings = False
            elif in_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                        sound_manager.play_sound("button_click")
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                        sound_manager.play_sound("button_click")
                    elif event.key == pygame.K_RETURN:
                        if menu_options[selected_option] == "New Game":
                            in_menu = False
                            new_game()
                        elif menu_options[selected_option] == "Settings":
                            in_settings = True
                        elif menu_options[selected_option] == "Quit":
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            else:
                # In-game controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        in_menu = True
                    elif event.key == pygame.K_SPACE:
                        draw_ball()
        
        # Check for Arduino messages
        if arduino_bridge.is_connected():
            message = arduino_bridge.read_message()
            if message:
                process_arduino_message(message)
        
        # Auto-draw balls at regular intervals when game is active
        if game_active and current_time - last_ball_draw_time >= settings['game']['ball_draw_delay']:
            draw_ball()
            last_ball_draw_time = current_time
        
        # Check for bingo
        if game_active and check_for_bingo():
            end_game(True)
            game_active = False
            in_menu = True
        
        # Draw UI
        ui.draw_background()
        ui.draw_header()
        
        if in_settings:
            settings_screen.draw()
        elif in_menu:
            ui.draw_menu(menu_options, selected_option)
        else:
            if current_ball:
                ui.draw_current_ball(current_ball)
            
            ui.draw_recently_drawn_balls(balls_drawn)
            
            if player_cards:
                ui.draw_player_card(player_cards[0])
            
            ui.draw_score_panel()
            
            if not game_active:
                ui.draw_game_status("GAME OVER - Press ESC for menu")
        
        # Update display
        pygame.display.flip()
        clock.tick(settings['display']['fps'])
    
    # Clean up before quitting
    if arduino_bridge.is_connected():
        arduino_bridge.close()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()