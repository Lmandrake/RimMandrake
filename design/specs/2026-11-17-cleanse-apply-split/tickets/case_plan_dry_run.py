#!/usr/bin/env python3
"""Failing acceptance cases for ticket RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS (split from
RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL after three Codex rounds; review-3 findings 1, 5, 6, 7, 8
are cases here, finding 4 is the write ticket's).

Contract read (the ticket's ## spec): `designer_cleanse.apply_plan(repo, mod)` -> dict with `answer` one of
WOULD_WRITE / NOTHING_TO_APPLY / REFUSED / COULD_NOT_LOOK, `cause`, `path`, `files` {path under the concept folder:
text}; it writes nothing. CLI `designer_cleanse.py apply <Mod> --repo <root>` prints one closing line
`APPLY <Mod> <ANSWER> ...`, exit 0 / 3 / 1 / 4 for those four; `--write` is `REFUSED WRITE_NOT_BUILT` (exit 1).

Input kinds read, each a copy of a real concept folder under a temp repo root (never the live folder):
K1 proposal only (BlueDesert); K2 old tree + stage ready, idle (Cauldron); K2 + an old leaf the proposal does not map;
K3 stage blocked (GelatinousSlime); K4 VERSION locked + later_version.md (LeaningScrub); Contagion (later_version.md,
VERSION open); K5 a Designer run open; converge missing / {} / 0-byte / not converged / no digest / stale digest;
result not applyable; zero kept; zero moved; an unreadable scenes.json and converge.json; Pyrelands; no proposal;
a re-plan of an already-materialized plan; and the selftest run from a copy holding only src/RimMandrake/{rimflow,Utils,contracts}.
Run from the repo root:  python3 design/specs/2026-11-17-cleanse-apply-split/tickets/case_plan_dry_run.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import hashlib
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

TMP = tempfile.mkdtemp(prefix="case_plan_dry_run_")
WRONG = []
READ = [0]
ANSWERS = ("WOULD_WRITE", "NOTHING_TO_APPLY", "REFUSED", "COULD_NOT_LOOK")
EXIT = {"WOULD_WRITE": 0, "NOTHING_TO_APPLY": 3, "REFUSED": 1, "COULD_NOT_LOOK": 4}
MARK_BEGIN, MARK_END = "<!-- cleanse:next_version begin -->", "<!-- cleanse:next_version end -->"


def case(name, ok, why=""):
    READ[0] += 1
    if not ok:
        WRONG.append(name)
        print("WRONG %s: %s" % (name, why))


def fixture(mod, tag):
    """A temp repo root holding a copy of design/concepts/<mod>; -> (root, concept dir)."""
    root = os.path.join(TMP, tag)
    d = os.path.join(root, "design", "concepts", mod)
    shutil.copytree(os.path.join(ROOT, "design", "concepts", mod), d, symlinks=True)
    return root, d


def tree_digest(d):
    h = hashlib.sha256()
    for base, dirs, files in sorted(os.walk(d)):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(base, f)
            h.update(os.path.relpath(p, d).encode() + b"\0")
            try:
                st = os.stat(p)
                h.update(str((st.st_mode, st.st_size, st.st_mtime_ns)).encode())
                with open(p, "rb") as fh:
                    h.update(fh.read())
            except OSError as e:
                h.update(repr(e.errno).encode())
    return h.hexdigest()


def plan(root, mod):
    if not hasattr(DC, "apply_plan"):
        return None, "designer_cleanse has no apply_plan"
    try:
        r = DC.apply_plan(root, mod)
    except Exception as e:  # a crash is a wrong answer, not a verdict
        return None, "apply_plan raised %s: %s" % (type(e).__name__, e)
    if not isinstance(r, dict) or r.get("answer") not in ANSWERS:
        return None, "apply_plan returned %r" % (r if not isinstance(r, dict) else r.get("answer"),)
    return r, ""


def cli(root, mod, *extra):
    p = subprocess.run([sys.executable, os.path.join(RF, "designer_cleanse.py"), "apply", mod, "--repo", root] +
                       list(extra), capture_output=True, text=True, timeout=120)
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    return p.returncode, (lines[-1] if lines else ""), p.stderr[-300:]


def expect(name, root, mod, answer, cause=None, path_has=None):
    """apply_plan and the CLI agree on answer (and cause); the concept folder is byte-for-byte unchanged."""
    d = os.path.join(root, "design", "concepts", mod)
    before = tree_digest(d) if os.path.isdir(d) else None
    r, why = plan(root, mod)
    if r is None:
        case(name + " (seam)", False, why)
    else:
        got = (r.get("answer"), r.get("cause") if cause else None)
        case(name + " (seam)", got == (answer, cause), "got %r, want %r" % (got, (answer, cause)))
        if path_has:
            case(name + " (path)", path_has in str(r.get("path") or ""), "path %r lacks %r" % (r.get("path"), path_has))
    code, last, err = cli(root, mod)
    want = "APPLY %s %s" % (mod, answer) + (" %s" % cause if cause else "")
    case(name + " (cli)", code == EXIT[answer] and last.startswith(want),
         "exit %s line %r, want exit %s line starting %r %s" % (code, last, EXIT[answer], want, err.strip()[-160:]))
    after = tree_digest(d) if os.path.isdir(d) else None
    case(name + " (writes nothing)", before == after, "the concept folder changed during a dry run")
    return r


def materialize(d, files):
    for rel, text in (files or {}).items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)


def reconverge(d):
    """Make converge.json name the current proposal digest (for fixtures whose proposal text the case edits)."""
    out = os.path.join(d, "cleanse")
    p = os.path.join(out, "converge.json")
    doc = json.load(open(p, encoding="utf-8"))
    doc["digest"] = DC.proposal_digest(out)
    json.dump(doc, open(p, "w", encoding="utf-8"), indent=1)


def edit_json(p, fn):
    doc = json.load(open(p, encoding="utf-8"))
    fn(doc)
    json.dump(doc, open(p, "w", encoding="utf-8"), indent=1)


def leaf_ids(tree):
    return [x.get("id") for x in (tree.get("leaves") or []) if isinstance(x, dict)]


def planned_shape(name, root, mod, r, old_ids):
    d = os.path.join(root, "design", "concepts", mod)
    files = r.get("files") or {}
    need = {"tree.json", "sheet.md", "stage.json", "version/VERSION.json"}
    case(name + " files", need <= set(files), "planned files %s lack %s" % (sorted(files), sorted(need - set(files))))
    if not need <= set(files):
        return
    case(name + " deterministic", (plan(root, mod)[0] or {}).get("files") == files, "a second plan differs")
    try:
        tree = json.loads(files["tree.json"])
        stage = json.loads(files["stage.json"])
        ver = json.loads(files["version/VERSION.json"])
    except ValueError as e:
        case(name + " json", False, "planned json does not parse: %s" % e)
        return
    bars = [b.get("id") for b in json.load(open(os.path.join(d, "cleanse", "bars.json")))["bars"]]
    case(name + " every bar a leaf", set(bars) <= set(leaf_ids(tree)), "bars %s not leaves" % sorted(set(bars) - set(leaf_ids(tree))))
    cl = tree.get("cleanse") if isinstance(tree.get("cleanse"), dict) else {}
    case(name + " tree digest", cl.get("digest") == DC.proposal_digest(os.path.join(d, "cleanse")), "tree.cleanse.digest %r" % cl.get("digest"))
    case(name + " old leaf ids kept", cl.get("old_leaf_ids") == old_ids, "old_leaf_ids %r, want %r" % (cl.get("old_leaf_ids"), old_ids))
    case(name + " stage withdrawn", stage.get("status") == "blocked" and stage.get("running") is None and bool(stage.get("blocked_on")),
         "planned stage status %r running %r blocked_on %r" % (stage.get("status"), stage.get("running"), stage.get("blocked_on")))
    case(name + " version", ver.get("version") == "0.1.0" and ver.get("proposal_digest") == cl.get("digest") and "replaces" in ver,
         "planned VERSION %r" % {k: ver.get(k) for k in ("version", "proposal_digest", "replaces")})
    rows = json.load(open(os.path.join(d, "cleanse", "census.json")))["rows"]
    moved = [x["id"] for x in rows if x.get("fate") == "next_version"]
    lv = files.get("later_version.md")
    if moved:
        ok = lv is not None and lv.count(MARK_BEGIN) == 1 and lv.count(MARK_END) == 1
        case(name + " next-version section once", ok, "later_version.md missing or markers not exactly once")
        if ok:
            sec = lv.split(MARK_BEGIN)[1].split(MARK_END)[0]
            case(name + " moved ids listed", all(m in sec for m in moved), "moved ids missing from section: %s" % [m for m in moved if m not in sec][:5])
    old_lv = os.path.join(d, "later_version.md")
    if os.path.exists(old_lv) and lv is not None:
        prior = open(old_lv, encoding="utf-8").read()
        outside = prior.split(MARK_BEGIN)[0] + (prior.split(MARK_END)[1] if MARK_END in prior else "")
        case(name + " earlier text kept", outside.strip() in lv, "earlier later_version.md text not kept verbatim")
    # load the planned folder through the readers, in a copy
    cp = os.path.join(TMP, name.replace(" ", "_") + "_applied")
    shutil.copytree(d, cp)
    materialize(cp, files)
    try:
        CT.load(cp)
        s = DS.status(cp)
        case(name + " stage reader", s.get("status") == "blocked" and s.get("running") is None, "status() read %r" % {k: s.get(k) for k in ("stage", "status", "running")})
    except Exception as e:
        case(name + " stage reader", False, "applied copy does not load: %s: %s" % (type(e).__name__, e))
    refs, _ = DC.check_dir(os.path.join(cp, "cleanse"))
    case(name + " check after apply", not refs, "check refuses the applied copy: %s" % [x.get("rule") for x in refs][:4])
    return cp


def main():
    # K1, proposal only
    root, d = fixture("BlueDesert", "k1")
    r = expect("K1 BlueDesert dry run", root, "BlueDesert", "WOULD_WRITE")
    if r:
        cp = planned_shape("K1", root, "BlueDesert", r, [])
        if cp:  # a re-plan of the materialized plan has nothing to apply
            croot = os.path.join(TMP, "k1_again")
            shutil.copytree(cp, os.path.join(croot, "design", "concepts", "BlueDesert"))
            expect("K1 re-plan after apply", croot, "BlueDesert", "NOTHING_TO_APPLY")
    code, last, _ = cli(root, "BlueDesert", "--write")
    case("--write not built here", code == 1 and last.startswith("APPLY BlueDesert REFUSED WRITE_NOT_BUILT"), "exit %s line %r" % (code, last))
    case("--write wrote nothing", not os.path.exists(os.path.join(d, "tree.json")), "tree.json appeared")

    # K2, old tree, stage ready and idle (a queued Designer job): the plan withdraws it
    root, d = fixture("Cauldron", "k2")
    old = leaf_ids(json.load(open(os.path.join(d, "tree.json"))))
    r = expect("K2 Cauldron dry run", root, "Cauldron", "WOULD_WRITE")
    if r:
        cp = planned_shape("K2", root, "Cauldron", r, old)
        if cp:  # retry: check still runs and still guards the original old bars (finding 6)
            croot = os.path.join(TMP, "k2_retry")
            dd = os.path.join(croot, "design", "concepts", "Cauldron")
            shutil.copytree(cp, dd)
            edit_json(os.path.join(dd, "tree.json"), lambda t: t["cleanse"]["old_leaf_ids"].append("unmapped_old_bar"))
            expect("K2 retry, an old bar unmapped", croot, "Cauldron", "REFUSED", "CHECK_FAILED")
    root, d = fixture("Cauldron", "k2_unmapped")
    edit_json(os.path.join(d, "tree.json"), lambda t: t["leaves"].append(dict(t["leaves"][0], id="unmapped_old_bar")))
    expect("K2 old leaf not mapped", root, "Cauldron", "REFUSED", "CHECK_FAILED")

    # K5, a Designer run open (finding 1)
    root, d = fixture("Cauldron", "k5")
    edit_json(os.path.join(d, "stage.json"), lambda s: s.update(running={"run": "rm-role-designercodex-1", "stage": 4}))
    expect("K5 Designer run open", root, "Cauldron", "REFUSED", "DESIGNER_RUN_OPEN")

    # K3 blocked, K4 locked with later_version.md, Contagion with later_version.md (finding 5)
    for mod, tag in (("GelatinousSlime", "k3"), ("LeaningScrub", "k4"), ("Contagion", "contagion")):
        root, d = fixture(mod, tag)
        old = leaf_ids(json.load(open(os.path.join(d, "tree.json"))))
        r = expect("%s %s dry run" % (tag.upper(), mod), root, mod, "WOULD_WRITE")
        if r:
            cp = planned_shape(tag.upper(), root, mod, r, old)
            if cp:
                croot = os.path.join(TMP, tag + "_again")
                shutil.copytree(cp, os.path.join(croot, "design", "concepts", mod))
                expect("%s re-plan after apply" % tag.upper(), croot, mod, "NOTHING_TO_APPLY")
    root, d = fixture("LeaningScrub", "k4_newer")
    edit_json(os.path.join(d, "version", "VERSION.json"), lambda v: v.update(version="0.2.0"))
    expect("VERSION newer than 0.1.0", root, "LeaningScrub", "REFUSED", "VERSION_DOWNGRADE")

    # converge and result kinds (finding 7, second half)
    def kinds():
        yield "converge missing", lambda d: os.remove(os.path.join(d, "cleanse", "converge.json")), "CONVERGE_MISSING"
        yield "converge {}", lambda d: open(os.path.join(d, "cleanse", "converge.json"), "w").write("{}"), "CONVERGE_EMPTY"
        yield "converge 0 bytes", lambda d: open(os.path.join(d, "cleanse", "converge.json"), "w").close(), "CONVERGE_EMPTY"
        yield "converge not converged", lambda d: edit_json(os.path.join(d, "cleanse", "converge.json"), lambda c: c.update(applyable=False, open=["x"])), "NOT_CONVERGED"
        yield "converge no digest", lambda d: edit_json(os.path.join(d, "cleanse", "converge.json"), lambda c: c.pop("digest")), "STALE_CONVERGENCE"
        yield "converge stale digest", lambda d: edit_json(os.path.join(d, "cleanse", "converge.json"), lambda c: c.update(digest="0" * 64)), "STALE_CONVERGENCE"
        yield "result not applyable", lambda d: edit_json(os.path.join(d, "cleanse", "result.json"), lambda c: c.update(applyable=False)), "RESULT_NOT_APPLYABLE"
        yield "no proposal", lambda d: shutil.rmtree(os.path.join(d, "cleanse")), "NO_PROPOSAL"
    for i, (name, fn, cause) in enumerate(kinds()):
        root, d = fixture("BlueDesert", "kind%d" % i)
        fn(d)
        expect(name, root, "BlueDesert", "REFUSED", cause)

    # zero kept is refused; zero moved is planned (the proposal edited, its counts and convergence made consistent)
    def refate(d, frm, to):
        p = os.path.join(d, "cleanse", "census.json")
        edit_json(p, lambda c: [x.update(fate=to) for x in c["rows"] if (x.get("fate") in frm)])
        rows = json.load(open(p))["rows"]
        edit_json(os.path.join(d, "cleanse", "result.json"), lambda r: r["counts"].update(
            kept=sum(1 for x in rows if x.get("fate") in DC.KEPT), next_version=sum(1 for x in rows if x.get("fate") == "next_version")))
        reconverge(d)
    root, d = fixture("BlueDesert", "zero_kept")
    refate(d, DC.KEPT, "next_version")
    expect("zero kept", root, "BlueDesert", "REFUSED", "ZERO_KEPT")
    root, d = fixture("BlueDesert", "zero_moved")
    refate(d, ("next_version",), "land")
    refs, _ = DC.check_dir(os.path.join(d, "cleanse"))
    if refs:
        case("zero moved fixture", False, "fixture itself fails check: %s" % [x.get("rule") for x in refs][:4])
    else:
        r = expect("zero moved", root, "BlueDesert", "WOULD_WRITE")
        if r:
            case("zero moved writes no next-version file", "later_version.md" not in (r.get("files") or {}), "later_version.md planned with nothing moved")

    # strict reads (finding 7, first half): an existing file that cannot be read is COULD_NOT_LOOK, never a pass
    if os.geteuid() != 0:
        for rel in ("scenes.json", "cleanse/converge.json"):
            root, d = fixture("Cauldron", "unreadable_" + rel.replace("/", "_"))
            os.chmod(os.path.join(d, rel), 0)
            expect("unreadable " + rel, root, "Cauldron", "COULD_NOT_LOOK", path_has=os.path.basename(rel))
            os.chmod(os.path.join(d, rel), 0o644)
    else:
        case("unreadable files", False, "running as root: chmod cannot make a file unreadable; run as a user")

    # Pyrelands is outside the cleanse
    root = os.path.join(TMP, "pyre")
    os.makedirs(os.path.join(root, "design", "concepts", "Pyrelands", "cleanse"))
    expect("Pyrelands", root, "Pyrelands", "REFUSED", "PYRELANDS")

    # finding 8: the selftest passes from a copy holding src/RimMandrake/{rimflow,Utils,contracts} and nothing under design/
    sp = os.path.join(TMP, "sparse")
    for sub in ("rimflow", "Utils", "contracts"):  # the source dirs of scratch_clone.BASE_CONE; no design/, no infrastructure/
        shutil.copytree(os.path.join(ROOT, "src", "RimMandrake", sub), os.path.join(sp, "src", "RimMandrake", sub),
                        ignore=shutil.ignore_patterns("__pycache__"))
    p = subprocess.run([sys.executable, os.path.join(sp, "src", "RimMandrake", "rimflow", "selftest_designer_cleanse.py")],
                       capture_output=True, text=True, timeout=300, cwd=sp)
    tail = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
    case("selftest in a source-only copy", p.returncode == 0, "exit %s: %s" % (p.returncode, tail[0][:200]))
    src = open(os.path.join(RF, "selftest_designer_cleanse.py"), encoding="utf-8").read()
    case("selftest covers apply", "apply_plan" in src, "selftest_designer_cleanse.py never calls apply_plan")

    print("cases read %d; wrong %d (worst: %s); limit 0" % (READ[0], len(WRONG), WRONG[0] if WRONG else "none"))
    shutil.rmtree(TMP, ignore_errors=True)
    return 1 if WRONG else 0


if __name__ == "__main__":
    sys.exit(main())
