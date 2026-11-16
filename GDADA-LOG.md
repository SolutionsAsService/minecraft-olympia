# GDADA log: Olympia slice one (2026-11-16)

**Run:** Mod run type, Quick run (one person's brief, built in one session), single-voice. **No critic panel was seated, no WHOLE
round was run, and the stop test (S1 to S7) was not run as a formal test.** The site was built with DADA's rules (palette from the
subject with a measured gate, first screen complete at 1280x800 and 375x812, a Status box on every page) but without a DADA panel.
Mode and criterion: Player-first (the mod serves players and builders); the Minotaur must be found and fought, not admired.

## Traversal Plan
Seed: Salen and Zimmerman (inner necessity: every rule earns its place), Meier (interesting decisions: which god, which item, turn back
by the thread or go on), Swink (feel: a boss that charges and slams). Dotted counterpoint: the master prompt's breadth against its own
rule that "a functional Minotaur encounter is more valuable than ten unfinished monsters".

## Frontier
| Candidate | Status |
|---|---|
| Marble blocks with stairs, slabs, columns | TAKEN (M1) |
| Gods: favor, offerings, blessings, altars (4 of 12) | TAKEN (M2); the other eight DEFERRED (Phase 4) |
| Relics: Thunderbolt (favor-gated), Thread of Ariadne, ambrosia, potions | TAKEN (M3) |
| Structures: three temples, shrine, grove, ruin | TAKEN (M4) |
| Labyrinth with a Minotaur that hunts | TAKEN (M5) |
| Creatures: hoplite, cyclops (zombie model, skins) | TAKEN (M6); Pegasus, centaurs, harpies, Medusa, Hydra, Cerberus DEFERRED (Phase 3) |
| Site and mod pack | TAKEN (M7) |
| Custom biomes, Olympus, Atlantis, Underworld, sailing, prophecy, cities and NPCs | DEFERRED (Phases 1, 2, 5 to 8) |
| Multiple labyrinth floors, traps, puzzles | DEFERRED |
| Hand-playtest and balance of the Minotaur | OPEN: needs the owner |

## Decision Records (short)
- **M5 Labyrinth.** Options: one-wide corridors (a classic maze, small) against three-wide (bigger, the boss can move). Chose three-wide
  after measuring that the Minotaur circled the hall and never reached a player 14 blocks away (`mod` L16). Before: unreached in 60 s;
  after: reached a player a 163-block walk away in 58 s.
- **M3 Thunderbolt.** Gated by favor stage so the god system matters: refused at Unknown Mortal, struck at Favored (tested).
- **M1 Palette for the site.** From the brief's colours; the gate passed at delta-E 32.1 (structures against the gold signal).

## Measurements at the final state
lint ok; build ok; server loads, no data errors; `/locate` found 6 of 7 structures (Poseidon needs a beach); site: wall bottom 781 of
800 (desktop) and 752 of 812 (phone), no sideways scroll on any of 8 pages at either size; computed headline font "Iowan Old Style".
Claim audit: measured or tested claims are labelled with their rung on every page; everything not hand-played is listed as not tested.

## Not done / looked at only
No panel; no `check_floor.py` (needs a tool not installed here); no real phone; altar clicks, ambrosia, brewing, hoplite and cyclops
fights, a real boss fight, multiplayer and restarts are untested; the Temple of Poseidon was placed by command and not seen generating on a
beach; the labyrinth's natural generation in a normal world was not checked; the olive-grove photograph is distant.

## Lessons written
`gdada` mod-lessons L16 to L19; shadw-modding LESSONS and playtest (`--deep`, tutorial toast off); `shadwlib` structure entities.
