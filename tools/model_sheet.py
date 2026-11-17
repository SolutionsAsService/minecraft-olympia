#!/usr/bin/env python3
"""Write playtest/model-<id>.json scenes: a mob with its AI off, photographed front, three-quarter, side, back and two face close-ups.
The spectator's eye is 1.62 blocks above the position it is teleported to, so camera y = target height - 1.62.
    python3 tools/model_sheet.py satyr gorgon ...   then   shadw-mod playtest . shoot playtest/model-<id>.json
"""
import json
import sys

# id: (height in blocks, head-centre height, full-view distance, face distance)
SIZES = {"pegasus": (1.9, 1.7, 6.5, 2.2, 0.9), "satyr": (1.96, 1.7, 4.4, 1.9), "gorgon": (2.2, 2.0, 5.0, 2.2), "hoplite": (2.0, 1.75, 4.4, 1.9), "cyclops": (2.9, 2.5, 6.4, 3.0), "minotaur": (3.2, 2.8, 7.0, 3.3),
         "mummy": (1.95, 1.7, 4.4, 1.9), "royal_mummy": (2.1, 1.85, 4.6, 2.0), "scarab": (0.7, 0.5, 2.6, 1.3), "tomb_guardian": (2.7, 2.3, 6.0, 2.8), "forgotten_pharaoh": (3.2, 2.8, 7.0, 3.3)}


K = {"fenrir": 0.95, "raven": 0.85, "warg": 0.9, "sleipnir": 0.6, "pegasus": 0.7, "troll": 0.8, "jotunn": 0.82, "draugr_lord": 0.8, "crocodile": 0.9, "chariot": 0.85, "cobra": 0.85, "scarab": 1.0, "forgotten_pharaoh": 0.85, "sun_pharaoh": 0.85, "tomb_guardian": 0.8, "minotaur": 0.85, "cyclops": 0.8, "gorgon": 0.8}   # framing: the fraction of the full-view distance the portrait cameras use (default 0.75)


def cam(x, y, z, yaw, p, n):
    return {"tp": [x, y, z, yaw, p], "capture": n, "wait": 6}


def main(ids, ns):
    for mob in ids:
        hgt, head, dist, fd, *rest = SIZES[mob]
        hz = rest[0] if rest else 0.0      # how far in front of the feet the head is (a wolf's is a block ahead)
        fy = f"G+{max(head - 1.62, -1.2):.2f}"
        mid = f"G+{max(hgt * 0.5 - 1.62, -0.9):.2f}"
        cx, cz = 0, -20
        t = dist * K.get(mob, 0.75)        # tight, for the site's pictures: the subject fills about half the frame, and the camera is AIMED at it (yaw 135 looks at the mob from 45 degrees)
        up = f"G+{hgt * 0.5 - 1.62 + 0.21 * t:.2f}"      # the portraits look down 12 degrees at the creature's centre, so the ground shows and the creature sits mid-frame
        steps = [cam(cx, mid, cz + dist, 180, 6, f"{mob}-front"), cam(cx + t * 0.7, up, cz + t * 0.7, 135, 12, f"{mob}-three-quarter"),
                 cam(cx + t, up, cz, 90, 12, f"{mob}-side"), cam(cx, mid, cz - dist, 0, 6, f"{mob}-back"),
                 cam(cx, fy, cz + hz + fd, 180, 0, f"{mob}-face"), cam(fd * 0.8, fy, cz + hz + fd * 0.7, 153, 0, f"{mob}-face-side")]
        scene = {"out": "playtest/models", "settle": 8, "steps": steps, "setup": [
            "forceload add -20 -40 20 0", "kill @e[type=slime]", "gamerule doMobSpawning false"] + [f"kill @e[type={ns}:{m}]" for m in SIZES] + ["kill @e[type=item]"] +
            [f"summon {ns}:{mob} 0 $G -20 {{NoAI:1b,PersistenceRequired:1b,Rotation:[0f,0f]}}"]}
        with open(f"playtest/model-{mob}.json", "w") as f:
            json.dump(scene, f, indent=2)


if __name__ == "__main__":
    main(sys.argv[1:], "olympia")
