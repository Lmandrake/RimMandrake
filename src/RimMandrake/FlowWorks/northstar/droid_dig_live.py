"""DROID DIG live proof (DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL row 3: a Droidworks droid digs past the 2 m colonist cap).

  python.exe src/RimMandrake/FlowWorks/northstar/droid_dig_live.py [out.json] [--origin X,Z] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held; Droidworks (mandrake.rsw.droidworks) must be RUNNING, since
its patch FlowWorks_DroidsDigDeep.xml gives RSW_DW_FleshType_Droid the RM_MachineDigger mod extension
(RM_DigLabor.IsMachineLabour). Exit 0 = every row PASS. Written offline 2026-10-26; the mock is selftest_droid_dig_live.py.

Settings for the run (read back, restored after): shovelRequired ON (a machine digs bare-handed, so the droid needs no
shovel), machineDigEnabled ON, maxDigDepth 4 (2 m, shipped), maxMachineDigDepth 40, digToDepthEnabled ON,
digCostRisesWithDepth OFF, digFindsEnabled OFF, digDeepStoneEnabled OFF (a 2 m pit must stay soil to be cut again),
digLabourMultiplier 0.25 and digRockGroundEnabled OFF (the cut's price, see WAIT_TICKS).

WAIT_TICKS and the cut's price (SteveDesktop job J20261029T221052Z-6cdd1a, 2026-10-29): the D4 -> D5 cut is
WorkToCut(5, flat) = 12,800 x digLabourMultiplier (shipped 4.0, DIG_FILL_TUNE_HOURS_OF_SHOVEL_WORK) = 51,200 work, about
30,000 ticks even at MiningSpeed 1.0 (1.7 work a tick). The first runs never set the multiplier, waited 15,000 ticks, and read
an accepted, running dig as "no cut landed": a harness window, not the mod. At 0.25 (the slider floor) the cut is 3,200 work,
which 15,000 ticks covers down to MiningSpeed ~0.13. This row proves who may cut past 2 m, not how long a cut takes.

Scene (plot from --origin, default 40,40; 16 x 10, cleared and read back by validation_core.prepare_site): one Soil square at
(+8, +5) driven to D4 (2 m) by jawa/flowworks_excavation_drive and read back, RM_DigCanal designated on it. Every player pawn is
vanished first so nobody else takes the job.

The run LEAVES A LIVE COLONIST (STEVE_LANE_FIX_DEAD_COLONY_CANARY_RED): it vanishes the whole colony and then its own colonist
and droid, so it used to hand the session back with zero colonists; modcheck's vanilla canary, run after the drivers, then read
red ("no live colonist") and voided every live chain of the job, and the kept game voided the next jobs too (SteveDesktop
2026-10-26..29). The finally block spawns one Colonist when none is left, and records it as res["colony_left"].

Rows:
  DD_colonist_held_at_2m   a Colonist (Mining enabled, skill 10) probed on the D4 square: the dig work giver must NOT offer
                           RM_DigCanalJob (the colonist cap is in force). Offered = FAIL/MOD (the cap leaks).
  DD_droid_digs_past_2m    a player RSW_DW_OuterRim_ImperialLaborDroid (Droidworks' labour droid, kind read from the def dump
                           2026-10-26T13-58-35Z), Mining enabled, skill 10, no shovel: census needs=False, probe offers
                           RM_DigCanalJob, and an ordered cut takes the square D4 -> D5 within WAIT_TICKS.

ANTI-GUESSING NOTES
- Droidworks not in the running list: every row UNMEASURED/HARNESS (the patch cannot have applied).
- A colonist that is offered the job means the droid row could pass with no machine rule at all: the droid row is then
  UNMEASURED (the control failed), and the colonist row FAILs.
- A droid that does not spawn, or spawns with Mining disabled, is UNMEASURED/SITE (kind or work tags), never a mod FAIL.
- A droid offered the job bare with no cut landing in WAIT_TICKS is UNMEASURED/SITE (path, reach, speed), not FAIL;
  a droid NOT offered the job (or told it needs a shovel) is FAIL/MOD: the machine rule did not reach the droid.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ITEM = "DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
SH = "RimMandrake.FlowWorks.RM_Shovels"
DROIDWORKS = "mandrake.rsw.droidworks"
DROID_KIND = "RSW_DW_OuterRim_ImperialLaborDroid"
JOB = "RM_DigCanalJob"
CAP = 4                       # notches: 2 m, the shipped colonist cap
LABOUR = 0.25                 # RM_DigDepthMath.MinLabourMultiplier: the cheapest cut the mod allows
CUT_WORK = int(12800 * LABOUR)  # WorkToCut(5, costRisesWithDepth=False) = 3200 x PitDepth 4, x LABOUR = 3,200
WAIT_TICKS = 15000            # CUT_WORK / (1.7 work a tick x speed): ~1,900 ticks at MiningSpeed 1, enough down to ~0.13
ROW_IDS = ("DD_colonist_held_at_2m", "DD_droid_digs_past_2m")
RUN_SETTINGS = {"shovelRequired": True, "machineDigEnabled": True, "maxDigDepth": 4, "maxMachineDigDepth": 40,
                "digToDepthEnabled": True, "digCostRisesWithDepth": False, "digFindsEnabled": False,
                "digDeepStoneEnabled": False, "digLabourMultiplier": LABOUR, "digRockGroundEnabled": False}


def kv(text):
    """'a=1 b=True' -> dict (the census text)."""
    return dict(t.split("=", 1) for t in str(text or "").split() if "=" in t)


def job_of(probe):
    return ((probe or {}).get("workGiver") or {}).get("jobDef")


def colonist_verdict(probe):
    """-> (status, class) for the control: the work giver must not offer the colonist the D4 square."""
    if not isinstance(probe, dict) or probe.get("success") is False or "workGiver" not in probe:
        return "UNMEASURED", "HARNESS"
    if (probe.get("pawn") or {}).get("workTypeDisabled") is True:
        return "UNMEASURED", "SITE"
    return ("FAIL", "MOD") if job_of(probe) == JOB else ("PASS", "MOD")


def droid_verdict(control, probe, census, d0, d1):
    """-> (status, class, why) for the bar row."""
    if control != "PASS":
        return "UNMEASURED", "HARNESS", "the colonist control did not PASS: a droid cut would prove nothing"
    if d0 != CAP:
        return "UNMEASURED", "SITE", "the square is not at D%d (read D%s)" % (CAP, d0)
    if not isinstance(probe, dict) or probe.get("success") is False or "workGiver" not in probe:
        return "UNMEASURED", "HARNESS", "job probe refused"
    if (probe.get("pawn") or {}).get("workTypeDisabled") is True:
        return "UNMEASURED", "SITE", "the droid has Mining disabled"
    if job_of(probe) != JOB:
        return "FAIL", "MOD", "the droid is not offered %s past 2 m" % JOB
    if census.get("needs") != "False":
        return "FAIL", "MOD", "the droid is told it needs a shovel (needs=%s)" % census.get("needs")
    if d1 == CAP + 1:
        return "PASS", "MOD", "cut D%d -> D%d" % (d0, d1)
    if d1 is not None and d1 > CAP + 1:
        return "PASS", "MOD", "cut D%d -> D%d (more than one notch in the window)" % (d0, d1)
    return "UNMEASURED", "SITE", "offered the job bare, but no cut landed (D%s)" % d1


def run(B, V, a, out, stamp=None):
    rows = []
    res = {"script": "droid_dig_live.py", "item": ITEM, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows,
           "args": vars(a)}
    if stamp:
        stamp(res, B.call)   # validation.py reads a result only at the current mod hash AND deployed DLL

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-26s %-10s %-7s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def rest(cls, why):
        done = {r["id"] for r in rows}
        for rid in ROW_IDS:
            if rid not in done:
                row(rid, "UNMEASURED", cls, {"why": why})

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v)) or {"success": False}

    def depth(c):
        return (B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1) or {}).get("depth")

    def probe(c, pid):
        return B.call("jawa/flowworks_job_probe", x=c[0], z=c[1], kind="dig", pawnId=pid) or {}

    def census(pid):
        r = B.call("jawa/static_call", type=SH, method="ProofShovelCensus", args="pawn:" + str(pid).replace("Thing_", "")) or {}
        return kv(r.get("result")) if r.get("success") is not False else {}

    def cur_job(pid):
        """The pawn's curJob def name through jawa/attack_target_probe (ladder_wall_proof's read); None when unreadable."""
        try:
            r = B.call("jawa/attack_target_probe", pawn=str(pid), maxDist=1) or {}
        except Exception:      # noqa: BLE001 - a diagnostic read only; the row's verdict is the depth grid
            return None
        return r.get("curJob") if r.get("success") is not False else None

    def step(n):
        left = n
        while left > 0:
            k = min(left, 2500)
            B.call("rimworld/step_game_ticks", ticks=k, pauseFirst=True, timeoutMs=max(60000, k * 40))
            left -= k

    def spawn(kind, c):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction="player", count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id"), r

    def vanish(pid):
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")

    def live_colonists():
        # the canary's own rule (modcheck/helpers.is_colonist): a humanlike player pawn, not dead
        return [p.get("id") for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []
                if p.get("isPlayer") and p.get("intelligence") == "Humanlike" and not p.get("dead")]

    def leave_a_colonist(c):
        """The session invariant every driver owes the next one: at least one live colonist on the map."""
        try:
            alive = live_colonists()
            if alive:
                return {"live": len(alive), "spawned": None}
            got, r = spawn("Colonist", c)
            return {"live": len(live_colonists()), "spawned": got, "reply": None if got else str(r)[:160]}
        except Exception as ex:      # noqa: BLE001 - recorded; modcheck's after-driver check still sees the map
            return {"error": "%s: %s" % (type(ex).__name__, ex)}

    def ready_worker(pid):
        B.call("jawa/set_pawn_skill", pawn=pid, skill="Mining", level=10)
        import work_bar
        return work_bar.set_all(B.call, pid, [("Mining", 1), ("Hauling", 0), ("Cleaning", 0)])

    ox, oz = (int(v) for v in a.origin.split(","))
    plot = (ox, oz, 16, 10)
    cell = (ox + 8, oz + 5)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        rest("HARNESS", "no game in Playing")
        return 2
    prof = (B.call("jawa/companion_handshake") or {}).get("effectiveProfile")
    if prof != "test":
        rest("HARNESS", "companion profile is %r, not 'test'" % prof)
        return 2
    running = (res.get("env") or {}).get("running")
    if running is None:
        running = [p.lower() for p in (B.call("jawa/running_mods", details=False) or {}).get("packageIds") or []]
    res["droidworks_running"] = DROIDWORKS in (running or [])
    if not res["droidworks_running"]:
        rest("HARNESS", "%s is not in the running list (%d mods): deploy and enable Droidworks" % (DROIDWORKS, len(running or [])))
        return 2
    res["site_calm"] = V.site_calm(B)
    before = {k: sget(k) for k in RUN_SETTINGS}
    res["settings_before"] = before
    if any(v is None for v in before.values()):
        rest("HARNESS", "a FlowWorks setting is unreadable (deployed DLL without machine dig?): %s" % before)
        return 2
    try:
        bad = [k for k, v in RUN_SETTINGS.items() if sset(k, v).get("success") is False]
        res["settings_run"] = {k: sget(k) for k in RUN_SETTINGS}
        if bad:
            rest("HARNESS", "mod_settings_field set refused: %s" % bad)
            return 2
        site_rows = []
        if not V.prepare_site(B, plot, site_rows, "DD_site"):
            rest("SITE", "site not prepared: %s" % str(site_rows[:2])[:200])
            return 2
        for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
            if not p.get("dead") and p.get("isPlayer"):
                vanish(p.get("id"))
        B.call("jawa/set_terrain", terrainDef="Soil", x=cell[0], z=cell[1])
        d_now = depth(cell)
        drive = B.call("jawa/flowworks_excavation_drive", x=cell[0], z=cell[1], deepenLevels=max(0, CAP - (d_now or 0)),
                       setFill=-1) or {}
        d0 = depth(cell)
        res["site"] = {"cell": cell, "depthBefore": d_now, "drive": str(drive)[:200], "depth0": d0}
        if d0 != CAP:
            rest("SITE", "the square did not read D%d after the drive (D%s)" % (CAP, d0))
            return 2
        des = B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % cell) or {}
        res["site"]["designate"] = str(des)[:200]
        step(2)

        # 1. the control: a colonist is held at 2 m
        pid, rolls = None, []
        for _ in range(4):
            got, r = spawn("Colonist", (cell[0] - 3, cell[1]))
            if not got:
                rolls.append({"reply": str(r)[:120]})
                break
            step(5)
            p0 = probe(cell, got)
            rolls.append({"id": got, "miningDisabled": (p0.get("pawn") or {}).get("workTypeDisabled")})
            if (p0.get("pawn") or {}).get("workTypeDisabled") is not True:
                pid = got
                break
            vanish(got)
        res["colonist_rolls"] = rolls
        if not pid:
            rest("SITE", "no colonist with Mining enabled spawned")
            return 2
        bar_ok, bar_why = ready_worker(pid)
        step(2)
        pc = probe(cell, pid)
        st_c, cls_c = colonist_verdict(pc) if bar_ok else ("UNMEASURED", "HARNESS")
        row("DD_colonist_held_at_2m", st_c, cls_c, {"colonist": pid, "probe": pc.get("workGiver"), "pawn": pc.get("pawn"),
                                                    "workBar": bar_why, "depth": depth(cell)})
        vanish(pid)

        # 2. the bar: a Droidworks labour droid cuts the D4 square to D5
        did, r = spawn(DROID_KIND, (cell[0] - 3, cell[1]))
        if not did:
            row("DD_droid_digs_past_2m", "UNMEASURED", "SITE", {"why": "no %s spawned" % DROID_KIND, "reply": str(r)[:200]})
            return 1
        res["droid"] = {"id": did, "kind": DROID_KIND, "spawn": str(r)[:200]}
        bar_ok, bar_why = ready_worker(did)
        step(2)
        pd = probe(cell, did)
        cen = census(did)
        d0 = depth(cell)
        od = B.call("jawa/ordered_job", pawnId=did, jobDef=JOB, targetAX=cell[0], targetAZ=cell[1], waitTicks=0) or {}
        t, d1, trail = 0, d0, [[0, cur_job(did)]]
        while t < WAIT_TICKS:
            step(250)
            t += 250
            d1 = depth(cell)
            if d1 not in (None, d0):
                break
            if t % 2500 == 0:
                j = cur_job(did)
                if j != trail[-1][1]:
                    trail.append([t, j])     # (tick, curJob) at each change: shows whether the dig ran the whole window
        st, cls, why = droid_verdict(st_c, pd, cen, d0, d1)
        if st == "UNMEASURED" and why.startswith("offered the job bare"):
            why += "; %d ticks for %d work; curJob trail %s" % (t, CUT_WORK, trail)
        if not bar_ok and st != "PASS":
            st, cls, why = "UNMEASURED", "HARNESS", "work bar did not take: %s" % bar_why
        row("DD_droid_digs_past_2m", st, cls, {"droid": did, "why": why, "probe": pd.get("workGiver"), "pawn": pd.get("pawn"),
                                               "census": cen, "order": str(od)[:200], "depth0": d0, "depth": d1,
                                               "ticks": t if d1 != d0 else None, "cutWork": CUT_WORK, "jobTrail": trail})
        vanish(did)
    finally:
        for k, v in before.items():
            if v is not None:
                sset(k, v)
        res["settings_restored"] = {k: sget(k) for k in RUN_SETTINGS}
        res["colony_left"] = leave_a_colonist((cell[0] - 3, cell[1]))
        save()
    return 0 if all(r["status"] == "PASS" for r in rows) and len(rows) == len(ROW_IDS) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    import driver_stamp               # noqa: E402
    out = a.out or os.path.join(HERE, "droid_dig_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    return run(PH.PB(), PH.V, a, out, stamp=driver_stamp.stamp)


if __name__ == "__main__":
    sys.exit(main())
