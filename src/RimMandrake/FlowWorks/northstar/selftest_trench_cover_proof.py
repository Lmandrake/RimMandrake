"""Offline checks of trench_cover_proof.py (no bridge): the bar follows the target's body size, and every exit path of run()
hands the map back with a live colonist (TRENCH_COVER_PROVE_COLONY_SURVIVES_UNSEEN: modcheck's vanilla canary runs after the
drivers and voids the whole job on "no live colonist").

    python3 src/RimMandrake/FlowWorks/northstar/selftest_trench_cover_proof.py
"""
import argparse
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import trench_cover_proof as T  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


check(abs(T.trench_bar(1.0) - 0.441) < 0.001, "adult human (size 1) square-on bar is the design's 0.441")
# live 20261023T044826: a teenager colonist (HumanlikeTeenager bodySizeFactor 0.8) read trench=0.493, one_back 0.164
check(abs(T.trench_bar(0.8) - 0.493) < 0.001, "a teenager (size 0.8) bar is 0.493, the live read the fixed bar called a FAIL")
check(abs(T.trench_bar(0.8) * 0.3333 - 0.164) < 0.001, "one_back for the same teenager is 0.164, as read live")
check(abs(T.trench_bar(0.2) - 0.75) < 1e-9, "a target shorter than the 1 m wall is fully screened: 0.75 cap")
check(T.trench_bar(None) is None and T.trench_bar("x") is None and T.trench_bar(0) is None, "an unread size is no bar")
kv = T.parse("TRENCH trench=0.493 vanilla=0.000 combined=0.493 hit=0.416 hitNoTrench=0.626 cage=False target=22,20 "
             "shooter=22,30 size=0.800")
check(kv.get("size") == "0.800" and T.near_verdict(kv, "trench", T.trench_bar(kv["size"]), 0.02) == "PASS",
      "the live teenager read PASSes against its own bar")
check(T.near_verdict(kv, "trench", T.trench_bar(1.0), 0.02) == "FAIL", "can-fail: the same read against the adult bar FAILs")

# ============================================================================ the colony survives every exit of run()
class FakeB(object):
    """A bridge whose prepare_site wipes the colony standing in the plot (destroy_batch categories All), as a debug map's
    starting colonists can; `fail` names the step that refuses or raises."""

    def __init__(self, fail=None):
        self.fail = fail
        self.pawns = {"Human1": {"id": "Human1", "isPlayer": True, "intelligence": "Humanlike"},
                      "Human2": {"id": "Human2", "isPlayer": True, "intelligence": "Humanlike"}}
        self.n = 0
        self.settings = {"trenchCoverEnabled": "False", "trenchCoverStrength": "0.5", "trenchCoverCap": "0.5"}

    def ticks(self, n):
        pass

    def call(self, name, **kw):
        if name == "jawa/list_pawns":
            return {"pawns": list(self.pawns.values())}
        if name == "jawa/spawn_pawn":
            self.n += 1
            pid = "Spawn%d" % self.n
            self.pawns[pid] = {"id": pid, "isPlayer": kw.get("faction") == "player", "intelligence": "Humanlike"}
            return {"success": True, "pawns": [{"id": pid}]}
        if name == "jawa/mod_settings_field":
            if kw.get("action") == "get":
                return {"value": self.settings.get(kw["field"])}
            if self.fail == "raise_all" and self.settings["trenchCoverEnabled"] == "True":
                raise RuntimeError("bridge dropped while restoring settings")
            if self.fail == "settings":
                return {"success": False}
            self.settings[kw["field"]] = kw["value"]
            return {"success": True}
        if name == "jawa/flowworks_excavation_drive":
            if self.fail in ("raise", "raise_all"):
                raise RuntimeError("bridge dropped mid-dig")
            if self.fail == "dig":
                return {"success": True, "depth": 0}
            return {"success": True, "depth": 2, "waterSet": True, "waterDl": 10000}
        if name == "jawa/static_call":
            return {"success": True, "result": "TRENCH trench=0.441 vanilla=0 combined=0.441 hit=0.35 hitNoTrench=0.626 size=1.0"}
        return {"success": True}


class FakeV(object):
    def __init__(self, B):
        self.B = B

    def _wait_playing(self, B, leave_s=0):
        return True, None

    def site_calm(self, B):
        return {"ok": True}

    def prepare_site(self, B, rect, rows, rid):
        B.pawns.clear()                    # the colony stood in the plot
        return B.fail != "site"


def run_fake(fail, mod=T):
    B = FakeB(fail)
    out = os.path.join(tempfile.mkdtemp(prefix="trench_selftest_"), "r.json")
    a = argparse.Namespace(out=out, origin="120,120", fresh_map=True)
    try:
        with contextlib.redirect_stdout(io.StringIO()):     # the driver's row lines
            rc = mod.run(B, FakeV(B), a, out, stamp=lambda res, call: None)
    except RuntimeError as ex:
        rc = "raised: %s" % ex
    import json
    with open(out) as f:
        res = json.load(f)
    return rc, len(T.live_colonists(B)), res, B


for fail in (None, "site", "settings", "dig", "raise", "raise_all"):
    rc, live, res, B = run_fake(fail)
    if fail == "raise_all":       # the restore itself died: the guard still ran, and the failed restore is recorded
        check(live >= 1 and "error" in (res.get("settings_restored") or {}),
              "exit raise_all: a restore that raises still leaves %d live colonist(s) and records %s"
              % (live, res.get("settings_restored")))
        continue
    check(live >= 1 and (res.get("colony_left") or {}).get("live", 0) >= 1,
          "exit %-8s: the map is handed back with %d live colonist(s), recorded as colony_left %s (rc %s)"
          % (fail or "full", live, res.get("colony_left"), rc))
    check(B.settings["trenchCoverEnabled"] == "False", "exit %-8s: the owner's trenchCoverEnabled is restored" % (fail or "full"))
rc, live, res, B = run_fake(None)
check(len([r for r in res["rows"] if r["class"] == "MOD"]) == 6, "the full fake run reaches all six MOD rows (rc %s)" % rc)
check((res.get("colony_left") or {}).get("spawned") is None, "a colony that survived (target + shooters) gets no extra spawn")

# can-fail: the pre-fix driver had no leave_a_colonist, so an early exit after prepare_site wiped the colony left none
real = T.leave_a_colonist
T.leave_a_colonist = lambda B, c: {"stub": "pre-fix"}
try:
    for fail in ("site", "settings", "dig", "raise"):
        rc, live, res, B = run_fake(fail)
        check(live == 0, "can-fail: without the guard, exit %s leaves %d live colonists (the canary's red)" % (fail, live))
finally:
    T.leave_a_colonist = real

print("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
