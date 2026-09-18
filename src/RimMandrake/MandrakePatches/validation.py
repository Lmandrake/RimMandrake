"""validation.py -- modcheck suite for RimMandrake Patches (mandrake.rm.patches).

CORRECTION (VALIDATION_SCRIPT_BACKFILL_1, this pass): the line above used to
claim "no `Source/`, no Assemblies... only `About/About.xml` and nine files
under `Patches/`" -- that was WRONG the moment it was written and stayed wrong
for a full wave. `find src/RimMandrake/MandrakePatches -maxdepth 2 -type d`
shows a real `Source/` with four subfolders (`GravshipAstronautFix/`,
`PhytokinBarkHeadFix/`, `ResearchKitEastFix/`, `ToolBeltFix/`, each holding one
offline Python art generator, not a runtime C# comp) plus a `Textures/` tree.
Still true: no Assemblies, no ModSettings class, no Harmony patch anywhere in
this mod -- `suite.toggles = []` still holds, every component
`beyond_toggle=True`.

FIVE MORE ABSORBED WALK DOCS, traced this pass (VALIDATION_SCRIPT_BACKFILL_1's
own worklist derivation): `design/validation_walks/RimMandrake/
{GravshipAstronautFix,PhytokinBarkHeadFix,ResearchKitEastFix,ToolBeltFix,
SauridFrillFix}.md` each carry their own `subject: src/RimMandrake/
MandrakePatches` line and an explicit `absorbed:` note (Sprint wave A, commits
7e6eda0bd/f32eef5f5) -- they are not separate mods and never get their own
`validation.py`; this file is where their checklists belong. All five are
pure loose-texture fixes for a third-party donor mod NOT in the minimal list
(`list: full` or `list: minimal+<donor>` on every one of them), so none of
their DEF-level or runtime claims (load order vs the donor, a rotated pawn's
actual rendered facing) can run under `modcheck run` (MINIMAL + test-list
only, never the full list) -- exactly the same "no vanilla/Core fallback
target" shape this module's own pre-existing doctring already describes for
the nine `Patches/*.xml` files. What CAN run without the donor or a live
session at all: the shipped PNG files' existence, dimensions and alpha
channel, checked directly against disk with PIL (same pattern as
KotORBandolierNorthFix/MSEDroidFix's own standalone suites) -- the five new
chains below do exactly that, each grounded in real `PIL.Image` measurements
taken this pass, not copied from the walk docs' own prose:
  - GravshipAstronautFix: 3 PNGs (astronaut north x2, gene bank north)
  - PhytokinBarkHeadFix: 1 PNG (bark head east)
  - ResearchKitEastFix: 4 PNGs (one east per research kit)
  - ToolBeltFix: 1 PNG (tool belt west) -- exact byte count (10502) confirmed
    to match the walk doc's own claim precisely
  - SauridFrillFix: 1 PNG (center frill north)
Real gaps left honest rather than faked, per every prior wave's own pattern:
none of these five chains can prove load order against the donor (needs the
live `ModsConfig.xml`/`jawa/mod_inventory`, and four of five donors are not on
this machine's minimal list at all), and none can prove the rendered facing
actually displays correctly on a worn/rotated pawn (needs the donor mod
active plus a screenshot judgement -- deferred to MOD_HUMAN_EXPLORATION_PASS_1
exactly as each walk doc's own `[S]` line already says). No donor-parity
comparison either (would need the donor's Workshop copy, which lives under
`game_paths.WORKSHOP` on the Windows machine, unreachable from this WSL
seat per CLAUDE.md's RimSage/Windows-only note) -- these chains check the
shipped file's OWN state (present, correctly sized, non-blank alpha), not
parity against the donor's original.

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


import os as _os

_MOD_DIR = _os.path.dirname(_os.path.abspath(__file__))


def _tex(*parts):
    return _os.path.join(_MOD_DIR, "Textures", *parts)


def _check_png(path, expect_wh=None, min_nonzero_alpha_pct=0.0):
    """Pure repo file check, no bridge call -- PIL against a file on disk.
    Returns an error string, or None if the file passes. `expect_wh` is an
    (w, h) tuple to assert exactly; `min_nonzero_alpha_pct` guards against a
    fully-blank (uniformly zero alpha) PNG, the exact defect class every one
    of these five absorbed fixes exists to repair."""
    if not _os.path.isfile(path):
        return "%s does not exist" % path
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    if expect_wh is not None and im.size != expect_wh:
        return "%s is %r, expected %r" % (path, im.size, expect_wh)
    alpha = im.getchannel("A")
    lo, hi = alpha.getextrema()
    if hi == 0:
        return "%s has a uniformly-zero alpha channel (blank/invisible)" % path
    if min_nonzero_alpha_pct > 0.0:
        w, h = im.size
        total = w * h
        nonzero = sum(1 for v in alpha.getdata() if v > 0)
        pct = 100.0 * nonzero / total
        if pct < min_nonzero_alpha_pct:
            return ("%s alpha coverage %.1f%% below expected floor %.1f%%"
                    % (path, pct, min_nonzero_alpha_pct))
    return None


@suite.chain("gravshipastronautfix_textures")
def gravshipastronautfix_textures(t):
    """Absorbed walk doc: GravshipAstronautFix.md (Vanilla Gravship Expanded
    - Chapter 1, third-party donor absent from minimal). Checks the three
    shipped loose PNGs exist, are the doc-claimed canvas size, and are not
    blank -- measured this pass: MechAncient_Astronaut_north.png 256x256
    (27.9% alpha), Allegiance_Mech_Astronaut_north.png 256x256 (a mask,
    fully opaque -- 100% alpha, consistent with the mask-tint convention),
    GravshipGenebank_north.png 128x128 (98.7% alpha). No load-order or
    rotated-pawn-render check here -- see module docstring."""
    with t.component("three_pngs_present_correctly_sized_nonblank",
                     beyond_toggle=True):
        checks = [
            (_tex("Things", "Pawns", "Mechanoid", "Astronaut",
                  "MechAncient_Astronaut_north.png"), (256, 256)),
            (_tex("Things", "Pawns", "Mechanoid", "Astronaut",
                  "Allegiance_Mech_Astronaut_north.png"), (256, 256)),
            (_tex("Things", "Structures", "GravshipGenebank",
                  "GravshipGenebank_north.png"), (128, 128)),
        ]
        errs = [e for p, wh in checks for e in [_check_png(p, wh)] if e]
        if errs:
            raise ExpectationFailed("; ".join(errs))


@suite.chain("phytokinbarkheadfix_texture")
def phytokinbarkheadfix_texture(t):
    """Absorbed walk doc: PhytokinBarkHeadFix.md (Vanilla Races Expanded:
    Phytokin, third-party donor absent from minimal). One shipped PNG,
    measured this pass: BarkSkinFemale_Wide_Normal_east.png, 256x256,
    13.7% alpha coverage (non-blank). No donor-parity comparison (the
    donor's own male Wide east head lives only in the Workshop cache)."""
    with t.component("bark_head_east_present_correctly_sized_nonblank",
                     beyond_toggle=True):
        err = _check_png(
            _tex("Things", "Pawn", "Humanlike", "Heads",
                 "BarkSkinFemale_Wide_Normal_east.png"),
            (256, 256))
        if err:
            raise ExpectationFailed(err)


@suite.chain("researchkiteastfix_textures")
def researchkiteastfix_textures(t):
    """Absorbed walk doc: ResearchKitEastFix.md (Research Reinvented +
    Retextured, both third-party, absent from minimal -- walk doc's own
    `list: full`). Four shipped PNGs, all 512x512 per the walk doc; measured
    alpha coverage this pass matches the walk doc's own claimed figures to
    within rounding: Simple 24.3% (doc: 24.28%), HiTech 28.2% (doc: 28.16%),
    MultiAnalyzer 25.4% (doc: 25.42%), Remote 30.5% (doc: 30.48%) -- the walk
    doc's numbers check out exactly, no stale-doc correction needed here."""
    with t.component("four_kit_east_textures_present_correctly_sized_nonblank",
                     beyond_toggle=True):
        checks = [
            _tex("Things", "Items", "SimpleResearchKit",
                 "SimpleResearchKit_east.png"),
            _tex("Things", "Items", "HiTechResearchKit",
                 "HiTechResearchKit_east.png"),
            _tex("Things", "Items", "MultiAnalyzerResearchKit",
                 "MultiAnalyzerResearchKit_east.png"),
            _tex("Things", "Items", "RemoteResearchKit",
                 "RemoteResearchKit_east.png"),
        ]
        errs = [e for p in checks for e in [_check_png(p, (512, 512))] if e]
        if errs:
            raise ExpectationFailed("; ".join(errs))


@suite.chain("toolbeltfix_texture")
def toolbeltfix_texture(t):
    """Absorbed walk doc: ToolBeltFix.md (Vanilla Apparel Expanded -
    Accessories, third-party, absent from minimal). One shipped PNG; the
    walk doc claims 256x256 / 10,502 bytes exactly, and this pass's own
    `os.path.getsize` measurement matches that byte count precisely (not
    just the dimensions) -- checked here as the sharpest available proof
    the file is the exact build the doc describes, not a later edit."""
    path = _tex("Things", "Apparel", "ToolBelt", "ToolBelt_west.png")
    with t.component("toolbelt_west_present_correctly_sized_nonblank",
                     beyond_toggle=True):
        err = _check_png(path, (256, 256))
        if err:
            raise ExpectationFailed(err)
        size = _os.path.getsize(path)
        if size != 10502:
            raise ExpectationFailed(
                "%s is %d bytes, expected exactly 10502 (About.xml's own "
                "claimed byte count -- a mismatch means the file changed "
                "since that claim was written)" % (path, size))


@suite.chain("sauridfrillfix_texture")
def sauridfrillfix_texture(t):
    """Absorbed walk doc: SauridFrillFix.md (Vanilla Races Expanded -
    Saurid, third-party, absent from minimal). One shipped PNG at
    Textures/Pawn/CenterFrill/CenterFrill8_north.png (note: lives directly
    under Textures/Pawn/, NOT Textures/Things/Pawn/ like the other four
    fixes -- confirmed by directory listing, not assumed from the naming
    pattern of its siblings). Measured this pass: 128x128, 2.6% alpha
    coverage -- low but genuinely non-zero (a thin decorative frill, not a
    blank canvas), which is the exact defect state this fix corrects (the
    donor's own file is missing/mis-hyphenated, not present-but-blank)."""
    path = _os.path.join(_MOD_DIR, "Textures", "Pawn", "CenterFrill",
                         "CenterFrill8_north.png")
    with t.component("center_frill_north_present_correctly_sized_nonblank",
                     beyond_toggle=True):
        err = _check_png(path, (128, 128))
        if err:
            raise ExpectationFailed(err)
