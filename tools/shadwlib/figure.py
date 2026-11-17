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


def face(w, h, eye="#8ae8ff", socket="#101418", brow=None, nose=None, nostril=None, mouth=None, teeth=None, cheek=None, pupil=None, eye_row=2, eye_w=2, gap=None):
    """Decals for the front face of a head box (w x h pixels; the box's front face is w by h). Layout, top to bottom: brow (a dark line across
    the eyes), the eyes (a dark socket row over a glowing row, the pupil on the inner pixel), a nose bridge and nostrils on the centre line, cheek
    hollows under the eyes, and a mouth line with teeth on the last row. Every part is optional: pass only the colours the creature has.
    Faces read from a distance by their eyes and brow, and up close by the nose and mouth: set all of them, then look at the close-up photograph."""
    w, h = int(math.ceil(w)), int(math.ceil(h))
    d = []
    ex = gap if gap is not None else max(0, round(w * 0.16))
    lx, rx = ex, w - ex - eye_w
    r_ = eye_row
    if brow:
        d.append(rect("front", max(0, lx - 1), r_ - 1, min(w, rx + eye_w + 1 - max(0, lx - 1)), 1, brow)) if r_ >= 1 else None
    for x in (lx, rx):
        d.append(rect("front", x, r_, eye_w, 1, socket))
        d.append(rect("front", x, r_ + 1, eye_w, 1, eye))
    if pupil:
        d.append(rect("front", lx + eye_w - 1, r_ + 1, 1, 1, pupil))
        d.append(rect("front", rx, r_ + 1, 1, 1, pupil))
    c0 = w // 2 - 1
    if nose and r_ + 2 < h:
        d.append(rect("front", c0, r_ + 2, 2, 1, nose))
    if nostril and r_ + 3 < h:
        d.append(rect("front", c0 - 1 if w > 6 else c0, r_ + 3, 1, 1, nostril))
        d.append(rect("front", c0 + 2 if w > 6 else c0 + 1, r_ + 3, 1, 1, nostril))
    if cheek and r_ + 3 < h:
        d.append(rect("front", lx, r_ + 3, 1, 1, cheek))
        d.append(rect("front", rx + eye_w - 1, r_ + 3, 1, 1, cheek))
    if mouth:
        my = h - 1
        d.append(rect("front", 2, my, w - 4, 1, mouth))
        if teeth:
            for x in range(2, w - 2, 2):
                d.append(rect("front", x, my - 1, 1, 1, teeth))
    return d


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

    def scaled(self, k):
        """A copy of this rig with every pivot, box position, box size and grow multiplied by k (a pony from a horse)."""
        out = Rig(self.paints)
        for p in self.parts:
            out.part(p["name"], p["parent"], [v * k for v in p["pivot"]], p["rot"], [
                {**b, "from": [v * k for v in b["from"]], "size": [max(0.2, v * k) for v in b["size"]], "grow": b.get("grow", 0) * k} for b in p["boxes"]])
        out.anims = [dict(a) for a in self.anims]
        return out

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


    # ---------- a finely shaped four-legged beast (wolf, hound, boar, big cat) ----------
    def quadruped(self, fur, belly=None, mane=None, claw=None, nose=None, body=(8, 8, 17), head=(7, 6, 6), snout=(4, 3.4, 5.5), leg_w=3.0,
                  front=(6.5, 6, 3), hind=(6.5, 6.5, 3), tail=None, ears=(2.2, 3.4), neck=(5.5, 6, 5), walk=0.9, eye="#ffd040", eye_glow=None,
                  fangs=True, jaw_open=8, front_pose=(8, -8, 0), hind_pose=(-24, 42, -20), neck_rot=48, mane_len=0.45, ruff=True, tail_rot=100, hoof_paint=None, extra=None, head_drop=6):
        """Builds a lean body with a deeper chest and a mane, a neck, a head with a stepped snout, jaw, ears and fangs, four legs of three
        segments (thigh, lower leg, paw) in a diagonal walk, and an optional tail chain. The hip height is solved from the leg angles so the
        paws meet the ground. Returns the part names."""
        bw, bh, bl = body
        hw, hh, hd = head
        sw, sh, sl = snout
        belly = belly or fur
        mane = mane or fur
        n = {}

        def drop(seg, pose):
            """Vertical drop of a three-segment leg given its relative x rotations (degrees)."""
            ang, tot = 0.0, 0.0
            for ln, rx in zip(seg, pose):
                ang += rx
                tot += ln * math.cos(math.radians(ang))
            return tot
        fd = drop(front, front_pose)
        hd_ = drop(hind, hind_pose)
        hip = -max(fd, hd_) - 0.6            # the body's underside sits this high; the shorter leg is lifted by its pose
        # body: the lean barrel, a deeper chest, a mane over the shoulders, a belly stripe
        n["body"] = self.part("body", "root", (0, hip, 0), (0, 0, 0), [
            box((-bw / 2, -bh, -bl / 2 + 3), (bw, bh, bl - 3), fur), box((-bw / 2 + 0.6, -0.2, -bl / 2 + 3.4), (bw - 1.2, 1.4, bl - 3.8), belly, 0.0)])
        n["chest"] = self.part("chest", "body", (0, 0, -bl / 2 + 3), (0, 0, 0), [
            box((-bw / 2 - 0.7, -bh - 0.4, -3.2), (bw + 1.4, bh + 1.4, 6.4), fur), box((-bw / 2 + 0.3, 0.2, -2.8), (bw - 0.6, 1.4, 5.6), belly)])
        if ruff:
            n["mane"] = self.part("mane", "chest", (0, -bh - 0.2, -0.5), (-6, 0, 0), [
                box((-bw / 2 - 0.4, -2.4, -2.6), (bw + 0.8, 2.6, 5.4), mane), box((-1.4, -3.4, -1.8), (2.8, 1.2, 4.2), mane, 0.0)])
            self.anim("mane", "sway", axis="z", amp=0.02, freq=0.07)
        # neck and head
        nw, nl, nd = neck
        n["neck"] = self.part("neck", "chest", (0, -bh + 1.4, -2.2), (neck_rot, 0, 0), [box((-nw / 2, -nl, -nd / 2), (nw, nl, nd), fur), box((-nw / 2 - 0.4, -nl + 0.4, -nd / 2 - 0.3), (nw + 0.8, nl * 0.55, nd + 0.6), mane, 0.0)])
        eyes = face(hw, hh, eye=eye_glow or eye, socket="#0c0c0e", brow="#1a1a1e", nostril=None, eye_row=2, eye_w=max(1, int(hw // 3)), gap=0)
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


    # ---------- a finely shaped four-legged beast (wolf, hound, boar, big cat) ----------
    def quadruped(self, fur, belly=None, mane=None, claw=None, nose=None, body=(8, 8, 17), head=(7, 6, 6), snout=(4, 3.4, 5.5), leg_w=3.0,
                  front=(6.5, 6, 3), hind=(6.5, 6.5, 3), tail=None, ears=(2.2, 3.4), neck=(5.5, 6, 5), walk=0.9, eye="#ffd040", eye_glow=None,
                  fangs=True, jaw_open=8, front_pose=(8, -8, 0), hind_pose=(-24, 42, -20), neck_rot=48, mane_len=0.45, ruff=True, tail_rot=100, hoof_paint=None, extra=None, head_drop=6):
        """Builds a lean body with a deeper chest and a mane, a neck, a head with a stepped snout, jaw, ears and fangs, four legs of three
        segments (thigh, lower leg, paw) in a diagonal walk, and an optional tail chain. The hip height is solved from the leg angles so the
        paws meet the ground. Returns the part names."""
        bw, bh, bl = body
        hw, hh, hd = head
        sw, sh, sl = snout
        belly = belly or fur
        mane = mane or fur
        n = {}

        def drop(seg, pose):
            """Vertical drop of a three-segment leg given its relative x rotations (degrees)."""
            ang, tot = 0.0, 0.0
            for ln, rx in zip(seg, pose):
                ang += rx
                tot += ln * math.cos(math.radians(ang))
            return tot
        fd = drop(front, front_pose)
        hd_ = drop(hind, hind_pose)
        hip = -max(fd, hd_) - 0.6            # the body's underside sits this high; the shorter leg is lifted by its pose
        # body: the lean barrel, a deeper chest, a mane over the shoulders, a belly stripe
        n["body"] = self.part("body", "root", (0, hip, 0), (0, 0, 0), [
            box((-bw / 2, -bh, -bl / 2 + 3), (bw, bh, bl - 3), fur), box((-bw / 2 + 0.6, -0.2, -bl / 2 + 3.4), (bw - 1.2, 1.4, bl - 3.8), belly, 0.0)])
        n["chest"] = self.part("chest", "body", (0, 0, -bl / 2 + 3), (0, 0, 0), [
            box((-bw / 2 - 0.7, -bh - 0.4, -3.2), (bw + 1.4, bh + 1.4, 6.4), fur), box((-bw / 2 + 0.3, 0.2, -2.8), (bw - 0.6, 1.4, 5.6), belly)])
        if ruff:
            n["mane"] = self.part("mane", "chest", (0, -bh - 0.2, -0.5), (-6, 0, 0), [
                box((-bw / 2 - 0.4, -2.4, -2.6), (bw + 0.8, 2.6, 5.4), mane), box((-1.4, -3.4, -1.8), (2.8, 1.2, 4.2), mane, 0.0)])
            self.anim("mane", "sway", axis="z", amp=0.02, freq=0.07)
        # neck and head
        nw, nl, nd = neck
        n["neck"] = self.part("neck", "chest", (0, -bh + 1.4, -2.2), (neck_rot, 0, 0), [box((-nw / 2, -nl, -nd / 2), (nw, nl, nd), fur), box((-nw / 2 - 0.4, -nl + 0.4, -nd / 2 - 0.3), (nw + 0.8, nl * 0.55, nd + 0.6), mane, 0.0)])
        ew_ = max(1, int(hw // 3))
        eyes = [rect("front", 0, 2, ew_, 1, "#101010"), rect("front", int(math.ceil(hw)) - ew_, 2, ew_, 1, "#101010"), rect("front", 0, 3, ew_, 1, eye_glow or eye), rect("front", int(math.ceil(hw)) - ew_, 3, ew_, 1, eye_glow or eye)]
        n["head"] = self.part("head", "neck", (0, -nl + 0.6, 0.3), (-neck_rot + head_drop, 0, 0), [
            box((-hw / 2, -hh / 2, -hd + 1.5), (hw, hh, hd), fur, 0.0, eyes), box((-hw / 2 - 0.5, -hh / 2 + 1.5, -hd / 2 + 1.5), (hw + 1.0, hh - 2.0, 2.5), mane)])
        self.anim("head", "look", amount=0.8)
        n["snout"] = self.part("snout", "head", (0, 0.4, -hd + 1.5), (0, 0, 0), [
            box((-sw / 2, -sh / 2, -sl), (sw, sh - 0.9, sl), fur), box((-sw / 2 + 0.3, sh / 2 - 1.2, -sl + 0.3), (sw - 0.6, 0.6, sl - 0.6), belly)])
        n["nose"] = self.part("nose", "snout", (0, -sh / 2 + 0.3, -sl + 0.2), (0, 0, 0), [box((-sw / 2 + 0.7, -0.4, -1.1), (sw - 1.4, 1.5, 1.4), nose or fur)])
        n["jaw"] = self.part("jaw", "head", (0, sh / 2 - 0.6, -hd / 2 + 1), (jaw_open, 0, 0), [
            box((-sw / 2 + 0.3, 0, -sl - 0.5), (sw - 0.6, 1.3, sl + 0.5), belly)])
        if fangs:
            for sx in (-1, 1):
                self.part(f"fang_{'l' if sx > 0 else 'r'}", "snout", (sx * (sw / 2 - 0.8), sh / 2 - 0.5, -sl + 1.2), (0, 0, 0), [box((-0.35, 0, -0.35), (0.7, 1.8, 0.7), claw or "bone")])
                self.part(f"lfang_{'l' if sx > 0 else 'r'}", "jaw", (sx * (sw / 2 - 0.9), 0.1, -sl + 0.2), (0, 0, 0), [box((-0.3, -1.4, -0.3), (0.6, 1.4, 0.6), claw or "bone")])
        ew, eh = ears
        for sx in (-1, 1):
            side = "l" if sx > 0 else "r"
            self.part(f"ear_{side}", "head", (sx * (hw / 2 - 1.1), -hh / 2 + 0.2, -hd / 2 + 2.2), (-8, 0, sx * -10), [
                box((-ew / 2, -eh, -0.6), (ew, eh, 1.2), fur), box((-ew / 2 + 0.5, -eh + 0.5, -0.65), (ew - 1.0, eh - 1.0, 0.4), belly, 0.0)])
            self.anim(f"ear_{side}", "sway", axis="z", amp=0.05, freq=0.11, phase=0 if sx > 0 else 2.0)
        # four legs (plus any extra pairs): thigh, lower leg, paw (+ claws)
        def leg(who, seg, pose, z, w, flip):
            for sx in (-1, 1):
                side = "l" if sx > 0 else "r"
                k = f"{who}{side}"
                hind = who == "b"
                x = sx * (bw / 2 - w / 2 + (0.4 if hind else 0.2))
                self.part(f"leg_{k}", "body", (x, -1.4 if hind else -0.5, z), (pose[0], 0, 0), [
                    box((-w / 2, 0, -w / 2 - (0.4 if hind else 0)), (w, seg[0], w + (0.8 if hind else 0)), fur)])
                self.part(f"shin_{k}", f"leg_{k}", (0, seg[0] - 0.4, 0), (pose[1], 0, 0), [box((-w / 2 + 0.4, 0, -w / 2 + 0.4), (w - 0.8, seg[1], w - 0.8), fur)])
                self.part(f"paw_{k}", f"shin_{k}", (0, seg[1] - 0.3, 0), (pose[2], 0, 0), [
                    box((-w / 2 - 0.1, 0, -w / 2 - 1.4), (w + 0.2, 1.4 if seg[2] <= 3 else seg[2] - 2, w + 1.6), hoof_paint or fur),
                    box((-w / 2 - 0.1, 0.9, -w / 2 - 1.8), (w + 0.2, 0.5, 0.6), claw or "bone")])
                ph = (0.0 if (side == "l") != flip else math.pi)
                self.anim(f"leg_{k}", "walk", axis="x", amp=walk, phase=ph)
                self.anim(f"shin_{k}", "walk", axis="x", amp=-walk * 0.4, phase=ph + 1.0)
        leg("f", front, front_pose, -bl / 2 + 4.2, leg_w, False)
        leg("b", hind, hind_pose, bl / 2 - 1.6, leg_w + 0.4, True)
        for ex in (extra or []):
            leg(ex["tag"], ex.get("seg", front), ex.get("pose", front_pose), ex["z"], leg_w + ex.get("grow", 0.2), ex.get("flip", False))
        if tail:
            segs = tail["segs"]
            first = self.chain("tail", "body", (0, -bh + 1.5, bl / 2 - 0.5), [(segs[0][0], segs[0][1], segs[0][2], tail_rot, 0)] + [(a, b, c, d, 0) for a, b, c, d in segs[1:]],
                               tail.get("paint", fur), sway="z", amp=0.12, freq=0.13, walk_amp=0.15)
            n["tail"] = first
        return n


    # ---------- a riding horse (and variants: winged, many-legged) ----------
    def horse(self, coat, mane, belly=None, hoof=None, nose=None, saddle="saddle", trim="trim", eye="#2a1c10", eye_glow=None, tail_paint=None, extra=None, body=(9, 9.5, 22), scale_legs=1.0, head_drop=20):
        """A saddled riding horse built on quadruped(): a long arched neck with a mane down its back, a long head with a forelock, a deep chest,
        long legs with hooves, a hanging tail and a saddle with stirrups on the back. Returns the part names; `extra` adds leg pairs (Sleipnir's eight)."""
        sl = lambda t: tuple(round(v * scale_legs, 2) for v in t)
        n = self.quadruped(coat, belly=belly or coat, mane=mane, claw=hoof or "hoof", nose=nose or hoof or "hoof", body=body, head=(5.4, 6.2, 7), snout=(4.0, 4.2, 7), leg_w=3.4, ears=(1.8, 3.2),
                           neck=(5.6, 12, 6.4), neck_rot=34, front=sl((7, 7, 2.6)), hind=sl((7, 7.8, 2.6)), front_pose=(4, -4, 0), hind_pose=(-18, 34, -16), walk=0.8, eye=eye, eye_glow=eye_glow,
                           fangs=False, jaw_open=2, ruff=False, hoof_paint=hoof or "hoof", extra=extra, head_drop=head_drop,
                           tail={"segs": [(5, 2.4, 2.4, 0), (6, 3.2, 3.2, -4), (6, 3.0, 3.0, -4), (5, 2.0, 2.0, -4)], "paint": tail_paint or mane}, tail_rot=30)
        bw, bh, bl = body
        nw, nl, nd = 5.6, 12, 6.4
        for p_ in self.parts:
            if p_["name"] == "neck":
                p_["boxes"].append(box((-0.9, -nl - 0.2, nd / 2 - 0.4), (1.8, nl + 0.6, 2.4), mane))              # the mane down the back of the neck
                p_["boxes"].append(box((-nw / 2 + 0.3, -3, -nd / 2 - 0.8), (nw - 0.6, 5.5, 1.2), coat))           # the throat
            if p_["name"] == "head":
                p_["boxes"].append(box((-1.2, -3.6, -6.4), (2.4, 2.0, 1.8), mane))                                # the forelock
            if p_["name"] == "body":
                p_["boxes"].append(box((-bw / 2 - 0.4, -bh - 0.9, -5.0), (bw + 0.8, 1.2, 9), saddle))             # the saddle
                p_["boxes"].append(box((-bw / 2 - 0.5, -bh - 1.6, -5.4), (bw + 1.0, 1.0, 1.8), trim))             # pommel and cantle
                p_["boxes"].append(box((-bw / 2 - 0.5, -bh - 1.6, 3.4), (bw + 1.0, 1.0, 1.8), trim))
                p_["boxes"].append(box((-bw / 2 - 0.8, -bh * 0.2, -2.0), (bw + 1.6, 0.8, 5), trim))                # the girth blanket
        return n

    def wings(self, parent, pivot_y, pivot_z, paint, light, span=(9, 9), feathers=6, flen=15, flap=0.8, spread=1.0, shoulder_x=3.5, raise_=1.3, curl=0.55):
        """A pair of feathered wings: an arm, a forearm and a fan of long primaries, that beat while the entity is off the ground; on the ground they
        stand raised (an angel's pose: the arm up, the forearm curled outward). The raised pose is the model's own pose and the `wing` animation undoes it in the
        air. Positive x is the left wing."""
        for side, sx in (("l", 1), ("r", -1)):
            a, b_ = span
            x0 = lambda ln: 0 if sx > 0 else -ln
            fz, fz2 = sx * -raise_, sx * curl
            self.part(f"wing_{side}", parent, (sx * shoulder_x, pivot_y, pivot_z), (0, 0, math.degrees(fz)), [box((x0(a), -0.9, -2.6), (a, 1.8, 5.4), paint), box((x0(a - 0.4), -1.3, -2.4), (a - 0.4, 0.6, 4.8), light, 0.0)])
            self.part(f"wing_{side}2", f"wing_{side}", (sx * a, 0, 0), (0, 0, math.degrees(fz2)), [box((x0(b_), -0.8, -2.4), (b_, 1.6, 5.0), paint)])
            for i in range(feathers):
                ln = flen - abs(i - feathers * 0.35) * 0.9
                self.part(f"prim_{side}{i}", f"wing_{side}2", (sx * (b_ - 0.4), 0, 2.2 - i * (4.6 / max(1, feathers - 1))), (0, sx * (-5 + i * 3 * spread), 0), [box((x0(ln), -0.4, -0.9), (ln, 0.8, 1.9), paint if i % 2 else light)])
            self.anim(f"wing_{side}", "wing", axis="z", amp=flap * sx, freq=1.0, phase=0, air=-fz)
            self.anim(f"wing_{side}2", "wing", axis="z", amp=flap * 0.55 * sx, freq=1.0, phase=0.9, air=-fz2)


def merge(into, other, prefix, dx=0.0, dz=0.0, dy=0.0, rot=(0, 0, 0)):
    """Copy another Rig's parts into this one under a wrapper part `<prefix>` placed at (dx, dy, dz): two horses drawn from one builder."""
    into.part(prefix, "root", (dx, dy, dz), rot, [])
    for p in other.parts:
        into.part(prefix + p["name"], prefix if p["parent"] == "root" else prefix + p["parent"], p["pivot"], p["rot"], p["boxes"])
    for a in other.anims:
        into.anims.append({**a, "part": prefix + a["part"]})


def mirror(v):
    return [-v[0], v[1], v[2]]
