#!/usr/bin/env python3
"""Selftest for map awareness phase 1 (VISITOR_DETECTORS_MEND_NAME_THE_STRANGER).

Each check is the GPT review (Transient/foundry_map_awareness_review_gpt_20261010.md) section 7 phase-1
acceptance row it proves, run offline on rimdrive.fake.FakeWorld. Every check FAILS against the code
before this item (written first, run red, then the code). The owner's rule (question card 2026-10-10): an
unexpected visitor is RECORDED and REMOVED and the run carries on; only EVIDENCE that it disrupted the
criterion makes the run DISRUPTED; an observation that failed makes it INDETERMINATE.

Run: python3 src/RimMandrake/Utils/modcheck/selftest_awareness.py
"""
import json
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import detectors as D                                   # noqa: E402
import snapshot as S                                    # noqa: E402
import helpers as H                                     # noqa: E402
import contract as C                                    # noqa: E402
import scene_report as R                                # noqa: E402
from rimdrive.fake import FakeWorld, pawn_row           # noqa: E402
from suite import TestContext                           # noqa: E402
from watch import Watch, SurpriseAbort                  # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append(bool(cond))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + str(detail)) if (detail and not cond) else ""))


def world(tmp=None):
    w = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103), pawn_row("Col3", x=106)])
    w.shot_dir = tmp
    return w


def snap(w):
    return S.take_snapshot(w, "full", companion=True)


def det(hits, name):
    return [h for h in hits if h.detector == name]


def main():
    tmp = tempfile.mkdtemp(prefix="np_aware_")
    try:
        # ---- 1. stranger near anchor names exact id / kind / faction / state (count-only output fails)
        w = world()
        base = S.Baseline(snap(w))
        w.pawns["Trader7"] = pawn_row("Trader7", kind="Caravan_Trader", faction="OutlanderCivil", is_player=False,
                                      x=110, z=100)
        w.pawns["Trader7"]["downed"] = True
        hits = D.sweep(snap(w), base, anchor=(100, 100))
        st = det(hits, "strangers_near_anchor")
        check("strangers_near_anchor fires", len(st) == 1, [h.detector for h in hits])
        s = st[0].summary if st else ""
        check("its text names the pawn id, kind, faction and state",
              all(t in s for t in ("Trader7", "Caravan_Trader", "OutlanderCivil", "downed")), s)

        # ---- 2. an unexpected pawn that JOINS THE PLAYER FACTION is detected (non-player-only filtering fails)
        w = world()
        base = S.Baseline(snap(w))
        w.pawns["Whistler"] = pawn_row("Whistler", x=180, z=180)            # a wanderer joiner, player faction
        hits = D.sweep(snap(w), base, anchor=(100, 100))
        pj = det(hits, "player_joiner")
        check("player-faction joiner detected", len(pj) == 1 and "Whistler" in pj[0].summary, [h.summary for h in hits])
        check("player joiner is a visitor-class surprise", pj and pj[0].severity == D.SURPRISE)

        # ---- 3. the SAME pawn recruited / tamed is a state change, never an arrival
        w = world()
        w.pawns["Pris1"] = pawn_row("Pris1", kind="Villager", faction="OutlanderCivil", is_player=False, x=150, z=150)
        base = S.Baseline(snap(w))
        w.pawns["Pris1"].update({"faction": "PlayerColony", "factionName": "PlayerColony", "isPlayer": True})
        hits = D.sweep(snap(w), base, anchor=(100, 100))
        check("recruit reads as pawn_state_changed", len(det(hits, "pawn_state_changed")) == 1, [h.detector for h in hits])
        check("recruit is NOT a player_joiner / pawn_arrived / roster arrival",
              not det(hits, "player_joiner") and not det(hits, "pawn_arrived")
              and not [h for h in det(hits, "pawn_roster_transition") if h.evidence.get("direction") == "arrived"],
              [h.summary for h in hits])

        # ---- 4. an OLD-ID pawn arriving after the baseline is caught by set diff (an id watermark misses it)
        w = world()
        base = S.Baseline(snap(w))
        w.pawns["Human5"] = pawn_row("Human5", kind="WorldPawn_Redressed", faction=None, is_player=False,
                                     intelligence="Animal", x=240, z=240)
        hits = D.sweep(snap(w), base, anchor=(100, 100))
        arr = det(hits, "pawn_arrived")
        check("old-id arrival far from everyone is reported by set diff", len(arr) == 1 and "Human5" in arr[0].summary,
              [h.summary for h in hits])

        # ---- 5. bounded expectations: expected condition accepted, a second condition of the same mod rejected
        w = world()
        w.conditions = []
        base = S.Baseline(snap(w))
        w.conditions = [{"def": "RM_ForgePulse", "scope": "map", "affectsThisMap": True, "permanent": False},
                        {"def": "RM_ForgeAshfall", "scope": "map", "affectsThisMap": True, "permanent": False}]
        exps = D.Expectations()
        exps.expect("condition", {"def": "RM_ForgePulse"}, max_count=1)
        hits = D.sweep(snap(w), base, exps, anchor=(100, 100))
        cu = det(hits, "condition_unexpected")
        check("declared condition accepted, undeclared sibling from the same mod rejected",
              [h.evidence["def"] for h in cu] == ["RM_ForgeAshfall"], [h.summary for h in cu])
        # letters: one expected, the same letter arriving twice exceeds the bound
        w = world()
        base = S.Baseline(snap(w))
        w.letters += [{"defName": "NeutralEvent", "label": "Slicked", "arrivalTick": 10},
                      {"defName": "NeutralEvent", "label": "Slicked", "arrivalTick": 20}]
        exps = D.Expectations()
        exps.expect("letter", {"label_contains": "Slicked"}, max_count=1)
        hits = D.sweep(snap(w), base, exps, anchor=(100, 100))
        lu = det(hits, "letter_unexpected")
        check("a bounded letter expectation admits one and reports the extra",
              len(lu) == 1 and lu[0].evidence["arrivalTick"] == 20, [h.summary for h in lu])
        # unbounded expectation keeps the old behaviour (both admitted)
        exps = D.Expectations()
        exps.expect("letter", {"label_contains": "Slicked"})
        hits = D.sweep(snap(w), base, exps, anchor=(100, 100))
        check("an unbounded expectation still admits every match", not det(hits, "letter_unexpected"))

        # ---- 6. owner rule: a harmless visitor is RECORDED and REMOVED, and the wait carries on -> CLEAN
        w = world(tmp)

        def visitor(world_):
            world_.pawns["Megaspider9"] = pawn_row("Megaspider9", kind="Megaspider", faction="Insect", is_player=False,
                                                   hostile=True, intelligence="Animal", x=200, z=200)
        w.at(700, visitor)
        with Watch(w, (100, 100), tmp, mod="M", chain="visitor", chunk=600) as wt:
            r = wt.wait(None, 2400)
        check("a harmless visitor does not abort the wait", r["advanced"] == 2400, r)
        check("the visitor was removed from the map", "Megaspider9" not in w.pawns)
        sm = wt.summary()
        rv = sm.get("runValidity") or {}
        check("run validity CLEAN with the visitor recorded", rv.get("verdict") == C.CLEAN, rv)
        vis = [v for v in rv.get("visitors", []) if v.get("id") == "Megaspider9"]
        check("visitor record names id/kind/faction and says removed",
              vis and vis[0].get("kind") == "Megaspider" and vis[0].get("faction") == "Insect" and vis[0].get("removed"),
              rv.get("visitors"))
        check("evidence was captured BEFORE removal (one capture)", len(wt.captures) == 1, len(wt.captures))

        # ---- 6b. a visitor that ATTACKS a colonist is evidence of disruption -> DISRUPTED, abort (redo owed)
        w = world(tmp)

        def attacker(world_):
            world_.pawns["Raider9"] = pawn_row("Raider9", kind="Tribal_Berserker", faction="TribeRough",
                                               is_player=False, hostile=True, x=104, z=100)
            world_.record_damage("Col1", damage_def="Cut", amount=5.0, instigator="Raider9")
        w.at(700, attacker)
        err = None
        with Watch(w, (100, 100), tmp, mod="M", chain="attacker", chunk=600) as wt:
            try:
                wt.wait(None, 2400)
            except SurpriseAbort as e:
                err = e
        check("a visitor that damaged a colonist aborts the run", err is not None)
        rv = wt.summary().get("runValidity") or {}
        check("validity DISRUPTED, naming the evidence", rv.get("verdict") == C.DISRUPTED
              and any(d.get("visitor") == "Raider9" for d in rv.get("disruptions", [])), rv)
        check("evidence before action: the attacker was NOT removed", "Raider9" in w.pawns)

        # ---- 6c. a visitor targeting a test fixture (census enemy target) is disruption too
        w = world(tmp)
        with Watch(w, (100, 100), tmp, mod="M", chain="target", chunk=600) as wt:
            ctx = TestContext(w, anchor=(100, 100), watch=wt)
            subj = ctx.spawn_pawn("Muffalo")

            def hunter(world_):
                world_.pawns["Warg3"] = pawn_row("Warg3", kind="Warg", faction=None, is_player=False,
                                                 intelligence="Animal", x=101, z=101)
                world_.jobs["Warg3"] = {"def": "PredatorHunt", "targetA": subj}
            w.at(w.ticks + 300, hunter)
            err = None
            try:
                wt.wait(None, 1200)
            except SurpriseAbort as e:
                err = e
        rv = wt.summary().get("runValidity") or {}
        check("a predator hunting the test subject makes the run DISRUPTED",
              err is not None and rv.get("verdict") == C.DISRUPTED, rv)

        # ---- 6d. an observation that failed makes the run INDETERMINATE, never CLEAN
        w = world(tmp)
        w.at(700, lambda world_: setattr(world_, "list_truncate_at", 1))
        with Watch(w, (100, 100), tmp, mod="M", chain="trunc", chunk=600) as wt:
            try:
                wt.wait(None, 1800)
            except SurpriseAbort:
                pass
        rv = wt.summary().get("runValidity") or {}
        check("a truncated pawn listing makes the run INDETERMINATE", rv.get("verdict") == C.INDETERMINATE, rv)

        # ---- 6e. a quiet run is CLEAN with no visitors
        w = world(tmp)
        with Watch(w, (100, 100), tmp, mod="M", chain="quiet", chunk=600) as wt:
            wt.wait(None, 1200)
        rv = wt.summary().get("runValidity") or {}
        check("a quiet run is CLEAN with no visitors", rv.get("verdict") == C.CLEAN and not rv.get("visitors"), rv)
        check("the Watch wrote a baseline scene report before the timed stage",
              wt.baseline_scene and os.path.exists(wt.baseline_scene), wt.baseline_scene)

        # ---- 7. action receipts: a SUBSTITUTED spawn exposes requested vs actual (repeating the request fails)
        w = world(tmp)
        w.modes.add("spawn_substitutes")
        ctx = TestContext(w, anchor=(100, 100))
        pid = ctx.spawn_pawn("Jawa_Scavenger")
        rc = ctx.receipts[-1] if getattr(ctx, "receipts", None) else {}
        check("receipt records requested and actual kinds", rc.get("requestedKind") == "Jawa_Scavenger"
              and rc.get("toolKinds") == ["Colonist"], rc)
        check("receipt read-back kind comes from an independent map read", rc.get("readBackKinds") == ["Colonist"], rc)
        check("receipt flags the mismatch", rc.get("mismatch") is True and pid in rc.get("returnedIds", []), rc)
        w.modes.discard("spawn_substitutes")
        ctx.spawn_pawn("Muffalo")
        check("an honest spawn is not a mismatch", ctx.receipts[-1].get("mismatch") is False, ctx.receipts[-1])

        # ---- 8. scene report: hostility decomposed, involvement and expectation independent, coverage declared
        w = world(tmp)
        ctx = TestContext(w, anchor=(100, 100))
        ours = ctx.spawn_pawn("Muffalo")
        w.pawns["Wolf1"] = pawn_row("Wolf1", kind="Wolf_Timber", faction=None, is_player=False,
                                    intelligence="Animal", x=120, z=100)
        w.mental["Wolf1"] = "Manhunter"
        rep = R.collect(w, anchor=(100, 100), receipts=ctx.receipts)
        rows = {p["id"]: p for p in rep["pawns"]}
        check("report has a schema version, a report id and a non-atomic acquisition label",
              rep.get("schemaVersion") and rep.get("reportId") and rep["acquisition"]["atomic"] is False, rep.keys())
        wolf = rows.get("Wolf1", {})
        th = wolf.get("threat", {})
        check("factionless manhunter: no faction relation, aggression from mental state",
              th.get("factionRelationToPlayer") == "no-faction" and th.get("mentalState") == "Manhunter"
              and th.get("aggressionReason") == "mental:Manhunter", th)
        check("our spawn: ourInvolvement confirmedDirectSpawn", rows.get(ours, {}).get("ourInvolvement") == "confirmedDirectSpawn",
              rows.get(ours))
        check("an unknown pawn: ourInvolvement unknown, expectation unresolved (no contract given)",
              wolf.get("ourInvolvement") == "unknown" and wolf.get("expectation") == "unresolved", wolf)
        cov = rep["scope"]["coverage"]
        check("coverage declares held pawns NOT covered and dormant as not distinguished",
              cov.get("held", "").startswith("not covered") and "dormant" in cov, cov)
        check("letter association says unavailable rather than guessing",
              wolf.get("evidence", {}).get("letters") == "unavailable", wolf.get("evidence"))
        exps = D.Expectations()
        exps.expect("pawn", {"id": "Wolf1"})
        rep2 = R.collect(w, anchor=(100, 100), receipts=ctx.receipts, expectations=exps, baseline=rep)
        rows2 = {p["id"]: p for p in rep2["pawns"]}
        check("an expected-but-not-ours pawn: unknown + expected (independent fields)",
              rows2["Wolf1"]["ourInvolvement"] == "unknown" and rows2["Wolf1"]["expectation"] == "expected", rows2["Wolf1"])
        check("a diff against the baseline report lists nothing added", rep2["diff"]["added"] == [], rep2["diff"])
        text = R.render_text(rep2)
        check("the text footer says origin unknown, never caused-by",
              "origin unknown" in text and "caused by" not in text.lower(), text[-300:])
        # empty map / failed reads
        e = FakeWorld(pawns=[])
        rep3 = R.collect(e)
        check("empty map: a valid empty report, not a crash", rep3["pawns"] == [] and rep3["acquisition"]["failed"] == [], rep3)
        e.list_truncate_at = 0
        e.pawns["X1"] = pawn_row("X1")
        rep4 = R.collect(e)
        check("a truncated pawn read is declared incomplete", rep4["scope"]["complete"] is False, rep4["scope"])

        # ---- 9. quiet-world profile with read-back of what was actually suppressed; quests never ended
        w = world(tmp)
        w.debug["logRaidInfo"] = False
        with H.SettingsTransaction(w) as tx:
            q = H.quiet_world(w, tx)
            rb = q.evidence.get("readBack", {})
            check("quiet world reads back storyteller off and logRaidInfo on",
                  rb.get("enableStoryteller") is False and rb.get("logRaidInfo") is True, rb)
            check("wild-spawner block reports unavailable when the tool is absent (never assumed)",
                  str(q.evidence.get("wildSpawner", "")).startswith("unavailable"), q.evidence)
            check("quests are left alone by default", q.evidence.get("quests") == "not touched", q.evidence)
        check("settings restored after the profile", w.debug["logRaidInfo"] is False and w.debug["enableStoryteller"] is True,
              w.debug)
        w2 = world(tmp)
        w2.wild_blocked = False
        w2._t_jawa_wild_spawner_block = lambda action="get", **_: (
            setattr(w2, "wild_blocked", action == "block") if action in ("block", "release") else None) or {
            "success": True, "blocked": w2.wild_blocked, "skippedTicks": 0}
        with H.SettingsTransaction(w2) as tx:
            q = H.quiet_world(w2, tx)
            check("wild-spawner block read back when the tool exists", q.evidence.get("wildSpawner") == "blocked (read back)",
                  q.evidence)
        check("the wild-spawner block is released on exit", w2.wild_blocked is False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n, bad = len(_results), _results.count(False)
    print("\n%d/%d passed" % (n - bad, n))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
