#!/usr/bin/env python3
"""old_ticks_sheet.py — the one-off "confirm old variant ticks" sheet (owner ruling by question card 2026-10-10).

Before 2026-10-10 one click on any variant tick turned the machine's default ticks of that row into his (DESIGN §2), so
schema-1 ticks cannot be told apart from his own. The migration (decisions_v2.py) moved every such tick to
`legacyVariants`, where it ships NOTHING. This sheet lists each one once: he confirms it (it is his: on a random pool it
ships as a variant; elsewhere it stays protected from deletion) or drops it (not his: it neither ships nor protects).
enact/ingest read his answers through decisions_v2.confirmations().

    python3 src/RimMandrake/Utils/art/old_ticks_sheet.py build     # (re)build the sheet + prefill decisions (never over his)

Served with serve_gated.py as a non-art sheet (nonart_sheet.py), from Transient/old_ticks_confirm_2026-10-10/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import decisions_v2 as DV  # noqa: E402

BIOMES = L.REPO_ROOT / "Transient" / "biome_ffar"
OUT_DIR = L.REPO_ROOT / "Transient" / DV.CONFIRM_SHEET
FACES = ("south", "east", "north", "west", "single")

RENDER = r"""<script id="RENDER">
window.itemBody = it => {
  const strip = (title, faces, cls) => `<div class="ot-set ${cls || ''}"><div class="ot-h">${esc(title)}</div><div class="ot-f">${faces.map(f => `<div class="thumb ot-t" data-zoom="${esc(f.t)}" data-cap="${esc(it.label + ' · ' + f.f)}"><img src="${esc(f.t)}" loading="lazy" alt=""></div>`).join('') || '<span class="sub">no pictures on record</span>'}</div></div>`;
  return `<div class="effect">${esc(it.effect)}</div>
    <div class="ot-what ${it.pool ? 'pool' : 'nopool'}">${esc(it.meaning)}</div>
    <div class="ot-row">${strip('ticked set ' + it.letter + ' — ' + it.setLabel, it.tick, 'tick')}${it.pick.length ? strip('your pick for the row: ' + it.pickLetter, it.pick, 'pick') : ''}</div>`;
};
</script>
<style>
.ot-row{display:flex;gap:14px;flex-wrap:wrap;margin-top:4px}
.ot-set{border:1px solid var(--line);border-radius:6px;padding:4px;background:#0f1216}
.ot-set.tick{border-color:#7a6aa8}.ot-set.pick{border-color:#2f7a45;opacity:.85}
.ot-h{font-size:11.5px;color:#d6c8ff;margin-bottom:3px}.ot-set.pick .ot-h{color:#9fe0a8}
.ot-f{display:flex;gap:3px}.ot-t{width:96px;height:96px;flex:0 0 96px}
.ot-what{font-size:12.5px;margin:3px 0;padding:2px 6px;border-left:3px solid #7a6aa8}
.ot-what.nopool{border-left-color:#8a6a3a;color:#d8c7a8}
</style>"""


def collect() -> list[dict]:
    import art_sheet as A
    imgdir = OUT_DIR / "img"
    items = []
    for f in sorted(BIOMES.glob("*_sheet_*.decisions.json")):
        doc = json.loads(f.read_text())
        sp = Path(doc.get("snapshot") or "")
        sp = sp if sp.is_absolute() else L.REPO_ROOT / sp
        snap = json.loads(sp.read_text()) if sp.is_file() else {}
        biome = doc.get("biome") or snap.get("biome") or ""
        for row, v in (doc.get("decisions") or {}).items():
            if not isinstance(v, dict) or not v.get("at") or not v.get("legacyVariants"):
                continue
            srow = (snap.get("rows") or {}).get(row) or {}
            cols, gof, labels = srow.get("columns") or {}, srow.get("graphic_of") or {}, srow.get("labels") or {}
            pick = (v.get("decision") or "").strip()
            for l in v["legacyVariants"]:
                g = gof.get(l) or ""
                pool = g in (srow.get("pools") or []) or any("random variant" in str(labels.get(x, "")) for x, gg in gof.items() if gg == g)
                if g.startswith("_flip:"):
                    kind = "flight frames"
                elif g == "_byname" or not g:
                    kind = "a render nobody has said is which picture"
                elif g.startswith("_reference"):
                    kind = "a render of the living creature (reference only)"
                else:
                    kind = g.rsplit("/", 1)[-1]

                def faces(letter):
                    out = []
                    for fc in FACES + tuple(sorted(k for k in (cols.get(letter) or {}) if k not in FACES)):
                        sh = (cols.get(letter) or {}).get(fc)
                        if sh and L.store_has(sh) and len(out) < 4:
                            out.append({"f": fc, "t": A.thumb(sh, imgdir, size=160)})
                    return out
                items.append({
                    "id": DV.confirm_key(doc.get("sheetId") or f.name.replace(".decisions.json", ""), row, l),
                    "label": f"{row} · tick {l}", "group": (biome or doc.get("sheetId", "")).replace("RM_", ""),
                    "effect": f"{doc.get('sheetId')} · {kind}" + (f" · your note: “{(v.get('note') or '')[:160]}”" if v.get("note") else ""),
                    "letter": l, "setLabel": str(labels.get(l, ""))[:90], "pool": pool,
                    "meaning": ("This set is in a RANDOM POOL. Confirm = it is yours: it ships as one of the pictures the game "
                                "picks at random. Drop = not yours: it ships nothing.") if pool else
                               (f"This set is NOT in a random pool ({kind}), so it can never ship as a variant. Confirm = keep "
                                "it protected from deletion. Drop = no protection; nothing else changes."),
                    "tick": faces(l), "pick": faces(pick) if pick in cols and pick != l else [], "pickLetter": pick,
                    # the agent's SUGGESTION only (a prefill ships nothing: decisions_v2.confirmations reads his clicks,
                    # decidedAt): a tick on a pool is suggested confirm, one that can never ship is suggested drop
                    "prefill": "confirm" if pool else "drop", "contested": True,
                    "prefillWhy": "agent suggestion — not yours until you click"})
    return items


def build() -> dict:
    import art_sheet as A
    import nonart_sheet as NA
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sid = DV.CONFIRM_SHEET
    html_p, dec_p = OUT_DIR / f"{sid}.html", OUT_DIR / f"{sid}.decisions.json"
    items = collect()
    n_pool = sum(1 for i in items if i["pool"])
    cfg = {"sheetId": sid, "title": "Confirm old variant ticks",
           "subtitle": f"{len(items)} old ticks on {len({i['id'].rsplit('|', 1)[0] for i in items})} rows · {n_pool} in a random pool",
           "briefHtml": ("<p><b>Old variant ticks — yours, or the machine's?</b> Before today, one click on any variant tick turned "
                         "every machine-default tick of that row into yours, so these can no longer be told apart. Each is "
                         "listed ONCE. <b>confirm</b> = it is yours; <b>drop</b> = it is not. Nothing ships from any of them "
                         "until you confirm it, and an unanswered tick keeps its pictures protected.</p>"),
           "criterion": "Rows: one per old tick, grouped by biome, in sheet and row order. The order ranks nothing.",
           "invented": ["Which old ticks were the machine's default cannot be recovered from the files: every one is asked."],
           "posture": {"mode": "pick-one", "explain": "Each row: confirm or drop. Unanswered = nothing ships, pictures stay protected."},
           "options": [{"key": "confirm", "label": "confirm", "hotkey": "c", "color": "#5ac37f", "counts": "in"},
                       {"key": "drop", "label": "drop", "hotkey": "d", "color": "#e06c6c", "counts": "out"}],
           "groupLabel": "biome", "media": True,
           "decisionsFile": dec_p.name, "decisionsPath": str(dec_p), "sheetPath": str(html_p)}
    html = A._fill_template(cfg, items, RENDER, cfg["title"])
    html_p.write_text(NA.declare(html))
    wrote = False
    if not dec_p.is_file():
        dec_p.write_text(json.dumps({"sheetId": sid, "posture": "pick-one", "criterion": cfg["criterion"],
                                     "reviewStatus": {"state": "prefill", "by": None, "at": None,
                                                      "evidence": "generated by old_ticks_sheet.py; no human has ruled"},
                                     "decisions": {i["id"]: {"decision": i["prefill"], "note": "", "prefill": i["prefill"]} for i in items}}, indent=1))
        wrote = True
    ok, msg = NA.verify(html_p, dec_p)
    return {"html": str(html_p), "decisions": str(dec_p), "items": len(items), "in_pool": n_pool,
            "wrote_decisions": wrote, "nonart_check": msg if ok else "FAIL " + msg}


if __name__ == "__main__":
    if sys.argv[1:] == ["build"]:
        print(json.dumps(build(), indent=1))
    else:
        print(__doc__)
