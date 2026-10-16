#!/usr/bin/env python3
"""selftest_ruled_row_stays_open.py — a row collapsed as "already ruled on another sheet" never re-collapses under the
owner's own click, and a row holding unruled new pictures is not collapsed at all.

The bug (owner, 2026-10-15: "Clicking anything on the Murrelith kept closing their art as "already ruled" and I had
to re-open it each time"): RM_Murrelith was ruled `redo` on feverwood 2026-10-08, so the redraw sheet wrapped it in
<details class="bs-ruled">. Every click ran artRepaint, which replaced only the inner .ac-body with itemBody(it) —
and itemBody returns the WHOLE collapsed <details>, so each click nested a fresh CLOSED "already ruled" block inside
the open one. FAILS on the pre-fix artRepaint / itemBody / build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


# A one-row fake DOM: the row's HTML is a string; querySelector hands back a node whose outerHTML setter splices the
# replacement over exactly that element's text, as a browser does.
CLICK = r"""
const it = byId.get(ID);
let html = window.itemBody(it);
const initialOpen = /^<details class="bs-ruled" open/.test(html);
const span = sel => {
  if (sel === 'details.bs-ruled') return html.startsWith('<details class="bs-ruled"') ? [0, html.length] : null;
  if (sel === '.ac-body') { const i = html.indexOf('<div class="ac-body'); const j = html.lastIndexOf('</details>');
    return i < 0 ? null : [i, j > i ? j : html.length]; }
  return null;
};
const row = {querySelector: sel => { const s = span(sel); if (!s) return null;
  return {set outerHTML(v) { html = html.slice(0, s[0]) + v + html.slice(s[1]); }}; }};
document.querySelector = sel => !sel.startsWith('.row[') ? null : sel.endsWith(' .ac-body') ? row.querySelector('.ac-body')
  : sel.includes(' ') ? null : row;
for (let n = 0; n < CLICKS; n++) window.artRepaint(ID);
const tags = html.match(/<details class="bs-ruled"[^>]*>/g) || [];
console.log(JSON.stringify({initialOpen, ruledBlocks: tags.length, allOpen: tags.every(t => / open/.test(t))}));
"""


def clicked(item: dict, clicks: int, dec: dict | None = None) -> dict:
    import sheet_js_harness as H
    snip = ("DEC = " + json.dumps({item["id"]: dec} if dec else {}) + "; byId = new Map([[" + json.dumps(item["id"])
            + ", " + json.dumps(item) + "]]); const ID = " + json.dumps(item["id"]) + "; const CLICKS = " + str(clicks)
            + ";\n" + CLICK)
    return H.run_js(snip)


class _Idx:
    def __init__(self, seen: dict):
        self.variants = {sha: [{"ts": ts}] for sha, ts in seen.items()}


def main():
    import sheet_js_harness as H
    from selftest_sheet_hit import flyer_item
    import art_sheet as A
    if not H.node():
        print("UNMEASURED: node not found")
        return 1
    it, _ = flyer_item()
    it = dict(it, id="RM_Murrelith", ruledElsewhere={"sheet": "feverwood_sheet_2026-10-05", "sheetId": "x",
                                                    "pick": "redo", "label": "", "note": "", "at": "2026-10-08"})
    r0 = clicked(it, 0)
    check(r0["ruledBlocks"] == 1 and not r0["initialOpen"], "initial load: an already-ruled row renders collapsed")
    for n in (1, 3):
        r = clicked(it, n)
        check(r["ruledBlocks"] == 1, f"{n} click(s): still exactly one 'already ruled' block (no nested copy), got {r['ruledBlocks']}")
        check(r["allOpen"], f"{n} click(s): the row he is working in stays open")
    r = clicked(it, 0, {"decision": "B", "note": "", "at": "2026-10-15T05:00:00Z", "decidedAt": "2026-10-15T05:00:00Z"})
    check(r["initialOpen"], "a row he already saved a pick in on THIS sheet renders open after a reload")

    # build side: pictures first recorded after his ruling elsewhere are unruled candidates -> no collapse
    gitems = [{"cols": [{"letter": "A", "faces": {"south": "old1", "east": "old2"}},
                        {"letter": "B", "faces": {"south": "new1", "east": "new2"}},
                        {"letter": "C", "faces": {"south": "old1", "east": "new2"}}]}]
    idx = _Idx({"old1": "2026-10-07T00:00:00Z", "old2": "2026-10-07T00:00:00Z",
                "new1": "2026-10-15T20:00:00Z", "new2": "2026-10-15T20:00:00Z"})
    check(A.new_sets_since(gitems, idx, "2026-10-08T04:20:31.026Z") == ["B"],
          "a set redrawn after his 10-08 ruling is new (a set mixing old pictures is not)")
    check(A.new_sets_since([{"cols": gitems[0]["cols"][:1]}], idx, "2026-10-08T04:20:31Z") == [],
          "only old pictures: the ruling stands and the row may collapse")
    check(A.new_sets_since(gitems, idx, "") == [], "an unparseable ruling time never reopens a row")
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
