#!/usr/bin/env python3
"""Selftest for modaudit/merge_checks.py (offline, pure functions only).

    python3 src/RimMandrake/Utils/modaudit/selftest_merge_checks.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


def assess(**k):
    base = {"packageId": "a.b", "batch": 3, "verdict": "ELIMINATE-COMPLETELY", "fit": "dissonant",
            "card_worthy": True, "needs_owner": "Should it go?", "open_questions": ["q1"],
            "problems": [{"kind": "memory", "severity": 2}, {"kind": "log_noise", "severity": 3},
                         {"kind": "log_noise", "severity": 1}],
            "source": {"available": "yes", "url": "https://github.com/pardeike/Harmony", "kind": "github",
                       "confidence": "MEASURED"},
            "retirement_cost": {"dependants": []}, "verdict_confidence": "INFERRED", "adds": {}}
    base.update(k)
    return base


def chk(verdict="CHALLENGE", corrections=()):
    return {"packageId": "a.b", "check_verdict": verdict, "corrections": list(corrections), "confidence": "MEASURED"}


def main():
    import merge_checks as m
    # parsers
    check("verdict parse with tail", m.parse_verdict("KEEP-TEMPORARILY-THEN-PHASE-OUT (follows docmate)"),
          "KEEP-TEMPORARILY-THEN-PHASE-OUT")
    check("verdict parse KEEP not eaten by KEEP-TEMP", m.parse_verdict("KEEP (as framework)"), "KEEP")
    check("verdict parse none", m.parse_verdict("pending the card"), None)
    check("card false", m.parse_card("merged into the MiningCo family card")[0], False)
    check("card true text", m.parse_card("True, re-asked as: keep it?")[0], True)
    check("card bool", m.parse_card(False)[0], False)
    check("sev U", m.parse_sev("U (save-side dead references)"), "U")
    check("sev first standalone digit", m.parse_sev("size 2: disk_mb 51.33"), 2)
    check("sev ignores decimals", m.parse_sev("1 (proxy is 432.9 MB of icons)"), 1)
    check("needs_owner string -> list", m.norm_questions("Ask him?"), ["Ask him?"])
    check("needs_owner none", m.norm_questions(None), [])
    check("answered text clears", m.answered("[] (answered: owner override 2026-08-12)"), True)
    check("question text kept", m.answered("add: 'Remove it, or keep it?'"), False)
    check("field slot problems", m.slot("problems[memory].severity"), ("problem", "memory"))
    check("field slot dotted", m.slot("problems.log_noise.severity"), ("problem", "log_noise"))
    check("field slot confidence only", m.slot("problems.log_noise.confidence"), ("other", None))
    check("field slot source", m.slot("source.url"), ("source", "url"))
    # conflict case: checker proposes KEEP-TEMP, spot-check NOT confirmed -> DISPUTED, assessor verdict kept
    c = chk(corrections=[{"field": "verdict", "old": "ELIMINATE-COMPLETELY",
                          "new": "KEEP-TEMPORARILY-THEN-PHASE-OUT (decide the trio together)", "evidence": "batch 01"}])
    r = m.merge_row(assess(), c, {"spotchecks": {"a.b": {"result": "NOT_CONFIRMED", "path": "x", "finding": "no"}}},
                    facts={})
    check("dispute keeps assessor", r["final_decision"], "ELIMINATE-COMPLETELY")
    check("dispute status", r["decision_status"], "DISPUTED")
    check("dispute keeps checker's", r["checker_proposed_decision"], "KEEP-TEMPORARILY-THEN-PHASE-OUT")
    check("dispute not changed", r["decision_changed_by_checker"], False)
    # no spot-check at all is also a dispute (never auto-accept)
    r = m.merge_row(assess(), c, {"spotchecks": {}}, facts={})
    check("unchecked challenge disputed", r["decision_status"], "DISPUTED")
    # confirmed -> checker verdict taken
    r = m.merge_row(assess(), c, {"spotchecks": {"a.b": {"result": "CONFIRMED", "path": "p.md:3", "finding": "ok"}}},
                    facts={})
    check("confirmed takes checker", r["final_decision"], "KEEP-TEMPORARILY-THEN-PHASE-OUT")
    check("confirmed changed flag", r["decision_changed_by_checker"], True)
    check("confirmed reason cites spotcheck", "p.md:3" in r["decision_change_reason"], True)
    # field amendments
    c2 = chk("AMEND", [{"field": "card_worthy", "old": True, "new": False, "evidence": "e"},
                       {"field": "needs_owner", "old": "x", "new": "[] (answered: ruling R-S7)", "evidence": "spec:1"},
                       {"field": "problems[memory].severity", "old": 2, "new": 1, "evidence": "band"},
                       {"field": "source.url", "old": "pardeike", "new": "none verified (bundled-library false match)",
                        "evidence": "facts"},
                       {"field": "fit", "old": "dissonant", "new": "neutral (library)", "evidence": "e"}])
    r = m.merge_row(assess(), c2, {"spotchecks": {}}, facts={})
    check("amend card", r["card_worthy"], False)
    check("amend answered question dropped", r["needs_owner"], [])
    check("answered recorded", len(r["questions_answered_by_checker"]), 1)
    check("amend memory sev", r["sev_memory"], 1)
    check("log_noise max of duplicates", r["sev_log_noise"], 3)
    check("source url rejected", (r["source_url"], r["source_kind"]), (None, "none"))
    check("fit amended", r["fit"], "neutral")
    check("status amended", r["decision_status"], "AGREED")
    check("evidence pointers", "assessments/batch_03.jsonl" in r["evidence"], True)
    # facts regen rejection: assessor kept a false-match url that facts now REJECTS
    r = m.merge_row(assess(source={"url": "https://github.com/pardeike/Harmony", "kind": "github", "confidence": "MEASURED"}),
                    None, {}, facts={"a.b": {"source_rejected": ["pardeike/Harmony (bundled lib)"], "source_url": None,
                                              "source_kind": "steam-only", "source_confidence": "INFERRED"}})
    check("facts rejection overrides assessor url", (r["source_url"], r["source_kind"]), (None, "steam-only"))
    if FAILS:
        print("FAIL %d" % len(FAILS))
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("OK selftest_merge_checks")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:                 # a crash is a failure, named
        print("FAIL crashed: %s: %s" % (type(e).__name__, e))
        sys.exit(1)
