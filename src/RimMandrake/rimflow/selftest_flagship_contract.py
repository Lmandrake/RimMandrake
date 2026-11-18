#!/usr/bin/env python3
"""selftest_flagship_contract.py — the scene contract's flagship paragraph says what designer.md and the showcase
validator (designer_stage.showcase_errors) already permit (RIMMANDRAKE_RECONCILE_FLAGSHIP_CONTRACT_WITH_DELEGATED_PICK).

LeaningScrub's coverage judge (rm-coverage-judge-1794823485, gap g12) read the contract's "Showcase 1 is the flagship he
picked ... (speaker owner) ... OWNER:<tsn>" as forbidding the recorded Evidence-for-Ask pick that designer.md allows and
the validator accepts. The behaviour is pinned by selftest_designer_stage.py (a delegated pick accepted, a pick that is
not marked delegated or is about another concept refused, root approval alone refused) and
selftest_concept_owner_certify.py (a --per-ruling event certifies nothing); this checks the prose a fresh reader gets.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def bullet(text, head):
    """The markdown bullet starting with `head`, up to the next bullet or blank line."""
    i = text.find(head)
    if i < 0:
        return ""
    m = re.search(r"\n(?:- |\n)", text[i:])
    return text[i:i + m.start()] if m else text[i:]


def main():
    import designer_stage as DS
    contract = open(os.path.join(HERE, "roles", "designer_scene_contract.md"), encoding="utf-8").read()
    para = " ".join(bullet(contract, "- **Showcase 1 is the flagship").split())
    check(bool(para), "the contract has its flagship paragraph")
    own, _, dele = para.partition("Evidence-for-Ask rule")
    check("OWNER:<tsn>" in own and "speaker `owner`" in own and '"flagship": "<this showcase id>"' in own,
          "his own pick: speaker owner, his OWNER:<tsn>, naming this showcase as the flagship")
    check(DS.EVIDENCE_FOR_ASK in para, "the delegated pick names the Evidence-for-Ask ruling %s" % DS.EVIDENCE_FOR_ASK)
    check("speaker `conductor`" in para and 'delegated: "evidence-for-ask"' in para and "CONDUCTOR:<tsn>" in para,
          "the delegated pick's record: speaker conductor, delegated evidence-for-ask, CONDUCTOR:<tsn>")
    check('"flagship": "<this showcase id>"' in dele, "the delegated decision names this showcase as the flagship too")
    check(re.search(r"`answers`.*`evidence_against` is empty", dele) is not None,
          "a delegated decision that answers an ask needs that ask's evidence_against empty (designer_stage.ask_waits)")
    check(DS.EFA_WHY in para, "the delegated call's why starts %r (so it reaches his digest)" % DS.EFA_WHY)
    check("root approval is not a pick" in para, "root approval alone is still not a pick")
    check(re.search(r"ask him at stage 2 only with concrete evidence against it", para) is not None,
          "an ask goes to him only with evidence against the obvious pick")
    check(re.search(r"first-touch certification stays his and is never delegated", para) is not None,
          "first-touch certification stays his")
    check("If he has picked none, ask at stage 2" not in para,
          "no bare 'ask at stage 2' that would re-ask a settled delegated flagship")
    print("%d check(s) failed" % len(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
