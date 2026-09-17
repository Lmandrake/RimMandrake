"""validation.py -- modcheck suite for RimStarWars Jawa Rules
(mandrake.rsw.jawarules).

Grounded in the mod's actual Source, read whole before writing this:
`JawaRules.cs` (the five independently-armed Harmony rules -- three
postfixes, two transpilers, each patched by hand via `Apply()`/
`ApplyTranspiler()` rather than `PatchAll`, "so a wrong target throws inside
a static constructor... [and does not kill] the WHOLE MOD" per the class's
own header comment) and `RSW_JawaRulesSettings.cs` (the seven `public
static` Mod Settings fields this suite's `suite.toggles` lists). This mod
ships NO `Defs/` folder at all (checked: `find Defs` on this tree returns
nothing) -- same register as `StructureInjections`' own docstring: every
rule here patches vanilla/DLC methods and vanilla/DLC content, so full
behavioral proof of what a rule GATES depends on content this mod does not
own and must not guess at.

THE FIVE RULES, exactly as `JawaRulesMod`'s static constructor arms them:
  1. no-sow            Patch_GrowerSow_ExtraRequirements (postfix on
                        WorkGiver_GrowerSow.ExtraRequirements) -- a pawn
                        whose Xenotype.defName == "RSW_MandrakeJawa" can
                        never be given a Sow job.
  2. droid-relations    Patch_CreateInitialComponents (postfix on
                        PawnComponentsUtility.CreateInitialComponents) --
                        any Humanlike pawn generated with relations==null
                        gets a Pawn_RelationsTracker attached.
  3. pet-names          Patch_GenerateNecessaryName (postfix on
                        Pawn.GenerateNecessaryName) -- a tamed/newborn
                        player-faction animal with no chosen name draws one
                        from its own race's nameGenerator instead of
                        vanilla's numeric fallback.
  4. world-labels       Patch_WorldFeatures_UpdateAlpha (TRANSPILER on
                        WorldFeatures.UpdateAlpha) -- the one `0.3f` alpha
                        constant becomes a live read of
                        RSW_JawaRulesSettings.CurrentWorldLabelAlpha().
  5. world-label-lift   Patch_WorldFeatureText_Lift (TRANSPILER on
                        WorldFeatureTextMesh_TextMeshPro.WrapAroundPlanet
                        Surface) -- all FOUR `0.4f` lift constants (one per
                        glyph-quad corner) become a live read of
                        CurrentWorldLabelLift().

Rules 4/5 are TRANSPILERS, not postfixes, and the class's own comments are
explicit about why a postfix would be structurally wrong for either (a
postfix on UpdateAlpha would fight the method's own
`Mathf.Approximately(text.Color.a, num)` change-guard and force a full mesh
rebuild every frame; WrapAroundPlanetSurface has already written the vertex
buffer by the time a postfix could run). Each transpiler COUNTS its own
substitution hits and logs a named error if the count is wrong (1 for the
alpha constant, 4 for the lift constant) -- this suite checks for the
ABSENCE of that self-reported error as real coverage of the transpiler's
own correctness claim, per the class's own "being patched and being
REACHED are different claims" warning.

MOD SETTINGS -- all seven are `public static` fields on
`RSW_JawaRulesSettings`, the shape `jawa/mod_settings_field` resolves
(BRIDGE_STATIC_SETTINGS_FIELDS_1, already fixed and used by
`StructureInjections`/`Antiquities`) -- so, unlike Antiquities' partial
coverage, every one of the seven flips and reads back cleanly here with no
setter limitation. `toggle_flips` below exercises all seven.

WHAT IS AND ISN'T BEHAVIORALLY PROVEN, and why -- read before trusting a
green run at face value:

  RULE 1 (no-sow): `WorkGiver_GrowerSow.ExtraRequirements` is a method the
  vanilla WORK-GIVER SCANNER calls while deciding whether to OFFER a Sow
  job to an idle colonist during ordinary autonomous work assignment. It is
  NOT on the JobDriver's own path, so FORCING the job directly (this
  family's usual `jawa/ordered_job` primitive, or `jawa/order_pawn`, which
  is a GOTO/movement verb per `skills/rimbridge/references/traps.md` and
  never a job dispatcher) would bypass the WorkGiver entirely and prove
  nothing about this rule -- the exact same structural shape
  `StructureInjections/validation.py` already documented for its own
  `enabled` toggle. Proving the ban for real needs a designated Growing
  Zone (or hydroponics basin) plus autonomous, un-forced work assignment
  over real time, isolating which single pawn in the colony did or did not
  sow it. No suite in this family (grepped: none of the other 18) has ever
  designated a zone through the bridge, `apply_architect_designator`'s
  growing-zone `designatorId` and how a zone's plant selection is set are
  both unconfirmed against a live call, and CLAUDE.md's own rule is never
  to guess a defName/parameter shape. `xenotype_ban_guard_exists` below
  proves the GUARD CONDITION's target is real and reachable (a pawn's
  Xenotype really can read back as `RSW_MandrakeJawa`); it does NOT prove
  the WorkGiver actually refuses the job. That is a genuine, named
  coverage gap, not an oversight.

  RULE 2 (droid-relations): the postfix's OWN comment says the humanlike
  pawnkinds it actually fixes are OuterRim/KotOR droid races whose
  fleshType is `Asimov_Automaton` (isOrganic false) -- and this mod names
  no such pawnkind anywhere in its own files (no dependency, no
  MayRequire). Spawning a plain vanilla Humanlike colonist and confirming
  its relations tracker is non-null (`droid_relations_smoke` below) is,
  per the walk doc's OWN word for it, "weak on its own": a vanilla organic
  Humanlike gets a tracker via `RaceProps.IsFlesh` regardless of whether
  this patch runs at all, so this component can only prove the postfix
  does not CRASH ordinary pawn generation, not that it fixes anything. The
  real fix is provable only with a live droid pawnkind from another mod,
  named nowhere in JawaRules' own tree -- deferred, not guessed.

  RULE 3 (pet-names): proving a SPECIFIC animal race draws a namer-based
  name instead of the vanilla numeric fallback needs a race whose
  `RaceProperties` actually carries a `nameGenerator`/`nameGeneratorFemale`
  -- and this mod's own tree names no such race (again, no Defs/ at all).
  Guessing one (a Muffalo? a Labrador Retriever? a Thrumbo?) without
  reading that race's own RaceProperties first is exactly the kind of
  guess CLAUDE.md forbids ("never guess a defName, field, or namespace").
  Left an explicit gap rather than an invented pass.

  RULES 4/5 (labels): no bridge tool renders or measures a world-feature
  label's actual on-screen alpha or its lift off the terrain mesh -- the
  walk doc's own step 8 calls this "(human pass)". This suite covers the
  TRANSPILER'S OWN arithmetic self-check (hit count) instead, which is the
  full extent of what is provable without a screenshot a human judges.

Still not proven / likely first-live-run corrections:
  1. `jawa/set_pawn_xenotype`'s post-hoc gene swap (used here rather than
     `jawa/spawn_pawn(..., xenotype=...)`, per StarWarsRaces/validation.py's
     own note on why the two are NOT interchangeable for GENERATION-time
     effects) is sufficient for `IsJawa()`'s check, since that check only
     ever reads `pawn.genes.Xenotype.defName` post-hoc -- unlike a
     generation-time-only mechanism, this rule's guard has no dependency on
     which path set the xenotype.
  2. `jawa/pawn_relations` with no dedicated `action` for "is my relations
     tracker null" -- `droid_relations_smoke` below treats a normal
     (non-error) response to `action="list"` as evidence of a non-null
     tracker, and an exception/error response as evidence of a null one.
     Not independently confirmed against a live call for this specific
     null-vs-populated distinction.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("JawaRules")
suite.toggles = [
    "sowBanEnabled", "droidRelationsEnabled", "petNamesEnabled",
    "worldLabelAlphaBoostEnabled", "worldLabelAlpha",
    "worldLabelLiftEnabled", "worldLabelLift",
]

JAWA_XENOTYPE = "RSW_MandrakeJawa"
SETTINGS_TYPE = "RimMandrake.StarWars.JawaRules.RSW_JawaRulesSettings"

ARM_LINES = [
    ("no-sow", "[RimMandrake.StarWars.JawaRules] no-sow: armed for xenotype "
               "RSW_MandrakeJawa"),
    ("droid-relations",
     "[RimMandrake.StarWars.JawaRules] droid-relations: armed for humanlike "
     "pawns with no relations tracker"),
    ("pet-names",
     "[RimMandrake.StarWars.JawaRules] pet-names: armed; tamed and newborn "
     "animals will draw from their race namer"),
    ("world-labels",
     "[RimMandrake.StarWars.JawaRules] world-labels: armed; world feature "
     "names peak at 0.60 alpha instead of 0.30"),
    ("world-label-lift",
     "[RimMandrake.StarWars.JawaRules] world-label-lift: armed; world "
     "feature names sit 1.50 above the surface instead of 0.40"),
]


@suite.chain("rules_armed_at_load")
def rules_armed_at_load(t):
    """Each of the five rules logs its own named arm line (or, per
    `Apply()`/`ApplyTranspiler()`'s design, a named `TARGET METHOD NOT
    FOUND` error) -- never neither, and never a shared failure across
    rules. `jawa/drain_log`'s own `contains` filter does the substring
    match; a hit on the exact arm text is the strongest evidence available
    offline that the target methods still exist under their 1.6 names."""
    for rule, line in ARM_LINES:
        with t.component("armed_%s" % rule.replace("-", "_"), beyond_toggle=True):
            r = t.bridge_call("jawa/drain_log", limit=400, contains=line)
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            ok = any(line in m for m in msgs)
            t._record("drain_log contains %r -> %s" % (line, ok), ok)
            if not ok:
                raise ExpectationFailed(
                    "no Player.log line matched the exact arm text for %r "
                    "(%r) -- either the rule failed to arm (check for its "
                    "named 'TARGET METHOD NOT FOUND' error instead) or a "
                    "game update changed the target method" % (rule, line))


@suite.chain("transpilers_hit_expected_count")
def transpilers_hit_expected_count(t):
    """The two transpilers' own self-checks (JawaRules.cs's `hits != 1` /
    `hits != ExpectedHits` guards) -- absence of their named error IS the
    positive signal here, since a correct transpile logs nothing beyond
    the plain arm line already checked above."""
    with t.component("alpha_transpile_hit_count_correct", beyond_toggle=True):
        r = t.bridge_call(
            "jawa/drain_log", limit=400,
            contains="world-labels: expected exactly ONE 0.30 constant")
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        ok = not msgs
        t._record("no alpha-transpile hit-count error logged", ok)
        if not ok:
            raise ExpectationFailed(
                "found the alpha transpiler's own 'expected exactly ONE "
                "0.30 constant' error -- WorldFeatures.UpdateAlpha changed "
                "shape and the label alpha is NOT what was asked for: %r"
                % msgs)

    with t.component("lift_transpile_hit_count_correct", beyond_toggle=True):
        r = t.bridge_call(
            "jawa/drain_log", limit=400,
            contains="world-label-lift: expected exactly 4 0.40 constant")
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        ok = not msgs
        t._record("no lift-transpile hit-count error logged", ok)
        if not ok:
            raise ExpectationFailed(
                "found the lift transpiler's own 'expected exactly 4 0.40 "
                "constant' error -- WrapAroundPlanetSurface changed shape "
                "and the label lift is NOT applied on all four corners: %r"
                % msgs)


@suite.chain("xenotype_ban_guard_exists")
def xenotype_ban_guard_exists(t):
    """Proves the no-sow rule's own guard condition
    (`JawaRulesMod.IsJawa`, which reads `pawn.genes.Xenotype.defName ==
    "RSW_MandrakeJawa"`) has a real, reachable target -- NOT that the
    WorkGiver actually refuses the job (see module docstring's RULE 1
    section for why that half is a documented gap, not attempted here)."""
    t.clear_area(size=20)
    jawa = t.spawn_pawn("Colonist", hostile=False)
    other = t.spawn_pawn("Colonist", hostile=False)

    with t.component("xenotype_swap_readback", beyond_toggle=True):
        r = t.bridge_call("jawa/set_pawn_xenotype", pawnId=jawa,
                          xenotype=JAWA_XENOTYPE, clearEndogenes=True)
        rows = (r or {}).get("pawns") or []
        got = rows[0].get("now") if rows else None
        ok = got == JAWA_XENOTYPE
        t._record("set_pawn_xenotype(%s) -> now=%r" % (jawa, got), ok)
        if not ok:
            raise ExpectationFailed(
                "jawa/set_pawn_xenotype did not read back %r for the "
                "would-be Jawa pawn: %r" % (JAWA_XENOTYPE, r))

        genes = t.bridge_call("jawa/pawn_genes", pawn=other, action="list")
        other_xeno = (genes or {}).get("xenotype")
        ok2 = other_xeno != JAWA_XENOTYPE
        t._record("control pawn's xenotype -> %r (must not be %r)"
                  % (other_xeno, JAWA_XENOTYPE), ok2)
        if not ok2:
            raise ExpectationFailed(
                "the control pawn unexpectedly already carries %r -- "
                "it would not be a valid non-Jawa control" % JAWA_XENOTYPE)
        t.screenshot()


@suite.chain("droid_relations_smoke")
def droid_relations_smoke(t):
    """WEAK by construction -- see module docstring's RULE 2 section. This
    only proves the postfix does not crash generation for an ordinary
    Humanlike colonist, which would happen with or without the patch."""
    t.clear_area(size=10)
    colonist = t.spawn_pawn("Colonist", hostile=False)
    with t.component("humanlike_pawn_has_relations_tracker",
                     toggle="droidRelationsEnabled"):
        try:
            r = t.bridge_call("jawa/pawn_relations", pawn=colonist, action="list")
            ok = r is not None and "error" not in (r or {})
        except Exception:
            ok, r = False, None
        t._record("pawn_relations(list) on a plain Humanlike colonist -> %r"
                  % r, ok)
        if not ok:
            raise ExpectationFailed(
                "jawa/pawn_relations(list) failed/errored for a plain "
                "Humanlike colonist, which should always have a tracker "
                "regardless of this patch: %r" % r)


@suite.chain("toggle_flips")
def toggle_flips(t):
    """All seven `RSW_JawaRulesSettings` fields are `public static` and
    resolve through `jawa/mod_settings_field`'s static-first path
    (BRIDGE_STATIC_SETTINGS_FIELDS_1) -- unlike Antiquities' partial
    coverage, nothing here blocks a full flip+read-back of every declared
    setting."""
    with t.component("boolean_settings_flip", toggle=None, beyond_toggle=True):
        for field in ("sowBanEnabled", "droidRelationsEnabled", "petNamesEnabled",
                      "worldLabelAlphaBoostEnabled", "worldLabelLiftEnabled"):
            t.set_setting(SETTINGS_TYPE, {field: False})
            t.set_setting(SETTINGS_TYPE, {field: True})

    with t.component("numeric_settings_flip", toggle=None, beyond_toggle=True):
        t.set_setting(SETTINGS_TYPE, {"worldLabelAlpha": 0.45})
        t.set_setting(SETTINGS_TYPE, {"worldLabelAlpha": 0.6})
        t.set_setting(SETTINGS_TYPE, {"worldLabelLift": 2.0})
        t.set_setting(SETTINGS_TYPE, {"worldLabelLift": 1.5})
