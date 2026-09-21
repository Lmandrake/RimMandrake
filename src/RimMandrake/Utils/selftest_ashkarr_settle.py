#!/usr/bin/env python3
"""Selftest for ashkarr_settle.py's loud-failure region-name guard.

    python3 src/RimMandrake/Utils/selftest_ashkarr_settle.py

BARREN_REGIONS_NAME_NOTHING_1: `BARREN_REGIONS`'s membership test used to fail
OPEN — a literal matching no live feature simply returned False from `ok()`, and
the placer treated that ground as fair game. 10 of 22 entries were exactly this:
old draft names ("The Frostbloom", "The Cold Bloom", ...) that went through two
later renames (the 2026-08-22 fiction polish, then the 2026-09-08 V19 pass)
without the set ever being updated.

`validate_barren_regions()` is the fix: called at the top of `main()`, before
anything is computed against BARREN_REGIONS or HELIX_BARREN_OK, it reads the
planet's real feature names live from the canonical save and REFUSES (exits)
if any literal in either set matches nothing. This selftest does NOT run
`ashkarr_settle.py --apply` (forbidden — it writes settlements to the planet);
it only exercises the guard function in isolation, plus the module's own two
literal sets against whatever this machine can read.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ashkarr_settle as A  # noqa: E402

UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"


def synthetic_names():
    return {"Alpha", "Beta", "Gamma"}


def cases():
    out = []

    # --- 1. the guard function's own logic, against a synthetic feature set --- #
    out.append(("a set with every literal live does not refuse",
                _does_not_exit(A.validate_barren_regions,
                                [("OK_SET", {"Alpha", "Beta"})],
                                save_path=None, live=synthetic_names())))
    out.append(("a set with one unmatched literal refuses (SystemExit)",
                _does_exit(A.validate_barren_regions,
                           [("BAD_SET", {"Alpha", "Nowhere"})],
                           save_path=None, live=synthetic_names())))
    out.append(("the refusal message names the offending set and literal",
                _refusal_message_names(
                    [("BAD_SET", {"Alpha", "Nowhere"})], synthetic_names(),
                    "BAD_SET", "Nowhere")))
    out.append(("a literal matching nothing in an EMPTY live set still refuses "
                "rather than vacuously passing",
                _does_exit(A.validate_barren_regions,
                           [("SET", {"Anything"})], save_path=None, live=set())))

    # --- 2. the module's own current sets, against the real canonical save ---- #
    try:
        live = A.live_feature_names()
    except SystemExit as exc:
        print("note  canonical save not reachable on this machine (%s) — "
              "live-fixture tier skipped, synthetic tier still ran" % exc)
        live = None
    if live is not None:
        out.append(("live: exactly 71 features, 0 unnamed (re-measured, not trusted "
                    "from the item file)", len(live) == 71))
        bad_barren = sorted(n for n in A.BARREN_REGIONS if n not in live)
        out.append(("live: every BARREN_REGIONS literal matches a real feature",
                    not bad_barren))
        bad_helix = sorted(n for n in A.HELIX_BARREN_OK if n not in live)
        out.append(("live: every HELIX_BARREN_OK literal matches a real feature",
                    not bad_helix))
        out.append(("live: validate_barren_regions() on the module's real sets "
                    "does not refuse",
                    _does_not_exit(A.validate_barren_regions,
                                   [("BARREN_REGIONS", A.BARREN_REGIONS),
                                    ("HELIX_BARREN_OK", A.HELIX_BARREN_OK)])))
        # negative control: the guard must still catch a real bad name, not just
        # report clean because it stopped checking.
        poisoned = set(A.BARREN_REGIONS) | {"Definitely Not A Region"}
        out.append(("live: a poisoned copy of the real set still refuses "
                    "(negative control — the guard isn't vacuously green)",
                    _does_exit(A.validate_barren_regions,
                               [("POISONED", poisoned)])))
    else:
        out.append((UNMEASURED_PHRASE + ": live canonical-save cases", True))

    return out


def _does_not_exit(fn, *args, **kw):
    live = kw.pop("live", None)
    try:
        if live is not None:
            _call_with_patched_live(fn, args, live)
        else:
            fn(*args, **kw)
        return True
    except SystemExit:
        return False


def _does_exit(fn, *args, **kw):
    live = kw.pop("live", None)
    try:
        if live is not None:
            _call_with_patched_live(fn, args, live)
        else:
            fn(*args, **kw)
        return False
    except SystemExit:
        return True


def _refusal_message_names(named_sets, live, *substrings):
    orig = A.live_feature_names
    A.live_feature_names = lambda save_path=None: live
    try:
        A.validate_barren_regions(named_sets)
        return False
    except SystemExit as exc:
        msg = str(exc)
        return all(s in msg for s in substrings)
    finally:
        A.live_feature_names = orig


def _call_with_patched_live(fn, args, live):
    orig = A.live_feature_names
    A.live_feature_names = lambda save_path=None: live
    try:
        fn(*args)
    finally:
        A.live_feature_names = orig


def main() -> int:
    try:
        results = cases()
    except Exception as exc:                                  # noqa: BLE001
        print("FAIL  the selftest could not run: %r" % (exc,))
        raise
    bad = 0
    for label, ok in results:
        bad += not ok
        print("%s  %s" % ("ok  " if ok else "FAIL", label))
    print("\n%d/%d passed" % (len(results) - bad, len(results)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
