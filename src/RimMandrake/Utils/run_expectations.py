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
                        defType for one batch call per type, `deep=true` on
                        every call. The deep-serialize upgrade shipped
                        2026-09-04 and was live-proved 2026-09-13
                        (MASS_VALIDATION_LADDER_1) - both SCALAR and DEEP
                        checks run for real; there is no more
                        SKIPPED-PENDING-UPGRADE path in --live mode. `fields`
                        per call is the union of every scalar path plus every
                        deep check's top-level field name for that defType.

--l2 --plan-only        Offline. Parses every manifest's "l2" section
                        (expectations_l2.py) and prints the one batch's spawn
                        plan on a 250x250 map. Exit 1 on an unparsable manifest,
                        a grid that does not fit, or no manifest carrying l2.
--l2 --live             The L2 behaviour gauntlet: EVERY matched manifest's l2
                        spawns on ONE map in one sitting - spawn, readback,
                        screenshot (magenta count), step ticks, readback, one
                        log read - zero restarts (map id + clock checked).

USAGE
    python3 run_expectations.py --l2 --glob "infrastructure/state/expectations/*.expectations.json" --plan-only
    python.exe run_expectations.py --l2 --glob "..." --live
    python3 run_expectations.py --manifest infrastructure/state/expectations/FOO_1.expectations.json --fixture testdata/foo_fixture.json
    python3 run_expectations.py --glob "infrastructure/state/expectations/*.expectations.json" --live
    python.exe run_expectations.py --glob "..." --live   # --live needs Windows python (WSL has no bridge route)

Exit 0 = every check PASS (both modes now resolve SCALAR and DEEP checks for
real; SKIPPED-PENDING-UPGRADE can no longer occur in either mode).
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
import expectations_l2 as l2  # noqa: E402


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


def _top_field(path: str) -> str:
    """'wildness' -> 'wildness'; 'stages[0].label' -> 'stages'. get_defs'
    `fields` arg names top-level def fields only - a deep check's dotted/
    bracketed path is walked locally (expectations_manifest.walk_path)
    against whatever DeepSerializeValue handed back for that top field."""
    return path.split(".", 1)[0].split("[", 1)[0]


def _live_defs(manifest: em.Manifest) -> dict:
    """One jawa/get_defs batch call per defType named in ANY check (scalar
    or deep), `deep=true` on every call. The deep-serialize upgrade
    (MASS_VALIDATION_LADDER_1) is deployed and live-proved as of 2026-09-13
    - deep=true is byte-identical to deep=false for plain scalar fields, so
    there is no reason left to make two calls or to special-case scalar
    checks."""
    from rimbridge_client import RimBridge, resolve_endpoint  # local import: only needed live

    by_type: dict[str, set[str]] = {}
    fields_by_type: dict[str, set[str]] = {}
    for c in manifest.checks:
        by_type.setdefault(c.defType, set()).add(c.defName)
        fields_by_type.setdefault(c.defType, set()).add(_top_field(c.path))

    out: dict = {}
    if not by_type:
        return out
    host, port, token = resolve_endpoint()
    with RimBridge(host=host, port=port, token=token) as bridge:
        for defType, names in by_type.items():
            # jawa/get_defs takes `defs` as ';'-separated 'DefType/defName' pairs
            # and returns {"defs": [{"defName":..., "found":..., "fields": {...}}, ...]}
            # - NOT a bare {defName: fields} response, and NOT under a "rows" key
            # either (a prior version of this comment said "rows" - checked against
            # a live call 2026-09-18 and corrected; this path had never actually
            # been exercised live before, only against --fixture data, so the wrong
            # key silently returned zero rows every time instead of failing loud).
            defs_arg = ";".join("%s/%s" % (defType, n) for n in sorted(names))
            fields_arg = ",".join(sorted(fields_by_type[defType]))
            resp = bridge.call("jawa/get_defs",
                                {"defs": defs_arg, "fields": fields_arg, "deep": True})
            rows = resp.get("defs", []) if isinstance(resp, dict) else []
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


def run_l2(paths: list[str], *, live: bool) -> int:
    """One L2 batch over every manifest that carries an l2 section."""
    if not paths:
        print("no manifests matched")
        return 1
    manifests, bad = [], 0
    for p in paths:
        try:
            manifests.append(em.load_manifest(p))
        except em.ManifestError as exc:
            print("MANIFEST-ERROR %s: %s" % (p, exc))
            bad += 1
    batch = [m for m in manifests if m.l2]
    print("L2 batch: %d of %d manifests carry an l2 section; ticks %d"
          % (len(batch), len(manifests), l2.batch_ticks(batch)))
    if not batch:
        print("nothing to run: no manifest has an l2 section")
        return 1
    if not live:
        try:
            plan = l2.plan_batch(batch, (250, 250))
        except ValueError as exc:
            print("PLAN-ERROR %s" % exc)
            return 1
        for p in plan:
            print("  plan %-28s %-5s %-28s x%d @%d,%d" % (p.item, p.kind, p.defName, p.count, p.x, p.z))
        print("  rect %s" % (l2.batch_rect(plan),))
        print("\nPLAN: %d spawns, %d manifest(s) unparsable" % (len(plan), bad))
        return 1 if bad else 0
    rows = l2.run_l2_live(batch)
    for r in rows:
        print("  %-17s %-28s %s%s" % (r.status, r.scope, r.subject, ("  -- " + r.detail) if r.detail else ""))
    failing = [r for r in rows if not r.ok]
    print("\nL2 TOTAL: %d rows, %d not PASS, %d manifest(s) unparsable" % (len(rows), len(failing), bad))
    return 1 if (failing or bad) else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", help="one manifest file")
    ap.add_argument("--glob", help="glob of manifest files, e.g. infrastructure/state/expectations/*.expectations.json")
    ap.add_argument("--fixture", help="offline JSON stand-in for live_defs (see module docstring)")
    ap.add_argument("--live", action="store_true", help="call the real bridge (needs python.exe on WSL)")
    ap.add_argument("--l2", action="store_true", help="the L2 behaviour batch instead of the L1 def checks")
    ap.add_argument("--plan-only", action="store_true", help="with --l2: parse and plan offline, touch no game")
    args = ap.parse_args(argv)

    if not args.manifest and not args.glob:
        ap.error("pass --manifest or --glob")
    if args.l2:
        if args.plan_only == args.live or args.fixture:
            ap.error("--l2 takes exactly one of --plan-only or --live (no --fixture)")
        paths = [args.manifest] if args.manifest else sorted(globmod.glob(args.glob))
        return run_l2(paths, live=args.live)
    if args.plan_only:
        ap.error("--plan-only goes with --l2")
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
        allow_deep = True  # get_defs deep=true is deployed and live-proved (2026-09-13)

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
