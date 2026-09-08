## spec

Packet **B1** of `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5.
Inputs it names: **unit 10** (`design/Jawa/droid_system_build_spec.md` §3 row 10 —
"Format tiers mindless/programmable/sapient/blank: one `Hediff_FormatTier`, stages
gate capacities; workTags via Harmony postfix on `WorkTagIsDisabled`; needs switch")
and **ruling 4** (`DROID_UNIFIED_FRAMEWORK_DESIGN.md` §0.4, verbatim: *"Inner life by
tier: SAPIENT gets everything; PROGRAMMABLE gets Mood but not Joy/Beauty/Comfort;
MINDLESS and BLANK have no needs."*). Behind both sits the FROZEN owner sheet
`design/Jawa/droid_verbs_decisions.json` rows `abf_formatting` and
`abf_format_murder`, restated as `design/Jawa/droid_system_spec.md` §5 and §8.

### what was built

**1. `RSW_DW_FormatTier` — a 4-stage HediffDef, permanent, coexisting.**
`src/RimStarWars/Droidworks/Defs/HediffDefs/HediffDefs_Droidworks.xml`.
Severity **is** the ladder — 1 blank / 2 mindless / 3 programmable / 4 sapient —
with stage cuts at the half-points (0 / 1.5 / 2.5 / 3.5) so float wobble cannot
change a tier. `isBad false`, `everCurableByItem false`, `minSeverity 1`,
`initialSeverity 3`.

It **coexists with, and replaces nothing**. `RSW_DW_PoweredDown` answers "is this
droid running right now" and is cleared by a reboot; the format tier answers "what
is this droid capable of at all" and is changed only by a bench operation. Neither
reads the other. The frozen sheet's own framing settles it: mindless is *"NOT the
default droid setting, this should be a reduced state due to damage, hacking, or a
deeply restrictive restraining bolt"* — a classification, not a state.

**Default tier = PROGRAMMABLE**, put on every droid at spawn by
`CompDWFormatTier` (`Source/Droidworks/CompDWFormatTier.cs`), wired onto
`DW_Race_Base` in `Defs/Races_Base.xml` so all 57 concrete races inherit it.
Idempotent, so a droid formatted to sapient two years ago is not reset on load.
Mindless is explicitly not a default (owner, above); sapience is what a long-unwiped
droid *drifts into* (packet E2), so the middle rung is where every droid starts.

**2. Need gating — VANILLA XML, NOT HARMONY.** Packet B1 and unit 10 both describe a
C# route (`ShouldHaveNeed` extension / `WorkTagIsDisabled` postfix). Two vanilla
`HediffStage` fields already do it natively, so the Charter's "a named defName/xpath
is an example, not a mandate" was taken:

- `<disablesNeeds>` is read by `Pawn_NeedsTracker.ShouldHaveNeed` itself, through
  `HediffSet.DisablesNeed` — the exact method the postfix would have wrapped.
  Vanilla precedent: Anomaly's `VoidTouched`, `Hediffs_Global_Misc.xml`.
- `<disabledWorkTags>` folds into `Pawn.CombinedDisabledWorkTags`, which is all
  `Pawn.WorkTagIsDisabled` returns — a postfix there re-implements the field one line
  downstream. Vanilla precedent: Anomaly's `CrumbledMind` and `BlissLobotomy`.

XML also puts the restrictions in the pawn's "incapable of" line and the hediff
tooltip for free. **No new Harmony patch was added by this item.**

Per ruling 4: blank + mindless disable Mood/Joy/Beauty/Comfort/Outdoors;
programmable disables Joy/Beauty/Comfort/Outdoors (keeps Mood); sapient disables
none. `RSW_DW_Power` is never disabled at any tier — that is what makes "mindless
has Power only" true.

**3. Work gating by tier**, from sheet row `abf_formatting`:

| tier | disabled work tags | also |
|---|---|---|
| blank | all 19 concrete `WorkTags` | `blocksMentalBreaks`, `blocksInspirations` |
| mindless | ManualSkilled, Violent, Caring, Social, Intellectual, Animals, Artistic, Crafting, Cooking, PlantWork, Hunting, Constructing, Shooting — leaving ManualDumb, Hauling, Cleaning, Firefighting, Mining, Commoner | `blocksMentalBreaks`, `blocksInspirations` |
| programmable | Artistic, Social | `blocksInspirations` |
| sapient | none | — |

**4. Three format recipes** (`Source/Droidworks/Recipe_DWFormat.cs`,
`Defs/RecipeDefs/RecipeDefs_Droidworks.xml`), all whole-pawn, all on
`DW_Race_Base`'s `<recipes>`:
`RSW_DW_FormatDroid` (blank/mindless → programmable, not a violation),
`RSW_DW_RestrictiveFormat` (anything above → mindless, violation),
`RSW_DW_DeformatDroid` (anything → blank, violation).
**There is deliberately no recipe that formats a droid UP to sapient** — the
head-gate ruling (ruling 6) exists so no bench manufactures a mind.

**5. Deformat-sapient consequences** (`Defs/Misc/Ethics_Droidworks.xml`).
`HistoryEventDef RSW_DW_DeformattedSapientDroid` recorded, plus
`ReportViolation` against the droid's home faction scaled by
`DroidEthicsExtension.DeformatStance` (Embraces 0 / Regrettable −25 / Murder −100;
calibrated against vanilla's own −70 for a harvested organ), plus a
`ThoughtDef RSW_DW_KnowSapientDroidDeformatted` (−8, 10 days, stacks 5).

## judgement calls — things the design docs do NOT settle

1. **`Intellectual` left ENABLED at programmable.** The sheet places "exceptional
   skill functions, savants" on the sapient side but never names research; an
   astromech slicing a computer is the canonical case. Savant-ness is expressed as
   `blocksInspirations` instead, which is the mechanism vanilla actually uses for it.
2. **The restrictive format from sapient fires the same murder consequences as a
   deformat.** The design text names only deformatting, but §5's own reason
   (*"which is exactly why deformatting a sapient is killing someone"*) does not
   distinguish: both destroy the mind. Implemented as one rule — *was sapient, is now
   below programmable*.
3. **Crafting skill numbers** (format 6 / restrictive 5 / deformat 4). No doc sets
   them. The ordering is the argument: destroying programming is easier than writing
   it. Research gating is packet B8's to add; these ship ungated.
4. **`Commoner` and `Mining` left enabled at mindless** as "low-level activities".

## verify

**Offline, done:**
- `dotnet build -c Release` — **0 warnings, 0 errors**; DLL written to the REPO's
  `src/RimStarWars/Droidworks/Assemblies/`, not to the game's Mods folder. Nothing
  was deployed and the running game was not touched.
- `validate_patch.py` on the 4 changed/new def files against the real load set
  (`--defs` Data + workshop + Mods, 25 active mods): **0 errors, 0 warnings**. The one
  `info` is the expected "no def in the load set uses
  `RimMandrake.StarWars.Droidworks.CompProperties_DWFormatTier`" — our own class,
  public, namespace confirmed against the built assembly.
- Every vanilla mechanism used was read in the 1.6 source before use, not assumed:
  `Pawn_NeedsTracker.ShouldHaveNeed`, `HediffSet.DisablesNeed`/`DirtyCache`,
  `HediffStage` (confirming `disablesNeeds`, `disabledWorkTags`, `blocksMentalBreaks`,
  `blocksInspirations` all exist in 1.6), `Pawn.CombinedDisabledWorkTags`,
  `Hediff.Severity`, `RecipeWorker.ReportViolation`/`IsViolationOnPawn`,
  `ThoughtUtility.GiveThoughtsForPawnOrganHarvested`, `MentalBreaker.CurMood`
  (confirmed null-mood-safe, so disabling Mood on a Humanlike is survivable),
  `HistoryEventDef`, `ThoughtDef`, `HediffDef.ConfigErrors`.
- **One real bug found by reading rather than by testing**, and fixed:
  `HediffSet.DirtyCache()` refreshes `cachedDisabledNeeds` but never calls
  `pawn.needs.AddOrRemoveNeedsAsAppropriate()`. Vanilla rebuilds the need list only on
  hediff ADD/REMOVE, not on a severity (stage) change — so a droid formatted from
  sapient down to mindless would have kept a live Joy need. `SetTier` calls it
  explicitly.

**🔴 NOT verified — no live quicktest was run.** This item was built with the bridge
and the running game deliberately untouched (another window may hold the live
session). Packet B1's own verify line is still entirely owed:

- [ ] a **programmable** droid shows Mood and **no** Joy in the needs tab
- [ ] a **mindless** droid shows **Power only**
- [ ] a **sapient** droid breaks (i.e. mental breaks actually fire at tier 4)
- [ ] a **blank** droid is genuinely inert and is not stuck in a job-loop error
- [ ] `CompDWFormatTier` actually puts the hediff on a spawned droid (spawn a
      `RSW_DW_OuterRim_GNKDroid`, read `jawa/pawn_health`)
- [ ] the three recipes appear in the operations tab, and each one's eligibility
      gate hides it on the wrong tier
- [ ] a deformat of a sapient droid fires the goodwill hit and, with Ideology
      **off**, the witness thought

Nothing above was observed running. The DLL is **not deployed**;
`deploy_custom_mods.py --apply` is owed before any of it can be tested.

## criteria

Closes when the seven boxes above are ticked on a minimal-list quicktest
(`ModsConfig.MINIMAL.xml`, per `DROIDWORKS_LIVE_LOOP_PROOF_1`'s method) after a
deploy, with the results written back here.

## owed elsewhere — NOT this item's files

- **No ideoligion in this repo reacts to `RSW_DW_DeformattedSapientDroid`.** In 1.6
  vanilla has no non-ideoligious witness-thought route left — `ThoughtUtility`'s own
  organ-harvest and execution paths only record a `HistoryEvent`, and the memory is
  granted by a `PreceptComp_KnowsMemoryThought` on whichever ideoligion cares. So
  **with Ideology active (i.e. the campaign), a deformat currently moves faction
  goodwill but produces no colonist thought.** `Recipe_DWFormatBase` grants the memory
  directly ONLY when Ideology is inactive, so the two routes can never double-count.
  The precept wiring is campaign/ideoligion work (RimUtinni), not platform.
- **Nothing attaches `DroidEthicsExtension` to any FactionDef**, so every faction
  currently reads as `Regrettable`. Per `droid_system_spec.md` §8 the intended values
  are: Junkers / Ascendant Helix / Empire → `Embraces`; Free Droid Enclaves /
  Homestead moisture farmers → `Murder`; everyone else default. That belongs with
  `DROID_FACTION_LOADOUTS_1` (packet C1).
- Packet B8 (`DROIDWORKS_RESEARCH_ROWS_1`) owes `RSW_DW_Research_Formatting` as a
  `researchPrerequisite` on the three recipes.
