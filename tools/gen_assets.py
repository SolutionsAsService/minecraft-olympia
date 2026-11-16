#!/usr/bin/env python3
"""Generate the language file, item models, item definitions and item sprites from potions.json.

Run from the mod root after editing potions.json:

    python3 tools/gen_assets.py

Everything written here is derived; edit potions.json, not the generated files.
Stdlib only.
"""

import json
import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD_ID = "olympia"
ASSETS = ROOT / "src/main/resources/assets" / MOD_ID
DATA = json.loads((ASSETS / "potions.json").read_text(encoding="utf-8"))

EFFECT_NAMES = {
    "minecraft:speed": "Speed", "minecraft:slowness": "Slowness", "minecraft:haste": "Haste",
    "minecraft:mining_fatigue": "Mining Fatigue", "minecraft:strength": "Strength",
    "minecraft:jump_boost": "Jump Boost", "minecraft:regeneration": "Regeneration",
    "minecraft:resistance": "Resistance", "minecraft:fire_resistance": "Fire Resistance",
    "minecraft:water_breathing": "Water Breathing", "minecraft:invisibility": "Invisibility",
    "minecraft:blindness": "Blindness", "minecraft:night_vision": "Night Vision",
    "minecraft:hunger": "Hunger", "minecraft:weakness": "Weakness", "minecraft:poison": "Poison",
    "minecraft:wither": "Wither", "minecraft:health_boost": "Health Boost",
    "minecraft:absorption": "Absorption", "minecraft:glowing": "Glowing",
    "minecraft:levitation": "Levitation", "minecraft:luck": "Luck", "minecraft:unluck": "Unluck",
    "minecraft:slow_falling": "Slow Falling", "minecraft:conduit_power": "Conduit Power",
    "minecraft:dolphins_grace": "Dolphin's Grace", "minecraft:darkness": "Darkness", "minecraft:saturation": "Saturation",
}

REALM_HUE = {r["id"]: r["hue"] for r in DATA["realms"]}


def lang():
    out = {}
    for realm in DATA["realms"]:
        out[f"pantheon.realm.{realm['id']}"] = realm["name"]
    for p in DATA["potions"]:
        ing_key = f"item.{MOD_ID}.{p['ingredient']}"
        out[ing_key] = p["ingredient"].replace("_", " ").title()
        out[f"item.{MOD_ID}.{p['ingredient']}.lore"] = p["lore"]
        out[f"item.minecraft.potion.effect.{p['id']}"] = f"Potion of {p['name']}"
        out[f"item.minecraft.splash_potion.effect.{p['id']}"] = f"Splash {p['name']}"
        out[f"item.minecraft.lingering_potion.effect.{p['id']}"] = f"Lingering {p['name']}"
    return out


def write_lang():
    path = ASSETS / "lang/en_us.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = lang()
    extra = Path(__file__).resolve().parent / "content_lang.json"   # written by tools/gen_content.py
    if extra.exists():
        entries.update(json.loads(extra.read_text(encoding="utf-8")))
    mobs = Path(__file__).resolve().parent / "mobs_lang.json"   # written by `shadw-mod mob gen`
    if mobs.exists():
        entries.update(json.loads(mobs.read_text(encoding="utf-8")))
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_models():
    for p in DATA["potions"]:
        path = ASSETS / "models/item" / f"{p['ingredient']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        model = {"parent": "minecraft:item/generated",
                 "textures": {"layer0": f"{MOD_ID}:item/{p['ingredient']}"}}
        path.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")


def write_item_definitions():
    """Minecraft 1.21.4 draws an item from assets/<ns>/items/<id>.json, which names the model.
    A model file alone is not enough: the item renders as the purple-and-black missing model."""
    for p in DATA["potions"]:
        path = ASSETS / "items" / f"{p['ingredient']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        definition = {"model": {"type": "minecraft:model", "model": f"{MOD_ID}:item/{p['ingredient']}"}}
        path.write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def sprite(index, colour):
    """A 16x16 sprite: one of six shapes, drawn in the realm's colour with a dark outline."""
    shape = index % 6
    r, g, b = colour
    dark = (max(0, r // 3), max(0, g // 3), max(0, b // 3), 255)
    light = (min(255, r + 70), min(255, g + 70), min(255, b + 70), 255)
    body = (r, g, b, 255)
    px = []
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            d = math.hypot(dx, dy)
            c = (0, 0, 0, 0)
            if shape == 0:      # drop
                if y > 3 and abs(dx) < 4.5 * (1 - (y - 9) / 7.5 if y > 9 else 1) and y < 14:
                    c = body
                if d < 2.2 and y < 9:
                    c = light
            elif shape == 1:    # leaf
                if (dx / 6) ** 2 + (dy / 3.2) ** 2 <= 1:
                    c = body
                if abs(dy - dx * 0.3) < 0.6 and abs(dx) < 5:
                    c = dark
            elif shape == 2:    # star
                if d < 3.2 or (abs(dx) < 1 and abs(dy) < 6.5) or (abs(dy) < 1 and abs(dx) < 6.5):
                    c = body
                if d < 1.2:
                    c = light
            elif shape == 3:    # shard
                if abs(dx) * 0.9 + abs(dy) * 0.6 < 5.5:
                    c = body
                if abs(dx) < 0.8 and dy < -1:
                    c = light
            elif shape == 4:    # orb
                if d <= 6.2:
                    c = body if d > 3 else light
            else:               # flask
                if abs(dx) < 2 and 2 < y < 5:
                    c = dark
                if abs(dx) < 4 and 5 <= y <= 13 and (dx ** 2) / 16 + ((y - 9) ** 2) / 20 < 1:
                    c = body
            if c[3] and d > 7.4:
                c = (0, 0, 0, 0)
            px.append(c)
    return px


def write_png(path, width, height, pixels):
    raw = b"".join(b"\x00" + bytes(c for x in range(width) for c in pixels[y * width + x])
                   for y in range(height))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    data = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_sprites():
    for index, p in enumerate(DATA["potions"]):
        colour = hex_rgb(p.get("hue") or REALM_HUE[p["realm"]])  # a potion may set its own sprite colour
        write_png(ASSETS / "textures/item" / f"{p['ingredient']}.png", 16, 16, sprite(index, colour))


if __name__ == "__main__":
    write_lang()
    write_models()
    write_item_definitions()
    write_sprites()
    print(f"wrote lang, {len(DATA['potions'])} models, item definitions and sprites for {MOD_ID}")
