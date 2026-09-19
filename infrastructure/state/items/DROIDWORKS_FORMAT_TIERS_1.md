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

- [x] a **programmable** droid shows Mood and **no** Joy in the needs tab
      — **CONFIRMED 2026-09-14**, see live re-test section below
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

## 🔴 live quicktest run 2026-09-08 (FOUNDRY) — need-gating does NOT work live, box 1/2 FAIL

Deployed (`deploy_custom_mods.py --mod Droidworks --apply`, 53 files) and quicktested
on the minimal list. Spawned `RSW_DW_KotORDroidColonist_ADMkI`
(`RSW_DW_Race_guy762_DroidRace_ADMkI53446`), then swept `RSW_DW_FormatTier` through
all four stages via `jawa/pawn_health` remove+add (severity 0.5/1.5/2.5/3.9 —
blank/mindless/programmable/sapient):

```
severity 0.5 (blank):        needs=['Mood', 'RSW_DW_Power']
severity 1.5 (mindless):     needs=['Mood', 'RSW_DW_Power']
severity 2.5 (programmable): needs=['Mood', 'RSW_DW_Power']
severity 3.9 (sapient):      needs=['Mood', 'RSW_DW_Power']
```

**Identical needs list at every tier.** Blank/mindless should show `Power` ONLY (no
Mood); this pawn keeps Mood at every tier including blank. Joy/Beauty/Comfort/Outdoors
are absent at ALL tiers including sapient — so either they were never on this race's
need list to begin with (plausible for a non-organic race, in which case "sapient
gets everything" may need those needs ADDED at the sapient stage, not just
un-disabled) or the disabling is masking something upstream. **Boxes 1 and 2 above:
FAIL, not pending.** Box 5 (hediff lands on spawn) partially confirms — default tier
WAS present (severity 3.0 pre-test) — but the gating itself does not respond to a
stage change, live, despite the item's own reasoning about `ShouldHaveNeed`/
`DisablesNeed` reading `disablesNeeds` per-stage.

**Not root-caused this pass** — candidate causes, untested: (a) my remove+add via
`jawa/pawn_health` may not trigger the same code path a real `SetTier`/recipe call
would (the item's own bug-fix note says `SetTier` explicitly calls
`AddOrRemoveNeedsAsAppropriate()` — a raw hediff add via the bridge tool goes through
`Pawn_HealthTracker.AddHediff` directly, which *should* trigger the same vanilla
recalculation, but evidently doesn't observably change the needs list here); (b) the
4 stages' `disablesNeeds` XML may not be doing what the file above claims — worth
literally reading the shipped `HediffDefs_Droidworks.xml` stage-by-stage rather than
trusting the description; (c) `Mood` may be added by something OTHER than
`Pawn_NeedsTracker.ShouldHaveNeed`'s per-hediff check (e.g. `RaceProps.Humanlike`
forces it elsewhere and `disablesNeeds` cannot override that path for a Humanlike-
intelligence race — recall Droidworks races deliberately keep `intelligence
Humanlike`, which may be exactly why Mood cannot be suppressed this way).

**Item reopened, not closed, not silently trusted.** Whoever picks this back up:
start by reading the actual stage-by-stage `<disablesNeeds>` XML in
`HediffDefs_Droidworks.xml` against what vanilla's `HediffSet.DisablesNeed` actually
checks (`hediff.CurStageIndex` vs the LIST of disabled needs on THAT stage,
specifically) before assuming the mechanism vs the wiring is at fault.

## root-cause read 2026-09-09 (FOUNDRY, offline — bridge held by another item, cold-load in progress)

Picked this back up per its own instruction: read the stage-by-stage XML against
what vanilla's need-caching actually does, before assuming mechanism vs wiring is
at fault. Mechanism, not wiring, is CLEARED — the 2026-09-08 FAIL is a test-tool
artifact, not a shipped-code bug. Read live (via RimSage), not assumed:

- `HediffSet.CacheNeeds()` reads `hediff.CurStage.disablesNeeds` correctly, and
  `Hediff.Severity`'s setter DOES call `Pawn_HealthTracker.Notify_HediffChanged` →
  `HediffSet.DirtyCache()` on every stage-index change — so `cachedDisabledNeeds`
  itself was never stale.
- But `Pawn_NeedsTracker.ShouldHaveNeed` is only *consulted* when something calls
  `pawn.needs.AddOrRemoveNeedsAsAppropriate()` to rebuild the actual `Need` object
  list. `HediffSet.AddDirect` calls it once, at add-time. Bare `Hediff.Severity`'s
  setter — confirmed by reading it end to end — does **not** call it again.
- `DroidFormatTier.SetTier` (`Source/Droidworks/DroidFormatTier.cs:95-111`) already
  knows this and calls `pawn.needs?.AddOrRemoveNeedsAsAppropriate()` explicitly
  after setting severity — its own comment (lines 85-94) names this exact vanilla
  gap. `Recipe_DWFormat.cs:48` calls `DroidFormatTierUtility.SetTier`, not a raw
  severity write. Both are correct as shipped.
- The 2026-09-08 quicktest drove the hediff through `jawa/pawn_health` instead:
  `AddHediff(hd, part)` (creates it at `initialSeverity` = 3 = programmable, which
  fires `AddOrRemoveNeedsAsAppropriate` ONCE at that stage — Joy/Beauty/Comfort/
  Outdoors disabled, Mood not), then a bare `h.Severity = severity` line
  (`JawaBenchPawnTools.cs:862-863`) for each of the four probed stages. That later
  line updates `cachedDisabledNeeds` but never calls `AddOrRemoveNeedsAsAppropriate`
  again — so the actual `Need` list stayed frozen at the programmable-stage snapshot
  for all four "different" severities tested. That reproduces the logged result
  exactly: Mood present and Joy/Beauty/Comfort/Outdoors absent at every stage
  including blank and sapient, because all four readings were the same stale
  snapshot, not four live measurements. (Checked `Joy`'s NeedDef too:
  `colonistsOnly true`, `minIntelligence Humanlike` — no other gate involved; a
  player-faction Humanlike-intelligence pawn passes both.)
- This resolves candidates (a) and (b) from the prior entry: (a) confirmed —
  the bridge probe doesn't exercise the fixed code path; (b) ruled out — the
  shipped XML/stage wiring is correct as read. (c) is subsumed: Joy/Beauty/
  Comfort/Outdoors were never actually re-evaluated at blank/mindless/sapient in
  that test, so their absence there proves nothing about whether they're on this
  race's need list at all.

**Offline verify re-run clean**, confirming nothing regressed since 2026-09-08:
`dotnet build Droidworks.csproj -c Release` → 0 warnings/0 errors;
`validate_patch.py` on the same 4 def files against the live 586-mod load set →
0 errors/0 warnings (the one `info` on `Races_Base.xml` is
`CompProperties_DWServiceRecord`, packet E2's class, not this item's).

**Still NOT live-retested — leaving `doing`, not closing.** The seven-box live
checklist above is still owed exactly as stated; this pass only clears WHY the
last attempt failed. Whoever has the bridge next: retest by driving
`DroidFormatTier.SetTier` — either through the three real recipes (bill on a
droid at a crafting spot) or, faster, a bridge call that invokes `SetTier`
directly — and do **not** reuse the raw `jawa/pawn_health` remove+add+severity-poke
pattern to probe stage-gated needs on any hediff again; it cannot see
`AddOrRemoveNeedsAsAppropriate`-gated effects on this or any other tier-style
hediff in this repo. (`jawa/pawn_health`'s own tool description is otherwise
accurate for its stated purpose — installing/removing hediffs — this is a gap in
what it can prove about needs specifically, not a bug in it.)

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

## live re-test 2026-09-14 (FOUNDRY) — box 1 CONFIRMED PASS for real; boxes 2/3/6/7 need a different tool, root cause is now structural not circumstantial

Bridge taken, game was already UP on a live map with 57 pre-existing pawns
(another window's creature-review rig — confirmed via `jawa/list_pawns`
before touching anything, zero player colonists, time left PAUSED the whole
pass). Spawned `RSW_DW_KotORDroidColonist_ADMkI` via debug action at an empty
cell, read it, destroyed it with `Actions\T: Destroy` targeted at its exact
cell, and re-ran `jawa/list_pawns` to confirm the map was back to its
original 57 — twice (once per droid spawned this pass), never trusting
`success: true` alone. Never unpaused; nothing else on the map was touched.

**Box 1 — CONFIRMED PASS, this time with an actually-correct tool.**
`jawa/pawn_need` (action=`list`) — NOT `jawa/pawn_health`, which has no
`list` action at all (its declared actions are `add`/`remove`/`bionic`/
`restore` only; the 2026-09-08 test's read step must have gone through a
different, unrecorded route) — on a freshly-spawned droid at its genuine
spawn-time default tier (Programmable, via `CompDWFormatTier`'s real
`SetTier` call, no bridge poke involved) returned exactly `['Mood',
'RSW_DW_Power']`. Joy/Beauty/Comfort/Outdoors absent, Mood present — precisely
what ruling 4 asks for at Programmable. This also stands as confirmation of
box 5 (the comp does put the hediff on a spawned droid): if it hadn't,
`ShouldHaveNeed` would have left the full Humanlike need set instead of this
narrower one.

**Boxes 2/3/6/7 — still NOT live-tested, and now for a structural reason, not
just "wasn't attempted."** Read `jawa/pawn_health`'s C# in full
(`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnTools.cs`,
the `PawnHealth` method) before touching it again: its `action=add` path
calls `p.health.AddHediff(hd, part)` — which creates the hediff at
`hd.initialSeverity` (3.0 = Programmable for `RSW_DW_FormatTier`) and is
exactly where vanilla's `AddOrRemoveNeedsAsAppropriate` needs-rebuild fires
— and **only afterward**, if `severity >= 0f` was passed, does `h.Severity =
severity` as a bare post-add poke. That poke changes the hediff's stage but,
per this item's own 2026-09-09 root-cause read, a bare `Hediff.Severity`
setter never re-triggers the needs rebuild. **This means `jawa/pawn_health`
cannot EVER correctly test a non-default format tier, for any severity value
passed to it, on this or any hediff whose gate depends on
`AddOrRemoveNeedsAsAppropriate` reading the CURRENT stage** — not a mistake
in how the 2026-09-08 test drove it, a hard ceiling in the tool's own code.
Confirmed by reading the method start-to-finish, not inferred.

**What actually needs to happen, for whoever has bridge time next:**
1. Fastest, most correct: a new companion tool (`jawa/droid_format_tier` or
   similar, per the `rimbridge-companion` skill's own pattern) that calls
   `DroidFormatTierUtility.SetTier(pawn, tier)` directly — the exact
   already-shipped, already-correct method, no workaround needed. One-minute
   edit→build→deploy→test cycle on the minimal list per that skill; **not
   attempted this pass** because it needs a restart and this pass found the
   game already up and in active use by another window's creature-review
   work — restarting it to save a few minutes of companion-tool build time
   was judged the wrong trade this session, not because the fix is hard.
2. Slower but mechanically faithful: drive the real `Recipe_DWFormat` bill
   with an actual player colonist at a real bench — needs a colonist and an
   unpause, neither available on this pass's shared map without disturbing
   the other window's pawn census further.

Boxes 2 (mindless=Power only), 3 (sapient mental breaks fire), 6 (recipe
eligibility gating per tier), 7 (deformat goodwill+witness-thought) all still
require one of the two routes above. **Item stays in `doing`, not closed** —
one of seven boxes moved from "not attempted" to "confirmed," and the
remaining six now have a precise, actionable path instead of an open
question.

## 2026-09-18 (FOUNDRY, belt mode, subagent) — root-cause pass on the 2026-09-08 need-gating failure

Task brief for this pass framed the root cause as still open ("not root-caused
yet, two untested candidates"), but that framing was **stale** — this item's
own 2026-09-09 and 2026-09-14 entries above already root-caused and confirmed
it. This pass's job became: independently re-verify that analysis against live
source rather than trust it secondhand, and act on the one piece the prior
entries left as a recommendation rather than code. Bridge was checked first
(`rimflow bridge who` → FREE) and the game was found RUNNING live (`./game` →
RUNNING); per this pass's own brief, that means no restart, no deploy, no live
retest — noted as owed below, not forced.

**Root cause re-confirmed independently, both halves, with exact source now
read (not just cited):**

- **(b) XML — ruled out, confirmed correct as claimed.** Read
  `src/RimStarWars/Droidworks/Defs/HediffDefs/HediffDefs_Droidworks.xml` lines
  224-329 directly. All four `RSW_DW_FormatTier` stages are exactly as the item
  describes: blank/mindless `disablesNeeds` = Mood+Joy+Beauty+Comfort+Outdoors;
  programmable `disablesNeeds` = Joy+Beauty+Comfort+Outdoors (Mood absent from
  the list, i.e. kept); sapient has no `disablesNeeds` block at all. Work tags
  per tier also match the item's table exactly. The XML was never the bug.
- **(a) the bridge tool's code path — ruled out as a misuse, confirmed as a
  structural gap, down to the exact vanilla lines.** Read live via RimSage
  (this session DOES have RimSage access, unlike the Mac-laptop case CLAUDE.md
  warns about):
  - `Hediff.Severity`'s setter (`Source/Verse/Hediff.cs:239-266`) calls
    `pawn.health.Notify_HediffChanged(this)` on a stage-index change, but never
    `Pawn_NeedsTracker.AddOrRemoveNeedsAsAppropriate()`.
  - That rebuild is called from exactly two places in vanilla:
    `HediffSet.AddDirect` (`Source/Verse/HediffSet.cs` ~line 368-372, checking
    the stage active **at add time**) and `Hediff.PostRemoved`
    (`Source/Verse/Hediff.cs:606-624`, checking the stage active **at removal
    time**). Both gate on that one moment's `CurStage.disablesNeeds`/
    `enablesNeeds`; neither fires again for a severity change in between.
  - `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnTools.cs`
    (`PawnHealth`, `action=='add'` branch, confirmed at line 930):
    `if (severity >= 0f) h.Severity = severity;` runs strictly *after*
    `AddHediff` already fired the rebuild once at `initialSeverity`. This one
    line is the entire defect surface — it is a bare post-add severity poke
    that can never re-trigger `AddOrRemoveNeedsAsAppropriate()`, confirming the
    2026-09-09 entry's read to the exact line.
  - `DroidFormatTierUtility.SetTier` (`Source/Droidworks/DroidFormatTier.cs:95-111`,
    read again this pass) calls `pawn.needs?.AddOrRemoveNeedsAsAppropriate()`
    explicitly right after setting severity — already correct, already shipped,
    unchanged by this pass.

**New, previously-unstated fact this pass found: the 2026-09-14 entry's
"fastest, most correct" fix (a companion tool calling `SetTier` directly) was
not actually buildable as described.** `JawaBench.BridgeTools.csproj` had no
reference to the Droidworks mod assembly at all — bridgetools only referenced
`RimBridgeServer.Sdk`, `RimMandrakeOracle`, `RimDefDump`, `Assembly-CSharp`,
`UnityEngine.CoreModule` and `0Harmony`. Calling `DroidFormatTierUtility.SetTier`
needed a new `Reference` entry, the same "call straight into the already-loaded
mod" pattern `JawaBenchOracleTools.cs` already uses for `RimMandrakeOracle.dll`
(Droidworks is an ordinary mod, already loaded by the mod loader before
RimBridgeServer attaches its companions).

**Fix applied — written, wired, and build-verified offline; NOT deployed:**

- Added `DroidworksModDir` property + `Reference Include="Droidworks"` +
  matching `Error Condition` check to
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBench.BridgeTools.csproj`,
  pointing at the live deployed
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Droidworks\Assemblies\Droidworks.dll`
  (confirmed present on disk this pass).
- New file
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchDroidworksTools.cs`:
  `jawa/droid_format_tier` (`action='get'|'set'`, `tier='blank'|'mindless'|
  'programmable'|'sapient'`), calling `DroidFormatTierUtility.SetTier`/`TierOf`
  directly and reading back `pawn.needs.AllNeeds` (the live Need list, not the
  cached disabled-needs set) after the rebuild. Refuses on a non-droid pawn.
  Rule-9-checked against the phantom-tool trap: `jawa/pawn_health` is mentioned
  inside this tool's own `Description` string, but `build.py`'s tool-surface
  scan was hardened past the loose-substring-match bug that trap describes
  (`BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1`, 2026-09-06 — it now reads the actual
  `CustomAttribute` metadata table, not a string-blob regex), confirmed by
  reading `tool_surface()`'s current docstring in `build.py` this pass — so no
  phantom risk.
- **Offline build-verified, not deployed:** `dotnet build` (via the user-local
  `C:\Users\Mandrake\.dotnet\dotnet.exe`, invoked through the WSL/Windows
  interop path since this is a WSL shell) on
  `JawaBench.BridgeTools.csproj` in Release → **0 warnings, 0 errors**, output
  written only to the repo's own `bridgetools/artifacts/BridgeTools/JawaBench/`
  (gitignored), never touching the game's Mods folder or the live process.

**🔴 Deploy + live retest deliberately NOT done this pass.** `rimflow game` and
`./game` both read the game as RUNNING for the whole pass, with an unrelated
water-terrain regression under active investigation by another window per this
pass's own brief. Deploying this companion DLL needs `taskkill.exe /F /IM
RimWorldWin64.exe` first (the DLL is memory-mapped) — an involuntary restart of
someone else's live session, which this pass's brief explicitly said not to
force. **Owed to the next game-down window:**

1. `taskkill.exe` + `build.py --gm --apply` (or without `--gm`, since this tool
   carries no GM gate) + relaunch.
2. Prove `jawa/droid_format_tier` live: spawn a droid, `action='set'
   tier='mindless'`, read back `needs` → expect `['RSW_DW_Power']` only
   (box 2); `tier='sapient'` → expect the full Humanlike need set including
   Joy/Beauty/Comfort/Outdoors if this race has them, or confirm via a second
   instrument if it does not carry them at baseline (the 2026-09-08 entry's
   open question about whether Joy/Beauty/Comfort/Outdoors are on this race's
   need list at all, independent of gating, is still unresolved and this tool
   now makes it directly checkable for the first time).
3. Boxes 3 (sapient mental breaks fire), 6 (recipe eligibility gating per
   tier) and 7 (deformat goodwill+witness-thought) still need the recipe/bench
   route or debug actions — `jawa/droid_format_tier` only covers boxes 2 and
   re-confirms 1/5; it does not touch bills, eligibility gates, or
   `RecipeWorker.ReportViolation`.

**Item stays in `doing`.** Root cause: CONFIRMED (independently, this pass, to
exact source lines on both the XML and C# sides). Fix: WRITTEN and
BUILD-VERIFIED offline, not yet deployed or live-tested — that step is owed to
whoever next has a game-down window, not forced onto a live, shared session.

## re-verify pass 2026-09-18 (FOUNDRY, belt mode, subagent) — confirmed already done, no duplicate work

Picked up with a brief asking to build `jawa/droid_format_tier` calling
`DroidFormatTierUtility.SetTier` and forcing the needs rebuild. That work was
**already written and committed** by the immediately-prior pass (section
above) at `b60c7e4ff`: `JawaBenchDroidworksTools.cs` exists, the `.csproj`
carries the `DroidworksModDir`/`Reference Include="Droidworks"`/`Error
Condition` wiring, all committed, no local diff. Did not re-do it.

Re-confirmed offline this pass: `python.exe src/RimMandrake/bridgetools/build.py`
(plan-only, no `--apply`) → **0 Warnings, 0 Errors**, unchanged from the prior
report. Checked live state fresh: `./game` → RimWorldWin64 RUNNING, bridge
answers; `rimflow bridge who` → FREE. Per this pass's own brief (game up means
build-only, no deploy, no forced restart), **did not deploy and did not touch
the live game/bridge**.

Deploy + live-proof of boxes 2/3/6/7 via `jawa/droid_format_tier` is still
owed at the next game-down window, exactly as stated above — nothing new
found, nothing regressed. Item left in `doing`.
