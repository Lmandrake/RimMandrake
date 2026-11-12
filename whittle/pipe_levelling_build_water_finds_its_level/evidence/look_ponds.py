"""Look at the two pond rigs walk_gaps_proof.py --only PONDS_* leaves on the map (origin 40,40), the way a player would:
select a hose reel and read its inspect pane, in a screenshot. Then the ordinary-use follow-up: top pool 1 of the levelled
(A4) rig back up, as rain or a pump would, and watch the reel go back to "flowing" and the pools level again.

  python.exe whittle/pipe_levelling_build_water_finds_its_level/evidence/look_ponds.py <out.json>

Run right after the PONDS_* proof on the same map, from the repo root, bridge held. Writes screenshots named lev_* into the
game's Screenshots folder (their paths are in the out json).
"""
import json
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
for p in ("src/RimMandrake/FlowWorks/northstar", "src/RimMandrake/Utils"):
    sys.path.insert(0, os.path.join(REPO, p))
import validation_core as V  # noqa: E402
import proof_hose as PH  # noqa: E402

LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
FLUIDP = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
OX, OZ = 40, 40
A4 = {"reels": [(50, 62), (50, 64)], "pools": [(40, 56), (40, 68)]}     # POND_RIG at plot z+20
A5 = {"reels": [(50, 82), (50, 84)], "pools": [(40, 76), (40, 88)]}     # POND_RIG at plot z+40

DESK_DIR = r"D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_STEVEDESKTOP_FWLIVE"     # python.exe on Steve writes it
B = V.guard(PH.PB())
out = {"shots": [], "reads": []}


def static(ty, m, arg):
    r = B.call("jawa/static_call", type=ty, method=m, args=arg, _answer=True) or {}
    return str(r.get("result") or r.get("message") or r.get("error") or "")


def reel_id(c):
    lt = B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,2" % c, limit=1, _answer=True) or {}
    return ((lt.get("things") or [{}])[0]).get("id")


def inspect(rid):
    ins = B.call("jawa/inspect_string", thingIds=str(rid), _answer=True) or {}
    return [ln for t in (ins.get("things") or []) for ln in (t.get("inspect") or [])]


def pools(rig):
    return [static(LPROOF, "ProofPitWater", "%d,%d,3,3" % p) for p in rig["pools"]]


def shot(name, rig, which=0, label=""):
    rid = reel_id(rig["reels"][which])
    B.call("rimworld/set_camera_zoom", rootSize=14)
    cx = (rig["pools"][0][0] + rig["reels"][0][0]) // 2 + 1
    cz = (rig["pools"][0][1] + rig["pools"][1][1]) // 2 + 1
    B.call("rimworld/jump_camera_to_cell", x=cx, z=cz)
    B.call("jawa/select_things", ids=str(rid), action="select")
    # a desktop capture, so the inspect pane the player reads is in frame (jawa/take_screenshot renders the map only, and a
    # desktop capture taken after it showed no UI at all, live 2026-11-12), after a frame with the selection has drawn
    ticks(2)
    time.sleep(1.5)
    desk = DESK_DIR + "\\" + name + "_desktop.bmp"
    # the old file goes first: a capture whose subprocess crashed (a 'Fatal Python error' interop flake, 2026-11-12) left the
    # previous run's image in place under this name, showing an older build's text. One retry; written or not is recorded.
    if os.path.exists(desk):
        os.remove(desk)
    for _ in range(2):
        subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "Utils", "system_screenshot.py"), desk], timeout=60)
        if os.path.exists(desk):
            break
    rec = {"name": name, "label": label, "reel": rid, "inspect": inspect(rid), "pools": pools(rig), "desktop": desk,
           "desktopWritten": os.path.exists(desk), "capturedAt": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out["shots"].append(rec)
    print(json.dumps(rec)[:600], flush=True)


def ticks(n):
    B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40))


B.call("rimworld/pause_game", pause=True)
# jawa/clear_ui defaults hideHud=true: screenshot mode for a 20 s lease, no inspect pane and no bottom bar in any capture inside
# it (skills/rimbridge/references/traps/debug-actions-ui.md; met live 2026-11-12). These shots are OF the inspect pane.
B.call("jawa/clear_ui", hideHud=False)
shot("lev_a4_level", A4, 0, "A4 rig after the proof: pools level, intake reel selected")
# the proof caps the A5 rig's reels after its row (so it cannot move anything during A4): put them back as a player left them
for c, role in zip(A5["reels"], ("Intake", "Outflow")):
    static(LPROOF, "ProofHoseRole", "%d,%d;%s" % (c + (role,)))
ticks(520)                                      # two levelling cycles, so the readout is this rig's own
shot("lev_a5_nomix", A5, 0, "A5 rig: water pool vs chemfuel pool, intake reel selected")
shot("lev_a5_nomix_outflow", A5, 1, "A5 rig: the outflow reel says the same")
# ordinary use: pool 1 gets water again (rain, a pump, a bucket brigade): top it to 4 notches on all 9 squares
for i in range(3):
    for j in range(3):
        static(FLUIDP, "ProofFillWithFluid", "%d,%d,4,RM_Fluid_Water" % (A4["pools"][0][0] + i, A4["pools"][0][1] + j))
before = pools(A4)
ticks(500)
shot("lev_a4_refilled_flowing", A4, 0, "A4 rig 500 ticks after pool 1 was topped up again: flowing again")
trail = []
for k in range(24):
    ticks(250)
    rid = reel_id(A4["reels"][0])
    line = [ln for ln in inspect(rid) if "Levelling" in ln]
    trail.append({"tick": 500 + 250 * (k + 1), "pools": pools(A4), "inspect": line})
    if line and "level." in line[0]:
        break
out["refill"] = {"before": before, "trail": trail}
shot("lev_a4_relevelled", A4, 0, "A4 rig after the refill has levelled again")
shot("lev_a4_relevelled_outflow", A4, 1, "A4 rig, outflow reel")
B.call("jawa/select_things", action="clear")
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
print("wrote", sys.argv[1])
