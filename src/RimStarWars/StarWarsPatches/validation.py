"""validation.py -- modcheck suite for RimStarWars: Patches
(mandrake.rsw.patches).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run StarWarsPatches

No hard `<modDependencies>` at all (About.xml, checked whole -- everything
this mod names is `<loadAfter>`, softly), so the runner's own environment
convention ("minimal + the mod(s) under test") loads NOTHING beyond this
mod itself unless a caller passes extra mod names to `run` alongside it.
See "REAL ENVIRONMENT RISK" below for why that matters more here than for
most mods in this family.

THE WALK DOC (`design/validation_walks/RimStarWars/StarWarsPatches.md`) HAS
TWO CONFIRMED DEFECTS, found by reading the shipped Defs, not assumed:
  1. It is missing an entire absorbed wave. `About.xml`'s own header names
     28 XML-only patches; the CURRENT mod also ships `Defs/Absorbed_
     LumiDoorsExpanded/` (3 concrete blast-door ThingDefs + 2 abstract
     bases + SoundDefs + a ResearchProjectDef, ported from the retired
     `Lumi.doorsexpanded` per `BLASTDOOR_LUMI_PORT_1`, 2026-09-08) and
     several texture-only overrides (Cerean mane fix, Bantha/Behemoth/
     Eopie `swanimals/` art) the walk never mentions at all.
  2. Its Gamorrean defNames are PRE-TIER-RENAME and wrong for the current
     source. Walk steps 13-16 say `Jawa_Gamorrean_Guard`/`_Enforcer` and
     `Jawa_Xeno_Gamorrean`; `Defs/PawnKindDefs/GamorreanPawnKinds.xml` and
     `Defs/XenotypeDefs/GamorreanXenotype.xml` actually ship
     `RSW_Jawa_Gamorrean_Guard`/`RSW_Jawa_Gamorrean_Enforcer` and
     `RSW_Jawa_Xeno_Gamorrean` (the `RSW_` tier prefix, per
     `NAMING_SCHEME_EXECUTION_1`). This suite uses the REAL, current
     defNames.

Given the above, and that [D] def read-back items (the walk's steps 2-27,
nearly the entire document) are covered by the offline def dump / RimSage
rather than this bridge-driven runtime suite -- matching every other suite
in this family -- almost nothing in the walk's own text maps onto a bridge
call at all. This suite instead covers the two mechanisms that are
BEHAVIORAL (something a spawn+read-back can actually observe) and entirely
this mod's OWN content, not a donor's: the absorbed blast doors and the two
Gamorrean `PawnKindDef`s. `suite.toggles = []` -- no `ModSettings`
anywhere (`Source/` holds only two offline Python art-authoring scripts,
`build_frameasync_east.py`/`draw_mane_south.py`; no `.cs`, no `Assemblies/`
at all -- confirmed by a full file listing, not the walk's stale "content-
only" claim taken on faith).

REAL ENVIRONMENT RISK, found by reading the Defs, not the walk (which
claims "zero red XML errors... by construction" for the whole mod, a claim
its own "must be true" section scopes to the `Patches/` folder's
`PatchOperationConditional`/`MayRequire` wrapping -- the NEW `Defs/`
content below is NOT wrapped the same way):
  - The blast-door `ThingDef`s' `thingClass` is `DoorsExpanded.Building_
    DoorExpanded` (`jecrell.doorsexpanded`) with NO `MayRequire` guard, and
    the file's own header names `jecrell.doorsexpanded`/`jecrell.jecstools`
    as "real frameworks this content needs directly now" -- but both are
    only in this mod's `<loadAfter>`, never `<modDependencies>`. On the
    runner's plain minimal environment (StarWarsPatches alone), that class
    will not resolve.
  - `GamorreanPawnKinds.xml`'s `apparelRequired`/`weaponTags` name KotOR
    ThingDefs/tags (`guy762_Clothing_gamorrean`, `guy762_Hat_gamorrean`,
    `guy762_HvyArmor_gamorrean`, `Jawa_GamorreanAxe`, `HC_gamorrean_melee`)
    with NO `MayRequire` guard either, and `guy762.MM.KotORCore`/
    `guy762.KotORWeapons` are likewise `loadAfter`-only.
  Both chains below are written to FAIL LOUDLY and diagnostically if the
  environment lacks these donors, rather than silently passing on a
  degraded outcome or crashing uninterpretably -- a failure here is the
  correct signal to re-run with `jecrell.doorsexpanded`+`jecrell.jecstools`
  (blast doors) or `guy762.MM.KotORCore`+`guy762.KotORWeapons` (Gamorreans)
  included on the CLI's mod list, not evidence this mod's own content is
  broken.

WHAT THIS SUITE CANNOT PROVE, and why:
  - Every `[D]`-tagged walk step (weather commonalities, plant/item label
    renames, gene/xenotype field values, weapon-tag renormalisation, the
    Empire faction's xenotype chances, OuterRim droid `fixedGender`, the
    cross-tier `mandrake.rut.patches` droid check, the vehicle/sound
    relabels, and more) -- covered by the def dump, not here.
  - Walk step 26's Behemoth Player.log check (`Failed to find any textures
    at swanimals/Behemoth/JawaBehemoth_fPack`) and step 9's
    `BuildableDef.ResolveIcon` NRE check are both load-order-dependent
    Player.log absences from a PAST defect, not a mechanism this suite
    triggers -- a clean load already proves them by omission, nothing
    further to assert.
  - Walk step 28 (human pass: Gamorrean art, the wrecked-landspeeder ruin,
    Hutt eye-render-node fix) -- pure visual judgment, deferred the same
    way the walk doc itself defers it.

Still not proven / likely first-live-run corrections:
  1. Whether `jawa/spawn_pawn` on a Gamorrean kind whose `apparelRequired`
     cannot resolve produces a clean Fail(), a pawn generated bare instead,
     or something else entirely (an unhandled `PawnGenerator` exception) --
     not measured; `gamorrean_pawnkinds_spawn_armed` below checks the
     actual result shape defensively rather than assuming one outcome.

TWO MORE ABSORBED WALK DOCS, added VALIDATION_SCRIPT_BACKFILL_1: `design/
validation_walks/RimStarWars/{BlastDoorFrameAsyncFix,CereanManeFix}.md` are
not separate mods -- both carry their own `subject: src/RimStarWars/
StarWarsPatches` + `absorbed:` line (Sprint wave A, commit 7e6eda0bd) -- and
their checklists had NO coverage anywhere, including in the two chains
above (which test the PORTED DEFS from a different absorption,
BLASTDOOR_LUMI_PORT_1, not these two loose-texture fixes). Both fixes'
donor mods (`Lumi.doorsexpanded`, `Neronix17.OuterRim.GalacticDiversity`)
are absent from the minimal test list, so only the shipped-file checks
below are provable here (no load-order, no rendered-facing -- same
limitation as MandrakePatches' five absorbed fixes, same wave). One real
stale-doc number found and fixed in BlastDoorFrameAsyncFix.md itself: it
claimed the donor's/this mod's canvas is 933x933; PIL measurement against
all 6 shipped files this pass says 936x936, corrected in that file.
"""
from modcheck import Suite, ExpectationFailed
import os as _os

suite = Suite("StarWarsPatches")
suite.toggles = []   # no ModSettings anywhere in this mod -- confirmed, no Source/*.cs at all.

# The 3 concrete blast doors this mod ports from the retired Lumi.doorsexpanded
# (Absorbed_Lumi_BlastDoors_ThingDefs.xml) -- defNames preserved verbatim.
BLAST_DOORS = ["PH_DoorThickBlastBDoor", "PH_DoorBlastCDoor", "PH_DoorBlastDDoor"]

# Current, post-tier-rename defNames (GamorreanPawnKinds.xml/GamorreanXenotype.xml) --
# NOT the walk doc's pre-rename Jawa_Gamorrean_Guard/Jawa_Xeno_Gamorrean.
GAMORREAN_GUARD = "RSW_Jawa_Gamorrean_Guard"
GAMORREAN_ENFORCER = "RSW_Jawa_Gamorrean_Enforcer"
GAMORREAN_XENOTYPE = "RSW_Jawa_Xeno_Gamorrean"

_MOD_DIR = _os.path.dirname(_os.path.abspath(__file__))


def _check_png(path, expect_wh=None):
    """Pure repo file check, no bridge call -- PIL against a file on disk.
    Returns an error string, or None if the file passes."""
    if not _os.path.isfile(path):
        return "%s does not exist" % path
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    if expect_wh is not None and im.size != expect_wh:
        return "%s is %r, expected %r" % (path, im.size, expect_wh)
    lo, hi = im.getchannel("A").getextrema()
    if hi == 0:
        return "%s has a uniformly-zero alpha channel (blank/invisible)" % path
    return None


@suite.chain("absorbed_blast_doors_spawn_cleanly")
def absorbed_blast_doors_spawn_cleanly(t):
    """This mod's own ported content (no MayRequire, but needs
    jecrell.doorsexpanded's thingClass to resolve -- see module docstring's
    environment risk). A failure here most likely means that framework is
    not on this run's mod list, not a defect in the ported defs themselves."""
    t.clear_area(size=30)
    x, z = t.anchor
    with t.component("blast_doors_present_after_spawn", beyond_toggle=True):
        for i, defName in enumerate(BLAST_DOORS):
            t.spawn(defName, count=1, at="line")
        r = t.bridge_call("jawa/list_things", rect="%d,%d,20,5" % (x - 2, z - 2))
        if t._guard():
            present = {row.get("def") for row in ((r or {}).get("things") or [])}
            missing = [d for d in BLAST_DOORS if d not in present]
            if missing:
                raise ExpectationFailed(
                    "spawned %r but jawa/list_things is missing %r afterward "
                    "(present: %r) -- most likely jecrell.doorsexpanded (the "
                    "thingClass DoorsExpanded.Building_DoorExpanded needs it, "
                    "and it is only loadAfter, never a hard dependency of this "
                    "mod) is absent from this run's mod list, per module "
                    "docstring's environment risk note" % (BLAST_DOORS, missing, present))
        t.screenshot()


@suite.chain("gamorrean_pawnkinds_spawn_armed")
def gamorrean_pawnkinds_spawn_armed(t):
    """This mod's own PawnKindDefs (GamorreanPawnKinds.xml), but their
    apparelRequired/weaponTags name KotOR ThingDefs/tags with no MayRequire
    guard (module docstring's environment risk). Proves the xenotype wiring
    either way (useFactionXenotypes=false, xenotypeChances={GAMORREAN:1.0}
    is unconditional data on the def) and reports the armed/apparel outcome
    defensively rather than assuming KotOR content is present."""
    t.clear_area(size=20)
    guard = t.spawn_pawn(GAMORREAN_GUARD, hostile=False)
    enforcer = t.spawn_pawn(GAMORREAN_ENFORCER, hostile=False)

    with t.component("gamorrean_xenotype_wired", beyond_toggle=True):
        r = t.bridge_call("jawa/pawn_get", pawn=guard)
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("jawa/pawn_get(%s) failed: %r" % (guard, r))
            row = (r.get("pawns") or [{}])[0]
            if row.get("xenotype") != GAMORREAN_XENOTYPE:
                raise ExpectationFailed(
                    "%s's xenotype read back as %r, expected %r (xenotypeSet/"
                    "xenotypeChances={%r: 1.0} on the def is unconditional -- "
                    "this does not depend on KotOR content at all)"
                    % (guard, row.get("xenotype"), GAMORREAN_XENOTYPE, GAMORREAN_XENOTYPE))
        t.screenshot()

    with t.component("gamorrean_enforcer_apparel_and_weapon", beyond_toggle=True):
        r = t.bridge_call("jawa/pawn_get", pawn=enforcer)
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("jawa/pawn_get(%s) failed: %r" % (enforcer, r))
            row = (r.get("pawns") or [{}])[0]
            apparel_defs = {a.get("def") for a in (row.get("apparel") or [])}
            equipment_defs = {e.get("def") for e in (row.get("equipment") or [])}
            # apparelRequired names guy762_HvyArmor_gamorrean/guy762_Hat_gamorrean;
            # weaponTags names Jawa_GamorreanAxe/HC_gamorrean_melee. Both lists have
            # no MayRequire guard (module docstring) -- if KotOR content is absent,
            # this pawn is expected to generate BARE, which is exactly the risk this
            # suite exists to surface, not hide.
            if not apparel_defs:
                raise ExpectationFailed(
                    "%s generated with NO worn apparel at all -- apparelRequired "
                    "[guy762_HvyArmor_gamorrean, guy762_Hat_gamorrean] could not be "
                    "satisfied. Most likely guy762.MM.KotORCore is absent from "
                    "this run's mod list (see module docstring's environment risk)."
                    % enforcer)
            if not equipment_defs:
                raise ExpectationFailed(
                    "%s generated with NO equipped weapon -- weaponTags "
                    "[Jawa_GamorreanAxe, HC_gamorrean_melee] found nothing to "
                    "equip. Most likely guy762.MM.KotORCore/guy762.KotORWeapons "
                    "is absent from this run's mod list (see module docstring's "
                    "environment risk) -- this is also the exact historical bug "
                    "(weapon_tag_audit.py, 2026-08-19) this pawnkind's own "
                    "comments say Jawa_GamorreanAxe was added to fix." % enforcer)
        t.screenshot()


@suite.chain("blastdoorframeasyncfix_textures")
def blastdoorframeasyncfix_textures(t):
    """Absorbed walk doc: BlastDoorFrameAsyncFix.md (Doors Expanded Star
    Wars edition, third-party donor absent from minimal). 6 shipped PNGs
    (3 doors x east + eastm), all measured this pass at 936x936 with
    non-zero alpha -- corrects the walk doc's own stale 933x933 claim (see
    module docstring). No donor-parity or built-door-in-game check here."""
    blast_dir = _os.path.join(_MOD_DIR, "Textures", "Things", "Building",
                              "Door", "Blast")
    files = [
        "SWDoorBlastDoor_FrameAsync_east.png",
        "SWDoorBlastDoor_FrameAsync_eastm.png",
        "SWDoorBlastBDoor_FrameAsync_east.png",
        "SWDoorBlastBDoor_FrameAsync_eastm.png",
        "SWDoorBlastDDoor_FrameAsync_east.png",
        "SWDoorBlastDDoor_FrameAsync_eastm.png",
    ]
    with t.component("six_frameasync_east_pngs_present_936_nonblank",
                     beyond_toggle=True):
        errs = [e for f in files
                for e in [_check_png(_os.path.join(blast_dir, f), (936, 936))]
                if e]
        if errs:
            raise ExpectationFailed("; ".join(errs))


@suite.chain("cereanmanefix_texture")
def cereanmanefix_texture(t):
    """Absorbed walk doc: CereanManeFix.md (Outer Rim - Galactic Diversity,
    third-party donor absent from minimal). One shipped PNG, measured this
    pass: CereanMane_south.png, 512x512, non-zero alpha -- matches the walk
    doc's own claimed canvas exactly. No donor-parity or rendered-hair
    check here (needs the donor's AssetBundle and a live Cerean pawn)."""
    path = _os.path.join(_MOD_DIR, "Textures", "OuterRim", "Hairs", "Cerean",
                         "CereanMane_south.png")
    with t.component("cerean_mane_south_present_512_nonblank",
                     beyond_toggle=True):
        err = _check_png(path, (512, 512))
        if err:
            raise ExpectationFailed(err)
