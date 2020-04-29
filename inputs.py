from dataclasses import dataclass
import pygame
import weakref

from actions import ActionContainer

class ButtonInput:
    def match(self, event) -> bool:
         # Implement in inheriting class
        return False

    def update(self, event):
        if self.match(event):
            return self.pressed(event)
        return None

    def pressed(self, event) -> bool:
        # Implement in inheriting class
        return False

@dataclass(frozen=True)
class KeyPress(ButtonInput):
    value: int

    def match(self, event):
        return event.type in (pygame.KEYDOWN, pygame.KEYUP) and event.key == self.value

    def pressed(self, event) -> bool:
        """Whether a matching event is a press or a release"""
        return event.type == pygame.KEYDOWN
    
@dataclass(frozen=True)
class MousePress(ButtonInput):
    value: int

    def match(self, event):
        return event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and event.button == self.value

    def pressed(self, event) -> bool:
        """Whether a matching event is a press or a release"""
        return event.type == pygame.MOUSEBUTTONDOWN

@dataclass(frozen=True)
class MouseMove(ButtonInput):
    value: int

    def match(self, event):
        return event.type is (pygame.MOUSEMOTION)

    def pressed(self, event) -> bool:
        """Whether a matching event is a press or a release"""
        return True

class Inputs():
    def __init__(self):
        self.inputs = {}

    def update(self, dt):
        for i in self.inputs.values():
            i.update(dt)

    def register(self, name, button):
        self.inputs[name] = button

    def handle_events(self, events):
        for i in self.inputs.values():
            i.process_events(events)

class Button():
    def __init__(self, button_type, button):
        if button_type in (pygame.KEYDOWN, pygame.KEYUP):
            self.trigger = KeyPress(button)
        elif button_type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.trigger = MousePress(button)
        elif button_type is pygame.MOUSEMOTION:
            self.trigger = MouseMove(0)

        self._pressed_now = False
        self._released_now = False
        self._pressed_time = 0

        self._always = ActionContainer()
        self._on_press = ActionContainer()
        self._on_release = ActionContainer()
        self._on_press_repeat = ActionContainer()

    def process_events(self, events):
        self._pressed_now = False
        self._released_now = False
        
        for event in events:
            if self.trigger.match(event):
                if self.trigger.pressed(event):
                    self._pressed_now = True
                else:
                    self._released_now = True

    def update(self, dt):
        self._always()

        if self._pressed_now:
            self._on_press()
            self._pressed_time += dt

        if self._released_now:
            self._on_release()
            self._pressed_time = 0
        else:
            if self._pressed_time > 0:
                self._pressed_time += dt

        if self._pressed_time:
            self._on_press_repeat.block()
            for act in self._on_press_repeat.actions:
                if isinstance(act, weakref.ref):
                    wact = act
                    act = wact()
                    if not act:
                        continue
                if act.delay*act.repeat_count <= self._pressed_time:
                    act.repeat_count += 1
                    act()
            self._on_press_repeat.unblock()
        else:
            for act in self._on_press_repeat.actions:
                if isinstance(act, weakref.ref):
                    wact = act
                    act = wact()
                    if not act:
                        continue
                act.repeat_count = 0

    def always(self, func):
        return self._always.add(func)

    def on_press(self, func):
        return self._on_press.add(func)

    def on_release(self, func):
        return self._on_release.add(func)

    def on_press_repeat(self, func, repeat_delay):
        action = self._on_press_repeat.add(func)
        action.delay = repeat_delay
        action.repeat_count = 0
        return action