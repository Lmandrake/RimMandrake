#!/usr/bin/env python3
"""The owner's Designer Cleanse plan, checked by stable census id (item RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID).

The owner approved the 23 cleanse proposals as THE PLAN (2026-11-17 9:04 PM PST); his five marks on Abyss and TheRot
live in the machine-readable plan `design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.json` as {census row id: mark}. This
module answers "may this mod's proposal be applied?" from that file and the proposal's census.json / converge.json
alone. It never reads owner_marks.md or any markdown: parsing his table failed in every review round.

    plan_check(repo, mod, plan=None) -> {"answer", "mod", "ids", "path"}

Answers, in the order they are decided (reads, plan, exclusion, marks, approval):
    COULD_NOT_LOOK          the plan, census.json, converge.json or a digested proposal file exists but cannot be read
    PLAN_MISSING            no plan file
    PLAN_MALFORMED          not JSON, a wrong shape, an unknown mark word or an unknown approve kind
    EXCLUDED                the plan excludes the mod (Pyrelands)
    NOT_IN_PLAN             the plan has no entry for the mod
    MARK_ROW_MISSING        ids: a marked id has no census row (rows match by `id` only, never by text)
    MARK_NOT_FOLDED         ids: a marked row's fate is outside the mark's class
    CHANGED_SINCE_APPROVAL  approve "digest" and the proposal's digest is not the approved one
    AWAITING_REVIEW         approve "fresh_review" and converge.json is not (applyable, open [], the current digest)
    APPROVED

CLI:  cleanse_plan.py check (<Mod> | --all) [--repo R] [--plan P]
      one `PLAN <Mod> <ANSWER> [ids|path]` line per mod; exit 0 all APPROVED, 4 any COULD_NOT_LOOK, else 1.
Selftest: selftest_cleanse_plan.py. Acceptance: design/specs/2026-11-17-cleanse-apply-split/tickets/case_owner_marks.py."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import designer_cleanse as DC  # noqa: E402

PLAN_REL = os.path.join("design", "concepts", "CLEANSE_PLAN_OWNER_2026-11-17.json")
MARK_CLASS = {"keep": tuple(DC.KEPT), "next_version": ("next_version",), "drop": ("recommend_retire",)}
APPROVE = ("digest", "fresh_review")


class _Unreadable(Exception):
    pass


def _exists(path):
    """-> True | False; _Unreadable(path) when the answer itself cannot be had (a parent that denies search, say):
    os.path.lexists would call that "absent"."""
    try:
        os.lstat(path)
        return True
    except FileNotFoundError:
        return False
    except OSError:
        raise _Unreadable(path)


def _load(path):
    """-> (True, parsed JSON) | (False, None) when absent; _Unreadable(path) when present but unreadable; ValueError
    when it reads but is not JSON."""
    if not _exists(path):
        return False, None
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        raise _Unreadable(path)
    return True, json.loads(text)


def _plan_shape(doc):
    """-> None when the plan is well formed, else why not. Every mod is checked: a malformed plan is malformed."""
    if not isinstance(doc, dict) or not isinstance(doc.get("mods"), dict) or not doc["mods"]:
        return "no mods object, or it names no mod"
    if not isinstance(doc.get("excluded", {}), dict):
        return "excluded is not an object"
    for mod, ent in doc["mods"].items():
        if not isinstance(ent, dict):
            return "%s: entry is not an object" % mod
        if ent.get("approve") not in APPROVE:
            return "%s: unknown approve kind %r" % (mod, ent.get("approve"))
        if ent["approve"] == "digest" and not isinstance(ent.get("approved_digest"), str):
            return "%s: approve digest without approved_digest" % mod
        marks = ent.get("marks", {})
        if not isinstance(marks, dict):
            return "%s: marks is not an object" % mod
        for rid, word in marks.items():
            if not isinstance(word, str) or word not in MARK_CLASS:
                return "%s: unknown mark %r on %s" % (mod, word, rid)
    return None


def _out(mod, answer, ids=(), path=""):
    return {"answer": answer, "mod": mod, "ids": sorted(ids), "path": path}


def plan_check(repo, mod, plan=None):
    repo = os.path.abspath(repo)
    plan_path = os.path.join(repo, plan) if plan else os.path.join(repo, PLAN_REL)
    out = os.path.join(repo, "design", "concepts", mod, "cleanse")
    # reads first: a file that is there but cannot be read is "could not look", never a verdict
    try:
        have_plan, doc = _load(plan_path)
    except _Unreadable:
        return _out(mod, "COULD_NOT_LOOK", path=plan_path)
    except ValueError:
        have_plan, doc = True, ValueError
    loaded = {}
    for name in ("census.json", "converge.json"):
        p = os.path.join(out, name)
        try:
            loaded[name] = _load(p)
        except (_Unreadable, ValueError):
            return _out(mod, "COULD_NOT_LOOK", path=p)
    for name in DC.FILES:  # the digest's inputs: an unreadable one would read as "changed", which it is not
        p = os.path.join(out, name)
        try:
            if _exists(p) and not os.access(p, os.R_OK):
                return _out(mod, "COULD_NOT_LOOK", path=p)
        except _Unreadable:
            return _out(mod, "COULD_NOT_LOOK", path=p)
    have_census, census = loaded["census.json"]
    if have_census and not (isinstance(census, dict) and isinstance(census.get("rows"), list)):
        return _out(mod, "COULD_NOT_LOOK", path=os.path.join(out, "census.json"))
    # the plan
    if not have_plan:
        return _out(mod, "PLAN_MISSING", path=plan_path)
    if doc is ValueError or _plan_shape(doc):
        return _out(mod, "PLAN_MALFORMED", path=plan_path)
    if mod in doc.get("excluded", {}):
        return _out(mod, "EXCLUDED")
    ent = doc["mods"].get(mod)
    if ent is None:
        return _out(mod, "NOT_IN_PLAN")
    # his marks, by row id
    fates = {}
    for row in (census or {}).get("rows", []):
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            fates.setdefault(row["id"], []).append(row.get("fate"))
    marks = ent.get("marks", {})
    missing = [rid for rid in marks if rid not in fates]
    if missing:
        return _out(mod, "MARK_ROW_MISSING", missing)
    unfolded = [rid for rid, word in marks.items() if any(f not in MARK_CLASS[word] for f in fates[rid])]
    if unfolded:
        return _out(mod, "MARK_NOT_FOLDED", unfolded)
    # approval
    digest = DC.proposal_digest(out)
    if ent["approve"] == "digest":
        return _out(mod, "APPROVED" if digest == ent["approved_digest"] else "CHANGED_SINCE_APPROVAL")
    _, cv = loaded["converge.json"]
    ok = isinstance(cv, dict) and cv.get("applyable") is True and cv.get("open") == [] and cv.get("digest") == digest
    return _out(mod, "APPROVED" if ok else "AWAITING_REVIEW")


def _line(r):
    tail = ",".join(r["ids"]) or r["path"]
    return ("PLAN %s %s %s" % (r["mod"], r["answer"], tail)).rstrip()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cleanse_plan.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="may each mod's cleanse proposal be applied under the owner's plan")
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("mod", nargs="?")
    g.add_argument("--all", action="store_true", help="every mod the plan names")
    c.add_argument("--repo", default=ROOT)
    c.add_argument("--plan", help="plan file (default %s under the repo)" % PLAN_REL)
    a = ap.parse_args(argv)
    plan = os.path.abspath(a.plan) if a.plan else None
    if a.all:
        plan_path = plan or os.path.join(os.path.abspath(a.repo), PLAN_REL)
        try:
            have, doc = _load(plan_path)
            bad = None if not have else _plan_shape(doc)
        except _Unreadable:
            have, doc, bad = True, None, "unreadable"
        except ValueError:
            have, doc, bad = True, None, "not JSON"
        if not have or bad:
            # no mod list to walk: one line for the plan itself
            answer = "PLAN_MISSING" if not have else "COULD_NOT_LOOK" if bad == "unreadable" else "PLAN_MALFORMED"
            results = [_out("*", answer, path=plan_path)]
        else:
            results = [plan_check(a.repo, m, plan) for m in sorted(doc["mods"])]
    else:
        results = [plan_check(a.repo, a.mod, plan)]
    for r in results:
        print(_line(r))
    answers = [r["answer"] for r in results]
    if "COULD_NOT_LOOK" in answers:
        return 4
    return 0 if answers and all(x == "APPROVED" for x in answers) else 1


if __name__ == "__main__":
    sys.exit(main())
