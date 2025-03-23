import pygame
from Container.imports_library import *

class GridSystem:
    def __init__(self, rect, grid_size=(4, 3), cell_padding=10):
        self.rect = rect  # (x, y, width, height)
        self.grid_size = grid_size  # (columns, rows)
        self.cell_padding = cell_padding

        # Calculate cell dimensions dynamically
        self.cell_width = (rect[2] - (grid_size[0] + 1) * cell_padding) // grid_size[0]
        self.cell_height = (rect[3] - (grid_size[1] + 1) * cell_padding) // grid_size[1]

        # Initialize grid with None (empty cells)
        self.grid = [[None for _ in range(grid_size[0])] for _ in range(grid_size[1])]

        # Precompute cell positions
        self.cell_positions = [[(
            rect[0] + col * (self.cell_width + cell_padding) + cell_padding,
            rect[1] + row * (self.cell_height + cell_padding) + cell_padding
        ) for col in range(grid_size[0])] for row in range(grid_size[1])]

    def add_card(self, card, row, col):
        if 0 <= row < self.grid_size[1] and 0 <= col < self.grid_size[0] and self.grid[row][col] is None:
            self.grid[row][col] = card
            card.x, card.y = self.cell_positions[row][col]
            card.original_y = card.y
            card.grid_pos = (row, col)
            return True
        return False

    def remove_card(self, card):
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                if self.grid[row][col] == card:
                    self.grid[row][col] = None
                    return True
        return False

    def get_nearest_cell(self, pos):
        x, y = pos
        return min(((row, col) for row in range(self.grid_size[1]) for col in range(self.grid_size[0]) if self.grid[row][col] is None),
                   key=lambda rc: ((x - (self.cell_positions[rc[0]][rc[1]][0] + self.cell_width / 2)) ** 2 +
                                   (y - (self.cell_positions[rc[0]][rc[1]][1] + self.cell_height / 2)) ** 2) ** 0.5,
                   default=None)

    def snap_to_grid(self, card, pos):
        if self.is_position_in_grid(pos):
            nearest_cell = self.get_nearest_cell(pos)
            if nearest_cell:
                return self.add_card(card, *nearest_cell)
        return False

    def is_position_in_grid(self, pos):
        x, y = pos
        return self.rect[0] <= x <= self.rect[0] + self.rect[2] and self.rect[1] <= y <= self.rect[1] + self.rect[3]

    def draw(self, screen, debug=False):
        if debug:
            for row in range(self.grid_size[1]):
                for col in range(self.grid_size[0]):
                    pygame.draw.rect(screen, (100, 100, 100), (*self.cell_positions[row][col], self.cell_width, self.cell_height), 1)

class CardDeck_Display(pygame.sprite.Sprite):
    def __init__(self, pos, size, screen_size, back_image_path, front_image_path, grid_system):
        super().__init__()
        self.x, self.y = pos
        self.screenWidth, self.screenHeight = screen_size
        self.original_x = self.x
        self.width, self.height = size
        self.image_back = pygame.image.load(back_image_path)
        self.image_back = pygame.transform.rotate(pygame.transform.scale(self.image_back, (self.width, self.height)), 90)

        self.image_front = front_image_path
        self.grid_system = grid_system
        self.cards = []

    def draw(self, screen):
        screen.blit(self.image_back, (self.x, self.y))  # draw image

        for card in self.cards:
            card.draw(screen)

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_over = self.x < mouse_x < self.x + self.width and self.y < mouse_y < self.y + self.height
        if mouse_over:
            self.x = self.original_x - 10
        else:
            self.x = self.original_x

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            card = Card_Display((109, 109), (80, 110), (self.screenWidth, self.screenHeight), self.image_front)
            self.grid_system.add_card(card,0,0)
            self.cards.append(card)

        for card in self.cards:
            card.handle_event(event, self.grid_system)


class Card_Display(pygame.sprite.Sprite):
    def __init__(self, pos, size, screen_size, front_image_path):
        super().__init__()
        self.x, self.y = pos
        self.WIDTH, self.HEIGHT = screen_size
        self.width, self.height = size
        self.original_y = self.y
        self.image = pygame.transform.scale(pygame.image.load(front_image_path), (self.width, self.height))
        self.dragging = False
        self.grid_pos = None
        self.in_grid = False

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def handle_event(self, event, grid):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_over = self.x < mouse_x < self.x + self.width and self.y < mouse_y < self.y + self.height
        if mouse_over and not self.dragging:
            self.y = self.original_y - 10
        elif not self.dragging and not mouse_over:
            self.y = self.original_y

        if event.type == pygame.MOUSEBUTTONDOWN and mouse_over:
            self.dragging = True
            if grid and self.in_grid:
                grid.remove_card(self)
                self.in_grid = False
                self.grid_pos = None

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            if grid and grid.snap_to_grid(self, (self.x + self.width / 2, self.y + self.height / 2)):
                self.in_grid = True
            else:
                self.y = self.y

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.x = max(0, min(mouse_x - self.width / 2, self.WIDTH - self.width))
            self.y = max(0, min(mouse_y - self.height / 2, self.HEIGHT - self.height))
            self.original_y = self.y