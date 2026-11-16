"""Build a Minecraft structure template block by block and write it as a gzip NBT file (data/<ns>/structure/*.nbt).

Only blocks you `put` are placed, so a template never carves terrain unless you put AIR explicitly (an underground room needs it).
Block states are (name, props) pairs made with state(); put a chest with its loot table via chest().
"""
from . import nbt

DATA_VERSION = 4189  # Minecraft 1.21.4

AIR = ("minecraft:air", ())


def state(name, **props):
    return (name, tuple(sorted(props.items())))


def chest(facing, loot):
    """(block state, block entity data) for a chest that rolls the given loot table id on first open."""
    return state("minecraft:chest", facing=facing, type="single", waterlogged="false"), {"id": "minecraft:chest", "LootTable": loot}


def hole(x, y, z):
    """Deterministic scatter in [0, 100), for weathering and gaps."""
    return ((x * 73856093) ^ (y * 19349663) ^ (z * 83492791)) % 100


class Structure:
    def __init__(self, sx, sy, sz):
        self.size = (sx, sy, sz)
        self.blocks = {}
        self.nbt = {}
        self.entities = []

    def put(self, x, y, z, block, tag=None):
        sx, sy, sz = self.size
        if 0 <= x < sx and 0 <= y < sy and 0 <= z < sz:
            self.blocks[(x, y, z)] = block
            if tag:
                self.nbt[(x, y, z)] = tag

    def fill(self, x0, y0, z0, x1, y1, z1, block):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                for x in range(x0, x1 + 1):
                    self.put(x, y, z, block)

    def entity(self, x, y, z, entity_id, persistent=True):
        """Place a creature when the structure is placed (a boss in its room). x, y, z are block coordinates inside the template;
        the creature stands at the middle of that block. `persistent` keeps it from despawning."""
        data = {"id": (nbt.STRING, entity_id)}
        if persistent:
            data["PersistenceRequired"] = (nbt.BYTE, 1)
        self.entities.append({"pos": (nbt.LIST, (nbt.DOUBLE, [x + 0.5, float(y), z + 0.5])),
                              "blockPos": (nbt.LIST, (nbt.INT, [x, y, z])), "nbt": (nbt.COMPOUND, data)})

    def remove(self, x, y, z):
        self.blocks.pop((x, y, z), None)

    def dumps(self):
        palette, index = [], {}
        for blk in self.blocks.values():
            if blk not in index:
                index[blk] = len(palette)
                palette.append(blk)
        pal = []
        for name, props in palette:
            c = {"Name": (nbt.STRING, name)}
            if props:
                c["Properties"] = (nbt.COMPOUND, {k: (nbt.STRING, v) for k, v in props})
            pal.append(c)
        blocks = []
        for (x, y, z), blk in sorted(self.blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            c = {"pos": (nbt.LIST, (nbt.INT, [x, y, z])), "state": (nbt.INT, index[blk])}
            tag = self.nbt.get((x, y, z))
            if tag:
                c["nbt"] = (nbt.COMPOUND, {k: (nbt.STRING, v) for k, v in tag.items()})
            blocks.append(c)
        root = {
            "DataVersion": (nbt.INT, DATA_VERSION),
            "size": (nbt.LIST, (nbt.INT, list(self.size))),
            "palette": (nbt.LIST, (nbt.COMPOUND, pal)),
            "blocks": (nbt.LIST, (nbt.COMPOUND, blocks)),
            "entities": (nbt.LIST, (nbt.COMPOUND, self.entities)),
        }
        return nbt.dumps(root)
