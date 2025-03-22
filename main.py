import pygame
import pygame_gui
import random
import sys
import time
import map
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextEntryLine, UIScrollingContainer, UIStatusBar

screenWidth, screenHeight = 1280, 720
current_time = time.time()
random.seed(current_time)
clock = pygame.time.Clock()
cell_size = 10

# details
class Details_Panel:
    def __init__(self, ui_manager, weather):
        self.ui_manager = ui_manager
        self.weather = weather  # Link to the Weather class
        self.details_panel = UIPanel(relative_rect=pygame.Rect((10, 10), (450, 200)), manager=self.ui_manager, starting_height=1)

        self.last_update = pygame.time.get_ticks()
        self._build()

    def _build(self):
        """Create UI elements for displaying weather details."""
        self.current_temperature = UIButton(relative_rect=pygame.Rect((0, 20), (444, 40)), manager=self.ui_manager, container=self.details_panel, text="Current: --°C")
        self.weather_type = UILabel(relative_rect=pygame.Rect((0, 65), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Weather: --")
        self.wind_speeds = UILabel(relative_rect=pygame.Rect((0, 90), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Wind Speeds: -- km/h | Direction: --")
        self.feels_like = UILabel(relative_rect=pygame.Rect((0, 110), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Feels Like: --°C")
        self.pressure = UILabel(relative_rect=pygame.Rect((0, 130), (444, 20)),  manager=self.ui_manager, container=self.details_panel, text="Atmospheric Pressure: -- PA")
        self.frostbite_risk = UILabel(relative_rect=pygame.Rect((0, 150), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Frostbite Risk: --")

    def update(self):
        """Fetch weather data and update the UI."""
        self.weather.update()  # Update weather conditions

        self.current_temperature.set_text(f"Current: {self.weather.current_temperature}°C")
        self.weather_type.set_text(f"Weather: {self.weather.current_weather.capitalize()}")
        self.wind_speeds.set_text(f"Wind Speeds: {self.weather.wind_speed} km/h | Direction: {self.weather.wind_direction}")
        self.feels_like.set_text(f"Feels Like: {self.weather.feels_like}°C")
        self.pressure.set_text(f"Atmospheric Pressure: {self.weather.pressure} PA")
        self.frostbite_risk.set_text(f"Frostbite Risk: {self.weather.frostbite_risk}")

# camera
class Camera:
    def __init__(self, x, y, size=10):
        self.x = x
        self.y = y
        self.size = size
        self.color = (255, 0, 0)
        self.edge_size = 50 # Size of edge area that triggers scrolling
        self.speed = 10

    def draw(self, screen, camera_offset_x, camera_offset_y):
        # Draw player at center of screen
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        pygame.draw.rect(screen, self.color, (center_x - self.size//2, center_y - self.size//2, self.size, self.size))

    def move(self, mouse_pos, keys):
        # Edge scrolling with mouse
        # Left edge
        if mouse_pos[0] < self.edge_size:
            self.x -= self.speed * (1 - mouse_pos[0] / self.edge_size)
        # Right edge
        elif mouse_pos[0] > screenWidth - self.edge_size:
            self.x += self.speed * (1 - (screenWidth - mouse_pos[0]) / self.edge_size)
        # Top edge
        if mouse_pos[1] < self.edge_size:
            self.y -= self.speed * (1 - mouse_pos[1] / self.edge_size)
        # Bottom edge
        elif mouse_pos[1] > screenHeight - self.edge_size:
            self.y += self.speed * (1 - (screenHeight - mouse_pos[1]) / self.edge_size)

        # Keyboard controls
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

# app
class App:
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
        self.weather = map.Weather()
        self.details_panel = Details_Panel(self.ui_manager, self.weather)
        self.ground = map.Ground(screenWidth, screenHeight, (cell_size,cell_size))

        # camera
        self.camera = Camera(0, 0)
        self.camera_position = Camera(0, 0)

    def run(self):
        while self.running:
            time_delta = self.clock.tick(64) / 1000.0
            # Get input
            mouse_pos = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
                self.ui_manager.process_events(event)
            # Draw elements
            self.ui_manager.update(time_delta)
            self.screen.blit(self.background_surface, (0, 0))

            self.ground.draw(self.screen, self.camera.x, self.camera.y)
            self.weather.draw(self.screen)

            self.camera.draw(self.screen, self.camera.x, self.camera.y)
            self.camera.move(mouse_pos, keys)

            self.ui_manager.draw_ui(self.screen)
            # update
            self.details_panel.update()
            self.weather.update()
            self.clock.tick(64)
            pygame.display.flip()
            pygame.display.update()

# loop
if __name__ == "__main__":
    app = App()
    app.run()