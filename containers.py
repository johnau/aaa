import pygame
from objects import CelestialObject

class CelestialSpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.__id_track = 1

    def add(self, *celestials):
        for celestial in celestials:
            if isinstance(celestial, CelestialObject):
                celestial.id = "CB" + str(self.__id_track)

                print(f"Added a new Celestial Body with id: {celestial.id}")

                self.__id_track += 1
        # call the pygame.sprite.Group() add method
        super().add(*celestials)            

    def draw(self, surface):
        super().draw(surface)