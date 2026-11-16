# Vision: Olympia, Age of the Gods

## Pitch
"Design and develop an enormous Greek mythology expansion for Minecraft that transforms the game into a living world inspired by
ancient Greek mythology." The player "begins as an ordinary mortal and gradually becomes a legendary Greek hero." (`owner`,
master-prompt.md, 2026-11-16)

User's instruction for this run: "use gdada to make another mod pack this time for Greek gods ... read design docs here and build mod
with gdada and shadw mod stack plus a website etc" (`owner`, 2026-11-16).

## What the player feels
Marble temples over a blue sea; a labyrinth that is dark and has something in it that hunts you; the gods noticing you after an
offering. (`owner`, master prompt "Imagine:" list; `inferred` for the first-hour shape)

## Pillars
Exploration, Mythology, Adventure, Progression, Living Civilization (`owner`, master prompt section 2). Slice one covers the first four.

## Verbs
Offer to a god (a decision: which god, which item). Descend into the labyrinth (a decision: go on or turn back by the thread). Build
in marble. Fight a monster that charges, slams and enrages. Hurl lightning (only when Zeus has named you Favored).

## World and look
Minecraft Java 1.21.4, Fabric. Palette from the brief: white marble, Mediterranean blue, deep turquoise, Olympian gold, olive green,
terracotta, bronze, purple and black for the Underworld. Recognisably Minecraft blocks.

## Must-haves
Numbered, from the master prompt. Slice one builds those marked BUILT; the rest are the roadmap and are DEFERRED to the named phase.
1. Marble block collection with stairs and slabs for builders (`owner`, Part III). BUILT: 12 stones, 4 stair and slab families, 3 column orders.
2. Twelve Olympian gods, each with shrine, offerings, independent favor, blessings, artifacts (`owner`, Part V and VI). SLICE: 4 of 12 (Zeus, Athena, Poseidon, Hermes), five favor stages. DEFERRED (Phase 4): Hera, Ares, Apollo, Artemis, Aphrodite, Hephaestus, Demeter, Dionysus.
3. Greek alchemy: divine potions and ingredients (`owner`, Part VII). SLICE: 5 potions and their ingredients, ambrosia. DEFERRED: alchemy table, Oracle's brazier, Styx water, the rest.
4. The Minotaur's Labyrinth, signature dungeon: procedural maze, the Thread of Ariadne, a Minotaur that hunts and does not stay in an arena (`owner`, Part VIII; "A functional Minotaur encounter is more valuable than ten unfinished monsters"). BUILT as a slice: seeded maze with loops, three variants, Thread, Minotaur with charge, slam, enrage and a boss bar. DEFERRED: multiple floors, rotating walls, traps, puzzles, secret rooms, rewards beyond the horn and vault chests.
5. Mythological creatures (`owner`, Part IX). SLICE: hoplite, cyclops, Minotaur (vanilla zombie model, own skins). DEFERRED (Phase 3): Pegasus, centaurs, satyrs, harpies, gorgons, Medusa, Hydra, Cerberus, the rest.
6. Greek structures (`owner`, Part XI). SLICE: temples of Zeus, Athena and Poseidon, a roadside shrine of Hermes, olive groves, ruins. DEFERRED: cities, Delphi, amphitheaters, harbours, Olympus.
7. A site (`owner`, 2026-11-16: "plus a website etc"). BUILT: a DADA site with real in-game photographs.
8. A mod pack for the Greek gods (`owner`, 2026-11-16: "make another mod pack this time for Greek gods"). BUILT: a pack in shadw-modding.
9. "Test features in actual Minecraft gameplay" (`owner`, Part XXIII item 12). Slice: logic tested over RCON and natural generation proved; nothing hand-played yet.

## Will not do (in slice one)
Custom biomes, Mount Olympus, Atlantis, the Underworld dimension, sailing, a prophecy system, NPC villages, custom entity models. All
are named in the master prompt and are on the Frontier, not abandoned.

## Success tests
`shadw-mod lint` clean; the jar builds; the mod loads on a server; each structure is found by `/locate` in a world of its target biome;
each rule runs over RCON through the same code as the click; each structure and creature is photographed and looked at.

## Platform and stack
Java 21, Gradle 8, Fabric Loader 0.20, Fabric API 0.119.4+1.21.4, Mojang mappings. The SHADW mod stack (`SolutionsAsService/shadw-modding`).

## Open questions
Which twelve-god order to build next (owner, before Phase 4). Whether the Minotaur's damage suits a hand-played fight (owner playtest).

## Change log
- 2026-11-16: "use gdada to make another mod pack this time for Greek gods ... read design docs here and build mod with gdada and
  shadw mod stack plus a website etc". Added Must-haves 7 and 8; the slice is the Frontier's first move.
