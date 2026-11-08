#!/usr/bin/env python3
"""stage_beast_grid.py -- one of every beast OUR mods ship, in a labelled penned grid, for a fast art-acceptance pass.

Owner, 2026-11-08: "make a grid of all the beasts in the game for a fast art acceptance pass".

Three modes, because WSL python cannot reach the bridge and Windows python cannot read the mod folders the
same way (it can, but the def scan is the slow offline part and belongs in WSL):

    python3    stage_beast_grid.py --build-roster          offline: scan the defs of the ACTIVE mod list (ModsConfig.xml)
                                                           and of every installed mandrake.* mod; writes roster.json
    python3    stage_beast_grid.py --dry-run               prints the planned layout + writes KEY.md (no bridge)
    python.exe stage_beast_grid.py --apply                 LIVE: stage the grid on the current map (needs the bridge)
    python.exe stage_beast_grid.py --restore-settings      put threatScale / allowBigThreats back to what they were

Files (all under D:\\ClaudeWork\\rimmandrake\\beast_grid\\): roster.json, KEY.md, prior_difficulty.json, last_apply.json.

THE ROSTER. A "beast" is any ThingDef that declares its own <race> in a mod whose packageId starts `mandrake.`
(prefixes RM_/RSW_/RUT_ plus the JOE_/VAEWaste_/SWPotF_ defs our rut.patches / armoury mods ship), non-abstract, with at
least one PawnKindDef pointing at it. The def set is resolved by def_inventory.py (inheritance merged) from the game's
Mods folder -- an OFFLINE scan, not the live RimDefDump. XML PatchOperations are NOT applied, so a def another patch
deletes at load would still be listed. The tier list is whatever ModsConfig.xml says at build time.

THE STAGE (order is the trap list from skills/rimworld-live-review):
  1. refuse unless the clock is PAUSED (ticksGame read twice). This script NEVER touches game speed -- the owner runs it.
  2. raids off: jawa/difficulty_tune threatScale=0 allowBigThreats=False (prior values saved), incident_queue_clear.
  3. remove hostiles, clear_area over the grid rect (refuses if a player colonist stands in it), unfog, paint ground.
  4. one build_batch per row: 4 orthogonal walls around each creature's cell. Orthogonal walls are enough: the engine
     does not let a pawn squeeze diagonally between two blocked orthogonals.
  5. spawn each creature standing (wild, faction none) in its pen; a Colonist human at each row's start, drafted so he
     holds still, for scale. Flyers are spawned standing; flight is never exercised.
  6. face everyone south, pin a review_label above each pen "r01c03 label", read the pawn list back and report holes.
"""
import argparse
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

WORK_WSL = "/mnt/d/ClaudeWork/rimmandrake/beast_grid"
WORK_WIN = "D:\\ClaudeWork\\rimmandrake\\beast_grid"
WORK = WORK_WIN if os.name == "nt" else WORK_WSL
ROSTER = os.path.join(WORK, "roster.json")
KEYMD = os.path.join(WORK, "KEY.md")
PRIOR = os.path.join(WORK, "prior_difficulty.json")
LASTRUN = os.path.join(WORK, "last_apply.json")
TAG = "beast_grid"
OURS = "mandrake."
DLC_BASE = ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology",
            "ludeon.rimworld.biotech", "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"]


# ------------------------------------------------------------------ roster (offline, WSL)
def _floats(s):
    return [float(v) for v in re.findall(r"[-+]?\d*\.?\d+", s or "")]


def _art_index():
    """-> (rel_stem -> latest live sha, sha -> (verdict, by)). From the art ledger events; best effort."""
    events_dir = os.path.join(HERE, "..", "..", "..", "infrastructure", "state", "art", "events")
    live, ruled = {}, {}
    if not os.path.isdir(events_dir):
        return live, ruled
    rows = []
    for fn in sorted(os.listdir(events_dir)):
        if not fn.endswith(".jsonl"):
            continue
        with open(os.path.join(events_dir, fn), encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"type":"live"' in line or '"type":"ruling"' in line:
                    try:
                        rows.append(json.loads(line))
                    except ValueError:
                        pass
    rows.sort(key=lambda e: e.get("ts") or "")
    for e in rows:
        if e.get("type") == "live" and e.get("rel"):
            stem = re.sub(r"_(north|south|east|west)?\.png$|\.png$", "", e["rel"].replace("\\", "/").split("/")[-1])
            stem = re.sub(r"_(north|south|east|west)$", "", stem)
            live[(stem, "south" in e["rel"].lower() or "")] = e.get("sha")
            live[(stem, "")] = e.get("sha")
        elif e.get("type") == "ruling":
            sha = (e.get("target") or {}).get("sha")
            if sha:
                ruled[sha] = (e.get("verdict"), e.get("by"), e.get("trust"))
    return live, ruled


def art_status(stems, live, ruled):
    for stem in stems:
        sha = live.get((stem, True)) or live.get((stem, ""))
        if sha:
            v = ruled.get(sha)
            return ("%s (%s)" % (v[0], v[1])) if v else "installed, no ruling on this image"
    return "art ledger has no install for this texture"


def build_roster():
    import xml.etree.ElementTree as ET
    import tempfile
    import def_inventory as di
    from game_paths import LOCAL_MODS, MODS_CONFIG

    ours = []
    for d in sorted(os.listdir(LOCAL_MODS)):
        p = os.path.join(LOCAL_MODS, d, "About", "About.xml")
        if os.path.exists(p):
            m = re.search(r"<packageId>([^<]+)", open(p, encoding="utf-8", errors="replace").read())
            if m and m.group(1).lower().startswith(OURS):
                ours.append(m.group(1).lower())
    root = ET.parse(MODS_CONFIG).getroot()
    active = [e.text.strip().lower() for e in root.find("activeMods")]
    tier_ids = [a for a in active if a.startswith(OURS)]
    cfg_ids = list(DLC_BASE) + sorted(set(ours) | set(tier_ids))
    cfg = ("<ModsConfigData><version>1.6</version><activeMods>%s</activeMods><knownExpansions>%s</knownExpansions>"
           "</ModsConfigData>") % ("".join("<li>%s</li>" % i for i in cfg_ids),
                                   "".join("<li>%s</li>" % i for i in DLC_BASE[2:]))
    tmp = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False)
    tmp.write(cfg)
    tmp.close()
    ds = di.build(config=tmp.name, types=["ThingDef", "PawnKindDef"], quiet=True)
    os.unlink(tmp.name)
    order = {m["packageId"].lower(): i for i, m in enumerate(ds.mods)}

    kinds = {}
    for r in ds.of_type("PawnKindDef"):
        if r.isAbstract:
            continue
        race = (r.element.findtext("race") or "").strip()
        kinds.setdefault(race, []).append(r)

    live, ruled = _art_index()
    recs = []
    for r in ds.of_type("ThingDef"):
        pid = r.packageId.lower()
        if r.isAbstract or not pid.startswith(OURS) or r.own.find("race") is None:
            continue
        ks = sorted(kinds.get(r.defName, []), key=lambda k: (k.defName != r.defName, k.defName))
        if not ks:
            continue
        kind = ks[0]
        el = r.element
        stages = kind.element.findall("lifeStages/li")
        draw = 0.0
        for st in stages[-1:]:
            draw = max(_floats(st.findtext("bodyGraphicData/drawSize")) or [0.0])
        body = float((el.findtext("race/baseBodySize") or "1").strip() or 1)
        if not draw:
            draw = round(body * 1.5, 2)
        stems = [r.defName]
        for st in stages:
            tp = (st.findtext("bodyGraphicData/texPath") or "").strip()
            if tp:
                stems.insert(0, tp.replace("\\", "/").split("/")[-1])
        own_text = ET.tostring(r.own, encoding="unicode")
        recs.append({
            "def": r.defName, "kind": kind.defName, "kinds": [k.defName for k in ks],
            "label": (el.findtext("label") or r.defName).strip(),
            "pkg": pid, "mod": r.modName, "onTier": pid in tier_ids,
            "draw": round(draw, 2), "body": body,
            "intel": (el.findtext("race/intelligence") or "Animal (default)").strip(),
            "flyer": bool(re.search(r"flyingAnimation|FlightTracker|CompProperties_Flyer|flies", own_text, re.I)),
            "art": art_status(stems, live, ruled),
        })
    recs.sort(key=lambda d: (order.get(d["pkg"], 999), d["draw"], d["body"], d["def"]))
    out = {
        "built": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "def_inventory offline scan of the game Mods folder, resolved load set (%d mods); XML patches NOT applied"
                  % len(ds.mods),
        "tierModsConfig": tier_ids, "activeCount": len(active), "modOrder": order,
        "beasts": recs,
    }
    os.makedirs(WORK, exist_ok=True)
    with open(ROSTER, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    on = [b for b in recs if b["onTier"]]
    print("roster: %d beasts overall, %d on the active tier, %d NOT on it -> %s" % (len(recs), len(on), len(recs) - len(on), ROSTER))
    by = {}
    for b in recs:
        by.setdefault((b["pkg"], b["onTier"]), []).append(b)
    for (pkg, t), v in sorted(by.items(), key=lambda kv: (not kv[0][1], kv[0][0])):
        print("  %-42s %-8s %d" % (pkg, "TIER" if t else "off-tier", len(v)))
    return out


# ------------------------------------------------------------------ layout (pure)
def fit_layout(beasts, per_row, origin, map_w, map_h):
    """plan_layout, widening the rows (+2 per try, up to 40) until the grid fits the map. -> (layout, per_row used)."""
    pr = per_row
    while True:
        lay = plan_layout(beasts, pr, origin)
        ox, oz, w, h = lay["rect"]
        if (ox + w <= map_w - 2 and oz + h <= map_h - 2) or pr >= 40:
            return lay, pr
        pr += 2


def plan_layout(beasts, per_row=10, origin=(6, 6), only_tier=True):
    """-> dict(rows=[...], cells=[...], width, height). Rows break at every mod change; within a mod, small -> large.

    Column 0 of every row is the scale human. x grows right; row 1 is at the TOP (highest z), so reading order on
    screen is reading order in the key. Pitch is per row: the bigger the biggest creature in the row, the wider."""
    items = [b for b in beasts if b["onTier"] or not only_tier]
    groups = []
    for b in items:
        if not groups or groups[-1][0] != b["pkg"]:
            groups.append((b["pkg"], []))
        groups[-1][1].append(b)
    rows = []
    for pkg, bs in groups:
        for i in range(0, len(bs), per_row):
            rows.append((pkg, bs[i:i + per_row], i == 0))
    ox, oz = origin
    # first pass: pitch and height of each row
    meta = []
    for pkg, bs, first in rows:
        big = max(b["draw"] for b in bs)
        pitch = int(max(3, min(12, math.ceil(big) + 1)))
        meta.append((pitch, pitch + 1))
    height = sum(m[1] for m in meta) + 4
    width = max(m[0] * (len(r[1]) + 1) for m, r in zip(meta, rows)) + 3
    z = oz + height - 3
    cells, row_out = [], []
    for ri, ((pkg, bs, first), (pitch, zstep)) in enumerate(zip(rows, meta), 1):
        z -= zstep
        x = ox + 2
        human = {"row": ri, "col": 0, "x": x, "z": z, "pkg": pkg, "first": first, "pitch": pitch}
        row_out.append(human)
        for ci, b in enumerate(bs, 1):
            cx = x + ci * pitch
            cells.append({"id": "r%02dc%02d" % (ri, ci), "row": ri, "col": ci, "x": cx, "z": z, "pitch": pitch, **b})
    return {"rows": row_out, "cells": cells, "width": width, "height": height, "origin": origin,
            "rect": (ox, oz, width, height)}


def write_key(lay, roster, applied=None):
    os.makedirs(WORK, exist_ok=True)
    on = [b for b in roster["beasts"] if b["onTier"]]
    off = [b for b in roster["beasts"] if not b["onTier"]]
    L = ["# Beast grid key", "",
         "Roster built %s from: %s." % (roster["built"], roster["source"]),
         "Tier on the game when built: %d active mods (our mods: %s)." % (roster["activeCount"], ", ".join(roster["tierModsConfig"])),
         "%d beasts on this tier are in the grid; %d more of ours exist but are NOT on this tier (not in the grid)." % (len(on), len(off)),
         "Layout: %d rows x up to %d beasts, rect %s (x,z,w,h)%s." % (len(lay["rows"]), max(c["col"] for c in lay["cells"]),
                                                                    lay["rect"], "" if applied else " -- PLANNED, not yet staged"),
         "Each row starts with a drafted human for scale. Labels in game read `rRRcCC name`. Row 1 is the top row.",
         "Art column: the art ledger's verdict on the CURRENT south image ('keep (owner)' = owner-ruled).", "",
         "| cell | label | defName | kind | mod | draw | flyer? | x,z | art |", "|---|---|---|---|---|---|---|---|---|"]
    for c in lay["cells"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %d,%d | %s |" % (
            c["id"], c["label"], c["def"], c["kind"], c["pkg"].replace("mandrake.", ""), c["draw"],
            "yes" if c["flyer"] else "", c["x"], c["z"], c["art"]))
    L += ["", "## Not in the grid: ours, but not on this tier (%d)" % len(off), ""]
    pk = {}
    for b in off:
        pk.setdefault(b["pkg"], []).append(b)
    for p, v in sorted(pk.items()):
        L.append("- %s: %d (%s%s)" % (p, len(v), ", ".join(x["def"] for x in v[:6]), ", ..." if len(v) > 6 else ""))
    with open(KEYMD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def load_roster():
    if not os.path.exists(ROSTER):
        sys.exit("no roster.json at %s -- run `python3 %s --build-roster` first" % (ROSTER, os.path.abspath(__file__)))
    with open(ROSTER, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ live (python.exe)
def live_stage(args, roster):
    import rimbridge_client as rc
    from stage_xenotype_grid import Stage, ok

    host, port, token = rc.resolve_endpoint()
    with rc.RimBridge(host=host, port=port, token=token) as b:
        st = Stage(b)
        info = st.call("jawa/map_info", {})
        if not ok(info):
            print("NO MAP: %s" % info.get("message"))
            return 2
        sx, sz = int(info.get("sizeX") or 250), int(info.get("sizeZ") or 250)
        st.say("map %s %dx%d %s ticksGame=%s" % (info.get("mapId"), sx, sz, info.get("mapBiome"), info.get("ticksGame")))
        t1 = info.get("ticksGame")
        time.sleep(1.5)
        t2 = st.call("jawa/map_info", {}).get("ticksGame")
        if t1 is None or t1 != t2:
            print("REFUSING: the clock is running (ticksGame %s -> %s). Pause the game yourself; this script never touches speed." % (t1, t2))
            return 3

        origin = tuple(int(v) for v in args.at.split(",")) if args.at else (6, 6)
        lay, used = fit_layout(roster["beasts"], args.per_row, origin, sx, sz)
        if used != args.per_row:
            st.say("rows widened from %d to %d per row to fit the %dx%d map" % (args.per_row, used, sx, sz))
        ox, oz, w, h = lay["rect"]
        if ox + w > sx - 2 or oz + h > sz - 2:
            print("REFUSING: grid %dx%d at %s does not fit the %dx%d map; raise --per-row or pass --at" % (w, h, origin, sx, sz))
            return 4
        st.say("grid rect %s, %d cells, %d rows" % (lay["rect"], len(lay["cells"]), len(lay["rows"])))

        # raids off
        prior = st.call("jawa/difficulty_tune", {}, check=False)
        keep = {k: prior.get(k) for k in ("threatScale", "allowBigThreats")}
        if not os.path.exists(PRIOR):
            os.makedirs(WORK, exist_ok=True)
            with open(PRIOR, "w", encoding="utf-8") as fh:
                json.dump(keep, fh)
        st.call("jawa/difficulty_tune", {"threatScale": 0, "allowBigThreats": False})
        after = st.call("jawa/difficulty_tune", {}, check=False)
        st.say("raids: threatScale %s->%s allowBigThreats %s->%s" % (keep["threatScale"], after.get("threatScale"),
                                                                       keep["allowBigThreats"], after.get("allowBigThreats")))
        q = st.call("jawa/incident_queue_clear", {}, check=False)
        st.say("incident queue cleared: %s" % q.get("clearedCount"))
        hostile = [p for p in (st.call("jawa/list_pawns", {"limit": 5000}).get("pawns") or [])
                   if p.get("hostile") and not p.get("dead")]
        for p in hostile:
            st.call("jawa/damage", {"thingId": p.get("id"), "damageDef": "Bomb", "amount": 9999})
        left = [p for p in (st.call("jawa/list_pawns", {"limit": 5000}).get("pawns") or [])
                if p.get("hostile") and not p.get("dead")]
        st.say("hostiles: bombed %d, %d still standing" % (len(hostile), len(left)))

        rect = "%d,%d,%d,%d" % (ox, oz, w, h)
        pawns = st.call("jawa/list_pawns", {"limit": 5000}).get("pawns") or []
        inside = [p for p in pawns if not p.get("dead") and p.get("x") is not None
                  and ox <= p["x"] < ox + w and oz <= p["z"] < oz + h]
        cols = [p for p in inside if p.get("isPlayer") and p.get("intelligence") == "Humanlike"]
        if cols and not args.force_clear:
            print("REFUSING: %d player pawn(s) stand inside the grid rect %s; pass --at elsewhere." % (len(cols), rect))
            return 5
        dry = st.call("jawa/clear_area", {"rect": rect, "dryRun": True}, check=False)
        st.say("clear_area dry run: %s" % json.dumps({k: v for k, v in dry.items() if k != "things"})[:300])
        if args.no_clear:
            st.say("--no-clear: skipping clear_area")
        else:
            cl = st.call("jawa/clear_area", {"rect": rect, "dryRun": False})
            st.say("cleared: %s things removed" % cl.get("destroyedCount"))
        st.call("jawa/set_terrain_batch", {"ops": "%s:%s" % (args.ground, rect)})
        st.call("jawa/set_fog", {"action": "unfog", "rect": rect})

        # walls, one batch per row
        planned_walls = 0
        for ri in range(1, len(lay["rows"]) + 1):
            ops = []
            for c in lay["cells"]:
                if c["row"] == ri:
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ops.append("Wall:%d,%d" % (c["x"] + dx, c["z"] + dz))
            planned_walls += len(ops)
            r = st.call("jawa/build_batch", {"ops": ";".join(ops), "stuff": args.stuff, "faction": "player",
                                              "wipeExisting": False, "readBack": 8})
            if not ok(r):
                st.say("WALL BATCH row %d: %s" % (ri, str(r.get("message"))[:160]))
        walls = st.call("jawa/list_things", {"defName": "Wall", "limit": 20000}, check=False)
        inwalls = [t for t in (walls.get("things") or []) if ox <= t.get("x", -1) < ox + w and oz <= t.get("z", -1) < oz + h]
        st.say("walls in rect: %d of %d planned" % (len(inwalls), planned_walls))

        before = {p.get("id") for p in st.call("jawa/list_pawns", {"limit": 5000}).get("pawns") or []}
        bad = []
        for row in lay["rows"]:
            r = st.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": row["x"], "z": row["z"], "faction": "player",
                                             "count": 1, "xenotype": "Baseliner"})
            if not ok(r):
                bad.append(("human r%02d" % row["row"], str(r.get("message"))[:80]))
        for c in lay["cells"]:
            r = st.call("jawa/spawn_pawn", {"kindDef": c["kind"], "x": c["x"], "z": c["z"], "faction": "none", "count": 1})
            if not ok(r):
                bad.append((c["id"] + " " + c["def"], str(r.get("message"))[:80]))
        st.say("spawn failures: %d" % len(bad))
        for k, m in bad[:40]:
            st.say("  FAIL %s: %s" % (k, m))

        pawns = st.call("jawa/list_pawns", {"limit": 5000}).get("pawns") or []
        mine = [p for p in pawns if p.get("id") not in before]
        at = {}
        for p in mine:
            at.setdefault((p.get("x"), p.get("z")), []).append(p)
        holes = [c for c in lay["cells"] if (c["x"], c["z"]) not in at]
        st.say("new pawns on map: %d (expected %d); cells with nobody: %d" % (
            len(mine), len(lay["cells"]) + len(lay["rows"]), len(holes)))
        for c in holes[:40]:
            st.say("  EMPTY %s %s (%s)" % (c["id"], c["def"], c["kind"]))

        humans = [p for row in lay["rows"] for p in at.get((row["x"], row["z"]), [])]
        for p in humans:
            st.call("jawa/set_draft", {"pawnId": str(p["id"]), "drafted": True})
            st.call("jawa/set_pawn_identity", {"pawn": str(p["id"]), "single": "Human"})
        ids = ",".join(str(p["id"]) for p in mine)
        rot = st.call("jawa/set_pawn_rotation", {"pawnId": ids, "dir": "south", "lockRotation": True}, check=False)
        st.say("faced south: %s" % str(rot.get("message") or rot.get("success"))[:100])

        st.call("jawa/review_label", {"action": "clear", "tag": TAG})
        ops = []
        for row in lay["rows"]:
            ops.append("%d|%d|%s" % (row["x"], row["z"] + 1, "HUMAN (scale)" + ("  [%s]" % row["pkg"].replace("mandrake.", "") if row["first"] else "")))
        for c in lay["cells"]:
            ops.append("%d|%d|%s" % (c["x"], c["z"] + 1, "%s %s" % (c["id"], c["label"])))
        for i in range(0, len(ops), 120):
            st.call("jawa/review_label", {"action": "add", "tag": TAG, "ops": "\n".join(ops[i:i + 120])})

        st.call("rimworld/jump_camera_to_cell", {"x": ox + min(w, 40) // 2, "z": oz + h - 12})
        write_key(lay, roster, applied=True)
        with open(LASTRUN, "w", encoding="utf-8") as fh:
            json.dump({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "rect": lay["rect"], "cells": len(lay["cells"]),
                       "newPawns": len(mine), "empty": [c["id"] for c in holes], "spawnFailures": bad,
                       "walls": [len(inwalls), planned_walls]}, fh, indent=1)
        print("\nDONE. Game left PAUSED as found. Key: %s" % KEYMD)
        print("Raids stay OFF until: python.exe %s --restore-settings" % os.path.abspath(__file__))
        return 0


def restore_settings():
    import rimbridge_client as rc
    if not os.path.exists(PRIOR):
        print("no %s -- nothing saved" % PRIOR)
        return 1
    with open(PRIOR, encoding="utf-8") as fh:
        keep = json.load(fh)
    host, port, token = rc.resolve_endpoint()
    with rc.RimBridge(host=host, port=port, token=token) as b:
        args = {k: v for k, v in keep.items() if v is not None}
        b.call("jawa/difficulty_tune", args)
        print("restored:", args, "now:", {k: b.call("jawa/difficulty_tune", {}).get(k) for k in args})
    os.unlink(PRIOR)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build-roster", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--restore-settings", action="store_true")
    ap.add_argument("--per-row", type=int, default=10)
    ap.add_argument("--at", default="", help="grid SW corner x,z (default 6,6 = the map's south-west corner)")
    ap.add_argument("--ground", default="Concrete")
    ap.add_argument("--stuff", default="Steel", help="wall material for the pens (Steel does not burn)")
    ap.add_argument("--no-clear", action="store_true")
    ap.add_argument("--force-clear", action="store_true")
    ap.add_argument("--map-size", type=int, default=250, help="dry-run only: map edge to fit-check against")
    args = ap.parse_args()

    if args.build_roster:
        build_roster()
        return 0
    if args.restore_settings:
        return restore_settings()
    roster = load_roster()
    if args.dry_run or not args.apply:
        origin = tuple(int(v) for v in args.at.split(",")) if args.at else (6, 6)
        lay, used = fit_layout(roster["beasts"], args.per_row, origin, args.map_size, args.map_size)
        print("per-row asked %d, used %d to fit a %d-cell map" % (args.per_row, used, args.map_size))
        on = [b for b in roster["beasts"] if b["onTier"]]
        print("roster built %s; %d on tier, %d off tier" % (roster["built"], len(on), len(roster["beasts"]) - len(on)))
        print("layout: %d rows, %d creatures + %d humans, rect (x,z,w,h) = %s, walls %d, map-fit %s" % (
            len(lay["rows"]), len(lay["cells"]), len(lay["rows"]), lay["rect"], 4 * len(lay["cells"]),
            "OK" if lay["rect"][0] + lay["rect"][2] <= args.map_size - 2 and lay["rect"][1] + lay["rect"][3] <= args.map_size - 2
            else "DOES NOT FIT %d" % args.map_size))
        for row in lay["rows"][:6] + lay["rows"][-2:]:
            cs = [c for c in lay["cells"] if c["row"] == row["row"]]
            print("  r%02d pitch %d z=%d  %s: %s" % (row["row"], row["pitch"], row["z"], row["pkg"].replace("mandrake.", ""),
                                                      ", ".join(c["def"] for c in cs[:4]) + (" ..." if len(cs) > 4 else "")))
        write_key(lay, roster)
        print("KEY.md (planned) -> %s" % KEYMD)
        return 0
    return live_stage(args, roster)


if __name__ == "__main__":
    sys.exit(main())
