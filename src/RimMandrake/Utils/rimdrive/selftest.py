"""rimdrive.selftest -- offline proof of the mutate/reconnect/litter contracts.

No socket, no game. Everything here is decidable on this side of the socket,
and a live bridge session costs a game load or at least a live driver's
attention -- see bridgetools/load_session.py's own docstring for why an
item's plumbing gets proven here first, the same discipline this package
inherits.

    python3 src/RimMandrake/Utils/rimdrive/selftest.py

Picked up automatically by run_selftests.py (glob `selftest*.py` under src/).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
# Only the PARENT goes on sys.path -- never `_HERE` itself. `session.py`
# imports `verify` via `from .verify import ...` (bound to the package name
# `rimdrive.verify`); if this file also put `_HERE` on sys.path, an
# unqualified `import verify` would load a SECOND copy of that module under
# the bare name `verify`, and its `UNVERIFIED = object()` sentinel would be a
# different object from the one `rimdrive.verify` created -- every `is
# UNVERIFIED` identity check below would then silently fail for the wrong
# reason. Import everything through the package name, always.
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)

from rimdrive import verify as v  # noqa: E402
from rimdrive.session import Session, SessionError  # noqa: E402
import rimdrive.session as session_mod  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s  %s" % (name, detail))
        FAILURES.append(name)


class Scripted(object):
    """The bare surface `verify.mutate()` needs: `strict`, counters, `log()`.
    Not a `Session` -- `mutate()` is a free function taking any duck-typed
    session-like object, which this test leans on directly."""

    def __init__(self):
        self.strict = True
        self.mutations = 0
        self.no_ops = []
        self.unverified = []
        self.logged = []

    def log(self, msg):
        self.logged.append(msg)


# --------------------------------------------------------- verify.mutate()

def t_mutate_happy_path():
    s = Scripted()
    got = v.mutate(s, "spawn X", lambda: None, lambda: True)
    check("mutate: happy path returns truthy", got is True)
    check("mutate: happy path counts one mutation", s.mutations == 1)
    check("mutate: happy path has no no-ops", s.no_ops == [])


def t_mutate_noop_strict_raises():
    s = Scripted()
    try:
        v.mutate(s, "paint nothing", lambda: None, lambda: False)
        check("mutate: strict no-op raises Unchanged", False)
    except v.Unchanged:
        check("mutate: strict no-op raises Unchanged", True)
    check("mutate: strict no-op is still recorded", s.no_ops == ["paint nothing"])


def t_mutate_noop_nonstrict_logs():
    s = Scripted()
    s.strict = False
    got = v.mutate(s, "paint nothing", lambda: None, lambda: False)
    check("mutate: non-strict no-op returns None", got is None)
    check("mutate: non-strict no-op logs it",
          any("NO-OP" in m for m in s.logged), s.logged)


def t_mutate_unverified_is_not_a_noop():
    s = Scripted()
    got = v.mutate(s, "set stuff, no cell", lambda: None, lambda: v.UNVERIFIED)
    check("mutate: UNVERIFIED sentinel returned as-is", got is v.UNVERIFIED)
    check("mutate: UNVERIFIED tracked separately from no_ops",
          s.unverified == ["set stuff, no cell"] and s.no_ops == [])


def t_mutate_reconnect_then_verified_is_success():
    s = Scripted()
    calls = {"n": 0}

    def do():
        calls["n"] += 1
        if calls["n"] == 1:
            raise v.Reconnected("died mid-call")

    got = v.mutate(s, "spawn X", do, lambda: True)
    check("mutate: reconnect + post-condition true -> success", got is True)
    check("mutate: post-condition already satisfied -> no blind retry",
          calls["n"] == 1)


def t_mutate_reconnect_then_unresolved_is_indeterminate():
    s = Scripted()

    def do():
        raise v.Reconnected("died mid-call")

    try:
        v.mutate(s, "spawn X", do, lambda: False, idempotent=False)
        check("mutate: reconnect + still-false + non-idempotent -> Indeterminate",
              False)
    except v.Indeterminate:
        check("mutate: reconnect + still-false + non-idempotent -> Indeterminate",
              True)


def t_mutate_reconnect_idempotent_retries_once():
    s = Scripted()
    calls = {"n": 0}
    verifies = {"n": 0}

    def do():
        calls["n"] += 1
        if calls["n"] == 1:
            raise v.Reconnected("died mid-call")

    def verify():
        verifies["n"] += 1
        return verifies["n"] >= 2   # false right after reconnect, true on retry

    got = v.mutate(s, "spawn X", do, verify, idempotent=True)
    check("mutate: declared-idempotent retry succeeds", got is True)
    check("mutate: declared-idempotent retry calls do() exactly twice",
          calls["n"] == 2)


# --------------------------------------------------------- Session.sweep()

def _bare_session():
    """A real `Session` with `__init__` never run -- no socket opened, no
    entry in the one-per-process registry. `sweep()`'s actual logic is what's
    under test, not a reimplementation of it."""
    s = Session.__new__(Session)
    s.strict = True
    s.quiet = True
    s.calls = 0
    s.mutations = 0
    s.no_ops = []
    s.unverified = []
    s.litter = []
    return s


def t_sweep_things_destroys_and_verifies_empty():
    s = _bare_session()
    seen = []

    def fake_call(tool, **p):
        seen.append((tool, p))
        if tool == "rimworld/get_cell_info":
            return {"success": True, "cell": {"things": []}}   # empty after the destroy
        return {"success": True}

    s.call = fake_call
    s.track("thing", "Thing_1", x=5, z=5)
    result = s.sweep()
    check("sweep: a tracked thing -> destroy_batch(categories=All)",
          any(t == "jawa/destroy_batch" and p.get("categories") == "All"
              for t, p in seen), seen)
    check("sweep: fully swept thing reports nothing left",
          result == {"swept": 1, "left": []}, result)


def t_sweep_pawn_still_alive_is_reported_left():
    s = _bare_session()

    def fake_call(tool, **p):
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": "Pawn_1"}]}   # still there after teardown
        return {"success": True}

    s.call = fake_call
    s.track("pawn", "Pawn_1", x=9, z=9)
    result = s.sweep()
    check("sweep: a pawn that survived teardown is reported, never hidden",
          result["swept"] == 0 and len(result["left"]) == 1, result)


def t_sweep_pawn_gone_counts_swept():
    s = _bare_session()

    def fake_call(tool, **p):
        if tool == "jawa/list_pawns":
            return {"pawns": []}
        return {"success": True}

    s.call = fake_call
    s.track("pawn", "Pawn_1", x=9, z=9)
    result = s.sweep()
    check("sweep: a pawn confirmed gone counts as swept",
          result == {"swept": 1, "left": []}, result)


def t_sweep_pawn_kill_is_exact_id_and_non_explosive():
    """The sweep used jawa/damage Bomb 99999, which hurt neighbours and lit
    fires (NORTHSTAR_SWEEP_BOMB_1). It must kill by exact id through
    jawa/pawn_force_incapacitate, which has no colonist rail to override and
    no blast radius."""
    s = _bare_session()
    seen = []

    def fake_call(tool, **p):
        seen.append((tool, p))
        if tool == "jawa/list_pawns":
            return {"pawns": []}
        return {"success": True}

    s.call = fake_call
    s.track("pawn", "Pawn_1", x=9, z=9)
    s.sweep()
    kills = [p for t, p in seen if t == "jawa/pawn_force_incapacitate"]
    check("sweep: kills by exact id with action=kill",
          len(kills) == 1 and kills[0].get("pawn") == "Pawn_1" and kills[0].get("action") == "kill",
          kills)
    check("sweep: never calls jawa/damage (no explosion)",
          not [1 for t, _ in seen if t == "jawa/damage"], seen)


def t_sweep_empty_litter_makes_no_calls():
    s = _bare_session()
    called = []
    s.call = lambda tool, **p: called.append(tool) or {"success": True}
    result = s.sweep()
    check("sweep: nothing tracked -> no calls at all, not even a read",
          result == {"swept": 0, "left": []} and called == [], (result, called))


def t_one_session_per_process():
    sentinel = object()
    session_mod._ACTIVE.append(sentinel)
    try:
        try:
            Session()
            ok = False
        except SessionError:
            ok = True
    finally:
        session_mod._ACTIVE.remove(sentinel)
    check("one Session per process is enforced", ok)


# ------------------------------------------- situational companion tools (NORTHSTAR_COMPANION_GAPS_1)

import re  # noqa: E402
from rimdrive.fake import FakeWorld, pawn_row  # noqa: E402

_CS = os.path.join(os.path.dirname(_UTILS), "bridgetools", "JawaBench.BridgeTools",
                   "JawaBenchSituationalTools.cs")
_NEW_TOOLS = ("jawa/pawn_census", "jawa/pawn_roles", "jawa/incident_queue_peek",
              "jawa/incident_queue_remove", "jawa/damage_log", "jawa/thing_lineage")


def _tool_block(src, name):
    """The C# text from a [Tool("name") attribute to its method signature (Description +
    ResultDescription), where every key the real tool returns is named."""
    i = src.find('"%s"' % name)
    if i < 0:
        return None
    j = src.find("public static async", i)
    return src[i:j]


def _keys(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k)
            _keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _keys(v, out)
    return out


def _world():
    w = FakeWorld(pawns=[pawn_row("Col1", x=10, z=10),
                         pawn_row("Husky1", kind="Husky", intelligence="Animal", x=11, z=10),
                         pawn_row("Wolf1", kind="Wolf_Timber", faction=None, is_player=False,
                                  intelligence="Animal", x=40, z=40),
                         pawn_row("Raider1", kind="Tribal", faction="TribeRough", is_player=False,
                                  hostile=True, x=60, z=60)])
    w.mental["Raider1"] = "Berserk"
    w.jobs["Wolf1"] = {"def": "PredatorHunt", "targetA": "Husky1"}
    w.lords["Raider1"] = {"loadId": 7, "lordJob": "LordJob_AssaultColony", "toil": "LordToil_AssaultColony"}
    w.queue = [{"defName": "RaidEnemy", "fireTick": 500, "retryDurationTicks": 0, "triedToFire": False,
                "points": 300.0, "faction": "TribeRough", "forced": False, "target": "map:0",
                "source": None, "fromQuest": False},
               {"defName": "Eclipse", "fireTick": 900, "retryDurationTicks": 0, "triedToFire": False,
                "points": -1.0, "faction": None, "forced": False, "target": "map:0",
                "source": None, "fromQuest": False}]
    w.things = {"Meat1": {"def": "Meat_Cow", "stackCount": 20, "x": 5, "z": 5},
                "Meat2": {"def": "Meat_Cow", "stackCount": 15, "x": 6, "z": 5},
                "Meat3": {"def": "Meat_Cow", "stackCount": 10, "x": 7, "z": 5}}
    return w


def t_situational_fake_keys_match_real_tool():
    """Every key the fake emits must be named in the real tool's attribute text, so a key the fake
    invents cannot make a detector selftest lie (northstar_helpers_plan.md §8)."""
    src = open(_CS, encoding="utf-8").read()
    w = _world()
    w.kill("Col1")
    w.eat("Meat1", "Col1")
    calls = {
        "jawa/pawn_census": w.call("jawa/pawn_census", includeDead=True),
        "jawa/pawn_roles": w.call("jawa/pawn_roles", includeDead=True),
        "jawa/incident_queue_peek": w.call("jawa/incident_queue_peek"),
        "jawa/incident_queue_remove": w.call("jawa/incident_queue_remove", defName="Eclipse"),
        "jawa/damage_log": w.call("jawa/damage_log", pawnsOnly=False),
        "jawa/thing_lineage": w.call("jawa/thing_lineage", ids="Meat1,Meat2"),
    }
    for name in _NEW_TOOLS:
        block = _tool_block(src, name)
        if block is None:
            check("contract: %s declared in C#" % name, False)
            continue
        r = calls[name]
        missing = sorted(k for k in _keys(r, set()) if not re.search(r"\b%s\b" % re.escape(k), block))
        check("contract: fake %s keys all named by the real tool" % name, r.get("success") and not missing,
              missing or r)


def t_situational_contract_probe_can_fail():
    """Sanity probe: the key check must be able to fire -- an invented key is caught."""
    src = open(_CS, encoding="utf-8").read()
    block = _tool_block(src, "jawa/pawn_census")
    check("contract probe: an invented key is not found in the block",
          not re.search(r"\bmentalStateInventedKey\b", block) and re.search(r"\bpreyId\b", block))


def t_census_reads_mental_and_hunting():
    w = _world()
    r = w.call("jawa/pawn_census")
    rows = {p["id"]: p for p in r["pawns"]}
    check("census: berserk raider shows mentalState def + aggro",
          rows["Raider1"]["mentalState"]["def"] == "Berserk" and rows["Raider1"]["mentalState"]["isAggro"])
    check("census: factionless wolf is NOT hostile but IS hunting, with prey id",
          rows["Wolf1"]["hostile"] is False and rows["Wolf1"]["isPredatorHunting"]
          and rows["Wolf1"]["preyId"] == "Husky1")
    check("census: animal has no mood need (None), not a zero", rows["Husky1"]["needs"]["mood"] is None)
    check("census: raider carries its lord", rows["Raider1"]["lord"]["lordJob"] == "LordJob_AssaultColony")


def t_census_unknown_id_fails_loudly():
    w = _world()
    r = w.call("jawa/pawn_census", ids="Col1,Nobody9")
    check("census: an unresolved id fails the whole call", r["success"] is False and "Nobody9" in r["message"])
    s = _bare_session()
    s.call = w.call
    try:
        s.pawn_census(ids=["Nobody9"])
        check("session.pawn_census raises on refusal", False)
    except SessionError:
        check("session.pawn_census raises on refusal", True)


def t_roles_colony_animal_is_player_not_colonist():
    w = _world()
    rows = {p["id"]: p for p in w.call("jawa/pawn_roles", faction="player")["pawns"]}
    check("roles: colony husky isPlayer but not isColonist",
          rows["Husky1"]["isPlayer"] and not rows["Husky1"]["isColonist"] and rows["Col1"]["isColonist"])


def t_incident_queue_peek_and_selective_remove():
    w = _world()
    s = _bare_session()
    s.call = w.call
    q = s.incident_queue()
    check("queue peek lists both entries", [e["defName"] for e in q] == ["RaidEnemy", "Eclipse"])
    dry = s.incident_queue_remove(def_name="RaidEnemy")
    check("queue remove: dry run is the default and removes nothing",
          dry["dryRun"] and dry["removedCount"] == 0 and len(w.queue) == 2)
    real = s.incident_queue_remove(def_name="RaidEnemy", dry_run=False)
    check("queue remove: removes ONLY the matched entry, measured",
          real["removedCount"] == 1 and [e["defName"] for e in w.queue] == ["Eclipse"])
    try:
        s.incident_queue_remove(def_name="RaidEnemy", dry_run=False)
        check("queue remove: zero-match raises (never a silent 'removed')", False)
    except SessionError:
        check("queue remove: zero-match raises (never a silent 'removed')", True)


def t_damage_log_records_damage_and_death():
    w = _world()
    s = _bare_session()
    s.call = w.call
    w.call("jawa/damage", thingId="Col1", damageDef="Bite", amount=12)
    w.kill("Col1")
    log = s.damage_log()
    kinds = [(e["kind"], e["victimId"]) for e in log["events"]]
    check("damage_log: a bite then a kill on the colonist, in order",
          kinds == [("damage", "Col1"), ("kill", "Col1")], kinds)
    nxt = log["nextSeq"]
    w.call("jawa/damage", thingId="Raider1", damageDef="Cut", amount=5)
    later = s.damage_log(since_seq=nxt - 1)
    check("damage_log: sinceSeq returns only the newer event",
          [e["victimId"] for e in later["events"]] == ["Raider1"] and later["completeSinceSeq"])
    w.recorder_installed = False
    try:
        s.damage_log()
        check("damage_log: an uninstalled recorder raises, never reads empty", False)
    except SessionError:
        check("damage_log: an uninstalled recorder raises, never reads empty", True)


def t_thing_lineage_fates():
    w = _world()
    s = _bare_session()
    s.call = w.call
    w.eat("Meat1", "Col1")
    w.merge("Meat2", "Meat3")
    res = {r["id"]: r for r in s.thing_lineage(["Meat1", "Meat2", "Meat3", "Meat9"])}
    check("lineage: eaten stack -> eatenBy:<pawn>", res["Meat1"]["fate"] == "eatenBy:Col1", res["Meat1"])
    check("lineage: merged stack -> absorbedInto:<survivor>", res["Meat2"]["fate"] == "absorbedInto:Meat3")
    check("lineage: survivor found with the merged quantity",
          res["Meat3"]["found"] and res["Meat3"]["stackCount"] == 25)
    check("lineage: never-journalled id is UNRECORDED, not 'destroyed'", res["Meat9"]["fate"] == "UNRECORDED")


TESTS = [
    t_mutate_happy_path,
    t_mutate_noop_strict_raises,
    t_mutate_noop_nonstrict_logs,
    t_mutate_unverified_is_not_a_noop,
    t_mutate_reconnect_then_verified_is_success,
    t_mutate_reconnect_then_unresolved_is_indeterminate,
    t_mutate_reconnect_idempotent_retries_once,
    t_sweep_things_destroys_and_verifies_empty,
    t_sweep_pawn_still_alive_is_reported_left,
    t_sweep_pawn_gone_counts_swept,
    t_sweep_pawn_kill_is_exact_id_and_non_explosive,
    t_sweep_empty_litter_makes_no_calls,
    t_one_session_per_process,
    t_situational_fake_keys_match_real_tool,
    t_situational_contract_probe_can_fail,
    t_census_reads_mental_and_hunting,
    t_census_unknown_id_fails_loudly,
    t_roles_colony_animal_is_player_not_colonist,
    t_incident_queue_peek_and_selective_remove,
    t_damage_log_records_damage_and_death,
    t_thing_lineage_fates,
]


def main():
    for t in TESTS:
        t()
    passed = len(TESTS) - len(FAILURES)
    print("\nSELFTEST %s -- %d/%d passed"
          % ("FAILED" if FAILURES else "OK", passed, len(TESTS)))
    if FAILURES:
        print("  failed: %s" % ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
