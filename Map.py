import pygame
import random, sys, time, math
from perlin_noise import PerlinNoise
pygame.init()
current_time = time.time()
random.seed(current_time)

# ground
class Segment:
    def __init__(self, x, y, width, height, color):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.color = color
        self.clicked = False
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update_color(self, new_color):
        self.color = new_color

# map
class Ground:
    def __init__(self, screen_width, screen_height, cell_size, weather_panel):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.width = screen_width // self.cell_size[0]
        self.height = screen_height // self.cell_size[1]
        
        # Direct reference to weather panel
        self.weather_panel = weather_panel
        self.weather_values = self.weather_panel.weather_values
        self.wind_vector = (0, 0)
        self.wind_speed = 0
        # Terrain generation parameters - Extreme Cold Version
        self.freq = random.uniform(30, 80)  # More variation in terrain
        self.amp = random.uniform(20, 50)   # Higher amplitude for more jagged landscapes
        self.octaves = random.randint(5, 10) # More octaves for extreme details
        self.seed = random.randint(0, sys.maxsize)
        
        # Biome thresholds for extreme frozen wasteland
        self.ice_threshold = random.uniform(-1.0, -0.8)
        self.frozen_water_threshold = random.uniform(-0.8, -0.6)
        self.tundra_threshold = random.uniform(-0.6, -0.4)
        self.snow_threshold = random.uniform(-0.4, -0.1)
        self.rocky_threshold = random.uniform(-0.1, 0.2)
        self.mountain_threshold = 0.2
        
        # Sync time of day with weather panel
        self.time_of_day = self.weather_panel.time_of_day
        self.day_length = self.weather_panel.day_length
        self.last_update = pygame.time.get_ticks()
        
        # Weather
        self.weather = "blizzard"
        self.weather_timer = random.randint(20, 60)
        self.weather_last_update = pygame.time.get_ticks()
        self.weather_particles = []
        
        # Visuals affected by temperature 
        self.ice_crystallization = 0.0  # How much ice forms (0-1)
        self.color_desaturation = 0.0   # How desaturated colors become (0-1)
        self.deep_freeze_factor = 0.6   # Overall darkness factor
        
        # Aurora effects (visible during clear nights)
        self.aurora_visible = False
        self.aurora_particles = []
        self.aurora_colors = [(0, 255, 100), (0, 200, 255), (100, 0, 255)]
        
        self.segmentList = []
        self.ground_data = self.generate_ground()
        self.build()

    def generate_ground(self):
        base_noise = PerlinNoise(octaves=self.octaves, seed=self.seed)
        detail_noise = PerlinNoise(octaves=self.octaves * 2, seed=self.seed // 2)
        ridge_noise = PerlinNoise(octaves=3, seed=self.seed * 2)
        moisture_noise = PerlinNoise(octaves=4, seed=self.seed + 1000)
        ice_crack_noise = PerlinNoise(octaves=8, seed=self.seed + 2000)
        
        ground_data = []

        for x in range(self.width):
            for y in range(self.height):
                cell_x = x * self.cell_size[0]
                cell_y = y * self.cell_size[1]
                
                base_height = base_noise([cell_x / self.freq, cell_y / self.freq])
                detail_height = detail_noise([cell_x / (self.freq/2), cell_y / (self.freq/2)]) * 0.2
                ridge_value = abs(ridge_noise([cell_x / (self.freq*1.5), cell_y / (self.freq*1.5)])) * 0.7
                
                cell_height = (base_height + detail_height + ridge_value) * self.amp
                moisture = moisture_noise([cell_x / (self.freq*2), cell_y / (self.freq*2)])
                ice_cracks = ice_crack_noise([cell_x / (self.freq/4), cell_y / (self.freq/4)])
                
                biome_type = self.get_biome_type(cell_height, moisture)
                
                normalized_height = (cell_height + self.amp) / (2 * self.amp)
                normalized_height = max(0, min(1, normalized_height))
                
                # Store all relevant data for each cell
                ground_data.append({
                    "position": (cell_x, cell_y),
                    "height": cell_height,
                    "biome": biome_type,
                    "moisture": moisture,
                    "normalized_height": normalized_height,
                    "ice_cracks": ice_cracks
                })

        return ground_data
    
    def get_biome_type(self, height, moisture):
        # More extreme biomes for ultra-cold environments
        if height < self.ice_threshold:
            return 'methane_ice'  # So cold that methane freezes
        elif height < self.frozen_water_threshold:
            return 'nitrogen_seas'  # Liquid nitrogen pools
        elif height < self.tundra_threshold:
            if moisture > 0.6:
                return 'crystalline_formations'
            else:
                return 'deep_frozen_tundra' 
        elif height < self.snow_threshold:
            if moisture > 0.7:
                return 'frozen_gas_vents'
            else:
                return 'carbon_dioxide_snow'  # CO2 snow
        elif height < self.rocky_threshold:
            if moisture > 0.5:
                return 'shattered_glacier'
            else:
                return 'exposed_cryorock'
        else:
            return 'metallic_frost_peaks'  # Metal becomes brittle at these temperatures
    
    def get_biome_color(self, biome_type, brightness, moisture, temp_factor=1.0):
        # Base colors for ultra-cold biomes
        base_colors = {
            'methane_ice': (80, 100, 150),
            'nitrogen_seas': (100, 120, 180),
            'deep_frozen_tundra': (150, 160, 190),
            'crystalline_formations': (170, 190, 220),
            'carbon_dioxide_snow': (200, 210, 230),
            'frozen_gas_vents': (130, 140, 180),
            'shattered_glacier': (180, 190, 220),
            'exposed_cryorock': (140, 150, 180),
            'metallic_frost_peaks': (190, 200, 240)
        }
        
        # Get base color for the biome
        base_color = base_colors.get(biome_type, (220, 230, 250))
        
        # Apply temperature effects (colder = more blue shift, less brightness)
        # Temperature ranges from -950 to -880 Celsius
        temp = self.weather_values['current_temperature']
        temp_normalized = (temp + 950) / 70  # 0 = coldest, 1 = "warmest"
        temp_normalized = max(0, min(1, temp_normalized))
        
        # Apply freezing effects (more intense at lower temperatures)
        freezing_factor = 1 - temp_normalized * 0.4
        
        # Desaturate colors based on extreme cold
        r, g, b = base_color
        gray = (r + g + b) / 3
        r = r * (1 - self.color_desaturation) + gray * self.color_desaturation
        g = g * (1 - self.color_desaturation) + gray * self.color_desaturation
        b = b * (1 - self.color_desaturation) + gray * self.color_desaturation
        base_color = (r, g, b)
        
        # Apply blue shift at extreme cold
        blue_boost = max(0, (1 - temp_normalized) * 30)
        r_adj = max(0, r - blue_boost * 0.5)
        g_adj = max(0, g - blue_boost * 0.3)
        b_adj = min(255, b + blue_boost)
        
        # Apply darkness factor from deep freeze and brightness from height
        adjusted_brightness = self.deep_freeze_factor + brightness * 0.3
        adjusted_color = (
            int(r_adj * adjusted_brightness * temp_factor),
            int(g_adj * adjusted_brightness * temp_factor),
            int(b_adj * adjusted_brightness * freezing_factor * temp_factor)
        )
        
        # Apply small random variation
        color_variation = random.randint(-8, 8)
        final_color = tuple(max(0, min(255, c + color_variation)) for c in adjusted_color)
        
        # Apply day/night cycle tint
        final_color = self.apply_day_night_tint(final_color)
        
        return final_color
    
    def apply_day_night_tint(self, color):
        # Sync with weather panel time of day
        self.time_of_day = self.weather_panel.time_of_day
        
        # Calculate light factor based on time of day (sine wave)
        # Extreme environment: shorter days, longer nights
        if self.time_of_day < 0.3 or self.time_of_day > 0.7:
            # Longer night period (70% of day)
            night_factor = 0.15 + 0.2 * abs(math.sin(math.pi * self.time_of_day * 2))
            night_color = (
                int(color[0] * night_factor * 0.7),
                int(color[1] * night_factor * 0.8),
                int(color[2] * night_factor * 0.9)
            )
            
            # Aurora chance during night
            self.aurora_visible = (self.weather == "clear" and random.random() > 0.7)
            
            return night_color
        
        # Brief dawn/dusk (just 10% of day each)
        elif 0.3 <= self.time_of_day <= 0.32 or 0.68 <= self.time_of_day <= 0.7:
            twilight_factor = 0.4
            dawn_dusk_color = (
                int(color[0] * twilight_factor * 1.1),
                int(color[1] * twilight_factor * 0.9),
                int(color[2] * twilight_factor * 0.8)
            )
            return dawn_dusk_color
        
        # Short daylight period (20% of day)
        else:
            # Even daytime is dim in this environment
            day_factor = 0.5 + 0.3 * math.sin(math.pi * ((self.time_of_day - 0.3) / 0.4))
            day_color = (
                int(color[0] * day_factor),
                int(color[1] * day_factor),
                int(color[2] * day_factor)
            )
            return day_color
    
    def update_weather_from_panel(self):
        # Get current weather values from panel
        self.weather_values = self.weather_panel.weather_values
        
        # Temperature affects visibility and weather conditions
        temp = self.weather_values['current_temperature']
        
        # Determine weather based on temperature and storm chance
        if self.weather_values["storm_chance"] > 95:
            self.weather = "blizzard"
        elif self.weather_values["storm_chance"] > 75:
            self.weather = "light_snow"
        else:
            self.weather = "clear"
        
        # Wind affects particle movement
        self.wind_speed = self.weather_values["wind_speeds"] / 100.0
        self.wind_direction = self.weather_values["wind_direction"]
        
        # Calculate wind vector based on direction
        dir_to_vector = {
            "North": (0, -1),
            "North-East": (0.7, -0.7),
            "East": (1, 0),
            "South-East": (0.7, 0.7),
            "South": (0, 1),
            "South-West": (-0.7, 0.7),
            "West": (-1, 0),
            "North-West": (-0.7, -0.7)
        }
        self.wind_vector = dir_to_vector.get(self.wind_direction, (0, -1))
        
        # Temperature affects visual representation
        temp_normalized = (temp + 950) / 70  # 0 = coldest, 1 = "warmest"
        self.ice_crystallization = max(0, min(1, 1 - temp_normalized * 1.5))
        self.color_desaturation = max(0, min(0.8, 1 - temp_normalized * 1.2))
        
        # Deeper freeze at lower temperatures
        self.deep_freeze_factor = 0.3 + temp_normalized * 0.3
        
        # Update pressure and frost risk display appearance
        self.frostbite_risk = self.weather_values["frostbite_risk"]
    
    def update_time_of_day(self):
        # Use the weather panel's time of day
        self.time_of_day = self.weather_panel.time_of_day
        
        # Update colors based on new time of day
        self.update_colors()
    
    def update_colors(self):
        # Update all segment colors based on current time, temperature, and weather
        for i, segment in enumerate(self.segmentList):
            ground_item = self.ground_data[i]
            
            # Extract data for this cell
            biome_type = ground_item["biome"]
            normalized_height = ground_item["normalized_height"]
            moisture = ground_item["moisture"]
            
            # Calculate temperature factor for this specific cell
            temp_factor = 1.0
            
            # Lower areas are colder (cold air sinks)
            if normalized_height < 0.3:
                # Areas with low elevation can be up to 15% colder
                temp_factor *= 0.85 + normalized_height * 0.5
            
            # High elevations are also colder (normal lapse rate)
            if normalized_height > 0.7:
                # Higher elevations can be up to 20% colder
                temp_factor *= 1.0 - ((normalized_height - 0.7) * 0.67)
            
            # Recalculate color with all factors
            new_color = self.get_biome_color(biome_type, normalized_height, moisture, temp_factor)
            segment.update_color(new_color)
    
    def build(self):
        for item in self.ground_data:
            cell_x, cell_y = item["position"]
            
            # Calculate initial color
            biome_type = item["biome"]
            normalized_height = item["normalized_height"]
            moisture = item["moisture"]
            
            color = self.get_biome_color(biome_type, normalized_height, moisture)
            
            segment_width = self.screen_width // self.width
            segment_height = self.screen_height // self.height

            self.segment = Segment(cell_x, cell_y, segment_width, segment_height, color)
            self.segmentList.append(self.segment)
    
    def draw(self, screen):
        # Draw terrain
        for item in self.segmentList:
            item.draw(screen)
        
        # Draw aurora during clear nights if visible
        if self.aurora_visible:
            self.draw_aurora(screen)
        
        # Draw weather effects
        if self.weather == "light_snow":
            self.draw_snow(screen, 80)
        elif self.weather == "blizzard":
            self.draw_snow(screen, 300)
            self.draw_wind_effect(screen)
        
        # Draw ice crystallization at extreme cold
        if self.ice_crystallization > 0.2:
            self.draw_ice_crystals(screen)
    
    def draw_snow(self, screen, count):
        # Wind direction and speed affect snow movement
        wind_x, wind_y = self.wind_vector
        wind_factor = self.wind_speed / 100.0
        
        # Create snow particles if needed
        if len(self.weather_particles) < count:
            for _ in range(count - len(self.weather_particles)):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                
                # Base speed and direction
                base_speed_x = random.uniform(-2, 2) 
                base_speed_y = random.uniform(1, 4)
                
                # Apply wind influence
                speed_x = base_speed_x + (wind_x * wind_factor * 20)
                speed_y = base_speed_y + (wind_y * wind_factor * 10)
                
                size = random.randint(1, 3)
                
                # Temperature affects snow appearance
                temp = self.weather_values['current_temperature']
                if temp < -920:  # Extremely cold, more like ice crystals
                    # Small sparkly particles
                    alpha = random.randint(150, 255)
                    color = (220, 230, 255, alpha)
                else:  # Standard snow
                    color = (255, 255, 255, random.randint(200, 255))
                
                self.weather_particles.append([x, y, speed_x, speed_y, size, color])
        
        # Update and draw snow particles
        updated_particles = []
        for particle in self.weather_particles:
            x, y, speed_x, speed_y, size, color = particle
            
            # Move particle according to its speed
            x += speed_x
            y += speed_y
            
            # Add some randomness to movement
            x += random.uniform(-0.5, 0.5)
            
            # Wrap around screen edges
            if y > self.screen_height:
                y = 0
                x = random.randint(0, self.screen_width)
            elif y < 0:
                y = self.screen_height
                x = random.randint(0, self.screen_width)
            
            if x < 0:
                x = self.screen_width
            elif x > self.screen_width:
                x = 0
            
            # Save updated particle
            updated_particle = [x, y, speed_x, speed_y, size, color]
            updated_particles.append(updated_particle)
            
            # Draw particle
            if len(color) == 4:  # Has alpha
                pygame.draw.circle(screen, color[:3], (int(x), int(y)), size)
            else:
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
        
        self.weather_particles = updated_particles
    
    def draw_wind_effect(self, screen):
        # Add wind lines based on direction and speed
        wind_x, wind_y = self.wind_vector
        wind_factor = self.wind_speed / 50.0  # Normalize 
        
        for _ in range(40):
            # Start positions randomly across screen
            start_x = random.randint(0, self.screen_width)
            start_y = random.randint(0, self.screen_height)
            
            # Length based on wind speed
            length = random.randint(10, 30) * wind_factor
            
            # Direction based on wind vector
            end_x = start_x + (wind_x * length)
            end_y = start_y + (wind_y * length)
            
            # Add slight random variation
            end_x += random.randint(-5, 5)
            end_y += random.randint(-5, 5)
            
            # Alpha based on wind speed
            alpha = min(220, int(150 * wind_factor))
            
            # Create wind streak surface with alpha
            wind_surface = pygame.Surface((int(length), 1), pygame.SRCALPHA)
            wind_color = (220, 230, 250, alpha)
            wind_surface.fill(wind_color)
            
            # Calculate angle for rotation
            angle = math.degrees(math.atan2(end_y - start_y, end_x - start_x))
            rotated_surface = pygame.transform.rotate(wind_surface, -angle)
            
            # Position so the rotation happens around the start point
            rect = rotated_surface.get_rect(center=(start_x, start_y))
            screen.blit(rotated_surface, rect)
    
    def draw_ice_crystals(self, screen):
        # Draw ice crystal formations at extreme cold temperatures
        crystal_count = int(100 * self.ice_crystallization)
        
        for _ in range(crystal_count):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(1, 3)
            
            # Crystal shape - small lines or points
            if random.random() > 0.7:
                # Line crystal
                length = random.randint(2, 6)
                angle = random.randint(0, 359)
                end_x = x + length * math.cos(math.radians(angle))
                end_y = y + length * math.sin(math.radians(angle))
                
                # Brightness based on temperature
                brightness = int(200 + (self.ice_crystallization * 55))
                crystal_color = (brightness, brightness, 255)
                
                pygame.draw.line(screen, crystal_color, (x, y), (end_x, end_y), 1)
            else:
                # Point crystal
                brightness = int(200 + (self.ice_crystallization * 55))
                crystal_color = (brightness, brightness, 255)
                
                pygame.draw.circle(screen, crystal_color, (x, y), size)
    
    def draw_aurora(self, screen):
        # Create aurora particles if needed
        if len(self.aurora_particles) < 200:
            for _ in range(200 - len(self.aurora_particles)):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height // 3)  # Only in the sky
                
                speed_x = random.uniform(-0.5, 0.5)
                speed_y = random.uniform(-0.2, 0.2)
                
                size = random.randint(2, 5)
                color = random.choice(self.aurora_colors)
                alpha = random.randint(30, 100)
                
                self.aurora_particles.append([x, y, speed_x, speed_y, size, color, alpha])
        
        # Update and draw aurora particles
        updated_particles = []
        for particle in self.aurora_particles:
            x, y, speed_x, speed_y, size, color, alpha = particle
            
            # Move particle according to its speed
            x += speed_x
            y += speed_y
            
            # Wrap around screen edges
            if x < 0:
                x = self.screen_width
            elif x > self.screen_width:
                x = 0
            
            if y < 0:
                y = self.screen_height // 3
            elif y > self.screen_height // 3:
                y = 0
            
            # Pulse alpha
            alpha += random.randint(-5, 5)
            alpha = max(20, min(100, alpha))
            
            # Save updated particle
            updated_particles.append([x, y, speed_x, speed_y, size, color, alpha])
            
            # Draw particle with glow effect
            surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            r, g, b = color
            
            # Draw with alpha gradient for glow effect
            pygame.draw.circle(surf, (r, g, b, alpha), (size * 2, size * 2), size * 2)
            pygame.draw.circle(surf, (r, g, b, alpha * 2), (size * 2, size * 2), size)
            
            screen.blit(surf, (int(x - size * 2), int(y - size * 2)))
        
        self.aurora_particles = updated_particles

    def update(self):
        self.update_weather_from_panel()
        self.update_time_of_day()