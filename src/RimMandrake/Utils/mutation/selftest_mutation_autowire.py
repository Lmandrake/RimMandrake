#!/usr/bin/env python3
"""Class guard for NIGHTLY_COP_FIX_RED_YWAYLS_DPFF: a new selftest that imports a mutation target must reach that
target's mutants without anyone editing run_mutation.TARGETS. Twice (delegated_digest 2026-11-03, role_launch
2026-11-05) a hand-kept list missed a new importer and the nightly sweep went red on audit_targets.
The effective list (`tests_for`) is the hand list plus every importing selftest not in TARGET_EXCLUDE."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_mutation as M  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def effective(name, root):
    fn = getattr(M, "tests_for", None)
    return fn(name, root) if fn else list(M.TARGETS[name][1])


def main():
    # the live repo: every importing selftest (bar the deliberate exclusions) is in its target's effective list
    for name in M.TARGETS:
        mod = os.path.splitext(os.path.basename(M.TARGETS[name][0]))[0]
        eff = set(effective(name, M.REPO))
        miss = []
        for top in ("src/RimMandrake/Utils", "src/RimMandrake/rimflow"):
            for dp, _dn, fns in os.walk(os.path.join(M.REPO, top)):
                for fn in fns:
                    if not (fn.startswith("selftest_") and fn.endswith(".py")):
                        continue
                    rel = os.path.relpath(os.path.join(dp, fn), M.REPO).replace(os.sep, "/")
                    if rel in M.TARGET_EXCLUDE.get(name, {}) or rel in eff:
                        continue
                    try:
                        text = open(os.path.join(dp, fn), encoding="utf-8").read()
                    except (OSError, UnicodeDecodeError):
                        continue
                    if M._imports(text, mod):
                        miss.append(rel)
        check(not miss, "%s: every importing selftest reaches its mutants (missing %s)" % (name, sorted(miss)))

    # a planted importer is wired in with no TARGETS edit; an excluded one is not; the hand list comes first, once
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "src", "RimMandrake", "rimflow")
        os.makedirs(d)
        open(os.path.join(d, "selftest_planted_new.py"), "w").write("import os\nimport role_launch as RL\n")
        excl = sorted(M.TARGET_EXCLUDE.get("role_launch", {}))[0]
        open(os.path.join(td, excl), "w").write("import role_launch\n")
        eff = effective("role_launch", td)
        check("src/RimMandrake/rimflow/selftest_planted_new.py" in eff, "planted importer is wired in automatically")
        check(excl not in eff, "an importer in TARGET_EXCLUDE stays out")
        hand = list(M.TARGETS["role_launch"][1])
        check(eff[:len(hand)] == hand and len(eff) == len(set(eff)), "hand list first, no duplicates")
    if FAILS:
        print("%d failure(s)" % len(FAILS))
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
