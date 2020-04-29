import pygame
import glm
from glm import vec2, vec3
import math

from constants import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

class SpriteEntity(pygame.sprite.Sprite):
    """
    Base class for objects that will be drawn to the screen and derive from pygame.sprite.Sprite
    """
    def __init__(self):
        super().__init__()

        self.world_offset = vec3(0)

    def update(self, dt):
        self.rect.x += int(self.world_offset.x)
        self.rect.y += int(self.world_offset.y)

class CelestialObject(SpriteEntity):
    def __init__(self, center, **kwargs):
        super().__init__()   

        self.neighbours = pygame.sprite.Group()

        radius = kwargs.pop("radius", 0)
        self.density = kwargs.pop("density", PLANET_DEFAULT_DENSITY)
        
        self.__radius = self.__correct_radius(radius)
        self.mass = self.density*(4/3*math.pi*(self.__radius**3)) 
        
        self.F = vec3(0)
        self.acc = vec3(0)
        self.vel = vec3(0)
        self.pos = vec3(center[0], center[1], 0)

        size = 2*self.__radius+2
        surf = pygame.Surface([size]*2, pygame.SRCALPHA)
        pygame.draw.circle(surf, PLANET_COLOR, [self.__radius]*2, self.__radius)
        self.image = surf.convert_alpha()
        self.rect = self.image.get_rect(center=center)

        # Store the original image copy to prevent scale transform artifacts
        self.__zero_image = self.image.convert_alpha()

        self.force_just_calcd = False  

    ###
    ### Properties
    ###

    @property
    def radius(self):
        """
        Getter for radius
        """
        return self.__radius

    @radius.setter
    def radius(self, r):
        """
        Setter for radius
        - Resets image, rect, mass and radius
        """
        r = self.__correct_radius(r)
        size = 2*r+2        
        surf = pygame.Surface([size]*2, pygame.SRCALPHA)
        pygame.draw.circle(surf, PLANET_COLOR, [r]*2, r)
        self.image = surf.convert_alpha()
        self.rect = self.image.get_rect(center=self.rect.center)            
        self.mass = self.density*r**3
        self.__radius = r

        # Store original image copy to prevent scale transform artifacts
        self.__zero_image = self.image.convert_alpha()

    @property
    def velocity(self):
        """
        Getter for velocity
        """
        return self.vel

    @velocity.setter
    def velocity(self, vel : vec3):
        """
        Setter for velocity
        - Takes the length of an arrow and sets the velocity proportional to it.
        """
        self.vel.x = vel.x * ARROW_TO_VEL_RATIO
        self.vel.y = vel.y * ARROW_TO_VEL_RATIO
        self.vel.z = 0

    @property
    def position(self):
        return self.pos

    @position.setter
    def position(self, pos):
        if isinstance(pos, tuple):
            self.pos = vec3(pos[0], pos[1], 0)
            self.rect.center = pos
        elif isinstance(pos, vec3):
            self.pos = pos
            self.rect.center = (pos.x, pos.y)

    ###
    ### Public functions
    ###

    def update(self, dt):
        """
        Update function
        """
        super().update(dt) # This is a waste right now but will leave
        
        # Euler function
        self.__integration_euler()

        # Update rect position from actual position
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Update rect position based on world offset
        wx = self.rect.center[0] + int(self.world_offset.x)
        wy = self.rect.center[1] + int(self.world_offset.y)
        center_in_world = (wx, wy)
        self.rect.center = center_in_world

        # Update image + rect (but not radius?) for zoom
        if self.world_offset.z != 0:
            # Calc new drawing diameter
            zoom_perc = (self.world_offset.z+100)/100
            draw_diam = int(self.__radius*zoom_perc)
            
            # Check if we need to scale
            if draw_diam != self.rect.width:
                # Check if we even need to show the body anymore
                if draw_diam > 0:
                    new_size = [draw_diam]*2
                    self.image = pygame.transform.scale(self.__zero_image, new_size)
                else:
                    surf = pygame.Surface((1,1)).convert_alpha()
                    surf.fill(PLANET_COLOR)
                    self.image = surf

                self.rect = self.image.get_rect(center = (self.rect.center))
    ###
    ### Private functions 
    ###

    def __correct_radius(self, radius):
        """
        Private function to limit radius min and max
        (used by __init__ and in radius @setter)
        """
        if radius > PLANET_MAX_RADIUS:
            return PLANET_MAX_RADIUS
        elif radius < PLANET_MIN_RADIUS:
            return PLANET_MIN_RADIUS

        return radius
    
    def __integration_euler(self):
        '''
        Calculates the new position and velocity using Euler integration method.
        
        The force is also added to the other object so it doesn't have to be 
        calculated twice.
        '''
        for obj in self.neighbours:
            if obj != self:
                f = self.__get_force(obj)
                self.F.x += f.x
                self.F.y += f.y
                if not self.force_just_calcd:                
                    obj.F.x -= f.x
                    obj.F.y -= f.y
                    obj.force_just_calcd = True
        self.force_just_calcd = True
            
        self.acc.x = self.F.x / self.mass
        self.acc.y = self.F.y / self.mass
        
        self.pos.x += self.vel.x * DELTA_T + 0.5 * self.acc.x * DELTA_T
        self.pos.y += self.vel.y * DELTA_T + 0.5 * self.acc.y * DELTA_T
        
        self.vel.x += self.acc.x * DELTA_T
        self.vel.y += self.acc.y * DELTA_T
        
        self.F = vec3(0) #resets force for the next iteration
        
    def __get_force(self, obj) -> vec3:
        '''
        Return the force between self and obj.
        '''
        vect = vec3(obj.pos.x - self.pos.x, obj.pos.y - self.pos.y, 0)
        dist = glm.distance(self.pos, obj.pos)
        factor = self.mass * obj.mass / dist**3 #Power of 3 because the directional vector is not normalized
        return vec3(vect.x*factor, vect.y*factor, 0)
    
class TransientDrawEntity():
    """
    Base class for Objects that will be drawn to screen but do not derive from pygame.sprite.Sprite
    """
    def __init__(self):
        self.dead = False
        self.world_offset = vec3(0)

    def update(self, dt):
        pass

    def draw(self, surface : pygame.Surface):
        pass

class VelocityArrow(TransientDrawEntity):
    component = vec3(0)
    length = 0.0
    angle = 0.0

    def __init__(self, start, **kwargs):
        self.start = vec3(start[0], start[1], 0)
        self.end = vec3(start[0]+1, start[1]+1, 0)

        self.color = kwargs.pop("color", ARROW_COLOR_VEL)
        self.thickness = kwargs.pop("thickness", ARROW_HALF_THICKNESS)
        self.cap_angle = kwargs.pop("cap_angle", ARROW_CAP_ANGLE)
        self.cap_length = kwargs.pop("cap_length", ARROW_CAP_LENGTH)

    @property
    def arrow_end(self):
        return self.end

    @arrow_end.setter
    def arrow_end(self, e):
        # print(f"Updating arrow endpoint {e}")
        self.end = vec3(e[0], e[1], 0)
        self.__limit_length()

    def __limit_length(self):
        length = glm.distance(self.start, self.end)
        if length > ARROW_MAX_LENGTH:
            self.end = vec3((self.end.x - self.start.x) / length * ARROW_MAX_LENGTH + self.start.x, 
                        (self.end.y - self.start.y) / length * ARROW_MAX_LENGTH + self.start.y,
                        0)
        self.length = glm.distance(self.start, self.end)

    @property
    def velocity_component(self) -> vec3:
        self.angle = math.atan2(self.start.y - self.end.y, self.end.x - self.start.x)
        v = vec3(self.length * math.cos(self.angle), self.length * math.sin(self.angle), 0)  
        return v

    def update(self, dt):
        super().update(dt)
        self.start += self.world_offset
        self.end += self.world_offset

    def draw(self, surface : pygame.Surface):
        super().draw(surface)
        pygame.draw.line(surface, self.color, (self.start.x, self.start.y), (self.end.x, self.end.y), 2)    


class TextObject(TransientDrawEntity):
    def __init__(self, text, font : pygame.font, color):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color

    def draw(self, surface : pygame.Surface):
        super().draw(surface)
        pycol = pygame.Color(self.color[0], self.color[1], self.color[2])
        rtxt = self.font.render(self.text, False, pycol)
        rsiz = self.font.size(self.text)
        surface.blit(rtxt, (5, 5))

