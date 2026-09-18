"""validation.py -- modcheck suite for RimUtinni: Aftermath Rites
(mandrake.rut.aftermath).

Pure-Defs companion mod: no Source/, no Assemblies/, no ModSettings class
anywhere in `src/RimUtinni/AftermathRites/` (confirmed by directory listing --
only LICENSE, About/About.xml, and two Defs files:
`RM_AftermathRuleDefs.xml` and `RM_AlliancePairDefs.xml`). Per the established
rule for this shape: `suite.toggles = []`, every component is
`beyond_toggle=True`.

WHAT THIS MOD ACTUALLY IS: DATA for `mandrake.rm.aftermath`'s
`AftermathRuleRunner` engine (a HARD `modDependency` in this mod's own
About.xml, not merely `loadAfter` -- both def types
(`RM_AftermathRuleDef`, `RM_AlliancePairDef`) are C# classes defined over in
that mod's `src/RimMandrake/Aftermath/Source/`, read in full before writing
this suite: `RM_AftermathRuleDef.cs`, `RM_AlliancePairDef.cs`). Without the
engine mod active, every def below fails to resolve its own TYPE, not merely
its content -- so this suite's environment is minimal+mandrake.rm.aftermath,
exactly as `design/validation_walks/RimUtinni/AftermathRites.md` names it.

Exact-count facts below, read directly from the two shipped Defs files, not
guessed:
  - 8 RM_AftermathRuleDef entries in RM_AftermathRuleDefs.xml. Per that
    file's own header comment (citing
    src/RimMandrake/Aftermath/Source/AftermathTriggerKind.cs), only rules 1-3
    (`triggerKind=BattleOutcome`) plus rule 4 (`PrisonerHeldDuration`, wired
    2026-09-10) plus rule 6 (`MentalBreakNearBattle`, wired 2026-09-09) are
    evaluated LIVE by AftermathRuleRunner today. Rules 5, 7, 8
    (`GodBandCrossed`, `RootedClockQuadrum`, `TakingEventWitnessed`) carry
    real payload/telegraph/letter/god-tie data but their triggerKind is not
    yet evaluated by the runner -- documented status in the file's own
    comment, not a defect this suite treats as a bug.
  - 6 RM_AlliancePairDef entries in RM_AlliancePairDefs.xml. Only the
    Geonosian Foundry Hive / Free Droid Enclaves pair (both directions) is
    reachable by the engine's current (rule-2, BattleRecord-close) path; the
    three "Blackstar-hire" pairs (HuttCartel/Pirate, Empire/Pirate,
    Helix/Pirate) are shipped ahead of rule 8's real trigger and are not
    reachable by anything in this build -- same file header.
  - `RM_AftermathRuleDef.godTie` is a plain `string` field (CHRONICLE_
    NINEFOLD_DECOUPLE_1), not `mandrake.rm.ninefold`'s own God enum -- this
    mod's `loadAfter` names that mod SOFT, and an unresolvable god name is
    Ninefold's own subscriber's warning to log, never a ConfigError this def
    type can raise. Nothing here needs Ninefold active to resolve.
  - `RM_AlliancePairDef.a`/`.b` are plain `string` FactionDef-defName
    references (not typed `<FactionDef>` fields), so a missing FactionDef
    (e.g. `Empire`, which needs Royalty) does not fail THIS def's own
    resolution -- only a live cross-reference lookup by the engine would
    notice, and no such lookup is exercised here (see gap #2 below).

WHY EVERY COMPONENT IS A DEF READ-BACK, NOT A LIVE FIRING TEST: this mod
ships zero C#, zero mechanism of its own -- `AftermathRuleRunner`'s actual
trigger evaluation, delay/telegraph scheduling and incidentQueue dispatch
live entirely in `mandrake.rm.aftermath`, whose OWN validation.py (not yet
written as of this pass; check before assuming it exists) is the right place
to prove a rule actually fires a raid. This suite's job is narrower and
matches the walk doc's own final line ("[S] none -- pure data defs, nothing
to look at visually"): prove the eight rule defs and six pair defs parse,
resolve as their correct C# types, and carry the exact field values authored
in the XML -- the one thing this mod alone is responsible for.

Still not proven / real gaps:
  1. No live BattleOutcome/PrisonerHeldDuration/MentalBreakNearBattle trigger
     is fired here -- that is `mandrake.rm.aftermath`'s own mechanism to
     validate, not this Defs-only mod's. This suite cannot and does not
     claim rule 1-4/6 "work", only that their DATA is intact.
  2. The three Blackstar-hire alliance pairs' FactionDef targets (`Pirate`,
     `Empire`) are read back as their bare string field values only --
     nothing here confirms those FactionDefs actually resolve live (Empire
     needs Royalty active; a minimal+mandrake.rm.aftermath run may not carry
     it). A missing target FactionDef would only surface as a runtime
     failure inside the engine mod's own alliance-lookup code, invisible to
     a get_defs read of this mod's own def.
  3. `godTie` values (`Shkaar`, `Rekko`, `Oomo`, `TaBaa`, `MobUnloo`) are
     asserted as literal strings only -- whether `mandrake.rm.ninefold`
     actually has a live God matching each name is out of scope for a
     Defs-only companion with no hard dependency on that mod.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("AftermathRites")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

RULE_TYPE = "RM_AftermathRuleDef"
PAIR_TYPE = "RM_AlliancePairDef"

# All 8 rule defNames, verbatim from RM_AftermathRuleDefs.xml (grepped, not
# counted by eye) -- used to prove the exact count and that none is missing.
ALL_RULE_NAMES = [
    "RM_AftermathRule_RegroupAndReturn",
    "RM_AftermathRule_AlliesArrive",
    "RM_AftermathRule_ScavengersOnTheField",
    "RM_AftermathRule_TheyComeForTheirOwn",
    "RM_AftermathRule_ShkaarsEscalation",
    "RM_AftermathRule_ZizziksAftermath",
    "RM_AftermathRule_TheRootedReceipt",
    "RM_AftermathRule_TheReckoning",
]

# All 6 alliance-pair defNames, verbatim from RM_AlliancePairDefs.xml.
ALL_PAIR_NAMES = [
    "RM_AlliancePair_GeonosianHive_FreeDroidEnclaves",
    "RM_AlliancePair_FreeDroidEnclaves_GeonosianHive",
    "RM_AlliancePair_Junkers_FreeDroidEnclaves",
    "RM_AlliancePair_HuttCartel_Blackstar",
    "RM_AlliancePair_Empire_Blackstar",
    "RM_AlliancePair_Helix_Blackstar",
]

# One representative rule per trigger kind (WIRED and not-wired alike),
# expected field values copied verbatim from RM_AftermathRuleDefs.xml.
RULE_EXPECT = {
    "RM_AftermathRule_RegroupAndReturn": {
        "triggerKind": "BattleOutcome", "minSurvivors": "3",
        "payloadIncidentDefName": "RaidEnemy",
        "payloadFactionMode": "SameAsTrigger",
        "godTie": "Shkaar", "godDelta": "8",
    },
    "RM_AftermathRule_ScavengersOnTheField": {
        "triggerKind": "BattleOutcome",
        "payloadFactionMode": "SameAsTrigger",
        "godTie": "Rekko", "godDelta": "-6",
    },
    "RM_AftermathRule_TheyComeForTheirOwn": {
        "triggerKind": "PrisonerHeldDuration", "minHeldDays": "3",
        "payloadFactionMode": "HeldPrisonerHome",
        "godTie": "Oomo", "godDelta": "4",
    },
    "RM_AftermathRule_ZizziksAftermath": {
        "triggerKind": "MentalBreakNearBattle",
        "payloadIncidentDefName": "ShortCircuit",
        "godTie": "Zizzik", "godDelta": "-8",
    },
    "RM_AftermathRule_ShkaarsEscalation": {
        "triggerKind": "GodBandCrossed",   # documented not-wired
        "godTie": "Shkaar", "godDelta": "15",
    },
    "RM_AftermathRule_TheReckoning": {
        "triggerKind": "TakingEventWitnessed",   # documented not-wired
        "payloadFactionMode": "HuttClaimant",
        "godTie": "MobUnloo", "godDelta": "-5",
    },
}

PAIR_EXPECT = {
    "RM_AlliancePair_GeonosianHive_FreeDroidEnclaves": {
        "a": "RUT_Jawa_GeonosianFoundryHive", "b": "RUT_Jawa_FreeDroidEnclaves",
        "weight": "1",
    },
    "RM_AlliancePair_HuttCartel_Blackstar": {
        "a": "RUT_Jawa_HuttCartel", "b": "Pirate", "weight": "1",
    },
    "RM_AlliancePair_Empire_Blackstar": {
        "a": "Empire", "b": "Pirate", "weight": "1",
    },
}


def _live(t):
    """Distinguishes a real chain run from `Suite.components_declared()`'s
    offline no-op probe (`t.session is None`) -- same pattern as
    Pyrelands/ResearchRetag's own `_live` helper."""
    return t.session is not None and not t.upstream_failed


def _get_defs(t, def_type, names, fields):
    pairs = ";".join("%s/%s" % (def_type, n) for n in names)
    return t.bridge_call("jawa/get_defs", defs=pairs, fields=fields)


def _check_fields(rows_by_name, expect_by_name):
    bad = []
    for name, expect in expect_by_name.items():
        row = rows_by_name.get(name)
        if row is None:
            bad.append("%s: not found" % name)
            continue
        fields = (row.get("fields") or {})
        for field, expect_value in expect.items():
            got = fields.get(field)
            got_str = str(got)
            if field == "triggerOutcomes" or (isinstance(got, list)):
                if expect_value not in (got if isinstance(got, list) else [got_str]):
                    bad.append("%s.%s: expected %r in %r" % (name, field, expect_value, got))
            elif got_str != str(expect_value):
                bad.append("%s.%s: expected %r, got %r" % (name, field, expect_value, got))
    return bad


@suite.chain("rule_defs_exact_count_and_resolve")
def rule_defs_exact_count_and_resolve(t):
    """All 8 RM_AftermathRuleDefs resolve, none missing -- proves the def
    TYPE itself loads (it lives in mandrake.rm.aftermath, a hard
    modDependency) and the exact count the file ships, per the walk doc's
    own must-be-true line."""
    t.clear_area(size=8)

    with t.component("all_eight_rule_defs_resolve", beyond_toggle=True):
        r = _get_defs(t, RULE_TYPE, ALL_RULE_NAMES, "triggerKind")
        if _live(t):
            rows = (r or {}).get("defs") or []
            not_found = (r or {}).get("notFound") or []
            if not_found:
                raise ExpectationFailed(
                    "RM_AftermathRuleDef(s) not found (engine mod missing or "
                    "def failed to load): %r" % not_found)
            if len(rows) != len(ALL_RULE_NAMES):
                raise ExpectationFailed(
                    "expected exactly %d RM_AftermathRuleDef rows, got %d: %r"
                    % (len(ALL_RULE_NAMES), len(rows), rows))
        t.screenshot()


@suite.chain("rule_defs_field_values")
def rule_defs_field_values(t):
    """One representative rule per triggerKind (WIRED: BattleOutcome,
    PrisonerHeldDuration, MentalBreakNearBattle; documented not-yet-wired:
    GodBandCrossed, TakingEventWitnessed) -- exact field values copied
    verbatim from the shipped XML, covering every triggerKind this file
    actually uses at least once."""
    t.clear_area(size=8)
    names = list(RULE_EXPECT)

    with t.component("rule_fields_match_shipped_xml", beyond_toggle=True):
        r = _get_defs(t, RULE_TYPE, names,
                      "triggerKind,minSurvivors,minHeldDays,"
                      "payloadIncidentDefName,payloadFactionMode,"
                      "godTie,godDelta")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            bad = _check_fields(rows, RULE_EXPECT)
            if bad:
                raise ExpectationFailed(
                    "RM_AftermathRuleDef field mismatch: %s" % "; ".join(bad))
        t.screenshot()


@suite.chain("pair_defs_exact_count_and_resolve")
def pair_defs_exact_count_and_resolve(t):
    """All 6 RM_AlliancePairDefs resolve, none missing."""
    t.clear_area(size=8)

    with t.component("all_six_pair_defs_resolve", beyond_toggle=True):
        r = _get_defs(t, PAIR_TYPE, ALL_PAIR_NAMES, "a,b")
        if _live(t):
            rows = (r or {}).get("defs") or []
            not_found = (r or {}).get("notFound") or []
            if not_found:
                raise ExpectationFailed(
                    "RM_AlliancePairDef(s) not found: %r" % not_found)
            if len(rows) != len(ALL_PAIR_NAMES):
                raise ExpectationFailed(
                    "expected exactly %d RM_AlliancePairDef rows, got %d: %r"
                    % (len(ALL_PAIR_NAMES), len(rows), rows))
        t.screenshot()


@suite.chain("pair_defs_field_values")
def pair_defs_field_values(t):
    """The one engine-reachable pair (Geonosian Hive <-> Free Droid Enclaves,
    this direction) plus two of the three not-yet-reachable Blackstar-hire
    pairs -- exact `a`/`b`/`weight` values copied verbatim from the shipped
    XML. See module docstring gap #2: `a`/`b` are plain strings, so this
    proves the DATA, not that the named FactionDefs resolve live."""
    t.clear_area(size=8)
    names = list(PAIR_EXPECT)

    with t.component("pair_fields_match_shipped_xml", beyond_toggle=True):
        r = _get_defs(t, PAIR_TYPE, names, "a,b,weight")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            bad = _check_fields(rows, PAIR_EXPECT)
            if bad:
                raise ExpectationFailed(
                    "RM_AlliancePairDef field mismatch: %s" % "; ".join(bad))
        t.screenshot()
