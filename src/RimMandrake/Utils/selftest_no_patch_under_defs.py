#!/usr/bin/env python3
"""Selftest: no `<Patch>`-rooted XML file sits under a `Defs/` path in `src/`.

`PATCH_FILES_UNDER_DEFS_INERT_1` — RimWorld loads everything under a mod's
`Defs/` folder AS A DEF. A file whose root element is `<Patch>` placed there is
parsed by the def loader, which logs `Type PatchOperationX is not a Def type or
could not be found` once and then silently drops every operation in the file.
No crash, no red error after the first line, no signal that anything is wrong —
the mod just quietly loses whatever that patch was supposed to do.

Two files shipped this way for weeks before it was caught: `DryingBiomes.xml`
(GelatinousSlime's whole cure-geography mechanic) and
`WreckedMachines_HideDonorSmelter.xml` (an owner ruling from 2026-09-16 that
had been a no-op since the day it was "shipped"). Both are correct XML — the
defect was purely which folder they sat in.

WHAT THIS TESTS
----------------
Parses every `*.xml` file under `src/` whose path has a `Defs` path component,
and fails if any of them has a root element `<Patch>`. That is the exact
signature of the bug: it is not "mentions PatchOperation" (~20 files do, and
almost all of them are ordinary def files using it inline as a nested element
inside a legitimate Def) — it is the file's OWN root tag.

    python3 selftest_no_patch_under_defs.py
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")

PASS: list = []
FAIL: list = []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as ex:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, ex))
    except Exception as ex:                                        # noqa: BLE001
        FAIL.append(name)
        print("ERROR %s\n        %s: %s" % (name, type(ex).__name__, ex))


def _find_patch_files_under_defs():
    """Return the sorted list of repo-relative paths violating the rule."""
    hits = []
    for dirpath, _dirnames, filenames in os.walk(SRC):
        rel_dir = os.path.relpath(dirpath, REPO)
        parts = rel_dir.split(os.sep)
        if "Defs" not in parts:
            continue
        for fname in filenames:
            if not fname.lower().endswith(".xml"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                root = ET.parse(fpath).getroot()
            except ET.ParseError:
                # Not well-formed XML is a different problem; not this test's job.
                continue
            if root.tag == "Patch":
                hits.append(os.path.relpath(fpath, REPO))
    return sorted(hits)


def t_no_patch_rooted_xml_sits_under_a_defs_path():
    hits = _find_patch_files_under_defs()
    assert not hits, (
        "%d file(s) with a <Patch> root sit under a Defs/ path, where the def "
        "loader parses them as an inert Def instead of the game applying them "
        "as a patch: %s — move each to the mod's top-level Patches/ folder "
        "(see PATCH_FILES_UNDER_DEFS_INERT_1)" % (len(hits), ", ".join(hits))
    )


def t_the_two_known_fixed_files_are_where_they_belong():
    """Guards the specific regression, not just the general rule."""
    must_exist = [
        "src/RimMandrake/GelatinousSlime/Patches/DryingBiomes.xml",
        "src/RimMandrake/WreckedMachines/Patches/WreckedMachines_HideDonorSmelter.xml",
    ]
    must_not_exist = [
        "src/RimMandrake/GelatinousSlime/Defs/Patches/DryingBiomes.xml",
        "src/RimMandrake/WreckedMachines/Defs/Patches/WreckedMachines_HideDonorSmelter.xml",
    ]
    for rel in must_exist:
        assert os.path.isfile(os.path.join(REPO, rel)), (
            "%s is missing — expected at the mod's top-level Patches/" % rel
        )
    for rel in must_not_exist:
        assert not os.path.isfile(os.path.join(REPO, rel)), (
            "%s still exists — the old inert copy under Defs/ was not removed" % rel
        )


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.startswith("t_"):
            case(k[2:], v)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
