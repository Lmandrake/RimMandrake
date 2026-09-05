#!/usr/bin/env python3
"""codebase_health.py — a picture of what in this repo is reviewed, in flight,
untouched, or known-broken. Two layouts over the same data: a squarified
treemap and a Voronoi treemap.

    python3 src/RimMandrake/Utils/codebase_health.py                 # writes Transient/codebase_health.html
    python3 src/RimMandrake/Utils/codebase_health.py --docs          # include .md/.txt/.csv/.json too
    python3 src/RimMandrake/Utils/codebase_health.py --json-only     # data only, no page

WHAT A COLOUR MEANS
===================
Every leaf is one file, sized by its line count. Exactly one colour is
assigned, by this precedence — the FIRST rule that matches wins:

  1. RED   "known error or bug"
           The file is named, by path, in the prose or ledger text of an OPEN
           rimflow item whose `kind` is `bug`, `defect` or `fix`. Red beats
           everything: a file that is both review-clean and named by an open
           bug is RED.

  2. BLUE  "in dev"
           The file has uncommitted changes in the working tree (modified,
           staged, or untracked-but-not-ignored), OR it is named by an open
           rimflow item whose state is `doing`.

  3. GREEN "clean"
           `CODE_REVIEW_STATUS.json` records a clean mark for this exact path
           and git reports zero commits against it since the recorded sha.
           This is read through the `code_review_status` module — its own
           `load()` and `commits_since()` — never by hand-parsing the JSON.

  4. GREY  "dirty" — the default, and per CLAUDE.md the correct answer for
           almost every file. No review entry at all, or commits since one.
           Grey is a MEASURED verdict, not a shrug.

  5. HATCHED / UNMEASURED
           Status could not be determined. Reserved and visibly distinct so it
           is never mistaken for grey. Fires when git refuses to answer for a
           path, when a review entry names a sha that no longer resolves (the
           log is stale), or when the file cannot be decoded as text and so
           cannot be sized by lines.

HOW A FILE GETS NAMED BY AN ITEM
================================
rimflow items carry no path field, so paths are EXTRACTED from the item's
title, its ledger event text (`spec`, `text`, `reason`, `note`) and the
DESCRIPTIVE sections of `infrastructure/state/items/<ID>.md`. The procedural
sections — `verify`, `criteria`, `watch out`, `prove it`, `validation` — are
skipped on purpose: they name the tool that CHECKS the bug, not the file that
HAS it, and including them painted validate_patch.py and deploy_custom_mods.py
red on someone else's defect. A token counts as naming a file only when it
resolves to a file that actually exists, and is not being INVOKED as a command
(`python3 foo.py`, or `foo.py --flag`) — that is a tool being run, not the
subject of the item. A token counts when it is:

  * an exact repo-relative path, or
  * a path fragment matching exactly one file in the index, or
  * a bare filename owned by exactly one file in the index.

Ambiguous or non-existent tokens name nothing. Directory-only mentions colour
nothing. The generator reports how many open bugs it could not map to any
file — an unmapped bug colours nothing red and is counted, never guessed at.

OUTPUT
======
  Transient/codebase_health.html   self-contained; d3 and the Voronoi plugins
                                   are inlined from src/RimMandrake/Utils/vendor_viz/
  Transient/codebase_health.json   the same data, for anything else to read

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
VENDOR = os.path.join(HERE, "vendor_viz")

sys.path.insert(0, os.path.dirname(HERE))  # src/RimMandrake/, which holds rimflow/
sys.path.insert(0, HERE)

import code_review_status as CRS  # noqa: E402  the authority on CLEAN/DIRTY

CODE_EXT = {
    "py", "cs", "xml", "lua", "sh", "js", "mjs", "ts", "html", "css",
    "csproj", "sln", "rml", "yml", "yaml", "bat", "ps1", "sql",
}
DOC_EXT = {"md", "txt", "csv", "json"}

# Third-party, generated, or not-our-code. Prefix match on the repo-relative path.
EXCLUDE_PREFIXES = (
    "vendor/",
    "Transient/",
    "src/RimMandrake/Utils/vendor_viz/",
    "deployed/",
    ".git/",
    "research/",  # AI-workforce research notes, not reviewed code (owner, 2026-09-04)
    "world/",  # per-session live-bridge provenance scripts, not maintained code — each
               # subdir with a README self-declares "throwaway"/"nothing here is
               # regenerable"; the rest are cited the same way from design docs as
               # docstring-carries-the-reasoning session records (FOUNDRY, 2026-09-04,
               # DIRTY_CODE_REVIEW_LOOP_RESTART_8 follow-on — 211 files, world/_lf/README.md)
    "infrastructure/state/evidence/",  # same pattern: one item's live-measurement
               # scripts + README, kept as the record for a closed item (FOUNDRY, 2026-09-04)
)
EXCLUDE_PARTS = ("__pycache__", "node_modules", "/bin/", "/obj/")

# Item kinds that mean "something is WRONG here", per the ledger's own vocabulary.
BUG_KINDS = ("bug", "defect", "fix")

STATUSES = ("red", "blue", "green", "grey", "unmeasured")


# ---------------------------------------------------------------- git helpers

# Found in the 2026-09-05 code review wave: code_review_status.py added this same
# hard timeout after concurrent review agents were observed hammering .git into
# lock contention and hanging a caller for 10 minutes on this exact shared mount.
# This file's git()/git_z() had no timeout and were exposed to the same hang.
GIT_TIMEOUT = 8  # seconds


def git(args):
    try:
        return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                               text=True, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, -1, "", "git timed out after %ss" % GIT_TIMEOUT)


def git_z(args):
    """Run git with -z output and split on NUL, so paths with spaces survive."""
    r = git(args)
    if r.returncode != 0:
        return None
    return [p for p in r.stdout.split("\0") if p]


def tracked_files():
    out = git_z(["ls-files", "-z"])
    return set(out) if out is not None else None


def working_tree_changes():
    """Repo-relative paths with uncommitted changes: modified, staged, untracked.

    Returns None if git could not be consulted at all — the caller must then
    treat 'in dev' as UNDETERMINED rather than assume False.
    """
    r = git(["status", "--porcelain=1", "-z", "--untracked-files=all"])
    if r.returncode != 0:
        return None
    fields = r.stdout.split("\0")
    paths = set()
    i = 0
    while i < len(fields):
        f = fields[i]
        i += 1
        if len(f) < 4:
            continue
        xy, path = f[:2], f[3:]
        paths.add(path)
        # A rename/copy entry is followed by its source path in the next field.
        if "R" in xy or "C" in xy:
            if i < len(fields):
                paths.add(fields[i])
                i += 1
    return paths


# ------------------------------------------------------------ review status

def review_verdicts(paths):
    """{path: 'clean' | 'dirty' | 'unknown'} via the code_review_status module.

    'unknown' is a real outcome: a legacy entry `migrate-hashes` couldn't
    resolve a hash for. The module's own check() folds both into DIRTY for
    its CLI purpose; here they must stay distinguishable from a measured dirty.

    🔴 ZERO git CALLS, not one per path, not even one bulk walk. This used to
    call `CRS.commits_since()` per path — 526 separate `git log` spawns
    measured 2026-09-04 — then `CRS.commits_since_bulk()` (one history walk
    for all of them). The 2026-09-05 rewrite (owner: "this isn't scaling
    properly, it's a bottleneck") replaced git-history comparison with a
    SHA-256 content-hash comparison — `CRS.clean_state()` is now pure Python,
    so calling it once per path here costs nothing a bulk git walk would have
    saved. See code_review_status.py's own module docstring for the full story.
    """
    log = CRS.load()
    verdicts = {}
    for p in paths:
        entry = log.get(p)
        if entry is None:
            verdicts[p] = "dirty"          # measured: no entry has ever been recorded
            continue
        state, detail = CRS.clean_state(p, entry)
        if state == "CLEAN":
            verdicts[p] = "clean"
        elif entry.get("hash"):
            verdicts[p] = "dirty"          # measured: content differs from the recorded hash
        else:
            verdicts[p] = "unknown"        # legacy entry, no hash ever resolved for it
    return verdicts, log


# ------------------------------------------------------- rimflow item mapping

PATH_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"[A-Za-z0-9_][A-Za-z0-9_./+-]*"
    r"\.(?:py|cs|xml|lua|sh|js|mjs|ts|html|css|csproj|sln|rml|yml|yaml|bat|ps1|sql|md|txt|csv|json)"
    r"(?![A-Za-z0-9_])"
)


# A token used as a COMMAND is a tool being RUN, not the subject of the item.
# `deploy_custom_mods.py --mod Droidworks` in a bug's spec means "and I deployed
# it", not "this deploy script is broken".
INVOKED_BEFORE = re.compile(r"(?:python3?|bash|sh|node|pwsh)\s+$")
INVOKED_AFTER = re.compile(r"^\s+-{1,2}[A-Za-z]")


def is_invocation(blob, start, end):
    return bool(INVOKED_BEFORE.search(blob[max(0, start - 12):start])
                or INVOKED_AFTER.match(blob[end:end + 12]))


def build_index(all_paths):
    by_basename = {}
    by_suffix = {}
    for p in all_paths:
        by_basename.setdefault(os.path.basename(p), []).append(p)
        parts = p.split("/")
        for i in range(1, len(parts)):
            by_suffix.setdefault("/".join(parts[i:]), []).append(p)
    return by_basename, by_suffix


def resolve_token(tok, all_paths, by_basename, by_suffix):
    """A token names a file only if it unambiguously IS one. Else nothing."""
    tok = tok.strip().lstrip("./")
    if not tok:
        return None
    if tok in all_paths:
        return tok
    hits = by_suffix.get(tok)
    if hits and len(hits) == 1:
        return hits[0]
    if "/" not in tok:
        hits = by_basename.get(tok)
        if hits and len(hits) == 1:
            return hits[0]
    return None


# A section that tells you HOW TO CHECK the item names the instrument, not the
# defect. Reading those paints the checker red for the checked file's bug.
HEADING = re.compile(r"^#{1,4}\s+(.+?)\s*$", re.M)
PROCEDURAL = re.compile(r"verif|criteri|watch\s*out|prove\s*it|validat|accept|rollback|"
                        r"how\s*to\s*test|run\s*sheet", re.I)


def descriptive_prose(text):
    """Everything outside the procedural sections of an item's markdown."""
    marks = [(m.start(), m.end(), m.group(1)) for m in HEADING.finditer(text)]
    if not marks:
        return text
    out = [text[:marks[0][0]]]
    for i, (start, end, title) in enumerate(marks):
        stop = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        if not PROCEDURAL.search(title):
            out.append(text[end:stop])
    return "\n".join(out)


def item_texts():
    """{item_id: one big blob of everything DESCRIPTIVE written about it}."""
    blobs = {}
    ledger = os.path.join(ROOT, "infrastructure", "state", "ledger", "events.jsonl")
    if os.path.isfile(ledger):
        with open(ledger, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                iid = ev.get("id")
                if not iid:
                    continue
                chunk = " ".join(
                    str(ev[k]) for k in ("title", "spec", "text", "reason", "note")
                    if ev.get(k)
                )
                if chunk:
                    blobs[iid] = blobs.get(iid, "") + " " + chunk
    items_dir = os.path.join(ROOT, "infrastructure", "state", "items")
    if os.path.isdir(items_dir):
        for name in os.listdir(items_dir):
            if not name.endswith(".md"):
                continue
            iid = name[:-3]
            try:
                with open(os.path.join(items_dir, name), "r", encoding="utf-8",
                          errors="replace") as f:
                    blobs[iid] = blobs.get(iid, "") + " " + descriptive_prose(f.read())
            except OSError:
                pass
    return blobs


def open_item_map(all_paths, by_basename, by_suffix):
    """Returns (bug_files, doing_files, stats) — or (None, None, stats) if the
    ledger could not be replayed, which makes red/blue UNDETERMINED."""
    stats = {"ledgerOk": False, "openItems": 0, "openBugs": 0, "openBugsStrict": 0,
             "bugKinds": list(BUG_KINDS),
             "bugsMapped": 0, "bugsUnmapped": 0, "unmappedBugIds": [],
             "doingItems": 0, "doingMapped": 0}
    try:
        from rimflow import model
        world = model.replay()
    except Exception as exc:                       # noqa: BLE001 — any failure is UNDETERMINED
        stats["error"] = "%s: %s" % (type(exc).__name__, exc)
        return None, None, stats
    stats["ledgerOk"] = True

    blobs = item_texts()
    bug_files, doing_files = {}, {}
    open_items = [i for i in world.items.values() if i.open]
    stats["openItems"] = len(open_items)

    for item in open_items:
        blob = (item.title or "") + " " + blobs.get(item.id, "")
        found = set()
        for m in PATH_TOKEN.finditer(blob):
            if is_invocation(blob, m.start(), m.end()):
                continue
            hit = resolve_token(m.group(0), all_paths, by_basename, by_suffix)
            if hit:
                found.add(hit)
        is_bug = (item.kind in BUG_KINDS)
        if is_bug:
            stats["openBugs"] += 1
            if item.kind == "bug":
                stats["openBugsStrict"] += 1
            if found:
                stats["bugsMapped"] += 1
                for p in found:
                    bug_files.setdefault(p, []).append(item.id)
            else:
                stats["bugsUnmapped"] += 1
                stats["unmappedBugIds"].append(item.id)
        if item.state == "doing":
            stats["doingItems"] += 1
            if found:
                stats["doingMapped"] += 1
                for p in found:
                    doing_files.setdefault(p, []).append(item.id)
    stats["unmappedBugIds"].sort()
    return bug_files, doing_files, stats


# ------------------------------------------------------------------ scanning

def wanted(path, exts):
    for pre in EXCLUDE_PREFIXES:
        if path.startswith(pre):
            return False
    for part in EXCLUDE_PARTS:
        if part in "/" + path:
            return False
    ext = path.rsplit(".", 1)[-1].lower() if "." in os.path.basename(path) else ""
    return ext in exts


def count_lines(abspath):
    """(loc, measured). measured=False means the file could not be read as text."""
    try:
        with open(abspath, "rb") as f:
            raw = f.read()
    except OSError:
        return 0, False
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("latin-1")
        except Exception:                          # noqa: BLE001
            return 0, False
        if b"\0" in raw:
            return 0, False
    if not raw:
        return 0, True
    return len(text.splitlines()), True


# -------------------------------------------------------------------- colours

def classify(path, loc_measured, uncommitted, doing_files, bug_files, verdict,
             wt_known, ledger_known, clean_count=0):
    """`clean_count` is how many times `code_review_status.py mark-clean` has
    ever recorded this exact path (0 if it never has). A file currently grey
    with clean_count > 0 has been reviewed clean before and drifted dirty
    again since — the recidivism the board now surfaces, not just "never
    looked at"."""
    reasons = []
    if ledger_known and path in bug_files:
        return "red", ["open bug item: " + ", ".join(sorted(set(bug_files[path]))[:4])]

    if wt_known and path in uncommitted:
        reasons.append("uncommitted changes in the working tree")
    if ledger_known and path in doing_files:
        reasons.append("open item in `doing`: " + ", ".join(sorted(set(doing_files[path]))[:4]))
    if reasons:
        return "blue", reasons

    if not loc_measured:
        return "unmeasured", ["file could not be decoded as text, so it cannot be sized by lines"]
    if not wt_known:
        return "unmeasured", ["git status could not be read, so 'in dev' is undetermined"]
    if not ledger_known:
        return "unmeasured", ["the rimflow ledger could not be replayed, so bug/doing state is undetermined"]
    if verdict == "clean":
        return "green", ["review recorded clean, zero commits since"]
    if verdict == "unknown":
        return "unmeasured", ["a review entry exists but its recorded sha does not resolve"]
    if clean_count > 0:
        return "grey", ["reviewed and marked clean %d× before — dirty again every time"
                        % clean_count]
    return "grey", ["no review entry has ever been recorded for this path"]


# ----------------------------------------------------------------- tree build

def build_tree(leaves):
    root = {"name": os.path.basename(ROOT) or "repo", "children": [], "_idx": {}}
    for leaf in leaves:
        parts = leaf["path"].split("/")
        node = root
        for part in parts[:-1]:
            child = node["_idx"].get(part)
            if child is None:
                child = {"name": part, "children": [], "_idx": {}}
                node["_idx"][part] = child
                node["children"].append(child)
            node = child
        node["children"].append(leaf)

    def strip(n):
        n.pop("_idx", None)
        for c in n.get("children", ()):
            if "children" in c:
                strip(c)
    strip(root)
    return root


# ---------------------------------------------------------------------- page

def read_vendor(name):
    p = os.path.join(VENDOR, name)
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def write_html(out_path, payload):
    libs = "".join(
        "<script>%s</script>\n" % read_vendor(n) for n in (
            "d3.min.js",
            "d3-weighted-voronoi.min.js",
            "d3-voronoi-map.min.js",
            "d3-voronoi-treemap.min.js",
        )
    )
    data = json.dumps(payload, separators=(",", ":"))
    html = PAGE.replace("/*__LIBS__*/", "").replace("__LIBS__", libs)
    html = html.replace("__DATA__", data)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Codebase Health</title>
<style>
:root{
  --bg:#12141a; --panel:#1a1d26; --line:#2b303d; --ink:#e6e9f0; --dim:#98a0b3;
  --red:#e0483c; --blue:#2f7fd8; --green:#3ea55f; --grey:#79808f; --unk:#c9a227;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);
  font:13px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
#app{display:flex;flex-direction:column;height:100vh}
header{padding:10px 16px;border-bottom:1px solid var(--line);background:var(--panel);
  display:flex;gap:18px;align-items:center;flex-wrap:wrap}
h1{font-size:15px;margin:0;font-weight:650;letter-spacing:.2px}
.sub{color:var(--dim);font-size:11.5px}
.stampRel{font-weight:600}
.stampRel.stale{color:var(--unk)}
.seg{display:flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}
.seg button{background:transparent;color:var(--dim);border:0;padding:5px 13px;
  font:inherit;font-size:12px;cursor:pointer}
.seg button.on{background:#333a4d;color:var(--ink)}
.chip i.hatch{background:repeating-linear-gradient(45deg,#5c4a0d 0 3px,#c9a227 3px 6px)}
.dirhit{cursor:pointer}
.counts{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto}
.chip{display:flex;align-items:center;gap:6px;padding:3px 9px;border-radius:999px;
  border:1px solid var(--line);background:#161923;font-size:11.5px;cursor:pointer;
  user-select:none}
.chip.off{opacity:.35}
.chip i{width:10px;height:10px;border-radius:2px;display:block}
.chip b{font-variant-numeric:tabular-nums}
main{flex:1;display:flex;min-height:0}
#stage{flex:1;position:relative;min-width:0}
svg{display:block;width:100%;height:100%}
aside{width:308px;border-left:1px solid var(--line);background:var(--panel);
  overflow:auto;padding:14px 16px;flex:none}
aside h2{font-size:11px;text-transform:uppercase;letter-spacing:.09em;color:var(--dim);
  margin:0 0 8px}
aside section{margin-bottom:20px}
.rule{display:grid;grid-template-columns:14px 1fr;gap:9px;margin-bottom:9px;
  align-items:start;font-size:11.5px;line-height:1.45}
.rule i{width:12px;height:12px;border-radius:3px;margin-top:3px}
.rule b{display:block;color:var(--ink);font-size:11.5px}
.rule span{color:var(--dim)}
#crumbs{display:flex;gap:5px;align-items:center;flex-wrap:wrap;font-size:12px;
  padding:7px 16px;border-bottom:1px solid var(--line);background:#151822;
  color:var(--dim);min-height:33px}
#crumbs a{color:#8ab4f8;cursor:pointer;text-decoration:none}
#crumbs a:hover{text-decoration:underline}
#tip{position:fixed;pointer-events:none;background:#0b0d12;border:1px solid var(--line);
  border-radius:6px;padding:8px 10px;font-size:11.5px;max-width:400px;opacity:0;
  transition:opacity .08s;z-index:9;box-shadow:0 6px 24px rgba(0,0,0,.6)}
#tip .p{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;
  word-break:break-all;color:#dfe4ef}
#tip .r{color:var(--dim);margin-top:4px}
#busy{position:absolute;inset:0;display:none;align-items:center;justify-content:center;
  background:rgba(18,20,26,.82);font-size:13px;color:var(--dim);z-index:5}
.cell{cursor:pointer}
.lbl{pointer-events:none;font-size:10px;fill:#0d0f14;font-weight:600}
.dlbl{pointer-events:none;font-size:11px;fill:#cfd6e6;font-weight:650;
  letter-spacing:.04em;text-transform:uppercase}
table.n{width:100%;border-collapse:collapse;font-size:11.5px}
table.n td{padding:2px 0;color:var(--dim)}
table.n td:last-child{text-align:right;color:var(--ink);font-variant-numeric:tabular-nums}
.warn{border-left:2px solid var(--unk);padding-left:9px;color:var(--dim);font-size:11.5px}
code{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#c3cbdb}
.recid{display:grid;grid-template-columns:1fr auto;gap:8px;padding:3px 0;font-size:11.5px}
.recid .p{font-family:ui-monospace,Menlo,monospace;color:var(--ink);word-break:break-all}
.recid .c{color:#ff8a5c;font-weight:700;font-variant-numeric:tabular-nums;white-space:nowrap}
.badge{pointer-events:none;font-size:6.5px;font-weight:700;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.6);stroke-width:.7px}
</style></head><body>
<div id="app">
  <header>
    <div><h1>Codebase Health</h1>
      <div class="sub" id="stamp"></div></div>
    <div class="seg">
      <button id="bSq" class="on">Squarified</button>
      <button id="bVo">Voronoi</button>
    </div>
    <div class="counts" id="counts"></div>
  </header>
  <div id="crumbs"></div>
  <main>
    <div id="stage"><svg id="svg"></svg><div id="busy">computing Voronoi tessellation…</div></div>
    <aside>
      <section><h2>Colour, by precedence</h2><div id="legend"></div></section>
      <section><h2>This run</h2><div id="stats"></div></section>
      <section><h2>Unmapped open bugs</h2><div id="unmapped"></div></section>
      <section><h2>Reviewed, dirty again</h2><div id="recid"></div></section>
      <section><h2>Reading it</h2>
        <div class="rule"><i style="background:transparent"></i><span>
        Area is lines of code. Click a cell to descend, the breadcrumb to come back.
        Toggle a colour chip to grey out that class. The Voronoi view aggregates deep
        folders when a level is too large to tessellate — an aggregate cell is hatched
        and its tooltip gives the exact breakdown.</span></div>
      <div class="rule"><i style="background:var(--red)"></i><span>
        <b>What red actually asserts.</b> rimflow items have no path field, so red means
        <i>an open bug item's descriptive prose names this file</i> — a real, checkable
        naming, not a guess. It is not a claim that the defect lives in these lines. Every
        red tooltip names the item, so the claim can be read at source. A mention can still
        be incidental; nothing is inferred beyond the naming.</span></div>
      <div class="rule"><i style="background:var(--green)"></i><span>
        <b>Green is expected to be empty.</b> CLAUDE.md's rule is that every file is dirty
        until a full-file review says otherwise, recorded by
        <code>code_review_status.py mark-clean</code>. The count above says how many entries
        exist. Zero green means zero recorded reviews, not a broken tool.</span></div>
      </section>
    </aside>
  </main>
</div>
<div id="tip"></div>
__LIBS__
<script>
const DATA = __DATA__;
const COLOR = {red:"#e0483c",blue:"#2f7fd8",green:"#3ea55f",grey:"#79808f",unmeasured:"#c9a227"};
const LABEL = {red:"BUG",blue:"IN DEV",green:"CLEAN",grey:"DIRTY",unmeasured:"UNMEASURED"};
const ORDER = ["red","blue","green","grey","unmeasured"];
const RULES = [
 ["red","1 · RED — known error or bug","Named by path in the descriptive prose of an OPEN rimflow item of kind <code>bug</code>, <code>defect</code> or <code>fix</code>. Red wins over every other rule: a review-clean file named by an open bug is red. An item's <i>verify</i> and <i>criteria</i> sections are deliberately not read — they name the instrument, not the defect."],
 ["blue","2 · BLUE — in dev","Uncommitted changes in the working tree, or named by an open item whose state is <code>doing</code>."],
 ["green","3 · GREEN — clean","CODE_REVIEW_STATUS.json records a clean mark and git shows zero commits against the path since."],
 ["grey","4 · GREY — dirty","The default, and the correct answer for almost every file: no review entry, or commits since one. A measured verdict, not a shrug."],
 ["unmeasured","5 · HATCHED — UNMEASURED","Status could not be determined: git refused, a recorded review sha no longer resolves, or the file is not decodable as text. Never counted as dirty."]
];

const svg = d3.select("#svg"), tip = d3.select("#tip");
let mode = "sq", path = [], hidden = new Set();

/* ---- hatch pattern for UNMEASURED and for aggregate cells ---- */
const defs = svg.append("defs");
function hatch(id, bg, fg){
  const p = defs.append("pattern").attr("id",id).attr("width",7).attr("height",7)
    .attr("patternUnits","userSpaceOnUse").attr("patternTransform","rotate(45)");
  p.append("rect").attr("width",7).attr("height",7).attr("fill",bg);
  p.append("rect").attr("width",3).attr("height",7).attr("fill",fg);
}
hatch("hUnk", "#c9a227", "#5c4a0d");
ORDER.forEach(k => hatch("agg_"+k, COLOR[k], "rgba(0,0,0,.42)"));

/* ---- header ---- */
// DATA.generated is "YYYY-MM-DD HH:MM" local time, same clock this page renders on.
const genDate = new Date(DATA.generated.replace(" ", "T"));
function relTime(){
  if (isNaN(genDate.getTime())) return "";
  const mins = Math.round((Date.now() - genDate.getTime()) / 60000);
  return mins < 1 ? "just now"
       : mins < 60 ? mins + " min ago"
       : mins < 1440 ? Math.round(mins / 60) + " h ago"
       : Math.round(mins / 1440) + " d ago";
}
function renderStamp(){
  const mins = (Date.now() - genDate.getTime()) / 60000;
  d3.select("#stamp").html(
    DATA.head + " · " + DATA.generated +
    ' <span class="stampRel' + (mins >= 30 ? " stale" : "") + '">(' + relTime() + ")</span>" +
    " · " + DATA.counts.total.toLocaleString() + " files · " +
    DATA.loc.total.toLocaleString() + " lines");
}
renderStamp();
setInterval(renderStamp, 30000);

const counts = d3.select("#counts");
ORDER.forEach(k=>{
  const c = counts.append("div").attr("class","chip").attr("data-k",k)
    .on("click",function(){
      hidden.has(k) ? hidden.delete(k) : hidden.add(k);
      d3.select(this).classed("off", hidden.has(k));
      render();
    });
  c.append("i").attr("class", k==="unmeasured" ? "hatch" : null)
    .style("background", k==="unmeasured" ? null : COLOR[k]);
  c.append("span").text(LABEL[k]);
  c.append("b").text(DATA.counts[k].toLocaleString());
});

const legend = d3.select("#legend");
RULES.forEach(([k,t,d])=>{
  const r = legend.append("div").attr("class","rule");
  r.append("i").style("background",COLOR[k])
   .style("background-image", k==="unmeasured"
     ? "repeating-linear-gradient(45deg,#5c4a0d 0 3px,#c9a227 3px 6px)" : "none");
  const s = r.append("div");
  s.append("b").html(t); s.append("span").html(d);
});

const st = d3.select("#stats").append("table").attr("class","n");
[["files scanned", DATA.counts.total],
 ["lines of code", DATA.loc.total],
 ["open rimflow items", DATA.items.openItems],
 ["open bug/defect/fix items", DATA.items.openBugs],
 ["…of those, kind:bug", DATA.items.openBugsStrict],
 ["…mapped to a real file", DATA.items.bugsMapped],
 ["…naming no resolvable file", DATA.items.bugsUnmapped],
 ["items in doing, mapped", DATA.items.doingMapped + " / " + DATA.items.doingItems],
 ["review entries recorded", DATA.reviewEntries],
 ["files undecodable as text", DATA.locEstimatedFiles]].forEach(([a,b])=>{
  const tr = st.append("tr"); tr.append("td").text(a);
  tr.append("td").text(typeof b === "number" ? b.toLocaleString() : b);
});

const um = d3.select("#unmapped");
if(DATA.items.unmappedBugIds.length === 0){
  um.append("div").attr("class","rule").append("span")
    .text("Every open bug named at least one file that exists.");
} else {
  um.append("div").attr("class","warn").html(
    "<b>" + DATA.items.unmappedBugIds.length + "</b> open bug item(s) name no resolvable file path, "
    + "so they colour nothing red:<br><br>"
    + DATA.items.unmappedBugIds.map(i=>"<code>"+i+"</code>").join("<br>"));
}

/* ---- files reviewed clean at least once, currently dirty again ---- */
const recid = d3.select("#recid");
const RECID = DATA.recidivists || [];
if(RECID.length === 0){
  recid.append("div").attr("class","rule").append("span")
    .text("None. Every file ever marked clean is still clean.");
} else {
  recid.append("div").attr("class","rule").append("span").html(
    "<b>"+RECID.length+"</b> file(s) went clean, then dirty again — the small number "
    + "in a cell's top-right corner is this same count.");
  RECID.slice(0, 40).forEach(r=>{
    const row = recid.append("div").attr("class","recid");
    row.append("span").attr("class","p").text(r.path);
    row.append("span").attr("class","c").text("×"+r.cycles);
  });
  if(RECID.length > 40){
    recid.append("div").attr("class","warn").text("+ "+(RECID.length-40)+" more.");
  }
}

/* ---- tree helpers ---- */
function visible(node){
  if(!node.children) return hidden.has(node.status) ? null : node;
  const kids = node.children.map(visible).filter(Boolean);
  if(!kids.length) return null;
  return {name:node.name, children:kids};
}
function current(){
  let n = visible(DATA.tree) || {name:DATA.tree.name, children:[]};
  for(const p of path){
    const nx = (n.children||[]).find(c=>c.name===p && c.children);
    if(!nx){ break; } n = nx;
  }
  return n;
}
function crumbs(){
  const c = d3.select("#crumbs").html("");
  c.append("a").text(DATA.tree.name).on("click",()=>{path=[];render();});
  path.forEach((p,i)=>{
    c.append("span").text("/");
    c.append("a").text(p).on("click",()=>{path=path.slice(0,i+1);render();});
  });
  const n = current();
  const leaves = d3.hierarchy(n).leaves().filter(d=>d.data.path);
  const loc = d3.sum(leaves, d=>d.data.loc);
  const mix = {};
  leaves.forEach(d=>mix[d.data.status]=(mix[d.data.status]||0)+d.data.loc);
  c.append("span").style("margin-left","10px")
   .text(leaves.length.toLocaleString()+" files · "+loc.toLocaleString()+" lines · ");
  ORDER.filter(k=>mix[k]).forEach(k=>{
    c.append("span").style("color",COLOR[k]).style("margin-right","8px")
     .text(LABEL[k]+" "+Math.round(100*mix[k]/loc)+"%");
  });
}

function showTip(ev,d){
  const n = d.data;
  let h;
  if(n.path){
    h = "<div class='p'>"+n.path+"</div><div class='r'><b style='color:"+COLOR[n.status]+"'>"
      + LABEL[n.status]+"</b> · "+n.loc.toLocaleString()+" lines</div>"
      + "<div class='r'>"+(n.why||[]).join("<br>")+"</div>";
  } else if(n.agg){
    h = "<div class='p'>"+n.name+"/</div><div class='r'><b>AGGREGATE</b> — "
      + n.agg.files.toLocaleString()+" files, "+d.value.toLocaleString()+" lines</div><div class='r'>"
      + ORDER.filter(k=>n.agg.mix[k]).map(k=>"<span style='color:"+COLOR[k]+"'>"+LABEL[k]
        +"</span> "+n.agg.mix[k].toLocaleString()+" lines").join("<br>")+"</div>";
  } else {
    h = "<div class='p'>"+n.name+"/</div><div class='r'>"+d.value.toLocaleString()+" lines</div>";
  }
  tip.html(h).style("opacity",1)
     .style("left", Math.min(ev.clientX+14, innerWidth-410)+"px")
     .style("top", Math.min(ev.clientY+14, innerHeight-120)+"px");
}
const hideTip = ()=>tip.style("opacity",0);
function fillOf(n){
  if(n.path) return n.status==="unmeasured" ? "url(#hUnk)" : COLOR[n.status];
  if(n.agg)  return "url(#agg_"+n.agg.top+")";
  return "none";
}
function descend(d){
  const chain=[]; let n=d;
  while(n.parent){ chain.unshift(n.data.name); n=n.parent; }
  if(d.data.path) chain.pop();
  path = path.concat(chain); render();
}

/* ---- squarified ---- */
function renderSquarified(w,h){
  const root = d3.hierarchy(current())
    .sum(d=>d.children?0:Math.max(d.loc,1))
    .sort((a,b)=>b.value-a.value);
  d3.treemap().tile(d3.treemapSquarify).size([w,h])
    .paddingOuter(3).paddingTop(d=>d.depth?14:0).paddingInner(1)(root);

  const g = svg.append("g");
  g.selectAll("rect.dir").data(root.descendants().filter(d=>d.children&&d.depth>0))
    .join("rect").attr("class","dir dirhit")
    .attr("x",d=>d.x0).attr("y",d=>d.y0)
    .attr("width",d=>Math.max(0,d.x1-d.x0)).attr("height",d=>Math.max(0,d.y1-d.y0))
    .attr("fill","#1b1f2b").attr("stroke","#333a4d").attr("stroke-width",.7)
    .on("mousemove",showTip).on("mouseleave",hideTip)
    .on("click",(e,d)=>{hideTip(); descend(d);});
  g.selectAll("text.dlbl").data(root.descendants()
      .filter(d=>d.children&&d.depth>0&&d.x1-d.x0>44&&d.y1-d.y0>18))
    .join("text").attr("class","dlbl")
    .attr("x",d=>d.x0+4).attr("y",d=>d.y0+10)
    .text(d=>d.data.name).each(function(d){
      const max=d.x1-d.x0-6; let t=d.data.name;
      while(this.getComputedTextLength()>max && t.length>2){t=t.slice(0,-1);this.textContent=t+"…";}
    });

  g.selectAll("rect.cell").data(root.leaves())
    .join("rect").attr("class","cell")
    .attr("x",d=>d.x0).attr("y",d=>d.y0)
    .attr("width",d=>Math.max(0,d.x1-d.x0)).attr("height",d=>Math.max(0,d.y1-d.y0))
    .attr("fill",d=>fillOf(d.data))
    .attr("stroke","rgba(0,0,0,.45)").attr("stroke-width",.5)
    .on("mousemove",showTip).on("mouseleave",hideTip)
    .on("click",(e,d)=>{hideTip(); if(!d.data.path) descend(d);});

  g.selectAll("text.lbl").data(root.leaves().filter(d=>d.x1-d.x0>38&&d.y1-d.y0>13))
    .join("text").attr("class","lbl")
    .attr("x",d=>d.x0+3).attr("y",d=>d.y0+10)
    .text(d=>d.data.name).each(function(d){
      const max=d.x1-d.x0-5; let t=d.data.name;
      while(this.getComputedTextLength()>max && t.length>1){t=t.slice(0,-1);this.textContent=t;}
      if(this.getComputedTextLength()>max) this.textContent="";
    });

  // reviewed-then-dirty-again streak: a small number in the top-right corner,
  // only where the cell is big enough to hold one.
  const recidCells = root.leaves().filter(d=>d.data.status==="grey" && d.data.cycles>0 && d.x1-d.x0>20 && d.y1-d.y0>12);
  g.selectAll("text.badge").data(recidCells)
    .join("text").attr("class","badge")
    .attr("x",d=>d.x1-2.5).attr("y",d=>d.y0+8)
    .attr("text-anchor","end")
    .text(d=>d.data.cycles);
}

/* ---- collapse a subtree so the Voronoi solver stays tractable ---- */
const VOR_CAP = 320;
function collapseFor(node){
  const count = n => n.children ? d3.sum(n.children, count) : 1;
  function agg(n){
    const mix = {}; let files = 0;
    (function walk(x){
      if(x.children) x.children.forEach(walk);
      else { mix[x.status] = (mix[x.status]||0) + Math.max(x.loc,1); files++; }
    })(n);
    let top = "grey", best = -1;
    for(const k in mix) if(mix[k] > best){ best = mix[k]; top = k; }
    return {mix, top, files};
  }
  let total = count(node);
  if(total <= VOR_CAP) return node;
  // Too many cells to tessellate. Collapse whole directories DEEPEST-FIRST,
  // largest-first within a depth, until the level fits under the cap — so the
  // top structure survives and the blobs of many tiny files go first. A
  // collapsed cell is marked `agg`: hatched, and its tooltip carries the exact
  // per-colour breakdown, so it is never read as one file's verdict.
  const byDepth = [];
  (function walk(n, depth){
    if(!n.children) return;
    (byDepth[depth] = byDepth[depth] || []).push(n);
    n.children.forEach(c => walk(c, depth + 1));
  })(node, 0);
  const cells = new Map(), collapsed = new Set();
  const cellsOf = n => n.children ? cells.get(n) : 1;
  for(let d = byDepth.length - 1; d >= 1; d--){
    const level = byDepth[d] || [];
    level.forEach(n => cells.set(n, n.children.reduce((s,c) => s + cellsOf(c), 0)));
    level.sort((a,b) => cells.get(b) - cells.get(a));
    for(const n of level){
      if(total <= VOR_CAP) break;
      if(cells.get(n) <= 1) continue;
      collapsed.add(n);
      total -= cells.get(n) - 1;
      cells.set(n, 1);
    }
  }
  const rebuild = n => {
    if(!n.children) return n;
    if(collapsed.has(n)){
      const a = agg(n); let s = 0; for(const k in a.mix) s += a.mix[k];
      return {name:n.name, agg:a, loc:s};
    }
    return {name:n.name, children:n.children.map(rebuild)};
  };
  return rebuild(node);
}

function renderVoronoi(w,h){
  const busy = d3.select("#busy").style("display","flex");
  setTimeout(()=>{
    const src = collapseFor(current());
    const R = Math.min(w,h)/2 - 12;
    const cx = w/2, cy = h/2, N = 72;
    const clip = d3.range(N).map(i=>{
      const a = 2*Math.PI*i/N;
      return [cx + R*Math.cos(a), cy + R*Math.sin(a)];
    });
    const root = d3.hierarchy(src).sum(d=>d.children?0:Math.max(d.loc,1));
    let seed = 20260902;
    const prng = ()=>{ seed = (seed*1664525 + 1013904223) % 4294967296; return seed/4294967296; };
    try{
      d3.voronoiTreemap().clip(clip).prng(prng)
        .convergenceRatio(0.012).maxIterationCount(60)(root);
    }catch(err){
      busy.style("display","none");
      svg.append("text").attr("x",20).attr("y",30).attr("fill","#e0483c")
         .text("Voronoi layout failed: "+err.message);
      return;
    }
    const g = svg.append("g");
    const line = d3.line();
    const nodes = root.descendants().filter(d=>d.polygon && d.depth>0);
    g.selectAll("path.cell").data(nodes.filter(d=>!d.children))
      .join("path").attr("class","cell")
      .attr("d",d=>line(d.polygon)+"z")
      .attr("fill",d=>fillOf(d.data))
      .attr("stroke","rgba(0,0,0,.5)").attr("stroke-width",.6)
      .on("mousemove",showTip).on("mouseleave",hideTip)
      .on("click",(e,d)=>{hideTip(); if(!d.data.path) descend(d);});
    g.selectAll("path.dir").data(nodes.filter(d=>d.children))
      .join("path").attr("class","dir")
      .attr("d",d=>line(d.polygon)+"z").attr("fill","none")
      .attr("stroke","#aab2c6")
      .attr("stroke-opacity",d=>Math.max(.15, .95-d.depth*0.22))
      .attr("stroke-width",d=>Math.max(.6, 3.4-d.depth*0.85))
      .style("pointer-events","none");
    g.selectAll("text.dlbl").data(nodes.filter(d=>d.children&&d.depth<=2))
      .join("text").attr("class","dlbl")
      .attr("x",d=>d3.polygonCentroid(d.polygon)[0])
      .attr("y",d=>d3.polygonCentroid(d.polygon)[1])
      .attr("text-anchor","middle")
      .attr("opacity",d=>Math.abs(d3.polygonArea(d.polygon))>5200?1:0)
      .text(d=>d.data.name);
    busy.style("display","none");
  }, 30);
}

function render(){
  crumbs();
  svg.selectAll("g").remove(); svg.selectAll("text").remove();
  const el = document.getElementById("stage");
  const w = el.clientWidth, h = el.clientHeight;
  if(w<10||h<10) return;
  (mode==="sq" ? renderSquarified : renderVoronoi)(w,h);
}
d3.select("#bSq").on("click",()=>{mode="sq";
  d3.select("#bSq").classed("on",true); d3.select("#bVo").classed("on",false); render();});
d3.select("#bVo").on("click",()=>{mode="vo";
  d3.select("#bVo").classed("on",true); d3.select("#bSq").classed("on",false); render();});
let rt; addEventListener("resize",()=>{clearTimeout(rt); rt=setTimeout(render,180);});
render();
</script></body></html>
"""


# ---------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="codebase_health.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", action="store_true",
                    help="include .md/.txt/.csv/.json as well as source code")
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "Transient"),
                    help="where the .html and .json land (default: Transient/)")
    ap.add_argument("--json-only", action="store_true", help="skip the HTML page")
    args = ap.parse_args(argv)

    exts = set(CODE_EXT) | (DOC_EXT if args.docs else set())

    tracked = tracked_files()
    if tracked is None:
        print("FAIL: `git ls-files` failed — is this a git repo?", file=sys.stderr)
        return 2
    wt = working_tree_changes()
    wt_known = wt is not None
    if not wt_known:
        wt = set()
        print("WARN: `git status` failed; every file's 'in dev' state is UNMEASURED.",
              file=sys.stderr)

    candidates = set(tracked) | {p for p in wt if os.path.isfile(os.path.join(ROOT, p))}
    paths = sorted(p for p in candidates if wanted(p, exts))
    if not paths:
        print("FAIL: no files matched.", file=sys.stderr)
        return 2

    by_basename, by_suffix = build_index(candidates)
    bug_files, doing_files, istats = open_item_map(candidates, by_basename, by_suffix)
    ledger_known = bug_files is not None
    if not ledger_known:
        bug_files, doing_files = {}, {}
        print("WARN: the rimflow ledger could not be replayed (%s); bug/doing state is "
              "UNMEASURED for every file." % istats.get("error"), file=sys.stderr)

    verdicts, log = review_verdicts(paths)

    leaves, counts, loc_by = [], dict.fromkeys(STATUSES, 0), dict.fromkeys(STATUSES, 0)
    total_loc = 0
    est_loc = 0
    recidivists = []
    for p in paths:
        loc, measured = count_lines(os.path.join(ROOT, p))
        if not measured:
            est_loc += 1
            # count_lines() answers (0, False) for a file it could not OPEN as
            # well as one it could not DECODE, and `git ls-files` still lists a
            # tracked file deleted from the working tree — so getsize() is
            # called on paths that are gone, and raises. Falling back to 1 line
            # reports that one file UNMEASURED; without it a single `rm` takes
            # the whole board down with a traceback.
            try:
                loc = max(1, os.path.getsize(os.path.join(ROOT, p)) // 60)
            except OSError:
                loc = 1
        # A pre-existing entry with no `cleanCount` (recorded before that field
        # existed) has still been marked clean at least once — default it to 1,
        # not 0, or a legacy entry silently reads as "never reviewed".
        entry = log.get(p)
        clean_count = (entry.get("cleanCount") or 1) if entry else 0
        status, why = classify(p, measured, wt, doing_files, bug_files,
                               verdicts[p], wt_known, ledger_known, clean_count)
        counts[status] += 1
        loc_by[status] += loc
        total_loc += loc
        leaves.append({"name": os.path.basename(p), "path": p, "loc": loc,
                       "status": status, "why": why, "cycles": clean_count})
        if status == "grey" and clean_count > 0:
            recidivists.append({"path": p, "loc": loc, "cycles": clean_count})
    recidivists.sort(key=lambda r: (-r["cycles"], -r["loc"]))

    head = git(["rev-parse", "--short", "HEAD"]).stdout.strip() or "unknown"
    payload = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "head": head,
        "extensions": sorted(exts),
        "excluded": list(EXCLUDE_PREFIXES) + list(EXCLUDE_PARTS),
        "counts": dict(counts, total=len(paths)),
        "loc": dict(loc_by, total=total_loc),
        "locEstimatedFiles": est_loc,
        "reviewEntries": len(log),
        "recidivists": recidivists,
        "items": istats,
        "workingTreeKnown": wt_known,
        "ledgerKnown": ledger_known,
        "tree": build_tree(leaves),
    }

    os.makedirs(args.out_dir, exist_ok=True)
    json_path = os.path.join(args.out_dir, "codebase_health.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))

    print("HEAD %s   %d files   %d lines" % (head, len(paths), total_loc))
    for s in STATUSES:
        print("  %-11s %6d files  %9d lines  %s"
              % (s.upper(), counts[s], loc_by[s],
                 {"red": "known bug", "blue": "in dev", "green": "review-clean",
                  "grey": "dirty (measured)", "unmeasured": "could not determine"}[s]))
    print("  review entries recorded: %d" % len(log))
    if recidivists:
        print("  reviewed-then-dirty-again: %d file(s), worst is x%d (%s)"
              % (len(recidivists), recidivists[0]["cycles"], recidivists[0]["path"]))
    print("  open items %d, open bugs %d (%d mapped to a file, %d naming none)"
          % (istats["openItems"], istats["openBugs"],
             istats["bugsMapped"], istats["bugsUnmapped"]))
    if est_loc:
        print("  %d file(s) undecodable as text — sized by bytes, status UNMEASURED" % est_loc)
    print("  json -> %s" % json_path)

    if not args.json_only:
        html_path = os.path.join(args.out_dir, "codebase_health.html")
        write_html(html_path, payload)
        print("  html -> %s" % html_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
