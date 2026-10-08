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
import subject as S  # noqa: E402  (ART_SUBJECT_RESOLVER_1: the one name->art matcher)
import placeholder_detect as PD  # noqa: E402
import scaled_review_gate as SG  # noqa: E402  (the hard gate: a sheet failing a scaled-review requirement is never written)

SKILL = Path.home() / ".claude" / "skills" / "review-sheets" / "assets"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from game_paths import MODS_CONFIG as _MC  # noqa: E402
MODSCONFIG = Path(_MC)
CANON = L.REPO_ROOT / "design" / "RimStarWars" / "canon_references"
FACINGS = ("south", "east", "north", "west", "single")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"   # >26 sets: lowercase continues
NEAR = 10   # dHash bits: at or under this on every facing = near-duplicate (shown folded, never hidden)


# ─────────────────────────────────────────────────────────── load order ──

FULL_LIST = L.REPO_ROOT / "infrastructure" / "state" / "modlists" / "ModsConfig.FULL.LATEST.xml"
MIN_REAL_LIST = 200   # a live list shorter than this is a swapped-in test list, not what the owner plays


def _active(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    return [li.text.strip().lower() for li in root.find("activeMods") if (li.text or "").strip()]


def load_order():
    """packageId(lower) -> load index, plus a fingerprint line. The LIVE ModsConfig.xml when it is the
    owner's real list; when a small test list is swapped in (it decides nothing about what he plays),
    the captured FULL.LATEST list instead — otherwise every one of our mods reads 'not loaded' and no
    column can be IN GAME."""
    act, src = [], None
    if MODSCONFIG.is_file():
        act, src = _active(MODSCONFIG), "live ModsConfig.xml"
    if len(act) < MIN_REAL_LIST and FULL_LIST.is_file():
        live_n = len(act)
        act = _active(FULL_LIST)
        src = f"ModsConfig.FULL.LATEST.xml (live list has {live_n} mods — a test list)"
    if not act:
        return {}, "no mod list readable — runtime winner UNMEASURED"
    return {p: i for i, p in enumerate(act)}, f"{src}: {len(act)} active"


def _composed() -> dict:
    """source folder -> the composed mod's packageId, for entries a *.compose.json ships inside a unified mod
    (wave <= compose_wave). Their own packageIds are never on the load list: the unified mod is."""
    if not hasattr(_composed, "m"):
        _composed.m = {}
        for f in (L.REPO_ROOT / "src").glob("*/*.compose.json"):
            try:
                d = json.loads(f.read_text())
                pid = d["about"]["packageId"].lower()
                for e in d["entries"]:
                    if e.get("wave", 99) <= d.get("compose_wave", -1):
                        _composed.m[str((f.parent / e["source"]).relative_to(L.REPO_ROOT))] = pid
            except (OSError, ValueError, KeyError, TypeError):
                continue
    return _composed.m


def package_id(mod: str) -> str:
    if mod.rstrip("/") in _composed():
        return _composed()[mod.rstrip("/")]
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


VARIANT_WORDS = {"alpha", "juv", "juvenile", "feral", "mature", "elder", "young", "adult", "baby", "calf", "pup", "wild"}


NO_SOURCE = CANON / "NO_SOURCE.json"


def _no_source() -> tuple[set, dict]:
    try:
        d = json.loads(NO_SOURCE.read_text())
    except (OSError, ValueError):
        return set(), {}
    unlinked = {k.lower(): v for k, v in (d.get("not_canon_linked") or {}).items()}
    for k, v in (d.get("owner_ours") or {}).items():
        if not k.startswith("_"):
            unlinked.setdefault(re.sub(r"^(RM_|RSW_|RUT_)", "", k).lower(), v)
    return {n.lower() for n in d.get("no_source", [])}, unlinked


def canon_state(key: str) -> str:
    """The row tag when no canon entry matched. Only Star Wars-tier rows get one; our own RM_/RUT_ inventions
    get nothing (they are not meant to be canon)."""
    if not key.startswith("RSW_"):
        return ""
    stem = TIER_RE.sub("", key).lower()
    stem2 = re.sub(r"^plant_|_wild$", "", stem)
    nos, unlinked = _no_source()
    for s_ in (stem, stem2):
        if s_ in unlinked:
            return "not canon-linked — " + unlinked[s_]
        if s_ in nos:
            return "invented creature — searched Wookieepedia + SWTOR wiki, no canon source exists; judge on its own"
    return "canon not yet checked"


def canon_base(key: str, label: str = "", census_entries: dict | None = None) -> tuple[dict, str]:
    """For a Star Wars (RSW_) row with no exact canon entry: drop life-stage/variant words (WraidAlpha,
    FeralNerf, 'young faa scalefish') and match the remainder EXACTLY to an entry dir, or to the entry of
    the census row for that base defName. Never a substring/prefix match (AA_Lockjaw must not find jawa,
    RM_ShaleGorgerJuv must not find gorg). Returns (entry, base name) or ({}, '')."""
    if not key.startswith("RSW_"):
        return {}, ""
    stem = TIER_RE.sub("", key)
    cands = [re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", stem.replace("_", " ")), (label or "").split()]
    for words in cands:
        base = [w for w in words if w.lower() not in VARIANT_WORDS]
        if not base or len(base) == len(words):
            continue
        name = "".join(base).lower()
        if (CANON / name).is_dir():
            return canon_entry(name), name
        e = (census_entries or {}).get("RSW_" + "".join(w[:1].upper() + w[1:] for w in base))
        if e:
            return canon_entry(Path(e).name), Path(e).name
    return {}, ""


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

GENERIC_DIRS = {"plant", "plants", "things", "thing", "item", "items", "building", "buildings", "animal", "animals",
                "pawn", "pawns", "terrain", "filth", "mote", "motes", "projectile", "weapon", "weapons", "apparel"}
FAM_RE = re.compile(r"_(north|east|south|west)(_r\d+)?$")


def build_row(idx: L.Index, res: str, order: dict, slots: dict) -> dict:
    parts = res.split("/")
    # the creature word is the folder (swanimals/Wraid/Wraid_j -> Wraid) unless that folder is a generic
    # category (Things/Plant/RM_Shadespire): then the file name. A generic word like "plant" joined every
    # *_plant_* render to every plant row (49 foreign renders on RM_Shadespire, 2026-10-04).
    word = parts[-2] if len(parts) > 1 and parts[-2].lower() not in GENERIC_DIRS else parts[-1]
    # render alias: the FILE STEM minus tier prefix, never the folder (art_resolution_rootcause §5.4 / B0)
    wl = S.stem(parts[-1]).lower()   # subject.stem: donor tiers (RG_, AB_ ...) and Plant_ too
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
    # game copies of this texPath (donor / other mods, ingested by gametex.py bound by texPath): one per mod
    dons, don_meta = defaultdict(dict), {}
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") == "donor" and v.get("res") == res and not v.get("mask"):
                pkg = (v.get("donor_pkg") or "?").lower()
                dons[pkg].setdefault(v.get("facing"), sha)
                m = don_meta.setdefault(pkg, {"mod": v.get("donor_mod") or pkg, "how": v.get("how"),
                                              "random_of": v.get("random_of"), "bound_by": v.get("bound_by"),
                                              "loc": v.get("loc", "")})
                if v.get("donor_mod"):
                    m["mod"] = v["donor_mod"]
    dranks = {p: order.get(p, order.get(p + "_steam", -1)) for p in dons}
    allr = list(ranks.values()) + list(dranks.values())
    top = max(allr) if allr and max(allr) >= 0 else None
    winner = next((m for m in ranks if top is not None and ranks[m] == top), None)
    dwinner = next((p for p in dranks if top is not None and dranks[p] == top), None) if winner is None else None
    for mod in sorted(live, key=lambda m: -ranks[m]):
        f = live[mod]
        g = [first_git[s] for s in f.values() if s in first_git]
        g.sort(key=lambda v: v.get("date", ""))
        lastg = g[-1] if g else {}
        cols.append({"kind": "live", "mod": mod, "faces": dict(f), "date": lastg.get("date", ""),
                     "label": f"{'IN GAME — ' if mod == winner else 'shipped, shadowed — ' if ranks[mod] >= 0 else 'shipped, not loaded — '}{mod.split('/')[-1]}",
                     "detail": (f"load index {ranks[mod]}" + (" (last loaded, wins)" if mod == winner else "")
                                + (f" · bytes from {lastg.get('commit')} {lastg.get('date')}: {lastg.get('subject', '')}" if lastg else "")),
                     "commit_subjects": [v.get("subject", "") for v in g],
                     "winner": mod == winner})

    # 2. artpipe render families: bound by collected.jsonl dest, or alias by creature word
    fams = defaultdict(dict)
    fam_meta = {}
    _fc = failed_canon_jobs()
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") != "artpipe":
                continue
            job = v.get("job", "")
            bound = v.get("res") == res
            alias = len(S.norm(wl)) >= 4 and S.token_match(job, S.norm(wl))
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
        if not fam_meta[fam]["bound"] and (NOT_BODY_JOB.search(fam) or FLIP_FAM_RE.match(fam)):
            continue          # a flight frame joined by name is not a body candidate (flipbook_cols shows it)
        m = fam_meta[fam]
        cols.append({"kind": "artpipe", "faces": faces, "date": m["date"],
                     "label": f"render {fam}" + (FAILED_CANON_BADGE if _is_failed_canon(fam, _fc) else ""),
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

    # 4. game copies from other mods: the one the game draws first (IN GAME), then donor originals
    for pkg in sorted(dons, key=lambda p: -dranks[p]):
        m = don_meta[pkg]
        win = pkg == dwinner
        how = "AssetBundle extract" if m["how"] == "assetbundle-extract" else "loose PNG in the game's mod folders"
        col = {"kind": "donor", "faces": dons[pkg], "date": "", "winner": win,
               "ours": pkg.startswith("mandrake."),   # our own deployed copy is not a donor original
               "label": (f"IN GAME — {m['mod']}" if win else
                         f"our deployed art — {m['mod']}" if pkg.startswith("mandrake.") else f"donor original — {m['mod']}"),
               "detail": (f"load index {dranks[pkg]}" + (" (last loaded, wins)" if win else
                          " (shadowed by a later mod)" if dranks[pkg] >= 0 else " (not in the measured load order)")
                          + f" · {pkg} · {how}"
                          + (f" · 1 of {m['random_of']} random variants" if m.get("random_of") else "")
                          + (f" · bound: {m['bound_by']}" if m.get("bound_by") else ""))}
        if win:
            cols.insert(0, col)
        else:
            cols.append(col)

    # drop purged pictures; fold exact duplicates into the first column carrying them
    out, seen, donor_purged = [], {}, False
    for c in cols:
        was = bool(c["faces"])
        c["faces"] = {f: s for f, s in c["faces"].items() if not idx.is_purged(s)}
        if not c["faces"]:
            if was and c["kind"] == "donor" and not c.get("ours"):
                donor_purged = True      # a donor ORIGINAL the owner purged: shown and rejected (gate req 4)
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
    return {"res": res, "word": word, "cols": out, "masks": masks, "subjects": subj, "donorPurged": donor_purged}


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

DOUBLES_BODY = r"""
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
"""

COMMON_JS = r"""
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
  /* Any save of a row's record first writes the defaulted variants into it, so the default is data. */
  const origQueue = window.queue;
  if (typeof origQueue === 'function') window.queue = function (id) {
    const it = byId.get(id);
    if (it && DEC[id]) window.artEnsureVariants(it, DEC[id]);
    return origQueue.apply(this, arguments);
  };
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
/* Column letters are per row: the pick buttons show only the letters this row has (template hook). */
window.itemOptions = it => OPTS.filter(o => !(o.key.length === 1 && /[A-Za-z]/.test(o.key)) || (it.letters || []).includes(o.key));
"""

STYLE = r"""
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

RENDER = '<script id="RENDER">' + DOUBLES_BODY + COMMON_JS + "</script>" + STYLE


def pick_options(n: int) -> list[dict]:
    """Column letters (per row: the same letter is a different picture on every row, so no group bulk),
    then redo / hold. Only 'hold' gets an all-rows button."""
    opts = [{"key": LETTERS[i], "label": LETTERS[i], "hotkey": str(i + 1) if i < 9 else "",
             "color": "#5ac37f", "counts": "in", "bulk": False} for i in range(n)]
    return opts + [{"key": "redo", "label": "redo", "hotkey": "r", "color": "#e8b64c",
                    "counts": "out", "bulk": False},
                   {"key": "hold", "label": "hold", "hotkey": "h", "color": "#98a2b3", "counts": "out"}]


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
            c["purgeable"] = c["kind"] != "live" and not (c["kind"] == "donor" and c.get("winner"))   # the game's own art
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
                      if k in ("letter", "kind", "label", "detail", "faces", "winner", "also", "prompt", "purgeable", "near_of", "placeholder", "ours")}
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

    opts = pick_options(maxcols)
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


# ─────────────────────────── per-biome sheet (BIOME_FLORAFAUNA_ART_REVIEW_1, owner rulings 2026-10-04) ──
#
#   python3 src/RimMandrake/Utils/art/art_sheet.py --refresh --biome first3
#     --refresh = art.py backfill artpipe (~45 s, finished renders into the ledger) + gametex.py ingest (game copies of
#     every row's texPath, ~10 s; ~65 s more when its /tmp/rm_gametex index must be rebuilt) + biome_census.py; the sheets then
#     take ~4 min for the first three biomes (thumbnails are cached by sha, so a re-run only renders new pictures)
#
# One sheet per biome from Transient/biome_ffar/census.json (biome_census.py). One item per census row (flora AND
# fauna); within a row, one section per body graphic (body / swimming / flying …) holding every picture set the
# ledger knows for it (build_row, recomputed live on every run, so finished renders appear on a re-run), plus
# renders found by the row's NAME that no graphic binds yet. Canon images + Must show beside every canon row; a
# row with no entry says so. Census twins become two-way "related" links; linked rows share a group + colour band
# and sit together. Desert sitting 1 picks (census prior_selection) prefill the matching graphic. Letters are kept
# STABLE across re-runs (read back from the previous snapshot), so a decisions file the owner has touched still
# resolves; an untouched prefill decisions file is regenerated.

CENSUS = L.REPO_ROOT / "Transient" / "biome_ffar" / "census.json"
BIOME_OUT = L.REPO_ROOT / "Transient" / "biome_ffar"
BIOME_SLUG = {"RM_LongShade": "desert", "RM_Stillsand": "deep_desert", "RM_BlueDesert": "blue_desert",
              "desert": "desert", "deep_desert": "deep_desert", "blue_desert": "blue_desert"}   # others: _stem(key).lower()
TIER_RE = S.TIER_RE
NOT_BODY_JOB = re.compile(r"dess?icc?at|corpse|_mote|halo|filth|skeleton|print|mask|_icon\b", re.I)
PAIR_COLOURS = ["#e8b64c", "#5ac3c3", "#c38ae8", "#e07a5f", "#7fc35a", "#5a8ae8", "#e85aa8", "#c3b85a"]
ROLE_TEXT = {"body": "body", "swimming": "swimming graphic", "flying": "flying graphic",
             "plant_immature": "young plant", "plant_leafless": "leafless plant", None: "renders found by NAME"}
SIT1 = "desert sitting 1"


def _stem(n: str) -> str:
    return S.stem(n)


def _human(row: dict) -> str:
    if row.get("label"):
        return row["label"]
    s = _stem(row["key"])
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s).replace("_", " ").lower()


def _tier(row: dict) -> tuple[str, str]:
    k = row["key"]
    if (row.get("canon") or {}).get("entry"):
        return "canon", "canon Star Wars creature (has a canon-library entry)"
    if k.startswith("RSW_"):
        return "sw", "Star Wars tier (RSW_), no canon-library entry"
    if k.startswith(("RM_", "RUT_", "rut_")):
        return "ours", "our own design (franchise-free RM_/RUT_)"
    return "donor", "a donor mod's def, not one of ours"


def _layer(row: dict) -> str:
    parts = []
    if isinstance(row.get("layer"), str) and row["layer"]:
        parts.append(row["layer"])
    for p in row.get("placements") or []:
        if p.get("layer") == "inline_RM" or (p.get("source") == "inline" and not p.get("patch_mod")):
            parts.append("in this biome's own roster")
        else:
            parts.append(f"added by the {p.get('patch_mod') or 'patch'} layer")
    return " + ".join(dict.fromkeys(parts))


def _short(c: dict) -> str:
    """One readable line for a set's header; the full provenance is its tooltip."""
    lab = c.get("label", "")
    if c.get("kind") == "live":
        return ("IN GAME · " if c.get("winner") else "not loaded · " if "not loaded" in lab else "shadowed copy · ") + lab.split("— ")[-1]
    if c.get("kind") == "artpipe":
        return f"render {(c.get('date') or '')[:10]} · {lab.removeprefix('render ')}"
    if c.get("kind") == "git":
        return f"history {(c.get('date') or '')[:10]} · {lab.removeprefix('history ').rsplit(' ', 1)[0]}"
    if c.get("kind") == "kept":
        return "KEPT · your ruled pick, no longer found · " + lab
    if c.get("kind") == "donor" and c.get("oursRender"):
        return ("IN GAME · " if c.get("winner") else "our art, shadowed · ") + lab.split(" — ")[0]
    if c.get("kind") == "donor":
        if c.get("winner"):
            return "IN GAME · " + lab.split("— ", 1)[-1]
        return "donor original · " + lab.split("— ", 1)[-1].removeprefix("donor original ")
    return lab


def _prefill_short(source: str, why: str) -> str:
    if source == "inferred" and why.startswith("inferred: newest render"):
        return "newest render found by name"
    if "no resolvable keep" in why:
        return "what the game shows now (no pick of yours)"
    if why.startswith("inferred"):
        return "a commit says you approved it"
    if source == "none":
        return "hold — no art yet" if "no art" in why else why
    return why[:80]


def _fkey(c: dict) -> tuple:
    return tuple(sorted(c["faces"].items()))


OVERRIDES = Path(__file__).resolve().parent / "sheet_row_overrides.json"


FAILED_CANON_BADGE = " — failed canon check"


_FC_CACHE: dict = {}


def failed_canon_jobs() -> set:
    """Job ids the artpipe canon gate filed as failed_canon (failed/<job>.manifest.json). The render still exists in
    _artsrc and is a CANDIDATE: the gate has false-failed before (owner accepted such a render). Read at build time."""
    import os
    root = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe") / "failed"
    if root in _FC_CACHE:
        return _FC_CACHE[root]
    out = _FC_CACHE[root] = set()
    if root.is_dir():
        for m in root.glob("*.manifest.json"):
            try:
                if json.loads(m.read_text()).get("worker_status") == "failed_canon":
                    out.add(m.name[:-len(".manifest.json")])
            except (OSError, ValueError):
                pass
    return out


def _is_failed_canon(fam: str, fc: set) -> bool:
    return any(j == fam or FAM_RE.sub("", j) == fam for j in fc)


def name_render_cols(idx: L.Index, words, exact) -> list[dict]:
    """Artpipe render families whose job name carries one of WORDS (word-bounded, >= 4 chars) or is one of
    EXACT (artpipe_state_jobs). Corpse/mote/mask/filth jobs are not body art and never join."""
    keys = [S.norm(w) for w in words if w and len(S.norm(w)) >= 4]
    exact = {e.lower() for e in exact}
    fams, meta = defaultdict(dict), {}
    for sha, vs in idx.variants.items():
        if idx.is_purged(sha):
            continue
        for v in vs:
            if v.get("kind") != "artpipe":
                continue
            job = v.get("job", "")
            fam = FAM_RE.sub("", job)
            fl = fam.lower()
            if NOT_BODY_JOB.search(fl) or not (fl in exact or any(S.token_match(fl, k) for k in keys)):
                continue
            fac = v.get("facing")
            if fac not in FACINGS:
                fm = FAM_RE.search(job)
                fac = fm.group(1) if fm else "single"
            fams[fam].setdefault(fac, sha)
            meta[fam] = {"date": v.get("date", ""), "prompt": v.get("prompt", ""), "item": v.get("item")}
    fc = failed_canon_jobs()
    return [{"kind": "artpipe", "faces": f, "date": meta[k]["date"],
             "label": f"render {k}" + (FAILED_CANON_BADGE if _is_failed_canon(k, fc) else ""),
             "detail": f"{meta[k]['date']} · found by NAME — not wired to any graphic of ours yet · {meta[k]['item'] or ''}",
             "prompt": (meta[k]["prompt"] or "")[:240], "bound": False}
            for k, f in sorted(fams.items(), key=lambda kv: meta[kv[0]]["date"], reverse=True)]


# FLYER_FLIPBOOK_ART_1: a wing-beat is a whole-animal flip-book, `<prefix><N>_<facing>` for N = 1..8. Each frame
# is its own artpipe job (`<seq>_<N>_<facing>`), so by name they would show as eight one-frame sets nobody can
# judge. They are joined into ONE set per sequence (faces keyed "N_facing"), drawn as a frames grid with a looping
# playback per facing, and picked as a whole.
FLIP_FAM_RE = re.compile(r"^(?P<seq>.*fl(?:y|ight|ying)\w*?)_(?P<n>\d{1,2})$", re.I)
FLIP_RES_RE = re.compile(r"^(?P<prefix>.*_fly(?:ing)?_?)(?P<n>\d{1,2})$", re.I)
FLIP_FACINGS = ("east", "south", "north")
FLIP_ROLE = "wing-beat flight frames"


def flip_key(n, facing) -> str:
    return f"{int(n)}_{facing}"


def flipbook_cols(idx: L.Index, words, exact, prefixes=()) -> list[dict]:
    """Flip-book sets for a row: artpipe frame sequences found by name (word-bounded, like name_render_cols), and
    live frame sets under any of the row's flyingAnimationFramePathPrefix values."""
    keys = [S.norm(w) for w in words if w and len(S.norm(w)) >= 4]
    exact = {e.lower() for e in exact}
    seqs, meta = defaultdict(dict), {}
    for sha, vs in idx.variants.items():
        if idx.is_purged(sha):
            continue
        for v in vs:
            if v.get("kind") != "artpipe":
                continue
            job = v.get("job", "")
            fm = FLIP_FAM_RE.match(FAM_RE.sub("", job))
            fac = v.get("facing") if v.get("facing") in FLIP_FACINGS else (FAM_RE.search(job) or [None, None])[1]
            if not fm or fac not in FLIP_FACINGS:
                continue
            seq = fm.group("seq")
            sl = seq.lower()
            if not (sl in exact or any(S.token_match(sl, k) for k in keys)):
                continue
            seqs[seq].setdefault(flip_key(fm.group("n"), fac), sha)
            m = meta.setdefault(seq, {"date": "", "prompt": v.get("prompt", ""), "item": v.get("item")})
            m["date"] = max(m["date"], v.get("date", "") or "")
    out = [{"kind": "artpipe", "faces": f, "date": meta[k]["date"], "label": f"flight frames {k}",
            "detail": f"{meta[k]['date']} · {len(f)} frames · {meta[k]['item'] or ''}",
            "prompt": (meta[k]["prompt"] or "")[:240], "bound": False}
           for k, f in sorted(seqs.items(), key=lambda kv: meta[kv[0]]["date"], reverse=True)]
    for pre in prefixes:
        faces = {}
        for (mod, rel), ev in idx.live.items():
            pt = L.parse_texfile(rel)
            fm = FLIP_RES_RE.match(pt["res"])
            if fm and not pt["mask"] and pt["res"].startswith(pre) and pt["facing"] in FLIP_FACINGS:
                faces.setdefault(flip_key(fm.group("n"), pt["facing"]), ev["sha"])
        if faces:
            out.insert(0, {"kind": "live", "faces": faces, "date": "", "winner": True, "bound": True,
                           "label": f"IN GAME — {pre.rsplit('/', 1)[-1]}", "prompt": "",
                           "detail": f"the flip-book the game draws now ({len(faces)} frames under {pre})"})
    return out


def flip_layout(cols: list[dict]) -> tuple[list[str], int, list[str]]:
    """(face keys in grid order, frame count, facings present) for a flip-book graphic."""
    keys = {k for c in cols for k in c["faces"]}
    n = max([int(k.split("_")[0]) for k in keys] + [0])
    fac = [f for f in FLIP_FACINGS if any(k.endswith("_" + f) for k in keys)]
    return [flip_key(i, f) for f in fac for i in range(1, n + 1)], n, fac


def _assign_letters(cols: list[dict], prev: dict, reserved=()) -> None:
    """Reuse the remembered letter for a column whose pictures are unchanged; new columns take the next letter
    never used on this row before (remembered or reserved). Letters are append-only: a set keeps its letter for
    good and a vanished set's letter is never handed to another set."""
    back = {}
    for l, f in (prev or {}).items():
        back.setdefault(tuple(sorted(f.items())), l)
    used = set((prev or {}).keys()) | set(reserved or ())
    for c in cols:
        l = back.get(_fkey(c))
        if l and l not in {d.get("letter") for d in cols}:
            c["letter"] = l
    free = (l for l in LETTERS if l not in used)
    for c in cols:
        if not c.get("letter"):
            c["letter"] = next(free)


def _merge_memory(ruled_rows: dict, prev_rows: dict) -> dict:
    """Letter memory per row: the ruled snapshot's letters win; a later snapshot adds only letters (and sets)
    the ruled one did not have. Every letter either ever carried stays reserved."""
    out = {}
    for k in set(ruled_rows) | set(prev_rows):
        r, p = ruled_rows.get(k) or {}, prev_rows.get(k) or {}
        cols = dict(r.get("columns") or {})
        labels, gof = dict(r.get("labels") or {}), dict(r.get("graphic_of") or {})
        have = {tuple(sorted(f.items())) for f in cols.values()}
        for l, f in (p.get("columns") or {}).items():
            if l not in cols and tuple(sorted(f.items())) not in have:
                cols[l] = f
                have.add(tuple(sorted(f.items())))
                if l in (p.get("labels") or {}):
                    labels[l] = p["labels"][l]
                if l in (p.get("graphic_of") or {}):
                    gof[l] = p["graphic_of"][l]
        reserved = set(r.get("reserved") or []) | set(p.get("reserved") or []) | set(r.get("columns") or {}) \
            | set(p.get("columns") or {})
        out[k] = {"columns": cols, "labels": labels, "graphic_of": gof, "reserved": sorted(reserved, key=LETTERS.index),
                  "subject_key": r.get("subject_key") or p.get("subject_key"), "res": r.get("res") or p.get("res")}
    return out


def _kept_cols(cols: list[dict], mem: dict, used: set) -> list[dict]:
    """A set the owner's decision names (decision / pick / variant letter) that this rebuild no longer finds
    keeps its letter as a KEPT column with the very pictures he ruled on, so the letter still resolves."""
    have = {c["letter"] for c in cols}
    out = []
    for l in sorted(used - have, key=LETTERS.index):
        f = (mem.get("columns") or {}).get(l)
        if not f:
            continue
        lab = (mem.get("labels") or {}).get(l) or f"set {l}"
        out.append({"kind": "kept", "letter": l, "faces": dict(f), "label": lab, "date": "", "winner": False,
                    "prompt": "", "bound": False,
                    "detail": "no longer among this row's current pictures — kept because your decision names it "
                              "(the exact pictures you ruled on)"})
    return out


def _graphic_prefill(g: dict, rulings: list[dict]):
    """(key, why, source) — source: sit1 | ruled | inferred | none."""
    p = g.get("prior")
    if p:
        pf = set((p.get("picked_faces") or {}).values())
        for c in g["cols"]:
            if pf and pf & set(c["faces"].values()):
                return c["letter"], f"your earlier pick ({SIT1}): {p.get('picked_label') or p.get('decision')}", "sit1"
        dec = (p.get("decision") or "").strip()
        if dec in ("redo", "hold"):
            return dec, f"your earlier ruling ({SIT1}): {dec}", "sit1"
    if not g["cols"]:
        return "", "", "none"
    if g["res"] is None:
        return g["cols"][0]["letter"], "inferred: newest render found by name — nothing of ours ships art for this yet", "inferred"
    letter, why, contested = prefill_for({"cols": g["cols"]}, rulings)
    if p:
        why = f"your {SIT1} pick is no longer among these pictures — " + why
    return letter, why, ("inferred" if contested else "ruled")


BIOME_BODY = r"""
/* Layout (owner complaint 2026-10-04, "poorly constructed"): one compact strip per graphic. Each picture
   set is a card whose facings sit SIDE BY SIDE; cards wrap across the width, so a row is about one
   thumbnail tall. Provenance is a tooltip, never wallpaper. Letters are row-local; the pick buttons on
   the right show only this row's letters. */
const FACE_ABBR = { south: 'S', east: 'E', north: 'N', west: 'W', single: '' };
const faceAbbr = f => f in FACE_ABBR ? FACE_ABBR[f] : f.replace(/^(\d+)_(\w).*$/, (m, n, d) => n + d.toUpperCase());
if (!window.__bsAnim) window.__bsAnim = setInterval(() => document.querySelectorAll('.bs-play[data-anim]').forEach(el => {
  const fr = el.dataset.anim.split('|'), i = ((+el.dataset.i || 0) + 1) % fr.length;
  /* advance only once the current frame has loaded: a frame that 404s (the gate's image-less scratch copy) must not
     re-request every 66 ms, which kept headless Edge's virtual clock from ever settling (req 13 hang, 2026-10-07) */
  const im = el.querySelector('img'); if (!im || !im.complete || !im.naturalWidth) return;
  el.dataset.i = i; im.src = fr[i];
}), 66);
/* Variant default (owner, 2026-10-06): a row whose record has no `variants` key starts with EVERY set that is ours
   (not a donor original), not purged and not purgedLive marked as a variant; the owner turns off what is wrong.
   An explicit list, even an empty one, is never overwritten. */
window.artDefaultVariants = (it, d) => {
  const purge = new Set((d && d.purge) || []);
  const out = [];
  for (const g of (it.graphics || [])) for (const c of g.cols) {
    if (c.purgedLive || (c.kind === 'donor' && !c.ours) || out.includes(c.letter)) continue;
    const shas = Object.values(c.faces || {});
    if (shas.length && shas.every(x => purge.has(x))) continue;
    out.push(c.letter);
  }
  return out.sort((a, b) => LETTER_ORDER.indexOf(a) - LETTER_ORDER.indexOf(b));
};
window.artEnsureVariants = (it, rec) => {
  if (rec && !Object.prototype.hasOwnProperty.call(rec, 'variants')) {
    rec.variants = window.artDefaultVariants(it, rec); rec.variantsDefault = true;
  }
};
const _itemBody = it => {
  const d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
  const purge = new Set(d.purge || []);
  const picks = Object.assign({}, it.prefillPicks || {}, d.picks || {});
  const variants = new Set(Object.prototype.hasOwnProperty.call(d, 'variants') ? d.variants : window.artDefaultVariants(it, d));
  const cell = (c, f) => {
    const s = c.faces[f];
    if (!s) return `<div class="bs-cell bs-gap" title="no ${f} picture in this set">—</div>`;
    const t = it.thumbs[s];
    if (!t) return `<div class="bs-cell bs-gap" title="picture not archived">?</div>`;
    const p = purge.has(s);
    const btn = c.purgeable ? `<button class="ac-purge${p ? ' on' : ''}" title="reject + PURGE: delete this picture from the art store so it never appears again" onclick="event.stopPropagation();artTogglePurge('${it.id}','${s}')">${p ? '✕ purging' : '✕'}</button>` : '';
    const ab = faceAbbr(f);
    return `<div class="bs-cell${p ? ' ac-purged' : ''}"><div class="thumb ac-thumb" data-zoom="${t}" data-cap="${esc(it.label)} · ${c.letter} · ${f}"><img src="${t}" loading="lazy" alt=""></div>${ab ? `<span class="bs-face">${ab}</span>` : ''}${btn}</div>`;
  };
  /* flip-book (wing-beat) sets: one grid row per facing, a looping playback cell first, then frames 1..N */
  const faces = (c, g) => {
    if (!g.flip) return `<div class="bs-faces">${g.facings.map(f => cell(c, f)).join('')}</div>`;
    const rows = g.flipFacings.map(face => {
      const ks = g.facings.filter(k => k.endsWith('_' + face));
      const fr = ks.map(k => c.faces[k] && it.thumbs[c.faces[k]]).filter(Boolean);
      const play = fr.length ? `<div class="bs-cell bs-play" title="${face}: the frames looping at half game speed" data-anim="${fr.join('|')}"><img src="${fr[0]}" alt=""><span class="bs-face">▶${FACE_ABBR[face]}</span></div>` : '<div class="bs-cell bs-gap">—</div>';
      return play + ks.map(k => cell(c, k)).join('');
    }).join('');
    return `<div class="bs-faces bs-frames" style="grid-template-columns:repeat(${g.nframes + 1},auto)">${rows}</div>`;
  };
  const col = (c, g) => {
    const picked = g.primary ? d.decision === c.letter : picks[g.key] === c.letter;
    const tip = `${c.label}\n${c.detail}${c.ppc ? `\n\nresolution: ${c.srcPx[0]}×${c.srcPx[1]} px over the ${it.scale.kind === 'plant' ? 'quad' : 'drawSize'} = ${c.ppc} px/cell` : ''}${c.also ? '\n\nidentical copies:\n' + c.also.join('\n') : ''}${c.prompt ? '\n\nprompt: ' + c.prompt : ''}`;
    const vr = variants.has(c.letter);
    const vbtn = `<button class="bs-var${vr ? ' on' : ''}" title="keep this set as a valid VARIANT as well as your one pick (saved as variants: [...] on the row)" onclick="event.stopPropagation();artToggleVariant('${it.id}','${c.letter}')">${vr ? '✓ variant' : '+ variant'}</button>`;
    return `<div class="bs-set ac-${c.kind}${c.winner ? ' ac-win' : ''}${picked ? ' ac-picked' : ''}${vr ? ' bs-isvar' : ''}">
      <div class="bs-head${c.purgedLive ? '' : ' bs-pick'}"${c.purgedLive ? '' : ` data-pick-id="${esc(it.id)}" data-pick-g="${esc(g.key)}" data-pick-l="${c.letter}" data-pick-primary="${g.primary ? 1 : 0}"`} title="${esc(tip)}${c.purgedLive ? '' : '\n\nclick to pick this set'}"><b>${c.letter}</b>${c.near_of ? `<i class="bs-nearof" title="near-duplicate of set ${c.near_of} (dHash within ${NEAR_BITS} bits on every facing)">≈${c.near_of}</i>` : ''}<span>${esc(c.short)}</span>${c.placeholder ? `<i class="bs-ph" title="${esc(c.placeholder)}">PLACEHOLDER</i>` : ''}${c.purgedLive ? `<i class="bs-ph" title="You purged this picture. The game still shows it until a replacement is installed, so it is listed here for reference only and cannot be picked.">you purged this — still live until a replacement is installed</i>` : ''}${c.also ? `<i class="sub">+${c.also.length}</i>` : ''}</div>
      ${faces(c, g)}
      <div class="bs-foot">${vbtn}${g.primary && c.ppc ? `<i class="bs-ppc" title="resolution of this set: ${c.srcPx[0]} px wide over ${fmt(it.scale.kind === 'plant' ? it.scale.quad : (it.scale.drawSize||[])[0])} cells = ${c.ppc} px per cell (enhanced zoom resolves 128–256)">${c.ppc} px/cell</i>` : ''}</div>
    </div>`;
  };
  const donorAbs = it.donorAbsent ? `<div class="bs-canonp"><div class="bs-head bs-chead"><b>donor column</b><span>${esc(it.donorAbsent)}</span></div></div>` : '';
  const canon = it.canon ? `<div class="bs-canonp"><div class="bs-head bs-chead"><b>canon</b><span>${it.canon.base ? 'entry for the base species: ' + esc(it.canon.base) : 'reference — not pickable'}</span></div>
      <div class="bs-cimgs">${it.canon.imgs.map(u => `<div class="thumb bs-cthumb" data-zoom="${u}" data-cap="canon reference · ${esc(it.canon.dir)}"><img src="${u}" loading="lazy" alt=""></div>`).join('') || '<span class="sub">entry has no images</span>'}</div>
      <div class="bs-must"><b>Must show</b><pre>${esc(it.canon.must || '(this entry lists no Must show)')}</pre>${it.canon.ruling ? `<b>Your ruling on the entry</b><pre>${esc(it.canon.ruling)}</pre>` : ''}<details><summary>visual brief</summary><pre>${esc(it.canon.brief)}</pre></details></div></div>` : '';
  const sec = (g, i) => {
    /* Every set in LETTER order, so the letters read contiguously (owner, Vhaulk note 2026-10-04: "I see only
       A and C, no B"). A near-duplicate keeps its place and its letter as a narrow stub that expands in place. */
    const ordered = g.cols.slice().sort((a, b) => LETTER_ORDER.indexOf(a.letter) - LETTER_ORDER.indexOf(b.letter));
    const stub = c => `<details class="bs-nearstub"${d.decision === c.letter || picks[g.key] === c.letter || variants.has(c.letter) ? ' open' : ''}><summary title="set ${c.letter} looks almost the same as set ${c.near_of} — click to show it"><b>${c.letter}</b><span>≈ ${c.near_of}</span><span class="sub">near-<br>duplicate<br>▸ show</span></summary>${col(c, g)}</details>`;
    const many = it.graphics.length > 1;
    const cur = g.primary ? d.decision : picks[g.key];
    const head = many ? `<div class="bs-gh" title="${esc(g.res || 'renders matched by name, not bound to a texture path')}"><b>${esc(g.role)}</b>${g.res ? ` <span class="sub">${esc(g.res.split('/').pop())}</span>` : ''} · ${g.primary ? 'buttons on the right' : `click a set · picked <b>${esc(cur || 'nothing')}</b>`}</div>` : '';
    const prior = g.prior ? `<div class="bs-prior" title="${esc(g.prior.was)}">${esc(g.prior.text)}${g.prior.note ? ' — “' + esc(g.prior.note) + '”' : ''}</div>` : '';
    return `<div class="bs-g">${head}${prior}
      <div class="bs-strip">${ordered.map(c => c.near_of ? stub(c) : col(c, g)).join('')}</div></div>`;
  };
  const links = it.related.length ? `<div class="bs-links">related (judged separately): ${it.related.map(r => `<a href="#" data-jump="${esc(r.id)}">${esc(r.label)} <span class="sub">${esc(r.id)}</span></a> <span class="sub">${esc(r.why)}</span>`).join(' · ')}</div>` : '';
  const elsewhere = it.elsewhere.length ? `<div class="sub">also related, not in this biome: ${it.elsewhere.map(esc).join(', ')}</div>` : '';
  const purgedNote = it.purgedHidden ? `<div class="sub" title="pictures you rejected with the purge mark; they no longer appear on any sheet">${it.purgedHidden} purged picture${it.purgedHidden === 1 ? '' : 's'} hidden</div>` : '';
  const noart = it.noArt ? `<div class="bs-noart">NO ART YET — nothing found after searching every source:<div style="font-size:11px;font-weight:normal;opacity:.85;margin-top:3px;word-break:break-word">${esc(it.noArtWhy)}</div></div>` : '';
  const rline = r => `<div class="ac-r bs-r ac-t-${r.trust}" title="${esc(r.at + ' ' + r.verdict + ' · ' + r.trust + ' · ' + r.sheet + (r.note ? '\n“' + r.note + '”' : ''))}">${esc(r.at)} <b>${esc(r.verdict)}</b> <span class="sub">${esc(r.trust)} · ${esc(r.sheet)}</span> ${r.note ? '“' + esc(r.note) + '”' : ''}</div>`;
  const rs = it.rulings.slice().reverse();          /* newest first; older ones fold */
  const rul = rs.length ? `<div class="ac-rulings">${rs.slice(0, 2).map(rline).join('')}${rs.length > 2 ? `<details><summary class="sub">${rs.length - 2} older ruling(s)</summary>${rs.slice(2).map(rline).join('')}</details>` : ''}</div>` : '';
  const ds = it.desc || {};
  const dtext = ds.description || '';
  const desc = !ds.def ? `<div class="bs-desc sub">in-game description: UNMEASURED — no ThingDef of this row in the live def dump</div>`
    : dtext.length > 260 ? `<details class="bs-desc" title="${esc(ds.source)}"><summary><b>${esc(ds.label)}</b> — <span class="bs-dclamp">${esc(dtext)}</span></summary></details>`
    : `<div class="bs-desc" title="${esc(ds.source)}"><b>${esc(ds.label)}</b> — ${esc(dtext || '(the def has no description)')}</div>`;
  const pf = it.prefillSource === 'sit1' ? '' : it.contested ? '<span class="mark inferred" title="' + esc(it.prefillWhy) + '">⚠ agent prefill: ' + esc(it.prefillShort) + '</span>' : '<span class="mark absent">prefill: ' + esc(it.prefillShort) + '</span>';
  const re = it.ruledElsewhere;
  const reHead = re ? `<summary class="bs-ruledsum" title="You already ruled on this subject on another sheet, so it needs no pick here. Expand to see the pictures and change your mind.">Already ruled on <b>${esc(re.sheet)}</b>: ${esc(re.pick)}${re.label ? ' — ' + esc(re.label) : ''}${re.note ? ' · “' + esc(re.note) + '”' : ''} <span class="sub">${esc(re.at)} · expand to change your mind</span></summary>` : '';
  const inner = `<div class="ac-body bs-body" style="${it.band ? 'border-left:6px solid ' + it.band + ';padding-left:8px' : ''}">
    <div class="bs-meta"><div class="effect">${esc(it.effect)}</div>
    <div class="marks"><span class="mark bs-tier bs-${it.tier}">${esc(it.tierText)}</span>${it.canonTag ? `<span class="mark bs-nocanon">${esc(it.canonTag)}</span>` : ''}${it.flags.filter(f => f !== 'NO ART YET').map(f => `<span class="mark contested">${esc(f)}</span>`).join('')}${pf}</div>
    ${desc}${links}${elsewhere}${rul}${purgedNote}${noart}</div>
    <div class="bs-content"><div class="bs-graphics">${it.graphics.map(sec).join('')}</div>${scaleBlock(it)}${donorAbs}${canon}</div></div>`;
  return re ? `<details class="bs-ruled">${reHead}${inner}</details>` : inner;
};
const fmt = x => (x == null ? '?' : (+x).toFixed(3).replace(/\.?0+$/, ''));
function scaleBlock(it) {
  const s = it.scale; if (!s) return '';
  const size = s.kind === 'plant'
    ? `<b>${fmt(s.quad)}-cell</b> plant <span class="sub">= drawSize.x ${fmt((s.drawSize||[])[0])} × visualSize.max ${fmt(s.visualMax)}</span>${s.mesh > 1 ? ` · <b>×${s.mesh}</b> per cell` : ''}`
    : `<b>${fmt(s.cells)} cells</b> <span class="sub">adult drawSize ${fmt((s.drawSize||[])[0])}×${fmt((s.drawSize||[])[1])}</span> · bodySize ${fmt(s.bodySize)}`;
  const sizeTip = s.kind === 'plant' ? `Plant.Print draws a SQUARE quad of drawSize.x × visualSizeRange (max at maturity)${s.mesh > 1 ? `; maxMeshCount ${s.mesh} prints ${s.mesh} quads on a ${Math.round(Math.sqrt(s.mesh))}×${Math.round(Math.sqrt(s.mesh))} sub-grid of ONE cell` : '; one mesh, centred, lifted so its base sits on the cell edge'}` : 'the adult (last) life stage bodyGraphicData.drawSize — what the engine draws';
  const q = s.kind === 'plant' ? s.quad : (s.drawSize || [])[0];
  const vcls = !s.ppc ? '' : s.ppc < 64 ? 'bs-low' : s.ppc < 120 ? 'bs-mid' : s.ppc > 256 ? 'bs-over' : 'bs-ok';
  const res = s.img ? `<div class="bs-scl bs-scres ${vcls}" title="${esc(s.verdict)}. Enhanced zoom (owner, 2026-10-04) resolves 128–256 px per cell of the draw size; below 128 reads soft at max zoom, below 64 loses detail. Shown: set ${esc(s.set)} (${esc(s.by)}, ${esc(s.face)} facing).">set <b>${esc(s.set)}</b> · ${s.srcPx[0]}px ÷ ${fmt(q)} = <b>${s.ppc} px/cell</b> <span class="sub">${s.ppc < 64 ? 'below 64 floor' : s.ppc < 120 ? 'soft at max zoom' : s.ppc > 256 ? 'above 256 max zoom' : 'in the 128–256 zoom range'} · ${esc(s.by)}</span></div>` : `<div class="sub">${esc(s.why || '')}</div>`;
  const pic = s.img ? `<div class="bs-scimg" data-zoom="${s.full}" data-cap="${esc(it.label)} · set ${esc(s.set)} · max zoom ${s.zoomFullPpc || '?'} px/cell (human | this), then normal play 32 and zoomed out 18 px/cell, each also ×4 nearest"><img src="${s.img}" alt=""></div>` : '';
  return `<div class="bs-scale"><div class="bs-head bs-schead"><b>in-game size</b><span>vanilla human beside it at the same scale · max zoom ${s.zoomPpc ? s.zoomPpc + ' px/cell' : ''}${s.zoomFitted ? ' (shrunk to fit)' : ''}${s.zoomCropped ? ' (cropped, not shrunk)' : ''} + normal play 32 · click to enlarge</span></div>${pic}
    <div class="bs-scl bs-scsize" title="${esc(sizeTip)}">${size}</div>${res}
    <div class="bs-scsrc ${s.status === 'measured' ? '' : 'bs-fallback'}" title="${esc(s.source)}">${s.status === 'measured' ? 'MEASURED' : 'FALLBACK'} · ${esc(s.source)}</div></div>`;
}

const LETTER_ORDER = "%LETTERS%";
const NEAR_BITS = %NEAR%;
window.artToggleVariant = (id, letter) => {
  if (frozen) return;
  const it = byId.get(id); if (!it) return;
  const rec = DEC[id] || (DEC[id] = { decision: '', note: '', prefill: prefillOf(it) });
  window.artEnsureVariants(it, rec);
  const s = new Set(rec.variants || []);
  if (s.has(letter)) s.delete(letter); else s.add(letter);
  delete rec.variantsDefault;
  rec.variants = [...s].sort((a, b) => LETTER_ORDER.indexOf(a) - LETTER_ORDER.indexOf(b));
  rec.variantsAt = new Date().toISOString();
  queue(id); patchRow(id); paintCounts();
};
window.artPick = (id, g, letter) => {
  if (frozen) return;
  const it = byId.get(id); if (!it) return;
  const rec = DEC[id] || (DEC[id] = { decision: '', note: '', prefill: prefillOf(it) });
  rec.picks = Object.assign({}, it.prefillPicks || {}, rec.picks || {});
  rec.picks[g] = letter; rec.decidedAt = new Date().toISOString();
  queue(id); patchRow(id); paintCounts();
};
document.addEventListener('click', e => {
  if (e.target.closest('.ac-purge') || e.target.closest('.bs-var')) return;
  const p = e.target.closest('[data-pick-l]');
  if (p) {
    e.preventDefault(); e.stopPropagation();
    if (p.dataset.pickPrimary === '1') setDecision(p.dataset.pickId, p.dataset.pickL);
    else window.artPick(p.dataset.pickId, p.dataset.pickG, p.dataset.pickL);
    return;
  }
  const j = e.target.closest('[data-jump]');
  if (j) {
    e.preventDefault(); e.stopPropagation();
    const node = document.querySelector(`.row[data-id="${cssEsc(j.dataset.jump)}"]`);
    if (node) { node.scrollIntoView({ block: 'center' }); node.classList.add('bs-flash'); setTimeout(() => node.classList.remove('bs-flash'), 1500); }
    else alert('That row is hidden by the current filter.');
  }
}, true);
/* rebuilt-sheet notice: poll the served page every ~60 s; when its build stamp (the gate stamp, else a hash of the HTML) differs
   from what this tab loaded, show a banner. NEVER auto-reloads: an unsaved note would be lost. */
(() => {
  const fp = t => { const m = t.match(/<meta name="scaled-review-gate" content="([^"]*)">/); if (m) return m[1];
    let h = 2166136261; for (let i = 0; i < t.length; i += 7) { h ^= t.charCodeAt(i); h = Math.imul(h, 16777619); } return 'h' + (h >>> 0) + ':' + t.length; };
  const get = () => fetch(location.href, { cache: 'no-store' }).then(r => r.ok ? r.text() : null).then(t => t && fp(t)).catch(() => null);
  let base = null, shown = false;
  const banner = () => { if (shown) return; shown = true; const d = document.createElement('div');
    d.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#b8860b;color:#000;padding:10px 14px;font:600 15px sans-serif;display:flex;gap:14px;align-items:center;box-shadow:0 2px 8px #000';
    d.innerHTML = '<span>This sheet was rebuilt with new content — reload (your picks are saved)</span><button style="font:600 14px sans-serif;padding:4px 12px;cursor:pointer">Reload now</button><button style="font:14px sans-serif;padding:4px 10px;cursor:pointer">dismiss</button>';
    d.children[1].onclick = () => location.reload(); d.children[2].onclick = () => d.remove(); document.body.appendChild(d); };
  get().then(f => { base = f; });
  setInterval(() => get().then(f => { if (f && base && f !== base) banner(); }), 60000);
})();
window.itemBody = it => { try { return _itemBody(it); } catch (e) { return `<div class="bs-noart">row render error (this row only; the sheet is intact): ${esc(String(e && e.message || e))}</div>`; } };
"""

BIOME_STYLE = """
<style>
.bs-body{display:flex;gap:14px;align-items:flex-start}
.bs-meta{flex:0 0 300px;min-width:0}
.bs-meta .effect{font-size:12px}
.bs-r{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bs-content{flex:1;min-width:0;display:flex;flex-wrap:wrap;gap:10px;align-items:flex-start}
@media (max-width:1450px){.bs-body{display:block}.bs-meta{margin-bottom:4px}
  .bs-cell,.bs-cell .ac-thumb{width:72px;height:72px;flex-basis:72px}}
.bs-graphics{flex:1 1 340px;min-width:0;display:flex;flex-wrap:wrap;gap:6px 16px;align-items:flex-start}
.bs-g{max-width:100%;min-width:0}
.bs-gh{font-size:12px;color:#d8c7a8;margin:2px 0}
.bs-strip{display:flex;flex-wrap:wrap;gap:6px;align-items:flex-start}
.bs-set{border:1px solid var(--line);border-radius:6px;padding:3px;background:#0f1216;max-width:100%}
.bs-set.ac-win{border-color:var(--info)}
.bs-set.ac-picked{border-color:var(--ok);box-shadow:0 0 0 2px #5ac37f66}
.bs-head{display:flex;gap:5px;align-items:baseline;font-size:11px;line-height:1.3;height:1.35em;overflow:hidden;color:var(--ink);width:0;min-width:100%;box-sizing:border-box;padding:0 2px}
.bs-head span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.bs-head b{font-size:13px;color:var(--accent)}
.bs-head i{font-style:normal;flex:none}
.bs-set.ac-artpipe .bs-head span{color:#d9b8ff}.bs-set.ac-git .bs-head span{color:#9fb3c8}.bs-set.ac-donor .bs-head span{color:#e8b64c}
.bs-set.ac-win .bs-head span{color:#8ac3e8;font-weight:600}
.bs-pick{cursor:pointer}.bs-set:hover{border-color:#3d4653}.bs-set.ac-picked:hover{border-color:var(--ok)}
.bs-faces{display:flex;gap:3px;cursor:default}
.bs-frames{display:grid;gap:3px}
.bs-play{outline:2px solid #e8b64c;outline-offset:-2px}
.bs-cell{position:relative;width:86px;height:86px;display:flex;align-items:center;justify-content:center}
.bs-cell .ac-thumb{width:86px;height:86px;flex:0 0 86px}
.bs-gap{color:#3a4250;font-size:18px;border:1px dashed #222a33;border-radius:5px}
.bs-face{position:absolute;left:3px;bottom:2px;font-size:9.5px;color:#8a95a5;background:#0b0d10cc;border-radius:2px;padding:0 3px;pointer-events:none}
.bs-nearstub{align-self:stretch}
.bs-nearstub>summary{list-style:none;cursor:pointer;height:100%;min-height:60px;box-sizing:border-box;width:58px;border:1px dashed #3d4653;border-radius:6px;padding:3px;font-size:10.5px;color:var(--dim);display:flex;flex-direction:column;gap:2px;line-height:1.25}
.bs-nearstub>summary::-webkit-details-marker{display:none}
.bs-nearstub>summary b{font-size:13px;color:var(--accent)}
.bs-nearstub[open]{display:flex;gap:4px}.bs-nearstub[open]>summary{width:auto;min-height:0;height:auto}
.bs-nearstub[open]>summary .sub{display:none}
.bs-nearof{color:#9fb3c8;font-size:10.5px}
.bs-foot{display:flex;flex-wrap:wrap;gap:3px 6px;align-items:center;justify-content:space-between;margin-top:3px;width:0;min-width:100%}
.bs-var{font-size:10.5px;padding:1px 7px;border-radius:4px;border:1px solid #2f4a35;background:#0f1612;color:#7fae86;cursor:pointer;opacity:.75}
.bs-var:hover{opacity:1}.bs-var.on{background:#2f7a45;color:#fff;border-color:#5ac37f;opacity:1}
.bs-set.bs-isvar{border-style:dashed;border-color:#5ac37f}
.bs-desc{font-size:12px;line-height:1.4;color:#d8cdb8;margin:4px 0;padding:3px 6px;border-left:3px solid #6a5a3a;background:#15120d}
.bs-desc b{color:#e8d6a8}
details.bs-desc>summary{cursor:pointer;list-style:none}
details.bs-desc>summary::-webkit-details-marker{display:none}
details.bs-desc:not([open]) .bs-dclamp{display:-webkit-inline-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden;vertical-align:top}
details.bs-desc:not([open])>summary::after{content:" ▸ more";color:#e8b64c;font-size:11px}
details.bs-desc[open]>summary::after{content:" ▴ less";color:#e8b64c;font-size:11px}
.bs-canonp{flex:0 0 300px;border:1px solid #5a4a2a;background:#14110c;border-radius:6px;padding:3px 5px}
.bs-chead span{color:#e8b64c}.bs-chead b{color:#e8b64c}
.bs-cimgs{display:flex;gap:4px;flex-wrap:wrap;margin:3px 0}
.bs-cthumb{width:68px;height:68px;flex:0 0 68px}
.bs-must{font-size:11.5px;color:#c3cad6;max-height:112px;overflow:auto}
.bs-must pre{white-space:pre-wrap;font:inherit;margin:1px 0 4px}
.bs-must summary{cursor:pointer;color:var(--dim)}
.bs-prior{font-size:11.5px;color:#9fe0a8;margin:1px 0 2px}
.bs-links{font-size:12px;margin:3px 0;color:#d8c7a8}.bs-links a{color:#e8b64c}
.bs-noart{display:inline-block;font-size:12.5px;font-weight:700;color:#000;background:#e06c6c;padding:4px 10px;border-radius:5px;margin:5px 0 0}
.bs-tier{border-color:#5a4a2a}.bs-canon{background:#3a2c10;color:#e8b64c}.bs-ours{background:#10283a;color:#8ac3e8}
.bs-ph{background:#b3261e;color:#fff;font-style:normal;font-weight:700;padding:1px 5px;border-radius:3px;margin-left:4px;font-size:.8em}.bs-sw{background:#2a1a3a;color:#c38ae8}.bs-donor{background:#222;color:#aaa}
.mark.bs-nocanon{color:#b9a27a;border-color:#4a3f2a;background:#15120c}
.row.bs-flash{outline:3px solid #e8b64c}
.bs-scale{flex:0 1 auto;width:min-content;min-width:350px;max-width:100%;box-sizing:border-box;border:1px solid #3a4a3a;background:#10140f;border-radius:6px;padding:3px 5px;font-size:11.5px}
.bs-schead b{color:#9fe0a8;flex:none}.bs-schead span{color:#8aa58a}
.bs-scimg{overflow-x:auto;cursor:zoom-in;margin:3px 0 2px}
.bs-scimg img{display:block;max-width:none;width:auto;height:auto;image-rendering:pixelated}
.bs-scsize{color:#d8c7a8}
.bs-scl{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bs-scale>.bs-scl,.bs-scale>.bs-scsrc,.bs-scale>.bs-head{width:0;min-width:100%;box-sizing:border-box}
.bs-scres b{color:#fff}.bs-scres.bs-low b{color:#e06c6c}.bs-scres.bs-mid b{color:#e8b64c}.bs-scres.bs-over b{color:#8ac3e8}.bs-scres.bs-ok b{color:#9fe0a8}
.bs-scsrc{color:#7f8a7f;font-size:10.5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.bs-scsrc.bs-fallback{color:#e06c6c}
.bs-set{position:relative}
.bs-ppc{font-style:normal;white-space:nowrap;color:#9fe0a8;background:#0b0d10d9;border-radius:3px;padding:0 4px;font-size:10px;pointer-events:auto}
/* a subject already ruled on another sheet: dimmed pick column until expanded */
.row:has(.bs-ruled:not([open])) .ctrl{opacity:.35}
.bs-ruledsum{cursor:pointer;color:#9fb6c9;padding:2px 0;font-size:12px}
.bs-ruled[open]>.bs-ruledsum{margin-bottom:6px}
/* right-hand pick column: only this row's letters, readable redo/hold */
.row .ctrl{width:200px}
.row .opts{flex-wrap:wrap}
.row .opts button{flex:0 0 auto;min-width:30px;padding:3px 0}
.row .opts button[data-set="redo"]{margin-left:auto}
.row .opts button[data-set="redo"],.row .opts button[data-set="hold"]{flex:1 1 40%;padding:4px 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row .opts button[data-set="redo"]{order:98}.row .opts button[data-set="hold"]{order:99}
.row .opts::after{content:"";order:97;flex-basis:100%;height:0}
@media (max-width:1400px){.bs-canonp{flex-basis:240px}.bs-cthumb{width:56px;height:56px;flex-basis:56px}}
</style>
"""


def _fill_template(cfg: dict, items: list, render: str, title: str) -> str:
    tpl = (SKILL / "sheet_template.html").read_text()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<!-- ══ FILL IN #3 (optional)", render + "\n<!-- ══ FILL IN #3 (optional)", 1)
    return re.sub(r"<title>.*?</title>", f"<title>{title}</title>", tpl, count=1, flags=re.S)


def _clusters(rows: list[dict]):
    """Two-way related links from census twins (only between rows on this sheet) + union-find clusters."""
    of = {}
    for r in rows:
        for dn in [r["key"], r.get("port")] + list(r.get("defNames") or []):
            if dn:
                of.setdefault(dn, r["key"])
    rel, elsewhere = defaultdict(dict), defaultdict(list)
    for r in rows:
        for t in r.get("twins") or []:
            o = of.get(t["defName"])
            if o and o != r["key"]:
                why = t.get("relation", "").replace("_", " ")
                rel[r["key"]].setdefault(o, why)
                rel[o].setdefault(r["key"], why)
            elif not o:
                elsewhere[r["key"]].append(f"{t['defName']} ({t.get('relation', '').replace('_', ' ')})")
    parent = {r["key"]: r["key"] for r in rows}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, bs in rel.items():
        for b in bs:
            parent[find(a)] = find(b)
    return rel, elsewhere, find


BIOME_BRIEF = """<p><b>{label}</b> — every flora and fauna row of this biome ({n} rows), one row per species. Each row shows
<b>every picture we hold</b> for it: <b>IN GAME</b> (blue frame) is what the game draws now; <b>shipped, shadowed</b> is a copy losing
the load-order race; <b>render</b> columns are artpipe outputs (newest first); <b>history</b> columns are earlier states of our files
from git; <b>donor original</b> is the donor mod's own sprite. Each set shows its facings side by side (S, E, N);
hover a set's header for where it came from.</p>
<p><b>Pick, per row, the column the game should show</b> (letter buttons, or click a column's header). A row with a second graphic
(swimming, flying) shows it as its own strip — click a column header there to pick for it. <b>✕</b> on a non-live picture rejects and
purges it for good. The note box is the most useful control on the row: say what is wrong, and a redo is written from it.</p>
<p><b>Canon rows</b> show the canon-library reference images and the entry's <b>Must show</b> list beside the pictures. A canon creature and
our own (franchise-free) stand-in for it are <b>separate rows</b>, each judged on its own, but grouped together under one coloured band
with a <b>related</b> link both ways. A stand-in's Star Wars twin (RSW_) is always its own full row in the band, even where the biome
never casts it. Rows you already ruled on in <b>desert sitting 1</b> are prefilled with that pick and say so
(green line naming the set). The counter separates rows <b>you</b> decided from rows still holding the agent's
prefill. Nothing installs from this sheet: your picks become ledger rulings, then you see an install plan.</p>"""


# Ground colour behind the scaled portrayal (owner 2026-10-05: "You also did not include the scaled portrayal on that
# sheet"): the panel is UNCONDITIONAL, on every biome sheet. The colour is MEASURED per biome by measure_ground():
# the mean opaque RGB of the texture of the biome's lowest-fertility terrain (terrainsByFertility, first threshold =
# the dominant ground at low fertility) from the def dump -> TerrainDef.texturePath -> an installed texture (our src/,
# vanilla bundle_textures by basename, then the Steam Mods / workshop folders). Where nothing can be measured the panel
# uses scale_panel's default tan and the sheet's progress record lists the biome. Hand measurements below predate the
# function and are kept as overrides only where they were taken from the texture the owner named.
SCALE_BIOMES = {"RM_LongShade": None, "RM_Stillsand": (126, 110, 91), "RM_BlueDesert": (155, 164, 172),
                # Abyss: AB_ForsakenSands.png (near-black, 25,25,35); Cauldron: RM_CauldronSoil -> Soil.png (93,76,61);
                # Contagion: GU_AlienSand/GU_AlienSandFine mean (fine sand dominates fertility < 0.2)
                "RM_Abyss": (24, 24, 34), "RM_Cauldron": (93, 76, 61), "RM_Contagion": (145, 113, 115)}
STEAM_ROOTS = [Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"),
               Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")]
_GROUND: dict = {}
GROUND_LOG: dict = {}


def _find_terrain_png(tex_path: str):
    base = tex_path.replace("\\", "/")
    hits = list((L.REPO_ROOT / "src").glob(f"**/Textures/{base}.png"))
    if hits:
        return hits[0]
    van = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core") / (base.split("/")[-1] + ".png")
    if van.is_file():
        return van
    for root in STEAM_ROOTS:
        if root.is_dir():
            for mod in root.iterdir():
                for sub in ("Textures", "1.6/Textures", "Common/Textures"):
                    f = mod / sub / (base + ".png")
                    if f.is_file():
                        return f
    return None


def measure_ground(biome: str):
    """(rgb, source) — mean opaque RGB of the biome's low-fertility ground texture — or (None, why it is unmeasurable)."""
    if biome in _GROUND:
        return _GROUND[biome]
    import sqlite3
    from PIL import Image
    why = ""
    try:
        import scale_panel
        db = sqlite3.connect(str(scale_panel.DB))
        r = db.execute("select json from defs where def_name=? and def_type='BiomeDef'", (biome,)).fetchone()
        tbf = sorted(((json.loads(r[0]).get("fields") or {}).get("terrainsByFertility") or []),
                     key=lambda t: t.get("min", 0)) if r else []
        if not tbf:
            why = "BiomeDef has no terrainsByFertility in the def dump"
        for t in tbf:
            tr = db.execute("select json from defs where def_name=? and def_type='TerrainDef'", (t.get("terrain"),)).fetchone()
            tp = ((json.loads(tr[0]).get("fields") or {}).get("texturePath")) if tr else None
            f = _find_terrain_png(tp) if tp else None
            if not f:
                why = f"terrain {t.get('terrain')}: texture {tp or 'not in dump'} not found"
                continue
            im = Image.open(f).convert("RGBA")
            px = [p for p in im.getdata() if p[3] > 8]
            if not px:
                continue
            rgb = tuple(round(sum(p[i] for p in px) / len(px)) for i in range(3))
            _GROUND[biome] = (rgb, f"{t.get('terrain')} -> {tp} ({f.name}, mean of {len(px)} opaque px)")
            return _GROUND[biome]
    except Exception as e:                                  # noqa: BLE001
        why = f"{type(e).__name__}: {e}"
    _GROUND[biome] = (None, why or "no terrain texture measurable")
    return _GROUND[biome]


SCALE_FACE = ("east", "south", "single", "west", "north")
SCALE_RENDER_VERSION = 6   # 2 = max-zoom primary scene (owner 2026-10-04: enhanced zoom, "don't down-resolve")


def _img_px(sha: str):
    from PIL import Image
    try:
        return Image.open(L.store_path(sha)).size
    except Exception:                                       # noqa: BLE001
        return None


def _scale_for(R, row: dict, gitems: list, prefill_letter: str, dec: dict | None, imgdir: Path) -> dict:
    """In-game size (cells, with its SOURCE) + a true-scale panel of the set the owner picked (else the
    prefill), and px/cell for every set of the body graphic. See scale_panel.py for the measurement."""
    import scale_panel as SP
    size = R.size(row)
    out = {"status": size["status"], "source": size["source"], "kind": size.get("kind"),
           "cells": round(size["cells"], 3), "bodySize": size.get("bodySize"), "mesh": size.get("mesh"),
           "drawSize": size.get("drawSize"), "visualMax": size.get("visualMax"), "quad": size.get("quad")}
    prim = next((g for g in gitems if g["primary"]), None)
    if prim is None:
        out["why"] = "no picture to scale"
        return out
    qx = (size.get("drawSize") or [None])[0] if size.get("kind") == "animal" else size.get("quad")
    sets = []
    for c in prim["cols"]:
        f = next((f for f in SCALE_FACE if f in c["faces"] and L.store_has(c["faces"][f])), None)
        px = _img_px(c["faces"][f]) if f else None
        c["ppc"] = round(px[0] / qx) if (px and qx) else None
        c["srcPx"] = list(px) if px else None
        sets.append((c["letter"], f, px))
    want = (dec or {}).get("decision") or ""
    by = "your pick"
    if not (dec or {}).get("decidedAt") or want not in [c["letter"] for c in prim["cols"]]:
        want, by = prefill_letter, "prefill"
    col = next((c for c in prim["cols"] if c["letter"] == want), None) or prim["cols"][0]
    if col["letter"] != want:
        by = "first set (no pick, no prefill)"
    f = next((f for f in SCALE_FACE if f in col["faces"] and L.store_has(col["faces"][f])), None)
    if not f:
        out["why"] = f"set {col['letter']} has no archived picture"
        return out
    sha = col["faces"][f]
    stem = re.sub(r"[^A-Za-z0-9_]", "_", row["key"]) + "_" + sha[:10] + "_" + hashlib.sha1(
        json.dumps([SCALE_RENDER_VERSION, SP.TERRAIN, size.get("drawSize"), size.get("quad"), size.get("mesh"),
                    size.get("color")]).encode()).hexdigest()[:6]
    comp, full, mj = imgdir / f"scale_{stem}.png", imgdir / f"scale_{stem}_full.png", imgdir / f"scale_{stem}.json"
    try:
        m = json.loads(mj.read_text()) if comp.exists() and full.exists() else None
    except (OSError, ValueError):
        m = None
    if m is None:
        m = SP.render_panel(L.store_get(sha), size, comp, full)
        mj.write_text(json.dumps(m))
    out.update({"img": f"{imgdir.name}/{comp.name}", "full": f"{imgdir.name}/{full.name}", "set": col["letter"],
                "by": by, "face": f, "srcPx": m["srcPx"], "ppc": m["pxPerCell"], "verdict": SP.ppc_verdict(m["pxPerCell"]),
                "zoomPpc": m.get("zoomPpc"), "zoomFitted": m.get("zoomFitted"), "zoomCropped": m.get("zoomCropped"), "zoomFullPpc": m.get("zoomFullPpc"),
                "sets": [{"l": l, "ppc": (round(px[0] / qx) if px and qx else None), "px": (px[0] if px else None)}
                         for l, _f, px in sets]})
    return out


def _subject_names(name: str) -> set[str]:
    """Every spelling of ONE subject: the normalised stem ('RSW_Plant_Nysyllin_Wild' -> 'nysyllin_wild' -> 'nysyllinwild')
    and, when the name carries a variant word ('WraidAlpha'), the base species ('wraid'). Matching goes through subject.py
    so a tier prefix, a Plant_ prefix or a variant word never makes a ruled subject look new."""
    out = {S.norm(S.stem(name))}
    v = S.variant_stripped(name)
    if v:
        out.add(S.norm(v))
    out.discard("")
    return out


def ruled_elsewhere(sheet_dir: Path, sheet_id: str, labels: dict | None = None) -> list[dict]:
    """Rows the owner has ALREADY ruled on some OTHER sheet in sheet_dir (owner, 2026-10-05: "a lot of redundant
    creatures from other forms listed on here as well that I've already reviewed").

    A ruling is a row of another *.decisions.json that the sidecar wrote (savedBy + writeCount, or reviewStatus
    ruled), carrying an owner `at` stamp and a decision (a purge-only touch is not a ruling). Each entry:
    {names, sheet, sheet_id, row, decision, label, note, at}. The pick's label comes from that sheet's snapshot."""
    out = []
    for f in sorted(sheet_dir.glob("*.decisions.json")):
        if f.name == sheet_id + ".decisions.json":
            continue
        try:
            doc = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        rs = doc.get("reviewStatus") if isinstance(doc.get("reviewStatus"), dict) else {}
        if not ((doc.get("savedBy") and int(doc.get("writeCount") or 0) > 0) or rs.get("state") == "ruled"):
            continue
        snap = {}
        sp = doc.get("snapshot")
        if sp:
            sp = Path(sp) if Path(sp).is_absolute() else L.REPO_ROOT / sp
            try:
                snap = json.loads(sp.read_text()).get("rows") or {}
            except (OSError, ValueError):
                snap = {}
        nice = (labels or {}).get(doc.get("biome") or "") or f.name.replace(".decisions.json", "")
        for row, v in (doc.get("decisions") or {}).items():
            if not isinstance(v, dict) or not v.get("at") or not (v.get("decision") or "").strip():
                continue
            if not (v.get("decidedAt") or not v.get("purgeTouched")):
                continue
            dec = v["decision"].strip()
            lab = ((snap.get(row) or {}).get("labels") or {}).get(dec, "")
            out.append({"names": _subject_names(row), "sheet": nice, "sheet_id": f.stem.replace(".decisions", ""),
                        "row": row, "decision": dec, "label": lab, "note": (v.get("note") or "").strip(),
                        "at": v.get("at")})
    return out


def ruled_elsewhere_for(row_names: set[str], entries: list[dict]) -> dict | None:
    """The newest other-sheet ruling on any spelling of this subject, or None."""
    hit = [e for e in entries if e["names"] & row_names]
    return max(hit, key=lambda e: e["at"] or "") if hit else None


def generate_biome(biome: str, census_path: Path = CENSUS, out_html: Path | None = None,
                   date: str | None = None, thumb_size: int = 160, sheet_only: bool = False,
                   allow_failing: str | None = None) -> dict:
    _FC_CACHE.clear()          # the gate reads the failed-canon record fresh; a cache from earlier in a long refresh run would disagree with it
    census = json.loads(Path(census_path).read_text())
    b = census["biomes"].get(biome)
    if b is None:
        raise SystemExit(f"biome {biome!r} not in {census_path} (have: {', '.join(census.get('biome_order', []))})")
    date = date or time.strftime("%Y-%m-%d")
    slug = BIOME_SLUG.get(biome) or _stem(biome).lower()
    out_html = Path(out_html) if out_html else BIOME_OUT / f"{slug}_sheet_{date}.html"
    sheet_id = out_html.stem
    imgdir = out_html.parent / "img"
    snap_path = L.ledger_dir() / "sheets" / f"{sheet_id}.snapshot.json"
    prev = json.loads(snap_path.read_text()) if snap_path.is_file() else {}
    prev_rows = prev.get("rows") or {}
    decisions_path = out_html.parent / (out_html.stem + ".decisions.json")
    old = json.loads(decisions_path.read_text()) if decisions_path.is_file() else None
    untouched = old is not None and not old.get("savedBy") and not old.get("writeCount") and \
        (old.get("reviewStatus") or {}).get("state") == "prefill"
    # letters are kept stable only once a human has written to the decisions file; until then every row
    # is lettered A, B, C … afresh, with no gaps left by columns that have since disappeared
    # Memory = the snapshot the owner RULED on (by the decisions file's snapshotId, from git history if a later
    # rebuild overwrote it) first, then any letter a later rebuild added. Letters are append-only per row: a set
    # keeps its letter for good, a vanished set's letter is never reused, and a vanished set a decision still
    # names is carried forward as a "kept" column so the letter keeps resolving to the same pictures.
    ruled = None
    if old is not None and not untouched:
        ruled = L.snapshot_by_id(snap_path, old.get("snapshotId")) or None
        if ruled is None and old.get("snapshotId"):
            print(f"WARNING {decisions_path.name}: its snapshot {old.get('snapshotId')} is not on disk or in git "
                  f"history — letters kept from the latest snapshot only", file=sys.stderr)
    letter_memory = _merge_memory((ruled or {}).get("rows") or {}, prev_rows) if (old is not None and not untouched) else {}
    used_letters = {k: L.decision_letters(v) for k, v in ((old or {}).get("decisions") or {}).items()} \
        if letter_memory else {}
    idx = L.Index()
    slots = L.scan_def_slots()
    order, fp = load_order()
    rows = b["rows"]
    _elsewhere = ruled_elsewhere(out_html.parent, sheet_id, {k: v.get("label", k) for k, v in census["biomes"].items()})
    _own_touched = {k for k, v in ((old or {}).get("decisions") or {}).items() if isinstance(v, dict) and v.get("at")}
    scale_res = None
    if True:                              # owner 2026-10-05: the scaled portrayal is on EVERY biome sheet
        import scale_panel
        _rgb, _src = measure_ground(biome)
        _rgb = SCALE_BIOMES.get(biome) or _rgb
        if _rgb:
            scale_panel.set_terrain(_rgb)
        else:
            scale_panel.set_terrain(scale_panel.DEFAULT_TERRAIN)
        scale_res = scale_panel.Resolver()
        GROUND_LOG[biome] = {"rgb": list(_rgb) if _rgb else None, "source": _src if not SCALE_BIOMES.get(biome) else "hand-measured override"}
        _gp = BIOME_OUT / "scale_ground_measured.json"
        try:
            _g = json.loads(_gp.read_text()) if _gp.is_file() else {}
            if _g.get(biome) != GROUND_LOG[biome]:
                _g[biome] = GROUND_LOG[biome]
                _gp.write_text(json.dumps(_g, indent=1, sort_keys=True))
        except (OSError, ValueError):
            pass
    # the in-game label + description on every row (owner, Vapaad note 2026-10-04: "Your sheets need to include
    # the animal descriptions as well for reference") — from the live dump, post-patch
    try:
        import scale_panel
        desc_res = scale_res or scale_panel.Resolver()
    except Exception as e:                                  # noqa: BLE001
        print(f"WARNING: no def dump for descriptions ({e}) — rows say UNMEASURED", file=sys.stderr)
        desc_res = None
    rel, elsewhere, find = _clusters(rows)
    # per-row overrides (sheet_row_overrides.json): the NEW in-game name of a donor row being ported, and extra
    # artpipe job families (new renders filed under another name, legacy crags_* sets) to show on that row
    _ov = (json.loads(OVERRIDES.read_text()) if OVERRIDES.is_file() else {}).get(biome, {})
    for r in rows:
        o = _ov.get(r["key"])
        if o:
            r["artpipe_state_jobs"] = sorted(set(r.get("artpipe_state_jobs") or []) | set(o.get("jobs") or []))
    labels = {r["key"]: (f"{_ov[r['key']]['new_label']} (new name; was {r['key']})" if r["key"] in _ov and _ov[r["key"]].get("new_label") else _human(r)) for r in rows}

    census_canon = {cr["key"]: (cr.get("canon") or {}).get("entry") for bb in census["biomes"].values()
                    for cr in bb["rows"] if (cr.get("canon") or {}).get("entry")}
    _ph_shared = PD.shared_map(census)
    built, purged_hidden, hidden_kept = [], {}, {}
    donor_purged = set()
    # only bytes an artpipe render MADE are ours: donor art copied into one of our mods is still the donor's original
    ours_shas = {s_ for s_, vv in idx.variants.items() if any(v.get("kind") == "artpipe" for v in vv)}
    for r in rows:
        graphics, seen = [], set()
        for res in (r.get("art") or {}).get("resources") or []:
            if res.get("role") == "flying" and FLIP_RES_RE.match(res["res"] + "1"):
                continue          # a flip-book prefix: its frames join one set below, never per-frame columns
            br = build_row(idx, res["res"], order, slots)
            if br.get("donorPurged"):
                donor_purged.add(r["key"])
            cols = [c for c in br["cols"] if _fkey(c) not in seen]
            seen.update(_fkey(c) for c in cols)
            p = res.get("prior_selection")
            graphics.append({"res": res["res"], "role": ROLE_TEXT.get(res.get("role"), res.get("role") or "graphic"),
                             "cols": cols, "prior_raw": p, "joined_by": res.get("joined_by")})
        have = {s for g in graphics for c in g["cols"] for s in c["faces"].values()}
        words = {_stem(x) for x in [r["key"], r.get("port")] + list(r.get("defNames") or []) if x}
        words |= {(r.get("label") or "").replace(" ", "")}
        prefixes = [res["res"] for res in (r.get("art") or {}).get("resources") or []
                    if res.get("role") == "flying" and FLIP_RES_RE.match(res["res"] + "1")]
        flips = [c for c in flipbook_cols(idx, words, r.get("artpipe_state_jobs") or [], prefixes)
                 if not (set(c["faces"].values()) & have)]
        flip_shas = {s for c in flips for s in c["faces"].values()}
        named = [c for c in name_render_cols(idx, words, r.get("artpipe_state_jobs") or [])
                 if _fkey(c) not in seen and not (set(c["faces"].values()) & (have | flip_shas))]
        if flips:
            graphics.append({"res": "_flip:" + (prefixes[0] if prefixes else r["key"]), "role": FLIP_ROLE,
                             "cols": flips, "prior_raw": None, "flip": True})
        if named:
            graphics.append({"res": None, "role": ROLE_TEXT[None], "cols": named, "prior_raw": None})
        # req 14: a picture the ledger has PURGED (his reject+purge, on any sheet) is never shown as a column
        n_hidden = 0
        for g in graphics:
            kept_cols = []
            for c in g["cols"]:
                live = {f: sh for f, sh in c["faces"].items() if not idx.is_purged(sh)}
                if c.get("winner") and len(live) < len(c["faces"]):
                    # purged but STILL what the game shows today: keep it as the IN GAME column, flagged, never pickable
                    c["purgedLive"] = True
                    kept_cols.append(c)
                    continue
                n_hidden += len(c["faces"]) - len(live)
                if c["kind"] == "donor" and not c.get("ours") and not live:
                    donor_purged.add(r["key"])   # a donor ORIGINAL the owner purged: shown and rejected (gate req 4)
                if live:
                    c["faces"] = live
                    kept_cols.append(c)
            g["cols"] = kept_cols
        purged_hidden[r["key"]] = n_hidden
        graphics = [g for g in graphics if g["cols"]] or graphics[:0]
        # primary = first body graphic with pictures, else first graphic; name renders are offered to it too
        prim = next((g for g in graphics if g["res"] and g["role"] == "body"), graphics[0] if graphics else None)
        if prim is not None and graphics.index(prim) != 0:
            graphics.remove(prim)
            graphics.insert(0, prim)
        allcols = [c for g in graphics for c in g["cols"]]
        mem = letter_memory.get(r["key"]) or {}
        _assign_letters(allcols, mem.get("columns"), mem.get("reserved"))
        kept = _kept_cols(allcols, mem, used_letters.get(r["key"]) or set())
        _k = [c for c in kept if not any(idx.is_purged(sh) for sh in c["faces"].values())]
        for c in kept:      # a set he picked that has since been purged is hidden from the page but its letter stays in the snapshot
            if c not in _k:
                hidden_kept.setdefault(r["key"], []).append((c, (mem.get("graphic_of") or {}).get(c["letter"])))
        purged_hidden[r["key"]] += len(kept) - len(_k)
        kept = _k
        for c in kept:
            gk = (mem.get("graphic_of") or {}).get(c["letter"])
            g = next((g for g in graphics if (g["res"] or "_byname") == gk), None)
            if g is None:
                g = graphics[0] if graphics else None
            if g is None:
                g = {"res": gk if gk and gk != "_byname" else None, "role": "body", "cols": [], "prior_raw": None}
                graphics.append(g)
            g["cols"].append(c)
            allcols.append(c)
        for c in allcols:
            # a "donor" column whose bytes an artpipe render made is our art under a donor-ported texPath
            # (TheRot's RotSporeKit/... carries rot_*_v2 renders): it must not read as donor-only (gate req 3)
            if c["kind"] == "donor" and set(c["faces"].values()) & ours_shas:
                jobs = sorted({v.get("job", "") for s_ in c["faces"].values() for v in idx.variants.get(s_, [])
                               if v.get("kind") == "artpipe" and v.get("job")})
                c["oursRender"] = True
                c["label"] = "our deployed art" + (" (render %s)" % FAM_RE.sub("", jobs[0]) if jobs else "") + " — " + \
                    c.get("label", "").split("— ", 1)[-1]
            c["purgeable"] = c["kind"] not in ("live", "kept") and not (c["kind"] == "donor" and c.get("winner"))   # the game's own art
            if c.get("purgedLive"):
                c["purgeable"] = False
        try:   # placeholder_detect: a row drawn by script-flat shapes or borrowed vanilla textures has no art of ours
            _pv = PD.classify_row(r, _ph_shared)
        except Exception as e:                              # noqa: BLE001
            _pv = {"verdict": "UNMEASURED", "reasons": [f"{type(e).__name__}: {e}"]}
        if _pv["verdict"] == "PLACEHOLDER":
            for c in allcols:
                if c["kind"] == "live":
                    c["placeholder"] = "; ".join(_pv["reasons"])[:400]
        for g in graphics:
            letters = {id(c) for c in allcols}
            for c in g["cols"]:
                if c.get("near_of") is not None and id(c["near_of"]) not in letters:
                    c.pop("near_of")
        built.append((r, graphics))

    maxl = max([LETTERS.index(c["letter"]) + 1 for _, gs in built for g in gs for c in g["cols"]] + [1])
    items, snap_rows, prefills = [], {}, {}
    cluster_ids, n_sit1 = {}, 0
    for r, graphics in built:
        key = r["key"]
        keys = {L.subject_key(x) for x in [key] + list(r.get("defNames") or []) + [_stem(key)] if x}
        rul = idx.subject_rulings(keys)
        gitems, picks, prim_pf = [], {}, ("", "", "none")
        thumbs, missing = {}, 0
        for gi, g in enumerate(graphics):
            g["prior"] = g.pop("prior_raw", None)
            pf = _graphic_prefill(g, rul)
            gkey = g["res"] or "_byname"
            if gi == 0:
                prim_pf = pf
            elif g["res"] is not None and pf[0]:
                picks[gkey] = pf[0]
            facings = [f for f in FACINGS if any(f in c["faces"] for c in g["cols"])]
            flip = {}
            if g.get("flip"):
                facings, nfr, ffac = flip_layout(g["cols"])
                flip = {"flip": True, "nframes": nfr, "flipFacings": ffac}
            for c in g["cols"]:
                for f, s in list(c["faces"].items()):
                    if s in thumbs:
                        continue
                    if not L.store_has(s):
                        missing += 1
                        continue
                    thumbs[s] = thumb(s, imgdir, size=thumb_size)
            pr = g["prior"]
            prior = None
            if pr:
                was = f"{SIT1} recorded: {pr.get('decision')} — {pr.get('picked_label') or ''}".strip(" —")
                pf_shas = set((pr.get("picked_faces") or {}).values())
                hit = next((c for c in g["cols"] if pf_shas and pf_shas & set(c["faces"].values())), None)
                dec = (pr.get("decision") or "").strip()
                if hit:
                    text = f"your {SIT1} pick is set {hit['letter']} here ({_short(hit)})"
                elif dec in ("redo", "hold"):
                    text = f"your {SIT1} ruling: {dec}"
                else:
                    text = f"your {SIT1} pick is not among these pictures any more"
                prior = {"text": text, "note": pr.get("note", ""), "was": was}
            gitems.append({
                "key": gkey, "res": g["res"], "role": g["role"], "primary": gi == 0, "facings": facings,
                "prior": prior, **flip,
                "cols": [{k: (v if k != "near_of" else v["letter"]) for k, v in c.items()
                          if k in ("letter", "kind", "label", "detail", "faces", "winner", "also", "prompt", "purgeable", "near_of", "placeholder", "purgedLive")}
                         | {"short": _short(c)} for c in g["cols"]]})
        letter, why, source = prim_pf
        no_art = not graphics
        if no_art:
            letter, why, source = "hold", "no art yet — held until a picture exists", "none"
        if source == "sit1":
            n_sit1 += 1
        ce = canon_entry(Path(r["canon"]["entry"]).name) if (r.get("canon") or {}).get("entry") else {}
        base = (r["canon"].get("base") or "") if ce else ""
        if not ce:
            ce, base = canon_base(key, r.get("label") or "", census_canon)
        canon = None
        if ce:
            seen_c = {}
            for p in ce["images"]:
                seen_c.setdefault(L.sha256_file(p), p.read_bytes())
            canon = {"dir": ce["dir"], "brief": ce["brief"][:2500], "must": ce["must"][:1500],
                     "ruling": ce["ruling"][:800] if "(empty" not in ce["ruling"] else "", "base": base,
                     "imgs": [thumb(sh, imgdir, bb, 260) for sh, bb in seen_c.items()]}
        root = find(key)
        clustered = bool(rel.get(key))
        if clustered and root not in cluster_ids:
            cluster_ids[root] = len(cluster_ids)
        tier, tier_text = _tier(r)
        if base:
            tier, tier_text = "canon", f"canon Star Wars creature (entry for the base species: {base})"
        canon_tag = (canon_state(key) or "no canon-library entry for this subject — judge on its own") if not canon else ""
        flags = []
        # a row the owner decided whose pictures changed since the snapshot he ruled on (a redo landed, a pick was
        # installed under new bytes, or the row was renamed and its decision carried over under `carriedFrom`)
        _od = ((old or {}).get("decisions") or {}).get(key) or {}
        if _od.get("decidedAt") and ruled:
            _rr = ((ruled.get("rows") or {}).get(_od.get("carriedFrom") or key) or {}).get("columns") or {}
            _seen = {json.dumps(v, sort_keys=True) for v in _rr.values()}
            _new = [c["letter"] for g in gitems for c in g["cols"] if json.dumps(c["faces"], sort_keys=True) not in _seen]
            if _new:
                flags.append(f"NEW ART since your {_od['decidedAt'][:10]} ruling: column(s) {', '.join(sorted(set(_new)))}")
        if _od.get("carriedFrom"):
            flags.append(f"your ruling carried over from {_od['carriedFrom']} (renamed row)")
        if no_art:
            flags.append("NO ART YET")
        if missing:
            flags.append(f"{missing} picture(s) not archived — not shown")
        n_sets = sum(len(g["cols"]) for g in gitems)
        plc = r.get("placements") or []
        # donor-sourced row with no donor original on disk and none recorded as purged: say so explicitly, naming the
        # donor mod and texPath (SHEET_DONOR_COLUMN_FALSE_PASS_1) — the gate counts this note as the donor column shown
        donor_absent = ""
        if (r.get("donors") or tier == "donor") and key not in donor_purged and not any(
                c.get("kind") == "donor" and not c.get("ours") and not SG._is_ours_label(c.get("label"))
                for g in gitems for c in g["cols"]):
            donor_absent = ("donor original not on disk (mod absent): " + (", ".join(r.get("donors") or ["donor tier"]))[:120]
                            + " · texPath " + (", ".join(x["res"] for x in (r.get("art") or {}).get("resources") or [])[:200] or "unknown"))
        item = {
            "donorAbsent": donor_absent,
            "id": key, "kind": r["kind"], "label": labels[key].capitalize(),
            "_root": root, "_clustered": clustered,
            "effect": (f"{r['kind']} · {_layer(r)} · commonality {r.get('commonality_max')} · "
                       + (f"{n_sets} picture set(s)" + (f" across {len(gitems)} graphics" if len(gitems) > 1 else "")
                          if gitems else "no pictures")),
            "tier": tier, "tierText": tier_text, "canonTag": canon_tag, "flags": flags,
            "prefillShort": _prefill_short(source, why),
            "prefill": letter, "prefillWhy": why, "prefillSource": source,
            "contested": source in ("inferred", "none"), "inferred": source == "inferred",
            "prefillPicks": picks, "graphics": gitems, "thumbs": thumbs, "canon": canon,
            "letters": [c["letter"] for g in gitems if g["primary"] or g["res"] is None for c in g["cols"] if not c.get("purgedLive")],
            "related": [{"id": o, "label": labels[o], "why": w} for o, w in sorted(rel.get(key, {}).items())],
            "elsewhere": elsewhere.get(key, []),
            "noArt": no_art, "purgedHidden": purged_hidden.get(key, 0), "donorPurged": key in donor_purged,
            "noArtWhy": ((r.get("art") or {}).get("searched") or "searched by graphic and by name: " + ", ".join(sorted(w for w in {_stem(key)} | set(r.get("defNames") or []) if w))
                         + ("; artpipe jobs on record: " + ", ".join(r.get("artpipe_state_jobs") or []) if r.get("artpipe_state_jobs") else "")),
            "rulings": [{"at": (x.get("at") or "")[:10], "verdict": x.get("raw_verdict") or x.get("verdict"),
                         "trust": x.get("trust"), "sheet": Path(x.get("source_file") or "").name.replace(".decisions.json", ""),
                         "note": (x.get("note") or x.get("blanket_said") or "")[:240]}
                        for x in sorted(rul, key=lambda x: x.get("at") or "") if x.get("trust") not in ("prefill",)],
        }
        item["desc"] = desc_res.describe(r) if desc_res is not None else {}
        # a subject the owner already ruled on another sheet renders collapsed at the bottom (never deleted), unless he
        # has himself touched this row on THIS sheet
        _re = None if key in _own_touched else ruled_elsewhere_for(
            set().union(*[_subject_names(x) for x in [key] + list(r.get("defNames") or []) if x]), _elsewhere)
        if _re:
            item["ruledElsewhere"] = {"sheet": _re["sheet"], "sheetId": _re["sheet_id"], "pick": _re["decision"],
                                      "label": _re["label"], "note": _re["note"][:300], "at": (_re["at"] or "")[:10]}
        if scale_res is not None:
            item["scale"] = _scale_for(scale_res, r, gitems, letter, (old or {}).get("decisions", {}).get(key), imgdir)
            if item["scale"].get("status") == "fallback":     # req 2: a FALLBACK size is allowed but must be flagged
                item["flags"].append(f"{SG.SIZE_FALLBACK_FLAG} — {item['scale'].get('source')}")
        items.append(item)
        prefills[key] = (letter, picks)
        snap_rows[key] = {"subject_key": _stem(key).lower(), "res": (gitems[0]["res"] if gitems else None),
                          "columns": {c["letter"]: c["faces"] for g in gitems for c in g["cols"]},
                          "labels": {c["letter"]: c["label"] for g in gitems for c in g["cols"]},
                          "graphic_of": {c["letter"]: g["key"] for g in gitems for c in g["cols"]},
                          "reserved": sorted(set((letter_memory.get(key) or {}).get("reserved") or [])
                                             | {c["letter"] for g in gitems for c in g["cols"]}, key=LETTERS.index)}

    for key, cs in hidden_kept.items():
        sr = snap_rows.get(key)
        if sr is None:
            continue
        for c, gk in cs:
            sr["columns"].setdefault(c["letter"], c["faces"])
            sr["labels"].setdefault(c["letter"], c.get("label", ""))
            sr["graphic_of"].setdefault(c["letter"], gk or "_byname")
            sr["reserved"] = sorted(set(sr["reserved"]) | {c["letter"]}, key=LETTERS.index)
    # a row the owner ruled on that has left this biome's census keeps its snapshot entry (not shown on the page),
    # so his decision letters still resolve to the pictures he ruled on
    touched_rows = {k for k, v in ((old or {}).get("decisions") or {}).items() if isinstance(v, dict) and v.get("at")}
    for key, ls in used_letters.items():
        mem = letter_memory.get(key)
        if key in snap_rows or not mem or not ((ls & set(mem.get("columns") or {})) or key in touched_rows):
            continue
        snap_rows[key] = {"subject_key": mem.get("subject_key") or _stem(key).lower(), "res": mem.get("res"),
                          "columns": mem["columns"], "labels": mem.get("labels") or {},
                          "graphic_of": mem.get("graphic_of") or {}, "reserved": mem.get("reserved") or [],
                          "rowGone": "not in this biome's census any more — kept so the owner's ruled letters resolve"}

    # order + groups: per kind, unlinked rows first, then each linked cluster as its own band
    kinds = ["fauna", "flora", "fish"]
    kinds += sorted({it["kind"] for it in items} - set(kinds))
    ordered = []
    for k in kinds:
        ks = sorted([it for it in items if it["kind"] == k], key=lambda it: it["label"].lower())
        for it in ks:
            if not it["_clustered"]:
                it["group"] = k.capitalize()
                ordered.append(it)
        roots = []
        for it in ks:
            if it["_clustered"] and it["_root"] not in roots:
                roots.append(it["_root"])
        for root in roots:
            mem = [it for it in items if it["_clustered"] and it["_root"] == root]
            mem.sort(key=lambda it: ({"canon": 0, "sw": 1, "ours": 2, "donor": 3}[it["tier"]], it["id"]))
            band = PAIR_COLOURS[cluster_ids[root] % len(PAIR_COLOURS)]
            gname = "Related: " + " ↔ ".join(f"{it['label']} ({it['id']})" for it in mem)
            for it in mem:
                if it in ordered:
                    continue
                it["group"], it["band"] = gname, band
                ordered.append(it)
    for it in ordered:
        it.pop("_root", None)
        it.pop("_clustered", None)
    # already-ruled subjects sink to the bottom under one group, in their old order
    ordered = [it for it in ordered if not it.get("ruledElsewhere")] + \
        [dict(it, group="Already ruled on another sheet", band=None) for it in ordered if it.get("ruledElsewhere")]
    n_collapsed = sum(1 for it in ordered if it.get("ruledElsewhere"))

    snap = {"sheetId": sheet_id, "built": L.now(), "loadOrder": fp, "census": _rel(Path(census_path)),
            "census_git_head": census.get("git_head"), "biome": biome, "rows": snap_rows}
    new_id = hashlib.sha1(json.dumps(snap_rows, sort_keys=True).encode()).hexdigest()[:16]
    superset = bool(prev_rows) and all(
        snap_rows.get(rk, {}).get("columns", {}).get(l) == f
        for rk, pr in prev_rows.items() for l, f in (pr.get("columns") or {}).items())
    snap["snapshotId"] = prev.get("snapshotId") if superset and prev.get("snapshotId") else new_id

    opts = pick_options(maxl)
    n_canon = sum(1 for it in ordered if it["canon"])
    n_link = sum(1 for it in ordered if it["related"])
    n_noart = [it["id"] for it in ordered if it["noArt"]]
    cfg = {
        "sheetId": sheet_id, "title": f"{b.get('label', biome)} — flora & fauna art",
        "subtitle": (f"{len(ordered)} rows · {n_canon} canon · {n_link} linked · {n_sit1} prefilled from {SIT1} · "
                     f"{len(n_noart)} NO ART YET" + (f" · {n_collapsed} already ruled on another sheet (collapsed at the bottom)" if n_collapsed else "") + (f" · IN GAME judged on {fp.split(':')[0]}" if "FULL.LATEST" in fp else "")),
        "briefHtml": BIOME_BRIEF.format(label=b.get("label", biome), n=len(ordered)),
        "criterion": ("Rows: fauna, flora, fish, alphabetical; related rows banded together. Columns: what the game shows "
                      "now first, then shadowed copies, renders newest first, history oldest first, donor last. "
                      "The order ranks RECENCY and RUNTIME, never quality or worth."),
        "invented": [
            "Renders are joined to a row by its NAME (defName stem, label, artpipe job names) when nothing binds them to a "
            "texture path; such columns say 'found by NAME' and could belong to a namesake.",
            "Related links come from the census's twin detection (same stem, shared texture, or a 'copied from' comment) — "
            "a name match, not a ruling that the two are the same creature.",
            "Where you have no pick and no keep, the prefill trusts a commit message citing your approval (⚠), else what the "
            "game shows now; a row with only name-found renders is prefilled to the newest render (⚠).",
        ],
        "posture": {"mode": "pick-one", "explain": "Each row: pick the ONE set the game should show (and one per extra "
                    "graphic). The winner goes into the owning mod and the loser is archived — nothing installs until you see "
                    "that plan. ✕ on a picture = reject + PURGE."},
        "options": opts, "groupLabel": "group", "media": True,
        "decisionsFile": decisions_path.name, "decisionsPath": str(decisions_path), "sheetPath": str(out_html),
    }
    render = '<script id="RENDER">' + BIOME_BODY.replace("%LETTERS%", LETTERS).replace("%NEAR%", str(NEAR)) + COMMON_JS + "</script>" + STYLE + BIOME_STYLE
    out_html.parent.mkdir(parents=True, exist_ok=True)
    # THE GATE (scaled-game-image-review): build to <sheet>.gate.tmp, check every requirement, and only then move the
    # HTML (stamped) into place. A failure raises GateFailed with the previous sheet, snapshot and decisions untouched.
    prefill_doc = json.dumps({
        "sheetId": sheet_id, "posture": "pick-one", "snapshot": _rel(snap_path), "snapshotId": snap["snapshotId"],
        "criterion": cfg["criterion"], "biome": biome,
        "reviewStatus": {"state": "prefill", "by": None, "at": None,
                         "evidence": "generated by art_sheet.py --biome; rows marked sit1 carry the owner's desert sitting 1 picks, no human has ruled on this sheet"},
        "decisions": {k: ({"decision": l, "note": "", "prefill": l} | ({"picks": p} if p else {}))
                      for k, (l, p) in prefills.items()},
    }, indent=1)
    will_write = not sheet_only and (old is None or untouched)
    # a FIRST build has no decisions file yet, and check_sheet (req 9) wants one: the gate reads the prefill it is
    # about to write, staged beside it, so a new biome sheet can pass on its first build (FLYER_FLIPBOOK_ART_1 note)
    gate_dec = decisions_path
    if will_write:
        gate_dec = decisions_path.with_name(decisions_path.stem + ".gate.tmp.json")
        gate_dec.write_text(prefill_doc)
    gate_ctx = {"sheet_id": sheet_id, "sheet_dir": out_html.parent, "snap": snap, "snap_path": snap_path,
                "decisions": old, "decisions_path": gate_dec, "biome": biome, "census_rows": rows,
                "ground": GROUND_LOG.get(biome)}
    try:
        gate_checks = SG.enforce(_fill_template(cfg, ordered, render, cfg["title"]), gate_ctx, out_html, allow_failing)
    finally:
        if gate_dec != decisions_path:
            gate_dec.unlink(missing_ok=True)
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    snap_path.write_text(json.dumps(snap, indent=1, sort_keys=True))
    SG.commit(out_html.with_name(out_html.stem + ".gate.tmp.html"), out_html)

    # decisions: written when absent, or regenerated while it is still the untouched prefill
    wrote = False
    if sheet_only:
        if old is not None and old.get("snapshotId") != snap["snapshotId"]:
            print(f"WARNING --sheet-only: columns changed (snapshot {old.get('snapshotId')} -> {snap['snapshotId']}) and "
                  f"{decisions_path.name} was NOT rewritten — its letters may now point at different sets", file=sys.stderr)
    elif will_write:
        decisions_path.write_text(prefill_doc)
        wrote = True
    elif old.get("snapshotId") != snap["snapshotId"]:
        # letters are stable, so only a letter his decisions USE naming different pictures is a problem
        base = ruled or prev
        bad = L.letter_mismatches(old, base, snap) if base else [("?", "?")]
        if bad:
            print(f"WARNING {decisions_path.name}: the owner has touched it and these decision letters now name "
                  f"different pictures than in snapshot {old.get('snapshotId')}: "
                  + ", ".join(f"{r}:{l}" for r, l in bad[:20]) + " — ingest will refuse until reconciled", file=sys.stderr)
    return {"biome": biome, "html": _rel(out_html), "decisions": _rel(decisions_path), "wrote_decisions": wrote,
            "gate": ("PASS " if all(c.ok for c in gate_checks) else "OVERRIDE (unstamped, bannered) ") + SG.GATE_VERSION, "snapshot": _rel(snap_path), "snapshotId": snap["snapshotId"], "census_rows": len(rows), "rows": len(ordered),
            "ruled_rows_gone_kept_in_snapshot": sorted(k for k, v in snap_rows.items() if v.get("rowGone")),
            "collapsed_ruled_elsewhere": n_collapsed, "canon_rows": n_canon, "canon_rows_with_images": sum(1 for it in ordered if it["canon"] and it["canon"]["imgs"]),
            "canon_rows_with_must_show": sum(1 for it in ordered if it["canon"] and it["canon"]["must"]),
            "linked_rows": n_link, "prefilled_sit1": n_sit1, "no_art": n_noart,
            "sets": sum(len(g["cols"]) for it in ordered for g in it["graphics"]),
            "images": len(list(imgdir.glob("*.webp")))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doubles", action="store_true", help="every texPath shipped by >1 of our mods with different bytes")
    ap.add_argument("--biome", action="append", default=[],
                    help="build the per-biome sheet for this census biome key (repeatable); 'first3' = the first three in census order")
    ap.add_argument("--census", default=str(CENSUS))
    ap.add_argument("--refresh", action="store_true",
                    help="with --biome: first pull finished artpipe renders into the ledger (art.py backfill artpipe) "
                         "and re-run biome_census.py, so new renders show on the sheets")
    ap.add_argument("--date", help="date stamp in the biome sheet's file name (default today)")
    ap.add_argument("--sheet-only", action="store_true",
                    help="with --biome: rewrite the HTML only, never the decisions file — use while a sheet is being "
                         "reviewed live (an untouched-prefill decisions file is otherwise regenerated)")
    ap.add_argument("--allow-failing", metavar="REASON",
                    help="with --biome: if the gate fails, still write the sheet UNSTAMPED with a red banner naming what fails — "
                         "only for replacing a sheet that is itself unusable (blank). Never for a sheet that merely fails a requirement.")
    ap.add_argument("--res", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--title", default="Art: all versions compared")
    ap.add_argument("--sheet-id")
    a = ap.parse_args(argv)
    if a.biome:
        if a.refresh:
            import subprocess
            here = Path(__file__).resolve().parent
            for cmd in ([sys.executable, str(here / "art.py"), "backfill", "artpipe"],
                        # the game's own copies of every row's texPath (donor/vanilla art), bound by texPath
                        [sys.executable, str(here / "gametex.py"), "ingest", "--census", str(a.census)],
                        [sys.executable, str(here / "biome_census.py"), "--out", str(Path(a.census).parent)]):
                print("refresh:", " ".join(cmd[1:]), flush=True)
                if subprocess.run(cmd, cwd=str(L.REPO_ROOT)).returncode:
                    raise SystemExit(f"refresh step failed: {cmd[1:]}")
        keys = []
        for k in a.biome:
            keys += json.loads(Path(a.census).read_text())["biome_order"][:3] if k == "first3" else [k]
        rc = 0
        for k in keys:
            try:
                r = generate_biome(k, Path(a.census), Path(a.out) if a.out and len(keys) == 1 else None, a.date,
                                   sheet_only=a.sheet_only, allow_failing=a.allow_failing)
            except SG.GateFailed as e:
                print(f"GATE FAILED for {k}: sheet NOT written; the previous sheet (if any) is untouched\n"
                      + SG.report(e.sheet, e.checks), file=sys.stderr)
                rc = 3
                continue
            print(json.dumps(r, indent=1))
        return rc
    if not a.out:
        ap.error("--out is required without --biome")
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
