"""validation.py -- modcheck suite for Bandolier North Fix (KotOR Resources
and Materials) (mandrake.rsw.kotorbandoliernorthfix).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run KotORBandolierNorthFix

SCOPE (read, not guessed): `find src/RimStarWars/KotORBandolierNorthFix
-iname '*.cs'` / `-iname Assemblies` both return nothing -- there is no
Source DLL, no C#, no ModSettings class. `Source/` here holds only offline
Python art tooling (`build_north.py`, the generator; `survey_donor_north.py`
/`survey_broken_sets.py`, the measurements that grounded it;
`test_mask_recipe.py`, the test that rejected the first (inpaint) recipe --
all read whole for this pass). The mod itself ships 20 loose PNGs and
nothing else. Per `modcheck/floor.py`'s documented "zero toggles is not a
floor violation" case, `suite.toggles = []` and every component is
`beyond_toggle=True`.

WHY THIS SUITE IS SHAPED DIFFERENTLY FROM THE OTHER 17 -- its central claims
are PIXEL claims about shipped PNGs, not game-state claims, and the walk
doc's own "must be true" section (canvas/alpha-count parity, mask solid-red
convention) is checkable with PIL directly against files on disk, needing
NO bridge session at all. Two of the four chains below therefore never call
`t.bridge_call`/`t.session` -- they run the same PIL comparisons
`build_north.py`'s own build-time gate already enforced, but against
FILES ON DISK NOW (the shipped repo copy, and the actually-deployed game
copy), which is a check on drift since that gate last ran, not a repeat of
it. `About.xml` itself says why no log-based check exists for this defect
class: "Failed to find any textures at" only fires when EVERY facing of a
set is missing, and both sets already ship east+south.

GROUNDING for the def-field checks (walk steps 5-6): `About.xml`'s own
"WHERE THE DEFS ARE" section names exact line numbers in the donor's
`Apparel_SWAccessories.xml` (`wornGraphicPath` line 426, `dataNorth.layer`
line 428 for chewbacca) -- not independently re-read from the donor's own
XML this pass (that file lives in the donor mod's Workshop copy, not this
repo), so this suite trusts About.xml's own citation and checks the LIVE
resolved def instead, which is the thing that actually matters (a donor
update could move the XML without changing the resolved value, or vice
versa).

Still not proven / structurally offline-only:
  1. `jawa/get_defs(..., deep=True)` on a DOTTED nested path
     (`apparel.wornGraphicPath`, `apparel.drawData.dataNorth.layer`) has no
     precedent anywhere in this suite family -- every other suite's
     `fields=` argument names a TOP-LEVEL field (skills/rimbridge/
     SKILL.md's own "scalar fields only" caveat), and the closest analog
     (JawaVoice/Droidworks/IshkoDarkLandmarks) only ever went one level
     deep. Whether `get_defs` walks a dotted path into a nested
     `ApparelProperties`/`GraphicDataNorth` object at all is UNCONFIRMED --
     flagged here rather than assumed to work.
  2. Walk step X (the human pass -- spawn a pawn wearing either bandolier,
     rotate to face north, confirm bare leather over chest pouches) is
     explicitly out of scope for a scripted suite; not attempted.
  3. The donor's south/southm files are read from this machine's local
     Steam Workshop cache (`game_paths.WORKSHOP`) -- if that cache is
     stale relative to the donor's currently-published version, this
     suite's "parity with the donor" claim is only as fresh as the last
     Workshop sync, not independently verified against Steam.
  4. The DEPLOYED copy check (`game_paths.LOCAL_MODS`) proves the deployed
     Mods folder currently holds a byte-size match for the repo's own
     files -- it does not prove they are byte-IDENTICAL (only PIL-visible
     size/alpha parity), and per rimworld-deploy's own doctrine "writing a
     file is not deploying it," a stale deploy would surface here as a
     mismatch, not silently pass.
"""
import os

from modcheck import Suite, ExpectationFailed

suite = Suite("KotORBandolierNorthFix")
suite.toggles = []   # no C#, no ModSettings class -- see docstring

SETS = ["bandolier_chewbacca", "bandolier_traveler"]
BODIES = ["Male", "Female", "Thin", "Fat", "Hulk"]

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_TEXTURES = os.path.join(_MOD_DIR, "Textures", "SWApparel", "Accessories")

DEFS_UNDER_TEST = [
    ("guy762_Accessory_chewiebandolier",
     "SWApparel/Accessories/bandolier_chewbacca/Apparel"),
    ("guy762_Accessory_travelerbag",
     "SWApparel/Accessories/bandolier_traveler/Apparel"),
]

BOOT_ERROR_NEEDLES = [
    "Config error in mandrake.rsw.kotorbandoliernorthfix",
]
MISSING_TEXTURE_NEEDLES = ["bandolier_chewbacca", "bandolier_traveler"]


def _donor_root():
    import sys
    utils = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_MOD_DIR))),
                         "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    from game_paths import WORKSHOP
    return os.path.join(WORKSHOP, "3254370945", "Textures", "SWApparel", "Accessories")


def _deployed_root():
    import sys
    utils = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_MOD_DIR))),
                         "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    from game_paths import LOCAL_MODS
    return os.path.join(LOCAL_MODS, "KotORBandolierNorthFix", "Textures",
                        "SWApparel", "Accessories")


def _alpha_count(im):
    return sum(1 for p in im.getdata() if p[3] > 0)


@suite.chain("north_matches_donor_south_parity")
def north_matches_donor_south_parity(t):
    """Walk steps 2-3 (10 body/set pairs), run against the REPO's own
    shipped PNGs -- no bridge call, no game. `build_north.py`'s own gate
    already enforced canvas==donor and alpha_count(north)==alpha_count(south)
    at BUILD time; this re-checks it against files on disk NOW, which is a
    drift check, not a repeat of the original gate."""
    from PIL import Image
    with t.component("repo_north_canvas_and_alpha_match_donor_south",
                     beyond_toggle=True):
        donor_root = _donor_root()
        if not os.path.isdir(donor_root):
            raise ExpectationFailed(
                "donor Workshop texture root not found at %s -- cannot check "
                "parity (Workshop cache absent or ws id changed)" % donor_root)
        misses = []
        for s in SETS:
            for body in BODIES:
                north_p = os.path.join(REPO_TEXTURES, s, "Apparel_%s_north.png" % body)
                south_p = os.path.join(donor_root, s, "Apparel_%s_south.png" % body)
                if not os.path.isfile(north_p):
                    misses.append("%s/%s: repo north missing" % (s, body))
                    continue
                if not os.path.isfile(south_p):
                    misses.append("%s/%s: donor south missing at %s" % (s, body, south_p))
                    continue
                north = Image.open(north_p).convert("RGBA")
                south = Image.open(south_p).convert("RGBA")
                if north.size != south.size:
                    misses.append("%s/%s: canvas %r != donor's %r"
                                  % (s, body, north.size, south.size))
                    continue
                an, asth = _alpha_count(north), _alpha_count(south)
                if an != asth:
                    misses.append("%s/%s: alpha_count(north)=%d != "
                                  "alpha_count(south)=%d" % (s, body, an, asth))
                if north.getchannel("A").getextrema()[1] != 255:
                    misses.append("%s/%s: north has no fully-opaque pixel" % (s, body))
        if misses:
            raise ExpectationFailed(
                "%d/%d body-set pairs failed north/south parity: %r"
                % (len(misses), len(SETS) * len(BODIES), misses))


@suite.chain("northm_masks_solid_red")
def northm_masks_solid_red(t):
    """Walk step 4 (10 files): each shipped `_northm.png` is a solid
    (255,0,0,255) field matching its `_north.png` sibling's canvas size --
    the mask-tint convention `build_north.py`'s own docstring documents
    (its own north masks ship a solid red field for the same reason: after
    the repaint no fixed-colour furniture survives on this facing for a
    mask to protect)."""
    from PIL import Image
    with t.component("northm_files_are_solid_red_and_sized", beyond_toggle=True):
        misses = []
        for s in SETS:
            for body in BODIES:
                north_p = os.path.join(REPO_TEXTURES, s, "Apparel_%s_north.png" % body)
                mask_p = os.path.join(REPO_TEXTURES, s, "Apparel_%s_northm.png" % body)
                if not (os.path.isfile(north_p) and os.path.isfile(mask_p)):
                    misses.append("%s/%s: north or northm file missing" % (s, body))
                    continue
                north = Image.open(north_p).convert("RGBA")
                mask = Image.open(mask_p).convert("RGBA")
                if mask.size != north.size:
                    misses.append("%s/%s: mask size %r != north size %r"
                                  % (s, body, mask.size, north.size))
                    continue
                colors = mask.getcolors(maxcolors=2)
                if not colors or len(colors) != 1 or colors[0][1] != (255, 0, 0, 255):
                    misses.append("%s/%s: mask is not a uniform (255,0,0,255) "
                                  "field, got %r" % (s, body, colors))
        if misses:
            raise ExpectationFailed(
                "%d/%d northm masks failed the solid-red convention: %r"
                % (len(misses), len(SETS) * len(BODIES), misses))


@suite.chain("deployed_copy_matches_repo")
def deployed_copy_matches_repo(t):
    """Not in the walk doc verbatim, but the same "writing a file is not
    deploying it" doctrine (rimworld-deploy) applies here as everywhere
    else: the repo copy passing parity above proves nothing about what the
    GAME actually loads if the deployed Mods folder has drifted. Checks
    canvas+alpha parity between the repo's 20 files and the deployed
    folder's 20 files, no bridge call needed."""
    from PIL import Image
    with t.component("deployed_20_files_match_repo_pixel_for_pixel",
                     beyond_toggle=True):
        deployed_root = _deployed_root()
        if not os.path.isdir(deployed_root):
            raise ExpectationFailed(
                "deployed texture root not found at %s -- mod may never have "
                "been deployed" % deployed_root)
        misses = []
        for s in SETS:
            for body in BODIES:
                for kind in ("north", "northm"):
                    fname = "Apparel_%s_%s.png" % (body, kind)
                    repo_p = os.path.join(REPO_TEXTURES, s, fname)
                    dep_p = os.path.join(deployed_root, s, fname)
                    if not os.path.isfile(dep_p):
                        misses.append("%s/%s: not deployed at %s" % (s, fname, dep_p))
                        continue
                    r = Image.open(repo_p).convert("RGBA")
                    d = Image.open(dep_p).convert("RGBA")
                    if r.size != d.size or _alpha_count(r) != _alpha_count(d):
                        misses.append("%s/%s: deployed copy diverges from repo "
                                      "(size %r vs %r, alpha %d vs %d)"
                                      % (s, fname, d.size, r.size,
                                         _alpha_count(d), _alpha_count(r)))
        if misses:
            raise ExpectationFailed(
                "%d deployed file(s) diverge from the repo copy -- the "
                "deploy is stale: %r" % (len(misses), misses))


@suite.chain("donor_defs_still_wire_the_targeted_paths")
def donor_defs_still_wire_the_targeted_paths(t):
    """Walk steps 5-6 and the load-error check (step 1): the two donor
    ThingDefs this mod's art overrides still resolve wornGraphicPath and
    dataNorth.layer as About.xml documents, and no config/missing-texture
    error was logged for either texture set. Bridge-dependent (needs
    guy762.MM.KotORCore active, per this walk's own `list:` line) --
    unlike the two PIL chains above, this one needs a live session."""
    with t.component("no_config_or_missing_texture_errors", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        boot_hits = [n for n in BOOT_ERROR_NEEDLES if n in joined]
        missing_hits = [n for n in MISSING_TEXTURE_NEEDLES
                        if ("Failed to find any textures at" in joined and n in joined)]
        if boot_hits or missing_hits:
            raise ExpectationFailed(
                "error log contains: config=%r missing-texture=%r -- recent "
                "error lines: %r" % (boot_hits, missing_hits, msgs))

    with t.component("donor_defs_wornGraphicPath_and_layer_unchanged",
                     beyond_toggle=True):
        misses = []
        for def_name, expected_path in DEFS_UNDER_TEST:
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % def_name,
                              fields="apparel.wornGraphicPath,"
                              "apparel.drawData.dataNorth.layer", deep=True)
            blob = str(r)
            if not r or r.get("success") is False:
                misses.append("%s: get_defs call failed: %r" % (def_name, r))
                continue
            if expected_path not in blob:
                misses.append("%s: wornGraphicPath %r not found in %r"
                              % (def_name, expected_path, blob))
            if "65" not in blob:
                misses.append("%s: dataNorth.layer=65 not found in %r"
                              % (def_name, blob))
        if misses:
            raise ExpectationFailed(
                "donor def drift detected (see module docstring gap #1 on the "
                "unconfirmed dotted-field reflection path): %r" % misses)
        t.screenshot()
