#!/usr/bin/env python3
"""Interactive cherrypick review server for the RimWorld sprite contact sheets.

Serves one HTML page per category. Every def gets its own cell with its own
sprite (the individual texture file on disk, never a slice of a composite
sheet) and its own CUT checkbox. Decisions autosave to
``observed/inventory/decisions_<category>.json``.

stdlib only -- no Pillow, no Flask. Run under WSL python3.

    python3 src/RimMandrake/Utils/cherrypick_review.py [--category weapons] [--port 8788]
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import html
import json
import mimetypes
import os
import posixpath
import re
import sys
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[3]
INVENTORY = REPO / "observed" / "inventory"

# category -> (sheet directory, file stem used inside it)
CATEGORIES = {
    "animals": ("sheets_animals", "animal"),
    "weapons": ("sheets_weapons", "weapons"),
    "apparel": ("sheets_apparel", "apparel"),
    "items": ("sheets_items", "items"),
    "buildings": ("sheets_buildings", "buildings"),
    "plants": ("sheets_plants", "plants"),
}

DIR_SUFFIX_RE = re.compile(r"^<dir:(.+)>$")


# --------------------------------------------------------------------------
# Paths: the CSVs hold native Windows paths; we read them from WSL.
# --------------------------------------------------------------------------

def to_local(p: str) -> str | None:
    """Translate a path out of the CSV into something openable here."""
    if not p:
        return None
    p = p.strip()
    if not p:
        return None
    if os.name == "nt":
        return p
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    if m:
        return "/mnt/" + m.group(1).lower() + "/" + m.group(2).replace("\\", "/")
    return p.replace("\\", "/")


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def g(row: dict, *names: str, default: str = "") -> str:
    for n in names:
        v = row.get(n)
        if v:
            return v.strip()
    return default


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------

class Category:
    """All reviewable cells for one category, plus its on-disk decisions."""

    def __init__(self, name: str):
        self.name = name
        subdir, stem = CATEGORIES[name]
        self.dir = INVENTORY / subdir
        self.index_csv = self.dir / f"{stem}_sheet_index.csv"
        self.missing_csv = self.dir / f"{stem}_textures_missing.csv"
        self.decisions_path = INVENTORY / f"decisions_{name}.json"
        self.lock = threading.Lock()
        self.cells: list[dict] = []
        self.files: list[str | None] = []      # cell idx -> local sprite path
        self.state: dict[str, dict] = {}       # key -> {"cut": bool, "note": str}
        self._load_cells()
        self._load_decisions()

    # ---- input -----------------------------------------------------------

    def _load_cells(self) -> None:
        seen: dict[tuple[str, str], int] = {}
        cells: list[dict] = []

        def key_for(row: dict, tag: str, n: int) -> str:
            dn = g(row, "defName")
            if dn:
                return dn
            return f"<{tag}#{n}>"

        # rendered entries. The sprites live on the Steam drive, where a stat
        # costs milliseconds over the 9p mount -- 3.6k of them serially is 13
        # seconds. Fan them out first: 0.4s.
        index_rows = read_csv(self.index_csv)
        locals_ = [to_local(g(r, "textureFile")) for r in index_rows]
        with ThreadPoolExecutor(32) as ex:
            exists = list(ex.map(lambda p: bool(p) and os.path.exists(p), locals_))

        for n, row in enumerate(index_rows):
            defname = g(row, "defName")
            mod = g(row, "modName", "mod", default="(unknown mod)")
            key = key_for(row, "unnamed", n)
            ident = (key, mod)
            if ident in seen:
                cells[seen[ident]]["variants"] += 1
                continue
            suffix = g(row, "texSuffix")
            dm = DIR_SUFFIX_RE.match(suffix)
            local = locals_[n]
            cell = {
                "i": len(cells),
                "key": key,
                "defName": defname,
                "label": g(row, "label", default="(no label)"),
                "mod": mod,
                "pkg": g(row, "packageId"),
                "order": g(row, "loadOrder"),
                "texPath": g(row, "texPath"),
                "dirVariant": dm.group(1) if dm else "",
                "img": exists[n],
                "missing": "",
                "dup": bool(g(row, "duplicateDefName")),
                "err": g(row, "renderError"),
                "variants": 1,
                "extra": g(row, "thingCategory") or g(row, "pawnKindDefName"),
            }
            if not cell["img"]:
                cell["missing"] = cell["err"] or "file not on disk"
            seen[ident] = len(cells)
            cells.append(cell)
            self.files.append(local if cell["img"] else None)

        # entries with no renderable sprite at all
        for n, row in enumerate(read_csv(self.missing_csv)):
            mod = g(row, "modName", "mod", default="(unknown mod)")
            key = key_for(row, "nodef", n)
            ident = (key, mod)
            if ident in seen:
                cells[seen[ident]]["variants"] += 1
                continue
            cell = {
                "i": len(cells),
                "key": key,
                "defName": g(row, "defName"),
                "label": g(row, "label") or g(row, "detail") or "(no label)",
                "mod": mod,
                "pkg": g(row, "packageId"),
                "order": g(row, "loadOrder"),
                "texPath": g(row, "texPath"),
                "dirVariant": "",
                "img": False,
                "missing": g(row, "reason", default="no texture"),
                "dup": bool(g(row, "duplicateDefName")),
                "err": "",
                "variants": 1,
                "extra": g(row, "thingCategory") or g(row, "pawnKindDefName"),
            }
            seen[ident] = len(cells)
            cells.append(cell)
            self.files.append(None)

        self.cells = cells

    # ---- persistence -----------------------------------------------------

    def _load_decisions(self) -> None:
        if not self.decisions_path.exists():
            return
        try:
            data = json.loads(self.decisions_path.read_text(encoding="utf-8"))
        except Exception as exc:                      # noqa: BLE001
            print(f"  ! ignoring unreadable {self.decisions_path.name}: {exc}")
            return
        for entry in data.get("cut", []):
            k = entry.get("key") or entry.get("defName")
            if k:
                self.state[k] = {"cut": True, "note": entry.get("note", "")}
        for k, note in (data.get("notes") or {}).items():
            if note and k not in self.state:
                self.state[k] = {"cut": False, "note": note}

    def apply(self, changes: list[dict]) -> None:
        with self.lock:
            for ch in changes:
                k = ch.get("key")
                if not k:
                    continue
                cur = self.state.setdefault(k, {"cut": False, "note": ""})
                if "cut" in ch:
                    cur["cut"] = bool(ch["cut"])
                if "note" in ch:
                    cur["note"] = str(ch["note"])[:2000]
                if not cur["cut"] and not cur["note"]:
                    self.state.pop(k, None)
            self._write()

    def _write(self) -> None:
        by_key = {c["key"]: c for c in self.cells}
        cut, notes = [], {}
        for k, st in sorted(self.state.items()):
            c = by_key.get(k, {})
            if st["cut"]:
                cut.append({
                    "defName": c.get("defName", "") or k,
                    "label": c.get("label", ""),
                    "mod": c.get("mod", ""),
                    "note": st["note"],
                    "key": k,
                })
            elif st["note"]:
                notes[k] = st["note"]
        payload = {
            "category": self.name,
            "updated": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "cut": cut,
            "kept_count": len(self.cells) - len(cut),
            "total_count": len(self.cells),
        }
        if notes:
            payload["notes"] = notes
        self.decisions_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.decisions_path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, self.decisions_path)

    def payload(self) -> str:
        """Everything the page needs, as one embedded JSON blob."""
        return json.dumps({
            "category": self.name,
            "categories": [c for c in CATEGORIES if (INVENTORY / CATEGORIES[c][0]).exists()],
            "cells": self.cells,
            "state": self.state,
        }, ensure_ascii=False, separators=(",", ":"))


_cats: dict[str, Category] = {}
_cats_lock = threading.Lock()


def category(name: str) -> Category:
    with _cats_lock:
        c = _cats.get(name)
        if c is None:
            c = Category(name)
            _cats[name] = c
        return c


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>cherrypick &mdash; __CAT__</title>
<style>
:root{--bg:#15171b;--panel:#1e2128;--line:#2f343e;--fg:#e6e8ec;--dim:#98a0ad;
      --cut:#e0524a;--keep:#4ea36b;--accent:#6aa8ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
     font:14px/1.4 -apple-system,Segoe UI,Roboto,sans-serif}
#bar{position:sticky;top:0;z-index:30;background:var(--panel);
     border-bottom:1px solid var(--line);padding:8px 12px;display:flex;
     gap:10px;align-items:center;flex-wrap:wrap}
#bar select,#bar input,#bar button{background:#12141a;color:var(--fg);
     border:1px solid var(--line);border-radius:5px;padding:5px 9px;font:inherit}
#bar button{cursor:pointer}
#bar button:hover{border-color:var(--accent)}
#filter{min-width:280px}
#count{font-variant-numeric:tabular-nums;font-weight:600}
#count b{color:var(--cut)}
.spacer{flex:1}
.hint{color:var(--dim);font-size:12px}
h2.mod{position:sticky;top:45px;z-index:20;margin:0;padding:7px 12px;
     background:#232833;border-top:1px solid var(--line);
     border-bottom:1px solid var(--line);font-size:14px;
     display:flex;gap:10px;align-items:center}
h2.mod .nm{font-weight:600}
h2.mod .ct{color:var(--dim);font-weight:400;font-size:12px}
h2.mod button{background:#12141a;color:var(--dim);border:1px solid var(--line);
     border-radius:4px;padding:2px 7px;font-size:11px;cursor:pointer}
h2.mod button:hover{color:var(--fg);border-color:var(--accent)}
section{content-visibility:auto;contain-intrinsic-size:auto 400px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));
     gap:8px;padding:10px 12px 16px}
.cell{background:var(--panel);border:1px solid var(--line);border-radius:7px;
     padding:6px;display:flex;flex-direction:column;gap:4px;cursor:pointer;
     transition:background .08s,border-color .08s}
.cell:hover{border-color:#49505e}
.cell.cut{background:#3a1c1c;border-color:var(--cut);opacity:.62}
.cell.cut .thumb{filter:grayscale(1) sepia(.5) hue-rotate(-30deg) saturate(3)}
.thumb{height:82px;display:flex;align-items:center;justify-content:center;
     background:#0d0f13;border-radius:4px;overflow:hidden}
.thumb img{max-width:100%;max-height:82px;image-rendering:pixelated}
.nosprite{color:#7a828f;font-size:10px;text-align:center;padding:4px;
     border:1px dashed #4a515e;border-radius:4px;width:100%;height:100%;
     display:flex;align-items:center;justify-content:center}
.lbl{font-size:12px;line-height:1.25;overflow-wrap:anywhere}
.dn{font:11px/1.25 ui-monospace,Consolas,monospace;color:var(--dim);
    user-select:text;cursor:text;overflow-wrap:anywhere}
.tags{display:flex;gap:4px;flex-wrap:wrap}
.tag{font-size:9px;padding:1px 4px;border-radius:3px;background:#2c3444;
     color:#9ab;letter-spacing:.02em}
.tag.dir{background:#3a3320;color:#d9bc74}
.tag.nos{background:#402a2a;color:#e39a94}
.tag.dup{background:#2f2540;color:#bda4e6}
.row{display:flex;align-items:center;gap:6px}
.row input[type=checkbox]{width:16px;height:16px;accent-color:var(--cut);cursor:pointer}
.row .cutword{font-size:11px;color:var(--dim)}
.cell.cut .cutword{color:var(--cut);font-weight:700}
.notebtn{margin-left:auto;background:none;border:none;color:var(--dim);
     cursor:pointer;font-size:12px;padding:0 2px}
.notebtn.has{color:var(--accent)}
textarea{display:none;width:100%;background:#0d0f13;color:var(--fg);
     border:1px solid var(--line);border-radius:4px;font:11px/1.3 inherit;
     padding:4px;resize:vertical;min-height:44px}
textarea.open{display:block}
#saved{font-size:12px;color:var(--dim);min-width:64px}
#saved.on{color:var(--keep)}
</style></head><body>
<div id="bar">
  <select id="cat"></select>
  <span id="count">&mdash;</span>
  <input id="filter" placeholder="filter label / defName / mod &hellip;" autocomplete="off">
  <button id="cutall">cut all visible</button>
  <button id="clearall">clear all visible</button>
  <span class="spacer"></span>
  <span id="saved">&nbsp;</span>
  <span class="hint">checkbox = CUT &middot; autosaves</span>
</div>
<div id="out"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const CELLS = D.cells, ST = D.state || {};
const out = document.getElementById('out');
const els = new Array(CELLS.length);
const secs = [];

// ---- group by mod, stable, biggest contributors keep CSV order ----------
const groups = new Map();
for (const c of CELLS) {
  if (!groups.has(c.mod)) groups.set(c.mod, []);
  groups.get(c.mod).push(c);
}
const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));

const frag = document.createDocumentFragment();
for (const [mod, list] of groups) {
  const sec = document.createElement('section');
  const h = document.createElement('h2');
  h.className = 'mod';
  h.innerHTML = '<span class="nm">' + esc(mod) + '</span>' +
    '<span class="ct" data-ct></span>' +
    '<button data-act="cut">cut all visible</button>' +
    '<button data-act="clear">clear all visible</button>';
  const grid = document.createElement('div');
  grid.className = 'grid';
  for (const c of list) {
    const d = document.createElement('div');
    d.className = 'cell';
    d.dataset.i = c.i;
    const st = ST[c.key] || {};
    const tags = [];
    if (c.dirVariant) tags.push('<span class="tag dir" title="texPath is a DIRECTORY (' +
        esc(c.texPath) + ') &mdash; showing 1 of N variants">dir: ' + esc(c.dirVariant) + '</span>');
    if (c.variants > 1) tags.push('<span class="tag">' + c.variants + ' rows</span>');
    if (c.dup) tags.push('<span class="tag dup">dup defName</span>');
    if (!c.img) tags.push('<span class="tag nos">' + esc(c.missing) + '</span>');
    d.innerHTML =
      '<div class="thumb">' + (c.img
        ? '<img loading="lazy" src="/img/' + D.category + '/k/' + encodeURIComponent(c.key) + '" alt="">'
        : '<div class="nosprite">NO SPRITE</div>') + '</div>' +
      '<div class="lbl">' + esc(c.label) + '</div>' +
      '<div class="dn">' + esc(c.defName || c.key) + '</div>' +
      (tags.length ? '<div class="tags">' + tags.join('') + '</div>' : '') +
      '<div class="row"><input type="checkbox"><span class="cutword">cut</span>' +
      '<button class="notebtn" title="note">&#9998;</button></div>' +
      '<textarea placeholder="comment&hellip;"></textarea>';
    const box = d.querySelector('input'), ta = d.querySelector('textarea'),
          nb = d.querySelector('.notebtn');
    if (st.cut) { box.checked = true; d.classList.add('cut'); }
    if (st.note) { ta.value = st.note; nb.classList.add('has'); }
    d.addEventListener('click', e => {
      if (e.target === box || e.target === ta || e.target === nb) return;
      if (e.target.closest('.dn')) return;
      box.checked = !box.checked; onCut(c, d, box.checked);
    });
    box.addEventListener('change', () => onCut(c, d, box.checked));
    nb.addEventListener('click', e => { e.stopPropagation(); ta.classList.toggle('open');
      if (ta.classList.contains('open')) ta.focus(); });
    ta.addEventListener('input', () => { nb.classList.toggle('has', !!ta.value);
      queue({key: c.key, note: ta.value}); });
    grid.appendChild(d);
    els[c.i] = {el: d, box, ta, cell: c, sec};
  }
  sec.appendChild(h); sec.appendChild(grid); frag.appendChild(sec);
  secs.push({sec, h, list, ct: h.querySelector('[data-ct]')});
  h.querySelector('[data-act=cut]').onclick   = () => bulk(list, true);
  h.querySelector('[data-act=clear]').onclick = () => bulk(list, false);
}
out.appendChild(frag);

function onCut(c, d, v) {
  d.classList.toggle('cut', v);
  ST[c.key] = ST[c.key] || {cut:false, note:''};
  ST[c.key].cut = v;
  queue({key: c.key, cut: v});
  recount();
}
function bulk(list, v) {
  const chg = [];
  for (const c of list) {
    const e = els[c.i];
    if (e.el.style.display === 'none') continue;
    if (e.box.checked === v) continue;
    e.box.checked = v; e.el.classList.toggle('cut', v);
    ST[c.key] = ST[c.key] || {cut:false, note:''};
    ST[c.key].cut = v;
    chg.push({key: c.key, cut: v});
  }
  if (chg.length) { chg.forEach(queue); recount(); }
}

// ---- autosave: debounced, coalesced ------------------------------------
let pend = new Map(), timer = null;
const savedEl = document.getElementById('saved');
function queue(ch) {
  const p = pend.get(ch.key) || {key: ch.key};
  if ('cut' in ch) p.cut = ch.cut;
  if ('note' in ch) p.note = ch.note;
  pend.set(ch.key, p);
  clearTimeout(timer); timer = setTimeout(flush, 300);
}
function flush() {
  if (!pend.size) return;
  const body = JSON.stringify({category: D.category, changes: [...pend.values()]});
  pend = new Map();
  fetch('/save', {method:'POST', keepalive:true,
                  headers:{'Content-Type':'application/json'}, body})
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(j => { savedEl.textContent = 'saved ' + j.cut; savedEl.className = 'on';
                 setTimeout(() => savedEl.className = '', 900); })
    .catch(e => { savedEl.textContent = 'SAVE FAILED'; savedEl.className = '';
                  console.error(e); });
}
addEventListener('beforeunload', () => { if (pend.size) { clearTimeout(timer);
  navigator.sendBeacon('/save', new Blob([JSON.stringify(
    {category: D.category, changes: [...pend.values()]})], {type:'application/json'})); }});

// ---- filter -------------------------------------------------------------
const hay = CELLS.map(c => (c.label + ' ' + c.defName + ' ' + c.key + ' ' + c.mod).toLowerCase());
const fin = document.getElementById('filter');
let ftimer = null;
fin.addEventListener('input', () => { clearTimeout(ftimer); ftimer = setTimeout(applyFilter, 120); });
function applyFilter() {
  const terms = fin.value.toLowerCase().split(/\\s+/).filter(Boolean);
  for (let i = 0; i < CELLS.length; i++) {
    const ok = terms.every(t => hay[i].includes(t));
    els[i].el.style.display = ok ? '' : 'none';
  }
  recount();
}
function recount() {
  let vis = 0, cut = 0, tcut = 0;
  for (let i = 0; i < CELLS.length; i++) {
    const e = els[i], shown = e.el.style.display !== 'none';
    if (e.box.checked) tcut++;
    if (shown) { vis++; if (e.box.checked) cut++; }
  }
  document.getElementById('count').innerHTML =
    '<b>' + tcut + '</b> cut of ' + CELLS.length +
    (vis !== CELLS.length ? ' &middot; ' + cut + '/' + vis + ' shown' : '');
  for (const s of secs) {
    let v = 0, c2 = 0;
    for (const cl of s.list) { const e = els[cl.i];
      if (e.el.style.display !== 'none') { v++; if (e.box.checked) c2++; } }
    s.sec.style.display = v ? '' : 'none';
    s.ct.textContent = c2 + ' cut / ' + v + (v !== s.list.length ? ' shown' : '');
  }
}
document.getElementById('cutall').onclick   = () => secs.forEach(s => bulk(s.list, true));
document.getElementById('clearall').onclick = () => secs.forEach(s => bulk(s.list, false));

// ---- category switcher --------------------------------------------------
const sel = document.getElementById('cat');
for (const c of D.categories) {
  const o = document.createElement('option');
  o.value = c; o.textContent = c; if (c === D.category) o.selected = true;
  sel.appendChild(o);
}
sel.onchange = () => { flush(); location.href = '/c/' + sel.value; };
recount();
</script></body></html>
"""


# --------------------------------------------------------------------------
# Server
# --------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "cherrypick/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):        # quiet
        pass

    # ---- helpers ---------------------------------------------------------

    def _send(self, code: int, body: bytes, ctype: str, extra: dict | None = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _err(self, code: int, msg: str):
        self._send(code, msg.encode(), "text/plain; charset=utf-8")

    # ---- routes ----------------------------------------------------------

    def do_GET(self):                          # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", f"/c/{DEFAULT_CATEGORY}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path.startswith("/c/"):
            name = posixpath.basename(path)
            if name not in CATEGORIES:
                return self._err(404, f"unknown category {name!r}")
            cat = category(name)
            page = (PAGE.replace("__CAT__", html.escape(name))
                        .replace("__DATA__", cat.payload().replace("</", "<\\/")))
            return self._send(200, page.encode("utf-8"),
                              "text/html; charset=utf-8",
                              {"Cache-Control": "no-store"})
        if path.startswith("/img/"):
            parts = path.split("/")
            # /img/<cat>/k/<key> — keyed by the cell's stable key, so a
            # regeneration that reorders cells cannot serve a cached image
            # against the wrong item. The index form below is legacy.
            if len(parts) == 5 and parts[3] == "k":
                name = parts[2]
                if name not in CATEGORIES:
                    return self._err(404, "bad image path")
                cat = category(name)
                key = urllib.parse.unquote(parts[4])
                fp = None
                for c, f in zip(cat.cells, cat.files):
                    if c.get("key") == key:
                        fp = f
                        break
                if not fp:
                    return self._err(404, "no sprite")
                try:
                    data = Path(fp).read_bytes()
                except OSError as exc:
                    return self._err(404, f"unreadable: {exc}")
                ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
                return self._send(200, data, ctype,
                                  {"Cache-Control": "no-cache"})
            if len(parts) != 4:
                return self._err(404, "bad image path")
            name, idx = parts[2], parts[3]
            if name not in CATEGORIES or not idx.isdigit():
                return self._err(404, "bad image path")
            cat = category(name)
            i = int(idx)
            if i >= len(cat.files) or not cat.files[i]:
                return self._err(404, "no sprite")
            fp = cat.files[i]
            try:
                data = Path(fp).read_bytes()
            except OSError as exc:
                return self._err(404, f"unreadable: {exc}")
            ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
            return self._send(200, data, ctype,
                              {"Cache-Control": "no-cache"})
        if path.startswith("/decisions/"):
            name = posixpath.basename(path)
            if name not in CATEGORIES:
                return self._err(404, "unknown category")
            p = category(name).decisions_path
            body = p.read_bytes() if p.exists() else b"{}"
            return self._send(200, body, "application/json; charset=utf-8",
                              {"Cache-Control": "no-store"})
        self._err(404, "not found")

    def do_HEAD(self):                         # noqa: N802
        self.do_GET()

    def do_POST(self):                         # noqa: N802
        if urllib.parse.urlparse(self.path).path != "/save":
            return self._err(404, "not found")
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._err(400, "bad length")
        if n <= 0 or n > 8 * 1024 * 1024:
            return self._err(400, "bad length")
        try:
            req = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception as exc:               # noqa: BLE001
            return self._err(400, f"bad json: {exc}")
        name = req.get("category")
        if name not in CATEGORIES:
            return self._err(400, "unknown category")
        changes = req.get("changes") or []
        if not isinstance(changes, list):
            return self._err(400, "changes must be a list")
        cat = category(name)
        try:
            cat.apply(changes)
        except OSError as exc:
            return self._err(500, f"write failed: {exc}")
        n_cut = sum(1 for s in cat.state.values() if s["cut"])
        self._send(200,
                   json.dumps({"ok": True, "cut": n_cut,
                               "kept": len(cat.cells) - n_cut}).encode(),
                   "application/json; charset=utf-8",
                   {"Cache-Control": "no-store"})


DEFAULT_CATEGORY = "weapons"


def main() -> int:
    global DEFAULT_CATEGORY
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--category", default="weapons", choices=sorted(CATEGORIES))
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--preload", action="store_true",
                    help="load every category at startup instead of on demand")
    ap.add_argument("--counts", action="store_true",
                    help="print the cell count per category and exit")
    args = ap.parse_args()
    DEFAULT_CATEGORY = args.category

    if args.counts:
        for name in CATEGORIES:
            if not (INVENTORY / CATEGORIES[name][0]).exists():
                print(f"{name:<10} (no sheet directory)")
                continue
            c = category(name)
            with_img = sum(1 for x in c.cells if x["img"])
            print(f"{name:<10} {len(c.cells):>5} cells  "
                  f"{with_img:>5} with sprite  {len(c.cells)-with_img:>5} placeholder  "
                  f"{len({x['mod'] for x in c.cells}):>4} mods")
        return 0

    names = list(CATEGORIES) if args.preload else [args.category]
    for name in names:
        if (INVENTORY / CATEGORIES[name][0]).exists():
            c = category(name)
            print(f"  {name}: {len(c.cells)} cells, "
                  f"{sum(1 for s in c.state.values() if s['cut'])} already cut")

    try:
        httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    except OSError as exc:
        print(f"cannot bind {args.host}:{args.port} -- {exc}", file=sys.stderr)
        return 1
    httpd.daemon_threads = True
    print(f"\ncherrypick review -> http://{args.host}:{args.port}/c/{args.category}")
    print(f"decisions -> {INVENTORY / 'decisions_<category>.json'}\nCtrl-C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
