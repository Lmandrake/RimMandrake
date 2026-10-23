#!/usr/bin/env python3
"""Ladder-climber census (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED, owner Q1 2026-10-23).

Owner, verbatim: "Needs a per-creature evaluation, unfortunately. Many mechs, droids, humans, animals should be able to
climb, jump up alone, or slither along a ladder as long as they fit in a 1x1 cell area. Bigger things no, wheeled things
no, and many creatures without arms no."

Applies the SAME rule the game runs (RM_LadderParity.TraitsOf + RM_LadderParityMath.ClimbEligible) to every race ThingDef
in the offline def database (defs.sqlite at the DefDump root; its provenance is printed), and writes the classification
table. Read-only on the database. Borderline rows are MARKED for a judge, never decided here.

    python3 src/RimMandrake/FlowWorks/Tools/ladder_climber_census.py <defs.sqlite> <out.md> [--max-size 1.2]
"""
import argparse
import json
import sqlite3
import sys

MANIP, MOVE = "ManipulationLimbCore", "MovingLimbCore"
WHEEL_WORDS = ("wheel", "tread", "track")


TRUNC = [0]


def walk(part, out):
    if not isinstance(part, dict):
        TRUNC[0] += 1   # the dump cuts deep part trees ("<maxdepth:List`1>"): counted, reported
        return
    out.append((part.get("def"), part.get("customLabel") or ""))
    for ch in part.get("parts") or []:
        walk(ch, out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("out")
    ap.add_argument("--max-size", type=float, default=1.2)
    a = ap.parse_args(argv)
    c = sqlite3.connect(a.db)
    prov = dict(c.execute("select key, value from provenance"))
    part_defs = {}
    for name, js in c.execute("select def_name, json from defs where def_type='BodyPartDef'"):
        f = (json.loads(js).get("fields") or {})
        part_defs[name] = (f.get("tags") or [], f.get("label") or "")
    bodies = {}
    for name, js in c.execute("select def_name, json from defs where def_type='BodyDef'"):
        parts = []
        walk((json.loads(js).get("fields") or {}).get("corePart"), parts)
        bodies[name] = parts
    rows = []
    n_race = 0
    for name, label, mod, js in c.execute("select def_name, label, mod_name, json from defs where def_type='ThingDef'"):
        f = json.loads(js).get("fields") or {}
        race = f.get("race")
        if not isinstance(race, dict):
            continue
        n_race += 1
        body = race.get("body")
        parts = bodies.get(body, [])
        ptags = [part_defs.get(d, ([], ""))[0] for d, _ in parts]
        # jaws are not arms (vanilla SnakeMouth: EatingSource + ManipulationLimbCore); a body that is its own moving limb
        # (the core part, vanilla SnakeBody) slithers -- the same reading as RM_LadderParity.TraitsOf
        arms = any(MANIP in t and "EatingSource" not in t for t in ptags) or race.get("intelligence") == "Humanlike"
        legs = any(MOVE in t for t in ptags[1:])
        words = " ".join(("%s %s %s" % (d, part_defs.get(d, ([], ""))[1], cl)).lower() for d, cl in parts)
        wheeled = any(w in words for w in WHEEL_WORDS)
        moves = not race.get("doesntMove", False)
        slithers = (not legs) and (not wheeled) and moves and len(parts) > 0
        exts = json.dumps(f.get("modExtensions") or [])
        jumps = "RM_PitTravelExtension" in exts and '"jumps": true' in exts
        over = None
        if "RM_LadderClimber" in exts:
            over = '"climbs": false' not in exts
        size = race.get("baseBodySize")
        size = float(size) if isinstance(size, (int, float)) else 1.0
        if over is not None:
            ok = over
        else:
            ok = size <= a.max_size and not wheeled and (arms or jumps or slithers)
        fleshType = race.get("fleshType") or ""
        why = []
        if size > a.max_size:
            why.append("size %.2f > %.1f" % (size, a.max_size))
        if wheeled:
            why.append("wheeled")
        if not (arms or jumps or slithers):
            why.append("no arms, no jump, has legs")
        way = "arms" if arms else "jumps" if jumps else "slithers" if slithers else "-"
        judge = []
        if 0.9 * a.max_size < size <= 1.6:
            judge.append("size near the limit")
        if slithers and fleshType in ("Mechanoid",):
            judge.append("legless mech: hover/float, not a slither?")
        if slithers and not judge and len(parts) <= 3:
            judge.append("body too simple to read (%d parts)" % len(parts))
        if arms and fleshType == "Insectoid":
            judge.append("insect: legs read as arms")
        if wheeled and arms:
            judge.append("wheeled but has arms")
        if not arms and legs and size <= 0.5 and race.get("intelligence") == "Animal" and any(
                k in (body or "").lower() for k in ("monkey", "primate", "squirrel", "lizard", "gecko", "spider", "insect")):
            judge.append("small climber body without arms")
        rows.append(dict(def_=name, label=label, mod=mod, body=body, size=size, arms=arms, legs=legs, wheeled=wheeled,
                         slithers=slithers, jumps=jumps, over=over, ok=ok, way=way, why="; ".join(why),
                         judge="; ".join(judge), flesh=fleshType))
    rows.sort(key=lambda r: (not r["judge"], r["ok"], r["mod"] or "", r["def_"]))
    yes = sum(1 for r in rows if r["ok"])
    out = []
    out.append("# Ladder climbers — census (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED, owner Q1 2026-10-23)\n")
    out.append('Owner, verbatim: *"Needs a per-creature evaluation, unfortunately. Many mechs, droids, humans, animals should '
               'be able to climb, jump up alone, or slither along a ladder as long as they fit in a 1x1 cell area. Bigger '
               'things no, wheeled things no, and many creatures without arms no."*\n')
    out.append("Rule (the game's own: `RM_LadderParity.TraitsOf` + `RM_LadderParityMath.ClimbEligible`): a per-def "
               "`RM_LadderClimber` extension wins; else body size <= %.1f (setting `ladderMaxClimberBodySize`, PROVISIONAL), "
               "no part named wheel/tread/track, and a way up: arms (a `ManipulationLimbCore` part, or humanlike), a jump "
               "(`RM_PitTravelExtension.jumps`), or a legless moving body (slithers). In game the size is the pawn's own "
               "(life stage), so a calf may climb where its parent cannot.\n" % a.max_size)
    out.append("INSTRUMENT LIMIT: the dump cuts body-part trees past a fixed depth (`<maxdepth:List`1>`, %d cut points "
               "here), so a part deeper than that (a hand under arm under shoulder) is invisible to this table; arms are "
               "read at the shoulder (ManipulationLimbCore), which sits above the cut on every vanilla body checked, but a "
               "modded body that puts it deeper reads as armless here and NOT in game (the game reads the whole tree). "
               "Treat a 'no arms' row on a humanoid-looking body as a judge case.\n" % TRUNC[0])
    out.append("Source: `%s`, generated by `src/RimMandrake/FlowWorks/Tools/ladder_climber_census.py`. Provenance: captured "
               "%s, %s mods, load-order fingerprint %s, %s defs (refresh.py 2026-10-23: defs.sqlite *current*). Races our "
               "own mods added after that capture are not in it.\n" % (
                   a.db.split("/")[-1], prov.get("captured_utc"), prov.get("mod_count"), prov.get("load_order_fingerprint"),
                   prov.get("defs_total")))
    out.append("**%d race defs; %d climb, %d do not; %d marked for a judge** (spawn none; a judge agent rules each and the "
               "ruling becomes an `RM_LadderClimber` extension).\n" % (n_race, yes, n_race - yes, sum(1 for r in rows if r["judge"])))
    out.append("| judge? | def | label | mod | size | way up | climbs | why not |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        out.append("| %s | `%s` | %s | %s | %.2f | %s | %s | %s |" % (
            ("**" + r["judge"] + "**") if r["judge"] else "", r["def_"], (r["label"] or "").replace("|", "/"),
            (r["mod"] or "").replace("|", "/"), r["size"], r["way"],
            ("yes" if r["ok"] else "no") + (" (override)" if r["over"] is not None else ""), r["why"]))
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("races=%d climb=%d no=%d judge=%d -> %s" % (n_race, yes, n_race - yes, sum(1 for r in rows if r["judge"]), a.out))
    return 0 if n_race > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
