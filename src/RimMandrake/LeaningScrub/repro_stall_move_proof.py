#!/usr/bin/env python3
"""LEANINGSCRUB_STALL_SHARED_MOVE_1: pin repro_stall_move.py to the item's OWN repro, offline and on a live record.

The item's words: "stall pad (anchor-45,-45), lock RM_Stall, RM_Thornhold (x-3,z) + RM_Shirrel (x+3,z) faction none;
read jawa/site_state job + list_pawns x/z every 25 ticks for 300 ticks."  repro_stall_move.py --selftest tests only the
verdict arithmetic; this file goes red when the repro itself drifts from those words.

  (no args)        offline: pins the constants, then drives repro_stall_move.live() against a recording fake bridge and
                   checks every call it makes (spawn kind/cell/faction, anchor, RM_Stall lock, 12 steps of 25 ticks,
                   site_state + list_pawns read on every sample) and the record it writes (13 samples 25 ticks apart).
  --record <json>  live: checks the record a real run wrote (repro_stall_move.py --out) the same way, from the game's own
                   tick counter, plus a named verdict (exit 0). Exit 0 holds, 1 does not, 2 unreadable.
"""
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import repro_stall_move as R  # noqa: E402

STEP, SPAN, SAMPLES = 25, 300, 13          # the item: every 25 ticks for 300 ticks -> 13 readings incl. tick 0
CELLS = {"RM_Thornhold": -3, "RM_Shirrel": 3}


def check_record(rec, need_named=True):
    """-> list of failures (empty = holds) for a record written by repro_stall_move.live()."""
    bad = []
    mi, anchor = rec.get("map") or {}, rec.get("anchor")
    if not (mi.get("sizeX") and anchor == [mi["sizeX"] // 2 - 45, mi["sizeZ"] // 2 - 45]):
        bad.append("anchor %r is not map centre -45,-45 (map %r)" % (anchor, mi))
    if rec.get("weather") != "RM_Stall":
        bad.append("weather %r, not RM_Stall" % rec.get("weather"))
    arms = rec.get("arms") or {}
    if "scent_on" not in arms:
        bad.append("no scent_on arm")
    for name, a in arms.items():
        tr = a.get("tracks") or {}
        if set(tr) != set(CELLS):
            bad.append("%s: tracked %s, not %s" % (name, sorted(tr), sorted(CELLS)))
        for kind, rows in tr.items():
            ticks = [r.get("tick") for r in rows]
            if len(rows) != SAMPLES:
                bad.append("%s %s: %d samples, not %d" % (name, kind, len(rows), SAMPLES))
            if any(t is None for t in ticks):
                bad.append("%s %s: a sample has no tick" % (name, kind))
                continue
            gaps = sorted(set(b - c for c, b in zip(ticks, ticks[1:])))
            if gaps != [STEP]:
                bad.append("%s %s: sample spacing %s ticks, not %d" % (name, kind, gaps, STEP))
            if ticks and ticks[-1] - ticks[0] != SPAN:
                bad.append("%s %s: span %d ticks, not %d" % (name, kind, ticks[-1] - ticks[0], SPAN))
            if not all("job" in r and "x" in r and "z" in r for r in rows):
                bad.append("%s %s: a sample lacks job or x/z" % (name, kind))
    if not mi.get("mapBiome") or mi.get("mapBiome") == "RM_LeaningScrub":
        # the 2026-10-07 move happened on the baroque_wave0 quicktest map, which validation.py at f9647fd94a (the commit
        # that filed this item) states is NOT a Scrub map; the Lean (scent flee included) cannot apply off a biome
        # carrying RM_LeanExtension. A Scrub map is the one condition the 10-07 move never had (gen15's two Scrub runs).
        bad.append("map biome %r: the 10-07 move was on a NON-Scrub quicktest map, so the repro must be"
                   % mi.get("mapBiome"))
    if need_named and "scent_on" in arms:
        # recompute the verdict from the record's own tracks: a stored verdict from an older, looser repro (LIVE
        # 2026-11-02 gen15/run1: one animal's den Goto stored as NAMED) must not pass
        summ = {arm: {k: R.summarise(rows) for k, rows in (arms[arm].get("tracks") or {}).items()}
                for arm in ("scent_on", "scent_off") if arm in arms}
        code, lines = R.verdict(summ.get("scent_on") or {}, summ.get("scent_off"))
        if code != 0 or not any(str(l).startswith("NAMED:") for l in lines):
            bad.append("recomputed verdict names no job: %s" % (lines[-1] if lines else code))
    v = rec.get("verdict") or {}
    if need_named and (v.get("exit") != 0 or not any(str(l).startswith("NAMED:") for l in v.get("lines", []))):
        bad.append("verdict names no job: %r" % v)
    return bad


class Fake:
    """A recording RimBridge: one map, two animals that flee +12,+12 over the first four steps when scent is on."""

    def __init__(self, biome="TemperateForest", down=False):
        self.log, self.tick, self.weather, self.scent = [], 1000, "Clear", "True"
        self.pawns, self.next_id, self.biome, self.down = {}, 1, biome, down

    def connect(self):
        if self.down:
            raise sys.modules["rimbridge_client"].RimBridgeError("refused (fake: game down)")

    def call(self, tool, kw):
        self.log.append((tool, dict(kw)))
        if tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250, "mapBiome": self.biome, "tile": 1}
        if tool == "rimworld/get_game_info":
            return {"ticksGame": self.tick}
        if tool == "rimworld/step_game_ticks":
            for _ in range(kw["ticks"]):
                self.tick += 1
                for p in self.pawns.values():
                    if p["live"] and self.scent == "True" and p["moved"] < 12 and self.tick % 8 == 0:
                        p["x"] += 1; p["z"] += 1; p["moved"] += 1
            return {"success": True}
        if tool == "jawa/weather_set":
            if kw.get("weather"):
                self.weather = kw["weather"]
            return {"success": True}
        if tool == "jawa/weather_get":
            return {"weather": {"current": self.weather}}
        if tool == "jawa/mod_settings_field":
            if kw["action"] == "set":
                self.scent = kw["value"]
            return {"value": self.scent}
        if tool == "jawa/spawn_pawn":
            pid = "Thing_%d" % self.next_id
            self.next_id += 1
            self.pawns[pid] = {"x": kw["x"], "z": kw["z"], "moved": 0, "live": True}
            return {"pawns": [{"id": pid}]}
        if tool == "jawa/pawn_force_incapacitate":
            self.pawns[kw["pawn"]]["live"] = False
            return {"success": True}
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": k, "x": p["x"], "z": p["z"], "intelligence": "Animal"}
                              for k, p in self.pawns.items() if p["live"]]}
        if tool == "jawa/site_state":
            return {"pawns": [{"id": k, "job": "Flee" if 0 < p["moved"] < 12 else "Wait_Wander", "targetA": None}
                              for k, p in self.pawns.items() if p["live"]]}
        return {"success": True}


def drive_fake(**kw):
    fake = Fake(**kw)
    mod = types.ModuleType("rimbridge_client")
    mod.RimBridgeError = type("RimBridgeError", (Exception,), {})
    mod.resolve_endpoint = lambda: ("h", 0, "t")
    mod.RimBridge = lambda **kw: fake
    sys.modules["rimbridge_client"] = mod
    out = os.path.join(tempfile.mkdtemp(prefix="repro_stall_proof_"), "rec.json")
    stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        code = R.live(out)
    except Exception as e:  # an unguarded bridge error must read as a proof failure, not a crash
        code = "raised %s" % type(e).__name__
    finally:
        sys.stdout.close()
        sys.stdout = stdout
    if not os.path.exists(out):
        return code, fake.log, {}
    with open(out) as fh:
        return code, fake.log, json.load(fh)


def offline():
    bad = []
    if R.STEP != STEP or R.STEP * R.STEPS != SPAN:
        bad.append("STEP,STEPS = %r,%r; the item says every %d ticks for %d" % (R.STEP, R.STEPS, STEP, SPAN))
    if tuple(R.PAD) != (-45, -45):
        bad.append("PAD %r, not (-45,-45)" % (R.PAD,))
    code, log, rec = drive_fake()
    if code != 0:
        bad.append("fake 10-07 move: live() exit %r, not 0" % code)
    anchor = (250 // 2 - 45, 250 // 2 - 45)
    spawns = [kw for t, kw in log if t == "jawa/spawn_pawn"]
    if len(spawns) != 4:
        bad.append("%d spawns, not 2 per arm x 2 arms" % len(spawns))
    for kw in spawns:
        want = CELLS.get(kw.get("kindDef"))
        if want is None or (kw.get("x"), kw.get("z")) != (anchor[0] + want, anchor[1]):
            bad.append("spawn %r not at the item's cell (anchor %r)" % (kw, anchor))
        if kw.get("faction") != "none":
            bad.append("spawn %s faction %r, not 'none'" % (kw.get("kindDef"), kw.get("faction")))
        if kw.get("count") != 1:
            bad.append("spawn %s count %r" % (kw.get("kindDef"), kw.get("count")))
    if not any(t == "jawa/weather_set" and kw.get("weather") == "RM_Stall" and kw.get("lockWeather") for t, kw in log):
        bad.append("RM_Stall never locked")
    steps = [kw for t, kw in log if t == "rimworld/step_game_ticks"]
    if [s.get("ticks") for s in steps] != [STEP] * (2 * SPAN // STEP):
        bad.append("steps %s, not %d x %d per arm" % ([s.get("ticks") for s in steps], SPAN // STEP, STEP))
    # every sample reads both instruments the item names
    for tool in ("jawa/site_state", "jawa/list_pawns"):
        n = sum(1 for t, _ in log if t == tool)
        if n < 2 * SAMPLES:
            bad.append("%s read %d times, fewer than %d samples" % (tool, n, 2 * SAMPLES))
    if not rec:
        bad.append("live() wrote no record")
        return bad
    bad += check_record(rec)
    # the record checker can see: a 125x2 record and a missing arm must fail it
    thin = json.loads(json.dumps(rec))
    for rows in thin["arms"]["scent_on"]["tracks"].values():
        del rows[3:]
        for i, r in enumerate(rows):
            r["tick"] = 1000 + 125 * i
    if not check_record(thin):
        bad.append("check_record passed a 125-tick x 2 record")
    if not check_record(dict(rec, arms={})):
        bad.append("check_record passed a record with no arms")
    # a lone mover (gen15/run1: the Thornhold's den Goto, the Shirrel held) whose stored verdict still says NAMED
    lone = json.loads(json.dumps(rec))
    for arm in lone["arms"].values():
        rows = arm["tracks"]["RM_Shirrel"]
        for r in rows:
            r["x"], r["z"] = rows[0]["x"], rows[0]["z"]
    if not any("recomputed verdict" in b for b in check_record(lone)):
        bad.append("check_record passed a record where only one animal moved")
    if not any("10-07 move" in b for b in check_record(dict(rec, map=dict(rec["map"], mapBiome="RM_LeaningScrub")))):
        bad.append("check_record passed a record from an RM_LeaningScrub map (the 10-07 move was off-Scrub)")
    if not any("10-07 move" in b for b in check_record(dict(rec, map=dict(rec["map"], mapBiome=None)))):
        bad.append("check_record passed a record that does not name its map biome")
    # the repro itself refuses a site that measures nothing, BEFORE touching the pad: exit 2 (UNMEASURED), never 1
    # (LIVE 2026-11-02 21:51Z on RM_LeaningScrub and 2026-11-03 02:53Z with the game down were both read as a fail)
    for label, kw in (("an RM_LeaningScrub map", {"biome": "RM_LeaningScrub"}), ("a map with no biome", {"biome": None}),
                      ("an unreachable bridge", {"down": True})):
        c2, log2, rec2 = drive_fake(**kw)
        touched = [t for t, _ in log2 if t in ("jawa/spawn_pawn", "jawa/destroy_batch", "jawa/weather_set")]
        if c2 != 2 or touched or rec2:
            bad.append("%s: live() exit %r (not 2), touched %s, record %s" % (label, c2, touched[:3], bool(rec2)))
    bad += check_live_line()
    return bad


LIVE_FILE = os.path.join(HERE, "..", "..", "..", "infrastructure", "state", "live_proofs",
                         "LEANINGSCRUB_STALL_SHARED_MOVE_1.txt")


def check_live_line(path=LIVE_FILE):
    """The live A1 line must pass the game gate (relentless_live.refused_proof: no run-time expansion, no mutation),
    run the repro with --out, then --record on the SAME file (Windows D:/ spelling vs WSL /mnt/d/ spelling)."""
    sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
    import relentless_live as L  # noqa: E402
    try:
        lines = [l for l in open(path).read().splitlines() if l.startswith("live-proof A1:")]
    except OSError as e:
        return ["live proof file unreadable: %s" % e]
    if len(lines) != 1:
        return ["%d 'live-proof A1:' lines, not 1" % len(lines)]
    proof = lines[0].split(":", 1)[1].strip()
    bad = []
    why = L.refused_proof(L.DEFAULTS, "LeaningScrub stall shared move", "", proof)
    if why:
        bad.append("game gate refuses the A1 line: %s" % why)
    parts = proof.split(" && ")
    if len(parts) != 2 or "repro_stall_move.py --out " not in parts[0] or "repro_stall_move_proof.py --record " not in parts[1]:
        return bad + ["A1 line is not 'repro --out X && proof --record X': %r" % proof]
    out = parts[0].split("--out ", 1)[1].split()[0]
    rec = parts[1].split("--record ", 1)[1].split()[0]
    if not out.startswith("D:/") or rec != "/mnt/d/" + out[3:]:
        bad.append("--out %r and --record %r are not the same file" % (out, rec))
    return bad


if __name__ == "__main__":
    if "--record" in sys.argv:
        try:
            with open(sys.argv[sys.argv.index("--record") + 1]) as fh:
                rec = json.load(fh)
        except (OSError, ValueError, IndexError) as e:
            print("UNMEASURED: %s" % e)
            sys.exit(2)
        bad = check_record(rec)
        wrong_map = [b for b in bad if "10-07 move" in b]
        if wrong_map:
            # RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED: a record from the wrong map measured nothing about the
            # move (live 2026-11-02 21:51Z on RM_LeaningScrub was logged game_fail); the site was wrong, not the mod
            print("UNMEASURED: %s" % wrong_map[0])
            sys.exit(2)
    else:
        bad = offline()
    for b in bad:
        print("FAIL: %s" % b)
    print("proof %s" % ("FAILED" if bad else "ok"))
    sys.exit(1 if bad else 0)
