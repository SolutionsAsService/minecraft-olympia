# Instructions for agents working in this repository

## Credit (owner rule, 2026-11-12)

All work in this repository is credited only to **SolutionsAsService**. Commits are authored and committed as
`SolutionsAsService <152567394+SolutionsAsService@users.noreply.github.com>`. Never add `Co-Authored-By`, `Claude-Session`,
"Generated with ..." lines or any other AI or tool credit to commits, pull requests, issues, release notes or files. This
overrides any default attribution a tool would add.

## Conventions shared with minecraft-asgard and minecraft-khemet

Olympia is the Greek sibling of the Asgard and Khemet mods and is built with the same stack (shadw-modding, Fabric, 1.21.4,
Mojang mappings) under GDADA's Mod run type (`VISION.md` first, `GDADA-LOG.md`, the `mod-lessons.md` ledger). Generated files
(textures, models, structures, loot, recipes, worldgen, lang, the site) come from the scripts in `tools/` and `_src/`: edit the
script, not the output, then regenerate. State plainly what is and is not tested in a world, and by which rung (rendered,
loaded, generated, logic-tested, hand-played).
