#!/usr/bin/env python3
"""Generate Olympia's structures as Minecraft structure files (data/olympia/structure/*.nbt).

    python3 tools/gen_structures.py

Temples of Zeus, Athena and Poseidon (a peristyle temple builder, two variants each: whole and ruined), the shrine of Hermes, an
olive grove, a Greek ruin and the Labyrinth: a procedurally generated maze (depth-first, seeded) under a surface pavilion, with
the Minotaur placed in its centre. Deterministic: the same run writes the same bytes. Placement is data/olympia/worldgen (gen_data.py).
Stdlib only.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shadwlib import nbt  # noqa: E402
from shadwlib.structure import Structure, chest, hole, state  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "src/main/resources/data/olympia/structure"

O = lambda name, **props: state(f"olympia:{name}", **props)
M = lambda name, **props: state(f"minecraft:{name}", **props)
WHITE, POLISHED, BRICKS, TILES = O("white_marble"), O("polished_marble"), O("marble_bricks"), O("marble_tiles")
BRAZIER = O("greek_brazier")


def stairs(name, facing, half="bottom"):
    return O(f"{name}_stairs", facing=facing, half=half, shape="straight", waterlogged="false")


def slab(name, kind="bottom"):
    return O(f"{name}_slab", type=kind, waterlogged="false")


def column(order, axis="y"):
    return O(f"{order}_column", axis=axis)


def weathered(seed, x, y, z, ruined):
    """Marble that has stood a few thousand years: in a ruined variant, some cracked, some weathered, some gone."""
    r = hole(x + seed * 5, y, z)
    if not ruined:
        return WHITE if r > 6 else O("weathered_marble")
    if r < 14:
        return O("cracked_marble")
    if r < 32:
        return O("weathered_marble")
    return WHITE


# ---------- the peristyle temple ----------
# W (x) by L (z); front at z = 0, the altar at the back. Steps, a colonnade, a cella with a door, a pitched roof.

def temple(god, order, ruined, seed, accent_block, loot, extra=None):
    rnd = random.Random(seed * 1297 + len(god))
    W, L = 15, 23
    H = 17
    s = Structure(W, H, L)
    cx = W // 2

    def gone(x, y, z, chance):
        return ruined and hole(x + seed * 3, y, z + 7) < chance

    # base and two steps
    for z in range(L):
        for x in range(W):
            s.put(x, 0, z, weathered(seed, x, 0, z, ruined))
    for z in range(1, L - 1):
        for x in range(1, W - 1):
            s.put(x, 1, z, O("polished_marble") if not gone(x, 1, z, 6) else O("cracked_marble"))
    for z in range(2, L - 2):
        for x in range(2, W - 2):
            s.put(x, 2, z, TILES if (x + z) % 2 == 0 else O("polished_marble"))
    # ring of steps (stairs on the outside edge of the first step)
    for x in range(1, W - 1):
        s.put(x, 1, 0, stairs("polished_marble", "south"))
        s.put(x, 1, L - 1, stairs("polished_marble", "north"))
    for z in range(1, L - 1):
        s.put(0, 1, z, stairs("polished_marble", "east"))
        s.put(W - 1, 1, z, stairs("polished_marble", "west"))
    # the colonnade: columns every second block around the platform at x=3 and x=W-4, z=3.. L-4
    col_height = 7
    xs = [3, W - 4]
    zs = list(range(3, L - 3, 2))
    for x in (3, W - 4):
        for z in zs:
            for y in range(3, 3 + col_height):
                if gone(x, y, z, 14 if y > 6 else 4):
                    break
                s.put(x, y, z, column(order))
    for z in (3, L - 4):
        for x in range(3, W - 3, 2):
            if x in (3, W - 4):
                continue
            for y in range(3, 3 + col_height):
                if gone(x, y, z, 14 if y > 6 else 4):
                    break
                s.put(x, y, z, column(order))
    # entablature: a polished band with a mosaic frieze, then a cornice slab ring
    top = 3 + col_height
    for z in range(3, L - 2):
        for x in range(3, W - 2):
            edge = x in (3, W - 4) or z in (3, L - 4)
            if not edge:
                continue
            if gone(x, top, z, 18):
                continue
            s.put(x, top, z, POLISHED)
            if not gone(x, top + 1, z, 24):
                s.put(x, top + 1, z, O("greek_mosaic") if (x + z) % 2 == 0 else WHITE)
    # the cella: walls of marble bricks, a doorway at the front, the altar at the back
    for z in range(8, L - 4):
        for x in range(5, W - 5):
            if x in (5, W - 6) or z in (8, L - 5):
                for y in range(3, 3 + col_height):
                    if gone(x, y, z, 10 if y > 5 else 3):
                        continue
                    s.put(x, y, z, BRICKS if hole(x, y, z) > 8 else O("weathered_marble"))
    for y in range(3, 6):
        s.remove(cx, y, 8)                                              # the door
    s.put(cx, 6, 8, O("greek_mosaic"))
    # a pitched roof over the colonnade: roof-tile stairs rising to a ridge along z
    for z in range(2, L - 1):
        for k in range(0, W // 2 + 1):
            y = top + 2 + k
            if y >= H - 1:
                break
            for x, facing in ((2 + k, "east"), (W - 3 - k, "west")):
                if x < 2 or x > W - 3:
                    continue
                if gone(x, y, z, 22):
                    continue
                if (x == cx):
                    s.put(x, y, z, slab("roof_tile", "bottom"))
                else:
                    s.put(x, y, z, stairs("roof_tile", facing))
    for z in (2, L - 3):                                                # the pediments, in marble, at the two ends
        for y in range(top + 2, H - 1):
            half = (y - (top + 2))
            for x in range(2 + half + 1, W - 3 - half):
                if not gone(x, y, z, 18):
                    s.put(x, y, z, WHITE if (x + y) % 5 else accent_block)
    # inside: altar, braziers, a chest
    s.put(cx, 3, L - 6, O(f"{god}_altar"))
    s.put(cx - 2, 3, L - 6, BRAZIER)
    s.put(cx + 2, 3, L - 6, BRAZIER)
    blk, tag = chest("north", loot)
    s.put(cx + 3, 3, L - 7, blk, tag)
    if extra:
        extra(s, rnd, W, L, cx)
    # front approach: braziers and an amphora either side of the steps
    for x in (2, W - 3):
        s.put(x, 3, 1, BRAZIER)
    s.put(cx - 2, 3, 1, O("amphora"))
    s.put(cx + 2, 3, 1, O("amphora"))
    return s


def zeus_extra(s, rnd, W, L, cx):
    # lightning bolts of gold above the door, a pair of eagle perches (gold blocks) on the front columns
    for y in range(9, 12):
        s.put(cx, y, 2, M("gold_block") if y % 2 else M("glowstone"))
    s.put(3, 11, 3, M("gold_block")); s.put(W - 4, 11, 3, M("gold_block"))
    s.put(cx - 1, 12, 2, M("lightning_rod", facing="up", powered="false", waterlogged="false"))


def athena_extra(s, rnd, W, L, cx):
    # a small library alcove along the cella wall, and an owl perch (a grey block) over the door
    for z in range(L - 9, L - 6):
        for y in (3, 4):
            s.put(6, y, z, M("bookshelf"))
            s.put(W - 7, y, z, M("bookshelf"))
    s.put(cx, 9, 3, M("light_gray_concrete")); s.put(cx, 10, 3, M("white_concrete"))


def poseidon_extra(s, rnd, W, L, cx):
    # water basins either side of the altar (water placed in marble) and prismarine trim
    for dx in (-3, 3):
        s.put(cx + dx, 3, L - 9, M("prismarine_bricks"))
        s.put(cx + dx, 4, L - 9, M("sea_lantern"))
    for x in range(4, W - 4):
        s.put(x, 3, 4, M("prismarine_brick_slab", type="bottom", waterlogged="false")) if x % 2 else None


def apollo_extra(s, rnd, W, L, cx):
    # a sun disc of gold and glowstone over the door, and a lyre stand (gold blocks and a note block) by the altar
    import math
    for yy in range(-3, 4):
        for xx in range(-3, 4):
            d = math.hypot(xx, yy)
            if 2.2 <= d <= 3.2:
                s.put(cx + xx, 11 + yy, 2, M("gold_block"))
            elif d < 2.2:
                s.put(cx + xx, 11 + yy, 2, M("glowstone") if d < 1.2 else M("yellow_stained_glass"))
    s.put(cx - 4, 3, L - 8, M("note_block")); s.put(cx - 4, 4, L - 8, M("gold_block"))


def artemis_extra(s, rnd, W, L, cx):
    # a crescent over the door in white concrete, with lanterns, and a pair of deer (white wool) at the steps
    import math
    for yy in range(-3, 4):
        for xx in range(-3, 4):
            if math.hypot(xx, yy) <= 3.2 and math.hypot(xx - 1.5, yy) > 2.6:
                s.put(cx + xx, 11 + yy, 2, M("white_concrete"))
    for x in (cx - 3, cx + 3):
        s.put(x, 5, 1, M("lantern", hanging="false", waterlogged="false"))


def ares_extra(s, rnd, W, L, cx):
    # weapon racks along the cella wall (iron bars with anvils below) and red banners at the door
    for z in range(L - 10, L - 6, 2):
        s.put(6, 3, z, M("anvil", facing="east"))
        s.put(W - 7, 3, z, M("anvil", facing="west"))
        for y in (4, 5):
            s.put(6, y, z, M("iron_bars")); s.put(W - 7, y, z, M("iron_bars"))
    for x in (cx - 1, cx + 1):
        for y in (6, 7, 8):
            s.put(x, y, 7, M("red_wool"))


def demeter_extra(s, rnd, W, L, cx):
    # sheaves of hay beside the altar and a little crop plot of wheat in front of the steps
    for x in (cx - 3, cx + 3):
        s.put(x, 3, L - 7, M("hay_block", axis="y"))
    for x in range(cx - 2, cx + 3):
        s.put(x, 3, 1, M("hay_block", axis="y"))


# ---------- the shrine of Hermes: a roadside herm ----------

def hermes_shrine(seed):
    ruined = seed == 1
    N = 9
    s = Structure(N, 9, N)
    c = N // 2
    for z in range(N):
        for x in range(N):
            s.put(x, 0, z, weathered(seed, x, 0, z, ruined))
            if max(abs(x - c), abs(z - c)) <= 3:
                s.put(x, 1, z, TILES if (x + z) % 2 else POLISHED)
    # the herm: a squared pillar with a gold staff and a marble head
    for y in range(2, 6):
        s.put(c, y, c - 1, POLISHED if y < 4 else WHITE)
    s.put(c, 6, c - 1, WHITE)
    s.put(c, 7, c - 1, M("gold_block"))
    s.put(c - 1, 5, c - 1, slab("white_marble", "bottom")); s.put(c + 1, 5, c - 1, slab("white_marble", "bottom"))   # the stubs of arms
    s.put(c, 2, c + 1, O("hermes_altar"))
    s.put(c - 2, 2, c + 1, BRAZIER); s.put(c + 2, 2, c + 1, BRAZIER)
    blk, tag = chest("north", "olympia:chests/hermes_shrine")
    s.put(c + 2, 2, c - 1, blk, tag)
    s.put(c - 2, 2, c - 1, O("amphora"))
    for dx in (-3, 3):                                                  # a road marker either side
        s.put(c + dx, 2, c + 3, column("doric"))
        s.put(c + dx, 3, c + 3, slab("polished_marble", "bottom"))
    return s


# ---------- the olive grove ----------

def olive_tree(s, rnd, x, z, tall):
    for y in range(1, 1 + tall):
        s.put(x, y, z, O("olive_log", axis="y"))
    if tall > 3:
        s.put(x + 1, tall - 1, z, O("olive_log", axis="x"))              # a twisted second trunk
    cy = 1 + tall
    for dy in range(-1, 3):
        r = 2 if dy in (0, 1) else 1
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) > r + 1 or hole(x + dx, cy + dy, z + dz) < 12:
                    continue
                pos = (x + dx, cy + dy, z + dz)
                if pos not in s.blocks:
                    s.put(*pos, O("olive_leaves", persistent="true", distance="1", waterlogged="false"))


def olive_grove(seed):
    rnd = random.Random(seed * 424242 + 5)
    N = 27
    s = Structure(N, 10, N)
    trees = []
    attempts = 0
    while len(trees) < 7 + seed * 2 and attempts < 400:
        attempts += 1
        x, z = rnd.randint(2, N - 3), rnd.randint(2, N - 3)
        if all(abs(x - tx) + abs(z - tz) >= 7 for tx, tz in trees) and abs(x - N // 2) + abs(z - N // 2) > 5:
            trees.append((x, z))
    for x, z in trees:
        s.put(x, 0, z, M("grass_block"))
        olive_tree(s, rnd, x, z, rnd.choice((3, 4, 4, 5)))
    for _ in range(26):
        x, z = rnd.randint(1, N - 2), rnd.randint(1, N - 2)
        if (x, 1, z) not in s.blocks and all((x, y, z) not in s.blocks for y in (2, 3)):
            s.put(x, 0, z, M("grass_block"))
            s.put(x, 1, z, O("laurel"))
    c = N // 2
    for dz in (-1, 0, 1):                                                # a little wayside shrine in the middle
        for dx in (-1, 0, 1):
            s.put(c + dx, 0, c + dz, TILES)
    s.put(c, 1, c, O("amphora")); s.put(c - 1, 1, c, BRAZIER); s.put(c + 1, 1, c, BRAZIER)
    blk, tag = chest("south", "olympia:chests/olive_grove")
    s.put(c, 1, c + 1, blk, tag)
    for dx in range(-1, 2):
        s.put(c + dx, 1, c - 1, slab("white_marble", "bottom"))
    return s


# ---------- a Greek ruin ----------

def greek_ruin(seed):
    rnd = random.Random(seed * 7770 + 3)
    N = 17
    s = Structure(N, 12, N)
    c = N // 2
    for z in range(N):
        for x in range(N):
            if max(abs(x - c), abs(z - c)) <= 7:
                s.put(x, 0, z, weathered(seed, x, 0, z, True))
                r = hole(x, 1, z + seed)
                if r < 62:
                    s.put(x, 1, z, O("greek_mosaic") if (r < 14 and abs(x - c) < 4 and abs(z - c) < 4) else O("cracked_marble") if r < 30 else TILES)
    for px, pz in ((3, 3), (13, 3), (3, 13), (13, 13), (8, 2), (8, 14)):    # broken columns of different heights
        order = rnd.choice(("doric", "ionic", "corinthian"))
        for y in range(2, 2 + rnd.randint(2, 6)):
            s.put(px, y, pz, column(order))
    for _ in range(7):                                                     # fallen drums and rubble
        x, z = rnd.randint(2, N - 3), rnd.randint(2, N - 3)
        s.put(x, 2, z, column(rnd.choice(("doric", "ionic")), axis=rnd.choice(("x", "z"))))
    s.put(c, 2, c - 3, O("amphora"))
    s.put(c - 1, 2, c - 3, O("cracked_marble")); s.put(c + 1, 2, c - 3, O("cracked_marble"))
    blk, tag = chest("south", "olympia:chests/greek_ruin")
    s.put(c, 2, c + 2, blk, tag)
    if seed != 1:
        s.put(c + 2, 2, c, BRAZIER)
    for x in range(4, 13):                                                 # a stretch of low wall
        if hole(x, 2, 1) < 70:
            s.put(x, 2, 1, slab("polished_marble", "bottom"))
    return s


# ---------- the Labyrinth ----------
# Layout (template y): maze floor 0, corridors 1..3, ceiling 4; a ladder shaft rises from the entrance cell to a pavilion whose
# floor (y = 13) replaces the top layer of the ground. start_height in gen_data.py is -14, so y = 13 is the top ground layer.
# Corridors are three wide: a one-wide corridor stopped a creature of the Minotaur's size at every corner (measured: it circled
# the hall for a minute and never reached a player 14 blocks away), and a boss needs room to charge.

CELLS = 15
CELL = 3                                                                   # passage width in blocks
PITCH = CELL + 1                                                           # a cell plus one wall
SIZE = CELLS * PITCH + 1                                                   # 61
SURFACE = 13


def maze(seed):
    """A maze on CELLS x CELLS cells, as an open-passage set: depth-first search from the entrance, then about 7 percent of the
    remaining walls knocked through so there are loops. (A perfect maze had routes of 118-266 blocks from the centre to the entrance.)"""
    rnd = random.Random(seed * 9973 + 17)
    start = (CELLS // 2, CELLS - 1)
    seen = {start}
    stack = [start]
    open_between = set()
    while stack:
        cx, cz = stack[-1]
        options = [(cx + dx, cz + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
                   if 0 <= cx + dx < CELLS and 0 <= cz + dz < CELLS and (cx + dx, cz + dz) not in seen]
        if not options:
            stack.pop()
            continue
        nxt = rnd.choice(options)
        open_between.add(frozenset(((cx, cz), nxt)))
        seen.add(nxt)
        stack.append(nxt)
    for cx in range(CELLS):
        for cz in range(CELLS):
            for dx, dz in ((1, 0), (0, 1)):
                other = (cx + dx, cz + dz)
                if other[0] < CELLS and other[1] < CELLS and rnd.random() < 0.07:
                    open_between.add(frozenset(((cx, cz), other)))
    return start, open_between


def cell_origin(c):
    """The lowest x, z of a cell's CELL x CELL floor."""
    return c[0] * PITCH + 1, c[1] * PITCH + 1


def labyrinth(seed):
    start, opened = maze(seed)
    s = Structure(SIZE, 21, SIZE)
    centre = (CELLS // 2, CELLS // 2)
    air = M("air")

    def wall_block(x, y, z):
        r = hole(x, y, z + seed)
        if r < 8:
            return O("cracked_marble")
        if r < 22:
            return O("weathered_marble")
        if r < 26:
            return O("black_marble")
        return BRICKS

    # shell: floor, ceiling, and everything between them solid; passages are carved below
    for z in range(SIZE):
        for x in range(SIZE):
            s.put(x, 0, z, TILES if (x // 2 + z // 2) % 2 else POLISHED)
            for y in range(1, 5):
                s.put(x, y, z, wall_block(x, y, z))

    def carve(x0, x1, z0, z1):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                for y in range(1, 4):
                    s.put(x, y, z, air)

    for cx in range(CELLS):
        for cz in range(CELLS):
            x0, z0 = cell_origin((cx, cz))
            carve(x0, x0 + CELL - 1, z0, z0 + CELL - 1)
    for pair in opened:
        a, b = sorted(tuple(pair))
        ax, az = cell_origin(a)
        if b[0] != a[0]:                                                   # b is east of a: open the wall column between them
            carve(ax + CELL, ax + CELL, az, az + CELL - 1)
        else:                                                              # b is south of a
            carve(ax, ax + CELL - 1, az + CELL, az + CELL)
    # the hall: the centre cell and its neighbours merged into one room, 11 by 11, with a mosaic floor and four black pillars
    hx0, hz0 = cell_origin((centre[0] - 1, centre[1] - 1))
    hx1, hz1 = hx0 + 3 * CELL + 2 - 1, hz0 + 3 * CELL + 2 - 1
    carve(hx0, hx1, hz0, hz1)
    hcx, hcz = (hx0 + hx1) // 2, (hz0 + hz1) // 2
    for z in range(hz0, hz1 + 1):
        for x in range(hx0, hx1 + 1):
            ring = max(abs(x - hcx), abs(z - hcz))
            s.put(x, 0, z, O("greek_mosaic") if ring in (3, 5) else (O("black_marble") if ring == 4 else TILES))
    for px, pz in ((hcx - 4, hcz - 4), (hcx + 4, hcz - 4), (hcx - 4, hcz + 4), (hcx + 4, hcz + 4)):
        for y in range(1, 4):
            s.put(px, y, pz, column("doric"))
    for dx in (-3, 3):
        s.put(hcx + dx, 1, hz0, BRAZIER)
    for dx in (-1, 0, 1):                                                  # a bull altar of black marble against the back wall, with the vault
        s.put(hcx + dx, 1, hz0, O("black_marble"))
    blk, tag = chest("south", "olympia:chests/labyrinth_vault")
    s.put(hcx, 2, hz0, blk, tag)
    s.entity(hcx, 1, hcz, "olympia:minotaur")
    # lamps flush into the ceiling at the middle of some cells (a floor or hanging lantern would block a corridor)
    cells = [(cx, cz) for cx in range(CELLS) for cz in range(CELLS) if max(abs(cx - centre[0]), abs(cz - centre[1])) > 1]
    for c in cells:
        if hole(c[0], 9, c[1] + seed) < 14:
            x0, z0 = cell_origin(c)
            s.put(x0 + 1, 4, z0 + 1, M("glowstone"))
    # treasure vaults: a chest in the middle of each of the four dead-end cells farthest from the entrance
    degree = {c: 0 for c in cells}
    for pair in opened:
        for c in pair:
            if c in degree:
                degree[c] += 1
    dead = sorted((c for c, d in degree.items() if d == 1), key=lambda c: -(abs(c[0] - start[0]) + abs(c[1] - start[1])))
    for c in dead[:4]:
        x0, z0 = cell_origin(c)
        blk, tag = chest("north", "olympia:chests/labyrinth_vault")
        s.put(x0 + 1, 1, z0 + 1, blk, tag)
    # the shaft: a ladder up from the entrance cell (against the outer south wall) to the pavilion, walled so sand and gravel stay out
    ex0, ez0 = cell_origin(start)
    sx, sz = ex0 + 1, ez0 + CELL - 1                                        # middle of the entrance cell's south edge, against the outer wall
    for y in range(4, SURFACE + 1):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if dx or dz:
                    s.put(sx + dx, y, sz + dz, BRICKS)
        s.put(sx, y, sz, air)
    for y in range(1, SURFACE + 2):
        s.put(sx, y, sz, M("ladder", facing="north", waterlogged="false"))      # climbs to y = 14, just above the pavilion floor
    # the pavilion (a stoa): 9 wide, 7 deep, open to the front, with a back wall the ladder leans on
    px0, px1, pz0, pz1 = sx - 4, sx + 4, sz - 6, sz
    for z in range(pz0, pz1 + 1):
        for x in range(px0, px1 + 1):
            s.put(x, SURFACE, z, TILES if (x + z) % 2 else POLISHED)
    s.put(sx, SURFACE, sz, air)
    s.put(sx, SURFACE + 1, sz, M("ladder", facing="north", waterlogged="false"))
    for x in range(px0, px1 + 1):
        for y in range(SURFACE, SURFACE + 5):
            s.put(x, y, sz + 1, BRICKS if hole(x, y, sz) > 10 else O("weathered_marble"))
    for x in range(px0 - 1, px1 + 2):
        if x != sx:
            s.put(x, SURFACE, pz0 - 1, stairs("polished_marble", "south"))
    for cxp, czp in ((px0, pz0), (px1, pz0), (px0, pz1), (px1, pz1)):
        for y in range(SURFACE + 1, SURFACE + 5):
            s.put(cxp, y, czp, column("doric"))
    for z in range(pz0, pz1 + 1):
        for x in range(px0, px1 + 1):
            s.put(x, SURFACE + 5, z, slab("white_marble", "bottom") if (x in (px0, px1) or z in (pz0, pz1)) else O("roof_tile"))
    blk, tag = chest("south", "olympia:chests/labyrinth_entrance")                                      # Ariadne's thread waits up here
    s.put(sx - 2, SURFACE + 1, pz0 + 1, blk, tag)
    s.put(sx, SURFACE + 1, pz0 + 1, O("black_marble")); s.put(sx, SURFACE + 2, pz0 + 1, O("black_marble"))      # a bull altar
    s.put(sx + 2, SURFACE + 1, pz0 + 1, BRAZIER)
    s.put(sx - 1, SURFACE + 1, pz0 + 1, BRAZIER); s.put(sx + 1, SURFACE + 1, pz0 + 1, BRAZIER)
    for x in (px0 + 1, px1 - 1):
        s.put(x, SURFACE + 1, sz - 1, O("amphora"))
    return s


STRUCTURES = {
    "temple_of_zeus": (lambda i: temple("zeus", "doric", i == 1, i, M("gold_block"), "olympia:chests/temple_of_zeus", zeus_extra), 2),
    "temple_of_athena": (lambda i: temple("athena", "ionic", i == 1, i, M("light_gray_concrete"), "olympia:chests/temple_of_athena", athena_extra), 2),
    "temple_of_poseidon": (lambda i: temple("poseidon", "corinthian", i == 1, i, M("prismarine_bricks"), "olympia:chests/temple_of_poseidon", poseidon_extra), 2),
    "temple_of_apollo": (lambda i: temple("apollo", "ionic", i == 1, i, M("gold_block"), "olympia:chests/temple_of_apollo", apollo_extra), 2),
    "temple_of_artemis": (lambda i: temple("artemis", "corinthian", i == 1, i, M("white_concrete"), "olympia:chests/temple_of_artemis", artemis_extra), 2),
    "temple_of_ares": (lambda i: temple("ares", "doric", i == 1, i, M("red_terracotta"), "olympia:chests/temple_of_ares", ares_extra), 2),
    "temple_of_demeter": (lambda i: temple("demeter", "ionic", i == 1, i, M("hay_block", axis="y"), "olympia:chests/temple_of_demeter", demeter_extra), 2),
    "hermes_shrine": (hermes_shrine, 2),
    "olive_grove": (olive_grove, 2),
    "greek_ruin": (greek_ruin, 3),
    "labyrinth": (labyrinth, 3),
}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.nbt"):
        old.unlink()
    for name, (fn, n) in STRUCTURES.items():
        for i in range(n):
            st = fn(i)
            data = st.dumps()
            (OUT / f"{name}_{i}.nbt").write_bytes(data)
            back = nbt.loads(data)
            assert len(back["blocks"][1][1]) == len(st.blocks), name
            assert len(back["entities"][1][1]) == len(st.entities), name
            print(f"{name}_{i}: size {st.size}, {len(st.blocks)} blocks, {len(st.entities)} entities, {len(back['palette'][1][1])} states, {len(data)} bytes")
