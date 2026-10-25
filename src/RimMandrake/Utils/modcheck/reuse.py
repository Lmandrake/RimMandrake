"""modcheck.reuse -- reuse an external live driver's result after an edit that cannot have changed what it measured.

focused_testing_plan_2026-10-25 option B. A FlowWorks reader (validation.py core_live_rows, hose_live_rows, the
driver_rows_at chains) trusts a result made at the current `status.mod_hash` -- FRESH, unchanged. With none, a result
is REUSABLE when its `manifest` (status.run_manifest, stamped by the driver at run start) equals the manifest of the
same script NOW and the game ran the repo's DLL:

  * mode 'live', not aborted (and `certifiable` where the reader demands it);
  * manifest schema current, `unresolved` empty on both sides (an unprovable import closure never reuses);
  * runtime hash equal (everything the game loads: Defs, Patches, Textures, ..., the committed Assemblies/*.dll);
  * test hash equal (the driver script, its transitive local imports and the data files they name);
  * env.assembly_sha256 equal to the repo DLL's sha (the deployed DLL was the repo's).

What happens to a reusable row is MODE, read from the environment (`modcheck run --reuse` sets it):
  MODCHECK_REUSE unset -> "report": the row keeps its old verdict (UNMEASURED), `Component.freshness` is
                          "reusable@<file>" -- the hit rate is measured, nothing is certified by it;
  MODCHECK_REUSE=1     -> "reuse": the row takes the reused result's status, freshness "reused@<file>"; a run with any
                          reused row is never `fresh_green` (runner summary.reuse);
  MODCHECK_REUSE=0     -> "off": not looked for at all.
A result with no manifest (every result written before 2026-10-25) is never reused: history is not reconstructed.
The live mod list (env.running) is recorded by the drivers but compared by neither path: a reader runs with no game.
"""
import glob
import json
import os

ENV = "MODCHECK_REUSE"
OFF, REPORT, REUSE = "off", "report", "reuse"

_CURRENT = {}


def mode(environ=None):
    v = str((environ if environ is not None else os.environ).get(ENV, "")).strip().lower()
    return REUSE if v in ("1", "yes", "true", "reuse") else OFF if v in ("0", "no", "false", "off") else REPORT


def _status():
    try:
        from modcheck import status as st  # noqa: E402 - validation.py imports the package
    except ImportError:
        import status as st  # noqa: E402 - modcheck dir on sys.path
    return st


def current_manifest(mod_dir, script_rel):
    """status.run_manifest for `script_rel` (relative to `mod_dir`), cached until runner.run_suite clears _CURRENT at
    the start of each suite run (an edit between runs is seen; one inside a run is not)."""
    key = (os.path.abspath(mod_dir), script_rel)
    if key not in _CURRENT:
        _CURRENT[key] = _status().run_manifest(mod_dir, os.path.join(mod_dir, script_rel))
    return _CURRENT[key]


def why_not(d, mod_dir, dll_sha, certifiable=False, _current=None):
    """None when result `d` is reusable now, else the first reason it is not. Pure given `_current`."""
    if d.get("mode") != "live":
        return "not live"
    if d.get("aborted"):
        return "aborted"
    if certifiable and not d.get("certifiable"):
        return "not certifiable"
    m = d.get("manifest")
    if not isinstance(m, dict):
        return "no manifest (written before manifests existed)"
    from_status = _status()
    if m.get("schema") != from_status.MANIFEST_SCHEMA:
        return "manifest schema %r" % m.get("schema")
    if m.get("unresolved"):
        return "manifest unresolved: %s" % "; ".join(map(str, m["unresolved"]))[:200]
    if not m.get("script") or not m.get("runtime") or not m.get("test"):
        return "manifest incomplete"
    cur = _current if _current is not None else current_manifest(mod_dir, m["script"])
    if cur.get("unresolved"):
        return "current manifest unresolved: %s" % "; ".join(map(str, cur["unresolved"]))[:200]
    if cur.get("runtime") != m["runtime"]:
        return "runtime changed (defs/patches/textures/DLL)"
    if cur.get("test") != m["test"]:
        return "test code changed (%s closure)" % m["script"]
    got = str((d.get("env") or {}).get("assembly_sha256") or "").lower()
    if not dll_sha or not got:
        return "no DLL identity (env.assembly_sha256 / repo DLL)"
    if got != dll_sha.lower():
        return "the game ran a DLL other than the repo's"
    return None


def _load(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def newest(paths, mod_dir, dll_sha, certifiable=False):
    """(path, result) of the newest reusable result among `paths` (by `started`, then file name), or None."""
    best = None
    for p in paths:
        d = _load(p)
        if d is None or why_not(d, mod_dir, dll_sha, certifiable) is not None:
            continue
        k = (str(d.get("started") or ""), os.path.basename(p))
        if best is None or k > best[0]:
            best = (k, p, d)
    return (best[1], best[2]) if best else None


def rows(patterns, ns, mod_dir, dll_sha, exclude=()):
    """{row id: (row, file basename)} from every reusable result matching `patterns` in `ns`, newest per id, ids in
    `exclude` (the fresh rows) left out -- the driver_rows_at contract for reuse."""
    found = []
    for g in patterns:
        for p in glob.glob(os.path.join(ns, g)):
            d = _load(p)
            if d is not None and why_not(d, mod_dir, dll_sha) is None:
                found.append((str(d.get("started") or ""), os.path.basename(p), d))
    found.sort(key=lambda x: (x[0], x[1]))
    got = {}
    for _, name, d in found:
        for r in d.get("rows") or []:
            if r.get("id") and r["id"] not in exclude:
                got[r["id"]] = (r, name)
    return got


def tag(name, m=None):
    """The Component.freshness of a row read from result file `name` under mode `m`."""
    return "%s@%s" % ("reused" if (m or mode()) == REUSE else "reusable", name)


def mark(components, names, freshness):
    """Set `freshness` on every component in `components` whose name is in `names`."""
    names = set(names)
    for c in components:
        if c.name in names:
            c.freshness = freshness


def summarize(chains):
    """{reused: [chain/row], reusable: [chain/row], fresh_green_blocked: bool} from runner chain dicts."""
    out = {"reused": [], "reusable": []}
    for ch in chains:
        for c in ch.get("components") or []:
            f = str(c.get("freshness") or "")
            if f.startswith("reused@"):
                out["reused"].append("%s/%s" % (ch.get("name"), c.get("name")))
            elif f.startswith("reusable@"):
                out["reusable"].append("%s/%s" % (ch.get("name"), c.get("name")))
    return out
