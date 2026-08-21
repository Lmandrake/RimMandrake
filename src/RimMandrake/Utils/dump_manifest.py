#!/usr/bin/env python3
"""The one supported way to read `DefDump/manifest.json` in this repo.

🔴 **Why this exists.** `manifest.json` holds **532 `defCounts` entries under
517 distinct names** — the dumper wrote a line per def TYPE, and 13 simple names
were claimed by more than one type. A plain `json.load` keeps the last value
silently, so `defCounts["AbilityDef"]` reads **0** where 612 defs were written
first and overwritten twice. A dict cannot hold a duplicate key, so the evidence
is destroyed at parse time by every reader that does not take care.

⚠️ **Measured 2026-08-21, and the honest scope is narrower than it first looked:
nothing in this repo returns a wrong number from the manifest today.** The 532
entries sit under 517 distinct NAMES, so `.keys()` loses no name — only the
shadowed VALUES. The one keys-only consumer
(`skills/rimworld-modding/scripts/validate_patch.py`) is therefore correct as
written, and an audit that called it the live bug was wrong.

What this module is actually for, then:
  * the next reader who wants a defCounts VALUE — `AbilityDef` reads 0 there
  * `collision_report()`, which turns the duplicate keys into the only available
    evidence of what the dump destroyed (13 names, 824 defs)
  * keeping every reader one import away from both, rather than one field away
    from the bug

🔑 **This module is a LOCATOR, not a second implementation.** The real code is
`measure.dumpdb.read_manifest`, which lives in the generic
`measuring-large-artifacts` skill outside this repo. Keeping one seam here — and
not an import of an external path in thirteen files — is the whole point: if the
skill moves, one file changes.

    from dump_manifest import read_manifest, collision_report

    manifest, declared = read_manifest(path)   # declared: name -> [counts…]
    collided, lost = collision_report(declared)

`declared[name]` is a LIST, in write order. A list longer than one is a
collision, and everything but the last entry was lost. Use `declared[name][-1]`
only when you knowingly want the value a naive parse would have given.
"""
from __future__ import annotations

import contextlib
import os
import sys

SKILL = "measuring-large-artifacts"


def skill_scripts():
    """Locate the skill's `scripts/` directory, or None.

    Three places, most explicit first. Returns None rather than raising so a
    caller can degrade with a clear message instead of a traceback.
    """
    cands = []
    env = os.environ.get("MEASURE_SKILL_HOME")
    if env:
        cands.append(os.path.join(env, "scripts"))
    cands.append(os.path.expanduser(f"~/.claude/skills/{SKILL}/scripts"))
    # a sibling checkout of this repo
    d = os.path.abspath(__file__)
    while d != os.path.dirname(d):
        d = os.path.dirname(d)
        if os.path.isdir(os.path.join(d, ".git")):
            cands.append(os.path.join(os.path.dirname(d), SKILL, "scripts"))
            break
    for c in cands:
        if os.path.isdir(os.path.join(c, "measure")):
            return c
    return None


def _load():
    s = skill_scripts()
    if s is None:
        raise ImportError(
            f"{SKILL} is not installed. Expected it beside this repo, at "
            f"~/.claude/skills/{SKILL}, or named by MEASURE_SKILL_HOME. "
            f"Clone https://github.com/Lmandrake/measuring-large-artifacts")
    if s not in sys.path:
        sys.path.insert(0, s)
    from measure.dumpdb import read_manifest as _rm, collision_report as _cr
    return _rm, _cr


def read_manifest(path):
    """(manifest, declared_order). Duplicate `defCounts` keys are preserved."""
    return _load()[0](path)


def collision_report(declared_order):
    """(collided name -> counts in write order, total defs lost)."""
    return _load()[1](declared_order)


@contextlib.contextmanager
def dump_db(dump_dir, check_currency: bool = True):
    """Yield a live `measure.dumpdb.DumpDB` for this dump, or **None**.

    🔑 **The db-first pattern lives here once, not in every reader.** Five tools
    used to carry ~20 lines of "find the skill, import DumpDB, check .stale"
    apiece; that is five copies of a locator that must all change together the
    day the skill moves, which is exactly what this module exists to prevent.

        with dump_db(DUMP) as db:
            if db is not None:
                return {r[0] for r in db.sql("SELECT def_name FROM defs")}
        ...                       # the JSON fallback, unchanged

    **None means "answer it the old way", never "the answer is empty."** It is
    returned when the skill is not installed, when `defs.sqlite` has not been
    built, when the db is stale against its capture, or when opening it raises
    at all. A tool that cannot run is worse than one that is merely slow, so
    every caller keeps its JSON path — and that path is also what runs on a
    machine without the skill.

    ⚠️ `check_currency=False` suppresses only the staleness check, for a caller
    that knowingly wants a db whose source dump has moved. It does not make an
    absent db appear.
    """
    db = None
    try:
        path = os.path.join(str(dump_dir), "defs.sqlite")
        if not os.path.exists(path):
            yield None
            return
        s = skill_scripts()
        if s is None:
            yield None
            return
        if s not in sys.path:
            sys.path.insert(0, s)
        from measure.dumpdb import DumpDB
        db = DumpDB(path, check_currency=check_currency)
        if check_currency and db.stale:
            db.close()
            db = None
        yield db
    except Exception:
        yield None
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                pass


def hash_table(def_type, dump_dir):
    """(shortHash -> defName, defName -> shortHash) for one def type, or None.

    `None` means "the db is not usable here" — the caller falls back to reading
    `defs/<Type>.json`, which two of them already stream. Two readers had
    hand-rolled this over `json.load` of a whole type file; `short_hash` is an
    ordinary column, so the db answers it as one indexed query.

    ⚠️ A hash table is only valid against a capture taken with the SAME mod list
    as the save being decoded — the db's staleness guard checks the db against
    its capture, and cannot check the capture against your save.
    """
    with dump_db(dump_dir) as db:
        if db is None:
            return None
        fwd, rev = {}, {}
        for h, n in db.sql(
                "SELECT short_hash, def_name FROM defs WHERE def_type = ? "
                "AND short_hash IS NOT NULL", (def_type,)):
            fwd[int(h)] = n
            rev[n] = int(h)
        return (fwd, rev) if fwd else None


def available() -> bool:
    """Is the skill installed? For callers that want to degrade quietly."""
    return skill_scripts() is not None


if __name__ == "__main__":
    import json
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from game_paths import DEF_DUMP
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        DEF_DUMP, "manifest.json")
    man, order = read_manifest(p)
    coll, lost = collision_report(order)
    print(json.dumps({
        "entries": sum(len(v) for v in order.values()),
        "names": len(order),
        "collided": len(coll),
        "defs_lost": lost,
        "capturedUtc": man.get("capturedUtc"),
        "modCount": man.get("modCount"),
    }, indent=None))
