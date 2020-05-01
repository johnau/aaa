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
        # Init pygame
        pygame.init()

        # Get clock
        self.clock = pygame.time.Clock()

        # Create screen
        self.__screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Main app font
        self.font = pygame.font.SysFont("Arial", 16, False, False)

        # Input pipeline (instance gets replaced by each state init())
        self.inputs = Inputs()

        # Persistent data dictionary, for data to persist across state change
        self.__data = {}

        # Current state
        self.__state = None
        # Next state name
        self.__next_state = init_state

        # Main game loop escape bool
        self.running = True

    @property
    def data(self):
        return self.__data

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, name):
        """
        State change setter function
        """
        self.__next_state = name

    @property
    def screen(self):
        return self.__screen

    def run(self):
        """
        Main run method
        - Main game loop
        """
        # Set window title
        pygame.display.set_caption(WINDOW_TITLE)

        # Main game loop
        while self.running:
            
            # Get events
            events = pygame.event.get()
            for event in events:
                # Handle Quit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 0
            
            # Send events to input pipeline
            self.inputs.handle_events(events)
            
            # Set FPS and get frame time
            delta_time = self.clock.tick(FPS_CAP)
            
            # Update input pipeline
            self.inputs.update(delta_time)
            
            # Update the system
            self.update(delta_time)
            
            # Draw next frame
            self.draw_frame()

    def update(self, delta_time):
        """
        Update state of the system
        """
        if self.__next_state:
            self.__state = self.STATES[self.__next_state.lower()](self)
            self.__next_state = ''
        else:
            self.__state.update(delta_time)

    def draw_frame(self):
        """
        Draw Next Frame
        """
        # Fill screen with background color
        bg_color = self.__state.scene_bg
        self.__screen.fill(bg_color)

        # Call .draw() func of state
        self.__state.draw() # For transient drawing to the screen, (arrows)
        
        # Draw fps to screen
        self.__draw_fps()
        
        # Update the display
        pygame.display.update()

    def __draw_fps(self):
        """
        Draw fps to screen
        """
        txt = f'{round(self.clock.get_fps())} FPS'
        rtxt = self.font.render(txt, False, pygame.Color('black'))
        rsiz = self.font.size(txt)
        self.__screen.blit(rtxt, (SCREEN_WIDTH-rsiz[0]-5, 5))     

app = App('draw')   # Start app in "draw" state, default is menu but no menu yet
app.run()

