"""validation.py -- modcheck suite for RimMandrake Patches (mandrake.rm.patches).

Pure-XML patch mod: no `Source/`, no Assemblies, no ModSettings class anywhere
under `src/RimMandrake/MandrakePatches/` (confirmed by directory listing --
only `About/About.xml` and nine files under `Patches/`). Per the briefing's own
rule for this shape: `suite.toggles = []`, every component is
`beyond_toggle=True`.

Read whole before writing this: all nine `Patches/*.xml` files and the walk
doc (`design/validation_walks/RimMandrake/MandrakePatches.md`).

THE REAL TEST-ENVIRONMENT PROBLEM, same family as ResearchRetag's own
docstring, and worse here: EVERY one of the nine patch files is guarded
(`PatchOperationFindMod`/`MayRequire`/`PatchOperationConditional`) on a
specific third-party WORKSHOP mod, and eight of the nine target defs that
belong entirely to that third-party mod -- there is no vanilla/Core fallback
target the way ResearchRetag had five Core rows inside 269 mostly-optional
ones. The walk doc's own header says it outright: `list: full # 9 patches
each target a different third-party mod; only WorldMapReadability_Ashkarr
(targets vanilla Settlement) runs on minimal`. A `modcheck run` composes
MINIMAL + the mod(s) under test (`modcheck.runner.swap_to_test_list`), never
the full list, so on the environment this suite actually runs in, none of
Biomes! Caverns / Star Wars Animal Collection / Insectoids 2 / [BTD] Gravship
Blueprints / Primordial Geysers / Det's Xenotypes - Buzzers / MiningCo.
DrillTurret / GRiNDTerra Biomes / Nals.FacialAnimation+companion / Dark.Signs
is present, so all eight of those patches' own `FindMod`/`Conditional`/
`MayRequire` guards take the no-op branch by design (CLAUDE.md: "a patch that
matches nothing logs nothing" / "PatchOperationConditional ... return[s] true
on no match") and there is nothing live to read back.

THE ONE PATCH THAT IS TESTABLE ON MINIMAL, and the only one this suite
asserts against a live game: `WorldMapReadability_Ashkarr.xml` targets
`WorldObjectDef` `Settlement`, a Core def always present, with a plain
`PatchOperationConditional` (no `MayRequire`) that adds/replaces
`expandingIconDrawSize` to `2` regardless of any third-party mod's presence.
Confirmed by reading the file directly, not guessed.

Still not proven / out of this validator's floor, same register as
ResearchRetag's "out of this validator's floor" note:
  1. The other eight patches' actual EFFECT (dessicated texPath corrections,
     the BTD grammar fix, the dangling-biome-animal removals, the Buzzer
     apostrophe rule fix, the drill turret WorkGiver retype, the nine Sign
     `disableImpassableShotOverConfigError` adds, the FacialAnimation
     `AgeBasedParams` revival) has NO live read-back in this suite at all --
     each needs its own specific Workshop mod added to the test list, which
     `modcheck run` does not do. A full-modlist pass, not this minimal-list
     smoke suite, is the only way to prove any of them; that is out of this
     validator's floor, exactly as ResearchRetag's other ~264 rows are.
  2. Even the NEGATIVE half of those eight -- "on minimal, this patch logs
     nothing and throws no red error" -- is not asserted either. `jawa/
     drain_log` has no built-in way to prove an ABSENCE of a specific
     upcoming line across the whole load (only that a searched string is
     NOT in the last `limit` matching lines, which is a much weaker claim
     than "was never emitted "), so a negative-log component here would be
     asserting something this suite cannot actually rule out. Left
     undone rather than faked; the walk doc's own step 9 flags the same
     gap ("must be run against a KNOWN inactive-mod baseline to be
     meaningful") and no such baseline harness exists yet.
  3. `RRElectricityBasicsSelfPrereq_Fix.xml` is not one of the nine the walk
     doc enumerates (it predates the walk doc, filed under
     QUICKTEST_POSTSETUP_CRASH_1) and is also third-party-guarded
     (`petetimessix.researchreinvented.steppingstones`), so it falls into
     the same "needs full list" bucket as the other eight -- not
     independently proven here either.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("MandrakePatches")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle


@suite.chain("settlement_icon_size")
def settlement_icon_size(t):
    """`WorldMapReadability_Ashkarr.xml`'s one unconditional patch: Core's
    `WorldObjectDef` `Settlement` carries `expandingIconDrawSize=2` (doubling
    the 30px base draw size per `ExpandableWorldObjectsUtility.cs`'s `30f *
    o.def.expandingIconDrawSize`), independent of any third-party mod --
    the ONE check in this mod's whole Patches/ folder that works on a
    minimal-list modcheck run, per the walk doc's own admission."""
    t.clear_area(size=8)   # no map state involved; keeps the runner's
                            # evidence/screenshot machinery uniform

    with t.component("settlement_icon_doubled", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="WorldObjectDef/Settlement",
                          fields="expandingIconDrawSize")
        if t._guard():
            rows = (r or {}).get("defs") or []
            row = rows[0] if rows else None
            got = (row or {}).get("fields", {}).get("expandingIconDrawSize")
            if str(got) != "2":
                raise ExpectationFailed(
                    "WorldObjectDef/Settlement.expandingIconDrawSize = %r, "
                    "expected '2' (WorldMapReadability_Ashkarr.xml's "
                    "unconditional PatchOperationConditional)" % got)
        t.screenshot()
