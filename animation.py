import os
import pygame

try:
    import pgzero
except ImportError:
    pgzero = None

if pgzero is not None:
    import pgzero.loaders
    import pgzero.actor

# TODO:
#   - Test combining multiple animations, like rotating and scaling an image-based animation
#   - Might be useful to have a "Tween" class (like in three.js)?
#   - AnimatedSprite and AnimatedActor classes


class Animation:
    def __init__(self, delay=100, loop=False):
        self.delay = delay
        self.loop = loop

        # initial state
        self.frames = []  # a list of surfaces
        self.animating = True
        self.frame_number = 0
        self._last_update = 0

    def update(self):
        if self.animating:
            # Advance frame according to timing
            now = pygame.time.get_ticks()
            if now - self._last_update > self.delay:
                self._last_update = now
                self._advance_frame()

    def _advance_frame(self):
        if (self.frame_number + 1) < len(self.frames):
            self.frame_number += 1
        elif self.loop:
            self.frame_number = 0
        else:
            self.animating = False

    @property
    def frame(self):
        return self.frames[self.frame_number]

    def draw(self, surface, *args, **kwargs):
        print(self.frame_number)
        surface.blit(self.frames[self.frame_number], *args, **kwargs)

    def play(self):
        """
        Plays the animation starting at the first frame
        """
        self.frame_number = 0
        self.animating = True

    def pause(self):
        """
        Pauses the animation at the current frame
        """
        self.animating = False

    def resume(self):
        """
        Resumes the animation at the current frame
        """
        self.animating = True

    def reset(self):
        """
        Sets the animation back to the first frame
        """
        self.frame_number = 0

    def is_ended(self):
        return self.frame_number == len(self.frames) - 1


class ImageAnimation(Animation):
    def __init__(self, path_format, num_frames, start, delay=100, loop=False, transparent=True, colorkey=None):
        """
        Loads images using the given path format and the given number of frames.
        The `path_format` argument is formatted using
        `path_format.format(frame)`, where frame_number is the current frame,
        starting at 1 (which can be changed via the `start` parameter).

        For example, if `path_format` is "images/walking_{}.png" and
        `num_frames` is 5, the following images will be loaded:

        - images/walking_1.png
        - images/walking_2.png
        - images/walking_3.png
        - images/walking_4.png
        - images/walking_5.png
        """
        super().__init__(delay, loop)
        pgz_load = pgzero is not None and pgzero.loaders.images.load or None

        self._images = []

        for i in range(start, start + num_frames):
            path = path_format.format(i)
            self._images.append(path)

            # try loading using pgzero if the path isn't found
            if not os.path.isfile(path) and pgz_load is not None:
                img = pgz_load(path)
            else:
                img = pygame.image.load(path)

            # pgzero always uses convert_alpha
            if transparent and not colorkey:
                img = img.convert_alpha()
            else:
                img = img.convert()
            if colorkey:
                img.set_colorkey(colorkey)

            self.frames.append(img)

    def get_image_name(self):
        return self._images[self.frame_number]

    def get_rect(self):
        return self.frame.get_rect()


class RotateAnimation(Animation):
    """
    TODO
    """
    pass


class SpriteSheetAnimation(Animation):
    """
    TODO
    """
    pass


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, animation=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: clone animation object
        self.animation = animation

    def update(self):
        self.animation.update()
        self.image = self.animation.frame


if pgzero is not None:
    class AnimatedActor(pgzero.actor.Actor):
        # TODO: Test this with Actor rotation
        def __init__(self, animation=None, **kwargs):
            self.animation=animation
            super().__init__(self.animation.get_image_name(), **kwargs)

        def draw(self):
            self.animation.update()
            self._image_name = self.animation.get_image_name()
            self._orig_surf = self._surf = self.animation.frame
            self._update_pos()
            super().draw()
