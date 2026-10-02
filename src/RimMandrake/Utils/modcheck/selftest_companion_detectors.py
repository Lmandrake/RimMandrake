"""Selftest: the companion-tool detectors (pawn_census / damage_log / incident_queue_peek) on FakeWorld.

Each hazard has a control. The point being proved is that the DIRECT read is what makes the hit:
the same world with the companion switched off must NOT name the cause (or must not see the event).
Run: python3 selftest_companion_detectors.py
"""
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from rimdrive.fake import FakeWorld, pawn_row          # noqa: E402
from watch import Watch, SurpriseAbort                 # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append(bool(cond))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if (detail and not cond) else ""))


def world(tmp):
    w = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103), pawn_row("Col3", x=106)])
    w.shot_dir = tmp
    return w


def run_hazard(tmp, hazard, companion=None, policy="abort", wait=600):
    """Open a Watch, apply `hazard(world)` AFTER the baseline, wait; return (watch, abort-or-None)."""
    w = world(tmp)
    ab = None
    wt = Watch(w, (100, 100), tmp, mod="Q", chain="h", chunk=300, policy=policy, companion=companion)
    with wt:
        hazard(w)
        try:
            wt.wait(None, wait)
        except SurpriseAbort as e:
            ab = e
    return w, wt, ab


def dets(ab):
    return [h.detector for h in ab.hits] if ab else []


def main():
    tmp = tempfile.mkdtemp(prefix="np_comp_")
    try:
        # ---- probe
        w, wt, ab = run_hazard(tmp, lambda w: None)
        check("companion probed present on FakeWorld", wt.companion is True)
        check("control: quiet wait with companion reads -> no abort, no serious hits",
              ab is None and not [h for h in wt.seen_hits if h["severity"] in ("SURPRISE", "FATAL")], str(wt.seen_hits))

        # ---- mental break, direct read
        def berserk(w):
            w.call("jawa/pawn_force_mental_break", pawn="Col2", breakDef="Berserk")
            w.mental["Col2"] = "Berserk"
        w, wt, ab = run_hazard(tmp, berserk)
        mb = [h for h in (ab.hits if ab else []) if h.detector == "mental_break"]
        check("Berserk on a colonist aborts via mental_break (census), FATAL",
              mb and mb[0].severity == "FATAL" and mb[0].evidence.get("via") == "pawn_census", str(dets(ab)))
        w, wt, ab = run_hazard(tmp, berserk, companion=False)
        check("same Berserk WITHOUT the census and no letter -> invisible (proves the direct read is what sees it)",
              ab is None, str(dets(ab)))

        # ---- expected mental state is not a surprise
        def berserk_expected(w):
            w.mental["Col2"] = "Wander_Sad"
        w = world(tmp)
        with Watch(w, (100, 100), tmp, mod="Q", chain="e", chunk=300) as wt:
            wt.expect("mental", {"id": "Col2"})
            berserk_expected(w)
            wt.wait(None, 600)
        check("declared 'mental' expectation suppresses the test's own induced break (Ninefold false surprise)",
              not [h for h in wt.seen_hits if h["detector"] == "mental_break"], str(wt.seen_hits))

        # ---- predator hunting a colonist
        def hunt(w):
            w.pawns["Wolf9"] = pawn_row("Wolf9", kind="Wolf_Timber", faction=None, is_player=False,
                                        intelligence="Animal", x=160, z=160)
            w.call("jawa/ordered_job", pawnId="Wolf9", jobDef="PredatorHunt", targetAId="Col1")
        w, wt, ab = run_hazard(tmp, hunt)
        check("a far wolf HUNTING a colonist aborts via predator_hunting (no proximity needed)",
              "predator_hunting" in dets(ab), str(dets(ab)))
        w, wt, ab = run_hazard(tmp, hunt, companion=False)
        check("same hunt without the census: invisible (wolf is 60 cells away, hostile:false)", ab is None, str(dets(ab)))

        def hunt_hare(w):
            w.pawns["Wolf9"] = pawn_row("Wolf9", kind="Wolf_Timber", faction=None, is_player=False,
                                        intelligence="Animal", x=160, z=160)
            w.pawns["Hare1"] = pawn_row("Hare1", kind="Hare", faction=None, is_player=False,
                                        intelligence="Animal", x=162, z=160)
            w.call("jawa/ordered_job", pawnId="Wolf9", jobDef="PredatorHunt", targetAId="Hare1")
        w, wt, ab = run_hazard(tmp, hunt_hare)
        check("control: a wolf hunting a hare far away is NOT a surprise", ab is None, str(dets(ab)))

        # ---- damage, cause read from the log
        def cut(w):
            w.call("jawa/damage", thingId="Col3", damageDef="Cut", amount=5)
        w, wt, ab = run_hazard(tmp, cut)
        cd = [h for h in (ab.hits if ab else []) if h.detector == "colonist_damaged"]
        check("a Cut on a colonist aborts via colonist_damaged with damageDef read from the log",
              cd and cd[0].evidence["events"][0]["damageDef"] == "Cut" and cd[0].evidence["via"] == "damage_log",
              str(dets(ab)))
        w, wt, ab = run_hazard(tmp, cut, companion=False)
        check("same Cut without damage_log (no hediff recorded by the fake) -> invisible", ab is None, str(dets(ab)))

        # ---- colonist killed: died FATAL, corroborated by the log
        def kill(w):
            w.call("jawa/pawn_force_incapacitate", pawn="Col1", action="kill")
        w, wt, ab = run_hazard(tmp, kill)
        died = [h for h in (ab.hits if ab else []) if h.detector == "colonist_died"]
        check("killing a colonist aborts FATAL colonist_died, damage_log_kill among its sources",
              died and died[0].severity == "FATAL" and "damage_log_kill" in died[0].evidence["sources"], str(dets(ab)))
        check("colonist_died is ONE hit, not one per source", len(died) == 1, str(len(died)))

        # ---- incident queued (seen before it fires)
        def queue_raid(w):
            w.call("jawa/incident_schedule", incidentDef="RaidEnemy", delayTicks=50000)
        w, wt, ab = run_hazard(tmp, queue_raid)
        iq = [h for h in (ab.hits if ab else []) if h.detector == "incident_queued"]
        check("a RaidEnemy queued mid-chain aborts SURPRISE via incident_queued before it fires",
              iq and iq[0].severity == "SURPRISE", str(dets(ab)))

        def queue_benign(w):
            w.call("jawa/incident_schedule", incidentDef="FarmAnimalsWanderIn", delayTicks=50000)
        w, wt, ab = run_hazard(tmp, queue_benign)
        check("a benign queued incident is WARN only (no abort), but recorded",
              ab is None and any(h["detector"] == "incident_queued" for h in wt.seen_hits), str(wt.seen_hits))

        w = world(tmp)
        with Watch(w, (100, 100), tmp, mod="Q", chain="i", chunk=300) as wt:
            w.call("jawa/incident_schedule", incidentDef="RaidEnemy", delayTicks=50000)
            wt.expect("incident", {"defName": "RaidEnemy"})
            wt.wait(None, 600)
        check("a declared 'incident' expectation suppresses the test's own scheduled raid",
              not [h for h in wt.seen_hits if h["detector"] == "incident_queued"], str(wt.seen_hits))

        # ---- census refuses -> source error, inference path still runs, no crash
        w = world(tmp)
        orig = w._t_jawa_pawn_census
        with Watch(w, (100, 100), tmp, mod="Q", chain="r", chunk=300) as wt:
            w._t_jawa_pawn_census = lambda **k: {"success": False, "message": "boom"}
            wt.wait(None, 600)
        w._t_jawa_pawn_census = orig
        check("a census that starts refusing mid-chain is reported evidence_stale (WARN), never a crash",
              any(h["detector"] == "evidence_stale" for h in wt.seen_hits), str(wt.seen_hits))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n = sum(_results)
    print("\n%d/%d passed" % (n, len(_results)))
    return 0 if n == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())
