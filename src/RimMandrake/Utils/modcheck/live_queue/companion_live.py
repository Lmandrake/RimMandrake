"""companion_live: the companion-backed detectors, live. abort_proof proves a hazard ABORTS; this proves the abort is a DIRECT READ.

Offline counterpart: modcheck/selftest_companion_detectors.py (FakeWorld). Each case checks the hit's evidence,
not just its name: `via` names the companion tool, and the read fields carry the game's own values.
  * census consistency: pawn_census and list_pawns agree on the living pawns of the map (same id set);
  * damage: a Cut 3 on a colonist -> colonist_damaged via damage_log with damageDef Cut; the same injury is NOT
    also reported by the inference detector (colonist_injured_unexpectedly) -- one event, one hit;
  * mental: Wander_Sad on a colonist -> mental_break via pawn_census, isAggro False, severity SURPRISE (not FATAL);
  * predator: a wolf ordered to PredatorHunt a colonist -> predator_hunting via pawn_census, preyIsColonist True;
  * incident: a benign FarmAnimalsWanderIn queued -> incident_queued WARN via incident_queue_peek, NO abort;
  * kill: a spawned colonist killed -> colonist_died with damage_log_kill among its sources.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import call, main   # noqa: E402


def run_case(s, job, name, hazard, wait=0):
    import helpers as H
    from watch import Watch, SurpriseAbort
    ax, az, _d = H.safe_anchor(s)
    w = Watch(s, (ax, az), os.path.join(job.outdir, name), mod="LiveQueue", chain=name, policy="abort",
              resurrect=True, chunk=60)
    ab = None
    with w:
        if not w.bland:
            return None, w, "not bland: %s" % w.report.problems
        if not w.companion:
            return None, w, "companion tools absent: direct reads unavailable"
        ctx = {"anchor": (ax, az)}
        try:
            hazard(s, ctx)
            if wait:
                w.wait(None, wait)
            else:
                w.check()
        except SurpriseAbort as e:
            ab = e
    return ab, w, None


def hits_of(ab, det):
    return [h for h in (ab.hits if ab else []) if h.detector == det]


def colonist(s, last=False):
    import helpers as H
    cols = [r for r in H.read_pawns(s, health=False) if H.is_colonist(r) and not r["dead"]]
    return cols[-1] if last else cols[0]


def body(s, job):
    import helpers as H
    cen = call(s, "jawa/pawn_census")
    lp = H.read_pawns(s, health=False)
    a = {p["id"] for p in cen.get("pawns") or [] if not p.get("dead")}
    b = {p["id"] for p in lp if not p["dead"]}
    job.check("census consistency: pawn_census and list_pawns name the same living pawns", cen.get("success") and a == b,
              {"census_only": sorted(a - b)[:10], "list_only": sorted(b - a)[:10]})

    def cut(s, ctx):
        c = colonist(s)
        r = call(s, "jawa/damage", thingId=c["id"], damageDef="Cut", amount=3, allowColonists=True)
        if not r.get("success"):
            raise RuntimeError("jawa/damage refused: %s" % r.get("message"))
    ab, w, why = run_case(s, job, "damage_cut", cut)
    cd = hits_of(ab, "colonist_damaged")
    ok = bool(cd) and cd[0].evidence.get("via") == "damage_log" and \
        any(e.get("damageDef") == "Cut" for e in cd[0].evidence.get("events", []))
    job.check("damage: colonist_damaged via damage_log names damageDef Cut", ok, why or [h.detector for h in (ab.hits if ab else [])])
    dup = [h for h in hits_of(ab, "colonist_injured_unexpectedly") if "Cut" in h.summary]
    job.check("damage: the Cut is not ALSO reported by the hediff-inference detector", ok and not dup, [h.summary for h in dup])

    def sad(s, ctx):
        c = colonist(s, last=True)
        r = call(s, "jawa/pawn_force_mental_break", pawn=c["id"], breakDef="Wander_Sad", reason="live queue companion_live")
        if not r.get("success"):
            raise RuntimeError("Wander_Sad refused: %s" % r)
    ab, w, why = run_case(s, job, "mental_wander_sad", sad)
    mb = hits_of(ab, "mental_break")
    job.check("mental: Wander_Sad -> mental_break via pawn_census, isAggro False, SURPRISE not FATAL",
              bool(mb) and mb[0].evidence.get("via") == "pawn_census" and mb[0].evidence.get("isAggro") is False
              and mb[0].severity == "SURPRISE", why or [(h.detector, h.severity, h.evidence) for h in (ab.hits if ab else [])][:3])

    def hunt(s, ctx):
        c = colonist(s)
        r = call(s, "jawa/spawn_pawn", kindDef="Wolf_Timber", x=max(5, c["x"] - 15), z=c["z"], faction="none", count=1)
        wid = (r.get("pawns") or [{}])[0].get("id")
        j = call(s, "jawa/ordered_job", pawnId=wid, jobDef="PredatorHunt", targetAId=c["id"])
        if not j.get("success"):
            raise RuntimeError("PredatorHunt not running: %s" % (j.get("message") or j))
    ab, w, why = run_case(s, job, "predator_census", hunt)
    ph = hits_of(ab, "predator_hunting")
    job.check("predator: predator_hunting via pawn_census with preyIsColonist True",
              bool(ph) and ph[0].evidence.get("via") == "pawn_census" and ph[0].evidence.get("preyIsColonist") is True,
              why or [h.detector for h in (ab.hits if ab else [])])

    def benign(s, ctx):
        r = call(s, "jawa/incident_schedule", incidentDef="FarmAnimalsWanderIn", delayTicks=40000)
        if not r.get("success"):
            raise RuntimeError("incident_schedule refused: %s" % r.get("message"))
    ab, w, why = run_case(s, job, "incident_benign", benign, wait=60)
    iq = [h for h in w.seen_hits if h["detector"] == "incident_queued"]
    job.check("incident: benign queue entry seen as incident_queued WARN, and it does NOT abort",
              ab is None and iq and iq[0]["severity"] == "WARN", why or {"aborted": ab is not None, "seen": iq[:2]})

    def kill(s, ctx):
        ax, az = ctx["anchor"]
        r = call(s, "jawa/spawn_pawn", kindDef="Colonist", x=ax, z=az, faction="player", count=1)
        pid = (r.get("pawns") or [{}])[0].get("id")
        k = call(s, "jawa/pawn_force_incapacitate", pawn=pid, action="kill")
        if not k.get("success"):
            raise RuntimeError("kill refused: %s" % k.get("message"))
    ab, w, why = run_case(s, job, "kill_corroborated", kill)
    died = hits_of(ab, "colonist_died")
    job.check("kill: colonist_died carries damage_log_kill among its sources",
              bool(died) and "damage_log_kill" in died[0].evidence.get("sources", []),
              why or [(h.detector, h.evidence.get("sources")) for h in died])


if __name__ == "__main__":
    sys.exit(main("companion_live", body))
