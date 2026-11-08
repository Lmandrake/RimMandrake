"""bars2_sluice.py -- pass-2 sluice_gate_state_legible on the story map, row z = 139..143, x = 179..190.

An east-west canal dug 1 m (D2) at z = 141, x = 180..188; a wooden RM_Sluice (player) on its middle square (184,141).
The four squares west of the gate are filled (fill 2), the four east of it are dry. SHUT: settle ~600 ticks, shots.
Then the gate is lifted (RM_FlowDoorRules.ProofSetGate, the same writer as the gate's own button), 400 ticks pass,
shots (OPEN; run 1 showed the canal dry by +1500, so the shot is taken while the level still stands both sides). ProofLiquid on the gate square and the canal depths/fill are logged each time. Nothing selected in a shot.
"""
import sys
from bars2_common import bridge, shot, log, j, dig, build, things, proof, play, GATES

B = bridge()
B.call("jawa/kill_hostiles")
B.call("rimworld/clear_selection")
Z = 141
RUN = [(x, Z) for x in range(180, 189)]
GATE = (184, Z)
for x in range(179, 191):
    for z in (Z - 1, Z + 1):
        B.call("jawa/clear_area", rect="%d,%d,1,1" % (x, z), dryRun=False)
dig(B, RUN, 2)
r = build(B, "RM_Sluice:%d,%d" % GATE, stuff="WoodLog")
if not things(B, "RM_Sluice", (GATE[0], GATE[1], 1, 1)):
    log("build fallback spawn", j(B.call("jawa/spawn_batch", ops="RM_Sluice:%d,%d" % GATE, stuff="WoodLog", faction="player"), 300))
got = things(B, "RM_Sluice", (GATE[0], GATE[1], 1, 1))
log("sluice", [(t.get("id") or t.get("thingId"), t.get("x"), t.get("z"), t.get("rot"), t.get("faction")) for t in got])
proof(B, GATES, "ProofSetGate", "current|%d,%d|false" % GATE)
for c in RUN[:4]:
    B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=2)


def canal(tag):
    ex = B.call("jawa/flowworks_excavation_rect", x=180, z=Z, w=9, h=1, onlyNonZero=False, includeTerrain=False) or {}
    cells = ex.get("cells") or ex.get("rows") or []
    log("CANAL", tag, [(c.get("x"), c.get("d"), c.get("fill") if "fill" in c else c.get("f")) for c in cells])
    log("GATE", tag, proof(B, GATES, "ProofLiquid", "current|%d,%d" % GATE))


B.call("rimworld/step_game_ticks", ticks=600, pauseFirst=True)
canal("shut")
R = (179, 138, 11, 7)
play(B, 800)
B.call("rimworld/clear_selection")
shot(B, "sluice_shut", R)
shot(B, "sluice_shut_close", R, root=7.2)
log("LIFT", proof(B, GATES, "ProofSetGate", "current|%d,%d|true" % GATE))
B.call("rimworld/step_game_ticks", ticks=400, pauseFirst=True)
canal("lifted +400")
play(B, 800)
B.call("rimworld/clear_selection")
shot(B, "sluice_open", R)
shot(B, "sluice_open_close", R, root=7.2)
canal("lifted, after shots")
for k in range(2):
    B.call("rimworld/step_game_ticks", ticks=500, pauseFirst=True)
    canal("lifted +%d more" % (500 * (k + 1)))
print("TABLE sluice gate=%s" % (got[:1],))
