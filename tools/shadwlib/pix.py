"""Sprite and block-texture helpers. Unpainted pixels are transparent when saved."""
import math

from .png import write_png


def h(x, y, salt=0):
    """Deterministic noise in [0, 100): the same input always gives the same value, so regenerating changes nothing."""
    return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) % 100


def shade(c, d):
    return tuple(max(0, min(255, v + d)) for v in c[:3])


class Pix:
    def __init__(self, w=16, hh=16):
        self.w, self.h = w, hh
        self.p = {}

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[(x, y)] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        n = max(abs(x1 - x0), abs(y1 - y0)) * 2 or 1
        for i in range(n + 1):
            x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
            for dx in range(thick):
                for dy in range(thick):
                    self.put(x + dx, y + dy, c)

    def disc(self, cx, cy, r, c):
        for y in range(self.h):
            for x in range(self.w):
                if math.hypot(x - cx, y - cy) <= r:
                    self.put(x, y, c)

    def outline(self, c=(11, 11, 13)):
        add = {}
        for (x, y) in self.p:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                k = (x + dx, y + dy)
                if k not in self.p and 0 <= k[0] < self.w and 0 <= k[1] < self.h:
                    add[k] = c
        self.p.update(add)

    def save(self, path):
        px = [(*self.p[(x, y)][:3], 255) if (x, y) in self.p else (0, 0, 0, 0) for y in range(self.h) for x in range(self.w)]
        write_png(path, self.w, self.h, px)


def tex(fn, size=16):
    """A fully painted square texture from fn(x, y) -> (r, g, b)."""
    p = Pix(size, size)
    for y in range(size):
        for x in range(size):
            p.put(x, y, fn(x, y))
    return p
