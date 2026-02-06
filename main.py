import pygame
import random
import sys
import math
import datetime
from asteroid_data import fetch_asteroid_data, fetch_apod_image

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Colors ---
SPACE_BG = (10, 10, 20)      
WHITE = (255, 255, 255)
STAR_DIM = (100, 100, 150)   
STAR_BRIGHT = (255, 255, 255)
NEON_CYAN = (0, 255, 255)    
NEON_RED = (255, 50, 50)     
ROCK_GREY = (160, 160, 170)  
ENGINE_ORANGE = (255, 165, 0)
ENGINE_YELLOW = (255, 255, 0)

# --- Helper Functions ---
def create_jagged_rock(radius, color):
    size = radius * 2 + 10
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    points = []
    num_points = random.randint(8, 14)
    for i in range(num_points):
        angle = math.radians(i * (360 / num_points))
        r = radius * random.uniform(0.7, 1.1)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    
    pygame.draw.polygon(surf, color, points)
    pygame.draw.polygon(surf, (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255)), points, 2)
    return surf

def format_number(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    return f"{n/1_000:.0f}K"

def log_mission(status, date_str, closest_name, closest_dist):
    """Writes the mission result to a local text file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] MISSION: {date_str} | STATUS: {status} | "
        f"CLOSEST: {closest_name} ({closest_dist:,.0f} km)\n"
    )
    
    try:
        with open("FLIGHT_RECORDER.txt", "a") as f:
            f.write(log_entry)
        print("Mission logged to FLIGHT_RECORDER.txt")
    except Exception as e:
        print(f"Recorder Error: {e}")

# --- Sprite Classes ---
class Particle(pygame.sprite.Sprite):
    """Engine exhaust"""
    def __init__(self, x, y):
        super().__init__()
        self.size = random.randint(2, 5)
        self.image = pygame.Surface((self.size, self.size))
        color = random.choice([ENGINE_ORANGE, ENGINE_YELLOW, NEON_RED])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.life = 15 
        self.speed_y = random.randint(2, 5)
        self.speed_x = random.randint(-1, 1)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        self.life -= 1
        if self.life <= 0: self.kill()

class ExplosionShard(pygame.sprite.Sprite):
    """Explosion debris"""
    def __init__(self, x, y, color):
        super().__init__()
        self.size = random.randint(3, 8)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.life = 30 
        self.vel_x = random.uniform(-6, 6)
        self.vel_y = random.uniform(-6, 6)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0: self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, NEON_CYAN, [(20, 0), (0, 40), (20, 30), (40, 40)])
        pygame.draw.polygon(self.image, WHITE, [(20, 10), (15, 25), (25, 25)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50
        self.speed = 6
        self.ammo = 1

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += self.speed

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return Bullet(self.rect.centerx, self.rect.top)
        return None

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 20), pygame.SRCALPHA)
        self.image.fill((255, 255, 0)) 
        pygame.draw.rect(self.image, WHITE, (1, 1, 4, 18))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 15

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0: self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, data_dict):
        super().__init__()
        self.data = data_dict
        diameter_m = self.data.get('diameter', 50)
        size_factor = max(20, min(diameter_m, 350)) 
        self.radius = int((size_factor / 350) * 100) + 20
        
        velocity_kph = self.data.get('velocity', 30000)
        self.fall_speed = max(5, min(velocity_kph / 5000, 15))
        self.drift_speed = random.choice([-2, -1, 0, 1, 2])

        # --- FIX: Save the color as an attribute so ExplosionShard can use it ---
        self.color = NEON_RED if self.data.get('is_hazardous') else ROCK_GREY
        
        self.image = create_jagged_rock(self.radius, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-2500, -100)

    def update(self):
        self.rect.y += self.fall_speed
        self.rect.x += self.drift_speed 
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH: self.drift_speed *= -1
        if self.rect.top > SCREEN_HEIGHT: self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self, layer):
        super().__init__()
        self.layer = layer 
        size = layer
        color = STAR_DIM if layer == 1 else STAR_BRIGHT
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = random.randint(0, SCREEN_HEIGHT)
        
    def update(self):
        self.rect.y += (self.layer * 1.5) 
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = 0
            self.rect.x = random.randint(0, SCREEN_WIDTH)

# --- MAIN ---
def main():
    print("\n--- NASA ASTEROID DEFENDER SYSTEM ---")
    user_date = input("Enter mission date (YYYY-MM-DD) or press ENTER for Today: ")
    if user_date.strip() == "":
        user_date = None 
        display_date = "TODAY"
    else:
        display_date = user_date
    
    print("Initializing Radar...")
    asteroid_list = fetch_asteroid_data(user_date)
    total_asteroids = len(asteroid_list)
    
    if total_asteroids > 0:
        closest_rock = min(asteroid_list, key=lambda x: x['miss_distance'])
        closest_name = closest_rock['name']
        closest_dist = closest_rock['miss_distance']
    else:
        closest_name = "None"
        closest_dist = 0
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Mission Date: {display_date}")
    clock = pygame.time.Clock()
    
    ui_font = pygame.font.SysFont("Courier New", 20, bold=True)
    name_font = pygame.font.SysFont("Arial", 12, bold=True)
    big_font = pygame.font.SysFont("Courier New", 40, bold=True) 

    # Background
    bg_file = fetch_apod_image()
    background_surf = None
    if bg_file:
        try:
            loaded_bg = pygame.image.load(bg_file)
            background_surf = pygame.transform.scale(loaded_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0,0,0))
            background_surf.blit(overlay, (0,0))
        except: pass

    # Groups
    all_sprites = pygame.sprite.Group()
    asteroids_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    particles_group = pygame.sprite.Group()
    
    player = None

    def reset_level():
        nonlocal player
        all_sprites.empty()
        asteroids_group.empty()
        bullets_group.empty()
        particles_group.empty()

        for _ in range(30): all_sprites.add(Star(1))
        for _ in range(20): all_sprites.add(Star(2))
        for _ in range(10): all_sprites.add(Star(3))

        player = Player()
        all_sprites.add(player)

        for data in asteroid_list:
            ast = Asteroid(data)
            all_sprites.add(ast)
            asteroids_group.add(ast)

    reset_level()

    running = True
    game_state = "PLAYING"
    logged_once = False 

    while running:
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
                    if event.key == pygame.K_r:
                        reset_level()
                        game_state = "PLAYING"
                        logged_once = False
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False

        if game_state == "PLAYING":
            p = Particle(player.rect.centerx, player.rect.bottom)
            all_sprites.add(p)
            particles_group.add(p)
            all_sprites.update()
            
            # 1. Bullet vs Asteroid
            hits = pygame.sprite.groupcollide(asteroids_group, bullets_group, True, True)
            for hit_ast in hits:
                # Spawn Shatter Debris
                for _ in range(25): 
                    shard = ExplosionShard(hit_ast.rect.centerx, hit_ast.rect.centery, hit_ast.color)
                    all_sprites.add(shard)
                    particles_group.add(shard)

            # 2. Player vs Asteroid
            if pygame.sprite.spritecollide(player, asteroids_group, False, pygame.sprite.collide_circle):
                game_state = "LOST"

            # 3. Win Condition
            if len(asteroids_group) == 0:
                game_state = "WON"

        # --- LOGGING ---
        if game_state in ["WON", "LOST"] and not logged_once:
            log_mission(game_state, display_date, closest_name, closest_dist)
            logged_once = True

        # --- Draw Phase ---
        if background_surf: screen.blit(background_surf, (0, 0))
        else: screen.fill(SPACE_BG)
        all_sprites.draw(screen)

        for ast in asteroids_group:
            if ast.rect.bottom > 0 and ast.rect.top < SCREEN_HEIGHT:
                name_text = name_font.render(ast.data['name'], True, (200, 200, 200))
                text_rect = name_text.get_rect(center=(ast.rect.centerx, ast.rect.top - 10))
                screen.blit(name_text, text_rect)

        if game_state == "PLAYING":
            color = NEON_CYAN if player.ammo > 0 else NEON_RED
            ammo_text = ui_font.render(f"MISSILES: {player.ammo}", True, color)
            screen.blit(ammo_text, (10, SCREEN_HEIGHT - 30))
            
            help_text = name_font.render("[SPACE] TO SHOOT", True, (150, 150, 150))
            screen.blit(help_text, (160, SCREEN_HEIGHT - 28))

            remaining = len(asteroids_group)
            rem_text = ui_font.render(f"THREATS: {remaining}/{total_asteroids}", True, WHITE)
            screen.blit(rem_text, (10, 10))

        elif game_state == "LOST":
            text = big_font.render("CRITICAL FAILURE", True, NEON_RED)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            screen.blit(text, rect)
            
            report = ui_font.render(f"Closest: {closest_name} ({format_number(closest_dist)} km)", True, WHITE)
            rep_rect = report.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            screen.blit(report, rep_rect)
            
            log_text = name_font.render("Report saved to FLIGHT_RECORDER.txt", True, (100, 100, 100))
            log_rect = log_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
            screen.blit(log_text, log_rect)

            sub = ui_font.render("[R] Restart   [Q] Quit", True, WHITE)
            sub_rect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            screen.blit(sub, sub_rect)

        elif game_state == "WON":
            text = big_font.render("ORBIT SECURE", True, NEON_CYAN)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            screen.blit(text, rect)
            
            report = ui_font.render(f"Closest Shave: {closest_name}", True, NEON_RED)
            rep_rect = report.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            screen.blit(report, rep_rect)
            
            dist_text = ui_font.render(f"Distance: {closest_dist:,.0f} km", True, WHITE)
            dist_rect = dist_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            screen.blit(dist_text, dist_rect)
            
            log_text = name_font.render("Report saved to FLIGHT_RECORDER.txt", True, (100, 100, 100))
            log_rect = log_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
            screen.blit(log_text, log_rect)
            
            sub = ui_font.render("[R] Restart   [Q] Quit", True, WHITE)
            sub_rect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            screen.blit(sub, sub_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()