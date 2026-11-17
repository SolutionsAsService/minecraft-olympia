#!/usr/bin/env python3
"""Compose the site's creature pictures from playtest/models/<id>-*.png (needs ImageMagick).

    python3 tools/creature_shots.py     site/img/shots/<id>-full.png (three-quarter), <id>.png (close up, from the face-side photograph), creatures.png (all)

The cameras are aimed and set by tools/model_sheet.py so the creature is centred and sits mid-frame; a boss's frame loses its top 40
pixels (the boss bar) and is trimmed back to 16:9. Nothing else is cropped, so there are no per-creature crop boxes.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "playtest/models"
OUT = ROOT / "site/img/shots"
ORDER = ["hoplite", "satyr", "gorgon", "cyclops", "minotaur", "pegasus"]
BOSSES = {"minotaur"}


def run(*a):
    subprocess.run(a, check=True)


def frame(src, dst, size="854x480", boss=False):
    if boss:
        run("convert", str(src), "-crop", "782x440+36+40", "+repage", "-filter", "point", "-resize", size + "!", str(dst))
    else:
        run("convert", str(src), "-filter", "point", "-resize", size + "!", str(dst))


def main():
    tiles = []
    for i in ORDER:
        frame(SRC / f"{i}-three-quarter.png", OUT / f"{i}-full.png", boss=i in BOSSES)
        frame(SRC / f"{i}-face-side.png", OUT / f"{i}.png")
        t = OUT / f".tile-{i}.png"
        run("convert", str(OUT / f"{i}-full.png"), "-crop", "570x480+142+0", "+repage", "-filter", "point", "-resize", "285x240!", str(t))
        tiles.append(str(t))
    run("montage", *tiles, "-tile", "3x2", "-geometry", "285x240+0+0", "-background", "#10141c", str(OUT / "creatures.png"))
    for t in tiles:
        Path(t).unlink()
    print("creature pictures written")


if __name__ == "__main__":
    main()
