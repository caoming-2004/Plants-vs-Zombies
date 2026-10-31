"""Normalize SDL finger events into the pointer events used by the game UI."""


class TouchEventAdapter:
    def __init__(self, pygame_module, *, android=False):
        self.pygame = pygame_module
        self.android = android
        self.active_finger = None
        self.previous_position = None

    def translate(self, event, window_size):
        """Return a pygame mouse event for the first active finger, or None.

        SDL finger coordinates are normalized to the actual window. Existing
        desktop mouse events pass through unchanged; Android synthetic mouse
        events are dropped so each tap/drag produces exactly one input stream.
        """
        pg = self.pygame
        finger_down = getattr(pg, "FINGERDOWN", None)
        finger_motion = getattr(pg, "FINGERMOTION", None)
        finger_up = getattr(pg, "FINGERUP", None)
        if event.type in (finger_down, finger_motion, finger_up):
            finger_id = getattr(event, "finger_id", 0)
            if event.type == finger_down:
                if self.active_finger is not None:
                    return None
                self.active_finger = finger_id
            elif finger_id != self.active_finger:
                return None

            width, height = window_size
            position = (round(event.x * width), round(event.y * height))
            if event.type == finger_down:
                self.previous_position = position
                return pg.event.Event(pg.MOUSEBUTTONDOWN,
                                      {"pos": position, "button": 1})
            if event.type == finger_motion:
                previous = self.previous_position or position
                self.previous_position = position
                return pg.event.Event(
                    pg.MOUSEMOTION,
                    {"pos": position,
                     "rel": (position[0] - previous[0], position[1] - previous[1]),
                     "buttons": (1, 0, 0)},
                )

            self.active_finger = None
            self.previous_position = None
            return pg.event.Event(pg.MOUSEBUTTONUP,
                                  {"pos": position, "button": 1})

        mouse_events = {
            pg.MOUSEBUTTONDOWN,
            pg.MOUSEBUTTONUP,
            pg.MOUSEMOTION,
        }
        if event.type in mouse_events:
            if self.android or getattr(event, "touch", False):
                return None
        return event
