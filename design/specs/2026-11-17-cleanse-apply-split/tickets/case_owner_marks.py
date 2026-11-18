#!/usr/bin/env python3
"""Failing acceptance cases for ticket RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID (split from
RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL; review-3 findings 2 and 3).

Contract read (the ticket's ## spec): `src/RimMandrake/rimflow/cleanse_plan.py`, `plan_check(repo, mod, plan=None)` ->
dict with `answer` one of APPROVED / EXCLUDED / NOT_IN_PLAN / PLAN_MISSING / PLAN_MALFORMED / MARK_ROW_MISSING /
MARK_NOT_FOLDED / CHANGED_SINCE_APPROVAL / AWAITING_REVIEW / COULD_NOT_LOOK, `ids` (sorted marked ids at fault) and
`path`. It reads the plan file `design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.json` (marks by census row id, approval
by proposal digest) and the proposal's census.json / converge.json; it never reads owner_marks.md or any prose.
CLI `cleanse_plan.py check (<Mod> | --all) [--repo R] [--plan P]`: one line per mod `PLAN <Mod> <ANSWER> [...]`;
exit 0 all APPROVED, 4 any COULD_NOT_LOOK, else 1.

Input kinds read: the live repo (21 unedited approved, Abyss and TheRot awaiting their fresh review); Pyrelands; a
proposal copied under a name the plan does not hold; TheRot with its marks file deleted, with pleasure_brew dropped,
with a converged current review; Abyss with the fishery row gone, renamed to a non-fishery id, with marks flipped, with
a stale and a current review; a marks file that contradicts the plan, one with bold headers and no outer pipes, and an
unreadable one; an unreadable plan, census and converge; a missing plan; a malformed plan; a proposal edited after
approval; and the selftest run from a copy holding only src/RimMandrake/{rimflow,Utils,contracts}.
Run from the repo root:  python3 design/specs/2026-11-17-cleanse-apply-split/tickets/case_owner_marks.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
RF = os.path.join(ROOT, "src", "RimMandrake", "rimflow")
sys.path.insert(0, RF)
import designer_cleanse as DC  # noqa: E402

PLAN_REL = os.path.join("design", "concepts", "CLEANSE_PLAN_OWNER_2026-11-17.json")
TMP = tempfile.mkdtemp(prefix="case_owner_marks_")
WRONG = []
READ = [0]
EXIT = {"APPROVED": 0, "COULD_NOT_LOOK": 4}


def case(name, ok, why=""):
    READ[0] += 1
    if not ok:
        WRONG.append(name)
        print("WRONG %s: %s" % (name, why))


def module():
    try:
        import cleanse_plan
        return cleanse_plan
    except ImportError as e:
        return str(e)


def check(root, mod, plan=None):
    m = module()
    if isinstance(m, str) or not hasattr(m, "plan_check"):
        return None, "no cleanse_plan.plan_check (%s)" % m
    try:
        r = m.plan_check(root, mod, plan) if plan else m.plan_check(root, mod)
    except Exception as e:
        return None, "plan_check raised %s: %s" % (type(e).__name__, e)
    return (r, "") if isinstance(r, dict) and r.get("answer") else (None, "plan_check returned %r" % (r,))


def cli(root, *args):
    p = subprocess.run([sys.executable, os.path.join(RF, "cleanse_plan.py"), "check"] + list(args) + ["--repo", root],
                       capture_output=True, text=True, timeout=120)
    return p.returncode, [x for x in p.stdout.splitlines() if x.startswith("PLAN ")], p.stderr.strip()[-200:]


def expect(name, root, mod, answer, ids=None, path_has=None, plan=None):
    r, why = check(root, mod, plan)
    if r is None:
        case(name + " (seam)", False, why)
    else:
        got = (r.get("answer"), sorted(r.get("ids") or []) if ids is not None else None)
        case(name + " (seam)", got == (answer, sorted(ids) if ids is not None else None), "got %r want %r" % (got, (answer, ids)))
        if path_has:
            case(name + " (path)", path_has in str(r.get("path") or ""), "path %r lacks %r" % (r.get("path"), path_has))
    code, lines, err = cli(root, mod, *(["--plan", plan] if plan else []))
    want = "PLAN %s %s" % (mod, answer)
    ok = len(lines) == 1 and lines[0].startswith(want) and code == EXIT.get(answer, 1)
    if ok and ids:
        ok = all(i in lines[0] for i in ids)
    case(name + " (cli)", ok, "exit %s lines %r, want %r exit %s %s" % (code, lines[:2], want, EXIT.get(answer, 1), err))
    return r


def fixture(tag, *mods):
    root = os.path.join(TMP, tag)
    for m in mods:
        shutil.copytree(os.path.join(ROOT, "design", "concepts", m), os.path.join(root, "design", "concepts", m))
    os.makedirs(os.path.dirname(os.path.join(root, PLAN_REL)), exist_ok=True)
    shutil.copy(os.path.join(ROOT, PLAN_REL), os.path.join(root, PLAN_REL))
    return root


def cdir(root, mod):
    return os.path.join(root, "design", "concepts", mod, "cleanse")


def edit_rows(root, mod, fn):
    p = os.path.join(cdir(root, mod), "census.json")
    doc = json.load(open(p, encoding="utf-8"))
    doc["rows"] = fn(doc["rows"])
    json.dump(doc, open(p, "w", encoding="utf-8"), indent=1)


def refate(rid, fate):
    return lambda rows: [dict(x, fate=fate) if x.get("id") == rid else x for x in rows]


def converge(root, mod, digest=None, applyable=True):
    out = cdir(root, mod)
    json.dump({"mod": mod, "applyable": applyable, "open": [], "digest": digest or DC.proposal_digest(out)},
              open(os.path.join(out, "converge.json"), "w"), indent=1)


def main():
    # the live repo, read in place (read only)
    code, lines, err = cli(ROOT, "--all")
    got = {ln.split()[1]: ln.split()[2] for ln in lines if len(ln.split()) >= 3}
    want = {m: "APPROVED" for m in json.load(open(os.path.join(ROOT, PLAN_REL)))["mods"]}
    want.update(Abyss="AWAITING_REVIEW", TheRot="AWAITING_REVIEW")
    case("live --all", got == want and code == 1, "exit %s; differs at %s %s" % (
        code, sorted(k for k in set(got) | set(want) if got.get(k) != want.get(k))[:6], err))
    case("live --all names 23", len(got) == 23, "%d mods read" % len(got))

    root = fixture("pyre")
    os.makedirs(os.path.join(root, "design", "concepts", "Pyrelands", "cleanse"))
    expect("Pyrelands", root, "Pyrelands", "EXCLUDED")

    # finding 2: membership is not approval; a copy under another name is not in the plan
    root = fixture("copy", "BlueDesert")
    os.rename(os.path.join(root, "design", "concepts", "BlueDesert"), os.path.join(root, "design", "concepts", "BlueDesertCopy"))
    expect("copy under another name", root, "BlueDesertCopy", "NOT_IN_PLAN")
    root = fixture("edited", "BlueDesert")
    edit_rows(root, "BlueDesert", lambda rows: rows[:-1])
    expect("approved proposal edited after approval", root, "BlueDesert", "CHANGED_SINCE_APPROVAL")
    expect("unedited approved proposal", fixture("plain", "BlueDesert"), "BlueDesert", "APPROVED")

    # finding 2: TheRot without its marks file still owes pleasure_brew
    root = fixture("rot_nomarks", "TheRot")
    os.remove(os.path.join(cdir(root, "TheRot"), "owner_marks.md"))
    expect("TheRot, marks file deleted", root, "TheRot", "AWAITING_REVIEW")
    edit_rows(root, "TheRot", refate("pleasure_brew", "recommend_retire"))
    expect("TheRot, pleasure_brew dropped, no marks file", root, "TheRot", "MARK_NOT_FOLDED", ["pleasure_brew"])
    converge(root, "TheRot")
    expect("TheRot, dropped brew, current review", root, "TheRot", "MARK_NOT_FOLDED", ["pleasure_brew"])
    root = fixture("rot_ok", "TheRot")
    converge(root, "TheRot")
    expect("TheRot, current converged review", root, "TheRot", "APPROVED")
    converge(root, "TheRot", applyable=False)
    expect("TheRot, current review not converged", root, "TheRot", "AWAITING_REVIEW")
    converge(root, "TheRot", digest="0" * 64)
    expect("TheRot, review of other bytes", root, "TheRot", "AWAITING_REVIEW")

    # finding 3: the fishery is the row id abyss_fishery, never a word in a row's text
    root = fixture("abyss_gone", "Abyss")
    edit_rows(root, "Abyss", lambda rows: [x for x in rows if x.get("id") != "abyss_fishery"])
    expect("Abyss, fishery row gone", root, "Abyss", "MARK_ROW_MISSING", ["abyss_fishery"])
    root = fixture("abyss_letter", "Abyss")
    edit_rows(root, "Abyss", lambda rows: [dict(x, id="warning_letter", what="a warning letter that is not a fishery")
                                           if x.get("id") == "abyss_fishery" else x for x in rows])
    expect("Abyss, fishery renamed to a letter", root, "Abyss", "MARK_ROW_MISSING", ["abyss_fishery"])
    root = fixture("abyss_flip", "Abyss")
    edit_rows(root, "Abyss", refate("fold_lamp", "next_version"))
    edit_rows(root, "Abyss", refate("heat_observation", "land"))
    expect("Abyss, two marks unfolded", root, "Abyss", "MARK_NOT_FOLDED", ["fold_lamp", "heat_observation"])
    for fate in DC.KEPT:  # any kept fate satisfies a 0.1.0 mark
        root = fixture("abyss_kept_" + fate, "Abyss")
        edit_rows(root, "Abyss", refate("vine_turning", fate))
        converge(root, "Abyss")
        expect("Abyss, vine_turning kept as %s, current review" % fate, root, "Abyss", "APPROVED")
    root = fixture("abyss_review", "Abyss")
    converge(root, "Abyss", digest="f" * 64)
    expect("Abyss, stale review", root, "Abyss", "AWAITING_REVIEW")

    # his prose is never parsed: a contradicting, a reformatted and an unreadable marks file change nothing
    root = fixture("abyss_prose", "Abyss")
    converge(root, "Abyss")
    mp = os.path.join(cdir(root, "Abyss"), "owner_marks.md")
    open(mp, "w").write("**mod** | **id** | **his mark**\n--- | --- | ---\nAbyss | fold_lamp | 0.2.0\nAbyss | abyss_fishery | DROP\n")
    expect("Abyss, marks file contradicts the plan", root, "Abyss", "APPROVED")
    if os.geteuid() != 0:
        os.chmod(mp, 0)
        expect("Abyss, marks file unreadable", root, "Abyss", "APPROVED")
        os.chmod(mp, 0o644)

    # could not look, missing, malformed: each its own answer
    if os.geteuid() != 0:
        root = fixture("noread_census", "BlueDesert")
        os.chmod(os.path.join(cdir(root, "BlueDesert"), "census.json"), 0)
        expect("census unreadable", root, "BlueDesert", "COULD_NOT_LOOK", path_has="census.json")
        root = fixture("noread_converge", "Abyss")
        converge(root, "Abyss")
        os.chmod(os.path.join(cdir(root, "Abyss"), "converge.json"), 0)
        expect("converge unreadable", root, "Abyss", "COULD_NOT_LOOK", path_has="converge.json")
        root = fixture("noread_plan", "BlueDesert")
        os.chmod(os.path.join(root, PLAN_REL), 0)
        expect("plan unreadable", root, "BlueDesert", "COULD_NOT_LOOK", path_has="CLEANSE_PLAN_OWNER")
    else:
        case("unreadable files", False, "running as root: chmod cannot make a file unreadable; run as a user")
    root = fixture("noplan", "BlueDesert")
    os.remove(os.path.join(root, PLAN_REL))
    expect("plan missing", root, "BlueDesert", "PLAN_MISSING")
    root = fixture("badplan", "Abyss")
    doc = json.load(open(os.path.join(root, PLAN_REL)))
    doc["mods"]["Abyss"]["marks"]["fold_lamp"] = "maybe"
    json.dump(doc, open(os.path.join(root, PLAN_REL), "w"))
    expect("plan holds an unknown mark", root, "Abyss", "PLAN_MALFORMED")
    open(os.path.join(root, PLAN_REL), "w").write("{not json")
    expect("plan not json", root, "Abyss", "PLAN_MALFORMED")
    alt = os.path.join(TMP, "alt_plan.json")
    shutil.copy(os.path.join(ROOT, PLAN_REL), alt)
    expect("--plan names another file", fixture("altplan", "BlueDesert"), "BlueDesert", "APPROVED", plan=alt)

    # the selftest stands on its own fixtures (review-3 finding 8, carried here)
    sp = os.path.join(TMP, "sparse")
    for sub in ("rimflow", "Utils", "contracts"):
        shutil.copytree(os.path.join(ROOT, "src", "RimMandrake", sub), os.path.join(sp, "src", "RimMandrake", sub),
                        ignore=shutil.ignore_patterns("__pycache__"))
    st = os.path.join(sp, "src", "RimMandrake", "rimflow", "selftest_cleanse_plan.py")
    if os.path.exists(st):
        p = subprocess.run([sys.executable, st], capture_output=True, text=True, timeout=300, cwd=sp)
        tail = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
        case("selftest_cleanse_plan in a source-only copy", p.returncode == 0, "exit %s: %s" % (p.returncode, tail[0][:200]))
    else:
        case("selftest_cleanse_plan in a source-only copy", False, "src/RimMandrake/rimflow/selftest_cleanse_plan.py does not exist")

    print("cases read %d; wrong %d (worst: %s); limit 0" % (READ[0], len(WRONG), WRONG[0] if WRONG else "none"))
    shutil.rmtree(TMP, ignore_errors=True)
    return 1 if WRONG else 0


if __name__ == "__main__":
    sys.exit(main())
