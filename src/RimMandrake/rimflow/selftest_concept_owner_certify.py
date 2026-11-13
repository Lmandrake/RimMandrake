#!/usr/bin/env python3
"""selftest_concept_owner_certify.py - the owner's coverage certificate (concept_tree.certify, `signed_by: owner`).

He passed ExplosiveKnockback on his own word past a not_covered judge verdict (2026-11-13, OWNER:1794608649743135329:
"Yes, fix it like that, and then please record this as an actual Pass."). The gate takes that certificate only on his
own OWNER event (ownerSaid or byCard), on this concept's item, newer than the judge verdict on file; an agent's --why or
--per-ruling event, an older word, another item's word, a newer verdict or changed claims refuse, and lint still
refuses. Each refusal is checked twice: certify refuses it, and a stamp forged by hand is refused by the gate itself.
Runs in a temp dir; touches no real concept and no ledger (the note goes to a fake)."""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import selftest_concept_tree as SCT  # noqa: E402

FAILS = []
ITEM = "FOO_CONCEPT_ITEM"
VERDICT_AT = "2026-11-13T19:59:20Z"


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def ev(tsn, ts, item=ITEM, **kw):
    return dict({"seat": "OWNER", "event": "note", "id": item, "text": "a note", "ts": ts, "tsn": tsn}, **kw)


EVENTS = {
    "good": ev(2001, "2026-11-13T22:24:09Z", ownerSaid="Yes, fix it like that, and then please record this as an actual Pass."),
    "per_ruling": ev(2002, "2026-11-13T22:30:00Z", perRuling="CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM",
                     why="the owner passed it", text="PASS on the owner's word"),
    "why_only": ev(2003, "2026-11-13T22:31:00Z", why="record this as an actual Pass"),
    "older": ev(2004, "2026-11-13T19:00:00Z", ownerSaid="Yes, record this as an actual Pass."),
    "other_item": ev(2005, "2026-11-13T22:40:00Z", item="OTHER_ITEM", ownerSaid="Pass it."),
    "card": ev(2006, "2026-11-13T22:50:00Z", byCard="Foo coverage -> pass it as it stands"),
}


def put_json(d, name, obj):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)


def fixture(tmp):
    repo, d = SCT.stage(tmp)
    SCT.validate_walk(repo)
    errs = CT.write(d, SCT.draft(), repo)
    assert not errs, errs
    with open(os.path.join(repo, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
        for e in EVENTS.values():
            f.write(json.dumps(e) + "\n")
    put_json(d, "coverage_verdict.json", {"judge": "rm-coverage-judge-100", "verdict": "not_covered", "at": VERDICT_AT,
                                          "gaps": [{"gid": "g1", "what": "a"}, {"gid": "g2", "what": "b"}]})
    put_json(d, "coverage_fixes.json", {"against": "rm-coverage-judge-100",
                                        "claims": [{"gap": "g1", "evidence": "x"}, {"gap": "g2", "evidence": "y"}]})
    return repo, d


def forge(d, base, event):
    """A hand-written owner stamp naming `event` (the gate, not certify, must refuse it)."""
    tree = CT.load(d)
    cov = dict(base, owner_event="OWNER:%s" % event["tsn"], owner_words=CT.his_word(event) or event.get("why"),
               owner_at=event["ts"])
    tree["coverage"] = cov
    CT.put(d, tree)


def main():
    tmp = tempfile.mkdtemp(prefix="concept_owner_certify_")
    notes = []
    emit = lambda r, i, t: notes.append((i, t))     # noqa: E731
    try:
        repo, d = fixture(tmp)
        errs, _ = CT.gate(d, repo)
        check("base: an unsigned tree is refused", errs == ["no coverage signature"], errs)
        before = open(os.path.join(d, "tree.json")).read()

        # (a)-(d) through certify: refused, nothing written, no ledger note
        cases = [("(a) no event", "OWNER:9999", "finds no event"),
                 ("(b) an agent's --per-ruling event", "OWNER:2002", "no ownerSaid or byCard"),
                 ("(b) an agent's --why event", "OWNER:2003", "no ownerSaid or byCard"),
                 ("(c) an owner event older than the last verdict", "OWNER:2004", "not newer than the last judge verdict"),
                 ("(d) an owner event on another item", "OWNER:2005", "not this concept's item")]
        for name, ref, want in cases:
            got = CT.certify(d, ref, repo, emit=emit)
            check("certify refuses %s" % name, len(got) == 1 and want in got[0], got)
        check("refused certifies wrote nothing and noted nothing",
              open(os.path.join(d, "tree.json")).read() == before and notes == [], notes)

        # accepted with his real event
        got = CT.certify(d, "OWNER:2001", repo, emit=emit)
        check("certify accepts his ownerSaid event on this item, newer than the verdict", got == [], got)
        tree = CT.load(d)
        cov = tree.get("coverage") or {}
        check("the stamp is signed_by owner, never a judge name", cov.get("signed_by") == "owner"
              and cov.get("signed_by") not in CT.SIGNER_UNITS, cov.get("signed_by"))
        check("the stamp carries his words, the event, the last verdict and the claims hash",
              cov.get("owner_words") == EVENTS["good"]["ownerSaid"] and cov.get("owner_event") == "OWNER:2001"
              and (cov.get("judge_run"), cov.get("judge_verdict"), cov.get("judge_gaps")) ==
              ("rm-coverage-judge-100", "not_covered", 2) and cov.get("fixes_hash") == CT.fixes_hash(d)
              and cov.get("owner_at") == "2026-11-13T22:24:09Z" and cov.get("judge_at") == VERDICT_AT, cov)
        errs, _ = CT.gate(d, repo)
        check("gate passes on the owner certificate", errs == [], errs)
        check("one ledger note, on the item, owner-certified, never a coverage-signed judge line",
              len(notes) == 1 and notes[0][0] == ITEM and notes[0][1].startswith(CT.OWNER_MARK + " ")
              and not notes[0][1].startswith(CT.SIGN_MARK) and "owner=OWNER:2001" in notes[0][1], notes)
        summ = CT.coverage_summary(d, repo)
        check("summary: passed on the owner's word, beside the judge's not_covered",
              summ.startswith("passed on the owner's word") and
              "last judge verdict not_covered (2 gaps, all claimed fixed" in summ and "signed by the coverage judge"
              not in summ, summ)
        good = copy.deepcopy(cov)

        # (a)-(d) at the gate: a stamp forged by hand on each event is refused by the gate itself
        for name, key, want in [("(b) per-ruling", "per_ruling", "no ownerSaid or byCard"),
                                ("(b) why-only", "why_only", "no ownerSaid or byCard"),
                                ("(c) older", "older", "not newer than the last judge verdict"),
                                ("(d) other item", "other_item", "not this concept's item")]:
            forge(d, good, EVENTS[key])
            errs, _ = CT.gate(d, repo)
            check("gate refuses a forged stamp on %s" % name, len(errs) == 1 and want in errs[0], errs)
        forge(d, good, {"tsn": 9999, "ts": "2026-11-14T00:00:00Z", "ownerSaid": "x"})
        errs, _ = CT.gate(d, repo)
        check("gate refuses a forged stamp on (a) no event", len(errs) == 1 and "finds no event" in errs[0], errs)
        tree = CT.load(d)
        tree["coverage"] = dict(good, owner_words="Pass everything forever.")
        CT.put(d, tree)
        errs, _ = CT.gate(d, repo)
        check("gate refuses words that are not the words on his event", len(errs) == 1 and "not the words" in errs[0],
              errs)

        # the certificate stands only past the verdict and the claims he saw
        tree["coverage"] = good
        CT.put(d, tree)
        check("restored stamp passes again", CT.gate(d, repo)[0] == [], CT.gate(d, repo)[0])
        vpath = os.path.join(d, "coverage_verdict.json")
        v0 = open(vpath).read()
        put_json(d, "coverage_verdict.json", dict(json.loads(v0), judge="rm-coverage-judge-200", at="2026-11-13T22:00:00Z"))
        errs, _ = CT.gate(d, repo)
        check("gate refuses once a newer judge verdict is on file", len(errs) == 1 and "newer" in errs[0], errs)
        with open(vpath, "w") as f:
            f.write(v0)
        fpath = os.path.join(d, "coverage_fixes.json")
        f0 = open(fpath).read()
        put_json(d, "coverage_fixes.json", {"against": "rm-coverage-judge-100", "claims": [{"gap": "g1", "evidence": "x"}]})
        errs, _ = CT.gate(d, repo)
        check("gate refuses once the gap claims change", len(errs) == 1 and "claims" in errs[0], errs)
        check("summary then says the certificate is NOT valid", CT.coverage_summary(d, repo).startswith(
            "owner certificate NOT valid"), CT.coverage_summary(d, repo))
        with open(fpath, "w") as f:
            f.write(f0)
        with open(os.path.join(d, "sheet.md"), "a") as f:
            f.write("\n")
        errs, _ = CT.gate(d, repo)
        check("gate refuses a certificate on another sheet", "the signature is on another sheet" in errs, errs)
        with open(os.path.join(d, "sheet.md"), "w") as f:
            f.write(SCT.SHEET)
        check("restored again: gate passes", CT.gate(d, repo)[0] == [], CT.gate(d, repo)[0])

        # (e) lint still runs and refuses under a valid certificate
        floor, _fh = CT.load_floor()
        alt = os.path.join(tmp, "floor_alt.json")
        with open(alt, "w") as f:
            json.dump(dict(floor, note="a changed floor"), f)
        lint_errs, _ = CT.lint(d, repo, alt)
        errs, _ = CT.gate(d, repo, alt)
        check("(e) lint red: the gate refuses with lint's reason while the certificate is valid",
              lint_errs != [] and all(e in errs for e in lint_errs) and not any("owner certificate" in e for e in errs),
              errs)
        bad = dict(CT.load(d), bogus_key=1)
        SCT.write_raw(d, bad)
        n0, lint_errs = len(notes), CT.lint(d, repo)[0]
        got = CT.certify(d, "OWNER:2001", repo, emit=emit)
        check("(e) certify refuses a tree lint refuses, with lint's reasons, and notes nothing",
              lint_errs != [] and got == lint_errs and len(notes) == n0, got)

        # a card is his word too
        repo2, d2 = fixture(os.path.join(tmp, "two"))
        got = CT.certify(d2, "2006", repo2, emit=emit)
        check("certify accepts his byCard event (bare tsn)", got == [] and CT.gate(d2, repo2)[0] == [], got)

        # the designer pages read it as his word, not as a judge pass
        import designer_stage as DS
        st = {"mod": "Foo", "item": ITEM, "stage": 5, "status": "locked", "parks": [{}],
              "results": [{"stage": s, "outcome": "done"} for s in range(6)]}
        page = DS.lock_summary(d2, st, "run-x")
        check("lock page: locked, and coverage passed on the owner's word beside the judge's verdict",
              page.startswith("# Foo: locked") and "passed on the owner's word" in page and "not_covered" in page
              and "parked for you" not in page, page)
        page = DS.park_summary(d2, dict(st, status="blocked"), "ceiling", "a test park")
        check("park page: the certificate replaces the judge's gap list",
              "Coverage: passed on the owner's word" in page and "says not covered" not in page, page)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest_concept_owner_certify: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
