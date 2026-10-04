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


@suite.chain("patch_xpaths_land")
def patch_xpaths_land(t):
    """STARWARSPATCHES_COVERAGE_GAPS_1 static bar. A patch whose xpath matches nothing logs NOTHING in game,
    so every Patches/*.xml op is REPLAYED offline (modcheck.patch_targets: Add/Replace/Remove applied in load
    order against Core+DLC Data, every src/ mod, the declared donors and any installed mod found to own a
    named def). Sanity-probed first (Core Steel/statBases seen; a missing child and a bogus def are not).
    FindMod branches for uninstalled mods are SKIP (never a pass); an unmodelled op class is UNMEASURED.
    MayRequire on a whole <Operation> is inert in 1.6, so such an op is replayed unconditionally."""
    with t.component("every_patch_op_matches_a_target", beyond_toggle=True):
        import sys as _sys
        _utils = _os.path.join(_MOD_DIR, "..", "..", "RimMandrake", "Utils")
        if _utils not in _sys.path:
            _sys.path.insert(0, _utils)
        from modcheck import patch_targets as PT
        if not PT.GAME_DATA.is_dir():
            t._why = "game Data unreachable from this machine: cannot index vanilla targets"
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: " + t._why
            return
        results, meta = PT.check_mod(_MOD_DIR)
        bad = PT.sanity(meta["index"])
        if bad:
            raise ExpectationFailed("SANITY: the def index cannot see: " + "; ".join(bad))
        if meta["files"] == 0 or not results:
            raise ExpectationFailed("blind parse: no patch files or no operations found under %s" % _MOD_DIR)
        fails = [r for r in results if r["status"] == "FAIL"]
        unm = [r for r in results if r["status"] == "UNMEASURED"]
        if fails:
            raise ExpectationFailed("%d of %d patch ops match nothing (silent no-ops): %s" % (
                len(fails), len(results), "; ".join("%s %s (%s)" % (r["where"], r["xpath"], r["why"]) for r in fails[:8])))
        if unm:
            t._why = "%d ops of an unmodelled class: %s" % (len(unm), sorted({r["class"] for r in unm}))
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: " + t._why

# ---------------------------------------------------------------------------------------------------------------------
# STARWARSPATCHES_COVERAGE_GAPS_1 (second half; the xpath replay above was the first). Static bars over the patch XML and the
# fresh offline def dump for what a silently-no-op or silently-destructive patch does: an <li> poured into a dictionary-keyed
# field (which discards the WHOLE BiomeDef), an inert MayRequire on a whole operation, a weather def never attached, a patch
# value naming a def that does not exist, and the post-patch weapon-tag index leaving a Core/campaign kind disarmed.
# Each rule has a planted-break selftest (selftest_starwarspatches_semantics.py). Still UNMEASURED: a blast door actually
# opening and closing (needs a built, powered door), and a generated pawn's gear after WeaponTags_Renormalise.
import json as _json
import re as _re
import xml.etree.ElementTree as _ET

DICT_KEYED_FIELDS = ("baseWeatherCommonalities", "wildAnimals", "wildPlants")
EDIT_CLASSES = ("PatchOperationAdd", "PatchOperationReplace", "PatchOperationInsert")
OURS_PREFIXES = ("RSW_", "RUT_", "RM_", "Jawa_")
OFFICIAL_MODS = ("Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")


def load_patch_roots(root=_MOD_DIR):
    import glob as _glob
    return [(_os.path.basename(f), _ET.parse(f).getroot()) for f in sorted(_glob.glob(_os.path.join(root, "Patches", "*.xml")))]


def pack_def_names(root=_MOD_DIR):
    """{defType: {defName}} from this mod's own Defs/."""
    import glob as _glob
    out = {}
    for f in _glob.glob(_os.path.join(root, "Defs", "**", "*.xml"), recursive=True):
        for e in _ET.parse(f).getroot():
            if isinstance(e.tag, str) and e.findtext("defName"):
                out.setdefault(e.tag.split(".")[-1], set()).add(e.findtext("defName").strip())
    return out


def _dump_dir():
    try:
        import sys as _sys
        _sys.path.insert(0, _os.path.join(_MOD_DIR, "..", "..", "RimMandrake", "Utils"))
        import game_paths as GP
        d = _os.path.join(GP.DEF_DUMP, "defs")
        return d if _os.path.isdir(d) else None
    except Exception:  # noqa: BLE001
        return None


def dump_defs(def_type):
    """The list of def dicts of one type from the newest offline def dump, or None (UNMEASURED) when unreadable."""
    d = _dump_dir()
    try:
        j = _json.load(open(_os.path.join(d, def_type + ".json"), encoding="utf-8"))
        return j["defs"] if len(j["defs"]) > 0 else None
    except Exception:  # noqa: BLE001
        return None


def dump_names(types=("XenotypeDef", "GeneDef", "WeatherDef", "ThingDef", "PawnKindDef", "FactionDef", "BiomeDef")):
    """{defType: {defName}} for the types the patch values can name, or None when the dump is unreadable."""
    out = {}
    for ty in types:
        rows = dump_defs(ty)
        if rows is None:
            return None
        out[ty] = set(r.get("defName") for r in rows)
    return out


def _walk(el, ancestors=()):
    yield el, ancestors
    for c in list(el):
        for x in _walk(c, ancestors + (el,)):
            yield x


def patch_findings(roots, pack, dump):
    bad = []
    n_ops = 0
    for fn, root in roots:
        if root.tag != "Patch":
            bad.append("%s: root is <%s>, not <Patch> (the whole file is ignored)" % (fn, root.tag))
        for el, anc in _walk(root):
            if not el.get("Class", "").startswith("PatchOperation"):
                continue        # any tag: nested branches are <match>/<nomatch>/<li>/<success>, not only <Operation>
            n_ops += 1
            cls = el.get("Class")
            if el.get("MayRequire") or el.get("MayRequireAnyOf"):
                bad.append("%s: %s carries MayRequire on a whole operation (inert in 1.6: it applies anyway); use PatchOperationFindMod/Conditional" % (fn, cls))
            if cls in EDIT_CLASSES + ("PatchOperationRemove", "PatchOperationAttributeAdd", "PatchOperationAttributeSet", "PatchOperationAttributeRemove") and not (el.findtext("xpath") or "").strip():
                bad.append("%s: %s has no xpath" % (fn, cls))
            if cls in EDIT_CLASSES + ("PatchOperationAttributeAdd", "PatchOperationAttributeSet") and el.find("value") is None:
                bad.append("%s: %s has no value" % (fn, cls))
            xp = el.findtext("xpath") or ""
            last = xp.rstrip("/").rsplit("/", 1)[-1].split("[", 1)[0]
            val = el.find("value")
            if cls in EDIT_CLASSES and val is not None and (last in DICT_KEYED_FIELDS or any(last == f for f in DICT_KEYED_FIELDS)):
                if any(c.tag == "li" for c in val):
                    bad.append("%s: adds <li> to dictionary-keyed %s (the whole def is discarded: element name = def, text = value)" % (fn, last))
            # weather attachments: element name must be a real weather and the commonality positive
            if cls in EDIT_CLASSES and val is not None and last == "baseWeatherCommonalities":
                for c in val:
                    known = (pack.get("WeatherDef", set()) | (dump["WeatherDef"] if dump else set()))
                    if dump is not None and c.tag not in known:
                        bad.append("%s: attaches weather %s, which no mod defines" % (fn, c.tag))
                    try:
                        if not float(c.text) > 0:
                            bad.append("%s: weather %s attached at commonality %s (never rolls)" % (fn, c.tag, c.text))
                    except (TypeError, ValueError):
                        bad.append("%s: weather %s has a non-numeric commonality %r" % (fn, c.tag, c.text))
            # a def literal in an xpath that neither this pack nor the dump knows must sit under a FindMod/Conditional
            if dump is not None and xp:
                for m in _re.finditer(r"/(\w+)\[defName\s*=\s*\"([^\"]+)\"", xp):
                    ty, nm = m.group(1), m.group(2)
                    if ty in dump and nm in dump[ty]:
                        continue
                    if nm in pack.get(ty, set()):
                        continue
                    guarded = any((a.get("Class") in ("PatchOperationFindMod", "PatchOperationConditional")) for a in anc) \
                        or el.get("Class") == "PatchOperationConditional"
                    if ty in dump and not guarded:
                        bad.append("%s: xpath targets %s %s, which is not in the loaded defs and the operation is not guarded (it matches nothing and logs nothing)" % (fn, ty, nm))
            # our own def names written as patch VALUES must exist
            if dump is not None and val is not None:
                for node in val.iter():
                    txt = (node.text or "").strip()
                    if txt.startswith("RSW_") and _re.fullmatch(r"\w+", txt) and node.tag in ("li", "xenotype", "weather", "gene", "kindDef", "def"):
                        if not any(txt in names for names in list(dump.values()) + list(pack.values())):
                            bad.append("%s: value names %s, which neither the pack nor the loaded defs define" % (fn, txt))
    if n_ops < 100:
        bad.append("parsed only %d patch operations, want >= 100 (sanity probe failed)" % n_ops)
    attached = set()
    for fn, root in roots:
        if fn == "SWDesertWeather_Attach.xml":
            for el in root.iter("value"):
                attached.update(c.tag for c in el)
    for w in sorted(pack.get("WeatherDef", set())):
        if w not in attached:
            bad.append("weather def %s is defined but SWDesertWeather_Attach.xml never attaches it to a biome (dead content)" % w)
    return bad


def disarmed_kinds(things, kinds):
    """[(defName, modName, weaponTags)] of fighter-capable PawnKindDefs whose every weapon tag matches no weapon in the loaded defs."""
    tags = set()
    for x in things:
        for tg in (x.get("fields") or {}).get("weaponTags") or []:
            tags.add(tg)
    out = []
    for k in kinds:
        f = k.get("fields") or {}
        wt = f.get("weaponTags") or []
        wm = f.get("weaponMoney")
        if wt and isinstance(wm, dict) and wm.get("max", 0) > 0 and not any(tg in tags for tg in wt):
            out.append((k["defName"], k.get("modName"), wt))
    return out


def ours_or_official(row):
    return row[0].startswith(OURS_PREFIXES) or row[1] in OFFICIAL_MODS


@suite.chain("patch_semantics_static")
def patch_semantics_static(t):
    roots, pack, dump = load_patch_roots(), pack_def_names(), dump_names()

    def pick(keys):
        return [f for f in patch_findings(roots, pack, dump) if any(k in f for k in keys)]
    with t.component("patch_files_wellformed_and_no_inert_mayrequire", beyond_toggle=True):
        bad = pick(["not <Patch>", "MayRequire", "no xpath", "has no value", "sanity probe"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("dictionary_keyed_fields_never_get_li", beyond_toggle=True):
        bad = pick(["dictionary-keyed"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("weather_defs_are_all_attached_with_real_names_and_positive_commonality", beyond_toggle=True):
        bad = pick(["weather", "commonality", "dead content"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("patch_xpath_literals_and_values_name_loaded_defs_or_are_guarded", beyond_toggle=True):
        bad = pick(["xpath targets", "value names"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
        if dump is None:
            t.upstream_reason, t.upstream_failed = "UNMEASURED: no readable offline def dump to look the targets up in", True
    with t.component("weapon_tag_index_leaves_no_core_or_campaign_kind_disarmed", beyond_toggle=True):
        things, kinds = dump_defs("ThingDef"), dump_defs("PawnKindDef")
        if things is None or kinds is None:
            t.upstream_reason, t.upstream_failed = "UNMEASURED: no readable offline def dump for ThingDef/PawnKindDef", True
        else:
            dis = disarmed_kinds(things, kinds)
            mine = [d for d in dis if ours_or_official(d)]
            t._record("%d kinds disarmed in this dump, %d of them Core/DLC/campaign; the rest are third-party: %s" % (
                len(dis), len(mine), sorted(set(d[1] for d in dis if not ours_or_official(d)))), not mine)
            if mine:
                raise ExpectationFailed("fighter kinds whose weapon tags match no loaded weapon (they spawn unarmed): %s" % mine[:8])
    with t.component("blast_door_opens_and_closes_state_read", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: a built, powered blast door actually opening and closing needs a constructed instance and ticks "
                                 "(DoorsExpanded.Building_DoorExpanded); the doors only spawn-check above; instrument missing: a [Tool] that "
                                 "builds a door and reads its openPct over time")
            t.upstream_failed = True


# Every def this mod ships is loaded and its label is what its XML says (NORTHSTAR_PARTIAL_GAPS_FILL_1;
# Heron research, pawnkinds, weathers). The Defs/ parse is the list, so a def added later is covered with no edit here.
from modcheck import shipped_defs  # noqa: E402
shipped_defs.add_chain(suite, __file__, sanity=('Heron_ResearchTab', 'ProjectHeron_Swdoors'), min_count=30)
