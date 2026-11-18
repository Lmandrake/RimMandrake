#!/usr/bin/env python3
"""Failing acceptance cases for ticket RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_UNTOUCHED (split from
RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL; review-3 finding 4 and the write half of finding 1).
It builds on RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS (apply_plan) and RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID
(cleanse_plan.plan_check); both must have landed first.

Contract read (the ticket's ## spec): `designer_cleanse.apply_write(repo, mod, fault=None)` -> dict with `answer` one of
WROTE / NOTHING_TO_APPLY / REFUSED / COULD_NOT_LOOK / WRITE_FAILED, `cause`, `path`, `files` (the relpaths written),
`cleanup_failed` (a list, empty when cleanup succeeded). It installs exactly apply_plan(repo, mod)["files"] inside
design/concepts/<Mod>/ and nowhere else. `fault(phase, rel)` is a test seam called at phase "locked" (once, after it takes
its lock and before it re-reads stage.json), "install" (before each file is put in place, rel = its relpath) and
"cleanup" (once, after every file is in place); an exception from it at "locked"/"install" ends in a full rollback.
CLI `designer_cleanse.py apply <Mod> --write --repo <root>` (fault from the module global `APPLY_FAULT`, default None)
prints `APPLY <Mod> CLEANUP_FAILED <detail>` when cleanup failed, then one closing line `APPLY <Mod> <ANSWER> ...`
(`APPLY <Mod> WROTE <n> files`); exit WROTE 0, NOTHING_TO_APPLY 3, REFUSED 1, COULD_NOT_LOOK 4, WRITE_FAILED 5.
Approval comes from cleanse_plan.plan_check(repo, mod): any answer but APPROVED refuses with cause NOT_APPROVED
(COULD_NOT_LOOK stays COULD_NOT_LOOK); apply_plan's own refusals come first and keep their causes.

Input kinds read (each a copy under a temp repo root holding the plan JSON and the owner-hold file, never the live folder):
K1 BlueDesert, K2 Cauldron (old tree, stage ready), K4 LeaningScrub (VERSION locked, later_version.md); a re-run;
TheRot awaiting review; BlueDesert changed since approval; plan missing; plan unreadable; converge missing; a Designer run
open before and during the write; an install fault on the first and on a later file; a cleanup fault; Pyrelands; and the
selftest from a copy holding only src/RimMandrake/{rimflow,Utils,contracts}.
Run from the repo root:  python3 design/specs/2026-11-17-cleanse-apply-split/tickets/case_write_apply.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import contextlib
import hashlib
import io
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
import designer_stage as DS  # noqa: E402
import concept_tree as CT  # noqa: E402

PLAN_REL = os.path.join("design", "concepts", "CLEANSE_PLAN_OWNER_2026-11-17.json")
HOLD_REL = os.path.join("src", "RimMandrake", "rimflow", "mod_owner_hold.json")
TMP = tempfile.mkdtemp(prefix="case_write_apply_")
WRONG = []
READ = [0]
ANSWERS = ("WROTE", "NOTHING_TO_APPLY", "REFUSED", "COULD_NOT_LOOK", "WRITE_FAILED")
EXIT = {"WROTE": 0, "NOTHING_TO_APPLY": 3, "REFUSED": 1, "COULD_NOT_LOOK": 4, "WRITE_FAILED": 5}


def case(name, ok, why=""):
    READ[0] += 1
    if not ok:
        WRONG.append(name)
        print("WRONG %s: %s" % (name, why))


def fixture(mod, tag):
    """A temp repo root: the concept copy, the plan JSON, the hold file and a stand-in mod source; -> (root, dir)."""
    root = os.path.join(TMP, tag)
    d = os.path.join(root, "design", "concepts", mod)
    shutil.copytree(os.path.join(ROOT, "design", "concepts", mod), d, symlinks=True)
    for rel in (PLAN_REL, HOLD_REL):
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), os.path.join(root, rel))
    src = os.path.join(root, "src", "RimMandrake", mod, "About")
    os.makedirs(src, exist_ok=True)
    open(os.path.join(src, "About.xml"), "w").write("<ModMetaData/>")
    return root, d


def content(d, skip=None):
    """{relpath: (mode, sha256)} under d (no mtimes: a rollback that restores bytes and modes is exact)."""
    out = {}
    for base, dirs, files in os.walk(d):
        if skip and os.path.abspath(base) == os.path.abspath(os.path.dirname(skip)):
            dirs[:] = [x for x in dirs if os.path.join(base, x) != skip]
        for f in files:
            p = os.path.join(base, f)
            if skip and (p + os.sep).startswith(skip + os.sep):
                continue
            try:
                with open(p, "rb") as fh:
                    out[os.path.relpath(p, d)] = (os.stat(p).st_mode, hashlib.sha256(fh.read()).hexdigest())
            except OSError as e:
                out[os.path.relpath(p, d)] = ("unreadable", e.errno)
    return out


def write(root, mod, fault=None):
    if not hasattr(DC, "apply_write"):
        return None, "designer_cleanse has no apply_write"
    try:
        r = DC.apply_write(root, mod, fault=fault)
    except Exception as e:
        return None, "apply_write raised %s: %s" % (type(e).__name__, e)
    if not isinstance(r, dict) or r.get("answer") not in ANSWERS:
        return None, "apply_write returned %r" % (r if not isinstance(r, dict) else r.get("answer"),)
    return r, ""


def cli(root, mod, fault=None):
    """In-process, so a fault can be injected through DC.APPLY_FAULT; -> (exit, stdout lines)."""
    buf = io.StringIO()
    old = getattr(DC, "APPLY_FAULT", None)
    DC.APPLY_FAULT = fault
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            code = DC.main(["apply", mod, "--write", "--repo", root])
    except SystemExit as e:
        code = e.code
    except Exception as e:
        code = "raised %s: %s" % (type(e).__name__, e)
    finally:
        DC.APPLY_FAULT = old
    return code, [x for x in buf.getvalue().splitlines() if x.strip()]


def refuse(name, root, mod, answer, cause=None, via_cli=True):
    """A refusal through the seam and the CLI: nothing anywhere under the temp root changes."""
    before = content(root)
    r, why = write(root, mod)
    if r is None:
        case(name + " (seam)", False, why)
    else:
        got = (r.get("answer"), r.get("cause") if cause else None)
        case(name + " (seam)", got == (answer, cause), "got %r, want %r" % (got, (answer, cause)))
    if via_cli:
        code, lines = cli(root, mod)
        want = "APPLY %s %s" % (mod, answer) + (" %s" % cause if cause else "")
        last = lines[-1] if lines else ""
        case(name + " (cli)", code == EXIT[answer] and last.startswith(want), "exit %r line %r, want %s %r" % (code, last, EXIT[answer], want))
    case(name + " (wrote nothing)", content(root) == before, "files changed under the temp root on a refusal")
    return r


def wrote(name, root, mod, old_leaves=None):
    """--write on an approved proposal: exactly the planned files, only in the concept folder, loads as blocked."""
    d = os.path.join(root, "design", "concepts", mod)
    if not hasattr(DC, "apply_plan"):
        case(name + " (plan first)", False, "designer_cleanse has no apply_plan (the dry-run ticket lands first)")
        return
    p = DC.apply_plan(root, mod)
    files = p.get("files") or {}
    outside = content(root, skip=d)
    real_hold = content(os.path.dirname(os.path.join(ROOT, HOLD_REL)))
    before = content(d)
    code, lines = cli(root, mod)
    last = lines[-1] if lines else ""
    case(name + " (cli)", code == 0 and last == "APPLY %s WROTE %d files" % (mod, len(files)),
         "exit %r line %r, want 0 'APPLY %s WROTE %d files'" % (code, last, mod, len(files)))
    case(name + " (no cleanup line)", not any("CLEANUP_FAILED" in x for x in lines), "a clean write printed CLEANUP_FAILED")
    for rel, text in files.items():
        try:
            got = open(os.path.join(d, rel), encoding="utf-8").read()
        except OSError as e:
            got = "<%s>" % e
        if got != text:
            case(name + " (installed = planned)", False, "%s differs from the plan" % rel)
            break
    else:
        case(name + " (installed = planned)", bool(files), "nothing was planned")
    after = content(d)
    stray = sorted(set(after) - set(before) - set(files))
    case(name + " (no stray files)", not stray, "left behind in the concept folder: %s" % stray[:5])
    gone = sorted(set(before) - set(after))
    case(name + " (nothing removed)", not gone, "removed from the concept folder: %s" % gone[:5])
    case(name + " (only the concept folder)", content(root, skip=d) == outside,
         "wrote outside design/concepts/%s (plan JSON, hold file or src/RimMandrake/%s)" % (mod, mod))
    case(name + " (live hold untouched)", content(os.path.dirname(os.path.join(ROOT, HOLD_REL))) == real_hold, "the live rimflow dir changed")
    try:
        CT.load(d)
        s = DS.status(d)
        case(name + " (stage reader)", s.get("status") == "blocked" and s.get("running") is None,
             "status() read %r" % {k: s.get(k) for k in ("stage", "status", "running")})
    except Exception as e:
        case(name + " (stage reader)", False, "applied folder does not load: %s: %s" % (type(e).__name__, e))
    refs, _ = DC.check_dir(os.path.join(d, "cleanse"))
    case(name + " (check after write)", not refs, "check refuses the applied folder: %s" % [x.get("rule") for x in refs][:4])
    if old_leaves is not None:
        t = json.load(open(os.path.join(d, "tree.json")))
        case(name + " (old leaves recorded)", (t.get("cleanse") or {}).get("old_leaf_ids") == old_leaves, "old_leaf_ids not kept")
    snap = content(root)
    code, lines = cli(root, mod)
    last = lines[-1] if lines else ""
    case(name + " re-run (cli)", code == 3 and last.startswith("APPLY %s NOTHING_TO_APPLY" % mod), "exit %r line %r" % (code, last))
    case(name + " re-run (wrote nothing)", content(root) == snap, "a re-run changed files")


def edit_json(p, fn):
    doc = json.load(open(p, encoding="utf-8"))
    fn(doc)
    json.dump(doc, open(p, "w", encoding="utf-8"), indent=1)


def main():
    for mod, tag in (("BlueDesert", "k1"), ("Cauldron", "k2"), ("LeaningScrub", "k4")):
        root, d = fixture(mod, tag)
        old = None
        if os.path.exists(os.path.join(d, "tree.json")):
            old = [x.get("id") for x in json.load(open(os.path.join(d, "tree.json"))).get("leaves") or []]
        wrote("%s %s write" % (tag.upper(), mod), root, mod, old)

    # approval from the owner's plan, by cleanse_plan.plan_check (never his markdown)
    root, d = fixture("TheRot", "rot")
    refuse("TheRot awaiting review", root, "TheRot", "REFUSED", "NOT_APPROVED")
    root, d = fixture("BlueDesert", "changed")
    p = os.path.join(d, "cleanse", "census.json")
    edit_json(p, lambda c: c["rows"].pop())
    edit_json(os.path.join(d, "cleanse", "converge.json"), lambda c: c.update(digest=DC.proposal_digest(os.path.join(d, "cleanse"))))
    refuse("BlueDesert changed since approval", root, "BlueDesert", "REFUSED", "NOT_APPROVED")
    root, d = fixture("BlueDesert", "noplan")
    os.remove(os.path.join(root, PLAN_REL))
    refuse("plan missing", root, "BlueDesert", "REFUSED", "NOT_APPROVED")
    if os.geteuid() != 0:
        root, d = fixture("BlueDesert", "planunreadable")
        os.chmod(os.path.join(root, PLAN_REL), 0)
        refuse("plan unreadable", root, "BlueDesert", "COULD_NOT_LOOK")
        os.chmod(os.path.join(root, PLAN_REL), 0o644)
    else:
        case("plan unreadable", False, "running as root: chmod cannot make a file unreadable")

    # the dry-run planner's refusals still decide first
    root, d = fixture("BlueDesert", "noconverge")
    os.remove(os.path.join(d, "cleanse", "converge.json"))
    refuse("converge missing", root, "BlueDesert", "REFUSED", "CONVERGE_MISSING")
    root = os.path.join(TMP, "pyre")
    os.makedirs(os.path.join(root, "design", "concepts", "Pyrelands", "cleanse"))
    refuse("Pyrelands", root, "Pyrelands", "REFUSED", "PYRELANDS")

    # a Designer run open: before the write, and opened while it waits on its lock (finding 1)
    root, d = fixture("Cauldron", "running")
    edit_json(os.path.join(d, "stage.json"), lambda s: s.update(running={"run": "rm-role-designercodex-1", "stage": 4}))
    refuse("Designer run open", root, "Cauldron", "REFUSED", "DESIGNER_RUN_OPEN")
    root, d = fixture("Cauldron", "race")

    def opens_run(phase, rel):
        if phase == "locked":
            edit_json(os.path.join(d, "stage.json"), lambda s: s.update(running={"run": "rm-role-designercodex-2", "stage": 4}))
    before = content(d)
    r, why = write(root, "Cauldron", fault=opens_run)
    case("run opened during the write (seam)", r is not None and (r.get("answer"), r.get("cause")) == ("REFUSED", "DESIGNER_RUN_OPEN"),
         why or "got %r" % ((r.get("answer"), r.get("cause")),))
    after = content(d)
    after.pop("stage.json", None)
    before.pop("stage.json", None)
    case("run opened during the write (wrote nothing)", after == before, "files changed besides the run the fault opened")

    # an install fault rolls back to the exact prior bytes (first file, and a later one)
    for n in (1, 3):
        root, d = fixture("Cauldron", "fault%d" % n)
        seen = []

        def boom(phase, rel, n=n, seen=seen):
            if phase == "install":
                seen.append(rel)
                if len(seen) == n:
                    raise OSError(28, "No space left on device (injected)")
        before = content(d)
        code, lines = cli(root, "Cauldron", fault=boom)
        last = lines[-1] if lines else ""
        case("install fault on file %d (cli)" % n, code == 5 and last.startswith("APPLY Cauldron WRITE_FAILED"), "exit %r line %r" % (code, last))
        case("install fault on file %d (rolled back)" % n, content(d) == before, "the concept folder differs from before the write")
        case("install fault on file %d (reached)" % n, len(seen) >= n, "only %d install calls" % len(seen))

    # a cleanup fault after a complete install is WROTE plus its own line, never WRITE_FAILED (finding 4)
    root, d = fixture("Cauldron", "cleanup")
    files = DC.apply_plan(root, "Cauldron").get("files") if hasattr(DC, "apply_plan") else {}

    def dirty(phase, rel):
        if phase == "cleanup":
            raise OSError(16, "Device or resource busy (injected)")
    code, lines = cli(root, "Cauldron", fault=dirty)
    last = lines[-1] if lines else ""
    case("cleanup fault (cli)", code == 0 and last == "APPLY Cauldron WROTE %d files" % len(files or {}), "exit %r line %r" % (code, last))
    case("cleanup fault (own line)", any(x.startswith("APPLY Cauldron CLEANUP_FAILED") for x in lines[:-1]), "lines %r" % lines[-3:])
    ok = bool(files) and all(open(os.path.join(d, rel), encoding="utf-8").read() == t for rel, t in files.items())
    case("cleanup fault (installed = planned)", ok, "the install is not complete")
    root, d = fixture("BlueDesert", "cleanup_seam")
    r, why = write(root, "BlueDesert", fault=dirty)
    case("cleanup fault (seam)", r is not None and r.get("answer") == "WROTE" and bool(r.get("cleanup_failed")),
         why or "got %r cleanup_failed %r" % (r.get("answer"), r.get("cleanup_failed")))

    # the selftest passes from a source-only copy and covers the write
    sp = os.path.join(TMP, "sparse")
    for sub in ("rimflow", "Utils", "contracts"):
        shutil.copytree(os.path.join(ROOT, "src", "RimMandrake", sub), os.path.join(sp, "src", "RimMandrake", sub),
                        ignore=shutil.ignore_patterns("__pycache__"))
    p = subprocess.run([sys.executable, os.path.join(sp, "src", "RimMandrake", "rimflow", "selftest_designer_cleanse.py")],
                       capture_output=True, text=True, timeout=300, cwd=sp)
    tail = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
    case("selftest in a source-only copy", p.returncode == 0, "exit %s: %s" % (p.returncode, tail[0][:200]))
    src = open(os.path.join(RF, "selftest_designer_cleanse.py"), encoding="utf-8").read()
    case("selftest covers the write", "apply_write" in src and "fault" in src, "selftest_designer_cleanse.py never calls apply_write with a fault")

    print("cases read %d; wrong %d (worst: %s); limit 0" % (READ[0], len(WRONG), WRONG[0] if WRONG else "none"))
    shutil.rmtree(TMP, ignore_errors=True)
    return 1 if WRONG else 0


if __name__ == "__main__":
    sys.exit(main())
