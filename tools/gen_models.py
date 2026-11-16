#!/usr/bin/env python3
"""Author the Satyr and Gorgon entity models (the "model" section of mobs/satyr.json and mobs/gorgon.json).

    python3 tools/gen_models.py && shadw-mod mob . gen

Edit this script, not the JSON. Coordinates are Minecraft model pixels: +y is down, -z is forward, "root" sits at the feet; a positive
x rotation swings the bottom of a part backward. See adapters/minecraft-fabric/mobmodel.py in shadw-modding.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def box(frm, size, paint, grow=0, decals=None):
    b = {"from": list(frm), "size": list(size), "grow": grow, "paint": paint}
    if decals:
        b["decals"] = decals
    return b


def part(name, parent, pivot, rot, boxes):
    return {"name": name, "parent": parent, "pivot": list(pivot), "rot": list(rot), "boxes": boxes}


def rect(face, x, y, w, h, color):
    return {"face": face, "type": "rect", "x": x, "y": y, "w": w, "h": h, "color": color}


def mirror(side, x):
    return -x if side == "r" else x


# ======================= SATYR =======================
def satyr():
    P, A = [], []
    paints = {
        "skin": {"type": "skin", "base": "#c9946a", "shade": 5},
        "face": {"type": "skin", "base": "#d09c70", "shade": 4},
        "fur": {"type": "fur", "base": "#6b4a2c", "dark": "#3b2616", "light": "#9a7448"},
        "fur_dark": {"type": "fur", "base": "#4a321c", "dark": "#2a1a0e", "light": "#6e4c2c"},
        "hair": {"type": "fur", "base": "#53351d", "dark": "#2e1c0e", "light": "#8a5e34"},
        "horn": {"type": "ridged", "base": "#e6dcc0", "dark": "#8f7f5c", "light": "#fff6dc"},
        "hoof": {"type": "plain", "base": "#2a2220"},
        "bamboo": {"type": "ridged", "base": "#d8b868", "dark": "#8a6a30", "light": "#f0d890"},
        "bind": {"type": "cloth", "base": "#7a2a2a", "trim": "#c9a050"},
        "ear": {"type": "skin", "base": "#b87c58", "shade": 4},
    }
    # head, with a long goat face, a goatee, shaggy hair, pointed ears
    eyes = []
    for ex in (1, 5):
        eyes += [rect("front", ex, 3, 2, 2, "#e8a820"), rect("front", ex, 4, 2, 1, "#120a04")]   # amber eye, horizontal goat pupil
    P.append(part("head", "root", (0, -28, 0), (0, 0, 0), [
        box((-4, -8, -4), (8, 8, 8), "face", 0, eyes + [rect("front", 0, 2, 3, 1, "#3a2414"), rect("front", 5, 2, 3, 1, "#3a2414"), rect("front", 2, 6, 4, 1, "#7a3a2a")]),
        box((-2.5, -4, -8.5), (5, 4, 4), "face", 0, [rect("front", 0, 1, 1, 1, "#2a1810"), rect("front", 4, 1, 1, 1, "#2a1810"), rect("front", 1, 3, 3, 1, "#6a3424")]),   # a long goat muzzle, nostrils, mouth
        box((-1.5, -0.5, -6.5), (3, 7, 3), "fur_dark"),                                                                            # a long goatee
        box((-4.5, -9, -4.5), (9, 3, 9), "hair"),                                                                              # a mop of hair on top
        box((-4.5, -6, -1), (1, 5, 5), "hair"), box((3.5, -6, -1), (1, 5, 5), "hair"),                                          # side locks
        box((-4.5, -9, 3.5), (9, 8, 1), "hair"),                                                                               # back of the head
    ]))
    for side in ("l", "r"):
        sx = 1 if side == "l" else -1
        # ears: long and pointed, out to the side
        P.append(part(f"ear_{side}", "head", (sx * 4, -6, 0.5), (0, sx * 20, sx * -28), [box((0 if sx > 0 else -7, -2, -0.5), (7, 4, 1), "ear")]))
        # ram horns: a chain of fat segments that sweeps up, curls back, down and round past the ear
        P.append(part(f"horn_{side}1", "head", (sx * 2.8, -8.5, -1.5), (-24, 0, sx * 20), [box((-2, -4, -2), (4, 4, 4), "horn")]))
        P.append(part(f"horn_{side}2", f"horn_{side}1", (0, -4, 0), (-34, 0, sx * 10), [box((-2, -4, -2), (4, 4, 4), "horn")]))
        P.append(part(f"horn_{side}3", f"horn_{side}2", (0, -4, 0), (-42, 0, sx * 8), [box((-1.5, -4, -1.5), (3, 4, 3), "horn")]))
        P.append(part(f"horn_{side}4", f"horn_{side}3", (0, -4, 0), (-48, 0, sx * 10), [box((-1.5, -4, -1.5), (3, 4, 3), "horn")]))
        P.append(part(f"horn_{side}5", f"horn_{side}4", (0, -4, 0), (-46, 0, sx * 8), [box((-1, -4, -1), (2, 4, 2), "horn")]))
        P.append(part(f"horn_{side}6", f"horn_{side}5", (0, -4, 0), (-40, 0, sx * 6), [box((-0.5, -3, -0.5), (1, 3, 1), "horn")]))
    # torso: bare chest with a dark hair patch, a shaggy goat-hair skirt
    P.append(part("body", "root", (0, -28, 0), (0, 0, 0), [
        box((-4, 0, -2), (8, 12, 4), "skin", 0, [rect("front", 2, 1, 4, 2, "#5a3a22"), rect("front", 3, 3, 2, 3, "#5a3a22"), rect("front", 1, 8, 2, 1, "#a8774f"), rect("front", 5, 8, 2, 1, "#a8774f"),
                                                    rect("front", 3, 6, 2, 1, "#a8774f")])]))
    P.append(part("loin", "root", (0, -17, 0), (0, 0, 0), [box((-4.5, 0, -2.5), (9, 5, 5), "fur")]))
    P.append(part("tail", "root", (0, -17, 2.2), (38, 0, 0), [box((-1, 0, -1), (2, 4, 2), "fur")]))
    # arms. The right arm bends up to a pan flute at the mouth.
    P.append(part("arm_l", "root", (6, -26, 0), (0, 0, 0), [box((-2, -2, -2), (4, 12, 4), "skin"), box((-2, 6, -2), (4, 3, 4), "fur", 0.4)]))
    P.append(part("arm_r", "root", (-6, -26, 0), (-50, 0, 0), [box((-2, -2, -2), (4, 7, 4), "skin")]))
    P.append(part("forearm_r", "arm_r", (0, 5, 0), (-90, 0, 0), [box((-2, 0, -2), (4, 5, 4), "skin"), box((-2, 3, -2), (4, 3, 4), "fur", 0.4)]))
    P.append(part("flute", "forearm_r", (0, 5, 0), (140, 0, 0), [box((-5.5, 0, -1.5), (11, 1, 3), "bind")] + [
        box((-5 + 2 * i, 1, -1), (2, L, 2), "bamboo") for i, L in enumerate((7, 6, 5, 4, 3))]))
    # goat legs: thigh forward, shin back, pastern, hoof
    for side in ("l", "r"):
        sx = 1 if side == "l" else -1
        P.append(part(f"leg_{side}", "root", (sx * 2.6, -15.25, 0), (0, 0, 0), []))
        P.append(part(f"thigh_{side}", f"leg_{side}", (0, 0, 0), (-38, 0, 0), [box((-2, 0, -2), (4, 6, 4), "fur")]))
        P.append(part(f"shin_{side}", f"thigh_{side}", (0, 6, 0), (76, 0, 0), [box((-1, 0, -1), (2, 7, 2), "fur_dark"), box((-1.5, 3, -1.5), (3, 3, 3), "fur", 0.2)]))
        P.append(part(f"pastern_{side}", f"shin_{side}", (0, 7, 0), (-38, 0, 0), [box((-1, 0, -1), (2, 3, 2), "fur_dark")]))
        P.append(part(f"hoof_{side}", f"pastern_{side}", (0, 3, 0), (0, 0, 0), [box((-1.5, 0, -2.5), (3, 2, 4), "hoof")]))
    A += [{"part": "head", "type": "look"},
          {"part": "arm_l", "type": "walk", "axis": "x", "amp": 1.0, "phase": 0}, {"part": "arm_l", "type": "sway", "axis": "z", "amp": 0.04, "freq": 0.09, "phase": 0},
          {"part": "arm_r", "type": "sway", "axis": "x", "amp": 0.05, "freq": 0.11, "phase": 1.0},
          {"part": "leg_l", "type": "walk", "axis": "x", "amp": 1.0, "phase": math.pi}, {"part": "leg_r", "type": "walk", "axis": "x", "amp": 1.0, "phase": 0},
          {"part": "ear_l", "type": "sway", "axis": "z", "amp": 0.10, "freq": 0.17, "phase": 0}, {"part": "ear_r", "type": "sway", "axis": "z", "amp": 0.10, "freq": 0.17, "phase": 1.6},
          {"part": "tail", "type": "sway", "axis": "x", "amp": 0.18, "freq": 0.21, "phase": 0, "walk_amp": 0.3}]
    return {"shadow": 0.5, "paints": paints, "parts": P, "anim": A}


# ======================= GORGON =======================
def gorgon():
    P, A = [], []
    paints = {
        "skin": {"type": "scales", "base": "#6a9a4c", "dark": "#33602c", "light": "#a8d878", "cell": 4},
        "face": {"type": "skin", "base": "#7aa858", "shade": 4},
        "tail": {"type": "scales", "base": "#4f8440", "dark": "#244a24", "light": "#98c868", "cell": 4},
        "snake": {"type": "scales", "base": "#3e7a3a", "dark": "#1c4420", "light": "#8cc25c", "cell": 3},
        "bronze": {"type": "metal", "base": "#b07a3a", "dark": "#6a4620", "light": "#e0b060"},
        "gold": {"type": "metal", "base": "#e0b838", "dark": "#8a6a14", "light": "#fff0a0"},
        "cloth": {"type": "cloth", "base": "#cfc2a0", "trim": "#9a2a2a"},
        "ivory": {"type": "plain", "base": "#efe6cc"},
        "claw": {"type": "plain", "base": "#d8d0b8"},
        "tongue": {"type": "plain", "base": "#b02838"},
    }
    eyes = []
    for ex in (1, 5):
        eyes += [rect("front", ex, 3, 2, 2, "#ecf24a"), rect("front", ex, 3, 1, 2, "#101808")]    # glowing eyes with a slit pupil
    P.append(part("head", "root", (0, -26, 0), (0, 0, 0), [
        box((-4, -8, -4), (8, 8, 8), "face", 0, eyes + [rect("front", 1, 2, 2, 1, "#244a24"), rect("front", 5, 2, 2, 1, "#244a24"), rect("front", 1, 6, 6, 1, "#1a1008"), rect("front", 3, 5, 2, 1, "#244a24")]),
        box((-3, -2.5, -4.6), (1, 3, 1), "ivory"), box((2, -2.5, -4.6), (1, 3, 1), "ivory"),                       # tusks
        box((-1, -1.2, -5.2), (2, 1, 2), "tongue"),                                                                  # tongue
        box((-4.5, -6.5, -4.5), (9, 1, 9), "bronze"),                                                                # a bronze circlet
    ]))
    # snakes for hair: a mane of twelve, each a chain of four that rises and arches outward and down, like a Medusa's
    n = 12
    for k in range(n):
        th = 2 * math.pi * k / n + 0.2
        xd, zd = math.sin(th), math.cos(th)                    # outward direction (+z is the back of the head)
        sx, sz = xd * 3.2, zd * 3.2
        lean = 22 if zd < -0.5 else 34                         # lean the front ones less so the face stays clear
        tag = f"{k:02d}"
        nm = f"sn{tag}"
        rx0, rz0 = -zd * lean, xd * lean
        sizes = [((3, 4, 3), (-1.5, -4, -1.5)), ((3, 4, 3), (-1.5, -4, -1.5)), ((2, 4, 2), (-1, -4, -1)), ((2, 2, 3), (-1, -2, -2))]
        pivots = [(sx, -8, sz), (0, -4, 0), (0, -4, 0), (0, -4, 0)]
        incr = [(rx0, rz0), (-zd * 30, xd * 30), (-zd * 34, xd * 34), (-zd * 36, xd * 36)]
        prev = "head"
        for j in range(4):
            box_ = box(sizes[j][1], sizes[j][0], "snake", 0, [rect("front", 0, 0, 2, 1, "#f4d820"), rect("top", 0, 0, 2, 1, "#f4d820")] if j == 3 else None)
            P.append(part(f"{nm}_{j}", prev, pivots[j], (incr[j][0], 0, incr[j][1]), [box_]))
            prev = f"{nm}_{j}"
            A.append({"part": prev, "type": "sway", "axis": "x" if j % 2 == 0 else "z", "amp": 0.10 + 0.06 * j, "freq": 0.10 + 0.004 * k + 0.02 * j, "phase": k * 0.9 + j})
    # torso, breastplate, belt and a tattered skirt
    P.append(part("body", "root", (0, -26, 0), (0, 0, 0), [box((-4, 0, -2), (8, 12, 4), "skin"), box((-4, 1, -2), (8, 6, 4), "bronze", 0.5),
                                                          box((-4, 9, -2), (8, 2, 4), "gold", 0.4), box((-4.5, 11, -2.5), (9, 4, 5), "cloth")]))
    # arms: bronze gauntlets with claws
    for side in ("l", "r"):
        sx = 1 if side == "l" else -1
        P.append(part(f"arm_{side}", "root", (sx * 5.5, -24, 0), (-24, 0, 0), [box((-1.5, -2, -2), (3, 7, 3), "skin")]))
        P.append(part(f"fore_{side}", f"arm_{side}", (0, 5, 0), (-20, 0, 0), [box((-2, 0, -2), (4, 6, 4), "bronze", 0.2)]))
        for j, cx in enumerate((-1.5, -0.5, 0.5)):
            P.append(part(f"claw_{side}{j}", f"fore_{side}", (cx + 0.5, 6, -1.5), (-14, 0, (j - 1) * 8), [box((-0.5, 0, -0.5), (1, 4, 1), "claw")]))
        # a golden wing
        P.append(part(f"wing_{side}", "root", (sx * 2, -22, 2.4), (0, sx * 38, sx * -6), [box((0 if sx > 0 else -8, -11, 0), (8, 11, 1), "gold")]))
        for j in range(4):
            P.append(part(f"feather_{side}{j}", f"wing_{side}", (sx * 8, -2 - j * 2.6, 0), (0, 0, sx * (-22 + j * 14)), [box((0 if sx > 0 else -5, -1, 0), (5, 2, 1), "gold")]))
        A.append({"part": f"wing_{side}", "type": "flap", "axis": "y", "amp": 0.16, "freq": 0.12, "phase": 0 if sx > 0 else math.pi})
        A.append({"part": f"arm_{side}", "type": "walk", "axis": "x", "amp": 0.5, "phase": 0 if sx > 0 else math.pi})
    # the serpent tail
    segs = [("tail1", "root", (0, -14, 1), 8, (-4, 0, -3), (8, 5, 6)), ("tail2", "tail1", (0, 5, 0), 28, (-3.5, 0, -3), (7, 6, 6)),
            ("tail3", "tail2", (0, 6, 0), 30, (-3, 0, -2.5), (6, 6, 5)), ("tail4", "tail3", (0, 6, 0), 28, (-2.5, 0, -2.5), (5, 6, 5)),
            ("tail5", "tail4", (0, 6, 0), 12, (-2, 0, -2), (4, 6, 4)), ("tail6", "tail5", (0, 6, 0), 8, (-1.5, 0, -1.5), (3, 6, 3)),
            ("tail7", "tail6", (0, 6, 0), 10, (-1, 0, -1), (2, 5, 2)), ("tail8", "tail7", (0, 5, 0), 14, (-0.5, 0, -0.5), (1, 4, 1))]
    for k, (nm, par, pv, rx, fr, sz) in enumerate(segs):
        P.append(part(nm, par, pv, (rx, 0, 0), [box(fr, sz, "tail")]))
        if k >= 1:
            A.append({"part": nm, "type": "sway", "axis": "y", "amp": 0.14 + 0.02 * k, "freq": 0.18, "phase": k * 0.8, "walk_amp": 0.30})
    A.append({"part": "head", "type": "look"})
    return {"shadow": 0.6, "paints": paints, "parts": P, "anim": A}


def main():
    for name, fn, scale in (("satyr", satyr, 0.87), ("gorgon", gorgon, 0.9)):
        p = ROOT / "mobs" / f"{name}.json"
        spec = json.loads(p.read_text())
        spec["model"] = fn()
        spec["attributes"]["scale"] = scale
        spec["skin"] = {"model": True}
        p.write_text(json.dumps(spec, indent=2) + "\n")
        print(name, len(spec["model"]["parts"]), "parts")


if __name__ == "__main__":
    main()
