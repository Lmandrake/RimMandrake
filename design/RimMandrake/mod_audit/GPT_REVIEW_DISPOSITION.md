# GPT review disposition (2026-10-10)

**Source:** `Transient/foundry_modaudit_review_gpt_20261010.md` (GPT, high effort, 72 KB). It is the only GPT pass until
2026-10-13; Codex is quota-blocked until then. GPT never saw the repo. It saw `GPT_PACKAGE.md` only. So every claim it
makes about the files, and about what a named workshop mod does, was re-checked here before it was acted on.

**How to read this file.** Each GPT finding has an id (`G1.n`, where the number is its section) and one disposition:

- **ACCEPT**: true, and acted on (the change is named) or queued (the ticket is named).
- **REJECT**: our own evidence contradicts it (the evidence is named).
- **DEFER**: plausible, but it needs work or a decision that is not this pass's (the trigger is named).

Labels on mod facts:

- **VERIFIED-here**: re-opened in this pass. The path is given.
- **UNVERIFIED**: GPT asserted a fact about a workshop mod that this pass could not open. Its weblinks were not followed.

**Where the changes live.**

- Registry changes are in `review_amendments.json`, which `merge_checks.apply_amendments` consumes. They show in
  `MASTER_REGISTRY.jsonl` as fields `review`, `review_status` and `decision_status` CHANGED_BY_REVIEW / DISPUTED, with the old verdict,
  the new verdict, the evidence and `review: gpt_review_2026-10-10`.
- Owner rulings are in the same file, under `owner_rulings`.

**Tally:** 133 findings: **105 ACCEPT · 5 REJECT · 23 DEFER**. In the 30-verdict table (§4): 7 CHANGED, 7 DISPUTED,
2 REJECTED, 10 CONSISTENT, 4 RULED. So 7 registry verdicts were changed by the review, and 46 rows carry an owner ruling.

---

## 1. Method and record critique (GPT §1)

| id | finding | disp. | reason / action |
|---|---|---|---|
| G1.1 | One verdict mixes destination ("target") and removal readiness | ACCEPT | True. ELIMINATE rows are not "safe to untick now". Action: the README's maintenance section says a verdict is a TARGET. Readiness lives in `ACTIONS_NOW.md` gates (save census, edge review). A schema split (`removal_readiness` column) is DEFERRED to the next merge-tool change (ticket `MODAUDIT_VERDICT_REDESIGN_SPLIT_READINESS`). |
| G1.2 | No ELIMINATE verdict proves save-safety (placements unmeasured) | ACCEPT | True; the README's known-gaps list already says so. RETIREMENT WAVE 1 makes the save check a prerequisite of every step. |
| G1.3 | R1 "breaks N KEEP dependants" overstates: loadAfter / guarded MayRequire are not mandatory | ACCEPT | VERIFIED-here, and worse than GPT knew. `class_ref` also ignores guards and namespaces: `biomesteam.coreframework`'s two class edges are both guarded (§4 R1), and Armoury's 72 `class_ref`s into JecsTools are our own `CompExtraSounds` namespace (§4 R4). Ticket `MODAUDIT_CLASSREF_FIX_GUARDED_EDGES`: defscan must drop refs under MayRequire/FindMod and older-version folders, and must not credit a namespace that one of our own DLLs also defines. |
| G1.4 | `FACTS_REGEN_DELTA.md` joins assessor verdicts, not merged ones | ACCEPT | VERIFIED-here: `facts_delta.py:6,53` reads `assessments/batch_NN.jsonl`. Ticket `FACTS_DELTA_REWIRE_TO_MASTER_REGISTRY`. Until it is fixed, read the delta beside `MASTER_REGISTRY` `final_decision`. |
| G1.5 | 589-mod universe ≠ 550-mod measured runtime | ACCEPT | The arithmetic is now stated in the README: 589 = 551 FULL.LATEST + 38 OURS_ABSENT_INSTALLED. The session loaded 550 because `vlvop.tormentmaster.expansion` is listed but not installed. Separate inventory / authoring / runtime / release manifests are DEFERRED with G1.12. |
| G1.6 | Merged rationale can contradict the merged verdict (Aoba, Factional War) | ACCEPT | VERIFIED-here. `aoba.framework` `verdict_reason` still says "no dependant" while its final decision is KEEP. The Factional War reason says "no ruling names it" while the not-carded table cites FULL ACCEPT. The merge keeps the assessor's prose on purpose. `decision_change_reason` and `review.note` carry the correction. Ticket `MODAUDIT_RATIONALE_CORRECT_STALE_PROSE`. |
| G1.7 | Source presence ≠ completeness ≠ licence | ACCEPT | See §6. The README now separates `source_*` (identity) from reuse rights, which are not recorded yet. |
| G1.8 | A max-severity field collapses unrelated concerns | DEFER | True in principle. The severities are already per kind (`sev_memory`, `sev_tps`, ...), so nothing is collapsed in the registry. Ranking the proxies is the risk, and the README now says not to. |
| G1.9 | Patch investment treated as value (sunk cost) | ACCEPT | C01 (port everything) settles this for the eight donors. The README rule: patch counts are migration cost, never a reason to keep. |
| G1.10 | Checker agreement over-weighted (shared pipeline) | ACCEPT | This is why verdict changes need a spot-check of the primary source (`merge_inputs.json`), and why this pass re-opened files rather than voting. |
| G1.11 | "Conservative = KEEP" inflates the final stack | DEFER | The rubric's conservative rule picks PHASE over ELIMINATE, not KEEP. The point stands for "preference KEEP" rows (e.g. Starjack, §4 R24 → DISPUTED). A `BLOCKED` decision state goes with G1.1. |
| G1.12 | Ruling chronology: later broad rulings do not repeal specific exceptions | ACCEPT | `OWNER_RULINGS.md` is append-only and says when a ruling reverses another. The lightsaber upstream exception is unaffected by C01 (it was never on C01's list). |
| G1.13 | C01 said "two" permanent residents stay KEEP; there were three | ACCEPT | VERIFIED-here: `sarg.alphamemes`, `vanillaexpanded.vmemese` and `oskarpotocki.vfe.tribals` were all KEEP. Moot now that C01 is ruled (all three → PHASE). |
| G1.14 | C22 "all 86 Big and Small defs cut" vs facts 83/85 | ACCEPT | VERIFIED-here: `cherry_picker_cut_defs` 83 of `def_total` 85. 86 is the commit message's count. C22 was reworded. |
| G1.15 | C22 cannot drop Custom Quest Framework while Dungeon Pack is KEEP | ACCEPT | VERIFIED-here: `mlie.dungeonpack` is KEEP. CQF was removed from C22's removal list. |
| G1.16 | Pyrinth: verbatim defNames vs "repoint to `Absorbed_EpochsPyrinth` defs" | ACCEPT | VERIFIED-here: `src/RimMandrake/Pyrinth/About/About.xml` keeps the donor's `DV_*` defNames verbatim. `Absorbed_EpochsPyrinth` is a folder name. ACTIONS_NOW A3's "repoint" step was wrong and is deleted: a swap needs no repointing. |
| G1.17 | PackageId spellings differ across files | REJECT | The registry ids come from About.xml (facts). VERIFIED-here, each resolves to one row: `ogliss.thewhitecrayon.quarry`, `det.keshig`, `det.brawnum`, `gmmp.dungeon`, `aelanna.weaponracks`, `keshash.extraexplosioneffects`, `usgiyi.slaveoutfits`. The differences were in GPT_PACKAGE prose. |
| G1.18 | ISEKAI RPG Leveling has no row | ACCEPT | VERIFIED-here: no name or id matches in the 589 rows, so it is in neither FULL.LATEST nor our mods. The brief's §5 conflict about it is moot for this list. |

## 2. Blind spots (GPT §1 "cheapest instrument" table)

The audit cannot see any of these. The audit's own known gaps (README) cover only memory, TPS and the save.

| id | blind spot | disp. | reason / action |
|---|---|---|---|
| G2.1 | Harmony interactions and the real patch order | DEFER | Needs a live Harmony census (`Harmony.GetAllPatchedMethods` + owners) as a JawaBench tool. Ticket `HARMONY_PATCH_CENSUS_TOOL`, next bridge window. |
| G2.2 | Donor-to-donor conflicts | DEFER | Same instrument as G2.1, over every assembly. |
| G2.3 | Prepatcher transformations | DEFER | Is Prepatcher in FULL.LATEST? Answer that before building anything. Folded into G2.1. |
| G2.4 | Static initialisation cost | ACCEPT | Partly measured: `static_ctors` counts them. Timing them is the load-phase timer in G5.2. |
| G2.5 | Runtime components (actual instances and frequency) | ACCEPT | `jawa/map_comp_timing` (`91f9c0a14`) exists. Running it on the fixed build is ACTIONS_NOW F1. |
| G2.6 | Hidden compiled settings defaults | ACCEPT | Matches E tickets (Better Ambushes default, fog, DBH). New ticket `MOD_SETTINGS_HARVEST_EFFECTIVE_VALUES`: dump in-memory ModSettings after init. |
| G2.7 | AssetBundles / native resources / lazy assets / texture overrides | ACCEPT | Known gap (README). `HEAVY_TEXTURES_MEASURE_REAL_VRAM` is now ACTIONS_NOW F3. GPT's point that readable textures keep a CPU copy (VERIFIED-from-knowledge, Unity docs) is why the proxy is no upper bound. |
| G2.8 | Save-bound state beyond `<def>` grep | ACCEPT | `DOOMED_MODS_CENSUS_SAVE_PLACEMENTS` is widened to typed traversal (class names, genes, hediffs, world objects). |
| G2.9 | Version folders actually selected | ACCEPT | `defs_outside_loaded_dirs` is an offline guess. A runtime export of loaded folders goes with G2.6. |
| G2.10 | Map generation after the world freezes | DEFER | Real (landing and quest maps still generate), but it is C06's acceptance test, not this audit's. |
| G2.11 | Cross-layer behaviour and accumulating state | DEFER | Needs the land–camp–launch–transfer cycle (G9 step 10). That belongs to a release-candidate gate, not now. |
| G2.12 | Silent suppression (a failed raid logs nothing) | ACCEPT | It is the RaidEnemy prefix case. ACTIONS_NOW A4 now asserts that a raid fires, not just that the package is absent. |
| G2.13 | OS/hardware memory counters | DEFER | Goes with G5.3. |

## 3. Cluster exit sequencing (GPT §2)

| id | finding | disp. | reason / action |
|---|---|---|---|
| G3.1 | Two graphs: mandatory and compatibility | ACCEPT | Same fix as G1.3 (`MODAUDIT_CLASSREF_FIX_GUARDED_EDGES`). After it, `dependants_detail` kinds split into mandatory and compatibility. |
| G3.2 | SWAC exit: classify 3,439 refs, then port, then satellites, then state, then remove at the remake | ACCEPT | Matches C02 (waits for the remake) and `SWAC_EDGES_CENSUS_PORTED_VS_LIVE`. The four-bucket split is adopted as that ticket's output. |
| G3.3 | Alpha Animals: creature-by-creature ownership matrix, without changing rosters | ACCEPT | Fits C01 and the stopped-evictions ruling, since a matrix changes no roster. Ticket `ALPHA_ANIMALS_CENSUS_OWNERSHIP_MATRIX`. |
| G3.4 | Alpha Biomes: classify the 84 direct Biomes refs apart from the 1,155 | ACCEPT | Folded into `BIOME_DONOR_DEPENDENCY_UNTANGLE_HARD_LINK`. |
| G3.5 | Other Alpha systems: skills leaf first, then VSE | ACCEPT | Ruled by C08: both go together in WAVE 1, and Alpha Skills is unticked first. |
| G3.6 | Outer Rim: furniture first, Core last | ACCEPT | C02 holds Furniture to the remake. The order is kept in the PHASE notes. |
| G3.7 | VE content: build an active class-provider map | DEFER | It needs G1.3's fixed class_ref first. |
| G3.8 | VGE / Insectoids / Isopoda paired exit | DEFER | The rows are already PHASE. The pairing goes into C15's per-capability split. |
| G3.9 | Baroque biome donors: consumer before provider | ACCEPT | Reinforced by §4 R1: Fossils' guarded ref means Biomes! Framework can go first. |
| G3.10 | ReGrowth: is the ExplosiveGrowth reference real? | DEFER | A candidate `def_ref`. It gets checked at ReGrowth's port (C01), not now. |
| G3.11 | GravTide: census of components and serialized types first | ACCEPT | C03 ruled it goes after our sea-floor layer works. `GRAVTIDE_SAVE_CENSUS_TYPES_BEFORE_EXIT` is a prerequisite of that exit. |
| G3.12 | Facial Animation: contact sheet of founders and species | DEFER | Waits on card C16. |
| G3.13 | Genetics frameworks: export founder genes and race contracts | ACCEPT | Same need as owner question Q2 (new card C25). |
| G3.14 | RimTek / display case / Jecs / tree clusters lacked endpoints | ACCEPT | Registry changed (§4 rows R3, R4, R5, R10). |
| G3.15 | Factory: belts ≠ factory backend | ACCEPT | C10 cut the belts. VFE Factory stays as WreckedMachines' backend (C13 still open). |
| G3.16 | Vehicles: carts, motor vehicles and enemy vehicles decided separately | ACCEPT | C11 reworded to split them, and VVE is now named. |
| G3.17 | Dungeon / ruins: keep the substrate | ACCEPT | Same as G1.15. |
| G3.18 | Authoring tools are profile membership, not content verdicts | ACCEPT | C04 ruled them authoring-only. They are PHASE with "off the player list at release". |
| G3.19 | Owned patch containers are retired op by op | ACCEPT | `mandrake.rut.patches` is DISPUTED (§4 R8). `rut.doctrine` is already op by op. |
| G3.20 | No global order between SWAC, ReGrowth and Outer Rim | ACCEPT | No order was imposed. Each runs on its own gate. |

## 4. The 30 verdicts GPT asked to re-examine (GPT §3)

Status is what `review_amendments.json` records. CHANGED: the verdict moved on our evidence. DISPUTED: open, row marked
DISPUTED. REJECTED: our evidence contradicts GPT. CONSISTENT: GPT's treatment is the existing verdict. RULED: an owner ruling
settles it.

| # | packageId | before | after | status | evidence (re-opened here) |
|---:|---|---|---|---|---|
| R1 | `biomesteam.coreframework` | ELIM | ELIM | REJECTED | Fossils' only ref is `<li MayRequire="BiomesTeam.BiomesCore,…" Class="BiomesCore.StockGenerators.HighQualityItems">` (1.6 `BMT_Caravan_Paleontologist.xml:33`). That packageId is not installed, so it never loads. MVB's ref is in a `1.5/` FindMod patch. |
| R2 | `jellypowered.survivaltools` | KEEP | ELIM | CHANGED | `items/closed/STAT_NORM_WAVE3_RETIRE_1.md:1-6`: retired with VSRexamined on 2026-09-11 |
| R3 | `deon.rimtek.core` | PHASE | KEEP | CHANGED | DocMate (KEEP) hard-depends on it. Conditional: follows C21. |
| R4 | `jecrell.jecstools` | PHASE | KEEP | CHANGED | Doors Expanded (KEEP) uses `JecsTools.PlaceWorker_Outline`×32 and `PlaceWorker_OnTopOfWalls`×12 unguarded. `StarWarsPatches/About/About.xml:45`. Armoury's 72 refs are false (its own `CompExtraSounds` namespace). |
| R5 | `nightmare.core` | KEEP | PHASE | CHANGED | Its sole dependant, Invisible Display Case, is PHASE. The pair retires together. |
| R6 | `mandrake.rm.pyrinth` | PHASE | KEEP | CHANGED | It is the absorber (the destination). Art is regenerated in place. |
| R7 | `mandrake.rut.restrainingbolts` | REPLACE | KEEP | CHANGED | The fix is a one-line repoint (ACTIONS_NOW C4), not a rewrite |
| R8 | `mandrake.rut.patches` | PHASE | PHASE | DISPUTED | It holds campaign policy as well as donor compat, and no successor is named. Ticket `RUT_PATCHES_UNTANGLE_POLICY_FROM_COMPAT`. |
| R9 | `mandrake.rut.doctrine` | PHASE | PHASE | CONSISTENT | For our mods, PHASE already means "migrate the policy, then retire". |
| R10 | `chaoticenrico.bettertrees` | KEEP | PHASE | CHANGED | `items/TREE_GRAPHICS_OWNERSHIP_1.md`, owner verbatim: *"drop all the nonsense of multiple tree mods"* |
| R11-13 | `sarg.alphamemes`, `vanillaexpanded.vmemese`, `oskarpotocki.vfe.tribals` | KEEP | PHASE | RULED | C01 port everything |
| R14 | `mingtuwuxiang.spacebasedecorative` | KEEP | KEEP | DISPUTED | Donor furniture art. Scope is C17's, and it was added there. |
| R15 | `usgiyi.slaveoutfits` | KEEP | KEEP | DISPUTED | C17. The id is verified. |
| R16 | `ali.growodysseyplants` | KEEP | KEEP | DISPUTED | VERIFIED-here: it makes Boomshroom, Psilocap, Nightgrass and Willowgill sowable, three of them in hydroponics. Ticket `ODYSSEY_PLANTS_JUDGE_SOWABLE_SCARCITY`. |
| R17 | `vanillaexpanded.outposts` | KEEP | KEEP | CONSISTENT | Owner adoption 2026-08-07 |
| R18 | `mrhydralisk.voeadditionaloutposts` | KEEP | KEEP | DISPUTED | Type-level review owed. Ticket `VOE_OUTPOSTS_AUDIT_EACH_TYPE`. |
| R19 | `jaeger972.factionterritories` | KEEP | KEEP | CONSISTENT | C05 is reworded: it is runtime expansion, not a generator |
| R20 | `oskarpotocki.vanillavehiclesexpanded` | KEEP | KEEP | CONSISTENT | Now named in C11 |
| R21 | `sk.gravshipraids` | KEEP | KEEP | CONSISTENT | The captured-hull question is in C11 |
| R22 | `propickelz.tinkerbench` | KEEP | KEEP | REJECTED | VERIFIED-here: 5 recipes, a quality reroll and biocode removal. No genes, so no genetics ladder. |
| R23 | `neronix17.outland.genetics` | KEEP | KEEP | CONSISTENT | Hard dep of StarWarsRaces. The trim is an experiment. |
| R24 | `vanillaracesexpanded.starjack` | KEEP | KEEP | DISPUTED | A preference KEEP with no dependant. Added to C20. |
| R25 | `koth.isid` | KEEP | KEEP | DISPUTED | May be inert under the infestation ban. Ticket `ISID_PROBE_UNDER_INFESTATION_BAN`. |
| R26 | `mlie.storytellerenhanced` | KEEP | ELIM | RULED | C09 |
| R27 | `vanillaracesexpanded.fungoid` | ELIM | ELIM | CONSISTENT | Readiness waits for the save census |
| R28 | `redmattis.bigsmall` | ELIM | ELIM | CONSISTENT | The C22 count is corrected to 83/85 |
| R29 | `deon.rimtek.digipal` | ELIM | ELIM | CONSISTENT | C21 now argues the accuracy buff |
| R30 | `adaptive.storage.framework` | KEEP | KEEP | CONSISTENT | Hard dep of Armoury and 5 others |

**Dispositions for §3 as a whole:**

| id | finding | disp. | reason / action |
|---|---|---|---|
| G4.1 | The 30-row re-examination | ACCEPT | Table above: 7 CHANGED, 7 DISPUTED, 2 REJECTED, 10 CONSISTENT, 4 RULED. |
| G4.2 | Twenty high-risk KEEP rows, including our own mods | ACCEPT | It is an investigation order, not a verdict. Rows 1-4 (Biomes, FlowWorks, VE Gravship, HugeThings) are exactly what F1's map-component timing covers. No verdict changes. |
| G4.3 | ELIM rows whose removal cost is understated (11) | ACCEPT | Each one gets the save census and edge review before its untick. `xmb.ancienturbanruins.mo` and `btd.gbp.shippack.kotor.vge` get an edge review first. |
| G4.4 | Re-judging the 13 checker-changed rows | ACCEPT | GPT agrees with all 13. The only follow-ups are the stale Aoba rationale (G1.6) and Trystan's shuttles, where ELIM may be better than PHASE once C11 is answered (DEFER to C11). |
| G4.5 | R3 proxies: rename to "texture estimate"; a 6 MB crossing of 250 MB is meaningless | ACCEPT | The README says "estimate". The 250 MB cut-off was removed from C18. |
| G4.6 | R6 "outside loaded dirs" ≠ an undercount | ACCEPT | The README now says verify folder selection first. Excluded CE compat is correctly absent. |
| G4.7 | Other inconsistencies (stairs, Psyshrooms vs Psilocap, cosmetic furniture) | DEFER | Real, but they are cosmetic-scope questions for C17, and the psychoactive-plant pair goes with R16's ticket. |

## 5. Performance attribution plan (GPT §4)

| id | finding | disp. | reason / action |
|---|---|---|---|
| G5.1 | mapPost + mapComp ≈ 97% of stage share, so time the map callbacks first, not a donor purge | ACCEPT | This is the cheapest first experiment. ACTIONS_NOW F1 `MAPCOMP_TIMING_MEASURE_FIXED_BUILD`: 1,000 warmed ticks on the post-HugeThings build, aggregated, with the unattributed remainder stated. |
| G5.2 | Load-phase timing (ingest, patch, xref, static init, assets) | ACCEPT | ACTIONS_NOW F2 `MOD_LOAD_PHASES_MEASURE_FULL_LIST`. |
| G5.3 | Memory: private bytes, managed, native, GPU separated; profiler-unavailable = UNKNOWN | ACCEPT | Widened scope of `HEAVY_TEXTURES_MEASURE_REAL_VRAM` (F3). |
| G5.4 | Marginal cost, not additive per-mod totals | ACCEPT | The README rule: a cluster's saving is full stack minus the cluster, measured. |
| G5.5 | Benchmark discipline (frozen hashes, paired runs, ms/tick distribution, reject a faster run that lost content) | ACCEPT | It goes into F1-F3 as acceptance criteria. Step 1 of GPT §7 (freeze the deployment manifest) is F0. |
| G5.6 | Do not subtract 70 ms from the old profile to advertise a TPS | ACCEPT | The HugeFootprints proof (`14fa9468a`) measured 62.6 → 0.98 ms/tick on the Rot only. Nothing was extrapolated. |
| G5.7 | Twenty removal/trim experiments | DEFER | They are queued behind F1. Several are already ruled (Sandworm #16, LightsOut #2, Raid Fee #1 are in WAVE 1). The visual-pack subtractions (#3-#8) wait for C16 and C18. |
| G5.8 | Four owned art packs ≈ 7.4 GB proxy, face packs ≈ 6.1 GB, so C16's "largest share" claim is unsupported | ACCEPT | That sentence was deleted from C16. |

## 6. Absorption opportunities and licences (GPT §5)

GPT's licence facts came from public repositories it cited. This pass did not fetch them, so they are recorded **UNVERIFIED** until a
licence ticket reads each repo's LICENSE file at the deployed revision.

| id | finding | disp. | reason / action |
|---|---|---|---|
| G6.1 | Small functionality worth owning (salvage yields, selected weapons, holograms, incident allowlists, founder genes, north textures) | ACCEPT | Matches C13 option A, C15, C18, C09 (its study task) and ACTIONS_NOW C2. No new work item. Each is already carried by a card or an action. |
| G6.2 | Keep big frameworks (Harmony, HAR, Adaptive Storage, VEF, Vehicle Framework) upstream while consumers remain | ACCEPT | Consistent with the registry: they are KEEP. C01 does not cover frameworks. |
| G6.3 | VEF has public source (the audit said steam-only); licence CC BY-NC-ND 4.0 with extra permissions | ACCEPT (source) / UNVERIFIED (licence) | The facts' `source_kind` for VEF is wrong if the repo is real. Ticket `DONOR_LICENCES_VERIFY_BEFORE_PORT`: read LICENSE at the deployed revision for every donor we port from. Until then, no copied VEF code ships in an absorbed mod. |
| G6.4 | Vehicle Framework: official repo `SmashPhil/Vehicle-Framework`, MIT | UNVERIFIED → DEFER | Same ticket. |
| G6.5 | Adaptive Storage MIT; Alpha Animals and Alpha Biomes have 1.6 source but the licence is unknown | UNVERIFIED → DEFER | Same ticket. It matters for C01's ports: porting art or XML from Alpha mods needs the licence read first. |
| G6.6 | SWAC is MIT at repo level; its art is in AssetBundles, which explains the tiny texture proxy | ACCEPT (bundle point) / UNVERIFIED (licence) | The bundle point matches the README's known gap (32 MB of bundles). |
| G6.7 | Yayo, Cherry Picker, Research Reinvented: MIT; HugsLib's real source is `UnlimitedHugs/RimworldHugsLib`, not Quickstart | ACCEPT (HugsLib) / UNVERIFIED (licences) | The facts already list HugsLib Quickstart as a suspicious match. The facts source for `unlimitedhugs.hugslib` is to be corrected by the same ticket. |
| G6.8 | Public code without a licence grants no reuse right | ACCEPT | A standing rule. Recorded in the README maintenance section. |
| G6.9 | Archive the shipped revision, licence, build steps and hashes; keep copied, commissioned and original assets traceable | DEFER | A provenance register belongs to the art ledger (`art_ledger_design_2026-10-04.md`) and to absorption items. It is not added here. |
| G6.10 | Cheap exits with no replacement (Raid Fee, the VSR/Survival pair, gag sounds, Torment Master id, authoring tools from the player profile, birthhatchdemo, the MSE/bandolier fixes, shells) | ACCEPT | Raid Fee and the pair are WAVE 1 step 1. Gag sounds are C19 (open). Authoring tools are C04 (ruled, at release). The fix packages are C2. Shells are C22. `mandrake.rut.birthhatchdemo` off the campaign deployment: ticket `BIRTHHATCH_DEMO_RETIRE_FROM_CAMPAIGN_LIST`. |
| G6.11 | Sandworm: replacement equivalence is not established by theme | ACCEPT | The owner ruled it out now (C02). WAVE 1 still requires a save census for Sandworm types before the untick. |

## 7. Card wording critique (GPT §6, cards C01-C23)

Answered cards (C01-C04, C07-C10) are marked ANSWERED in `OWNER_CARDS.md`. GPT's critique of them is kept only where it changes
how the ruling is carried out.

| id | card | disp. | action |
|---|---|---|---|
| G7.01 | C01 split content from backend; schedule unsupported; count wrong | ACCEPT | The ruling note says frameworks are not in C01. The count is corrected (G1.13). |
| G7.02 | C02 readiness ≠ timing | ACCEPT | WAVE 1 Sandworm step requires a census of classes and serialized types. |
| G7.03 | C03 access ≠ protection | ACCEPT | Already how the ruling reads (Warcasket protects, never transports). |
| G7.04 | C04 split editors, overlays and scouting | REJECT | The owner ruled the whole family out of the player list. Splitting it again would reopen a settled ruling. |
| G7.05 | C05 Faction Territories is not a generator | ACCEPT | C05 reworded, and Territories moved to its own question. |
| G7.06 | C06 acceptance needs generated-map comparisons | ACCEPT | Added to C06's evidence line. |
| G7.07 | C07 misframed (breeding, children, slaves) | REJECT | The owner answered it in his own words ("kill all the mods that do this"). Breeding and slaves were never in the card's scope. |
| G7.08 | C08 "small crew gains little" is backwards | ACCEPT | Moot (ruled). WAVE 1 adds the serialized-expertise check. |
| G7.09 | C09 split cadence, incidents and nemesis; add Better Ambushes | ACCEPT | The two pending mods stay pending the study. Better Ambushes' card reference is corrected C10→C09 in ACTIONS_NOW E. |
| G7.10 | C10 too broad | REJECT | The owner ruled to cut all and add back by design. `convenience_replacements.md` already splits the functions. |
| G7.11 | C11 split hulls, carts, motors, enemy vehicles, walking; name VVE | ACCEPT | C11 reworded. |
| G7.12 | C12 measure before resetting to vanilla; tanks do not create fuel | ACCEPT | C12's recommendation is now C (measure, then decide). |
| G7.13 | C13 split backend, access, yields and bones; WreckedMachines needs Factory | ACCEPT | C13 reworded. |
| G7.14 | C14 permanent Yayo needs an explicit exception and config contract | ACCEPT | C14 option A now names which Yayo options are on. |
| G7.15 | C15 split five decisions | ACCEPT | C15 reworded per capability. |
| G7.16 | C16 delete "largest share of 30 GB" | ACCEPT | Deleted. |
| G7.17 | C17 recommendation invents a sound/UI exemption | ACCEPT | C17 is now neutral, and Space Base furniture is added. |
| G7.18 | C18 drop the arbitrary 250 MB cut-off | ACCEPT | Dropped. |
| G7.19 | C19 "none used by ours" is false (Van Beasts, Crypts, Torment) | ACCEPT | Wording corrected. |
| G7.20 | C20 NPC species policy ≠ player gene access; include Starjack | ACCEPT | C20 reworded. |
| G7.21 | C21 judge DigiPal on its accuracy buff; Core follows DocMate | ACCEPT | C21 reworded. |
| G7.22 | C22 reject ≥90% as an uninstall rule; keep CQF; Medieval Flavour is not a shell | ACCEPT | C22 reworded with the "no retained behaviour, consumer or state" test. |
| G7.23 | C23 transport settled; remove option C; test the Oracle with the CLI missing | ACCEPT | Option C removed. |
| G7.24 | Missing decisions: release budgets, config ownership, map retention, licensing continuity | ACCEPT (2) / DEFER (2) | Release budgets and the founder state contract became new cards C24 and C25. Config ownership is FOUNDRY's (G2.6 tool). Licensing continuity is the G6.3 ticket. |

## 8. ACTIONS_NOW corrections (GPT §6)

| id | action | disp. | change made in `ACTIONS_NOW.md` |
|---|---|---|---|
| G8.A1 | Add donor refs, classes, saved state and counter-patches before removal | ACCEPT | Step text widened, and it is now WAVE 1 step 1. |
| G8.A2 | Census all donor defs, not only Jerbal; "A15" dangles | ACCEPT | Fixed: it points to `DOOMED_MODS_CENSUS_SAVE_PLACEMENTS`. |
| G8.A3 | Stop the blind swap; resolve the defName identity | ACCEPT | Identity resolved (verbatim). The repoint step was deleted. The swap stays gated on the save census. |
| G8.A4 | Verify that RaidEnemy executes | ACCEPT | Added. |
| G8.A5 | Use structured transitions, not text scraping | DEFER | The lint design takes it when built. |
| G8.B1 | Verify effective settings semantics; campaign-only enforcement goes in RUT | ACCEPT | B1 text: the override lives in a RUT mod, covers startup, settings save and restart. |
| G8.B2 | Record observed values separately from intended; "20.2 generators" needs interpreting | ACCEPT | B2 text amended. |
| G8.B3 | Hiding designationCategory is not enough for found-only | ACCEPT | B3 text amended (recipes, minify, blueprints). |
| G8.C1 | Check the resolved research tree in the UI | ACCEPT | Added. |
| G8.C2 | Verify the winning texPaths in four directions | ACCEPT | Added. |
| G8.C3 | Prefer deployment allowlists to a growing blacklist | DEFER | The cheap blacklist fix stays. An allowlist is a deploy-tool redesign. |
| G8.C4 | KEEP+fix; test goodwill | ACCEPT | Registry changed (R7). Test added. |
| G8.C5 | Preserve saved god identity, favour and subscriptions | ACCEPT | Added. |
| G8.C6 | Generic Property works without Droidworks | ACCEPT | Added. |
| G8.C7 | An empty texture dir does not prove no graphic | ACCEPT | Added. |
| G8.C9 | Restore only still-intended keys, not the whole stale backup | ACCEPT | Added, and C9 is now WAVE 1 step 0. |
| G8.D | Separate mandatory edges from order edges | ACCEPT | Note added to D. The Jecs and Biomes! Framework corrections were made. |
| G8.E | Widen the save census; separate VRAM from private memory; fix Better Ambushes' card ref; the Outer Rim ticket becomes a licence check | ACCEPT | All four made. |

## 9. Ten-step plan (GPT §7)

| id | step | disp. | where it went |
|---|---|---|---|
| G9.1 | Freeze the post-HugeThings deployment and fixtures | ACCEPT | ACTIONS_NOW F0 `BENCHMARK_MANIFEST_VERIFY_FROZEN_HASHES` |
| G9.2 | Repair the registry model and regenerate against merged verdicts | ACCEPT | Partly done in this pass (amendments, rulings). The rest: `MODAUDIT_VERDICT_REDESIGN_SPLIT_READINESS`, `FACTS_DELTA_REWIRE_TO_MASTER_REGISTRY`, `MODAUDIT_CLASSREF_FIX_GUARDED_EDGES`. |
| G9.3 | Profile map components on the fixed build | ACCEPT | F1 |
| G9.4 | Export and enforce effective settings | ACCEPT | `MOD_SETTINGS_HARVEST_EFFECTIVE_VALUES` + B1 |
| G9.5 | Execute the smallest settled retirement batch | ACCEPT | RETIREMENT WAVE 1 |
| G9.6 | Full save, asset and class ownership census | ACCEPT | Widened `DOOMED_MODS_CENSUS_SAVE_PLACEMENTS`. Its acceptance test: it must find the known Medieval Alchemist backstory and the Rosaline genes. |
| G9.7 | Resolve the Pyrinth and north-art transactions | ACCEPT | A3 and C2 |
| G9.8 | Memory and load by asset provenance | ACCEPT | F2, F3 |
| G9.9 | Prepare the SWAC and Outer Rim exits; untangle the Alpha mandatory links | DEFER | Gated on C01/C02 timing (biome sittings and the remake) |
| G9.10 | Release-candidate travel-cycle validation | DEFER | A release gate. Needs C24's budgets first. |

## 10. Owner questions (GPT §8)

| id | question | disp. | action |
|---|---|---|---|
| G10.1 | Numeric release budgets (load, memory, p95 ms/tick, retained maps, hardware) | ACCEPT | New card **C24** |
| G10.2 | Exactly which nested founder and ship state survives the remake | ACCEPT | New card **C25** |
| G10.3 | Annual maintenance budget for owned replacements | REJECT | The owner's rulings already answer it (C01 "port everything", C10 "unless too hard"). A budget number would add a rule where he asked for judgement. |
| G10.4 | Must shipped saves upgrade across revisions, or are releases pinned? | DEFER | Real, but it follows C25 and has no consequence before the first release. Ask after C25. |
