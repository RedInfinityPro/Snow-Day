import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Antarctica: 100 Degrees Colder Simulation")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE_ICE = (173, 216, 230)

# Clock
clock = pygame.time.Clock()

# Load assets
snowflakes = []

# Snowflake generator
def create_snowflake():
    x = random.randint(0, WIDTH)
    y = random.randint(-20, -5)
    speed = random.randint(1, 3)
    size = random.randint(2, 5)
    return {"x": x, "y": y, "speed": speed, "size": size}

# Populate initial snowflakes
for _ in range(100):
    snowflakes.append(create_snowflake())

# Wind effect on snowflakes
def update_snowflakes():
    for flake in snowflakes:
        flake["y"] += flake["speed"]
        flake["x"] += random.choice([-1, 1])  # Simulate slight wind
        if flake["y"] > HEIGHT or flake["x"] < 0 or flake["x"] > WIDTH:
            snowflakes.remove(flake)
            snowflakes.append(create_snowflake())

# Main loop
def main():
    running = True
    global snowflakes
    
    while running:
        screen.fill(DARK_GRAY)  # Dim background for harsh cold feel

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw snowflakes
        for flake in snowflakes:
            pygame.draw.circle(screen, WHITE, (flake["x"], flake["y"]), flake["size"])

        update_snowflakes()

        # Add cold wind and ice effect
        pygame.draw.rect(screen, BLUE_ICE, pygame.Rect(0, HEIGHT - 100, WIDTH, 100))
        pygame.draw.line(screen, GRAY, (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)

        # Display temperature
        font = pygame.font.SysFont("Arial", 28)
        temperature_text = font.render("Temperature: -200°F (-128.9°C)", True, WHITE)
        screen.blit(temperature_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
