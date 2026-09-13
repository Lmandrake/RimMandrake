"""validation.py -- modcheck suite for PawnFlavor (mandrake.rut.pawnflavor).

Pure-XML content mod: no Source/ folder, no C# at all, therefore no
ModSettings class -- `suite.toggles = []` and every component below is
`beyond_toggle=True` (per the briefing's own documented case for a mod with
no Mod Settings yet).

Grounded in the mod's actual Defs/ and Patches/ (read in full for this pass),
NOT in About.xml's own description, which is stale: it says "Fifty
BackstoryDefs ... five TraitDefs" but the current tree carries **77**
BackstoryDefs across 7 files and **13** TraitDefs (rounds 5-9 added more
after that description was written -- not fixed here, out of this task's
scope, but worth a note for whoever next touches About.xml).

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
from modcheck import Suite, ExpectationFailed

suite = Suite("PawnFlavor")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle


def _get_defs(t, defs, fields):
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
                     lambda v: str(v) == "0", "commonality 0 (forcedTraits-only)")


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
        ("RUT_Jawa_ColdForged", "Adulthood", "JawaBSC_FDECathedral"),
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
        r = _get_defs(t, "BackstoryDef/RUT_Jawa_RakataLastGeneration", "spawnCategories")
        _expect_field(t, r, "BackstoryDef/RUT_Jawa_RakataLastGeneration", "spawnCategories",
                     lambda v: "VQE_Experiment" in str(v), "VQE_Experiment present")


# ============================================================ patch wiring
@suite.chain("faction_patch_wired_vanilla")
def faction_patch_wired_vanilla(t):
    """The only two PatchOperationConditional targets that exist without any
    other Jawa mod active (Empire needs Royalty; see module docstring)."""
    t.clear_area(size=10)

    with t.component("empire_filter_wired", beyond_toggle=True):
        r = _get_defs(t, "FactionDef/Empire", "backstoryFilters")
        _expect_field(t, r, "FactionDef/Empire", "backstoryFilters",
                     lambda v: "JawaBSC_Empire" in str(v), "JawaBSC_Empire present")

    with t.component("pirate_filter_wired", beyond_toggle=True):
        r = _get_defs(t, "FactionDef/Pirate", "backstoryFilters")
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
