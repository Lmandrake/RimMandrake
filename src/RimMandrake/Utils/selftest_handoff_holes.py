#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_HARDEN_HANDOFF_CHECK_FOUR_HOLES_CODEX_FOUND: four holes in handoff.py's gate that
Codex's full-file review found on 2026-11-18, one case each.

    python3 src/RimMandrake/Utils/selftest_handoff_holes.py      # exit 0 and "PASS n/n"
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["RIMFLOW_SEAT"] = "BENCH"
import handoff as H  # noqa: E402

RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))


def doc(half_done, filed="none"):
    parts = ["# X — READ FIRST on wake", ""]
    for t, _p in H.JUDGEMENT_SECTIONS:
        parts += ["## %s" % t, "", half_done if t.startswith("What is half-done") else "nothing", ""]
    parts += ["## Filed and still open (1) — the next seat's queue", "", filed, "",
              "## Game / bridge / tree state at wrap", "", "- ok", ""]
    p = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    p.write("\n".join(parts))
    p.close()
    return p.name


def unaccounted(path, ids):
    real = H.open_this_window
    try:
        H.open_this_window = lambda since_ts, world=None: list(ids)
        probs = H.gates(None, path, doing_is_fatal=True)
    finally:
        H.open_this_window = real
    return [i for i in ids if any(i in p for p in probs)]


def hole_one_discharge():
    a = "RIMMANDRAKE_BUILD_SANDBOX_THING_HALF_DONE"
    p = doc("nothing", filed="- `%s` — doing" % a)
    check(unaccounted(p, [a]) == [a], "a doing item named only in the auto-listed queue is still unaccounted for")
    p = doc("- `%s_LONGER` — doing; NEXT: finish it" % a)
    check(unaccounted(p, [a]) == [a], "an id inside a longer id does not account for it")
    p = doc("- `%s` — parked at step 2" % a)
    check(unaccounted(p, [a]) == [a], "a half-done line without NEXT: does not account for it")
    p = doc("- `%s` — parked at step 2; NEXT: run the probe" % a)
    check(unaccounted(p, [a]) == [], "its own half-done pointer with a NEXT: accounts for it")


def hole_two_tree():
    check(H.tree_lines(run=lambda *a, **k: None) is None, "a git status that could not run is UNMEASURED (None)")

    class R:
        returncode, stdout, stderr = 128, "", "fatal: not a git repository"
    check(H.tree_lines(run=lambda *a, **k: R()) is None, "a failed git status is UNMEASURED, never a clean tree")

    class OK:
        returncode, stdout, stderr = 0, " M a.py\n?? Transient/x.md\n", ""
    check(H.tree_lines(run=lambda *a, **k: OK()) == [" M a.py"], "a good git status lists the dirt (Transient/ apart)")
    p = doc("- `X_Y_Z` — doing; NEXT: x")
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n%s\n" % H.TREE_UNMEASURED)
    check(any("tree" in s.lower() and "unmeasured" in s.lower() for s in H.todo_scan(p)),
          "--check refuses a handoff whose tree state is UNMEASURED")


def hole_three_since():
    head = H.sh("git", "log", "-1", "--format=%h")
    got = H.window_start(head, "2000-01-01T00:00:00Z")
    want = H._to_utc_z(H.sh("git", "log", "-1", "--format=%cI", head))
    check(got == want and got != "2000-01-01T00:00:00Z", "--since moves the ledger window to that commit's time")
    check(H.window_start(None, "2026-11-18T00:00:00Z") == "2026-11-18T00:00:00Z",
          "no --since keeps the previous handoff's time")


def hole_four_overwrite():
    d = tempfile.mkdtemp(prefix="handoff_out_")
    first = H.handoff_out("BENCH", d, stamp="202611181500")
    open(first, "w").write("filled")
    second = H.handoff_out("BENCH", d, stamp="202611181500")
    check(second and second != first and open(first).read() == "filled",
          "a second skeleton in the same minute never replaces the first (%s)" % os.path.basename(second or "None"))


def build_writes_twice():
    """build() itself, twice in one minute into a scratch handoffs dir: two files, the first untouched, each headed by
    its own name (the stamp the skeleton's heading carries). ./game is never run: its reading is stubbed."""
    d = tempfile.mkdtemp(prefix="handoff_build_")
    real = (H.HANDOFFS, H.sh, H.tree_lines)
    try:
        H.HANDOFFS = d
        H.sh = lambda *a, **k: "" if str(a[0]).endswith("game") else real[1](*a, **k)
        H.tree_lines = lambda run=None: None
        first = H.build(None, "2026-11-18T00:00:00Z", None)
        open(first, "a").write("FILLED BY THE WINDOW\n")
        second = H.build(None, "2026-11-18T00:00:00Z", None)
    finally:
        H.HANDOFFS, H.sh, H.tree_lines = real
    stem = lambda p: os.path.basename(p)[:-3]  # noqa: E731
    check(first != second and "FILLED BY THE WINDOW" in open(first).read(),
          "build() twice in a minute writes two skeletons and keeps the first")
    check(all(open(p).readline().startswith("# %s " % stem(p)) for p in (first, second)),
          "each skeleton is headed by its own name")
    check(H.TREE_UNMEASURED in open(second).read(), "a skeleton written while git status fails says UNMEASURED")


def main():
    for f in (hole_one_discharge, hole_two_tree, hole_three_since, hole_four_overwrite, build_writes_twice):
        try:
            f()
        except Exception as e:  # noqa: BLE001 - an absent helper on the base is a red case, said by name
            check(False, "%s raised %s: %s" % (f.__name__, type(e).__name__, e))
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(RESULTS) else "FAIL", passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
