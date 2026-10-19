#!/usr/bin/env python3
"""selftest_review_queue.py — `art.py review awaiting-pick` collects exactly the rows waiting on his pick (2026-10-19).

Fixture sheets in a temp dir (no defs, no build, no server):
  · an untouched row with an unassigned render or a candidate of ours awaits; a row he decided, noted, labelled
    `not needed`, or that has only what the game draws does not; a row collapsed as ruled elsewhere does not
  · ruled / frozen / returned sheets are not open; a texture-manifest sheet is skipped and named
  · the same subject on two sheets is one row with both sheets' jobs
  · rows he touched on the queue's OWN page stay on it
  · a ruling on another sheet made AFTER a sheet was built removes the row; one made before it does not
Then a compatibility pass over every real decisions file in Transient/: each parses and every row reads through
decisions_v2 (letters, asks, owner view) and owner_touched without error — the controls removed on 2026-10-19 left
their data readable.

    python3 src/RimMandrake/Utils/art/selftest_review_queue.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import review_queue as Q  # noqa: E402

FAILS = []
DATE = "2026-10-19"


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def col(letter, kind="artpipe", winner=False, **kw):
    return dict({"letter": letter, "kind": kind, "winner": winner, "faces": {"south": letter.lower() * 4}}, **kw)


def item(rid, cols=None, unassigned=None, required=False, **kw):
    gs = [{"key": "g", "lane": "slot", "primary": True, "slot": {"label": "ADULT", "required": required}, "cols": cols or []}]
    if unassigned:
        gs.append({"key": "_byname", "lane": "unassigned", "slot": {"label": "RENDERS NOT YET ASSIGNED"}, "cols": unassigned})
    return dict({"id": rid, "label": rid, "kind": "fauna", "graphics": gs}, **kw)


def sheet(out: Path, name: str, items: list, decisions: dict, doc_extra: dict | None = None, jobs: dict | None = None,
          census_extra: dict | None = None, mtime: float | None = None):
    base = f"{name}_sheet_{DATE}"
    html = out / f"{base}.html"
    html.write_text('<html><body><script id="ITEMS" type="application/json">' + json.dumps(items) + "</script></body></html>")
    key = f"SUBJECTS_{name}"
    rows = [{"key": it["id"], "defNames": [], "artpipe_state_jobs": (jobs or {}).get(it["id"], [])} for it in items]
    (out / f"{name}.subjects.json").write_text(json.dumps({"biomes": {key: dict({"rows": rows}, **(census_extra or {}))}}))
    doc = dict({"sheetId": base, "biome": key, "reviewStatus": {"state": "prefill"}, "decisions": decisions}, **(doc_extra or {}))
    (out / f"{base}.decisions.json").write_text(json.dumps(doc))
    if mtime:
        os.utime(html, (mtime, mtime))
    return base


def fixture_tests():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        live = col("A", "live", winner=True)
        old = time.time() - 86400
        sheet(out, "alpha", [
            item("RM_Una", [live], unassigned=[col("E")]),                     # unassigned render: awaits
            item("RM_Cand", [live, col("B")]),                                  # candidate of ours: awaits
            item("RM_Decided", [live, col("B")]),                               # he picked: no
            item("RM_Noted", [live, col("B")]),                                 # he typed a note: no
            item("RM_NotNeeded", [live], unassigned=[col("E")]),                # he said not needed: no
            item("RM_OnlyLive", [live]),                                        # nothing to pick: no
            item("RM_DonorOnly", [live, col("C", "donor")]),                    # a donor original is not a candidate: no
            item("RM_Empty", [], required=True),                                # required slot, nothing in game: awaits
            item("RM_Elsewhere", [live, col("B")], ruledElsewhere={"sheet": "x"}),   # collapsed: no
            item("RM_Twice", [live, col("B")]),
            item("RM_Later", [live, col("B")]),
            item("RM_Before", [live, col("B")]),
        ], {
            "RM_Decided": {"decision": "B", "prefill": "A", "decidedAt": "2026-10-18T00:00:00Z", "at": "x"},
            "RM_Noted": {"decision": "A", "prefill": "A", "note": "make it greener"},
            "RM_NotNeeded": {"decision": "A", "prefill": "A", "schema": 2, "assign": {"E": "not_needed"}},
            "RM_Cand": {"decision": "A", "prefill": "A"},                       # a seeded prefill is NOT his pick
        }, jobs={"RM_Twice": ["job_a"]}, mtime=old)
        sheet(out, "beta", [item("RM_Twice", [live, col("B")])], {}, jobs={"RM_Twice": ["job_b"]})
        sheet(out, "ruledsheet", [item("RM_R1", [live, col("B")])], {}, {"reviewStatus": {"state": "ruled"}})
        sheet(out, "frozensheet", [item("RM_F1", [live, col("B")])], {}, {"frozen": True})
        sheet(out, "returnedsheet", [item("RM_T1", [live, col("B")])], {}, {"returned": {"at": "x"}})
        sheet(out, "texsheet", [item("RM_X1", [live, col("B")])], {}, census_extra={"textures_manifest": "/x.json"})
        # his ruling on another (sidecar-written) sheet: RM_Later after alpha was built, RM_Before before it
        sheet(out, "gamma", [item("RM_Later", [live, col("B")]), item("RM_Before", [live, col("B")])], {
            "RM_Later": {"decision": "B", "decidedAt": "x", "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
            "RM_Before": {"decision": "B", "decidedAt": "x", "at": "2026-01-01T00:00:00Z"}},
            {"savedBy": "review-sheet-sidecar", "writeCount": 3, "reviewStatus": {"state": "ruled"}})
        sheet(out, Q.NAME, [item("RM_Mine", [live, col("B")])],
              {"RM_Mine": {"decision": "B", "prefill": "A", "decidedAt": "x", "at": "x"}})
        q = Q.awaiting(Q.NAME, DATE, out)
        got = {r["subject"]: r for r in q["rows"]}
        check({"RM_Una", "RM_Cand", "RM_Empty"} <= set(got), "awaits: an unassigned render, a candidate of ours, an empty required slot")
        for s in ("RM_Decided", "RM_Noted", "RM_NotNeeded", "RM_OnlyLive", "RM_DonorOnly", "RM_Elsewhere"):
            check(s not in got, f"{s} does not await")
        check(not ({"RM_R1", "RM_F1", "RM_T1", "RM_X1"} & set(got)), "ruled, frozen, returned and texture-manifest sheets add nothing")
        check(any("texsheet" in s and "texture-manifest" in s for s in q["skipped"]), "the texture-manifest sheet is named as skipped")
        tw = got.get("RM_Twice") or {}
        check(sorted(tw.get("jobs") or []) == ["job_a", "job_b"] and len(tw.get("sheets") or []) == 2,
              "the same subject on two sheets is ONE row carrying both sheets' jobs")
        check("RM_Mine" in got, "a row he touched on the queue's own page stays on it until enact")
        check("RM_Later" not in got and "RM_Before" in got,
              "a ruling elsewhere after the sheet was built removes the row; one from before it does not")
        kinds = [r["kind"] for r in q["rows"]]
        check(kinds == sorted(kinds, key=lambda k: {"fauna": 0, "flora": 1, "fish": 2}.get(k, 3)), "rows ordered by kind")


def compat_tests():
    import decisions_v2 as DV
    files = sorted((Q.L.REPO_ROOT / "Transient").rglob("*.decisions.json"))
    n_rows, bad = 0, []
    for f in files:
        try:
            doc = json.loads(f.read_text())
        except (OSError, ValueError) as e:
            bad.append(f"{f.name}: {e}")
            continue
        for k, v in (doc.get("decisions") or {}).items() if isinstance(doc.get("decisions"), dict) else ():
            try:
                if isinstance(v, dict):
                    DV.letters(v), DV.asks_of(v), DV.owner_view(v), Q.owner_touched(v)
                n_rows += 1
            except Exception as e:      # noqa: BLE001
                bad.append(f"{f.name}:{k}: {type(e).__name__}: {e}")
    check(files and not bad, f"every real decisions file reads after the 2026-10-19 control removal: {len(files)} files, "
                             f"{n_rows} rows, {len(bad)} problems {bad[:3]}")


def main() -> int:
    fixture_tests()
    compat_tests()
    print(f"{'FAIL' if FAILS else 'PASS'} selftest_review_queue ({len(FAILS)} failing)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
