import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, MOUSEMOTION, K_SPACE, K_LEFT, K_RIGHT, K_UP, K_DOWN
import glm
from glm import vec2, vec3
import math

from constants import BACKGROUND_COLOR
from objects import CelestialObject, VelocityArrow
from inputs import Inputs, Button
from scene import CelestialScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

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

        self.scene = None

        if kwargs:
            raise ValueError(f"Some kwargs not consumed: {kwargs}")

    def update(self, delta_time):
        self.scene.update(delta_time)

    @property
    def scene_bg(self):
        return self.scene.background

    # @property
    # def sprites(self):
    #     return self.scene.content

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
        
        self.scene = CelestialScene(app)
        
        self.__static_input_funcs = []
        self.__dynamic_input_funcs = {}
        self.__build_inputs()

        self.curr_celestial = None
        self.curr_velo_arrow = None

        self.paused = False

    def __build_inputs(self):
        """
        Private function to bind inputs to functions
        """
        inputs = Inputs()
        
        inputs.register("new_object", Button(MOUSEBUTTONDOWN, 1))
        inputs.register("update", Button(MOUSEMOTION, 0))
        inputs.register("kill_all_objects", Button(KEYDOWN, K_SPACE))

        inputs.register("mleft", Button(KEYDOWN, K_LEFT))
        inputs.register("mright", Button(KEYDOWN, K_RIGHT))
        inputs.register("mup", Button(KEYDOWN, K_UP))
        inputs.register("mdown", Button(KEYDOWN, K_DOWN))
        inputs.register("zoomin", Button(MOUSEBUTTONDOWN, 4))
        inputs.register("zoomout", Button(MOUSEBUTTONDOWN, 5))

        self.app.inputs = inputs

        # Store functions to maintain weakrefs
        self.__dynamic_input_funcs["temp"] = self.app.inputs.inputs["new_object"].on_press(self.__new_object_stage1)

        # Add all the inputs that do not change
        #
        #
        # TODO: Needs a restructure so not referring down to scene
        #
        #
        self.__static_input_funcs.append(self.app.inputs.inputs["kill_all_objects"].on_press(self.scene.kill_all_objects))
        # self.__static_input_funcs.append(self.app.inputs.inputs["kill_all_objects"].on_press(self.__reset_new_object_stage))
        self.__static_input_funcs.append(self.app.inputs.inputs["mleft"].on_press_repeat(self.scene.move_cam_left, 0))
        self.__static_input_funcs.append(self.app.inputs.inputs["mright"].on_press_repeat(self.scene.move_cam_right, 0))
        self.__static_input_funcs.append(self.app.inputs.inputs["mup"].on_press_repeat(self.scene.move_cam_up, 0))
        self.__static_input_funcs.append(self.app.inputs.inputs["mdown"].on_press_repeat(self.scene.move_cam_down, 0))
        self.__static_input_funcs.append(self.app.inputs.inputs["zoomout"].on_press(self.scene.move_cam_out))
        self.__static_input_funcs.append(self.app.inputs.inputs["zoomin"].on_press(self.scene.move_cam_in))

    def __reset_new_object_stage(self):
        self.__dynamic_input_funcs["temp"] = self.app.inputs.inputs["new_object"].on_press(self.__new_object_stage1)
        self.__dynamic_input_funcs["temp2"] = None

    def __new_object_stage1(self):
        """
        Private function to create a new celestial object
        """
        if not self.curr_celestial:
            self.paused = True
            # Replace functions for next stage
            self.__dynamic_input_funcs["temp"] = self.app.inputs.inputs["new_object"].on_press_repeat(self.__new_object_stage1_cont, 0)
            self.__dynamic_input_funcs["temp2"] = self.app.inputs.inputs["new_object"].on_release(self.__new_object_stage2)

            center = pygame.mouse.get_pos()
            self.curr_celestial = CelestialObject(center) #set radius to 0 so the initializer will set PLANET_MIN_RADIUS
    
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
            self.__dynamic_input_funcs["temp"] = self.app.inputs.inputs["update"].always(self.__new_object_stage2_cont)
            self.__dynamic_input_funcs["temp2"] = self.app.inputs.inputs["new_object"].on_press(self.__new_object_stage3)
            
            center = self.curr_celestial.rect.center
            center_v = vec3(center[0], center[1], 0)
            curpos = pygame.mouse.get_pos()
            curpos_v = vec3(curpos[0], curpos[1], 0)
            self.curr_celestial.radius = math.floor(glm.distance(center_v, curpos_v))
            self.setting_velocity = True

            center = self.curr_celestial.rect.center
            self.curr_velo_arrow = VelocityArrow(center)
            # self.scene.transient_objs.append(self.curr_velo_arrow)

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
            self.__dynamic_input_funcs["temp"] = self.app.inputs.inputs["new_object"].on_press(self.__new_object_stage1)            
            self.__dynamic_input_funcs["temp2"] = None

            vc = self.curr_velo_arrow.velocity_component
            vel = glm.vec3(vc.x, -vc.y, 0)
            self.curr_celestial.velocity = vel

            # Add celestial to the scene with add_new_celestial function to have world_offset applied
            self.scene.add_new_celestial(self.curr_celestial)

            #Clean up
            self.curr_celestial = None # completed drawing the celestial
            self.curr_velo_arrow.dead = True
            self.curr_velo_arrow = None
            self.paused = False

    def update(self, delta_time):
        if not self.paused:
            # Update the current celestial being drawn
            if self.curr_celestial:
                self.curr_celestial.update(delta_time)

            # Update the scene
            self.scene.update(delta_time)

    def draw(self):
        # Blit currently drawing celestial
        if self.curr_celestial:
            self.app.screen.blit(self.curr_celestial.image, (self.curr_celestial.rect.x, self.curr_celestial.rect.y))

        if self.curr_velo_arrow:
            self.curr_velo_arrow.draw(self.app.screen)

        # Draw teh scene
        self.scene.draw(self.app.screen)