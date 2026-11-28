#!/usr/bin/env python3
"""Acceptance cases for RIMMANDRAKE_LET_CLEANSE_GATE_PASS_CONDUCTOR_ACT_ROLES_ALLOW (Mandrake's card 2026-11-28 2:17 AM PST,
"Change the code (Recommended)"): the role files say the Conductor may retire or apply a cleanse proposal as its
recorded act; cleanse_plan.plan_check, and so designer_cleanse._gate, accepted only the owner's plan.

Contract: `design/concepts/CLEANSE_CONDUCTOR_ACTS.json` = {"schema": 1, "mods": {<Mod>: {"approved_digest": <str>,
"act": <ledger item id>}}}. plan_check(repo, mod) answers APPROVED for a mod whose owner's-plan answer is NOT_IN_PLAN,
PLAN_MISSING, CHANGED_SINCE_APPROVAL or AWAITING_REVIEW when the acts file names the mod, its approved_digest equals the
proposal's current digest, and `infrastructure/state/ledger/events/OWNER.jsonl` holds an event on item `act` whose
perRuling is RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS. His plan still wins where it speaks: EXCLUDED,
MARK_ROW_MISSING, MARK_NOT_FOLDED, PLAN_MALFORMED and COULD_NOT_LOOK are never turned into APPROVED. A named act with no
such ledger event answers CONDUCTOR_ACT_UNRECORDED; a stale digest answers CHANGED_SINCE_APPROVAL; an acts file or
ledger shard that exists but cannot be read or parsed answers COULD_NOT_LOOK. No acts file leaves every answer as it was.

Run from the repo root:  python3 design/specs/2026-11-28-cleanse-gate-conductor-act/case_conductor_act.py
Prints each wrong case, then `cases N wrong W`; exit 1 when any case is wrong."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import cleanse_plan as CP  # noqa: E402
import designer_cleanse as DC  # noqa: E402

RULING = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"
ACTS_REL = os.path.join("design", "concepts", "CLEANSE_CONDUCTOR_ACTS.json")
LEDGER_REL = os.path.join("infrastructure", "state", "ledger", "events", "OWNER.jsonl")
ROWS = [{"id": "body", "what": "the land", "fate": "land"}, {"id": "relic", "what": "old relic", "fate": "recommend_retire"}]
TMP = tempfile.mkdtemp(prefix="case_conductor_act_")
WRONG, N = [], [0]


def case(name, got, want):
    N[0] += 1
    if got != want:
        WRONG.append(name)
        print("WRONG %s: got %s, want %s" % (name, got, want))


def proposal(root, mod):
    out = os.path.join(root, "design", "concepts", mod, "cleanse")
    os.makedirs(out, exist_ok=True)
    json.dump({"rows": ROWS}, open(os.path.join(out, "census.json"), "w"))
    open(os.path.join(out, "owner_pages.md"), "w").write("# %s\n" % mod)
    return out


def world(tag, plan="default", acts=None, ledger=None):
    root = os.path.join(TMP, tag)
    for m in ("Held", "Fresh", "Marked", "Excl"):
        proposal(root, m)
    if plan == "default":
        plan = {"schema": 1, "excluded": {"Excl": "not part of the cleanse"},
                "mods": {"Fresh": {"approve": "fresh_review", "approved_digest": None, "marks": {}},
                         "Marked": {"approve": "fresh_review", "approved_digest": None, "marks": {"relic": "keep"}}}}
    if plan is not None:
        os.makedirs(os.path.dirname(os.path.join(root, CP.PLAN_REL)), exist_ok=True)
        json.dump(plan, open(os.path.join(root, CP.PLAN_REL), "w"))
    if acts is not None:
        p = os.path.join(root, ACTS_REL)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(acts if isinstance(acts, str) else json.dumps(acts))
    if ledger is not None:
        p = os.path.join(root, LEDGER_REL)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(ledger if isinstance(ledger, str) else "".join(json.dumps(e) + "\n" for e in ledger))
    return root


def digest(root, mod):
    return DC.proposal_digest(os.path.join(root, "design", "concepts", mod, "cleanse"))


def ans(root, mod):
    return CP.plan_check(root, mod)["answer"]


ACT = "RIMMANDRAKE_RETIRE_HELD_RELIC_CONDUCTOR_CALL"
GOOD_EV = [{"seat": "OWNER", "event": "note", "id": ACT, "text": "Conductor call", "perRuling": RULING, "why": "delegated"}]


def acts_for(root, *mods, act=ACT, stale=False):
    return {"schema": 1, "mods": {m: {"approved_digest": "stale" if stale else digest(root, m), "act": act} for m in mods}}


def main():
    # no acts file: every answer as before
    r = world("none")
    case("no acts file, mod not in plan", ans(r, "Held"), "NOT_IN_PLAN")
    case("no acts file, fresh review", ans(r, "Fresh"), "AWAITING_REVIEW")

    # a recorded act approves a mod outside his plan, and one awaiting review
    r = world("good", ledger=GOOD_EV)
    os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
    json.dump(acts_for(r, "Held", "Fresh"), open(os.path.join(r, ACTS_REL), "w"))
    case("recorded act, mod not in plan", ans(r, "Held"), "APPROVED")
    case("recorded act, plan awaiting review", ans(r, "Fresh"), "APPROVED")

    # the whole door: a real applyable proposal (the designer selftest's fixture), no owner's plan, a recorded act
    import selftest_designer_cleanse as SD
    repo, concept, out = SD.approved(plan=False)
    case("_gate with no plan and no act refuses NOT_APPROVED", (DC._gate(repo, "Demo")[0] or {}).get("cause"), "NOT_APPROVED")
    ap = os.path.join(repo, ACTS_REL)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    json.dump({"schema": 1, "mods": {"Demo": {"approved_digest": DC.proposal_digest(out), "act": ACT}}}, open(ap, "w"))
    lp = os.path.join(repo, LEDGER_REL)
    os.makedirs(os.path.dirname(lp), exist_ok=True)
    open(lp, "w").write(json.dumps(dict(GOOD_EV[0])) + "\n")
    case("_gate passes a recorded Conductor act", DC._gate(repo, "Demo")[0], None)
    case("apply_write writes on a recorded Conductor act", DC.apply_write(repo, "Demo")["answer"], "WROTE")

    # no plan file at all, act recorded
    r = world("noplan", plan=None, ledger=GOOD_EV)
    os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
    json.dump(acts_for(r, "Held"), open(os.path.join(r, ACTS_REL), "w"))
    case("recorded act, plan missing", ans(r, "Held"), "APPROVED")

    # his plan wins where it speaks
    r = world("his", ledger=GOOD_EV)
    os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
    json.dump(acts_for(r, "Excl", "Marked"), open(os.path.join(r, ACTS_REL), "w"))
    case("his exclusion stands", ans(r, "Excl"), "EXCLUDED")
    case("his mark not folded stands", ans(r, "Marked"), "MARK_NOT_FOLDED")

    # an act named but not on the ledger; an act under another ruling; a stale digest
    for tag, ev in (("unrecorded", []), ("otherruling", [dict(GOOD_EV[0], perRuling="RIMMANDRAKE_SOME_OTHER_RULING")]),
                    ("otheritem", [dict(GOOD_EV[0], id="RIMMANDRAKE_SOMETHING_ELSE_ENTIRELY")])):
        r = world(tag, ledger=ev)
        os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
        json.dump(acts_for(r, "Held"), open(os.path.join(r, ACTS_REL), "w"))
        case("act %s" % tag, ans(r, "Held"), "CONDUCTOR_ACT_UNRECORDED")
    r = world("noledger")
    os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
    json.dump(acts_for(r, "Held"), open(os.path.join(r, ACTS_REL), "w"))
    case("act with no ledger shard", ans(r, "Held"), "CONDUCTOR_ACT_UNRECORDED")
    r = world("stale", ledger=GOOD_EV)
    os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
    json.dump(acts_for(r, "Held", stale=True), open(os.path.join(r, ACTS_REL), "w"))
    case("stale digest", ans(r, "Held"), "CHANGED_SINCE_APPROVAL")
    r = world("other_mod_only", ledger=GOOD_EV)
    os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
    json.dump(acts_for(r, "Fresh"), open(os.path.join(r, ACTS_REL), "w"))
    case("acts file that does not name the mod", ans(r, "Held"), "NOT_IN_PLAN")

    # could not look is never a verdict
    case("acts file not JSON", ans(world("badjson", acts="{", ledger=GOOD_EV), "Held"), "COULD_NOT_LOOK")
    case("acts file wrong shape", ans(world("badshape", acts={"mods": {"Held": {"act": 3}}}, ledger=GOOD_EV), "Held"),
         "COULD_NOT_LOOK")
    r = world("badledger", ledger="{not json\n")
    os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
    json.dump(acts_for(r, "Held"), open(os.path.join(r, ACTS_REL), "w"))
    case("ledger shard not JSON", ans(r, "Held"), "COULD_NOT_LOOK")
    if os.geteuid() != 0:
        r = world("unreadable", ledger=GOOD_EV)
        os.makedirs(os.path.dirname(os.path.join(r, ACTS_REL)), exist_ok=True)
        json.dump(acts_for(r, "Held"), open(os.path.join(r, ACTS_REL), "w"))
        os.chmod(os.path.join(r, ACTS_REL), 0)
        case("acts file unreadable", ans(r, "Held"), "COULD_NOT_LOOK")
        os.chmod(os.path.join(r, ACTS_REL), 0o644)

    shutil.rmtree(TMP, ignore_errors=True)
    print("cases %d wrong %d" % (N[0], len(WRONG)))
    return 1 if WRONG else 0


if __name__ == "__main__":
    sys.exit(main())
