#!/usr/bin/env python3
"""selftest_concept_owner_certify.py - the owner's coverage certificate (concept_tree.certify, `signed_by: owner`).

He passed ExplosiveKnockback on his own word past a not_covered judge verdict (2026-11-13, OWNER:1794608649743135329:
"Yes, fix it like that, and then please record this as an actual Pass."). The gate takes that certificate only on his
own OWNER event (ownerSaid or byCard), on this concept's item or one caused by it or by its refusal records, newer than the judge verdict on file; an agent's --why or
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
    errs = CT.write(d, SCT.draft(), repo, legacy=True)
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


def conductor_certify():
    """Owner 2026-11-19 (RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS): the Conductor window's act certifies,
    recorded certified_by conductor and never as his words; a launched helper's act under the same ruling does not."""
    import conductor_acts as CA
    tmp = tempfile.mkdtemp(prefix="concept_conductor_certify_")
    why = CA.tagged("certify past the coverage verdict: both gaps are claimed fixed with evidence", "coverage certify")
    try:
        repo, d = fixture(tmp)
        with open(os.path.join(repo, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
            f.write(json.dumps(ev(3001, "2026-11-13T23:00:00Z", perRuling=CA.RULING, why=why, ranBy="BENCH",
                                  role_unit="rm-detached-bench-x-1")) + "\n")
            f.write(json.dumps(ev(3002, "2026-11-13T23:01:00Z", perRuling=CA.RULING, why=why, ranBy="BENCH")) + "\n")
        notes = []
        got = CT.certify(d, "OWNER:3001", repo, emit=lambda r, i, t: notes.append(t))
        check("conductor: a launched helper's act under the five-acts ruling certifies nothing",
              len(got) == 1 and "not the Conductor's act" in got[0] and notes == [], got)
        got = CT.certify(d, "OWNER:3002", repo, emit=lambda r, i, t: notes.append(t))
        check("conductor: the Conductor window's act certifies", got == [], got)
        cov = CT.load(d).get("coverage") or {}
        check("conductor: recorded certified_by conductor, its words the Conductor's act, never his",
              cov.get("certified_by") == "conductor" and str(cov.get("owner_words")).startswith("the Conductor's act: ")
              and "ownerSaid" not in json.dumps(cov), cov)
        errs, _ = CT.gate(d, repo)
        check("conductor: the gate passes on the Conductor's certificate", errs == [], errs)
        check("conductor: the summary says the Conductor's act",
              CT.coverage_summary(d, repo).startswith("passed as the Conductor's act"), CT.coverage_summary(d, repo))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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

        # his words on a repair item caused by the mod's item count for the mod's tree
        # (RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_BARRAGE_P99_HELD_AGAIN: twice his agreed rewording sat on the repair item
        # and had to be re-recorded on the concept's item by hand)
        repo3, d3 = fixture(os.path.join(tmp, "three"))
        rep = os.path.join(d3, "version", "criterion_repairs", "bar_x")
        os.makedirs(rep)
        put_json(rep, "refusal.json", {"item": "ROUTE_ITEM", "refusals": []})
        stray = os.path.join(d3, "version", "elsewhere")
        os.makedirs(stray)
        put_json(stray, "refusal.json", {"item": "STRAY_ROUTE"})
        led = os.path.join(repo3, CT.LEDGER_DIR, "events", "RUNNER.jsonl")
        os.makedirs(os.path.dirname(led), exist_ok=True)
        filed = [{"event": "spawn", "id": "PIPE_ITEM", "name": "ROUTE_ITEM", "from": "PIPE_ITEM"},
                 {"event": "file", "id": "REPAIR_ITEM", "caused_by": "ROUTE_ITEM"},
                 {"event": "file", "id": "RECERT_ITEM", "caused_by": "REPAIR_ITEM/run-1"},
                 {"event": "file", "id": "KID_ITEM", "caused_by": ITEM},
                 {"event": "file", "id": "STRAY_REPAIR", "caused_by": "STRAY_ROUTE"},
                 {"event": "file", "id": "LOOP_A", "caused_by": "LOOP_B"},
                 {"event": "file", "id": "LOOP_B", "caused_by": "LOOP_A"}]
        with open(led, "w", encoding="utf-8") as f:
            for e in filed:
                f.write(json.dumps(dict(e, seat="RUNNER", ts="2026-11-13T20:00:00Z")) + "\n")
        word = "1 agree."
        more = {"repair": ev(3001, "2026-11-14T03:29:30Z", item="REPAIR_ITEM", ownerSaid=word),
                "recert": ev(3002, "2026-11-14T03:30:00Z", item="RECERT_ITEM", ownerSaid=word),
                "kid": ev(3003, "2026-11-14T03:31:00Z", item="KID_ITEM", byCard="Bar -> agree"),
                "route": ev(3004, "2026-11-14T03:32:00Z", item="ROUTE_ITEM", ownerSaid=word),
                "pipe": ev(3005, "2026-11-14T03:33:00Z", item="PIPE_ITEM", ownerSaid=word),
                "stray": ev(3006, "2026-11-14T03:34:00Z", item="STRAY_REPAIR", ownerSaid=word),
                "loop": ev(3007, "2026-11-14T03:35:00Z", item="LOOP_A", ownerSaid=word),
                "repair_why": ev(3008, "2026-11-14T03:36:00Z", item="REPAIR_ITEM", why="he agreed")}
        with open(os.path.join(repo3, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
            for e in more.values():
                f.write(json.dumps(e) + "\n")
        for name, key in [("the item a refusal record of this concept names", "route"),
                          ("a repair item caused by it", "repair"),
                          ("an item caused by that repair item's run", "recert"),
                          ("an item caused by the concept's item", "kid")]:
            CT.load(d3) and CT.put(d3, dict(CT.load(d3), coverage={}))
            got = CT.certify(d3, "OWNER:%s" % more[key]["tsn"], repo3, emit=emit)
            check("certify accepts his word on %s" % name, got == [] and CT.gate(d3, repo3)[0] == [],
                  (got, CT.gate(d3, repo3)[0]))
        check("the certificate's note still goes to the concept's own item", notes[-1][0] == ITEM, notes[-1])
        summ = CT.coverage_summary(d3, repo3)
        check("summary names the item his word sat on when it is not the concept's", "on KID_ITEM" in summ, summ)
        good3 = copy.deepcopy(CT.load(d3)["coverage"])
        for name, key, want in [("the upstream pipeline item only (an ancestor, not caused by the mod)", "pipe",
                                 "not this concept's item"),
                                ("a repair caused by a refusal record outside criterion_repairs/", "stray",
                                 "not this concept's item"),
                                ("an item in a caused_by loop", "loop", "not this concept's item"),
                                ("the repair item, an agent's --why only", "repair_why", "no ownerSaid or byCard")]:
            n0 = len(notes)
            got = CT.certify(d3, "OWNER:%s" % more[key]["tsn"], repo3, emit=emit)
            check("certify refuses his word on %s" % name, len(got) == 1 and want in got[0] and len(notes) == n0, got)
            forge(d3, good3, more[key])
            errs, _ = CT.gate(d3, repo3)
            check("gate refuses a forged stamp on %s" % name, len(errs) == 1 and want in errs[0], errs)

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

        # RIMMANDRAKE_BIND_CERTIFICATE_TO_WHAT_HE_SAW and _CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT
        repo4, d4 = fixture(os.path.join(tmp, "four"))
        notes4 = []
        emit4 = lambda r, i, t: notes4.append((i, t))     # noqa: E731
        check("bind: certify on his event", CT.certify(d4, "OWNER:2001", repo4, emit=emit4) == [], notes4)
        c4 = CT.load(d4)["coverage"]
        check("bind: the stamp carries the gap ids and the gap text he passed past",
              c4.get("judge_gids") == ["g1", "g2"] and len(str(c4.get("judge_gaps_sha"))) == 64, c4)
        vp4 = os.path.join(d4, "coverage_verdict.json")
        v4 = open(vp4).read()
        put_json(d4, "coverage_verdict.json", dict(json.loads(v4), gaps=[{"gid": "g1", "what": "a"},
                                                                      {"gid": "g3", "what": "b"}]))
        errs, _ = CT.gate(d4, repo4)
        check("bind: a verdict with other gap ids (same run, verdict and count) refuses", len(errs) == 1
              and "gap ids" in errs[0], errs)
        put_json(d4, "coverage_verdict.json", dict(json.loads(v4), gaps=[{"gid": "g1", "what": "a"},
                                                                      {"gid": "g2", "what": "b, reworded"}]))
        errs, _ = CT.gate(d4, repo4)
        check("bind: the same gap ids with other gap text refuse", len(errs) == 1 and "gap text" in errs[0], errs)
        with open(vp4, "w") as f:
            f.write(v4)
        check("bind: the verdict he saw passes again", CT.gate(d4, repo4)[0] == [], CT.gate(d4, repo4)[0])
        with open(os.path.join(d4, "sheet.md"), "a") as f:
            f.write("\nAn edit after his word.\n")
        errs, _ = CT.gate(d4, repo4)
        check("bind: an edit after his event voids the certificate at the gate", errs and "another sheet" in errs[0], errs)
        got = CT.certify(d4, "OWNER:2001", repo4, emit=emit4)
        check("bind: his same event cannot be replayed onto the edited sheet", len(got) == 1
              and "already certified another" in got[0] and "carry" in got[0], got)
        for ref, want in (("OWNER:2004", "not newer than the certificate"), ("OWNER:2002", "no ownerSaid or byCard"),
                          ("OWNER:2005", "not this concept's item")):
            got = CT.carry(d4, ref, repo4, emit=emit4)
            check("carry refuses %s" % ref, len(got) == 1 and want in got[0], got)
        n4 = len(notes4)
        got = CT.carry(d4, "OWNER:2006", repo4, emit=emit4)
        c4 = CT.load(d4)["coverage"]
        check("carry: an edit made under his later card carries the certificate", got == [] and
              CT.gate(d4, repo4)[0] == [] and c4.get("carried_by") == "OWNER:2006" and c4.get("owner_event") ==
              "OWNER:2001", (got, CT.gate(d4, repo4)[0], c4))
        check("carry: the carry note is the edit's record and cites the card", len(notes4) == n4 + 1 and
              notes4[-1][1].startswith(CT.CARRY_MARK + " ") and "card=OWNER:2006" in notes4[-1][1], notes4[-1:])
        tree4 = CT.load(d4)
        tree4["coverage"] = dict(c4, carried_by="OWNER:2004")
        CT.put(d4, tree4)
        errs, _ = CT.gate(d4, repo4)
        check("carry: a stamp carried by hand on an older event is refused by the gate", len(errs) == 1
              and "carried through an edit" in errs[0], errs)
        repo5, d5 = fixture(os.path.join(tmp, "five"))
        CT.certify(d5, "OWNER:2001", repo5, emit=emit4)
        with open(os.path.join(d5, "sheet.md"), "a") as f:
            f.write("\nAn edit after his word.\n")
        got = CT.certify(d5, "OWNER:2006", repo5, emit=emit4)
        check("bind: his newer event after an edit certifies the edited tree", got == [] and
              CT.gate(d5, repo5)[0] == [] and CT.load(d5)["coverage"]["owner_event"] == "OWNER:2006", got)
        # replay holes the review found: each needs a newer word of his
        repo6, d6 = fixture(os.path.join(tmp, "six"))
        with open(os.path.join(repo6, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
            f.write(json.dumps(ev(2007, "2026-11-13T22:10:00Z", ownerSaid="Pass it as it stands.")) + "\n")
        CT.certify(d6, "OWNER:2001", repo6, emit=emit4)
        vp6 = os.path.join(d6, "coverage_verdict.json")
        v6 = open(vp6).read()
        put_json(d6, "coverage_verdict.json", dict(json.loads(v6), gaps=[{"gid": "g1", "what": "a"},
                                                                      {"gid": "g2", "what": "b, reworded"}]))
        got = CT.certify(d6, "OWNER:2001", repo6, emit=emit4)
        check("replay: his same event cannot re-certify past changed gap text", len(got) == 1
              and "already certified another gaps_sha" in got[0], got)
        with open(vp6, "w") as f:
            f.write(v6)
        with open(os.path.join(d6, "sheet.md"), "a") as f:
            f.write("\nAn edit after his word.\n")
        got = CT.certify(d6, "OWNER:2007", repo6, emit=emit4)
        check("replay: an unused event older than the one already used cannot certify the edit", len(got) == 1
              and "not newer than OWNER:2001" in got[0], got)
        check("replay: the carry under his later card still works", CT.carry(d6, "OWNER:2006", repo6, emit=emit4) == [])
        with open(os.path.join(d6, "sheet.md"), "a") as f:
            f.write("\nA second edit, under no card.\n")
        got = CT.certify(d6, "OWNER:2006", repo6, emit=emit4)
        check("replay: the card a carry used cannot certify a later edit", len(got) == 1
              and "already certified another" in got[0], got)
        bad = os.path.join(repo6, CT.LEDGER_DIR, "events", "BROKEN.jsonl")
        os.makedirs(os.path.dirname(bad), exist_ok=True)
        with open(bad, "w") as f:
            f.write('{"text": "%s concept=%s tree=x owner=OWNER:2001 broken\n' % (CT.OWNER_MARK, CT.concept_rel(d6, repo6)))
        got = CT.certify(d6, "OWNER:2006", repo6, emit=emit4)
        check("replay: a ledger record of this concept that does not parse refuses", len(got) == 1
              and "does not parse" in got[0], got)
        os.remove(bad)
        os.makedirs(os.path.join(repo6, CT.LEDGER_DIR, "events", "UNREADABLE.jsonl"), exist_ok=True)
        got = CT.certify(d6, "OWNER:2006", repo6, emit=emit4)
        check("replay: a ledger shard that cannot be read refuses (its history is unknown)", len(got) == 1
              and "cannot be read" in got[0], got)
        # the ledger is the history when the stamp has moved on: carry with a card, a newer word over changed gaps,
        # then the card again must refuse (its carry note binds the gaps it covered)
        repo7, d7 = fixture(os.path.join(tmp, "seven"))
        shard7 = os.path.join(repo7, CT.LEDGER_DIR, "events", "BENCH.jsonl")
        os.makedirs(os.path.dirname(shard7), exist_ok=True)

        def emit7(r, i, t):
            with open(shard7, "a") as f:
                f.write(json.dumps({"event": "note", "id": i, "text": t}) + "\n")
        with open(os.path.join(repo7, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
            f.write(json.dumps(ev(2008, "2026-11-13T23:30:00Z", ownerSaid="Pass it with the reworded gap.")) + "\n")
        CT.certify(d7, "OWNER:2001", repo7, emit=emit7)
        with open(os.path.join(d7, "sheet.md"), "a") as f:
            f.write("\nAn edit under his card.\n")
        check("ledger: carry under his card", CT.carry(d7, "OWNER:2006", repo7, emit=emit7) == [])
        vp7 = os.path.join(d7, "coverage_verdict.json")
        put_json(d7, "coverage_verdict.json", dict(json.loads(open(vp7).read()), gaps=[{"gid": "g1", "what": "a"},
                                                                                    {"gid": "g2", "what": "b2"}]))
        check("ledger: his newer word certifies past the reworded gap", CT.certify(d7, "OWNER:2008", repo7, emit=emit7) == [])
        got = CT.certify(d7, "OWNER:2006", repo7, emit=emit7)
        check("ledger: the carry's card cannot then certify the reworded gaps", len(got) == 1
              and "already certified another" in got[0], got)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    conductor_certify()
    print("selftest_concept_owner_certify: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
