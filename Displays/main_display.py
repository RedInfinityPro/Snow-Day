from Container.imports_library import *

# details
class Details_Panel:
    def __init__(self, ui_manager, weather):
        self.ui_manager = ui_manager
        self.weather = weather  # Link to the Weather class
        self.details_panel = UIPanel(relative_rect=pygame.Rect((10, 10), (450, 250)), manager=self.ui_manager, starting_height=1)
        self.PATH = os.path.join(os.getcwd(), "Data/weather_tracker.pkl")
        self.previous_data = self.load_data(self.PATH)
        self.last_update = pygame.time.get_ticks()
        self._build()

    def _build(self):
        """Create UI elements for displaying weather details."""
        self.current_temperature = UIButton(relative_rect=pygame.Rect((0, 20), (444, 40)), manager=self.ui_manager, container=self.details_panel, text="Current: --°C")
        self.weather_type = UILabel(relative_rect=pygame.Rect((0, 65), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Weather: --")
        self.wind_speeds = UILabel(relative_rect=pygame.Rect((0, 90), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Wind Speeds: -- km/h | Direction: --")
        self.feels_like = UILabel(relative_rect=pygame.Rect((0, 110), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Feels Like: --°C")
        self.pressure = UILabel(relative_rect=pygame.Rect((0, 130), (444, 20)),  manager=self.ui_manager, container=self.details_panel, text="Atmospheric Pressure: -- PA")
        self.visibility = UILabel(relative_rect=pygame.Rect((0, 150), (444, 20)),  manager=self.ui_manager, container=self.details_panel, text="Visibility: --")
        self.precipitation = UILabel(relative_rect=pygame.Rect((0, 175), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Precipitation: --")
        self.exposure_risk = UILabel(relative_rect=pygame.Rect((0, 200), (444, 20)), manager=self.ui_manager, container=self.details_panel, text="Frostbite Risk: --")

    def update(self):
        """Fetch weather data and update the UI."""
        self.weather.update()  # Update weather conditions
        self.weather_report = self.weather.get_weather_report()
        self.current_temperature.set_text(f"Current: {self.weather_report["Temperature"]}°C")
        self.weather_type.set_text(f"Weather: {self.weather_report["Weather"]}")
        self.wind_speeds.set_text(f"Wind Speeds: {self.weather_report["Wind"][0]} km/h | Direction: {self.weather_report["Wind"][1]}")
        self.feels_like.set_text(f"Feels Like: {self.weather_report["Feels like"]}°C")
        self.pressure.set_text(f"Atmospheric Pressure: {self.weather_report["Atmospheric pressure"]} atm")
        self.visibility.set_text(f"Visibility: {self.weather_report["Visibility"]}")
        self.precipitation.set_text(f"Precipitation: {self.weather_report["Precipitation"]}")
        self.exposure_risk.set_text(f"Frostbite Risk: {self.weather_report["Exposure risk"]}")
        # save data
        if self.previous_data != self.weather_report:
            self.save_weather_data(self.PATH, self.weather_report)
            self.previous_data = self.weather_report

    def save_weather_data(self, PATH, new_data):
        try:
            # Load existing data if file exists
            if os.path.exists(PATH):
                with open(PATH, 'rb') as file:
                    try:
                        data = pickle.load(file)
                    except EOFError:
                        data = []
            else:
                # If file doesn't exist, initialize an empty list
                data = []

            # Append new data to the existing data
            data.append(new_data)

            # Save the updated data back to the file
            with open(PATH, 'wb') as file:
                pickle.dump(data, file)

            print(f"Data saved to {os.path.abspath(PATH)}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def delete_weather_data(self, PATH):
        try:
            with open(PATH, 'wb') as file:
                pickle.dump([], file)
            print(f"All data in '{PATH}' has been cleared.")
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self, PATH):
        # Check if the file exists and has data
        try:
            with open(PATH, 'rb') as file:
                data = pickle.load(file)
                return data
        except FileNotFoundError:
            print(f"The file '{PATH}' does not exist.")
            return None
        except EOFError:
            # Handles the case where the file exists but is empty
            print(f"The file '{PATH}' is empty.")
            return None

    def handle_event(self, event, weather_window=None):
        if self.current_temperature.process_event(event) and not None:
            weather_window.window_open = not weather_window.window_open
            weather_window.toggle_store()
            weather_window.update()

# Weather Content
class WeatherContent:
    def __init__(self, ui_manager, window_size, scroll_container, weather_report):
        self.ui_manager = ui_manager
        self.window_width, self.window_height = window_size
        self.scroll_container = scroll_container
        self.weather_report = weather_report
        self.window_container = None
        self.labels = {}

    def build(self, index):
        # Panel container
        self.window_container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((5, index * (self.window_height + 10)), (self.window_width, self.window_height)),
            manager=self.ui_manager,
            container=self.scroll_container,
            starting_height=1
        )

        label_positions = [
            ("Current Temperature", "Current: --°C", (0, 5)),
            ("Weather Type", "Weather: --", (0, 35)),
            ("Wind Speed", "Wind Speeds: -- km/h | Direction: --", (0, 65)),
            ("Feels Like", "Feels Like: --°C", (0, 95)),
            ("Pressure", "Atmospheric Pressure: -- PA", (0, 125)),
            ("Visibility", "Visibility: --", (0, 155)),
            ("Precipitation", "Precipitation: --", (0, 185)),
            ("Exposure Risk", "Frostbite Risk: --", (0, 215))
        ]

        for key, text, pos in label_positions:
            self.labels[key] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(pos, (self.window_width - 10, 25)),
                text=text,
                manager=self.ui_manager,
                container=self.window_container
            )

    def update(self):
        data = {
            "Current Temperature": f"Current: {self.weather_report['Temperature']}°C",
            "Weather Type": f"Weather: {self.weather_report['Weather']}",
            "Wind Speed": f"Wind Speeds: {self.weather_report['Wind'][0]} km/h | Direction: {self.weather_report['Wind'][1]}",
            "Feels Like": f"Feels Like: {self.weather_report['Feels like']}°C",
            "Pressure": f"Atmospheric Pressure: {self.weather_report['Atmospheric pressure']} atm",
            "Visibility": f"Visibility: {self.weather_report['Visibility']}",
            "Precipitation": f"Precipitation: {self.weather_report['Precipitation']}",
            "Exposure Risk": f"Frostbite Risk: {self.weather_report['Exposure risk']}"
        }

        for key, label in self.labels.items():
            label.set_text(data[key])

class WeatherWindow:
    def __init__(self, ui_manager, screen_size, details_panel):
        self.ui_manager = ui_manager
        self.screen_width, self.screen_height = screen_size
        self.window_x, self.window_y = 465, 10
        self.weather_list = []
        self.window_open = False
        self.PATH = os.path.join(os.getcwd(), "Data/weather_tracker.pkl")
        self.details_panel = details_panel
        self.previous_data = details_panel.load_data(self.PATH)
        self.previous_data = []
        # Track last update time to avoid excessive updates
        self.last_update_time = 0
        self.update_interval = 1000

        if self.window_open:
            self._build()

    def _build(self):
        # Load the latest data from the file
        self.previous_data = self.details_panel.load_data(self.PATH) or []

        self.center_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((self.window_x, self.window_y), (self.screen_width - 470, self.screen_height - 20)),
            manager=self.ui_manager,
            starting_height=1
        )

        # Title Label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.screen_width // 2 - 350, 10), (200, 30)),
            text="Weather Tracker",
            manager=self.ui_manager,
            container=self.center_panel
        )

        # clear data Button
        self.clearData_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.screen_width // 2 + 25, 2), (100, 30)),
            text="Clear Data",
            manager=self.ui_manager,
            container=self.center_panel
        )

        # Close Button
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.screen_width // 2 + 125, 2), (30, 30)),
            text="X",
            manager=self.ui_manager,
            container=self.center_panel
        )

        # Scrollable Container for Weather Panels
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((10, 50), (self.screen_width - 500, self.screen_height - 80)),
            manager=self.ui_manager,
            container=self.center_panel
        )

        # Create weather panels for each data entry
        self._create_weather_panels()

    def _create_weather_panels(self):
        """Creates weather panels for all data entries"""
        # Clear existing weather panels
        self.weather_list = []

        # Calculate content height based on number of entries
        content_height = (250 * len(self.previous_data)) + 250
        self.scroll_container.set_scrollable_area_dimensions((self.screen_width - 520, max(content_height, self.screen_height - 100)))

        # Create new panels for each data entry
        for i, item in enumerate(self.previous_data):
            weather_panel = WeatherContent(self.ui_manager, (self.screen_width - 550, 250), self.scroll_container, item)
            weather_panel.build(i)
            weather_panel.update()
            self.weather_list.append(weather_panel)

    def update(self):
        """Check for new data and update the display if needed"""
        if not self.window_open:
            return

        current_time = pygame.time.get_ticks()

        # Only check for updates at set intervals to avoid performance issues
        if current_time - self.last_update_time > self.update_interval:
            self.last_update_time = current_time

            # Load latest data from file
            latest_data = self.details_panel.load_data(self.PATH) or []

            # Check if data has changed (new entries added or entries removed)
            if len(latest_data) != len(self.previous_data):
                # Data has changed, rebuild the panels
                self.previous_data = latest_data

                # Remove existing panels
                for panel in self.weather_list:
                    if hasattr(panel, 'window_container') and panel.window_container:
                        panel.window_container.kill()

                # Create new panels
                self._create_weather_panels()

    def close_store(self):
        """Closes and removes the planet store UI from the screen."""
        if hasattr(self, 'center_panel') and self.center_panel:
            self.center_panel.kill()
            self.window_open = False

    def toggle_store(self):
        """Toggles the visibility of the store panel."""
        if self.window_open:
            self._build()
        else:
            self.close_store()

    def handle_event(self, event):
        if not self.window_open:
            return

        if hasattr(self, 'close_button') and self.close_button.process_event(event):
            self.window_open = False
            self.close_store()

        if hasattr(self, 'clearData_button') and self.clearData_button.process_event(event):
            self.details_panel.delete_weather_data(self.details_panel.PATH)
            # After clearing data, rebuild the window
            self.close_store()
            self.window_open = True
            self._build()