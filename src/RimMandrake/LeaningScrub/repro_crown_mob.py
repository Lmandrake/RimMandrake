#!/usr/bin/env python3
"""LEANINGSCRUB_CROWN_MOB_LIVE_1: rerun the item's OWN crown repro live; name why dustflutters ranged far, show the mob.

On 2026-10-07 (validation.py crown chain) all three RM_Dustflutter, spawned ~16-20 cells from an RM_CrownVenomvine in a
locked RM_Stall, ended 23-70 cells off with crownMobEnabled ON or OFF. RM_MapComponent_CrownMob claims only an IDLE
mobber (no job / Wait_Wander / GotoWander / Wait), so whatever moved them held them in another job. Offline read
(2026-11-03), two suspects that answer with JobDefOf.Flee:
  bloom  RM_RunwayBloom: a colonist, or an animal of body size >= 1, moving on a non-tree plant within 12 cells makes a
         dustflutter Erupt (Flee 40 cells + real takeoff, RM_LeaningScrubFauna.xml RM_RunwayBloomExtension);
  scent  RM_TheLeanPatches.AnimalFlee_Postfix: a humanlike upwind within leanScentRange (24);
plus vanilla JobGiver_AnimalFlee (an AlwaysFlee thing within 18 -- the item lists Tornado, RM_SteamDevil,
RM_SandBusterMound, RM_DuneGale -- or a predator / hostile). A third hole was FIXED offline in the same change: the Stall
freeze exempted an airborne animal, and vanilla wander never waits while flying (RM_StallHuntKernel.Freezes).

Repro (the item's words): crown pad = map centre -45,+45, RM_Stall locked, RM_CrownVenomvine at the anchor, 3
RM_Dustflutter at (x+16+i, z+4-4i), faction none; jobs (jawa/site_state) every 50 ticks + the AlwaysFlee defs within 18
(jawa/list_things). The job read is the item's 500 ticks; the walk runs on to 2000 because a crown Goto is Walk urgency
(Pawn_PathFollower: x2, at least 50 ticks a cell, so 20 cells is ~1000 ticks after a send on a 250-tick pass).
Arms, fresh dustflutters each: mob_on, mob_off, mob_off_bloom_off, mob_off_scent_off, mob_on_quiet (bloom+scent off).
  exit 0  every far move (>= FAR cells from the stand at any sample, in mob_on / mob_off) has its non-wander job NAMED
          and ATTRIBUTED (a toggle arm that stays near, or an AlwaysFlee thing sampled within 18), AND
          mob_on_quiet gathers >= 2 of 3 within NEAR of the stand; if no far move reproduces, mob_on must gather instead;
  exit 1  a far move whose job is not named or not attributed, an airborne wander (the fixed hole is back), or the
          mob does not gather on a quiet site -- never a pass;
  exit 2  the site could not be staged or read (UNMEASURED).
Usage: repro_crown_mob.py [--out <json>]   (live; python.exe on archmagi)   |   repro_crown_mob.py --selftest
"""
import json
import math
import os
import sys

FLUTTER, CROWN = "RM_Dustflutter", "RM_CrownVenomvine"
FLEE_DEFS = ("Tornado", "RM_SteamDevil", "RM_SandBusterMound", "RM_DuneGale")
FLEE_R = 18
WANDER = {None, "", "GotoWander", "Wait_Wander", "Wait", "Wait_MaintainPosture"}
PAD = (-45, 45)
STEP, JOB_STEPS, STEPS = 50, 10, 40     # jobs every 50 ticks; the item's 500, the walk to 2000
FAR, NEAR = 23.0, 6.0    # 23 = the 10-07 floor (a flutter starts 16-18 off); 6 = validation.py crown_chain's `near`
SETTINGS = "RimMandrake.LeaningScrub.RM_LeaningScrubSettings"
ARMS = (("mob_on", {"crownMobEnabled": True, "runwayBloomEnabled": True, "leanScentEnabled": True}),
        ("mob_off", {"crownMobEnabled": False, "runwayBloomEnabled": True, "leanScentEnabled": True}),
        ("mob_off_bloom_off", {"crownMobEnabled": False, "runwayBloomEnabled": False, "leanScentEnabled": True}),
        ("mob_off_scent_off", {"crownMobEnabled": False, "runwayBloomEnabled": True, "leanScentEnabled": False}),
        ("mob_on_quiet", {"crownMobEnabled": True, "runwayBloomEnabled": False, "leanScentEnabled": False}))
TOUCHED = ("crownMobEnabled", "runwayBloomEnabled", "leanScentEnabled", "stallFreezeEnabled")


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def summarise(track, stand, min_pts=2):
    """One dustflutter's samples -> start/max/final distance to the stand and the jobs held while it moved AWAY.

    None (unmeasured) when fewer than min_pts samples carry a position or the last sample has none: a partial read
    must never pass. Jobs are per pawn and only from steps that took it farther from the stand, so an earlier Goto
    toward the crown, or another pawn's Flee, cannot name this pawn's excursion."""
    if not track or track[-1].get("x") is None:
        return None
    pts = [s for s in track if s.get("x") is not None and s.get("z") is not None]
    if len(pts) < max(2, min_pts):
        return None
    xy = [(s["x"], s["z"]) for s in pts]
    jobs, airborne_wander = set(), False
    for prev, cur in zip(pts, pts[1:]):
        if _dist((prev["x"], prev["z"]), (cur["x"], cur["z"])) < 1.0:
            continue
        for s in (prev, cur):
            if s.get("flying") and s.get("job") in WANDER:
                airborne_wander = True
        if _dist((cur["x"], cur["z"]), stand) > _dist((prev["x"], prev["z"]), stand):
            for s in (prev, cur):
                if s.get("job") not in WANDER:
                    jobs.add(s.get("job"))
    far = max(_dist(q, stand) for q in xy) >= FAR
    return {"start": _dist(xy[0], stand), "max": max(_dist(q, stand) for q in xy), "final": _dist(xy[-1], stand),
            "jobs": sorted(j for j in jobs if j), "airborneWander": airborne_wander, "far": far}


MIN_PTS = int(0.8 * (STEPS + 1))


def arm_summary(arm):
    stand = tuple(arm["stand"])
    rows = [summarise(t, stand, MIN_PTS) for t in arm["tracks"].values()]
    rows = [r for r in rows if r]
    far = [r for r in rows if r["far"]]
    return {"n": len(rows), "far": len(far), "gathered": sum(r["final"] <= NEAR for r in rows),
            "unnamed": sum(not r["jobs"] for r in far),
            "jobs": sorted(set(j for r in far for j in r["jobs"])),
            "airborneWander": any(r["airborneWander"] for r in rows),
            "threats": sorted(set(arm.get("threats") or [])),
            "nearby": sorted(set(q.get("kind") or "?" for q in (arm.get("near_pawns") or [])))}


def verdict(arms):
    """arms: {name: {"stand": (x, z), "tracks": {pid: [samples]}, "threats": [AlwaysFlee defs within 18]}} -> (exit, lines)."""
    S = dict((k, arm_summary(v)) for k, v in arms.items())
    lines = ["%s: far %d/%d gathered %d jobs %s threats %s%s" % (k, s["far"], s["n"], s["gathered"], s["jobs"],
             s["threats"], " AIRBORNE-WANDER" if s["airborneWander"] else "") for k, s in sorted(S.items())]
    missing = [k for k, _ in ARMS if k not in S or S[k]["n"] < 2]
    if missing:
        return 2, lines + ["UNMEASURED: fewer than 2 dustflutters fully read (%d of %d samples) in arm(s) %s"
                           % (MIN_PTS, STEPS + 1, missing)]
    if any(s["airborneWander"] for s in S.values()):
        return 1, lines + ["FAIL: an airborne dustflutter wandered in the Stall: the freeze still exempts flight"]
    bad = []
    off = S["mob_off"]
    for k in ("mob_off", "mob_on"):
        s = S[k]
        if not s["far"]:
            continue
        if s["unnamed"]:
            bad.append("%s: %d of %d far move(s) held only wander-family jobs while moving away: the job is NOT named"
                       % (k, s["unnamed"], s["far"]))
            continue
        if k == "mob_on" and not off["far"]:
            # the toggle arms all run with the mob OFF, so they can only explain a move mob_off shares
            bad.append("mob_on: far move under %s that mob_off does not share: the crown mob itself drives it"
                       % s["jobs"])
            continue
        cause = []
        if not S["mob_off_bloom_off"]["far"]:
            cause.append("runway bloom (RM_RunwayBloom Erupt)")
        if not S["mob_off_scent_off"]["far"]:
            cause.append("lean scent (RM_TheLeanPatches.AnimalFlee_Postfix)")
        if not cause and s["threats"]:
            cause.append("vanilla JobGiver_AnimalFlee from %s" % ", ".join(s["threats"]))
        if not cause:
            bad.append("%s: far move under %s but no toggle arm stays near and no AlwaysFlee thing within %d: "
                       "the cause is NOT attributed (pawns sampled within %d: %s)" % (k, s["jobs"], FLEE_R, FLEE_R,
                                                                                     s["nearby"] or "none"))
            continue
        lines.append("NAMED %s: far move under %s; cause: %s" % (k, s["jobs"], " + ".join(cause)))
    if bad:
        return 1, lines + ["FAIL: " + b for b in bad]
    reproduced = S["mob_on"]["far"] or S["mob_off"]["far"]
    mob = "mob_on_quiet" if reproduced else "mob_on"
    if S[mob]["gathered"] < 2:
        return 1, lines + ["FAIL: %s gathered %d of %d dustflutters within %.0f cells of the crown stand"
                           % (mob, S[mob]["gathered"], S[mob]["n"], NEAR)]
    if not reproduced:
        lines.append("NOT REPRODUCED: no far move in mob_on or mob_off; the 10-07 range did not recur")
    lines.append("PASS: %s gathers %d of %d within %.0f cells" % (mob, S[mob]["gathered"], S[mob]["n"], NEAR))
    return 0, lines


def live(out_path):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
    import rimbridge_client as rb  # noqa: E402

    h, p, tok = rb.resolve_endpoint()
    S = rb.RimBridge(host=h, port=p, token=tok, timeout=120.0)
    try:
        S.connect()
    except rb.RimBridgeError as e:
        print("UNMEASURED: bridge unreachable: %s" % str(e)[:200])
        return 2

    def call(tool, **kw):
        try:
            return S.call(tool, kw) or {}
        except rb.RimBridgeError as e:
            return {"success": False, "error": str(e)}

    def ticks():
        return (call("rimworld/get_game_info") or {}).get("ticksGame")

    def setting(field, value):
        call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=str(value))
        got = call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field).get("value")
        return str(got).strip().lower() == str(value).lower()

    mi = call("jawa/map_info")
    if not mi.get("sizeX"):
        print("UNMEASURED: no current map: %s" % str(mi)[:200])
        return 2
    x, z = mi["sizeX"] // 2 + PAD[0], mi["sizeZ"] // 2 + PAD[1]
    call("jawa/set_game_speed", speed=0)
    rec = {"map": {k: mi.get(k) for k in ("sizeX", "sizeZ", "mapBiome", "tile")}, "anchor": [x, z], "arms": {}}
    # the pad as validation._prep lays it, MINUS _settle_bystanders and _clear_wildlife (the 10-07 shape)
    rect = "%d,%d,%d,%d" % (x - 16, z - 16, 32, 32)
    call("jawa/destroy_batch", rects=rect, categories="All")
    call("jawa/set_roof_batch", ops="None:%s" % rect)
    call("jawa/set_terrain_batch", ops="Soil:%s" % rect, layer="top")
    call("jawa/weather_set", weather="RM_Stall", lockWeather=True)
    cur = (call("jawa/weather_get") or {}).get("weather")
    cur = cur.get("current") if isinstance(cur, dict) else cur
    rec["weather"] = cur
    if cur != "RM_Stall":
        print("UNMEASURED: RM_Stall did not lock (read back %r)" % cur)
        call("jawa/weather_set", unlock=True)
        return 2
    call("jawa/set_plants", ops="%s:%d,%d,1,1" % (CROWN, x, z), growth=1.0)
    stood = (call("jawa/list_things", defName=CROWN, rect="%d,%d,1,1" % (x, z)).get("things") or [])
    if not stood:
        print("UNMEASURED: %s did not stand at %d,%d after set_plants" % (CROWN, x, z))
        call("jawa/weather_set", unlock=True)
        return 2

    def arm(name, fields):
        # the freeze is the premise of every arm (an unfrozen flyer wanders airborne by vanilla design)
        for f, v in list(fields.items()) + [("stallFreezeEnabled", True)]:
            # restore-check: ok live()'s finally puts back every field's captured prior; arm runs only inside that try
            if not setting(f, v):
                print("UNMEASURED: %s=%s did not take" % (f, v))
                return False
        ids = []
        for i in range(3):
            sp = call("jawa/spawn_pawn", kindDef=FLUTTER, x=x + 16 + i, z=z + 4 - 4 * i, faction="none", count=1)
            pid = (((sp or {}).get("pawns") or [{}])[0]).get("id")
            if not pid:
                print("UNMEASURED: spawn %s failed: %s" % (FLUTTER, str(sp)[:200]))
                for done in ids:
                    call("jawa/pawn_force_incapacitate", pawn=done, action="vanish")
                return False
            ids.append(pid)
            for need in ("Food", "Rest"):
                call("jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)
        tracks, threats, others = dict((pid, []) for pid in ids), set(), []
        t0 = last = ticks()
        for i in range(STEPS + 1):
            if i:
                call("rimworld/step_game_ticks", ticks=STEP, pauseFirst=True)
            now = ticks()
            if now is None or (i and (now - last) < STEP):
                print("UNMEASURED: %s: the clock did not advance %d ticks (%r -> %r)" % (name, STEP, last, now))
                for pid in ids:
                    call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
                return False
            last = now
            rows = dict((q.get("id"), q) for q in (call("jawa/list_pawns", limit=1000).get("pawns") or []))
            jobs = dict((q.get("id"), q) for q in (call("jawa/site_state").get("pawns") or []))
            for pid in ids:
                row, js = rows.get(pid) or {}, jobs.get(pid) or {}
                fl = ((call("jawa/pawn_flight", action="report", pawn=pid).get("pawns") or [{}])[0]) if row else {}
                tracks[pid].append({"tick": now, "x": row.get("x"), "z": row.get("z"), "job": js.get("job"),
                                    "targetA": js.get("targetA"), "flying": fl.get("flying")})
            if i > JOB_STEPS and i % 5:
                continue   # the threat census at every step of the item's 500 ticks, then every 250
            for pid in ids:
                r = rows.get(pid) or {}
                if r.get("x") is None:
                    continue
                bx, bz = max(0, r["x"] - FLEE_R), max(0, r["z"] - FLEE_R)   # a negative corner fails the rect parse
                box = "%d,%d,%d,%d" % (bx, bz, r["x"] + FLEE_R + 1 - bx, r["z"] + FLEE_R + 1 - bz)
                for th in (call("jawa/list_things", defName=",".join(FLEE_DEFS), rect=box, limit=200).get("things") or []):
                    if th.get("x") is None or _dist((th["x"], th.get("z", 0)), (r["x"], r["z"])) <= FLEE_R:
                        threats.add(th.get("def") or th.get("defName") or str(th)[:40])
                for q in rows.values():
                    if q.get("id") in ids or q.get("x") is None or q.get("kindDef") == FLUTTER:
                        continue
                    if _dist((q["x"], q["z"]), (r["x"], r["z"])) <= FLEE_R:
                        others.append({"tick": now, "id": q.get("id"), "kind": q.get("kindDef"), "x": q["x"],
                                       "z": q["z"], "faction": q.get("faction"),
                                       "job": (jobs.get(q.get("id")) or {}).get("job")})
        call("jawa/set_game_speed", speed=0)
        for pid in ids:
            call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
        rec["arms"][name] = {"settings": fields, "stand": [x, z], "ids": ids, "startTick": t0, "tracks": tracks,
                             "threats": sorted(threats), "near_pawns": others}
        return True

    priors = {}
    for f in TOUCHED:
        priors[f] = call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f).get("value")
        if priors[f] is None:
            print("UNMEASURED: could not read %s before touching it" % f)
            call("jawa/weather_set", unlock=True)
            return 2
    ok = True
    try:
        for name, fields in ARMS:
            if not arm(name, fields):
                ok = False
                break
    finally:
        for f, was in priors.items():
            setting(f, was)
        call("jawa/weather_set", weather="Clear", lockWeather=True)
        call("jawa/weather_set", unlock=True)
    code, lines = verdict(rec["arms"]) if ok else (2, ["UNMEASURED: an arm could not be staged"])
    rec["verdict"] = {"exit": code, "lines": lines}
    for ln in lines:
        print(ln)
    if out_path:
        with open(out_path, "w") as fh:
            json.dump(rec, fh, indent=1)
        print("record: %s" % out_path)
    return code


# ---------------------------------------------------------------------------------------------------------- selftest

def selftest():
    stand = (100, 100)

    def tr(points, job="Wait_Wander", flying=None):
        return [{"x": px, "z": pz, "job": job, "flying": flying} for px, pz in points]

    held = [tr([(116, 104)] * 41), tr([(117, 100)] * 41), tr([(118, 96)] * 41)]
    gathered = [tr([(116 - k, 104) for k in range(14)] + [(102, 101)] * 27, "Goto")] * 3
    fled = [tr([(116 + 2 * k, 104) for k in range(20)] + [(156, 104)] * 21, "Flee")] * 3

    def arms(**over):
        base = dict((k, held) for k, _ in ARMS)
        base["mob_on_quiet"] = gathered
        base.update(over)
        return dict((k, {"stand": stand, "tracks": dict(("p%d" % i, t) for i, t in enumerate(v)),
                         "threats": []}) for k, v in base.items())

    cases = []
    # bloom: far Flee in both mob arms and the scent-off arm, the bloom-off arm holds -> named, attributed, quiet gathers
    cases.append(("bloom named", arms(mob_on=fled, mob_off=fled, mob_off_scent_off=fled), 0, "runway bloom"))
    cases.append(("scent named", arms(mob_on=fled, mob_off=fled, mob_off_bloom_off=fled), 0, "lean scent"))
    a = arms(mob_on=fled, mob_off=fled, mob_off_bloom_off=fled, mob_off_scent_off=fled)
    a["mob_off"]["threats"] = a["mob_on"]["threats"] = ["Tornado"]
    cases.append(("vanilla named", a, 0, "JobGiver_AnimalFlee from Tornado"))
    cases.append(("unattributed", arms(mob_on=fled, mob_off=fled, mob_off_bloom_off=fled, mob_off_scent_off=fled),
                  1, "NOT attributed"))
    cases.append(("wander-only far", arms(mob_off=[tr([(116 + 2 * k, 104) for k in range(41)], "GotoWander")] * 3,
                                          mob_off_bloom_off=fled, mob_off_scent_off=fled), 1, "NOT named"))
    cases.append(("quiet mob fails", arms(mob_on=fled, mob_off=fled, mob_off_scent_off=fled, mob_on_quiet=held),
                  1, "mob_on_quiet gathered 0"))
    cases.append(("not reproduced, mob gathers", arms(mob_on=gathered), 0, "NOT REPRODUCED"))
    cases.append(("not reproduced, mob idle", arms(), 1, "mob_on gathered 0"))
    cases.append(("airborne wander", arms(mob_on=[tr([(116 + k, 104) for k in range(41)], "GotoWander", True)] * 3),
                  1, "freeze still exempts"))
    short = arms()
    short["mob_off"]["tracks"] = {"p0": tr([(116, 104)])}
    cases.append(("unmeasured arm", short, 2, "UNMEASURED"))
    # GPT review 2026-11-03: one Flee pawn must not name another pawn's wander excursion
    mixed = [fled[0], tr([(116 + 2 * k, 104) for k in range(41)], "GotoWander"), held[0]]
    cases.append(("mixed pawns", arms(mob_off=mixed, mob_on=fled, mob_off_scent_off=fled), 1, "1 of 2 far"))
    cases.append(("mob_on only", arms(mob_on=fled), 1, "the crown mob itself drives it"))
    part = arms()
    part["mob_on"]["tracks"] = dict(("p%d" % i, held[0][:20]) for i in range(3))
    cases.append(("partial read", part, 2, "UNMEASURED"))
    lost = arms()
    lost["mob_off"]["tracks"] = dict(("p%d" % i, held[0][:-1] + [{"x": None, "z": None}]) for i in range(3))
    cases.append(("last sample lost", lost, 2, "mob_off"))
    toward = [tr([(116 - k, 104) for k in range(10)], "Goto") + tr([(106 + 3 * k, 104) for k in range(31)])] * 3
    cases.append(("goto toward then wander away", arms(mob_off=toward, mob_off_scent_off=fled), 1, "NOT named"))
    del short["mob_on_quiet"]
    cases.append(("missing arm", short, 2, "mob_on_quiet"))
    bad = 0
    for name, a, want, needle in cases:
        code, lines = verdict(a)
        text = "\n".join(lines)
        if code != want or needle not in text:
            bad += 1
            print("FAIL %s: exit %d (want %d), %r not in:\n%s" % (name, code, want, needle, text))
    # the real 10-07 shape: ~16 cells out, ended 23-70 off -> far by the FAR floor alone
    if not summarise(tr([(116, 104), (130, 110), (160, 130)], "Flee"), stand)["far"]:
        bad += 1
        print("FAIL 10-07 shape not far")
    if summarise(tr([(116, 104), (118, 104)], "Flee"), stand)["far"]:
        bad += 1
        print("FAIL a 2-cell step read as far")
    print("selftest ok (%d cases)" % (len(cases) + 2) if not bad else "selftest: %d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    sys.exit(live(out))
