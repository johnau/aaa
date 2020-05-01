from glm import vec2, vec3
import pygame

from constants import BACKGROUND_COLOR, CAM_MOVE_SPEED, CAM_ZOOM_AMOUNT, ZOOM_MIN, ZOOM_MAX, TYPE_ACCEL, TYPE_VEL
from objects import CelestialObject, SpriteEntity, TransientDrawEntity, TextObject, VelocityArrow
from containers import CelestialSpriteGroup

class Camera():
    def __init__(self):
        self.fov = 90
        self.position = vec3(0)
        self.tilt = 0
        self.yaw = 0

    def shift(self, v : vec3):
        self.position += v

class Scene():
    def __init__(self, app):
        self.app = app

        self.background = BACKGROUND_COLOR
        self.content = pygame.sprite.RenderUpdates()
        self.camera = Camera()

    def move_cam_left(self):
        self.camera.shift(vec3(CAM_MOVE_SPEED, 0, 0))

    def move_cam_right(self):
        self.camera.shift(vec3(-CAM_MOVE_SPEED, 0, 0))

    def move_cam_up(self):
        self.camera.shift(vec3(0, CAM_MOVE_SPEED, 0))

    def move_cam_down(self):
        self.camera.shift(vec3(0, -CAM_MOVE_SPEED, 0))

    def move_cam_out(self):
        if (self.camera.position.z > ZOOM_MIN):
            self.camera.shift(vec3(0, 0, -CAM_ZOOM_AMOUNT))
        else:
            print("Can't zoom out further")

    def move_cam_in(self):
        if (self.camera.position.z < ZOOM_MAX):
            self.camera.shift(vec3(0, 0, CAM_ZOOM_AMOUNT))
        else:
            print("Can't zoom in further")

    def update(self, delta_time):
        # Update all sprites in the scene.content
        self.content.update(delta_time)

    def draw(self, surface : pygame.Surface):
        # Draw all sprites in scene.content
        dirty_rects = self.content.draw(surface)  # TODO: handle dirty rects back up to App.draw()

class CelestialScene(Scene):
    """
    Celestial Scene Class
    - Handles graphical elements
    """
    def __init__(self, app):
        super().__init__(app)

        self.celest_objs = CelestialSpriteGroup()
        self.transient_objs = []
        
        self.__camera_pos_disp = TextObject('X: 0, Y: 0 | Zoom: 0%', self.app.font, (0,0,0))

    def add_new_celestial(self, new_celestial):
        # New celestial instance with world_offset
        ctr = new_celestial.rect.center
        world_ctr = (ctr[0] + int(-self.camera.position.x), ctr[1] + int(-self.camera.position.y))
        new_celestial.position = world_ctr
        
        # Set the group to the celestial
        new_celestial.neighbours = self.celest_objs

        # Add to sprite.Group() for processing
        self.celest_objs.add(new_celestial)
        
        # Add to scene sprite.Group() for drawing
        self.content.add(new_celestial)

        # Add vector arrows to for celestial
        arr_accel = VelocityArrow(new_celestial.position, new_celestial, color=(200,0,0), indicator_type=TYPE_ACCEL, thickness=1)
        arr_vel = VelocityArrow(new_celestial.position, new_celestial, color=(0,70,170), indicator_type=TYPE_VEL, thickness=1)

        self.transient_objs.append(arr_accel)
        self.transient_objs.append(arr_vel)

        return new_celestial

    def kill_all_objects(self):
        """
        Private function to kill all objects
        """
        # Iterate and call pygame.sprite.Sprite kill() function to remove from any pygame.sprite.Groups()
        for o in self.celest_objs:
            o.kill()
        
        # Clear all transients
        self.transient_objs.clear()

        print(f"Killed all objects: Celestials: {len(self.celest_objs)}, Transients: {len(self.transient_objs)}")

    def update(self, delta_time):
        """
        Update Scene
        """
        super().update(delta_time)

        # Update Camera Position Text Display
        cam_text = f"X: {self.camera.position.x}, Y: {self.camera.position.y} | Zoom: {self.camera.position.z+100}%"
        self.__camera_pos_disp.text = cam_text

        # Call update() method of all sprites in the sprite.Group()
        self.celest_objs.update(delta_time)

        # Iterate sprite group
        for o in self.celest_objs:
            # Update world offset for all items
            if isinstance(o, SpriteEntity):
                o.world_offset = self.camera.position

            # Reset 'just_calcd' variable for next frame
            if isinstance(o, CelestialObject):
                o.force_just_calcd = False

        # Iterate transient non-sprite graphical objects list (in reverse to protect when removing)
        for t in reversed(self.transient_objs):
            # Update world offset, call update() and remove expired Transients
            if isinstance(t, TransientDrawEntity):
                t.world_offset = self.camera.position
                t.update(delta_time)
                if t.dead:
                    self.transient_objs.remove(t)

    def draw(self, surface : pygame.Surface):
        """
        Draw function
        - Handles drawing any objects that are not automatically drawn through sprite.Group()s
        """
        # Call super() draw() function to draw scene.content
        super().draw(surface)

        # Draw sprites in sprite.Group()
        self.celest_objs.draw(surface)

        # Iterate all Transient objects and call .draw() func
        for t in self.transient_objs:
            if isinstance(t, TransientDrawEntity):
                t.draw(surface)

        self.__camera_pos_disp.draw(surface)