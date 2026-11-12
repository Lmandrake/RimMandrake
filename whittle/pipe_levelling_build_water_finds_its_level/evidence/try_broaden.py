"""BROADEN experiments on the A4 pond rig walk_gaps_proof.py --only PONDS_HOSE_LEVEL leaves on a fresh map (origin 40,40):
(1) save mid-flow, run on, reload and run the same span again: the reloaded run must land on the same volumes (no lost,
duplicated or stalled transfer across a save), total conserved; (2) the player flips the reels' roles mid-flow through the
role setting: swapped and both-Intake still level (roles do not set the direction: the higher water runs to the lower), a
Capped end stops it (nothing moves, the Levelling line goes), uncapping resumes it.

  python.exe whittle/pipe_levelling_build_water_finds_its_level/evidence/try_broaden.py <out.json>
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
FLUIDP = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
REELS = [(50, 62), (50, 64)]          # POND_RIG at plot z+20: reel 1 hose to pool 1, reel 2 to pool 2
POOLS = [(40, 56), (40, 68)]
SAVE = "lev_broaden_midflow"

B = V.guard(PH.PB())
out = {"steps": []}


def static(ty, m, arg):
    r = B.call("jawa/static_call", type=ty, method=m, args=arg, _answer=True) or {}
    return str(r.get("result") or r.get("message") or r.get("error") or "")


def dl():
    v = []
    for p in POOLS:
        t = static(LPROOF, "ProofPitWater", "%d,%d,3,3" % p)
        v.append(int(t.split("dl=")[1].split()[0]) if "dl=" in t else None)
    return v


def levelling_lines():
    lines = []
    for c in REELS:
        lt = B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,2" % c, limit=1, _answer=True) or {}
        rid = ((lt.get("things") or [{}])[0]).get("id")
        ins = B.call("jawa/inspect_string", thingIds=str(rid), _answer=True) or {}
        ln = [x for t in (ins.get("things") or []) for x in (t.get("inspect") or []) if "Levelling" in x or "Role:" in x]
        lines.append(" / ".join(ln))
    return lines


def tick(n):
    r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
    return r.get("success") is not False


def note(what, **kw):
    rec = dict(step=what, dl=dl(), inspect=levelling_lines(), **kw)
    rec["total"] = sum(rec["dl"]) if None not in rec["dl"] else None
    out["steps"].append(rec)
    print(json.dumps(rec)[:400], flush=True)
    return rec


def role(c, r):
    return static(LPROOF, "ProofHoseRole", "%d,%d;%s" % (c + (r,)))


B.call("rimworld/pause_game", pause=True)
# pool 1 topped back to 4 notches (rain, a pump): unequal again, so the link has work
for i in range(3):
    for j in range(3):
        static(FLUIDP, "ProofFillWithFluid", "%d,%d,4,RM_Fluid_Water" % (POOLS[0][0] + i, POOLS[0][1] + j))
tick(500)
s0 = note("flowing before the save")
sv = B.call("rimworld/save_game", saveName=SAVE, _answer=True) or {}
out["save"] = {k: sv.get(k) for k in ("success", "message", "saveName", "path")}
tick(750)
sa = note("750 ticks on, no reload")
t = time.time()
# waitForVisualReady: with map data alone the desktop capture below caught the loading screen (2026-11-12)
ld = B.call("rimworld/load_game_ready", saveName=SAVE, timeoutMs=240000, pauseIfNeeded=True, waitForVisualReady=True,
            _answer=True) or {}
out["load"] = {"success": ld.get("success"), "s": round(time.time() - t, 1), "message": str(ld.get("message") or ld.get("error"))[:200]}
# load_game_ready answered before the map could be read on the first try (dl null for two reads, 2026-11-12): wait until it can
for _ in range(60):
    if None not in dl():
        break
    time.sleep(2)
out["load"]["readableAfterS"] = round(time.time() - t, 1)
B.call("rimworld/pause_game", pause=True)
s1 = note("right after the reload (expect = before the save)")
# what a player sees on clicking the intake reel of a just-loaded, still-paused game (no levelling cycle has run yet)
lt = B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,2" % REELS[0], limit=1, _answer=True) or {}
B.call("rimworld/set_camera_zoom", rootSize=14)
B.call("rimworld/jump_camera_to_cell", x=46, z=63)
B.call("jawa/select_things", ids=str(((lt.get("things") or [{}])[0]).get("id")), action="select")
time.sleep(2.0)
desk = r"D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_STEVEDESKTOP_FWLIVE\lev_after_reload_desktop.bmp"
if os.path.exists(desk):            # never leave an older run's image under this name (see look_ponds.py)
    os.remove(desk)
for _ in range(2):
    subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "Utils", "system_screenshot.py"), desk], timeout=60)
    if os.path.exists(desk):
        break
out["afterReloadDesktop"] = desk
out["afterReloadDesktopWritten"] = os.path.exists(desk)
B.call("jawa/select_things", action="clear")
tick(750)
sb = note("750 ticks after the reload (expect = the no-reload run)")
out["saveLoad"] = {"reloadMatchesSave": s1["dl"] == s0["dl"], "replayMatchesNoReload": sb["dl"] == sa["dl"],
                   "conserved": len({s0["total"], sa["total"], s1["total"], sb["total"]}) == 1}
# roles flipped mid-flow: put pool 1 back on top first
for i in range(3):
    for j in range(3):
        static(FLUIDP, "ProofFillWithFluid", "%d,%d,4,RM_Fluid_Water" % (POOLS[0][0] + i, POOLS[0][1] + j))
tick(250)
r0 = note("refilled, roles Intake/Outflow")
role(REELS[0], "Outflow")
role(REELS[1], "Intake")
tick(500)
r1 = note("roles swapped Outflow/Intake")
role(REELS[0], "Intake")
tick(500)
r2 = note("both Intake")
role(REELS[1], "Capped")
tick(260)
r3 = note("reel 2 Capped (one cycle to settle)")
tick(500)
r4 = note("reel 2 Capped, 500 ticks later (expect no change)")
role(REELS[1], "Outflow")
tick(500)
r5 = note("reel 2 back to Outflow")


def falling(a, b):    # pool 1 (the higher) lost water and pool 2 gained the same
    return b["dl"][0] < a["dl"][0] and b["dl"][1] > a["dl"][1] and a["total"] == b["total"]


out["roles"] = {"swappedStillLevels": falling(r0, r1), "bothIntakeStillLevels": falling(r1, r2),
                "cappedStops": r4["dl"] == r3["dl"], "cappedReadsNoLevelling": "Levelling" not in r4["inspect"][1],
                "uncappedResumes": falling(r4, r5) or abs(r4["dl"][0] - r4["dl"][1]) < 900,
                "conserved": len({r0["total"], r1["total"], r2["total"], r3["total"], r4["total"], r5["total"]}) == 1}
print(json.dumps({"saveLoad": out["saveLoad"], "roles": out["roles"], "load": out["load"]}))
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
