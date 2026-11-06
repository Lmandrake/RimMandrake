#!/usr/bin/env python3
"""selftest_dessic_install_check.py — the dessic install proof goes red when a clause breaks (DESSICATED_CORPSES_INSTALL_AFTER_PICKS).

Runs dessic_install_check.main() on the committed art ledger (must be 0, every LIVE slot proven), then on
in-memory mutants of it (no ledger copy is written; artledger.read_events is swapped for the mutant list):
  m1  the two art.py install events for Akk and Devourer deleted          -> UNLEDGERED, exit 1
  m2  Boarwolf's bulk-accept install event relabelled as a plain copy     -> UNLEDGERED, exit 1
  m3  a later ledger install puts other bytes on the Akk slot             -> UNLEDGERED, exit 1
  m4  the Akk file reads as other bytes on disk                           -> STALE, exit 1
  m5  no dessic binding events at all                                     -> BLIND, exit 2
  m6  the owner keeps on the live Akk/Devourer v2 removed                 -> their v1 renders STALE, exit 1
      (KEPT_OTHER passes a render only while an owner keep holds the slot; m0 pins it at 2)
The owner took v2 for these two on 2026-11-06, so v2 is the live picture and v1 the render passed over.
Each mutant must turn the named job red, and only the real ledger may pass.
"""
from __future__ import annotations

import builtins
import contextlib
import copy
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import artledger as A  # noqa: E402
import dessic_install_check as C  # noqa: E402

AKK = "swanimals/Akk/Akk_Dessicated.png"
AKK_SHA = "9277f69cc4028a9e3c808ad671c0e02962fb8df6baf4e13a0ba5a18d86c32a0b"
ART_PY_INSTALL_IDS = {"23df71ea06254f51b1d3", "b6d9977838ca4ef289fd"}   # Akk, Devourer v2 (2026-11-06)
OWNER_KEEP_IDS = {"72c0d32501617c4961c9", "dc30d35a897ea20009bf"}       # his keeps on those v2 pictures (2026-11-06)


def run(events):
    real_read = A.read_events
    A.read_events = lambda: copy.deepcopy(events)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            rc = C.main()
    finally:
        A.read_events = real_read
    return rc, out.getvalue()


def main() -> int:
    base = A.read_events()
    fails, seen = [], []

    def expect(name, rc, out, want_rc, want_text):
        ok = rc == want_rc and want_text in out
        seen.append(name)
        print(f"{'PASS' if ok else 'FAIL'} {name}: exit={rc} want={want_rc} '{want_text}' "
              f"{'seen' if want_text in out else 'MISSING'} | {out.strip().splitlines()[-1] if out.strip() else ''}")
        if not ok:
            fails.append(name)

    rc, out = run(base)
    expect("m0 real ledger", rc, out, 0, "KEPT_OTHER=2 LIVE=60 RETIRED=3")

    m1 = [e for e in base if e.get("id") not in ART_PY_INSTALL_IDS]
    assert len(base) - len(m1) == 2, "sanity: both art.py install events must exist in the ledger"
    rc, out = run(m1)
    expect("m1 art.py installs deleted", rc, out, 1, "UNLEDGERED: dessic_akk_dessicated_v2")
    expect("m1 art.py installs deleted (Devourer)", rc, out, 1, "UNLEDGERED: dessic_devourer_dessicated_v2")

    m2, n = copy.deepcopy(base), 0
    for e in m2:
        if e.get("type") == "live" and e.get("rel", "").endswith("Boarwolf/Boarwolf_Dessicated.png") \
                and "bulk_accept_renders.py" in (e.get("reason") or ""):
            e["reason"], n = "script:cp", n + 1
    assert n, "sanity: Boarwolf's bulk-accept event must exist"
    rc, out = run(m2)
    expect("m2 bulk accept relabelled", rc, out, 1, "UNLEDGERED: dessic_boarwolf_dessicated_v1")

    m3 = base + [{"id": "selftestm3xxxxxxxxxx", "type": "live", "mod": "src/RimStarWars/SWBestiary", "rel": AKK,
                  "prev": AKK_SHA, "sha": "0" * 64, "reason": "install", "seat": "BENCH",
                  "ts": "2099-01-01T00:00:00-0800"}]
    rc, out = run(m3)
    expect("m3 ledger moved on", rc, out, 1, "UNLEDGERED: dessic_akk_dessicated_v2")

    real_open = builtins.open

    def fake_open(p, mode="r", *a, **k):     # the Akk file is there but holds other bytes
        if str(p).endswith(AKK) and "b" in mode:
            return io.BytesIO(b"not the render")
        return real_open(p, mode, *a, **k)
    builtins.open = fake_open
    try:
        rc, out = run(base)
    finally:
        builtins.open = real_open
    expect("m4 Akk bytes replaced", rc, out, 1, "STALE: dessic_akk_dessicated_v2")

    m5 = [e for e in base if not (e.get("type") == "binding" and str(e.get("job", "")).startswith("dessic_"))]
    rc, out = run(m5)
    expect("m5 blind", rc, out, 2, "BLIND")

    m6 = [e for e in base if e.get("id") not in OWNER_KEEP_IDS]
    assert len(base) - len(m6) == 2, "sanity: both owner keep rulings must exist in the ledger"
    rc, out = run(m6)
    expect("m6 owner keeps removed", rc, out, 1, "STALE: dessic_akk_dessicated_v1")
    expect("m6 owner keeps removed (Devourer)", rc, out, 1, "STALE: dessic_devourer_dessicated_v1")

    print(f"selftest_dessic_install_check: {len(seen) - len(fails)}/{len(seen)} PASS" + (f"; FAIL {fails}" if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
