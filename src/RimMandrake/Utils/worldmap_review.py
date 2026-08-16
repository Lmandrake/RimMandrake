#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""worldmap_review.py - the keep/cut sheet for WORLD-MAP content.

TileMutatorDefs and LandmarkDefs are what a tile *is* when you look at it on the
planet: the mountain, the caves, the oasis, the toxic vents. 449 of them arrive
from the mod stack and most have no business on a Star Wars desert world, so the
owner needs one surface on which to say keep / cut / where it goes.

    python3 src/RimMandrake/Utils/worldmap_review.py
    ->  design/Jawa/worldbuilding/review/worldmap_elements.html

Same shape as the other review sheets under design/Jawa/worldbuilding/review/,
but STATIC - no server. Decisions live in the browser's localStorage and come
back out through the export button, because the sheet has to survive being
opened from Explorer with nothing running behind it.

🔴 THE POSTURE IS WHITELIST - owner, 2026-08-15. Default is EXCLUDE: nothing is
on our planet unless it has been explicitly whitelisted, so "undecided" means
STRIPPED, not "decide later". A half-finished sheet is therefore a valid, if
brutal, answer - which is exactly why the export carries `"posture":"whitelist"`
and a full `whitelisted` list rather than a sparse diff. A consuming tool that
read a sparse file as "strip only these few" would invert the ruling.
The reason it is a whitelist and not a blacklist: when a mod updates and adds
content, a whitelist stays correct and a blacklist silently lets the new content
onto the planet.

🔑 The column that decides most rows is OCCURS. It is a real count out of a real
savegame, not a commonality guess: a mutator that appears 0 times in the frozen
world we ship is not a decision anybody needs to make.

How the counts are read - the two traps, both already paid for:

  🔴 tileMutatorDefsDeflate and tileMutatorTilesDeflate exist inside EVERY
     PlanetLayer. The OrbitLayers use the identical element names, so a naive
     find() lands on an orbit stub. Read inside <li Class="SurfaceLayer"> only.
     (Same rule as worldmap.py, same reason.)
  🔴 The shortHash table must come from a def dump of the SAME mod set as the
     save. A hash decoded against a different set resolves to a DIFFERENT
     mutator rather than failing, so a wrong table gives a plausible lie.
     `unresolved` is printed on every run; non-zero means stop.

🟢 THE SHEET SHIPS PRE-FILLED - 2026-08-16. Deciding 449 rows from a blank page
is a different job from disagreeing with 449 already-made calls, and the second
is the one worth the owner's time. `worldmap_elements.prefill.json` holds a
state and a "where it belongs" note for every def; it is baked into the page and
MERGED into localStorage per def - untouched rows take the prefill, his own edits are
never clobbered. "reset to pre-filled" is the deliberate way back. Export a
reviewed sheet over that JSON and the next regeneration ships HIS calls instead.

The two arrays are parallel: defs[i] is a 2-byte shortHash, tiles[i] is a 4-byte
tile id, so one mutator on one tile is one entry. Landmarks are not in a blob at
all - they are the plain <landmarks> keys/values dict, read as text.
"""
from __future__ import annotations

import argparse
import base64
import collections
import json
import os
import re
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import worldmap_effects as wme        # noqa: E402  the EFFECT sentences

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "design" / "Jawa" / "worldbuilding" / "review"
OUT_HTML = OUT_DIR / "worldmap_elements.html"

# 🔑 The sheet ships PRE-FILLED. Every def already carries a keep/cut call and a
# "where it belongs" note, so the owner REVIEWS rather than deciding 449 rows
# from scratch. The prefill is baked into the page as the default state and is
# only applied when localStorage is EMPTY - his own choices are never clobbered.
# Regenerate the prefill with src/RimMandrake/Utils/worldmap_prefill.py.
PREFILL_JSON = OUT_DIR / "worldmap_elements.prefill.json"

LOWLOW = Path("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios")
DEFDUMP = LOWLOW / "DefDump" / "defs"
SAVES = LOWLOW / "Saves"

DEF_TYPES = ("TileMutatorDef", "LandmarkDef")


# --------------------------------------------------------------------------
# defs
# --------------------------------------------------------------------------
def load_defs(def_type: str, dump_dir: Path):
    """Every def of one type, with the fields worth deciding on pulled up flat.

    `fields` is kept on the record because the EFFECT line is composed from it
    (see worldmap_effects.py); render() drops it again before it reaches the page.
    """
    path = dump_dir / (def_type + ".json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    defs = data if isinstance(data, list) else data.get("defs", data)
    out = []
    for d in defs:
        if not isinstance(d, dict) or not d.get("defName"):
            continue
        f = d.get("fields") or {}
        rec = {
            "defName": d["defName"],
            "label": d.get("label") or d["defName"],
            "type": "mutator" if def_type == "TileMutatorDef" else "landmark",
            "mod": d.get("modName") or "?",
            "packageId": d.get("packageId") or "",
            "hash": d.get("shortHash"),
            "desc": (f.get("description") or "").strip(),
            "meta": _meta(def_type, f),
            "fields": f,
        }
        out.append(rec)
    return out


def attach_effects(rows):
    """🔑 The "what this ACTUALLY DOES" line, one sentence per def.

    The owner's complaint, 2026-08-16: *"'headwater' for a river... so what? I can
    see where that is on the map... what does it mean if it has this particular
    mutator?"* A label says what a thing IS; nothing on the sheet said what
    CHANGES when you land on it. This does.

    🔴 A leading "~" means the sentence is inferred from the def NAME, because
    that def has no mechanical fields and a generic worker. Everything without
    one rests on a real field value, an unambiguous workerClass, or the def's own
    stated mechanic. Do not silently strip the marker.
    """
    labels = {r["defName"]: r["label"] for r in rows if r["type"] == "mutator"}
    effects = {}
    for r in rows:
        if r["type"] == "mutator":
            effects[r["defName"]] = wme.mutator_effect(r["defName"], r["fields"])
    for r in rows:
        if r["type"] == "mutator":
            r["effect"] = effects[r["defName"]]
        else:
            r["effect"] = wme.landmark_effect(r["fields"], labels, effects)
    return rows


def _meta(def_type: str, f: dict) -> str:
    """One line of whatever this def type has instead of a description.

    LandmarkDefs carry no description at all - not one of the 113 has one - so
    without this a landmark row is a bare name. category + commonality + the
    mutators it forces is the closest thing to 'what is this'.
    """
    bits = []
    if def_type == "LandmarkDef":
        if f.get("category"):
            bits.append("category %s" % f["category"])
        if f.get("commonality") is not None:
            bits.append("commonality %g" % f["commonality"])
        forced = [m.get("mutator") for m in (f.get("mutatorChances") or [])
                  if m.get("required")]
        if forced:
            bits.append("forces " + ", ".join(str(x) for x in forced))
    else:
        cats = f.get("categories") or []
        if cats:
            bits.append("categories " + ", ".join(str(c) for c in cats))
        c = f.get("chanceOnNonLandmarkTile")
        if c:
            bits.append("free chance %g" % c)
        for k, lab in (("preventsLandmarks", "prevents landmarks"),
                       ("preventsPondGeneration", "prevents ponds")):
            if f.get(k):
                bits.append(lab)
    return " · ".join(bits)


# --------------------------------------------------------------------------
# the save
# --------------------------------------------------------------------------
def newest_save(saves_dir: Path) -> Path:
    cands = sorted(saves_dir.glob("*.rws"), key=lambda p: p.stat().st_mtime)
    if not cands:
        raise SystemExit("no .rws in %s" % saves_dir)
    return cands[-1]


def _inflate(b64_text: str) -> bytes:
    return zlib.decompress(base64.b64decode("".join(b64_text.split())), -15)


def world_usage(save_path: Path):
    """{defName: instances} for mutators and landmarks in one savegame.

    Returns (mutator_counts, landmark_counts, stats). Mutator counts are keyed
    by shortHash at this point and resolved by the caller against the dump, so
    an unresolvable hash is visible rather than silently dropped.
    """
    text = open(save_path, encoding="utf-8", errors="surrogateescape").read()

    lo = text.find('<li Class="SurfaceLayer">')
    if lo < 0:
        raise SystemExit("no SurfaceLayer in %s" % save_path)
    hi = text.find('<li Class=', lo + 10)
    if hi < 0:
        hi = text.find("</layers>", lo)
    surf = text[lo:hi]

    def blob(tag):
        a = surf.find("<%s>" % tag)
        if a < 0:
            return b""
        b = surf.find("</%s>" % tag, a)
        return _inflate(surf[a + len(tag) + 2:b])

    mraw = blob("tileMutatorDefsDeflate")
    traw = blob("tileMutatorTilesDeflate")
    hashes = struct.unpack("<%dH" % (len(mraw) // 2), mraw)
    tiles = struct.unpack("<%dI" % (len(traw) // 4), traw)
    if len(hashes) != len(tiles):
        print("⚠️  mutator arrays disagree: %d defs vs %d tiles"
              % (len(hashes), len(tiles)), file=sys.stderr)

    mut_by_hash = collections.Counter(hashes)
    mut_tiles = collections.defaultdict(set)
    for h, t in zip(hashes, tiles):
        mut_tiles[h].add(t)

    # landmarks: plain XML dict, second <landmarks> is the inner one
    li = text.find("<landmarks>")
    li = text.find("<landmarks>", li + 1)
    lv = text.find("<values>", li), text.find("</values>", li)
    lm = collections.Counter(
        re.findall(r"<li>\s*<def>(.*?)</def>", text[lv[0]:lv[1]], re.S))

    stats = {
        "save": save_path.name,
        "mutatorInstances": len(hashes),
        "mutatorTiles": len(set(tiles)),
        "landmarkInstances": sum(lm.values()),
    }
    return mut_by_hash, {h: len(s) for h, s in mut_tiles.items()}, lm, stats


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------
def build_rows(dump_dir: Path, save_path: Path):
    rows = []
    for t in DEF_TYPES:
        rows.extend(load_defs(t, dump_dir))

    mut_counts, mut_tiles, lm_counts, stats = world_usage(save_path)
    by_hash = {r["hash"]: r for r in rows if r["type"] == "mutator"}
    by_name = {r["defName"]: r for r in rows if r["type"] == "landmark"}

    for r in rows:
        r["n"] = 0
        r["tiles"] = 0
    for h, n in mut_counts.items():
        if h in by_hash:
            by_hash[h]["n"] = n
            by_hash[h]["tiles"] = mut_tiles.get(h, 0)
    for name, n in lm_counts.items():
        if name in by_name:
            by_name[name]["n"] = n
            by_name[name]["tiles"] = n

    unresolved = sorted(h for h in mut_counts if h not in by_hash)
    missing_lm = sorted(k for k in lm_counts if k not in by_name)
    stats["unresolvedMutatorHashes"] = unresolved
    stats["landmarksNotInDump"] = missing_lm

    attach_effects(rows)

    rows.sort(key=lambda r: (r["mod"].lower(), -r["n"], r["label"].lower()))
    return rows, stats


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------
HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>World-map elements &mdash; keep / cut</title>
<style>
:root{
  --bg:#14161a; --panel:#1c1f25; --panel2:#22262e; --line:#2e333c;
  --fg:#d8dce3; --dim:#8b93a1; --dimmer:#666e7c;
  --keep:#3fa96b; --keepbg:#16301f; --rej:#c8503f; --rejbg:#331715;
  --accent:#d9a441; --link:#6fb2e0;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--fg);
  font:13px/1.45 "Segoe UI",Inter,system-ui,-apple-system,sans-serif}
a{color:var(--link)}
code,.mono{font-family:"Cascadia Mono",Consolas,"DejaVu Sans Mono",monospace}

header{position:sticky;top:0;z-index:30;background:var(--panel);
  border-bottom:1px solid var(--line);padding:8px 12px}
h1{margin:0 0 6px;font-size:15px;font-weight:600;letter-spacing:.02em}
h1 .sub{color:var(--dim);font-weight:400;font-size:12px;margin-left:8px}

.bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.bar + .bar{margin-top:6px}
input[type=text],input[type=search],select{
  background:var(--panel2);color:var(--fg);border:1px solid var(--line);
  border-radius:3px;padding:3px 6px;font:inherit}
input[type=search]{min-width:220px}
button{background:var(--panel2);color:var(--fg);border:1px solid var(--line);
  border-radius:3px;padding:3px 9px;font:inherit;cursor:pointer}
button:hover{background:#2b303a;border-color:#454c58}
button.on{background:var(--accent);color:#161616;border-color:var(--accent);font-weight:600}
button.keep{border-color:#2f6b47}
button.keep:hover{background:var(--keepbg)}
button.rej{border-color:#6b2f2a}
button.rej:hover{background:var(--rejbg)}
label.chk{display:inline-flex;gap:4px;align-items:center;color:var(--dim);
  user-select:none;cursor:pointer}
.sep{width:1px;height:18px;background:var(--line);margin:0 4px}
.spacer{flex:1}
.tally{color:var(--dim);font-size:12px;white-space:nowrap}
.tally b{color:var(--fg);font-weight:600}
.tally .k{color:var(--keep)} .tally .r{color:var(--rej)}

/* ---- the posture banner: the sheet is a WHITELIST ---- */
.posture{display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;
  background:#2a1d10;border:1px solid #6b4a1e;border-left:4px solid var(--accent);
  border-radius:3px;padding:5px 9px;margin:0 0 6px}
.posture .big{font-weight:700;color:var(--accent);letter-spacing:.02em}
.posture .why{color:#b09a76;font-size:11.5px}
.score{margin-left:auto;font-variant-numeric:tabular-nums;white-space:nowrap;
  font-size:13px}
.score .in{color:var(--keep);font-weight:700}
.score .out{color:var(--rej);font-weight:700}

/* ---- the prefill banner: the sheet arrives already decided ---- */
.prefill{display:flex;flex-wrap:wrap;gap:10px;align-items:center;
  background:#14251c;border:1px solid #2f6b47;border-left:4px solid var(--keep);
  border-radius:3px;padding:5px 9px;margin:0 0 6px}
.prefill .big{font-weight:700;color:var(--keep);letter-spacing:.02em}
.prefill .why{color:#8fb69d;font-size:11.5px}

main{padding:0 12px 60px}

/* ---- mod group ---- */
.mod{margin-top:14px;border:1px solid var(--line);border-radius:4px;
  background:var(--panel);overflow:hidden}
.modhead{display:flex;gap:8px;align-items:center;padding:6px 8px;
  background:var(--panel2);border-bottom:1px solid var(--line);
  position:sticky;top:var(--hh,96px);z-index:20}
.modhead .name{font-size:14px;font-weight:700;letter-spacing:.01em}
.modhead .cnt{color:var(--dim);font-size:12px}
.modhead .cnt b{color:var(--fg)}
.modhead .prog{font-size:11px;color:var(--dimmer)}
.caret{width:16px;text-align:center;color:var(--dim);cursor:pointer;user-select:none}
.mod.collapsed .rows{display:none}

/* ---- rows ---- */
.rows{display:block}
.row{display:grid;
  grid-template-columns:26px 26px 62px 1fr 210px 66px 240px;
  gap:8px;align-items:start;
  padding:4px 8px;border-top:1px solid #23272e}
.row:first-child{border-top:none}
.row:hover{background:#1f232a}
.row.keep{background:var(--keepbg)}
.row.keep:hover{background:#1b3a26}
.row.rej{background:var(--rejbg)}
.row.rej:hover{background:#3d1c19}
.row.hide{display:none}

.btn-s{border:1px solid var(--line);background:#20242b;border-radius:3px;
  width:24px;height:22px;line-height:1;cursor:pointer;color:var(--dim);
  font-size:13px;padding:0}
.btn-s:hover{color:#fff}
.row.keep .b-k{background:var(--keep);border-color:var(--keep);color:#0d1a12;font-weight:700}
.row.rej .b-r{background:var(--rej);border-color:var(--rej);color:#1a0d0c;font-weight:700}

.ty{font-size:10px;text-transform:uppercase;letter-spacing:.06em;
  padding:2px 4px;border-radius:3px;text-align:center;color:var(--dim);
  border:1px solid var(--line);background:#1a1d23}
.ty.landmark{color:#c89be0;border-color:#4a3358}

.main .lbl{font-weight:600}
.main .dn{color:var(--dimmer);font-size:11px;margin-left:6px}
.main .desc{color:var(--dim);font-size:11.5px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  overflow:hidden}
.main .meta{color:var(--dimmer);font-size:11px}

/* ---- the EFFECT line: what this ACTUALLY DOES ----
   Secondary to the label, but brighter than the flavour description, because
   it is the line that decides keep/cut. Never confusable with the owner's own
   NOTE field, which is a bordered input over in its own column. */
.main .eff{color:#c3cbd6;font-size:11.5px;margin:1px 0 1px;
  padding-left:7px;border-left:2px solid var(--accent)}
.main .eff.guess{color:#9aa2ae;border-left-color:#5a4a2a;font-style:italic}
.main .eff .tag{display:inline-block;font-size:9px;font-style:normal;
  letter-spacing:.06em;text-transform:uppercase;color:#161616;
  background:#8a7040;border-radius:2px;padding:0 3px;margin-right:5px;
  vertical-align:1px}

.modcell{color:var(--accent);font-size:11.5px;font-weight:600;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

.n{text-align:right;font-variant-numeric:tabular-nums;font-weight:700}
.n.zero{color:#4d5460;font-weight:400}
.n .t{display:block;font-size:10px;color:var(--dimmer);font-weight:400}

.note{width:100%;background:#191c22;border:1px solid var(--line);
  color:var(--fg);border-radius:3px;padding:3px 5px;font:inherit}
.note:focus{border-color:var(--accent);outline:none}
.note.has{border-color:#4a5a3a;background:#1b2019}

/* ---- export ---- */
#exp{position:fixed;inset:0;background:rgba(8,9,11,.82);z-index:60;
  display:none;padding:32px}
#exp.open{display:flex;align-items:center;justify-content:center}
#expbox{background:var(--panel);border:1px solid var(--line);border-radius:5px;
  width:min(900px,100%);max-height:100%;display:flex;flex-direction:column;
  padding:12px;gap:8px}
#expbox h2{margin:0;font-size:14px}
#expbox textarea{flex:1;min-height:320px;background:#131519;color:var(--fg);
  border:1px solid var(--line);border-radius:3px;padding:8px;
  font-family:"Cascadia Mono",Consolas,monospace;font-size:12px;white-space:pre}
.hint{color:var(--dim);font-size:11.5px}
.ok{color:var(--keep)}
.warn{color:var(--accent)}
</style></head><body>

<header>
  <h1>World-map elements &mdash; what belongs on the Jawa desert planet
    <span class="sub" id="hdr"></span></h1>

  <div class="posture">
    <span class="big">Default is EXCLUDE. Anything not whitelisted will be stripped from the planet.</span>
    <span class="why">A whitelist stays correct when a mod updates and adds content; a blacklist silently lets the new content in.</span>
    <span class="score" id="score"></span>
  </div>

  <div class="prefill" id="prefillbar">
    <span class="big">This sheet arrived PRE-FILLED.</span>
    <span class="why">Every row already has a call and a note saying <i>where it belongs</i> on the
      Jawa desert world &mdash; you are <b>reviewing</b>, not deciding 449 rows from scratch.
      Change anything you disagree with; your edits save over the prefill.</span>
    <span class="spacer" style="flex:1"></span>
    <button id="reprefill">reset to pre-filled</button>
  </div>
  <div class="prefill" id="rulesbar" style="border-color:#5a4a2a;background:#221d14">
    <span class="big" style="color:#d8a657">RULES THE CALLS WERE MADE AGAINST</span>
    <span class="why">Serious, lived-in Outer Rim desert world; Jawa salvage clan fleeing the Empire.
      <b>Slapstick is scoped to the Jawas themselves</b> (scrap, junk, hoarding, sandcrawler life) &mdash;
      whimsy that is not Jawa-flavoured is out. The world has oceans (~17%), has Geonosians as a
      faction, and may be tidally locked, so <b>night-side ice content is KEPT</b>.
      &#9888; <b>One rule was invented and is not yours:</b> this planet&rsquo;s volcanism is treated as
      <b>EXTINCT</b> &mdash; active lava is cut, while basalt, obsidian, black sand and resurgent
      calderas are kept. Flip the lava set if you want a Mustafar region.
      Use the <b>&#9888; flagged for review</b> filter to see only the contested calls.</span>
  </div>

  <div class="bar">
    <input type="search" id="q" placeholder="search label, defName, description, mod…">
    <select id="fmod"><option value="">all mods</option></select>
    <select id="ftype">
      <option value="">both types</option>
      <option value="mutator">mutators only</option>
      <option value="landmark">landmarks only</option>
    </select>
    <select id="fstate">
      <option value="">any state</option>
      <option value="undecided">not looked at (&rarr; stripped)</option>
      <option value="keep">whitelisted (&rarr; kept)</option>
      <option value="rej">deliberate NO (&rarr; stripped)</option>
      <option value="noted">has a note</option>
      <option value="flagged">&#9888; flagged for review</option>
      <option value="guess">effect line is a GUESS (~)</option>
    </select>
    <label class="chk"><input type="checkbox" id="fused"> occurs in world &gt; 0</label>
    <span class="sep"></span>
    <button id="clearf">reset filters</button>
    <span class="spacer"></span>
    <span class="tally" id="tally"></span>
  </div>

  <div class="bar">
    <span class="hint">click a row to <b>whitelist</b> · click again to mark a <b>deliberate NO</b> · third click clears · or use the ✓ ✗ buttons.
      ✗ and blank both get stripped — ✗ only records that you looked.
      <b style="color:var(--accent)">The gold-barred line is what the def ACTUALLY DOES in play</b> — read from its real fields;
      an italic <b>GUESS</b> tag means the def has no mechanical fields and the sentence was inferred from its name.</span>
    <span class="spacer"></span>
    <button id="collapse">collapse all</button>
    <button id="expand">expand all</button>
    <span class="sep"></span>
    <button id="btnexp" class="on">export decisions</button>
  </div>
</header>

<main id="main"></main>

<div id="exp"><div id="expbox">
  <h2>Whitelist export &mdash; <span id="expcount"></span></h2>
  <div class="bar">
    <button id="copy">copy to clipboard</button>
    <button id="dl">download .json</button>
    <span class="sep"></span>
    <button id="imp">import: replace from the box below</button>
    <span class="spacer"></span>
    <button id="expclose">close</button>
  </div>
  <div class="hint" id="expmsg">Everything is also in this box &mdash; select all and copy if the buttons are blocked.</div>
  <textarea id="expta" spellcheck="false"></textarea>
  <div class="hint"><b>Posture: whitelist.</b> <code>whitelisted</code> is the complete list of what may exist on the
    planet; everything else in <code>universe</code> is stripped, whether rejected on purpose or never looked at.
    <code>notes</code> carries the free text. Decisions autosave in this browser under <code>__LSKEY__</code>;
    paste an export back in and hit import to restore them.</div>
</div></div>

<script>
const DATA = __DATA__;
const STATS = __STATS__;
const LSKEY = "__LSKEY__";

/* 🔑 PREFILL is the baked-in default: {defName:{state,note}} for every def,
   already decided against the Jawa desert-world brief.
   🔴 It MERGES, it does not all-or-nothing. An earlier build seeded the prefill only
   when localStorage was completely empty — so a single earlier click suppressed all
   350 pre-filled rows and the sheet looked empty. Now every def the owner has NOT
   touched takes the prefill, and every def he HAS touched is left exactly alone. */
const PREFILL = __PREFILL__;
const clonePrefill = () => JSON.parse(JSON.stringify(PREFILL));

/* ---------- state ---------- */
let S = {};
try { S = JSON.parse(localStorage.getItem(LSKEY) || "{}") || {}; } catch(e) { S = {}; }
const save = () => { try { localStorage.setItem(LSKEY, JSON.stringify(S)); } catch(e){} };
let seeded = false, seededCount = 0, ownCount = 0;
(function mergePrefill(){
  const P = clonePrefill();
  ownCount = Object.keys(S).length;
  for(const d in P){
    const mine = S[d];
    // "touched" means he actually chose something - a bare {} does not count
    if(mine && (mine.state || mine.note)) continue;
    S[d] = P[d]; seededCount++;
  }
  seeded = seededCount > 0;
  if(seeded) save();
})();
const get  = d => S[d] || {state:"", note:""};
function set(d, patch){
  const cur = get(d), next = Object.assign({}, cur, patch);
  if(!next.state && !next.note) delete S[d]; else S[d] = next;
  save();
}

/* ---------- build ---------- */
const byMod = new Map();
DATA.forEach(r => { if(!byMod.has(r.mod)) byMod.set(r.mod, []); byMod.get(r.mod).push(r); });
const mods = [...byMod.keys()].sort((a,b) => byMod.get(b).length - byMod.get(a).length || a.localeCompare(b));

const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const main = document.getElementById("main");

main.innerHTML = mods.map(m => {
  const rs = byMod.get(m);
  const used = rs.filter(r => r.n > 0).length;
  return `<section class="mod" data-mod="${esc(m)}">
    <div class="modhead">
      <span class="caret" data-act="fold">▾</span>
      <span class="name">${esc(m)}</span>
      <span class="cnt"><b>${rs.length}</b> defs · <b>${used}</b> occur in world</span>
      <span class="spacer" style="flex:1"></span>
      <span class="prog" data-prog></span>
      <button class="keep" data-act="bulk" data-v="keep">whitelist all shown</button>
      <button class="rej"  data-act="bulk" data-v="rej">NO to all shown</button>
      <button data-act="bulk" data-v="">clear</button>
    </div>
    <div class="rows">${rs.map(rowHTML).join("")}</div>
  </section>`;
}).join("");

/* 🔴 A leading "~" on an effect means INFERRED FROM THE NAME - the def has no
   mechanical fields and a generic worker, so the sentence is a hypothesis, not
   a reading. It is rendered dimmer, italic and tagged GUESS so it can never be
   mistaken for a field-backed statement. */
function rowHTML(r){
  const st = get(r.defName);
  const body = r.desc ? `<div class="desc" title="${esc(r.desc)}">${esc(r.desc)}</div>` : "";
  const meta = r.meta ? `<div class="meta">${esc(r.meta)}</div>` : "";
  const guess = /^~\s*/.test(r.effect || "");
  const eff = r.effect
    ? `<div class="eff${guess?" guess":""}" title="what this actually does">` +
      (guess ? `<span class="tag">guess</span>` : "") +
      esc((r.effect||"").replace(/^~\s*/,"")) + `</div>`
    : "";
  return `<div class="row ${st.state}" data-d="${esc(r.defName)}" data-n="${r.n}"
      data-mod="${esc(r.mod)}" data-type="${r.type}" data-guess="${guess?1:0}"
      data-s="${esc((r.label+" "+r.defName+" "+r.desc+" "+r.mod+" "+r.meta+" "+(r.effect||"")).toLowerCase())}">
    <button class="btn-s b-k" data-act="keep" title="whitelist — keep on our planet">✓</button>
    <button class="btn-s b-r" data-act="rej"  title="reject — not on our planet">✗</button>
    <span class="ty ${r.type}">${r.type==="mutator"?"mut":"lmk"}</span>
    <div class="main">
      <div><span class="lbl">${esc(r.label)}</span><span class="dn mono">${esc(r.defName)}</span></div>
      ${eff}${body}${meta}
    </div>
    <div class="modcell">${esc(r.mod)}</div>
    <div class="n ${r.n?"":"zero"}">${r.n}${r.tiles && r.tiles!==r.n?`<span class="t">${r.tiles} tiles</span>`:""}</div>
    <input class="note ${st.note?"has":""}" data-act="note" placeholder="notes — where might it go?"
           value="${esc(st.note)}">
  </div>`;
}

/* ---------- interaction ---------- */
const CYCLE = {"":"keep","keep":"rej","rej":""};
function apply(row, state){
  row.classList.remove("keep","rej");
  if(state) row.classList.add(state);
  set(row.dataset.d, {state});
}

main.addEventListener("click", ev => {
  const bulk = ev.target.closest('[data-act="bulk"]');
  if(bulk){
    const sec = bulk.closest(".mod"), v = bulk.dataset.v;
    sec.querySelectorAll(".row:not(.hide)").forEach(r => apply(r, v));
    retally(); return;
  }
  if(ev.target.closest('[data-act="fold"]')){
    ev.target.closest(".mod").classList.toggle("collapsed");
    ev.target.textContent = ev.target.closest(".mod").classList.contains("collapsed") ? "▸" : "▾";
    return;
  }
  const row = ev.target.closest(".row");
  if(!row) return;
  if(ev.target.matches(".note")) return;
  const k = ev.target.closest('[data-act="keep"]'), j = ev.target.closest('[data-act="rej"]');
  const cur = row.classList.contains("keep") ? "keep" : row.classList.contains("rej") ? "rej" : "";
  if(k)       apply(row, cur === "keep" ? "" : "keep");
  else if(j)  apply(row, cur === "rej"  ? "" : "rej");
  else        apply(row, CYCLE[cur]);
  retally();
});

main.addEventListener("input", ev => {
  if(!ev.target.matches(".note")) return;
  const row = ev.target.closest(".row");
  set(row.dataset.d, {note: ev.target.value});
  ev.target.classList.toggle("has", !!ev.target.value);
  retally();
});

/* ---------- filters ---------- */
const q = document.getElementById("q"), fmod = document.getElementById("fmod"),
      ftype = document.getElementById("ftype"), fstate = document.getElementById("fstate"),
      fused = document.getElementById("fused");
fmod.innerHTML = '<option value="">all mods</option>' +
  mods.map(m => `<option value="${esc(m)}">${esc(m)} (${byMod.get(m).length})</option>`).join("");

function filter(){
  const term = q.value.trim().toLowerCase(), m = fmod.value, t = ftype.value,
        st = fstate.value, used = fused.checked;
  document.querySelectorAll(".mod").forEach(sec => {
    let shown = 0;
    sec.querySelectorAll(".row").forEach(row => {
      const s = row.classList.contains("keep") ? "keep" : row.classList.contains("rej") ? "rej" : "undecided";
      const noted = !!row.querySelector(".note").value;
      let ok = true;
      if(term && !row.dataset.s.includes(term)) ok = false;
      if(m && row.dataset.mod !== m) ok = false;
      if(t && row.dataset.type !== t) ok = false;
      const flagged = /^(\u26a0|UNSURE)/.test(row.querySelector(".note").value.trim());
      if(st === "flagged") { if(!flagged) ok = false; }
      else if(st === "guess") { if(row.dataset.guess !== "1") ok = false; }
      else if(st === "noted" ? !noted : st && s !== st) ok = false;
      if(used && +row.dataset.n === 0) ok = false;
      row.classList.toggle("hide", !ok);
      if(ok) shown++;
    });
    sec.style.display = shown ? "" : "none";
  });
  retally();
}
[q, fmod, ftype, fstate, fused].forEach(el => el.addEventListener("input", filter));
document.getElementById("clearf").onclick = () => {
  q.value=""; fmod.value=""; ftype.value=""; fstate.value=""; fused.checked=false; filter();
};
document.getElementById("collapse").onclick = () =>
  document.querySelectorAll(".mod").forEach(s => { s.classList.add("collapsed"); s.querySelector(".caret").textContent="▸"; });
document.getElementById("expand").onclick = () =>
  document.querySelectorAll(".mod").forEach(s => { s.classList.remove("collapsed"); s.querySelector(".caret").textContent="▾"; });

/* ---------- tallies ---------- */
function retally(){
  let k=0, r=0, n=0, shown=0;
  document.querySelectorAll(".mod").forEach(sec => {
    let sk=0, sr=0, tot=0;
    sec.querySelectorAll(".row").forEach(row => {
      tot++;
      if(!row.classList.contains("hide")) shown++;
      if(row.classList.contains("keep")) { k++; sk++; }
      if(row.classList.contains("rej"))  { r++; sr++; }
      if(row.querySelector(".note").value) n++;
    });
    sec.querySelector("[data-prog]").textContent =
      `${sk} whitelisted · ${tot-sk} stripped` + (sr ? ` (${sr} deliberate)` : "");
  });
  document.getElementById("tally").innerHTML =
    `<b>${shown}</b> shown · <span class="k">${k} whitelisted</span> · ` +
    `<span class="r">${DATA.length-k} stripped</span> ` +
    `(${r} deliberate NO, ${DATA.length-k-r} not looked at) · ${n} noted`;
  document.getElementById("score").innerHTML =
    `whitelisted <span class="in">${k}</span> of ${DATA.length} &nbsp;·&nbsp; ` +
    `will be stripped: <span class="out">${DATA.length-k}</span>`;
}

document.getElementById("hdr").textContent =
  `${DATA.length} defs · ${DATA.filter(d=>d.n>0).length} occur in ${STATS.save} · ` +
  `${STATS.mutatorInstances} mutator instances on ${STATS.mutatorTiles} tiles · ` +
  `${STATS.landmarkInstances} landmarks`;

/* ---------- export ----------
   🔴 The posture travels WITH the data. `whitelisted` is the complete list of
   what may exist on the planet; everything else in `universe` is stripped, and
   `rejected` only records which of those were looked at on purpose. A consumer
   that saw a sparse {defName: state} map could read it as "strip only these",
   which is the exact inversion of the ruling - hence the explicit shape. */
function payload(){
  const whitelisted = [], rejected = [], notes = {}, items = {};
  DATA.forEach(d => {
    const s = get(d.defName);
    if(s.state === "keep") whitelisted.push(d.defName);
    else if(s.state === "rej") rejected.push(d.defName);
    if(s.note) notes[d.defName] = s.note;
    if(s.state || s.note)
      items[d.defName] = {state: s.state === "keep" ? "whitelisted"
                               : s.state === "rej" ? "rejected" : "undecided",
                          note: s.note || "", label: d.label, mod: d.mod,
                          type: d.type, occurrences: d.n};
  });
  return {
    posture: "whitelist",
    meaning: "ONLY defNames in `whitelisted` may exist on the planet. " +
             "Everything else in `universe` is stripped, whether it was " +
             "rejected on purpose or never looked at.",
    world: STATS.save,
    universeSize: DATA.length,
    whitelistedCount: whitelisted.length,
    strippedCount: DATA.length - whitelisted.length,
    whitelisted, rejected, notes, items,
    universe: DATA.map(d => d.defName)
  };
}
const expEl = document.getElementById("exp"), ta = document.getElementById("expta"),
      msg = document.getElementById("expmsg");
document.getElementById("btnexp").onclick = () => {
  const p = payload(), txt = JSON.stringify(p, null, 2);
  ta.value = txt;
  document.getElementById("expcount").textContent =
    `whitelist of ${p.whitelistedCount}, stripping ${p.strippedCount} of ${p.universeSize}`;
  msg.innerHTML = "Everything is also in this box — select all and copy if the buttons are blocked.";
  expEl.classList.add("open");
  ta.focus(); ta.setSelectionRange(0,0);
};
document.getElementById("expclose").onclick = () => expEl.classList.remove("open");
expEl.addEventListener("click", e => { if(e.target === expEl) expEl.classList.remove("open"); });

document.getElementById("copy").onclick = async () => {
  try { await navigator.clipboard.writeText(ta.value); msg.innerHTML = '<span class="ok">Copied to clipboard.</span>'; }
  catch(e){ ta.select(); document.execCommand("copy");
            msg.innerHTML = '<span class="warn">Clipboard API blocked — selected the box and tried execCommand. Ctrl+C now.</span>'; }
};
document.getElementById("dl").onclick = () => {
  try{
    const b = new Blob([ta.value], {type:"application/json"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(b);
    a.download = "worldmap_whitelist.json";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href), 5000);
    msg.innerHTML = '<span class="ok">Download started — check your Downloads folder.</span>';
  } catch(e){ msg.innerHTML = '<span class="warn">Download blocked. Use copy, or select the box below.</span>'; }
};
document.getElementById("imp").onclick = () => {
  let obj; try { obj = JSON.parse(ta.value); } catch(e){
    msg.innerHTML = '<span class="warn">That is not valid JSON.</span>'; return; }
  S = {};
  const mark = (d, st, note) => {
    const cur = S[d] || {state:"", note:""};
    if(st) cur.state = st;
    if(note) cur.note = note;
    if(cur.state || cur.note) S[d] = cur;
  };
  if(Array.isArray(obj.whitelisted)){                 // the exported shape
    obj.whitelisted.forEach(d => mark(d, "keep"));
    (obj.rejected || []).forEach(d => mark(d, "rej"));
    Object.entries(obj.notes || {}).forEach(([d, t]) => mark(d, "", t));
  } else {                                            // a bare {defName: {...}} map
    Object.entries(obj).forEach(([d, v]) => {
      if(!v || typeof v !== "object") return;
      const st = (v.state === "keep" || v.state === "whitelisted") ? "keep"
               : (v.state === "rej"  || v.state === "rejected")    ? "rej" : "";
      mark(d, st, v.note);
    });
  }
  save();
  repaint();
  msg.innerHTML = '<span class="ok">Imported ' + Object.keys(S).length + ' items.</span>';
};

function repaint(){
  document.querySelectorAll(".row").forEach(row => {
    const s = get(row.dataset.d);
    row.classList.remove("keep","rej"); if(s.state) row.classList.add(s.state);
    const nt = row.querySelector(".note"); nt.value = s.note || ""; nt.classList.toggle("has", !!s.note);
  });
  filter();
}

/* ---------- back to the prefill ----------
   The only thing that overwrites the owner's own decisions, and it asks first. */
document.getElementById("reprefill").onclick = () => {
  if(!confirm("Throw away every decision in this browser and go back to the "
            + "pre-filled defaults?\n\nExport first if you want to keep them.")) return;
  S = clonePrefill(); save(); repaint();
};
document.getElementById("prefillbar").querySelector(".why").insertAdjacentHTML("beforeend",
  seeded
    ? ' <b class="ok">Filled in ' + seededCount + ' rows from the prefill just now'
      + (ownCount ? ', and kept your ' + ownCount + ' existing decisions untouched.' : '.') + '</b>'
    : ' <b class="warn">Every row already carries your own saved decision \u2014 nothing to fill in.</b>');

filter();

/* The mod headers stick UNDER the page header, whose height depends on how the
   filter bar wraps. Measure it rather than guessing a constant. */
const hdrEl = document.querySelector("header");
const fitHeader = () => document.documentElement.style.setProperty(
  "--hh", hdrEl.getBoundingClientRect().height + "px");
fitHeader(); addEventListener("resize", fitHeader);
</script></body></html>
"""


def load_prefill(path: Path) -> dict:
    """The baked-in defaults, as the browser's own {defName:{state,note}} map.

    Accepts the sheet's export shape (`whitelisted` / `rejected` / `notes`) so
    the owner can export a reviewed sheet straight back over this file and have
    the next regeneration ship HIS calls as the new default. An absent file is
    not an error - the sheet then simply opens blank, as it used to.
    """
    if not path.exists():
        return {}
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: dict = {}

    def mark(d, state="", note=""):
        cur = out.setdefault(d, {"state": "", "note": ""})
        if state:
            cur["state"] = state
        if note:
            cur["note"] = note

    if isinstance(obj.get("whitelisted"), list):
        for d in obj["whitelisted"]:
            mark(d, "keep")
        for d in obj.get("rejected") or []:
            mark(d, "rej")
        for d, t in (obj.get("notes") or {}).items():
            mark(d, "", t)
    else:                                       # a bare {defName: {...}} map
        for d, v in obj.items():
            if not isinstance(v, dict):
                continue
            st = {"keep": "keep", "whitelisted": "keep",
                  "rej": "rej", "rejected": "rej"}.get(v.get("state"), "")
            mark(d, st, v.get("note") or "")
    return {d: v for d, v in out.items() if v["state"] or v["note"]}


def render(rows, stats, prefill: dict | None = None) -> str:
    slim = [{"defName": r["defName"], "label": r["label"], "type": r["type"],
             "mod": r["mod"], "desc": r["desc"], "meta": r["meta"],
             "effect": r.get("effect", ""),
             "n": r["n"], "tiles": r["tiles"]} for r in rows]
    html = HTML
    html = html.replace("__DATA__", json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("__STATS__", json.dumps(stats, ensure_ascii=False))
    html = html.replace("__PREFILL__", json.dumps(prefill or {}, ensure_ascii=False,
                                                  separators=(",", ":")))
    html = html.replace("__LSKEY__", "jawa.worldmap.decisions.v1")
    return html


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--save", help="the .rws to count against (default: newest)")
    ap.add_argument("--dump", default=str(DEFDUMP), help="def dump defs/ dir")
    ap.add_argument("--out", default=str(OUT_HTML))
    ap.add_argument("--prefill", default=str(PREFILL_JSON),
                    help="decisions baked in as the page's default state")
    ap.add_argument("--no-prefill", action="store_true",
                    help="ship a blank sheet, the pre-2026-08-16 behaviour")
    a = ap.parse_args()

    dump = Path(a.dump)
    save = Path(a.save) if a.save else newest_save(SAVES)
    rows, stats = build_rows(dump, save)

    prefill = {} if a.no_prefill else load_prefill(Path(a.prefill))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(rows, stats, prefill), encoding="utf-8")

    used = sum(1 for r in rows if r["n"] > 0)
    per_mod = collections.Counter(r["mod"] for r in rows)
    print("save          %s" % stats["save"])
    print("defs          %d  (%d mutators, %d landmarks)"
          % (len(rows),
             sum(1 for r in rows if r["type"] == "mutator"),
             sum(1 for r in rows if r["type"] == "landmark")))
    print("occur > 0     %d   (%d mutator instances on %d tiles, %d landmarks)"
          % (used, stats["mutatorInstances"], stats["mutatorTiles"],
             stats["landmarkInstances"]))
    print("unresolved    %s" % (stats["unresolvedMutatorHashes"] or "none - table matches the save"))
    if stats["landmarksNotInDump"]:
        print("🔴 landmarks in the save with no def: %s" % stats["landmarksNotInDump"])
    for m, c in per_mod.most_common():
        u = sum(1 for r in rows if r["mod"] == m and r["n"] > 0)
        print("   %-42s %4d defs  %4d used" % (m, c, u))
    print("posture       WHITELIST - default is EXCLUDE; undecided means stripped")
    if prefill:
        pk = sum(1 for v in prefill.values() if v["state"] == "keep")
        pr = sum(1 for v in prefill.values() if v["state"] == "rej")
        print("prefill       %d rows baked in (%d keep, %d NO, %d left open) from %s"
              % (len(prefill), pk, pr, len(prefill) - pk - pr, Path(a.prefill).name))
    else:
        print("prefill       none - the sheet opens blank")
    print("wrote         %s  (%.0f KB)" % (out, out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
