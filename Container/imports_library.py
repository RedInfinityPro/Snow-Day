import pygame
import pygame_gui
import random
import sys
import time

import os
import pickle
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextEntryLine, UIScrollingContainer, UIStatusBar

current_time = time.time()
random.seed(current_time)