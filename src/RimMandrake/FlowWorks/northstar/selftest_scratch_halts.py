"""Offline self-test, TESTQ_SURPRISE_DIAGNOSE_SCRATCH_HALTS_CHAINS: the three harness routes that held FlowWorks chains
HARNESS-UNMEASURED on a safe_advance surprise stop, each driven with the shape the live testq store recorded.

  1 thirst   bland_world.feed_colonists tops up RM_Thirst below THIRST_FLOOR (> ThirstyBelow 0.3), not just Food:
             a thirsty colonist drinks toxic channel liquid ('ToxicBuildup age 15', dig_finds 2026-10-31).
  2 swept    the swept wait declares RM_SwimExhaustion beside Bruise, on the staged throwaways only
             ('newest hediff RM_SwimExhaustion age 0', swept 2026-11-05).
  3 colony   extensions._sweep_earlier_chains spawns a keeper colonist BEFORE it vanishes the map's last colonists
             (GameEnded 'Game Over' ~400 ticks into the next wait, bottle_revert 2026-10-29).
Each check also runs the OLD behaviour's shape and shows it would fail (a sanity probe that the test can see).
"""
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_scratch_halts_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(MOD)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class FakeMap(object):
    """list_pawns / pawn_need / spawn_pawn / set_draft / vanish over a dict of pawns; every call is logged in order."""

    def __init__(self, pawns):
        self.pawns = pawns          # id -> {"needs": {...}, "colonist": bool}
        self.log = []
        self.n = 900

    def call(self, tool, **kw):
        self.log.append((tool, kw))
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": i, "isPlayer": p["colonist"], "dead": False, "spawned": True,
                                                "intelligence": "Humanlike" if p["colonist"] else "Animal"}
                                               for i, p in self.pawns.items()]}
        if tool == "jawa/pawn_need":
            p = self.pawns[kw["pawn"]]
            if kw.get("action") == "list":
                return {"success": True, "needs": [{"need": k, "level": v} for k, v in p["needs"].items()]}
            p["needs"][kw["need"]] = kw["level"]
            return {"success": True}
        if tool == "jawa/spawn_pawn":
            self.n += 1
            pid = "Human%d" % self.n
            self.pawns[pid] = {"colonist": kw.get("faction") == "player", "needs": {}}
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/set_draft":
            return {"success": True}
        if tool == "jawa/pawn_force_incapacitate":
            self.pawns.pop(kw["pawn"], None)
            return {"success": True}
        if tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250}
        return {"success": True}

    def colonists(self):
        return [i for i, p in self.pawns.items() if p["colonist"]]


def check_thirst(probs):
    import bland_world as BW
    m = FakeMap({"Human1": {"colonist": True, "needs": {"Food": 0.9, "RM_Thirst": 0.29}},     # thirsty: drinks tar
                 "Human2": {"colonist": True, "needs": {"Food": 0.9, "RM_Thirst": 0.9}},      # fine: untouched
                 "Human3": {"colonist": True, "needs": {"Food": 0.1}},                        # no FlowWorks: food only
                 "Husky4": {"colonist": False, "needs": {"Food": 0.0, "RM_Thirst": 0.0}}})    # not a colonist
    fed = BW.feed_colonists(m)
    if sorted(fed) != ["Human1", "Human3"]:
        probs.append("thirst: fed %r, want Human1 (thirst) + Human3 (food)" % (fed,))
    if m.pawns["Human1"]["needs"]["RM_Thirst"] != 1.0:
        probs.append("thirst: a colonist at RM_Thirst 0.29 was not topped up (it would drink toxic channel liquid)")
    if m.pawns["Human2"]["needs"]["RM_Thirst"] != 0.9:
        probs.append("thirst: a colonist at 0.9 was touched (a needs row would lose its own effect)")
    if "RM_Thirst" in m.pawns["Human3"]["needs"]:
        probs.append("thirst: RM_Thirst written to a pawn without the need")
    if m.pawns["Husky4"]["needs"]["RM_Thirst"] != 0.0:
        probs.append("thirst: a non-colonist was topped up")
    if not BW.THIRST_FLOOR > 0.3:
        probs.append("thirst: THIRST_FLOOR %s is not above RM_ThirstMath.ThirstyBelow 0.3" % BW.THIRST_FLOOR)
    # the C# constant the floor is measured against still reads 0.3
    cs = open(os.path.join(MOD, "Source", "Thirst", "RM_ThirstMath.cs")).read()
    if "public const float ThirstyBelow = 0.3f;" not in cs:
        probs.append("thirst: RM_ThirstMath.ThirstyBelow is no longer 0.3f: re-derive THIRST_FLOOR")
    m2 = FakeMap({"Human1": {"colonist": True, "needs": {"Food": 0.9, "RM_Thirst": 0.1}}})
    if BW.feed_colonists(m2, thirst_floor=None) or m2.pawns["Human1"]["needs"]["RM_Thirst"] != 0.1:
        probs.append("thirst: thirst_floor=None still topped thirst")


def check_swept(probs):
    import testenv_guards as TG
    import clockgate

    src = open(os.path.join(HERE, "extensions_rivers.py")).read()
    want = None
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(x, "id", "") == "SWEPT_EXPECTED_HEDIFF" for x in node.targets):
            want = ast.literal_eval(node.value)
    if not isinstance(want, tuple) or set(want) != {"Bruise", "RM_SwimExhaustion"}:
        probs.append("swept: SWEPT_EXPECTED_HEDIFF is %r, want ('Bruise', 'RM_SwimExhaustion')" % (want,))
        return

    def stop(subject, detail):
        t = {"kind": "hurt", "severity": "damage", "subjectId": subject, "detail": detail}
        return {"state": "stopped", "stopBy": t, "triggers": [t]}
    live = "health 1 -> 0.94; newest hediff RM_SwimExhaustion age 0"       # testq 2026-11-05 06:25, verbatim
    with clockgate.expected_disturbance("swept", TG.expected_hurt(["Human460400"], want)):
        if clockgate.expected_stop_label(stop("Human460400", live)) != "swept":
            probs.append("swept: the live RM_SwimExhaustion stop on a staged throwaway is not resumed")
        if clockgate.expected_stop_label(stop("Human460400", "health 1 -> 0.9; newest hediff Bruise/Leg age 15")) != "swept":
            probs.append("swept: the declared Bruise no longer resumes")
        if clockgate.expected_stop_label(stop("Human77", live)):
            probs.append("swept: an UNSTAGED pawn's swim exhaustion resumed the clock")
        if clockgate.expected_stop_label(stop("Human460400", "health 1 -> 0.9; newest hediff ToxicBuildup age 15")):
            probs.append("swept: ToxicBuildup on a staged pawn resumed the clock")
    # sanity probe: the OLD single-hediff declaration does NOT resume the live stop (this is what held swept)
    with clockgate.expected_disturbance("old", TG.expected_hurt(["Human460400"], "Bruise")):
        if clockgate.expected_stop_label(stop("Human460400", live)):
            probs.append("swept probe: Bruise-only declaration resumes SwimExhaustion, so the test cannot see the bug")


class FakeT(object):
    def __init__(self, m):
        self.session = m
        self.records = []

    def bridge_call(self, tool, **kw):
        return self.session.call(tool, **kw)

    def _record(self, call, result):
        self.records.append(call)

    def _guard(self):
        return True


def check_colony(probs):
    import extensions as EXT
    m = FakeMap({"Human10": {"colonist": True, "needs": {}}, "Human11": {"colonist": True, "needs": {}}})
    earlier, now = FakeT(m), FakeT(m)
    EXT._SPAWNED[:] = [(EXT._chain_token(earlier), "Human10"), (EXT._chain_token(earlier), "Human11")]
    EXT._sweep_earlier_chains(now)
    tools = [tl for tl, _ in m.log]
    if "jawa/spawn_pawn" not in tools:
        probs.append("colony: sweeping the map's only two colonists spawned no keeper (GameEnded in ~400 ticks)")
    elif tools.index("jawa/spawn_pawn") > tools.index("jawa/pawn_force_incapacitate"):
        probs.append("colony: the keeper spawned AFTER a vanish (the colony touched zero): %r" % tools)
    if not m.colonists() or set(m.colonists()) & {"Human10", "Human11"}:
        probs.append("colony: after the sweep colonists are %r (want a keeper, the two fixtures gone)" % m.colonists())
    if EXT._SPAWNED:
        probs.append("colony: _SPAWNED still holds %r (a keeper must never be swept)" % EXT._SPAWNED)
    if not any("keep_colony" in r for r in now.records):
        probs.append("colony: the keeper spawn left no record in the chain's calls")
    # a map that still has a colonist of its own spawns nothing
    m2 = FakeMap({"Human20": {"colonist": True, "needs": {}}, "Human21": {"colonist": True, "needs": {}}})
    a, b = FakeT(m2), FakeT(m2)
    EXT._SPAWNED[:] = [(EXT._chain_token(a), "Human21")]
    EXT._sweep_earlier_chains(b)
    if any(tl == "jawa/spawn_pawn" for tl, _ in m2.log) or m2.colonists() != ["Human20"]:
        probs.append("colony: a keeper was spawned although Human20 survives the sweep: %r" % m2.log)
    # nothing to sweep: not even a pawn list read
    m3 = FakeMap({"Human30": {"colonist": True, "needs": {}}})
    EXT._SPAWNED[:] = []
    EXT._sweep_earlier_chains(FakeT(m3))
    if m3.log:
        probs.append("colony: an empty sweep made bridge calls: %r" % m3.log)
    EXT._SPAWNED[:] = []


def main():
    probs = []
    for fn in (check_thirst, check_swept, check_colony):
        try:
            fn(probs)
        except Exception as ex:                              # noqa: BLE001 - a crash is a failure, named
            import traceback
            probs.append("%s raised %s: %s\n%s" % (fn.__name__, type(ex).__name__, ex, traceback.format_exc()))
    for p in probs:
        print("FAIL", p)
    print("selftest_scratch_halts: %s (%d problem(s))" % ("FAIL" if probs else "PASS", len(probs)))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
