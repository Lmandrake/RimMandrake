#!/usr/bin/env python3
"""make_verdict_sheet.py — generates the owner's formal accept/reject review
sheet for every `awaiting_verdict` lane in the art registry
(`infrastructure/artpipe/registry.jsonl`, owned solely by `artreg.py`).

This script is READ-ONLY against the registry and the art pipeline's
`done/`/`_artsrc/` directories. It writes exactly one file:
`Transient/art_verdict_sheet_<DATE>.html`. It never calls `artreg.py verdict`
and never touches `registry.jsonl` — that is `apply_verdicts.py`'s job, and
`artreg.py` is that file's SOLE writer regardless.

Ground truth read before writing this (see infrastructure/artpipe/README.md):
  - a lane is a `target` (`<asset_key>/<facing>`, or bare `<asset_key>` when
    the job has no facing); state is DERIVED by replaying registry.jsonl,
    never hand-parsed here — this script calls `artreg.build_status()`
    directly so it can never disagree with `artreg.py status`.
  - the regenerated PNG for a target's current job lives at
    `infrastructure/artpipe/_artsrc/<job_id>/<job_id>.png` (confirmed by
    reading `done/<job_id>.manifest.json`'s `worker_self_report.out` and by
    listing `_artsrc/` directly).
  - the ORIGINAL a job was regenerated from, if any, is the job json's
    `reference` field (absolute path). Measured 2026-09-11 across all 147
    awaiting_verdict lanes: 141 carry `reference: null` (full "redo"/"improve"
    regenerations per the README's redo semantics — there is no 1:1 original
    to compare, often not even the same creature identity) and 6 carry a
    real loose-file path (the `lockjaw_improve_*` lanes, all 6 confirmed
    present on disk under the Steam workshop Textures folder — none of the
    6 required the AssetBundle fallback). The AssetBundle-unavailable path
    below is implemented and will fire on any FUTURE lane whose `reference`
    names a file that does not resolve as a loose PNG; it is inert on today's
    147, which is the honest, checked state — not a guess.
"""
from __future__ import annotations

import base64
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artreg  # noqa: E402
import common  # noqa: E402

try:
    from PIL import Image
except ImportError:
    print("make_verdict_sheet: PIL (Pillow) is required — pip install pillow", file=sys.stderr)
    raise

OUT_HTML = common.REPO_ROOT / "Transient" / "art_verdict_sheet_2026-09-12.html"
THUMB_MAX_SIDE = 256  # per the task spec: thumbnail if the self-contained page would be huge
# ORIGINALs get a smaller cap than regenerated art: with 89 lanes now carrying a
# current-in-game-texture original (see ORIGINALS_DIR below), 256px on both
# images pushed the self-contained page to 15.8MB — over the 14MB budget.
# 160px keeps every original comparable at a glance (still NEAREST, never
# smoothed) and brings the page back under budget with headroom.
ORIGINAL_THUMB_MAX_SIDE = 160

# Originals resolved from the LIVE deployed texture (loose PNG or extracted
# AssetBundle cache) for lanes whose job carries `reference: null` — see
# infrastructure/artpipe/README.md and skills/reading-rimworld-graphics.
# Populated by a one-shot offline resolver (not part of this script); keyed
# by the exact `target` string, mirroring done/*.json's own keying, so a
# target with a facing ("dactillion/east") nests as ORIGINALS_DIR/dactillion/
# east.png. `_unresolved.json` sits alongside with a one-line reason per
# lane this resolver could not find a current in-game texture for (mostly:
# no matching ThingDef/PawnKindDef in the def dump — a new/commissioned
# creature or test template with nothing to compare against).
ORIGINALS_DIR = common.REPO_ROOT / "Transient" / "art_verdict_originals"
UNRESOLVED_PATH = ORIGINALS_DIR / "_unresolved.json"
UNRESOLVED_REASONS: dict[str, str] = (
    json.loads(UNRESOLVED_PATH.read_text()) if UNRESOLVED_PATH.is_file() else {}
)


# --------------------------------------------------------------------------
# path display — the owner reads this sheet; native Windows paths for /mnt/c
# and /mnt/d, per project convention (CLAUDE.md "always give full paths").
# --------------------------------------------------------------------------

def to_windows_path(p: str) -> str:
    m = re.match(r"^/mnt/([a-z])/(.*)$", p)
    if not m:
        return p
    drive, rest = m.group(1).upper(), m.group(2)
    return f"{drive}:\\" + rest.replace("/", "\\")


# --------------------------------------------------------------------------
# creature grouping — target stem, with the lockjaw retry/facing-suffix
# naming quirk normalized so the three lockjaw_improve_a lanes (one bare,
# one "/north", one "lockjaw_improve_a_r13_south" — a retry id that ended up
# AS the target itself rather than a facing) land in one group. Checked
# against all 147 live targets: this normalization changes grouping for
# exactly lockjaw_improve_a/b and nothing else (51 groups vs 52 naive).
# --------------------------------------------------------------------------

_RETRY_SUFFIX_RE = re.compile(r"_r\d+(_[a-z]+)?$")


def creature_of(target: str) -> str:
    stem = target.split("/")[0]
    return _RETRY_SUFFIX_RE.sub("", stem)


def facing_of(target: str) -> str | None:
    parts = target.split("/", 1)
    return parts[1] if len(parts) == 2 else None


# --------------------------------------------------------------------------
# image handling
# --------------------------------------------------------------------------

def thumbnail_data_uri(path: Path, max_side: int = THUMB_MAX_SIDE) -> tuple[str, int, int, int]:
    """Returns (data_uri, orig_w, orig_h, bytes_embedded). Pixel-preserving
    NEAREST resample (never smoothed) capped at `max_side` per side; images
    already smaller are re-saved as-is (no upscaling)."""
    with Image.open(path) as im:
        im = im.convert("RGBA")
        w, h = im.size
        scale = min(1.0, max_side / max(w, h))
        if scale < 1.0:
            im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.NEAREST)
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        data = buf.getvalue()
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:image/png;base64,{b64}", w, h, len(data)


def resolve_original(reference: str | None, target: str) -> dict:
    """{"status": "none"|"found"|"unavailable_bundle", "path": str|None,
    "windows_path": str|None, "source": "job_reference"|"current_texture"|None,
    "unresolved_reason": str|None}

    Two sources, tried in order:
      1. the job's own `reference` field (a redo/improve lane compared against
         the specific file it was regenerated from).
      2. when that is null, the creature's CURRENT in-game texture, resolved
         offline (see ORIGINALS_DIR above) — the original a full "redo" lane
         still has, even though its own job never recorded one.
    """
    if reference:
        p = Path(reference)
        if p.is_file():
            return {"status": "found", "path": reference,
                     "windows_path": to_windows_path(reference), "source": "job_reference",
                     "unresolved_reason": None}
        # Unreachable as a loose file — per the task spec, this is the
        # AssetBundle (or otherwise-missing) case. Never guess a substitute.
        return {"status": "unavailable_bundle", "path": reference,
                "windows_path": to_windows_path(reference), "source": "job_reference",
                "unresolved_reason": None}

    current = ORIGINALS_DIR / f"{target}.png"
    if current.is_file():
        cp = str(current)
        return {"status": "found", "path": cp, "windows_path": to_windows_path(cp),
                "source": "current_texture", "unresolved_reason": None}
    return {"status": "none", "path": None, "windows_path": None, "source": None,
            "unresolved_reason": UNRESOLVED_REASONS.get(target)}


# --------------------------------------------------------------------------
# build the row data
# --------------------------------------------------------------------------

def build_rows() -> list[dict]:
    status = artreg.build_status()
    per_target = status["perTarget"]
    awaiting = {t: v for t, v in per_target.items() if v.get("state") == "awaiting_verdict"}

    rows = []
    stats = {"originals_found": 0, "originals_none": 0, "originals_unavailable": 0,
              "originals_found_job_reference": 0, "originals_found_current_texture": 0}
    for target in sorted(awaiting):
        info = awaiting[target]
        job_ids = info.get("job_ids") or []
        if not job_ids:
            print(f"make_verdict_sheet: WARNING {target!r} has no job_ids — skipped",
                  file=sys.stderr)
            continue
        job_id = job_ids[-1]
        job_path = common.DEFAULT_DONE / f"{job_id}.json"
        manifest_path = common.DEFAULT_DONE / f"{job_id}.manifest.json"
        if not job_path.is_file():
            print(f"make_verdict_sheet: WARNING {target!r} job {job_id!r} has no "
                  f"done/{job_id}.json — skipped", file=sys.stderr)
            continue
        job = json.loads(job_path.read_text())
        manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}

        regen_path = common.DEFAULT_ARTSRC / job_id / f"{job_id}.png"
        if not regen_path.is_file():
            print(f"make_verdict_sheet: WARNING {target!r} job {job_id!r} regenerated PNG "
                  f"missing at {regen_path} — skipped", file=sys.stderr)
            continue

        regen_uri, rw, rh, rbytes = thumbnail_data_uri(regen_path)

        orig = resolve_original(job.get("reference"), target)
        orig_uri = None
        if orig["status"] == "found":
            try:
                orig_uri, ow, oh, obytes = thumbnail_data_uri(Path(orig["path"]), ORIGINAL_THUMB_MAX_SIDE)
                orig["w"], orig["h"] = ow, oh
            except Exception as exc:  # a found file that PIL can't open is still "found"
                print(f"make_verdict_sheet: WARNING original for {target!r} at "
                      f"{orig['path']!r} could not be opened by PIL ({exc}) — "
                      f"showing regenerated only", file=sys.stderr)
                orig["status"] = "unavailable_bundle"

        if orig["status"] == "found":
            stats["originals_found"] += 1
            if orig["source"] == "current_texture":
                stats["originals_found_current_texture"] += 1
            else:
                stats["originals_found_job_reference"] += 1
        elif orig["status"] == "none":
            stats["originals_none"] += 1
        else:
            stats["originals_unavailable"] += 1

        rows.append({
            "target": target,
            "creature": creature_of(target),
            "facing": facing_of(target),
            "job_id": job_id,
            "iteration": info.get("iteration", 1),
            "renders": info.get("renders", 1),
            "rejected_count": info.get("rejected_count", 0),
            "prompt": job.get("prompt", ""),
            "style_notes": job.get("style_notes", ""),
            "channel": job.get("channel"),
            "regen_uri": regen_uri,
            "regen_w": rw, "regen_h": rh,
            "regen_path": str(regen_path),
            "regen_windows_path": to_windows_path(str(regen_path)),
            "original_status": orig["status"],
            "original_uri": orig_uri,
            "original_path": orig["path"],
            "original_windows_path": orig["windows_path"],
            "original_source": orig["source"],
            "original_unresolved_reason": orig["unresolved_reason"],
            "validator": manifest.get("validator"),
            "validator_findings": manifest.get("validator_findings", []),
        })

    return rows, stats


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------

PAGE_TEMPLATE = r"""<!doctype html>
<title>Art Verdict Sheet — 2026-09-12</title>
<style>
:root {
  --ground:#2A211A; --panel:#362B21; --panel2:#40332772; --ink:#EFE3D0;
  --ink-dim:#C9B79E; --accent:#D98E32; --accept:#4C9A5B; --reject:#B5473A;
  --skip:#6b6157; --border:#4a3c2d;
}
* { box-sizing: border-box; }
body { background: var(--ground); color: var(--ink); font-family: -apple-system, Segoe UI, Arial, sans-serif;
  margin: 0; padding: 0 16px 96px 16px; }
h1 { font-size: 1.3em; margin: 16px 0 4px; color: var(--ink); }
a { color: var(--accent); }
.brief { background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
  padding: 12px 16px; margin: 12px 0; font-size: 0.92em; line-height: 1.5; color: var(--ink-dim); }
.brief b { color: var(--ink); }
.brief .invented { color: var(--accent); font-weight: 600; }
.toolbar { display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin: 10px 0; }
.toolbar input[type=text] { background:#1f1811; border:1px solid var(--border); color:var(--ink);
  border-radius:6px; padding:6px 10px; font-size:0.9em; min-width:220px; }
.toolbar button, .filterbtn { background:#1f1811; color:var(--ink); border:1px solid var(--border);
  border-radius:6px; padding:6px 10px; font-size:0.85em; cursor:pointer; }
.filterbtn.active { border-color: var(--accent); color: var(--accent); }
.creature-group { background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
  margin: 14px 0; overflow: hidden; }
.creature-head { display:flex; justify-content:space-between; align-items:center; gap:12px;
  padding: 10px 14px; background:#3a2d20; cursor:pointer; user-select:none; }
.creature-head h2 { font-size: 1.02em; margin:0; color: var(--ink); }
.creature-head .prog { font-size: 0.82em; color: var(--ink-dim); white-space:nowrap; }
.creature-body { padding: 4px 10px 10px; }
.lane { display:grid; grid-template-columns: 1fr; gap:8px; border-top:1px solid var(--border);
  padding: 12px 4px; }
.lane:first-child { border-top:none; }
.lane.decided-accepted { box-shadow: inset 3px 0 0 var(--accept); }
.lane.decided-rejected { box-shadow: inset 3px 0 0 var(--reject); }
.lane.decided-skipped { box-shadow: inset 3px 0 0 var(--skip); }
.lane-head { display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px; font-size:0.85em;
  color: var(--ink-dim); }
.lane-head .lane-id { color: var(--ink); font-weight:600; }
.badge { display:inline-block; padding:1px 7px; border-radius:10px; font-size:0.78em; margin-left:6px; }
.badge.iter { background:#2c4a33; color:#bfe3c4; }
.badge.rejected { background:#5a2c26; color:#f2c4bd; }
.badge.unavail { background:#5a4a26; color:#f2dfa8; }
.badge.none { background:#333; color:#aaa; }
.images { display:flex; gap:14px; flex-wrap:wrap; align-items:flex-start; }
.imgbox { background:#100c08; border:1px solid var(--border); border-radius:8px; padding:8px;
  text-align:center; flex: 0 0 auto; }
.imgbox .cap { font-size:0.75em; color:var(--ink-dim); margin-top:6px; word-break:break-all; max-width:260px; }
.imgbox img { image-rendering: pixelated; image-rendering: crisp-edges; width:220px; height:220px;
  object-fit:contain; background:#100c08; display:block; }
.imgbox.noart { width:220px; height:220px; display:flex; align-items:center; justify-content:center;
  color:#7a6d5c; font-size:0.82em; padding:0; }
.prompt { font-size:0.8em; color:var(--ink-dim); max-width: 640px; }
.prompt summary { cursor:pointer; color: var(--accent); }
.controls { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.vbtn { padding:7px 16px; border-radius:6px; border:1px solid var(--border); background:#1f1811;
  color: var(--ink); font-weight:600; cursor:pointer; font-size:0.85em; }
.vbtn.accept.active, .vbtn.accept:hover { background: var(--accept); color:#0d150f; border-color:var(--accept); }
.vbtn.reject.active, .vbtn.reject:hover { background: var(--reject); color:#180d0b; border-color:var(--reject); }
.vbtn.skip.active, .vbtn.skip:hover { background: var(--skip); color:#0d0d0c; border-color:var(--skip); }
.note { flex:1; min-width:180px; background:#1f1811; border:1px solid var(--border); color:var(--ink);
  border-radius:6px; padding:6px 10px; font-size:0.85em; }
footer.sticky { position:fixed; left:0; right:0; bottom:0; background: var(--panel); border-top:2px solid var(--accent);
  padding: 10px 18px; display:flex; gap:20px; align-items:center; flex-wrap:wrap; z-index:50; }
footer.sticky .count { font-size:1.05em; font-weight:700; color: var(--ink); }
footer.sticky .sub { font-size:0.85em; color: var(--ink-dim); }
footer.sticky a.dl { background: var(--accent); color:#241a0f; padding:8px 16px; border-radius:6px;
  font-weight:700; text-decoration:none; font-size:0.9em; }
footer.sticky a.dl.stale { opacity:0.55; }
footer.sticky .savedat { font-size:0.78em; color: var(--ink-dim); }
[hidden] { display:none !important; }
</style>

<h1>Art Verdict Sheet — 147 regenerated sprites awaiting owner verdict</h1>
<div class="brief">
  <b>What this is:</b> every lane currently <code>awaiting_verdict</code> in the art registry
  (<code>infrastructure/artpipe/registry.jsonl</code>), grouped by creature. For each lane: the
  ORIGINAL (when one is tracked and reachable as a loose file) and the REGENERATED sprite,
  side by side at equal scale, rendered pixelated (no smoothing) on a dark neutral ground so
  alpha edges read honestly.<br>
  <b>Criterion:</b> none — this sheet ranks nothing and pre-fills nothing. Every lane starts
  undecided; you are the only judge of art quality here.
  <span class="invented">Invented by the generator: nothing.</span> Grouping-by-creature
  normalizes three <code>lockjaw_improve_*</code> retry ids whose facing got baked into the
  job id instead of the target (a naming quirk in the queue, not a judgement call).<br>
  <b>Where the original comes from:</b> 6 lanes (<code>lockjaw_improve_*</code>) carry a real
  job <code>reference</code>, found on disk and shown as-is. For the other 141, whose job
  <code>reference</code> is null (full "redo"/"improve" regenerations — the art may be a
  different creature identity entirely), the ORIGINAL shown is instead the creature's
  <b>current in-game texture</b> — resolved offline from the def dump's
  ThingDef/PawnKindDef&nbsp;→&nbsp;texPath chain and extracted from the live deployed loose
  PNG or AssetBundle cache (never guessed). __ORIGINALS_SUMMARY__<br>
  <b>Buttons:</b> ACCEPT / REJECT / SKIP. SKIP means "not decided yet", not "reject" — a
  skipped lane is left untouched by the applier. Add a note on any lane; it is exported
  verbatim as this lane's <code>notes</code>.<br>
  <b>Saving:</b> every click saves to this browser's local storage immediately AND
  regenerates the download link in the footer below. Nothing is sent anywhere. When you are
  done (or periodically), click <b>Download decisions JSON</b> in the footer and hand that
  file back — <code>apply_verdicts.py</code> reads it and runs <code>artreg.py verdict</code>
  for every ACCEPT/REJECT row.
</div>

<div class="toolbar">
  <input type="text" id="search" placeholder="filter by creature, lane, or prompt text…">
  <button class="filterbtn active" data-filter="all">All</button>
  <button class="filterbtn" data-filter="undecided">Undecided only</button>
  <button class="filterbtn" data-filter="decided">Decided only</button>
  <button class="filterbtn" data-filter="has-original">Has original</button>
  <button class="filterbtn" data-filter="no-original">No original</button>
</div>

<div id="groups"></div>

<footer class="sticky">
  <div class="count" id="footer-count">0 / 0 decided</div>
  <div class="sub" id="footer-breakdown"></div>
  <a class="dl" id="dl-link" download="art_verdicts_2026-09-12.json">Download decisions JSON</a>
  <div class="savedat" id="footer-saved"></div>
</footer>

<script type="application/json" id="ITEMS-DATA">__ITEMS_JSON__</script>
<script>
(function(){
  "use strict";
  const ITEMS = JSON.parse(document.getElementById("ITEMS-DATA").textContent);
  const STORE_KEY = "art_verdict_sheet_2026-09-12";
  const TOTAL = ITEMS.length;

  function loadDecisions(){
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (raw) return JSON.parse(raw);
    } catch(e) { /* private mode / blocked storage — start fresh, never crash */ }
    return {};
  }
  function saveDecisions(d){
    try { localStorage.setItem(STORE_KEY, JSON.stringify(d)); } catch(e) {}
  }
  let decisions = loadDecisions(); // target -> {decision: "accepted"|"rejected"|"skipped", notes: str}

  // ---- group by creature, preserving item order (already sorted by target) ----
  const groups = {};
  const groupOrder = [];
  for (const it of ITEMS) {
    if (!(it.creature in groups)) { groups[it.creature] = []; groupOrder.push(it.creature); }
    groups[it.creature].push(it);
  }

  const groupsEl = document.getElementById("groups");

  function laneRowHtml(it){
    const d = decisions[it.target] || {};
    const dec = d.decision || "";
    const note = d.notes || "";
    let originalHtml;
    if (it.original_status === "found") {
      const label = it.original_source === "current_texture" ? "ORIGINAL — current in-game texture" : "ORIGINAL";
      originalHtml = `<div class="imgbox"><img src="${it.original_uri}" alt="original">
        <div class="cap">${label} ${it.original_w}×${it.original_h}<br>${escapeHtml(it.original_windows_path||"")}</div></div>`;
    } else if (it.original_status === "unavailable_bundle") {
      originalHtml = `<div class="imgbox noart">ORIGINAL: UNAVAILABLE<br>(not a loose file —<br>likely an AssetBundle)<br><span class="cap">${escapeHtml(it.original_windows_path||"")}</span></div>`;
    } else {
      originalHtml = `<div class="imgbox noart">no original found<br><span class="cap">${escapeHtml(it.original_unresolved_reason||"no original tracked")}</span></div>`;
    }
    const badges = []
      .concat(it.iteration ? [`<span class="badge iter">iter ${it.iteration}</span>`] : [])
      .concat(it.rejected_count ? [`<span class="badge rejected">rejected ×${it.rejected_count}</span>`] : [])
      .concat(it.original_status !== "found" ? [`<span class="badge ${it.original_status==='none'?'none':'unavail'}">${it.original_status==='none'?'no original':'original unavailable'}</span>`] : [])
      .join("");
    return `
      <div class="lane ${dec ? 'decided-'+dec : ''}" data-target="${escapeAttr(it.target)}">
        <div class="lane-head">
          <span><span class="lane-id">${escapeHtml(it.target)}</span> ${badges}</span>
          <span>job ${escapeHtml(it.job_id)}${it.channel ? " · "+escapeHtml(it.channel) : ""}</span>
        </div>
        <div class="images">
          ${originalHtml}
          <div class="imgbox"><img src="${it.regen_uri}" alt="regenerated">
            <div class="cap">REGENERATED ${it.regen_w}×${it.regen_h}<br>${escapeHtml(it.regen_windows_path||"")}</div></div>
          <details class="prompt"><summary>prompt / style notes</summary>
            <div><b>prompt:</b> ${escapeHtml(it.prompt||"")}</div>
            ${it.style_notes ? `<div style="margin-top:6px"><b>style notes:</b> ${escapeHtml(it.style_notes)}</div>` : ""}
          </details>
        </div>
        <div class="controls">
          <button class="vbtn accept ${dec==='accepted'?'active':''}" data-act="accepted">ACCEPT</button>
          <button class="vbtn reject ${dec==='rejected'?'active':''}" data-act="rejected">REJECT</button>
          <button class="vbtn skip ${dec==='skipped'?'active':''}" data-act="skipped">SKIP</button>
          <input class="note" type="text" placeholder="optional note…" value="${escapeAttr(note)}">
        </div>
      </div>`;
  }

  function groupProgress(creature){
    const items = groups[creature];
    let done = 0;
    for (const it of items) { if (decisions[it.target] && decisions[it.target].decision) done++; }
    return `${done} / ${items.length}`;
  }

  function render(){
    groupsEl.innerHTML = groupOrder.map(creature => {
      const items = groups[creature];
      return `<div class="creature-group" data-creature="${escapeAttr(creature)}">
        <div class="creature-head">
          <h2>${escapeHtml(creature)} <span style="color:var(--ink-dim);font-weight:400">(${items.length} lane${items.length>1?'s':''})</span></h2>
          <span class="prog">${groupProgress(creature)} decided</span>
        </div>
        <div class="creature-body">${items.map(laneRowHtml).join("")}</div>
      </div>`;
    }).join("");
    wireLanes();
    applyFilter();
    updateFooter();
  }

  function wireLanes(){
    groupsEl.querySelectorAll(".lane").forEach(laneEl => {
      const target = laneEl.getAttribute("data-target");
      laneEl.querySelectorAll(".vbtn").forEach(btn => {
        btn.addEventListener("click", () => {
          const act = btn.getAttribute("data-act");
          const cur = decisions[target] || {};
          const already = cur.decision === act;
          decisions[target] = { decision: already ? "" : act, notes: cur.notes || "" };
          saveDecisions(decisions);
          render(); // re-render to update badges/progress/footer everywhere
        });
      });
      const noteEl = laneEl.querySelector(".note");
      noteEl.addEventListener("input", () => {
        const cur = decisions[target] || {};
        decisions[target] = { decision: cur.decision || "", notes: noteEl.value };
        saveDecisions(decisions);
        updateFooter(); // note edits don't change counts; cheap update only
      });
      noteEl.addEventListener("change", () => rebuildDownload());
    });
    // group header click = collapse/expand
    groupsEl.querySelectorAll(".creature-head").forEach(head => {
      head.addEventListener("click", () => {
        const body = head.parentElement.querySelector(".creature-body");
        body.hidden = !body.hidden;
      });
    });
  }

  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function escapeAttr(s){ return escapeHtml(s); }

  function decidedCount(){
    let n=0, acc=0, rej=0, skip=0;
    for (const it of ITEMS) {
      const d = decisions[it.target];
      if (d && d.decision) {
        n++;
        if (d.decision==='accepted') acc++;
        else if (d.decision==='rejected') rej++;
        else if (d.decision==='skipped') skip++;
      }
    }
    return {n, acc, rej, skip};
  }

  function buildExport(){
    const rows = [];
    for (const it of ITEMS) {
      const d = decisions[it.target];
      if (!d || !d.decision) continue;
      rows.push({
        target: it.target, job_id: it.job_id, decision: d.decision,
        notes: d.notes || ""
      });
    }
    return {
      sheet: "art_verdict_sheet_2026-09-12",
      generated_by: "make_verdict_sheet.py",
      total_lanes: TOTAL,
      exported_at: new Date().toISOString(),
      decisions: rows
    };
  }

  function rebuildDownload(){
    const payload = buildExport();
    const json = JSON.stringify(payload, null, 2);
    const uri = "data:application/json;charset=utf-8," + encodeURIComponent(json);
    const link = document.getElementById("dl-link");
    link.href = uri;
    document.getElementById("footer-saved").textContent =
      "decisions saved to this browser's local storage · link refreshed " + new Date().toLocaleTimeString();
  }

  function updateFooter(){
    const {n, acc, rej, skip} = decidedCount();
    document.getElementById("footer-count").textContent = `${n} / ${TOTAL} decided`;
    document.getElementById("footer-breakdown").textContent =
      `${acc} accept · ${rej} reject · ${skip} skip`;
    rebuildDownload();
  }

  // ---- filter / search ----
  let activeFilter = "all";
  function applyFilter(){
    const q = document.getElementById("search").value.trim().toLowerCase();
    groupsEl.querySelectorAll(".lane").forEach(laneEl => {
      const target = laneEl.getAttribute("data-target");
      const it = ITEMS.find(x => x.target === target);
      const d = decisions[target];
      const decided = !!(d && d.decision);
      let show = true;
      if (activeFilter === "undecided" && decided) show = false;
      if (activeFilter === "decided" && !decided) show = false;
      if (activeFilter === "has-original" && it.original_status !== "found") show = false;
      if (activeFilter === "no-original" && it.original_status === "found") show = false;
      if (q) {
        const hay = (it.creature+" "+it.target+" "+it.prompt).toLowerCase();
        if (!hay.includes(q)) show = false;
      }
      laneEl.hidden = !show;
    });
    // hide empty groups
    groupsEl.querySelectorAll(".creature-group").forEach(g => {
      const anyVisible = Array.from(g.querySelectorAll(".lane")).some(l => !l.hidden);
      g.hidden = !anyVisible;
    });
  }

  document.querySelectorAll(".filterbtn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filterbtn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeFilter = btn.getAttribute("data-filter");
      applyFilter();
    });
  });
  document.getElementById("search").addEventListener("input", applyFilter);

  render();
})();
</script>
"""


def main() -> int:
    rows, stats = build_rows()
    if len(rows) != 147:
        print(f"make_verdict_sheet: NOTE built {len(rows)} rows (expected 147 at the time "
              f"this script was written — the registry may have moved since)", file=sys.stderr)

    originals_summary = (
        f"<b>{stats['originals_found_current_texture']} of {len(rows) - 6} redo/improve lanes</b> "
        f"now show that current texture; <b>{stats['originals_none']}</b> have no matching "
        f"ThingDef/PawnKindDef in the def dump at all (new/commissioned creature or test "
        f"template — a one-line reason is shown on the lane)."
    )
    items_json = json.dumps(rows, indent=None, separators=(",", ":"))
    html = PAGE_TEMPLATE.replace("__ITEMS_JSON__", items_json)
    html = html.replace("__ORIGINALS_SUMMARY__", originals_summary)

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")

    size = OUT_HTML.stat().st_size
    print(f"wrote {OUT_HTML} ({size:,} bytes, {size/1e6:.2f} MB)")
    print(f"lanes on sheet: {len(rows)}")
    print(f"originals found: {stats['originals_found']} "
          f"(job reference: {stats['originals_found_job_reference']}, "
          f"current in-game texture: {stats['originals_found_current_texture']}) · "
          f"no original found: {stats['originals_none']} · "
          f"unavailable (bundle): {stats['originals_unavailable']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
