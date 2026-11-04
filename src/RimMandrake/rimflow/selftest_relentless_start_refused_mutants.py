#!/usr/bin/env python3
"""Proves selftest_relentless's refused-start tests can see each clause they guard: every mutant below breaks one clause of
RELENTLESS_START_SILENCE_REFUSED_RETRY_LOOP in a temp copy of relentless.py and must turn its guarding test red with a FAIL
line (a crash is no red). Never touches the tree. A mutant that no longer applies is a failure by name: re-aim it at the new
text, never delete it. A guarding test that is gone stays silent, so this fails by name too (one was deleted 2026-11-03)."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HELD = "t_refused_start_is_held"
WIRED = "t_refused_start_reason_reaches_hold"
TESTS = [HELD, WIRED]

START = "return None if r.returncode == 0 else refusal_words(r)"
HOLD_WHY = '"start refused %d times: %s" % (cur["start_refusals"], str(why)[:200])'
PUT_DOWN = 'put_down = cur["status"] == "queued" and cur["start_refusals"] >= r.get("start_refused_put_down", 3)'
HOLD_STATUS = '"start_refused", now)\n                        cur["status"] = "held"'
UNHOLD = 'st["hold"].get("kind") == "start_refused":    # what refused is fixed, or its wait starts over\n            st.pop("start_refusals", None)'
LANDED = '            st.pop("start_refusals", None)      # the count is of refusals in a row\n'
CUT = '    head = out.splitlines()[0][:cap // 2]\n    return "%s ... %s" % (head, out[-(cap - len(head) - 5):])'

# name, [(text, replacement), ...], the tests that must go red
MUTANTS = [
    ("ledger_start keeps the tail again (the checker's mutant)", [(START, "return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]")], [WIRED]),
    ("ledger_start takes every exit for a refusal", [(START, "return refusal_words(r) or 'refused'")], [WIRED]),
    ("the hold's why loses the refusal", [(HOLD_WHY, '"start refused %d times" % cur["start_refusals"]')], [HELD, WIRED]),
    ("the hold's why keeps the refusal's tail", [(HOLD_WHY, '"start refused %d times: %s" % (cur["start_refusals"], str(why)[-200:])')], [WIRED]),
    ("refusal_words cuts the tail only", [(CUT, "    return out[-cap:]")], [HELD, WIRED]),
    ("refused starts are never put down", [(PUT_DOWN, 'put_down = False')], [HELD, WIRED]),
    ("a reserved item is not put down", [(PUT_DOWN, 'put_down = not reserved and cur["status"] == "queued" and cur["start_refusals"] >= r.get("start_refused_put_down", 3)')], [HELD]),
    ("put down means retired again", [(HOLD_STATUS, '"start_refused", now)\n                        cur["status"] = "retired"')], [HELD, WIRED]),
    ("unhold keeps the count", [(UNHOLD, 'st["hold"].get("kind") == "start_refused":\n            pass')], [HELD]),
    ("a landed start keeps the count", [(LANDED, "")], [HELD]),
]


def run(box, src, tests=TESTS):
    with open(os.path.join(box, "relentless.py"), "w", encoding="utf-8") as f:
        f.write(src)
    # the real Effects loads role_launch, whose `from rimflow import ...` needs the package beside the box's flat copy
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=os.path.dirname(HERE))
    p = subprocess.run([sys.executable, os.path.join(box, "selftest_relentless.py")] + list(tests), env=env, timeout=300,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=box)
    fails, at = {}, None
    for line in p.stdout.splitlines():
        if line.startswith("-- "):
            at = line[3:].strip()
        elif line.startswith("FAIL ") and at:
            fails.setdefault(at, []).append(line)
    return p.returncode, fails, p.stdout


def main():
    with open(os.path.join(HERE, "relentless.py"), encoding="utf-8") as f:
        real = f.read()
    box = tempfile.mkdtemp(prefix="rl-mut-")
    bad = 0
    try:
        for name in os.listdir(HERE):       # abspath, not realpath, in HERE: the copy finds its own relentless.py first
            if name not in ("relentless.py", "__pycache__"):
                os.symlink(os.path.join(HERE, name), os.path.join(box, name))
        code, fails, out = run(box, real)
        gone = [t for t in TESTS if "-- %s" % t not in out]
        if code or fails or gone:
            print("FAIL the code as it stands shows nothing: exit %d, red %s, tests gone %s\n%s" % (code, sorted(fails), gone, out[-1500:]))
            return 1
        print("ok   the code as it stands is green on %d tests" % len(TESTS))
        for name, edits, want in MUTANTS:
            missing = [old for old, _ in edits if real.count(old) != 1]
            if missing:
                print("FAIL mutant no longer applies (re-aim it): %s: %r" % (name, missing[0][:70]))
                bad += 1
                continue
            src = real
            for old, new in edits:
                src = src.replace(old, new)
            # one process per test: a mutant that crashes the first after its FAIL line must not silence the second
            fails, out = {}, ""
            for t in want:
                _, red, said = run(box, src, [t])
                fails.update(red)
                out += said
            quiet = [t for t in want if t not in fails]
            if quiet:
                print("FAIL mutant stayed green: %s: silent: %s, red: %s\n%s" % (name, quiet, sorted(fails), out[-800:]))
                bad += 1
            else:
                print("ok   red: %s -> %s" % (name, ", ".join(sorted(fails))))
    finally:
        shutil.rmtree(box, ignore_errors=True)
    print("selftest_relentless_start_refused_mutants: %s" % ("FAIL %d" % bad if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
