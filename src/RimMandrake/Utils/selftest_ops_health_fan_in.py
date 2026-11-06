#!/usr/bin/env python3
"""ops_health's evidence-first classifier and fan-in order (RELENTLESS_REWIRE_ENROL_BY_FAN_IN; owner-ordered pipeline
redesign 2026-11-06, redesign_final.md G8). Acceptance: under the owner's pipeline-only pause every cause repair is classed
system and no content item is. Planted with the shipped rules: an environment-cause repair id (the very id
relentless_game.repair_id makes), the item a supervisor block of a cause class names, a caller-known repair, a successor
caused_by a cause repair or an alarm, and a pipeline kind are system; a content item caused_by content, caused_by a system
item that is system only by its words, of a content kind caused_by an alarm, or blocking others through an ordinary block
(blocks >= 1 is not evidence) stays content, as does an item a non-cause snag block names. fan_in counts transitive
dependents once (diamond), ends a cycle, never counts the item itself, weighs by age; system_items leads with it.
No network; the ledger is a fake world."""
import json
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import ops_health as H  # noqa: E402

FAILS = []
NOW = H.ts_epoch("2026-11-06T00:00:00Z")
SHIPPED = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
RULES = dict(SHIPPED, health=dict(SHIPPED["health"], system_rank=[], not_system=[]))     # no hand lists: evidence and words only
C = H.conf(RULES)
ROOT = Path(tempfile.mkdtemp(prefix="ops_fan_"))
(ROOT / "src" / "RimMandrake" / "FlowWorks" / "About").mkdir(parents=True)
(ROOT / "src" / "RimMandrake" / "FlowWorks" / "About" / "About.xml").write_text("<ModMetaData/>")
MODS = H.mod_names(ROOT)


def ok(what, cond, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def it(i, kind="task", on=None, also=(), bkind=None, reason=None, caused_by=None, created="2026-11-05T00:00:00Z", open_=True):
    return types.SimpleNamespace(id=i, kind=kind, open=open_, blocked=bool(on or bkind), blocked_on=on, blocked_also=tuple(also),
                                 blocked_kind=bkind or ("item" if on else None), blocked_reason=reason, caused_by=caused_by,
                                 created_at=created, raised=None, live_repeats=0, title="")


# preconditions the content cases lean on: the shipped lists still read these ids the way the cases assume
WORDY = "RELENTLESS_TICK_FIX_SLOW_WAKE"           # system by its words alone
CONTENT = ["SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED", "SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS", "WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS",
           "ARIDSHRUBLAND_TITAN_POPULATE_FORTY_NO_GIANT", "CHELLOW_NEST_BUILD_REED_BEDS"]
ok("precondition: %s is system by words" % WORDY, H.is_system(it(WORDY), C, MODS))
ok("precondition: the content ids read as content bare", not any(H.is_system(it(i), C, MODS) for i in CONTENT))
ok("precondition: art is a content kind and system/ops pipeline kinds", "art" in C["content_kinds"] and {"system", "ops"} <= set(C["pipeline_kinds"]))

# the id relentless_game makes is the id the classifier knows
import relentless_game as G  # noqa: E402
GID = G.repair_id(types.SimpleNamespace(kind="proof_site_or_reach", fp="3fa9c01d77e2b4aa"))
ok("relentless_game.repair_id output matches CAUSE_REPAIR_ID (%s)" % GID, bool(H.CAUSE_REPAIR_ID.match(GID)), GID)

# 1. the planted ledger: causes, their successors, and content in every disguise
OPS = "OPS_JAM_UNNAMED_DIAGNOSE_NEW_KIND_KUQY"
snag_i = "relentless snag instrument: the proof cannot see the pawn"
snag_g = "relentless snag game_env: the site is in rock"
snag_j = "relentless snag binding_repair: the judge waits"
rows = [
    it(GID), it("GAMEENV_FIX_PROOFSITE_0A1B2C3D_ITEMS_WAIT", caused_by=None),
    it("PROOFREACH_BEETLE_FIX_SEES_BEHIND_DOOR"),                                                  # named by an instrument snag
    it("SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED", on="PROOFREACH_BEETLE_FIX_SEES_BEHIND_DOOR", reason=snag_i),
    it("CAMSITE_PLACE_FIX_ROCK_PICKED"),                                                           # named by a game_env snag
    it("SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS", on="CAMSITE_PLACE_FIX_ROCK_PICKED", reason=snag_g),
    it("SNOWDRIFT_DUNE_FIX_FLAT_TOP"),                                                              # named by a NON-cause snag
    it("ARIDSHRUBLAND_TITAN_POPULATE_FORTY_NO_GIANT", on="SNOWDRIFT_DUNE_FIX_FLAT_TOP", reason=snag_j),
    it("STORE_INCIDENT_GRAB_HELD"),                                                                # known to the caller only
    it(OPS),
    it("BESKARPROBE_SPAWN_FIX_EMPTY_ROOM", caused_by=OPS),                                         # caused_by an alarm
    it("BESKARPROBE_SPAWN_FIX_TWICE", caused_by="BESKARPROBE_SPAWN_FIX_EMPTY_ROOM"),               # its successor
    it("PROOFSITE_RETRY_FIX_DEAD_AGAIN", caused_by="GAMEENV_FIX_OLDCLOSED_DEADBEEF_ITEMS_WAIT"),    # caused_by a closed repair
    it("EXAM_CONTROL_ENFORCE_FOUR_NEVER_MISSED", kind="system"), it("ARENA_TRIAL_RETIRE_HUNDRED_GIGS_IDLE", kind="ops"),
    it(WORDY),
    it("WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS", caused_by=WORDY),                                # caused_by a wordy system item
    it("CHELLOW_NEST_BUILD_REED_BEDS", caused_by="SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED"),    # caused_by content
    it("CHELLOW_SPRITE_REDO_EAST_FACING", kind="art", caused_by=OPS),                              # content kind beats the alarm
    it("KRISSEK_HIVE_BUILD_WALLS"), it("KRISSEK_QUEEN_BUILD_THRONE", on="KRISSEK_HIVE_BUILD_WALLS"),  # blocks >= 1, ordinary
    it("KRISSEK_DRONE_BUILD_NEST", on="KRISSEK_HIVE_BUILD_WALLS"), it("KRISSEK_EGG_BUILD_CLUTCH", on="KRISSEK_HIVE_BUILD_WALLS"),
]
world = types.SimpleNamespace(items={x.id: x for x in rows})
rules = RULES
got = set(H.system_ids(world, rules, ROOT, NOW, repairs={"STORE_INCIDENT_GRAB_HELD"}))
CAUSES = [GID, "GAMEENV_FIX_PROOFSITE_0A1B2C3D_ITEMS_WAIT", "PROOFREACH_BEETLE_FIX_SEES_BEHIND_DOOR", "CAMSITE_PLACE_FIX_ROCK_PICKED",
          "STORE_INCIDENT_GRAB_HELD", "BESKARPROBE_SPAWN_FIX_EMPTY_ROOM", "BESKARPROBE_SPAWN_FIX_TWICE", "PROOFSITE_RETRY_FIX_DEAD_AGAIN"]
for i in CAUSES:
    ok("cause repair %s is system" % i, i in got, sorted(got))
for i in ["EXAM_CONTROL_ENFORCE_FOUR_NEVER_MISSED", "ARENA_TRIAL_RETIRE_HUNDRED_GIGS_IDLE"]:
    ok("pipeline kind %s is system" % i, i in got)
LEAKS = CONTENT + ["CHELLOW_SPRITE_REDO_EAST_FACING", "KRISSEK_HIVE_BUILD_WALLS", "KRISSEK_QUEEN_BUILD_THRONE", "SNOWDRIFT_DUNE_FIX_FLAT_TOP"]
ok("no content item is system (caused_by content, caused_by words-only system, art caused_by alarm, blocks 3, non-cause snag)",
   not (got & set(LEAKS)), sorted(got & set(LEAKS)))

# 2. the owner's pipeline-only pause admits fx.first plus pipeline prefixes: the same list feeds it, so the clause holds there
import relentless as R  # noqa: E402
fx = types.SimpleNamespace(first={i: n for n, i in enumerate(H.system_ids(world, rules, ROOT, NOW, repairs={"STORE_INCIDENT_GRAB_HELD"}))},
                           owner_pause_rule={"pipeline_only": True, "pipeline_prefixes": []})
passed = {i for i in world.items if R.owner_pipeline({"prefixes": []}, fx, i)}
ok("under the pipeline-only pause every cause repair passes", set(CAUSES) <= passed, sorted(set(CAUSES) - passed))
ok("under the pipeline-only pause no content item passes", not (passed & set(LEAKS)), sorted(passed & set(LEAKS)))

# 3. fan_in: transitive, diamond counted once, a cycle ends, the item itself never counts, age weighs
f = [it("A"), it("B", on="A"), it("C", on="A"), it("D", on="B", also=("C",)), it("E", on="D"),     # diamond A<-B,C<-D<-E
     it("X", on="Y"), it("Y", on="X"), it("Z", on="X"),                                              # cycle X<->Y, Z
     it("S", on="S"),                                                                                # self edge
     it("OLD"), it("O1", on="OLD", created="2026-10-27T00:00:00Z"),                                   # 1 dependent, 10 days old
     it("NEW"), it("N1", on="NEW", created="2026-11-06T00:00:00Z"),
     it("SHUT"), it("Q1", on="SHUT", open_=False),                                                    # a closed dependent waits on nothing
     it("OTHER"), it("W1", bkind="judge", on="OTHER")]                                                # a judge wait is no item edge
fw = types.SimpleNamespace(items={x.id: x for x in f})
fan = H.fan_in(fw, NOW)
ok("fan_in: A has 4 transitive dependents, D counted once", fan.get("A", (0,))[0] == 4, fan.get("A"))
ok("fan_in: a cycle ends: X has Y and Z, Y has X and Z", fan.get("X", (0,))[0] == 2 and fan.get("Y", (0,))[0] == 2, (fan.get("X"), fan.get("Y")))
ok("fan_in: a self edge counts nothing", "S" not in fan, fan.get("S"))
ok("fan_in: age weighs (10-day dependent 11.0, fresh 1.0)", fan.get("OLD", (0, 0))[1] == 11.0 and fan.get("NEW", (0, 0))[1] == 1.0,
   (fan.get("OLD"), fan.get("NEW")))
ok("fan_in: closed dependents and non-item waits do not count", "SHUT" not in fan and "OTHER" not in fan, (fan.get("SHUT"), fan.get("OTHER")))

# 4. system_items leads with fan-in, then the hand order
order_rows = [it("OPS_FIRST_RANKED"), it("GAMEENV_FIX_PROOFSITE_11111111_ITEMS_WAIT"), it("GAMEENV_FIX_PROOFSITE_22222222_ITEMS_WAIT"),
              it("SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED", on="GAMEENV_FIX_PROOFSITE_22222222_ITEMS_WAIT"),
              it("SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS", on="GAMEENV_FIX_PROOFSITE_22222222_ITEMS_WAIT")]
ow = types.SimpleNamespace(items={x.id: x for x in order_rows})
orules = dict(SHIPPED, health=dict(SHIPPED["health"], system_rank=["OPS_FIRST_RANKED", "GAMEENV_FIX_PROOFSITE_11111111_ITEMS_WAIT"], not_system=[]))
ids = H.system_ids(ow, orules, ROOT, NOW)
ok("system_items: the repair 2 items wait on leads, then the hand order",
   ids[:3] == ["GAMEENV_FIX_PROOFSITE_22222222_ITEMS_WAIT", "OPS_FIRST_RANKED", "GAMEENV_FIX_PROOFSITE_11111111_ITEMS_WAIT"], ids)

print("selftest_ops_health_fan_in: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
