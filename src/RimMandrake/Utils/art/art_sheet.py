#!/usr/bin/env python3
"""art_sheet.py — the all-versions comparison sheet (design §3), built from the art ledger.

    python3 art_sheet.py --doubles --out Transient/art_doubles_compare_2026-10-04.html
    python3 art_sheet.py --res swanimals/Nuna/Nuna_f [--res ...] --out <html>

One row per body graphic of a creature (group = the creature); columns are every picture set
the ledger knows for it: each mod shipping it today (the runtime winner marked from the live
ModsConfig.xml load order), artpipe render families, every historical state in git, and the
donor original. S/E/N stacked in each column. Masks and corpse (dessicated) textures never
enter the main grid; masks sit in a folded strip. Canon references show beside the row as
REFERENCE, never pickable. Prior rulings show with their trust (a flawed-sheet ruling is struck
through). Every picture shown is archived in the art store first.

The sheet writes a SNAPSHOT (row -> column -> facing -> sha) to infrastructure/state/art/sheets/;
decisions are column letters resolved through it by `art.py ingest`. Per-picture "purge" is the
owner's reject+purge. Prefill = his latest keep that resolves to a column, else the runtime-live column.
Built on the review-sheets template; gated by check_sheet.py. Generating the SHEET is always
safe; the DECISIONS file is only written when absent (never over his rulings).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402

SKILL = Path.home() / ".claude" / "skills" / "review-sheets" / "assets"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from game_paths import MODS_CONFIG as _MC  # noqa: E402
MODSCONFIG = Path(_MC)
CANON = L.REPO_ROOT / "design" / "RimStarWars" / "canon_references"
FACINGS = ("south", "east", "north", "west", "single")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"   # >26 sets: lowercase continues
NEAR = 10   # dHash bits: at or under this on every facing = near-duplicate (shown folded, never hidden)


# ─────────────────────────────────────────────────────────── load order ──

def load_order():
    """packageId(lower) -> index in the LIVE ModsConfig.xml, plus a fingerprint line."""
    if not MODSCONFIG.is_file():
        return {}, "ModsConfig.xml unreachable — runtime winner UNMEASURED"
    root = ET.parse(MODSCONFIG).getroot()
    act = [li.text.strip().lower() for li in root.find("activeMods") if (li.text or "").strip()]
    st = MODSCONFIG.stat()
    fp = f"ModsConfig.xml {len(act)} active, modified {time.strftime('%Y-%m-%d %H:%M', time.localtime(st.st_mtime))}"
    return {p: i for i, p in enumerate(act)}, fp


def package_id(mod: str) -> str:
    about = L.REPO_ROOT / mod / "About" / "About.xml"
    try:
        el = ET.parse(about).getroot().find("packageId")
        return (el.text or "").strip().lower()
    except (ET.ParseError, OSError, AttributeError):
        return ""


# ─────────────────────────────────────────────────────────────── canon ──

def _canon_dirname(name: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", re.sub(r"^(rsw|rut|rm|aa|a)_", "", name.strip().lower()).replace(" ", ""))


def canon_entry(*names: str) -> dict:
    """The canon-library entry for the first of NAMES that has one ({} if none). Default on every
    sheet (owner rule 2026-10-04): reference images + Must show are shown on each row."""
    d = None
    for n in names:
        for cand in (n.lower(), _canon_dirname(n), _canon_dirname(n).replace("_", "")):
            if cand and (CANON / cand).is_dir():
                d = CANON / cand
                break
        if d:
            break
    if d is None:
        return {}
    txt = (d / "description.md").read_text(errors="replace") if (d / "description.md").exists() else ""
    secs = {}
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", txt, re.S | re.M):
        secs[m.group(1).strip().lower()] = m.group(2).strip()
    # the donor's sprite kept in the entry is not a canon reference (it is the donor column)
    imgs = sorted(p for p in d.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
                  and not p.name.startswith("donor_"))
    return {"brief": secs.get("visual brief", ""), "must": secs.get("must show", ""),
            "ruling": secs.get("ruling", ""), "images": imgs, "dir": str(d.relative_to(L.REPO_ROOT)),
            "key": d.name}


# ───────────────────────────────────────────────────────────── thumbs ──

def thumb(sha: str, imgdir: Path, src_bytes: bytes | None = None, size: int = 200) -> str:
    from PIL import Image
    out = imgdir / f"{sha[:20]}.webp"
    if not out.exists():
        b = src_bytes if src_bytes is not None else L.store_get(sha)
        im = Image.open(BytesIO(b)).convert("RGBA")
        im.thumbnail((size, size), Image.LANCZOS)
        imgdir.mkdir(parents=True, exist_ok=True)
        im.save(out, "WEBP", quality=88, method=6)
    return f"{imgdir.name}/{out.name}"


# ──────────────────────────────────────────────────────────── columns ──

FAM_RE = re.compile(r"_(north|east|south|west)(_r\d+)?$")


def build_row(idx: L.Index, res: str, order: dict, slots: dict) -> dict:
    word = res.split("/")[-2] if "/" in res else res
    wl = word.lower()
    cols = []          # {kind, label, detail, faces:{facing: sha}, date, live, winner}

    # 1. every mod shipping it today
    live = defaultdict(dict)
    for (mod, rel), ev in idx.live.items():
        pt = L.parse_texfile(rel)
        if pt["res"] == res and not pt["mask"]:
            live[mod][pt["facing"]] = ev["sha"]
    first_git = {}
    for sha in {s for f in live.values() for s in f.values()}:
        gs = sorted((v for v in idx.variants[sha] if v.get("kind") == "git"), key=lambda v: v.get("date", ""))
        if gs:
            first_git[sha] = gs[0]
    ranks = {m: order.get(package_id(m), -1) for m in live}
    winner = max(ranks, key=ranks.get) if ranks and max(ranks.values()) >= 0 else None
    for mod in sorted(live, key=lambda m: -ranks[m]):
        f = live[mod]
        g = [first_git[s] for s in f.values() if s in first_git]
        g.sort(key=lambda v: v.get("date", ""))
        lastg = g[-1] if g else {}
        cols.append({"kind": "live", "mod": mod, "faces": dict(f), "date": lastg.get("date", ""),
                     "label": f"{'IN GAME — ' if mod == winner else 'shipped, shadowed — '}{mod.split('/')[-1]}",
                     "detail": (f"load index {ranks[mod]}" + (" (last loaded, wins)" if mod == winner else "")
                                + (f" · bytes from {lastg.get('commit')} {lastg.get('date')}: {lastg.get('subject', '')}" if lastg else "")),
                     "commit_subjects": [v.get("subject", "") for v in g],
                     "winner": mod == winner})

    # 2. artpipe render families: bound by collected.jsonl dest, or alias by creature word
    fams = defaultdict(dict)
    fam_meta = {}
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") != "artpipe":
                continue
            job = v.get("job", "")
            bound = v.get("res") == res
            alias = re.search(rf"(^|_){re.escape(wl)}(_|$)", job.lower()) is not None
            if not (bound or alias):
                continue
            fam = FAM_RE.sub("", job)
            fac = v.get("facing")
            if fac not in FACINGS:
                fm = re.search(r"_(north|east|south|west)(_r\d+)?$", job)
                fac = fm.group(1) if fm else "single"
            fams[fam].setdefault(fac, sha)
            fam_meta[fam] = {"bound": bound or fam_meta.get(fam, {}).get("bound", False), "date": v.get("date", ""),
                             "prompt": v.get("prompt", ""), "derive": v.get("derive_from"), "item": v.get("item")}
    for fam, faces in sorted(fams.items(), key=lambda kv: fam_meta[kv[0]]["date"], reverse=True):
        m = fam_meta[fam]
        cols.append({"kind": "artpipe", "faces": faces, "date": m["date"], "label": f"render {fam}",
                     "detail": (f"{m['date']} · {'collected to this texPath' if m['bound'] else 'joined by creature name only (not bound to this graphic)'}"
                                f" · derive_from {'yes' if m['derive'] else 'no'} · {m['item'] or ''}"),
                     "prompt": m["prompt"][:240], "bound": m["bound"]})

    # 3. every historical state in git, per mod path, as an observed set
    hist = defaultdict(list)       # mod -> [(date, commit, subject, facing, sha)]
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") == "git" and v.get("res") == res and not v.get("mask"):
                hist[v.get("mod", "?")].append((v.get("date", ""), v.get("commit", ""), v.get("subject", ""),
                                               v.get("facing"), sha))
    for mod, evs in hist.items():
        state = {}
        bycommit = defaultdict(list)
        for e in sorted(evs):
            bycommit[(e[0], e[1], e[2])].append(e)
        for (date, commit, subj), es in sorted(bycommit.items()):
            for e in es:
                state[e[3]] = e[4]
            cols.append({"kind": "git", "mod": mod, "faces": dict(state), "date": date,
                         "label": f"history {mod.split('/')[-1]} {date}",
                         "detail": f"{commit} {date}: {subj}"})

    # 4. donor original
    dons = defaultdict(dict)
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") == "donor" and v.get("res") == res and not v.get("mask"):
                dons[v.get("donor_pkg", "?")].setdefault(v.get("facing"), sha)
    for pkg, faces in dons.items():
        cols.append({"kind": "donor", "faces": faces, "date": "", "label": f"donor original {pkg}",
                     "detail": "the donor mod's own sprite (AssetBundle extract)"})

    # drop purged pictures; fold exact duplicates into the first column carrying them
    out, seen = [], {}
    for c in cols:
        c["faces"] = {f: s for f, s in c["faces"].items() if not idx.is_purged(s)}
        if not c["faces"]:
            continue
        key = tuple(sorted(c["faces"].items()))
        if key in seen:
            seen[key].setdefault("also", []).append(f"{c['label']} — {c['detail']}")
            continue
        seen[key] = c
        out.append(c)
    # near-duplicates (perceptual) fold under their parent, shown on expand
    ph = {s: (idx.variants[s][0].get("ph") or "") for c in out for s in c["faces"].values()}
    for i, c in enumerate(out):
        if c["kind"] == "live":
            continue
        for p in out[:i]:
            if p.get("near_of"):
                continue
            common = [f for f in c["faces"] if f in p["faces"]]
            if common and len(common) == len(c["faces"]) and all(
                    ph.get(c["faces"][f]) and ph.get(p["faces"][f]) and
                    L.hamming(ph[c["faces"][f]], ph[p["faces"][f]]) <= NEAR for f in common):
                c["near_of"] = p
                break
    # masks: folded strip, never in the grid
    masks = defaultdict(dict)
    for (mod, rel), ev in idx.live.items():
        pt = L.parse_texfile(rel)
        if pt["res"] == res and pt["mask"]:
            masks[mod.split("/")[-1]][pt["facing"]] = ev["sha"]
    subj = sorted({s["subject"] for s in slots.get(res, [])})
    return {"res": res, "word": word, "cols": out, "masks": masks, "subjects": subj}


def prefill_for(row: dict, rulings: list[dict]) -> tuple[str, str, bool]:
    """(letter, why, contested). Latest ruled owner keep that resolves to a column; then an
    owner ruling cited in the commit that installed a live column's bytes (inferred); else the
    runtime-live column."""
    letter = {id(c): c["letter"] for c in row["cols"]}
    by_sha = {}
    for c in row["cols"]:
        for s in c["faces"].values():
            by_sha.setdefault(s, c)
    keeps = [r for r in rulings if r.get("verdict") == "keep" and r.get("trust") == "ruled" and r.get("by") == "owner"]
    for r in sorted(keeps, key=lambda r: r.get("at") or "", reverse=True):
        for s in (r.get("target") or {}).get("shas", []):
            if s in by_sha:
                return letter[id(by_sha[s])], f"your keep of {(r.get('at') or '')[:10]}", False
    pat = re.compile(r"owner|approved|ruling", re.I)
    for c in [c for c in row["cols"] if c["kind"] == "live"]:
        # the live bytes' own commit, or a look-alike parent: a mechanical sweep (the halo
        # zeroing) rewrote approved art without changing how it looks
        subs = list(c.get("commit_subjects", [])) + [d["detail"] for d in row["cols"] if d.get("near_of") is c]
        hit = next((s for s in subs if pat.search(s)), None)
        if hit:
            return c["letter"], f"inferred: the commit that installed it (or its look-alike parent) cites your approval (“{hit[:110]}”)", True
    win = next((c for c in row["cols"] if c.get("winner")), None) or (row["cols"][0] if row["cols"] else None)
    return (win["letter"] if win else ""), "no resolvable keep of yours — prefilled to what the game shows now", True


# ─────────────────────────────────────────────────────────── the page ──

RENDER = r"""
<script id="RENDER">
window.itemBody = it => {
  const d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
  const purge = new Set(d.purge || []);
  const facings = it.facings;
  const cell = (c, f) => {
    const s = c.faces[f];
    if (!s) return `<div class="ac-cell ac-gap" title="no ${f} in this set">—</div>`;
    const t = it.thumbs[s];
    const p = purge.has(s);
    const btn = c.purgeable ? `<button class="ac-purge${p ? ' on' : ''}" title="reject + PURGE: delete this picture from the art store so it never appears again" onclick="event.stopPropagation();artTogglePurge('${it.id}','${s}')">${p ? '✕ purging' : '✕'}</button>` : '';
    return `<div class="ac-cell${p ? ' ac-purged' : ''}"><div class="thumb ac-thumb" data-zoom="${t}" data-cap="${esc(it.label)} · ${c.letter} · ${f}"><img src="${t}" loading="lazy" alt=""></div>${btn}</div>`;
  };
  const col = c => `<div class="ac-col ac-${c.kind}${c.winner ? ' ac-win' : ''}${d.decision === c.letter ? ' ac-picked' : ''}">
      <div class="ac-head"><b>${c.letter}</b> ${esc(c.label)}</div>
      ${facings.map(f => cell(c, f)).join('')}
      <div class="ac-detail" title="${esc(c.detail)}${c.prompt ? '\n\nprompt: ' + esc(c.prompt) : ''}">${esc(c.detail)}</div>
      ${c.also ? `<details class="ac-also"><summary>${c.also.length} identical elsewhere</summary>${c.also.map(a => `<div>${esc(a)}</div>`).join('')}</details>` : ''}
    </div>`;
  const main = it.cols.filter(c => !c.near_of), near = it.cols.filter(c => c.near_of);
  /* Canon reference beside the variants on EVERY row (owner rule 2026-10-04): images + Must show
     always visible; the visual brief scrolls in place; no entry = said on the row. */
  const canon = it.canon ? `<div class="ac-col ac-canoncol"><div class="ac-head"><b>canon</b> reference — not pickable</div>
      <div class="ac-canon-imgs">${it.canon.imgs.map(u => `<div class="thumb ac-cthumb" data-zoom="${u}" data-cap="canon reference · ${esc(it.canon.dir)}"><img src="${u}" loading="lazy" alt=""></div>`).join('') || '<span class="sub">entry has no images</span>'}</div>
      <div class="ac-brief"><b>Must show</b><pre>${esc(it.canon.must || '(entry lists none)')}</pre><b>Visual brief</b><pre class="ac-vb">${esc(it.canon.brief)}</pre>${it.canon.ruling ? `<b>Ruling</b><pre>${esc(it.canon.ruling)}</pre>` : ''}<span class="sub">${esc(it.canon.dir)}</span></div></div>`
    : `<div class="ac-col ac-canoncol ac-nocanon"><div class="ac-head"><b>canon</b></div><div class="sub">${esc(it.noCanon || 'no canon-library entry')}</div></div>`;
  const flawed = it.flawed ? `<div class="ac-flawed"><b>Your 2026-10-03 desert sheet:</b> ${esc(it.flawed.decision || '(no decision)')}${it.flawed.note ? ' — “' + esc(it.flawed.note) + '”' : ''} <span class="sub">⚠ made against a flawed sheet (its “current” column showed corpse textures for 65 of 109 rows) — shown, authorises nothing</span></div>` : '';
  const ctx = it.context ? `<div class="ac-ctx">${esc(it.context)}</div>` : '';
  const rul = it.rulings.length ? `<div class="ac-rulings">${it.rulings.map(r => `<div class="ac-r ac-t-${r.trust}" title="${esc(r.why || '')}">${esc(r.at)} <b>${esc(r.verdict)}</b> <span class="sub">${esc(r.trust)} · ${esc(r.sheet)}</span> ${r.note ? '“' + esc(r.note) + '”' : ''}</div>`).join('')}</div>` : '';
  const masks = it.masks.length ? `<details class="ac-masks"><summary>masks (not judged here — they follow the body pick)</summary><div class="ac-canon-imgs">${it.masks.map(m => `<div class="thumb ac-thumb" data-zoom="${m.t}" data-cap="mask ${esc(m.mod)} ${m.f}"><img src="${m.t}" loading="lazy" alt=""></div>`).join('')}</div></details>` : '';
  return `<div class="ac-body"><div class="effect">${esc(it.effect)}</div>
    <div class="marks">${it.flags.map(f => `<span class="mark contested">${esc(f)}</span>`).join('')}${it.contested ? '<span class="mark inferred">⚠ prefill inferred — ' + esc(it.prefillWhy) + '</span>' : '<span class="mark absent">prefill: ' + esc(it.prefillWhy) + '</span>'}</div>
    ${ctx}${flawed}${rul}
    <div class="ac-grid"><div class="ac-col ac-facings"><div class="ac-head">&nbsp;</div>${facings.map(f => `<div class="ac-cell ac-flabel">${f}</div>`).join('')}</div>${main.map(col).join('')}${canon}</div>
    ${near.length ? `<details class="ac-near"><summary>${near.length} near-duplicate set(s) (dHash ≤ ${it.near} on every facing) — folded, not hidden</summary><div class="ac-grid">${near.map(c => col(c)).join('')}</div></details>` : ''}
    ${masks}</div>`;
};
window.artRepaint = id => {
  const node = document.querySelector(`.row[data-id="${cssEsc(id)}"] .ac-body`);
  const it = byId.get(id);
  if (node && it) node.outerHTML = window.itemBody(it);
};
window.artTogglePurge = (id, sha) => {
  if (frozen) return;
  const it = byId.get(id); if (!it) return;
  const rec = DEC[id] || (DEC[id] = { decision: '', note: '', prefill: prefillOf(it) });
  const s = new Set(rec.purge || []);
  if (s.has(sha)) s.delete(sha); else s.add(sha);
  rec.purge = [...s]; rec.purgeTouched = true;
  queue(id); patchRow(id); paintCounts();
};
addEventListener('DOMContentLoaded', () => {
  /* A decision click is recorded as decidedAt, so a row touched ONLY to purge or annotate
     never turns its prefill into a ruling at ingest (art_sheet.py docstring). */
  const orig = window.setDecision;
  if (typeof orig === 'function') window.setDecision = function (id, key, opts) {
    orig(id, key, opts);
    if (DEC[id]) { DEC[id].decidedAt = new Date().toISOString(); queue(id); }
  };
  /* The template's patchRow repaints only the buttons; the picked-column frame and the purge
     marks live in the row body, so repaint that too (also covers undo/redo). */
  const origPatch = window.patchRow;
  if (typeof origPatch === 'function') window.patchRow = function (id) { origPatch(id); window.artRepaint(id); };
});
/* Options are global; grey out a column letter this row does not have (never hide). */
new MutationObserver(() => { try {
  document.querySelectorAll('.row[data-id]').forEach(r => {
    const it = byId.get(r.dataset.id); if (!it) return;
    r.querySelectorAll('[data-set]').forEach(b => {
      const k = b.dataset.set;
      const has = !(k.length === 1 && /[A-Za-z]/.test(k)) || it.letters.includes(k);
      b.disabled = !has; b.style.opacity = has ? '' : '0.25';
    });
  });
} catch (e) { /* main script not initialised yet: the next mutation retries */ } }).observe(document.documentElement, { childList: true, subtree: true });
</script>
<style>
.ac-grid{display:flex;gap:8px;overflow-x:auto;padding:6px 0 4px;align-items:flex-start}
.ac-col{flex:0 0 auto;width:132px;border:1px solid var(--line);border-radius:6px;padding:4px;background:#0f1216}
.ac-col.ac-facings{width:44px;border:none;background:none}
.ac-col.ac-win{border-color:var(--info)}
.ac-col.ac-picked{border-color:var(--ok);box-shadow:0 0 0 2px #5ac37f55}
.ac-col.ac-artpipe .ac-head{color:#d9b8ff}.ac-col.ac-git .ac-head{color:#9fb3c8}.ac-col.ac-donor .ac-head{color:#e8b64c}
.ac-head{font-size:11px;line-height:1.25;height:2.6em;overflow:hidden;color:var(--ink)}
.ac-head b{font-size:13px;color:var(--accent)}
.ac-cell{position:relative;height:124px;display:flex;align-items:center;justify-content:center;margin:2px 0}
.ac-flabel{font-size:11px;color:var(--dim);writing-mode:vertical-rl}
.ac-gap{color:#3a4250;font-size:20px}
.ac-thumb{width:120px;height:120px;flex:0 0 120px}
.ac-purge{position:absolute;top:2px;right:2px;font-size:10px;padding:0 4px;border-radius:3px;border:1px solid #5a2a2a;background:#1a0f0f;color:#e06c6c;cursor:pointer;opacity:.55}
.ac-purge:hover,.ac-purge.on{opacity:1}
.ac-purge.on{background:#e06c6c;color:#000}
.ac-purged .ac-thumb{outline:3px solid #e06c6c;opacity:.45}
.ac-detail{font-size:10.5px;color:var(--dim);height:3.9em;overflow:hidden;line-height:1.3}
.ac-also,.ac-near,.ac-masks,.ac-canon{font-size:11.5px;color:var(--dim);margin-top:4px}
.ac-canon-imgs{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0}
.ac-brief pre{white-space:pre-wrap;font:inherit;color:#c3cad6;margin:2px 0 6px;max-height:16em;overflow:auto}
.ac-rulings{font-size:11.5px;margin:4px 0}
.ac-r{color:#c3cad6}.ac-t-flawed-sheet{text-decoration:line-through;color:#8a7070}
.ac-t-prefill{color:#5f6b7a}
.ac-canoncol{width:300px;background:#14110c;border-color:#5a4a2a}
.ac-canoncol .ac-head{color:#e8b64c}
.ac-cthumb{width:136px;height:136px;flex:0 0 136px}
.ac-vb{max-height:9em!important}
.ac-nocanon{width:170px;font-size:11.5px}
.ac-flawed{font-size:12px;margin:4px 0;padding:3px 6px;border-left:3px solid #b07a3a;background:#1a140c;color:#d8c7a8}
.ac-ctx{font-size:11.5px;color:var(--dim);margin:2px 0}
</style>
"""


def generate(resources: list[str], out_html: Path, title: str, sheet_id: str, brief: str,
             meta: dict | None = None, invented_extra: list[str] | None = None) -> dict:
    """META (optional) per texPath: group, subject_keys, canon_names, flags, flawed (the 10-03
    verdict), context (one line). Canon reference images + Must show are shown on EVERY row by
    default (owner rule 2026-10-04); a row without a canon entry says so."""
    meta = meta or {}
    idx = L.Index()
    slots = L.scan_def_slots()
    order, fp = load_order()
    imgdir = out_html.parent / (out_html.stem + "_img")
    rows, items, snap_rows = [], [], {}
    for res in resources:
        rows.append(build_row(idx, res, order, slots))
    maxcols = 0
    for row in rows:
        for i, c in enumerate(row["cols"]):
            c["letter"] = LETTERS[i]
            c["purgeable"] = c["kind"] != "live"
        maxcols = max(maxcols, len(row["cols"]))
    for row in rows:
        word = row["word"]
        m = meta.get(row["res"], {})
        keys = {word.lower(), L.subject_key(word)} | {L.subject_key(k) for k in m.get("subject_keys", [])}
        rul = idx.subject_rulings(keys)
        letter, why, contested = prefill_for(row, rul)
        facings = [f for f in FACINGS if any(f in c["faces"] for c in row["cols"])]
        thumbs = {}
        for c in row["cols"]:
            for s in c["faces"].values():
                if not L.store_has(s):
                    raise SystemExit(f"BYTES_MISSING {s} — every shown picture must be archived first")
                thumbs[s] = thumb(s, imgdir)
        masks = []
        for mod, faces in row["masks"].items():
            for f, s in sorted(faces.items()):
                masks.append({"mod": mod, "f": f, "t": thumb(s, imgdir)})
        cnames = list(m.get("canon_names", [])) + [word] + list(row["subjects"])
        ce = canon_entry(*cnames)
        canon = None
        if ce:
            seen_c = {}
            for p in ce["images"]:
                seen_c.setdefault(L.sha256_file(p), p.read_bytes())
            # the ledger's canon images for the same entry (same files normally; union by sha)
            for s_, vs in idx.variants.items():
                for v in vs:
                    if (v.get("kind") == "canon" and (v.get("subject_key") or "").lower() == ce["key"]
                            and not v.get("is_donor_sprite") and s_ not in seen_c and L.store_has(s_)):
                        seen_c[s_] = None
            canon = {"dir": ce["dir"], "brief": ce["brief"][:2500], "must": ce["must"][:1500],
                     "ruling": ce["ruling"][:800] if "(empty" not in ce["ruling"] else "",
                     "imgs": [thumb(sh, imgdir, b, 260) for sh, b in seen_c.items()]}
        rid = row["res"]
        shadow = [c for c in row["cols"] if c["kind"] == "live"]
        flags = list(m.get("flags", []))
        if len(shadow) > 1:
            flags.append(f"SHADOWED: {len(shadow)} of our mods ship this texPath")
        nonwin_mixed = [c for c in row["cols"] if c["kind"] == "live" and len({c["faces"].get(f) is None for f in facings}) > 1]
        if nonwin_mixed:
            flags.append("SET INCOMPLETE")
        n_hist = sum(1 for c in row["cols"] if c["kind"] == "git")
        n_rend = sum(1 for c in row["cols"] if c["kind"] == "artpipe")
        item = {
            "id": rid, "group": m.get("group", word), "label": f"{m.get('name', word)} — {rid.split('/')[-1]}",
            "context": m.get("context", ""), "flawed": m.get("flawed"),
            "noCanon": None if canon else ("no canon-library entry (looked for: " + ", ".join(dict.fromkeys(c for c in cnames if c)) + ")"),
            "effect": (f"{', '.join(row['subjects']) or 'no def of ours names this texPath'} · "
                       f"{len(row['cols'])} distinct sets: {len(shadow)} shipped now, {n_rend} renders, "
                       f"{n_hist} history states — pick the column the game should show"),
            "prefill": letter, "prefillWhy": why, "contested": contested,
            "facings": facings, "thumbs": thumbs, "letters": [c["letter"] for c in row["cols"]],
            "cols": [{k: (v if k != "near_of" else v["letter"]) for k, v in c.items()
                      if k in ("letter", "kind", "label", "detail", "faces", "winner", "also", "prompt", "purgeable", "near_of")}
                     for c in row["cols"]],
            "near": NEAR, "masks": masks, "canon": canon, "flags": flags,
            "rulings": [{"at": (r.get("at") or "")[:10], "verdict": r.get("raw_verdict") or r.get("verdict"),
                         "trust": r.get("trust"), "sheet": Path(r.get("source_file") or "").name.replace(".decisions.json", ""),
                         "note": (r.get("note") or r.get("blanket_said") or "")[:240], "why": r.get("why_not_protecting", "")}
                        for r in sorted(rul, key=lambda r: r.get("at") or "") if r.get("trust") != "prefill"
                        and not (m.get("flawed") and r.get("trust") == "flawed-sheet")],
        }
        items.append(item)
        snap_rows[rid] = {"subject_key": word.lower(), "res": rid,
                          "columns": {c["letter"]: c["faces"] for c in row["cols"]},
                          "labels": {c["letter"]: c["label"] for c in row["cols"]}}

    snapshot = {"sheetId": sheet_id, "built": L.now(), "loadOrder": fp, "rows": snap_rows}
    snapshot["snapshotId"] = hashlib.sha1(json.dumps(snap_rows, sort_keys=True).encode()).hexdigest()[:16]
    snap_path = L.ledger_dir() / "sheets" / f"{sheet_id}.snapshot.json"
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    snap_path.write_text(json.dumps(snapshot, indent=1, sort_keys=True))

    opts = [{"key": LETTERS[i], "label": LETTERS[i], "hotkey": str(i + 1) if i < 9 else "",
             "color": "#5ac37f", "counts": "in"} for i in range(maxcols)]
    opts += [{"key": "redo", "label": "none — redo (say what in the note)", "hotkey": "r", "color": "#e8b64c", "counts": "out"},
             {"key": "hold", "label": "hold", "hotkey": "h", "color": "#98a2b3", "counts": "out"}]
    decisions_path = out_html.parent / (out_html.stem + ".decisions.json")
    cfg = {
        "sheetId": sheet_id, "title": title,
        "subtitle": f"{len(items)} graphics · {sum(len(i['cols']) for i in items)} picture sets · {fp}",
        "briefHtml": brief,
        "criterion": ("Columns ordered: what the game shows now first (by live load order), then the other shipped copy, "
                      "renders newest first, history oldest first, donor last. The order ranks RECENCY and RUNTIME, not quality."),
        "invented": list(invented_extra or []) + [
            "Renders are joined to a creature by its NAME in the job id when no collect record binds them to a texPath; "
            "such columns say 'joined by creature name only' and may belong to a different graphic of the same creature.",
            "Where no ruling of yours names exact pictures, the prefill trusts a COMMIT MESSAGE that says the art was approved "
            "(e.g. 'Wire approved Pyrelands creature render wave'); those rows carry an ⚠ mark.",
            "History columns are OBSERVED states of one mod's files after each commit — they were real files, never a ruled set.",
        ],
        "posture": {"mode": "pick-one", "explain": "Each row: pick the ONE column the game should show. The winner goes into the "
                    "owning (override) mod and the losing copy is archived — nothing is installed until you see that plan. "
                    "✕ on a picture = reject + PURGE: it is deleted from the art store and never offered again."},
        "options": opts, "groupLabel": "creature", "media": True,
        "decisionsFile": decisions_path.name, "decisionsPath": str(decisions_path), "sheetPath": str(out_html),
    }
    tpl = (SKILL / "sheet_template.html").read_text()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<!-- ══ FILL IN #3 (optional)", RENDER + "\n<!-- ══ FILL IN #3 (optional)", 1)
    tpl = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", tpl, count=1, flags=re.S)
    out_html.write_text(tpl)
    wrote_dec = False
    if not decisions_path.exists():
        decisions_path.write_text(json.dumps({
            "sheetId": sheet_id, "posture": "pick-one", "snapshot": _rel(snap_path),
            "snapshotId": snapshot["snapshotId"], "criterion": cfg["criterion"],
            "reviewStatus": {"state": "prefill", "by": None, "at": None,
                             "evidence": "generated by art_sheet.py; no human has ruled"},
            "decisions": {it["id"]: {"decision": it["prefill"], "note": "", "prefill": it["prefill"]} for it in items},
        }, indent=1))
        wrote_dec = True
    return {"html": str(out_html), "decisions": str(decisions_path), "wrote_decisions": wrote_dec,
            "snapshot": str(snap_path), "rows": len(items), "sets": sum(len(i["cols"]) for i in items),
            "images": len(list(imgdir.glob("*.webp")))}


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(L.REPO_ROOT))
    except ValueError:
        return str(p)


def doubles(idx: L.Index) -> list[str]:
    by = defaultdict(lambda: defaultdict(set))
    for (mod, rel), ev in idx.live.items():
        by[rel][mod].add(ev["sha"])
    res = set()
    for rel, mods in by.items():
        if len(mods) > 1 and len({s for ss in mods.values() for s in ss}) > 1:
            pt = L.parse_texfile(rel)
            res.add(pt["res"])
    return sorted(res)


DOUBLES_BRIEF = """<p><b>The 45 doubled texture paths.</b> Two of our mods ship the same texture path with
<i>different</i> pictures, and the game shows whichever mod loads <b>last</b> — today that is SWBestiary,
so its older port art is what you see in game, shadowing override art that was wired on your 2026-09-13→17
approvals. Creatures: Nuna, Iriaz, Dalgo, Bantha, Eopie (your ruling 2026-10-04: a short compare sheet first,
winner to the override mod, loser archived).</p>
<p><b>Per row, pick the column the game should show.</b> Columns hold every picture set we have for that graphic:
<b>IN GAME</b> (blue frame) is what the game draws now; <b>shipped, shadowed</b> is the copy losing the race;
<b>render</b> columns are artpipe outputs; <b>history</b> columns are earlier states of our files from git;
<b>donor original</b> is the donor mod's own sprite. Facings are stacked south / east / north so a set whose
facings are different animals shows as a broken column. Masks and corpse textures are not judged here.</p>
<p><b>✕ on any non-live picture</b> = reject + purge: it is deleted from the art store and drops off every future
sheet. Your note box is the most useful control on the row. Nothing installs from this sheet: your picks become
ledger rulings, then you see an install plan.</p>"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doubles", action="store_true", help="every texPath shipped by >1 of our mods with different bytes")
    ap.add_argument("--res", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Art: all versions compared")
    ap.add_argument("--sheet-id")
    a = ap.parse_args(argv)
    idx = L.Index()
    res = list(a.res)
    brief = "<p>Pick, per row, the column the game should show. ✕ purges a picture for good.</p>"
    if a.doubles:
        res = doubles(idx) + res
        brief = DOUBLES_BRIEF
        if a.title == ap.get_default("title"):
            a.title = "Art doubles: pick the winner"
    out = Path(a.out)
    if not out.is_absolute():
        out = L.REPO_ROOT / out
    sid = a.sheet_id or out.stem
    r = generate(res, out, a.title, sid, brief)
    print(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
