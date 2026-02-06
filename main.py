import pygame
import random
import sys
from asteroid_data import fetch_asteroid_data

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREY = (150, 150, 150)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a simple triangle surface
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Draw triangle: (Point 1, Point 2, Point 3)
        pygame.draw.polygon(self.image, WHITE, [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        # Kill bullet if it goes off screen
        if self.rect.bottom < 0:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, data_dict):
        super().__init__()
        self.data = data_dict
        
        # --- 1. Calculate Radius from Diameter ---
        # Map 10m-300m real size to 10px-60px game size
        diameter_m = self.data.get('diameter', 50)
        # Clamp value so it doesn't break the game
        size_factor = max(10, min(diameter_m, 300)) 
        self.radius = int((size_factor / 300) * 50) + 10 

        # --- 2. Calculate Speed from Velocity ---
        # Map 20,000kph-100,000kph to 2-10 game speed
        velocity_kph = self.data.get('velocity', 30000)
        self.fall_speed = max(2, min(int(velocity_kph / 8000), 12))

        # --- 3. Determine Color ---
        self.color = RED if self.data.get('is_hazardous') else GREY

        # Create the image
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
        self.rect = self.image.get_rect()
        
        # Initialize position
        self.respawn()

    def respawn(self):
        """Reset to the top at a random X position."""
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        # Start slightly off-screen so they slide in
        self.rect.y = random.randint(-150, -40)

    def update(self):
        self.rect.y += self.fall_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NASA Asteroid Defender")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    game_over_font = pygame.font.SysFont("Arial", 48)

    # --- Fetch Data ---
    # We call your other script here!
    print("Initializing Game System...")
    asteroid_list = fetch_asteroid_data()
    
    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    asteroids_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Create Asteroid Objects from Data
    # If API gives 10 objects, we make 10 enemies.
    for data in asteroid_list:
        ast = Asteroid(data)
        all_sprites.add(ast)
        asteroids_group.add(ast)

    score = 0
    running = True
    game_over = False

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet = player.shoot()
                        all_sprites.add(bullet)
                        bullets_group.add(bullet)
            else:
                # Restart on key press if game over
                if event.type == pygame.KEYDOWN:
                    # Reset game
                    game_over = False
                    score = 0
                    bullets_group.empty()
                    # Reset all asteroids to top
                    for ast in asteroids_group:
                        ast.respawn()

        # 2. Update
        if not game_over:
            all_sprites.update()

            # Collision: Bullet hits Asteroid
            hits = pygame.sprite.groupcollide(asteroids_group, bullets_group, False, True)
            for hit_asteroid in hits:
                score += 100
                print(f"Destroyed: {hit_asteroid.data['name']}!")
                hit_asteroid.respawn()

            # Collision: Asteroid hits Player
            hits = pygame.sprite.spritecollide(player, asteroids_group, False)
            if hits:
                game_over = True
                print("GAME OVER - Impact Detected!")

        # 3. Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # Draw Asteroid Names (Optional Text)
        for ast in asteroids_group:
            text_surf = font.render(ast.data['name'], True, WHITE)
            # Center text above the asteroid
            text_rect = text_surf.get_rect(center=(ast.rect.centerx, ast.rect.top - 10))
            screen.blit(text_surf, text_rect)

        # Draw UI
        score_text = font.render(f"Score: {score}", True, GREEN)
        screen.blit(score_text, (10, 10))

        if game_over:
            go_text = game_over_font.render("GAME OVER", True, RED)
            go_rect = go_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(go_text, go_rect)
            
            sub_text = font.render("Press any key to restart", True, WHITE)
            sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(sub_text, sub_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()