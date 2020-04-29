import pygame
import glm
from glm import vec2, vec3
import math

from constants import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

class SpriteEntity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class CelestialObject(SpriteEntity):
    def __init__(self, group, center, **kwargs):
        super().__init__()   

        self.neighbours = group

        radius = kwargs.pop("radius", 0)
        self.density = kwargs.pop("density", PLANET_DEFAULT_DENSITY)
        
        self.__radius = self.__correct_radius(radius)
        self.mass = self.density*self.__radius**3          #not real mass, but proportional to it (missing 4/3*PI)
        
        self.F = vec3(0)
        self.acc = vec3(0)
        self.vel = vec3(0)

        size = 2*self.__radius+2
        surf = pygame.Surface([size]*2, pygame.SRCALPHA)
        pygame.draw.circle(surf, PLANET_COLOR, [self.__radius]*2, self.__radius)
        self.image = surf.convert_alpha()
        self.rect = self.image.get_rect(center=center)        
        
    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, r):
        r = self.__correct_radius(r)
        size = 2*r+2        
        surf = pygame.Surface([size]*2, pygame.SRCALPHA)
        pygame.draw.circle(surf, PLANET_COLOR, [r]*2, r)
        self.image = surf.convert_alpha()
        self.rect = self.image.get_rect(center=self.rect.center)            
        self.mass = self.density*r**3
        self.__radius = r
        

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

    def set_velocity(self, vel : vec3):
        '''
        Takes the length of an arrow and sets the velocity proportional to it.
        '''
        self.vel.x = vel.x * ARROW_TO_VEL_RATIO
        self.vel.y = vel.y * ARROW_TO_VEL_RATIO
        self.vel.z = 0
    
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
                obj.F.x -= f.x
                obj.F.y -= f.y
            
        self.acc.x = self.F.x / self.mass
        self.acc.y = self.F.y / self.mass
        
        center = vec3(self.rect.center[0], self.rect.center[1], 0)
        center.x += self.vel.x * DELTA_T + 0.5 * self.acc.x * DELTA_T
        center.y += self.vel.y * DELTA_T + 0.5 * self.acc.y * DELTA_T
        
        self.vel.x += self.acc.x * DELTA_T
        self.vel.y += self.acc.y * DELTA_T
        
        self.F = vec3(0) #resets force for the next iteration

        return center

    def update(self, dt):
        new_center = self.__integration_euler()
        self.rect.center = (new_center.x, new_center.y)
        

    def __get_force(self, obj) -> vec3:
        '''
        Return the force between self and obj.
        '''
        self_ctr = vec3(self.rect.center[0], self.rect.center[1], 0)
        othr_ctr = vec3(obj.rect.center[0], obj.rect.center[1], 0)

        vect = vec3(othr_ctr.x - self_ctr.x, othr_ctr.y - self_ctr.y, 0)
        print(f"Force vector {vect}")
        dist = glm.distance(self_ctr, othr_ctr)
        factor = self.mass * obj.mass / dist**3 #Power of 3 because the directional vector is not normalized
        print(f"Force factor {factor} | from self mass: {self.mass}, other mass: {obj.mass} and dist {dist}")
        return vec3(vect.x*factor, vect.y*factor, 0)
    
    # def integration_euler(self):
    #     '''Calculates the new position and velocity using Euler integration method.
        
    #     The force is also added to the other object so it doesn't have to be 
    #     calculated twice.'''
    #     for obj in self.neighbours:
    #         f = self.get_force(obj)

    #         self.F[0] += f[0]
    #         self.F[1] += f[1]
    #         obj.F[0] -= f[0]
    #         obj.F[1] -= f[1]
            
    #     self.acc[0] = self.F[0] / self.mass
    #     self.acc[1] = self.F[1] / self.mass
        
    #     self.rect.center[0] += self.vel[0] * DELTA_T + 0.5 * self.acc[0] * DELTA_T
    #     self.rect.center[1] += self.vel[1] * DELTA_T + 0.5 * self.acc[1] * DELTA_T
        
    #     self.vel[0] += self.acc[0] * DELTA_T
    #     self.vel[1] += self.acc[1] * DELTA_T
        
    #     self.F = [0, 0] #resets force for the next iteration

class VelocityArrow():
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
