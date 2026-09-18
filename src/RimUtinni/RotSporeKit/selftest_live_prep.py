#!/usr/bin/env python3
"""ROT_LIVE_PREPARATIONS_1's linter: ban 4 is enforced, not just intended.

The Rot's live preparations (rot_kit_spec.md M4, bans 4) may never be
stockpilable. The spec's own words: "Between the two comps, ban 4 (no
stockpilable teas/symbionts) is enforced by the engine, not by discipline —
a linter can check both comps are present on every def tagged live-prep."

This is that linter. A ThingDef carrying RM_LivePrepExtension MUST carry:

  * CompProperties_TemperatureRuinable with minSafeTemperature > 0
    (a fridge ruins it), and
  * CompProperties_Lifespan with a lifespanTicks it can actually reach, and
  * a tickerType that ticks at all — BOTH comps run off CompTickRare, so a
    def left at the default tickerType Never silently has neither clock.
    That last one is the trap: the def would look correct in review and be
    perfectly storable in play.

It also checks the inverse direction, which is the one a future pass is
likelier to break: a def whose comps say it is perishable live-prep but
which forgot the marker would be invisible to both the lenient-viability
option and to this test.

Reads the XML on disk. It deliberately does NOT need the game, a def dump or
the environmentalhazards assembly, so it runs in the ordinary parallel
selftest sweep:

    python3 src/RimUtinni/RotSporeKit/selftest_live_prep.py
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.join(HERE, "Defs")

MARKER = "RimMandrake.EnvironmentalHazards.RM_LivePrepExtension"
TREASURE_MARKER = "RimMandrake.EnvironmentalHazards.RM_TreasureMarkerExtension"
RUINABLE = "CompProperties_TemperatureRuinable"
LIFESPAN = "CompProperties_Lifespan"
TICKING = {"Rare", "Normal", "Long"}

# 2.5 in-game days at 60,000 ticks/day. A live prep may be shorter-lived than
# the spec's figure but never longer: the whole mechanism is that it dies
# before it can be shipped anywhere.
MAX_LIFESPAN_TICKS = 150000


def iter_thingdefs():
    for root_dir, _dirs, files in os.walk(DEFS):
        for name in sorted(files):
            if not name.endswith(".xml"):
                continue
            path = os.path.join(root_dir, name)
            try:
                tree = ET.parse(path)
            except ET.ParseError as exc:
                yield path, None, "XML PARSE ERROR: %s" % exc
                continue
            for td in tree.getroot().findall("ThingDef"):
                yield path, td, None


def comp_classes(td):
    comps = td.find("comps")
    if comps is None:
        return {}
    out = {}
    for li in comps.findall("li"):
        cls = li.get("Class")
        if cls:
            out[cls] = li
    return out


def ext_classes(td):
    exts = td.find("modExtensions")
    if exts is None:
        return set()
    return {li.get("Class") for li in exts.findall("li") if li.get("Class")}


def main() -> int:
    failures: list[str] = []
    checked = 0
    marked = 0

    for path, td, parse_error in iter_thingdefs():
        rel = os.path.relpath(path, HERE)
        if parse_error:
            failures.append("%s: %s" % (rel, parse_error))
            continue

        checked += 1
        defname_el = td.find("defName")
        defname = defname_el.text.strip() if defname_el is not None and defname_el.text else "(no defName)"
        exts = ext_classes(td)
        comps = comp_classes(td)

        is_marked = MARKER in exts
        has_ruinable = RUINABLE in comps
        has_lifespan = LIFESPAN in comps

        if not is_marked:
            # Inverse direction: perishable-by-comps but untagged is just as
            # broken as tagged-but-immortal.
            if has_ruinable and has_lifespan:
                failures.append(
                    "%s (%s): carries both live-prep comps but NOT %s — invisible to the "
                    "viability option and to this linter." % (defname, rel, MARKER.rsplit(".", 1)[-1]))
            continue

        marked += 1

        if not has_ruinable:
            failures.append("%s (%s): tagged live-prep but has no %s — a fridge would not ruin it."
                            % (defname, rel, RUINABLE))
        else:
            min_safe_el = comps[RUINABLE].find("minSafeTemperature")
            try:
                min_safe = float(min_safe_el.text) if min_safe_el is not None else 0.0
            except (TypeError, ValueError):
                min_safe = 0.0
            if min_safe <= 0.0:
                failures.append(
                    "%s (%s): minSafeTemperature is %s — at or below freezing, so a freezer would "
                    "keep it perfectly. Ban 4 needs a positive threshold." % (defname, rel, min_safe))

        if not has_lifespan:
            failures.append("%s (%s): tagged live-prep but has no %s — waiting would not kill it."
                            % (defname, rel, LIFESPAN))
        else:
            ticks_el = comps[LIFESPAN].find("lifespanTicks")
            try:
                ticks = int(ticks_el.text) if ticks_el is not None else -1
            except (TypeError, ValueError):
                ticks = -1
            if ticks <= 0:
                failures.append("%s (%s): lifespanTicks is %s — no usable expiry."
                                % (defname, rel, ticks))
            elif ticks > MAX_LIFESPAN_TICKS:
                failures.append(
                    "%s (%s): lifespanTicks %d is longer than the %d-tick (2.5 day) ceiling — long "
                    "enough to ship." % (defname, rel, ticks, MAX_LIFESPAN_TICKS))

        ticker_el = td.find("tickerType")
        ticker = ticker_el.text.strip() if ticker_el is not None and ticker_el.text else None
        if ticker not in TICKING:
            failures.append(
                "%s (%s): tickerType is %s — both live-prep comps run off CompTickRare, so neither "
                "clock would ever run and the item would be immortal in practice."
                % (defname, rel, ticker or "unset (defaults to Never)"))

        if TREASURE_MARKER not in exts:
            failures.append(
                "%s (%s): tagged live-prep but not marked as a Rot treasure (%s) — owner card 6's "
                "sale conscience would not see it sold." % (defname, rel, TREASURE_MARKER.rsplit(".", 1)[-1]))

    if marked == 0:
        failures.append(
            "no ThingDef in RotSporeKit carries %s at all — the linter passed vacuously, which is a "
            "failure, not a pass." % MARKER)

    print("selftest_live_prep: %d ThingDefs scanned, %d tagged live-prep" % (checked, marked))
    for f in failures:
        print("FAIL " + f)
    if failures:
        print("selftest_live_prep: FAILED (%d)" % len(failures))
        return 1
    print("selftest_live_prep: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
