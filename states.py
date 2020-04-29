import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, MOUSEMOTION, K_SPACE
import glm
from glm import vec2, vec3
import math

from constants import BACKGROUND_COLOR
from objects import CelestialObject, VelocityArrow
from inputs import Inputs, Button

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

class Camera():
    def __init__(self):
        self.fov = 90
        self.position = glm.vec3(0)
        self.tilt = 0
        self.yaw = 0

class Scene():
    def __init__(self):
        self.background = BACKGROUND_COLOR
        self.content = pygame.sprite.RenderUpdates()
        self.camera = Camera()

class State:
    """
    State base class
    - Derive from this class and override methods for each state
    """
    def __init__(self, app, **kwargs):
        self.app: App = app
        self.name = ''

        self.suspended = False
        self.terminated = False

        self.scene = Scene()

        if kwargs:
            raise ValueError("Some kwargs not consumed: {kwargs}")

    def update(self, delta_time):
        self.scene.content.update()

    @property
    def scene_bg(self):
        return self.scene.background

    @property
    def sprites(self):
        return self.scene.content

class MenuState(State):
    """
    Menu State Class
    """
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

    def update(self, delta_time):
        pass

class DrawState(State):
    """
    Draw State Class
    """
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

        self.__input_fns = {}
        self.__build_inputs()

        self.curr_celestial = None
        self.curr_velo_arrow = None
        self.celest_objs = pygame.sprite.Group()

        self.paused = False

    def __build_inputs(self):
        """
        Private function to bind inputs to functions
        """
        inputs = Inputs()
        inputs.register("new_object", Button(MOUSEBUTTONDOWN, 1))
        inputs.register("kill_all_objects", Button(KEYDOWN, K_SPACE))
        inputs.register("update", Button(MOUSEMOTION, 0))
        self.app.inputs = inputs

        # Store functions to maintain weakrefs
        self.__input_fns["temp"] = self.app.inputs.inputs["new_object"].on_press(self.__new_object_stage1)
        self.__input_fns["permanent"] = self.app.inputs.inputs["kill_all_objects"].on_press(self.__kill_all_objects)

    def __new_object_stage1(self):
        """
        Private function to create a new celestial object
        """
        if not self.curr_celestial:
            self.paused = True
            # Replace functions for next stage
            self.__input_fns["temp"] = self.app.inputs.inputs["new_object"].on_press_repeat(self.__new_object_stage1_cont, 0)
            self.__input_fns["temp2"] = self.app.inputs.inputs["new_object"].on_release(self.__new_object_stage2)

            center = pygame.mouse.get_pos()
            self.curr_celestial = CelestialObject(self.celest_objs, center) #set radius to 0 so the initializer will set PLANET_MIN_RADIUS
            self.celest_objs.add(self.curr_celestial)
            self.scene.content.add(self.curr_celestial)
    
    def __new_object_stage1_cont(self):
        """
        Private function to update celestial body radius
        """        
        if self.curr_celestial:
            center = self.curr_celestial.rect.center
            center_v = vec3(center[0], center[1], 0)
            curpos = pygame.mouse.get_pos()
            curpos_v = vec3(curpos[0], curpos[1], 0)
            self.curr_celestial.radius = math.floor(glm.distance(center_v, curpos_v))   

    def __new_object_stage2(self):
        """
        Private function to complete creating a new celestial object
        """
        if self.curr_celestial:
            # Replace functions for next stage
            self.__input_fns["temp"] = self.app.inputs.inputs["update"].always(self.__new_object_stage2_cont)
            self.__input_fns["temp2"] = self.app.inputs.inputs["new_object"].on_press(self.__new_object_stage3)
            
            center = self.curr_celestial.rect.center
            center_v = vec3(center[0], center[1], 0)
            curpos = pygame.mouse.get_pos()
            curpos_v = vec3(curpos[0], curpos[1], 0)
            self.curr_celestial.radius = math.floor(glm.distance(center_v, curpos_v))
            self.setting_velocity = True

            center = self.curr_celestial.rect.center
            self.curr_velo_arrow = VelocityArrow(center)

    def __new_object_stage2_cont(self):
        """
        Private function to update velocity arrow
        """           
        if self.curr_celestial and self.curr_velo_arrow:
            self.curr_velo_arrow.arrow_end = pygame.mouse.get_pos()

    def __new_object_stage3(self):
        """
        Private function to complete celestial body with velocity
        """          
        if self.curr_celestial and self.curr_velo_arrow:
            # Replace functions to start over
            self.__input_fns["temp"] = self.app.inputs.inputs["new_object"].on_press(self.__new_object_stage1)            
            self.__input_fns["temp2"] = None

            vc = self.curr_velo_arrow.velocity_component
            vel = glm.vec3(vc.x, -vc.y, 0)
            self.curr_celestial.set_velocity(vel)

            #Clean up
            self.curr_celestial = None # completed drawing the celestial
            self.curr_velo_arrow = None
            self.paused = False


    def __kill_all_objects(self):
        """
        Private function to kill all objects
        """
        for o in self.celest_objs:
            o.kill()

    def update(self, delta_time):
        if not self.paused:
            self.celest_objs.update(delta_time)

    def draw(self):
        cvr = self.curr_velo_arrow
        if cvr:
            pygame.draw.line(self.app.screen, cvr.color, (cvr.start.x, cvr.start.y), (cvr.end.x, cvr.end.y), 2)
