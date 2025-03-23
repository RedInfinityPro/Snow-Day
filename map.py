import sys
import pygame
import random, time
from perlin_noise import PerlinNoise

# weather
class Weather:
    def __init__(self):
        self.time = 0  # Represents in-game time (0-24 hours)
        self.day_length = 60  # Seconds for a full day
        self.weather_types = ["clear", "overcast", "snowstorm", "fog", "methane rain", "nitrogen snow"]
        self.frostbite_risk = random.choice(["Instantaneous", "Severe", "Critical"])
        self.current_weather = random.choice(self.weather_types)
        self.weather_timer = time.time() + random.randint(10, 30)  # Next weather change
        self.update_weather_values()

    def update_weather_values(self):
        """Generates weather values dynamically."""
        base_temp = -272.5
        variation = 1.5
        self.current_temperature = round(random.uniform(base_temp - variation, base_temp + variation), 2)
        # Wind speeds
        self.wind_speed = round(random.uniform(5, 30), 2)
        self.wind_direction = random.choice(["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"])

        self.feels_like = round(max(self.current_temperature - (self.wind_speed / 20), -273.15), 2)
        self.pressure = round(random.uniform(0.01, 0.05), 3)
        # At these temperatures, exposure would be instantly fatal to humans
        self.exposure_risk = "Instantly Fatal"

        # Special effects for different weather types
        if self.current_weather == "methane rain":
            self.precipitation_type = "liquid methane"
            self.visibility = round(random.uniform(5, 20), 1)
        elif self.current_weather == "nitrogen snow":
            self.precipitation_type = "solid nitrogen"
            self.visibility = round(random.uniform(2, 10), 1)
        elif self.current_weather == "snowstorm":
            self.precipitation_type = "hydrogen ice crystals"
            self.visibility = round(random.uniform(1, 5), 1)
        elif self.current_weather == "fog":
            self.precipitation_type = "helium mist"
            self.visibility = round(random.uniform(3, 8), 1)
        else:
            self.precipitation_type = "none"
            self.visibility = round(random.uniform(20, 100), 1)

    def get_lighting(self):
        """Returns a color overlay based on time of day."""
        if 6 <= self.time < 18:  # Daytime
            return (255, 255, 255, 50)  # Light overlay
        elif 18 <= self.time < 21 or 3 <= self.time < 6:  # Dawn/Dusk
            return (50, 50, 100, 100)  # Dark blue tint
        else:  # Night
            return (0, 0, 25, 150)  # Dark overlay

    def draw(self, screen):
        """Draws weather effects and lighting."""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill(self.get_lighting())  # Apply lighting
        screen.blit(overlay, (0, 0))

        if self.current_weather == "snowstorm":
            for _ in range(100):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.circle(screen, (220, 240, 255), (x, y), random.uniform(0.1, 0.3))
        elif self.current_weather == "methane rain":
            for _ in range(80):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.line(screen, (100, 150, 220), (x, y), (x + random.uniform(-2, 2), y + 10), 2)
        elif self.current_weather == "nitrogen snow":
            for _ in range(70):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.circle(screen, (200, 225, 255), (x, y), random.uniform(0.2, 0.4))
        elif self.current_weather == "fog":
            fog_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fog_overlay.fill((180, 180, 220, 120))
            screen.blit(fog_overlay, (0, 0))
            # Add swirling fog particles
            for _ in range(30):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.circle(screen, (200, 200, 240, 60), (x, y), random.uniform(0.10, 0.30))

    def update(self):
        """Update time and weather conditions."""
        self.time = (time.time() % self.day_length) / self.day_length * 24  # Simulate 24-hour cycle

        if time.time() > self.weather_timer:
            self.current_weather = random.choice(self.weather_types)
            self.update_weather_values()  # Refresh weather data
            self.weather_timer = time.time() + random.randint(15, 45)

    def get_weather_report(self):
        """Returns a formatted string with current weather conditions."""
        return {
            "Temperature": self.current_temperature,
            "Weather": self.current_weather.capitalize(),
            "Wind": (self.wind_speed, self.wind_direction),
            "Feels like": self.feels_like,
            "Atmospheric pressure": self.pressure,
            "Visibility":self.visibility,
            "Exposure risk": self.exposure_risk,
            "Precipitation": self.precipitation_type
        }

# ground
class Segment:
    def __init__(self, x, y, width, height, color):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update_color(self, new_color):
        self.color = new_color

class Ground:
    def __init__(self, screen_width, screen_height, cell_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.width = screen_width // cell_size[0]
        self.height = screen_height // cell_size[1]
        # Constants for extreme cold environment
        self.AVG_ANTARCTICA_TEMP = -60  # Avg temp in Antarctica (°C)
        self.EXTREME_COLD_FACTOR = 100  # Scaling factor
        self.BASE_TEMP = self.AVG_ANTARCTICA_TEMP * self.EXTREME_COLD_FACTOR
        # Cache for generated chunks
        self.chunk_size = 16  # Size of each chunk in cells
        self.chunks = {}  # Dictionary to store generated chunks
        # noise
        self.noise = PerlinNoise(octaves=4, seed=sys.maxsize)
        # biomes
        self.BIOMES = self.get_biomes()

    def get_biomes(self):
        # Biomes suitable for extreme cold
        BIOMES = {
            'deep_frozen_ocean': (0, 0, 80),
            'frozen_ocean': (0, 20, 150),
            'ice_shelf': (200, 200, 255),
            'glacier': (220, 220, 220),
            'permafrost': (150, 150, 150),
            'polar_desert': (180, 180, 180),
            'snow_fields': (255, 255, 255)
        }
        return BIOMES

    def set_biome(self, temperature):
        if temperature < self.BASE_TEMP + 5:
            return 'deep_frozen_ocean'
        elif temperature < self.BASE_TEMP + 10:
            return 'frozen_ocean'
        elif temperature < self.BASE_TEMP + 15:
            return 'ice_shelf'
        elif temperature < self.BASE_TEMP + 20:
            return 'glacier'
        elif temperature < self.BASE_TEMP + 25:
            return 'permafrost'
        elif temperature < self.BASE_TEMP + 30:
            return 'polar_desert'
        else:
            return 'snow_fields'

    def get_temperature(self, world_x, world_y):
        # Get temperature value for world coordinates
        noise_value = self.noise([world_x / 200, world_y / 200])
        return self.BASE_TEMP + (noise_value * 40)

    def get_chunk_key(self, chunk_x, chunk_y):
        return f"{chunk_x}_{chunk_y}"

    def generate_chunk(self, chunk_x, chunk_y):
        """Generate a new chunk at the specified chunk coordinates"""
        chunk_key = self.get_chunk_key(chunk_x, chunk_y)

        if chunk_key in self.chunks:
            return self.chunks[chunk_key]

        chunk_data = []
        for x in range(self.chunk_size):
            for y in range(self.chunk_size):
                # Convert chunk coords to world coords
                world_x = (chunk_x * self.chunk_size) + x
                world_y = (chunk_y * self.chunk_size) + y

                # Get world position in pixels
                pixel_x = world_x * self.cell_size[0]
                pixel_y = world_y * self.cell_size[1]

                # Get terrain data at this position
                temperature = self.get_temperature(world_x, world_y)
                biome = self.set_biome(temperature)
                color = self.BIOMES[biome]

                # Create segment
                segment = Segment(pixel_x, pixel_y, self.cell_size[0], self.cell_size[1], color)
                chunk_data.append(segment)

        self.chunks[chunk_key] = chunk_data
        return chunk_data

    def draw(self, screen, camera_x, camera_y):
        """Draw visible chunks based on camera position"""
        # Convert camera position (player world position) to chunk coordinates
        center_chunk_x = camera_x // (self.chunk_size * self.cell_size[0])
        center_chunk_y = camera_y // (self.chunk_size * self.cell_size[1])

        # Calculate pixel offset within the chunk
        offset_x = -(camera_x % (self.chunk_size * self.cell_size[0]))
        offset_y = -(camera_y % (self.chunk_size * self.cell_size[1]))

        # Calculate screen center
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2

        # Determine visible chunks
        chunks_visible_x = (screen.get_width() // (self.chunk_size * self.cell_size[0])) + 2
        chunks_visible_y = (screen.get_height() // (self.chunk_size * self.cell_size[1])) + 2

        # Draw all visible chunks
        for chunk_x_offset in range(-chunks_visible_x, chunks_visible_x + 1):
            for chunk_y_offset in range(-chunks_visible_y, chunks_visible_y + 1):
                chunk_x = int(center_chunk_x) + chunk_x_offset
                chunk_y = int(center_chunk_y) + chunk_y_offset
                chunk = self.generate_chunk(chunk_x, chunk_y)

                for segment in chunk:
                    # Calculate segment's screen position
                    screen_x = segment.x - camera_x + screen_center_x
                    screen_y = segment.y - camera_y + screen_center_y

                    # Check if segment is visible on screen
                    if (screen_x + segment.width > 0 and
                            screen_x < screen.get_width() and
                            screen_y + segment.height > 0 and
                            screen_y < screen.get_height()):
                        # Draw segment at offset position
                        pygame.draw.rect(screen, segment.color,
                                         (screen_x, screen_y,
                                          segment.width, segment.height))