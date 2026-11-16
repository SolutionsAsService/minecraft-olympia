"""figure: author creature model specs (the "model" section of a mob spec) without writing part trees by hand.

    from shadwlib.figure import Rig, rect
    r = Rig(paints={...})
    r.biped(head=..., ...)          # a finely shaped humanoid: head, two-piece torso, three-piece arms and legs, walk and look animation
    r.chain("tail", "root", (0, -12, 2), [...])   # a tapering chain of segments that sways
    spec_model = r.model(shadow=0.5)

Coordinates are Minecraft model pixels: +y down, -z forward, root at the feet. See adapters/minecraft-fabric/mobmodel.py.
Finer edges: tapered limbs, stacked torso boxes, shoulder/knee/hand joints, and fractional `grow` (a 2-pixel box with grow -0.25 is a 1.5-pixel edge).
"""
import math


def rect(face, x, y, w, h, color):
    return {"face": face, "type": "rect", "x": x, "y": y, "w": w, "h": h, "color": color}


def box(frm, size, paint, grow=0, decals=None):
    b = {"from": list(frm), "size": list(size), "grow": grow, "paint": paint}
    if decals:
        b["decals"] = decals
    return b


class Rig:
    def __init__(self, paints):
        self.paints = dict(paints)
        self.parts = []
        self.anims = []
        self.names = {"root"}

    def part(self, name, parent, pivot, rot, boxes):
        assert name not in self.names, f"duplicate part {name}"
        assert parent in self.names, f"{name}: parent {parent} not defined yet"
        self.names.add(name)
        self.parts.append({"name": name, "parent": parent, "pivot": list(pivot), "rot": list(rot), "boxes": boxes})
        return name

    def anim(self, part, kind, **kw):
        self.anims.append({"part": part, "type": kind, **kw})

    def model(self, shadow=0.5):
        return {"shadow": shadow, "paints": self.paints, "parts": self.parts, "anim": self.anims}

    # ---------- a tapering chain of segments that sways (tails, snakes, tassels, tentacles) ----------
    def chain(self, prefix, parent, pivot, segs, paint, sway="y", amp=0.15, freq=0.15, phase=0.0, walk_amp=0.0, last_decals=None):
        """segs: list of (length, width_x, width_z, rot_x_deg, rot_z_deg). The chain hangs down +y; each segment is rotated relative to the previous."""
        prev, pv = parent, pivot
        for i, (ln, wx, wz, rx, rz) in enumerate(segs):
            nm = f"{prefix}{i}"
            dec = last_decals if (i == len(segs) - 1 and last_decals) else None
            self.part(nm, prev, pv, (rx, 0, rz), [box((-wx / 2, 0, -wz / 2), (wx, ln, wz), paint, 0, dec)])
            self.anim(nm, "sway", axis=sway if i % 2 == 0 else ("x" if sway == "z" else "z"), amp=amp + 0.03 * i, freq=freq + 0.01 * i, phase=phase + i * 0.8, walk_amp=walk_amp)
            prev, pv = nm, (0, ln, 0)
        return prev

    # ---------- a finely shaped humanoid ----------
    def biped(self, skin, cloth=None, head=None, head_decals=None, torso_scale=1.0, arm_len=(5, 5), leg_len=(6, 6), stance=0.0,
              chest=(8, 7, 4), waist=(6, 5, 3), shoulder=True, hands=True, feet=True, walk=1.0, swing_arm="r", head_paint=None,
              hunch=0.0, shin_paint=None, arm_paint=None, thigh_paint=None, hip_y=None, legs=True, arm_pose=None, body_paint=None, chest_paint=None, cloth_hips=True, arm_w=3, leg_w=3, foot_paint=None, foot_len=5.5):
        """Builds head, chest + waist, shoulders, upper/lower arms with hands, thighs/shins with feet.
        Returns the names {head, body, arm_l, arm_r, forearm_l, forearm_r, hand_l, hand_r, leg_l, leg_r, shin_l, shin_r, foot_l, foot_r}."""
        ua, la = arm_len
        th, sh = leg_len
        hy = hip_y if hip_y is not None else -(th + sh)           # the hip height above the feet (negative)
        cw, ch, cd = chest
        ww, wh, wd = waist
        top = hy - (wh + ch)                                      # the top of the torso
        n = {}
        # pelvis and waist, then the chest
        if cloth_hips:
            n["pelvis"] = self.part("pelvis", "root", (0, hy, 0), (0, 0, 0), [box((-ww / 2 - 0.5, -1, -wd / 2 - 0.5), (ww + 1, 3, wd + 1), cloth or skin)])
        n["body"] = self.part("body", "root", (0, hy, 0), (hunch, 0, 0), [box((-ww / 2, -wh, -wd / 2), (ww, wh, wd), body_paint or skin)])
        n["chest"] = self.part("chest", "body", (0, -wh, 0), (-hunch * 0.5, 0, 0), [box((-cw / 2, -ch, -cd / 2), (cw, ch, cd), chest_paint or body_paint or skin)])
        # head: a skull, a narrower jaw and a brow, on a neck
        hb = head or {}
        w, hh, d = hb.get("size", (8, 8, 8))
        n["neck"] = self.part("neck", "chest", (0, -ch, 0), (0, 0, 0), [box((-1.5, -1, -1.5), (3, 2, 3), skin)])
        n["head"] = self.part("head", "neck", (0, -1, 0), (-hunch, 0, 0), [
            box((-w / 2, -hh + 2, -d / 2), (w, hh - 2, d), head_paint or skin, 0, head_decals),
            box((-w / 2 + 1, 0, -d / 2 + 1), (w - 2, 2, d - 2), head_paint or skin)])
        self.anim("head", "look")
        for side, sx in (("l", 1), ("r", -1)):
            ax = sx * (cw / 2 + 1.5)
            ay = -ch + 2
            # shoulder cap, upper arm, forearm, hand
            parts = []
            if shoulder:
                parts.append(box((-arm_w / 2 - 1, -2.5, -arm_w / 2 - 1), (arm_w + 2, 3, arm_w + 2), cloth or skin, 0.1))
            parts.append(box((-arm_w / 2, -0.5, -arm_w / 2), (arm_w, ua, arm_w), arm_paint or skin))
            pose = (arm_pose or {}).get(side)
            n[f"arm_{side}"] = self.part(f"arm_{side}", "chest", (ax, ay, 0), pose[0] if pose else (stance, 0, sx * 4), parts)
            n[f"forearm_{side}"] = self.part(f"forearm_{side}", f"arm_{side}", (0, ua - 0.5, 0), pose[1] if pose else (-12, 0, 0), [box((-arm_w / 2, 0, -arm_w / 2), (arm_w, la, arm_w), arm_paint or skin), box((-arm_w / 2, 1, -arm_w / 2), (arm_w, 2, arm_w), cloth or skin, 0.35)])
            if hands:
                n[f"hand_{side}"] = self.part(f"hand_{side}", f"forearm_{side}", (0, la, 0), (0, 0, 0), [box((-arm_w / 2, 0, -arm_w / 2), (arm_w, 2, arm_w), skin, 0.1)])
            phase = 0 if side == "l" else math.pi
            if side != swing_arm and not pose:
                self.anim(f"arm_{side}", "walk", axis="x", amp=0.9 * walk, phase=phase)
            if side == swing_arm and not pose:
                self.anim(f"arm_{side}", "swing", axis="x", amp=1.3)
            self.anim(f"arm_{side}", "sway", axis="z", amp=0.03, freq=0.09, phase=phase)
            if not legs:
                continue
            # leg: thigh, shin, foot
            lx = sx * (ww / 2 - 0.2)
            n[f"leg_{side}"] = self.part(f"leg_{side}", "root", (lx, hy, 0), (0, 0, 0), [box((-(leg_w + 1) / 2, 0, -(leg_w + 1) / 2), (leg_w + 1, th, leg_w + 1), thigh_paint or skin)])
            n[f"shin_{side}"] = self.part(f"shin_{side}", f"leg_{side}", (0, th, 0), (4, 0, 0), [box((-leg_w / 2, 0, -leg_w / 2), (leg_w, sh - 2, leg_w), shin_paint or skin), box((-leg_w / 2, 0.5, -leg_w / 2 - 0.5), (leg_w, 2, 1), shin_paint or skin)])
            if feet:
                n[f"foot_{side}"] = self.part(f"foot_{side}", f"shin_{side}", (0, sh - 2, 0), (-4, 0, 0), [box((-(leg_w + 1) / 2, 0, -foot_len + 2), (leg_w + 1, 2, foot_len), foot_paint or shin_paint or skin)])
            self.anim(f"leg_{side}", "walk", axis="x", amp=1.1 * walk, phase=math.pi if side == "l" else 0)
        return n


def mirror(v):
    return [-v[0], v[1], v[2]]
