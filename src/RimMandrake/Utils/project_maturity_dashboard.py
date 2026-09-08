#!/usr/bin/env python3
"""project_maturity_dashboard.py — PROJECT_MATURITY_DASHBOARD_1's renderer.

    python3 src/RimMandrake/Utils/project_maturity_dashboard.py
        writes Transient/project_maturity_dashboard.html (and .json alongside it)

WHAT THIS IS
============
The first honest answer to "how close are we to delivery", per the ruling
recorded at `infrastructure/state/items/PROJECT_MATURITY_DASHBOARD_1.md`. Two
spines on one page:

  1. SYSTEMS — a maturity grid, two independent axes per system:
       FUNCTION  planned -> designed -> implemented -> runnable -> validated -> played
       CONTENT   none -> placeholder -> authored -> final
     A system is "done" only at top-right. Read from the rimflow capability
     registry — `rimflow capability set/list` — never hand-edited, never
     invented here.

  2. CONTENT — the world inventory already written in
     `infrastructure/state/GOAL_SHEET.md` (10 sections, hand-ticked). Read
     AS-IS: this script counts its checkboxes, it does not invent a parallel
     inventory.

Plus one small tile for the clean/dirty code sheet
(`infrastructure/state/CODE_REVIEW_STATUS.json` via `code_review_status.py`),
and a regression view — rung counts over time, derived from `events.jsonl` —
so a DROP is visible.

⛔ NO HOOKS. This script READS state (the ledger, GOAL_SHEET.md, the review
log). It never blocks a write, never gates a commit, and is never a
prerequisite for anything else running. Same rendering approach as
`codebase_health.py` / `codebase_health_artifact.html`: one generator, a
JSON payload, a self-contained dark-themed page with the payload inlined —
no server, no build step, open the .html directly.

Every number printed on the page comes from the JSON this run wrote.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

sys.path.insert(0, os.path.dirname(HERE))   # src/RimMandrake/, which holds rimflow/
sys.path.insert(0, HERE)                     # this dir, which holds code_review_status.py

from rimflow import model               # noqa: E402  the capability registry's only writer
import code_review_status as CRS        # noqa: E402  the authority on CLEAN/DIRTY

GOAL_SHEET = os.path.join(ROOT, "infrastructure", "state", "GOAL_SHEET.md")

FUNCTION_RUNGS = model.FUNCTION_RUNGS
CONTENT_RUNGS = model.CONTENT_RUNGS


# ---------------------------------------------------------------- git helper
def git(args):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           text=True, timeout=8)
        return r.stdout.strip() if r.returncode == 0 else ""
    except subprocess.TimeoutExpired:
        return ""


# ------------------------------------------------------------ spine 1: SYSTEMS
def load_capabilities():
    """-> (world, raw_events). `world.capabilities` is rimflow's own projection —
    read, never hand-derived twice. `raw_events` (only the `capability` verb,
    in ledger order) is what the regression view walks."""
    try:
        events = model.read(model.EVENTS)
    except model.LedgerError as e:
        sys.stderr.write("FAIL: could not read the rimflow ledger: %s\n" % e)
        return model.World(), []
    world = model.replay(events)
    cap_events = [ev for ev in events if ev.get("event") == "capability"]
    return world, cap_events


def function_index(rung):
    return FUNCTION_RUNGS.index(rung) if rung in FUNCTION_RUNGS else -1


def content_index(rung):
    return CONTENT_RUNGS.index(rung) if rung in CONTENT_RUNGS else -1


TIER_DIRS = ("RimMandrake", "RimStarWars", "RimUtinni")


def mod_metadata():
    """system (mod folder name) -> {tier, label, blurb}, read from each mod's
    About/About.xml. The registry stores bare folder names; the human-facing
    name and description live only in the mod itself. Best-effort: a system
    with no readable About.xml just falls back to its folder name."""
    import xml.etree.ElementTree as ET
    meta = {}
    for tier in TIER_DIRS:
        base = os.path.join(ROOT, "src", tier)
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            about = os.path.join(base, d, "About", "About.xml")
            if d in meta or not os.path.isfile(about):
                continue
            label, blurb = d, ""
            try:
                root = ET.parse(about).getroot()
                raw = (root.findtext("name") or "").strip()
                # About names carry tier prefixes ("RimMandrake: RSW — Beast
                # Lairs"); strip them — the chip already encodes tier by colour.
                label = re.sub(r"^Rim(?:Mandrake|StarWars|Utinni)\s*:?\s*"
                               r"(?:(?:R(?:M|SW|UT)|Mandrake|Star\s?Wars|Utinni)"
                               r"\s*[—–-]\s*)?", "", raw) or d
                blurb = " ".join((root.findtext("description") or "").split())
                if len(blurb) > 360:
                    blurb = blurb[:357] + "…"
            except ET.ParseError:
                pass
            meta[d] = {"tier": tier, "label": label, "blurb": blurb}
    return meta


def systems_payload(world):
    meta = mod_metadata()
    systems = []
    for name in sorted(world.capabilities):
        cap = world.capabilities[name]
        m = meta.get(name, {})
        systems.append({
            "system": cap.system,
            "tier": m.get("tier", ""),
            "label": m.get("label", cap.system),
            "blurb": m.get("blurb", ""),
            "functionRung": cap.function_rung,
            "contentRung": cap.content_rung,
            "evidenceRef": cap.evidence_ref,
            "date": cap.date,
            "updatedAt": cap.updated_at,
            "updatedBy": cap.updated_by,
            "done": cap.function_rung == "played" and cap.content_rung == "final",
        })
    return systems


def headline_counts(systems, axis_key, ladder):
    """-> {rung: n}, total. Raw counts beside every % — a % over ~40
    capabilities misleads (the ruling, verbatim)."""
    counts = dict.fromkeys(ladder, 0)
    counts["__unset__"] = 0
    for s in systems:
        v = s[axis_key]
        if v in counts:
            counts[v] += 1
        else:
            counts["__unset__"] += 1
    return counts


def grid_payload(systems):
    """function_rung x content_rung -> [system names]. Unset axes get their own
    row/column ("unset") so a half-registered system is visible, not dropped."""
    grid = {}
    for s in systems:
        fr = s["functionRung"] or "unset"
        cr = s["contentRung"] or "unset"
        grid.setdefault(fr, {}).setdefault(cr, []).append(s["system"])
    return grid


def regression_payload(cap_events):
    """Rung counts over time, one snapshot per capability event, so a DROP in
    any rung's count is visible on the page. Walking raw events (not the
    replayed World) because the World only keeps the LATEST state per system —
    the regression view needs every step along the way."""
    state = {}   # system -> {"function": rung|None, "content": rung|None}
    snaps = []
    for ev in cap_events:
        sysname = ev.get("system")
        if not sysname:
            continue
        if ev.get("retired"):
            state.pop(sysname, None)
        else:
            st = state.setdefault(sysname, {"function": None, "content": None})
            if ev.get("function_rung"):
                st["function"] = ev["function_rung"]
            if ev.get("content_rung"):
                st["content"] = ev["content_rung"]
        fcounts = dict.fromkeys(FUNCTION_RUNGS, 0)
        ccounts = dict.fromkeys(CONTENT_RUNGS, 0)
        for s in state.values():
            if s["function"] in fcounts:
                fcounts[s["function"]] += 1
            if s["content"] in ccounts:
                ccounts[s["content"]] += 1
        snaps.append({
            "ts": ev.get("ts"),
            "system": sysname,
            "seat": ev.get("seat"),
            "function": fcounts,
            "content": ccounts,
            "nSystems": len(state),
        })
    return snaps


# ------------------------------------------------------ spine 2: GOAL_SHEET
SECTION_RE = re.compile(r"^##\s+(\d+)\.\s*(?:\U0001f512\s*)?(.+?)\s*$")
BOX_RE = re.compile(r"^(\s*)-\s*\[([ xX])\]\s*(.+?)\s*$")


def parse_goal_sheet():
    """Read GOAL_SHEET.md AS-IS: 10 sections, each a list of checkboxes,
    nested boxes counted too. No parallel inventory invented here — every
    number below is a literal count of `- [ ]` / `- [x]` lines under a `## N.`
    heading in that file."""
    if not os.path.isfile(GOAL_SHEET):
        return {"ok": False, "sections": [], "ticked": 0, "total": 0}
    with open(GOAL_SHEET, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    sections = []
    cur = None
    for line in lines:
        m = SECTION_RE.match(line)
        if m:
            cur = {"n": int(m.group(1)), "title": m.group(2), "ticked": 0,
                  "total": 0, "items": []}
            sections.append(cur)
            continue
        m = BOX_RE.match(line)
        if m and cur is not None:
            ticked = m.group(2).lower() == "x"
            cur["ticked"] += 1 if ticked else 0
            cur["total"] += 1
            cur["items"].append({"text": m.group(3)[:140], "ticked": ticked,
                                 "depth": len(m.group(1)) // 2})
    ticked_total = sum(s["ticked"] for s in sections)
    box_total = sum(s["total"] for s in sections)
    return {"ok": True, "sections": sections, "ticked": ticked_total, "total": box_total}


# --------------------------------------------------- the clean/dirty tile
def code_review_tile():
    """One small readout, not this dashboard's parent — the ruling's own words.
    Mirrors `code_review_status.py cmd_list`'s own walk: pure-Python hash
    compare per recorded entry, zero git spawns."""
    data = CRS.load()
    clean = dirty = unknown = recidivists = 0
    for rel, entry in data.items():
        state, _ = CRS.clean_state(rel, entry)
        if state == "CLEAN":
            clean += 1
        elif entry.get("hash"):
            dirty += 1
            if (entry.get("cleanCount") or 0) > 0:
                recidivists += 1
        else:
            unknown += 1
    return {"total": len(data), "clean": clean, "dirty": dirty, "unknown": unknown,
           "recidivists": recidivists}


# -------------------------------------------------------------------- page
def read_here(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


def write_html(out_path, payload):
    data = json.dumps(payload, separators=(",", ":"))
    html = PAGE.replace("__DATA__", data)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project Maturity Dashboard</title>
<style>
:root{
  /* warm 70s browns — owner-approved look from the seed-proposal page; keep this palette */
  --bg:#171310; --panel:#211b16; --panel2:#1c1712; --line:#332a20; --ink:#efe7d9;
  --dim:#a99d89; --accent:#e0803a;
  --r0:#7d7565; --r1:#c98536; --r2:#c96634; --r3:#8aa24a; --r4:#c9a44a;
  --c0:#7d7565; --c1:#c9a44a; --c2:#5390c4; --c3:#3a6ea0;
  --red:#d05a3c; --green:#4f9147; --grey:#7d7565; --unk:#c9a44a;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);
  font:13px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  padding:0 0 40px}
header{padding:16px 22px;border-bottom:1px solid var(--line);background:var(--panel);
  display:flex;gap:18px;align-items:baseline;flex-wrap:wrap;position:sticky;top:0;z-index:3}
h1{font-size:17px;margin:0;font-weight:650;letter-spacing:.2px}
.sub{color:var(--dim);font-size:11.5px}
main{max-width:1320px;margin:0 auto;padding:22px}
section.block{margin-bottom:30px}
h2{font-size:12.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--dim);
  margin:0 0 12px;display:flex;align-items:center;gap:10px}
h2 .n{color:var(--ink);font-weight:600;text-transform:none;letter-spacing:0;font-size:12px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
.row{display:flex;gap:18px;flex-wrap:wrap}
.row>.panel{flex:1;min-width:320px}

/* ---- headline bars ---- */
.ladder{display:flex;flex-direction:column;gap:8px}
.rungrow{display:grid;grid-template-columns:118px 1fr 92px;gap:10px;align-items:center;
  font-size:11.5px}
.rungrow b{color:var(--ink);font-weight:600;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.barbg{background:#0e1016;border-radius:4px;height:14px;overflow:hidden;
  border:1px solid var(--line)}
.barfg{height:100%;border-radius:3px}
.rungrow .cnt{text-align:right;color:var(--dim);font-variant-numeric:tabular-nums}
.rungrow .cnt b{color:var(--ink)}
.weighting{margin-top:10px;font-size:11px;color:var(--dim)}

/* ---- grid ---- */
table.grid{border-collapse:collapse;width:100%;font-size:11.5px}
table.grid th,table.grid td{border:1px solid var(--line);padding:6px 8px;text-align:left;
  vertical-align:top}
table.grid th{background:var(--panel2);color:var(--dim);font-weight:600;font-size:10.5px;
  text-transform:uppercase;letter-spacing:.04em}
table.grid td.corner{background:var(--panel2)}
table.grid td.cell{width:210px;min-width:210px;max-width:210px}
table.grid td.done{background:rgba(79,145,71,.16)}
/* one chip per row, all the same size, so the fills compare at a glance:
   the wash is a progress bar along the FUNCTION ladder, the thin bottom
   strip is the CONTENT ladder; tier is the left stripe's colour */
.chip2{position:relative;display:block;background:var(--panel2);border:1px solid var(--line);
  border-left:4px solid var(--grey);border-radius:4px;padding:2px 8px;margin:0 0 3px;
  font-size:11px;color:var(--ink);white-space:nowrap;overflow:hidden;cursor:default}
.chip2 .fill{position:absolute;left:0;top:0;bottom:0;opacity:.26;pointer-events:none}
.chip2 .cfill{position:absolute;left:0;bottom:0;height:2px;background:var(--c2);
  pointer-events:none}
.chip2 .lbl{position:relative;display:block;overflow:hidden;text-overflow:ellipsis}
.chip2:hover{border-color:var(--accent)}
.cellcount{color:var(--dim);font-size:10px;margin-bottom:4px}
.gridlegend{display:flex;gap:16px;flex-wrap:wrap;margin:0 0 10px;font-size:11px;color:var(--dim)}
.gridlegend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;
  vertical-align:-1px}
/* hover card for any [data-sys] element */
#tip{position:fixed;z-index:10;max-width:360px;background:var(--panel);
  border:1px solid var(--accent);border-radius:8px;padding:10px 12px;font-size:11.5px;
  pointer-events:none;box-shadow:0 6px 24px rgba(0,0,0,.5)}
#tip .t{font-weight:700;font-size:12.5px;margin-bottom:2px}
#tip .m{color:var(--dim);font-size:10.5px;margin-bottom:6px}
#tip .d{color:var(--ink);opacity:.9}
#tip .e{color:var(--dim);font-size:10.5px;margin-top:6px;border-top:1px solid var(--line);
  padding-top:5px}

/* ---- systems table ---- */
table.sys{border-collapse:collapse;width:100%;font-size:11.5px}
table.sys th{text-align:left;color:var(--dim);font-weight:600;font-size:10.5px;
  text-transform:uppercase;letter-spacing:.04em;padding:5px 8px;border-bottom:1px solid var(--line)}
table.sys td{padding:5px 8px;border-bottom:1px solid #2a221a}
table.sys tr:hover td{background:#2a2219}
.tag{display:inline-block;border-radius:4px;padding:1px 7px;font-size:10.5px;font-weight:600}
.tag.done{background:rgba(79,145,71,.25);color:#9fd08a}
.tiermark{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:7px;
  vertical-align:-1px}

/* ---- goal sheet ---- */
.gsrow{display:grid;grid-template-columns:230px 1fr 74px;gap:10px;align-items:center;
  padding:5px 0;font-size:12px}
.gsrow .barbg{height:10px}

/* ---- tile ---- */
.tiles{display:flex;gap:14px;flex-wrap:wrap}
.tile{background:var(--panel2);border:1px solid var(--line);border-radius:8px;
  padding:12px 16px;min-width:120px}
.tile .v{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}
.tile .l{color:var(--dim);font-size:10.5px;text-transform:uppercase;letter-spacing:.05em}
.tile.green .v{color:var(--green)}
.tile.grey .v{color:var(--grey)}
.tile.unk .v{color:var(--unk)}

/* ---- regression chart ---- */
svg.reg{width:100%;height:220px;display:block}
.reglegend{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;font-size:10.5px;color:var(--dim)}
.reglegend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;
  vertical-align:-1px}
.empty{color:var(--dim);font-style:italic;font-size:12px}
code{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#d8cdb8}
</style></head><body>
<div id="app">
  <header>
    <div><h1>Project Maturity Dashboard</h1>
      <div class="sub" id="stamp"></div></div>
  </header>
  <main>
    <section class="block">
      <h2>Headline <span class="n" id="headlineN"></span></h2>
      <div class="row">
        <div class="panel"><h2 style="margin-bottom:10px">Function axis</h2>
          <div class="ladder" id="functionBars"></div>
          <div class="weighting" id="functionWeight"></div></div>
        <div class="panel"><h2 style="margin-bottom:10px">Content axis</h2>
          <div class="ladder" id="contentBars"></div>
          <div class="weighting" id="contentWeight"></div></div>
      </div>
    </section>

    <section class="block">
      <h2>Systems — maturity grid <span class="n" id="gridN"></span></h2>
      <div class="panel"><div id="gridWrap" style="overflow-x:auto"></div></div>
    </section>

    <section class="block">
      <h2>Systems — the roster</h2>
      <div class="panel" style="overflow-x:auto"><table class="sys" id="sysTable"></table></div>
    </section>

    <section class="block">
      <h2>Regression — rung counts over time <span class="n">a drop is a regression</span></h2>
      <div class="row">
        <div class="panel" style="flex:1;min-width:420px">
          <div style="color:var(--dim);font-size:11px;margin-bottom:6px">FUNCTION</div>
          <svg class="reg" id="regFunction"></svg>
          <div class="reglegend" id="legFunction"></div>
        </div>
        <div class="panel" style="flex:1;min-width:420px">
          <div style="color:var(--dim);font-size:11px;margin-bottom:6px">CONTENT</div>
          <svg class="reg" id="regContent"></svg>
          <div class="reglegend" id="legContent"></div>
        </div>
      </div>
    </section>

    <section class="block">
      <h2>Content inventory — GOAL_SHEET.md, as-is <span class="n" id="gsN"></span></h2>
      <div class="panel" id="goalSheet"></div>
    </section>

    <section class="block">
      <h2>Code review — clean / dirty (one tile, not this dashboard's parent)</h2>
      <div class="panel"><div class="tiles" id="crTiles"></div></div>
    </section>
  </main>
</div>
<script>
const DATA = __DATA__;
/* Plain hex, not CSS var() — an SVG `stroke` attribute set via setAttribute does
   not resolve a custom property the way an inline `style` does, so one palette
   is kept here rather than fighting two different resolution rules for one map. */
const FCOLOR = {"planned":"#7d7565","designed":"#c98536","implemented":"#c96634",
                "runnable":"#8aa24a","validated":"#4f9147","played":"#c9a44a","unset":"#7d7565"};
const CCOLOR = {"none":"#7d7565","placeholder":"#c9a44a","authored":"#5390c4",
               "final":"#3a6ea0","unset":"#7d7565"};
const FLADDER = ["planned","designed","implemented","runnable","validated","played"];
const CLADDER = ["none","placeholder","authored","final"];
/* chip colour = TIER (position in the matrix already tells the rungs) */
const TIERCOL = {"RimMandrake":"#c96634","RimStarWars":"#5390c4","RimUtinni":"#8aa24a","":"#7d7565"};
const BYSYS = {}; DATA.systems.forEach(s=>{ BYSYS[s.system] = s; });
const TIERORD = {"RimMandrake":0,"RimStarWars":1,"RimUtinni":2,"":3};

function el(tag, attrs, kids){
  const e = document.createElement(tag);
  for(const k in (attrs||{})) e.setAttribute(k, attrs[k]);
  (kids||[]).forEach(k=>e.appendChild(typeof k==="string"?document.createTextNode(k):k));
  return e;
}

/* ---- header ---- */
document.getElementById("stamp").textContent =
  DATA.head + " · " + DATA.generated + " · " + DATA.systems.length + " system(s) registered";

/* ---- headline ladders ---- */
function renderLadder(mountId, counts, ladder, colorMap, total){
  const mount = document.getElementById(mountId);
  mount.innerHTML = "";
  ladder.forEach(rung=>{
    const n = counts[rung] || 0;
    const pct = total ? Math.round(100*n/total) : 0;
    const row = el("div", {"class":"rungrow"});
    row.appendChild(el("b", {}, [rung]));
    const bg = el("div", {"class":"barbg"});
    const fg = el("div", {"class":"barfg", "style":"width:"+pct+"%;background:"+colorMap[rung]});
    bg.appendChild(fg);
    row.appendChild(bg);
    const cnt = el("span", {"class":"cnt"});
    const b = document.createElement("b"); b.textContent = n;
    cnt.appendChild(b); cnt.appendChild(document.createTextNode(" ("+pct+"%)"));
    row.appendChild(cnt);
    mount.appendChild(row);
  });
  if(counts["__unset__"]){
    const row = el("div", {"class":"rungrow"});
    row.appendChild(el("b", {style:"color:var(--dim)"}, ["(unset)"]));
    row.appendChild(el("div", {"class":"barbg"}));
    row.appendChild(el("span", {"class":"cnt"}, [String(counts["__unset__"])]));
    mount.appendChild(row);
  }
}
const total = DATA.systems.length;
document.getElementById("headlineN").textContent =
  total + " system(s), equal-weight per capability (owner may retune)";
renderLadder("functionBars", DATA.functionCounts, FLADDER, FCOLOR, total);
renderLadder("contentBars", DATA.contentCounts, CLADDER, CCOLOR, total);
document.getElementById("functionWeight").textContent =
  "\"done\" is played AND final on the SAME system — see the grid below.";
document.getElementById("contentWeight").textContent =
  total===0 ? "No systems registered yet — this axis is 0/0 until `rimflow capability set` runs." : "";

/* ---- grid ---- */
document.getElementById("gridN").textContent =
  total + " system(s) across " + FLADDER.length + "x" + CLADDER.length + " cells";
(function(){
  const wrap = document.getElementById("gridWrap");
  if(total === 0){ wrap.appendChild(el("div",{"class":"empty"},
    ["No systems registered yet. Seed with `rimflow capability set <SYSTEM> --function-rung … --content-rung …`."]));
    return; }
  const legend = el("div", {"class":"gridlegend"});
  ["RimMandrake","RimStarWars","RimUtinni"].forEach(t=>{
    const item = el("span");
    item.appendChild(el("i", {style:"background:"+TIERCOL[t]}));
    item.appendChild(document.createTextNode(t));
    legend.appendChild(item);
  });
  legend.appendChild(el("span", {style:"margin-left:auto"},
    ["wash = how far along the function ladder · bottom strip = content ladder · hover for details"]));
  wrap.parentNode.insertBefore(legend, wrap);
  const rows = FLADDER.concat(["unset"]);
  const cols = CLADDER.concat(["unset"]);
  const table = el("table", {"class":"grid"});
  const thead = el("tr", {}, [el("th", {"class":"corner"}, ["function \\ content"])]
    .concat(cols.map(c=>el("th", {}, [c]))));
  table.appendChild(thead);
  rows.forEach(fr=>{
    const tr = el("tr");
    tr.appendChild(el("th", {}, [fr]));
    cols.forEach(cr=>{
      const list = ((DATA.grid[fr] && DATA.grid[fr][cr]) || []).slice()
        .sort((a,b)=>{
          const sa = BYSYS[a]||{}, sb = BYSYS[b]||{};
          return (TIERORD[sa.tier||""]-TIERORD[sb.tier||""])
              || (sa.label||a).localeCompare(sb.label||b);
        });
      const isDone = fr==="played" && cr==="final" && list.length;
      const td = el("td", {"class":"cell"+(isDone?" done":"")});
      if(list.length){
        td.appendChild(el("div", {"class":"cellcount"}, [String(list.length)+" system(s)"]));
        list.forEach(name=>{
          const s = BYSYS[name] || {label:name, tier:""};
          const fpct = Math.round(100*(FLADDER.indexOf(s.functionRung)+1)/FLADDER.length);
          const cpct = Math.round(100*(CLADDER.indexOf(s.contentRung)+1)/CLADDER.length);
          const tc = TIERCOL[s.tier||""];
          const chip = el("span", {"class":"chip2", "data-sys":name,
            style:"border-left-color:"+tc});
          chip.appendChild(el("i", {"class":"fill",
            style:"width:"+Math.max(0,fpct)+"%;background:"+tc}));
          if(cpct > 0) chip.appendChild(el("i", {"class":"cfill", style:"width:"+cpct+"%"}));
          chip.appendChild(el("span", {"class":"lbl"}, [s.label||name]));
          td.appendChild(chip);
        });
      }
      tr.appendChild(td);
    });
    table.appendChild(tr);
  });
  wrap.appendChild(table);
})();

/* ---- hover card: any element carrying data-sys ---- */
(function(){
  const tip = el("div", {id:"tip", hidden:""});
  document.body.appendChild(tip);
  function fill(s){
    tip.innerHTML = "";
    tip.appendChild(el("div", {"class":"t"}, [s.label||s.system]));
    tip.appendChild(el("div", {"class":"m"},
      [(s.tier||"tier unknown")+" / "+s.system+" · "
       +(s.functionRung||"—")+" × "+(s.contentRung||"—")]));
    tip.appendChild(el("div", {"class":"d"},
      [s.blurb || "No description in this mod's About.xml yet."]));
    if(s.evidenceRef) tip.appendChild(el("div", {"class":"e"}, ["evidence: "+s.evidenceRef]));
  }
  function move(ev){
    const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
    let x = ev.clientX + pad, y = ev.clientY + pad;
    if(x + w > innerWidth - 8) x = ev.clientX - w - pad;
    if(y + h > innerHeight - 8) y = ev.clientY - h - pad;
    tip.style.left = Math.max(4,x)+"px"; tip.style.top = Math.max(4,y)+"px";
  }
  document.addEventListener("mouseover", ev=>{
    const t = ev.target.closest("[data-sys]");
    if(!t){ tip.hidden = true; return; }
    const s = BYSYS[t.getAttribute("data-sys")];
    if(!s){ tip.hidden = true; return; }
    fill(s); tip.hidden = false; move(ev);
  });
  document.addEventListener("mousemove", ev=>{ if(!tip.hidden) move(ev); });
})();

/* ---- systems table ---- */
(function(){
  const t = document.getElementById("sysTable");
  if(total === 0){
    t.parentNode.replaceChild(el("div",{"class":"empty"},["Registry is empty."]), t);
    return;
  }
  const head = el("tr", {}, ["name","folder","function","content","done","evidence","date","updated"]
    .map(h=>el("th", {}, [h])));
  t.appendChild(head);
  DATA.systems.slice().sort((a,b)=>
      (TIERORD[a.tier||""]-TIERORD[b.tier||""]) || (a.label||a.system).localeCompare(b.label||b.system)
  ).forEach(s=>{
    const tr = el("tr", {"data-sys":s.system});
    const nameTd = el("td", {style:"font-weight:600;white-space:nowrap"});
    nameTd.appendChild(el("span", {"class":"tiermark", style:"background:"+TIERCOL[s.tier||""]}));
    nameTd.appendChild(document.createTextNode(s.label || s.system));
    tr.appendChild(nameTd);
    tr.appendChild(el("td", {style:"color:var(--dim)"}, [s.system]));
    tr.appendChild(el("td", {}, [s.functionRung || "—"]));
    tr.appendChild(el("td", {}, [s.contentRung || "—"]));
    tr.appendChild(el("td", {}, [s.done ? el("span",{"class":"tag done"},["DONE"]) : ""]));
    tr.appendChild(el("td", {}, [s.evidenceRef || "—"]));
    tr.appendChild(el("td", {}, [s.date || "—"]));
    tr.appendChild(el("td", {}, [(s.updatedAt||"").slice(0,10) + (s.updatedBy?" ("+s.updatedBy+")":"")]));
    t.appendChild(tr);
  });
})();

/* ---- regression: a small hand-rolled line chart, no library needed ---- */
function drawRegression(svgId, legId, snaps, ladder, colorMap, field){
  const svg = document.getElementById(svgId);
  const leg = document.getElementById(legId);
  if(!snaps.length){
    svg.replaceWith(el("div", {"class":"empty"}, ["No capability events yet."]));
    return;
  }
  const W = svg.clientWidth || 560, H = 220, padL = 28, padR = 10, padT = 10, padB = 22;
  const maxY = Math.max(1, ...snaps.map(s => Math.max(...ladder.map(r => s[field][r] || 0))));
  const x = i => padL + (W-padL-padR) * (snaps.length===1 ? 0 : i/(snaps.length-1));
  const y = v => H-padB - (H-padT-padB) * (v/maxY);
  const ns = "http://www.w3.org/2000/svg";
  function mk(tag, attrs){
    const e = document.createElementNS(ns, tag);
    for(const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  svg.setAttribute("viewBox", "0 0 "+W+" "+H);
  // axes
  svg.appendChild(mk("line", {x1:padL,y1:H-padB,x2:W-padR,y2:H-padB,stroke:"#332a20"}));
  svg.appendChild(mk("line", {x1:padL,y1:padT,x2:padL,y2:H-padB,stroke:"#332a20"}));
  [0, maxY].forEach(v=>{
    const t = mk("text", {x:2, y:y(v)+3, fill:"#a99d89", "font-size":"9"});
    t.textContent = v; svg.appendChild(t);
  });
  ladder.forEach(rung=>{
    const pts = snaps.map((s,i)=>x(i)+","+y(s[field][rung]||0)).join(" ");
    svg.appendChild(mk("polyline", {points:pts, fill:"none",
      stroke: colorMap[rung], "stroke-width":"1.6"}));
    const i = document.createElement("i");
    i.style.background = colorMap[rung];
    leg.appendChild(el("span", {}, [i, rung]));
  });
}
drawRegression("regFunction", "legFunction", DATA.regression, FLADDER, FCOLOR, "function");
drawRegression("regContent", "legContent", DATA.regression, CLADDER, CCOLOR, "content");

/* ---- GOAL_SHEET ---- */
(function(){
  const mount = document.getElementById("goalSheet");
  const gs = DATA.goalSheet;
  document.getElementById("gsN").textContent =
    gs.ticked + " / " + gs.total + " boxes ticked ("
    + (gs.total ? Math.round(100*gs.ticked/gs.total) : 0) + "%)";
  if(!gs.ok){
    mount.appendChild(el("div", {"class":"empty"}, ["GOAL_SHEET.md not found."]));
    return;
  }
  gs.sections.forEach(s=>{
    const pct = s.total ? Math.round(100*s.ticked/s.total) : 0;
    const row = el("div", {"class":"gsrow"});
    row.appendChild(el("b", {}, [s.n + ". " + s.title]));
    const bg = el("div", {"class":"barbg"});
    bg.appendChild(el("div", {"class":"barfg", "style":"width:"+pct+"%;background:var(--green)"}));
    row.appendChild(bg);
    row.appendChild(el("span", {"class":"cnt"}, [s.ticked + "/" + s.total]));
    mount.appendChild(row);
  });
})();

/* ---- code review tile ---- */
(function(){
  const cr = DATA.codeReview;
  const mount = document.getElementById("crTiles");
  const tiles = [
    ["clean", cr.clean, "green"],
    ["dirty (drifted since marked)", cr.dirty, "grey"],
    ["unknown (legacy, unresolved)", cr.unknown, "unk"],
    ["reviewed, dirty again", cr.recidivists, "grey"],
    ["total review entries", cr.total, ""],
  ];
  tiles.forEach(([label, v, cls])=>{
    const t = el("div", {"class":"tile"+(cls?" "+cls:"")});
    t.appendChild(el("div", {"class":"v"}, [String(v)]));
    t.appendChild(el("div", {"class":"l"}, [label]));
    mount.appendChild(t);
  });
})();
</script>
</body></html>
"""


# ---------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="project_maturity_dashboard.py",
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "Transient"),
                    help="where the .html and .json land (default: Transient/)")
    ap.add_argument("--json-only", action="store_true", help="skip the HTML page")
    args = ap.parse_args(argv)

    world, cap_events = load_capabilities()
    systems = systems_payload(world)

    payload = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "head": git(["rev-parse", "--short", "HEAD"]) or "unknown",
        "systems": systems,
        "functionCounts": headline_counts(systems, "functionRung", FUNCTION_RUNGS),
        "contentCounts": headline_counts(systems, "contentRung", CONTENT_RUNGS),
        "grid": grid_payload(systems),
        "regression": regression_payload(cap_events),
        "goalSheet": parse_goal_sheet(),
        "codeReview": code_review_tile(),
        "weighting": "equal-weight per capability (default; owner may retune once he "
                     "sees real numbers — PROJECT_MATURITY_DASHBOARD_1, 'open, and "
                     "deliberately not blocking')",
    }

    os.makedirs(args.out_dir, exist_ok=True)
    json_path = os.path.join(args.out_dir, "project_maturity_dashboard.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)

    print("systems registered : %d" % len(systems))
    print("function counts     : %s" % payload["functionCounts"])
    print("content counts      : %s" % payload["contentCounts"])
    print("GOAL_SHEET boxes    : %d/%d ticked"
          % (payload["goalSheet"]["ticked"], payload["goalSheet"]["total"]))
    print("code review         : %s" % payload["codeReview"])
    print("json -> %s" % json_path)

    if not args.json_only:
        html_path = os.path.join(args.out_dir, "project_maturity_dashboard.html")
        write_html(html_path, payload)
        print("html -> %s" % html_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
