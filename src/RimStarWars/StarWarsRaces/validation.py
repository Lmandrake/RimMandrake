"""validation.py -- modcheck suite for RimMandrake - Star Wars Races
(mandrake.rsw.starwarsraces).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run StarWarsRaces

SCOPE (read, not guessed): `About/About.xml` -- "Contains no compiled code."
There is no `Assemblies/` folder and no `Source/` folder anywhere under this
mod; every `Defs/` file under `Absorbed_*` and the top-level `GeneDefs/`,
`HeadTypeDefs/`, `PawnKindDefs/`, `RulePackDefs/`, `Misc/` and `XenotypeDefs/`
folders is XML data with no Mod Settings class possible. Per
`modcheck/floor.py`'s own documented case ("Zero toggles is not a floor
violation... every component in that mod's suite is necessarily
beyond_toggle=True"), `suite.toggles = []` and every component below is
`beyond_toggle=True`.

This mod is 69 species' worth of genes, head types, name-generating rule
packs and pawn kinds (`About.xml`'s own count) -- almost entirely cosmetic
render nodes with no observable behavior beyond "the def resolves and the
game does not choke on it." Testing all 69 is not what spec §1 asks for
("not exhaustive, not the playtest"); this suite instead exercises the ONE
thing in the mod with real, owner-ruled MECHANICAL consequences -- the
`RSW_MandrakeJawa` xenotype the player's own clan carries -- end to end, plus
one cheap def-resolution check standing in for "the other 68 species load
too," plus a check that the mod's OWN naming data (not a donor's) actually
drives name generation.

GROUNDING:
  - `Defs/XenotypeDefs/MandrakeJawaXenotype.xml` -- 38 genes, "authored here
    rather than copied." Its own header is a live warning that three of those
    38 genes (`AptitudeTerrible_Plants`, `RSW_Jawa_MiningDisabled`,
    `SEX_AlwaysAphrodor`) are NOT in the owner's saved `.xtp` and are
    "SILENTLY LOST" by a careless re-transcribe -- "the def still loads,
    every Jawa still generates, and the only symptoms are a clan that farms
    happily, digs its own ore, and quietly reverts to two ordinary sexes."
    That is exactly the kind of regression this suite exists to catch, so
    all three are asserted by name, not just a gene COUNT.
  - `Defs/GeneDefs/Jawa_MiningDisabled.xml` -- `disabledWorkTags: Mining`,
    contrasted on purpose with `AptitudeTerrible_Plants` (an APTITUDE
    penalty on the xenotype itself, not a `disabledWorkTags` -- the file's
    own header explains why `PlantWork` could never be hard-disabled without
    also stopping tree-chopping). The suite proves both halves of that
    asymmetry: Mining is refused outright, Plants/Growing is not.
  - `Defs/RulePackDefs/SW_NameMakers.xml` (`RSW_KoTOR_NamerJawa`) and
    `Languages/English/Strings/RimMandrakeSWNames/SWX/Jawa/First.txt` -- the
    xenotype's own `<nameMaker>` field points at this rule pack, which reads
    ONLY this mod's own word list (`Rule_File` path
    `RimMandrakeSWNames/SWX/Jawa/First`), never a donor's. Forcing the
    xenotype at PAWN GENERATION time (`jawa/spawn_pawn`'s `xenotype` param,
    NOT `jawa/set_pawn_xenotype`, which only swaps genes on an
    already-generated pawn and does not re-run name generation) is what
    actually exercises this path.
  - Bridge tools used, each read back independently of its own request:
    `jawa/set_pawn_xenotype` (genuine before/after read off the pawn, per its
    own docstring), `jawa/pawn_genes(action="list")` (a SEPARATE read of
    `Endogenes`/`Xenogenes`, never trusting the conversion call's own
    response for gene identity), `jawa/set_work_priority` (its own refusal
    path reads `pawn.GetDisabledWorkTypes()` off the live pawn and reports it
    in `details.disabledWorkTypes` -- a real engine query, not an echo).

Still not proven / likely first-live-run corrections:
  1. `jawa/spawn_pawn(..., xenotype="RSW_MandrakeJawa")` is assumed to run
     the FULL generation pipeline (including name generation via the
     xenotype's own `nameMaker`) rather than a lighter path -- grounded in
     the tool's own doc comment ("PawnGenerationRequest.ForcedXenotype...
     PawnGenerator checks FIRST") but not yet run live.
  2. The namer component reads the FIRST token of `pawn_get`'s `name`
     (`NameTriple.ToStringFull`) as the first name. If a generated Jawa ever
     gets a nickname formatted before the first name, or the full-string
     format changes, this parsing breaks before the mechanism does -- a
     false FAIL, not a real one, if that happens.
  3. Genes lists containing 300+ entries (`SW_Genes.xml` alone) were spot
     read, not read in full; a def-loading error deep in the un-sampled
     remainder (a bad `ParentName`, a missing icon) would not be caught by
     anything in this suite. `donor_xenotype_defs_resolve_without_donor_mods`
     is a cheap sample (3 of 69 species), not a census.
  4. `RSW_RimMandrakeWookiee` etc. are asserted to RESOLVE, not to look or
     play correctly -- art/render-node correctness for the other 68 species
     is out of scope for a scripted bridge check and belongs to a visual
     review, not this suite.
"""
from modcheck import Suite, ExpectationFailed
import os

suite = Suite("StarWarsRaces")
suite.toggles = []  # no compiled code, no ModSettings possible -- see docstring

JAWA_XENOTYPE = "RSW_MandrakeJawa"
JAWA_FRAGILE_GENES = {
    "AptitudeTerrible_Plants", "RSW_Jawa_MiningDisabled", "SEX_AlwaysAphrodor",
}
JAWA_OTHER_EXPECTED_GENES = {
    "RSW_Jawa_Skittish", "RSW_Jawa_Head_Plain", "SEX_Ovipositor", "Outland_AllMale",
}
DONOR_SAMPLE_XENOTYPES = [
    "RSW_RimMandrakeWookiee", "RSW_RimMandrakeTwilek", "RSW_RimMandrakeRodian",
]

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
_JAWA_FIRST_NAMES_PATH = os.path.join(
    _MOD_DIR, "Languages", "English", "Strings", "RimMandrakeSWNames", "SWX",
    "Jawa", "First.txt")


def _declared_genes():
    """The <genes> list of RSW_MandrakeJawa, read from this mod's own XML (the thing under test)."""
    import re
    path = os.path.join(_MOD_DIR, "Defs", "XenotypeDefs", "MandrakeJawaXenotype.xml")
    with open(path, "r", encoding="utf-8") as f:
        xml = f.read()
    m = re.search(r"<genes>(.*?)</genes>", xml, re.S)
    return re.findall(r"<li>\s*([A-Za-z0-9_]+)\s*</li>", m.group(1)) if m else []


def _spawn_pawn_forced_xenotype(t, kind_def, xenotype, count=1):
    """Mirrors `TestContext.spawn_pawn` exactly (same cell math, same
    teardown tracking via `t.session.track`) but adds `xenotype=`, which the
    built-in verb does not expose -- `jawa/spawn_pawn`'s own `xenotype` param
    forces the xenotype through `PawnGenerationRequest.ForcedXenotype` at
    GENERATION time, which `jawa/set_pawn_xenotype` (a post-hoc gene swap)
    cannot do. This is the escape valve (spec §1: `bridge_call` for anything
    the vocabulary does not cover), with the same spawn-tracking discipline
    the library itself uses so chain teardown still sweeps these pawns."""
    if not t._guard():
        return []
    x0, z0 = t.anchor
    ids = []
    for i in range(count):
        x, z = x0 + i * 2, z0
        r = t.bridge_call("jawa/spawn_pawn", kindDef=kind_def, x=x, z=z,
                          faction="player", count=1, xenotype=xenotype)
        rows = (r or {}).get("pawns") or []
        if not rows:
            raise ExpectationFailed(
                "jawa/spawn_pawn(kindDef=%r, xenotype=%r) produced no pawn: %r"
                % (kind_def, xenotype, r))
        pid = rows[0].get("id")
        if pid:
            t.session.track("pawn", pid, x=x, z=z)
            ids.append(pid)
    return ids


@suite.chain("jawa_xenotype_mechanism")
def jawa_xenotype_mechanism(t):
    """The player's own clan's xenotype, converted onto a fresh colonist and
    checked gene-by-gene against the three fragile, easily-lost genes plus
    four other structurally important ones -- then the Mining/Plants
    asymmetry the mod's own docs insist on is proven live."""
    t.clear_area(size=20)
    pawn = t.spawn_pawn("Colonist", hostile=False)

    with t.component("xenotype_applies_fragile_genes", beyond_toggle=True):
        r = t.bridge_call("jawa/set_pawn_xenotype", pawnId=pawn,
                          xenotype=JAWA_XENOTYPE, clearEndogenes=True)
        rows = (r or {}).get("pawns") or []
        if not rows:
            raise ExpectationFailed("jawa/set_pawn_xenotype returned no pawn row: %r" % r)
        row = rows[0]
        if row.get("now") != JAWA_XENOTYPE:
            raise ExpectationFailed(
                "pawn's xenotype reads back as %r, not %r" % (row.get("now"), JAWA_XENOTYPE))
        # CORRECTED 2026-10-02 (MODCHECK_SUITE_CORRECTIONS_1): "38" is the count the XML DECLARES, but 18 of
        # those 38 genes are donor genes (Alpha Genes, VRE, SEX_, Outland, Aptitude ...) and RimWorld drops a
        # gene whose def is not loaded. MEASURED live on the minimal list: genesInDef 24 of 38 = the 14
        # donor genes that environment lacked, not a silent loss in this mod. Compare against the declared
        # genes that EXIST in the run: a gene that does exist and still goes missing is the loss this
        # assertion is for; a gene the environment cannot supply is reported as evidence, not failed.
        declared = _declared_genes()
        resolved = t.bridge_call("jawa/get_defs",
                                 defs=";".join("GeneDef/%s" % g for g in declared), fields="label") or {}
        absent = set(resolved.get("notFound") or [])
        absent = set(a_.split("/", 1)[-1] for a_ in absent)
        present = [g for g in declared if g not in absent]
        t._record("genes declared=%d resolvable-in-this-load=%d unresolvable=%s"
                  % (len(declared), len(present), sorted(absent)), True)
        if len(declared) != 38:
            raise ExpectationFailed(
                "MandrakeJawaXenotype.xml now declares %d genes, this suite documents 38 -- the xenotype "
                "was edited without updating this suite" % len(declared))
        if not resolved.get("success", True) or not present:
            raise ExpectationFailed("could not resolve any declared gene def: %r" % resolved)
        if row.get("genesInDef") != len(present):
            raise ExpectationFailed(
                "RSW_MandrakeJawa reports %r genes, expected %d (the %d declared genes whose defs exist in "
                "this load; %d are donor genes this load lacks: %s) -- a gene silently dropped"
                % (row.get("genesInDef"), len(present), len(declared), len(absent), sorted(absent)))

        genes = t.bridge_call("jawa/pawn_genes", pawn=pawn, action="list")
        endo = set((genes or {}).get("endogenes") or [])
        missing_fragile = (JAWA_FRAGILE_GENES & set(present)) - endo
        if "RSW_Jawa_MiningDisabled" not in present:
            raise ExpectationFailed("this mod's OWN RSW_Jawa_MiningDisabled gene def is not loaded")
        if missing_fragile:
            raise ExpectationFailed(
                "JAWA_FRAGILE_GENES missing after xenotype conversion: %s -- this is "
                "the exact silent-loss failure MandrakeJawaXenotype.xml's own header "
                "warns about (a re-transcribe from the owner's .xtp drops these three)"
                % sorted(missing_fragile))
        missing_other = (JAWA_OTHER_EXPECTED_GENES & set(present)) - endo
        if missing_other:
            raise ExpectationFailed(
                "expected Jawa genes missing after conversion: %s" % sorted(missing_other))
        t.screenshot()

    with t.component("mining_disabled_not_plantwork", beyond_toggle=True):
        mining = t.bridge_call("jawa/set_work_priority", pawnId=pawn,
                               workType="Mining", priority=3)
        if mining.get("success") is not False:
            raise ExpectationFailed(
                "set_work_priority(Mining) SUCCEEDED on a Jawa -- "
                "RSW_Jawa_MiningDisabled's disabledWorkTags is not taking effect: %r"
                % mining)
        disabled = ((mining or {}).get("details") or {}).get("disabledWorkTypes") or []
        if "Mining" not in disabled:
            raise ExpectationFailed(
                "set_work_priority(Mining) was refused for a reason OTHER than the "
                "Mining work type being disabled: disabledWorkTypes=%r" % disabled)

        plants = t.bridge_call("jawa/set_work_priority", pawnId=pawn,
                               workType="PlantCutting", priority=3)
        if plants.get("success") is not True:
            raise ExpectationFailed(
                "set_work_priority(PlantCutting) was REFUSED for a Jawa -- "
                "AptitudeTerrible_Plants is a soft aptitude penalty, not a "
                "disabledWorkTags entry, and should not block assignment at all: %r"
                % plants)
        t.screenshot()


@suite.chain("jawa_naming")
def jawa_naming(t):
    """`RSW_MandrakeJawa.nameMaker` names `RSW_KoTOR_NamerJawa`, which reads
    ONLY this mod's own word list. Forces the xenotype at GENERATION time
    (see `_spawn_pawn_forced_xenotype`'s docstring) so name generation
    actually runs against it, then checks the generated first name against
    the mod's own `First.txt` -- proof the namer is wired to THIS mod's
    data, not silently falling back to a generic human namer."""
    t.clear_area(size=20)
    with t.component("namer_draws_from_jawa_wordlist", beyond_toggle=True):
        if not os.path.isfile(_JAWA_FIRST_NAMES_PATH):
            raise ExpectationFailed(
                "First.txt not found at %s -- cannot check the namer against its "
                "own word list" % _JAWA_FIRST_NAMES_PATH)
        with open(_JAWA_FIRST_NAMES_PATH, "r", encoding="utf-8") as f:
            first_names = {line.strip() for line in f if line.strip()}
        if len(first_names) < 10:
            raise ExpectationFailed(
                "First.txt only yielded %d names -- suspiciously small, refusing "
                "to trust the comparison" % len(first_names))

        pawns = _spawn_pawn_forced_xenotype(t, "Colonist", JAWA_XENOTYPE, count=3)
        misses = []
        for pid in pawns:
            g = t.bridge_call("jawa/pawn_get", pawn=pid)
            rows = (g or {}).get("pawns") or []
            if not rows:
                raise ExpectationFailed("jawa/pawn_get found no pawn for %r" % pid)
            full_name = rows[0].get("name") or ""
            first_token = full_name.split(" ")[0].strip() if full_name else ""
            if first_token not in first_names:
                misses.append((pid, full_name))
        if misses:
            raise ExpectationFailed(
                "%d/%d Jawa-xenotype pawns got a first name NOT in this mod's own "
                "SWX/Jawa/First.txt: %r -- the namer may have fallen back to a "
                "generic human name maker instead of RSW_KoTOR_NamerJawa"
                % (len(misses), len(pawns), misses))
        t.screenshot()


@suite.chain("donor_species_sample")
def donor_species_sample(t):
    """Cheap sample standing in for "the other 68 species load too" (spec:
    not exhaustive). No pawns, no map mutation beyond clear_area: these defs
    resolving AT ALL in a minimal-mechanism-list environment (none of
    Star Wars Xenotypes / Outer Rim Galactic Diversity / [BTD] Xenotype
    REMIX installed) is itself the proof of About.xml's central claim --
    "none of the three donors needs to be installed"."""
    t.clear_area(size=10)
    with t.component("donor_xenotype_defs_resolve_without_donor_mods", beyond_toggle=True):
        defs_arg = ";".join("XenotypeDef/%s" % x for x in DONOR_SAMPLE_XENOTYPES)
        r = t.bridge_call("jawa/get_defs", defs=defs_arg, fields="label")
        not_found = (r or {}).get("notFound") or []
        if not_found:
            raise ExpectationFailed(
                "sampled donor-species xenotypes did not resolve: %r -- either this "
                "mod failed to load them, or the run's mod list is missing something "
                "this mod needs" % not_found)
        rows = (r or {}).get("defs") or []
        found_names = {row.get("defName") for row in rows}
        missing = set(DONOR_SAMPLE_XENOTYPES) - found_names
        if missing or not rows:
            raise ExpectationFailed(
                "expected %d resolved XenotypeDef rows, got %r (missing %s)"
                % (len(DONOR_SAMPLE_XENOTYPES), rows, sorted(missing)))


# NORTHSTAR_PARTIAL_GAPS_FILL_1 row: every def this mod ships (527: genes, head types, pawnkinds, xenotypes, name
# rule packs, hediffs, recipes) must be loaded live, with authored scalar fields equal to the XML. MayRequire-guarded
# defs (VFE Core, pathfinding.framework) are graded by guard group: all absent = that mod inactive (skipped, said),
# partly absent = a real loss. XenotypeDef labels/descriptions are deliberately rewritten by PawnFlavor's
# PawnFlavorPhase2_Xenotype.xml, so xenotypes are compared on their non-text fields only.
from modcheck import shipped_defs  # noqa: E402

shipped_defs.add_chain(suite, __file__,
                       fields_by_type={"GeneDef": ("label", "biostatCpx", "biostatMet", "displayOrderInCategory"),
                                       "HeadTypeDef": ("graphicPath", "gender"),
                                       "PawnKindDef": ("label",),
                                       "XenotypeDef": ("inheritable", "factionlessGenerationWeight",
                                                       "canGenerateAsCombatant", "combatPowerFactor"),
                                       "HediffDef": ("label", "maxSeverity"),
                                       "RecipeDef": ("label", "jobString")},
                       sanity=("RSW_RimMandrakeJawa", "RSW_MandrakeJawa", "Head_Bone", "Male_HeavyBoneNormal"),
                       min_count=500)


# ---------------------------------------------------------------- name rulepacks (NORTHSTAR_PARTIAL_GAPS_FILL_1)
# Audit row: "48 name rulepacks beyond Jawa produce words? (a pack without its word list resolves and produces
# nothing)". Pure repo read, runs offline: every Rule_File path in every RulePackDef under Defs/ resolves to a
# NON-EMPTY Languages/English/Strings/<path>.txt, and every [keyword] a rulesStrings line uses is defined in the
# same pack (rule params like "(p=3)" stripped). First run 2026-10-04 went red on RSW_KoTOR_NamerAqualish (its three
# lists existed in no installed mod; canon lists written, AQUALISH_NAME_WORDLISTS_1) and SandP's empty Nick.txt.
def rulepack_findings(mod_dir=_MOD_DIR):
    """([finding], packs_read, files_checked)."""
    import glob as _glob
    import re as _re
    import xml.etree.ElementTree as _ET
    bad, n_packs, n_files = [], 0, 0
    strings = os.path.join(mod_dir, "Languages", "English", "Strings")
    for f in sorted(_glob.glob(os.path.join(mod_dir, "Defs", "**", "*.xml"), recursive=True)):
        for rp in _ET.parse(f).getroot().iter("RulePackDef"):
            name, n_packs = rp.findtext("defName"), n_packs + 1
            defined, used = set(), set()
            for li in rp.findall("rulePack/rulesStrings/li"):
                k, _sep, v = (li.text or "").partition("->")
                defined.add(_re.sub(r"\(.*\)", "", k).strip())
                used.update(_re.findall(r"\[(\w+)\]", v))
            for r in rp.findall("rulePack/rulesRaw/li"):
                kw, p = r.findtext("keyword"), r.findtext("path")
                if kw:
                    defined.add(kw.strip())
                if p:
                    n_files += 1
                    fp = os.path.join(strings, *p.strip().split("/")) + ".txt"
                    if not os.path.isfile(fp):
                        bad.append("%s: word list %s missing" % (name, p.strip()))
                    elif not any(l.strip() for l in open(fp, encoding="utf-8-sig")):
                        bad.append("%s: word list %s empty" % (name, p.strip()))
            bad.extend("%s: [%s] used but never defined" % (name, u) for u in sorted(used - defined))
    return bad, n_packs, n_files


@suite.chain("namer_wordlists_resolve")
def namer_wordlists_resolve(t):
    """Offline: every shipped name rulepack can produce a word (no live call)."""
    with t.component("every_rulepack_word_list_exists_and_every_keyword_is_defined", beyond_toggle=True):
        bad, packs, files = rulepack_findings()
        if packs < 40 or files < 100:
            raise ExpectationFailed("rulepack parse is blind: %d packs, %d Rule_File paths" % (packs, files))
        if bad:
            raise ExpectationFailed("%d rulepack defect(s): %s" % (len(bad), "; ".join(bad)))
