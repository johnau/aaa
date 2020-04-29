import pygame

from states import MenuState, DrawState
from inputs import Inputs
from constants import WINDOW_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS_CAP

class App():
    STATES = {
        'menu' : MenuState,
        'draw' : DrawState
    }

    def __init__(self, init_state = 'menu'):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.inputs = Inputs()          # Inputs management

        self.__data = {}                 # Dictionary to store data that needs to persist across states
        self.__state = None              # Current state object
        self.__next_state = init_state   # Next state name

        self.running = True

    @property
    def data(self):
        return self.__data

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, name):
        self.__next_state = name

    @property
    def screen(self):
        return self.__screen

    def run(self):
        pygame.display.set_caption(WINDOW_TITLE)
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 0
            self.inputs.handle_events(events)
            delta_time = self.clock.tick(FPS_CAP)
            self.inputs.update(delta_time)
            self.update(delta_time)
            self.draw_frame()

    def update(self, delta_time):
        if self.__next_state:
            self.__state = self.STATES[self.__next_state.lower()](self)
            self.__next_state = ''
        else:
            self.__state.update(delta_time)

    def draw_frame(self):
        bg_color = self.__state.scene_bg
        self.__screen.fill(bg_color)
        sprite_group = self.__state.sprites
        sprite_group.draw(self.__screen)
        self.__state.draw() # For transient drawing to the screen, (arrows)
        pygame.display.update()

app = App('draw')   # Start app in "draw" state, default is menu but no menu yet
app.run()

