#!/usr/bin/env python3
"""Selftest for gen_jds_armory_absorption.py and gen_kotorweapons_absorption.py
(WEAPONS_ABSORPTION_WAVE_1).

Both generators claim idempotency in their own docstrings ("re-running
overwrites the same generated Defs/ files... nothing here reads its own
prior output" / "collision-checks against existing defNames EXCLUDE this
generator's own output directory... a rerun never treats its own prior run
as a foreign pack") and that claim was proven this session by a MANUAL
rerun against the real Workshop folder. A claim that is only ever checked
by a human remembering to rerun a generator by hand is exactly the kind of
thing `selftest_*.py` exists to lock in (see
src/RimMandrake/Utils/selftest_validate_patch.py for why this pattern
exists at all: the same bug class shipped twice because a fix was never
backed by a test).

HOW THIS TESTS TWO SCRIPTS THAT HARD-CODE THEIR OWN WORKSHOP PATHS:
Neither generator takes a CLI argument or reads an env var for its source
folder or output root - both are plain module-level constants
(WORKSHOP_FOLDER, SRC_DEFS, ARMOURY_ROOT, DEFS_ROOT, ...) read directly by
main() and its helpers at call time, not at import time and not captured
into closures. That means they ARE unit-testable without editing either
script (which this item explicitly forbids while WEAPONS_ABSORPTION_WAVE_1
is mid-flight in this same directory tree): import each module, monkeypatch
its path constants to point at a throwaway fixture + a throwaway tmp output
tree, then call main() directly. Nothing under this repo's real
src/Jawa/Jawa_Armoury/ is ever touched - every patched constant points
outside it.

WHAT IS CHECKED, PER GENERATOR:
  1. main() runs cleanly against a small fixture (one real ThingDef/defName)
     without touching the real Workshop folder or the real Jawa_Armoury/Defs.
  2. IDEMPOTENCY: running main() a second time against the SAME tmp output
     tree produces byte-identical output - the real regression this test
     guards, since a self-collision bug would make the second run either
     drop the def (false "already absorbed") or emit a warning it didn't
     emit the first time.
  3. DEFNAME PRESERVATION: the fixture's defName appears verbatim in the
     written output, both runs.

WHAT THIS DOES NOT COVER: the real Workshop XML's actual shape (78 files,
1235-def kotorcore abstracts, the namespace-rewrite table, the blocked-class
filter, texture/sound copying) - this fixture is deliberately minimal. It
proves the RERUN-SAFETY mechanism (the OWN_OUTPUT_PREFIX / own-output-dir
exclusion), not full-scale correctness against the live pack, which needs
the real Workshop folder and is what the manual rerun this session already
checked once.

    python3 selftest_absorption_generators.py
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

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
    except Exception as ex:                                       # noqa: BLE001
        FAIL.append(name)
        print("ERROR %s\n        %s: %s" % (name, type(ex).__name__, ex))


def _load_module_fresh(path, name):
    """Import a throwaway copy of the generator module under a private name,
    so patching its globals never touches a shared/cached module object and
    two generators (or two test runs) never see each other's monkeypatches."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# gen_jds_armory_absorption.py: SOURCE_FILES is a fixed list of 5 filenames
# main() reads unconditionally, so the fixture must supply all 5 (most can
# be an empty <Defs></Defs> - only one needs a real defName to prove
# anything).
# ---------------------------------------------------------------------------
def _jds_fixture(root):
    about = ('<?xml version="1.0" encoding="utf-8" ?>\n<ModMetaData>\n'
              '  <packageId>m3.continued.jangodsoul.starwars.bti</packageId>\n'
              '</ModMetaData>\n')
    _write(os.path.join(root, "About", "About.xml"), about)
    _write(os.path.join(root, "1.6", "Defs", "ThingDefs_Weapon.xml"),
           '<?xml version="1.0" encoding="utf-8" ?>\n<Defs>\n'
           '  <ThingDef>\n    <defName>SelftestFixture_JDS_Weapon_1</defName>\n'
           '    <label>selftest fixture weapon</label>\n  </ThingDef>\n</Defs>\n')
    for fn in ("ThingDefs_Projectile.xml", "ThingDefs_Hediff.xml",
               "Buildings_Production.xml", "LaserSounds.xml"):
        _write(os.path.join(root, "1.6", "Defs", fn),
               '<?xml version="1.0" encoding="utf-8" ?>\n<Defs>\n</Defs>\n')


def _run_jds_generator_once(armoury_root, fixture_root):
    mod = _load_module_fresh(
        os.path.join(HERE, "gen_jds_armory_absorption.py"), "_selftest_jds_gen")
    mod.WORKSHOP_FOLDER = fixture_root
    mod.SRC_DEFS = os.path.join(fixture_root, "1.6", "Defs")
    mod.SRC_TEX = os.path.join(fixture_root, "Common", "Textures")
    mod.SRC_SOUND = os.path.join(fixture_root, "Common", "Sounds")
    mod.ARMOURY_ROOT = armoury_root
    mod.DEFS_ROOT = os.path.join(armoury_root, "Defs")
    mod.TEX_ROOT = os.path.join(armoury_root, "Textures")
    mod.SOUND_ROOT = os.path.join(armoury_root, "Sounds")
    mod.main()
    return mod


def t_jds_generator_writes_the_fixture_defName():
    tmp = tempfile.mkdtemp(prefix="selftest_jds_")
    try:
        fixture = os.path.join(tmp, "workshop")
        armoury = os.path.join(tmp, "armoury")
        _jds_fixture(fixture)
        _run_jds_generator_once(armoury, fixture)
        out = os.path.join(armoury, "Defs", "ThingDefs", "Absorbed_JDSArmory_Weapons.xml")
        assert os.path.isfile(out), "expected output file was not written: %s" % out
        assert "SelftestFixture_JDS_Weapon_1" in _read(out), \
            "the fixture's defName must appear verbatim in the generated output"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_jds_generator_is_idempotent_on_rerun():
    tmp = tempfile.mkdtemp(prefix="selftest_jds_idem_")
    try:
        fixture = os.path.join(tmp, "workshop")
        armoury = os.path.join(tmp, "armoury")
        _jds_fixture(fixture)
        out = os.path.join(armoury, "Defs", "ThingDefs", "Absorbed_JDSArmory_Weapons.xml")

        _run_jds_generator_once(armoury, fixture)
        first = _read(out)

        second_mod = _run_jds_generator_once(armoury, fixture)
        second = _read(out)

        # Content-diff alone has a blind spot: write_defs_file() no-ops
        # (`if not elements: return`) when every def got dropped, so a
        # self-collision bug that drops the WHOLE file's worth of defs on
        # rerun leaves the stale first-run content on disk untouched and
        # LOOKS byte-identical. Proven by deliberately disabling the
        # exclusion during this file's own development: content matched,
        # but a WARN "COLLIDES with already-absorbed" fired and 0 defs were
        # written on the second run. So idempotency also requires a clean
        # second run: zero collision warnings.
        assert not second_mod.R.warns, (
            "a second run against the same output tree raised warning(s) - "
            "%r - a truly idempotent rerun should raise none; a self-"
            "collision bug can make the file LOOK byte-identical (see this "
            "check's own comment) while silently dropping every def instead"
            % second_mod.R.warns)
        assert first == second, (
            "rerunning gen_jds_armory_absorption.py against the same output tree "
            "produced DIFFERENT content - the own-output-prefix exclusion "
            "(OWN_OUTPUT_PREFIX) that is supposed to make this idempotent is not "
            "working")
        assert "SelftestFixture_JDS_Weapon_1" in second, \
            "defName must survive a second run too, not be dropped as a false collision"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# gen_kotorweapons_absorption.py: walks SRC_DEFS with os.walk, so the
# fixture just needs SOME .xml file(s) under it - no fixed filename list.
# ---------------------------------------------------------------------------
def _kotor_fixture(root):
    about = ('<?xml version="1.0" encoding="utf-8" ?>\n<ModMetaData>\n'
              '  <packageId>guy762.KotORWeapons</packageId>\n'
              '</ModMetaData>\n')
    _write(os.path.join(root, "About", "About.xml"), about)
    _write(os.path.join(root, "1.6", "Defs", "Items", "TestItems.xml"),
           '<?xml version="1.0" encoding="utf-8" ?>\n<Defs>\n'
           '  <ThingDef>\n    <defName>SelftestFixture_Kotor_Item_1</defName>\n'
           '    <label>selftest fixture item</label>\n  </ThingDef>\n</Defs>\n')


def _run_kotor_generator_once(armoury_root, fixture_root, kotorcore_fallback_root):
    mod = _load_module_fresh(
        os.path.join(HERE, "gen_kotorweapons_absorption.py"), "_selftest_kotor_gen")
    mod.WORKSHOP_FOLDER = fixture_root
    mod.SRC_DEFS = os.path.join(fixture_root, "1.6", "Defs")
    mod.SRC_TEX = os.path.join(fixture_root, "Textures")
    mod.KOTORCORE_FOLDER = kotorcore_fallback_root
    mod.SRC_TEX_FALLBACK = os.path.join(kotorcore_fallback_root, "Textures")
    mod.ARMOURY_ROOT = armoury_root
    mod.DEFS_ROOT = os.path.join(armoury_root, "Defs")
    mod.TEX_ROOT = os.path.join(armoury_root, "Textures")
    mod.main()
    return mod


def t_kotor_generator_writes_the_fixture_defName():
    tmp = tempfile.mkdtemp(prefix="selftest_kotor_")
    try:
        fixture = os.path.join(tmp, "workshop")
        kotorcore_fallback = os.path.join(tmp, "kotorcore")  # empty, never used
        armoury = os.path.join(tmp, "armoury")
        _kotor_fixture(fixture)
        _run_kotor_generator_once(armoury, fixture, kotorcore_fallback)
        out = os.path.join(armoury, "Defs", "Absorbed_KotorWeapons", "Items",
                            "Absorbed_KotorWeapons_TestItems.xml")
        assert os.path.isfile(out), "expected output file was not written: %s" % out
        assert "SelftestFixture_Kotor_Item_1" in _read(out), \
            "the fixture's defName must appear verbatim in the generated output"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_kotor_generator_is_idempotent_on_rerun():
    tmp = tempfile.mkdtemp(prefix="selftest_kotor_idem_")
    try:
        fixture = os.path.join(tmp, "workshop")
        kotorcore_fallback = os.path.join(tmp, "kotorcore")
        armoury = os.path.join(tmp, "armoury")
        _kotor_fixture(fixture)
        out = os.path.join(armoury, "Defs", "Absorbed_KotorWeapons", "Items",
                            "Absorbed_KotorWeapons_TestItems.xml")

        _run_kotor_generator_once(armoury, fixture, kotorcore_fallback)
        first = _read(out)

        second_mod = _run_kotor_generator_once(armoury, fixture, kotorcore_fallback)
        second = _read(out)

        # See the matching comment in t_jds_generator_is_idempotent_on_rerun:
        # a content diff alone cannot catch a self-collision bug that drops
        # every def, because write_defs_file() then no-ops and leaves the
        # stale first-run file untouched - so also require zero warnings.
        assert not second_mod.R.warns, (
            "a second run against the same output tree raised warning(s) - %r - "
            "a truly idempotent rerun should raise none" % second_mod.R.warns)
        assert first == second, (
            "rerunning gen_kotorweapons_absorption.py against the same output "
            "tree produced DIFFERENT content - the own-output-dir exclusion "
            "(OUT_SUBDIR carved out of existing_defnames_in) that is supposed "
            "to make this idempotent is not working")
        assert "SelftestFixture_Kotor_Item_1" in second, \
            "defName must survive a second run too, not be dropped as a false collision"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.startswith("t_"):
            case(k[2:], v)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
