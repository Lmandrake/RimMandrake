#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_TYPE_SIX_MORE_CONSUMABLES_READERS_IN_LIVE_LANES.

Every promise on `design/specs/2026-11-19-consumable-readers/boundary.md` is owed a test of its name in
`selftest_pipeline_control.py`. This breaks each promise on purpose, one at a time, in a private copy of
src/RimMandrake/{rimflow,Utils,contracts} (a temp dir; the real files are never edited): the reader stops reading the
control store (or pipe forgets the consumable). First the unbroken copy must pass every named test, else a test that
always fails would read as a catch. Then each break must turn its named test red.

  exit 0  PASS: every break rejected by its named test
  exit 1  FAIL: a break slipped past (its named test passed), each named
  exit 3  COULD NOT LOOK: a break no longer matches its file exactly once, the copy failed, or the unbroken copy does
          not pass a named test (cause named); not a verdict about the tests
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
SRC = os.path.dirname(RIMFLOW)

# promise -> [(file in rimflow, the exact text, the broken text)]
BREAKS = {
    "ingame-runs-read-the-store": [("maturation_dispatch.py",
                                    'PC.used(mod, "ingame_runs_visit", len([x for x in ours if x is not retry]))',
                                    'len([x for x in ours if x is not retry])')],
    "steward-runs-read-the-store": [("maturation_autonomy.py", 'n, most = PC.used(row["mod"], "steward_runs", n), ',
                                     'n, most = n, ')],
    "launch-tries-read-the-store": [("maturation_autonomy.py", 'return PC.used(mod, "launch_tries", int(tries or 1)) <',
                                     'return int(tries or 1) <')],
    "chain-runs-read-the-store": [("role_launch.py",
                                   'return PC.used(mod, "chain_runs_day", n), PC.limit(mod, "chain_runs_day", cap)',
                                   'return n, cap')],
    "refusals-read-the-store": [("refusal_contract.py",
                                 'n_refused, most = PC.used(item, "refusals", n_refused), PC.limit(item, "refusals", '
                                 'ITEM_ALARM_AT)', 'pass')],
    "stage-spend-reads-the-store": [("maturation_dispatch.py", "if stage not in PC.SPEND_RES or", "if True or")],
    "every-limit-read-goes-through-the-store": [
        ("maturation_dispatch.py", 'PC.used(mod, "ingame_runs_visit", len([x for x in ours if x is not retry]))',
         'len([x for x in ours if x is not retry])'),
        ("maturation_dispatch.py",
         'per = PC.limit(mod, "ingame_runs_visit", int(cfg.get("ingame_auto_runs_per_visit", 1)))',
         'per = int(cfg.get("ingame_auto_runs_per_visit", 1))')],
    "one-line-each-with-its-undo": [("pipeline_control.py", '    "launch_tries": ("tries",', '    "launch_tries_": ("tries",')],
}
DRIVER = r'''
import shutil, sys
sys.path.insert(0, ".")
import selftest_pipeline_control as T
root, st = T.fixture()
try:
    getattr(T, sys.argv[1])()
except Exception as e:      # a break that raises is a catch too, named
    T.FAILS.append("raised %s: %s" % (type(e).__name__, e))
shutil.rmtree(root, ignore_errors=True)
print("FAILS %d" % len(T.FAILS))
sys.exit(1 if T.FAILS else 0)
'''


def test_name(promise):
    return "t_" + promise.replace("-", "_")


def run(rimflow, promise):
    env = dict(os.environ, RM_UNDER_SELFTEST="1")
    for k in ("RM_CONTROL_DB",):
        env.pop(k, None)
    r = subprocess.run([sys.executable, "-c", DRIVER, test_name(promise)], cwd=rimflow, env=env,
                       capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or ["(no output)"]


def main():
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else list(BREAKS)
    tmp = tempfile.mkdtemp(prefix="consumable_breaks_")
    try:
        for d in ("rimflow", "Utils", "contracts"):     # the repo's layout: maturation.py finds Utils by REPO
            shutil.copytree(os.path.join(SRC, d), os.path.join(tmp, "src", "RimMandrake", d),
                            ignore=shutil.ignore_patterns("__pycache__"))
        rf = os.path.join(tmp, "src", "RimMandrake", "rimflow")
        for promise in only:
            rc, tail = run(rf, promise)
            if rc != 0:
                print("COULD NOT LOOK: the unbroken copy fails %s (%s)" % (test_name(promise), tail[0]))
                return 3
        slipped = []
        for promise in only:
            saved = {}
            for f, old, new in BREAKS[promise]:
                p = os.path.join(rf, f)
                saved.setdefault(p, open(p, encoding="utf-8").read())
                cur = open(p, encoding="utf-8").read()
                if cur.count(old) != 1:
                    print("COULD NOT LOOK: the break of %s matches %s %d times, not once" % (promise, f, cur.count(old)))
                    return 3
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(cur.replace(old, new))
            rc, tail = run(rf, promise)
            for p, text in saved.items():
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(text)
            print("%-42s %s  (%s)" % (promise, "RED" if rc != 0 else "GREEN: SLIPPED PAST", tail[0]))
            if rc == 0:
                slipped.append(promise)
        if slipped:
            print("FAIL: %d of %d breaks slipped past: %s" % (len(slipped), len(only), ", ".join(slipped)))
            return 1
        print("PASS: %d of %d breaks rejected by their named tests" % (len(only), len(only)))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
