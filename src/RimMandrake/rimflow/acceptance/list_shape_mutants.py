#!/usr/bin/env python3
"""list_shape_mutants.py: planted faults in the Shape stage; selftest_list_shape.py must go red on each.

Item RIMMANDRAKE_BUILD_SHAPE_STAGE_CHECK_TESTS_THE_NEED_NOT_PAPER (mutate-your-checker). Each mutant is one realistic
fault in list_shape.py, the lane's Shape lines in list_dispatch.py, the `shape` verb in model.py, `rimflow shape` in
cli.py, or the Shape brief. The selftest must FAIL on it by its own FAIL line; the acceptance script's reading is shown
beside it. The unmutated control must pass both first. Files are mutated IN PLACE (cli.py imports from its own folder)
and restored in `finally`; the run ends by proving every byte is back. Predictions were written before the first run:
every mutant CAUGHT by the selftest except "the brief loses the fooled_by question" (predicted MISSED: the brief's JSON
example still says fooled_by). First run, 2026-11-23: 20 of 22; that one and "a route with no resumes is a hand-over"
(not predicted; the acceptance script caught it) were MISSED. The selftest then gained a check for each clause the page
states (empty resumes; the question's own words), so those two are fitted, not independent.

    python3 src/RimMandrake/rimflow/acceptance/list_shape_mutants.py      exit 0: control green, every mutant caught
"""
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
TEST = os.path.join(RIMFLOW, "selftest_list_shape.py")
ACCEPT = os.path.join(HERE, "step4_shape_accept.py")
LS, LD, MODEL, CLI, BRIEF = ("list_shape.py", "list_dispatch.py", "model.py", "cli.py", "roles/list_shape.md")

MUTANTS = [
    (LS, "weak makes a stop", 'return {"shaped": bool(parts) and not unshaped,',
     'return {"shaped": bool(parts) and not unshaped and not weak,'),
    (LS, "a route with no resumes is a hand-over", '            and bool(_text(r.get("resumes"))))', ')'),
    (LS, "a route to anyone is a hand-over", 'r.get("who") in ROUTES', 'bool(r.get("who"))'),
    (LS, "an unreadable check counts", 'return bool(_text(text)) and LE.parse(text)["kind"] != "unreadable"',
     'return bool(_text(text))'),
    (LS, "an empty split is shaped", 'return {"shaped": bool(parts) and not unshaped,', 'return {"shaped": not unshaped,'),
    (LS, "a routed part holds", '            fails += 1\n            r = p["route"]', '            r = p["route"]'),
    (LS, "unmeasured reads holds", 'return (1 if fails else 2 if blind else 0), lines', 'return (1 if fails else 0), lines'),
    (LS, "no parts holds", 'return 2, ["the item has no parts to check"]', 'return 0, ["the item has no parts to check"]'),
    (LS, "old items enter by themselves", '    if filed is None or filed < frm:', '    if filed is None:'),
    (LS, "the grace is ignored", '    if now - filed < grace:', '    if False:'),
    (LS, "a many-part item takes its first check only", '    return HOLDS_CMD % iid', '    return checks[0]'),
    (LS, "the step-1 gate is skipped per part", 'seen, refusal = gate(q["effect"], _text(p.get("holds_why")))',
     'seen, refusal = {"verdict": "fails"}, None'),
    (LS, "naming is ignored", '    if item.get("named"):', '    if False:'),
    (LD, "a large Shape run counts as a Work run",
     'work = [a for a in fresh if not (a.get("kind") == "shape" and it.get("shape_size") == "large")]', 'work = list(done)'),
    (LD, "a dead Shape run is launched again", '            if shape:\n                stop("Shape run',
     '            if False:\n                stop("Shape run'),
    (LD, "the account gate skips Shape runs", '        if not account[0]:', '        if not account[0] and not shape:'),
    (LD, "a route is ignored", '            elif it.get("route"):', '            elif False:'),
    (LD, "a route beside a failing check is ignored", '        if it.get("route"):     # an open routed part',
     '        if False:     # an open routed part'),
    (LD, "a Shape run gets the Work brief", '        if row.get("kind") == "shape":\n            import list_shape',
     '        if False:\n            import list_shape'),
    (LD, "live Shape runs fill no slot",
     '                     if (items[i] or {}).get("effect") or (items[i] or {}).get("shape_due"))',
     '                     if (items[i] or {}).get("effect"))'),
    (LD, "a due item never leaves a refused or heavy adoption", '            if (refused or heavy) and it.get("shape_due")',
     '            if False and it.get("shape_due")'),
    (LD, "gather drops due beside a script", '"shape_due": sdue,', '"shape_due": sdue and not acc,'),
    (LD, "a passed wait holds a due item", '            if wu > now or not shape:\n', '            if True:\n'),
    (LD, "a passed wait launches Work", '            if wu > now or not shape:\n', '            if wu > now:\n'),
    (LD, "a re-shape starts no new count", ' if sat and it.get("shape_unit") not in own else done', ' if False else done'),
    (LD, "the item's own run starts a new count", ' if sat and it.get("shape_unit") not in own else done', ' if sat else done'),
    (LD, "a run the lane did not launch starts a new count",
     ' | set(run.get("live") or []) | set(run.get("ended") or [])', ''),
    (LD, "a stop says a check None fails", '            if it.get("effect") else "%s: no program', '            if True else "%s: no program'),
    (LS, "status hides an item due by age", 'x.shape or x.shape_named or due(facts(x), cfg, now)[0])]', 'x.shape or x.shape_named)]'),
    (MODEL, "the shaping unit is not replayed", '"unit": ev.get("role_unit")}', '"unit": None}'),
    (MODEL, "the derived check is not replayed", '            item.effect, item.effect_seen = chk, (ev.get("seen") if chk else None)',
     '            pass'),
    (CLI, "the write drops the item check", '    ev.update(fields)\n    _emit(ev, w, quiet=True)\n    print("%s: shaped',
     '    ev.update(fields)\n    ev.pop("check", None)\n    _emit(ev, w, quiet=True)\n    print("%s: shaped'),
    (BRIEF, "the brief loses the fooled_by question", 'Beside it, its fooled_by line: "what would pass\n     this check and leave the need unmet?"',
     'Beside it, a line.'),
]


def run(path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=900, env=env,
                       stdin=subprocess.DEVNULL)
    out = r.stdout + r.stderr
    return r.returncode, [ln for ln in out.splitlines() if ln.startswith("FAIL ") or ln.startswith("FAIL  ")], out


def main():
    files = sorted(set(m[0] for m in MUTANTS))
    orig = {f: open(os.path.join(RIMFLOW, f), encoding="utf-8").read() for f in files}
    digest = {f: hashlib.sha256(t.encode()).hexdigest() for f, t in orig.items()}
    shutil.rmtree(os.path.join(RIMFLOW, "__pycache__"), ignore_errors=True)
    for path in (TEST, ACCEPT):
        rc, fails, out = run(path)
        if rc != 0:
            print("CONTROL RED: the unmutated %s fails, so no mutant result means anything\n%s"
                  % (os.path.basename(path), out[-2000:]))
            return 3
    print("control  green (selftest and acceptance)")
    missed = []
    try:
        for f, name, old, new in MUTANTS:
            src = orig[f]
            if src.count(old) != 1:
                print("NOT APPLIED  %s: its anchor in %s is %s" % (name, f, "absent" if not src.count(old) else "not unique"))
                missed.append(name)
                continue
            with open(os.path.join(RIMFLOW, f), "w", encoding="utf-8") as fh:
                fh.write(src.replace(old, new))
            rc, fails, _ = run(TEST)
            arc, afails, _ = run(ACCEPT)
            caught = rc != 0 and bool(fails)
            print("%-8s %-46s acceptance %-5s %s" % ("CAUGHT" if caught else "MISSED", name,
                                                     "red" if arc != 0 and afails else "green",
                                                     ("-- " + fails[0][5:110]) if fails else ""))
            if not caught:
                missed.append(name)
            with open(os.path.join(RIMFLOW, f), "w", encoding="utf-8") as fh:
                fh.write(src)
    finally:
        for f, t in orig.items():
            with open(os.path.join(RIMFLOW, f), "w", encoding="utf-8") as fh:
                fh.write(t)
    back = all(hashlib.sha256(open(os.path.join(RIMFLOW, f), encoding="utf-8").read().encode()).hexdigest() == digest[f]
               for f in files)
    print("restored %s" % ("byte-identical" if back else "NOT IDENTICAL: restore %s from git" % ", ".join(files)))
    print("%d of %d mutants caught%s" % (len(MUTANTS) - len(missed), len(MUTANTS),
                                         (": missed " + "; ".join(missed)) if missed else ""))
    return 0 if back and not missed else 1


if __name__ == "__main__":
    sys.exit(main())
