#!/usr/bin/env python3
"""Author Olympia's creature models (the "model" section of each mobs/<id>.json): Satyr, Gorgon, Hoplite, Cyclops, Minotaur.

    python3 tools/gen_models.py && shadw-mod mob . gen

Edit this script, not the JSON. It uses shadwlib.figure (a finely shaped biped builder, tapering chains) on top of the model system in
adapters/minecraft-fabric/mobmodel.py. Coordinates are Minecraft model pixels: +y is down, -z is forward, "root" sits at the feet.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from shadwlib.figure import Rig, box, rect  # noqa: E402


def eyes(y, color, slit="#120a04", horizontal=False, size=2):
    out = []
    for ex in (1, 5):
        out.append(rect("front", ex, y, size, 2, color))
        out.append(rect("front", ex, y + (1 if horizontal else 0), 2 if horizontal else 1, 1 if horizontal else 2, slit))
    return out


# ======================= SATYR =======================
def satyr():
    r = Rig({
        "skin": {"type": "skin", "base": "#c9946a", "shade": 5}, "face": {"type": "skin", "base": "#d09c70", "shade": 4},
        "fur": {"type": "fur", "base": "#6b4a2c", "dark": "#3b2616", "light": "#9a7448"}, "fur_dark": {"type": "fur", "base": "#4a321c", "dark": "#2a1a0e", "light": "#6e4c2c"},
        "hair": {"type": "fur", "base": "#53351d", "dark": "#2e1c0e", "light": "#8a5e34"},
        "horn": {"type": "ridged", "base": "#e6dcc0", "dark": "#8f7f5c", "light": "#fff6dc"}, "hoof": {"type": "plain", "base": "#2a2220"},
        "bamboo": {"type": "ridged", "base": "#d8b868", "dark": "#8a6a30", "light": "#f0d890"}, "bind": {"type": "cloth", "base": "#7a2a2a", "trim": "#c9a050"},
        "ear": {"type": "skin", "base": "#b87c58", "shade": 4}, "ear_in": {"type": "plain", "base": "#7a3a2a"},
    })
    hip = -15.25
    n = r.biped("skin", cloth="fur", head_paint="face", head_decals=eyes(2, "#e8a820", horizontal=True) + [rect("front", 0, 1, 3, 1, "#3a2414"), rect("front", 5, 1, 3, 1, "#3a2414")],
                legs=False, hip_y=hip, chest=(8, 7, 4), waist=(6, 5, 3), arm_len=(5, 5), arm_paint="skin",
                arm_pose={"r": ((-50, 0, 0), (-92, 0, 0))}, swing_arm="r")
    # chest hair and abs as decals on the chest part
    r.parts[[p["name"] for p in r.parts].index("chest")]["boxes"][0]["decals"] = [
        rect("front", 2, 1, 4, 2, "#5a3a22"), rect("front", 3, 3, 2, 3, "#5a3a22"), rect("front", 1, 5, 2, 1, "#a8774f"), rect("front", 5, 5, 2, 1, "#a8774f")]
    r.parts[[p["name"] for p in r.parts].index("body")]["boxes"][0]["decals"] = [rect("front", 2, 1, 2, 1, "#a8774f"), rect("front", 2, 3, 2, 1, "#a8774f")]
    # head extras: a long goat muzzle, nose, goatee, a shaggy mop and side locks, ears
    r.part("muzzle", "head", (0, 0, 0), (6, 0, 0), [box((-2.5, -3, -8.5), (5, 3.5, 4.5), "face", 0, [rect("front", 0, 0, 1, 1, "#2a1810"), rect("front", 4, 0, 1, 1, "#2a1810"), rect("front", 1, 2, 3, 1, "#6a3424")])])
    r.part("nose", "muzzle", (0, -1, -8.5), (0, 0, 0), [box((-1.5, -1, -0.7), (3, 2, 1.2), "ear_in", 0.1)])
    r.part("beard", "head", (0, 1.5, -5), (4, 0, 0), [box((-1.5, 0, -1.5), (3, 4, 3), "fur_dark")])
    r.part("beard2", "beard", (0, 4, 0), (6, 0, 0), [box((-1, 0, -1), (2, 4, 2), "fur_dark")])
    r.part("beard3", "beard2", (0, 4, 0), (8, 0, 0), [box((-0.5, 0, -0.5), (1, 3, 1), "fur_dark")])
    r.anim("beard", "sway", axis="x", amp=0.08, freq=0.12)
    r.anim("beard2", "sway", axis="x", amp=0.10, freq=0.15, phase=1)
    r.part("hair", "head", (0, -6, 0), (0, 0, 0), [box((-4.5, -2.5, -4.5), (9, 3, 9), "hair"), box((-4.5, -0.5, 3.5), (9, 7, 1.5), "hair"), box((-4.5, -0.5, -4.5), (1, 5, 3), "hair"), box((3.5, -0.5, -4.5), (1, 5, 3), "hair"),
                                           box((-3, -3.5, -3), (6, 1, 6), "hair")])
    for side, sx in (("l", 1), ("r", -1)):
        r.part(f"ear_{side}", "head", (sx * 4, -3.5, 0.5), (0, sx * 22, sx * -30), [box((0 if sx > 0 else -7, -2, -0.5), (7, 4, 1), "ear"), box((0.5 if sx > 0 else -5.5, -1, -0.6), (5, 2, 1.2), "ear_in")])
        r.anim(f"ear_{side}", "sway", axis="z", amp=0.10, freq=0.17, phase=0 if sx > 0 else 1.6)
        # ram horns: nine tapering segments that sweep up, curl back, down and round past the ear
        widths = [4, 4, 4, 3, 3, 3, 2, 2, 1]
        rots = [(-20, sx * 16), (-26, sx * 8), (-30, sx * 6), (-32, sx * 6), (-34, sx * 6), (-34, sx * 6), (-32, sx * 5), (-30, sx * 4), (-26, sx * 3)]
        prev, pv = "head", (sx * 2.8, -6.5, -1.5)
        for i, (w, (rx, rz)) in enumerate(zip(widths, rots)):
            nm = f"horn_{side}{i}"
            r.part(nm, prev, pv, (rx, 0, rz), [box((-w / 2, -3, -w / 2), (w, 3, w), "horn", 0.0)])
            prev, pv = nm, (0, -3, 0)
    # goat legs: thigh forward, shin back, pastern, split hoof, with fur ruffs
    for side, sx in (("l", 1), ("r", -1)):
        r.part(f"gleg_{side}", "root", (sx * 2.6, hip, 0), (0, 0, 0), [])
        r.part(f"thigh_{side}", f"gleg_{side}", (0, 0, 0), (-38, 0, 0), [box((-2, 0, -2), (4, 6, 4), "fur"), box((-2.5, 1, -2.5), (5, 3, 5), "fur", -0.3)])
        r.part(f"shin_{side}", f"thigh_{side}", (0, 6, 0), (76, 0, 0), [box((-1, 0, -1), (2, 7, 2), "fur_dark"), box((-1.5, 2, -1.5), (3, 3, 3), "fur", 0.2), box((-1, 5, -1.5), (2, 2, 1), "fur_dark", 0.2)])
        r.part(f"pastern_{side}", f"shin_{side}", (0, 7, 0), (-38, 0, 0), [box((-1, 0, -1), (2, 3, 2), "fur_dark")])
        r.part(f"hoof_{side}", f"pastern_{side}", (0, 3, 0), (0, 0, 0), [box((-1.5, 0, -2.5), (1.5, 2, 4), "hoof", -0.1), box((0, 0, -2.5), (1.5, 2, 4), "hoof", -0.1)])
        r.anim(f"gleg_{side}", "walk", axis="x", amp=1.0, phase=math.pi if side == "l" else 0)
    r.part("tail", "body", (0, 0, 1.6), (38, 0, 0), [box((-1, 0, -1), (2, 4, 2), "fur")])
    r.anim("tail", "sway", axis="x", amp=0.18, freq=0.21, walk_amp=0.3)
    # the pan-pipes: a lashed row of tapering reeds at the mouth
    r.part("flute", "hand_r", (0, 1, 0), (142, 0, 0), [box((-5.5, 0, -1.5), (11, 1, 3), "bind")] + [box((-5 + 2 * i, 1, -1), (2, L, 2), "bamboo", -0.1) for i, L in enumerate((7, 6, 5, 4, 3))])
    return r.model(0.5)


# ======================= GORGON =======================
def gorgon():
    r = Rig({
        "skin": {"type": "scales", "base": "#6a9a4c", "dark": "#33602c", "light": "#a8d878", "cell": 4}, "face": {"type": "skin", "base": "#7aa858", "shade": 4},
        "tail": {"type": "scales", "base": "#4f8440", "dark": "#244a24", "light": "#98c868", "cell": 4}, "snake": {"type": "scales", "base": "#3e7a3a", "dark": "#1c4420", "light": "#8cc25c", "cell": 3},
        "bronze": {"type": "metal", "base": "#b07a3a", "dark": "#6a4620", "light": "#e0b060"}, "gold": {"type": "metal", "base": "#e0b838", "dark": "#8a6a14", "light": "#fff0a0"},
        "cloth": {"type": "cloth", "base": "#cfc2a0", "trim": "#9a2a2a"}, "ivory": {"type": "plain", "base": "#efe6cc"}, "claw": {"type": "plain", "base": "#d8d0b8"},
        "tongue": {"type": "plain", "base": "#b02838"},
    })
    hip = -15
    n = r.biped("skin", cloth="cloth", head_paint="face", head_decals=[rect("front", 1, 2, 2, 2, "#ecf24a"), rect("front", 5, 2, 2, 2, "#ecf24a"), rect("front", 1, 2, 1, 2, "#101808"), rect("front", 5, 2, 1, 2, "#101808"),
                                                                       rect("front", 1, 1, 2, 1, "#244a24"), rect("front", 5, 1, 2, 1, "#244a24"), rect("front", 1, 5, 6, 1, "#1a1008"), rect("front", 3, 4, 2, 1, "#244a24")],
                legs=False, hip_y=hip, chest=(8, 7, 4), waist=(6, 5, 3), arm_len=(5, 5), arm_paint="skin", stance=-24, swing_arm="r", cloth_hips=False)
    for part in r.parts:
        if part["name"] == "chest":
            part["boxes"].append(box((-4, -6, -2), (8, 6, 4), "bronze", 0.5))           # a bronze breastplate
            part["boxes"].append(box((-4, -1, -2), (8, 1, 4), "gold", 0.6))
        if part["name"].startswith("forearm"):
            part["boxes"].append(box((-1.5, 0, -1.5), (3, 4, 3), "bronze", 0.6))        # a bronze gauntlet
    for side, sx in (("l", 1), ("r", -1)):
        for j, cx in enumerate((-1, 0, 1)):
            r.part(f"claw_{side}{j}", f"hand_{side}", (cx * 0.9, 2, -1.2), (-16, 0, cx * 10), [box((-0.5, 0, -0.5), (1, 4, 1), "claw", -0.1)])
    r.part("skirt", "body", (0, 0, 0), (0, 0, 0), [box((-4.5, -1, -2.5), (9, 4, 5), "cloth")])
    # head: tusks, a tongue, a bronze circlet
    r.part("tusk_l", "head", (3, -1, -4.2), (0, 0, 8), [box((-0.5, -2.5, -0.5), (1, 3, 1), "ivory", -0.05)])
    r.part("tusk_r", "head", (-3, -1, -4.2), (0, 0, -8), [box((-0.5, -2.5, -0.5), (1, 3, 1), "ivory", -0.05)])
    r.part("tongue", "head", (0, 0.5, -4.2), (10, 0, 0), [box((-1, 0, -1.5), (2, 1, 3), "tongue")])
    r.part("circlet", "head", (0, -5.5, 0), (0, 0, 0), [box((-4.5, -1, -4.5), (9, 1.5, 9), "bronze")])
    # snakes for hair: twelve chains of five tapering segments, rising and arching outward and down
    for k in range(12):
        th = 2 * math.pi * k / 12 + 0.2
        xd, zd = math.sin(th), math.cos(th)
        lean = 20 if zd < -0.5 else 32
        prev, pv = "head", (xd * 3.4, -6, zd * 3.4)
        for j in range(5):
            tilt = lean if j == 0 else 20 + 2 * j           # a gentle arc: outward, then drooping
            rx, rz = -zd * tilt, xd * tilt
            w = (3, 3, 2, 2, 2)[j]
            if j < 4:
                bx = box((-w / 2, -4.2, -w / 2), (w, 4.2, w), "snake")
            else:                                             # the head: a flat wedge with yellow eyes and a pair of fangs
                bx = box((-1.2, -2.4, -2.4), (2.4, 2.4, 3.6), "snake", 0, [rect("front", 0, 0, 2, 1, "#f4d820"), rect("top", 0, 0, 3, 1, "#f4d820"), rect("bottom", 0, 2, 2, 1, "#ece0b0")])
            nm = f"sn{k:02d}_{j}"
            r.part(nm, prev, pv, (rx, 0, rz), [bx])
            r.anim(nm, "sway", axis="x" if j % 2 == 0 else "z", amp=0.08 + 0.04 * j, freq=0.10 + 0.004 * k + 0.02 * j, phase=k * 0.9 + j)
            prev, pv = nm, (0, -4, 0)
    # golden wings, six feathers each
    for side, sx in (("l", 1), ("r", -1)):
        r.part(f"wing_{side}", "chest", (sx * 2, -5, 2.4), (0, sx * 38, sx * -6), [box((0 if sx > 0 else -8, -10, 0), (8, 10, 1), "gold")])
        for j in range(6):
            r.part(f"feather_{side}{j}", f"wing_{side}", (sx * 8, -1.5 - j * 1.6, 0), (0, 0, sx * (-30 + j * 13)), [box((0 if sx > 0 else -5, -0.5, 0), (5, 1, 1), "gold", 0.1)])
        r.anim(f"wing_{side}", "flap", axis="y", amp=0.16, freq=0.12, phase=0 if sx > 0 else math.pi)
    # the serpent tail, ten tapering segments, lying along the ground
    segs = [(5, 8, 6, 8), (6, 7, 6, 26), (6, 7, 5, 28), (6, 6, 5, 26), (6, 5, 5, 14), (6, 5, 4, 8), (6, 4, 4, 8), (5, 3, 3, 10), (5, 3, 3, 12), (4, 2, 2, 14)]
    prev, pv = "body", (0, 0, 1)
    for i, (ln, wx, wz, rx) in enumerate(segs):
        nm = f"tail{i}"
        r.part(nm, prev, pv, (rx, 0, 0), [box((-wx / 2, 0, -wz / 2), (wx, ln, wz), "tail", -0.1 * (i // 3))])
        if i >= 1:
            r.anim(nm, "sway", axis="y", amp=0.13 + 0.02 * i, freq=0.18, phase=i * 0.8, walk_amp=0.30)
        prev, pv = nm, (0, ln, 0)
    return r.model(0.6)


# ======================= HOPLITE =======================
def hoplite():
    r = Rig({
        "skin": {"type": "skin", "base": "#d6a880", "shade": 4}, "tunic": {"type": "cloth", "base": "#ece6d4", "trim": "#b02828"},
        "bronze": {"type": "metal", "base": "#b87c3c", "dark": "#6e4824", "light": "#f0c070"}, "leather": {"type": "cloth", "base": "#8a5a32", "trim": "#5a3818"},
        "crest": {"type": "fur", "base": "#b02828", "dark": "#6a1414", "light": "#e05040"}, "wood": {"type": "ridged", "base": "#9a7040", "dark": "#5a3c20", "light": "#c09860"},
        "iron": {"type": "metal", "base": "#a8acb4", "dark": "#60646c", "light": "#e0e4ec"}, "dark": {"type": "plain", "base": "#2a1c14"},
    })
    n = r.biped("skin", cloth="tunic", head_paint="skin", head_decals=[rect("front", 1, 2, 2, 1, "#201410"), rect("front", 5, 2, 2, 1, "#201410"), rect("front", 2, 5, 4, 1, "#7a4a3a")],
                hip_y=-12, chest=(8, 7, 4), waist=(7, 5, 4), shin_paint="skin", body_paint="tunic", chest_paint="tunic", arm_paint="skin", swing_arm="r", feet=True, foot_paint="leather")
    # a Corinthian helmet: dome, cheek guards, nose guard, brow, and a red horsehair crest that sways
    r.part("helmet", "head", (0, 0, 0), (0, 0, 0), [box((-4.5, -7.5, -4.5), (9, 5, 9), "bronze"), box((-4.5, -3, -4.5), (1, 5, 6), "bronze"), box((3.5, -3, -4.5), (1, 5, 6), "bronze"),
                                                    box((-4.5, -3, 3), (9, 4, 1), "bronze"), box((-0.5, -4, -5.2), (1, 5, 1), "bronze"), box((-4, -4.5, -4.8), (8, 1, 1), "bronze")])
    r.part("crest_base", "helmet", (0, -7.5, 0), (0, 0, 0), [box((-0.5, -2, -4), (1, 2, 8), "bronze")])
    prev, pv = "crest_base", (0, -2, 3.5)
    for i in range(5):
        nm = f"crest{i}"
        r.part(nm, prev, pv, (14, 0, 0), [box((-1, -0.5, -0.5), (2, 5, 2), "crest")])
        r.anim(nm, "sway", axis="x", amp=0.07 + 0.03 * i, freq=0.13, phase=i * 0.9, walk_amp=0.15)
        prev, pv = nm, (0, 4.5, 0)
    # a muscle cuirass over the chest and belly, shoulder flaps, and a leather pteruges skirt
    for part in r.parts:
        if part["name"] == "chest":
            part["boxes"].append(box((-4, -6, -2), (8, 6, 4), "bronze", 0.5, [rect("front", 3, 1, 1, 3, "#8a5a28"), rect("front", 4, 1, 1, 3, "#8a5a28"), rect("front", 1, 4, 6, 1, "#8a5a28")]))
        if part["name"] == "body":
            part["boxes"].append(box((-3, -4, -2), (6, 4, 4), "bronze", 0.5))
        if part["name"].startswith("shin"):
            part["boxes"].append(box((-1.5, 0, -1.5), (3, 4, 3), "bronze", 0.6))          # greaves
    for i in range(8):
        a = 2 * math.pi * i / 8
        r.part(f"ptery{i}", "pelvis", (math.sin(a) * 3.6, 1, math.cos(a) * 2.6), (-math.cos(a) * 6, 0, math.sin(a) * 6), [box((-1, 0, -0.5), (2, 5, 1), "leather")])
        r.anim(f"ptery{i}", "sway", axis="x", amp=0.06, freq=0.14, phase=i, walk_amp=0.2)
    # a round shield on the left forearm and a spear in the right hand
    r.part("shield", "forearm_l", (3.2, 3, -1), (0, 0, 0), [box((0, -5, -5), (1, 10, 10), "bronze"), box((0, -4, -6), (1, 8, 1), "bronze"), box((0, -4, 5), (1, 8, 1), "bronze"),
                                                           box((0.2, -2, -2), (2, 4, 4), "bronze", 0.2, [rect("right", 0, 0, 1, 4, "#f0c070")])])
    r.part("spear", "hand_r", (0, 1, -1), (-22, 0, 0), [box((-0.5, -10, -0.5), (1, 26, 1), "wood"), box((-1, -14, -0.5), (2, 5, 1), "iron"), box((-0.5, -17, -0.3), (1, 3, 0.6), "iron"), box((-1.2, 13, -0.7), (2.4, 2, 1.4), "iron")])
    return r.model(0.5)


# ======================= CYCLOPS =======================
def cyclops():
    r = Rig({
        "skin": {"type": "skin", "base": "#b08c68", "shade": 6}, "face": {"type": "skin", "base": "#b8946e", "shade": 5},
        "hide": {"type": "cloth", "base": "#6a4a2a", "trim": "#3a2814"}, "hair": {"type": "fur", "base": "#3a2a1c", "dark": "#1c120a", "light": "#5a4028"},
        "wood": {"type": "ridged", "base": "#7a5230", "dark": "#3a2814", "light": "#a07848"}, "spike": {"type": "plain", "base": "#9a9aa4"}, "bone": {"type": "plain", "base": "#e8e0c8"},
        "toe": {"type": "skin", "base": "#a07c5a", "shade": 4},
    })
    eye = [rect("front", 1, 1, 6, 1, "#463222"), rect("front", 1, 2, 6, 4, "#f4f0e6"), rect("front", 2, 3, 4, 3, "#3c82b4"), rect("front", 3, 4, 2, 2, "#14141a"), rect("front", 2, 7, 4, 1, "#3c1e18")]
    n = r.biped("skin", cloth="hide", head_paint="face", head=None, head_decals=eye, hip_y=-14, chest=(11, 8, 6), waist=(8, 6, 5), arm_len=(6, 6), leg_len=(7, 7), arm_w=4, leg_w=4,
                hunch=10, stance=-8, shin_paint="skin", body_paint="skin", arm_paint="skin", foot_paint="toe", swing_arm="r", foot_len=6.5)
    r.part("hair", "head", (0, -6, 0), (0, 0, 0), [box((-4.8, -2, -4.8), (9.6, 3, 9.6), "hair"), box((-4.8, -1, 3.2), (9.6, 8, 1.6), "hair"), box((-4.8, -1, -4.8), (1.4, 5, 4), "hair"), box((3.4, -1, -4.8), (1.4, 5, 4), "hair")])
    r.part("brow", "head", (0, -3, -4.2), (-8, 0, 0), [box((-4, -1, -1), (8, 2, 1.5), "face", 0.2)])
    r.part("tusk_l", "head", (2.4, 1.6, -4.2), (0, 0, 8), [box((-0.7, -3, -0.7), (1.4, 3, 1.4), "bone", -0.05)])
    r.part("tusk_r", "head", (-2.4, 1.6, -4.2), (0, 0, -8), [box((-0.7, -3, -0.7), (1.4, 3, 1.4), "bone", -0.05)])
    r.part("jaw", "head", (0, 1.8, -3), (0, 0, 0), [box((-3, 0, -2), (6, 2.5, 4), "face")])
    r.part("loin", "pelvis", (0, 0.5, 0), (0, 0, 0), [box((-5, 0, -3.5), (10, 6, 7), "hide"), box((-5.2, -0.5, -3.7), (10.4, 1.5, 7.4), "hair")])
    for i in range(6):
        r.part(f"tatter{i}", "loin", (-3.4 + i * 1.4, 6, -3.4), (4, 0, 0), [box((-0.6, 0, -0.3), (1.2, 3, 0.6), "hide")])
        r.anim(f"tatter{i}", "sway", axis="x", amp=0.05, freq=0.13, phase=i, walk_amp=0.15)
    for part in r.parts:
        if part["name"] == "chest":
            part["boxes"].append(box((-5.5, -3, -3), (11, 3, 6), "hair", 0.3))        # a shaggy pelt over the shoulders
    # a spiked club of one great log
    r.part("club", "hand_r", (0, 2, -2), (-30, 0, 0), [box((-1.5, -6, -1.5), (3, 14, 3), "wood"), box((-3, -18, -3), (6, 13, 6), "wood", 0.2)] + [box((sx - 0.5, -17 + dy, sz - 0.5), (1, 2.5, 1), "spike")
                                                                                                                                        for sx, sz, dy in ((-3.6, 0, 0), (3.6, 0, 3), (0, -3.6, 6), (0, 3.6, 1), (-3.6, 0, 8), (3.6, 0, 9))])
    return r.model(0.8)


# ======================= MINOTAUR =======================
def minotaur():
    r = Rig({
        "skin": {"type": "skin", "base": "#bd8a62", "shade": 5}, "fur": {"type": "fur", "base": "#5a3a24", "dark": "#2e1c10", "light": "#85593a"},
        "fur_dark": {"type": "fur", "base": "#40281a", "dark": "#20120a", "light": "#5c3c26"}, "snout": {"type": "skin", "base": "#a07a64", "shade": 4},
        "horn": {"type": "ridged", "base": "#ece2c4", "dark": "#8c7c58", "light": "#fff8e0"}, "hoof": {"type": "plain", "base": "#241c18"}, "hide": {"type": "cloth", "base": "#7a4e2c", "trim": "#3a2410"},
        "gold": {"type": "metal", "base": "#e0b838", "dark": "#8a6a14", "light": "#fff0a0"}, "iron": {"type": "metal", "base": "#8a8e96", "dark": "#4a4e56", "light": "#d0d4dc"}, "wood": {"type": "ridged", "base": "#6a4828", "dark": "#32200e", "light": "#8c6a40"},
        "eye": {"type": "plain", "base": "#d82818"},
    })
    n = r.biped("skin", cloth="hide", head_paint="fur", head_decals=[rect("front", 0, 2, 2, 2, "#2a1408"), rect("front", 6, 2, 2, 2, "#2a1408"), rect("front", 1, 2, 1, 2, "#e03020"), rect("front", 6, 2, 1, 2, "#e03020")],
                hip_y=-15, chest=(12, 9, 6), waist=(9, 6, 5), arm_len=(6, 7), leg_len=(7, 8), arm_w=4, leg_w=4, hunch=12, stance=-6, shin_paint="fur", thigh_paint="fur", body_paint="skin",
                arm_paint="skin", foot_paint="hoof", swing_arm="r", foot_len=5)
    # the bull's head: a long snout with a pale muzzle and a golden nose ring, ears, a mane, and great curving horns
    r.part("muzzle", "head", (0, 0, 0), (8, 0, 0), [box((-2.5, -3.5, -9), (5, 4.5, 5), "snout", 0, [rect("front", 0, 1, 1, 1, "#1a0e08"), rect("front", 4, 1, 1, 1, "#1a0e08")])])
    r.part("ring", "muzzle", (0, 0, -9), (0, 0, 0), [box((-1.5, 0, -0.4), (3, 1, 0.8), "gold"), box((-1.5, 0, -0.4), (1, 3, 0.8), "gold"), box((0.5, 0, -0.4), (1, 3, 0.8), "gold"), box((-1.5, 2, -0.4), (3, 1, 0.8), "gold")])
    r.part("mane", "head", (0, -5.5, 0), (0, 0, 0), [box((-4.5, -2.5, -4.5), (9, 3, 9), "fur_dark"), box((-5, -1, 3), (10, 10, 3), "fur_dark"), box((-5, -1, -3), (1.5, 6, 6), "fur_dark"), box((3.5, -1, -3), (1.5, 6, 6), "fur_dark")])
    for side, sx in (("l", 1), ("r", -1)):
        r.part(f"ear_{side}", "head", (sx * 4, -3.5, 0.5), (0, sx * 12, sx * -50), [box((0 if sx > 0 else -4, -1.5, -0.5), (4, 3, 1), "fur")])
        widths, rots = [4, 4, 3, 3, 2, 2, 1], [(-8, sx * 62), (-6, sx * 30), (-8, sx * 12), (-12, sx * -14), (-14, sx * -28), (-14, sx * -30), (-10, sx * -26)]
        prev, pv = "head", (sx * 3, -5.5, -1.5)
        for i, (w, (rx, rz)) in enumerate(zip(widths, rots)):
            nm = f"horn_{side}{i}"
            r.part(nm, prev, pv, (rx, 0, rz), [box((-w / 2, -3.5, -w / 2), (w, 3.5, w), "horn")])
            prev, pv = nm, (0, -3.5, 0)
    # a thick shaggy neck ruff and a belt of hide and gold, a loincloth
    for part in r.parts:
        if part["name"] == "chest":
            part["boxes"].append(box((-6, -4, -3.5), (12, 4, 7), "fur_dark", 0.4))
        if part["name"] == "body":
            part["boxes"].append(box((-4.5, -1, -2.5), (9, 2, 5), "gold", 0.3))
    r.part("loin", "pelvis", (0, 0.5, 0), (0, 0, 0), [box((-5, 0, -3.2), (10, 7, 6.4), "hide")])
    for i in range(5):
        r.part(f"tatter{i}", "loin", (-3.2 + i * 1.6, 7, -3.2), (4, 0, 0), [box((-0.7, 0, -0.3), (1.4, 3, 0.6), "hide")])
        r.anim(f"tatter{i}", "sway", axis="x", amp=0.05, freq=0.13, phase=i, walk_amp=0.15)
    r.chain("tail", "body", (0, 0, 2), [(4, 2, 2, 40, 0), (4, 2, 2, 12, 0), (3, 3, 3, 8, 0)], "fur_dark", sway="x", amp=0.14, freq=0.2)
    # a labrys: a double-bladed axe on a long haft
    r.part("labrys", "hand_r", (0, 2, -2), (-24, 0, 0), [box((-0.8, -22, -0.8), (1.6, 30, 1.6), "wood"), box((-5.5, -24, -0.5), (11, 6, 1), "iron", 0, [rect("front", 0, 2, 11, 1, "#d0d4dc")]),
                                                             box((-3, -22, -0.4), (6, 2, 0.8), "iron"), box((-1.2, -26, -1.2), (2.4, 2, 2.4), "gold")])
    return r.model(0.9)


def main():
    for name, fn, scale in (("satyr", satyr, 0.87), ("gorgon", gorgon, 0.9), ("hoplite", hoplite, 1.0), ("cyclops", cyclops, 1.2), ("minotaur", minotaur, 1.25)):
        p = ROOT / "mobs" / f"{name}.json"
        spec = json.loads(p.read_text())
        spec["model"] = fn()
        spec["attributes"]["scale"] = scale
        spec["skin"] = {"model": True}
        if name == "hoplite":
            spec["equipment"] = {}                       # the sword-less spear and shield are part of the model
        p.write_text(json.dumps(spec, indent=2) + "\n")
        print(name, len(spec["model"]["parts"]), "parts")


if __name__ == "__main__":
    main()
