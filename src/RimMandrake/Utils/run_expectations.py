#!/usr/bin/env python3
"""run_expectations.py - the ONE runner for expectations_manifest.py manifests.

MASS_VALIDATION_LADDER_1: "One manifest format, one runner; no bespoke V&V
scripts per item." Every build item's manifest
(`infrastructure/state/expectations/<ITEM_ID>.expectations.json`) is consumed
by this one script - nobody writes another one-off checker.

TWO MODES
=========
--fixture <path.json>   Offline. `path.json` is a hand-authored
                        {"ThingDef::RSW_Cindermare": {...fields...}, ...}
                        stand-in for what a live deep-serialized `jawa/get_defs`
                        batch read would return. Zero bridge dependency - this
                        is how CI/selftest and a human iterating on a manifest
                        run it before any game is involved.

--live                  Calls the real bridge (`RimBridge` from
                        rimbridge_client.py) via `jawa/get_defs`, grouped by
                        defType for one batch call per type. SCALAR checks run
                        for real. DEEP checks are reported
                        SKIPPED-PENDING-UPGRADE (get_defs is scalar-only until
                        MASS_VALIDATION_LADDER_1's deep-serialize criterion
                        lands) - never silently attempted, never silently
                        dropped.

USAGE
    python3 run_expectations.py --manifest infrastructure/state/expectations/FOO_1.expectations.json --fixture testdata/foo_fixture.json
    python3 run_expectations.py --glob "infrastructure/state/expectations/*.expectations.json" --live
    python.exe run_expectations.py --glob "..." --live   # --live needs Windows python (WSL has no bridge route)

Exit 0 = every check PASS or (in --live mode, honestly) SKIPPED-PENDING-UPGRADE.
Exit 1 = at least one FAIL, MISSING-DEF, or PATH-ERROR. A manifest that fails
to parse is ALSO exit 1 - never silently excluded from the run.
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import expectations_manifest as em  # noqa: E402


def _load_fixture(path: str) -> dict:
    """{"ThingDef::RSW_Cindermare": {...}} -> {(defType, defName): {...}}."""
    raw = json.loads(Path(path).read_text())
    out = {}
    for k, v in raw.items():
        if "::" not in k:
            raise em.ManifestError("fixture key %r must be 'DefType::defName'" % k)
        defType, defName = k.split("::", 1)
        out[(defType, defName)] = v
    return out


def _live_defs(manifest: em.Manifest) -> dict:
    """One jawa/get_defs batch call per defType named in the manifest's
    SCALAR checks only - deep checks never touch the bridge (see module
    docstring: get_defs is scalar-only until the upgrade lands)."""
    from rimbridge_client import RimBridge, resolve_endpoint  # local import: only needed live

    by_type: dict[str, set[str]] = {}
    for c in manifest.checks:
        if not c.is_deep:
            by_type.setdefault(c.defType, set()).add(c.defName)

    out: dict = {}
    if not by_type:
        return out
    host, port, token = resolve_endpoint()
    with RimBridge(host=host, port=port, token=token) as bridge:
        for defType, names in by_type.items():
            # jawa/get_defs takes `defs` as ';'-separated 'DefType/defName' pairs
            # and returns {"rows": [{"defName":..., "found":..., "fields": {...}}, ...]}
            # - NOT a {defType, defNames} request / bare {defName: fields} response.
            defs_arg = ";".join("%s/%s" % (defType, n) for n in sorted(names))
            resp = bridge.call("jawa/get_defs", {"defs": defs_arg})
            rows = resp.get("rows", []) if isinstance(resp, dict) else []
            for row in rows:
                if row.get("found") and row.get("defName") in names:
                    out[(defType, row["defName"])] = row.get("fields", {})
    return out


def run_one(manifest_path: str, live_defs_source, *, allow_deep: bool) -> tuple[int, int]:
    try:
        manifest = em.load_manifest(manifest_path)
    except em.ManifestError as exc:
        print("MANIFEST-ERROR %s: %s" % (manifest_path, exc))
        return (0, 1)

    live_defs = live_defs_source(manifest)
    results = em.evaluate(manifest, live_defs, allow_deep=allow_deep)
    counts = em.summarize(results)
    print("== %s (%s) ==" % (manifest.item, manifest_path))
    fails = 0
    for r in results:
        line = "  %-24s %s::%s#%s" % (r.status, r.check.defType, r.check.defName, r.check.path)
        if r.status == "FAIL":
            line += "  -- %s" % r.detail
            fails += 1
        elif r.status in ("MISSING-DEF", "PATH-ERROR"):
            line += "  -- %s" % r.detail
            fails += 1
        print(line)
    print("  summary: %s" % counts)
    return (len(results), fails)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", help="one manifest file")
    ap.add_argument("--glob", help="glob of manifest files, e.g. infrastructure/state/expectations/*.expectations.json")
    ap.add_argument("--fixture", help="offline JSON stand-in for live_defs (see module docstring)")
    ap.add_argument("--live", action="store_true", help="call the real bridge (needs python.exe on WSL)")
    args = ap.parse_args(argv)

    if not args.manifest and not args.glob:
        ap.error("pass --manifest or --glob")
    if bool(args.fixture) == bool(args.live):
        ap.error("pass exactly one of --fixture or --live")

    paths = [args.manifest] if args.manifest else sorted(globmod.glob(args.glob))
    if not paths:
        print("no manifests matched")
        return 1

    if args.fixture:
        fixture_defs = _load_fixture(args.fixture)
        source = lambda _m: fixture_defs  # noqa: E731
        allow_deep = True  # a fixture CAN carry deep data - it's a stand-in for post-upgrade live
    else:
        source = _live_defs
        allow_deep = False  # honest: live get_defs cannot serve deep checks yet

    total = 0
    total_fail = 0
    manifest_errors = 0
    for p in paths:
        n, f = run_one(p, source, allow_deep=allow_deep)
        if n == 0 and f == 1:
            manifest_errors += 1
        total += n
        total_fail += f

    print("\nTOTAL: %d checks, %d failing, %d manifest(s) unparsable" %
          (total, total_fail, manifest_errors))
    return 1 if (total_fail or manifest_errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
