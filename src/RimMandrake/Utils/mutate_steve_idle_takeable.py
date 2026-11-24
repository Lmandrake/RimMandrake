#!/usr/bin/env python3
"""mutate_steve_idle_takeable.py - the planted faults of selftest_steve_idle_takeable.py (mutate-your-checker).

Each mutant is one realistic fault in ops_watch.c_steve_takeable, maturation_dispatch.ingame_testq or the rules target,
planted in a COPY: a temp tree whose Utils/ and rimflow/ hold symlinks to every real file except the one mutated, which
is copied and edited there. The selftest copy runs from that tree, so ops_watch's HERE (resolve()) is the copy. The
control (no mutation) must PASS; each mutant must print the selftest's own FAIL line. A mutant whose anchor is not found
fails by name (it never applied). Prints the table, the count caught of the count planted, and exits 1 on any escape."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RF = HERE.parent / "rimflow"
TEST = "selftest_steve_idle_takeable.py"
OW, MD, RULES = "Utils/ops_watch.py", "rimflow/maturation_dispatch.py", "Utils/ops_watch_rules.json"

MUTANTS = [   # (name: the fault in words, file, anchor, replacement)
    ("filler on another mod reads busy", OW,
     'and (j.get("requested_by") != FILLER_BY or on_waiting(j, waiting))]', ']'),
    ("a run before the visit opened drains the check", OW,
     'and j.get("mod") in opened and fin >= opened[j["mod"]]:', 'and j.get("mod") in opened:'),
    ("an INVALID run drains the check", OW, 'if outcome_of(d) == "DONE" and', 'if outcome_of(d) and'),
    ("an unread in-game mod reads quiet", OW, '        if unread:\n            return {STEVE_TAKEABLE_KEY: U("nothing known',
     '        if False:\n            return {STEVE_TAKEABLE_KEY: U("nothing known'),
    ("a stale dispatch reading is believed", OW, 'or now - at > MATURATION_READING_MAX_AGE_S or', 'or'),
    ("the owner's gate is not his", OW, 'if state == "pending" and j.get("owner_gate") and', 'if False and'),
    ("a held mod's checks count", OW, 'if e.get("held") or e.get("blocked")', 'if e.get("blocked")'),
    ("a commissioned finish does not restart the clock", OW, 'if h == "stevedesktop" and fin > start and', 'if False and'),
    ("a job not ready yet reads busy", OW, 'and (state == "running" or ready(j))', ''),
    ("an unreadable hold reads as no hold", OW, 'if not isinstance(e, dict) or e.get("error") or e.get("hold_unreadable"):',
     'if not isinstance(e, dict) or e.get("error"):'),
    ("the dispatch counts an earlier visit's row as this visit's", MD,
     'if t and isinstance(r, dict) and r.get("_visit") == n}', 'if t and isinstance(r, dict)}'),
    ("the dispatch drops the owner's hold", MD, 'h = (holds or {}).get(OH.key(mod))', 'h = None'),
    ("the dispatch counts a check with no testq block", MD, 'if k in tq and isinstance(q, dict) and k not in ran:',
     'if k not in ran:\n                    q = q if isinstance(q, dict) else {"chains": [k]}'),
    ("the rule's line loosened to 60", RULES,
     '"key": "steve.idle_with_takeable_min", "op": ">", "value": 30,', '"key": "steve.idle_with_takeable_min", "op": ">", "value": 60,'),
    ("the rule raises no alarm", RULES,
     '"key": "steve.idle_with_takeable_min", "op": ">", "value": 30, "alarm": true,',
     '"key": "steve.idle_with_takeable_min", "op": ">", "value": 30, "alarm": false,'),
]


def tree(rel=None, anchor=None, repl=None):
    """-> a temp root mirroring the repo: every entry a symlink except the path down to Utils/ and rimflow/, which are
    dirs of symlinks; the selftest, ops_watch.py and maturation_dispatch.py copied (so HERE resolves into the copy),
    `rel` mutated. Returns the temp src/RimMandrake."""
    t = Path(tempfile.mkdtemp(prefix="mut_takeable_"))
    repo = HERE.parents[2]
    keep = {repo: {"src"}, repo / "src": {"RimMandrake"}, repo / "src" / "RimMandrake": {"Utils", "rimflow"},
            HERE: set(), RF: set()}
    for src, skip in keep.items():
        dst = t / src.relative_to(repo)
        dst.mkdir(parents=True, exist_ok=True)
        for p in src.iterdir():
            if p.name not in skip and p.name != "__pycache__":
                os.symlink(p, dst / p.name)
    rm = t / "src" / "RimMandrake"
    for rel_copy in {"Utils/" + TEST, OW, MD} | ({rel} if rel else set()):
        dst = rm / rel_copy
        dst.unlink()
        shutil.copy(HERE.parent / rel_copy, dst)
    if rel:
        p = rm / rel
        s = p.read_text(encoding="utf-8")
        if s.count(anchor) != 1:
            raise RuntimeError("anchor found %d times in %s" % (s.count(anchor), rel))
        p.write_text(s.replace(anchor, repl), encoding="utf-8")
    return t


def run(t):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(t / "pyc"))
    r = subprocess.run([sys.executable, str(t / "src" / "RimMandrake" / "Utils" / TEST)], capture_output=True, text=True, timeout=400, env=env)
    out = r.stdout + r.stderr
    fails = [ln for ln in out.splitlines() if ln.startswith("FAIL ")]
    return r.returncode, out, fails


def main():
    rows, escaped = [], 0
    t = tree()
    rc, out, fails = run(t)
    shutil.rmtree(t, ignore_errors=True)
    ok = rc == 0 and "selftest_steve_idle_takeable: PASS" in out and not fails
    print("%-62s %s" % ("control (no mutation)", "green" if ok else "RED: %s" % (fails[:1] or out[-300:])))  # cut-ok: test diagnostic display
    if not ok:
        print("mutate_steve_idle_takeable: the control is red; nothing below would mean anything")
        return 2
    for name, rel, anchor, repl in MUTANTS:
        try:
            t = tree(rel, anchor, repl)
        except RuntimeError as e:
            print("%-62s NOT APPLIED (%s)" % (name, e))
            escaped += 1
            continue
        rc, out, fails = run(t)
        shutil.rmtree(t, ignore_errors=True)
        mods = [ln for ln in out.splitlines() if ln.startswith("modules: ")]
        if not mods or any(not f.startswith(str(t)) for f in mods[0][9:].split()):
            print("%-62s HARNESS: the real module was imported (%s)" % (name, mods[:1]))
            escaped += 1
            continue
        own = [f for f in fails if " raised " not in f]     # the check's own FAIL line, not a crash
        caught = rc != 0 and bool(own)
        fails = own or fails
        rows.append((name, caught))
        escaped += 0 if caught else 1
        print("%-62s %s" % (name, "caught: %s" % fails[0][5:110] if caught else "ESCAPED (rc %d, %d FAIL)" % (rc, len(fails))))
    print("mutate_steve_idle_takeable: %d of %d planted faults caught" % (sum(c for _, c in rows), len(MUTANTS)))
    return 1 if escaped else 0


if __name__ == "__main__":
    sys.exit(main())
