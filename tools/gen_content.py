#!/usr/bin/env python3
"""Generate Olympia's textures, models, block states, item definitions, creature skins and language entries.

    python3 tools/gen_content.py && python3 tools/gen_assets.py

Everything is derived from this script: edit it, not the output. Deterministic (shadwlib.pix.h), stdlib only.
Palette: the colours of the brief (white marble, Mediterranean blue, deep turquoise, Olympian gold, olive, terracotta, bronze,
Underworld purple and black).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from shadwlib.pix import Pix, h, shade, tex  # noqa: E402
from shadwlib.png import write_png  # noqa: E402
from shadwlib import skin as sk  # noqa: E402

ROOT = HERE.parent
NS = "olympia"
ASSETS = ROOT / "src/main/resources/assets" / NS

MARBLE = (232, 230, 222)
BLUE, TURQ = (28, 112, 176), (20, 150, 160)
GOLD, GOLD_D, GOLD_L = (230, 184, 60), (170, 126, 30), (255, 232, 140)
OLIVE, OLIVE_D = (110, 122, 56), (70, 82, 36)
TERRA, TERRA_D = (196, 98, 60), (140, 64, 40)
BRONZE, BRONZE_D = (168, 116, 62), (110, 72, 36)
PURPLE, NIGHT = (74, 40, 110), (30, 28, 36)
INK = (11, 11, 13)

STONES = ["white_marble", "polished_marble", "weathered_marble", "cracked_marble", "black_marble", "pink_marble", "veined_marble",
          "golden_marble", "marble_bricks", "marble_tiles", "greek_mosaic", "roof_tile"]
FAMILIES = ["white_marble", "polished_marble", "marble_bricks", "roof_tile"]
COLUMNS = ["doric_column", "ionic_column", "corinthian_column"]
GODS = ["zeus", "athena", "poseidon", "hermes", "apollo", "artemis", "ares", "demeter"]


def wj(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def item_def(name, model, tints=None):
    m = {"type": "minecraft:model", "model": model}
    if tints:
        m["tints"] = [{"type": "minecraft:constant", "value": t} for t in tints]
    wj(ASSETS / "items" / f"{name}.json", {"model": m})


# ---------- marble ----------

def vein(x, y, salt, slope=1.0, wobble=3, every=11):
    """True on a thin wandering diagonal line, repeated every `every` pixels."""
    off = (h(x // 3, 0, salt) % wobble) - wobble // 2
    return ((x * slope + y * 1.0 + off + salt) % every) < 1.0


def marble(base, salt, spread=5, vein_c=None, vein_every=11, slope=1.0):
    def fn(x, y):
        c = shade(base, (h(x, y, salt) % (2 * spread + 1)) - spread)
        if vein_c and vein(x, y, salt, slope, 3, vein_every):
            c = vein_c
        return c
    return fn


def white_marble(x, y):
    return marble(MARBLE, 1, 4, (190, 192, 200), 13)(x, y)


def polished_marble(x, y):
    c = marble((240, 238, 230), 2, 2)(x, y)
    if x in (0, 15) or y in (0, 15):
        c = shade((240, 238, 230), -28)
    if (x + y) % 16 == 5 and 2 < x < 13:
        c = shade(c, 14)
    return c


def weathered_marble(x, y):
    c = marble((206, 206, 198), 3, 7, (160, 164, 160), 9)(x, y)
    if h(x // 2, y // 2, 9) < 24:
        c = (122, 146, 104) if h(x, y, 10) < 60 else (150, 170, 120)
    return c


def cracked_marble(x, y):
    c = marble((226, 224, 216), 4, 5)(x, y)
    crack = [(7, 0), (7, 2), (8, 3), (8, 5), (6, 6), (6, 8), (7, 9), (9, 10), (9, 12), (10, 13), (10, 15), (3, 5), (4, 6), (12, 4), (13, 5)]
    if (x, y) in crack:
        c = (70, 70, 78)
    return c


def black_marble(x, y):
    c = marble((36, 36, 44), 5, 5, (236, 214, 150), 10, -1.0)(x, y)
    return c


def pink_marble(x, y):
    return marble((228, 186, 186), 6, 5, (244, 226, 226), 12)(x, y)


def veined_marble(x, y):
    c = marble((236, 236, 232), 7, 3, (90, 110, 150), 8, 0.6)(x, y)
    if vein(x, y, 21, -0.8, 3, 14):
        c = (140, 150, 176)
    return c


def golden_marble(x, y):
    return marble((226, 200, 126), 8, 5, (250, 236, 176), 9)(x, y)


def marble_bricks(x, y):
    c = shade(MARBLE, (h(x, y, 11) % 9) - 4)
    if y % 8 == 0 or (x + (4 if (y // 8) % 2 else 0)) % 8 == 0:
        c = shade(MARBLE, -34)
    return c


def marble_tiles(x, y):
    base = (238, 236, 228) if ((x // 8) + (y // 8)) % 2 == 0 else (206, 208, 214)
    c = shade(base, (h(x, y, 12) % 5) - 2)
    if x in (0, 8) or y in (0, 8):
        c = shade(base, -26)
    return c


# a Greek key (meander) band, blue on marble with a gold line
MEANDER = [
    "################",
    "#..............#",
    "#.############.#",
    "#.#..........#.#",
    "#.#.########.#.#",
    "#.#.#......#.#.#",
    "#.#.#.####.#.#.#",
    "#.#.#.#..#.#.#.#",
]


def greek_mosaic(x, y):
    c = shade((236, 232, 218), (h(x, y, 13) % 5) - 2)
    row = MEANDER[y % 8] if y < 8 else MEANDER[7 - (y % 8)]
    if row[(x % 16)] == "#":
        c = BLUE if y < 8 else shade(BLUE, 24)
    if y in (7, 8):
        c = GOLD
    return c


def roof_tile(x, y):
    row = y // 4
    xo = (x + (4 if row % 2 else 0)) % 8
    c = shade(TERRA, (h(x, y, 14) % 11) - 5)
    if y % 4 == 3:
        c = shade(TERRA_D, -8)
    elif xo == 0:
        c = shade(TERRA_D, 4)
    elif y % 4 == 0:
        c = shade(TERRA, 18)
    return c


STONE_FNS = {"white_marble": white_marble, "polished_marble": polished_marble, "weathered_marble": weathered_marble,
             "cracked_marble": cracked_marble, "black_marble": black_marble, "pink_marble": pink_marble, "veined_marble": veined_marble,
             "golden_marble": golden_marble, "marble_bricks": marble_bricks, "marble_tiles": marble_tiles, "greek_mosaic": greek_mosaic,
             "roof_tile": roof_tile}


# ---------- columns ----------

def column_side(order):
    def fn(x, y):
        c = shade(MARBLE, (h(x, y, 30) % 5) - 2)
        flutes = {"doric": 4, "ionic": 3, "corinthian": 2}[order]
        k = x % flutes
        if k == 0:
            c = shade(c, -26)
        elif k == 1:
            c = shade(c, 10)
        if order == "ionic" and y <= 2:
            c = BLUE if y == 1 else GOLD
        if order == "corinthian" and y <= 3:
            c = shade(OLIVE, 20) if (x + y) % 3 else GOLD
        if order == "doric" and y >= 14:
            c = shade(MARBLE, -34)
        return c
    return fn


def column_end(order):
    def fn(x, y):
        d = math.hypot(x - 7.5, y - 7.5)
        c = shade(MARBLE, -30)
        if d <= 7.2:
            c = shade(MARBLE, (h(x, y, 31) % 5) - 2)
        if order == "doric" and 3.0 <= d <= 4.2:
            c = shade(MARBLE, -28)
        if order == "ionic":
            if (abs(x - 4.5) + abs(y - 7.5)) in (2, 3) or (abs(x - 11.5) + abs(y - 7.5)) in (2, 3):
                c = BLUE
        if order == "corinthian" and d <= 6 and d >= 3:
            c = shade(OLIVE, 24) if int(math.atan2(y - 7.5, x - 7.5) * 4 / math.pi) % 2 == 0 else GOLD
        if d > 7.2:
            c = shade(MARBLE, -30)
        return c
    return fn


# ---------- other blocks ----------

def amphora_tex(x, y):
    c = shade(TERRA, (h(x, y, 40) % 9) - 4)
    if y in (3, 4, 11, 12):
        c = (28, 20, 18)
    if 5 <= y <= 10:
        figure = [(4, 6), (4, 7), (5, 8), (6, 9), (7, 10), (8, 9), (9, 8), (10, 6), (10, 7), (7, 5), (7, 6), (7, 7), (8, 5)]
        c = (28, 20, 18) if (x, y) in figure else shade(TERRA, 24)
    if y in (0, 15):
        c = shade(TERRA_D, -6)
    return c


def brazier_side(x, y):
    c = shade(BRONZE, (h(x, y, 41) % 7) - 3)
    if y in (0, 1, 14, 15):
        c = BRONZE_D
    if y in (7, 8):
        c = GOLD
    if x in (0, 15):
        c = BRONZE_D
    return c


def brazier_top(x, y):
    d = math.hypot(x - 7.5, y - 7.5)
    if d <= 5.5:
        n = h(x, y, 42)
        return (255, 140, 20) if n < 40 else ((255, 210, 70) if n < 75 else (240, 90, 20))
    return GOLD if d <= 7.2 else BRONZE_D


def altar_side(accent):
    def fn(x, y):
        c = shade(MARBLE, (h(x, y, 43) % 5) - 2)
        if x in (0, 15) or y in (0, 15):
            c = shade(MARBLE, -34)
        if y in (3, 4):
            c = accent
        if y in (11, 12):
            c = shade(accent, -30)
        if y == 7 or y == 8:
            c = shade(c, -10)
        return c
    return fn


def altar_top(god, accent):
    def fn(x, y):
        c = shade(MARBLE, (h(x, y, 44) % 5) - 2)
        if x in (0, 15) or y in (0, 15):
            c = shade(MARBLE, -34)
        if x in (1, 14) or y in (1, 14):
            c = shade(accent, -20)
        sym = set()
        if god == "zeus":        # a lightning bolt
            sym = {(9, 3), (8, 4), (7, 5), (6, 6), (7, 7), (8, 7), (9, 7), (8, 8), (7, 9), (6, 10), (6, 11), (5, 12), (9, 4), (8, 5), (7, 6)}
        elif god == "athena":    # an owl: two eyes over a beak
            sym = {(5, 5), (6, 5), (5, 6), (6, 6), (9, 5), (10, 5), (9, 6), (10, 6), (7, 8), (8, 8), (7, 9), (8, 9), (4, 4), (11, 4)}
        elif god == "poseidon":  # a trident
            sym = {(7, 3), (8, 3), (7, 12), (8, 12)} | {(7, y) for y in range(4, 12)} | {(8, y) for y in range(4, 12)}
            sym |= {(4, 3), (4, 4), (4, 5), (5, 6), (6, 7), (11, 3), (11, 4), (11, 5), (10, 6), (9, 7), (5, 7), (10, 7)}
        elif god == "hermes":    # a winged staff
            sym = {(7, y) for y in range(3, 13)} | {(8, y) for y in range(3, 13)}
            sym |= {(4, 5), (5, 5), (6, 5), (3, 6), (4, 6), (5, 6), (4, 7), (5, 7), (9, 5), (10, 5), (11, 5), (10, 6), (11, 6), (12, 6), (10, 7), (11, 7)}
        elif god == "apollo":    # a sun: a disc with eight rays
            sym = {(x, y) for x in range(16) for y in range(16) if math.hypot(x - 7.5, y - 7.5) <= 2.4}
            sym |= {(7, 3), (8, 3), (7, 12), (8, 12), (3, 7), (3, 8), (12, 7), (12, 8), (4, 4), (11, 4), (4, 11), (11, 11), (7, 4), (8, 4), (7, 11), (8, 11), (4, 7), (4, 8), (11, 7), (11, 8)}
        elif god == "artemis":   # a crescent moon and an arrow
            sym = {(x, y) for x in range(16) for y in range(16) if math.hypot(x - 7.5, y - 7.5) <= 4.6 and math.hypot(x - 9.4, y - 7.0) > 3.7}
            sym |= {(x, 12) for x in range(4, 13)} | {(12, 11), (12, 13), (11, 10), (11, 14)}
        elif god == "ares":      # crossed spears
            sym = {(i, i) for i in range(3, 13)} | {(15 - i, i) for i in range(3, 13)} | {(i + 1, i) for i in range(3, 12)} | {(14 - i, i) for i in range(3, 12)} | {(7, 7), (8, 7), (7, 8), (8, 8)}
        elif god == "demeter":   # an ear of wheat
            sym = {(7, y) for y in range(7, 14)} | {(8, y) for y in range(7, 14)} | {(7, 3), (8, 3)}
            sym |= {(6, 4), (9, 4), (6, 5), (9, 5), (5, 6), (10, 6), (6, 6), (9, 6), (5, 8), (10, 8), (6, 9), (9, 9), (4, 7), (11, 7)}
        if (x, y) in sym:
            c = accent
        return c
    return fn


ACCENT = {"zeus": GOLD, "athena": (88, 104, 128), "poseidon": TURQ, "hermes": (190, 196, 206), "apollo": (240, 150, 40), "artemis": (170, 190, 224),
          "ares": (176, 48, 40), "demeter": (160, 170, 60)}


def laurel():
    p = Pix()
    for y in range(7, 16):
        p.put(7, y, (80, 66, 40)); p.put(8, y, (80, 66, 40))
    for (x, y) in [(6, 6), (9, 6), (5, 8), (10, 8), (4, 10), (11, 10), (6, 4), (9, 4), (7, 3), (8, 3), (5, 11), (10, 12), (3, 12), (12, 12), (7, 1), (8, 2)]:
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            p.put(x + dx, y + dy, OLIVE if (x + y) % 2 else shade(OLIVE, 26))
    p.put(5, 7, GOLD); p.put(10, 9, GOLD); p.put(8, 5, GOLD)
    return p


def olive_log_side(x, y):
    c = shade((112, 96, 78), (h(x, y, 50) % 9) - 4)
    if (x + (y // 4) * 2) % 5 == 0:
        c = shade(c, -30)
    return c


def olive_log_end(x, y):
    d = math.hypot(x - 7.5, y - 7.5)
    c = shade((176, 152, 108), (h(x, y, 51) % 7) - 3)
    if int(d) % 2 == 1:
        c = shade(c, -22)
    if d > 7.2:
        c = shade((112, 96, 78), -10)
    return c


def olive_leaves():
    p = Pix()
    for y in range(16):
        for x in range(16):
            n = h(x, y, 52)
            if n < 12:
                continue                                 # a gap: cutout
            c = OLIVE if n < 60 else (shade(OLIVE, 22) if n < 85 else (150, 166, 130))   # grey-green underside
            p.put(x, y, shade(c, (h(x, y, 53) % 9) - 4))
    return p


# ---------- items ----------

def thunderbolt():
    p = Pix()
    bolt = [(11, 1), (10, 2), (9, 3), (8, 4), (7, 5), (8, 6), (9, 6), (7, 7), (6, 8), (5, 9), (4, 10), (3, 11), (3, 12), (9, 5), (8, 5), (10, 3), (9, 4), (6, 9), (5, 10)]
    for (x, y) in bolt:
        p.put(x, y, GOLD_L if (x + y) % 3 == 0 else GOLD)
        p.put(x + 1, y, GOLD)
    p.outline((90, 60, 10))
    return p


def thread():
    p = Pix()
    red = (190, 40, 50)
    for t in range(0, 60):
        a = t * 0.35
        r = 1.2 + t * 0.1
        p.put(round(7.5 + math.cos(a) * r), round(7.5 + math.sin(a) * r), red if t % 5 else shade(red, 40))
    p.disc(7.5, 7.5, 1.0, (230, 200, 170))
    p.outline((60, 10, 14))
    return p


def ambrosia():
    p = Pix()
    p.disc(7.5, 9.0, 5.2, GOLD)
    p.disc(7.5, 8.0, 3.0, GOLD_L)
    p.rect(5, 3, 10, 4, (255, 255, 255))
    p.rect(6, 5, 9, 5, GOLD_D)
    p.put(4, 8, (255, 255, 255)); p.put(11, 6, (255, 255, 255))
    p.outline((110, 70, 10))
    return p


def obol():
    p = Pix()
    p.disc(7.5, 7.5, 5.4, BRONZE)
    p.disc(7.5, 7.5, 3.6, shade(BRONZE, 22))
    p.rect(7, 5, 8, 10, BRONZE_D)
    p.rect(5, 7, 10, 8, BRONZE_D)
    p.outline((60, 36, 10))
    return p


def bloodstone():
    p = Pix()
    for (x0, y0, x1, y1) in [(5, 3, 10, 12), (4, 5, 11, 10), (6, 2, 9, 13)]:
        p.rect(x0, y0, x1, y1, (176, 30, 40))
    p.rect(6, 4, 7, 6, (240, 100, 110))
    p.outline((50, 8, 12))
    return p


def horn():
    p = Pix()
    path = [(2, 13), (3, 12), (4, 11), (5, 10), (6, 8), (7, 6), (9, 5), (11, 4), (12, 3), (13, 3), (13, 4)]
    for i, (x, y) in enumerate(path):
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            p.put(x + dx, y + dy, (236, 224, 196) if i % 3 else (206, 190, 150))
    p.rect(1, 13, 3, 14, (120, 90, 60))
    p.outline((70, 50, 30))
    return p


# ---------- lang ----------

LANG = {
    "item.olympia.thunderbolt": "Thunderbolt of Zeus",
    "item.olympia.thunderbolt.lore": "Hurled from where you look. Answers only to those Zeus has named Favored.",
    "item.olympia.thread_of_ariadne": "Thread of Ariadne",
    "item.olympia.thread_of_ariadne.lore": "Use once to tie the thread here. Use it again anywhere to learn the way back.",
    "item.olympia.ambrosia": "Ambrosia",
    "item.olympia.ambrosia.lore": "Food of the gods. Eat it, even when you are not hungry.",
    "item.olympia.obol": "Obol",
    "item.olympia.obol.lore": "A small bronze coin. The dead are said to pay the ferryman.",
    "item.olympia.cyclops_bloodstone": "Cyclops Bloodstone",
    "item.olympia.cyclops_bloodstone.lore": "A red stone from a cyclops' forge. Still warm.",
    "item.olympia.minotaur_horn": "Minotaur Horn",
    "item.olympia.minotaur_horn.lore": "Taken from the thing in the labyrinth. It remembers the dark.",
    "block.olympia.white_marble": "White Marble", "block.olympia.polished_marble": "Polished Marble",
    "block.olympia.weathered_marble": "Weathered Marble", "block.olympia.cracked_marble": "Cracked Marble",
    "block.olympia.black_marble": "Black Marble", "block.olympia.pink_marble": "Pink Marble",
    "block.olympia.veined_marble": "Veined Marble", "block.olympia.golden_marble": "Golden Marble",
    "block.olympia.marble_bricks": "Marble Bricks", "block.olympia.marble_tiles": "Marble Tiles",
    "block.olympia.greek_mosaic": "Greek Mosaic", "block.olympia.roof_tile": "Greek Roof Tile",
    "block.olympia.doric_column": "Doric Column", "block.olympia.ionic_column": "Ionic Column",
    "block.olympia.corinthian_column": "Corinthian Column", "block.olympia.amphora": "Amphora",
    "block.olympia.greek_brazier": "Greek Fire Brazier", "block.olympia.laurel": "Laurel",
    "block.olympia.olive_log": "Olive Log", "block.olympia.olive_leaves": "Olive Leaves",
    "block.olympia.zeus_altar": "Altar of Zeus",
    "block.olympia.apollo_altar": "Altar of Apollo",
    "block.olympia.artemis_altar": "Altar of Artemis",
    "block.olympia.ares_altar": "Altar of Ares",
    "block.olympia.demeter_altar": "Altar of Demeter", "block.olympia.athena_altar": "Altar of Athena",
    "block.olympia.poseidon_altar": "Altar of Poseidon", "block.olympia.hermes_altar": "Altar of Hermes",
    "entity.olympia.hoplite": "Hoplite", "entity.olympia.cyclops": "Cyclops", "entity.olympia.minotaur": "Minotaur",
    "item.olympia.hoplite_spawn_egg": "Hoplite Spawn Egg", "item.olympia.cyclops_spawn_egg": "Cyclops Spawn Egg",
    "item.olympia.minotaur_spawn_egg": "Minotaur Spawn Egg",
    "itemGroup.olympia": "Olympia",
}
for f in FAMILIES:
    title = f.replace("_", " ").title()
    LANG[f"block.olympia.{f}_stairs"] = f"{title} Stairs"
    LANG[f"block.olympia.{f}_slab"] = f"{title} Slab"

EGGS = {}   # spawn eggs belong to `shadw-mod mob gen` (mobs/*.json)


# ---------- creature skins (zombie model) ----------

def fill_faces(s, part, c, noise=3, salt=60):
    for name in part:
        s.face_fill = None
        x0, y0, x1, y1 = part[name]
        s.fill(x0, y0, x1, y1, c, noise, salt)


def hoplite():
    s = sk.Skin()
    skin_c, chiton, bronze = (214, 168, 128), (236, 232, 218), (176, 124, 60)
    fill_faces(s, sk.HEAD, skin_c)
    fill_faces(s, sk.BODY, chiton, 4, 61)
    fill_faces(s, sk.RARM, skin_c, 3, 62)
    fill_faces(s, sk.LARM, skin_c, 3, 62)
    fill_faces(s, sk.RLEG, (180, 130, 90), 3, 63)
    fill_faces(s, sk.LLEG, (180, 130, 90), 3, 63)
    # breastplate over the body front and back
    for f in ("front", "back"):
        x0, y0, x1, y1 = sk.BODY[f]
        s.fill(x0, y0, x1, y0 + 6, bronze, 5, 64)
        s.fill(x0, y0 + 7, x1, y0 + 8, BRONZE_D, 2, 65)
    # the Corinthian helmet: bronze on the head, a dark T-shaped face opening and a red crest on top
    for f in ("right", "left", "back", "top"):
        x0, y0, x1, y1 = sk.HEAD[f]
        s.fill(x0, y0, x1, y1, bronze, 5, 66)
    fx0, fy0, fx1, fy1 = sk.HEAD["front"]
    s.fill(fx0, fy0, fx1, fy0 + 2, bronze, 4, 67)
    s.fill(fx0 + 1, fy0 + 3, fx0 + 6, fy0 + 6, skin_c, 3, 68)
    s.fill(fx0 + 3, fy0 + 3, fx0 + 4, fy0 + 7, (50, 34, 24))                       # nose guard
    s.put(fx0 + 1, fy0 + 4, (30, 24, 20)); s.put(fx0 + 6, fy0 + 4, (30, 24, 20))
    tx0, ty0, tx1, ty1 = sk.HEAD["top"]
    s.fill(tx0 + 3, ty0, tx0 + 4, ty1, (176, 40, 40))                              # crest
    # sandals and shield-arm band
    for f in sk.SIDES:
        x0, y0, x1, y1 = sk.RLEG[f]
        s.fill(x0, y1 - 1, x1, y1, (110, 74, 40))
        x0, y0, x1, y1 = sk.LLEG[f]
        s.fill(x0, y1 - 1, x1, y1, (110, 74, 40))
        x0, y0, x1, y1 = sk.LARM[f]
        s.fill(x0, y0 + 4, x1, y0 + 5, bronze)
    return s


def cyclops():
    s = sk.Skin()
    skin_c, rag = (178, 140, 104), (118, 84, 52)
    fill_faces(s, sk.HEAD, skin_c, 5, 70)
    fill_faces(s, sk.BODY, skin_c, 5, 71)
    fill_faces(s, sk.RARM, skin_c, 5, 72)
    fill_faces(s, sk.LARM, skin_c, 5, 72)
    fill_faces(s, sk.RLEG, rag, 5, 73)
    fill_faces(s, sk.LLEG, rag, 5, 73)
    # a ragged tunic
    for f in sk.SIDES:
        x0, y0, x1, y1 = sk.BODY[f]
        s.fill(x0, y0 + 2, x1, y1, rag, 5, 74)
        for x in range(x0, x1 + 1, 2):
            s.put(x, y1, skin_c)
    # one huge eye in the middle of the face, a heavy brow above it, a tooth below
    fx0, fy0, fx1, fy1 = sk.HEAD["front"]
    s.fill(fx0 + 1, fy0 + 1, fx1 - 1, fy0 + 1, (70, 50, 34))
    s.fill(fx0 + 2, fy0 + 2, fx1 - 2, fy0 + 5, (244, 240, 230))
    s.fill(fx0 + 3, fy0 + 3, fx1 - 3, fy0 + 4, (60, 130, 170))
    s.put(fx0 + 3, fy0 + 3, (20, 20, 24)); s.put(fx0 + 4, fy0 + 3, (20, 20, 24))
    s.fill(fx0 + 2, fy0 + 6, fx1 - 2, fy0 + 6, (60, 30, 24))
    s.put(fx0 + 3, fy0 + 7, (240, 236, 220))
    for f in ("top", "back", "right", "left"):
        x0, y0, x1, y1 = sk.HEAD[f]
        s.fill(x0, y0, x1, y1, (60, 44, 32), 3, 75) if f == "top" else None
    return s


def minotaur():
    s = sk.Skin()
    fur, fur_d, horn_c, skin_c = (96, 62, 44), (70, 44, 30), (230, 218, 186), (190, 140, 110)
    fill_faces(s, sk.HEAD, fur, 6, 80)
    fill_faces(s, sk.BODY, skin_c, 5, 81)
    fill_faces(s, sk.RARM, skin_c, 5, 82)
    fill_faces(s, sk.LARM, skin_c, 5, 82)
    fill_faces(s, sk.RLEG, fur, 6, 83)
    fill_faces(s, sk.LLEG, fur, 6, 83)
    for f in sk.SIDES:                                                             # a leather kilt and fur legs
        x0, y0, x1, y1 = sk.BODY[f]
        s.fill(x0, y1 - 3, x1, y1, (120, 80, 48), 4, 84)
    fx0, fy0, fx1, fy1 = sk.HEAD["front"]
    s.fill(fx0 + 2, fy0 + 4, fx1 - 2, fy1, (160, 118, 96), 4, 85)                   # a pale muzzle
    s.fill(fx0 + 3, fy0 + 6, fx0 + 4, fy0 + 6, (30, 20, 18)); s.fill(fx1 - 4, fy0 + 6, fx1 - 3, fy0 + 6, (30, 20, 18))   # nostrils
    s.fill(fx0 + 3, fy1, fx1 - 3, fy1, (210, 190, 40))                             # a gold nose ring
    s.fill(fx0 + 1, fy0 + 2, fx0 + 2, fy0 + 3, (220, 40, 30)); s.fill(fx1 - 2, fy0 + 2, fx1 - 1, fy0 + 3, (220, 40, 30))   # red eyes
    for f, (a, b) in (("right", (0, 2)), ("left", (0, 2))):                        # horns drawn on the head's sides (painted, not 3D)
        x0, y0, x1, y1 = sk.HEAD[f]
        s.fill(x0, y0, x0 + 1, y0 + 2, horn_c)
        s.fill(x1 - 1, y0, x1, y0 + 2, horn_c)
    x0, y0, x1, y1 = sk.HEAD["top"]
    s.fill(x0, y0, x0 + 1, y1, horn_c); s.fill(x1 - 1, y0, x1, y1, horn_c)
    return s


# ---------- block family models ----------

def stairs_state(name):
    base = f"{NS}:block/{name}_stairs"
    inner, outer = base + "_inner", base + "_outer"
    rot = {"straight": {"east": 0, "west": 180, "south": 90, "north": 270}, "outer_right": {"east": 0, "west": 180, "south": 90, "north": 270},
           "outer_left": {"east": 270, "west": 90, "south": 0, "north": 180}, "inner_right": {"east": 0, "west": 180, "south": 90, "north": 270},
           "inner_left": {"east": 270, "west": 90, "south": 0, "north": 180}}
    top = {"straight": {"east": 0, "west": 180, "south": 90, "north": 270}, "outer_right": {"east": 90, "west": 270, "south": 180, "north": 0},
           "outer_left": {"east": 0, "west": 180, "south": 90, "north": 270}, "inner_right": {"east": 90, "west": 270, "south": 180, "north": 0},
           "inner_left": {"east": 0, "west": 180, "south": 90, "north": 270}}
    v = {}
    for shape in rot:
        model = base if shape == "straight" else (inner if shape.startswith("inner") else outer)
        for facing in ("east", "west", "south", "north"):
            e = {"model": model, "y": rot[shape][facing]}
            if e["y"] == 0:
                del e["y"]
            else:
                e["uvlock"] = True
            v[f"facing={facing},half=bottom,shape={shape}"] = e
            t = {"model": model, "x": 180, "uvlock": True}
            if top[shape][facing]:
                t["y"] = top[shape][facing]
            v[f"facing={facing},half=top,shape={shape}"] = t
    return {"variants": v}


def main():
    for name, fn in STONE_FNS.items():
        tex(fn).save(ASSETS / f"textures/block/{name}.png")
        wj(ASSETS / f"models/block/{name}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/{name}"}})
        wj(ASSETS / f"blockstates/{name}.json", {"variants": {"": {"model": f"{NS}:block/{name}"}}})
        item_def(name, f"{NS}:block/{name}")
    for name in FAMILIES:
        tx = {"bottom": f"{NS}:block/{name}", "top": f"{NS}:block/{name}", "side": f"{NS}:block/{name}"}
        for suffix, parent in (("", "stairs"), ("_inner", "inner_stairs"), ("_outer", "outer_stairs")):
            wj(ASSETS / f"models/block/{name}_stairs{suffix}.json", {"parent": f"minecraft:block/{parent}", "textures": tx})
        wj(ASSETS / f"blockstates/{name}_stairs.json", stairs_state(name))
        item_def(f"{name}_stairs", f"{NS}:block/{name}_stairs")
        wj(ASSETS / f"models/block/{name}_slab.json", {"parent": "minecraft:block/slab", "textures": tx})
        wj(ASSETS / f"models/block/{name}_slab_top.json", {"parent": "minecraft:block/slab_top", "textures": tx})
        wj(ASSETS / f"blockstates/{name}_slab.json", {"variants": {"type=bottom": {"model": f"{NS}:block/{name}_slab"},
            "type=top": {"model": f"{NS}:block/{name}_slab_top"}, "type=double": {"model": f"{NS}:block/{name}"}}})
        item_def(f"{name}_slab", f"{NS}:block/{name}_slab")
    for order in ("doric", "ionic", "corinthian"):
        name = f"{order}_column"
        tex(column_side(order)).save(ASSETS / f"textures/block/{name}.png")
        tex(column_end(order)).save(ASSETS / f"textures/block/{name}_top.png")
        tx = {"end": f"{NS}:block/{name}_top", "side": f"{NS}:block/{name}"}
        wj(ASSETS / f"models/block/{name}.json", {"parent": "minecraft:block/cube_column", "textures": tx})
        wj(ASSETS / f"models/block/{name}_horizontal.json", {"parent": "minecraft:block/cube_column_horizontal", "textures": tx})
        wj(ASSETS / f"blockstates/{name}.json", {"variants": {"axis=y": {"model": f"{NS}:block/{name}"},
            "axis=x": {"model": f"{NS}:block/{name}_horizontal", "x": 90, "y": 90}, "axis=z": {"model": f"{NS}:block/{name}_horizontal", "x": 90}}})
        item_def(name, f"{NS}:block/{name}")
    # olive log: a pillar
    tex(olive_log_side).save(ASSETS / "textures/block/olive_log.png")
    tex(olive_log_end).save(ASSETS / "textures/block/olive_log_top.png")
    tx = {"end": f"{NS}:block/olive_log_top", "side": f"{NS}:block/olive_log"}
    wj(ASSETS / "models/block/olive_log.json", {"parent": "minecraft:block/cube_column", "textures": tx})
    wj(ASSETS / "models/block/olive_log_horizontal.json", {"parent": "minecraft:block/cube_column_horizontal", "textures": tx})
    wj(ASSETS / "blockstates/olive_log.json", {"variants": {"axis=y": {"model": f"{NS}:block/olive_log"},
        "axis=x": {"model": f"{NS}:block/olive_log_horizontal", "x": 90, "y": 90}, "axis=z": {"model": f"{NS}:block/olive_log_horizontal", "x": 90}}})
    item_def("olive_log", f"{NS}:block/olive_log")
    olive_leaves().save(ASSETS / "textures/block/olive_leaves.png")
    wj(ASSETS / "models/block/olive_leaves.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/olive_leaves"}})
    wj(ASSETS / "blockstates/olive_leaves.json", {"variants": {"": {"model": f"{NS}:block/olive_leaves"}}})
    item_def("olive_leaves", f"{NS}:block/olive_leaves")
    tex(amphora_tex).save(ASSETS / "textures/block/amphora.png")
    wj(ASSETS / "models/block/amphora.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/amphora"}})
    wj(ASSETS / "blockstates/amphora.json", {"variants": {"": {"model": f"{NS}:block/amphora"}}})
    item_def("amphora", f"{NS}:block/amphora")
    tex(brazier_side).save(ASSETS / "textures/block/greek_brazier_side.png")
    tex(brazier_top).save(ASSETS / "textures/block/greek_brazier_top.png")
    wj(ASSETS / "models/block/greek_brazier.json", {"parent": "minecraft:block/cube_bottom_top", "textures": {
        "top": f"{NS}:block/greek_brazier_top", "bottom": f"{NS}:block/greek_brazier_side", "side": f"{NS}:block/greek_brazier_side"}})
    wj(ASSETS / "blockstates/greek_brazier.json", {"variants": {"": {"model": f"{NS}:block/greek_brazier"}}})
    item_def("greek_brazier", f"{NS}:block/greek_brazier")
    for god in GODS:
        tex(altar_side(ACCENT[god])).save(ASSETS / f"textures/block/{god}_altar_side.png")
        tex(altar_top(god, ACCENT[god])).save(ASSETS / f"textures/block/{god}_altar_top.png")
        wj(ASSETS / f"models/block/{god}_altar.json", {"parent": "minecraft:block/cube_bottom_top", "textures": {
            "top": f"{NS}:block/{god}_altar_top", "bottom": f"{NS}:block/{god}_altar_side", "side": f"{NS}:block/{god}_altar_side"}})
        wj(ASSETS / f"blockstates/{god}_altar.json", {"variants": {"": {"model": f"{NS}:block/{god}_altar"}}})
        item_def(f"{god}_altar", f"{NS}:block/{god}_altar")
    laurel().save(ASSETS / "textures/block/laurel.png")
    wj(ASSETS / "models/block/laurel.json", {"parent": "minecraft:block/cross", "textures": {"cross": f"{NS}:block/laurel"}})
    wj(ASSETS / "blockstates/laurel.json", {"variants": {"": {"model": f"{NS}:block/laurel"}}})
    wj(ASSETS / "models/item/laurel.json", {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:block/laurel"}})
    item_def("laurel", f"{NS}:item/laurel")
    for name, art in (("thunderbolt", thunderbolt()), ("thread_of_ariadne", thread()), ("ambrosia", ambrosia()), ("obol", obol()),
                      ("cyclops_bloodstone", bloodstone()), ("minotaur_horn", horn())):
        art.save(ASSETS / f"textures/item/{name}.png")
        parent = "minecraft:item/handheld" if name == "thunderbolt" else "minecraft:item/generated"
        wj(ASSETS / f"models/item/{name}.json", {"parent": parent, "textures": {"layer0": f"{NS}:item/{name}"}})
        item_def(name, f"{NS}:item/{name}")
    for name, (a, b) in EGGS.items():
        tint = lambda c: c[0] * 65536 + c[1] * 256 + c[2]
        wj(ASSETS / f"models/item/{name}_spawn_egg.json", {"parent": "minecraft:item/template_spawn_egg"})
        item_def(f"{name}_spawn_egg", f"{NS}:item/{name}_spawn_egg", [tint(a), tint(b)])
    hoplite().save(ASSETS / "textures/entity/hoplite.png")
    cyclops().save(ASSETS / "textures/entity/cyclops.png")
    minotaur().save(ASSETS / "textures/entity/minotaur.png")
    wj(HERE / "content_lang.json", LANG)
    print("content assets written")


if __name__ == "__main__":
    main()
