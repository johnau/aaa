#WINDOW SETTINGS
WINDOW_TITLE = "Gravitational Simulator"
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS_CAP = 144
BACKGROUND_COLOR = (50, 50, 50)

#SIMULATOR PARAMETERS
PLANET_DEFAULT_DENSITY = 0.005
PLANET_MAX_DISTANCE = 3000 #distance an object can get away from the center of the screen

DELTA_T = 0.1 #simulation time between frames

PLANET_MIN_RADIUS = 10
PLANET_MAX_RADIUS = 200

REALITY_MULTI = 50

ARROW_TO_VEL_RATIO = 0.025 #how many pixels/frame a body gets for each pixel of the arrow length
ARROW_TO_ACC_RATIO = 0.0005

ARROW_MAX_LENGTH = 500
ARROW_HALF_THICKNESS = 2 #pixel offset above and under the central line
ARROW_CAP_LENGTH = 30 
ARROW_CAP_ANGLE = 25
SMALL_ARROW_HALF_THICKNESS = 0
SMALL_ARROW_CAP_LENGTH = 15 
SMALL_ARROW_CAP_ANGLE = 20

PLANET_COLOR = (0, 255, 50)
ARROW_COLOR_VEL = (50, 130, 200)
ARROW_COLOR_ACC = (200, 0, 0)

CAM_MOVE_SPEED = 20
CAM_ZOOM_AMOUNT = 5
ZOOM_MIN = -95
ZOOM_MAX = 500

TYPE_VEL = "vel"
TYPE_ACCEL = "accel"