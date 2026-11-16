"""Paint a humanoid skin face by face for the zombie model (64x64). Unpainted pixels are transparent, which matters:
the model's outer "hat" layer reads the area x 32..63, y 0..15, and an opaque black there renders as a black box on the head.
"""
from .pix import h, shade
from .png import write_png

# face rectangles (x0, y0, x1, y1) on the standard layout
HEAD = dict(top=(8, 0, 15, 7), bottom=(16, 0, 23, 7), right=(0, 8, 7, 15), front=(8, 8, 15, 15), left=(16, 8, 23, 15), back=(24, 8, 31, 15))
BODY = dict(top=(20, 16, 27, 19), bottom=(28, 16, 35, 19), right=(16, 20, 19, 31), front=(20, 20, 27, 31), left=(28, 20, 31, 31), back=(32, 20, 39, 31))
RARM = dict(top=(44, 16, 47, 19), bottom=(48, 16, 51, 19), right=(40, 20, 43, 31), front=(44, 20, 47, 31), left=(48, 20, 51, 31), back=(52, 20, 55, 31))
LARM = dict(top=(36, 48, 39, 51), bottom=(40, 48, 43, 51), right=(32, 52, 35, 63), front=(36, 52, 39, 63), left=(40, 52, 43, 63), back=(44, 52, 47, 63))
RLEG = dict(top=(4, 16, 7, 19), bottom=(8, 16, 11, 19), right=(0, 20, 3, 31), front=(4, 20, 7, 31), left=(8, 20, 11, 31), back=(12, 20, 15, 31))
LLEG = dict(top=(20, 48, 23, 51), bottom=(24, 48, 27, 51), right=(16, 52, 19, 63), front=(20, 52, 23, 63), left=(24, 52, 27, 63), back=(28, 52, 31, 63))
PARTS = dict(head=HEAD, body=BODY, rarm=RARM, larm=LARM, rleg=RLEG, lleg=LLEG)
SIDES = ("right", "front", "left", "back")


class Skin:
    def __init__(self):
        self.px = {}

    def fill(self, x0, y0, x1, y1, c, noise=0, salt=1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                d = ((h(x, y, salt) % (2 * noise + 1)) - noise) if noise else 0
                self.px[(x, y)] = shade(c, d)

    def face(self, part, name, c, noise=0, salt=1):
        self.fill(*PARTS[part][name], c, noise, salt)

    def put(self, x, y, c):
        self.px[(x, y)] = c

    def save(self, path):
        write_png(path, 64, 64, [(*self.px[(x, y)], 255) if (x, y) in self.px else (0, 0, 0, 0) for y in range(64) for x in range(64)])
