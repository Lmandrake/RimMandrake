"""PIT RESCUE live check (PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS A4: "a colonist downed in a sheer pit nobody can reach gets
a ladder job queued at the nearest wall (portable if spare/shallow, else fixed), it is built and the colonist rescued";
BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/pit_rescue_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]
      [--scene rescue|escape] [--raised-ticks N]

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

--scene escape (PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN; LADDER_PARITY_BUILD_NO_KEYS_REQUIRED A6, owner Q4 2026-10-23: "A prison
ladder left down is equivalent to a prison door left open... same game rules apply."): the same plot and sheer pit, an RM_Ladder
on its west wall (6, 5), a hostile Villager on the floor (8, 5) made the colony's prisoner (pawn_set_guest_status, read back).
Phase 1 RAISED (RM_PromotionProofs.ProofLadder raise, read back) for --raised-ticks; phase 2 LOWERED for up to --ticks or
until he is off the pit floor. Each phase reads RM_LadderParity.ProofLadderParity "may:" (mayClimb, letsOut) and counts the
new "escap" lines in rimworld/list_messages (vanilla JobGiver_PrisonerEscape sends MessagePrisonerIsEscaping as it starts the
escape: a Goto with exitMapOnArrival); in the LOWERED phase a sampled Goto counts as the escape started too (a live message can expire between
samples). Verdict: escape_verdict (pure; selftest_pit_escape_live.py).
  LADDER_RAISED_PRISONER_STAYS     EXPECT no escape message and the prisoner on the pit floor at every sample.
  LADDER_LOWERED_PRISONER_ESCAPES  EXPECT an escape message and the prisoner off the pit floor (or gone off the map).
  LIES: a ladder not read back in the wanted state, a pawn not a prisoner, a dead prisoner -> UNMEASURED SITE; a prisoner
  already out when the lowered phase starts -> UNMEASURED SITE; asleep (LayDown) through a quiet lowered phase -> UNMEASURED
  SITE (vanilla does not escape in his sleep), never MOD.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
LADP = "RimMandrake.FlowWorks.RM_LadderParity"
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


ESCAPE_ITEM = "PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN"
ESCAPE_IDS = ("LADDER_RAISED_PRISONER_STAYS", "LADDER_LOWERED_PRISONER_ESCAPES")


def kv(txt):
    """'a=1 b=x' -> {'a': '1', 'b': 'x'} (the ProofLadder / ProofLadderParity reply shape)."""
    out = {}
    for tok in str(txt or "").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def escape_lines(reply):
    """Every string anywhere in a rimworld/list_messages reply that speaks of an escape (lowercase 'escap')."""
    found = []

    def walk(x):
        if isinstance(x, str):
            if "escap" in x.lower():
                found.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    walk((reply or {}).get("messages") if isinstance(reply, dict) else reply)
    return found


def new_lines(before, after):
    """Lines in <after> beyond their count in <before> (a ring of messages: the same text may repeat)."""
    left = list(before or [])
    out = []
    for line in after or []:
        if line in left:
            left.remove(line)
        else:
            out.append(line)
    return out


def escape_verdict(raised, lowered):
    """Pure verdict of the escape scene. Each phase: {"ladder": ProofLadder kv, "prisoner": bool read back, "startInPit": bool,
    "trail": [{"t", "inPit", "gone", "dead", "job"}], "escapeMsgs": int, "escapeJob": bool (a Goto sampled), "may":
    ProofLadderParity may: kv}. A phase the driver
    never reached is None. Returns [(row id, status, class, detail)] for ESCAPE_IDS, in order."""
    rows = []
    for rid, ph, want_raised in ((ESCAPE_IDS[0], raised, True), (ESCAPE_IDS[1], lowered, False)):
        if not ph:
            rows.append((rid, "UNMEASURED", "HARNESS", {"why": "phase not run"}))
            continue
        det = {k: ph.get(k) for k in ("ladder", "may", "escapeMsgs", "escapeJob", "startInPit")}
        trail = ph.get("trail") or []
        det["samples"] = len(trail)
        det["last"] = trail[-1] if trail else None
        lad = ph.get("ladder") or {}
        why = None
        if lad.get("present") != "True" or lad.get("raised") != str(want_raised):
            why = "ladder not read back %s" % ("raised" if want_raised else "lowered")
        elif not ph.get("prisoner"):
            why = "the pawn is not the colony's prisoner (read back)"
        elif not trail:
            why = "no samples"
        elif any(s.get("dead") for s in trail):
            why = "the prisoner died"
        elif not ph.get("startInPit"):
            why = "the prisoner was not on the pit floor when the phase began"
        if why:
            det["why"] = why
            rows.append((rid, "UNMEASURED", "SITE", det))
            continue
        # escape started: MessagePrisonerIsEscaping; when LOWERED also the Goto it gives (rimworld/list_messages may read the
        # live, expiring messages, so a message can fall between samples). Not when RAISED: vanilla gives other plain Gotos
        # too (JobGiver_MoveToStandable, FleePotentialExplosion, SeekAllowedArea), so a Goto alone never fails that row.
        msgs = int(ph.get("escapeMsgs") or 0) + (1 if ph.get("escapeJob") and not want_raised else 0)
        out = any((not s.get("inPit")) or s.get("gone") for s in trail)
        if want_raised:
            rows.append((rid, "PASS" if msgs == 0 and not out else "FAIL", "MOD", det))
            continue
        if msgs > 0 and out:
            rows.append((rid, "PASS", "MOD", det))
            continue
        tail = [str(s.get("job") or "") for s in trail[-3:]]
        if msgs == 0 and not out and len(tail) == 3 and all(j.startswith("LayDown") for j in tail):
            det["why"] = "asleep through the lowered phase (no escape is started in sleep)"
            rows.append((rid, "UNMEASURED", "SITE", det))
            continue
        rows.append((rid, "FAIL", "MOD", det))
    return rows


def run_escape(a, B, V, res, row, all_rows, step, P):
    """The escape scene (module docstring, --scene escape); the plot is already reset and prepared."""
    pit = {P(x, z) for x in range(6, 9) for z in range(4, 7)}
    for c in sorted(pit):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setBodyWaterM=-1)
    foot, start = P(6, 5), P(8, 5)
    lad = B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d" % foot) or {}
    step(60)
    sp = B.call("jawa/spawn_pawn", kindDef="Villager", x=start[0], z=start[1], faction="hostile", count=1) or {}
    pid = ((sp.get("pawns") or [{}])[0]).get("id")
    gs = (B.call("jawa/pawn_set_guest_status", pawn=pid, guestStatus="Prisoner", hostFaction="PlayerColony") or {}) if pid else {}
    res["scene"] = {"ladder": {k: lad.get(k) for k in ("success", "thingsPlaced")}, "prisoner": pid, "guest": str(gs)[:200]}

    def sc(typ, method, arg):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        return str(r.get("result") if r.get("result") is not None else "")

    def state():
        ps = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400, includeCorpses=True) or {}).get("pawns") or []}
        p = ps.get(pid)
        if p is None:  # list_pawns lists spawned pawns and corpses: absent = off the map (an escape ends at the edge)
            return {"gone": True, "inPit": False, "dead": False}
        pos = (p.get("x"), p.get("z"))
        return {"pos": pos, "inPit": pos in pit, "gone": p.get("spawned") is False, "dead": bool(p.get("dead"))}
    # list_pawns carries no prisoner flag; the guest tool reads GuestStatus and HostFaction back after the engine call
    is_prisoner = gs.get("guestStatusAfter") == "Prisoner" and bool(gs.get("hostFactionAfter"))
    # ProofLadderParity takes the thingIDNumber (int.TryParse); spawn_pawn gives the ThingID ("Human123")
    m = re.search(r"(\d+)$", str(pid or ""))
    num = int(m.group(1)) if m else None

    def phase(op, ticks, stop_out):
        ladder = kv(sc(PROMO, "ProofLadder", "%d,%d,%s" % (foot[0], foot[1], op)))
        step(2)
        s0 = state()
        ph = {"ladder": ladder, "prisoner": is_prisoner, "startInPit": bool(s0.get("inPit") and not s0.get("gone")),
              "may": kv(sc(LADP, "ProofLadderParity", "may:%d,%d,%d" % (num, foot[0], foot[1]))) if num else {}}
        before = escape_lines(B.call("rimworld/list_messages", limit=200))
        trail, t, msgs = [], 0, []
        while t < ticks:
            step(250)
            t += 250
            s = state()
            pr = B.call("jawa/attack_target_probe", pawn=pid, maxDist=60, _answer=True) or {}
            s.update({"t": t, "job": pr.get("curJob")})
            trail.append(s)
            msgs = new_lines(before, escape_lines(B.call("rimworld/list_messages", limit=200)))
            if s.get("dead") or (stop_out and (msgs or s["job"] == "Goto") and (s["gone"] or not s["inPit"])):
                break
        ph.update({"trail": trail, "escapeMsgs": len(msgs), "escapeText": msgs[:3],
                   "escapeJob": any(s_.get("job") == "Goto" for s_ in trail)})
        return ph
    if not pid or not (lad.get("success") and lad.get("thingsPlaced")):
        for rid in ESCAPE_IDS:
            row(rid, "UNMEASURED", "SITE", {"why": "scene not staged", "scene": res["scene"]})
        if pid:
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
        return 2
    raised = phase("raise", a.raised_ticks, False)
    lowered = phase("lower", a.ticks, True) if raised["trail"] and not raised["trail"][-1].get("dead") else None
    res["phases"] = {"raised": raised, "lowered": lowered}
    for rid, st, cls, det in escape_verdict(raised, lowered):
        row(rid, st, cls, det)
    if pid:
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return 0 if all(r["status"] == "PASS" for r in res["rows"]) else 1


def main(argv=None, bridge=None, validation=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="30,30")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=8000)
    ap.add_argument("--scene", choices=("rescue", "escape"), default="rescue")
    ap.add_argument("--raised-ticks", type=int, default=2500)
    a = ap.parse_args(argv)
    if bridge is None or validation is None:
        import proof_hose as PH  # noqa: E402
    V = validation or PH.V
    B = bridge or PH.PB()
    out = a.out or os.path.join(HERE, "pit_rescue_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    rows = []
    res = {"script": "pit_rescue_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    IDS = ESCAPE_IDS if a.scene == "escape" else ("RESCUE_LADDER_QUEUED", "RESCUE_LADDER_BUILT", "RESCUE_COLONIST_OUT")
    item = ESCAPE_ITEM if a.scene == "escape" else ITEM

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": item, "detail": det})
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
    if a.scene == "escape":
        rc = run_escape(a, B, V, res, row, all_rows, step, P)
        save()
        return rc
    pit = {P(x, z) for x in range(6, 9) for z in range(4, 7)}
    for c in sorted(pit):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setBodyWaterM=-1)
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
