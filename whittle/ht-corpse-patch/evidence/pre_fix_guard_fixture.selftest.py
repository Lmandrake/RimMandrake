#!/usr/bin/env python3
"""selftest_evictions_no_rostered_pair.py -- the generated BiomeCastEvictions_WildBiomes.xml never
evicts a pair a roster admits (EVICTIONS_RAZORJACK_FIX_STALE_ROW: AA_Razorjack x ZBiome_Grasslands
was shipped though rostered), and the generator never emits Corpse_ targets.

Offline: reads rosters/shipped XML and runs main() against temporary capture/cache fixtures.
Never walks installed mods or reads a real capture."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "design", "Jawa", "fauna"))
import biome_wildbiomes_evictions as E  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


roster = E.rostered()
# Positive control: the instrument can see the very pair the item named.
check("AA_Razorjack" in roster.get("ZBiome_Grasslands", set()),
      "control: the ZBiome_Grasslands roster admits AA_Razorjack")
check(sum(len(v) for v in roster.values()) > 100,
      "control: rosters read (%d admissions)" % sum(len(v) for v in roster.values()))

# Generator unit: race, kind and corpse twin are all exempt; an unrostered race is not.
r = {"B": {"KindX", "RaceY"}}
k = {"RaceX": ["KindX"]}
check(E.is_rostered("RaceY", "B", r, k), "is_rostered: race named directly")
check(E.is_rostered("RaceX", "B", r, k), "is_rostered: race via its kind")
check(E.is_rostered("Corpse_RaceX", "B", r, k), "is_rostered: corpse twin via its race's kind")
check(E.is_rostered("Corpse_RaceY", "B", r, k), "is_rostered: corpse twin of a named race")
check(not E.is_rostered("RaceZ", "B", r, k), "is_rostered: unrostered race is evictable")
check(not E.is_rostered("RaceY", "Other", r, k), "is_rostered: scoped to the biome")

xml = os.path.join(E.REPO, "src", "RimUtinni", "UtinniPatches", "Patches",
                   "BiomeCastEvictions_WildBiomes.xml")
pairs = set(E.PAIR_RE.findall(open(xml, encoding="utf-8").read()))
check(len(pairs) > 100, "control: shipped file parsed (%d pairs)" % len(pairs))
# Kinds are capture-only; offline, a race counts as rostered by its own name or its corpse's race.
bad = sorted((a, b) for a, b in pairs if E.is_rostered(a, b, roster, {}))
check(not bad, "shipped evictions hold no rostered pair: %s" % bad[:5])
check(("AA_Razorjack", "ZBiome_Grasslands") not in pairs,
      "the named pair AA_Razorjack x ZBiome_Grasslands is not evicted")
check(not any(a.startswith("Corpse_") for a, _b in pairs),
      "shipped evictions hold no Corpse_ target")


def exercise_main():
    """Use real capture/cache readers and XML writing, with all disk-walk inputs isolated."""
    import dumppath

    with tempfile.TemporaryDirectory(prefix="corpse-evictions-") as tmp:
        root = Path(tmp)
        defs = root / "capture" / "defs"
        defs.mkdir(parents=True)
        (defs / "PawnKindDef.json").write_text(json.dumps({"defs": [
            {"defName": "KindRostered", "fields": {"race": "RaceRostered"}},
            {"defName": "KindAllowed", "fields": {"race": "RaceAllowed"}},
        ]}))
        races = {"RaceAllowed", "RaceRostered", "RaceDirect", "RaceDuplicate", "RaceDead"}
        corpses = {"Corpse_" + r for r in races}
        cache = root / "animal-side.json"
        cache.write_text(json.dumps({"B": sorted(races | corpses)}))
        (defs / "ThingDef.json").write_text(json.dumps([
            {"defName": r} for r in sorted((races | corpses) - {"RaceDead", "Corpse_RaceDead"})
        ]))
        baseline = root / "shipped.xml"
        out = root / "generated.xml"
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(dumppath, "captures_newest_first",
                                            return_value=[str(defs.parent)]))
            stack.enter_context(patch.object(E, "painted_defs", return_value={"B"}))
            stack.enter_context(patch.object(E, "rostered",
                                            return_value={"B": {"KindRostered", "RaceDirect"}}))
            stack.enter_context(patch.object(E, "already_removed", return_value={
                ("RaceDuplicate", "B"), ("Corpse_RaceDuplicate", "B")}))
            stack.enter_context(patch.object(E, "SHIPPED_XML", str(baseline)))
            # A cache must bypass the installed-mod scan entirely.
            walk = stack.enter_context(patch("gen_cast_patch._animal_side_biomes",
                                             side_effect=AssertionError("installed-mod walk forbidden")))
            for live in (True, False):
                if not live:
                    (defs / "ThingDef.json").unlink()
                expected = {("RaceAllowed", "B")}
                if not live:
                    expected.add(("RaceDead", "B"))  # None preserves the existing fallback.
                baseline.write_text("<Patch>" + "".join(
                    E.OP % {"n": i, "race": r, "biome": b}
                    for i, (r, b) in enumerate(sorted(expected), 1)) + "</Patch>")
                stdout = io.StringIO()
                with patch.object(E, "is_rostered", wraps=E.is_rostered) as roster_filter:
                    with contextlib.redirect_stdout(stdout):
                        rc = E.main(["--cache", str(cache), "--xml", str(out)])
                print("fixture main, live=%s:\n%s" % (live, stdout.getvalue()))
                check(rc == 0 and out.is_file(), "main writes fixture XML, live=%s" % live)
                if out.is_file():
                    ops = ET.parse(out).getroot().findall("Operation")
                    targets = [E.PAIR_RE.fullmatch(op.findtext("xpath", "")).groups()
                               for op in ops]
                    check(set(targets) == expected and len(targets) == len(expected),
                          "main exact real-race output, live=%s: %s" % (live, targets))
                    check(not any(r.startswith("Corpse_") for r, _b in targets),
                          "main rejects every corpse, live=%s" % live)
                check(not any(c.args[0].startswith("Corpse_")
                              for c in roster_filter.call_args_list),
                      "corpse rejection precedes roster filtering, live=%s" % live)
            check(not walk.called, "main never walks installed mods with a cache")


exercise_main()

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
