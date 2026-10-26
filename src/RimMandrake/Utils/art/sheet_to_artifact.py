#!/usr/bin/env python3
"""sheet_to_artifact.py — export a gated review sheet as a self-contained page the PARENT session publishes as a
private claude.ai Artifact, so the owner can review art from a device that is not on our Tailscale network.

    python3 src/RimMandrake/Utils/art/sheet_to_artifact.py <sheet>.html [--decisions <x>.decisions.json] --out <dir>
                                                           [--title "Two To Four"] [--budget-mb 15.5]

WHY. serve_gated.py binds a tailnet-only port; a claude.ai web session on his phone cannot reach it. An Artifact can be
reached, but it has no sidecar to POST to: his picks go to the artifact's own `db` capability, the parent reads them
back with the ArtifactData tool, and `sheet_artifact_merge.py` folds them into the sheet's decisions.json.

WRITES (and nothing else):
    <dir>/index.html   a plain, phone-first list of the sheet's rows (no external scripts at all)
    <dir>/img/*        every picture the rows show, from the SAME files the sheet's ITEMS block points at
    <dir>/files.json   {published path: source path} — the Artifact tool's `files` argument

ROW DATA comes from the sheet's ITEMS block (art_sheet.py's own row data), never from scraping the rendered HTML. Each
lane (slot) keeps every column and EVERY facing the sheet shows, and each column keeps its true-scale panel beside a
vanilla human (scale_panel.py's picture, re-encoded for display only). Tapping any picture opens the sprite itself at
its full pixel resolution.

SIZE. The artifact must stay under 16 MB. Sprites ship as lossless WebP (exact pixels); the scale panels and thumbnails
are display copies. If the total still exceeds --budget-mb, the largest sprites are re-encoded as WebP q95 at the same
pixel size until it fits, and those pictures say so on the page ("near-exact"). Nothing is silently dropped: a picture
that cannot be shipped is a hard error.

GATES (the phone chokepoint, owner question card 2026-10-11 and owner 2026-10-22): game art leaves only on a sheet the
scaled-review gate stamped (`game_art.delivery_check`), and only once every row was read (`prereview.verify`). Either
refusal exits 4 and writes nothing.

DB LAYOUT (what the page writes; `sheet_artifact_merge.py` reads it):
    picks/<docId>   one document per touched row, rewritten whole on each change:
        {rowId, sheetId, rev, pick, slots{<lane key>: {state: pick|redraw, pick?}}, note, done, ts, pickedAt, route}
    docId is rowId with every char outside [A-Za-z0-9_] escaped as "~" + 4 hex digits ("~~" + 6 above U+FFFF), which
    is injective; rowId also rides in the body, which is what the merge reads. `pick` is the primary slot's choice: a letter, "redo", "hold" or "".
    `pickedAt` moves only when a pick/redraw/hold changed, so a row touched only for a note never turns the agent's
    prefill into his decision (decisions_v2.decision_is_his).

CAPABILITIES the parent declares when publishing (printed at the end of a run):
    {"db": {"rules": [{"path": "", "read": "admin", "write": "owner"}]}}
`user` is not needed: the page never reads an id, and a refused write is handled as read-only.
"""
from __future__ import annotations

import argparse
import html as H
import io
import json
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

CAPABILITIES = {"db": {"rules": [{"path": "", "read": "admin", "write": "owner"}]}}
ROUTE = "claude-artifact-db"
MB = 1024 * 1024


def doc_id(row_id: str) -> str:
    """db path segment for a row id; must match the page's JS docId() exactly (selftest checks both)."""
    return "".join(c if (c.isascii() and (c.isalnum() or c == "_")) else
                   "~%04x" % ord(c) if ord(c) <= 0xFFFF else "~~%06x" % ord(c) for c in row_id)


def default_title(cfg: dict, sheet: Path) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z0-9]*", (cfg.get("title") or sheet.stem).split("(")[0].split("—")[0])
    words = [w for w in words if w.lower() not in {"art", "sheet", "the", "of"}][:3]
    return " ".join(words + ["review"]) if words else "Art review"


def strip_tags(s: str) -> str:
    return H.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


class Images:
    """Copies/encodes every picture once; tracks the published path and its byte size."""

    def __init__(self, base: Path, out: Path):
        self.base, self.out = base, out
        self.map: dict[tuple[str, str], str] = {}     # (source ref, role) -> published path
        self.full: dict[str, dict] = {}               # published path -> {src, mode}
        (out / "img").mkdir(parents=True, exist_ok=True)

    def src(self, ref: str) -> Path:
        p = Path(ref)
        p = p if p.is_absolute() else self.base / ref
        if not p.is_file():
            raise SystemExit(f"FAIL: the sheet shows {ref} but {p} does not exist — refusing to ship a page with a hole")
        return p

    def _name(self, ref: str, suffix: str, ext: str) -> str:
        stem = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(ref).stem)
        name, n = f"img/{stem}{suffix}.{ext}", 1
        while name in self.map.values():      # two sources with one stem must never overwrite each other
            n += 1
            name = f"img/{stem}{suffix}-{n}.{ext}"
        return name

    def thumb(self, ref: str) -> str:
        """The sheet's own thumbnail, byte-for-byte."""
        key = (ref, "thumb")
        if key not in self.map:
            p = self.src(ref)
            name = self._name(ref, "", p.suffix.lstrip(".").lower() or "png")
            shutil.copyfile(p, self.out / name)
            self.map[key] = name
        return self.map[key]

    def panel(self, ref: str) -> str:
        """A true-scale panel (scale_panel.py), as a lossy display copy at its own pixel size."""
        from PIL import Image
        key = (ref, "panel")
        if key not in self.map:
            name = self._name(ref, "_disp", "webp")
            with Image.open(self.src(ref)) as im:
                im.save(self.out / name, "WEBP", quality=85, method=6)
            self.map[key] = name
        return self.map[key]

    def sprite(self, ref: str) -> str:
        """The sprite at full pixel resolution, lossless; may be downgraded to q95 later by fit_budget."""
        from PIL import Image
        key = (ref, "full")
        if key not in self.map:
            name = self._name(ref, "_full", "webp")
            with Image.open(self.src(ref)) as im:
                im.save(self.out / name, "WEBP", lossless=True, method=6, exact=True)
            self.map[key] = name
            self.full[name] = {"src": str(self.src(ref)), "mode": "exact"}
        return self.map[key]

    def published(self) -> list[str]:
        return sorted(set(self.map.values()))

    def total(self, extra: int = 0) -> int:
        return extra + sum((self.out / n).stat().st_size for n in self.published())

    def fit_budget(self, budget: int, page_bytes: int) -> list[str]:
        from PIL import Image
        downgraded = []
        for name in sorted(self.full, key=lambda n: -(self.out / n).stat().st_size):
            if self.total(page_bytes) <= budget:
                break
            with Image.open(self.full[name]["src"]) as im:
                im.save(self.out / name, "WEBP", quality=95, method=6, exact=True)
            self.full[name]["mode"] = "q95"
            downgraded.append(name)
        return downgraded


def build_rows(items: list, cfg: dict, decisions: dict, imgs: Images) -> list[dict]:
    letters_ok = {o["key"] for o in cfg.get("options") or [] if isinstance(o, dict) and o.get("key")}
    rows = []
    for it in items:
        thumbs, fulls = it.get("thumbs") or {}, it.get("fulls") or {}
        lanes = []
        for g in it.get("graphics") or []:
            slot = g.get("slot") or {}
            cols = []
            for c in g.get("cols") or []:
                faces = []
                for face, sha in (c.get("faces") or {}).items():
                    t, f = thumbs.get(sha), fulls.get(sha)
                    if not (t or f):
                        raise SystemExit(f"FAIL: row {it.get('id')} set {c.get('letter')} face {face}: no picture "
                                         f"for {sha[:12]} in ITEMS — the sheet itself is broken")
                    faces.append({"face": face, "thumb": imgs.thumb(t or f), "full": imgs.sprite(f or t)})
                sc = c.get("scale") or {}
                cols.append({
                    "L": c.get("letter") or "", "label": c.get("short") or c.get("label") or "",
                    "detail": c.get("detail") or "", "kind": c.get("kind") or "", "winner": bool(c.get("winner")),
                    "setId": c.get("setId"), "noSelect": bool(c.get("noSelect")), "purgedLive": bool(c.get("purgedLive")),
                    "ppc": c.get("ppc"), "srcPx": c.get("srcPx"), "faces": faces,
                    "panel": imgs.panel(sc["img"]) if sc.get("img") else None, "panelFace": sc.get("face"),
                })
            lanes.append({
                "key": g.get("key"), "lane": g.get("lane") or "slot", "primary": bool(g.get("primary")),
                "slotId": slot.get("id"), "label": slot.get("label") or g.get("role") or "",
                "desc": slot.get("desc") or "", "facings": g.get("facings") or [], "cols": cols,
                "pickable": (g.get("lane") or "slot") == "slot",
            })
        scale = it.get("scale") or {}
        desc = it.get("desc") or {}
        rows.append({
            "id": it["id"], "label": it.get("label") or it["id"], "kind": it.get("kind") or "",
            "group": it.get("group") or "", "effect": it.get("effect") or "", "rev": it.get("rev"),
            "description": desc.get("description") or "", "descSource": desc.get("source") or "",
            "prefill": it.get("prefill") or "", "prefillWhy": it.get("prefillWhy") or "",
            "prefillPicks": it.get("prefillPicks") or {}, "flags": it.get("flags") or [],
            "scaleSource": scale.get("source") or "", "scaleVerdict": scale.get("verdict") or "",
            "scaleStatus": scale.get("status") or "", "cells": scale.get("cells"), "footprint": scale.get("footprint"),
            "lanes": lanes, "rec": decisions.get(it["id"]) if isinstance(decisions.get(it["id"]), dict) else None,
            "letters": sorted({c["L"] for ln in lanes for c in ln["cols"] if c["L"] in letters_ok}),
        })
    return rows


def render(title: str, data: dict) -> str:
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (PAGE.replace("__TITLE__", H.escape(title)).replace("__DATA__", blob))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", nargs="?", help="the gated review sheet .html")
    ap.add_argument("--sheet", dest="sheet_opt", help=argparse.SUPPRESS)
    ap.add_argument("--decisions", help="its decisions.json (default: <sheet stem>.decisions.json beside it)")
    ap.add_argument("--out", required=True, help="output directory (created)")
    ap.add_argument("--title", help="page <title>, 2-4 words (default: from the sheet's title)")
    ap.add_argument("--budget-mb", type=float, default=15.5, help="total size cap in MiB (hard limit 16)")
    a = ap.parse_args(argv)
    sheet = Path(a.sheet or a.sheet_opt or ap.error("give the sheet .html")).resolve()

    import game_art
    import prereview
    ok, msg = game_art.delivery_check(sheet)
    if not ok:
        print("REFUSED sheet_to_artifact: " + msg, file=sys.stderr)
        return 4
    ok, msg = prereview.verify(sheet)
    if not ok:
        print("REFUSED sheet_to_artifact: nothing reaches the owner unread: " + msg, file=sys.stderr)
        return 4

    import scaled_review_gate as SG
    html = sheet.read_text(encoding="utf-8")
    cfg, items = SG._json_block(html, "CONFIG") or {}, SG._json_block(html, "ITEMS")
    if not isinstance(items, list) or not items:
        print(f"FAIL: {sheet.name} has no readable ITEMS block — this tool reads row data, never the rendered page",
              file=sys.stderr)
        return 2
    dpath = Path(a.decisions) if a.decisions else sheet.with_name(sheet.stem + ".decisions.json")
    ddoc = json.loads(dpath.read_text(encoding="utf-8")) if dpath.is_file() else {}
    if a.decisions and not dpath.is_file():
        print(f"FAIL: --decisions {dpath} does not exist", file=sys.stderr)
        return 2
    title = a.title or default_title(cfg, sheet)
    if not 2 <= len(title.split()) <= 4:
        print(f"FAIL: title {title!r} must be 2-4 words", file=sys.stderr)
        return 2
    budget = int(min(a.budget_mb, 16.0) * MB)

    out = Path(a.out).resolve()
    if out.is_dir() and any(out.iterdir()) and not (out / "files.json").is_file():
        print(f"FAIL: {out} already holds files that are not an earlier export (no files.json) — choose an empty --out",
              file=sys.stderr)
        return 2
    if out.exists():
        shutil.rmtree(out / "img", ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    imgs = Images(sheet.parent, out)
    rows = build_rows(items, cfg, ddoc.get("decisions") or {}, imgs)
    data = {
        "sheetId": cfg.get("sheetId") or ddoc.get("sheetId") or sheet.stem, "title": cfg.get("title") or title,
        "brief": strip_tags(cfg.get("briefHtml") or "")[:1500], "posture": strip_tags((cfg.get("posture") or {}).get("explain", "")),
        "criterion": cfg.get("criterion") or "", "snapshotId": ddoc.get("snapshotId"), "route": ROUTE,
        "frozen": bool(ddoc.get("frozen")), "rows": rows, "fullMode": {},
        "options": [{"key": o["key"], "label": o.get("label") or o["key"], "counts": o.get("counts")}
                    for o in cfg.get("options") or [] if isinstance(o, dict) and o.get("key")],
    }
    page = render(title, data)
    downgraded = imgs.fit_budget(budget, len(page.encode()) + 4096)
    data["fullMode"] = {n: v["mode"] for n, v in imgs.full.items() if v["mode"] != "exact"}
    page = render(title, data)
    (out / "index.html").write_text(page, encoding="utf-8")
    total = imgs.total(len(page.encode()))
    if total > budget:
        print(f"FAIL: {total / MB:.2f} MiB even with every sprite at q95 — over the {budget / MB:.1f} MiB cap",
              file=sys.stderr)
        return 3
    files = {"index.html": str(out / "index.html")}
    files.update({n: str(out / n) for n in imgs.published()})
    (out / "files.json").write_text(json.dumps(files, indent=1) + "\n", encoding="utf-8")
    nlanes = sum(len(r["lanes"]) for r in rows)
    print(f"{out / 'index.html'}  {len(page.encode()):,} bytes")
    print(f"rows {len(rows)} · lanes {nlanes} · pictures {len(imgs.published())} · total {total / MB:.2f} MiB "
          f"(cap {budget / MB:.1f}) · sprites near-exact (q95) {len(downgraded)} of {len(imgs.full)}")
    print(f"files: {out / 'files.json'}")
    print("capabilities: " + json.dumps(CAPABILITIES, separators=(",", ":")))
    return 0


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f6f5f2;--card:#ffffff;--ink:#1d1d1b;--mute:#62605a;--line:#dedbd3;--accent:#2f6fb2;--accent-ink:#ffffff;
--pick:#2e8b57;--pick-bg:#e5f3ea;--warn:#9a5b00;--warn-bg:#fff2d6;--bad:#a32020;--bad-bg:#fbe3e3;--panel:#5d4c3e;--chip:#efede7}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#151514;--card:#1f1f1d;--ink:#ecebe6;--mute:#a7a59d;
--line:#3a3935;--accent:#6aa5e6;--accent-ink:#0d1622;--pick:#5cc58a;--pick-bg:#173323;--warn:#f0b54a;--warn-bg:#3a2c10;
--bad:#ff8a8a;--bad-bg:#3d1717;--panel:#4a3d32;--chip:#2a2a27}}
:root[data-theme="dark"]{--bg:#151514;--card:#1f1f1d;--ink:#ecebe6;--mute:#a7a59d;--line:#3a3935;--accent:#6aa5e6;
--accent-ink:#0d1622;--pick:#5cc58a;--pick-bg:#173323;--warn:#f0b54a;--warn-bg:#3a2c10;--bad:#ff8a8a;--bad-bg:#3d1717;
--panel:#4a3d32;--chip:#2a2a27}
*{box-sizing:border-box}
html,body{margin:0;overflow-x:hidden}
body{background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:0 16px 48px}
.wrap{max-width:1100px;margin:0 auto}
h1{font-size:20px;margin:16px 0 4px}
.sub,.mute{color:var(--mute);font-size:13px}
a{color:var(--accent)}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:8px 0;margin:0 0 12px;
display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;font-size:14px}
.bar label{display:flex;gap:6px;align-items:center}
.banner{border-radius:8px;padding:10px 12px;margin:10px 0;font-size:14px}
.banner.warn{background:var(--warn-bg);color:var(--warn)}
.banner.bad{background:var(--bad-bg);color:var(--bad)}
.hide{display:none!important}
details.brief{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:8px 0;font-size:14px}
.row{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;margin:0 0 16px;min-width:0}
.row.done{border-color:var(--pick)}
.rhead{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline}
.rhead h2{font-size:17px;margin:0}
.rid{font:12px ui-monospace,Menlo,monospace;color:var(--mute);overflow-wrap:anywhere}
.lane{margin:12px 0 0;padding:10px 0 0;border-top:1px dashed var(--line)}
.lane h3{font-size:14px;margin:0 0 2px}
.cols{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,260px),1fr));gap:10px;margin-top:8px}
.col{border:2px solid var(--line);border-radius:8px;padding:8px;min-width:0;background:var(--card)}
.col.sel{border-color:var(--pick);background:var(--pick-bg)}
.col .cap{font-size:13px;overflow-wrap:anywhere}
.L{display:inline-block;min-width:24px;text-align:center;font-weight:700;border-radius:5px;background:var(--chip);padding:0 5px;margin-right:4px}
.ingame{font-size:11px;font-weight:700;color:var(--pick);margin-left:4px}
.panel{display:block;width:100%;height:auto;max-width:max-content;image-rendering:auto;border-radius:4px;background:var(--panel)}
.faces{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.face{display:flex;flex-direction:column;align-items:center;font-size:11px;color:var(--mute);text-decoration:none}
.face img{width:72px;height:72px;object-fit:contain;background:var(--panel);border-radius:4px;image-rendering:pixelated}
button{font:inherit;font-size:14px;border:1px solid var(--line);background:var(--chip);color:var(--ink);border-radius:7px;
padding:8px 12px;min-height:40px;cursor:pointer}
button.on{background:var(--pick);border-color:var(--pick);color:var(--accent-ink)}
button:disabled{opacity:.45;cursor:not-allowed}
.acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
textarea{width:100%;min-height:64px;font:inherit;font-size:15px;color:var(--ink);background:var(--bg);border:1px solid var(--line);
border-radius:7px;padding:8px;margin-top:10px}
.foot{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin-top:8px}
.state{font-size:12px;color:var(--mute)}
.state.err{color:var(--bad)}
.chip{font-size:12px;background:var(--chip);border-radius:10px;padding:1px 8px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;background:var(--card);border:1px solid var(--line);padding:8px;border-radius:6px}
</style>
</head>
<body>
<div class="wrap">
<h1 id="ttl"></h1>
<div class="sub" id="sub"></div>
<div id="dbmsg" class="banner warn">Connecting to this page's storage…</div>
<details class="brief"><summary>How this works</summary><p id="brief"></p><p id="posture"></p><p class="mute" id="crit"></p>
<p class="mute">Tap any picture to open the sprite at full resolution. The large picture in each set is its true in-game
size beside a vanilla human. Each change is saved here as you go; the decisions file in the repo is updated only when
Claude merges this page's saved picks.</p></details>
<div class="bar"><span id="count"></span><label><input type="checkbox" id="hidedone"> hide done</label>
<button id="copy" type="button">copy my picks</button><span class="state" id="gstate"></span></div>
<pre id="copied" class="hide"></pre>
<div id="rows"></div>
</div>
<script id="DATA" type="application/json">__DATA__</script>
<script>
(() => {
'use strict';
const D = JSON.parse(document.getElementById('DATA').textContent);
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const docId = r => Array.from(r).map(c => { const n = c.codePointAt(0); return /^[A-Za-z0-9_]$/.test(c) ? c : n > 0xFFFF ? '~~' + n.toString(16).padStart(6, '0') : '~' + n.toString(16).padStart(4, '0'); }).join('');
const byId = new Map(D.rows.map(r => [r.id, r]));
/* S[rowId] = what HE chose on this page: {pick, slots{lane: {state, pick?}}, note, done, ts, pickedAt} */
const S = {};
let db = null, readOnly = !!D.frozen, saving = 0;
const writing = {}, dirty = {}, noteTimer = {};

/* the row's starting state: his earlier choices from the decisions file only (a prefill is a suggestion, shown as such) */
function hisRec(rec) {
  if (!rec) return null;
  const d = (rec.decision || '').trim();
  const his = d && (rec.decidedAt || rec.carriedRuledAt || (!('prefill' in rec) ? !!rec.at : (rec.prefill && d !== rec.prefill)));
  return his ? rec : null;
}
function laneState(r, ln) {
  const s = S[r.id];
  if (s && s.slots && s.slots[ln.key]) return s.slots[ln.key];
  if (s && s.slotsTouched && s.slotsTouched[ln.key]) return {state: ''};
  const rec = r.rec || {}, h = hisRec(rec);
  const sl = (rec.slots || {})[ln.key];
  if (sl && sl.state && !sl.migrated && (h || sl.at)) return {state: sl.state, pick: sl.pick, from: 'file'};
  if (ln.primary && h) { if (h.decision === 'redo') return {state: 'redraw', from: 'file'}; if (h.decision.length === 1) return {state: 'pick', pick: h.decision, from: 'file'}; }
  const lp = (rec.picks || {})[ln.key]; if (lp) return {state: 'pick', pick: lp, from: 'file'};   /* legacy second-slot map (SLX.state) */
  return {state: ''};
}
function suggested(r, ln) {
  if (ln.primary) return r.prefill && r.prefill.length === 1 ? r.prefill : '';
  return (r.prefillPicks || {})[ln.key] || '';
}
function rowHold(r) { const s = S[r.id]; if (s && 'pick' in s) return s.pick === 'hold'; const h = hisRec(r.rec); return !!(h && h.decision === 'hold'); }
function ensure(r) {
  if (!S[r.id]) { const rec = r.rec || {}; S[r.id] = {slots: {}, slotsTouched: {}, note: rec.note || '', done: false}; }
  return S[r.id];
}

function laneHTML(r, ln) {
  const st = laneState(r, ln), sug = suggested(r, ln);
  const cols = ln.cols.map(c => {
    const sel = st.state === 'pick' && st.pick === c.L;
    const faces = c.faces.map(f => `<a class="face" href="${esc(f.full)}" target="_blank" rel="noopener"><img loading="lazy" src="${esc(f.thumb)}" alt="${esc(c.L + ' ' + f.face)}">${esc(f.face)}${D.fullMode[f.full] ? ' ·q95' : ''}</a>`).join('');
    const pf = (c.faces.find(f => f.face === c.panelFace) || c.faces[0] || {}).full;
    const panel = c.panel ? `<a href="${esc(pf || c.panel)}" target="_blank" rel="noopener"><img class="panel" loading="lazy" src="${esc(c.panel)}" alt="set ${esc(c.L)} at true scale beside a human"></a>` : '<div class="mute">no true-scale panel for this set</div>';
    const can = ln.pickable && !c.noSelect && !c.purgedLive && !readOnly;
    const btn = ln.pickable ? `<button type="button" data-act="pick" data-row="${esc(r.id)}" data-lane="${esc(ln.key)}" data-l="${esc(c.L)}" class="${sel ? 'on' : ''}"${can ? '' : ' disabled'}>${sel ? 'using ' + esc(c.L) : 'use ' + esc(c.L)}</button>` : '';
    return `<div class="col${sel ? ' sel' : ''}"><div class="cap"><span class="L">${esc(c.L)}</span>${esc(c.label)}${c.winner && !/in game/i.test(c.label) ? '<span class="ingame">IN GAME</span>' : ''}${sug === c.L && st.state !== 'pick' ? ' <span class="chip">suggested</span>' : ''}</div>
${panel}<div class="faces">${faces}</div><div class="mute" style="font-size:12px">${esc(c.srcPx ? c.srcPx.join('×') + ' px' : '')}${c.ppc ? ' · ' + esc(c.ppc) + ' px/cell' : ''}${c.detail ? ' · ' + esc(c.detail) : ''}</div>
<div class="acts">${btn}</div></div>`;
  }).join('');
  const redo = ln.pickable ? `<div class="acts"><button type="button" data-act="redraw" data-row="${esc(r.id)}" data-lane="${esc(ln.key)}" class="${st.state === 'redraw' ? 'on' : ''}"${readOnly ? ' disabled' : ''}>${st.state === 'redraw' ? 'redraw requested' : 'redraw this slot'}</button></div>` : `<div class="mute">Not yet assigned to a slot: these cannot be picked here. Say in the note what they are.</div>`;
  const now = st.state === 'pick' ? 'your pick: ' + st.pick : st.state === 'redraw' ? 'your pick: redraw' : 'no pick (keeps what the game shows)';
  return `<div class="lane"><h3>${esc(ln.label)}${ln.primary ? '' : ' <span class="mute">(second slot)</span>'}</h3>
<div class="mute">${esc(ln.desc)}${ln.desc ? ' · ' : ''}facings: ${esc(ln.facings.join(', '))} · <b>${esc(now)}</b></div><div class="cols">${cols}</div>${redo}</div>`;
}
function rowHTML(r) {
  const s = S[r.id] || {}, rec = r.rec || {}, hold = rowHold(r);
  const note = 'note' in s ? s.note : (rec.note || '');
  const size = r.cells != null ? `${r.footprint ? r.footprint.join('×') + ' cell footprint · ' : ''}${r.cells} cell(s) drawn` : '';
  return `<div class="row${s.done ? ' done' : ''}" id="row-${esc(docId(r.id))}" data-id="${esc(r.id)}">
<div class="rhead"><h2>${esc(r.label)}</h2><span class="rid">${esc(r.id)}</span><span class="chip">${esc(r.kind)}</span>${r.scaleStatus && r.scaleStatus !== 'measured' ? '<span class="chip">size: ' + esc(r.scaleStatus) + '</span>' : ''}</div>
<div class="mute">${esc(r.description)}</div>
<div class="mute" style="font-size:12px">${esc(size)}${r.scaleVerdict ? ' · ' + esc(r.scaleVerdict) : ''}${r.scaleSource ? ' · size from: ' + esc(r.scaleSource) : ''}</div>
${r.prefillWhy ? '<div class="mute" style="font-size:12px">suggested: ' + esc(r.prefill) + ' — ' + esc(r.prefillWhy) + '</div>' : ''}
${r.lanes.map(ln => laneHTML(r, ln)).join('')}
<textarea data-act="note" data-row="${esc(r.id)}" placeholder="Note for this row (what to change, what is wrong)"${readOnly ? ' disabled' : ''}>${esc(note)}</textarea>
<div class="foot"><div class="acts"><button type="button" data-act="hold" data-row="${esc(r.id)}" class="${hold ? 'on' : ''}"${readOnly ? ' disabled' : ''}>${hold ? 'on hold' : 'hold'}</button>
<button type="button" data-act="done" data-row="${esc(r.id)}" class="${s.done ? 'on' : ''}"${readOnly ? ' disabled' : ''}>${s.done ? 'done ✓' : 'mark done'}</button></div>
<span class="state" id="st-${esc(docId(r.id))}">${esc(s._msg || (s.ts ? 'saved' : ''))}</span></div></div>`;
}
function paintRow(id) {
  const r = byId.get(id), el = $('row-' + docId(id));
  const ta = el && el.querySelector('textarea'), focused = ta && document.activeElement === ta;
  if (!el) return;
  if (focused) { paintState(id); el.classList.toggle('done', !!(S[id] || {}).done); return; }   /* never yank the box he types in */
  el.outerHTML = rowHTML(r);
  applyHide();
}
function paintState(id, msg, err) {
  const el = $('st-' + docId(id)); if (!el) return;
  if (msg != null) { (S[id] || {})._msg = msg; }
  el.textContent = (S[id] || {})._msg || ''; el.classList.toggle('err', !!err);
}
function paintCount() {
  const done = D.rows.filter(r => (S[r.id] || {}).done).length;
  const touched = Object.keys(S).filter(k => S[k].ts).length;
  $('count').textContent = `${done} of ${D.rows.length} rows done · ${touched} saved`;
  $('gstate').textContent = saving ? 'saving…' : '';
}
function applyHide() {
  const on = $('hidedone').checked;
  document.querySelectorAll('.row').forEach(el => el.classList.toggle('hide', on && !!(S[el.dataset.id] || {}).done));
}
function body(id) {
  const r = byId.get(id), s = S[id], prim = r.lanes.find(l => l.primary && l.pickable);
  const slots = {};
  for (const [k, v] of Object.entries(s.slots)) if (v && v.state) slots[k] = v.state === 'pick' ? {state: 'pick', pick: v.pick} : {state: v.state};
  for (const k of Object.keys(s.slotsTouched)) if (!slots[k]) slots[k] = {state: ''};
  let pick = '';
  if (rowHold(r)) pick = 'hold';   /* a hold from the file stands until he takes it back */
  else if (prim) { const ps = laneState(r, prim); pick = ps.state === 'pick' ? ps.pick : ps.state === 'redraw' ? 'redo' : ''; }
  return {rowId: id, sheetId: D.sheetId, rev: r.rev || null, pick, slots, note: s.note || '', done: !!s.done,
          ts: new Date().toISOString(), pickedAt: s.pickedAt || null, route: D.route};
}
async function save(id) {
  paintCount();
  if (!db || readOnly) { paintState(id, db ? 'read-only: not saved' : 'not saved: storage unavailable (use "copy my picks")', true); return; }
  if (writing[id]) { dirty[id] = true; return; }        /* one write at a time per document */
  writing[id] = true; saving++; paintCount(); paintState(id, 'saving…');
  try {
    do {
      dirty[id] = false;
      const b = body(id);
      let tries = 0;
      for (;;) {
        try { await db.collection('picks').doc(docId(id)).set(b); break; }
        catch (e) {
          const code = (e && e.code) || 'unavailable';
          if (code === 'unavailable' && tries++ < 1) { await new Promise(res => setTimeout(res, 400 + Math.random() * 800)); continue; }
          throw e;
        }
      }
      S[id].ts = b.ts;
    } while (dirty[id]);
    paintState(id, 'saved ' + new Date().toLocaleTimeString());
  } catch (e) {
    const code = (e && e.code) || 'unavailable';
    if (code === 'invalid_argument' || code === 'revoked' || code === 'not_granted') {
      readOnly = true; showDb('This page is read-only for you: your picks are not being saved (' + code + '). Use "copy my picks" to keep them.', 'bad');
      D.rows.forEach(r => paintRow(r.id));
    } else if (code === 'quota_exceeded') showDb('Storage is full: this pick was not saved. Use "copy my picks" and send the text to Claude.', 'bad');
    paintState(id, 'NOT saved (' + code + ')', true);
  } finally { writing[id] = false; saving--; paintCount(); }
}
function showDb(msg, kind) { const b = $('dbmsg'); b.textContent = msg; b.className = 'banner ' + (kind || 'warn'); b.classList.toggle('hide', !msg); }

document.addEventListener('click', e => {
  const b = e.target.closest('button[data-act]'); if (!b || b.disabled) return;
  const id = b.dataset.row, r = byId.get(id); if (!r) return;
  const s = ensure(r), act = b.dataset.act;
  if (act === 'pick' || act === 'redraw') {
    const ln = r.lanes.find(l => l.key === b.dataset.lane); if (!ln || !ln.pickable) return;
    const cur = laneState(r, ln);
    const next = act === 'pick' ? (cur.state === 'pick' && cur.pick === b.dataset.l ? null : {state: 'pick', pick: b.dataset.l})
                                : (cur.state === 'redraw' ? null : {state: 'redraw'});
    if (next) { s.slots[ln.key] = next; delete s.slotsTouched[ln.key]; } else { delete s.slots[ln.key]; s.slotsTouched[ln.key] = true; }
    if (ln.primary) s.pick = '';   /* body() derives the primary pick from the lane */
    s.pickedAt = new Date().toISOString();
  } else if (act === 'hold') {
    const prim = r.lanes.find(l => l.primary && l.pickable);
    if (rowHold(r)) s.pick = ''; else { s.pick = 'hold'; if (prim) { delete s.slots[prim.key]; s.slotsTouched[prim.key] = true; } }
    s.pickedAt = new Date().toISOString();
  } else if (act === 'done') s.done = !s.done;
  else return;
  paintRow(id); save(id);
});
document.addEventListener('input', e => {
  const t = e.target; if (t.dataset.act !== 'note') return;
  const id = t.dataset.row, r = byId.get(id); if (!r) return;
  ensure(r).note = t.value; paintState(id, 'typing…');
  clearTimeout(noteTimer[id]); noteTimer[id] = setTimeout(() => save(id), 700);   /* one write per pause */
});
$('hidedone').addEventListener('change', applyHide);
$('copy').addEventListener('click', async () => {
  const out = {picks: {}};
  for (const id of Object.keys(S)) out.picks[docId(id)] = body(id);
  const txt = JSON.stringify(out, null, 1), pre = $('copied');
  try { await navigator.clipboard.writeText(txt); $('gstate').textContent = 'copied ' + Object.keys(out.picks).length + ' row(s)'; }
  catch (e) { $('gstate').textContent = 'clipboard blocked: the text is below'; }
  pre.textContent = txt; pre.classList.remove('hide');
});

function applyRemote(doc) {
  const b = doc.data && doc.data(); if (!doc.exists || !b || !b.rowId || !byId.has(b.rowId)) return;
  const id = b.rowId, cur = S[id];
  if (writing[id] || dirty[id] || (cur && cur.ts && b.ts && b.ts < cur.ts)) return;   /* our own newer write wins */
  if (cur && document.activeElement && document.activeElement.dataset && document.activeElement.dataset.row === id && cur.ts === b.ts) return;
  const s = {slots: {}, slotsTouched: {}, note: b.note || '', done: !!b.done, ts: b.ts, pickedAt: b.pickedAt || null};
  for (const [k, v] of Object.entries(b.slots || {})) { if (v && v.state) s.slots[k] = v; else s.slotsTouched[k] = true; }
  if (b.pickedAt) s.pick = b.pick === 'hold' ? 'hold' : '';
  S[id] = s; paintRow(id);
}

$('ttl').textContent = D.title;
$('sub').textContent = `${D.rows.length} rows · sheet ${D.sheetId}`;
$('brief').textContent = D.brief; $('posture').textContent = D.posture; $('crit').textContent = D.criterion;
$('rows').innerHTML = D.rows.map(rowHTML).join('');
paintCount();
if (D.frozen) showDb('This sheet is frozen: it is shown for reference and nothing can be changed.', 'warn');

(async () => {
  try { db = (window.claude && typeof window.claude.use === 'function') ? await window.claude.use('db') : null; }
  catch (e) { db = null; }
  if (!db) { showDb('Saving is unavailable on this view: picks you make here are NOT kept. Open the page inside claude.ai to save, or use "copy my picks" and send the text to Claude.', 'bad'); return; }
  if (!D.frozen) showDb('', 'warn');
  db.collection('picks').onSnapshot(q => { q.docs.forEach(applyRemote); paintCount(); },
    e => showDb('Live updates stopped (' + ((e && e.code) || 'error') + '). Your picks still save; reload to see changes from another device.', 'warn'));
})();
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(main())
