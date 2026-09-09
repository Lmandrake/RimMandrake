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


BUG_KINDS = ("bug", "defect", "fix")
ITEMS_DIR = os.path.join(ROOT, "infrastructure", "state", "items")


def _name_patterns(system, tier):
    """How an item names a system: the mod folder path (strong), the folder name
    as a case-sensitive whole word in the title, or its UPPER_SNAKE form in the
    item id (DROIDWORKS / SEA_BEASTS both match SeaBeasts)."""
    upper_flat = system.upper()
    upper_snake = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", system).upper()
    return {
        "path": "src/%s/%s" % (tier, system) if tier else None,
        "title_re": re.compile(r"\b%s\b" % re.escape(system)),
        "id_tokens": {upper_flat, upper_snake},
    }


def system_flags(world, systems):
    """system -> {"blocked": [ids], "awaiting": [ids]} from OPEN ledger items.
    RED/YELLOW per the owner's 2026-09-08 ruling: red = blocked by a bug
    (an open bug/defect/fix item naming the system), yellow = awaiting his
    decision (an open item with needs=owner naming it). Name-matching is
    deliberately conservative — path mention, exact folder word in the title,
    or the folder's UPPER_SNAKE in the item id — a false red cries wolf."""
    pats = {s["system"]: _name_patterns(s["system"], s.get("tier") or "") for s in systems}
    prose_cache = {}

    def prose(item_id):
        if item_id not in prose_cache:
            p = os.path.join(ITEMS_DIR, item_id + ".md")
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    prose_cache[item_id] = fh.read()
            except OSError:
                prose_cache[item_id] = ""
        return prose_cache[item_id]

    flags = {name: {"blocked": [], "awaiting": []} for name in pats}
    counts = {"openItems": 0, "openBugs": 0, "needsOwner": 0}
    for item in world.items.values():
        if item.state not in ("proposed", "ready", "doing", "blocked"):
            continue
        counts["openItems"] += 1
        is_bug = (item.kind or "") in BUG_KINDS
        needs_owner = item.needs == "owner"
        if is_bug:
            counts["openBugs"] += 1
        if needs_owner:
            counts["needsOwner"] += 1
        if not is_bug and not needs_owner:
            continue
        title = item.title or ""
        for name, pat in pats.items():
            hit = (pat["path"] and pat["path"] in prose(item.id)) \
                or pat["title_re"].search(title) \
                or any(tok in item.id for tok in pat["id_tokens"])
            if not hit:
                continue
            if is_bug:
                flags[name]["blocked"].append(item.id)
            if needs_owner:
                flags[name]["awaiting"].append(item.id)
    return flags, counts


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
    dirty_paths = []
    for rel, entry in data.items():
        state, _ = CRS.clean_state(rel, entry)
        if state == "CLEAN":
            clean += 1
        elif entry.get("hash"):
            dirty += 1
            dirty_paths.append(rel)
            if (entry.get("cleanCount") or 0) > 0:
                recidivists += 1
        else:
            unknown += 1
    return {"total": len(data), "clean": clean, "dirty": dirty, "unknown": unknown,
           "recidivists": recidivists, "dirtyPaths": sorted(dirty_paths)}


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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* warm 70s browns — the owner-approved look; single committed dark theme.
   Colour DOCTRINE (owner, 2026-09-08): RED = blocked by a bug, YELLOW =
   awaiting his decision, otherwise a brown ramp dark (beginning) -> light
   (satisfyingly complete). Tier is identity only: a small stripe/dot. */
:root{
  --bg:#171310; --panel:#211b16; --panel2:#1c1712; --line:#332a20; --ink:#efe7d9;
  --dim:#a99d89; --accent:#e0803a;
  --f0:#453321; --f1:#63492e; --f2:#82603a; --f3:#a37c49; --f4:#c49a5d; --f5:#e6be7e;
  --c0:#4a3624; --c1:#7a5a38; --c2:#ab8250; --c3:#dcb076;
  --red:#d05a3c; --yellow:#e0b13e; --green:#4f9147; --grey:#7d7565;
  --t-rm:#c96634; --t-sw:#5390c4; --t-ut:#8aa24a;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);
  font:13px/1.45 "IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  padding:0 0 40px}
header{padding:12px 22px 10px;border-bottom:1px solid var(--line);background:var(--panel);
  display:flex;gap:18px;align-items:baseline;flex-wrap:wrap;position:sticky;top:0;z-index:3}
h1{font-family:"Archivo",sans-serif;font-size:17px;margin:0;font-weight:800;letter-spacing:.2px}
.sub{color:var(--dim);font-size:11px}
.legend{display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-size:10.5px;
  color:var(--dim);margin-left:auto}
.legend .sw{display:inline-flex;vertical-align:-2px;margin-right:5px}
.legend .sw i{width:9px;height:11px;display:inline-block}
.legend .dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;
  vertical-align:-1px}
main{max-width:1860px;margin:0 auto;padding:16px 22px}
section.block{margin-bottom:22px}
h2{font-family:"Archivo",sans-serif;font-size:12px;text-transform:uppercase;
  letter-spacing:.09em;color:var(--dim);margin:0 0 10px;display:flex;
  align-items:center;gap:10px;font-weight:700}
h2 .n{color:var(--ink);font-weight:500;text-transform:none;letter-spacing:0;font-size:11.5px;
  font-family:"IBM Plex Sans"}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
.row{display:flex;gap:14px;flex-wrap:wrap}
code,.mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace}
code{font-size:11px;color:#d8cdb8}

/* ---- tile strip ---- */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:10px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:9px 12px 8px}
.tile .v{font-family:"IBM Plex Mono";font-size:20px;font-weight:600;
  font-variant-numeric:tabular-nums;line-height:1.15}
.tile .v small{font-size:11px;color:var(--dim);font-weight:400}
.tile .l{color:var(--dim);font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;margin-top:1px}
.tile.red{border-color:var(--red)} .tile.red .v{color:var(--red)}
.tile.yellow{border-color:var(--yellow)} .tile.yellow .v{color:var(--yellow)}
.tile.bright .v{color:var(--f5)}
.tile.green .v{color:var(--green)}

/* ---- two-column middle ---- */
.rail3{display:grid;grid-template-columns:repeat(2,minmax(240px,1fr));gap:14px;margin-bottom:16px}
@media(max-width:980px){.rail3{grid-template-columns:1fr}}

/* ---- matrix ---- */
table.grid{border-collapse:collapse;width:100%;font-size:11px}
table.grid th,table.grid td{border:1px solid var(--line);padding:5px 7px;text-align:left;
  vertical-align:top}
table.grid th{background:var(--panel2);color:var(--dim);font-weight:600;font-size:10px;
  text-transform:uppercase;letter-spacing:.04em}
table.grid td.corner{background:var(--panel2)}
table.grid td.cell{min-width:150px}
table.grid td.done{background:rgba(79,145,71,.16)}
table.grid td.zero{color:var(--line);text-align:center;font-family:"IBM Plex Mono";font-size:10px}
table.grid .marg{font-family:"IBM Plex Mono";color:var(--dim);text-align:right;
  font-variant-numeric:tabular-nums;background:var(--panel2)}
.cellcount{color:var(--dim);font-size:9.5px;margin-bottom:3px;font-family:"IBM Plex Mono"}
/* one chip per row, all the same size, so fills compare at a glance:
   wash = the brown progress ramp at this system's function rung; thin bottom
   strip = content rung; left stripe = tier; red/yellow REPLACE the wash when
   the system is blocked / awaiting the owner */
.chip2{position:relative;display:block;background:var(--panel2);border:1px solid var(--line);
  border-left:4px solid var(--grey);border-radius:4px;padding:1px 7px;margin:0 0 3px;
  font-size:10.5px;color:var(--ink);white-space:nowrap;overflow:hidden;cursor:default}
.chip2 .fill{position:absolute;left:0;top:0;bottom:0;pointer-events:none}
.chip2 .cfill{position:absolute;left:0;bottom:0;height:2px;pointer-events:none;opacity:.9}
.chip2 .lbl{position:relative;display:block;overflow:hidden;text-overflow:ellipsis}
.chip2 .lbl .g{font-family:"IBM Plex Mono";font-weight:600;margin-right:4px}
.chip2:hover{border-color:var(--accent)}
.chip2.blocked{border-color:var(--red);border-left-color:var(--red)}
.chip2.blocked .lbl .g{color:var(--red)}
.chip2.awaiting{border-color:var(--yellow);border-left-color:var(--yellow)}
.chip2.awaiting .lbl .g{color:var(--yellow)}

/* ---- ladders + tier rollup (right rail) ---- */
.rail{display:flex;flex-direction:column;gap:14px}
.rungrow{display:grid;grid-template-columns:96px 1fr 74px;gap:8px;align-items:center;
  font-size:10.5px;padding:2px 0}
.rungrow b{color:var(--ink);font-weight:500;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;font-family:"IBM Plex Mono";font-size:10.5px}
.barbg{height:11px;background:var(--panel2);border:1px solid var(--line);border-radius:3px;
  overflow:hidden}
.barfg{height:100%}
.rungrow .cnt{text-align:right;color:var(--dim);font-variant-numeric:tabular-nums;
  font-family:"IBM Plex Mono";font-size:10.5px}
.rungrow .cnt b{color:var(--ink);font-family:"IBM Plex Mono"}
.weighting{margin-top:8px;font-size:10px;color:var(--dim)}
.stackrow{display:grid;grid-template-columns:96px 1fr 40px;gap:8px;align-items:center;
  font-size:10.5px;padding:3px 0}
.stackrow b{font-weight:500;white-space:nowrap}
.stack{display:flex;height:13px;border-radius:3px;overflow:hidden;border:1px solid var(--line)}
.stack i{display:block;height:100%}
.stack i + i{border-left:1px solid var(--bg)}

/* ---- roster ---- */
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
.controls input[type=search]{background:var(--panel2);border:1px solid var(--line);
  border-radius:5px;color:var(--ink);font:11.5px "IBM Plex Sans";padding:4px 9px;width:190px}
.controls input[type=search]:focus{outline:1px solid var(--accent)}
.fbtn{background:var(--panel2);border:1px solid var(--line);border-radius:99px;
  color:var(--dim);font:10.5px "IBM Plex Sans";padding:2px 10px;cursor:pointer}
.fbtn.on{color:var(--ink);border-color:var(--accent)}
.fbtn .dot{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:5px;
  vertical-align:-1px}
table.sys{border-collapse:collapse;width:100%;font-size:11px}
table.sys th{text-align:left;color:var(--dim);font-weight:600;font-size:9.5px;
  text-transform:uppercase;letter-spacing:.04em;padding:4px 7px;
  border-bottom:1px solid var(--line);cursor:pointer;user-select:none;white-space:nowrap}
table.sys th:hover{color:var(--ink)}
table.sys td{padding:3px 7px;border-bottom:1px solid #2a221a;white-space:nowrap}
table.sys tr:hover td{background:#2a2219}
table.sys td.ev{max-width:330px;overflow:hidden;text-overflow:ellipsis;color:var(--dim);
  font-size:10.5px}
.tag{display:inline-block;border-radius:4px;padding:0 6px;font-size:9.5px;font-weight:600;
  font-family:"IBM Plex Mono"}
.tag.done{background:rgba(79,145,71,.25);color:#9fd08a}
.tag.blocked{background:rgba(208,90,60,.18);color:var(--red)}
.tag.awaiting{background:rgba(224,177,62,.15);color:var(--yellow)}
.tiermark{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:6px;
  vertical-align:-.5px}
.meter{display:inline-flex;gap:1.5px;margin-right:6px;vertical-align:-1px}
.meter i{width:7px;height:9px;border-radius:1.5px;background:var(--panel2);
  border:1px solid var(--line)}
.rungword{font-family:"IBM Plex Mono";font-size:10px;color:var(--dim)}
.age{font-family:"IBM Plex Mono";font-size:10px;color:var(--dim);
  font-variant-numeric:tabular-nums}
.age.stale{color:var(--yellow)}

/* ---- movement + regression ---- */
.movelist{font-size:10.5px;display:flex;flex-direction:column;gap:2px;
  max-height:238px;overflow-y:auto}
.movelist .mrow{display:grid;grid-template-columns:76px 1fr auto;gap:8px;padding:2px 0;
  border-bottom:1px solid #241d16}
.movelist .mts{color:var(--dim);font-family:"IBM Plex Mono";font-size:9.5px}
.movelist .mto{font-family:"IBM Plex Mono";font-size:9.5px}
svg.reg{width:100%;height:190px;display:block}
.reglegend{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;font-size:10px;color:var(--dim)}
.reglegend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:4px;
  vertical-align:-1px}

/* ---- goal sheet + code review ---- */
.bottom{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}
@media(max-width:980px){.bottom{grid-template-columns:1fr}}
.gsrow{display:grid;grid-template-columns:170px 1fr 58px;gap:8px;align-items:center;
  padding:3px 0;font-size:11px}
.gsrow .barbg{height:9px}
.dirtylist{columns:2;column-gap:18px;font-size:10px;color:var(--dim);margin-top:8px}
.dirtylist div{break-inside:avoid;padding:1px 0;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.empty{color:var(--dim);font-style:italic;font-size:11.5px}

/* ---- hover card ---- */
#tip{position:fixed;z-index:10;max-width:380px;background:var(--panel);
  border:1px solid var(--accent);border-radius:8px;padding:10px 12px;font-size:11.5px;
  pointer-events:none;box-shadow:0 6px 24px rgba(0,0,0,.5)}
#tip .t{font-family:"Archivo";font-weight:700;font-size:12.5px;margin-bottom:2px}
#tip .m{color:var(--dim);font-size:10.5px;margin-bottom:6px;font-family:"IBM Plex Mono"}
#tip .d{color:var(--ink);opacity:.9}
#tip .flag{margin-top:6px;font-size:10.5px;font-weight:600}
#tip .flag.blocked{color:var(--red)} #tip .flag.awaiting{color:var(--yellow)}
#tip .e{color:var(--dim);font-size:10.5px;margin-top:6px;border-top:1px solid var(--line);
  padding-top:5px}
</style></head><body>
<div id="app">
  <header>
    <div><h1>Project Maturity Dashboard</h1>
      <div class="sub" id="stamp"></div></div>
    <div class="legend">
      <span><span class="sw" id="rampSw"></span>progress: dark → light brown</span>
      <span><i class="dot" style="background:var(--red)"></i>✖ blocked by a bug</span>
      <span><i class="dot" style="background:var(--yellow)"></i>? awaiting your decision</span>
      <span><i class="dot" style="background:var(--t-rm)"></i>RimMandrake</span>
      <span><i class="dot" style="background:var(--t-sw)"></i>RimStarWars</span>
      <span><i class="dot" style="background:var(--t-ut)"></i>RimUtinni</span>
    </div>
  </header>
  <main>
    <section class="block">
      <div class="tiles" id="tiles"></div>
    </section>

    <section class="block">
      <div class="rail3">
        <div>
          <h2>Function ladder</h2>
          <div class="panel"><div class="ladder" id="functionBars"></div>
            <div class="weighting" id="functionWeight"></div></div>
        </div>
        <div>
          <h2>Content ladder</h2>
          <div class="panel"><div class="ladder" id="contentBars"></div></div>
          <h2 style="margin-top:14px">By tier <span class="n">function-rung mix</span></h2>
          <div class="panel" id="tierRoll"></div>
        </div>
      </div>
      <h2>Maturity grid <span class="n" id="gridN"></span></h2>
      <div class="panel"><div id="gridWrap" style="overflow-x:auto;scrollbar-width:thin"></div><div class="muted" id="gridScrollHint" style="display:none;font-size:10px;margin-top:4px">⟷ grid wider than panel — scroll horizontally</div></div>
    </section>

    <section class="block">
      <h2>The roster <span class="n" id="rosterN"></span></h2>
      <div class="panel">
        <div class="controls" id="rosterControls"></div>
        <div style="overflow-x:auto"><table class="sys" id="sysTable"></table></div>
      </div>
    </section>

    <section class="block">
      <div class="row">
        <div class="panel" style="flex:1;min-width:300px">
          <h2 style="margin-bottom:8px">Latest movement <span class="n">newest first</span></h2>
          <div class="movelist" id="movement"></div>
        </div>
        <div class="panel" style="flex:1.4;min-width:380px">
          <h2 style="margin-bottom:8px">Function rungs over time <span class="n">a drop is a regression</span></h2>
          <svg class="reg" id="regFunction"></svg>
          <div class="reglegend" id="legFunction"></div>
        </div>
        <div class="panel" style="flex:1.4;min-width:380px">
          <h2 style="margin-bottom:8px">Content rungs over time</h2>
          <svg class="reg" id="regContent"></svg>
          <div class="reglegend" id="legContent"></div>
        </div>
      </div>
    </section>

    <section class="block">
      <div class="bottom">
        <div>
          <h2>Content inventory <span class="n" id="gsN">GOAL_SHEET.md, as-is</span></h2>
          <div class="panel" id="goalSheet"></div>
        </div>
        <div>
          <h2>Code review <span class="n">one tile, not this dashboard's parent</span></h2>
          <div class="panel"><div class="tiles" id="crTiles" style="grid-template-columns:repeat(auto-fit,minmax(96px,1fr))"></div>
            <div class="dirtylist" id="dirtyList"></div></div>
        </div>
      </div>
    </section>
  </main>
</div>
<script>
const DATA = __DATA__;
/* Plain hex, not CSS var() — SVG setAttribute strokes don't resolve custom
   properties; one palette map serves both worlds. Colour doctrine (owner,
   2026-09-08): brown ramp = progress, red = blocked, yellow = awaiting him. */
const RAMPF = ["#453321","#63492e","#82603a","#a37c49","#c49a5d","#e6be7e"];
const RAMPC = ["#4a3624","#7a5a38","#ab8250","#dcb076"];
const RED = "#d05a3c", YELLOW = "#e0b13e", INK = "#efe7d9";
const FLADDER = ["planned","designed","implemented","runnable","validated","played"];
const CLADDER = ["none","placeholder","authored","final"];
const TIERCOL = {"RimMandrake":"#c96634","RimStarWars":"#5390c4","RimUtinni":"#8aa24a","":"#7d7565"};
const TIERORD = {"RimMandrake":0,"RimStarWars":1,"RimUtinni":2,"":3};
const BYSYS = {}; DATA.systems.forEach(s=>{ BYSYS[s.system] = s; });
const fIdx = s => FLADDER.indexOf(s.functionRung);
const cIdx = s => CLADDER.indexOf(s.contentRung);
const flag = s => s.blocked && s.blocked.length ? "blocked"
               : s.awaiting && s.awaiting.length ? "awaiting" : null;
/* chart strokes: ramp steps lifted toward ink so the dark end stays visible */
function mix(hex, hex2, t){
  const a=parseInt(hex.slice(1),16), b=parseInt(hex2.slice(1),16);
  const ch=(sh)=>Math.round(((a>>sh&255)*(1-t))+((b>>sh&255)*t));
  return "#"+((1<<24)+(ch(16)<<16)+(ch(8)<<8)+ch(0)).toString(16).slice(1);
}
const STROKEF = RAMPF.map(c=>mix(c, INK, .25));
const STROKEC = RAMPC.map(c=>mix(c, INK, .25));

function el(tag, attrs, kids){
  const e = document.createElement(tag);
  for(const k in (attrs||{})) e.setAttribute(k, attrs[k]);
  (kids||[]).forEach(k=>e.appendChild(typeof k==="string"?document.createTextNode(k):k));
  return e;
}
const total = DATA.systems.length;

/* ---- header ---- */
document.getElementById("stamp").textContent =
  DATA.head + " · " + DATA.generated + " · " + total + " systems registered";
(function(){
  const sw = document.getElementById("rampSw");
  RAMPF.forEach(c=>sw.appendChild(el("i",{style:"background:"+c})));
})();

/* ---- tile strip ---- */
(function(){
  const t = document.getElementById("tiles");
  const n = k => DATA.functionCounts[k]||0;
  const c = k => DATA.contentCounts[k]||0;
  const runnablePlus = n("runnable")+n("validated")+n("played");
  const validatedPlus = n("validated")+n("played");
  const authoredPlus = c("authored")+c("final");
  const blocked = DATA.systems.filter(s=>flag(s)==="blocked").length;
  const awaiting = DATA.systems.filter(s=>flag(s)==="awaiting").length;
  const gs = DATA.goalSheet, cr = DATA.codeReview, lg = DATA.ledger||{};
  const done = DATA.systems.filter(s=>s.done).length;
  function tile(v, sub, label, cls){
    const d = el("div", {"class":"tile"+(cls?" "+cls:"")});
    const vv = el("div", {"class":"v"}, [String(v)]);
    if(sub) vv.appendChild(el("small", {}, [" "+sub]));
    d.appendChild(vv); d.appendChild(el("div", {"class":"l"}, [label]));
    return d;
  }
  t.appendChild(tile(total, "", "systems"));
  t.appendChild(tile(runnablePlus, "/"+total, "proven runnable+", "bright"));
  t.appendChild(tile(validatedPlus, "/"+total, "validated+", "bright"));
  t.appendChild(tile(done, "/"+total, "done (played × final)", done?"green":""));
  t.appendChild(tile(authoredPlus, "/"+total, "content authored+"));
  t.appendChild(tile(blocked, "", "blocked by a bug", blocked?"red":""));
  t.appendChild(tile(awaiting, "", "awaiting your decision", awaiting?"yellow":""));
  t.appendChild(tile(gs.ticked, "/"+gs.total, "goal-sheet boxes"));
  t.appendChild(tile(cr.clean, "/"+cr.total, "files review-clean", ""));
  t.appendChild(tile((lg.openItems!=null?lg.openItems:"—"), lg.openBugs!=null?"("+lg.openBugs+" bugs)":"", "open ledger items"));
  t.appendChild(tile((lg.needsOwner!=null?lg.needsOwner:"—"), "", "open items needing you", lg.needsOwner?"yellow":""));
})();

/* ---- ladders ---- */
function renderLadder(mountId, counts, ladder, ramp){
  const mount = document.getElementById(mountId);
  mount.innerHTML = "";
  /* most-mature first, so every vertical read on the page runs the same way
     as the matrix: light brown (done) at the top, dark (beginning) below */
  ladder.slice().reverse().forEach((rung, ri)=>{
    const i = ladder.length - 1 - ri;
    const n = counts[rung] || 0;
    const pct = total ? Math.round(100*n/total) : 0;
    const row = el("div", {"class":"rungrow"});
    row.appendChild(el("b", {}, [rung]));
    const bg = el("div", {"class":"barbg"});
    bg.appendChild(el("div", {"class":"barfg", "style":"width:"+pct+"%;background:"+ramp[i]}));
    row.appendChild(bg);
    const cnt = el("span", {"class":"cnt"});
    const b = document.createElement("b"); b.textContent = n;
    cnt.appendChild(b); cnt.appendChild(document.createTextNode(" · "+pct+"%"));
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
renderLadder("functionBars", DATA.functionCounts, FLADDER, RAMPF);
renderLadder("contentBars", DATA.contentCounts, CLADDER, RAMPC);
document.getElementById("functionWeight").textContent =
  DATA.weighting + " — “done” is played AND final on the same system.";

/* ---- tier rollup: one 100% stacked bar per tier, segments = function rungs ---- */
(function(){
  const mount = document.getElementById("tierRoll");
  ["RimMandrake","RimStarWars","RimUtinni"].forEach(tier=>{
    const rows = DATA.systems.filter(s=>s.tier===tier);
    if(!rows.length) return;
    const row = el("div", {"class":"stackrow"});
    const b = el("b", {});
    b.appendChild(el("span", {"class":"tiermark", style:"background:"+TIERCOL[tier]}));
    b.appendChild(document.createTextNode(tier.replace("Rim","")));
    row.appendChild(b);
    const stack = el("div", {"class":"stack"});
    FLADDER.forEach((rung,i)=>{
      const n = rows.filter(s=>s.functionRung===rung).length;
      if(n) stack.appendChild(el("i", {style:"width:"+(100*n/rows.length)+"%;background:"+RAMPF[i],
        title:rung+": "+n}));
    });
    row.appendChild(stack);
    row.appendChild(el("span", {"class":"cnt mono", style:"text-align:right;color:var(--dim);font-size:10.5px"},
      [String(rows.length)]));
    mount.appendChild(row);
  });
})();

/* ---- matrix with marginals ---- */
document.getElementById("gridN").textContent =
  total + " systems · rows: function · columns: content";
(function(){
  const wrap = document.getElementById("gridWrap");
  if(total === 0){ wrap.appendChild(el("div",{"class":"empty"},["No systems registered yet."])); return; }
  const hasUnset = DATA.systems.some(s=>!s.functionRung||!s.contentRung);
  const rows = FLADDER.slice().reverse().concat(hasUnset?["unset"]:[]);
  const cols = CLADDER.concat(hasUnset?["unset"]:[]);
  const table = el("table", {"class":"grid"});
  const thead = el("tr", {}, [el("th", {"class":"corner"}, ["function \\ content"])]
    .concat(cols.map(c=>el("th", {}, [c]))).concat([el("th",{"class":"marg"},["Σ"])]));
  table.appendChild(thead);
  const colTot = {};
  rows.forEach(fr=>{
    const tr = el("tr");
    tr.appendChild(el("th", {}, [fr]));
    let rowTot = 0;
    cols.forEach(cr=>{
      const list = ((DATA.grid[fr] && DATA.grid[fr][cr]) || []).slice()
        .sort((a,b)=>{
          const sa = BYSYS[a]||{}, sb = BYSYS[b]||{};
          return (TIERORD[sa.tier||""]-TIERORD[sb.tier||""])
              || (sa.label||a).localeCompare(sb.label||b);
        });
      rowTot += list.length; colTot[cr] = (colTot[cr]||0) + list.length;
      const isDone = fr==="played" && cr==="final" && list.length;
      const td = el("td", {"class": list.length ? "cell"+(isDone?" done":"") : "cell zero"});
      if(list.length){
        td.appendChild(el("div", {"class":"cellcount"}, [String(list.length)]));
        list.forEach(name=>{
          const s = BYSYS[name] || {label:name, tier:""};
          const st = flag(s);
          const fi = fIdx(s), ci = cIdx(s);
          const chip = el("span", {"class":"chip2"+(st?" "+st:""), "data-sys":name,
            style: st ? "" : "border-left-color:"+TIERCOL[s.tier||""]});
          const fillCol = st==="blocked" ? RED : st==="awaiting" ? YELLOW : RAMPF[Math.max(0,fi)];
          const w = st ? 100 : Math.round(100*(fi+1)/FLADDER.length);
          chip.appendChild(el("i", {"class":"fill",
            style:"width:"+w+"%;background:"+fillCol+";opacity:"+(st?".30":".45")}));
          if(ci >= 0) chip.appendChild(el("i", {"class":"cfill",
            style:"width:"+Math.round(100*(ci+1)/CLADDER.length)+"%;background:"+RAMPC[ci]}));
          const lbl = el("span", {"class":"lbl"});
          if(st) lbl.appendChild(el("span", {"class":"g"}, [st==="blocked"?"✖":"?"]));
          lbl.appendChild(document.createTextNode(s.label||name));
          chip.appendChild(lbl);
          td.appendChild(chip);
        });
      } else { td.textContent = "·"; }
      tr.appendChild(td);
    });
    tr.appendChild(el("td", {"class":"marg"}, [String(rowTot)]));
    table.appendChild(tr);
  });
  const tf = el("tr", {}, [el("th", {"class":"marg"}, ["Σ"])]
    .concat(cols.map(c=>el("td", {"class":"marg"}, [String(colTot[c]||0)])))
    .concat([el("td", {"class":"marg"}, [String(total)])]));
  table.appendChild(tf);
  wrap.appendChild(table);
  requestAnimationFrame(()=>{ if(wrap.scrollWidth > wrap.clientWidth + 4) document.getElementById("gridScrollHint").style.display="block"; });
})();

/* ---- roster: filter + sort ---- */
(function(){
  const t = document.getElementById("sysTable");
  const controls = document.getElementById("rosterControls");
  if(total === 0){
    t.parentNode.replaceChild(el("div",{"class":"empty"},["Registry is empty."]), t);
    return;
  }
  const state = {q:"", tier:null, flagged:false, sort:"name", dir:1};
  const search = el("input", {type:"search", placeholder:"filter systems…"});
  search.addEventListener("input", ()=>{ state.q = search.value.toLowerCase(); render(); });
  controls.appendChild(search);
  ["RimMandrake","RimStarWars","RimUtinni"].forEach(tier=>{
    const b = el("button", {"class":"fbtn"});
    b.appendChild(el("span", {"class":"dot", style:"background:"+TIERCOL[tier]}));
    b.appendChild(document.createTextNode(tier.replace("Rim","")));
    b.addEventListener("click", ()=>{
      state.tier = state.tier===tier ? null : tier;
      controls.querySelectorAll(".fbtn").forEach(x=>x.classList.remove("on"));
      if(state.tier) b.classList.add("on");
      render();
    });
    controls.appendChild(b);
  });
  const fb = el("button", {"class":"fbtn"}, ["✖/? only flagged"]);
  fb.addEventListener("click", ()=>{ state.flagged=!state.flagged; fb.classList.toggle("on"); render(); });
  controls.appendChild(fb);

  const days = s => {
    if(!s.date) return null;
    const d = Math.round((Date.parse(DATA.generated.slice(0,10)) - Date.parse(s.date))/864e5);
    return isNaN(d) ? null : d;
  };
  const SORTS = {
    name:  (a,b)=>(a.label||a.system).localeCompare(b.label||b.system),
    tier:  (a,b)=>(TIERORD[a.tier||""]-TIERORD[b.tier||""])||SORTS.name(a,b),
    status:(a,b)=>((flag(b)==="blocked")-(flag(a)==="blocked"))||((flag(b)==="awaiting")-(flag(a)==="awaiting"))||SORTS.name(a,b),
    fn:    (a,b)=>(fIdx(b)-fIdx(a))||SORTS.name(a,b),
    ct:    (a,b)=>(cIdx(b)-cIdx(a))||SORTS.name(a,b),
    age:   (a,b)=>((days(a)==null)-(days(b)==null))||((days(b)||0)-(days(a)||0))||SORTS.name(a,b),
  };
  function meter(idx, steps, ramp){
    const m = el("span", {"class":"meter"});
    for(let i=0;i<steps;i++)
      m.appendChild(el("i", {style: i<=idx ? "background:"+ramp[i]+";border-color:"+ramp[i] : ""}));
    return m;
  }
  function render(){
    t.innerHTML = "";
    const head = el("tr");
    [["name","name"],["tier","tier"],["status","status"],["fn","function"],["ct","content"],
     ["age","evidence age"],[null,"evidence"]].forEach(([key,label])=>{
      const th = el("th", {}, [label + (key===state.sort ? (state.dir>0?" ▾":" ▴") : "")]);
      if(key) th.addEventListener("click", ()=>{
        state.dir = state.sort===key ? -state.dir : 1; state.sort = key; render();
      });
      head.appendChild(th);
    });
    t.appendChild(head);
    let rows = DATA.systems.slice();
    if(state.q) rows = rows.filter(s=>((s.label||"")+" "+s.system+" "+(s.blurb||"")).toLowerCase().includes(state.q));
    if(state.tier) rows = rows.filter(s=>s.tier===state.tier);
    if(state.flagged) rows = rows.filter(s=>flag(s));
    rows.sort(SORTS[state.sort]); if(state.dir<0) rows.reverse();
    document.getElementById("rosterN").textContent =
      rows.length===total ? total+" systems" : rows.length+" of "+total+" shown";
    rows.forEach(s=>{
      const st = flag(s);
      const tr = el("tr", {"data-sys":s.system});
      const nameTd = el("td", {style:"font-weight:600"});
      nameTd.appendChild(el("span", {"class":"tiermark", style:"background:"+TIERCOL[s.tier||""]}));
      nameTd.appendChild(document.createTextNode(s.label || s.system));
      tr.appendChild(nameTd);
      tr.appendChild(el("td", {style:"color:var(--dim);font-size:10.5px"}, [(s.tier||"?").replace("Rim","")]));
      const stTd = el("td");
      if(s.done) stTd.appendChild(el("span",{"class":"tag done"},["DONE"]));
      else if(st==="blocked") stTd.appendChild(el("span",{"class":"tag blocked"},["✖ "+s.blocked.length+" bug"+(s.blocked.length>1?"s":"")]));
      else if(st==="awaiting") stTd.appendChild(el("span",{"class":"tag awaiting"},["? decision"]));
      tr.appendChild(stTd);
      const fnTd = el("td");
      fnTd.appendChild(meter(fIdx(s), 6, RAMPF));
      fnTd.appendChild(el("span", {"class":"rungword"}, [s.functionRung||"—"]));
      tr.appendChild(fnTd);
      const ctTd = el("td");
      ctTd.appendChild(meter(cIdx(s), 4, RAMPC));
      ctTd.appendChild(el("span", {"class":"rungword"}, [s.contentRung||"—"]));
      tr.appendChild(ctTd);
      const d = days(s);
      tr.appendChild(el("td", {}, [el("span", {"class":"age"+(d!=null&&d>14?" stale":"")},
        [d==null?"—":(d+"d")])]));
      tr.appendChild(el("td", {"class":"ev", title:s.evidenceRef||""}, [s.evidenceRef||"—"]));
      t.appendChild(tr);
    });
  }
  render();
})();

/* ---- movement feed ---- */
(function(){
  const mount = document.getElementById("movement");
  const mv = DATA.movement||[];
  if(!mv.length){ mount.appendChild(el("div",{"class":"empty"},["No capability events yet."])); return; }
  mv.forEach(m=>{
    const s = BYSYS[m.system];
    const row = el("div", s ? {"class":"mrow", "data-sys": m.system} : {"class":"mrow"});
    row.appendChild(el("span", {"class":"mts"}, [(m.ts||"").slice(5,16).replace("T"," ")]));
    row.appendChild(el("span", {style:"overflow:hidden;text-overflow:ellipsis;white-space:nowrap"},
      [(s&&s.label)||m.system]));
    const to = el("span", {"class":"mto"});
    if(m.retired){ to.textContent = "retired"; to.style.color = "var(--dim)"; }
    else {
      const parts = [];
      if(m.functionRung) parts.push("→ "+m.functionRung);
      if(m.contentRung) parts.push("→ "+m.contentRung+" (content)");
      to.textContent = parts.join("  ") || "note";
      const i = FLADDER.indexOf(m.functionRung);
      if(i>=0) to.style.color = STROKEF[i];
    }
    row.appendChild(to);
    mount.appendChild(row);
  });
})();

/* ---- regression: a small hand-rolled step chart, no library ---- */
function drawRegression(svgId, legId, snaps, ladder, strokes, field){
  const svg = document.getElementById(svgId);
  const leg = document.getElementById(legId);
  if(!snaps.length){
    svg.replaceWith(el("div", {"class":"empty"}, ["No capability events yet."]));
    return;
  }
  const W = svg.clientWidth || 560, H = 190, padL = 26, padR = 34, padT = 8, padB = 20;
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
  svg.appendChild(mk("line", {x1:padL,y1:H-padB,x2:W-padR,y2:H-padB,stroke:"#332a20"}));
  svg.appendChild(mk("line", {x1:padL,y1:padT,x2:padL,y2:H-padB,stroke:"#332a20"}));
  [0, Math.ceil(maxY/2), maxY].forEach(v=>{
    const t = mk("text", {x:2, y:y(v)+3, fill:"#a99d89", "font-size":"9"});
    t.textContent = v; svg.appendChild(t);
  });
  ladder.forEach((rung, li)=>{
    let dstr = "";
    snaps.forEach((s,i)=>{
      dstr += (i? " L":"M") + x(i).toFixed(1) + " " + y(s[field][rung]||0).toFixed(1);
    });
    svg.appendChild(mk("path", {d:dstr, fill:"none", stroke:strokes[li], "stroke-width":2}));
    const last = snaps[snaps.length-1][field][rung]||0;
    if(last){
      const t = mk("text", {x:W-padR+4, y:y(last)+3, fill:strokes[li], "font-size":"9",
        "font-family":"IBM Plex Mono"});
      t.textContent = last; svg.appendChild(t);
    }
    const sp = el("span");
    sp.appendChild(el("i", {style:"background:"+strokes[li]}));
    sp.appendChild(document.createTextNode(rung+" ("+last+")"));
    leg.appendChild(sp);
  });
}
drawRegression("regFunction", "legFunction", DATA.regression, FLADDER, STROKEF, "function");
drawRegression("regContent", "legContent", DATA.regression, CLADDER, STROKEC, "content");

/* ---- goal sheet ---- */
(function(){
  const gs = DATA.goalSheet, mount = document.getElementById("goalSheet");
  if(!gs.ok && !gs.sections.length){
    mount.appendChild(el("div",{"class":"empty"},["GOAL_SHEET.md not found."])); return;
  }
  document.getElementById("gsN").textContent =
    gs.ticked+"/"+gs.total+" boxes ticked — GOAL_SHEET.md, as-is";
  gs.sections.forEach(sec=>{
    const row = el("div", {"class":"gsrow"});
    if(sec.items && sec.items.length)
      row.title = sec.items.map(it=>(it.ticked?"☑ ":"☐ ")+it.text).join("\n");
    row.appendChild(el("span", {style:"overflow:hidden;text-overflow:ellipsis;white-space:nowrap"},
      [sec.n+". "+sec.title]));
    const bg = el("div", {"class":"barbg"});
    const pct = sec.total ? Math.round(100*sec.ticked/sec.total) : 0;
    bg.appendChild(el("div", {"class":"barfg", style:"width:"+pct+"%;background:#c49a5d"}));
    row.appendChild(bg);
    row.appendChild(el("span", {"class":"cnt mono", style:"text-align:right;color:var(--dim);font-size:10px"},
      [sec.ticked+"/"+sec.total]));
    mount.appendChild(row);
  });
})();

/* ---- code review tile ---- */
(function(){
  const cr = DATA.codeReview, mount = document.getElementById("crTiles");
  function tile(v,label,cls){
    const d = el("div", {"class":"tile"+(cls?" "+cls:"")});
    d.appendChild(el("div", {"class":"v"}, [String(v)]));
    d.appendChild(el("div", {"class":"l"}, [label]));
    return d;
  }
  mount.appendChild(tile(cr.clean, "clean", "green"));
  mount.appendChild(tile(cr.dirty, "dirty", cr.dirty?"":"green"));
  mount.appendChild(tile(cr.recidivists, "clean→dirty again"));
  if(cr.unknown) mount.appendChild(tile(cr.unknown, "unknown state", "red"));
  mount.appendChild(tile(cr.total, "recorded"));
  const dl = document.getElementById("dirtyList");
  (cr.dirtyPaths||[]).forEach(p=>dl.appendChild(el("div", {"class":"mono", title:p}, [p])));
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
       +(s.functionRung||"—")+" × "+(s.contentRung||"—")
       +(s.updatedAt?" · set "+s.updatedAt.slice(0,10)+(s.updatedBy?" by "+s.updatedBy:""):"")]));
    tip.appendChild(el("div", {"class":"d"},
      [s.blurb || "No description in this mod's About.xml yet."]));
    if(s.blocked && s.blocked.length)
      tip.appendChild(el("div", {"class":"flag blocked"},
        ["✖ blocked by: "+s.blocked.join(", ")]));
    if(s.awaiting && s.awaiting.length)
      tip.appendChild(el("div", {"class":"flag awaiting"},
        ["? awaiting your decision: "+s.awaiting.join(", ")]));
    if(s.evidenceRef) tip.appendChild(el("div", {"class":"e"},
      ["evidence"+(s.date?" ("+s.date+")":"")+": "+s.evidenceRef]));
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
    flags, ledger_counts = system_flags(world, systems)
    for s in systems:
        f = flags.get(s["system"], {})
        s["blocked"] = f.get("blocked", [])
        s["awaiting"] = f.get("awaiting", [])

    movement = [{"ts": ev.get("ts"), "system": ev.get("system"),
                 "functionRung": ev.get("function_rung"),
                 "contentRung": ev.get("content_rung"),
                 "retired": bool(ev.get("retired")), "seat": ev.get("seat")}
                for ev in cap_events[-40:]][::-1]

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
        "ledger": ledger_counts,
        "movement": movement,
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
