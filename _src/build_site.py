#!/usr/bin/env python3
"""Build the Olympia site (site/) from the mod's own files.

Every figure, table row and colour check on the site is computed here from the mod's data: block states and language entries,
potions.json, content.json (gods, favor, relics, creatures), the structure NBT and worldgen JSON, and the loot tables. In-game
photographs are read from site/img/shots/ and a page never refers to a capture that does not exist.

    python3 _src/build_site.py

The output (site/) is committed. The deploy serves it as static files and never runs this script. The build fails when the
palette or the Shadw/Vercel deploy files do not hold (see check_palette and check_deploy).
"""

import html
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
SITE_URL = "https://minecraft-olympia.shadw.app"
ASSETS = REPO / "src/main/resources/assets/olympia"
DATA = REPO / "src/main/resources/data/olympia"
JAVA = REPO / "src/main/java/dev/shadw/olympia"
sys.path.insert(0, str(REPO / "tools"))
from shadwlib import nbt  # noqa: E402

# ---------- palette: the colours of the brief ----------
# "White marble. Mediterranean blue. Deep ocean turquoise. Olympian gold. Olive green. Terracotta. Bronze. Purple and black for the
# Underworld." The page ground is the Underworld (purple-black); Olympian gold is reserved for the argument (links, buttons); marble
# white is the text. Each topic category has its own hue from the rest; bronze is left out because it sits too near the gold.
GROUND = "#13101A"        # the Underworld
CARD = "#1E1A28"
TEXT = "#F1EEE6"          # white marble
MUTED = "#B9B4C4"
SIGNAL = "#E6B83C"        # Olympian gold, the argument
HUES = {                  # category -> (hue, the colour of the brief)
    "blocks": ("#E2845C", "terracotta"),
    "gods": ("#5B9BE0", "Mediterranean blue"),
    "structures": ("#A9BC5A", "olive green"),
    "labyrinth": ("#B58CE8", "Underworld purple"),
    "creatures": ("#36C2B4", "deep ocean turquoise"),
    "relics": ("#E58BB0", "pink marble"),
}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(rgb(a), rgb(b)))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    r, g, b = rgb(h)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def lab(h):
    r, g, b = (_lin(v) for v in rgb(h))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(a, b):
    return math.dist(lab(a), lab(b))


def check_palette():
    """Measured, not asserted: the build fails below delta-E 30 between any two hues, below 3:1 for marks, or below 4.5:1 for text."""
    hues = {k: v[0] for k, v in HUES.items()}
    hues["signal"] = SIGNAL
    pairs = [(a, b) for i, a in enumerate(hues) for b in list(hues)[i + 1:]]
    worst = min(pairs, key=lambda p: delta_e(hues[p[0]], hues[p[1]]))
    de = delta_e(hues[worst[0]], hues[worst[1]])
    errors = []
    if de < 30:
        errors.append(f"hues {worst[0]} / {worst[1]} are only delta-E {de:.1f} apart (need 30)")
    for k, h in hues.items():
        band = mix(h, GROUND, 0.82)       # the dark panel band the hue sits on
        for ground, what in ((GROUND, "page ground"), (CARD, "card"), (band, "panel band")):
            c = contrast(h, ground)
            if c < 4.5:
                errors.append(f"{k} text on {what} is {c:.2f}:1 (need 4.5)")
    for what, fg, bg in (("body text", TEXT, GROUND), ("body text on card", TEXT, CARD), ("muted text", MUTED, GROUND), ("muted on card", MUTED, CARD)):
        if contrast(fg, bg) < 4.5:
            errors.append(f"{what} is {contrast(fg, bg):.2f}:1 (need 4.5)")
    if errors:
        raise SystemExit("palette check failed:\n  " + "\n  ".join(errors))
    return {"min_delta_e": round(de, 1), "min_pair": f"{worst[0]} / {worst[1]}",
            "min_contrast": round(min(contrast(h, band_) for h in hues.values() for band_ in (GROUND, CARD)), 2)}


def check_deploy():
    """The Shadw/Vercel guarantee, checked rather than remembered."""
    need = {}
    for rel, expect in (("vercel.json", "site"), ("site/vercel.json", ".")):
        d = json.loads((REPO / rel).read_text())
        for k, v in (("framework", None), ("installCommand", ""), ("buildCommand", ""), ("outputDirectory", expect), ("cleanUrls", True), ("fluid", True)):
            if d.get(k, "MISSING") != v:
                need[f"{rel}: {k}"] = f"expected {v!r}, found {d.get(k, 'MISSING')!r}"
    f = json.loads((REPO / "fluid.json").read_text())
    if f.get("project") != "minecraft-olympia" or f.get("static_dir") != "site" or f.get("routes") != [{"pattern": "/", "target": "static"}]:
        need["fluid.json"] = "needs project minecraft-olympia, static_dir site, and routes [{pattern: /, target: static}] only"
    if "site/index.html" not in (REPO / "index.html").read_text():
        need["index.html"] = "the root redirect must point at site/index.html"
    ignore = (REPO / ".vercelignore").read_text().split()
    if "/_src/" not in ignore or any(not e.startswith("/") for e in ignore):
        need[".vercelignore"] = "entries must be anchored at the root (/_src/)"
    if need:
        raise SystemExit("deploy files check failed:\n  " + "\n  ".join(f"{k}: {v}" for k, v in need.items()))




# ---------- reading the mod ----------

def jread(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def esc(v):
    return html.escape(str(v), quote=True)


def label(rid):
    return rid.split(":")[-1].replace("_", " ").title()


def dur(s):
    return f"{s // 60}:{s % 60:02d}"


def roman(n):
    return ["", "I", "II", "III", "IV", "V"][n]


def shot(name):
    return f"/img/shots/{name}.png" if (SITE / "img/shots" / f"{name}.png").exists() else None


def nbt_size(name):
    root = nbt.loads((DATA / "structure" / f"{name}.nbt").read_bytes())
    return tuple(root["size"][1][1]), len(root["blocks"][1][1])


def variants(slug):
    return len(list((DATA / "structure").glob(f"{slug}_*.nbt")))


def chest_items(slug):
    d = jread(DATA / "loot_table/chests" / f"{slug}.json")
    out = []
    for pool in d["pools"]:
        for e in pool["entries"]:
            if e.get("type") == "minecraft:item":
                n = e["name"]
                if n == "minecraft:potion":
                    pid = e["functions"][0]["id"].split(":")[-1]
                    n = "Potion of " + next((p["name"] for p in POTIONS if p["id"] == pid), label(pid))
                else:
                    n = label(n)
                if n not in out:
                    out.append(n)
    return out


# ---------- page shell ----------

NAV = [("index.html", "Home", "home"), ("blocks.html", "Blocks", "blocks"), ("potions.html", "Potions", "potions"),
       ("gods.html", "Gods", "gods"), ("structures.html", "Structures", "structures"), ("creatures.html", "Creatures", "creatures"),
       ("relics.html", "Relics", "relics"), ("install.html", "Install", "install")]


def typo(markup):
    """Real apostrophes in prose; <pre> and <code> keep straight ones."""
    out = []
    for part in re.split(r"(<pre.*?</pre>|<code>.*?</code>|<style.*?</style>)", markup, flags=re.S):
        out.append(part if part.startswith(("<pre", "<code>", "<style")) else part.replace("&#x27;", "’").replace("'", "’"))
    return "".join(out)


def css():
    hv = "\n".join(f"  --{k}: {v[0]};" for k, v in HUES.items())
    return f""":root {{
  --ground: {GROUND}; --card: {CARD}; --text: {TEXT}; --muted: {MUTED}; --signal: {SIGNAL};
{hv}
  --hue: var(--signal);
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{ margin: 0; background: var(--ground); color: var(--text); font: 16px/1.55 "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif; }}
img {{ max-width: 100%; height: auto; }}
a {{ color: var(--signal); }}
a:focus-visible, .btn:focus-visible {{ outline: 3px solid var(--text); outline-offset: 3px; }}
.skip {{ position: absolute; left: 12px; top: -60px; background: var(--signal); color: #000; padding: 10px 14px; z-index: 9; }}
.skip:focus {{ top: 10px; }}
.skip:focus-visible {{ outline: 3px solid #000; outline-offset: 2px; }}
.serif, h1, h2, h3, .brand, .panel .name, .ladder b {{ font-family: var(--serif); }}
.frieze {{ height: 12px; background:
  linear-gradient(var(--signal), var(--signal)) 0 0 / 100% 2px no-repeat,
  linear-gradient(var(--signal), var(--signal)) 0 100% / 100% 2px no-repeat,
  repeating-linear-gradient(90deg, var(--signal) 0 6px, transparent 6px 12px) 0 50% / 100% 4px no-repeat; }}
.top {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 2px 14px; padding: 6px 16px; background: #0c0a08; }}
.brand {{ font-weight: 800; letter-spacing: .22em; color: var(--text); text-decoration: none; display: inline-flex; align-items: center; min-height: 44px; }}
.top nav {{ display: flex; flex-wrap: wrap; gap: 0 2px; }}
.top nav a {{ display: inline-flex; align-items: center; min-height: 44px; padding: 6px 10px; color: var(--text); text-decoration: none; font-size: 15px; }}
.top nav a[aria-current="page"] {{ border-bottom: 4px solid var(--signal); }}
@media (hover: hover) {{ .top nav a:hover {{ background: var(--card); }} }}
main {{ display: block; }}
.eyebrow {{ text-transform: uppercase; letter-spacing: .16em; font-size: 13px; color: var(--hue); margin: 0 0 4px; font-weight: 700; }}
h1 {{ font-size: clamp(30px, 6vw, 52px); line-height: 1.08; margin: 0 0 10px; letter-spacing: .06em; text-transform: uppercase; }}
h2 {{ font-size: 28px; margin: 34px 0 8px; line-height: 1.2; }}
h3 {{ font-size: 20px; margin: 0 0 4px; }}
.page {{ max-width: 980px; margin: 0 auto; padding: 26px 16px 56px; }}
.page p, .page li, .band p {{ max-width: 38em; text-wrap: pretty; }}
.lede {{ color: var(--muted); font-size: 18px; max-width: 34em; }}
.meta {{ color: var(--muted); font-size: 14px; max-width: 38em; }}
.page .rule {{ border-top: 4px solid var(--hue); margin: 4px 0 18px; width: 90px; }}
.btn {{ display: inline-flex; align-items: center; min-height: 44px; padding: 8px 20px; font-weight: 800; text-decoration: none; background: var(--signal); color: #000; border: 3px solid #000; }}
.btn-alt {{ background: var(--text); }}
.btn-quiet {{ background: transparent; color: var(--signal); border-color: var(--signal); }}
.action {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 0 0; }}
.shots {{ display: grid; grid-template-columns: 1fr; gap: 14px; margin: 14px 0; }}
.shot {{ margin: 0; }}
.shot img {{ display: block; width: 100%; border: 3px solid var(--hue); }}
.shot figcaption {{ color: var(--muted); font-size: 14px; margin-top: 6px; }}
@media (min-width: 760px) {{ .shots.two {{ grid-template-columns: 1fr 1fr; }} }}
table.data {{ width: 100%; border-collapse: collapse; background: var(--card); margin: 12px 0 8px; font-size: 15px; }}
table.data td, .ladder b {{ font-variant-numeric: lining-nums tabular-nums; }}
table.data th, table.data td {{ text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid #3a322a; overflow-wrap: anywhere; }}
table.data th {{ width: 8.5em; color: var(--hue); font-weight: 700; }}
.sr {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }}
.cards {{ display: grid; grid-template-columns: 1fr; gap: 10px; margin: 12px 0; padding: 0; list-style: none; }}
@media (min-width: 720px) {{ .cards {{ grid-template-columns: 1fr 1fr; }} }}
.card {{ display: flex; gap: 14px; align-items: flex-start; background: var(--card); border: 3px solid #000; border-left: 6px solid var(--hue); padding: 12px; }}
.card img.px {{ flex: none; width: 64px; height: 64px; image-rendering: pixelated; background: #000; padding: 4px; border: 2px solid #3a322a; }}
.card h3 {{ margin: 0; }} .card p {{ margin: 2px 0 0; font-size: 15px; color: var(--muted); }}
.wallnote {{ margin: 8px 0 0; font-size: 13px; }}
.gloss {{ max-width: 44em; }} .gloss dt {{ font-family: var(--serif); font-weight: 700; color: var(--signal); margin-top: 10px; }} .gloss dd {{ margin: 2px 0 0; color: var(--text); }}
.status {{ border: 3px solid var(--hue); background: var(--card); padding: 12px 16px; margin: 26px 0 0; }}
.status h2 {{ font-size: 20px; margin: 0 0 6px; }} .status p, .status li {{ font-size: 15px; max-width: 46em; }} .status ul {{ margin: 6px 0; padding-left: 20px; }}
.ladder {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin: 14px 0; padding: 0; list-style: none; max-width: 760px; }}
.ladder li {{ background: var(--card); border-top: 6px solid var(--gods); padding: 8px 8px 10px; text-align: center; }}
.ladder li:nth-child(2) {{ border-top-width: 10px; }} .ladder li:nth-child(3) {{ border-top-width: 14px; }} .ladder li:nth-child(4) {{ border-top-width: 18px; }} .ladder li:nth-child(5) {{ border-top-width: 22px; }}
.ladder b {{ display: block; font-size: 24px; }} .ladder span {{ font-size: 13px; color: var(--muted); }}
.sec {{ margin-top: 40px; scroll-margin-top: 12px; }}
/* the landing: a register wall of six photograph panels under a cartouche */
.wall {{ max-width: 1060px; margin: 0 auto; padding: 14px 14px 10px; }}
.cartouche {{ display: flex; flex-wrap: wrap; align-items: center; gap: 4px 24px; margin: 4px 0 14px; }}
.cartouche h1 {{ margin: 0; border: 3px solid var(--signal); border-radius: 999px; padding: 4px 30px 4px 26px; position: relative; font-size: clamp(30px, 5.4vw, 58px); }}
.cartouche .dot {{ display: none; }}
.cartouche .btn {{ margin-left: 4px; }}
.cartouche .sub {{ margin: 0; color: var(--muted); font-size: 16px; max-width: 28em; }}
.panels {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 0; padding: 0; list-style: none; }}
.panel {{ display: block; text-decoration: none; color: var(--text); background: color-mix(in srgb, var(--hue) 18%, var(--ground)); border: 3px solid var(--hue); height: 100%; }}
.panel .ph {{ display: block; width: 100%; aspect-ratio: 2 / 1; object-fit: cover; background: #000; }}
.panel .ph.art {{ display: flex; align-items: center; justify-content: center; gap: 14px; }}
.panel .ph.art img {{ width: 56px; height: 56px; image-rendering: pixelated; }}
.panel .pn {{ display: block; padding: 7px 10px 9px; }}
.panel .name {{ display: flex; align-items: center; gap: 8px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--hue); font-size: 15px; line-height: 1.15; }}
.panel .name img {{ width: 22px; height: 22px; image-rendering: pixelated; flex: none; }}
.panel .name::after {{ content: "\\2192"; margin-left: auto; color: var(--text); }}
.panel .fig {{ display: block; font-size: 14px; font-weight: 700; margin-top: 2px; }}
.panel .claim {{ display: none; font-size: 13px; color: var(--muted); margin-top: 1px; }}
@media (hover: hover) {{ .panel:hover {{ background: color-mix(in srgb, var(--hue) 30%, var(--ground)); }} }}
@media (min-width: 1100px) {{ .panel .ph {{ aspect-ratio: 7 / 4; }} }}
@media (min-width: 720px) {{ .panel .claim {{ display: block; }} .panel .name {{ font-size: 16px; }} }}
@media (max-width: 719px) {{ .cartouche .dot {{ display: inline; }} .panels {{ grid-template-columns: repeat(2, 1fr); gap: 8px; }} .cartouche {{ margin-bottom: 10px; }} .cartouche .sub {{ font-size: 15px; }} .cartouche .sub .more {{ display: none; }}
  .top nav a {{ font-size: 14px; padding: 6px 8px; }} .panel .ph {{ aspect-ratio: 5 / 2; }} .panel .name img {{ display: none; }} .panel .name {{ font-size: 13px; }} .panel .fig {{ font-size: 13px; }} .panel .pn {{ padding: 6px 8px 8px; }} }}
code, pre {{ font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 14px; overflow-wrap: anywhere; }}
pre {{ white-space: pre-wrap; background: var(--card); border-left: 4px solid var(--hue); padding: 10px 12px; margin: 10px 0; }}
.foot {{ border-top: 0; padding: 18px 16px 30px; color: var(--muted); font-size: 14px; max-width: 980px; margin: 0 auto; }}
.foot p {{ max-width: 46em; }} .foot a {{ display: inline-block; padding: 3px 0; }}
@media (max-width: 560px) {{ .ladder {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} .ladder span {{ overflow-wrap: anywhere; }} }}
@media (forced-colors: active) {{
  .btn, .btn-quiet {{ border: 2px solid ButtonText; }}
  .top nav a[aria-current="page"] {{ border-bottom: 4px solid Highlight; }}
  a:focus-visible, .btn:focus-visible {{ outline: 3px solid CanvasText; }}
  .panel {{ border: 3px solid CanvasText; }}
  .frieze {{ background: none; border-top: 2px solid CanvasText; border-bottom: 2px solid CanvasText; }}
}}
@media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior: smooth; }} }}
"""


def page(title, desc, body, active, path, hue=None, image="/img/og.png"):
    nav = "".join(f'<a href="/{h}"{" aria-current=\"page\"" if k == active else ""}>{t}</a>' for h, t, k in NAV)
    style = f' style="--hue:var(--{hue})"' if hue else ""
    return typo(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(SITE_URL + '/' + path)}">
<meta property="og:image" content="{SITE_URL}{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{GROUND}">
<link rel="icon" href="/img/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
</head>
<body{style}>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <a class="brand" href="/index.html">OLYMPIA</a>
  <nav aria-label="Primary">{nav}</nav>
</header>
<div class="frieze" aria-hidden="true"></div>
<main id="main" tabindex="-1">
{body}
</main>
<div class="frieze" aria-hidden="true"></div>
<footer class="foot">
  <p>A Minecraft mod for Fabric 1.21.4, the Greek sibling of <a href="https://github.com/SolutionsAsService/minecraft-asgard">Asgard</a> and <a href="https://github.com/SolutionsAsService/minecraft-khemet">Khemet</a>. Source: <a href="https://github.com/SolutionsAsService/minecraft-olympia">minecraft-olympia</a>. Built with <a href="https://github.com/SolutionsAsService/shadw-modding">shadw-modding</a>. Credit: SolutionsAsService. Dark theme only. English only.</p>
</footer>
</body>
</html>
""")


def status(tested, untested, hue=None):
    t = "".join(f"<li>{esc(x)}</li>" for x in tested)
    u = "".join(f"<li>{esc(x)}</li>" for x in untested)
    return (f'<section class="status"><h2>Status</h2><p><b>Seen in a running Minecraft 1.21.4 game:</b></p><ul>{t}</ul>'
            f'<p><b>Not yet tested:</b></p><ul>{u}</ul></section>')


def fig(name, caption, alt):
    return (f'<figure class="shot"><img src="{shot(name)}" alt="{esc(alt)}" width="854" height="480" loading="lazy"><figcaption>{esc(caption)}</figcaption></figure>'
            if shot(name) else "")


def sprite(rel, size=64, alt=""):
    return f'<img class="px" src="/img/tex/{rel}.png" width="{size}" height="{size}" alt="{esc(alt)}">'


RECIPE_TEXT = {
    "golden_pillar": "Crafting: three Golden Sandstone in a column make three pillars",
    "lotus_column": "Crafting: White Limestone above and below a Blue Lotus makes two columns",
    "sacred_brazier": "Crafting: Black Basalt across the bottom row and both sides of the middle row, Coal in the middle, a Gold Ingot in each top corner",
    "khopesh": "Crafting: Gold Ingots in a curve (two on top, one below on the right) over a Stick",
}


def recipe_text(name):
    p = DATA / "recipe" / f"{name}.json"
    if not p.exists():
        return ""
    d = jread(p)
    names = lambda i: label(i if isinstance(i, str) else i.get("item", ""))
    if d["type"] == "minecraft:stonecutting":
        return f"Stonecutter, from {names(d['ingredient'])}"
    if d["type"] == "minecraft:crafting_shapeless":
        from collections import Counter
        c = Counter(names(i) for i in d["ingredients"])
        return "Shapeless: " + ", ".join(f"{n} ×{k}" if k > 1 else n for n, k in c.items())
    if name in RECIPE_TEXT:
        return RECIPE_TEXT[name]
    key = {k: names(v) for k, v in d.get("key", {}).items()}
    return "Crafting: " + " / ".join("".join(r) for r in d["pattern"]).replace(" ", "·") + "; " + ", ".join(f"{k} = {v}" for k, v in key.items())




LANG = jread(ASSETS / "lang/en_us.json")
CONTENT = jread(ASSETS / "content.json")
POTIONS = jread(ASSETS / "potions.json")["potions"]
EFFECT = {"minecraft:strength": "Strength", "minecraft:fire_resistance": "Fire Resistance", "minecraft:regeneration": "Regeneration",
          "minecraft:speed": "Speed", "minecraft:slow_falling": "Slow Falling", "minecraft:luck": "Luck", "minecraft:resistance": "Resistance",
          "minecraft:night_vision": "Night Vision", "minecraft:absorption": "Absorption", "minecraft:water_breathing": "Water Breathing",
          "minecraft:dolphins_grace": "Dolphin's Grace", "minecraft:conduit_power": "Conduit Power", "minecraft:jump_boost": "Jump Boost",
          "minecraft:haste": "Haste"}


def fx(e):
    return f"{EFFECT.get(e['effect'], label(e['effect']))} {roman(e['amplifier'] + 1)} for {dur(e['seconds'])}"


def block_ids():
    return sorted(p.stem for p in (ASSETS / "blockstates").glob("*.json"))


def lang_block(n):
    return LANG["block.olympia." + n]


STAGES = CONTENT["favor"]["stages"]
STONES = ["white_marble", "polished_marble", "weathered_marble", "cracked_marble", "black_marble", "pink_marble", "veined_marble",
          "golden_marble", "marble_bricks", "marble_tiles", "greek_mosaic", "roof_tile"]
FAMILIES = ["white_marble", "polished_marble", "marble_bricks", "roof_tile"]
STONE_NOTES = {
    "white_marble": "The base stone: pale, with thin grey veins.", "polished_marble": "Smooth, with a worn edge and a sheen line, for floors and plinths.",
    "weathered_marble": "Grey-green with moss patches, for old walls.", "cracked_marble": "One long crack through white stone, for ruins.",
    "black_marble": "Near-black with gold veins, for the Underworld and the Minotaur's court.", "pink_marble": "Rose-white stone with pale veins.",
    "veined_marble": "White with strong blue-grey veining.", "golden_marble": "Warm gold stone with light veins.",
    "marble_bricks": "Offset marble bricks, like a real wall.", "marble_tiles": "A checker of white and grey tiles.",
    "greek_mosaic": "A Greek key (meander) band in blue and gold.", "roof_tile": "Overlapping terracotta tiles for pitched roofs.",
}
GODS = [("zeus", "temple_of_zeus", "temple-of-zeus"), ("athena", "temple_of_athena", "temple-of-athena"),
        ("poseidon", "temple_of_poseidon", "temple-of-poseidon"), ("hermes", "hermes_shrine", "hermes-shrine")]
PLACES = [
    ("temple_of_zeus", "Temple of Zeus", "A peristyle temple of Doric columns on three steps, a pitched roof of terracotta tiles, gold in the pediment, and inside the altar of Zeus between two braziers, with a chest. One variant is whole, one ruined.", ("temple-of-zeus", "temple-of-zeus-ruined")),
    ("temple_of_athena", "Temple of Athena", "The same plan in Ionic columns, with bookshelves along the cella wall and an owl perch of grey and white over the door.", ("temple-of-athena",)),
    ("temple_of_poseidon", "Temple of Poseidon", "Corinthian columns, prismarine trim and sea lanterns. Meant for shores: it is set to generate on beaches.", ("temple-of-poseidon",)),
    ("hermes_shrine", "Shrine of Hermes", "A small roadside herm: a squared pillar with a marble head and a gold staff on a tiled pad, two road markers, the altar of Hermes and a chest.", ("hermes-shrine",)),
    ("olive_grove", "Olive grove", "Seven to nine olive trees with silver-green leaves, laurel underfoot, and a tiled wayside shrine with a chest of olives.", ("olive-grove",)),
    ("greek_ruin", "Greek ruin", "A broken court: columns of three orders at different heights, fallen drums, a mosaic floor in patches, a low wall, a chest. Hoplites are set to patrol it.", ("greek-ruin",)),
]
CHEST_LABEL = {"temple_of_zeus": "the Temple of Zeus", "temple_of_athena": "the Temple of Athena", "temple_of_poseidon": "the Temple of Poseidon",
               "hermes_shrine": "a shrine of Hermes", "olive_grove": "an olive grove", "greek_ruin": "a Greek ruin", "labyrinth_vault": "a labyrinth vault",
               "labyrinth_entrance": "the labyrinth pavilion"}
SPAWNS = {"hoplite": "plains, meadow and sunflower plains", "cyclops": "windswept hills, stony peaks and savanna plateau"}  # as in OlympiaEntities.java


def n_structs():
    return len(list((DATA / "worldgen/structure_set").glob("*.json")))


def read_struct(name):
    root = nbt.loads((DATA / "structure" / f"{name}.nbt").read_bytes())
    pal = [p["Name"][1] for p in root["palette"][1][1]]
    blocks = {tuple(b["pos"][1][1]): pal[b["state"][1]] for b in root["blocks"][1][1]}
    return root, blocks


def maze_routes():
    """For each labyrinth variant: floor tiles reachable from the ladder, the shortest walk from the ladder to the Minotaur's hall, chests."""
    from collections import deque
    out = []
    for i in range(variants("labyrinth")):
        root, blocks = read_struct(f"labyrinth_{i}")
        size = tuple(root["size"][1][1])
        ladder = next(p for p, n in blocks.items() if n == "minecraft:ladder" and p[1] == 1)
        ent = root["entities"][1][1][0]["blockPos"][1][1]
        free = lambda x, z: all(blocks.get((x, y, z)) in ("minecraft:air", "minecraft:ladder") for y in (1, 2, 3))
        start, goal = (ladder[0], ladder[2]), (ent[0], ent[2])
        seen = {start: 0}
        q = deque([start])
        while q:
            u = q.popleft()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v = (u[0] + dx, u[1] + dz)
                if v not in seen and 0 <= v[0] < size[0] and 0 <= v[1] < size[2] and free(*v):
                    seen[v] = seen[u] + 1
                    q.append(v)
        out.append(dict(tiles=len(seen), walk=seen.get(goal), chests=sum(1 for n in blocks.values() if n == "minecraft:chest"), size=size))
    return out


def chance_of(path, item):
    for pool in jread(path)["pools"]:
        for e in pool["entries"]:
            if e.get("name") == item:
                for c in pool.get("conditions", []):
                    if c.get("condition") == "minecraft:random_chance":
                        return round(c["chance"] * 100)
    return None


def favor_ladder():
    li = "".join(f"<li><b>{s['at']}</b><span>{esc(s['name'])}</span></li>" for s in STAGES)
    return f'<ol class="ladder" aria-label="Divine favor stages by points">{li}</ol>'


NAV = [("index.html", "Home", "home"), ("blocks.html", "Blocks", "blocks"), ("gods.html", "Gods", "gods"), ("structures.html", "Places", "structures"),
       ("labyrinth.html", "Labyrinth", "labyrinth"), ("creatures.html", "Creatures", "creatures"), ("relics.html", "Relics", "relics"),
       ("install.html", "Install", "install")]
RECIPE_TEXT = {}


def home_wall():
    panels = [
        ("gods", "Gods", f"4 gods · {len(STAGES)} stages", "Make an offering. Be named Champion.", "gods.html", "panels/temple-of-zeus", "zeus_altar"),
        ("structures", "Places", f"{n_structs() - 1} places", "Temples, shrines, groves and ruins.", "structures.html", "panels/greek-ruin", "marble_bricks"),
        ("labyrinth", "Labyrinth", "61 by 61 blocks", "A maze under a pavilion, and a bull in it.", "labyrinth.html", "panels/labyrinth-hall", "black_marble"),
        ("blocks", "Blocks", f"{len(block_ids())} blocks", "Marble, columns, stairs and slabs.", "blocks.html", "panels/blocks", "greek_mosaic"),
        ("creatures", "Creatures", "3 creatures", "A hoplite, a cyclops, the Minotaur.", "creatures.html", "panels/creatures", "hoplite-face"),
        ("relics", "Relics", "2 relics · 5 potions", "A thunderbolt, a thread, and ambrosia.", "relics.html", "panels/relics", "thunderbolt"),
    ]
    items = ""
    for hue, name, figure, claim, href, img, icon in panels:
        items += (f'<li><a class="panel" style="--hue:var(--{hue})" href="/{href}"><img class="ph" src="/img/{img}.jpg" width="640" height="320" alt="" loading="eager">'
                  f'<span class="pn"><span class="name"><img src="/img/tex/{icon}.png" alt="" width="22" height="22">{esc(name)}</span>'
                  f'<span class="fig">{esc(figure)}</span><span class="claim">{esc(claim)}</span></span></a></li>')
    return f"""
<section class="wall" aria-labelledby="h1">
  <div class="cartouche"><h1 id="h1">Olympia</h1><p class="sub">Age of the gods. A Minecraft mod<span class="more">: marble temples, four Olympians, and a Minotaur that hunts you</span><span class="dot">.</span></p><a class="btn" href="/install.html">Build &amp; install</a></div>
  <ul class="panels">{items}</ul>
  <p class="meta wallnote">Real in-game photos from a flat test world; the grass and sky are vanilla.</p>
</section>"""


def build_index():
    body = home_wall() + f"""
<section class="page">
  <p class="lede">Olympia is the Greek sibling of the Asgard and Khemet mods: the same stack and ideas (shrines, offerings, relics, creatures, ancient structures), with a different mythology. This is slice one of a much larger <a href="https://github.com/SolutionsAsService/minecraft-olympia/blob/main/master-prompt.md">design</a>; the roadmap is on the <a href="https://github.com/SolutionsAsService/minecraft-olympia/blob/main/VISION.md">vision page</a>.</p>
  <p class="action"><a class="btn" href="/gods.html">Meet the gods</a> <a class="btn btn-alt" href="/labyrinth.html">Enter the labyrinth</a> <a class="btn btn-quiet" href="/install.html">Install</a></p>
  <h2>New here?</h2>
  <dl class="gloss">
    <dt>A Minecraft mod</dt><dd>An add-on that changes the game. This one adds marble blocks, temples, four gods, a few creatures and a labyrinth.</dd>
    <dt>A temple and an altar</dt><dd>A temple is a building for a god. Its altar is a block: hold an offering (say, a gold ingot for Zeus) and use it, and the god gives you a blessing.</dd>
    <dt>Favor</dt><dd>A score each god keeps for you. More offerings, more favor, and the god names you higher: Unknown Mortal, Recognized, Favored, Blessed, Champion of Olympus.</dd>
    <dt>The Thread of Ariadne</dt><dd>In the myth, a thread let Theseus find his way out of the labyrinth. Here it is an item that remembers where you tied it and points the way back.</dd>
  </dl>
  <h2>Divine favor</h2>
  <p>Each god takes offerings at its altar. Every offering adds favor, favor moves you up five stages, and each stage from Favored on adds a blessing.</p>
  {favor_ladder()}
  <p class="meta">The points are the thresholds in the mod's own data file.</p>
  {status(["The mod loads on a Fabric 1.21.4 server with no data errors.", "Six of the seven structures generate on their own in a flat plains world and the game's /locate finds them (the Temple of Poseidon needs a beach and was placed by command).", "Offering, favor stages, blessings, the Thunderbolt's favor gate and the Thread of Ariadne work through the same code the items and altars use.", "A Minotaur placed by its labyrinth hunted a player through the maze and reached them."],
          ["Using an altar by hand (the same code path was tested through a command).", "Eating ambrosia, brewing the potions, and the Thunderbolt by a real right-click.", "Fighting a cyclops or a hoplite, and either spawning on their own.", "A fight with the Minotaur in real gear.", "Anything in multiplayer, or a server restart."])}
</section>"""
    return page("Olympia: Greek gods, temples and a Minotaur for Minecraft", "A Minecraft mod: marble blocks, four Olympian gods with offerings and divine favor, the Thunderbolt and the Thread of Ariadne, temples, and a labyrinth with a Minotaur that hunts you.", body, "home", "index.html", None)


def build_blocks():
    cards = "".join(f'<li class="card">{sprite(n, 64, lang_block(n))}<div><h3>{esc(lang_block(n))}</h3><p>{esc(STONE_NOTES[n])}</p><p>{esc(recipe_text(n + "_from_stonecutting"))}</p></div></li>' for n in STONES)
    fam = "".join(f'<li class="card">{sprite(f, 64, lang_block(f + "_stairs"))}<div><h3>{esc(lang_block(f))} stairs and slabs</h3><p>{esc(recipe_text(f + "_stairs"))}.</p><p>Slabs: {esc(recipe_text(f + "_slab"))}; or cut from the stone at a stonecutter.</p></div></li>' for f in FAMILIES)
    others = [("doric_column", "Plain flutes and a plain base: the oldest order."), ("ionic_column", "Finer flutes with a blue and gold band under the scrolls."),
              ("corinthian_column", "The finest flutes and a gold-and-olive leaf capital."), ("amphora", "A terracotta storage jar with a black-figure runner."),
              ("greek_brazier", "A bronze bowl of fire. Light level 14."), ("laurel", "A small laurel plant with gold berries; grows on grass, dirt, sand and gravel."),
              ("olive_log", "Grey twisted bark with a ringed end."), ("olive_leaves", "Silver-green leaves with gaps; sometimes drop a sacred olive.")]
    oc = "".join(f'<li class="card">{sprite(n, 64, lang_block(n))}<div><h3>{esc(lang_block(n))}</h3><p>{esc(t)}</p><p>{esc(recipe_text(n))}</p></div></li>' for n, t in others)
    body = f"""
<section class="page">
  <p class="eyebrow">Blocks</p><h1>Marble for builders</h1><div class="rule"></div>
  <p class="lede">Twelve stones, four stair-and-slab families, three column orders, and a few things to put in a city. Every stone has a stonecutter recipe. The recipes are written and checked by a linter; none has been cut in play.</p>
  <div class="shots two">{fig("blocks", "The twelve stones in a row, with the columns and the altars behind.", "Twelve marble and tile blocks in a row on grass")}{fig("stairs", "Stairs and slabs in four materials, in front of the columns.", "Marble stairs and slabs in four materials")}</div>
  <h2>The twelve stones</h2><ul class="cards">{cards}</ul>
  <h2>Stairs and slabs</h2><ul class="cards">{fam}</ul>
  <h2>Columns and the rest</h2><ul class="cards">{oc}</ul>
  {status(["Every block loads, shows its own texture, and its item shows in the inventory and tab.", "The blocks in these photographs were placed in the game and photographed from a client; the plants and leaves render with cutouts."],
          ["Mining speeds and tool requirements.", "Placing stairs and slabs in every orientation and corner (the block states are generated for all of them).", "Crafting any recipe by hand."])}
</section>"""
    return page("Blocks: marble, columns, stairs and slabs", "The twelve marble and tile blocks, stairs and slabs, three column orders and city details of the Olympia mod.", body, "blocks", "blocks.html", "blocks")


def blessing_rows(god):
    rows = ""
    for b in CONTENT["gods"][god]["blessings"]:
        eff = ", ".join(f"{EFFECT.get(e[0], label(e[0]))} {roman(e[2] + 1)} for {dur(e[1])}" for e in b["effects"])
        rows += f'<tr><th scope="row">{esc(STAGES[b["stage"]]["name"])}</th><td>{esc(eff)}</td></tr>'
    return rows


def build_gods():
    secs = ""
    for god, slug, ph in GODS:
        g = CONTENT["gods"][god]
        off = "".join(f"<tr><th scope=\"row\">{esc(label(o['item']))}</th><td>{o['favor']} favor</td></tr>" for o in g["offerings"])
        extra = fig("zeus-altar", "The altar of Zeus inside the temple, between two braziers.", "The altar of Zeus with a gold lightning bolt on its top") if god == "zeus" else ""
        secs += f"""<section class="sec" id="{god}"><p class="eyebrow">{esc(g['title'])}</p><h2>{esc(g['name'])}</h2><p class="meta">{esc(g['domain'])}.</p>
  <div class="shots two">{fig(ph, g['temple'] + ".", g['temple'] + " on grass")}{extra}</div>
  <table class="data"><caption class="sr">{esc(g['name'])}: offerings</caption><tbody>{off}</tbody></table>
  <p>Blessings: each stage adds to the ones before it, so a Champion gets all of them. Blessings come when you make an offering.</p>
  <table class="data"><caption class="sr">{esc(g['name'])}: blessings by stage</caption><tbody>{blessing_rows(god)}</tbody></table></section>"""
    tb = CONTENT["thunderbolt"]
    body = f"""
<section class="page">
  <p class="eyebrow">Gods</p><h1>Four of the Twelve</h1><div class="rule"></div>
  <p class="meta">The gods here are game material: a simplified retelling for a Minecraft mod, made with respect for the ancient Greek world it draws on, and not a statement about religion.</p>
  <p class="lede">Each god has a temple or shrine and an altar. Hold an offering, use the altar, and the god takes one item, adds to your favor and gives you the blessings your stage has earned (tested through the matching command; the click itself is not yet tried). Favor is saved with the player.</p>
  <h2>Favor</h2>{favor_ladder()}
  <p>Use an altar with an empty hand to see your favor and what the god wants. <code>/olympia favor</code> lists your standing with every god. Zeus's Thunderbolt works only once Zeus has named you {esc(STAGES[tb['required_stage']]['name'])}.</p>
  {secs}
  <p class="meta">Eight more gods are in the design (Hera, Ares, Apollo, Artemis, Aphrodite, Hephaestus, Demeter, Dionysus); slice one has four.</p>
  {status(["Offering, refusal of the wrong item and favor kept per god, through the command that runs the same code as the altar: Zeus 1 and 2 favor for gold ingots, Poseidon refused gold, Athena accepted a book.", "At 37 favor (Champion of Olympus) Zeus's blessings were active: Resistance and Strength II.", "The temples and the shrine are photographed from a client; five generate on their own in a plains world."],
          ["Using an altar block with a held item (the click path).", "Favor kept across death or a server restart (it is set to be kept; not yet checked in Olympia).", "The blessings of Athena, Poseidon and Hermes at each stage were not individually inspected."])}
</section>"""
    return page("Gods: Zeus, Athena, Poseidon and Hermes", "Four Olympians in the Olympia mod: their temples, altars, offerings, five stages of divine favor and the blessings each stage gives.", body, "gods", "gods.html", "gods")


def build_structures():
    secs = ""
    for slug, title, blurb, shots in PLACES:
        (sx, sy, sz), nblocks = nbt_size(slug + "_0")
        sset = jread(DATA / "worldgen/structure_set" / f"{slug}.json")["placement"]
        biomes = ", ".join(b.replace("#minecraft:is_", "").replace("minecraft:", "").replace("_", " ") for b in jread(DATA / "tags/worldgen/biome/has_structure" / f"{slug}.json")["values"])
        spawns = jread(DATA / "worldgen/structure" / f"{slug}.json").get("spawn_overrides", {})
        sp = ", ".join(f"{label(s['type'])} ({s['minCount'] if s['minCount'] == s['maxCount'] else str(s['minCount']) + ' to ' + str(s['maxCount'])})" for c in spawns.values() for s in c["spawns"]) or "none"
        sp = (sp + ". Set in the structure's data; not yet watched in play.") if sp != "none" else sp
        figs = "".join(fig(n, title + (", ruined variant." if n.endswith("ruined") else "."), title) for n in shots)
        secs += f"""<section class="sec" id="{slug}"><h2>{esc(title)}</h2><p>{esc(blurb)}</p><div class="shots two">{figs}</div>
  <table class="data"><caption class="sr">{esc(title)}: facts</caption><tbody>
  <tr><th scope="row">Size</th><td>{sx} by {sz} blocks, {sy} high; {variants(slug)} variants</td></tr>
  <tr><th scope="row">Spacing</th><td>One in every {sset['spacing']} by {sset['spacing']} chunks</td></tr>
  <tr><th scope="row">Biomes</th><td>{esc(biomes)}</td></tr>
  <tr><th scope="row">Guardians</th><td>{esc(sp)}</td></tr>
  <tr><th scope="row">Chest</th><td>{esc(", ".join(chest_items(slug)))}</td></tr></tbody></table></section>"""
    body = f"""
<section class="page">
  <p class="eyebrow">Places</p><h1>Six things in the grass</h1><div class="rule"></div>
  <p class="lede">Three temples, a roadside shrine, an olive grove and a ruin. Each is a template with variants, generated by the game where the biome allows, with a chest of themed loot. The labyrinth has <a href="/labyrinth.html">its own page</a>.</p>
  {secs}
  {status(["Zeus, Athena, the shrine, the grove and the ruin generate on their own in a flat plains world: the game's /locate found each, from 97 to 273 blocks away.", "All six were also placed with the template command and photographed from a client."],
          ["The Temple of Poseidon generating on a beach on its own.", "How these sit among vanilla villages and terrain (a flat test world has none).", "Cities, Delphi, harbours and Mount Olympus are not in this slice."])}
</section>"""
    return page("Places: temples, a shrine, olive groves and ruins", "The six overworld structures of the Olympia mod: the temples of Zeus, Athena and Poseidon, the shrine of Hermes, olive groves and Greek ruins.", body, "structures", "structures.html", "structures")


def build_labyrinth():
    routes = maze_routes()
    rows = "".join(f'<tr><th scope="row">Variant {i}</th><td>{r["tiles"]} floor tiles; the walk from the ladder to the Minotaur\'s hall is {r["walk"]} blocks; {r["chests"]} chests</td></tr>' for i, r in enumerate(routes))
    m = CONTENT["creatures"]["minotaur"]
    loot = ", ".join(chest_items("labyrinth_vault"))
    body = f"""
<section class="page">
  <p class="eyebrow">Labyrinth</p><h1>The way down</h1><div class="rule"></div>
  <p class="lede">A stoa of marble columns stands over a ladder. Thirteen blocks down is a maze of three-wide corridors, built fresh from a seed, with a hall at its centre and a Minotaur in the hall. It does not wait there.</p>
  <div class="shots two">{fig("labyrinth-pavilion", "The pavilion over the ladder: Doric columns, a black marble altar, braziers, and a chest with Ariadne's thread.", "A marble pavilion with columns on grass")}{fig("labyrinth-hall", "The hall at the centre, with the Minotaur standing (its AI is off for the photograph).", "A marble hall underground with a large bull-headed creature")}</div>
  <div class="shots two">{fig("labyrinth-corridor", "A corridor, lit by a lamp set into the ceiling.", "A dim three-wide marble corridor")}</div>
  <h2>What it is</h2>
  <table class="data"><caption class="sr">The labyrinth: facts</caption><tbody>
  <tr><th scope="row">Size</th><td>{routes[0]['size'][0]} by {routes[0]['size'][2]} blocks, {routes[0]['size'][1]} high; 15 by 15 cells; corridors 3 wide and 3 high</td></tr>
  <tr><th scope="row">Variants</th><td>{len(routes)}, each a different maze</td></tr>
  <tr><th scope="row">Placement</th><td>The top ground layer is the pavilion's floor; the maze is 13 blocks below. Set to generate in plains, meadows, savannas and forests, one in every {jread(DATA / 'worldgen/structure_set/labyrinth.json')['placement']['spacing']} by {jread(DATA / 'worldgen/structure_set/labyrinth.json')['placement']['spacing']} chunks.</td></tr>
  {rows}
  <tr><th scope="row">Treasure</th><td>Chests at the farthest dead ends and one in the hall: {esc(loot)}</td></tr>
  <tr><th scope="row">The thread</th><td>A chest in the pavilion holds a Thread of Ariadne. Use it where you tie it, use it anywhere to be told the way back.</td></tr></tbody></table>
  <h2>The Minotaur</h2>
  <p>{m['health']:g} health, {m['damage']:g} damage, {m['armor']:g} armour, scale {m['scale']:g}. It hunts: it picks the nearest player within {m['follow_range']:g} blocks, <em>without needing to see them</em>, and walks the maze toward them. In the open it charges (Speed III for {m['charge_seconds']} seconds); close in, it slams the ground for {m['slam_damage']:g} damage and a shove; below half health it enrages: faster and harder. It never despawns and has a boss bar.</p>
  <p>It took three fixes to make it find a player in the maze: its target goal still wanted line of sight; floor lanterns blocked the corridors; and one-wide corridors stopped a creature its size at every corner. It now reaches a player standing {routes[2]['walk']} blocks of corridor away in about a minute.</p>
  {status(["The labyrinth was placed in a world with room underground and the maze explored from a client; the connectivity of every variant was checked from the structure files.", "The Minotaur, placed by the structure, charged (Speed III seen), slammed (it took a player from full health to zero in about six seconds with Regeneration running), enraged below half health (speed up, damage up), and hunted a player through the maze to reach them.", "Its boss bar shows on screen (it is in the photographs, from a long way off: a boss bar shows to every player the game tracks the creature for)."],
          ["A fight with real armour and weapons, and whether the damage is fair.", "Natural generation of the whole maze in a normal world (in a flat world with no depth, only its entrance exists).", "Multiple floors, traps, rotating walls and puzzles: not in this slice."])}
</section>"""
    return page("Labyrinth: a maze, a thread and a Minotaur that hunts", "The Olympia labyrinth: a seeded maze under a marble pavilion, the Thread of Ariadne, and a Minotaur that tracks players through the corridors.", body, "labyrinth", "labyrinth.html", "labyrinth")


def build_creatures():
    cards = ""
    c = CONTENT["creatures"]
    info = (("hoplite", "Hoplite", "creatures", "A citizen-soldier in a bronze Corinthian helmet and breastplate with a sword and shield. As written in the code (not yet seen in a fight): it does not burn in sunlight and calls no reinforcements.", "Plains: groups of 1 to 3, weight 8; set to patrol the Greek ruin and to guard the temples of Zeus and Athena."),
            ("cyclops", "Cyclops", "cyclops", "A one-eyed brute, 1.4 times your size. As written: hard to push, and its blows throw you into the air.", "Hills and peaks: one at a time, weight 3."),
            ("minotaur", "Minotaur", "minotaur", "The bull-headed thing of the labyrinth. See <a href=\"/labyrinth.html\">its page</a>. It has no natural spawn: the labyrinth places it.", "None; the labyrinth places one."))
    for key, name, shotn, blurb, spawn in info:
        a = c[key]
        loot = ", ".join(label(e["name"]) for pool in jread(DATA / "loot_table/entities" / f"{key}.json")["pools"] for e in pool["entries"] if e.get("type") == "minecraft:item")
        cards += f"""<section class="sec" id="{key}"><h2>{name}</h2><p>{blurb}</p>{fig(shotn if key != 'hoplite' else 'creatures', name + ", with the AI off for the photograph.", name + " standing on grass")}
  <table class="data"><caption class="sr">{name}: facts</caption><tbody>
  <tr><th scope="row">Stats</th><td>{a['health']:g} health ({a['health'] / 2:g} hearts), {a['damage']:g} attack damage, {a['armor']:g} armour</td></tr>
  <tr><th scope="row">Spawns</th><td>{esc(spawn)}</td></tr>
  <tr><th scope="row">Drops</th><td>{esc(loot)}</td></tr>
  <tr><th scope="row">Spawn egg</th><td>In the Spawn Eggs tab, and <code>/summon olympia:{key}</code></td></tr></tbody></table></section>"""
    body = f"""
<section class="page">
  <p class="eyebrow">Creatures</p><h1>Bronze, one eye, and a bull</h1><div class="rule"></div>
  <p class="lede">Three creatures from the design's Phase 3. They use the zombie model with skins painted for the mod; the Minotaur's horns are painted on the head, not modelled.</p>
  {cards}
  {status(["All three load, render with their skins and are summoned and photographed.", "The Minotaur's behaviour was watched in play (see the labyrinth page). The stats are the ones in the data file, read at build time."],
          ["Hoplites and cyclopes spawning on their own, and a fight with either.", "Their drops (the tables are written, not yet watched).", "Custom models and animations: they reuse the zombie's."])}
</section>"""
    return page("Creatures: hoplite, cyclops and Minotaur", "The hoplite, the cyclops and the Minotaur of the Olympia mod: stats, spawns, drops and what they do.", body, "creatures", "creatures.html", "creatures")


def build_relics():
    tb, th, am = CONTENT["thunderbolt"], CONTENT["thread"], CONTENT["ambrosia"]
    where = {}
    for slug in CHEST_LABEL:
        for it in chest_items(slug):
            where.setdefault(it, []).append(CHEST_LABEL[slug])
    rows = ""
    for p in POTIONS:
        ing = p["ingredient"].replace("_", " ").title()
        found = ", ".join(where.get(ing, [])) or "only by crafting or other drops"
        rows += (f'<li class="card">{sprite("item-" + p["ingredient"], 64, ing)}<div><h3>{esc(p["name"])}</h3><p>{esc(p["god"])}, {esc(p["epithet"])}. '
                 f'{" ".join(esc(fx(e)) + "." for e in p["effects"])}</p><p>Brew an Awkward Potion with {esc(ing)}. Found in {esc(found)}.</p><p>{esc(p["lore"])}</p></div></li>')
    tchance = chance_of(DATA / "loot_table/chests/temple_of_zeus.json", "olympia:thunderbolt")
    body = f"""
<section class="page">
  <p class="eyebrow">Relics &amp; potions</p><h1>A thunderbolt, a thread, and ambrosia</h1><div class="rule"></div>
  <div class="shots two">{fig("relics", "The relics and drops (below) and the five potions (above), shown large.", "Relics and potions shown at display size")}</div>
  <h2>Relics</h2>
  <p class="meta">The numbers here are as written in the data; the relics were exercised through a command that runs the same code as a right-click.</p>
  <ul class="cards"><li class="card">{sprite("thunderbolt", 64, "Thunderbolt of Zeus")}<div><h3>Thunderbolt of Zeus</h3><p>Hurls lightning where you look (up to {tb['range']} blocks), with {tb['damage']:g} extra damage to anything near the strike. It works only once Zeus has named you {esc(STAGES[tb['required_stage']]['name'])}; before that, it refuses. It wears out after {tb['durability']} uses and needs {tb['cooldown_ticks'] // 20} seconds between throws.</p><p>Found in {tchance}% of the Temple of Zeus's chests.</p></div></li>
  <li class="card">{sprite("thread_of_ariadne", 64, "Thread of Ariadne")}<div><h3>Thread of Ariadne</h3><p>Use it to tie the thread where you stand. Use it again anywhere (in the same dimension) and it says which way the knot lies, how far, and how high, with a line of light along the first stretch. Sneak and use to tie it somewhere new.</p><p>In a chest in the labyrinth pavilion.</p></div></li>
  <li class="card">{sprite("ambrosia", 64, "Ambrosia")}<div><h3>Ambrosia</h3><p>Food of the gods: eat it at any hunger for {am['nutrition']} food points and Regeneration {roman(am['regen_amplifier'] + 1)} for {am['regen_seconds']} seconds. {esc(recipe_text('ambrosia'))}.</p></div></li></ul>
  <h2>Drops</h2>
  <ul class="cards"><li class="card">{sprite("obol", 64, "Obol")}<div><h3>Obol</h3><p>A bronze coin dropped by hoplites and found in chests. It has no use yet: it is for the Underworld's ferryman, which is not in this slice.</p></div></li>
  <li class="card">{sprite("cyclops_bloodstone", 64, "Cyclops Bloodstone")}<div><h3>Cyclops Bloodstone</h3><p>A red stone dropped by cyclopes and found in labyrinth vaults. No use yet.</p></div></li>
  <li class="card">{sprite("minotaur_horn", 64, "Minotaur Horn")}<div><h3>Minotaur Horn</h3><p>Always dropped by the Minotaur. No use yet.</p></div></li></ul>
  <h2>The five potions</h2><ul class="cards">{rows}</ul>
  <p class="meta">The potions use the same data format as Asgard's and Khemet's: one entry in <code>potions.json</code> adds an ingredient, a potion and a brewing recipe.</p>
  {status(["The Thunderbolt refused at Unknown Mortal, struck at Favored (a lightning bolt appeared; the item took one point of damage).", "The Thread of Ariadne tied at one point and then said \\u201cnorth-west, 50 blocks\\u201d and \\u201csouth-east, 25 blocks\\u201d from two other points, both correct.", "The five potions and their ingredients load, and the recipes register."],
          ["A right-click with the Thunderbolt or the thread by hand.", "Eating ambrosia.", "Brewing, drinking or splashing the potions.", "Any use for the obol, the bloodstone and the horn."])}
</section>"""
    return page("Relics & potions: the Thunderbolt, the Thread of Ariadne and ambrosia", "The Thunderbolt of Zeus, the Thread of Ariadne, ambrosia and the five divine potions of the Olympia mod.", body, "relics", "relics.html", "relics")


def build_install():
    mf = jread(REPO / "shadw.mod.json")
    body = f"""
<section class="page">
  <p class="eyebrow">Install</p><h1>Install Olympia</h1><div class="rule"></div>
  <p class="lede">Olympia is a Fabric mod for Minecraft {esc(mf['game_versions'][0])}. No release jar is published yet, so you build it. It is also in the <b>Greek Pantheon</b> mod pack in <a href="https://github.com/SolutionsAsService/shadw-modding">shadw-modding</a>.</p>
  <p class="meta">Words used here: a <b>mod</b> is an add-on for the game; a <b>jar</b> is the mod’s file; <b>Fabric</b> is the program that loads mods; an <b>operator</b> is a player allowed to use admin commands.</p>
  <h2>You need</h2><ul><li>Minecraft Java Edition {esc(mf['game_versions'][0])} (not Bedrock)</li><li><a href="https://fabricmc.net">Fabric</a> Loader 0.16 or later, and Fabric API</li><li>Java 21 and Gradle 8 (the repository has no Gradle wrapper)</li></ul>
  <h2>Build</h2>
  <pre><code>git clone https://github.com/SolutionsAsService/minecraft-olympia
cd minecraft-olympia
gradle build
# the jar is in build/libs/olympia-{esc(mf['version'])}.jar</code></pre>
  <p>Copy the jar into your <code>mods</code> folder and start the game. The server log line <code>Olympia loaded: 5 potions, 5 brewing recipes, 0 unknown effects skipped; {len(block_ids())} blocks, 4 gods, 3 creatures</code> confirms the registration.</p>
  <h2>Commands</h2>
  <table class="data"><caption class="sr">Commands</caption><tbody><tr><th scope="row"><code>/olympia favor</code></th><td>Your favor and stage with each god.</td></tr>
  <tr><th scope="row"><code>/olympia offer &lt;god&gt;</code></th><td>Operators: offer the item in your hand to a god (the same code the altar runs).</td></tr>
  <tr><th scope="row"><code>/olympia setfavor &lt;god&gt; &lt;n&gt;</code></th><td>Operators: set your favor with a god, for testing.</td></tr>
  <tr><th scope="row"><code>/olympia use</code></th><td>Operators: use the held item exactly as a right-click does.</td></tr>
  <tr><th scope="row"><code>/olympia thread</code></th><td>Operators: print what the held Thread of Ariadne says.</td></tr></tbody></table>
  {status(["Builds on Fabric Loom 1.11.8 and Gradle 8, and loads on a Fabric 1.21.4 dedicated server; a client joined and rendered every photograph here."],
          ["Other platforms and mods: it is built and tried only on Fabric 1.21.4 with Fabric API.", "A published release jar."])}
</section>"""
    return page("Install Olympia", "How to build and install the Olympia Minecraft mod.", body, "install", "install.html", None)


def convert(*args):
    return subprocess.run(["convert", *map(str, args)], capture_output=True).returncode == 0


def prepare_assets():
    tex = SITE / "img/tex"
    shutil.rmtree(tex, ignore_errors=True)
    tex.mkdir(parents=True, exist_ok=True)
    pick = {"greek_brazier": "greek_brazier_top", "zeus_altar": "zeus_altar_top", "athena_altar": "athena_altar_top", "poseidon_altar": "poseidon_altar_top",
            "hermes_altar": "hermes_altar_top"}
    for n in block_ids():
        for src in (ASSETS / "textures/block" / f"{pick.get(n, n)}.png", ASSETS / "textures/block" / f"{n.rsplit('_', 1)[0]}.png"):
            if src.exists():
                shutil.copyfile(src, tex / f"{n}.png")
                break
    for p in POTIONS:
        shutil.copyfile(ASSETS / "textures/item" / f"{p['ingredient']}.png", tex / f"item-{p['ingredient']}.png")
    for n in ("thunderbolt", "thread_of_ariadne", "ambrosia", "obol", "cyclops_bloodstone", "minotaur_horn"):
        shutil.copyfile(ASSETS / "textures/item" / f"{n}.png", tex / f"{n}.png")
    convert(ASSETS / "textures/entity/hoplite.png", "-crop", "8x8+8+8", "+repage", "-filter", "point", "-resize", "88x88", tex / "hoplite-face.png")
    panels = SITE / "img/panels"
    shutil.rmtree(panels, ignore_errors=True)
    panels.mkdir(parents=True, exist_ok=True)
    for name in ("temple-of-zeus", "greek-ruin", "labyrinth-hall", "blocks", "creatures", "relics"):
        src = SITE / "img/shots" / f"{name}.png"
        if src.exists():
            convert(src, "-gravity", "south", "-crop", "854x420+0+0", "+repage", "-resize", "640x320^", "-gravity", "center", "-extent", "640x320", "-quality", "80", panels / f"{name}.jpg")   # the top 60 px can hold a boss bar
        else:
            raise SystemExit(f"missing photograph for the landing: {src}")
    og = SITE / "img/og.png"
    ok = convert(SITE / "img/shots/temple-of-zeus.png", "-resize", "1200x630^", "-gravity", "center", "-extent", "1200x630", "-fill", "#13101AD0",
                 "-draw", "rectangle 0,430 1200,630", "-fill", TEXT, "-pointsize", "92", "-gravity", "southwest", "-annotate", "+48+86", "OLYMPIA",
                 "-fill", SIGNAL, "-pointsize", "34", "-annotate", "+52+36", "Age of the gods · a Minecraft mod", og)
    if not ok:
        shutil.copyfile(SITE / "img/shots/temple-of-zeus.png", og)
    (SITE / "img/icon.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="16" fill="{GROUND}"/>'
                                       f'<rect x="2" y="3" width="12" height="2" fill="{SIGNAL}"/><rect x="3" y="5" width="2" height="8" fill="{SIGNAL}"/>'
                                       f'<rect x="7" y="5" width="2" height="8" fill="{SIGNAL}"/><rect x="11" y="5" width="2" height="8" fill="{SIGNAL}"/>'
                                       f'<rect x="2" y="13" width="12" height="2" fill="{SIGNAL}"/></svg>\n')


def write(rel, text):
    path = SITE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    palette = check_palette()
    check_deploy()
    prepare_assets()
    write("style.css", css())
    for rel, fn in (("index.html", build_index), ("blocks.html", build_blocks), ("gods.html", build_gods), ("structures.html", build_structures),
                    ("labyrinth.html", build_labyrinth), ("creatures.html", build_creatures), ("relics.html", build_relics), ("install.html", build_install)):
        write(rel, fn())
    weight = {p.name: p.stat().st_size for p in (SITE / "img/panels").glob("*.jpg")}
    print(f"site written: {len(list(SITE.glob('*.html')))} pages; palette min delta-E {palette['min_delta_e']} ({palette['min_pair']}); "
          f"min hue contrast {palette['min_contrast']}; first-screen images {sum(weight.values()) // 1024} KB over {len(weight)} files, largest {max(weight.values()) // 1024} KB")


if __name__ == "__main__":
    main()
