#!/usr/bin/env python3
"""selftest_enact_seen_build.py — a sheet click records WHICH build its page was loaded from (SHEET_DECISION_WIRE_BUILD_STAMP).

enact used to infer the build he clicked on as "the newest snapshot built at or before his decidedAt", which is wrong for a
tab left open across a rebuild. Now every row carries the snapshot's `built` (it.build), the page writes it as
`seen_build` beside every click time it stamps, and enact.ruled_snapshot prefers it. End-to-end enact cases (a schema-1
decision and a slot record across a rebuild) are case 22 of selftest_enact_stale_lane.py.

  1 ruled_snapshot: build A 09:00, rebuild B 09:30 (today's), click 10:00 stamped A -> A; unstamped -> B (old inference);
    stamped with today's build -> today's, no revision walk; a stamp no copy holds -> None, named; an unreadable copy in
    the window with no match -> None naming it; a match found past an unreadable copy -> the match;
  2 page JS (node): SLX.setSlot stamps the slot record and, for the primary slot, the row (beside decidedAt); a page with
    no build stamp REMOVES a stale row stamp; a state carrying its own earlier `at` keeps its own stamp;
  3 the right-hand letter wrapper (setDecision) stamps the row and the primary slot record (source check: the harness
    stubs DOMContentLoaded); art_sheet emits it.build from the snapshot it writes;
  4 sheet_artifact_merge: a mirrored pick that rewrites decidedAt drops the earlier click's seen_build; so does
    decisions_v2.accept_looks;
  5 the review-sheets sidecar's writer (the page's save path) keeps seen_build on the record it writes.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def case_ruled_snapshot():
    import enact as E
    A = {"built": "2026-10-10T02:00:00-0700", "tag": "A"}
    B = {"built": "2026-10-10T02:30:00-0700", "tag": "B"}
    bad = {"_unreadable": "revision deadbeef unreadable: not UTF-8 JSON"}
    walked = []
    revs = [B, A]

    def fake(_p):
        walked.append(1)
        yield from revs
    run0 = E.snapshot_revisions
    E.snapshot_revisions = fake
    try:
        click = "2026-10-10T10:00:00.000Z"
        s, why = E.ruled_snapshot(Path("x"), B, click, A["built"])
        check(s is A and not why, f"1 stamped with A, today's sheet B: resolves to A ({s}, {why})")
        s, why = E.ruled_snapshot(Path("x"), B, click)
        check(s is B, f"1 unstamped: the time inference picks B, built before the click ({s})")
        walked.clear()
        s, why = E.ruled_snapshot(Path("x"), B, click, B["built"])
        check(s is B and not walked, f"1 stamped with today's build: today's, no revision walked ({s}, {len(walked)})")
        s, why = E.ruled_snapshot(Path("x"), B, click, "2026-10-09T00:00:00-0700")
        check(s is None and "not on disk or in git" in why and "2026-10-09" in why,
              f"1 a stamp no copy holds: None, named — never the time inference ({why})")
        revs[:] = [B, bad]
        s, why = E.ruled_snapshot(Path("x"), B, click, A["built"])
        check(s is None and "deadbeef" in why, f"1 no match and an unreadable copy: None naming it ({why})")
        revs[:] = [bad, A]
        s, why = E.ruled_snapshot(Path("x"), B, click, A["built"])
        check(s is A, f"1 the exact build found past an unreadable copy: that build ({s}, {why})")
        s, why = E.ruled_snapshot(Path("x"), B, None, A["built"])
        check(s is A, f"1 a stamped record needs no click time ({s}, {why})")
    finally:
        E.snapshot_revisions = run0


def case_js():
    import sheet_js_harness as H
    if not H.node():
        check(False, "2 UNMEASURED: node not found")
        return
    it = {"id": "R", "build": "BUILD-A", "graphics": [
        {"key": "P", "lane": "slot", "primary": True, "slot": {"id": "R/p"},
         "cols": [{"letter": "B", "kind": "artpipe", "faces": {"south": "b"}, "setId": "sb"}]},
        {"key": "Y", "lane": "slot", "primary": False, "slot": {"id": "R/y"},
         "cols": [{"letter": "C", "kind": "artpipe", "faces": {"south": "c"}, "setId": "sc"}]}]}
    import json
    o = H.run_js(
        "const S = window.SLX; const it = " + json.dumps(it) + "; const g = k => it.graphics.find(x => x.key === k);"
        "const a = {}; S.setSlot(it, a, g('P'), {state: 'pick', pick: 'B'});"
        "const b = {}; S.setSlot(it, b, g('Y'), {state: 'pick', pick: 'C'});"
        "const it2 = Object.assign({}, it); delete it2.build;"
        "const c = {seen_build: 'OLD'}; S.setSlot(it2, c, g('P'), {state: 'redraw'});"
        "const d = {}; S.setSlot(it, d, g('Y'), {state: 'pick', pick: 'C', at: '2026-01-01T00:00:00Z', seen_build: 'EARLIER'});"
        "console.log(JSON.stringify({a, b, c, d}));")
    check(o["a"]["slots"]["P"].get("seen_build") == "BUILD-A" and o["a"].get("seen_build") == "BUILD-A"
          and o["a"].get("decidedAt") == o["a"]["slots"]["P"]["at"],
          f"2 a primary slot click stamps the slot record and the row beside decidedAt ({o['a']})")
    check(o["b"]["slots"]["Y"].get("seen_build") == "BUILD-A" and "seen_build" not in o["b"],
          f"2 a non-primary slot click stamps its slot record only ({o['b']})")
    check("seen_build" not in o["c"] and "seen_build" not in o["c"]["slots"]["P"],
          f"2 a page with no build stamp removes a stale row stamp ({o['c']})")
    check(o["d"]["slots"]["Y"].get("seen_build") == "EARLIER",
          f"2 a state carrying its own earlier click time keeps its own stamp ({o['d']})")


def case_sources():
    src = (HERE / "art_sheet.py").read_text()
    check("window.SLX.stampBuild(it_, DEC[id]);" in src
          and src.count("S.stampBuild(it_, { state: ") == 2,
          "3 the setDecision wrapper stamps the row and both primary slot records")
    check('it["build"] = snap["built"]' in src, "3 art_sheet emits it.build from the snapshot it writes")


def case_merge():
    import sheet_artifact_merge as M
    it = {"id": "R", "graphics": [{"key": "P", "lane": "slot", "primary": True, "slot": {"id": "R/p"},
                                   "cols": [{"letter": "B", "setId": "sb", "faces": {"south": "b"}}]}]}
    rec = {"decision": "", "note": "", "decidedAt": "2026-10-01T00:00:00Z", "seen_build": "OLD"}
    body = {"pick": "B", "slots": {"P": {"state": "pick", "pick": "B"}}, "pickedAt": "2026-10-26T10:00:00Z",
            "ts": "2026-10-26T10:00:00Z", "note": ""}
    r = M.merge_row(rec, body, it)
    check(r.get("decidedAt") == "2026-10-26T10:00:00Z" and "seen_build" not in r,
          f"4 a mirrored pick rewriting decidedAt drops the earlier click's seen_build ({r})")


def case_accept_looks():
    import json
    import tempfile
    import decisions_v2 as DV
    lane = "things/Tank/Tank"
    snap = {"snapshotId": "s1", "rows": {"RM_Tank": {
        "res": lane, "columns": {"A": {"single": "A" * 64}, "C": {"single": "C" * 64}},
        "graphic_of": {"A": lane, "C": lane}, "labels": {"A": "IN GAME — X", "C": "render tank_c"}}}}
    doc = {"snapshotId": "s1", "snapshot": "x", "decisions": {
        "RM_Tank": {"decision": "C", "decidedAt": "2026-10-01T00:00:00Z", "seen_build": "OLD", "prefill": "A"}}}
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "d.json"
        p.write_text(json.dumps(doc))
        r = DV.accept_looks(p, "Just accept the art and go on.", snapshot=snap, apply=True)
        v = json.loads(p.read_text())["decisions"]["RM_Tank"]
        check(r.get("ok") and v.get("decidedAt") != "2026-10-01T00:00:00Z" and "seen_build" not in v,
              f"4 accept_looks rewriting decidedAt drops the earlier click's seen_build ({r.get('error')}, {v})")


def case_sidecar():
    import json
    import tempfile
    import sheet_artifact_merge as M
    with tempfile.TemporaryDirectory() as td:
        dp = Path(td) / "t_sheet.decisions.json"
        dp.write_text(json.dumps({"sheetId": "t_sheet", "decisions": {"R": {"decision": "", "note": ""}}}))
        side, guard = M._sidecar()
        df = side.DecisionsFile(str(dp))
        rec = {"decision": "B", "note": "", "decidedAt": "2026-10-26T10:00:00Z", "seen_build": "BUILD-A",
               "slots": {"P": {"state": "pick", "pick": "B", "at": "2026-10-26T10:00:00Z", "seen_build": "BUILD-A"}}}
        df.write_ops(guard({"R": rec}, df.read().get("decisions") or {}))
        v = json.loads(dp.read_text())["decisions"]["R"]
        check(v.get("seen_build") == "BUILD-A" and v["slots"]["P"].get("seen_build") == "BUILD-A",
              f"5 the sidecar's writer keeps seen_build on the row and its slot record ({v})")


def main() -> int:
    case_ruled_snapshot()
    case_js()
    case_sources()
    case_merge()
    case_accept_looks()
    case_sidecar()
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
