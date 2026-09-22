#!/usr/bin/env python3
"""No def may be declared twice inside one of our mods.

RimWorld keeps the LAST def loaded for a given (defType, defName) and the earlier
one vanishes with **no error** — so a duplicate is a silent content loss whose
winner depends on filename order.

Why this test exists, measured:

  2026-09-20 10:50 PDT  DESERT_PORT_DUPLICATE_DEFS_1 closed "0 duplicates",
                        deleting 366 duplicate copies out of SWBestiary.
  2026-09-20 17:35 PDT  DESERT_FAMILY_PORT_EXECUTION_1 added a port of Alpha
                        Animals' AA_BoulderMit under the defName RSW_Stoneback —
                        already taken by a Biomes! port of BMT_Stoneback. One
                        duplicate, reintroduced 6 hours 45 minutes after the
                        sweep that removed 366 of them.
  2026-09-22            Found by hand (STONEBACK_DEFNAME_COLLISION_1). The two
                        defs were different ANIMALS — a bodySize 0.4 reptile and
                        a bodySize 4.00 giant crab — so one of them did not exist
                        in the shipped game and nothing said which.

The sweep was correct and its claim was true when made. What was missing was a
guard, so the next commit could undo it invisibly. That is what this is.
"""

import glob
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

_HERE = os.path.abspath(__file__)                      # src/RimMandrake/Utils/<this>
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))


def _is_loaded(path):
    """Does RimWorld actually load defs from this path?

    Only the mod root's `Defs/` (and version folders) are loaded. A `Source/` tree
    holds C# and, in one mod here, a byte-identical stale copy of the def tree —
    which is dead weight rather than a live collision. Counting it would make this
    test fail on 30 defs the game never sees, and would train people to ignore it.
    """
    parts = path.split(os.sep)
    return "Source" not in parts


def duplicates_in(mod_dir, unloaded=None):
    """Map (defType, defName) -> [files] for every key declared more than once."""
    seen = defaultdict(list)
    for path in glob.glob(os.path.join(mod_dir, "**", "*.xml"), recursive=True):
        # Patches are xpath operations, not declarations — a defName inside one is
        # a REFERENCE and may legitimately repeat.
        if os.sep + "Patches" + os.sep in path:
            continue
        if not _is_loaded(path):
            if unloaded is not None:
                unloaded.append(os.path.relpath(path, REPO))
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue  # malformed XML is validate_patch.py's job, not this test's
        if root.tag != "Defs":
            continue
        for node in root:
            name = node.findtext("defName")
            if name:
                seen[(node.tag, name.strip())].append(os.path.relpath(path, REPO))
    return {k: v for k, v in seen.items() if len(set(v)) > 1 or len(v) > 1}


def main():
    mod_dirs = sorted(
        d for d in glob.glob(os.path.join(REPO, "src", "*", "*"))
        if os.path.isfile(os.path.join(d, "About", "About.xml"))
    )
    if not mod_dirs:
        print("FAIL  found no mods to check (no src/*/*/About/About.xml)")
        return 1

    failures, checked, unloaded = [], 0, []
    for mod_dir in mod_dirs:
        dups = duplicates_in(mod_dir, unloaded)
        checked += 1
        if dups:
            failures.append((os.path.relpath(mod_dir, REPO), dups))

    for mod, dups in failures:
        print(f"FAIL  {mod}: {len(dups)} def(s) declared more than once")
        for (tag, name), files in sorted(dups.items())[:20]:
            print(f"        <{tag}> {name}")
            for f in sorted(set(files)):
                print(f"            {f}")
        print("      RimWorld keeps the LAST one loaded and the earlier def vanishes")
        print("      silently. Pick a survivor, merge anything the loser carried, and")
        print("      rename or delete the other — see STONEBACK_DEFNAME_COLLISION_1.")

    if unloaded:
        print(f"note  skipped {len(unloaded)} def file(s) under a Source/ tree — RimWorld does "
              f"not load those, so a duplicate there is dead weight, not a live collision. "
              f"Worth deleting anyway (it makes defName measurements over-report): "
              f"{sorted(set(os.path.dirname(u) for u in unloaded))}")

    if failures:
        print(f"\n{checked - len(failures)}/{checked} mods clean, {len(failures)} with duplicates")
        return 1
    print(f"ok    no def declared twice in any of our {checked} loaded mod def trees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
