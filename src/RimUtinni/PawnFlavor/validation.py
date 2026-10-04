"""validation.py -- modcheck suite for PawnFlavor (mandrake.rut.pawnflavor).

Pure-XML content mod: no Source/ folder, no C# at all, therefore no
ModSettings class -- `suite.toggles = []` and every component below is
`beyond_toggle=True` (per the briefing's own documented case for a mod with
no Mod Settings yet).

Grounded in the mod's actual Defs/ and Patches/ (read in full for this pass): 77
BackstoryDefs across 7 files and 13 TraitDefs. (About.xml once said "Fifty ... five"; it
was corrected under PAWNFLAVOR_COVERAGE_GAPS_1 and `about_counts_match_the_shipped_defs`
now fails if it drifts again.)

THE MECHANISM (mod's own description, verified against 1.6 source via
PawnBioAndNameGenerator): a spawned pawn's childhood/adulthood backstory is
drawn from the union of its FACTION's `backstoryFilters` and its PAWNKIND's
own filters, each filter naming one or more `spawnCategories`. This mod adds
one filter per faction naming a `JawaBSC_<Faction>` category (or, for two of
the eleven, restates the whole list because a child def's own declared list
OVERRIDES an inherited one -- see Patches/FactionBackstoryWiring.xml's own
header comment for exactly which factions take which route).

ENVIRONMENT GAP, same register as Droidworks' Jawa Ion Weapons note: 9 of
the 11 `PatchOperationConditional` targets in FactionBackstoryWiring.xml
(everything except vanilla `Empire` and `Pirate`) name `RUT_Jawa_*`
FactionDefs that live in `mandrake.rut.patches` -- named only in
`<loadAfter>`, NOT `<modDependencies>` in this mod's own About.xml. Run
against minimal+PawnFlavor alone, every one of those 9 operations' own
`<xpath>` matches nothing (the FactionDef does not exist to be found) and
logs nothing (a patch that matches nothing logs nothing, CLAUDE.md's own
rule) -- so this suite proves the mechanism live only on the two vanilla
factions, and proves the other 9 by def read-back of this mod's OWN side
(the BackstoryDefs and the patch's declared xpath/value) rather than by
watching a `RUT_Jawa_*` FactionDef's `backstoryFilters` actually change.
Re-run with `mandrake.rut.patches` added to the smoke-test list to see the
other 9 apply live.

Similarly, `Backstories_Rakata_Sleepers.xml`'s two categories
(`VQE_AncientPatient`, `VQE_Experiment` -- these feed a "Vanilla Quests
Expanded"-family ancient-cryptosleep-casket quest's patient pool, per that
file's own header comment, not the FactionDef mechanism at all) are proven
by def read-back only: drawing one live needs that quest mod active and its
quest actually offered, neither attempted here.

`Empire` needs Royalty active to exist as a FactionDef at all -- if the
smoke-test's mod list has no Royalty, `empire_pawn_draws_flavor_backstory`
fails cleanly naming the missing faction, which is the correct signal for
that environment, not a script bug.

STILL NOT PROVEN: `empire_pawn_draws_flavor_backstory` is probabilistic (see
its own component for the reasoning) -- run once, not repeated to confirm a
failure isn't just bad luck.
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))

suite = Suite("PawnFlavor")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle


def _get_defs(t, defs, fields, deep=False):
    if deep:
        return t.bridge_call("jawa/get_defs", defs=defs, fields=fields, deep=True)
    return t.bridge_call("jawa/get_defs", defs=defs, fields=fields)


def _expect_field(t, r, def_key, field, predicate, why):
    row = None
    for d in (r or {}).get("defs", (r or {}).get("results", [])) or []:
        if d.get("defName") == def_key.split("/", 1)[-1]:
            row = d
            break
    fields = (row or {}).get("fields") or {}
    val = fields.get(field, "(no such field)")
    ok = predicate(val)
    t._record("%s.%s -> %r (%s)" % (def_key, field, val, why), ok)
    if not ok:
        raise ExpectationFailed("%s.%s = %r, expected %s" % (def_key, field, val, why))
    return val


# ============================================================== trait defs
@suite.chain("trait_defs_readback")
def trait_defs_readback(t):
    """Every stat name on these TraitDefs was verified against Core's own
    TraitDegreeData fields when the file was written (its own header
    comment) -- this re-confirms the defs still resolve with those fields
    live, across the two shapes the file uses: a rollable trait with real
    commonality, and a commonality-0 trait that exists only via a
    backstory's forcedTraits."""
    t.clear_area(size=10)

    with t.component("rollable_trait_resolves", beyond_toggle=True):
        r = _get_defs(t, "TraitDef/RUT_Jawa_WaterDiscipline", "commonality,degreeDatas")
        _expect_field(t, r, "TraitDef/RUT_Jawa_WaterDiscipline", "commonality",
                     lambda v: v not in (None, "(no such field)"), "a numeric commonality")

    with t.component("forced_only_trait_resolves", beyond_toggle=True):
        r = _get_defs(t, "TraitDef/RUT_Jawa_Numbered", "commonality")
        _expect_field(t, r, "TraitDef/RUT_Jawa_Numbered", "commonality",
                     lambda v: v not in (None, "(no such field)") and float(v) == 0.0,
                     "commonality 0 (forcedTraits-only)")   # CORRECTED 2026-10-02: the bridge reads 0.0; str(0.0) != "0"


# =========================================================== backstory defs
@suite.chain("backstory_defs_readback")
def backstory_defs_readback(t):
    """Sample across the seven Backstories_*.xml files and both slots,
    rather than all 77 -- enough to catch a whole-file load break
    (rimworld-custom-loader's own <li>-trap register) without being a
    trivial rubber stamp."""
    t.clear_area(size=10)
    sample = [
        ("RUT_Jawa_AcademyCadet", "Childhood", "JawaBSC_Empire"),
        ("RUT_Jawa_Majordomo", "Adulthood", "JawaBSC_Hutt"),
        ("RUT_Jawa_PurificationEngineer", "Adulthood", "JawaBSC_Deepwater"),
        ("RUT_Jawa_ColdForged", "Childhood", "JawaBSC_FDENightside"),   # CORRECTED 2026-10-02: Backstories_FDE_Droids.xml
        ("RUT_Jawa_AshSpeaker", "Adulthood", "JawaBSC_Tribes"),
        ("RUT_Jawa_MootSpeaker", "Adulthood", "JawaBSC_Moot"),
        ("RUT_Jawa_RetrievalAgent", "Adulthood", "JawaBSC_Helix"),
    ]
    for name, slot, category in sample:
        with t.component("backstory_%s" % name, beyond_toggle=True):
            r = _get_defs(t, "BackstoryDef/%s" % name, "slot,spawnCategories")
            _expect_field(t, r, "BackstoryDef/%s" % name, "slot",
                         lambda v, s=slot: v == s, "slot=%s" % slot)
            _expect_field(t, r, "BackstoryDef/%s" % name, "spawnCategories",
                         lambda v, c=category: c in str(v), "category %s present" % category)


@suite.chain("vqe_rakata_categories_readback")
def vqe_rakata_categories_readback(t):
    """VQE_AncientPatient/VQE_Experiment feed a third-party quest's patient
    pool (see module docstring) -- structural only, no quest fired here."""
    t.clear_area(size=10)
    with t.component("ancient_patient_pool_marked", beyond_toggle=True):
        r = _get_defs(t, "BackstoryDef/RUT_Jawa_RakataSiegeChild", "spawnCategories")
        _expect_field(t, r, "BackstoryDef/RUT_Jawa_RakataSiegeChild", "spawnCategories",
                     lambda v: "VQE_AncientPatient" in str(v), "VQE_AncientPatient present")

    with t.component("experiment_pool_marked", beyond_toggle=True):
        # CORRECTED 2026-10-02: RakataLastGeneration is an ancient-patient childhood; the two
        # VQE_Experiment backstories are RakataTakenChild / RakataFleshShaped (Backstories_Rakata_Sleepers.xml).
        r = _get_defs(t, "BackstoryDef/RUT_Jawa_RakataTakenChild", "spawnCategories")
        _expect_field(t, r, "BackstoryDef/RUT_Jawa_RakataTakenChild", "spawnCategories",
                     lambda v: "VQE_Experiment" in str(v), "VQE_Experiment present")


# ============================================================ patch wiring
@suite.chain("faction_patch_wired_vanilla")
def faction_patch_wired_vanilla(t):
    """The only two PatchOperationConditional targets that exist without any
    other Jawa mod active (Empire needs Royalty; see module docstring)."""
    t.clear_area(size=10)

    with t.component("empire_filter_wired", beyond_toggle=True):
        # CORRECTED 2026-10-02: without deep=True get_defs names only the element TYPE
        # (['BackstoryCategoryFilter', 'BackstoryCategoryFilter']), never its categories.
        r = _get_defs(t, "FactionDef/Empire", "backstoryFilters", deep=True)
        _expect_field(t, r, "FactionDef/Empire", "backstoryFilters",
                     lambda v: "JawaBSC_Empire" in str(v), "JawaBSC_Empire present")

    with t.component("pirate_filter_wired", beyond_toggle=True):
        r = _get_defs(t, "FactionDef/Pirate", "backstoryFilters", deep=True)
        _expect_field(t, r, "FactionDef/Pirate", "backstoryFilters",
                     lambda v: "JawaBSC_Blackstar" in str(v), "JawaBSC_Blackstar present")


@suite.chain("empire_pawn_generation")
def empire_pawn_generation(t):
    """LIVE generation test: a plain vanilla `Colonist` kind (no restrictive
    filters of its own) spawned into the `Empire` faction should draw its
    childhood/adulthood partly from the newly-added JawaBSC_Empire category.
    Probabilistic -- Empire's own raw filters are ImperialCommon+Royalty
    Factions_Empire (2 filters) plus this mod's added JawaBSC_Empire (1
    filter) = roughly 1-in-3 per slot per pawn; 12 pawns x 2 slots gives a
    high but not certain chance of at least one Jawa-flavoured hit."""
    t.clear_area(size=15)
    x, z = t.anchor
    hits = []
    for _ in range(12):
        r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z,
                          faction="Empire", count=1)
        row = ((r or {}).get("pawns") or [{}])[0]
        pid = row.get("id")
        if not pid:
            continue
        t.session.track("pawn", pid, x=x, z=z)
        pd = t.bridge_call("jawa/pawn_get", pawn=pid)
        p = ((pd or {}).get("pawns") or [{}])[0]
        hits.append((p.get("childhood"), p.get("adulthood")))

    with t.component("empire_pawn_draws_flavor_backstory", beyond_toggle=True):
        if not hits:
            raise ExpectationFailed(
                "no Empire-faction pawn spawned at all -- Empire probably does "
                "not exist in this environment (needs Royalty active)")
        flat = [d for pair in hits for d in pair if d]
        found = [d for d in flat if d.startswith("RUT_Jawa_")]
        if not found:
            raise ExpectationFailed(
                "none of %d spawned Empire pawns drew a RUT_Jawa_* backstory: %s"
                % (len(hits), hits))
        t.screenshot()

# Every def this mod ships is loaded and its label is what its XML says (NORTHSTAR_PARTIAL_GAPS_FILL_1;
# 77 BackstoryDefs + 13 TraitDefs; a backstory has a title, not a label, and a trait's label sits in degreeDatas). The Defs/ parse is the list, so a def added later is covered with no edit here.
from modcheck import shipped_defs  # noqa: E402
shipped_defs.add_chain(suite, __file__, fields_by_type={"BackstoryDef": ("title", "titleShort", "slot")},
                       sanity=('RUT_Jawa_CisternHatched', 'RUT_Jawa_WaterWarden'), min_count=85)


# ---------------------------------------------------------------------------------------------------------------------
# PAWNFLAVOR_COVERAGE_GAPS_1. The faction-filter wiring and the defs it feeds, asserted STATICALLY over the mod's own XML
# (so the 9 RUT_Jawa_* operations that cannot apply without mandrake.rut.patches are still checked, against that mod's
# FactionDefs on disk), plus the vanilla names against the offline def dump when one is readable. Each rule is one a
# planted XML break must redden (selftest_pawnflavor_wiring.py). Still UNMEASURED: a live pawn of each faction drawing a
# flavour backstory (needs mandrake.rut.patches loaded), the pirate leak observed on a spawned Junker, and a trait's
# stat effect on a live pawn.
WIRING_FILE = os.path.join(HERE, "Patches", "FactionBackstoryWiring.xml")
PARENT_CATS = {   # what a faction that INHERITS its filters must restate (a declared list OVERRIDES the parent's)
    "OutlanderCivil": ["Outlander", "Offworld"], "RUT_Jawa_HuttCartel": ["Outlander", "Offworld"],
    "RUT_Jawa_WildsteamClan": ["Outlander", "Offworld"], "RUT_Jawa_GeonosianFoundryHive": ["Outlander", "Offworld"],
    "RUT_Jawa_AscendantHelix": ["Outlander", "Offworld"], "RUT_Jawa_DeepwaterCompact": ["Outlander", "Offworld"],
    "TribeCivil": ["Tribal"], "RUT_Jawa_Junkers": ["Pirate"], "RUT_Jawa_FreeDroidEnclaves": [],
}
RAW_FACTIONS = ("Empire", "Pirate", "RUT_Jawa_IndigenousTribes")
LEAK = "JawaBSC_Blackstar"
EFFECT_TAGS = ("statOffsets", "statFactors", "skillGains", "disallowedWorkTags", "disabledWorkTags", "hungerRateFactor",
               "socialFightChanceFactor", "theOnlyAllowedMentalBreaks", "disallowedMentalStates", "disallowedMentalBreaks",
               "marketValueFactorOffset", "randomMentalState", "mentalBreakInc", "needMods", "foodPreferenceFactors", "forcedPassions",
               "painOffset", "painFactor", "plantWorkSpeed", "mentalBreakThresholdOffset", "ingestibleEffects", "meleeDamageFactor")


def load_wiring(path=WIRING_FILE):
    """[(target defName, 'raw'|'declare', [[categories of each li]])] from the patch, in file order."""
    out = []
    for op in ET.parse(path).getroot().findall("Operation"):
        m = re.search(r'defName="([^"]+)"', op.findtext("xpath") or "")
        if m is None:
            continue
        for branch, kind in (("match", "raw"), ("nomatch", "declare")):
            b = op.find(branch)
            if b is None:
                continue
            lis = b.findall("value/li") if kind == "raw" else b.findall("value/backstoryFilters/li")
            out.append((m.group(1), kind, [[c.text for c in li.findall("categories/li")] for li in lis]))
    return out


def load_pack_defs(root=HERE):
    stories, traits = {}, {}
    for f in sorted(glob.glob(os.path.join(root, "Defs", "*.xml"))):
        for e in ET.parse(f).getroot():
            if e.tag == "BackstoryDef":
                stories[e.findtext("defName")] = dict(
                    slot=e.findtext("slot"), cats=[c.text for c in e.findall("spawnCategories/li")],
                    traits=[t.tag for t in e.findall("forcedTraits/*")] + [t.tag for t in e.findall("disallowedTraits/*")])
            elif e.tag == "TraitDef":
                traits[e.findtext("defName")] = e
    return stories, traits


def patch_faction_names():
    """FactionDef defNames the sibling Patches mod ships (where every RUT_Jawa_* faction lives)."""
    names = set()
    for f in glob.glob(os.path.join(HERE, "..", "UtinniPatches", "Defs", "FactionDefs", "*.xml")):
        for e in ET.parse(f).getroot():
            if e.findtext("defName"):
                names.add(e.findtext("defName").strip())
    return names


def dump_names(def_type):
    """defNames of a def type from the newest readable offline def dump, or None (UNMEASURED) when there is none."""
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
        import game_paths as GP
        j = json.load(open(os.path.join(GP.DEF_DUMP, "defs", def_type + ".json"), encoding="utf-8"))
        names = set(d.get("defName") for d in j["defs"])
        return names if len(names) > 5 else None
    except Exception:  # noqa: BLE001
        return None


def about_counts(root=HERE):
    t = ET.parse(os.path.join(root, "About", "About.xml")).getroot().findtext("description") or ""
    return t


WORDS = {"seven": 7, "eight": 8, "fifty": 50, "five": 5, "seventy-seven": 77, "thirteen": 13, "thirty": 30, "forty-seven": 47, "eleven": 11}


# Traits that are deliberately label-only until their C# hook lands. Each is also required to carry a preceding XML comment
# saying so (trait_comments), and an entry that has since gained a real effect must be removed from this list.
DEFERRED_LABEL_ONLY = ("RUT_Jawa_ReapsTheFlames", "RUT_Jawa_StillTemper", "RUT_Jawa_FreedomScarred")


def trait_comments(root=HERE):
    """{trait defName: the XML comment immediately before its <TraitDef>} from the raw file text."""
    txt = open(os.path.join(root, "Defs", "Traits_JawaPawnFlavor.xml"), encoding="utf-8").read()
    return dict((m.group(2), m.group(1)) for m in re.finditer(r"<!--((?:(?!-->).)*?)-->\s*<TraitDef>\s*<defName>(\w+)</defName>", txt, re.S))


def wiring_findings(wiring, stories, traits, patch_factions, vanilla_factions=None, vanilla_traits=None, about=None, comments=None):
    """Findings for: restated parent categories, one flavour category per filter, the pirate leak's containment, every wired
    category drawable in both slots, no orphan flavour category, targets that exist, traits that do something, forced
    traits that resolve, and About's own counts."""
    bad = []
    by_target = {}
    for tgt, kind, lis in wiring:
        by_target.setdefault(tgt, []).append((kind, lis))
    flat = lambda lis: [c for cats in lis for c in cats]            # noqa: E731
    if len(by_target) < 11:
        bad.append("wiring parse found %d faction targets, want >= 11 (sanity probe failed)" % len(by_target))
    for tgt in RAW_FACTIONS:
        ops = by_target.get(tgt, [])
        if [k for k, _l in ops] != ["raw"]:
            bad.append("%s: expected exactly one raw `add a filter` operation, found %r" % (tgt, [k for k, _l in ops]))
        elif len([c for c in flat(ops[0][1]) if c.startswith("JawaBSC_")]) != 1 or len(ops[0][1]) != 1:
            bad.append("%s: the added filter must name exactly one JawaBSC_ category: %r" % (tgt, ops[0][1]))
    for tgt, parent in PARENT_CATS.items():
        ops = by_target.get(tgt, [])
        if [k for k, _l in ops] != ["declare"]:
            bad.append("%s: expected exactly one declared filter list (a child's own list OVERRIDES the parent's), found %r" % (tgt, [k for k, _l in ops]))
            continue
        cats = flat(ops[0][1])
        for pc in parent:
            if pc not in cats:
                bad.append("%s: its declared filters drop the parent's %s category (the override would strip vanilla pawns)" % (tgt, pc))
        flavour = [c for c in cats if c.startswith("JawaBSC_")]
        want = 2 if tgt == "RUT_Jawa_FreeDroidEnclaves" else 1
        if len(flavour) != want:
            bad.append("%s: declares %d JawaBSC_ categories, want %d: %r" % (tgt, len(flavour), want, flavour))
        if any(c not in parent and not c.startswith("JawaBSC_") for c in cats):
            bad.append("%s: declares a vanilla category its parent does not supply: %r" % (tgt, cats))
    leakers = sorted(t for t, ops in by_target.items() if any(LEAK in flat(l) for _k, l in ops))
    if leakers != ["Pirate"]:
        bad.append("pirate leak containment: %s is wired to %r, want only Pirate (the abstract PirateBandBase leaks to siblings; Junkers must override it)" % (LEAK, leakers))
    junk = by_target.get("RUT_Jawa_Junkers", [])
    if not junk or LEAK in flat(junk[0][1]) or "Pirate" not in flat(junk[0][1]):
        bad.append("RUT_Jawa_Junkers must declare its own list with Pirate and WITHOUT %s (it inherits PirateBandBase, the leak's route)" % LEAK)
    wired = sorted(set(c for ops in by_target.values() for _k, l in ops for c in flat(l) if c.startswith("JawaBSC_")))
    for c in wired:
        slots = set(v["slot"] for v in stories.values() if c in v["cats"])
        if slots != {"Childhood", "Adulthood"}:
            bad.append("category %s is wired to a faction but has backstories for slots %s only (a pawn draw in the other slot falls through)" % (c, sorted(slots)))
    drawn = set(c for v in stories.values() for c in v["cats"] if c.startswith("JawaBSC_"))
    for c in sorted(drawn - set(wired)):
        bad.append("category %s has backstories but no faction wires it (they can never be drawn)" % c)
    for tgt in sorted(by_target):
        if tgt in patch_factions:
            continue
        if vanilla_factions is not None and tgt in vanilla_factions:
            continue
        if vanilla_factions is None and not tgt.startswith("RUT_Jawa_"):
            continue   # a vanilla name with no dump to check against: reported UNMEASURED by the chain, not a finding
        bad.append("wiring targets FactionDef %s, which neither the Patches mod nor the vanilla def dump defines (a patch that matches nothing logs nothing)" % tgt)
    comments = comments if comments is not None else {}
    for name, tdef in sorted(traits.items()):
        degrees = tdef.findall("degreeDatas/li")
        effect = bool(degrees) and all(any(d.find(tag) is not None and (list(d.find(tag)) or (d.findtext(tag) or "").strip()) for tag in EFFECT_TAGS) for d in degrees)
        if name in DEFERRED_LABEL_ONLY:
            if effect:
                bad.append("trait %s now has a real effect: remove it from DEFERRED_LABEL_ONLY" % name)
            elif not re.search(r"C#|hook|Neither is faked", comments.get(name, "")):
                bad.append("trait %s is label-only but its XML comment no longer says a C# hook is pending" % name)
        elif not effect:
            bad.append("trait %s has a degree with no mechanical effect (a label and a description only)" % name)
        if not all((d.findtext("label") or "").strip() and (d.findtext("description") or "").strip() for d in degrees):
            bad.append("trait %s has a degree with no label or description" % name)
    for sname, v in sorted(stories.items()):
        for tr in v["traits"]:
            if tr in traits:
                continue
            if vanilla_traits is not None and tr in vanilla_traits:
                continue
            if vanilla_traits is None and not tr.startswith("RUT_Jawa_"):
                continue
            bad.append("backstory %s names trait %s, which neither the pack nor the vanilla dump defines" % (sname, tr))
    if about is not None:
        n_child = sum(1 for v in stories.values() if v["slot"] == "Childhood")
        n_adult = sum(1 for v in stories.values() if v["slot"] == "Adulthood")
        low = about.lower()
        for word, n in (("seventy-seven", len(stories)), ("thirteen backstory", None), ("thirteen traitdefs", len(traits))):
            if n is None:
                continue
            if word not in low:
                bad.append("About.xml no longer says %r; the shipped count is %d" % (word, n))
            elif WORDS[word.split()[0]] != n:
                bad.append("About.xml says %r but %d are shipped" % (word, n))
        if "%d childhoods, %d adulthoods" % (n_child, n_adult) not in low:
            bad.append("About.xml's childhood/adulthood split is not %d/%d" % (n_child, n_adult))
        m = re.search(r"the other (\w+) inherit", low)
        restating = sum(1 for t_, p_ in PARENT_CATS.items() if p_)
        if m is None or WORDS.get(m.group(1)) != restating:
            bad.append("About.xml says %r inherit filters but %d targets restate a parent's categories" % (m.group(1) if m else None, restating))
        if "thirteen faction categories" not in low or len(drawn) != 13:
            bad.append("About.xml's 'thirteen faction categories' does not match the %d JawaBSC_ categories shipped" % len(drawn))
    return bad


def _all_findings(vanilla=True):
    stories, traits = load_pack_defs()
    van_f = dump_names("FactionDef") if vanilla else None
    van_t = dump_names("TraitDef") if vanilla else None
    return wiring_findings(load_wiring(), stories, traits, patch_faction_names(), van_f, van_t, about_counts(), trait_comments()), van_f, van_t


@suite.chain("faction_wiring_static")
def faction_wiring_static(t):
    found, van_f, van_t = _all_findings()

    def pick(keys):
        return [f for f in found if any(k in f for k in keys)]
    with t.component("inherited_filters_restate_the_parent_and_add_one_flavour_category", beyond_toggle=True):
        bad = pick(["declared filter", "drop the parent", "JawaBSC_ categor", "vanilla category", "raw `add", "added filter", "sanity probe"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("blackstar_does_not_leak_into_the_junkers", beyond_toggle=True):
        bad = pick(["leak", "Junkers"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("every_wired_category_is_drawable_in_both_slots_and_none_is_orphaned", beyond_toggle=True):
        bad = pick(["slots", "no faction wires"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("all_nine_modded_and_the_vanilla_targets_exist", beyond_toggle=True):
        bad = pick(["wiring targets FactionDef"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
        if van_f is None:
            t.upstream_reason = "UNMEASURED: no readable offline def dump, so the vanilla targets (Empire, Pirate, OutlanderCivil, TribeCivil) were not looked up"
            t.upstream_failed = True
    with t.component("every_trait_does_something_and_forced_traits_resolve", beyond_toggle=True):
        bad = pick(["trait ", "names trait"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
        if van_t is None:
            t.upstream_reason = "UNMEASURED: no readable offline def dump, so backstory forcedTraits naming vanilla traits were not looked up"
            t.upstream_failed = True
    with t.component("about_counts_match_the_shipped_defs", beyond_toggle=True):
        bad = pick(["About.xml"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("no_finding_escapes_the_bars_above", beyond_toggle=True):
        known = ["declared filter", "drop the parent", "JawaBSC_ categor", "vanilla category", "raw `add", "added filter", "sanity probe",
                 "leak", "Junkers", "slots", "no faction wires", "wiring targets FactionDef", "trait ", "names trait", "About.xml", "label-only", "DEFERRED_LABEL_ONLY"]
        stray = [f for f in found if not any(k in f for k in known)]
        if stray:
            raise ExpectationFailed("finding(s) no bar claims: %s" % "; ".join(stray))
    with t.component("label_only_traits_are_the_declared_deferred_ones", beyond_toggle=True):
        bad = pick(["label-only", "DEFERRED_LABEL_ONLY"])
        if bad:
            raise ExpectationFailed("; ".join(bad))
        if t._guard():
            t.upstream_reason = ("UNMEASURED: %d traits (%s) are label-only until their C# hooks land (their XML comments say so): "
                                 "they do nothing yet, by declaration" % (len(DEFERRED_LABEL_ONLY), ", ".join(DEFERRED_LABEL_ONLY)))
            t.upstream_failed = True
    with t.component("live_draw_per_faction_and_trait_effect_state_read", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: a spawned pawn of each RUT_Jawa_* faction drawing a flavour backstory (needs mandrake.rut.patches loaded), "
                                 "a Junker never drawing Blackstar, and a trait's stat effect on a live pawn; the wiring and defs are asserted statically above")
            t.upstream_failed = True
