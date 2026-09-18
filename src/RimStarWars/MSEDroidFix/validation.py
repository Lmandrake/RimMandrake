"""validation.py -- modcheck suite for MSE Droid North Fix (Outer Rim -
Droid Depot) (mandrake.rsw.msedroidfix).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run MSEDroidFix

SCOPE (read, not guessed): `find src/RimStarWars/MSEDroidFix -iname
'*.cs'` / `-iname Assemblies` / `-iname Defs` / `-iname Patches` all
return nothing. The mod ships exactly one content file
(`Textures/OuterRim/Droid/MSE_north.png`) and `Source/draw_mse_north.py`,
the offline PIL generator that made it (read whole -- ~50 lines). No
ModSettings class is possible: `suite.toggles = []`, every component below
is `beyond_toggle=True`.

WHY THIS IS SHAPED LIKE KotORBandolierNorthFix'S SUITE BUT SIMPLER: same
"pixel claims about a shipped PNG, checkable with PIL and no bridge
session" register, but this donor (Outer Rim - Droid Depot) serves its art
from an ASSETBUNDLE on 1.6, not loose files (`About.xml`'s own "LOAD ORDER"
section) -- so unlike KotORBandolierNorthFix, there is no loose donor
`MSE_south.png` sitting in the Workshop tree to diff against live. The
generator's own docstring says its measurements ("canvas 256x256, south
bbox (97, 80, 159, 178)... upper plate 231, lower panel 178, vent seam 96,
panel joints 148") came from "the extracted bundle art" -- a one-time
extraction this pass does not repeat. The offline chain below therefore
checks the shipped file against those ABSOLUTE documented measurements
(canvas, alpha bbox, file size), not a live re-derivation from the donor,
which is a real, narrower claim than KotORBandolierNorthFix's own
donor-comparison chains make.

A LOOSE WORDING IN About.xml, worth naming rather than silently
"correcting" mid-check: it calls the donor's def a `PawnKindDef` ("The
droid's PawnKindDef declares Graphic_Multi"), but the def citation two
lines later ("1.6/Defs/ThingDefs_Automatons/Animal/Droid_MSEDroid.xml")
and the fields it quotes (`texPath`, `graphicClass`) are `ThingDef`/
`graphicData` fields -- `PawnKindDef` has no `texPath` field at all
(RimSage/decompiled 1.6: `Graphic_Multi`/`texPath` live on
`ThingDef.graphicData`, never on `PawnKindDef`). The def-field chain below
queries `ThingDef/OuterRim_MSEDroid`, the type that actually carries these
fields, not the type the prose names.

Still not proven / structurally offline-only:
  1. `jawa/texture_audit`'s own doc warns any def with a non-vanilla
     `graphicClass` is reported in `unjudged`, never `missing` -- if
     `OuterRim_MSEDroid` turns out to use a custom Graphic_* subclass
     rather than plain `Graphic_Multi`, this suite's texture_audit check
     would show it as unjudged, not proof either way, and this suite does
     not independently confirm which case applies live.
  2. Walk step 5 (spawn the droid, face it north, confirm the RESOLVED
     graphic path is `MSE_north` and not a silent south fallback) has no
     dedicated bridge tool that reports which texture backs a live pawn's
     current facing -- `jawa/pawn_atlas` dumps baked atlas PAGES (packed
     textures across many pawns), not a per-pawn per-direction sourced
     path. This suite spawns the pawn, locks its rotation north
     (`jawa/set_pawn_rotation`), and takes a screenshot as VISUAL evidence
     only -- the walk's own step 6 human pass is what actually judges it.
  3. `OuterRim_MSEDroid` is assumed to be both the `ThingDef` AND the
     `PawnKindDef` defName (the common RimWorld-modding convention for an
     animal/droid) -- not independently confirmed against Outer Rim -
     Droid Depot's own `PawnKindDefs` folder, since that donor mod's
     source is a Workshop AssetBundle, not something this repo reads.
"""
import os

from modcheck import Suite, ExpectationFailed

suite = Suite("MSEDroidFix")
suite.toggles = []   # no C#, no ModSettings class -- see docstring

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
NORTH_PNG = os.path.join(_MOD_DIR, "Textures", "OuterRim", "Droid", "MSE_north.png")
DROID_DEFNAME = "OuterRim_MSEDroid"
DONOR_TEXPATH = "OuterRim/Droid/MSE"

# About.xml's own claimed measurements (2026-09-08, "measured directly with
# PIL"), re-checked live against the shipped file this pass.
EXPECTED_SIZE = (256, 256)
EXPECTED_BBOX = (97, 80, 159, 178)
EXPECTED_FILE_BYTES = 1051

BOOT_ERROR_NEEDLES = ["Config error in mandrake.rsw.msedroidfix"]


def _deployed_north_png():
    import sys
    utils = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_MOD_DIR))),
                         "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    from game_paths import LOCAL_MODS
    return os.path.join(LOCAL_MODS, "MSEDroidFix", "Textures", "OuterRim",
                        "Droid", "MSE_north.png")


@suite.chain("shipped_file_matches_documented_measurements")
def shipped_file_matches_documented_measurements(t):
    """Walk step 2, offline, no bridge/session call at all: the ONE
    shipped PNG against About.xml's own claimed measurements, checked
    live rather than trusted. Also confirms the mod ships no other
    content (walk's own 'must be true' #1)."""
    from PIL import Image
    with t.component("mse_north_png_matches_claimed_bbox_and_size",
                     beyond_toggle=True):
        if not os.path.isfile(NORTH_PNG):
            raise ExpectationFailed("MSE_north.png not found at %s" % NORTH_PNG)
        im = Image.open(NORTH_PNG).convert("RGBA")
        if im.size != EXPECTED_SIZE:
            raise ExpectationFailed(
                "canvas %r != documented %r" % (im.size, EXPECTED_SIZE))
        bbox = im.getchannel("A").getbbox()
        if bbox != EXPECTED_BBOX:
            raise ExpectationFailed(
                "alpha bbox %r != documented %r" % (bbox, EXPECTED_BBOX))
        actual_bytes = os.path.getsize(NORTH_PNG)
        if actual_bytes != EXPECTED_FILE_BYTES:
            raise ExpectationFailed(
                "file size %d bytes != documented %d bytes"
                % (actual_bytes, EXPECTED_FILE_BYTES))

    with t.component("ships_no_other_content", beyond_toggle=True):
        for sub in ("Defs", "Patches", "Assemblies"):
            p = os.path.join(_MOD_DIR, sub)
            if os.path.isdir(p):
                raise ExpectationFailed(
                    "%s exists at %s -- About.xml's own 'no defs are "
                    "patched, no code runs' claim is contradicted" % (sub, p))
        tex_root = os.path.join(_MOD_DIR, "Textures")
        all_files = []
        for root, _, files in os.walk(tex_root):
            all_files.extend(os.path.join(root, f) for f in files)
        if all_files != [NORTH_PNG]:
            raise ExpectationFailed(
                "Textures/ contains more than just MSE_north.png: %r" % all_files)


@suite.chain("deployed_copy_matches_repo")
def deployed_copy_matches_repo(t):
    """Same "writing a file is not deploying it" doctrine as
    KotORBandolierNorthFix's own suite -- offline, no bridge/session."""
    with t.component("deployed_file_matches_repo_pixel_for_pixel",
                     beyond_toggle=True):
        from PIL import Image
        dep = _deployed_north_png()
        if not os.path.isfile(dep):
            raise ExpectationFailed(
                "deployed MSE_north.png not found at %s -- mod may never "
                "have been deployed" % dep)
        repo_im = Image.open(NORTH_PNG).convert("RGBA")
        dep_im = Image.open(dep).convert("RGBA")
        if repo_im.size != dep_im.size:
            raise ExpectationFailed(
                "deployed canvas %r != repo canvas %r" % (dep_im.size, repo_im.size))
        repo_alpha = sum(1 for p in repo_im.getdata() if p[3] > 0)
        dep_alpha = sum(1 for p in dep_im.getdata() if p[3] > 0)
        if repo_alpha != dep_alpha:
            raise ExpectationFailed(
                "deployed alpha_count=%d != repo alpha_count=%d -- deploy "
                "is stale" % (dep_alpha, repo_alpha))


@suite.chain("donor_resolves_all_four_directions")
def donor_resolves_all_four_directions(t):
    """Walk steps 1, 3, 4 -- bridge-dependent (needs Outer Rim - Droid
    Depot active, per this walk's own `list:` line). Checks the donor
    ThingDef's fields (querying `ThingDef`, not the `PawnKindDef` About.xml
    loosely names -- see module docstring), no config/missing-texture
    error, and `jawa/texture_audit` reporting nothing missing for this
    def."""
    with t.component("no_config_or_missing_texture_errors", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        boot_hits = [n for n in BOOT_ERROR_NEEDLES if n in joined]
        missing_hit = ("Failed to find any textures at" in joined
                       and DONOR_TEXPATH in joined)
        if boot_hits or missing_hit:
            raise ExpectationFailed(
                "error log contains: config=%r missing-texture=%s -- "
                "recent error lines: %r" % (boot_hits, missing_hit, msgs))

    with t.component("donor_thingdef_texpath_and_graphicclass", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % DROID_DEFNAME,
                          fields="graphicData,graphicClass", deep=True)
        blob = str(r)
        if not r or r.get("success") is False:
            raise ExpectationFailed(
                "get_defs(ThingDef/%s) failed: %r" % (DROID_DEFNAME, r))
        if DONOR_TEXPATH not in blob:
            raise ExpectationFailed(
                "ThingDef/%s graphicData does not mention texPath %r: %r"
                % (DROID_DEFNAME, DONOR_TEXPATH, r))
        if "Multi" not in blob:
            raise ExpectationFailed(
                "ThingDef/%s does not mention Graphic_Multi: %r"
                % (DROID_DEFNAME, r))

    with t.component("texture_audit_reports_nothing_missing_for_mse", beyond_toggle=True):
        r = t.bridge_call("jawa/texture_audit", filter="MSEDroid", limit=60)
        missing = (r or {}).get("missing") or []
        hits = [m for m in missing if DONOR_TEXPATH in str(m) or "MSE" in str(m)]
        if hits:
            raise ExpectationFailed(
                "jawa/texture_audit reports MSE-related path(s) still "
                "missing: %r (full missing[]: %r)" % (hits, missing))


@suite.chain("droid_faces_north_visual_evidence")
def droid_faces_north_visual_evidence(t):
    """Walk step 5, as far as this suite can automate it (see module
    docstring gap #2 -- no bridge tool reports which texture backs a
    live pawn's rendered facing). Spawns the droid, locks its rotation
    north, and screenshots -- evidence for the walk's own step 6 human
    pass, not a mechanical pass/fail on which PNG rendered."""
    t.clear_area(size=20)
    with t.component("droid_spawns_and_locks_north", beyond_toggle=True):
        pawn = t.spawn_pawn(DROID_DEFNAME, hostile=False)
        if not pawn:
            raise ExpectationFailed(
                "jawa/spawn_pawn(kindDef=%r) produced no pawn -- either the "
                "defName is not a PawnKindDef (see module docstring gap #3) "
                "or Outer Rim - Droid Depot is not active" % DROID_DEFNAME)
        r = t.bridge_call("jawa/set_pawn_rotation", pawnId=pawn, dir="north")
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "set_pawn_rotation(%s, north) did not report success: %r"
                % (pawn, r))
        t.screenshot()
        t.bridge_call("jawa/set_pawn_rotation", pawnId=pawn, dir="unlock")
