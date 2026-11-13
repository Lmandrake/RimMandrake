"""selftest_designer_quick_look.py - once code exists, a Designer result that asks him something says whether a quick
look would settle it (RIMMANDRAKE_OFFER_OWNER_QUICK_LOOK_LOUDLY; owner, OWNER.jsonl:1794527688430451936: "If we can
insert an owner quick-look to settle a difficult or several questions swiftly, offer that loudly.").

designer_stage.result_errors refuses a waiting_owner result, or a return that proposes a question, without a
well-formed quick_look when record.json's inventory has a capability with impl present; a concept with no code, and a
return with no question, owe nothing. The loud half (QUICK LOOK OFFERED on his queue line and park page) is
selftest_designer_park's. Every write goes to a temp dir; the real alarm and told files are checked unchanged."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402
from selftest_coverage_judge import concept  # noqa: E402
from selftest_designer_park import real_marks  # noqa: E402

FAILS = []
BUILT = [{"id": "knockback", "impl": "present", "impl_evidence": "src/x.cs"}]
NONE_BUILT = [{"id": "knockback", "impl": "absent", "search_scope": "src/"}]
OFFER = {"offer": True, "settles": ["ask_blast"], "scene": "a wall throws a pawn in the storeroom"}
DECLINE = {"offer": False, "why": "the question is about intent, not what the code does"}


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def ql_errs(errs):
    return [e for e in errs if "quick_look" in e or "quick look" in e]


def units():
    rec = {"inventory": BUILT}
    check("no code: nothing owed", DS.quick_look_errors({}, {"inventory": NONE_BUILT}) == [])
    check("no record: nothing owed", DS.quick_look_errors({}, None) == [])
    check("code, no quick_look: refused", len(DS.quick_look_errors({}, rec)) == 1, DS.quick_look_errors({}, rec))
    check("code, offer as a string: refused", DS.quick_look_errors({"quick_look": {"offer": "yes"}}, rec) != [])
    check("an offer with what it settles and what he sees: accepted", DS.quick_look_errors({"quick_look": OFFER}, rec) == [])
    check("an offer settling nothing: refused",
          DS.quick_look_errors({"quick_look": dict(OFFER, settles=[])}, rec) != [])
    check("an offer with no scene: refused",
          DS.quick_look_errors({"quick_look": {"offer": True, "settles": ["a"]}}, rec) != [])
    check("a decline with why: accepted", DS.quick_look_errors({"quick_look": DECLINE}, rec) == [])
    check("a decline with no why: refused", DS.quick_look_errors({"quick_look": {"offer": False}}, rec) != [])


def staged(base, name, stage, inventory):
    root = os.path.join(base, name)
    d = concept(root, stage=stage, status="ready")
    DS.write_json(os.path.join(d, "record.json"), {"inventory": inventory, "asks": [
        {"id": "ask_blast", "status": "sent", "text": "Which way does a wall throw a pawn?"}]})
    st = DS.load_state(d)
    st["running"] = {"run": "r1"}
    return root, d, st


def through_result_errors(base):
    root, d, st = staged(base, "wait_code", 2, BUILT)
    res = {"run": "r1", "stage": 2, "outcome": "waiting_owner", "summary": "asked"}
    e = ql_errs(DS.result_errors(res, d, st, repo=root))
    check("waiting_owner, code exists, no quick_look: the launcher refuses it", len(e) == 1 and "knockback" in e[0], e)
    for ql, what in ((OFFER, "an offer"), (DECLINE, "a decline")):
        e = ql_errs(DS.result_errors(dict(res, quick_look=ql), d, st, repo=root))
        check("waiting_owner, code exists, %s: no quick_look refusal" % what, e == [], e)
    root, d, st = staged(base, "wait_nocode", 2, NONE_BUILT)
    e = ql_errs(DS.result_errors(res, d, st, repo=root))
    check("waiting_owner, nothing built: no quick_look owed", e == [], e)

    root, d, st = staged(base, "ret_code", 4, BUILT)
    ret = {"run": "r1", "stage": 4, "outcome": "return", "to": 2, "decision": "how far a wall throws",
           "question": "Should a wall throw a pawn its own length?"}
    e = DS.result_errors(ret, d, st, repo=root)
    check("return with a question, code exists, no quick_look: refused", len(ql_errs(e)) == 1, e)
    e = DS.result_errors(dict(ret, quick_look=OFFER), d, st, repo=root)
    check("return with a question and an offer: accepted", e == [], e)
    e = DS.result_errors({k: v for k, v in ret.items() if k != "question"}, d, st, repo=root)
    check("return with no question: no quick_look owed", e == [], e)
    root, d, st = staged(base, "ret_nocode", 4, NONE_BUILT)
    e = DS.result_errors(ret, d, st, repo=root)
    check("return with a question, nothing built: accepted", e == [], e)


def main():
    DS.owner_away = lambda: (False, "selftest: attended")   # the real presence must not move this test
    marks = real_marks()
    with tempfile.TemporaryDirectory() as base:
        units()
        through_result_errors(base)
    check("the real alarm and told files are untouched", real_marks() == marks, (marks, real_marks()))
    print("selftest_designer_quick_look: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
