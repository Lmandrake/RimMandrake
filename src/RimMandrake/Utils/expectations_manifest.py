#!/usr/bin/env python3
"""expectations_manifest.py - the ONE manifest format for MASS_VALIDATION_LADDER_1's
L1 tier ("deploy -> minimal-list restart (22s) -> jawa/get_defs -> offline diff
against an expectations manifest", skills/rimworld-modding/SKILL.md #2).

NOTE: this docstring used to name jawa/hot_reload_defs as the L1 step. That call was
RETIRED by the owner on 2026-09-03 as unstable - on a 589-mod list it hung the bridge
five minutes and left the game unable to generate any pawn while reporting healthy
(HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1). Nothing in THIS file depended on it: the manifest
format and runner only care that the live state is current when jawa/get_defs reads it.

WHY THIS EXISTS
===============
Every FOUNDRY build item this session hand-rolled its own one-off offline check
(a validate_patch.py PatchOperationConditional probe, a bespoke defName grep, a
one-off sweep script with its own bug). VALIDATION_LADDER.md's own criteria name
the fix: "One manifest format, one runner; no bespoke V&V scripts per item."

THE FORMAT
==========
A manifest is one JSON file:

    {
      "item": "SOME_BUILD_ITEM_1",     # required, the rimflow item ID this belongs to
      "note": "optional free text",
      "checks": [
        {"defType": "ThingDef", "defName": "RSW_Cindermare",
         "path": "race.wildness", "expected": 1.0},
        {"defType": "HediffDef", "defName": "RSW_ColdDrain",
         "path": "stages[0].label", "expected": "hypothermic shock"}
      ]
    }

`path` is dotted-with-brackets: `a.b[0].c` walks dict key "a", dict key "b",
list index 0, dict key "c". A path with no "." and no "[" is a SCALAR check
(the field itself is a top-level def field) - these already work against the
LIVE `jawa/get_defs`, which is scalar-only today. A path with "." or "[" is a
DEEP check - it needs the deep-serialize upgrade to `jawa/get_defs`
(MASS_VALIDATION_LADDER_1's own second criterion) and reads SKIPPED-PENDING-
UPGRADE until that lands; write it into the manifest now anyway so nothing
has to be re-authored once the upgrade ships.

Each build item should ship its manifest at
`infrastructure/state/expectations/<ITEM_ID>.expectations.json` (create the
directory if it doesn't exist yet - it's new as of this item).

WHAT THIS MODULE DOES NOT DO
=============================
It does not call the bridge. That is `run_expectations.py`'s job (this module
stays importable and testable with zero network/bridge dependency - see
`selftest_expectations_manifest.py`).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_PATH_TOKEN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)((?:\[\d+\])*)$")
_INDEX = re.compile(r"\[(\d+)\]")


class ManifestError(ValueError):
    pass


@dataclass
class Check:
    defType: str
    defName: str
    path: str
    expected: Any
    kind: str  # "scalar" or "deep", derived from path shape

    @property
    def is_deep(self) -> bool:
        return self.kind == "deep"


@dataclass
class Manifest:
    item: str
    note: str
    checks: list[Check]
    source_path: str | None = None


def classify_path(path: str) -> str:
    """"wildness" -> scalar. "stages[0].label" or "a.b" -> deep."""
    if not path:
        raise ManifestError("empty path")
    return "deep" if ("." in path or "[" in path) else "scalar"


def load_manifest(path: str | Path) -> Manifest:
    """Load and validate one manifest file. Raises ManifestError on anything
    malformed - a manifest that fails to parse must never be silently
    skipped (that is exactly the "silent success" failure mode this whole
    ladder exists to catch)."""
    p = Path(path)
    try:
        raw = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError("%s: cannot read/parse: %s" % (p, exc)) from exc
    return parse_manifest(raw, source_path=str(p))


def parse_manifest(raw: dict, source_path: str | None = None) -> Manifest:
    if not isinstance(raw, dict):
        raise ManifestError("manifest root must be an object")
    item = raw.get("item")
    if not item or not isinstance(item, str):
        raise ManifestError("manifest missing required string field 'item'")
    checks_raw = raw.get("checks")
    if not isinstance(checks_raw, list) or not checks_raw:
        raise ManifestError("manifest '%s' has no non-empty 'checks' list" % item)

    checks: list[Check] = []
    for i, c in enumerate(checks_raw):
        if not isinstance(c, dict):
            raise ManifestError("checks[%d] is not an object" % i)
        for field in ("defType", "defName", "path"):
            if not c.get(field):
                raise ManifestError("checks[%d] missing required field %r" % (i, field))
        if "expected" not in c:
            raise ManifestError("checks[%d] missing required field 'expected'" % i)
        path = c["path"]
        for seg in path.split("."):
            base = _INDEX.sub("", seg)
            if not _PATH_TOKEN.match(seg) and not base:
                raise ManifestError("checks[%d] path segment %r is malformed" % (i, seg))
        checks.append(Check(
            defType=c["defType"], defName=c["defName"], path=path,
            expected=c["expected"], kind=classify_path(path),
        ))
    return Manifest(item=item, note=raw.get("note", ""), checks=checks,
                     source_path=source_path)


def _walk_segment(obj: Any, seg: str) -> Any:
    m = _INDEX.search(seg)
    key = _INDEX.sub("", seg)
    if key:
        if not isinstance(obj, dict):
            raise KeyError("expected a dict to read key %r, got %s" % (key, type(obj).__name__))
        if key not in obj:
            raise KeyError("key %r not present (have: %s)" % (key, sorted(obj.keys())[:20]))
        obj = obj[key]
    for idx in (int(x) for x in _INDEX.findall(seg)):
        if not isinstance(obj, list):
            raise KeyError("expected a list to index [%d], got %s" % (idx, type(obj).__name__))
        if idx >= len(obj):
            raise KeyError("index [%d] out of range (len=%d)" % (idx, len(obj)))
        obj = obj[idx]
    return obj


def walk_path(root: Any, path: str) -> Any:
    """Walk a dotted-with-brackets path into a (nested) dict/list structure.
    Raises KeyError with a specific reason on any miss - never returns a
    silent None, since None is also a legitimate expected value."""
    obj = root
    for seg in path.split("."):
        obj = _walk_segment(obj, seg)
    return obj


@dataclass
class Result:
    check: Check
    status: str          # "PASS" | "FAIL" | "MISSING-DEF" | "SKIPPED-PENDING-UPGRADE" | "PATH-ERROR"
    actual: Any = None
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "PASS"


def evaluate(manifest: Manifest, live_defs: dict, *, allow_deep: bool = False) -> list[Result]:
    """`live_defs` maps (defType, defName) -> the def's field dict, exactly the
    shape a (future, deep-serialized) `jawa/get_defs` batch read returns.

    `allow_deep=False` (the honest default until the C# upgrade lands) marks
    every deep check SKIPPED-PENDING-UPGRADE rather than attempting to walk a
    live_defs structure that live jawa/get_defs cannot actually produce yet -
    getting this wrong (silently attempting deep checks against scalar-only
    live data) is exactly the kind of "reports success, checked nothing" bug
    this ladder exists to prevent."""
    results = []
    for c in manifest.checks:
        if c.is_deep and not allow_deep:
            results.append(Result(c, "SKIPPED-PENDING-UPGRADE",
                                   detail="jawa/get_defs deep-serialize not live yet"))
            continue
        key = (c.defType, c.defName)
        if key not in live_defs:
            results.append(Result(c, "MISSING-DEF",
                                   detail="%s %s not present in live_defs" % key))
            continue
        try:
            actual = walk_path(live_defs[key], c.path)
        except KeyError as exc:
            results.append(Result(c, "PATH-ERROR", detail=str(exc)))
            continue
        if actual == c.expected:
            results.append(Result(c, "PASS", actual=actual))
        else:
            results.append(Result(c, "FAIL", actual=actual,
                                   detail="expected %r, got %r" % (c.expected, actual)))
    return results


def summarize(results: list[Result]) -> dict:
    counts: dict[str, int] = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    return counts
