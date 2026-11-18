#!/usr/bin/env python3
"""Selftest of cleanse_plan.py (item RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID): the owner's cleanse plan checked by
stable census id. One row per answer, the order they are decided in, the prose that is never read, and the CLI's lines
and exit codes. Pure: temp fixtures only (no design/ folder needed), no git, agent or network."""
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []
N = [0]


def check(ok, msg):
    N[0] += 1
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


import cleanse_plan as CP          # noqa: E402  (red first: this import fails before the module exists)
import designer_cleanse as DC      # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_cleanse_plan_")
ROWS = [{"id": "body", "what": "the land", "fate": "land"},
        {"id": "lamp", "what": "a lamp that is not a fishery", "fate": "life"},
        {"id": "fishery", "what": "the fishery", "fate": "signature"},
        {"id": "heat", "what": "heat watch", "fate": "next_version"},
        {"id": "relic", "what": "old relic", "fate": "recommend_retire"}]


def cdir(root, mod):
    return os.path.join(root, "design", "concepts", mod, "cleanse")


def proposal(root, mod, rows=None):
    out = cdir(root, mod)
    os.makedirs(out, exist_ok=True)
    json.dump({"rows": rows if rows is not None else ROWS}, open(os.path.join(out, "census.json"), "w"), indent=1)
    open(os.path.join(out, "owner_pages.md"), "w").write("# %s\n" % mod)
    return out


def world(tag, plan_edit=None):
    """-> repo root with two proposals (Plain approved by digest, Marked awaiting a fresh review) and the plan."""
    root = os.path.join(TMP, tag)
    plain = proposal(root, "Plain")
    proposal(root, "Marked")
    proposal(root, "Excl")
    plan = {"schema": 1, "excluded": {"Excl": "not part of the cleanse"},
            "mods": {"Plain": {"approve": "digest", "approved_digest": DC.proposal_digest(plain), "marks": {}},
                     "Marked": {"approve": "fresh_review", "approved_digest": None,
                                "marks": {"lamp": "keep", "fishery": "keep", "heat": "next_version", "relic": "drop"}}}}
    if plan_edit:
        plan_edit(plan)
    p = os.path.join(root, CP.PLAN_REL)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(plan, open(p, "w"), indent=1)
    return root


def converge(root, mod, **kw):
    out = cdir(root, mod)
    doc = {"applyable": True, "open": [], "digest": DC.proposal_digest(out)}
    doc.update(kw)
    json.dump(doc, open(os.path.join(out, "converge.json"), "w"))


def refate(root, mod, rid, fate=None, new_id=None, drop=False):
    p = os.path.join(cdir(root, mod), "census.json")
    doc = json.load(open(p))
    rows = []
    for r in doc["rows"]:
        if r["id"] == rid:
            if drop:
                continue
            r = dict(r, fate=fate or r["fate"], id=new_id or r["id"])
        rows.append(r)
    doc["rows"] = rows
    json.dump(doc, open(p, "w"))


def ans(root, mod, plan=None):
    r = CP.plan_check(root, mod, plan)
    return r["answer"], r["ids"]


def cli(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = CP.main(list(argv))
    return code, buf.getvalue().splitlines()


def main():
    root = world("base")
    check(ans(root, "Plain") == ("APPROVED", []), "an unedited proposal approved by digest is APPROVED")
    check(ans(root, "Marked") == ("AWAITING_REVIEW", []), "a fresh_review mod with no converge.json is AWAITING_REVIEW")
    converge(root, "Marked")
    check(ans(root, "Marked") == ("APPROVED", []), "a converged review of the current bytes approves it")
    converge(root, "Marked", applyable=False)
    check(ans(root, "Marked")[0] == "AWAITING_REVIEW", "a review that is not applyable does not")
    converge(root, "Marked", open=[{"id": "x"}])
    check(ans(root, "Marked")[0] == "AWAITING_REVIEW", "a review with an open record does not")
    converge(root, "Marked", digest="0" * 64)
    check(ans(root, "Marked")[0] == "AWAITING_REVIEW", "a review of other bytes does not")
    check(ans(root, "Excl")[0] == "EXCLUDED", "an excluded mod is EXCLUDED")
    check(ans(root, "Nobody")[0] == "NOT_IN_PLAN", "a mod the plan does not name is NOT_IN_PLAN")

    root = world("edited")
    refate(root, "Plain", "body", "life")
    check(ans(root, "Plain")[0] == "CHANGED_SINCE_APPROVAL", "a digest-approved proposal edited after approval")

    # marks are by row id, never by row text
    root = world("gone")
    refate(root, "Marked", "fishery", drop=True)
    check(ans(root, "Marked") == ("MARK_ROW_MISSING", ["fishery"]), "a marked row removed is MARK_ROW_MISSING")
    root = world("renamed")
    refate(root, "Marked", "fishery", new_id="letter")
    check(ans(root, "Marked") == ("MARK_ROW_MISSING", ["fishery"]),
          "a marked row renamed is missing, though another row's text says fishery")
    root = world("flip")
    refate(root, "Marked", "lamp", "next_version")
    refate(root, "Marked", "relic", "land")
    converge(root, "Marked")
    check(ans(root, "Marked") == ("MARK_NOT_FOLDED", ["lamp", "relic"]),
          "two marks unfolded are MARK_NOT_FOLDED, sorted, even under a current review")
    for fate in DC.KEPT:
        root = world("kept_" + fate)
        refate(root, "Marked", "lamp", fate)
        converge(root, "Marked")
        check(ans(root, "Marked")[0] == "APPROVED", "keep is satisfied by kept fate %s" % fate)
    root = world("dup")
    p = os.path.join(cdir(root, "Marked"), "census.json")
    doc = json.load(open(p))
    doc["rows"].append({"id": "lamp", "what": "a second lamp row", "fate": "recommend_retire"})
    json.dump(doc, open(p, "w"))
    check(ans(root, "Marked") == ("MARK_NOT_FOLDED", ["lamp"]), "every row under a marked id must hold the mark")

    # his prose is never read
    root = world("prose")
    converge(root, "Marked")
    mp = os.path.join(cdir(root, "Marked"), "owner_marks.md")
    open(mp, "w").write("**id** | **mark**\n--- | ---\nlamp | DROP\nfishery | 0.2.0\n")
    check(ans(root, "Marked")[0] == "APPROVED", "a marks file contradicting the plan changes nothing")
    if os.geteuid() != 0:
        os.chmod(mp, 0)
        check(ans(root, "Marked")[0] == "APPROVED", "an unreadable marks file changes nothing")
        os.chmod(mp, 0o644)

    # could not look, missing, malformed: four different answers
    if os.geteuid() != 0:
        for name, mod in (("census.json", "Plain"), ("owner_pages.md", "Plain"), ("converge.json", "Marked")):
            root = world("noread_" + name)
            converge(root, "Marked")
            p = os.path.join(cdir(root, mod), name)
            os.chmod(p, 0)
            r = CP.plan_check(root, mod)
            check(r["answer"] == "COULD_NOT_LOOK" and r["path"].endswith(name), "%s unreadable is COULD_NOT_LOOK naming it" % name)
        root = world("noread_plan")
        os.chmod(os.path.join(root, CP.PLAN_REL), 0)
        r = CP.plan_check(root, "Plain")
        check(r["answer"] == "COULD_NOT_LOOK" and "CLEANSE_PLAN_OWNER" in r["path"], "an unreadable plan is COULD_NOT_LOOK")
        code, lines = cli("check", "--all", "--repo", root)
        check(code == 4 and len(lines) == 1 and " COULD_NOT_LOOK " in lines[0], "--all on an unreadable plan exits 4")
        root = world("noread_dir")
        converge(root, "Marked")
        os.chmod(cdir(root, "Marked"), 0)
        r = CP.plan_check(root, "Marked")
        check(r["answer"] == "COULD_NOT_LOOK", "a cleanse folder that denies search is COULD_NOT_LOOK, never missing rows")
        os.chmod(cdir(root, "Marked"), 0o755)
        priv = os.path.join(TMP, "priv")
        os.makedirs(priv)
        shutil.copy(os.path.join(root, CP.PLAN_REL), os.path.join(priv, "plan.json"))
        os.chmod(priv, 0)
        r = CP.plan_check(root, "Plain", os.path.join(priv, "plan.json"))
        check(r["answer"] == "COULD_NOT_LOOK" and r["path"].endswith("plan.json"),
              "a plan behind a folder that denies search is COULD_NOT_LOOK, never PLAN_MISSING")
        os.chmod(priv, 0o755)
    root = world("badcensus")
    open(os.path.join(cdir(root, "Plain"), "census.json"), "w").write("{not json")
    check(ans(root, "Plain")[0] == "COULD_NOT_LOOK", "a census that is not JSON is COULD_NOT_LOOK, not a verdict")
    root = world("nocensus")
    os.remove(os.path.join(cdir(root, "Marked"), "census.json"))
    check(ans(root, "Marked") == ("MARK_ROW_MISSING", ["fishery", "heat", "lamp", "relic"]),
          "no census at all leaves every marked row missing")
    root = world("noplan")
    os.remove(os.path.join(root, CP.PLAN_REL))
    check(ans(root, "Plain")[0] == "PLAN_MISSING", "no plan file is PLAN_MISSING")
    code, lines = cli("check", "--all", "--repo", root)
    check(code == 1 and len(lines) == 1 and " PLAN_MISSING" in lines[0], "--all with no plan says PLAN_MISSING, exit 1")
    for tag, edit in (("mark", lambda d: d["mods"]["Marked"]["marks"].update(lamp="maybe")),
                      ("approve", lambda d: d["mods"]["Plain"].update(approve="sure")),
                      ("listmark", lambda d: d["mods"]["Marked"]["marks"].update(lamp=[])),
                      ("objmark", lambda d: d["mods"]["Marked"]["marks"].update(lamp={})),
                      ("nomods", lambda d: d.update(mods={})),
                      ("nodigest", lambda d: d["mods"]["Plain"].update(approved_digest=None)),
                      ("othermod", lambda d: d["mods"].update(Other={"approve": "digest", "approved_digest": "x",
                                                                     "marks": {"a": "perhaps"}}))):
        root = world("bad_" + tag, edit)
        check(ans(root, "Plain")[0] == "PLAN_MALFORMED", "a plan with a bad %s is PLAN_MALFORMED" % tag)
    open(os.path.join(root, CP.PLAN_REL), "w").write("{not json")
    check(ans(root, "Plain")[0] == "PLAN_MALFORMED", "a plan that is not JSON is PLAN_MALFORMED")
    code, lines = cli("check", "--all", "--repo", root)
    check(code == 1 and len(lines) == 1 and " PLAN_MALFORMED" in lines[0], "--all on a malformed plan says so, exit 1")
    root = world("emptyplan", lambda d: d.update(mods={}))
    code, lines = cli("check", "--all", "--repo", root)
    check(code == 1 and len(lines) == 1 and " PLAN_MALFORMED" in lines[0], "--all on a plan naming no mod is not silent")

    # order: reads before plan, plan before exclusion, exclusion before marks, marks before approval
    root = world("order")
    os.remove(os.path.join(root, CP.PLAN_REL))
    open(os.path.join(cdir(root, "Plain"), "census.json"), "w").write("[]")
    check(ans(root, "Plain")[0] == "COULD_NOT_LOOK", "a census without rows outranks a missing plan")
    root = world("order2", lambda d: d["mods"].update(Excl={"approve": "digest", "approved_digest": "x", "marks": {}}))
    check(ans(root, "Excl")[0] == "EXCLUDED", "exclusion outranks a plan entry")
    root = world("order3", lambda d: d["mods"]["Plain"]["marks"].update(body="drop"))
    refate(root, "Plain", "relic", "land")
    check(ans(root, "Plain") == ("MARK_NOT_FOLDED", ["body"]), "an unfolded mark outranks a changed digest")

    # --plan names another file; the CLI's lines and exits
    root = world("alt")
    alt = os.path.join(TMP, "alt.json")
    shutil.move(os.path.join(root, CP.PLAN_REL), alt)
    check(ans(root, "Plain")[0] == "PLAN_MISSING" and CP.plan_check(root, "Plain", alt)["answer"] == "APPROVED",
          "--plan reads the named file")
    code, lines = cli("check", "Plain", "--repo", root, "--plan", alt)
    check(code == 0 and lines == ["PLAN Plain APPROVED"], "one APPROVED mod exits 0 with one line")
    root = world("cli")
    refate(root, "Marked", "fishery", drop=True)
    code, lines = cli("check", "--all", "--repo", root)
    check(code == 1 and lines == ["PLAN Marked MARK_ROW_MISSING fishery", "PLAN Plain APPROVED"],
          "--all prints one line per planned mod, ids named, exit 1")
    converge(world("cli2"), "Marked")
    code, lines = cli("check", "--all", "--repo", os.path.join(TMP, "cli2"))
    check(code == 0 and len(lines) == 2, "--all all APPROVED exits 0")

    shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_cleanse_plan: %d checks, %d failed" % (N[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
