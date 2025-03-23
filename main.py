from Container.imports_library import *
from Displays.main_display import *
from Displays.card_display import *
import map

screenWidth, screenHeight = 1280, 720
clock = pygame.time.Clock()
cell_size = 10

# camera
class Camera:
    def __init__(self, x, y, size=10):
        self.x = x
        self.y = y
        self.size = size
        self.color = pygame.Color("Red")
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
        # display
        self.detail_window = WeatherWindow(self.ui_manager, (screenWidth, screenHeight), self.details_panel)
        # cards
        self.PATH_BACK = os.path.join(os.getcwd(), "Assets/cardBack.png")
        self.PATH_FRONT = os.path.join(os.getcwd(), "Assets/cardFront.png")
        self.card_grid = GridSystem((screenWidth - 120, 120, 100, screenHeight - 130), grid_size=(1, 5))
        self.cardDeck = CardDeck_Display(pos=(screenWidth - 130, 10), size=(100, 120), screen_size=(screenWidth, screenHeight), back_image_path=self.PATH_BACK, front_image_path=self.PATH_FRONT, grid_system=self.card_grid)

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
                # details
                self.details_panel.handle_event(event, self.detail_window)
                if self.detail_window.window_open:
                    self.detail_window.handle_event(event)
                    self.detail_window.update()
                # cards
                self.cardDeck.handle_event(event)

            # Draw elements
            self.ui_manager.update(time_delta)
            self.screen.blit(self.background_surface, (0, 0))

            self.ground.draw(self.screen, self.camera.x, self.camera.y)
            self.weather.draw(self.screen)
            # Draw cards
            self.cardDeck.draw(self.screen)
            self.card_grid.draw(self.screen, debug=True)
            # windows
            if not self.detail_window.window_open:
                self.camera.draw(self.screen, self.camera.x, self.camera.y)
                self.camera.move(mouse_pos, keys)

            self.ui_manager.draw_ui(self.screen)
            # update
            self.details_panel.update()
            self.weather.update()
            self.clock.tick(64)
            pygame.display.flip()
            pygame.display.update()
        pygame.quit()
        sys.exit()

# loop
if __name__ == "__main__":
    app = App()
    app.run()