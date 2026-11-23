#!/usr/bin/env python3
"""follow_through_mutants.py - plant faults in a copy of follow_through.py and see the checks go red.

Page: design/specs/2026-11-23-follow-through-audit/boundary.md. The checks: selftest_follow_through.py and
src/RimMandrake/rimflow/acceptance/step5_follow_through_accept.py. Each mutant is one realistic fault; a mutant whose
anchor is not found fails by name (it never reads as caught). An unmutated copy runs first and must be green in both.
The copy is loaded under the module's own name before the check runs, and its __file__ is asserted.

    python3 src/RimMandrake/Utils/follow_through_mutants.py      exit 0: control green, every mutant red
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(HERE, "follow_through.py")
CHECKS = (os.path.join(HERE, "selftest_follow_through.py"),
          os.path.join(REPO, "src", "RimMandrake", "rimflow", "acceptance", "step5_follow_through_accept.py"))
HANG_S = 300     # hang guard for one check run (the selftest takes about 2 s)

MUTANTS = [
    ("sample ignores the seed", 'rng = random.Random("%s|%s" % (seed, name))', 'rng = random.Random(name)'),
    ("sample turns could-not-read into []", '            out[name] = None\n            continue\n        needs = list',
     '            out[name] = []\n            continue\n        needs = list'),
    ("rates counts moved as followed", 'FOLLOWED = ("outcome", "disposed")', 'FOLLOWED = ("outcome", "disposed", "moved")'),
    ("the headline is the higher rate", 'else min(by.values())', 'else max(by.values())'),
    ("a stream with no verdicts reads 0", '        if not counted:\n            by[name] = None\n            unm.append(name)',
     '        if not counted:\n            by[name] = 0.0'),
    ("an unknown verdict is swallowed", '        if bad:\n            raise ValueError', '        if False:\n            raise ValueError'),
    ("no closed item reads share 0", 'return {"share": None, "closed": len(closed), "hands_off": ho}',
     'return {"share": 0.0 if not closed else None, "closed": len(closed), "hands_off": ho}'),
    ("an unreadable act count is guessed as 0", 'if not closed or any(i.get("window_acts") is None for i in closed):',
     'if not closed:'),
    ("OWNER with no ranBy reads as the window", 'WINDOW_SEATS = ("BENCH", "CONDUCTOR")',
     'WINDOW_SEATS = ("BENCH", "CONDUCTOR", "OWNER")'),
    ("a launched run reads as the window", '    if str(ev.get("role_unit") or "").strip():\n        return False\n',
     '    pass\n'),
    ("the pipe need is the last note, not the first", 'if not LEFT_OPEN_RX.match(text) or e["id"] in seen:',
     'if not LEFT_OPEN_RX.match(text):'),
    ("a mention of LEFT OPEN counts", 'if not LEFT_OPEN_RX.match(text)', 'if "LEFT OPEN:" not in text.upper()'),
    ("machine text is kept as his typing", 'sent = [m for m in msgs if machine.match((m["text"] or "").strip())]',
     'sent = []'),
    ("every open debt reads ripe", '        if now - ripe > RIPE_S:', '        if True:'),
    ("a wait looked at since still counts", 'if not any(_t(e) > tw for e in evs):', 'if True:'),
    ("judged skips the evidence line", 'or not str(x.get("evidence") or "").strip()]', ']'),
    ("judged skips the page", '    if page != render(rec):', '    if False:'),
    ("sample --write overwrites verdicts", '            if has_verdict(old):', '            if False:'),
    ("an unjudged rate prints 0%", 'return "UNMEASURED (not judged yet)" if x is None else',
     'return "0%" if x is None else'),
    ("the tick launches again after a run", '    elif runs["n"]:\n', '    elif False:\n'),
    ("a dry tick launches", 'rc, text = (fx.get("launch") or launch)(date, rid, apply)',
     'rc, text = (fx.get("launch") or launch)(date, rid, True)'),
    ("the tick works weeks before the first", '    if date < FIRST_WEEK:', '    if False:'),
    ("the planted need's hours are minutes", 'round((te - t0) / 3600.0, 1)', 'round((te - t0) / 60.0, 1)'),
    ("the week starts on the date", 's = d - dt.timedelta(days=7)', 's = d'),
]

RUNNER = r"""
import importlib.util, os, runpy, sys
repo = sys.argv[3]
for p in (os.path.join(repo, "src", "RimMandrake", "Utils"), os.path.join(repo, "src", "RimMandrake", "rimflow"),
          os.path.join(repo, "src", "RimMandrake")):
    sys.path.insert(0, p)
spec = importlib.util.spec_from_file_location("follow_through", sys.argv[1])
m = importlib.util.module_from_spec(spec)
sys.modules["follow_through"] = m
spec.loader.exec_module(m)
assert m.__file__ == sys.argv[1], m.__file__
# the copy lives in a scratch folder: its repo paths are the real repo's
m.REPO, m.HERE = repo, os.path.join(repo, "src", "RimMandrake", "Utils")
m.RIMFLOW = os.path.join(repo, "src", "RimMandrake", "rimflow")
m.PROBE = os.path.join(repo, "src", "RimMandrake", "Utils", "probe_his_words.py")
m.BRIEF = os.path.join(m.HERE, "follow_through_reader.md")
sys.argv = [sys.argv[2]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def run_checks(copy):
    """-> {check: "green" | "red" | "broke"}: red only on the check's own FAIL line."""
    out = {}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for c in CHECKS:
        try:
            r = subprocess.run([sys.executable, "-c", RUNNER, copy, c, REPO], capture_output=True, text=True, timeout=HANG_S,
                               env=env, cwd=REPO)
        except subprocess.TimeoutExpired:
            out[os.path.basename(c)] = "broke"
            continue
        text = r.stdout + r.stderr
        if r.returncode == 0 and ("ALL PASS" in text or "PASS 15/15" in text):
            out[os.path.basename(c)] = "green"
        elif r.returncode != 0 and ("FAIL " in text):
            out[os.path.basename(c)] = "red"
        else:
            out[os.path.basename(c)] = "broke"
    return out


def main():
    src = open(SRC, encoding="utf-8").read()
    top = tempfile.mkdtemp(prefix="ft_mutants_")
    bad = 0
    try:
        copy = os.path.join(top, "follow_through.py")
        shutil.copy(SRC, copy)
        ctl = run_checks(copy)
        print("control (unmutated): %s" % ctl)
        if set(ctl.values()) != {"green"}:
            print("HARNESS BROKEN: the control is not green; no mutant result counts")
            return 2
        for name, old, new in MUTANTS:
            if src.count(old) != 1:
                print("NOT APPLIED  %s (anchor found %d times)" % (name, src.count(old)))
                bad += 1
                continue
            with open(copy, "w", encoding="utf-8") as f:
                f.write(src.replace(old, new))
            res = run_checks(copy)
            caught = "red" in res.values() and "broke" not in res.values()
            bad += 0 if caught else 1
            print("%s  %s  %s" % ("CAUGHT    " if caught else "NOT CAUGHT", name, res))
    finally:
        shutil.rmtree(top, ignore_errors=True)
    print("%d of %d mutants caught" % (len(MUTANTS) - bad, len(MUTANTS)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
