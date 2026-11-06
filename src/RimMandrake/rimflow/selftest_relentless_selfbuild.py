#!/usr/bin/env python3
"""relentless_selfbuild (SELFBUILD_DESIGN_STAGE_ZERO_KEEPS_KEYS): the protected-list check refuses a candidate touching
a grader part, a protected key, or a module a protected check imports (also when the import is new), and passes a clean
diff; `ready` refuses until a builder wall denies the keys; `promote` swaps only on >= pass^k on every frozen set; the
replay draw is stratified, seeded, token-sized and drops the builder's rows; `cross` refuses labels or held-out cases by
the building instance and a hand-picked replay list. A throwaway git repo and planted docs; one read of the real list."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless_selfbuild as S  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def git(root, *a):
    subprocess.run(["git", "-C", root, *a], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                        "GIT_COMMITTER_EMAIL": "t@t"})
    return subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def write(root, rel, text):
    p = Path(root, rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


SPEC = {
    "protected": [{"path": "r/judge.py", "part": "Judge"}, {"path": "doc/counting.md", "part": "counting rules"}],
    "protected_keys": [{"path": "r/rules.json", "keys": ["walls"], "part": "wall"}],
    "import_roots": ["u"],
    "outside": [{"path": "/keys/seeds", "part": "keys"}, {"path": "/store", "part": "store"}],
    "build_wall": "builder",
    "promotion": {"sets": ["E1", "E2"], "min_repeats": 2},
    "replay": {"token_max": 4, "token_min": 2},
}


def test_protected():
    with tempfile.TemporaryDirectory() as root:
        subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
        write(root, "r/judge.py", "import helper\nfrom pkg import sub\n\ndef f():\n    from verdict import v\n")
        write(root, "u/pkg/__init__.py", "")
        write(root, "u/pkg/sub.py", "")
        write(root, S.SPEC_REL, json.dumps(SPEC))
        write(root, "r/helper.py", "X = 1\n")
        write(root, "u/verdict.py", "import deep\n")
        write(root, "u/deep.py", "")
        write(root, "u/free.py", "Y = 1\n")
        write(root, "r/worker.py", "Z = 1\n")
        write(root, "r/rules.json", json.dumps({"walls": {"marker": 1}, "max_workers": 4}))
        write(root, "doc/counting.md", "rules\n")
        git(root, "add", "-A")
        base = git(root, "commit", "-qm", "base")

        def diff(edit):
            for rel, text in edit.items():
                write(root, rel, text)
            git(root, "add", "-A")
            head = git(root, "commit", "-qm", "c")
            return head, S.check_protected(root, base_now[0], head, SPEC)

        base_now = [base]
        prot = S.protected_set(SPEC, S._reader(root, base))
        ok({"r/judge.py", "r/helper.py", "u/verdict.py", "u/deep.py", "doc/counting.md", "u/pkg/sub.py"} <= set(prot),
           "closure holds the list, a same-dir import, a function-local import from an import root, its import, "
           "and a submodule named by `from pkg import sub`", prot)
        ok("u/free.py" not in prot and "r/worker.py" not in prot, "an unimported module stays free", prot)

        h, why = diff({"r/worker.py": "Z = 2\n", "r/rules.json": json.dumps({"walls": {"marker": 1}, "max_workers": 8})})
        ok(why == [], "a worker edit and an unprotected rules key pass", why)
        base_now[0] = h
        h, why = diff({"u/deep.py": "BAD = 1\n"})
        ok(len(why) == 1 and "imported by" in why[0], "an edit two imports deep from the Judge is refused", why)
        base_now[0] = h
        h, why = diff({"r/rules.json": json.dumps({"walls": {"marker": 0}, "max_workers": 8})})
        ok(len(why) == 1 and "'walls'" in why[0], "a change to a protected rules key is refused", why)
        base_now[0] = h
        h, why = diff({"doc/counting.md": "looser rules\n"})
        ok(len(why) == 1 and "counting rules" in why[0], "an edit to the counting rules is refused", why)
        base_now[0] = h
        h, why = diff({"r/judge.py": "import helper\nimport free\n", "u/free.py": "Y = 2\n"})
        ok(any(w.startswith("u/free.py") for w in why), "a module newly imported by the Judge is protected in the same diff", why)
        base_now[0] = h
        lax = {**SPEC, "protected": [e for e in SPEC["protected"] if e["path"] != "r/judge.py"]}
        for rel, text in {S.SPEC_REL: json.dumps(lax), "r/judge.py": "import helper\n# looser\n"}.items():
            write(root, rel, text)
        git(root, "add", "-A")
        h = git(root, "commit", "-qm", "c")
        why = S.check_protected(root, base_now[0], h)
        ok(any(w.startswith("r/judge.py") for w in why),
           "a candidate that drops the Judge from its own copy of the list is still refused (list read at base)", why)
        base_now[0] = h
        try:
            S.check_protected(root, "deadbeef" * 5, h, SPEC)
            ok(False, "an unknown base sha is UNMEASURED, not a pass")
        except S.Unmeasured:
            ok(True, "an unknown base sha is UNMEASURED, not a pass")


def test_ready():
    ok(S.ready(SPEC, {"walls": {"marker": {"enforce": True}}}) and "no walls.builder" in S.ready(SPEC, {"walls": {}})[0],
       "no builder wall: not ready")
    ok(len(S.ready(SPEC, {"walls": {"builder": {"enforce": True, "deny": ["/keys"]}}})) == 1,
       "a builder wall that misses the store: not ready")
    ok(S.ready(SPEC, {"walls": {"builder": {"enforce": True, "deny": ["/keys", "/store"]}}}) == [],
       "an enforced builder wall denying keys and store: ready")
    ok(len(S.ready(SPEC, {"walls": {"builder": {"enforce": False, "deny": ["/keys", "/store"]}}})) == 1,
       "an unenforced builder wall: not ready")
    ok(len(S.ready(SPEC, {"walls": {"builder": {"enforce": True, "deny": ["/keysX", "/store"]}}})) == 1,
       "a prefix that is not a parent directory does not count as denying")


def runs(passed, total=5, repeats=2, flaky=()):
    out = []
    for i in range(repeats):
        out.append({f"c{c}": (c < passed and not (c in flaky and i == 1)) for c in range(total)})
    return out


def test_promote():
    ids = [f"c{c}" for c in range(5)]
    frozen = {"E1": S.manifest_hash(ids), "E2": S.manifest_hash(ids)}
    base = {"frozen": frozen, "protected_ok": True}
    swap, why = S.promote(SPEC, {**base, "stage0": {"E1": runs(3), "E2": runs(3)}, "stage1": {"E1": runs(3), "E2": runs(4)}})
    ok(swap and not why, "a tie on E1 and a gain on E2 swaps (>=)", why)
    swap, why = S.promote(SPEC, {**base, "stage0": {"E1": runs(3), "E2": runs(3)}, "stage1": {"E1": runs(4, flaky=(3, 2)), "E2": runs(3)}})
    ok(not swap and "pass^2 2/5 < stage 0 3/5" in why[0], "pass once but not on every repeat counts as a fail (pass^k)", why)
    swap, why = S.promote(SPEC, {**base, "stage0": {"E1": runs(3)}, "stage1": {"E1": runs(5)}})
    ok(not swap and any(w.startswith("E2") for w in why), "a missing held-out set refuses", why)
    swap, why = S.promote(SPEC, {**base, "stage0": {"E1": runs(3, repeats=1), "E2": runs(3)}, "stage1": {"E1": runs(5, repeats=1), "E2": runs(3)}})
    ok(not swap and "fewer than 2 repeats" in why[0], "one repeat is inside the noise and refuses", why)
    swap, why = S.promote(SPEC, {**base, "stage0": {"E1": runs(3), "E2": runs(3)}, "stage1": {"E1": runs(3, total=4), "E2": runs(3)}})
    ok(not swap and "different case lists" in why[0], "a stage 1 that dropped a case refuses", why)
    swap, why = S.promote(SPEC, {**base, "stage0": {"E1": runs(1, total=4), "E2": runs(3)}, "stage1": {"E1": runs(4, total=4), "E2": runs(3)}})
    ok(not swap and "not the frozen one" in why[0], "both stages on a re-picked list (not the frozen one) refuses", why)
    swap, why = S.promote(SPEC, {**base, "protected_ok": False, "stage0": {"E1": runs(3), "E2": runs(3)}, "stage1": {"E1": runs(5), "E2": runs(5)}})
    ok(not swap and "protected" in why[0], "a better score with a grader edit refuses", why)


POOL = ([{"id": f"p{i}", "outcome": "pass", "leaf_class": "tool", "author": "B"} for i in range(6)]
        + [{"id": f"f{i}", "outcome": "escape", "leaf_class": "tool", "author": "B"} for i in range(3)]
        + [{"id": f"x{i}", "outcome": "pass", "leaf_class": "xml", "author": "B"} for i in range(2)]
        + [{"id": "mine", "outcome": "reverted", "leaf_class": "tool", "author": "A"}])


def test_draw():
    d1 = S.draw(SPEC, POOL, "seed-1", "A")
    ok(d1 == S.draw(SPEC, list(reversed(POOL)), "seed-1", "A"), "the draw is a function of the seed, not of row order", d1)
    ok(len(d1) == 3 + 1 and len({x[0] for x in d1}) == 3, "every stratum drawn once before any twice, capped at token_max", d1)
    ok("mine" not in d1, "a row authored by the building instance is never drawn", d1)
    ok(len(S.draw(SPEC, POOL, "s", "A", n=50)) == 4, "a request over token_max is capped (the owner's token sample)")


def test_cross():
    seed = "fixed-before-build"
    good = {"builder": "A", "target": "B", "seed": seed, "pool": POOL, "replays": S.draw(SPEC, POOL, seed, "A"),
            "labels": [{"case": c, "label": "FAIL" if c[0] == "f" else "PASS", "author": "store"}
                       for c in S.draw(SPEC, POOL, seed, "A")] + [{"case": "f1", "label": "FAIL", "author": "store"}],
            "held_out": [{"case": "h1", "author": "store"}], "mutants": [{"case": "m1", "author": "C"}]}
    ok(S.cross(SPEC, good) == [], "labels, held-out and mutants from others, a known-good, the seeded draw: pass", S.cross(SPEC, good))
    bad = {**good, "held_out": [{"case": "h1", "author": "A"}]}
    ok(any("authored by the building instance" in w for w in S.cross(SPEC, bad)), "a held-out case by A refuses")
    bad = {**good, "labels": [r for r in good["labels"] if r["label"] != "PASS"]}
    ok(any("must PASS" in w for w in S.cross(SPEC, bad)), "no known-good the Judge must pass refuses")
    bad = {**good, "labels": good["labels"][1:]}
    ok(any("no known outcome" in w for w in S.cross(SPEC, bad)), "a drawn replay with no label refuses (it cannot score)")
    bad = {**good, "replays": ["p0", "p1", "p2", "p3"]}
    ok(any("not the seeded draw" in w for w in S.cross(SPEC, bad)), "a hand-picked replay list refuses (selection bias)")
    bad = {**good, "target": "A"}
    ok(any("differ" in w for w in S.cross(SPEC, bad)), "building a Judge for yourself is not a cross-build")
    bad = {**good, "mutants": [{"case": "m1"}]}
    ok(any("no author" in w for w in S.cross(SPEC, bad)), "a mutant with no recorded author refuses")


def test_real_list():
    spec = S.load()
    prot = S.protected_set(spec, lambda p: Path(S.REPO, p).read_text(encoding="utf-8") if Path(S.REPO, p).is_file() else None)
    for p in ("src/RimMandrake/rimflow/relentless_wall.py", ".claude/agents/rm-judge.md",
              "design/RimMandrake/relentless_counting_rules_2026-11-01.md", "src/RimMandrake/rimflow/relentless_selfbuild.py"):
        ok(p in prot, f"the real list protects {p}")
    missing = [e["path"] for e in spec["protected"] if not Path(S.REPO, e["path"]).is_file()]
    ok(not missing, "every listed grader path exists in this tree (a renamed one would protect nothing)", missing)
    rules = json.loads((S.HERE / "relentless_rules.json").read_text(encoding="utf-8"))
    gone = [k for e in spec["protected_keys"] for k in e["keys"] if k not in rules]
    ok(not gone, "every protected rules key exists", gone)


for t in (test_protected, test_ready, test_promote, test_draw, test_cross, test_real_list):
    t()
print(("FAIL %d" % len(FAILS)) if FAILS else "PASS")
sys.exit(1 if FAILS else 0)
