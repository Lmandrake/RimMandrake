#!/usr/bin/env python3
"""selftest_extra_art_filed_rows_kept.py — a redraw that resizes a reference sprite must not make commission.csv stale.

Instance (item SELFTEST_FIX_EXTRA_ART_COMMISSION_UBZM, 2026-11-06): FACING_AUDIT_BUILD_REDRAW_BATCH installed a 256 px
RSW_Sacapillar redraw over the 512 px reference; plan() re-derived canvas 256 for the filed RM_Wastes jobs, and the nightly
selftest_extra_art_commission.py went red. A filed job cannot be refiled under its id (fill_queue refuses duplicates), so a
filed biome's rows are a record: plan() keeps them while they still match the biome's rows_sha.

Class check: every reference sprite reads as a different size (png_size patched); the table must still equal plan(), and
drift() must name the changed canvases. Counter-check: a biome whose rows_sha no longer matches is NOT kept, so check()
still sees it.

    python3 selftest_extra_art_filed_rows_kept.py                     # the current extra_art_commission.py: PASS
    python3 selftest_extra_art_filed_rows_kept.py --blob REV:PATH     # replay a past one, e.g.
        --blob b325fff525:src/RimMandrake/Utils/art/extra_art_commission.py   (re-derived canvas: must FAIL)
"""
from __future__ import annotations

import copy
import subprocess
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if "--blob" in sys.argv:
    blob = sys.argv[sys.argv.index("--blob") + 1]
    src = subprocess.run(["git", "show", blob], cwd=str(HERE.parents[3]), capture_output=True, text=True,
                         check=True).stdout
    E = types.ModuleType("extra_art_commission")
    E.__file__ = str(HERE / "extra_art_commission.py")
    sys.modules["extra_art_commission"] = E
    exec(compile(src, E.__file__, "exec"), E.__dict__)
    print(f"replaying extra_art_commission.py from {blob}")
else:
    import extra_art_commission as E  # noqa: E402

FAILS = []


def expect(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


table, state = E.read_table(), E.read_state()
expect(bool(table) and bool(state.get("biomes")), f"sanity: {len(table)} table rows, {len(state.get('biomes', {}))} "
       "filed biomes (the instrument can see a filed commission)")
defs = E.Defs()
real = E.png_size
E.png_size = lambda p: 1024 if real(p) != 1024 else 2048          # every reference redrawn at another size
stale = lambda errs: [e for e in errs if "is stale" in e]          # noqa: E731
errs = E.check(E.plan(defs), table, state, None)
expect(not stale(errs), "every reference resized: commission.csv still equals plan() for the filed biomes"
       + (f" ({stale(errs)[0][:160]})" if stale(errs) else ""))
if hasattr(E, "drift"):
    notes = E.drift(defs, table, state)
    expect(any("canvas" in n for n in notes), f"drift() names the resized canvases ({len(notes)} notes)")
b = next(iter(state["biomes"]))
bad = copy.deepcopy(state)
bad["biomes"][b]["rows_sha"] = "0" * 64
try:
    rows = E.plan(defs, table=table, state=bad)
except TypeError:                                                   # a plan() that never reads the filing
    rows = E.plan(defs)
expect(bool(stale(E.check(rows, table, bad, None))),
       f"{b} with a broken rows_sha is not kept: check() still reports the re-derived rows")
E.png_size = real
print("ALL PASS" if not FAILS else f"FAIL: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
