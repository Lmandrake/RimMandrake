#!/usr/bin/env python3
# selftest-timeout: 300
"""selftest_placeholder_lint.py — the repo lint: no shipped def draws a geometric placeholder (owner rule 2026-10-07
22:33 PDT), except the dated allowlist, which can only shrink.

Part 1, synthetic: resolve() follows Graphic_Random folders and Graphic_Multi facings and skips masks and UI/;
lint() fails an unlisted placeholder, a stale entry, an entry added after the freeze, an entry with no job and not
OWED, and changed placeholder bytes.
Part 2, the REAL repo: every placeholder a shipped def draws is on the allowlist and every entry still ships.
SANITY PROBE: the scan must find the known Webwork/FeverWood circles, or it is not looking.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placeholder_lint as PL  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:600]}]"))
    if not cond:
        FAILS.append(msg)


def main() -> int:
    from PIL import Image
    d = Path(tempfile.mkdtemp(prefix="phlint_"))
    root = d / "Textures"
    for rel in ("Things/Plant/X/X_a.png", "Things/Plant/X/X_b.png", "Things/Plant/X/X_am.png", "Things/Pawn/Y/Y_south.png",
                "Things/Pawn/Y/Y_east.png", "Things/Pawn/Y/Y_southm.png", "Things/Item/Z.png", "UI/Icons/Q.png"):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (4, 4), (1, 2, 3, 255)).save(p)
    names = lambda ps: sorted(p.name for p in ps)  # noqa: E731
    check(names(PL.resolve("Things/Plant/X", [root])) == ["X_a.png", "X_b.png"], "Graphic_Random folder: every PNG, no mask")
    check(names(PL.resolve("Things/Pawn/Y/Y", [root])) == ["Y_east.png", "Y_south.png"], "Graphic_Multi facings, no mask")
    check(names(PL.resolve("Things/Item/Z", [root])) == ["Z.png"], "Graphic_Single file")
    check(PL.resolve("UI/Icons/Q", [root]) == [], "UI/ is never judged")

    f = {"src/a.png": {"reason": "r", "texPath": "t", "defs": ["d.xml"], "sha256": "1"}}
    ok = {"frozen": "2026-10-07", "entries": [{"path": "src/a.png", "sha256": "1", "added": "2026-10-07", "job": ["j"]}]}
    check(PL.lint(f, ok) == [], "a listed placeholder with a job passes")
    check(any("PLACEHOLDER SHIPS" in x for x in PL.lint(f, {"frozen": "2026-10-07", "entries": []})), "an unlisted placeholder fails")
    check(any("STALE" in x for x in PL.lint({}, ok)), "an entry that no longer ships as a placeholder fails (delete it)")
    grew = {"frozen": "2026-10-07", "entries": [dict(ok["entries"][0], added="2026-10-09")]}
    check(any("GREW" in x for x in PL.lint(f, grew)), "an entry added after the freeze fails (list only shrinks)")
    nojob = {"frozen": "2026-10-07", "entries": [dict(ok["entries"][0], job=[])]}
    check(any("no queued job" in x for x in PL.lint(f, nojob)), "an entry with no job and not OWED fails")
    owed = {"frozen": "2026-10-07", "entries": [dict(ok["entries"][0], job=[], status="OWED: no job queued")]}
    check(PL.lint(f, owed) == [], "an OWED entry passes (reported, not hidden)")
    check(any("NEW PLACEHOLDER BYTES" in x for x in PL.lint({"src/a.png": dict(f["src/a.png"], sha256="2")}, ok)),
          "changed placeholder bytes fail")

    found = PL.shipped_placeholders()
    probe = [k for k in found if k.endswith(("RM_Brennoth_a.png", "RM_Ammeth_a.png"))]
    allow = PL.load_allowlist()
    probe_listed = [e["path"] for e in allow.get("entries", []) if e["path"].endswith(("RM_Brennoth_a.png", "RM_Ammeth_a.png"))]
    check(len(probe) == len(probe_listed), "sanity probe: the scan finds every allowlisted Brennoth/Ammeth circle still shipping",
          (probe, probe_listed))
    check(len(PL.texpaths()) > 500, "the scan reads the repo's texPaths", len(PL.texpaths()))
    fails = PL.lint(found, allow)
    check(not fails, f"REPO: {len(found)} shipped placeholder(s), all on the shrinking allowlist", fails[:8])
    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
