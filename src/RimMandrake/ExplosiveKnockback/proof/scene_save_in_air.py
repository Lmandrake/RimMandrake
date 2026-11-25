#!/usr/bin/env python3
"""sc_save_in_air - Explosive Knockback: a save taken while thrown things are in the air, then a load, counts each thing
once (bar walk_storeroom_raid, its red: "a build whose thrown things duplicate or vanish across a reload"). PROOF BUILD.

It replaces sc_walk_blasts (RIMMANDRAKE_SHRINK_KNOCKBACK_SCENES_ONE_SAVE_IN_AIR, design/specs/2026-11-24-oversized-scenes/
table.md): 17 of that walk's 18 rows are decided by other scenes; the save in the air is the one it alone held.

Kind A. Any free game with a map on the Explosive Knockback tier list (a quicktest map will do), proof build deployed.
One shell: RM_KnockbackProof.Stage("items") clears a 7x7 site at a clear origin, lays 75 Steel, 1 component and one
minified building over the light-mass limit around it, and sets off one Bomb blast of radius 2.9 (the HE shell's type and
radius, damage 1: it pushes at the Bomb's reference force and harms nothing). Two ticks later the light goods are in their
carriers. Then validation_core.saveload_triplet: save, arm A live, arms B and C two loads of that save, each read at the
save tick + TRIPLET_MIN_TICKS on the measured clock, so only the round trip differs between the arms.

The census an arm reads: each of the three staged things by its id, wherever it is, spawned or inside a carrier, with
its stack count (a thing seen in two places is a duplicate), and the total of each staged def over every id in the site
(a load-made copy under a new id shows there). The blast reaches only the stage's cleared site, so no other thing is the
mod's; a map's own things are not counted by id (a regenerated map renumbers them across a save: see census()).

  SA_PRE          proof build, the stage STAGED, three staged things read before the shell
  SA_IN_AIR       at the save, at least one staged thing is inside a carrier (else nothing in the air was saved)
  SA_AIR_AT_LOAD  right after each load, every carrier that had more than TRIPLET_LOAD_SLACK ticks left at the save still
                  holds the same thing (the load kept the flight, not only the thing)
  SA_EACH_ONCE    no arm counts a thing twice, and the triplet reads IDENTICAL (live == load == load); SAVE_DROPS_STATE
                  is the mod's FAIL; LOAD_NONDETERMINISTIC or an unread arm is UNMEASURED, never a pass
  SA_LANDED       after arm C, once nothing is in the air, every staged thing is spawned exactly once, Steel still 75

    python.exe src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_save_in_air.py [--out evidence.json]
    python.exe src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_save_in_air.py --plant lose_heavy

The plant `lose_heavy` destroys the minified building (it stays on its cell: too heavy to throw) right after each load, a
thing the save holds and the loads then lack: SA_EACH_ONCE and SA_LANDED must FAIL, which shows the census can see a loss.
The offline oracle of the judgment is selftest_explosiveknockback_save_in_air.py. Exit 0 only if every row passes; 1 any
FAIL; 2 any UNMEASURED and no FAIL; 3 PROOF BUILD REQUIRED.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KP = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
SCENE = "items"                 # RM_KnockbackProof.Stage: steel (75, O+1,0), comp (1, O+0,1), heavy minified (O-1,0)
STAGED = 3
STEEL = 75
SITE = 10                       # half-width of the census rect around the origin: a 2.9 blast throws goods a few cells
AIR_TICKS = 2                   # ticks from the shell to the save (the ticket: "save at 2 ticks")
LAND_MAX = 240                  # a hang guard: goods fly 14 cells/s, so a throw lands in under 40 ticks; 6x that
CELLS = {(1, 0): "steel", (0, 1): "comp", (-1, 0): "heavy"}   # the items stage's three cells, from the origin (O(s, dx, dz))
# The staged things are found by cell and new id, never by def: live 2026-11-25 (ArchBig) the minified building did not
# read back as def "MinifiedThing" and SA_PRE refused a good stage (APPARATUS FAULT); its def is whatever list_things says.
ROWS = ("SA_PRE", "SA_IN_AIR", "SA_AIR_AT_LOAD", "SA_EACH_ONCE", "SA_LANDED")


def num(s):
    return "".join(ch for ch in str(s) if ch.isdigit())


def pos(t):
    """A thing's cell: jawa/list_things answers top-level x/z; older payloads a position dict."""
    p = t.get("position") if isinstance(t.get("position"), dict) else t
    return (p.get("x"), p.get("z")) if p.get("x") is not None and p.get("z") is not None else None


def flights(text):
    """RM_KnockbackProof.Flights text -> [{innerId (digits), def, count, left}]."""
    out = []
    for line in str(text or "").splitlines():
        m = re.search(r"innerId=(\S+)", line)
        if not m or line.startswith("NONE"):
            continue
        left = re.search(r"left=(-?\d+)", line)
        inner = re.search(r"inner=(\S+) x(\d+)", line)
        out.append({"innerId": num(m.group(1)), "def": inner.group(1) if inner else None,
                    "count": int(inner.group(2)) if inner else None, "left": int(left.group(1)) if left else None})
    return out


def census(things, flight_text, keep, defs=()):
    """One arm's reading: {"ids": sorted ids, "dup": sorted ids seen twice, "stack": {id: count}, "total": {def: count}}.
    things is jawa/list_things' list for the site; only the staged ids (keep) are in ids. The blast (radius 2.9) reaches
    only the stage's cleared 15x15, where the staged things are the only things; a map thing outside it is never the
    mod's. Live 2026-11-25 (ArchSmall, then a control on ArchBig with no blast): on a map made by the debug action
    Regenerate Current Map, every rock chunk took a NEW id across its own save and load (31 lost, 31 new), so a census
    of the map's old ids read a loss the mod never made (APPARATUS FAULT). total sums the staged
    defs over every id, new ones included, spawned and in the air: a load-made copy under a NEW id reads as more Steel
    there, where ids alone see nothing (fresh reader, 2026-11-25)."""
    seen, stack, total, where = [], {}, {}, {}
    for t in things or []:
        if t.get("def") in defs:
            total[t["def"]] = total.get(t["def"], 0) + int(t.get("stackCount") or 0)
        n = num(t.get("id"))
        if n in keep:
            seen.append(n)
            stack[n] = t.get("stackCount")
            where[n] = (t.get("def"), pos(t))
    for f in flights(flight_text):
        if f.get("def") in defs:
            total[f["def"]] = total.get(f["def"], 0) + int(f.get("count") or 0)
        if f["innerId"] in keep:
            seen.append(f["innerId"])
            stack.setdefault(f["innerId"], "in_air")
    return {"ids": sorted(set(seen)), "dup": sorted(i for i in set(seen) if seen.count(i) > 1),
            "stack": {k: stack[k] for k in sorted(stack)}, "total": {k: total[k] for k in sorted(total)},
            "where": {k: where[k] for k in sorted(where)}}      # evidence only: not in the triplet's compared reading


def judge(ev):
    """Evidence -> {row: (status, detail)}. Pure: the offline selftest feeds it planted evidence."""
    rows = {}

    def r(rid, st, det):
        rows[rid] = (st if isinstance(st, str) else ("PASS" if st else "FAIL"), str(det)[:400])

    staged = ev.get("staged_ids") or []
    if not str(ev.get("stage") or "").startswith("STAGED") or len(staged) != STAGED:
        r("SA_PRE", False, "stage %r; staged things read %s (want %d)" % (str(ev.get("stage"))[:120], staged, STAGED))
        for rid in ROWS[1:]:
            r(rid, "UNMEASURED", "no staged site")
        return rows
    r("SA_PRE", True, "stage %s; staged %s" % (str(ev["stage"])[:80], staged))
    air = [f for f in ev.get("air_at_save") or [] if f.get("innerId") in staged]
    r("SA_IN_AIR", bool(air), "%d staged thing(s) in a carrier %d ticks after the shell: %s" % (len(air), AIR_TICKS, air))
    if not air:
        for rid in ROWS[2:]:
            r(rid, "UNMEASURED", "UNMEASURED: nothing in the air was saved")
        return rows
    slack = ev.get("load_slack", 3)
    want = sorted(f["innerId"] for f in air if (f.get("left") or 0) > slack)
    loads = ev.get("air_at_load") or []
    at = ev.get("arms_at_target") or {}
    loaded = all(at.get(k) for k in "ABC")      # a load that never took leaves the live game, or a loading one, to read
    if not loaded or len(loads) < 2:
        r("SA_AIR_AT_LOAD", "UNMEASURED", "arms read at the target %s, %d load(s) read (the triplet stopped early: %s)" % (
            at, len(loads), ev.get("why")))
    elif not want:
        r("SA_AIR_AT_LOAD", "UNMEASURED", "every flight had %d ticks or fewer left at the save: %s" % (slack, air))
    else:
        got = [sorted(f["innerId"] for f in ld if f.get("innerId") in staged) for ld in loads]
        r("SA_AIR_AT_LOAD", all(set(want) <= set(g) for g in got),
          "in the air at the save with > %d ticks left: %s; in the air right after load B %s, load C %s" % (
              slack, want, got[0], got[1]))
    tr = ev.get("triplet") or {}
    arms = ev.get("arms") or {}
    dups = {k: a.get("dup") for k, a in arms.items() if a.get("dup")}
    ids = {k: a.get("ids") or [] for k, a in arms.items()}
    lost = sorted(set(ids.get("A", [])) - set(ids.get("B", [])))
    new = sorted(set(ids.get("B", [])) - set(ids.get("A", [])))
    det = "at tick %s: live %d, load %d, reload %d things; dup %s; lost %s new %s (load vs live); %s %s" % (
        tr.get("target"), len(ids.get("A", [])), len(ids.get("B", [])), len(ids.get("C", [])), dups, lost[:5], new[:5],
        tr.get("verdict"), tr.get("why") or "")
    missing = [i for i in staged if i not in ids.get("A", [])]
    want_total = ev.get("staged_total") or {}
    tot = {k: a.get("total") for k, a in arms.items()}
    off = {k: v for k, v in tot.items() if k in ("B", "C") and v != want_total}
    det += "; totals by def %s (staged %s)" % (tot, want_total)
    if dups:
        r("SA_EACH_ONCE", False, "MOD: a thing counted twice; " + det)
    elif missing or tot.get("A") != want_total:
        r("SA_EACH_ONCE", "UNMEASURED", "the live arm lacks staged thing(s) %s or its totals differ: the census rect missed them; %s" % (missing, det))
    elif off:
        r("SA_EACH_ONCE", False, "MOD: a load changed the total of a staged def (a copy under a new id, or a loss) in %s; %s" % (sorted(off), det))
    elif ev.get("plant") and not ev.get("planted"):
        r("SA_EACH_ONCE", "UNMEASURED", "the plant %s was asked and nothing was planted; %s" % (ev.get("plant"), det))
    elif tr.get("verdict") == "IDENTICAL":
        r("SA_EACH_ONCE", True, det)
    elif tr.get("verdict") == "SAVE_DROPS_STATE":
        r("SA_EACH_ONCE", False, "MOD: both loads agree and differ from the live game; " + det)
    else:
        r("SA_EACH_ONCE", "UNMEASURED", det)
    end = ev.get("landed")
    if not loaded:
        r("SA_LANDED", "UNMEASURED", "the triplet did not read every arm at its target (%s): the game after it is not a load" % at)
    elif not end:
        r("SA_LANDED", "UNMEASURED", "no reading after the flights (%s)" % ev.get("land_why"))
    else:
        c = end.get("census") or {}
        left = end.get("carriers_left")
        st = (c.get("stack") or {}).get(ev.get("steel_id"))
        absent = [i for i in staged if i not in (c.get("ids") or [])]
        r("SA_LANDED", not left and not c.get("dup") and not absent and st == STEEL and c.get("total") == want_total,
          "after %s tick(s): %d carrier(s) left; dup %s; staged absent %s; Steel %s; totals by def %s (staged %s)" % (
              end.get("ticks"), len(left or []), c.get("dup"), absent, st, c.get("total"), want_total))
    return rows


def verdict_exit(rows):
    sts = [s for s, _ in rows.values()]
    return 0 if sts and all(s == "PASS" for s in sts) else 1 if "FAIL" in sts else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", default=None, choices=["lose_heavy"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(HERE, "..", "..", "FlowWorks", "northstar"))
    sys.path.insert(0, os.path.join(HERE, ".."))
    sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))
    import proof_hose as PH  # noqa: E402
    import validation_core as VC  # noqa: E402
    from proof_build_gate import require_proof_build  # noqa: E402
    B = PH.PB()
    ev = {"plant": a.plant, "load_slack": VC.TRIPLET_LOAD_SLACK}

    def c(tool, **kw):
        try:
            return B.call(tool, **kw) or {}
        except Exception as e:  # noqa: BLE001 - one failed call is that row's evidence, never a crash
            return {"success": False, "exc": repr(e)[:300]}

    def kp(method, arg="x"):
        return str(c("jawa/static_call", type=KP, method=method, args=arg).get("result") or "")

    def step(n):
        c("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=120000)

    require_proof_build(c("jawa/static_call", type=KP, method="Names", args="x"))
    c("rimworld/set_time_speed", speed=0)
    kp("Clear")
    origin = kp("Origins", "1").split(";")[0]
    ox, oz = (int(v) for v in origin.split(",")) if re.match(r"^\d+,\d+$", origin) else (None, None)
    site = "%d,%d,%d,%d" % (ox - SITE, oz - SITE, 2 * SITE + 1, 2 * SITE + 1) if ox is not None else None

    def things():
        return c("jawa/list_things", rect=site, group="HaulableEver", limit=2000).get("things") or []

    if site:
        before = things()                     # the old things of the site, before the stage lays its three
        ev["stage"] = kp("Stage", "%s,%s" % (SCENE, origin))
        now = things()
        old = set(num(t.get("id")) for t in before)
        at = {(ox + dx, oz + dz): k for (dx, dz), k in CELLS.items()}
        mine = [t for t in now if num(t.get("id")) and num(t.get("id")) not in old and pos(t) in at]
        ev["staged"] = [(at[pos(t)], t.get("def"), num(t.get("id")), t.get("stackCount"), pos(t)) for t in mine]
        if len(mine) != STAGED:                # what the cells hold, any group, so a miss names its cause
            ev["around"] = [(t.get("def"), t.get("id"), pos(t), t.get("stackCount")) for t in
                            c("jawa/list_things", rect="%d,%d,3,3" % (ox - 1, oz - 1), limit=50).get("things") or []]
        defs = sorted(set(t.get("def") for t in mine))
        ev["staged_ids"] = sorted(num(t.get("id")) for t in mine)
        ev["staged_total"] = {}
        for t in mine:
            ev["staged_total"][t["def"]] = ev["staged_total"].get(t["def"], 0) + int(t.get("stackCount") or 0)
        ev["steel_id"] = next((i for k, _d, i, _n, _p in ev["staged"] if k == "steel"), None)
        heavy = next((p for k, _d, _i, _n, p in ev["staged"] if k == "heavy"), None)
        keep = set(ev["staged_ids"])
    else:
        ev["stage"] = "no clear origin (Origins: %r)" % origin
    rows = judge(ev)
    if rows["SA_PRE"][0] == "PASS":
        step(AIR_TICKS)
        ev["air_at_save"] = flights(kp("Flights"))
        rows = judge(ev)
    if rows.get("SA_IN_AIR", ("",))[0] == "PASS":
        ev["air_at_load"], ev["arms"] = [], {}
        arm = ["A"]

        def read_state(_B=None):
            cs = census(things(), kp("Flights"), keep, defs)
            ev["arms"][arm[0]] = cs
            return {"ids": cs["ids"], "dup": cs["dup"], "stack": cs["stack"]}

        def wait_playing(_B):
            ok, why = VC._wait_playing(B, leave_s=3)
            c("rimworld/set_time_speed", speed=0)
            arm[0] = "B" if arm[0] == "A" else "C"
            ev["air_at_load"].append(flights(kp("Flights")))
            if a.plant == "lose_heavy" and heavy:
                got = c("jawa/destroy_batch", rects="%d,%d,1,1" % heavy, categories="Item")
                if got.get("success") is not False:     # a refused plant is no plant: SA_EACH_ONCE then reads UNMEASURED
                    ev.setdefault("planted", []).append(got)
            return ok, why

        class _TB(object):
            def call(self, tool, _answer=False, **kw):
                return B.call(tool, _answer=_answer, **kw)

            def ticks(self, n):
                step(n)

        name = "EK_SAVE_IN_AIR_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        ev["save"] = name
        try:
            tr = VC.saveload_triplet(_TB(), read_state, ticks=VC.TRIPLET_MIN_TICKS, save_name=name, wait_playing=wait_playing)
        except Exception as e:  # noqa: BLE001 - a bridge fault inside the triplet is an unread row, never a verdict
            tr = {"verdict": "UNMEASURED", "why": "saveload_triplet raised %r" % e}
        ev["triplet"] = {k: tr.get(k) for k in ("verdict", "why", "target", "save")}
        ev["why"] = tr.get("why")
        # every arm read at the target, or the game after the triplet is not a load of the save (fresh reader, 2026-11-25:
        # arms["A"] is set before arm B loads, so a non-empty arms dict proves nothing)
        tgt = tr.get("target")
        ev["arms_at_target"] = {k: tgt is not None and (tr.get("arms") or {}).get(k, {}).get("readTick") == tgt for k in "ABC"}
        if all(ev["arms_at_target"].values()):
            t_end = None
            for t in range(0, LAND_MAX, 10):
                if not flights(kp("Flights")):
                    t_end = t
                    break
                step(10)
            left = flights(kp("Flights"))
            ev["landed"] = {"ticks": t_end if t_end is not None else LAND_MAX, "carriers_left": left,
                            "census": census(things(), kp("Flights"), keep, defs)}
        else:
            ev["land_why"] = "the triplet did not read every arm at its target"
        rows = judge(ev)
    kp("Clear")
    out = a.out or os.path.join(os.environ.get("RM_SCRATCH", r"D:\ClaudeWork\rimmandrake"), "ek_proof",
                                "scene_save_in_air_%s.json" % datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"rows": rows, "ev": ev}, fh, indent=1, default=str)
    for rid in ROWS:
        st, det = rows.get(rid, ("UNMEASURED", "not reached"))
        print("%-16s %-10s %s" % (rid, st, det))
    code = verdict_exit(rows)
    print("%s sc_save_in_air%s; evidence: %s" % ({0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code],
                                                  " (plant %s)" % a.plant if a.plant else "", out))
    return code


if __name__ == "__main__":
    sys.exit(main())
