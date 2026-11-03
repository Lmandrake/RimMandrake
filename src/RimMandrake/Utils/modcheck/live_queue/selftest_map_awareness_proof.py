"""Offline test of map_awareness_proof.verdict(): every clause has a passing fixture, at least one failing fixture
that must exit 1 and an unmeasured fixture that must exit 2. Also proves the live receipt path (contract.spawn_receipt)
sees a kind change the tool did not report, on a hand-built list_pawns read. No bridge, no game."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import map_awareness_proof as P   # noqa: E402
import contract                   # noqa: E402

RAID = "bridge:jawa/fire_incident#3 > incident:RaidEnemy#4"
fails = []


def check(name, clause, d, want):
    code, why = P.verdict(clause, d)
    ok = code == want
    print("%s %-48s -> %d %s" % ("ok  " if ok else "FAIL", name, code, why[:110]))
    if not ok:
        fails.append(name)


def hit(det, *ids, **kw):
    h = {"detector": det, "ids": list(ids), "summary": det}
    h.update(kw)
    return h


# A1 -- the receipt itself, built from a tool reply and an independent read (the live path)
tool = {"success": True, "pawns": [{"id": "Human10", "kindActual": "Tribal_Warrior"}]}
ctl_tool = {"success": True, "pawns": [{"id": "Human11", "kindActual": "Tribal_Warrior"}]}
rows = [{"id": "Human10", "kindDef": "Colonist"}, {"id": "Human11", "kindDef": "Tribal_Warrior"}]
sub = contract.spawn_receipt("A1", "jawa/spawn_pawn", "Tribal_Warrior", tool, rows)
ctl = contract.spawn_receipt("A1c", "jawa/spawn_pawn", "Tribal_Warrior", ctl_tool, rows)
a1 = {"requested": "Tribal_Warrior", "receipt": sub, "control": ctl, "problems": contract.receipt_problems([sub])}
check("A1 kind change seen by read-back", "A1", a1, 0)
same = contract.spawn_receipt("A1", "jawa/spawn_pawn", "Tribal_Warrior", tool, [{"id": "Human10", "kindDef": "Tribal_Warrior"}])
check("A1 read-back blind to the change", "A1", dict(a1, receipt=same, problems=contract.receipt_problems([same])), 1)
gone = contract.spawn_receipt("A1c", "jawa/spawn_pawn", "Tribal_Warrior", ctl_tool, [])
check("A1 control missing on read-back", "A1", dict(a1, control=gone), 1)
unread = contract.spawn_receipt("A1c", "jawa/spawn_pawn", "Tribal_Warrior", {"success": True, "pawns": [{"id": "Human11"}]},
                                [{"id": "Human11"}])
check("A1 control kinds unreadable", "A1", dict(a1, control=unread), 1)
check("A1 no spawn", "A1", {"why": "spawn failed"}, 2)

# A2
check("A2 first admitted, second reported", "A2", {"first": [], "second": ["Aurora"]}, 0)
check("A2 unbounded (second admitted)", "A2", {"first": [], "second": []}, 1)
check("A2 bound ignored (first reported)", "A2", {"first": ["Eclipse"], "second": ["Eclipse", "Aurora"]}, 1)
check("A2 conditions unreadable", "A2", {"why": "weather_get unreadable"}, 2)

# A3
check("A3 joiner named once", "A3", {"id": "Human20", "hits": [hit("player_joiner", "Human20")]}, 0)
check("A3 joiner missed", "A3", {"id": "Human20", "hits": [hit("pawn_arrived", "Human21")]}, 1)
check("A3 double report", "A3", {"id": "Human20", "hits": [hit("player_joiner", "Human20"),
                                                         hit("pawn_arrived", "Human20")]}, 1)
check("A3 not staged", "A3", {"why": "x"}, 2)

# A4
rows4 = [{"id": "Warg30", "relation": "no-faction", "aggression": "mental:Manhunter", "involvement": "confirmedIndirectAction",
          "statement": "generated during bridge:jawa/spawn_pawn#5; first observed spawn in this recording epoch"},
         {"id": "Human31", "relation": "player", "aggression": None, "involvement": "unknown", "statement": "origin unknown"}]
TXT4 = "Warg30         Warg  -  no-faction  active  mental:Manhunter  5  confirmedIndirectAction  -\nHuman31        Colonist  PlayerColony  player  active  -  5  unknown  -"
a4 = {"warg": "Warg30", "joiner": "Human31", "rows": rows4, "text": TXT4,
      "hits": [hit("wildlife_near_colonist", "Warg30"), hit("player_joiner", "Human31")]}
check("A4 both named, hostility decomposed", "A4", a4, 0)
check("A4 manhunter unnamed", "A4", dict(a4, hits=[hit("player_joiner", "Human31")]), 1)
bad4 = [dict(rows4[0], aggression=None), rows4[1]]
check("A4 hostility not decomposed", "A4", dict(a4, rows=bad4), 1)
over = [dict(rows4[0], statement="created by the bridge"), rows4[1]]
check("A4 statement over-claims", "A4", dict(a4, rows=over), 1)
check("A4 text prints ids only", "A4", dict(a4, text="Warg30 \nHuman31 "), 1)
check("A4 rendered row over-claims", "A4", dict(a4, text=TXT4.replace("unknown  -", "unknown  created by the bridge")), 1)
check("A4 not staged", "A4", {"why": "x"}, 2)

# A5
sc = hit("pawn_state_changed", "Human40", isPlayerBefore=False, isPlayerAfter=True)
check("A5 recruit is a state change", "A5", {"id": "Human40", "hits": [sc]}, 0)
check("A5 recruit read as joiner", "A5", {"id": "Human40", "hits": [sc, hit("player_joiner", "Human40")]}, 1)
check("A5 before-state unread", "A5", {"id": "Human40", "hits": [hit("pawn_state_changed", "Human40", isPlayerAfter=True)]}, 1)
check("A5 state change missed", "A5", {"id": "Human40", "hits": []}, 1)

# A6
a6 = {"id": "Human50", "back_ok": True, "baseline_max": 57, "hits": [hit("player_joiner", "Human50")]}
check("A6 old id reported on return", "A6", a6, 0)
check("A6 colonist seen only as pawn_arrived", "A6", dict(a6, hits=[hit("pawn_arrived", "Human50")]), 1)
check("A6 return missed (watermark)", "A6", dict(a6, hits=[]), 1)
check("A6 vacuous (not an old id)", "A6", dict(a6, baseline_max=40), 1)
check("A6 caravan never came back", "A6", dict(a6, back_ok=False), 2)

# A7
amb = {"success": True, "resolved": False, "ambiguous": [{"id": "Muffalo60"}, {"id": "Muffalo61"}, {"id": "Muffalo9"}]}
a7 = {"ids": ["Muffalo60", "Muffalo61"], "ambiguous": amb,
      "single": {"success": True, "resolved": True, "what": {"id": "Muffalo60"}}}
check("A7 listed, none picked", "A7", a7, 0)
check("A7 silently picked", "A7", dict(a7, ambiguous={"success": True, "what": {}}), 1)
check("A7 id selector resolved the other one", "A7",
      dict(a7, single={"success": True, "resolved": True, "what": {"id": "Muffalo61"}}), 1)
check("A7 ambiguous reply also picked one", "A7", dict(a7, ambiguous=dict(amb, what={"id": "Muffalo60"})), 1)
check("A7 only one muffalo", "A7", {"ids": ["Muffalo60"], "why": "x"}, 2)

# A8
row8 = {"def": "ShortCircuit", "called": True, "outerBodyRan": "true", "returned": "false",
        "statement": "incident ShortCircuit was called; outer body ran: true; returned false; worker entered: unknown"}
check("A8 called, returned false", "A8", {"row": row8, "tool": {"fired": False}}, 0)
check("A8 journal says true", "A8", {"row": dict(row8, returned="true"), "tool": {"fired": False}}, 1)
check("A8 'fired' wording", "A8", {"row": dict(row8, statement="ShortCircuit fired"), "tool": {"fired": False}}, 1)
check("A8 none failed", "A8", {"why": "all fired"}, 2)

# A9
row9 = {"def": "RaidEnemy", "chain": RAID, "returned": "true", "pawnsGeneratedDuring": 3, "pawnsSpawnedDuring": 3,
        "tick": 100}
org = [{"id": "Human70", "generation": {"chain": RAID}}]
check("A9 chain on row and pawns", "A9", {"row": row9, "tool": {}, "origins": org}, 0)
check("A9 chain lost on pawns", "A9", {"row": row9, "tool": {}, "origins": [{"id": "Human70", "generation": {"chain": "incident:RaidEnemy#4"}}]}, 1)
check("A9 pawns from ANOTHER RaidEnemy call", "A9", {"row": row9, "tool": {}, "origins": [
    {"id": "Human70", "generation": {"chain": "bridge:jawa/fire_incident#30 > incident:RaidEnemy#40"}}]}, 1)
check("A9 a raid pawn has no origin row", "A9", {"row": row9, "tool": {}, "origins": org, "new": ["Human70", "Human71"]}, 1)
check("A9 chain order reversed", "A9", {"row": dict(row9, chain="incident:RaidEnemy#4 > bridge:jawa/fire_incident#3"), "tool": {}, "origins": org}, 1)
check("A9 nothing generated", "A9", {"row": dict(row9, pawnsGeneratedDuring=0), "tool": {}, "origins": org}, 1)
check("A9 fired but no journal row", "A9", {"row": None, "tool": {"fired": True}, "why": "no row"}, 1)
check("A9 dialog swallowed", "A9", {"row": row9, "tool": {"blockedByDialog": True}, "origins": org}, 2)

# A10
row10 = dict(row9, pawnsSpawnedDuring=0)
org10 = [{"id": "Mech80", "generation": {"chain": RAID}, "spawn": {"tick": 250}, "ourInvolvement": "confirmedIndirectAction"}]
check("A10 pods landed later, chain kept", "A10", {"row": row10, "origins": org10, "waited": 600}, 0)
check("A10 spawned at call tick", "A10", {"row": row10, "origins": [dict(org10[0], spawn={"tick": 100})]}, 1)
check("A10 involvement lost", "A10", {"row": row10, "origins": [dict(org10[0], ourInvolvement="unknown")]}, 1)
check("A10 a landed pawn has no origin row", "A10", {"row": row10, "origins": org10, "new": ["Mech80", "Mech81"]}, 1)
check("A10 pods never delivered", "A10", {"row": row10, "origins": [], "waited": 600}, 1)
MG = "mapgen:Settlement#1 > bridge:jawa/fire_incident#3 > incident:RaidEnemy#4"
check("A10 chain not bridge-rooted", "A10", {"row": dict(row10, chain=MG), "origins": [dict(org10[0], generation={"chain": MG})]}, 1)
check("A10 no deferred raid", "A10", {"tries": 3, "why": "walk-in"}, 2)

# A11
st = {"success": True, "startedBy": "bridge-registration", "options": {"install.generation-early": True},
      "generationHook": "installed early (install.generation-early) by bridge-registration"}
an = [{"id": "Hare90", "generation": {"chain": "mapgen:Settlement#1 > wild-spawner:SpawnRandomWildAnimalAt#2"}},
      {"id": "Hare91", "generation": None}]
check("A11 mapgen chain at startup", "A11", {"status": st, "animals": an}, 0)
check("A11 no mapgen chain", "A11", {"status": st, "animals": [an[1]]}, 1)
check("A11 lazy hook", "A11", {"status": dict(st, generationHook="installed lazily by jawa/awareness arm"), "animals": an}, 1)
check("A11 started by a call", "A11", {"status": dict(st, startedBy="jawa/awareness"), "animals": an}, 1)
check("A11 option absent at launch", "A11", {"status": dict(st, options={}), "animals": an}, 2)
check("A11 no animals", "A11", {"status": st, "animals": []}, 2)

# A12
o12 = {"id": "Human95", "spawn": {"classification": "observedRespawn"}, "statement": "seen spawned on this map before"}
check("A12 respawn", "A12", {"id": "Human95", "back_ok": True, "origin": o12}, 0)
check("A12 map transfer", "A12", {"id": "Human95", "back_ok": True, "origin": dict(o12, spawn={"classification": "mapTransfer"})}, 0)
check("A12 read as first spawn", "A12", {"id": "Human95", "back_ok": True, "origin": dict(o12, spawn={"classification": "firstObservedSpawn"})}, 1)
check("A12 never back", "A12", {"id": "Human95", "back_ok": False}, 2)

# A13
b = {"success": True, "retained": {"incidents": 40}, "evictions": {"incidents": 0}}
a = {"success": True, "retained": {"incidents": 512}, "evictions": {"incidents": 60}}
d13 = {"before": b, "after": a, "calls": 532, "oldest_before": 5, "journal": {"overwritten": 60, "oldestRetainedSeq": 70}}
check("A13 overflow counted", "A13", d13, 0)
check("A13 overflow not counted", "A13", dict(d13, after=dict(a, evictions={"incidents": 0}),
                                              journal={"overwritten": 0, "oldestRetainedSeq": 70}), 1)
check("A13 ring grew past capacity", "A13", dict(d13, after=dict(a, retained={"incidents": 572})), 1)
check("A13 status/journal disagree", "A13", dict(d13, journal={"overwritten": 59, "oldestRetainedSeq": 70}), 1)
check("A13 counter inflated (journal repeats it)", "A13", dict(d13, after=dict(a, evictions={"incidents": 61}),
                                                          journal={"overwritten": 61, "oldestRetainedSeq": 70}), 1)
check("A13 oldest seq did not advance", "A13", dict(d13, journal={"overwritten": 60, "oldestRetainedSeq": 5}), 1)
check("A13 oldest seq went backwards", "A13", dict(d13, journal={"overwritten": 60, "oldestRetainedSeq": 3}), 1)
check("A13 oldest seq missing", "A13", dict(d13, journal={"overwritten": 60}), 1)
check("A13 status unreadable", "A13", {"before": {}, "after": {}, "calls": 0, "why": "x"}, 2)

# every clause has a gatherer and a verdict
missing = [c for c in P.CLAUSES if not hasattr(P, "g_" + c) or c not in P.VERDICTS]
if missing:
    fails.append("missing clause code: %s" % missing)
check("malformed data is UNMEASURED, never PASS", "A9", {"row": 5}, 2)

print("RESULT: %s (%d failing)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
