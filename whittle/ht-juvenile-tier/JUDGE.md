# Independent Codex judgment

2026-11-11 — RIMMANDRAKE_REVIEW_HUGETHINGS_JUVENILE_PASSAGE_CLASSIFICATION

Accepted for the frozen L0/L1 scope. I did not build this work. I independently inspected allowed source, raw receipts and installed metadata, executed the preserved offline test assembly without building, and recalculated the live results. Builder PASS/ok fields were not treated as proof.

## Frozen bullets

1. **TRUE:** “Resolve juvenile-only race classification and T3 passage spacing through an independent delegated design decision, preserving the owner's calf allowance, biome pools, land/sea matching and explicit force overrides.”

   evidence/design_prompt.txt presents competing semantics and owner constraints without a builder verdict. evidence/design_raw.json, session a0ff342d-d9bf-4cf5-b1de-e7003ea4a231, records the tools-disabled, single-turn independent consultation: retain lineage AdultTier and conservative DefQualifies; refine only spacing to the maximum trustworthy supported stage. This is delegated design, not owner approval. evidence/raw/before/owner-calf-ruling.json preserves “Calves are ok” and tsn1792618983088247673; its accompanying implementation gloss is not itself an owner quote.

   I agree with this separation. Replacing eligibility with supported tier would remove the calf at custom4/18/30, where supported size16 is only T1. The consultation's claim that below-one factors cannot yield T3 must be read relative to thresholds and absent runtime modifiers: custom T3=16 is an explicit counterexample to an unconditional reading, correctly handled by the decision's matrix and implementation.

2. **TRUE:** “Make the source and current specifications agree with that decision, retaining the separate conservative comp-attachment policy and focused adult, juvenile-only, growth-above-one, missing-stage, force and threshold controls.”

   Current src/RimMandrake/HugeThings/TIERING.md, infrastructure/state/items/TITAN_CAMPS_SCAVENGERS_EVENTS_1.md:20, and design/RimMandrake/hugethings_codex_2026-11-09/REVIEW.md:78 agree with the implementation. REEFBACK_CALF_DECISION.md:20 distinguishes its earlier measurement from today's refinement. The closed titan package's original hard population-cap aspiration does not prove a fully implemented population cap.

   TitanicTierUtility.cs:96 retains AdultTier's factor floor1; :111 adds SpacingTier; :125 retains runtime GetTier. RM_TitanicKernel.cs:66 rejects incomplete/malformed folds; :235 preserves all other boolean gates and applies the existing-T3 veto to spacingTier. TitanPassage.cs:55 still rejects invalid/nonanimal/dryad/harness-only candidates and AdultTier below T2. Against evidence/raw/before/TitanPassage.cs, its sole executable change is passing SpacingTier to the kernel. Biome opt-out, list precedence over roster, sea/land matching, season, pending check, route checks, warning and arrival recheck remain. T3OnMap still reads living spawned pawns through actual GetTier.

   DefQualifies stays separate at TitanicTierUtility.cs:78 and RM_TitanicKernel.cs:48–61; startup attachment still calls it in RM_TitanicCreaturesMod.cs:54. A base6/factor.5 control has runtime size3/None, lineage T1, spacing None, but qualifies for the comp. Force-in floors at T1 without admitting a passage; force-out wins for runtime, both def tiers and comp qualification.

3. **TRUE, with the limits below:** “On a fresh deployed SteveDesktop process, prove actual GetTier, AdultTier and T3-spacing predicate results for representative definitions under default and custom thresholds, restoring every changed setting and fixture exactly; retain raw proof and a fresh independent Codex judgment without claiming a completed passage, crossing, flight or L4 acceptance.”

   The successful evidence is evidence/raw/live-attempt5/, not the failed earlier runs. Actual static-call signatures include Observe(ThingDef, Int32), Fixture(ThingDef, Single, String, Int32, Int32), GateMatrix(Int32, Int32), Census(), Environment(), and null utility calls. The compiled hook calls actual GetTier, AdultTier, SpacingTier, DefQualifies and RM_TitanicKernel.TitanEventEligible. Independently inspected installed GetTier IL resolves its calls to Verse.Pawn.get_BodySize, Thresholds, ForceOf and TierFor; it does not substitute the test's size formula.

   Five changed static settings have original reads, set/read pairs, and final restoring set/read pairs: giantAnimalsEnabled=True, tierThresholdsCustom=False, T1/T2/T3=4/8/20. I replayed all 75 setter receipts, verified valueBefore continuity and requested/valueAfter/readback agreement, and obtained exactly the original values at the end. JawaBenchModSettingsFieldTools.cs uses reflection SetValue, without saving settings. The before/after settings-file inventories are both empty: that proves only absence of matching files, not a general filesystem audit.

   Real definitions are read, not rewritten. Runtime observations own each new Pawn, age tracker, cached stage index and health tracker. Synthetic races own cloned race properties, replacement stage lists/stage defs and force extension; they are never registered. The successful batch retains the sampled environment, exact per-call and whole-batch RNG state, definition counts and VEF dictionary count. Remaining fixture memo references disappear at recorded shutdown. This is restoration by disposal of process-local fixtures, not a claim that every global cache was restored in place.

## Independent controls and values

I executed evidence/raw/offline-test-bin/JuvenileTier.dll using installed Windows dotnet, with no build or game action: exit0, **14,798 checks**. Binary/deps/runtimeconfig hashes and current test-program/stub/project hashes match its manifest. These production adapter/kernel tests use engine stand-ins: L0, not a new live engine observation. The inspected program covers missing shipped-def fallback/logging, malformed data, force, valid/invalid ladders and same-process stage edits/restoration.

I separately replayed the raw calls in live-attempt5/loaded-methods.json, not its derived observations/ok labels: **153 observations, 686 resolved-kind census rows and 4,096 loaded gate cells**, recomputed from recorded settings/factors/forces and independent predicates, with zero discrepancies. The derived observation array matches its raw calls. All 332 calls report Entry/no current game and ticksGame=-1.

For default juvenile Adult3/Spacing2 versus ordinary Adult3/Spacing3, exactly eight gate cells change: masks216,222,224,230,240,246,248,254. Every change is an occupied-T3 rejection becoming admission with all other gates satisfied; unoccupied eligibility does not change. Bit order is opt-out, sea creature, sea map, has list, on list, homed here, season, T3 present.

| Definition/control and ladder | GetTier by supported stage | AdultTier | SpacingTier | Beside T3, other kernel gates true |
|---|---|---|---|---|
| Resolved RM_ReefbackJuv, 4/8/20 | T1,T2 | T3 | T2 | yes |
| Resolved RM_Reefback, 4/8/20 | T1,T2,T3 | T3 | T3 | no |
| Resolved juvenile, 4/8/16 | T1,T3 | T3 | T3 | no |
| Resolved juvenile, 4/18/30 | T1,T1 | T3 | T1 | yes |
| Resolved juvenile, 4/8/40 | T1,T2 | T2 | T2 | yes |
| Synthetic base3/factor4, 4/8/20 | T2 | T2 | T2 | yes |
| Same synthetic growth, 4/8/12 | T3 | T3 | T3 | no |

Stage observations repeat forward and backward for each ladder. Independently recomputed float32 body bits are 40CCCCCD (6.400000095367432), 41800000 (16), 42000000 (32), and 41400000 (12). Installed Core Data/Core/Defs/Misc/LifeStageDefs/LifeStages.xml supplies .2/.5; LifeStageDef constructor IL supplies omitted adult factor1. Current/deployed reefback XML replaces both juvenile lists with Inherit=False and inherits base32. Loaded observations confirm two juvenile stages, three ordinary stages, force auto and harness false.

Nine malformed fixtures cover null/empty lists, null entry/def, zero, negative, NaN and both infinities: Adult3/Spacing3, occupied veto retained. They intentionally provide no runtime GetTier claim for malformed stages. Twelve force controls cover base32/.2,.5, base6/.5, base1/.5 and base3/4 under out/auto/in. Equal, descending, NaN and infinite custom ladders, disabled custom tiers, disabled giant animals and return to defaults all produce shipped results. Nonpositive custom thresholds and missing shipped-definition fallback are additionally tested offline.

The census has six juvenile-only races: RM_CrimsonOpeeJuv, RM_ReefbackJuv, RM_RustNipperJuv, RM_ShaleGorgerJuv, RM_SiltLampreyJuv and RM_ThornbackColoJuv. Only ReefbackJuv is lineage T3/supported T2 at defaults; the others are None/None. Direct runtime Observe calls concern only RM_Reefback and RM_ReefbackJuv. Growth/force/malformed fixtures are synthetic controls, not newly resolved real-race claims.

## Production identity and fresh process

I independently hashed all 51 current production inputs and corresponding final-source snapshots against evidence/raw/source-built-identity.json: no differences. The explicit production csproj Compile set equals those 51 inputs. I verified the final build stdout hash against build-final.process.json; retained output reports successful Release build, zero warnings/errors.

Current repo and installed HugeThings DLL SHA256:
4a4f0cbcbcc2ad3f81c75b1d85f7c3deaae7d6e1623750e90692ddc9a68e1b9f.

Both source-stamp SHA256:
a7d9acee04dba20deb2f38df6047d38596eb0567637e949180feb6940c97b5c4.

Installed reflection-only MVID385de1c7-0e32-4880-892b-42afe31a9b93 equals the runtime Environment receipt. The selected reefback source/deployed XML hashes match (a1fed300…26daf9), as does the current live-script hash.

Attempt5 records game-down before deploy, one launch, PID13760 started 2026-11-11T17:29:40Z, port5174, then observations at17:31–17:32Z. Offline O01 sees no process; live O01/L01/L04 see that same fresh process and ordered running list. All five DLC are in the 16-mod list. Actual SteveDesktop lease/guard belongs to this seat, generation1422. Final status receipts say stopped and lease released.

Attempt1's O13 failure is real FlowWorks DLL/stamp drift, not N/A. Retained before/after dependency identities and my installed-only hashes confirm repair to DLL a4b1acd8…66d6cb and stamp d5a1ed0e…d1e0aef. The installed stamp matches the retained repo-stamp snapshot. This accepts dependency identity, not FlowWorks behavior.

Every required attempt5 offline/live preflight row passes. **Only O02 is N/A**, because it reads the other-host lease; actual-host ownership is separately evidenced above. O13 is required and reports six mods/5,972 files equal. O14 is cached lint with declared unsupported patch/donor scopes. O09 proves companion artifact equality while explicitly lacking a companion source stamp; it does not establish companion source provenance. Startup/post-probe observations report no exceptions/config/parse errors.

## Fixture fault and material caveats

I independently inspected exact installed VEF metadata and selected-method IL using reflection-only loading: SHA256 2f0c890c54dd0498aebcfa42b63a859f8acee894adddd08807a523d683e8dc6d, version1.1.7.0, MVID08cf6291-9208-48ec-82f7-5600b5af47da. These match live inventory and retained IL. About.xml identifies OskarPotocki.VanillaFactionsExpanded.Core and1.6 support; root LoadFolders.xml is absent.

VEF's BodySize postfix obtains a cache, adds bodySizeOffset and floors at.05. GetPawnDataCache checks needs then Pawn.Dead; needs-null/living returns defaultCache. Engine Pawn.Dead dereferences health; installed health constructor initializes healthState2 and HediffSet, while get_Dead compares against0. Thus attempt3's null-health exception in VEF is a fixture fault. Constructing the real health tracker fixes that contract without disabling the postfix or fabricating generated-pawn modifiers.

Attempt4 also failed: synthetic Def constructors consumed Rand. Installed Def constructor IL confirms RangeInclusive for debugRandomId. The final hook instead MemberwiseClones resolved Def objects, without RNG writes or Push/Pop. Every fixture and whole batch retain Rand93855105661918. Counts remain ThingDefs6158, stageDefs36, kindDefs686, VEF offset0 and dictionary count0. VEF memo still references the last fixture until shutdown: dictionary count0 does not mean all VEF caches are empty.

BodySize patch inventory names VEF and the local Forge postfix. The latter's source applies to registered swollen Dhoggur pawns, not these fresh fixtures. The observed VEF branch is needs-null/alive/empty-hediffs/unspawned, own-pawn/defaultCache memo, Tick10=0. This proves actual patched getter calls under that contract, not generated-pawn genes, hediff scaling, natural age progression or modifier computation.

The live hook calls the loaded kernel predicate with explicit occupancy and synthetic habitat inputs. It does **not** call map-level TitanPassageUtility.Eligible or T3OnMap on a populated map. Their wiring and unchanged arrival recheck are source evidence. No completed passage, crossing, flight, visual balance, hard resident/T2 cap or L4 acceptance is proved or owed here. Def-level spacing cannot forecast external runtime size modifiers; actual GetTier remains present-pawn authority. The pre-existing positive-infinite-factor AdultTier/DefQualifies discrepancy is preserved, not repaired.

## Original criteria and independence

**A1 L0: TRUE.** Independent policy, current source/spec agreement, preserved calf allowance and other gates, and meaningful positive/negative controls are established above.

**A2 L1: TRUE within loaded-method scope.** A fresh deployed minimal process provides actual tier/spacing-predicate results for two resolved representative races and explicit growth/force/threshold controls. Synthetic controls do not establish additional real-race facts.

No contamination identified. I did not open other Whittle folders, the builder decision document, prior judgments, parent summaries or handoffs. This judge performed no game/bridge/deploy/build/network/ledger/git mutations and accessed no other clone. Only JUDGE.md was written. Earlier failed runs remain failures; later success does not turn them into passes.

would show: yes
