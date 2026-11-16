# Olympia

Age of the Gods: Greek mythology for Minecraft Java Edition (Fabric, 1.21.4). Olympia is the sibling of the
[Asgard](https://github.com/SolutionsAsService/minecraft-asgard) and [Khemet](https://github.com/SolutionsAsService/minecraft-khemet)
mods: the same stack, the same design philosophy (shrines, offerings, legendary artifacts, creatures, ancient structures,
mythology-based progression) and a different mythology. The master design is [`master-prompt.md`](master-prompt.md); what this
repository builds, and what it defers, is in [`VISION.md`](VISION.md). The site is generated from the mod's own files (`_src/`).

## Slice one

A thread through every pillar the master design names, small but whole:

- **Blocks**: twelve marble and tile stones (white, polished, weathered, cracked, black, pink, veined and golden marble, marble
  bricks and tiles, a Greek-key mosaic, roof tile), stairs and slabs for four of them, three column orders (Doric, Ionic,
  Corinthian), an amphora, the Greek fire brazier, laurel, olive logs and leaves. Stonecutter and crafting recipes for all.
- **Four gods**, Zeus, Athena, Poseidon and Hermes, each with an **altar**. Offerings raise your **divine favor** with that god
  through five stages (Unknown Mortal, Recognized, Favored, Blessed, Champion of Olympus); each stage from Favored adds blessings.
  `/olympia favor` shows where you stand.
- **The Thunderbolt of Zeus** (lightning where you look, only once Zeus has named you Favored) and the **Thread of Ariadne** (tie it,
  then it points the way back), **ambrosia**, and **five divine potions** with their ingredients.
- **Structures**: temples of Zeus, Athena and Poseidon, a roadside shrine of Hermes, olive groves, Greek ruins, each with a chest.
- **The Labyrinth**: a seeded maze of three-wide corridors under a marble pavilion, three variants, treasure at the dead ends,
  and the **Minotaur** in the hall at its centre. It hunts through the maze, charges, slams, enrages below half health, and has a boss bar.
- **Creatures**: hoplite, cyclops, Minotaur (the zombie model with painted skins).

Not in this slice (see the roadmap in the master design and `VISION.md`): custom biomes, Mount Olympus, Atlantis, the Underworld,
sailing, prophecy, the other eight gods, the other creatures and bosses, cities and NPCs.

## What is tested, and how

Rendered in a client; loaded on a Fabric 1.21.4 server with no data errors; generated (six of the seven structures found by `/locate`
in a flat plains world; the Poseidon temple needs a beach); logic-tested over RCON through the same code the items and altars use
(`/olympia offer`, `setfavor`, `use`, `thread`); the Minotaur watched hunting through the maze. **Not hand-played**: altar clicks,
ambrosia, brewing, fighting a hoplite or cyclops, the boss fight with real gear, multiplayer, restarts. The site says the same.

## Build

```
git clone https://github.com/SolutionsAsService/minecraft-olympia
cd minecraft-olympia
gradle build        # the jar is in build/libs/
```

Needs Java 21, Gradle 8 (no wrapper in the repository), Fabric Loader 0.16+ and Fabric API. The mod is also in the **Greek Pantheon**
mod pack in [shadw-modding](https://github.com/SolutionsAsService/shadw-modding).

## Regenerate

Textures, models, structures, loot, recipes, worldgen and the site are generated. Edit the script, not the output:

```
python3 tools/gen_content.py && python3 tools/gen_assets.py   # textures, models, lang
python3 tools/gen_structures.py                               # the .nbt structure files
python3 tools/gen_data.py                                     # loot, recipes, tags, worldgen, advancements
python3 _src/build_site.py                                    # the site
sh playtest/run.sh                                            # rebuild the test world and take every photograph
```

## Credit

All work in this repository is credited only to SolutionsAsService.
