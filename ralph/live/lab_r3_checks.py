#!/usr/bin/env python3
"""Round 3 offline checks (owner 2026-11-08 5:18 PM look at the round-2 build), over a shape-lab world and its laid output, plus the
mod's textures. Runs here on files, no game.

    python3 ralph/live/lab_r3_checks.py WORLD.json LAID.json [--tex TEXTURES_DIR] [--json OUT]

Counts (each must be 0):
  side_entry    side-view plugs lying against a power strip's edge ("power strips don't plug into the sides, they plug in from above")
  uncovered     strip sockets a cord ends at with no face-on plug (PlugTop) centred on them
  wall_no_plug  Modern (strip-look) wall entries drawn as a hole plate, not an outlet with a seated plug
  dead_end      strand ends at no port, decal, machine, wall face, fray or other strand end
  undrawn       transmitter buildings ('t' ids) on a net through a touching drawn transmitter that no strand reaches
  baked_stub    (--tex) decal textures whose opaque pixels run where the code draws the cord: behind a plug's boot, from a wall/rock
                stub's cord side, past a junction arm's tuck point (a cord baked into the art)
Exit 1 when any count is non-zero.
"""
import argparse, glob, json, math, os, sys

STRIP_HEADS, STRIP_HEAD_Z, STRIP_LEAD = [-0.328, -0.128, 0.065, 0.264], -0.049, (0.39, -0.05)
PLUGTOP_REACH = 0.1445
ARM_TUCK = 0.40


def rot(x, z, a):
    return x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)


def strip_pt(d, x, z):
    _, px, pz, a, s = d[:5]
    ax, az = math.cos(a), math.sin(a)
    sx, sz = -az, ax                     # V2.Perp
    return px + ax * x * s + sx * z * s, pz + az * x * s + sz * z * s


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def lab_checks(W, L):
    out, msgs = {}, []
    decals = [d for p in L["pieces"] for d in p["decals"]]
    ends = []
    for p in L["pieces"]:
        for s in p["strands"]:
            if len(s) >= 2:
                ends.append(tuple(s[0][:2])); ends.append(tuple(s[-1][:2]))
    strips = [d for d in decals if d[0] in ("PowerStrip", "PowerStripDark")]
    # side_entry: a side-view plug whose head (art +0.46) pushes into a strip's outline (+0.05): plugged into the strip's edge
    side = 0
    for d in decals:
        if d[0] != "Plug":
            continue
        hx, hz = d[1] + math.cos(d[3]) * 0.46 * d[4], d[2] + math.sin(d[3]) * 0.46 * d[4]
        if any(m["x"] <= hx <= m["x"] + m["w"] and m["z"] <= hz <= m["z"] + m["h"] for m in W["machines"]):
            continue                      # a machine's own plug, drawn under its building
        for st in strips:
            ux, uz = hx - st[1], hz - st[2]
            al = ux * math.cos(st[3]) + uz * math.sin(st[3]); ac = -ux * math.sin(st[3]) + uz * math.cos(st[3])
            if abs(al) <= 0.45 * st[4] + 0.05 and abs(ac) <= 0.09 * st[4] + 0.05:
                side += 1; msgs.append(f"side_entry plug at ({d[1]:.2f},{d[2]:.2f})"); break
    out["side_entry"] = side
    # uncovered: an occupied socket (a cord end within 0.18 of it, not on the lead) with no PlugTop centred on it
    unc = 0
    tops = [d for d in decals if d[0] == "PlugTop"]
    for st in strips:
        lead = strip_pt(st, *STRIP_LEAD)
        for k, hx in enumerate(STRIP_HEADS):
            sk = strip_pt(st, hx, STRIP_HEAD_Z)
            occ = [e for e in ends if dist(e, sk) < 0.18 and dist(e, lead) > 0.05]
            if not occ:
                continue
            if not any(dist((t[1], t[2]), sk) < 0.02 for t in tops):
                unc += 1; msgs.append(f"uncovered socket {k} of strip at ({st[1]:.2f},{st[2]:.2f})")
    out["uncovered"] = unc
    # wall_no_plug: a strip-look wall stub drawn with the hole plate
    strip_cells = {tuple(c) for c in W.get("strips", [])}
    wnp = 0
    for p in L["pieces"]:
        for nm in (p["a"], p["b"]):
            if not nm.startswith("stub_wall:"):
                continue
            x, z = (int(v) for v in nm.split(":")[1].split(","))
            if (x, z) not in strip_cells:
                continue
            if any(d[0] in ("FrayLive", "FrayDead") for d in p["decals"]):
                continue                      # a cut wall terminal hangs loose by design
            near = [d for d in p["decals"] if d[0] in ("StubWall", "WallOutlet") and abs(d[1] - (x + 0.5)) < 1.2 and abs(d[2] - (z + 0.5)) < 1.2]
            if not any(d[0] == "WallOutlet" for d in near):
                wnp += 1; msgs.append(f"wall_no_plug at {nm}")
    out["wall_no_plug"] = wnp
    # dead_end
    mach = W["machines"]
    blocked = {(b[0], b[1]) for b in W["blocked"]}

    def explained(e, i):
        if any(m["x"] - 0.15 <= e[0] <= m["x"] + m["w"] + 0.15 and m["z"] - 0.15 <= e[1] <= m["z"] + m["h"] + 0.15 for m in mach):
            return True
        if (math.floor(e[0]), math.floor(e[1])) in blocked or any((math.floor(e[0] + dx), math.floor(e[1] + dz)) in blocked for dx, dz in ((0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1))):
            return True
        for d in decals:
            if dist(e, (d[1], d[2])) <= 0.5 * d[4] + 0.12:
                return True
        return any(j != i and dist(e, f) < 0.05 for j, f in enumerate(ends))
    dead = [e for i, e in enumerate(ends) if not explained(e, i)]
    out["dead_end"] = len(dead)
    msgs += [f"dead_end at ({e[0]:.2f},{e[1]:.2f})" for e in dead[:20]]
    # undrawn transmitters
    def touch(a, b):
        ox = a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]; oz = a["z"] < b["z"] + b["h"] and b["z"] < a["z"] + a["h"]
        tx = a["x"] + a["w"] == b["x"] or b["x"] + b["w"] == a["x"]; tz = a["z"] + a["h"] == b["z"] or b["z"] + b["h"] == a["z"]
        return (oz and tx) or (ox and tz)
    ts = [m for m in mach if m["id"].startswith("t")]
    fed = [m for m in ts if not m["hookups"] and not m.get("links") and any(o is not m and (o["hookups"] or o.get("links")) and touch(m, o) for o in ts)]
    und = 0
    for m in fed:
        if not any(m["x"] - 0.2 <= e[0] <= m["x"] + m["w"] + 0.2 and m["z"] - 0.2 <= e[1] <= m["z"] + m["h"] + 0.2 for e in ends):
            und += 1; msgs.append(f"undrawn transmitter {m['id']} at {m['x']},{m['z']}")
    out["undrawn"] = und
    return out, msgs


def baked(tex):
    from PIL import Image
    import numpy as np
    bad, msgs = 0, []
    for p in sorted(glob.glob(os.path.join(tex, "**", "*.png"), recursive=True)):
        n = os.path.basename(p)[:-4]
        if n not in ("Plug", "StubWall", "StubRock", "Junction_T", "Junction_X", "Junction_Tape", "Junction_Tin"):
            continue
        a = np.array(Image.open(p).convert("RGBA"))[..., 3] > 100
        H, Wd = a.shape
        if n == "Plug":
            hit = a[:, : int(0.15 * Wd)].sum()              # behind the boot, where the code's cord runs in
        elif n in ("StubWall", "StubRock"):
            hit = a[:, : int(0.06 * Wd)].sum()              # the cord side (art -X): the plate / rim never reaches the canvas edge
        else:
            cy = H / 2 + (0.152 * H if n in ("Junction_T", "Junction_Tape") else 0)   # the T's arms meet above the centre (TapeAnchorZ, art +Z = up)
            cy = H / 2 - 0.152 * H if n in ("Junction_T", "Junction_Tape") else H / 2
            r = (ARM_TUCK + 0.04) * Wd
            yy, xx = np.mgrid[0:H, 0:Wd]
            hit = (a & (np.hypot(xx - Wd / 2, yy - cy) > r)).sum()
        if hit > 0:
            bad += 1; msgs.append(f"baked_stub {os.path.relpath(p, tex)}: {int(hit)} px")
    return bad, msgs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("world"); ap.add_argument("laid")
    ap.add_argument("--tex"); ap.add_argument("--json")
    a = ap.parse_args()
    out, msgs = lab_checks(json.load(open(a.world)), json.load(open(a.laid)))
    if a.tex:
        out["baked_stub"], m2 = baked(a.tex); msgs += m2
    print(" ".join(f"{k}={v}" for k, v in out.items()))
    for m in msgs[:40]:
        print("  " + m)
    if a.json:
        json.dump({"counts": out, "msgs": msgs}, open(a.json, "w"), indent=1)
    sys.exit(1 if any(out.values()) else 0)
