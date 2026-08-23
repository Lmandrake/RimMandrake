#!/usr/bin/env python3
"""Read a FEW FIELDS of many defs without loading the whole def dump into memory.

Written for `WEAPON_TOOLS_PROJECT_NOT_LOAD_1`. Dependency-free: stdlib only,
`sqlite3` included. Keep it that way.

WHY THIS EXISTS
---------------
`defs/ThingDef.json` is ~316 MB of JSON holding 24,904 records. `json.load` on it
costs **3.2 s and 1.5 GB of resident memory**, and every tool that wanted six
fields per weapon was paying all of it.

🔴 THE DB IS NOT AUTOMATICALLY FASTER, AND MEASURING THAT WAS THE WHOLE JOB.
Measured 2026-08-22 against the same capture (578 mods, `9a204707f6dc183d`):

    json.load defs/ThingDef.json                         3.2 s   1500 MB
    SELECT json_extract(json,'$.fields.techLevel') …     6.7 s     16 MB   <- SLOWER
    the same with 3 json_extract columns                 6.8 s     16 MB   <- no worse
    side tables + json_extract over 771 rows             0.8 s     18 MB   <- this module

⇒ `json_extract` re-parses the whole row's JSON, so asking the db for a field of
every row is **twice as slow as reading the file** — the memory collapses and the
clock gets worse. The win is real only when the query never touches most rows:

  * `def_tags` and `def_flags` are **pre-extracted and indexed**. `weaponTags`
    and `ingestible` come out of them with no JSON parsing at all.
  * `defs.label` and `defs.def_name` are plain columns.
  * Everything else is `json_extract`, but only over rows a cheap indexed
    predicate already kept.

⚠️ Do not "simplify" this into one `json_extract` per field over `def_type='ThingDef'`.
That is the 6.7 s shape above, and it looks tidier.

⛔ AND DO NOT USE THE MULTI-PATH FORM. `json_extract(json,'$.a','$.b')` returns a
JSON array and looks like a single-parse win, but SQLite OMITS missing paths
rather than yielding null, so the array's positions shift per row. Measured: it
reported 535 defs carrying `weaponTags` where the truth is 721. It is both slower
AND wrong.

THE FALLBACK IS NOT OPTIONAL
----------------------------
`defs.sqlite` is built by the `measuring-large-artifacts` skill, which lives
OUTSIDE this repo. A machine with the def dump but not the skill has no db at
all, so every entry point here falls back to reading the JSON exactly as before
and returns the SAME shape. A caller cannot tell which path ran except by the
clock — and by `last_source()`, which says so for the report line.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys

__all__ = ["sqlite_path", "last_source", "weapon_tag_pairs", "weapon_defs",
           "defs_by_name", "weapon_cost_index"]

_TRUE = ("True", "true", "1", 1, True)
_last_source = "unknown"


def last_source() -> str:
    """Which path the most recent call took: 'sqlite' or 'json'."""
    return _last_source


def sqlite_path(dump_root: str) -> str | None:
    """The db for a dump, or None when it was never built.

    Accepts any of the three things a caller might hold, because they all mean
    "this dump" and the tools disagree about which they pass:

        …/DefDump                                   the root, flat layout
        …/DefDump/defs                              the def folder
        …/DefDump/captures/<id>                     a dated capture
        …/DefDump/captures/<id>/defs

    🔴 `defs.sqlite` LIVES AT THE DEFDUMP ROOT, OUTSIDE ANY CAPTURE, and that is
    the ruling (`DUMP_STORAGE_LAYOUT_RULING_1`), not an accident: it is DERIVED,
    so pruning a capture must never cost the database and re-deriving the
    database must never look like a new capture. ⚠️ That means `<capture>/defs.sqlite`
    does not exist and never will — walking up out of `captures/<id>` is required,
    not defensive. Measured 2026-08-22: these tools broke the moment the flat dump
    was migrated, because they looked only beside the path they were given.
    """
    root = os.path.normpath(dump_root)
    if os.path.basename(root) == "defs":
        root = os.path.dirname(root)
    cands = [root]
    # …/captures/<id>  ->  …  (the DefDump root, two levels up)
    parent = os.path.dirname(root)
    if os.path.basename(parent) == "captures":
        cands.append(os.path.dirname(parent))
    for base in cands:
        cand = os.path.join(base, "defs.sqlite")
        if os.path.isfile(cand):
            if _sqlite_describes(cand, root):
                return cand
            return None            # stale -> caller falls back to the capture's JSON
    return None


_WARNED = set()


def _sqlite_describes(db_path: str, capture_root: str) -> bool:
    """Does this defs.sqlite hold the SAME capture the caller is asking about?

    🔴 THE FAILURE THIS EXISTS TO STOP, measured 2026-08-23. `defs.sqlite` lives at
    the DefDump root and serves every capture, so it survives a new load untouched
    while the capture beside it moves on. `weapon_tag_audit.py` read its TAGS from
    a database built on 2026-08-21 and its HEADER from the newest capture's
    manifest, and printed:

        dump matches the live list: 578 mods, captured 2026-08-23T07:12:04Z
        🔴 pawn kinds with EVERY weapon tag empty: 12

    The capture it named says 2. `Mech_Pikeman`, `Drone_Sentry` and
    `Tribal_Archer_Fire` were all re-armed and it reported them disarmed — it would
    have closed a fixed item as still-broken, wearing a fresh timestamp.

    ⚠️ A modlist fingerprint cannot catch this. Both captures are the same 578 mods;
    what changed between them was OUR OWN XML. So compare the CAPTURE IDENTITY, not
    the mod set.

    Returns True when they match, or when neither side states its provenance (in
    which case there is nothing to contradict). On a mismatch it warns and returns
    False, and the caller falls back to the capture's own JSON — slower, and right.
    """
    import json as _json
    want = None
    man = os.path.join(capture_root, "manifest.json")
    if os.path.isfile(man):
        try:
            want = _json.loads(open(man, encoding="utf-8").read()).get("capturedUtc")
        except Exception:
            want = None
    got = None
    try:
        with _connect(db_path) as conn:
            row = conn.execute(
                "select value from provenance where key = 'captured_utc'").fetchone()
            got = row[0] if row else None
    except Exception:
        got = None
    if not want or not got:
        return True
    if _norm_utc(want) == _norm_utc(got):
        return True
    if (db_path, got, want) in _WARNED:          # once per run, not once per query
        return False
    _WARNED.add((db_path, got, want))
    sys.stderr.write(
        "⚠️  defs.sqlite describes capture %s, but you are asking about %s.\n"
        "    Falling back to that capture's JSON: the database is NOT a reading of\n"
        "    the load you mean, and a modlist fingerprint cannot tell them apart.\n"
        "    Rebuild it with `measure build` to get the fast path back.\n"
        % (got, want))
    return False


def _norm_utc(s: str) -> str:
    return str(s).replace("-", "").replace(":", "").replace("Z", "").replace("T", "").strip()


def _connect(path: str) -> sqlite3.Connection:
    # Read-only, always. These tools measure; they never write to the capture.
    return sqlite3.connect("file:%s?mode=ro" % path, uri=True)


_JSON_CACHE: dict = {}


def _load_json_defs(dump_root: str, def_type: str) -> list:
    """The fallback read, memoised.

    ⚠️ The memo is not an optimisation, it is a REGRESSION GUARD. A caller that
    asks this module three questions used to mean three `json.load`s of the same
    316 MB file — measured 7.9 s against the 3.5 s the tool cost before it was
    ported, i.e. the no-database machine would have been made WORSE by a change
    meant to make things better. One load, reused.
    """
    root = dump_root
    if os.path.basename(os.path.normpath(root)) != "defs":
        root = os.path.join(root, "defs")
    path = os.path.join(root, def_type + ".json")
    if path not in _JSON_CACHE:
        with open(path, "r", encoding="utf-8") as fh:
            _JSON_CACHE[path] = json.load(fh)["defs"]
    return _JSON_CACHE[path]


def _maybe_json(value):
    """A json_extract column: scalars come back as scalars, arrays as JSON text."""
    if isinstance(value, str) and value[:1] in "[{":
        try:
            return json.loads(value)
        except ValueError:
            return value
    return value


def weapon_tag_pairs(dump_root: str, def_type: str) -> list[tuple[str, str]]:
    """[(defName, tag), …] for every `weaponTags` entry on defs of that type.

    This is the join the item singled out: `def_tags` answers it without touching
    a single def's JSON.
    """
    global _last_source
    db = sqlite_path(dump_root)
    if db:
        _last_source = "sqlite"
        with _connect(db) as conn:
            return [(dn, tag) for dn, tag in conn.execute(
                "select d.def_name, t.tag from def_tags t "
                "join defs d on d.id = t.def_id "
                "where t.kind = 'weaponTags' and d.def_type = ?", (def_type,))]
    _last_source = "json"
    out = []
    for d in _load_json_defs(dump_root, def_type):
        for tag in ((d.get("fields") or {}).get("weaponTags") or []):
            out.append((d["defName"], tag))
    return out


# The fields `weapon_tag_audit` reads off a ThingDef, and nothing more.
_WEAPON_FIELDS = ("label", "techLevel", "weaponClasses", "weaponTags", "statBases")


def weapon_defs(dump_root: str) -> list[dict]:
    """Every def RimWorld itself classifies as a weapon, as {defName, fields}.

    🔑 The `weapon` flag is the engine's own classification, and restricting to it
    is SAFE for this purpose because it is a superset of what the callers test.
    Measured 2026-08-22: **0** ThingDefs carry a non-empty `weaponClasses` without
    also being flagged `weapon` (771 flagged). Every `eligible()` branch in
    `weapon_tag_audit` requires a non-empty `weaponClasses`, so a def outside this
    set could never have been returned anyway.

    ⚠️ That is a MEASURED equivalence over one capture, not a guarantee from the
    engine. If the flag and the field ever diverge the restriction stops being
    free — re-run the count in this docstring before trusting it again.
    """
    global _last_source
    db = sqlite_path(dump_root)
    if db:
        _last_source = "sqlite"
        cols = ", ".join("json_extract(d.json, '$.fields.%s')" % f for f in _WEAPON_FIELDS)
        sql = ("select d.def_name, %s, "
               "(select f.value from def_flags f "
               " where f.def_id = d.id and f.key = 'ingestible') "
               "from defs d "
               "join def_flags fl on fl.def_id = d.id and fl.key = 'weapon' "
               "where d.def_type = 'ThingDef' and fl.value in ('True','true','1')" % cols)
        out = []
        with _connect(db) as conn:
            for row in conn.execute(sql):
                fields = {k: _maybe_json(v) for k, v in zip(_WEAPON_FIELDS, row[1:-1])}
                fields["ingestible"] = row[-1] in _TRUE
                out.append({"defName": row[0], "fields": fields})
        return out
    _last_source = "json"
    return [d for d in _load_json_defs(dump_root, "ThingDef")
            if (d.get("fields") or {}).get("weaponClasses")]


def defs_by_name(dump_root: str, def_type: str, names, fields) -> dict[str, dict]:
    """{defName: {field: value}} for a NAMED handful of defs.

    For the questions that are about a specific short list — "which of the defs we
    cut still carry a weaponTag" — where scanning 24,904 records to look at 200 of
    them is the waste this module exists to remove.
    """
    global _last_source
    names = list(names)
    if not names:
        return {}
    db = sqlite_path(dump_root)
    if db:
        _last_source = "sqlite"
        cols = ", ".join("json_extract(json, '$.fields.%s')" % f for f in fields)
        out = {}
        with _connect(db) as conn:
            # Chunked so a very long cut list cannot hit SQLite's variable limit.
            for i in range(0, len(names), 500):
                chunk = names[i:i + 500]
                marks = ",".join("?" * len(chunk))
                sql = ("select def_name, %s from defs "
                       "where def_type = ? and def_name in (%s)" % (cols, marks))
                for row in conn.execute(sql, [def_type] + chunk):
                    out[row[0]] = {k: _maybe_json(v) for k, v in zip(fields, row[1:])}
        return out
    _last_source = "json"
    want = set(names)
    return {d["defName"]: {k: (d.get("fields") or {}).get(k) for k in fields}
            for d in _load_json_defs(dump_root, def_type) if d["defName"] in want}


# The fields a market-value recursion walks: the declared value, then the cost
# graph it has to fall back to.
_COST_FIELDS = ("statBases", "costList", "costStuffCount", "recipeMaker",
                "weaponTags")


class _LazyCostIndex:
    """A dict-shaped view over ThingDef cost fields that fetches ON DEMAND.

    🔴 THIS SHAPE EXISTS BECAUSE THE OBVIOUS ONE MEASURED WORSE. Projecting the six
    cost fields off ALL 24,904 ThingDefs costs **7.3 s** — `json_extract` re-parses
    each row's JSON, so touching every row is slower than `json.load` of the whole
    file (2.7 s), even though resident memory drops from 1500 MB to 270 MB.

    `base_market_value` recurses through `costList` into arbitrary materials, so it
    genuinely cannot know its working set in advance — but it only ever reaches a
    few hundred defs, not 24,904. Fetching by NAME on the miss keeps both wins:
    the recursion is unchanged, and the rows nobody asks for are never parsed.

    Reads are cached, including the misses, so a name is queried at most once.
    """

    def __init__(self, db: str):
        self._conn = _connect(db)
        self._cache: dict = {}
        self._cols = ", ".join(
            "json_extract(json, '$.fields.%s')" % f for f in _COST_FIELDS)

    def get(self, defname, default=None):
        if defname in self._cache:
            got = self._cache[defname]
            return default if got is None else got
        row = self._conn.execute(
            "select %s from defs where def_type = 'ThingDef' and def_name = ?"
            % self._cols, (defname,)).fetchone()
        rec = None if row is None else {
            "fields": {k: _maybe_json(v) for k, v in zip(_COST_FIELDS, row)}}
        self._cache[defname] = rec
        return default if rec is None else rec

    def __getitem__(self, defname):
        got = self.get(defname)
        if got is None:
            raise KeyError(defname)
        return got

    def __contains__(self, defname):
        return self.get(defname) is not None


def weapon_cost_index(dump_root: str):
    """(index, [(defName, weaponTags), …]) for pricing weapons.

    The list is every ThingDef carrying a `weaponTags` entry — off `def_tags`, so
    no JSON is parsed to build it. The index prices them and whatever their recipes
    reach, one named lookup at a time.

    Without a db both come from one `json.load`, exactly as before, and the index
    is a plain dict.
    """
    global _last_source
    db = sqlite_path(dump_root)
    if db:
        _last_source = "sqlite"
        by_def: dict[str, list] = {}
        with _connect(db) as conn:
            for dn, tag in conn.execute(
                    "select d.def_name, t.tag from def_tags t "
                    "join defs d on d.id = t.def_id "
                    "where t.kind = 'weaponTags' and d.def_type = 'ThingDef'"):
                by_def.setdefault(dn, []).append(tag)
        return _LazyCostIndex(db), sorted(by_def.items())
    _last_source = "json"
    defs = _load_json_defs(dump_root, "ThingDef")
    index = {d["defName"]: {"fields": {k: (d.get("fields") or {}).get(k)
                                       for k in _COST_FIELDS}}
             for d in defs}
    tagged = sorted((d["defName"], list((d.get("fields") or {}).get("weaponTags") or []))
                    for d in defs if (d.get("fields") or {}).get("weaponTags"))
    return index, tagged
