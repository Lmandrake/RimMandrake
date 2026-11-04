#!/usr/bin/env python3
"""selftest_delivery_metrics.py - delivery_metrics.py on a planted Relentless store, then the committed audit record.

Item CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY. Part 1 plants a store whose every metric has a known answer and checks
each one; an empty store must print UNMEASURED for every store-fed metric, never 0. Part 2 reads the committed
infrastructure/state/close_audits.jsonl: its first sample holds a targeted narrow_weak stratum beside a random one, and
every drawn row is audited by a named auditor with a method and evidence.

    python3 src/RimMandrake/rimflow/selftest_delivery_metrics.py
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import delivery_metrics as dm                     # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def plant(root):
    s = os.path.join(root, "store")
    os.makedirs(os.path.join(s, "items"))
    T = "2026-11-0%dT0%d:00:00Z"
    enrol = [("A", 1), ("B", 1), ("C", 2), ("D", 2), ("E", 2), ("F", 3), ("G", 3), ("H", 3)]
    j = [{"at": T % (d, 1), "do": "enrol", "item": i} for i, d in enrol]
    j.append({"at": T % (3, 2), "do": "tick", "acts": [{"do": "checker_lost", "item": "C"}, {"do": "game_implemented"},
                                                       {"do": "game_unmeasured"}, {"do": "game_fail"}]})
    with open(os.path.join(s, "journal.jsonl"), "w") as f:
        f.write("\n".join(json.dumps(x) for x in j) + "\nnot json\n")
    done = dm.ep("2026-11-03T05:00:00Z")
    states = {
        "A": {"status": "done", "done_at": done, "check": {"verdict": "PASS", "reasons": "ran it"}, "last_sha": "a" * 40,
              "contract": {"proof": "python3 a.py"}},
        "B": {"status": "done", "done_at": done, "check": {"verdict": "WEAK", "reasons": "GAP:OTHER. mutant elsewhere"},
              "last_sha": "b" * 40, "contract": {"proof": "python3 b.py"}},
        "C": {"status": "closing", "done_at": done, "check": {"verdict": "WEAK", "reasons": "GAP:DIFF. own hunk"}},
        "D": {"status": "closing", "done_at": done, "check": {"verdict": "WEAK", "reasons": "no tag"}},
        "E": {"status": "blocked"}, "F": {"status": "retired"}, "G": {"status": "queued"}, "H": {"status": "held"},
    }
    att = {
        "A": [{"at": T % (1, 2), "gen": 1, "start": 1, "approach": "build"}, {"at": T % (1, 3), "gen": 1, "end": "blind_fail"},
              {"at": T % (1, 4), "gen": 3, "start": 1, "approach": "build"}, {"at": T % (1, 5), "gen": 3, "end": "finish"}],
        "B": [{"at": T % (1, 2), "gen": 1, "start": 1, "approach": "build"},
              {"at": T % (1, 3), "gen": 1, "end": "proof_found_defect"},
              {"at": T % (1, 4), "gen": 3, "start": 1, "approach": "build"}],
        "C": [{"at": T % (2, 2), "gen": 1, "end": "checker_lost", "detail": "lost at 0123abcd /tmp/x.log 3 tries"},
              {"at": T % (2, 3), "gen": 1, "end": "checker_lost", "detail": "lost at 9f8e7d6c /tmp/y.log 5 tries"},
              {"at": T % (2, 4), "gen": 1, "end": "worker_lost"}],
        "E": [{"at": T % (2, 2), "gen": 1, "end": "blocked_by_predecessor", "on": "A"},
              {"at": T % (3, 6), "gen": 1, "start": 1, "approach": "build"}],
        "H": [{"at": T % (3, 1), "gen": 1, "end": "proof_weak", "detail": "GAP:DIFF"}],
    }
    for i, st in states.items():
        os.makedirs(os.path.join(s, "items", i))
        with open(os.path.join(s, "items", i, "state.json"), "w") as f:
            json.dump(dict(st, item=i), f)
        with open(os.path.join(s, "items", i, "attempts.jsonl"), "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in att.get(i, [])))
    u = lambda kind, i, g, c=None: "rm-relentless-%s-%s-g%d%s" % (kind, dm.short(i), g, "-c%d" % c if c else "")
    runs = {u("work", "A", 1): 100, u("check", "A", 1, 1): 10, u("work", "A", 3): 300, u("work", "B", 1): 50,
            u("work", "B", 3): 70, u("work", "E", 1): 5, u("work", "F", 1): 7, u("work", "G", 1): 11, "stray-unit": 1000}
    with open(os.path.join(s, "spend-20261103.json"), "w") as f:
        json.dump({"spent": sum(runs.values()), "runs": runs, "basis": {u("check", "A", 1, 1): "estimated"}}, f)
    with open(os.path.join(s, "items", "C", "attempts.jsonl"), "a") as f:
        f.write("{torn line\n")
    for i, body in (("J", "{not json"), ("K", json.dumps({"status": "held", "item": "K"}))):   # unreadable; no attempts file
        os.makedirs(os.path.join(s, "items", i))
        with open(os.path.join(s, "items", i, "state.json"), "w") as f:
            f.write(body)
    with open(os.path.join(s, "shadow.jsonl"), "w") as f:
        for w in ("PASS", "WEAK", "FAIL", "UNMEASURED"):
            f.write(json.dumps({"word": w, "shadow": w, "item": "A", "at": done}) + "\n")
    return s


def part1():
    root = tempfile.mkdtemp(prefix="dm_selftest_")
    try:
        s = plant(root)
        snap = dm.load(s)
        now = dm.ep("2026-11-04T05:00:00Z")
        m = dm.compute(snap, [], None, now)
        y = m["accepted_delivery_yield"]["cohorts"]
        check(y["2026-11-01"]["intake"] == 2 and y["2026-11-01"]["accepted"] == 2, "cohort 11-01: 2 in, 2 accepted")
        c2 = y["2026-11-02"]
        check((c2["accepted"], c2["waiting"]) == (2, 1) and c2["yield"]["rate"] == round(2 / 3, 3),
              "cohort 11-02: closing counts as accepted, blocked is shown waiting, yield 2/3")
        c3 = y["2026-11-03"]
        check((c3["dropped"], c3["unresolved"], c3["waiting"]) == (1, 1, 1) and c3["yield"]["n"] == 2,
              "cohort 11-03: a retired item leaves the denominator; queued unresolved, held waiting")
        c = m["end_to_end_cost"]
        check(c["accepted_spend"] == 530 and c["per_accepted_item_own"] == round(530 / 4)
              and c["per_accepted_item_all_in"] == round(1553 / 4),
              "cost: an accepted item's own spend, and all spend (unfinished, dropped, unmapped) per accepted item")
        check(c["unfinished_spend"] == 16 and c["dropped_spend"] == 7 and c["unmapped_spend"] == 1000,
              "cost: unfinished and dropped spend kept apart; an unmapped unit is shown, not dropped")
        check(c["by_role"]["check"] == 10 and c["estimated_part"] == 10, "cost: checker spend by role, estimated part shown")
        check(c["unpriced_generations"] == 0, "every planted started generation is priced")
        cz = dm.m_cost({"store": s, "spend": {}, "basis": {}, "states": {"Z": {"status": "done"}},
                        "attempts": {"Z": [{"start": 1, "gen": 1}]}})
        check((cz["unpriced_generations"], cz["accepted_items_with_unpriced_generations"]) == (1, 1),
              "an accepted item whose started generation has no spend record is counted unpriced, not free")
        r = m["rebuild_waste_before_attribution"]
        check((r["unattributed_rebuilds"], r["unattributed_rebuild_spend"]) == (1, 300),
              "rebuild after a red blind check counts as waste before attribution")
        check((r["attributed_rebuilds"], r["attributed_rebuild_spend"]) == (1, 70),
              "rebuild after proof_found_defect counts as attributed")
        check(r["by_cause"] == [["blind_fail", 1, 300]], "waste ranked by its preceding end")
        a = m["instrument_availability"]
        check(a["checker"]["k"] == 3 and a["checker"]["n"] == 5, "checker: 3 valid verdicts of 4 + 1 lost")
        check(a["game"]["k"] == 2 and a["game"]["n"] == 3, "game: implemented + fail measured, unmeasured not")
        check(a["worker_proof"]["k"] == 2 and a["worker_proof"]["n"] == 3 and a["worker_proof"]["lost"] == 1,
              "worker: a finish and a defect found are measurements, worker_lost is not")
        rw = m["repeat_waste"]
        check(rw["repeats"] == 1 and rw["items"] == 1, "repeat: same end, detail differing only by sha/number/path")
        rl = m["repair_leverage"]
        check(rl["per_blocker"]["A"] == {"dependents": 1, "repaired": True, "restored": 1, "recurred": 0},
              "repair leverage: dependent restarted after the blocker closed")
        check(m["attribution_reversal_rate"]["value"] == dm.UNMEASURED, "reversal rate is UNMEASURED, never 0")
        check(m["validator_sensitivity"]["value"] == dm.UNMEASURED, "no seed set -> sensitivity UNMEASURED")
        check(m["audited_false_closes"]["value"] == dm.UNMEASURED, "no audit drawn -> false closes UNMEASURED")
        check(m["unknown_validation_debt"]["items"] == 3, "debt: blocked + 2 held")
        cov = m["source_coverage"]
        check(cov["unreadable_states"] == ["J"] and cov["no_attempts_items"] == ["K"] and cov["states_read"] == 9,
              "coverage names an unreadable state and an item with no attempts record")
        check(cov["malformed_lines"] == {"items/C/attempts.jsonl": 1, "journal.jsonl": 1},
              "coverage counts a torn JSONL line per file instead of reading it as fewer events")
        check(r["unpriced_rebuilds"] == 0, "every planted rebuild has a spend record")
        rep = {"store": s, "spend": {"rm-relentless-work-%s-g2" % dm.short("Z"): 100},
               "attempts": {"Z": [{"end": "checker_lost", "gen": 2, "detail": "x"}] * 3,
                            "Y": [{"end": "checker_lost", "gen": 2, "detail": "x"}] * 2}}
        long = {"store": s, "spend": {}, "attempts": {"W": [{"end": "blind_fail", "gen": 1, "detail": "x" * 200 + "alpha"},
                                                              {"end": "blind_fail", "gen": 3, "detail": "x" * 200 + "omega"}]}}
        check(dm.m_repeat_waste(long)["repeats"] == 0, "two failures differing after character 200 are not a repeat")
        rr = dm.m_repeat_waste(rep)
        check((rr["repeats"], rr["repeat_spend"], rr["unpriced_repeat_gens"]) == (3, 100, 1),
              "repeat spend charges a generation once; a generation with no spend record is unpriced, not free")
        unp = {"spend": {}, "attempts": {"Z": [{"end": "blind_fail", "gen": 1}, {"start": 1, "gen": 3}]}}
        u2 = dm.m_rebuild_waste(unp)
        check((u2["unattributed_rebuilds"], u2["unpriced_rebuilds"]) == (1, 1), "a rebuild with no spend record is unpriced")
        two = {"store": s, "states": {"P": {"status": "held"}, "Q": {"status": "blocked"}},
               "attempts": {"P": [{"at": dm.iso(now - 86400)}], "Q": [{"at": dm.iso(now - 101 * 86400)}]}}
        check(dm.m_debt(two, now)["median_age_days"] == 51.0, "debt median of an even population averages the middle pair")
        late = {"states": {"A": {"status": "done", "done_at": 10.0}},
                "attempts": {"B": [{"at": dm.iso(11), "end": "blocked_by_predecessor", "on": "A"},
                                   {"at": dm.iso(12), "start": 1, "gen": 3}]}}
        check(dm.m_repair_leverage(late)["per_blocker"]["A"]["restored"] == 0,
              "a repair that closed before the dependent was blocked restores nothing")
        check(dm.ons({"on": ["A", 3, "B"]}) == ["A", "B"] and dm.ons({"on": "A"}) == ["A"] and dm.ons({}) == [],
              "a blocker list or a single blocker")

        # the audit record
        check(dm.narrow_weak(snap["states"]) == ["B"], "targeted: WEAK GAP:OTHER only; GAP:DIFF and untagged are not")
        rows = dm.draw(snap, [], 2, 7, now, "S1")
        again = dm.draw(snap, [], 2, 7, now, "S1")
        check(rows == again, "the random draw is reproducible from its seed")
        nw = [x for x in rows if x["stratum"] == "narrow_weak"]
        rnd = [x for x in rows if x["stratum"] == "random"]
        check([x["item"] for x in nw] == ["B"] and len(rnd) == 2 and all(x["population"] == 4 for x in rows)
              and all(x["population_sha1"] == dm.hashlib.sha1("\n".join("ABCD").encode()).hexdigest() for x in rows),
              "a sample: every narrow-WEAK close targeted, a seeded random draw over all 4 closes")
        check(nw[0]["sha"] == "b" * 40 and nw[0]["proof"] == "python3 b.py" and nw[0]["reasons"].startswith("GAP:OTHER"),
              "a draw carries sha, proof and the deciding reasons, so an audit needs no store")
        nxt = dm.draw(snap, rows, 0, 7, now, "S2")
        check(nxt == [], "a narrow-WEAK close an earlier sample targeted is not drawn again")
        try:
            dm.draw(snap, rows, 2, 7, now, "S1")
            check(False, "a second draw under one name is refused")
        except SystemExit:
            check(True, "a second draw under one name is refused")
        for bad in (("S1", "G", "HOLDS", "me", "ran", "green"), ("S1", "B", "HOLDS", "me", "", "green"),
                    ("S1", "B", "MAYBE", "me", "ran", "green")):
            try:
                dm.audit_row(rows, *bad, now=now)
                check(False, "refused: %s" % (bad,))
            except SystemExit:
                check(True, "refused: %s" % (bad,))
        later = now + 3 * 86400
        audits = rows + [dm.audit_row(rows, "S1", "B", "VIOLATED", "me", "reran", "red on its own clause", later)]
        audits += [dm.audit_row(rows, "S1", x["item"], "HOLDS", "me", "reran", "green", later) for x in rnd]
        audits += [dm.audit_row(rows, "S1", rnd[0]["item"], "UNMEASURED", "me", "reran", "live only", later)]
        fc = dm.compute(snap, audits, None, later)["audited_false_closes"]["S1"]
        check(fc["narrow_weak"]["VIOLATED"] == 1 and fc["narrow_weak"]["false_close_rate"]["n"] == 1,
              "targeted false close counted in its own population")
        check(fc["random"]["HOLDS"] == 1 and fc["random"]["UNMEASURED"] == 1 and fc["random"]["false_close_rate"]["k"] == 0
              and fc["random"]["false_close_rate"]["n"] == 1,
              "random population apart; the last audit of a row stands; UNMEASURED leaves the rate's denominator")
        check(fc["narrow_weak"]["by_age"] == {"1-7d": {"audited": 1, "VIOLATED": 1}}, "stratified by closure age at audit")

        both = [{"kind": "draw", "sample": "S9", "stratum": st, "item": "B", "closed_at": dm.iso(now - 86400), "at": dm.iso(now)}
                for st in ("narrow_weak", "random")]
        both.append(dm.audit_row(both, "S9", "B", "HOLDS", "me", "reran", "green", now))
        orph = dm.m_false_closes(both[2:])
        check(orph.get("orphan_audits") == ["S9/B"], "an audit whose draw line is gone is named as an orphan")
        ov = dm.m_false_closes(both)["S9"]
        check(all(ov[st]["drawn"] == 1 and ov[st]["HOLDS"] == 1 for st in ("narrow_weak", "random")),
              "an item drawn in both populations counts in each, neither overwrites the other")

        ap = os.path.join(root, "audits.jsonl")
        with open(ap, "w") as f:
            f.write(json.dumps(rows[0]))                  # a valid record that lost its final newline
        dm.append([rows[1]], ap)
        check(dm._jsonl(ap) == rows[:2], "append never glues a row onto a record missing its last newline")
        check(dm.damaged(rows) == [], "a drawn sample is well formed")
        typo = dict(dm.audit_row(rows, "S1", "B", "HOLDS", "me", "ran", "green", now), verdict="VIOLTED")
        check(dm.damaged(rows + [typo]) == ["row %d: verdict 'VIOLTED'" % (len(rows) + 1)], "a misspelled verdict is damage")
        lone = dm.audit_row(rows, "S1", "B", "HOLDS", "me", "ran", "green", now)
        check(dm.damaged([lone]) == ["row 1: audit of S1/B has no draw"], "an orphan audit is damage, refused like a torn line")
        with open(ap, "a") as f:
            f.write(json.dumps(typo) + "\n")
        null = open(os.devnull, "w")
        err, out = sys.stderr, sys.stdout
        sys.stderr = sys.stdout = null
        try:
            rc_audit = dm.main(["--store", s, "--audits", ap, "audit", "S1", "B", "HOLDS", "--by", "x", "--how", "y",
                                "--evidence", "z"])
            rc_report = dm.main(["--store", s, "--audits", ap, "report", "--json"])
        finally:
            sys.stderr, sys.stdout = err, out
            null.close()
        check((rc_audit, rc_report) == (2, 2), "a damaged audit record refuses a write and the report exits 2")
        check(sum(1 for _ in open(ap)) == 3, "the refused audit wrote nothing")

        e = dm.compute(dm.load(os.path.join(root, "nowhere")), [], None, now)
        store_fed = ("accepted_delivery_yield", "end_to_end_cost", "rebuild_waste_before_attribution", "instrument_availability",
                     "repeat_waste", "repair_leverage", "unknown_validation_debt")
        check(all(e[k].get("value") == dm.UNMEASURED for k in store_fed), "an absent store reads UNMEASURED everywhere, never 0")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def part2():
    bad = {}
    rows = dm._jsonl(dm.AUDITS, bad)
    check(not bad, "the committed audit record parses whole (bad lines: %s)" % bad)
    check(dm.damaged(rows) == [], "every committed row is a well-formed draw or audit (%s)" % dm.damaged(rows)[:3])
    draws = [r for r in rows if r.get("kind") == "draw"]
    check(bool(draws), "the committed audit record has a sample")
    if not draws:
        return
    first = min(r["at"] for r in draws)
    s1 = draws[0]["sample"]
    mine = [r for r in draws if r["sample"] == s1]
    check(mine[0]["at"] == first, "first sample is the earliest drawn")
    strata = {r["stratum"] for r in mine}
    check(strata == {"narrow_weak", "random"}, "first sample: a targeted narrow_weak stratum and a random one")
    check(all(r["verdict"] == "WEAK" and (r["reasons"] or "").startswith("GAP:OTHER") for r in mine
              if r["stratum"] == "narrow_weak"), "every targeted row closed on a WEAK read as PASS (GAP:OTHER)")
    audited = {(r["sample"], r["item"]): r for r in rows if r.get("kind") == "audit"}
    missing = [r["item"] for r in mine if (s1, r["item"]) not in audited]
    check(not missing, "every row of the first sample is audited (missing: %s)" % missing)
    check(all(a["by"] and a["how"] and a["evidence"] and a["verdict"] in dm.VERDICTS for a in audited.values()),
          "every audit names auditor, method, evidence and a verdict")
    m = dm.m_false_closes(rows)
    check("orphan_audits" not in m, "no audit in the record has lost its draw")
    check(set(m[s1]) == strata and all(m[s1][k]["unaudited"] == 0 for k in strata),
          "the report gives each population on its own, nothing unaudited")
    later = {(r["sample"], r["item"]) for r in draws} - set(audited)
    check(not later, "every later sample's drawn rows are audited too (missing: %s)" % sorted(later))


if __name__ == "__main__":
    part1()
    part2()
    print("RESULT: %s (%d failing)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
