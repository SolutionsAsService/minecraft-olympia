#!/usr/bin/env python3
"""Generate Olympia's loot tables, recipes, block tags, advancements and worldgen data.

    python3 tools/gen_data.py

The structures themselves come from tools/gen_structures.py. Everything here is derived from this script. Stdlib only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "src/main/resources/data"
K = D / "olympia"
STONES = ["white_marble", "polished_marble", "weathered_marble", "cracked_marble", "black_marble", "pink_marble", "veined_marble",
          "golden_marble", "marble_bricks", "marble_tiles", "greek_mosaic", "roof_tile"]
FAMILIES = ["white_marble", "polished_marble", "marble_bricks", "roof_tile"]
COLUMNS = ["doric_column", "ionic_column", "corinthian_column"]
GODS = ["zeus", "athena", "poseidon", "hermes"]
STAIRS = [f"{f}_stairs" for f in FAMILIES]
SLABS = [f"{f}_slab" for f in FAMILIES]
BLOCKS = STONES + STAIRS + SLABS + COLUMNS + ["amphora", "greek_brazier", "laurel", "olive_log", "olive_leaves"] + [f"{g}_altar" for g in GODS]


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def item(name, weight, lo=None, hi=None):
    e = {"type": "minecraft:item", "name": name, "weight": weight}
    if lo is not None:
        e["functions"] = [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]
    return e


def pool(entries, lo, hi):
    return {"rolls": {"type": "minecraft:uniform", "min": lo, "max": hi}, "entries": entries}


def chance(entries, c):
    return {"rolls": 1, "bonus_rolls": 0, "conditions": [{"condition": "minecraft:random_chance", "chance": c}], "entries": entries}


def sure(entries):
    return {"rolls": 1, "bonus_rolls": 0, "entries": entries}


def potion_item(pid, weight):
    return {"type": "minecraft:item", "name": "minecraft:potion", "weight": weight, "functions": [{"function": "minecraft:set_potion", "id": pid}]}


def survives():
    return [{"condition": "minecraft:survives_explosion"}]


def drops_self(name):
    return {"type": "minecraft:block", "random_sequence": f"olympia:blocks/{name}", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "conditions": survives(), "entries": [{"type": "minecraft:item", "name": f"olympia:{name}"}]}]}


def drops_slab(name):
    return {"type": "minecraft:block", "random_sequence": f"olympia:blocks/{name}", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"olympia:{name}", "functions": [
            {"function": "minecraft:set_count", "count": 2, "add": False, "conditions": [{"condition": "minecraft:block_state_property",
                                                                                         "block": f"olympia:{name}", "properties": {"type": "double"}}]},
            {"function": "minecraft:explosion_decay"}]}]}]}


def drops_leaves():
    shears = {"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}}
    silk = {"condition": "minecraft:match_tool", "predicate": {"predicates": {"minecraft:enchantments": [
        {"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}
    return {"type": "minecraft:block", "random_sequence": "olympia:blocks/olive_leaves", "pools": [
        {"rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:alternatives", "children": [
            {"type": "minecraft:item", "name": "olympia:olive_leaves", "conditions": [{"condition": "minecraft:any_of", "terms": [shears, silk]}]},
        ]}]},
        {"rolls": 1, "bonus_rolls": 0, "conditions": [{"condition": "minecraft:inverted", "term": {"condition": "minecraft:any_of", "terms": [shears, silk]}},
                                                      {"condition": "minecraft:random_chance", "chance": 0.07}],
         "entries": [{"type": "minecraft:item", "name": "olympia:sacred_olive"}]}]}


# structure name: (spacing, separation, salt, biomes, start_height, spawn overrides, terrain adaptation)
FOREST_LAND = ["minecraft:plains", "minecraft:meadow", "minecraft:sunflower_plains", "minecraft:savanna", "minecraft:forest"]
HOP = lambda lo, hi: {"monster": {"bounding_box": "piece", "spawns": [{"type": "olympia:hoplite", "weight": 10, "minCount": lo, "maxCount": hi}]}}
STRUCTS = {
    "temple_of_zeus": (34, 10, 9123401, ["minecraft:plains", "minecraft:meadow", "minecraft:sunflower_plains"], -1, HOP(1, 2), "beard_thin"),
    "temple_of_athena": (34, 10, 9123402, FOREST_LAND, -1, HOP(1, 2), "beard_thin"),
    "temple_of_poseidon": (36, 10, 9123403, ["#minecraft:is_beach"], -1, {}, "beard_thin"),
    "hermes_shrine": (18, 6, 9123404, FOREST_LAND, -1, {}, "beard_thin"),
    "olive_grove": (20, 8, 9123405, ["minecraft:plains", "minecraft:savanna", "minecraft:meadow", "minecraft:forest"], -1, {}, "none"),
    "greek_ruin": (22, 8, 9123406, FOREST_LAND, -1, HOP(2, 3), "beard_thin"),
    "labyrinth": (40, 14, 9123407, ["minecraft:plains", "minecraft:meadow", "minecraft:savanna", "minecraft:forest", "minecraft:sunflower_plains"], -14, {}, "none"),
}
VARIANTS = {"temple_of_zeus": 2, "temple_of_athena": 2, "temple_of_poseidon": 2, "hermes_shrine": 2, "olive_grove": 2, "greek_ruin": 3, "labyrinth": 3}


def main():
    for n in BLOCKS:
        if n in SLABS:
            write(K / "loot_table/blocks" / f"{n}.json", drops_slab(n))
        elif n == "olive_leaves":
            write(K / "loot_table/blocks" / f"{n}.json", drops_leaves())
        else:
            write(K / "loot_table/blocks" / f"{n}.json", drops_self(n))
    chests = {
        "temple_of_zeus": [pool([item("minecraft:gold_ingot", 6, 2, 6), item("minecraft:emerald", 4, 1, 3), item("minecraft:lightning_rod", 4, 1, 2),
                                 item("olympia:thunder_shard", 4, 1, 2), item("olympia:white_marble", 4, 4, 10), item("olympia:ambrosia", 2),
                                 item("olympia:obol", 4, 2, 6), potion_item("olympia:zeus_fury", 2)], 4, 6),
                           chance([item("olympia:thunderbolt", 1)], 0.35)],
        "temple_of_athena": [pool([item("minecraft:book", 6, 2, 5), item("minecraft:iron_ingot", 5, 2, 6), item("olympia:owl_feather", 4, 1, 3),
                                   item("minecraft:bookshelf", 3, 1, 3), item("olympia:polished_marble", 4, 4, 10), item("olympia:ambrosia", 2),
                                   item("olympia:obol", 4, 2, 6), potion_item("olympia:athena_wisdom", 2)], 4, 6),
                             chance([{"type": "minecraft:item", "name": "minecraft:book", "functions": [{"function": "minecraft:enchant_randomly"}]}], 0.5)],
        "temple_of_poseidon": [pool([item("minecraft:cod", 6, 2, 6), item("minecraft:prismarine_shard", 5, 2, 6), item("minecraft:nautilus_shell", 3, 1, 2),
                                     item("olympia:sea_pearl", 4, 1, 3), item("minecraft:prismarine_crystals", 4, 2, 5), item("olympia:ambrosia", 2),
                                     item("olympia:obol", 4, 2, 6), potion_item("olympia:poseidon_breath", 2)], 4, 6),
                               chance([item("minecraft:heart_of_the_sea", 1)], 0.2)],
        "hermes_shrine": [pool([item("minecraft:feather", 6, 2, 6), item("minecraft:emerald", 4, 1, 3), item("minecraft:leather_boots", 2),
                                item("olympia:winged_feather", 3, 1, 2), item("olympia:obol", 5, 2, 6), item("minecraft:map", 2),
                                potion_item("olympia:hermes_swiftness", 2)], 3, 5)],
        "olive_grove": [pool([item("olympia:sacred_olive", 7, 3, 6), item("minecraft:bread", 5, 1, 3), item("minecraft:honey_bottle", 3, 1, 2),
                              item("olympia:laurel", 4, 1, 3), item("minecraft:golden_apple", 1), item("olympia:ambrosia", 1)], 2, 4)],
        "greek_ruin": [pool([item("olympia:obol", 7, 2, 6), item("minecraft:gold_nugget", 5, 2, 8), item("olympia:amphora", 3, 1, 2),
                             item("olympia:cracked_marble", 4, 3, 8), item("minecraft:emerald", 2, 1, 2), item("minecraft:iron_ingot", 4, 1, 4)], 2, 4)],
        "labyrinth_entrance": [sure([item("olympia:thread_of_ariadne", 1)]), pool([item("minecraft:torch", 6, 8, 16), item("minecraft:bread", 4, 2, 4),
                                                                                    item("minecraft:string", 3, 2, 6)], 1, 2)],
        "labyrinth_vault": [pool([item("olympia:ambrosia", 3, 1, 2), item("olympia:obol", 6, 3, 9), item("minecraft:diamond", 2, 1, 2),
                                  item("minecraft:gold_ingot", 5, 2, 6), item("olympia:cyclops_bloodstone", 2, 1, 1),
                                  item("minecraft:golden_apple", 2), item("olympia:white_marble", 4, 4, 12)], 3, 5),
                            chance([item("minecraft:enchanted_golden_apple", 1)], 0.04)],
    }
    for name, pools in chests.items():
        write(K / "loot_table/chests" / f"{name}.json", {"type": "minecraft:chest", "pools": pools})
    write(K / "loot_table/entities/hoplite.json", {"type": "minecraft:entity", "pools": [
        pool([item("olympia:obol", 1, 0, 2)], 1, 1), chance([item("minecraft:iron_nugget", 1, 1, 4)], 0.4), chance([item("minecraft:emerald", 1)], 0.08)]})
    write(K / "loot_table/entities/cyclops.json", {"type": "minecraft:entity", "pools": [
        pool([item("minecraft:bone", 1, 1, 3)], 1, 1), chance([item("olympia:cyclops_bloodstone", 1)], 0.5),
        chance([item("minecraft:iron_ingot", 1, 1, 3)], 0.6), chance([item("olympia:obol", 1, 1, 4)], 0.5)]})
    write(K / "loot_table/entities/minotaur.json", {"type": "minecraft:entity", "pools": [
        sure([item("olympia:minotaur_horn", 1)]), pool([item("olympia:ambrosia", 1, 2, 4)], 1, 1), pool([item("minecraft:diamond", 1, 1, 3)], 1, 1),
        pool([item("olympia:obol", 1, 10, 20)], 1, 1)]})
    rec = K / "recipe"
    for n in STONES:
        if n == "white_marble":
            write(rec / "white_marble_from_stonecutting.json", {"type": "minecraft:stonecutting", "ingredient": "minecraft:calcite", "result": {"id": "olympia:white_marble", "count": 1}})
        elif n == "roof_tile":
            write(rec / "roof_tile_from_stonecutting.json", {"type": "minecraft:stonecutting", "ingredient": "minecraft:terracotta", "result": {"id": "olympia:roof_tile", "count": 1}})
        else:
            write(rec / f"{n}_from_stonecutting.json", {"type": "minecraft:stonecutting", "ingredient": "olympia:white_marble", "result": {"id": f"olympia:{n}", "count": 1}})
    for f in FAMILIES:
        write(rec / f"{f}_stairs.json", {"type": "minecraft:crafting_shaped", "category": "building", "pattern": ["X  ", "XX ", "XXX"],
              "key": {"X": f"olympia:{f}"}, "result": {"id": f"olympia:{f}_stairs", "count": 4}})
        write(rec / f"{f}_slab.json", {"type": "minecraft:crafting_shaped", "category": "building", "pattern": ["XXX"],
              "key": {"X": f"olympia:{f}"}, "result": {"id": f"olympia:{f}_slab", "count": 6}})
        write(rec / f"{f}_stairs_from_stonecutting.json", {"type": "minecraft:stonecutting", "ingredient": f"olympia:{f}", "result": {"id": f"olympia:{f}_stairs", "count": 1}})
        write(rec / f"{f}_slab_from_stonecutting.json", {"type": "minecraft:stonecutting", "ingredient": f"olympia:{f}", "result": {"id": f"olympia:{f}_slab", "count": 2}})
    write(rec / "doric_column.json", {"type": "minecraft:crafting_shaped", "category": "building", "pattern": ["X", "X", "X"],
          "key": {"X": "olympia:white_marble"}, "result": {"id": "olympia:doric_column", "count": 3}})
    write(rec / "ionic_column.json", {"type": "minecraft:crafting_shapeless", "category": "building", "ingredients": ["olympia:doric_column", "minecraft:lapis_lazuli"],
          "result": {"id": "olympia:ionic_column", "count": 1}})
    write(rec / "corinthian_column.json", {"type": "minecraft:crafting_shapeless", "category": "building",
          "ingredients": ["olympia:doric_column", "minecraft:gold_nugget", "olympia:olive_leaves"], "result": {"id": "olympia:corinthian_column", "count": 1}})
    write(rec / "greek_brazier.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": ["C C", "BCB", "BBB"],
          "key": {"C": "minecraft:copper_ingot", "B": "olympia:marble_bricks"}, "result": {"id": "olympia:greek_brazier", "count": 1}})
    write(rec / "amphora.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": ["T T", "T T", "TTT"],
          "key": {"T": "minecraft:terracotta"}, "result": {"id": "olympia:amphora", "count": 2}})
    for god, ing in (("zeus", "minecraft:lightning_rod"), ("athena", "minecraft:book"), ("poseidon", "minecraft:prismarine_shard"), ("hermes", "minecraft:feather")):
        write(rec / f"{god}_altar.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": [" X ", "PPP", "PPP"],
              "key": {"X": ing, "P": "olympia:polished_marble"}, "result": {"id": f"olympia:{god}_altar", "count": 1}})
    write(rec / "ambrosia.json", {"type": "minecraft:crafting_shapeless", "category": "food", "ingredients": [
        "olympia:sacred_olive", "minecraft:honey_bottle", "minecraft:gold_nugget"], "result": {"id": "olympia:ambrosia", "count": 1}})
    tag = D / "minecraft/tags/block"
    write(tag / "mineable/pickaxe.json", {"replace": False, "values": [f"olympia:{n}" for n in STONES + STAIRS + SLABS + COLUMNS + ["greek_brazier", "amphora"] + [f"{g}_altar" for g in GODS]]})
    write(tag / "mineable/axe.json", {"replace": False, "values": ["olympia:olive_log"]})
    write(tag / "mineable/hoe.json", {"replace": False, "values": ["olympia:olive_leaves"]})
    write(tag / "leaves.json", {"replace": False, "values": ["olympia:olive_leaves"]})
    write(tag / "logs.json", {"replace": False, "values": ["olympia:olive_log"]})
    write(tag / "logs_that_burn.json", {"replace": False, "values": ["olympia:olive_log"]})
    write(tag / "stairs.json", {"replace": False, "values": [f"olympia:{n}" for n in STAIRS]})
    write(tag / "slabs.json", {"replace": False, "values": [f"olympia:{n}" for n in SLABS]})
    write(tag / "small_flowers.json", {"replace": False, "values": ["olympia:laurel"]})
    for name, (spacing, sep, salt, biomes, start, spawns, adapt) in STRUCTS.items():
        write(K / "worldgen/structure" / f"{name}.json", {
            "type": "minecraft:jigsaw", "biomes": f"#olympia:has_structure/{name}", "step": "surface_structures", "spawn_overrides": spawns,
            "terrain_adaptation": adapt, "start_pool": f"olympia:{name}", "size": 1, "start_height": {"absolute": start},
            "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 80 if name == "labyrinth" else 40, "use_expansion_hack": False})
        write(K / "worldgen/template_pool" / f"{name}.json", {"fallback": "minecraft:empty", "elements": [
            {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": f"olympia:{name}_{i}",
                                      "processors": "minecraft:empty", "projection": "rigid"}} for i in range(VARIANTS[name])]})
        write(K / "worldgen/structure_set" / f"{name}.json", {"structures": [{"structure": f"olympia:{name}", "weight": 1}],
              "placement": {"type": "minecraft:random_spread", "spacing": spacing, "separation": sep, "salt": salt}})
        write(K / "tags/worldgen/biome/has_structure" / f"{name}.json", {"values": biomes})

    def adv(name, parent, icon, title, desc, trigger, conditions, frame="task", root=False):
        disp = {"icon": {"id": icon}, "title": {"text": title}, "description": {"text": desc}, "frame": frame,
                "show_toast": not root, "announce_to_chat": not root, "hidden": False}
        if root:
            disp["background"] = "minecraft:textures/gui/advancements/backgrounds/stone.png"
        d = {"display": disp, "criteria": {"c": {"trigger": trigger, "conditions": conditions}}}
        if parent:
            d["parent"] = f"olympia:{parent}"
        write(K / "advancement" / f"{name}.json", d)

    def loc(s):
        return {"player": [{"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"location": {"structures": f"olympia:{s}"}}}]}

    def kind(t):
        return {"entity": [{"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"type": f"olympia:{t}"}}]}

    def have(i):
        return {"items": [{"items": i}]}
    adv("root", None, "olympia:white_marble", "Olympia", "Age of the gods.", "minecraft:tick", {}, root=True)
    adv("greek_ruin", "root", "olympia:cracked_marble", "What the Years Left", "Find a Greek ruin.", "minecraft:location", loc("greek_ruin"))
    adv("olive_grove", "root", "olympia:olive_log", "Silver Leaves", "Find an olive grove.", "minecraft:location", loc("olive_grove"))
    adv("hermes_shrine", "olive_grove", "olympia:hermes_altar", "A God by the Road", "Find a shrine of Hermes.", "minecraft:location", loc("hermes_shrine"))
    adv("temple_of_zeus", "greek_ruin", "olympia:zeus_altar", "The King's House", "Find the Temple of Zeus.", "minecraft:location", loc("temple_of_zeus"))
    adv("temple_of_athena", "greek_ruin", "olympia:athena_altar", "The Grey-Eyed's House", "Find the Temple of Athena.", "minecraft:location", loc("temple_of_athena"))
    adv("temple_of_poseidon", "greek_ruin", "olympia:poseidon_altar", "The Earth-Shaker's House", "Find the Temple of Poseidon on a shore.", "minecraft:location", loc("temple_of_poseidon"))
    adv("labyrinth", "root", "olympia:thread_of_ariadne", "The Way Down", "Enter the Labyrinth.", "minecraft:location", loc("labyrinth"), "goal")
    adv("hoplite", "greek_ruin", "minecraft:iron_sword", "Bronze Against Bronze", "Defeat a hoplite.", "minecraft:player_killed_entity", kind("hoplite"))
    adv("cyclops", "temple_of_zeus", "olympia:cyclops_bloodstone", "One Eye, Many Bruises", "Defeat a cyclops.", "minecraft:player_killed_entity", kind("cyclops"), "goal")
    adv("minotaur", "labyrinth", "olympia:minotaur_horn", "The Bull of Minos", "Defeat the Minotaur.", "minecraft:player_killed_entity", kind("minotaur"), "challenge")
    adv("thread", "labyrinth", "olympia:thread_of_ariadne", "A Way Back", "Hold the Thread of Ariadne.", "minecraft:inventory_changed", have("olympia:thread_of_ariadne"))
    adv("thunderbolt", "temple_of_zeus", "olympia:thunderbolt", "The Sky's Weapon", "Hold the Thunderbolt of Zeus.", "minecraft:inventory_changed", have("olympia:thunderbolt"), "challenge")
    adv("ambrosia", "olive_grove", "olympia:ambrosia", "Food of the Gods", "Hold ambrosia.", "minecraft:inventory_changed", have("olympia:ambrosia"))
    print("olympia data written")


if __name__ == "__main__":
    main()
