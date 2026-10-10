#!/usr/bin/env python3
"""selftest_sheet_hit.py — every control on a biome art sheet row is clickable: nothing is drawn on top of it.

The bug (DESIGN 2026-10-10 §2): the wing-beat playback cell held a bare <img>, so a wide flight frame rendered at natural
size, overflowed its 86 px cell and covered the set's footer — the `✓ variant` button under it could not be clicked
(a real click landed on the image). This renders a flyer row with the REAL row markup (window.itemBody under node) and
the REAL page CSS (template + sheet) in headless Edge, then asks elementFromPoint at the centre of every button on the
row whether the button itself is what a click there hits. FAILS on the pre-fix CSS.
"""
from __future__ import annotations

import io
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


def png(w, h, rgb):
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGBA", (w, h), rgb + (255,)).save(b, "PNG")
    return b.getvalue()


def flyer_item() -> tuple[dict, dict]:
    thumbs, files = {}, {}
    faces = {}
    for f in ("east", "south", "north"):
        for n in (1, 2):
            sha = f"fr{n}{f}"
            thumbs[sha] = f"img/{sha}.png"
            files[f"img/{sha}.png"] = png(160, 160, (200, 80, 40))   # a wide wings-spread frame at thumbnail size
            faces[f"{n}_{f}"] = sha
    for sha in ("bodyS", "bodyE"):
        thumbs[sha] = f"img/{sha}.png"
        files[f"img/{sha}.png"] = png(160, 160, (60, 120, 60))
    keys = [f"{n}_{f}" for f in ("east", "south", "north") for n in (1, 2)]
    it = {"id": "RSW_Probe", "kind": "fauna", "label": "Probe", "effect": "fauna", "tier": "ours", "tierText": "ours",
          "flags": [], "related": [], "elsewhere": [], "rulings": [], "thumbs": thumbs, "letters": ["A"], "prefill": "A",
          "desc": {}, "graphics": [
              {"key": "swanimals/Probe/Probe", "res": "swanimals/Probe/Probe", "role": "body", "primary": True,
               "pool": True, "facings": ["south", "east"], "lane": "slot",
               "slot": {"label": "ADULT", "kind": "adult", "required": True},
               "cols": [{"letter": "A", "kind": "live", "label": "IN GAME", "detail": "", "short": "IN GAME",
                         "faces": {"south": "bodyS", "east": "bodyE"}, "winner": True},
                        {"letter": "B", "kind": "artpipe", "label": "render", "detail": "", "short": "render",
                         "faces": {"south": "bodyS", "east": "bodyE"}, "purgeable": True}]},
              {"key": "_flip:swanimals/Probe/Probe_Flying_", "res": "_flip:swanimals/Probe/Probe_Flying_",
               "role": "wing-beat flight frames", "primary": False, "pool": False, "flip": True, "nframes": 2,
               "lane": "slot", "slot": {"label": "FLYING", "kind": "flying", "required": False},
               "flipFacings": ["east", "south", "north"], "facings": keys,
               "cols": [{"letter": "C", "kind": "artpipe", "label": "flight frames", "detail": "", "short": "flight",
                         "faces": faces, "purgeable": True}]}]}
    return it, files


PROBE = r"""
document.querySelectorAll('details').forEach(d => { d.open = true; });   /* the requests block too */
const out = [];
for (const b of document.querySelectorAll('.row button, .row select, .row input')) {
  const r = b.getBoundingClientRect();
  if (!r.width || !r.height) continue;
  const x = r.left + r.width / 2, y = r.top + r.height / 2;
  b.scrollIntoView({block: 'center'});
  const r2 = b.getBoundingClientRect();
  const hit = document.elementFromPoint(r2.left + r2.width / 2, r2.top + r2.height / 2);
  const ok = hit && (hit === b || b.contains(hit));
  out.push((ok ? 'OK ' : 'BLOCKED ') + (b.className || b.tagName) + ' ' + (b.textContent || '').trim().slice(0, 16)
           + (ok ? '' : ' <- ' + (hit ? hit.tagName + '.' + hit.className : 'nothing')));
}
document.getElementById('probe').textContent = JSON.stringify(out);
"""


def main():
    import sheet_js_harness as H
    if not H.node():
        check(False, "node is needed to render the row (UNMEASURED)")
        return 1
    it, files = flyer_item()
    html = H.item_html(it, {"decision": "A", "note": "", "schema": 2})
    check("bs-play" in html, "the flyer row renders a wing-beat playback cell")
    body = f'<div class="row" data-id="RSW_Probe"><div class="main">{html}</div></div>'
    txt, why = H.edge_probe(body, PROBE, files)
    if txt is None:
        check(False, f"headless Edge probe ran ({why})")
        return 1
    res = json.loads(txt)
    blocked = [r for r in res if r.startswith("BLOCKED")]
    print("\n".join("   " + r for r in res))
    check(len(res) >= 3, f"the probe found the row's controls ({len(res)})")
    check(not blocked, "no control on the flyer row is covered by another element (playback frame constrained)")
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
