"""PIT RESCUE live check (PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS A4: "a colonist downed in a sheer pit nobody can reach gets
a ladder job queued at the nearest wall (portable if spare/shallow, else fixed), it is built and the colonist rescued";
BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/pit_rescue_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]

Scene (plot from --origin, default 30,30; 16 x 12 cleared + read back): a sheer pit x = 6..8, z = 4..6 dug D 4 (2 m: nobody
without gear climbs it, climb_proof); a colonist DOWNED on its floor (7, 5) (pawn_force_incapacitate, no bleeding); every
other colonist on the map vanished, then two fresh rescuers on the rim (2, 5), (2, 6), undrafted; MEDICAL wooden beds at
(12, 9) and (14, 9) (a rescue needs a bed: one for the control, one for the victim); 100 steel + 100 wood at (3, 9) for the ladder.
PIT_RESCUE_FIX_LADDER_UP_NOBODY_COMES (HARNESS, bridge run 1 2026-10-23): with plain beds a rescuer who got tired slept in the
victim's bed and so OWNED it (vanilla claims a non-medical bed on lying down); RestUtility.FindBedFor then had no bed for the
victim and WorkGiver_RescueDowned never offered the rescue (2/2 runs FAIL, both with a rescuer LayDown at (14, 9)). Medical
beds are never claimed for sleep and are the ones a patient is carried to; each is set with jawa/set_bed_owner_type
medical=true and READ BACK (not medical: every row UNMEASURED SITE). The final bed census rides in the result ("beds"), and a
colonist not out while fewer than two beds were left for a patient (owned, or a rescuer lying in it) is SITE, not MOD;
with no census to read, it is UNMEASURED HARNESS.
Rows:
  RESCUE_LADDER_QUEUED   EXPECT within 500 ticks (RM_MapComponent_PitRescueLadder checks every 250) a ladder blueprint,
                         frame or ladder stands on a pit square.
  RESCUE_LADDER_BUILT    EXPECT within --ticks a built RM_LadderPortable / RM_Ladder in the pit.
  RESCUE_COLONIST_OUT    EXPECT within --ticks the downed colonist is off the pit floor (carried out; in the bed or on
                         the way). LIES: a colonist who died is not rescued (dead is read); the plain stepper is used
                         (the governed clock stops on a downed colonist by design).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
ITEM = "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS"
LADDERS = ("RM_LadderPortable", "RM_Ladder")


def free_patient_beds(census, taken=()):
    """Beds a downed colonist can still be carried to: one with an unowned sleeping slot (a medical bed has no owners; a
    plain one a sleeper lay down in is his) whose cell is not in <taken> (a rescuer lying in it: an injured one may rest in a
    medical bed). Census rows are jawa/set_bed_owner_type's (owners, sleepingSlots, pos); a row that does not say is not
    counted. The control's bed is not marked in the census and still counts, hence the caller's < 2."""
    n = 0
    for b in (census or {}).get("beds") or []:
        pos = b.get("pos") or {}
        if (b.get("owners") is not None and b.get("sleepingSlots") is not None and b["owners"] < b["sleepingSlots"]
                and (pos.get("x"), pos.get("z")) not in set(taken)):
            n += 1
    return n


def lying_cells(last):
    """Cells where a rescuer of the last trail entry is lying down (job LayDown*)."""
    cells = []
    for _id, at, job in (last or {}).get("rescuers") or []:
        if str(job or "").startswith("LayDown") and at:
            cells.append((at.get("x"), at.get("z")))
    return cells


def main(argv=None, bridge=None, validation=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="30,30")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=8000)
    a = ap.parse_args(argv)
    if bridge is None or validation is None:
        import proof_hose as PH  # noqa: E402
    V = validation or PH.V
    B = bridge or PH.PB()
    out = a.out or os.path.join(HERE, "pit_rescue_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "pit_rescue_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    IDS = ("RESCUE_LADDER_QUEUED", "RESCUE_LADDER_BUILT", "RESCUE_COLONIST_OUT")

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-24s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def all_rows(st, cls, det):
        for rid in IDS:
            if rid not in [r["id"] for r in rows]:
                row(rid, st, cls, det)

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        all_rows("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox, oz, 16, 12)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "rescue_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        all_rows("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    pit = {P(x, z) for x in range(6, 9) for z in range(4, 7)}
    for c in sorted(pit):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setFill=-1)
    for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
        if not p.get("dead") and p.get("isPlayer"):
            B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
    beds = []

    def medical_bed(c):
        B.call("jawa/build_batch", ops="Bed:%d,%d" % c, faction="player", wipeExisting=False, stuff="WoodLog")
        th = (B.call("jawa/list_things", defName="Bed", rect="%d,%d,1,1" % c, limit=1) or {}).get("things") or [{}]
        bid = th[0].get("id")
        r = (B.call("jawa/set_bed_owner_type", thing=bid, medical="true") or {}) if bid else {}
        beds.append({"cell": c, "id": bid, "medicalAfter": r.get("medicalAfter")})
    medical_bed(P(12, 9))
    for d, c in (("Steel", P(3, 9)), ("WoodLog", P(4, 9))):
        B.call("rimworld/spawn_thing", defName=d, stackCount=100, x=c[0], z=c[1])

    def spawn(c):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player", count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")
    victim = spawn(P(7, 5))
    rescuers = [spawn(P(2, 5)), spawn(P(2, 6))]
    # SITE (belt live 2026-10-22): bridge-spawned colonists can come with work types at priority 0 (the quarry check's job
    # probe read Mining priority 0, workActive False) -- the first rescue runs' "nobody finishes the frame" may be exactly
    # that. Construction, Hauling and Doctor (rescue) are set on.
    res["work"] = {}
    for r_ in rescuers:
        for wt in ("Construction", "Hauling", "Doctor"):
            w = B.call("jawa/set_work_priority", pawnId=r_, workType=wt, priority=1) or {}
            res["work"]["%s/%s" % (r_, wt)] = str(w)[:160]
    inc = B.call("jawa/pawn_force_incapacitate", pawn=victim, action="downed", allowBleedingWounds=False) or {}
    # can-fail control (belt run 3: nobody rescued even after the ladder stood): a colonist downed on OPEN ground; if he is
    # not rescued either, the scene cannot rescue at all (SITE), whatever the pit does
    control = spawn(P(13, 3))
    B.call("jawa/pawn_force_incapacitate", pawn=control, action="downed", allowBleedingWounds=False)
    res["control"] = control
    medical_bed(P(14, 9))
    res["scene"] = {"victim": victim, "rescuers": rescuers, "incap": str(inc)[:200], "beds": beds}
    if any(b.get("medicalAfter") is not True for b in beds):
        all_rows("UNMEASURED", "SITE", {"why": "a rescue bed is not medical (read back)", "beds": beds})
        for pid in [victim, control] + rescuers:
            if pid:
                B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
        return 2

    def ladder_in_pit():
        hits = []
        lt = B.call("jawa/list_things", rect="%d,%d,3,3" % P(6, 4), limit=60) or {}
        for t in lt.get("things") or []:
            d = str(t.get("def") or t.get("defName") or "")
            if any(l in d for l in LADDERS) or "Blueprint" in d or "Frame" in d:
                hits.append((d, t.get("x"), t.get("z")))
        return hits

    def victim_state(who=None):
        ps = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400, includeCorpses=True) or {}).get("pawns") or []}
        p = ps.get(who or victim) or {}
        return (p.get("x"), p.get("z")), p.get("downed"), p.get("dead"), p.get("spawned")
    control_moved = None

    t, queued_at, built_at, out_at = 0, None, None, None
    trail = []
    while t < a.ticks:
        step(250)
        t += 250
        lad = ladder_in_pit()
        pos, downed, dead, spawned = victim_state()
        cpos = victim_state(control)
        if control_moved is None and (cpos[0] != P(13, 3) or cpos[3] is False):
            control_moved = t
        jobs = []
        for r_ in rescuers:
            pr = B.call("jawa/attack_target_probe", pawn=r_, maxDist=60, _answer=True) or {}
            jobs.append([r_, pr.get("position"), pr.get("curJob")])
        trail.append({"t": t, "ladder": lad, "victim": [pos, downed, dead, spawned], "rescuers": jobs})
        if lad and queued_at is None:
            queued_at = t
        if built_at is None and any(d in LADDERS for d, _x, _z in lad):
            built_at = t
        if out_at is None and (pos not in pit and pos[0] is not None or spawned is False) and not dead:
            out_at = t
        if dead:
            break
        if out_at is not None:
            break
        # belt live 2026-10-22: idle rescuers hauled the wood into the frame and then never took FinishFrame (8000 ticks,
        # 'Work left' untouched) while an ORDERED FinishFrame completed it. After 2000 stalled ticks the frame is finished
        # by order (recorded as an assist) so the rescue half can still be measured; RESCUE_LADDER_BUILT stays FAIL.
        frames = [x for x in lad if x[0].startswith("Frame_")]
        if frames and built_at is None and t >= 2000 and not res.get("assist"):
            fid = (B.call("jawa/list_things", defName=frames[0][0], rect="%d,%d,1,1" % (frames[0][1], frames[0][2]), limit=1)
                   or {}).get("things") or [{}]
            o = B.call("jawa/ordered_job", pawnId=rescuers[0], jobDef="FinishFrame", targetAId=fid[0].get("id")) or {}
            res["assist"] = {"t": t, "frame": fid[0].get("id"), "order": {k: o.get(k) for k in ("accepted", "afterJobDef")}}
        if t % 1000 == 0:
            save()
    res["trail"] = trail
    det = {"queuedAt": queued_at, "builtAt": built_at, "outAt": out_at, "last": trail[-1] if trail else None}
    row("RESCUE_LADDER_QUEUED", "PASS" if queued_at is not None and queued_at <= 500 else "FAIL", "MOD", det)
    det["assist"] = res.get("assist")
    row("RESCUE_LADDER_BUILT", "PASS" if built_at is not None and not res.get("assist") else "FAIL", "MOD", det)
    dead = trail and trail[-1]["victim"][2]
    det["controlRescuedAt"] = control_moved
    res["beds"] = B.call("jawa/set_bed_owner_type") or {}
    det["freePatientBeds"] = free_patient_beds(res["beds"], lying_cells(trail[-1] if trail else None))
    no_census = out_at is None and not (res["beds"].get("beds") or [])
    no_rescue_here = control_moved is None
    # a FAIL with no bed left for the victim (the control holds one) is the scene's, not the mod's
    no_bed = out_at is None and not no_census and det["freePatientBeds"] < 2
    site = dead or (no_rescue_here and out_at is None) or no_bed
    row("RESCUE_COLONIST_OUT", "UNMEASURED" if site or no_census else ("PASS" if out_at is not None else "FAIL"),
        "HARNESS" if no_census and not site else ("SITE" if site else "MOD"), det)
    for pid in [victim, control] + rescuers:
        if pid:
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
