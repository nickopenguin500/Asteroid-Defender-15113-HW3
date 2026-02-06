import pygame
import random
import sys
from asteroid_data import fetch_asteroid_data

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 15) # Deep space blue
WHITE = (220, 220, 220)
RED = (255, 60, 60)
GREY = (100, 100, 100)
YELLOW = (255, 200, 0)
GREEN = (50, 255, 50)
CYAN = (0, 255, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Make the ship smaller and more nimble
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        # Draw a cool little ship
        pygame.draw.polygon(self.image, CYAN, [(15, 0), (0, 30), (30, 30)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50
        self.speed = 7
        self.ammo = 3  # LIMITED AMMO

    def update(self):
        keys = pygame.key.get_pressed()
        
        # X-Axis Movement
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            
        # Y-Axis Movement (New!)
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return Bullet(self.rect.centerx, self.rect.top)
        return None

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 12

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, data_dict):
        super().__init__()
        self.data = data_dict
        
        # --- 1. Size ---
        diameter_m = self.data.get('diameter', 50)
        size_factor = max(15, min(diameter_m, 400)) 
        self.radius = int((size_factor / 400) * 60) + 10 
        
        # --- 2. Speed (FASTER now) ---
        velocity_kph = self.data.get('velocity', 30000)
        # Updated Scale: Faster divisor and higher cap
        # Fast rocks will now drop at up to 12px per frame
        self.fall_speed = max(3, min(velocity_kph / 6000, 12))

        # --- 3. Color ---
        self.color = RED if self.data.get('is_hazardous') else GREY

        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        
        # --- 4. Spawn Logic ---
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        # Spawn them spread out far above the screen
        self.rect.y = random.randint(-4000, -100)

    def update(self):
        self.rect.y += self.fall_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Star(pygame.sprite.Sprite):
    """Simple background star for scrolling effect"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = 0
            self.rect.x = random.randint(0, SCREEN_WIDTH)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NASA Asteroid Dodger: Daily Feed")
    clock = pygame.time.Clock()
    
    # Fonts
    ui_font = pygame.font.SysFont("Courier New", 20, bold=True)
    name_font = pygame.font.SysFont("Arial", 12) # Small font for names
    big_font = pygame.font.SysFont("Courier New", 50, bold=True)

    # --- Fetch Data ---
    print("Downloading Daily Asteroid Feed...")
    asteroid_list = fetch_asteroid_data()
    total_asteroids = len(asteroid_list)
    
    # Groups
    all_sprites = pygame.sprite.Group()
    asteroids_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    stars_group = pygame.sprite.Group()

    # Create Stars
    for _ in range(50):
        star = Star()
        all_sprites.add(star)
        stars_group.add(star)

    # Create Player
    player = Player()
    all_sprites.add(player)

    # Create Asteroids
    for data in asteroid_list:
        ast = Asteroid(data)
        all_sprites.add(ast)
        asteroids_group.add(ast)

    running = True
    game_state = "PLAYING" # PLAYING, WON, LOST

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet = player.shoot()
                        if bullet:
                            all_sprites.add(bullet)
                            bullets_group.add(bullet)

            elif game_state in ["WON", "LOST"]:
                if event.type == pygame.KEYDOWN:
                    running = False

        # 2. Update
        if game_state == "PLAYING":
            all_sprites.update()

            # Collision: Bullet hits Asteroid
            hits = pygame.sprite.groupcollide(asteroids_group, bullets_group, True, True)
            
            # Collision: Player hits Asteroid
            if pygame.sprite.spritecollide(player, asteroids_group, False):
                game_state = "LOST"

            # Check Win Condition
            if len(asteroids_group) == 0:
                game_state = "WON"

        # 3. Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # Draw Asteroid Names (New!)
        for ast in asteroids_group:
            # Only draw name if it's on screen
            if ast.rect.bottom > 0 and ast.rect.top < SCREEN_HEIGHT:
                name_text = name_font.render(ast.data['name'], True, WHITE)
                # Center text above the asteroid
                text_rect = name_text.get_rect(center=(ast.rect.centerx, ast.rect.top - 10))
                screen.blit(name_text, text_rect)

        # UI Overlay
        if game_state == "PLAYING":
            ammo_text = ui_font.render(f"MISSILES: {player.ammo}", True, YELLOW)
            screen.blit(ammo_text, (10, SCREEN_HEIGHT - 30))
            
            remaining = len(asteroids_group)
            rem_text = ui_font.render(f"THREATS: {remaining}/{total_asteroids}", True, WHITE)
            screen.blit(rem_text, (10, 10))

        elif game_state == "LOST":
            text = big_font.render("IMPACT DETECTED", True, RED)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, rect)
            
            sub = ui_font.render("Press any key to exit.", True, WHITE)
            sub_rect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(sub, sub_rect)

        elif game_state == "WON":
            text = big_font.render("ORBIT CLEAR", True, GREEN)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, rect)
            
            sub = ui_font.render("Daily Feed Survived.", True, WHITE)
            sub_rect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(sub, sub_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()