"""validation.py -- modcheck suite for RimUtinni ResearchRetag (mandrake.rut.researchretag).

Pure-XML patch mod: no C#, no Assemblies, no ModSettings class anywhere in
`src/RimUtinni/ResearchRetag/` (confirmed by directory listing -- only
About.xml, one Defs file, and three Patches files). Per the briefing's own
rule for this shape: `suite.toggles = []`, every component is
`beyond_toggle=True`.

THE REAL TEST-ENVIRONMENT PROBLEM, read from the mod itself, not assumed:
`RUT_ResearchRetag.xml` retags 269 `ResearchProjectDef`s and
`RUT_ResearchTabAssign.xml` retabs another set, but the overwhelming
majority of those defNames belong to OTHER, optional mods named in
`About.xml`'s 52-entry `forceLoadAfter` list (`ABF_ResearchProject_*`,
`AM_*`, `CGT_*`, `BMT_*`, ...) -- and every operation here is a
`PatchOperationConditional` specifically because most targets will be
ABSENT in many mod configurations (CLAUDE.md: "A patch that matches
nothing logs nothing" / "PatchOperationConditional ... return[s] true on
no match"). Against modcheck's own environment rule ("minimal mechanism
list + the mod under test", no dependency mods pulled in for a pure patch
mod with no declared `modDependencies`), essentially every one of those
269+ rows would silently no-op, and a validator built on any of them would
be un-provably green -- exactly the "zero rows is a failure, not a
footnote" trap (project memory) if left unguarded.

**The fix, not a workaround**: `infrastructure/output/research_manifest_draft.csv`
(the frozen source these patches were generated from) names each row's
`source_mod`. Five of the 269 retagged rows -- `AirConditioning`,
`Autodoors`, `CarpetMaking`, `ColoredLights`, `Cryptosleep` -- are
`source_mod=Core`: real vanilla `ResearchProjectDef`s that exist in EVERY
mod configuration, minimal or full, with or without any of the 52
`forceLoadAfter` mods installed. These five are the validator's targets,
confirmed present in both `RUT_ResearchRetag.xml` (techLevel/baseCost/
prerequisites) and `RUT_ResearchTabAssign.xml` (tab) by direct grep before
writing this file -- not guessed from the manifest alone.

Expected values below are copied verbatim from the patch XML itself
(`RUT_ResearchRetag.xml` lines ~393-933, `RUT_ResearchTabAssign.xml` lines
~51-5827), not from the manifest CSV, so a future regenerate-from-manifest
drift would be caught here even if the manifest and the generator disagree.

Still not proven / likely first-live-run corrections:
  1. The other ~264 retagged rows and the Supplement file's 13 rows
     (`RUT_ResearchRetag_Supplement.xml`) are NOT independently
     live-checked -- their operations are structurally identical
     `PatchOperationConditional`/`Replace`/`Add` triples to the five
     proven here, so the MECHANISM is the same, but their specific
     target defNames' presence depends on which of the 52 optional mods
     are actually in whatever list the runner uses. A full-modlist
     modcheck pass (not the minimal list) would be needed to check them
     for real; that is out of this validator's floor.
  2. `RESEARCH_RETAG_LOAD_ORDER_GAP_1`'s `forceLoadAfter` ordering itself
     (does RimSort/the game actually load this mod after all 52 named
     packageIds) has no bridge read-back at all -- `jawa/list_factions`-
     style load-order introspection was not found in a tool search: this
     validator cannot see load order, only resolved end-state def values,
     which is silent to an ordering bug that a LATER mod's own patch
     happens to still leave in the state this mod wants.
  3. `RETAG_BUILDER_SELF_ERASE_1` (the generator bug documented in the
     Supplement's own header) is a generator-code defect, not a def-state
     defect -- nothing observable at runtime distinguishes a row the
     generator would currently erase from one it would not. Out of scope
     for a live def check by construction.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("ResearchRetag")
suite.toggles = []

TAB_DEFS = {
    "RUT_Tree_Scavenging": "jawa scavenging",
    "RUT_Tree_Refinery": "the refinery",
    "RUT_Tree_Workshop": "the workshop",
    "RUT_Tree_Hearth": "the hearth",
    "RUT_Tree_PowderAndSlug": "powder & slug",
    "RUT_Tree_Utinni": "the utinni",
    "RUT_Tree_Shell": "the shell",
    "RUT_Tree_Unbolting": "the unbolting",
    "RUT_Tree_Blasterworks": "blasterworks",
    "RUT_Tree_WakingMind": "the waking mind",
    "RUT_Tree_Reach": "the reach",
    "RUT_Tree_AscendantLadder": "the ascendant ladder",
    "RUT_Tree_StrangeSchools": "the strange schools",
    "RUT_Tree_JunkerYards": "the junker yards",
    "RUT_Tree_FoundryHive": "the foundry hive",
}

# defName -> (expected field values), verbatim from RUT_ResearchRetag.xml +
# RUT_ResearchTabAssign.xml, restricted to source_mod=Core rows (research_
# manifest_draft.csv) so every target is guaranteed loaded regardless of
# which optional mods the runner's environment carries.
CORE_RETAG_ROWS = {
    "AirConditioning": {"baseCost": "700", "tab": "RUT_Tree_Scavenging"},
    "Autodoors": {"baseCost": "1700", "tab": "RUT_Tree_Scavenging"},
    "CarpetMaking": {"techLevel": "Industrial", "tab": "RUT_Tree_Hearth"},
    "ColoredLights": {"baseCost": "700", "tab": "RUT_Tree_Hearth"},
    "Cryptosleep": {"techLevel": "Industrial", "tab": "RUT_Tree_Reach",
                    "prerequisites": "VitalsMonitor"},
}


def _live(t):
    """See the equivalent helper in Pyrelands/validation.py -- same
    reasoning: distinguishes a real chain run from `Suite.
    components_declared()`'s offline no-op probe (`t.session is None`)."""
    return t.session is not None and not t.upstream_failed


@suite.chain("own_tab_defs")
def own_tab_defs(t):
    """This mod's OWN 15 `ResearchTabDef`s (`Defs/ResearchTabDefs/
    RUT_Tree_Defs.xml`) -- always loaded whenever ResearchRetag is in the
    mod list at all, independent of every other mod. The one part of this
    mod's content that is not a patch onto someone else's def."""
    t.clear_area(size=8)   # no map state involved; keeps the runner's
                            # evidence/screenshot machinery uniform

    with t.component("research_tabs_resolve", beyond_toggle=True):
        pairs = ";".join("ResearchTabDef/%s" % name for name in TAB_DEFS)
        r = t.bridge_call("jawa/get_defs", defs=pairs, fields="label,generalTitle")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                bad.append("not found: %r" % not_found)
            for name, expect_label in TAB_DEFS.items():
                row = rows.get(name)
                if row is None:
                    continue  # already covered by not_found above
                got_label = (row.get("fields") or {}).get("label")
                if got_label != expect_label:
                    bad.append("%s: expected label=%r, got %r" % (name, expect_label, got_label))
            if bad:
                raise ExpectationFailed(
                    "RUT_Tree_* ResearchTabDefs did not resolve as shipped: %s" % "; ".join(bad))
        t.screenshot()


@suite.chain("core_rows_retagged")
def core_rows_retagged(t):
    """Five vanilla-Core `ResearchProjectDef`s the retag actually touches
    (see module docstring for why these five, specifically, are the only
    safe live targets in an environment with none of the 52 optional
    donor mods installed). One `jawa/get_defs` call proves BOTH patch
    files at once: techLevel/baseCost/prerequisites from
    `RUT_ResearchRetag.xml`, `tab` from the separate, hand-authored
    `RUT_ResearchTabAssign.xml`."""
    t.clear_area(size=8)

    with t.component("core_rows_match_manifest", beyond_toggle=True):
        pairs = ";".join("ResearchProjectDef/%s" % name for name in CORE_RETAG_ROWS)
        r = t.bridge_call("jawa/get_defs", defs=pairs,
                          fields="baseCost,techLevel,tab,prerequisites")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                # These are vanilla Core rows -- absence here means Core
                # itself failed to load, or the patch xpath is broken, not
                # a "some optional mod is missing" case. A real failure,
                # not a footnote.
                bad.append("vanilla Core rows not found at all: %r" % not_found)
            for name, expect in CORE_RETAG_ROWS.items():
                row = rows.get(name)
                if row is None:
                    continue
                fields = row.get("fields") or {}
                for field, expect_value in expect.items():
                    got = fields.get(field)
                    if field == "prerequisites":
                        got_list = got if isinstance(got, list) else ([got] if got else [])
                        if expect_value not in got_list:
                            bad.append("%s.prerequisites: expected %r in %r"
                                       % (name, expect_value, got_list))
                    elif str(got) != str(expect_value):
                        bad.append("%s.%s: expected %r, got %r"
                                   % (name, field, expect_value, got))
            if bad:
                raise ExpectationFailed(
                    "Core research rows do not match the retag/tab-assign patches: %s"
                    % "; ".join(bad))
        t.screenshot()
