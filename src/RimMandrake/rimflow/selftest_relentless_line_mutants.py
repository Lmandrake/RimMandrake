#!/usr/bin/env python3
"""Proves selftest_relentless's enrol-line tests can see each clause they guard: every mutant below breaks one clause of
RELENTLESS_LINE_FIX_ONE_MOD_CLOGS_ALL in a temp copy of relentless.py and must turn its guarding test red with a FAIL line
(a crash is no red). Never touches the tree. A mutant that no longer applies is a failure by name: enrol changed, so
re-aim the mutant at the new text, never delete it."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = ["t_line_full_of_one_mod_still_leases_another", "t_parked_items_hold_no_place", "t_enrol_skips_taken_mod",
         "t_waiting_items_hold_no_line_place", "t_parked_system_items_hold_no_sys_room",
         "t_plain_queued_items_hold_their_places", "t_consulting_item_holds_no_line_place",
         "t_refused_start_holds_no_line_place", "t_incident_line_fills_every_place", "t_enrol_reads_store_once_per_line"]

COND = 'if now < st.get("start_again_at", 0) or st.get("not_before", 0) > now or help_pending(st):'
IN_TURN = "in_turn = [s for s in live if in_line(s) and not parked(store, fx, r, s, now, live)]"
QUEUED = "    queued = len(in_turn)\n"
SYS = 'sum(1 for s in in_turn if s["item"] in first))'
SYS_OLD = 'sum(1 for s in live if in_line(s) and s["item"] in first))'
TAKEN = 'for x in [s for s in live if s["status"] in HOLDS_A_PLACE] + in_turn:'
TAKEN_ALL = 'for x in [s for s in live if s["status"] in HOLDS_A_PLACE] + [s for s in live if in_line(s)]:'
HELD_ANY = "        return any(m in held for m in fx.item_mods(st))\n"
SKIP = "            if mods & taken:\n"
MODS_HELD_READ = "(store.states() if states is None else states)"

# name, [(text, replacement), ...], the tests that must go red
MUTANTS = [
    ("the count holds parked items again", [(QUEUED, "    queued = sum(1 for s in live if in_line(s))\n")],
     ["t_line_full_of_one_mod_still_leases_another", "t_incident_line_fills_every_place"]),
    ("a mod-blocked item is not parked", [(HELD_ANY, "        return False\n")],
     ["t_line_full_of_one_mod_still_leases_another", "t_incident_line_fills_every_place"]),
    ("everything is parked: max_queued means nothing", [(COND, "if True:")],
     ["t_plain_queued_items_hold_their_places"]),
    ("sys_room counts parked system items (the item's words, in the system lane)", [(SYS, SYS_OLD)],
     ["t_parked_system_items_hold_no_sys_room"]),
    ("a parked item shuts its mod", [(TAKEN, TAKEN_ALL)], ["t_waiting_items_hold_no_line_place"]),
    ("a wait holds a place", [(COND, 'if now < st.get("start_again_at", 0) or help_pending(st):')],
     ["t_waiting_items_hold_no_line_place"]),
    ("a consult holds a place", [(COND, 'if now < st.get("start_again_at", 0) or st.get("not_before", 0) > now:')],
     ["t_consulting_item_holds_no_line_place"]),
    ("a refused start holds a place", [(COND, 'if st.get("not_before", 0) > now or help_pending(st):')],
     ["t_refused_start_holds_no_line_place"]),
    ("enrol stops walking past taken mods", [(SKIP, "            if False:\n")], ["t_enrol_skips_taken_mod"]),
    ("parked() re-reads the store per queued item", [(IN_TURN, IN_TURN.replace(", live)]", ")]"))],
     ["t_enrol_reads_store_once_per_line"]),
    ("mods_held ignores the states it is given", [(MODS_HELD_READ, "store.states()")],
     ["t_enrol_reads_store_once_per_line"]),
    ("the whole enrol change of 36cbc9e5 put back", [
        ("def parked(store, fx, r, st, now, states=None):", "def parked(store, fx, r, st, now):"),
        (COND, 'if now < st.get("start_again_at", 0):'),
        ('held = mods_held(store, fx, st["item"], states)\n        return any', 'held = mods_held(store, fx, st["item"])\n        return any'),
        (IN_TURN + "\n" + QUEUED, "    queued = sum(1 for s in live if in_line(s) and not parked(store, fx, r, s, now))\n".lstrip()),
        (TAKEN + "\n            taken |= set(fx.item_mods(x))\n",
         'for x in live:\n            if x["status"] in HOLDS_A_PLACE or in_line(x):\n                taken |= set(fx.item_mods(x))\n'),
        (SYS, SYS_OLD),
        ("def mods_held(store, fx, item, states=None):", "def mods_held(store, fx, item):"),
        (MODS_HELD_READ, "store.states()"),
     ], ["t_waiting_items_hold_no_line_place", "t_parked_system_items_hold_no_sys_room",
         "t_consulting_item_holds_no_line_place", "t_enrol_reads_store_once_per_line"]),
]


def run(box, source):
    """Run the tests against `source` as relentless.py. -> (exit, {test: its FAIL lines})."""
    with open(os.path.join(box, "relentless.py"), "w", encoding="utf-8") as f:
        f.write(source)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, os.path.join(box, "selftest_relentless.py")] + TESTS, env=env, timeout=300,
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
        if code or fails:
            print("FAIL the code as it stands is red, so no mutant can show anything: exit %d %s\n%s" % (code, sorted(fails), out[-1500:]))
            return 1
        print("ok   the code as it stands is green on %d tests" % len(TESTS))
        for name, edits, want in MUTANTS:
            src = real
            missing = [old for old, _ in edits if src.count(old) != 1]
            for old, new in edits:
                src = src.replace(old, new)
            if missing:
                print("FAIL mutant no longer applies (enrol changed; re-aim it): %s: %r" % (name, missing[0][:70]))
                bad += 1
                continue
            code, fails, out = run(box, src)
            quiet = [t for t in want if t not in fails]
            if code != 1 or quiet:
                print("FAIL mutant stayed green: %s: exit %d, silent: %s, red: %s\n%s" % (name, code, quiet, sorted(fails), out[-800:] if code not in (0, 1) else ""))
                bad += 1
            else:
                print("ok   red: %s -> %s" % (name, ", ".join(sorted(fails))))
    finally:
        shutil.rmtree(box, ignore_errors=True)
    print("selftest_relentless_line_mutants: %s" % ("FAIL %d" % bad if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
