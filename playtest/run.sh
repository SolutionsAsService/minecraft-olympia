#!/bin/sh
# Rebuild the world and take every photograph. Run from the mod root: sh playtest/run.sh
# Needs Java, Gradle, Xvfb, ImageMagick. The deep flat world gives the labyrinth room underground (ground air at y=-20).
SM=../shadw-modding/tools/shadw-mod
MOD=$(pwd)
gradle build --offline -q || exit 1
$SM playtest $MOD down
$SM playtest $MOD up --deep 40 || exit 1
$SM playtest $MOD client || exit 1
for t in "temple_of_zeus_0 0 -300" "temple_of_zeus_1 40 -300" "temple_of_athena_0 80 -300" "temple_of_poseidon_0 120 -300" \
         "hermes_shrine_0 160 -300" "olive_grove_0 190 -300" "greek_ruin_0 235 -300"; do
  set -- $t
  $SM playtest $MOD place olympia:$1 $2 -21 $3
done
for s in structures zeus-interior blocks creatures relics; do
  $SM playtest $MOD shoot playtest/$s.json
done
# the labyrinth last: its Minotaur has a boss bar that shows from far away, and would be in every earlier photograph
$SM playtest $MOD place olympia:labyrinth_2 300 -34 -200
$SM playtest $MOD shoot playtest/labyrinth.json
