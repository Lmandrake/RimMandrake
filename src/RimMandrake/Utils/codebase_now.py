#!/usr/bin/env python3
r"""codebase_now.py — CODEBASE_NOW, the standing clean/dirty treemap page. No model call, no network.

Item RIMMANDRAKE_REVIVE_CLEAN_DIRTY_TREEMAP_ON_STANDING_TABS, his card of 2026-11-19 5:54 PM PST: "the Python to
visualize the clean/dirty codebase is ressurrected and included on the standard suite of Desktop visualizations to
track". Promises: design/specs/2026-11-19-codebase-now/boundary.md; tests: selftest_codebase_now.py.

    python3 src/RimMandrake/Utils/codebase_now.py                write CODEBASE_NOW.html and .json, exit 0 / 3
    python3 src/RimMandrake/Utils/codebase_now.py --json         the facts to stdout, write nothing
        --root DIR        measure another clone (default: this one)
        --out DIR         write the page there (default: <RM data root>/conductor = D:\ClaudeWork\rimmandrake\conductor)
        --no-page-tests   do not run boundary tests files; page states read UNMEASURED

One leaf per code file (the extensions of codebase_health.CODE_EXT), sized by lines. Its colour is one state:
  read-clean   code_review_status.clean_state() says CLEAN: the bytes equal the bytes of its last clean mark
  dirty        a mark exists, and the file changed since, or it was reopened
  never-read   no review record names the file
  unmeasured   the file is listed and could not be read
A ring marks a file that a boundary page names, in that page's state (CLEAN / DIRTY / UNREADABLE, page_states()).
FLAGGED (his card: a file whose one blind reread also found and fixed a significant finding) has no source yet in
code_review_status; the legend says UNMEASURED and names the item that builds it.

Exit 0: the page holds measured totals. Exit 3: the page was written, and it says UNMEASURED with the cause (git or the
review record could not be read, or the clone's last fetch is over 1 hour old).
"""
import argparse
import hashlib
import html
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import boundary_check as BC  # noqa: E402
import code_review_status as CRS  # noqa: E402  the one authority on the review record and on page states
import codebase_health as CH  # noqa: E402  the code extensions, the excluded trees, the line counter

PAGE_NAME = "CODEBASE_NOW.html"
FACTS_NAME = "CODEBASE_NOW.json"
CACHE_NAME = "codebase_now_tests_cache.json"
STATES = ("read-clean", "dirty", "never-read", "unmeasured")
PAGE_STATES = ("CLEAN", "DIRTY", "UNREADABLE")

# Temporary evidence trees, not code to review (the whittle loop's per-item kits; deleted 2026-11-13, kept here so a
# copy that comes back stays out of the denominator), then the trees the older treemap already leaves out.
EXCLUDED_TREES = ("whittle/", "infrastructure/whittle_claude/") + tuple(CH.EXCLUDE_PREFIXES)
EXCLUDED_PARTS = tuple(CH.EXCLUDE_PARTS)

# LIMITS (boundary page §LIMITS). Danger: a dead timer, or a clone that stopped fetching, leaves a page that looks
# current. The timer runs every 15 min and the dispatch clone fetches every few minutes (measured 2026-11-19).
STALE_S = 3600
# Danger: a tests verdict that a change to an unlisted file broke. Without a cache each run starts every boundary
# tests file, about two minutes for 14 of them (code_review_status.TESTS_TIMEOUT_S comment, 2026-11-19).
TESTS_CACHE_S = 24 * 3600
GIT_TIMEOUT_S = 120  # Danger: a hung git hangs the timer run for good; `git ls-files` here takes well under 1 s.

FLAGGED = {"state": "UNMEASURED",
           "cause": "code_review_status.py has no list of flagged files yet; "
                    "RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG builds the flag"}

REAL_RUN_TESTS = CRS._run_tests


class Unseen(Exception):
    """A could-not-look: the cause is the message."""


# ---- reading ---------------------------------------------------------------------------------------------------------

def point_at(root):
    """code_review_status reads its root at import; point it at `root` for this run."""
    CRS.ROOT = root
    CRS.REC_DIR = os.path.join(root, "infrastructure", "state", "code_review")


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True, timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Unseen("git %s could not run: %s" % (args[0], e))
    if r.returncode != 0:
        raise Unseen("git %s failed in %s: %s" % (args[0], root, r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout


def excluded_by(rel):
    for t in EXCLUDED_TREES:
        if rel.startswith(t):
            return t
    for p in EXCLUDED_PARTS:
        if p in "/" + rel:
            return p
    return None


def is_code(rel):
    base = os.path.basename(rel)
    return "." in base and base.rsplit(".", 1)[-1].lower() in CH.CODE_EXT


def fetch_age(root, now):
    try:
        return now - os.stat(os.path.join(root, ".git", "FETCH_HEAD")).st_mtime
    except OSError:
        return None


def records():
    """-> ({path: entry}, newest record ts). A shard that cannot be parsed is a could-not-look."""
    try:
        recs = CRS.read_records()
        return CRS.load(), max((r.get("ts", "") for r in recs), default="")
    except SystemExit as e:
        raise Unseen("the review record could not be read: %s" % e)
    except (OSError, ValueError) as e:
        raise Unseen("the review record could not be read: %s" % e)


def file_state(rel, entry):
    loc, measured = CH.count_lines(os.path.join(CRS.ROOT, rel))
    if not measured:
        return loc, "unmeasured", "the file could not be read as text"
    if entry is None:
        return loc, "never-read", "no review record names it"
    state, detail = CRS.clean_state(rel, entry)
    return loc, ("read-clean" if state == "CLEAN" else "dirty"), detail


def _bytes(rel):
    try:
        with open(os.path.join(CRS.ROOT, rel), "rb") as f:
            return f.read()
    except OSError:
        return b"<unreadable>"


def tests_key(tests, pages):
    """The cache key of one tests file: its bytes, and each page that registers it and every file that page names."""
    h = hashlib.sha256(b"tests\0" + _bytes(tests))
    for page in sorted(p for p, t in pages.items() if t == tests):
        h.update(b"\0page\0" + page.encode() + b"\0" + _bytes(page))
        try:
            named = sorted(CRS.code_files(os.path.join(CRS.ROOT, page)))
        except BC.Unreadable:
            named = []
        for rel in named:
            h.update(b"\0file\0" + rel.encode() + b"\0" + _bytes(rel))
    return h.hexdigest()


def page_states(rels, pages, runner, cache_path, now, run_tests=True):
    """-> ({rel: (state, detail)} for the rels a boundary page names, [unreadable page causes], tests ages).
    page_states() runs through a cached tests runner (§tests-cache-reused-only-when-unchanged)."""
    named, blind = set(), []
    import glob
    for page in sorted(glob.glob(os.path.join(CRS.ROOT, "design", "specs", "*", "boundary.md"))):
        try:
            named |= CRS.code_files(page)
        except BC.Unreadable as e:
            blind.append(str(e))
    ask = sorted(named & set(rels))
    try:
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        if not isinstance(cache, dict):
            cache = {}
    except (OSError, ValueError):
        cache = {}
    ages = {}

    def cached(tests):
        if not run_tests:
            return "was not run (--no-page-tests)"
        key = tests_key(tests, pages)
        hit = cache.get(tests)
        if isinstance(hit, dict) and hit.get("key") == key and now - hit.get("at", -1e18) <= TESTS_CACHE_S:
            ages[tests] = now - hit["at"]
            res = hit.get("res")
            return tuple(res) if isinstance(res, list) else res
        res = runner(tests)
        cache[tests] = {"key": key, "at": now, "res": list(res) if isinstance(res, tuple) else res}
        ages[tests] = 0.0
        return res

    old_pages, old_run = CRS.PAGES, CRS._run_tests
    CRS.PAGES, CRS._run_tests = pages, cached
    try:
        rows = CRS.page_states(ask) if ask else []
    finally:
        CRS.PAGES, CRS._run_tests = old_pages, old_run
    if run_tests:
        _atomic(cache_path, json.dumps(cache, indent=1, sort_keys=True))
    out = {rel: (state, detail) for state, rel, detail in rows if state in PAGE_STATES}
    return out, blind, ages


# ---- the facts -------------------------------------------------------------------------------------------------------

def gather(root, out, now, pages=None, runner=None, run_tests=True):
    facts = {"built": int(now), "built_local": local(now), "root": root, "causes": [], "files": [], "totals": None,
             "excluded": [], "flagged": dict(FLAGGED), "head": None, "fetch_age_s": None, "newest_record": None,
             "pages": None, "blind_pages": [], "tests_ages_s": {}}
    point_at(root)
    try:
        listed = [p for p in git(root, "ls-files", "-z").decode("utf-8", "replace").split("\0") if p]
        head = git(root, "log", "-1", "--format=%h %ct").decode().split()
        facts["head"] = {"sha": head[0], "time": local(int(head[1]))} if len(head) == 2 else None
    except Unseen as e:
        facts["causes"].append(str(e))
        return facts
    age = fetch_age(root, now)
    facts["fetch_age_s"] = age
    if age is None:
        facts["causes"].append("no .git/FETCH_HEAD: when this clone last fetched is unknown, so its review record "
                               "may be behind origin")
    elif age > STALE_S:
        facts["causes"].append("this clone last fetched %s ago (limit %s), so its review record may be behind origin"
                               % (span(age), span(STALE_S)))
    try:
        entries, newest = records()
        facts["newest_record"] = utc_local(newest) if newest else None
    except Unseen as e:
        facts["causes"].append(str(e))
        return facts
    if facts["causes"]:
        return facts
    dropped = {}
    files = []
    for rel in listed:
        ex = excluded_by(rel)
        if ex:
            dropped[ex] = dropped.get(ex, 0) + 1
            continue
        if not is_code(rel):
            continue
        loc, state, why = file_state(rel, entries.get(rel))
        files.append({"path": rel, "loc": loc, "state": state, "why": why, "page_state": None, "page_detail": None})
    facts["excluded"] = [{"tree": t, "files": dropped.get(t, 0)} for t in EXCLUDED_TREES + EXCLUDED_PARTS]
    pages = CRS.PAGES if pages is None else pages
    ps, blind, ages = page_states([f["path"] for f in files], pages, runner or REAL_RUN_TESTS,
                                  os.path.join(out, CACHE_NAME), now, run_tests)
    for f in files:
        if f["path"] in ps:
            f["page_state"], f["page_detail"] = ps[f["path"]]
    facts["blind_pages"], facts["tests_ages_s"] = blind, ages
    facts["files"] = files
    tot = {s: {"files": 0, "lines": 0} for s in STATES + ("all",)}
    pst = {s: {"files": 0, "lines": 0} for s in PAGE_STATES}
    for f in files:
        for k in (f["state"], "all"):
            tot[k]["files"] += 1
            tot[k]["lines"] += f["loc"]
        if f["page_state"]:
            pst[f["page_state"]]["files"] += 1
            pst[f["page_state"]]["lines"] += f["loc"]
    facts["totals"], facts["pages"] = tot, pst
    return facts


def local(t):
    s = time.strftime("%a %b %d, %I:%M %p %Z", time.localtime(t))
    return s.replace(" 0", " ")


def utc_local(ts):
    """An ISO UTC record stamp -> local Pacific clock text; the stamp itself when it does not parse."""
    import datetime as dt
    try:
        t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=dt.timezone.utc)
        return local(t.timestamp())
    except ValueError:
        return ts


def span(s):
    s = abs(s)
    if s < 3600:
        return "%d min" % round(s / 60)
    if s < 48 * 3600:
        return "%.1f h" % (s / 3600)
    return "%.1f days" % (s / 86400)


# ---- the treemap -----------------------------------------------------------------------------------------------------

def tree_of(files):
    root = {"name": "", "kids": {}, "size": 0}
    for f in files:
        node = root
        parts = f["path"].split("/")
        for p in parts[:-1]:
            node = node["kids"].setdefault(p, {"name": p, "kids": {}, "size": 0})
        node["kids"][parts[-1]] = {"name": parts[-1], "file": f, "size": max(f["loc"], 1)}
    def total(n):
        if "file" in n:
            return n["size"]
        n["size"] = sum(total(k) for k in n["kids"].values())
        return n["size"]
    total(root)
    def collapse(n):
        if "file" in n:
            return n
        while len(n["kids"]) == 1 and "file" not in next(iter(n["kids"].values())) and n["name"]:
            (k,) = n["kids"].values()
            n = {"name": n["name"] + "/" + k["name"], "kids": k["kids"], "size": n["size"]}
        n["kids"] = {k: collapse(v) for k, v in n["kids"].items()}
        return n
    return collapse(root)


def _worst(row, side):
    s = sum(row)
    return max(max(row) * side * side / (s * s), (s * s) / (side * side * min(row)))


def squarify(sizes, x, y, w, h):
    """Bruls, Huizing and van Wijk's squarified layout. `sizes` sorted largest first -> one (x, y, w, h) each."""
    total = float(sum(sizes))
    if total <= 0 or w <= 0 or h <= 0:
        return [(x, y, 0.0, 0.0) for _ in sizes]
    vals = [v * w * h / total for v in sizes]
    rects = []
    i = 0
    while i < len(vals):
        side = min(w, h)
        row = [vals[i]]
        j = i + 1
        while j < len(vals) and _worst(row + [vals[j]], side) <= _worst(row, side):
            row.append(vals[j])
            j += 1
        s = sum(row)
        if w >= h:
            cw = s / h if h else 0
            yy = y
            for v in row:
                rh = v / cw if cw else 0
                rects.append((x, yy, cw, rh))
                yy += rh
            x, w = x + cw, w - cw
        else:
            rh = s / w if w else 0
            xx = x
            for v in row:
                rw = v / rh if rh else 0
                rects.append((xx, y, rw, rh))
                xx += rw
            y, h = y + rh, h - rh
        i = j
    return rects


W, H = 1600.0, 1000.0
HEAD_PX = 13.0


def svg_of(files):
    out = ['<svg viewBox="0 0 %d %d" class="map" data-path="" role="img" aria-label="treemap of code files by review state">'
           % (W, H),
           '<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" '
           'patternTransform="rotate(45)"><rect width="5" height="5" fill="#2a221a"/>'
           '<line x1="0" y1="0" x2="0" y2="5" stroke="#c49a5d" stroke-width="2"/></pattern></defs>']
    labels = []

    def put(node, x, y, w, h, depth):
        if "file" in node:
            f = node["file"]
            tip = "%s\n%s lines · %s: %s" % (f["path"], f"{f['loc']:,}", f["state"], f["why"])
            if f["page_state"]:
                tip += "\nboundary page: %s (%s)" % (f["page_state"], f["page_detail"] or "")
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="s-%s" data-p="%s"><title>%s</title></rect>'
                       % (x, y, w, h, f["state"], html.escape(f["path"], quote=True), html.escape(tip)))
            if f["page_state"]:
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="ring-%s"/>'
                           % (x + 0.75, y + 0.75, max(w - 1.5, 0), max(h - 1.5, 0), f["page_state"].lower()))
            return
        pad = 1.0 if depth else 0.0
        if depth:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="dir"/>' % (x, y, w, h))
        top = 0.0
        if depth and depth <= 3 and w > 70 and h > 34:
            top = HEAD_PX
            name = node["name"]
            room = int(w / 6.2)
            if len(name) > room:
                name = "…" + name[-(room - 1):]
            labels.append('<text x="%.1f" y="%.1f" class="lab d%d">%s</text>'
                          % (x + 3, y + 10, depth, html.escape(name)))
        kids = sorted(node["kids"].values(), key=lambda k: -k["size"])
        rects = squarify([k["size"] for k in kids], x + pad, y + pad + top, w - 2 * pad, h - 2 * pad - top)
        for k, (kx, ky, kw, kh) in zip(kids, rects):
            put(k, kx, ky, kw, kh, depth + 1)

    if files:
        put(tree_of(files), 0.0, 0.0, W, H, 0)
    out += labels
    out.append("</svg>")
    return "".join(out)


def tree_json(files):
    """The collapsed tree for the click script: a leaf is [name, lines, state, page_state, why, page_detail]; a folder
    is {"n": name, "s": lines, "k": [kids, largest first]}. Same tree and order as svg_of draws."""
    def conv(node):
        if "file" in node:
            f = node["file"]
            return [node["name"], f["loc"], f["state"], f["page_state"], f["why"], f["page_detail"]]
        kids = sorted(node["kids"].values(), key=lambda k: -k["size"])
        return {"n": node["name"], "s": node["size"], "k": [conv(k) for k in kids]}
    return json.dumps(conv(tree_of(files)), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


CLICK_JS = r"""
(function () {
  var el = document.getElementById('tree');
  var svg = document.querySelector('svg.map');
  var crumb = document.getElementById('crumb');
  if (!el || !svg || !crumb) { return; }
  var T = JSON.parse(el.textContent), W = 1600, H = 1000, HEAD = 13;
  var stack = [{node: T, path: '', name: 'all code'}];
  function isLeaf(n) { return Array.isArray(n); }
  function size(n) { return isLeaf(n) ? Math.max(n[1], 1) : n.s; }
  function esc(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;'); }
  function worst(row, side) {
    var s = 0, mx = 0, mn = Infinity;
    for (var i = 0; i < row.length; i++) { s += row[i]; mx = Math.max(mx, row[i]); mn = Math.min(mn, row[i]); }
    return Math.max(mx * side * side / (s * s), (s * s) / (side * side * mn));
  }
  function squarify(sizes, x, y, w, h) {
    var total = 0, i, j, k, rects = [];
    for (i = 0; i < sizes.length; i++) { total += sizes[i]; }
    if (total <= 0 || w <= 0 || h <= 0) { return sizes.map(function () { return [x, y, 0, 0]; }); }
    var vals = sizes.map(function (v) { return v * w * h / total; });
    i = 0;
    while (i < vals.length) {
      var side = Math.min(w, h), row = [vals[i]];
      j = i + 1;
      while (j < vals.length && worst(row.concat([vals[j]]), side) <= worst(row, side)) { row.push(vals[j]); j++; }
      var s = row.reduce(function (a, b) { return a + b; }, 0);
      if (w >= h) {
        var cw = h ? s / h : 0, yy = y;
        for (k = 0; k < row.length; k++) { var rh = cw ? row[k] / cw : 0; rects.push([x, yy, cw, rh]); yy += rh; }
        x += cw; w -= cw;
      } else {
        var rh2 = w ? s / w : 0, xx = x;
        for (k = 0; k < row.length; k++) { var rw = rh2 ? row[k] / rh2 : 0; rects.push([xx, y, rw, rh2]); xx += rw; }
        y += rh2; h -= rh2;
      }
      i = j;
    }
    return rects;
  }
  function f1(v) { return v.toFixed(1); }
  function draw() {
    var out = [], labels = [];
    function put(node, x, y, w, h, depth, path) {
      if (isLeaf(node)) {
        var p = path ? path + '/' + node[0] : node[0];
        var tip = p + '\n' + node[1].toLocaleString('en-US') + ' lines \u00b7 ' + node[2] + ': ' + node[4];
        if (node[3]) { tip += '\nboundary page: ' + node[3] + ' (' + (node[5] || '') + ')'; }
        out.push('<rect x="' + f1(x) + '" y="' + f1(y) + '" width="' + f1(w) + '" height="' + f1(h) + '" class="s-' +
          node[2] + '" data-p="' + esc(p) + '"><title>' + esc(tip) + '</title></rect>');
        if (node[3]) {
          out.push('<rect x="' + f1(x + 0.75) + '" y="' + f1(y + 0.75) + '" width="' + f1(Math.max(w - 1.5, 0)) +
            '" height="' + f1(Math.max(h - 1.5, 0)) + '" class="ring-' + node[3].toLowerCase() + '"/>');
        }
        return;
      }
      var here = depth ? (path ? path + '/' + node.n : node.n) : path;
      var pad = depth ? 1 : 0, top = 0;
      if (depth) { out.push('<rect x="' + f1(x) + '" y="' + f1(y) + '" width="' + f1(w) + '" height="' + f1(h) +
        '" class="dir"/>'); }
      if (depth && depth <= 3 && w > 70 && h > 34) {
        top = HEAD;
        var name = node.n, room = Math.floor(w / 6.2);
        if (name.length > room) { name = '\u2026' + name.slice(name.length - (room - 1)); }
        labels.push('<text x="' + f1(x + 3) + '" y="' + f1(y + 10) + '" class="lab d' + depth + '">' + esc(name) +
          '</text>');
      }
      var kids = node.k;
      var rects = squarify(kids.map(size), x + pad, y + pad + top, w - 2 * pad, h - 2 * pad - top);
      for (var i = 0; i < kids.length; i++) {
        put(kids[i], rects[i][0], rects[i][1], rects[i][2], rects[i][3], depth + 1, here);
      }
    }
    var cur = stack[stack.length - 1];
    put(cur.node, 0, 0, W, H, 0, cur.path);
    svg.innerHTML = svg.querySelector('defs').outerHTML + out.join('') + labels.join('');
    svg.setAttribute('data-path', cur.path);
    crumb.innerHTML = '';
    stack.forEach(function (c, i) {
      var a = document.createElement(i === stack.length - 1 && i > 0 ? 'b' : 'a');
      a.textContent = c.name;
      if (a.tagName === 'A') { a.setAttribute('data-i', String(i)); a.href = '#'; }
      if (i) { crumb.appendChild(document.createTextNode(' / ')); }
      crumb.appendChild(a);
    });
  }
  svg.addEventListener('click', function (e) {
    var p = e.target.getAttribute && e.target.getAttribute('data-p');
    if (!p) { return; }
    var cur = stack[stack.length - 1], kids = cur.node.k;
    for (var i = 0; i < kids.length; i++) {
      var kid = kids[i];
      if (isLeaf(kid)) { continue; }
      var kp = cur.path ? cur.path + '/' + kid.n : kid.n;
      if (p.indexOf(kp + '/') === 0) { stack.push({node: kid, path: kp, name: kid.n}); draw(); return; }
    }
  });
  crumb.addEventListener('click', function (e) {
    var a = e.target;
    if (!a.getAttribute || a.tagName !== 'A') { return; }
    e.preventDefault();
    stack = stack.slice(0, Number(a.getAttribute('data-i')) + 1);
    draw();
  });
})();
"""


# ---- the page --------------------------------------------------------------------------------------------------------

CSS = """
:root{--bg:#171310;--panel:#211b16;--line:#332a20;--ink:#efe7d9;--dim:#a99d89;--accent:#e0803a;
--clean:#4f9147;--dirty:#e0803a;--never:#5a4a39;--red:#d05a3c;--yellow:#e0b13e}
body{background:var(--bg);color:var(--ink);font:13px/1.45 'Segoe UI',system-ui,sans-serif;margin:0;padding:14px 18px}
h1{font-size:19px;margin:0 0 2px;color:#e6be7e;font-weight:600}
.sub{color:var(--dim);margin:0 0 10px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:9px 12px;margin:0 0 10px}
.stale{background:#5c1f1a;color:#ffd9d2;padding:9px 14px;border-radius:6px;margin:0 0 10px;font-weight:600}
.unm{background:#3a2a14;color:#f3d79a;padding:9px 14px;border-radius:6px;margin:0 0 10px}
table{border-collapse:collapse}
td,th{padding:2px 9px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th{color:var(--dim);font-weight:500}
td:first-child,th:first-child{text-align:left}
.sw{display:inline-block;width:12px;height:12px;border-radius:2px;vertical-align:-2px;margin-right:5px}
.sw.s-read-clean,.map .s-read-clean{background:var(--clean);fill:var(--clean)}
.sw.s-dirty,.map .s-dirty{background:var(--dirty);fill:var(--dirty)}
.sw.s-never-read,.map .s-never-read{background:var(--never);fill:var(--never)}
.sw.s-unmeasured{background:repeating-linear-gradient(45deg,#2a221a 0 2px,#c49a5d 2px 4px)}
.map .s-unmeasured{fill:url(#hatch)}
.sw.s-flagged{background:var(--red)}
.sw.ring-clean,.sw.ring-dirty,.sw.ring-unreadable{background:transparent;border:2px solid}
.sw.ring-clean{border-color:#f6efe0}.sw.ring-dirty{border-color:var(--red)}
.sw.ring-unreadable{border-color:var(--yellow);border-style:dashed}
.map{width:100%;height:auto;display:block;background:#120f0c;border-radius:6px}
.map rect{stroke:#120f0c;stroke-width:.35}
.map rect.dir{fill:#1d1813;stroke:#3b3024;stroke-width:.8}
.map .ring-clean,.map .ring-dirty,.map .ring-unreadable{fill:none;stroke-width:1.5;pointer-events:none}
.map .ring-clean{stroke:#f6efe0}.map .ring-dirty{stroke:var(--red)}
.map .ring-unreadable{stroke:var(--yellow);stroke-dasharray:3 2}
.map .lab{fill:#e6d6b8;font-size:10px;pointer-events:none;paint-order:stroke;stroke:#120f0c;stroke-width:2.5px}
.map .lab.d1{font-size:11px;font-weight:600;fill:#f0d9a8}
.map rect[data-p]{cursor:pointer}
#crumb{margin:0 0 6px;color:var(--dim)}#crumb a{color:#e6be7e;text-decoration:none;cursor:pointer}
#crumb a:hover{text-decoration:underline}#crumb b{color:var(--ink)}
.legend span.it{margin-right:16px;white-space:nowrap;display:inline-block}
code{color:#d8cdb8;font-size:12px}
.cols{display:flex;gap:10px;flex-wrap:wrap}.cols>.panel{flex:1 1 380px}
"""

STALE_JS = """
(function () {
  var built = Number(document.body.dataset.built) * 1000;
  var age = Date.now() - built;
  if (!(age <= %d)) {
    var s = document.getElementById('stale');
    s.hidden = false;
    s.textContent = 'STALE: this page was built ' + Math.round(age / 60000) + ' min ago (limit %d min). ' +
      'Every total reads UNMEASURED until rm-codebase-now.timer writes a fresh page.';
    var t = document.querySelectorAll('.total');
    for (var i = 0; i < t.length; i++) { t[i].textContent = 'UNMEASURED'; }
  }
})();
""" % (STALE_S * 1000, STALE_S // 60)


def n(v):
    return f"{v:,}"


def tot_cell(files, lines):
    return '<td><span class="total">%s files</span></td><td><span class="total">%s lines</span></td>' % (
        n(files), n(lines))


def by_folder(files):
    groups = {}
    for f in files:
        p = f["path"].split("/")
        key = "/".join(p[:min(3 if p[0] == "src" else 2, len(p) - 1)]) or "(root)"
        g = groups.setdefault(key, {s: [0, 0] for s in STATES})
        g[f["state"]][0] += 1
        g[f["state"]][1] += f["loc"]
    rows = sorted(groups.items(), key=lambda kv: -sum(v[1] for v in kv[1].values()))
    return rows


def render(facts, native_out):
    e = html.escape
    tot, causes = facts["totals"], facts["causes"]
    head = facts["head"]
    b = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         # A tab left open reloads at the timer's cadence; without it a standing tab shows an old page until the
         # stale banner fires (an hour on).
         '<meta http-equiv="refresh" content="900">',
         '<title>CODEBASE_NOW: clean and dirty code</title><style>%s</style></head>' % CSS,
         '<body data-built="%d">' % facts["built"],
         '<h1>CODEBASE_NOW: which code a cold read found clean</h1>',
         '<p class="sub">Built %s by <code>codebase_now.py</code> (no model, no network), every 15 min by '
         '<code>rm-codebase-now.timer</code>. Clone <code>%s</code>, HEAD %s; last fetch %s; newest review record %s.'
         '</p>' % (e(facts["built_local"]), e(facts["root"]),
                   e("%s (%s)" % (head["sha"], head["time"])) if head else "UNMEASURED",
                   e(span(facts["fetch_age_s"]) + " ago") if facts["fetch_age_s"] is not None else "UNMEASURED",
                   e(facts["newest_record"] or "UNMEASURED")),
         '<div id="stale" class="stale" hidden></div>']
    if causes:
        b.append('<div class="unm"><b>UNMEASURED.</b> This run could not measure the codebase, so no total and no '
                 'file is shown (never 0, never green). Cause: %s</div>' % e("; ".join(causes)))
    legend = [
        ("s-read-clean", "read-clean", "a cold read found nothing significant, and the bytes are unchanged since "
                                       "its clean mark"),
        ("s-dirty", "dirty", "a clean mark exists, and the file changed since or was reopened"),
        ("s-never-read", "never read", "no review record names the file"),
        ("s-unmeasured", "unmeasured", "the file is listed and could not be read"),
    ]
    b.append('<div class="panel legend">')
    for cls, word, what in legend:
        b.append('<span class="it" title="%s"><span class="sw %s"></span><b>%s</b></span>' % (e(what), cls, word))
    b.append('<span class="it" title="%s"><span class="sw s-flagged"></span><b>FLAGGED</b> UNMEASURED: %s</span>'
             % (e(facts["flagged"]["cause"]), e(facts["flagged"]["cause"])))
    b.append('<br><span class="it"><span class="sw ring-clean"></span>ring: boundary page CLEAN</span>'
             '<span class="it"><span class="sw ring-dirty"></span>ring: boundary page DIRTY</span>'
             '<span class="it"><span class="sw ring-unreadable"></span>ring: boundary page UNREADABLE</span>'
             '<span class="it" style="color:var(--dim)">size = lines; hover a cell for its path and reason; click a cell to open its folder, the breadcrumb to come back</span>')
    b.append('</div>')
    if tot:
        b.append('<div class="cols"><div class="panel"><table><tr><th>state</th><th>files</th><th>lines</th>'
                 '<th>share of files</th><th>share of lines</th></tr>')
        allf, alll = tot["all"]["files"] or 1, tot["all"]["lines"] or 1
        for cls, word, _ in legend:
            s = tot[cls[2:]]
            b.append('<tr><td><span class="sw %s"></span>%s</td>%s<td>%.1f%%</td><td>%.1f%%</td></tr>' % (
                cls, word, tot_cell(s["files"], s["lines"]), 100.0 * s["files"] / allf, 100.0 * s["lines"] / alll))
        b.append('<tr><td><b>all code files</b></td>%s<td></td><td></td></tr></table></div>' % tot_cell(
            tot["all"]["files"], tot["all"]["lines"]))
        pst = facts["pages"]
        ages = facts["tests_ages_s"]
        b.append('<div class="panel"><table><tr><th>named by a boundary page</th><th>files</th><th>lines</th></tr>')
        for s in PAGE_STATES:
            b.append('<tr><td><span class="sw ring-%s"></span>page %s</td>%s</tr>' % (
                s.lower(), s, tot_cell(pst[s]["files"], pst[s]["lines"])))
        b.append('</table><p class="sub" style="margin:6px 0 0">Page state is <code>code_review_status.py check</code>'
                 ' (CLEAN: every promise has a test and the tests pass). The boundary tests verdict is %s; a tests '
                 'file runs again when its page, itself or a named file changes, or after 24 h.%s</p></div>' % (
                     ("oldest %s old, over %d tests files" % (span(max(ages.values())), len(ages))) if ages
                     else "UNMEASURED (no tests file ran)",
                     (" Pages that could not be read: %s." % e("; ".join(facts["blind_pages"])))
                     if facts["blind_pages"] else ""))
        b.append('</div>')
        b.append('<div id="crumb"><b>all code</b></div>')
        b.append(svg_of(facts["files"]))
        b.append('<script type="application/json" id="tree">%s</script>' % tree_json(facts["files"]))
        b.append('<div class="cols"><div class="panel"><b>By folder</b> (lines; files in brackets)<table><tr>'
                 '<th>folder</th><th>read-clean</th><th>dirty</th><th>never read</th><th>unmeasured</th></tr>')
        for key, g in by_folder(facts["files"])[:30]:
            b.append('<tr><td><code>%s</code></td>%s</tr>' % (e(key), "".join(
                '<td>%s (%s)</td>' % (n(g[s][1]), n(g[s][0])) for s in STATES)))
        b.append('</table></div>')
        b.append('<div class="panel"><b>Not in the denominator.</b> Temporary evidence trees and code that is not '
                 'ours to review. Listed files dropped per tree:<table>')
        for ex in facts["excluded"]:
            b.append('<tr><td><code>%s</code></td><td>%s files</td></tr>' % (e(ex["tree"]), n(ex["files"])))
        b.append('</table><p class="sub" style="margin:6px 0 0">Code means the extensions <code>%s</code>. '
                 'Docs (.md, .json, .csv, .txt) are not counted.</p></div></div>' % e(" ".join(sorted(CH.CODE_EXT))))
    sep = "\\" if ":" in native_out[:3] else "/"
    b.append('<p class="sub">Page: <code>%s%s%s</code>. Facts: <code>%s</code> beside it. Promises: '
             '<code>design/specs/2026-11-19-codebase-now/boundary.md</code>.</p>'
             % (e(native_out), sep, PAGE_NAME, FACTS_NAME))
    b.append("<script>%s</script><script>%s</script></body></html>\n" % (STALE_JS, CLICK_JS))
    return "".join(b)


def _atomic(path, text):
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def build(root=REPO, out=None, now=None, pages=None, runner=None, run_tests=True, native_out=None, write=True):
    """-> (exit code, facts). Writes the page and the facts file unless write=False."""
    now = time.time() if now is None else now
    facts = gather(root, out, now, pages=pages, runner=runner, run_tests=run_tests and write)
    rc = 3 if facts["causes"] else 0
    if write:
        os.makedirs(out, exist_ok=True)
        _atomic(os.path.join(out, FACTS_NAME), json.dumps(facts, indent=1))
        _atomic(os.path.join(out, PAGE_NAME), render(facts, native_out or out))
    return rc, facts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-page-tests", action="store_true")
    a = ap.parse_args(argv)
    native = None
    if a.out is None:
        import rmpaths
        a.out, native = rmpaths.rm_str("conductor"), rmpaths.rm_win("conductor")
    root = os.path.abspath(a.root)
    rc, facts = build(root=root, out=a.out, run_tests=not a.no_page_tests, native_out=native,
                      write=not a.json)
    if a.json:
        print(json.dumps(facts, indent=1))
        return rc
    if facts["causes"]:
        print("UNMEASURED: %s" % "; ".join(facts["causes"]))
    else:
        t = facts["totals"]
        print("CODEBASE_NOW %s files, %s lines: read-clean %s, dirty %s, never-read %s, unmeasured %s (files)" % (
            n(t["all"]["files"]), n(t["all"]["lines"]), *(n(t[s]["files"]) for s in STATES)))
    print("wrote %s" % os.path.join(native or a.out, PAGE_NAME))
    return rc


if __name__ == "__main__":
    sys.exit(main())
