"""abort_proof ABORT-PATH PROOF: deliberate hazards must trip their detector and abort with evidence; controls must not.

No real hazard occurred in the 2026-10-01 live pass, so the abort path has never fired live. Each hazard case
opens its own Watch (bland prep, baseline), applies ONE hazard after the baseline, then sweeps (check() or a
short wait). PASS for a hazard case requires ALL of: a SurpriseAbort of kind 'surprise'; the expected
detector among its hits; a sidecar json on disk; the game left paused. Control cases must end with no abort
and no SURPRISE/FATAL hit. The runner path is proved once end to end: a Suite chain whose component meets a
hostile must record that component UNMEASURED naming the detector, never PASS or FAIL.

Hazards are applied far from the starting colonists where the hazard itself allows it, and the next case's
bland prep (kill hostiles/wildlife, extinguish, calm, resurrect) cleans up after the last.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import call, main   # noqa: E402


def colonists(s):
    import helpers as H
    return [r for r in H.read_pawns(s, health=False) if H.is_colonist(r) and not r["dead"] and r.get("spawned", True)]


def spawned_id(r):
    rows = r.get("pawns") or r.get("spawned") or []
    if rows and isinstance(rows[0], dict):
        return rows[0].get("id") or rows[0].get("thingId")
    return r.get("id")


def _clamp(v, n):
    return max(5, min(n - 5, v))


def case(s, job, name, hazard, expect_detector, wait=0, control=False, declare=None):
    """Run one case; returns True if it met its criterion. `hazard(s, ctx)` runs after the baseline."""
    import clockgate
    import helpers as H
    from watch import Watch, SurpriseAbort
    ax, az, _d = H.safe_anchor(s)
    outdir = os.path.join(job.outdir, name)
    ab, w = None, None
    ctx = {"anchor": (ax, az), "size": int(call(s, "jawa/map_info").get("sizeX", 250))}
    w = Watch(s, (ax, az), outdir, mod="LiveQueue", chain=name, policy="abort", resurrect=True, chunk=60)
    with w:
        if not w.bland:
            job.check("%s: bland map established before the hazard" % name, False, w.report.problems)
            return False
        if declare:
            declare(w, ctx)
        try:
            hazard(s, ctx)
            if declare:
                declare(w, ctx, after=True)
            if wait:
                w.wait(None, wait)
            else:
                w.check()
        except SurpriseAbort as e:
            ab = e
    paused = True
    try:
        paused = clockgate.verify_pause(s)
    except Exception:                                           # noqa: BLE001
        paused = False
    hits = [h.detector for h in ab.hits] if ab else []
    serious_seen = [h for h in w.seen_hits if h["severity"] in ("SURPRISE", "FATAL")]
    rec = {"aborted": ab is not None, "kind": ab.kind if ab else None, "hits": hits,
           "evidence": ab.summary()["evidence"] if ab else [], "screenshots": ab.summary()["screenshots"] if ab else [],
           "serious_seen": serious_seen[:10], "companion": w.companion}
    job.note(name, rec)
    if control:
        return job.check("control %s: no abort and no SURPRISE/FATAL hit" % name,
                         ab is None and not serious_seen, rec)
    from surprise import to_local_path
    ev = [p for p in rec["evidence"] if p and os.path.isfile(to_local_path(p))]
    ok = (ab is not None and ab.kind == "surprise" and expect_detector in hits and ev and paused)
    return job.check("hazard %s: aborts via %s with sidecar on disk, game paused" % (name, expect_detector), ok, rec)


# ------------------------------------------------------------------ hazards
def hz_hostile(s, ctx):
    ax, az = ctx["anchor"]
    ids = []
    for i in range(3):
        r = call(s, "jawa/spawn_pawn", kindDef="Tribal_Warrior", x=ax + i, z=az, faction="hostile", count=1)
        if not r.get("success"):
            raise RuntimeError("spawn_pawn hostile refused: %s" % r.get("message"))
        ids.append(spawned_id(r))
    ctx["spawned"] = ids


def hz_fire(s, ctx):
    c = colonists(s)[0]
    n = ctx["size"]
    x, z = _clamp(c["x"] + 4, n), _clamp(c["z"], n)
    r = call(s, "jawa/map_fire", action="start", rect="%d,%d,3,1" % (x, z), fireSize=0.5)
    if not r.get("success") or not r.get("firesStarted"):
        # MEASURED 2026-10-01: map_fire is gated by flammability/wetness (0 of 3 cells on a bare desert tile).
        # Fall back to placing Fire things directly.
        sb = call(s, "jawa/spawn_batch", ops=";".join("Fire:%d,%d" % (x + i, z) for i in range(3)))
        if not sb.get("success"):
            raise RuntimeError("map_fire started nothing and spawn_batch Fire failed: %s / %s" % (r, sb))


def hz_kill_colonist(s, ctx):
    # the sacrificial colonist is spawned AFTER the baseline (so it was never a starting colonist) and killed
    ax, az = ctx["anchor"]
    r = call(s, "jawa/spawn_pawn", kindDef="Colonist", x=ax, z=az, faction="player", count=1)
    pid = spawned_id(r)
    if not r.get("success") or not pid:
        raise RuntimeError("spawn_pawn player colonist refused: %s" % r.get("message"))
    ctx["spawned"] = [pid]
    k = call(s, "jawa/pawn_force_incapacitate", pawn=pid, action="kill")
    if not k.get("success"):
        raise RuntimeError("kill refused: %s" % k.get("message"))


def hz_predator(s, ctx):
    c = colonists(s)[0]
    n = ctx["size"]
    r = call(s, "jawa/spawn_pawn", kindDef="Wolf_Timber", x=_clamp(c["x"] + 15, n), z=_clamp(c["z"], n),
             faction="none", count=1)
    wid = spawned_id(r)
    if not r.get("success") or not wid:
        raise RuntimeError("spawn wolf refused: %s" % r.get("message"))
    ctx["spawned"] = [wid]
    j = call(s, "jawa/ordered_job", pawnId=wid, jobDef="PredatorHunt", targetAId=c["id"])
    if not j.get("success"):
        raise RuntimeError("ordered_job PredatorHunt not running: %s" % (j.get("message") or j))


def hz_berserk(s, ctx):
    c = colonists(s)[-1]
    r = call(s, "jawa/pawn_force_mental_break", pawn=c["id"], breakDef="Berserk", reason="live queue abort_proof")
    if not r.get("success") or r.get("started") is False:
        raise RuntimeError("Berserk did not start: %s" % r)


def hz_queue_raid(s, ctx):
    r = call(s, "jawa/incident_schedule", incidentDef="RaidEnemy", delayTicks=30000)
    if not r.get("success"):
        raise RuntimeError("incident_schedule refused: %s" % r.get("message"))


def control_declared(w, ctx, after=False):
    """The negative control's declarations: what the TEST causes is not a surprise."""
    if not after:
        w.expect("incident", {"defName": "FarmAnimalsWanderIn"})
        return
    for pid in ctx.get("spawned", []):
        w.expect("hostile", {"id": pid})


def hz_declared(s, ctx):
    # a far hostile the test declares, and a benign incident it schedules itself
    n = ctx["size"]
    r = call(s, "jawa/spawn_pawn", kindDef="Tribal_Warrior", x=n - 8, z=n - 8, faction="hostile", count=1)
    ctx["spawned"] = [spawned_id(r)]
    call(s, "jawa/incident_schedule", incidentDef="FarmAnimalsWanderIn", delayTicks=30000)


def runner_path(s, job):
    """End to end through runner.run_suite: the component that meets the hazard is UNMEASURED, naming it."""
    import runner
    from suite import Suite
    su = Suite("LiveQueueAbort")

    @su.chain("hostile_inside_component")
    def _c(t):
        with t.component("meets_a_hostile"):
            ax, az = t.anchor
            call(s, "jawa/spawn_pawn", kindDef="Tribal_Warrior", x=ax + 2, z=az, faction="hostile", count=1)
            t.wait_ticks(120)
    summ = runner.run_suite(su, s, situational=True, policy="abort")
    comp = summ["chains"][0]["components"][0] if summ["chains"] and summ["chains"][0]["components"] else {}
    named = "hostile_pawns" in str(comp.get("surprises")) or "hostile_pawns" in str(comp.get("detail"))
    job.note("runner_path", {"verdict": comp.get("verdict"), "detail": str(comp.get("detail"))[:300]})
    job.check("runner path: the component meeting a hostile is UNMEASURED naming hostile_pawns",
              comp.get("verdict") == "UNMEASURED" and named, comp)


def body(s, job):
    case(s, job, "control_quiet", lambda s, c: None, None, wait=1200, control=True)
    case(s, job, "hostile_raid", hz_hostile, "hostile_pawns")
    case(s, job, "fire_near_colonist", hz_fire, "fire_on_map", wait=60)
    case(s, job, "colonist_killed", hz_kill_colonist, "colonist_died")
    case(s, job, "predator_hunts_colonist", hz_predator, "predator_hunting")
    case(s, job, "colonist_berserk", hz_berserk, "mental_break")
    case(s, job, "raid_queued", hz_queue_raid, "incident_queued")
    case(s, job, "control_declared", hz_declared, None, wait=60, control=True, declare=control_declared)
    runner_path(s, job)
    case(s, job, "control_after_cleanup", lambda s, c: None, None, wait=600, control=True)
    import bland_world
    rep = bland_world.reset(s)
    job.note("final_reset", rep)
    job.check("after all hazards, bland_world.reset() leaves a PROVABLY bland world (corpses, hediffs, queue, fires)",
              rep["bland"], rep["problems"])


if __name__ == "__main__":
    sys.exit(main("abort_proof", body))
