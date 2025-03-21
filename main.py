import pygame
import pygame_gui
import random
import sys
import time
import Map
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextEntryLine, UIScrollingContainer, UIStatusBar

screenWidth, screenHeight = 1280, 720
current_time = time.time()
random.seed(current_time)
clock = pygame.time.Clock()
cell_size = 20

# details
class Details_Panel:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.details_panel = UIPanel(relative_rect=pygame.Rect((10, 10), (450, 200)), manager=self.ui_manager, starting_height=1)
        # Day/night cycle - Shorter days, longer nights
        self.time_of_day = 0  # 0 = midnight, 0.5 = noon, 1 = midnight again
        self.day_length = 500  # Longer nights, shorter daylight
        self.last_update = pygame.time.get_ticks()
        self.day_count = 0
        self.weather_values = self._generate_weather_values()
        self._build()

    def _build(self):
        self.current_temperature = UIButton(relative_rect=pygame.Rect((0, 20), (444, 40)), manager=self.ui_manager, container=self.details_panel, text=f"Current: {self.weather_values['current_temperature']}°C")
        self.temperature_range = UILabel(relative_rect=pygame.Rect((0, 70), (444, 20)), manager=self.ui_manager, container=self.details_panel, text=f"Range: {self.weather_values['temperature_range'][0]}°C to {self.weather_values['temperature_range'][1]}°C")
        self.storm_chance = UILabel(relative_rect=pygame.Rect((0, 90), (444, 20)), manager=self.ui_manager, container=self.details_panel, text=f"Storm Chance: {self.weather_values['storm_chance']}%")
        self.wind_speeds = UILabel(relative_rect=pygame.Rect((0, 110), (444, 20)), manager=self.ui_manager, container=self.details_panel, text=f"Wind Speeds: {self.weather_values['wind_speeds']}km/h | Direction: {self.weather_values['wind_direction']}")
        self.feels_like = UILabel(relative_rect=pygame.Rect((0, 130), (444, 20)), manager=self.ui_manager, container=self.details_panel, text=f"Feels Like: {self.weather_values['feels_like']}°C")
        self.pressure = UILabel(relative_rect=pygame.Rect((0, 150), (444, 20)), manager=self.ui_manager, container=self.details_panel, text=f"Atmospheric Pressure: {self.weather_values['pressure']} PA")
        self.frostbite_risk = UILabel(relative_rect=pygame.Rect((0, 170), (444, 20)), manager=self.ui_manager, container=self.details_panel, text=f"Frostbite Risk: {self.weather_values['frostbite_risk']}")

    def _generate_weather_values(self):
        weather_data = {
            "current_temperature": round(random.uniform(-900, -880), 2),
            "temperature_range": (round(random.uniform(-905, -890), 2), round(random.uniform(-890, -880), 2)),
            "storm_chance": round(random.randint(0, 100), 2),
            "wind_speeds": round(random.randint(180, 250), 2),
            "wind_direction": random.choice(["North", "North-East", "East", "South-East", "South"]),
            "feels_like": round(random.uniform(-950, -910), 2),
            "pressure": round(random.uniform(14, 16), 2),
            "frostbite_risk": random.choice(["Instantaneous", "Severe", "Critical"])
        }
        return weather_data

    def _produce_values(self):
        self.weather_values = self._generate_weather_values()
        self.current_temperature_value = self.weather_values["current_temperature"]
        self.temperature_range_value = (self.weather_values["temperature_range"][0], self.weather_values["temperature_range"][1])
        self.storm_chance_value = self.weather_values["storm_chance"]
        self.wind_speeds_value = (self.weather_values["wind_speeds"], self.weather_values["wind_direction"])
        self.feels_like_value = self.weather_values["feels_like"]
        self.pressure_value = self.weather_values["pressure"]
        self.frostbite_risk_value = self.weather_values["frostbite_risk"]

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.last_update) / 1000
        self.last_update = current_time
        self.time_of_day = (self.time_of_day + elapsed / self.day_length) % 1.0
        if random.randint(0, 50) == 1:
            self.weather_values = self._generate_weather_values()
            self.current_temperature.set_text(f"Current: {self.weather_values['current_temperature']}°C")
            self.temperature_range.set_text(f"Range: {self.weather_values['temperature_range'][0]}°C to {self.weather_values['temperature_range'][1]}°C")
            self.storm_chance.set_text(f"Storm Chance: {self.weather_values['storm_chance']}%")
            self.wind_speeds.set_text(f"Wind Speeds: {self.weather_values['wind_speeds']}km/h | Direction: {self.weather_values['wind_direction']}")
            self.feels_like.set_text(f"Feels Like: {self.weather_values['feels_like']}°C")
            self.pressure.set_text(f"Atmospheric Pressure: {self.weather_values['pressure']} PA")
            self.frostbite_risk.set_text(f"Frostbite Risk: {self.weather_values['frostbite_risk']}")

# app
class App():
    def __init__(self):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
        pygame.display.set_caption("Snow Day")
        self.clock = pygame.time.Clock()
        self.running = True
        # ui_manager
        self.background_surface = pygame.Surface((screenWidth, screenHeight)).convert()
        self.ui_manager = UIManager((screenWidth, screenHeight))
        # map
        self.details_panel = Details_Panel(self.ui_manager)
        self.ground = Map.Ground(screenWidth, screenHeight, (cell_size,cell_size), self.details_panel)
        
        
    def run(self):
        while self.running:
            time_delta = self.clock.tick(64) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
                self.ui_manager.process_events(event)
            # Draw elements
            self.ui_manager.update(time_delta)
            self.screen.blit(self.background_surface, (0, 0))

            self.ground.draw(self.screen)
            self.ui_manager.draw_ui(self.screen)
            # update
            self.details_panel.update()
            self.ground.update()
            self.clock.tick(64)
            pygame.display.flip()
            pygame.display.update()
        
# loop
if __name__ == "__main__":
    app = App()
    app.run()