# FOUNDRY_REBOOT_HANDOFF_202610012215 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610011154`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner ruled 2026-10-01 that **every mod gets a north-star script and new content is PAUSED until they all have one** (`design/RimMandrake/debug_process.md`, `NORTHSTAR_EVERYWHERE_PROGRAM_1`). Throughput is bounded by LIVE-BRIDGE time, not authoring: 14 scripts are authored and READY TO RUN, zero have run live except Graffiti (state half), Pyrelands (8 runs, not green) — so the next seat's whole job is to keep the bridge busy: `python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod <Mod> --tier <tier> --plan <plan> [--compose]` takes one script from game-down to a recorded run (the exact command is in each `Transient/worker_notes_<ITEM>.md`). Author the next batch offline in parallel while a live run is going (owner: *"Multitasking to keep the bridge active... Live bridge usage... a great metric to track"*).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **New-content pause is in force** and BENCH has not been told except via CHARTER/FOUNDRY/BENCH text — tell the BENCH window directly.
- **His mod list was restored** to the 611-mod pre-session list (sha256 f69bb9026a4b, equals `deployed/config/ModsConfig.pre-ns-graffiti.20261001.xml`); game is DOWN, bridge FREE. The live Mods folder now carries newer deployed biome/FlowWorks/UtinniPatches content and `Mods\Pits` was moved to `ModsRetired\Pits-2026-10-01`.
- **Real mod defects the scripts found/predicted** (not yet fixed unless noted): ScorchFruit never grows from a single burn; `Plant_TreeAnima` grows on a Pyrelands site; BlueDesert `krissek_off_quiet` (ExplodeOnDeath ignores `nativeDetonationsEnabled`, double blast when on); Wasteland MovingDunes binding is dark once composed; furnace beast stops heating at 24 C. Fixed by authors: Warcasket missing tickerType + stat in wrong block, WeepingStones About.xml claims, Barbslinger double turret comp (710208b9d), ~150 tier ConfigErrors (eff879ac9).
- **Saves kept (he deletes):** `NS_Pyrelands_site_1_46a3a8544c79*.rws` (several attempts), `NS_probe_retile_persist.rws`.
- Agent-written scripts may declare passing (his typed ruling); he will periodically release adversarial/GPT review (`NORTHSTAR_ADVERSARIAL_REVIEW_1`).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `NORTHSTAR_EVERYWHERE_PROGRAM_1` — pause in force, 14 of ~62 scripts authored; NEXT: take the bridge (`rimflow bridge take --for "north-star live runs"`) and run Warcasket via live_session.py, then Bacta, ExplosiveGrowth, GelatinousSlime, LeaningScrub, WeepingStones, LuminousPigment, Contagion, Cauldron, FeverWood, TheForge, Stillsand, BlueDesert, Wasteland in that order
- `PYRELANDS_GREEN_MINIMAL_1` — run 8 NOT GREEN (PASS 0 / FAIL 1 / UNMEASURED 19), site fixture burned; NEXT: rebuild the site with northstar_site.py (name faction+settlement in the script), rerun, then run `judge_cli.py` on the results
- `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1` — state 10/10 but judge UNJUDGEABLE (clipped marks, tiny crops); NEXT: fix the gallery framing in Graffiti validation.py and rerun with judge_cli.py
- `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` — wired + tooling built, tools not deployed; NEXT: with the game down run `python.exe build.py --gm --apply` (needs EnableSourceControlManagerQueries=false via WSLENV in a worktree), then flowworks tier + prep_site live
- `NORTHSTAR_DRIVER_RECORD_STATUS_1` — filed; NEXT: make northstar_driver record runs through modcheck/status.py (the pause definition needs it)
- `NORTHSTAR_BRIDGE_UTILIZATION_1` — filed; NEXT: add tick time to the results JSON timing and write bridge_utilization.py
- `FOOTPRINT_TRACK_GRID_1` — landed 84a377bf0, compiled+selftest only; NEXT: quicktest it on a deployed run before closing
- `WARSCAR_FREE_TIER_BODY_1` — unverified work saved on origin/wip/warscar-free-tier-body-recovered; NEXT: rebase that branch, build the Warscar DLL, review the RUT_MortuaryCrawler.xml deletion, land it
- `EXPLOSIVE_GROWTH_PROBE_TOOL_1` — filed; NEXT: build the JawaBench probe tool named in Transient/worker_notes_EXPLOSIVE_GROWTH_FIRST_SCRIPT_1.md
- `SLIME_SEEKER_LOAD_TOOL_1` — filed; NEXT: build jawa/slime_seeker_load per Transient/worker_notes_GELATINOUS_SLIME_FIRST_SCRIPT_1.md
- `NORTHSTAR_COVERAGE_AUDIT_1` — filed, untouched; NEXT: audit the 55 existing validation.py files and run lint_calls.py over them
- Follow-up items the authors proposed are NOT filed: every `Transient/worker_notes_*_FIRST_SCRIPT_1.md` ends with a FOLLOW-UP ITEMS section; NEXT: file them with `rimflow file` in one sitting

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A bridge-generated map that is not owned by a player settlement is culled on save; found a player settlement first (colony_found) (filed: LESSONS_INBOX)
- Loading a save over a live game NREs (GlowGrid.GlowPool.Take, "Error while loading a map"): go to the main menu, then load_game once (filed: LESSONS_INBOX)
- Closing the settlement naming dialog hops the current map to the quicktest colony; cell temperatures read stale until ticks run (filed: LESSONS_INBOX)
- `ordered_job waitTicks` is a no-op on a paused site; `step_game_ticks` needs timeoutMs or it gives up at ~10 s and a stale response id breaks the socket (filed: LESSONS_INBOX)
- zsh: `P="a b"; git add $P` passes ONE word — use `${=P}`; a `git stash` of your own edits is never needed (filed: LESSONS_INBOX)
- A hook refuses a whole command whose text names the modcheck status registry file, even in prose (see: debug_process.md; rephrase) (filed: LESSONS_INBOX)
- `git worktree repair --relative-paths` was run once (shared repo) so Windows git and python.exe work inside WSL worktrees (see: this handoff)

## Closed since the last handoff (8)

- `PYRELANDS_WALKLINT_FINDINGS_1` — 0989f63a3
- `FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1` — ca9d6a4f5
- `DEPLOYED_BIOME_REFS_ROTSPOREKIT_1` — fac981995
- `RUST_CATHEDRAL_HUM_UNMAINTAINED_1` — 9b410b512
- `SHADEGRID_BRIDGE_READER_1` — f01c5d87d
- `PITS_STALE_DEPLOY_COLLISION_1` — bd8d58dbbf7a6bbe7a97a23e061f2ede9ad413f7
- `FLOWWORKS_NORTHSTAR_WIRE_1` — 84f3788da551446bed8f26ffd807d5af44a83998
- `PYRELANDS_NORTHSTAR_WIRING_1` — bb474242d771917b79640374343574c7f26a3f4b

## Filed and still open (80) — the next seat's queue

- `ABYSS_ETCHFALL_BUILD_1` — Etchfall: Dark grain erodes unroofed stone and steel into tholin dust (slider)
- `ABYSS_LAMP_CROPS_BUILD_1` — Lamp crops: transplanted glowing trees light a farm against the Dark
- `ABYSS_INVENTED_CREATURES_TO_RM_1` — Move cindermare and skarnix into the free RM_ tier
- `ABYSS_DONOR_BEASTS_FREED_1` — Free ghorrumak and zhurrakor: own names, regenerated art, zero donor dependency
- `ABYSS_FREE_CRYPTID_1` — The Nhaleth: Abyss free-tier cryptid; Utinni relabels to the Forsakens (Sith whisper)
- `ABYSS_LIGHTFALL_BROOD_WRECK_1` — Lightfall's bottom: the dragons' brood and the wreck that repairs your ship
- `ABYSS_FOLD_LAMP_BUILD_1` — Heat-folding research and the fold-lamp (Abyss)
- `ABYSS_SOUNDSCAPE_BUILD_1` — Abyss gust soundscape plus Dark-swallows-sound spike
- `ABYSS_FREE_TIER_BODY_1` — Abyss free-tier body: own labels, wire 12 done crags art sets, guard/own 8 flora, weather labels, About fix
- `NORTHSTAR_EVERYWHERE_PROGRAM_1` — North-star scripts for every mod; new-content pause until done
- `ABYSS_FIRST_SCRIPT_1` — First north-star script: Abyss
- `ACOUSTIC_SCANNER_FIRST_SCRIPT_1` — First north-star script: AcousticScanner
- `ASSAILANT_SALVAGE_FIRST_SCRIPT_1` — First north-star script: AssailantSalvage
- `BLUE_DESERT_FIRST_SCRIPT_1` — First north-star script: BlueDesert
- `CAULDRON_FIRST_SCRIPT_1` — First north-star script: Cauldron
- `CONTAGION_FIRST_SCRIPT_1` — First north-star script: Contagion
- `CREATURE_BEHAVIORS_FIRST_SCRIPT_1` — First north-star script: CreatureBehaviors
- `DIVING_INTERACTION_FIRST_SCRIPT_1` — First north-star script: DivingInteraction
- `ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1` — First north-star script: EnvironmentalHazards
- `EXPLOSIVE_GROWTH_FIRST_SCRIPT_1` — First north-star script: ExplosiveGrowth
- `FEVER_WOOD_FIRST_SCRIPT_1` — First north-star script: FeverWood
- `FLOODED_CANYON_FIRST_SCRIPT_1` — First north-star script: FloodedCanyon
- `GELATINOUS_SLIME_FIRST_SCRIPT_1` — First north-star script: GelatinousSlime
- `GRAVSHIP_LANDING_FIRST_SCRIPT_1` — First north-star script: GravshipLanding
- `GREENTIDE_FIRST_SCRIPT_1` — First north-star script: Greentide
- `HOSTILE_FLORA_FIRST_SCRIPT_1` — First north-star script: HostileFlora
- `LEANING_SCRUB_FIRST_SCRIPT_1` — First north-star script: LeaningScrub
- `LONG_SHADE_FIRST_SCRIPT_1` — First north-star script: LongShade
- `LORE_STAGES_FIRST_SCRIPT_1` — First north-star script: LoreStages
- `LUMINOUS_PIGMENT_FIRST_SCRIPT_1` — First north-star script: LuminousPigment
- `MIASMA_FIRST_SCRIPT_1` — First north-star script: Miasma
- `MOVING_DUNES_FIRST_SCRIPT_1` — First north-star script: MovingDunes
- `NIGHTSIDE_ICE_FIRST_SCRIPT_1` — First north-star script: NightsideIce
- `OASIS_MAKER_FIRST_SCRIPT_1` — First north-star script: OasisMaker
- `PROXIMITY_HATCH_FIRST_SCRIPT_1` — First north-star script: ProximityHatch
- `PYRINTH_FIRST_SCRIPT_1` — First north-star script: Pyrinth
- `RUST_CATHEDRAL_FIRST_SCRIPT_1` — First north-star script: RustCathedral
- `SCARLANDS_FIRST_SCRIPT_1` — First north-star script: Scarlands
- `SHIP_VERMIN_FIRST_SCRIPT_1` — First north-star script: ShipVermin
- `STILLSAND_FIRST_SCRIPT_1` — First north-star script: Stillsand
- `TERMINAL_BIOMES_FIRST_SCRIPT_1` — First north-star script: TerminalBiomes
- `THE_BAZAAR_FIRST_SCRIPT_1` — First north-star script: TheBazaar
- `THE_FORGE_FIRST_SCRIPT_1` — First north-star script: TheForge
- `THE_ROT_FIRST_SCRIPT_1` — First north-star script: TheRot
- `THE_SUMP_FIRST_SCRIPT_1` — First north-star script: TheSump
- `TITANIC_CREATURES_FIRST_SCRIPT_1` — First north-star script: TitanicCreatures
- `WARCASKET_FIRST_SCRIPT_1` — First north-star script: Warcasket
- `WASTELAND_FIRST_SCRIPT_1` — First north-star script: Wasteland
- `WEBWORK_FIRST_SCRIPT_1` — First north-star script: Webwork
- `WEEPING_STONES_FIRST_SCRIPT_1` — First north-star script: WeepingStones
- `BACTA_FIRST_SCRIPT_1` — First north-star script: Bacta
- `BRAIN_WORMS_FIRST_SCRIPT_1` — First north-star script: BrainWorms
- `GIZKA_STOWAWAY_FIRST_SCRIPT_1` — First north-star script: GizkaStowaway
- `GRAFFITI_IMPERIAL_FIRST_SCRIPT_1` — First north-star script: GraffitiImperial
- `SARLACC_FIRST_SCRIPT_1` — First north-star script: Sarlacc
- `SHOKK_FIRST_SCRIPT_1` — First north-star script: Shokk
- `TROPHY_CRAFT_FIRST_SCRIPT_1` — First north-star script: TrophyCraft
- `DROID_REPAIR_JOBS_FIRST_SCRIPT_1` — First north-star script: DroidRepairJobs
- `EGG_RECKONING_FIRST_SCRIPT_1` — First north-star script: EggReckoning
- `FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1` — First north-star script: FungalSoilTrade
- `GREENTIDE_RAID_ANT_FIRST_SCRIPT_1` — First north-star script: GreentideRaidAnt
- `KYBER_TRADE_PLOT_FIRST_SCRIPT_1` — First north-star script: KyberTradePlot
- `PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1` — First north-star script: PropaneLakeMechanics
- `PYRELANDS_MECHANICS_FIRST_SCRIPT_1` — First north-star script: PyrelandsMechanics
- `RIVER_COLORS_FIRST_SCRIPT_1` — First north-star script: RiverColors
- `RUST_CATHEDRAL_ROACHES_FIRST_SCRIPT_1` — First north-star script: RustCathedralRoaches
- `SCARLANDS_LADDER_FIRST_SCRIPT_1` — First north-star script: ScarlandsLadder
- `SCAVENGER_EVENTS_FIRST_SCRIPT_1` — First north-star script: ScavengerEvents
- `SHIP_SHIELDS_FIRST_SCRIPT_1` — First north-star script: ShipShields
- `SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1` — First north-star script: ShokkweaveEconomy
- `WILDSTEAM_EGG_BOUNTY_FIRST_SCRIPT_1` — First north-star script: WildsteamEggBounty
- `ART_OVERRIDE_FAMILY_SCRIPT_1` — One parametrized north-star script for the 48 *ArtOverride mods
- `NORTHSTAR_COVERAGE_AUDIT_1` — Audit the 55 existing validation.py files for coverage of intended function
- `NORTHSTAR_ADVERSARIAL_REVIEW_1` — Standing: periodic adversarial and GPT review of north-star scripts
- `NORTHSTAR_DRIVER_RECORD_STATUS_1` — northstar_driver records its runs in the modcheck status registry (needed to lift the new-content pause)
- `BIOME_TIER_CLEANUP_1` — Biome tier cleanup: move twin-only features to RM_, scrub Star Wars IP, move RUT_ defs out of free mods
- `NORTHSTAR_BRIDGE_UTILIZATION_1` — Track live bridge utilization (active driving time over held time) as the program's throughput metric
- `EXPLOSIVE_GROWTH_PROBE_TOOL_1` — JawaBench probe tool so the ExplosiveGrowth script can cover harvest jackpot, cut gamble, rupture mutation and tell stages
- `SLIME_SEEKER_LOAD_TOOL_1` — JawaBench tool to load a slime seeker so the GelatinousSlime script can cover prime, extract, inject and the antidote race
- `NIGHTSIDEICE_HEAT_DIAL_BUILD_1` — Nightside Ice: eviction housekeeping, heat dial and shivven breach loop

## Commits

```
be910cd62 northstar_driver/live_session.py: one command from authored script to one recorded live run (keeps the bridge busy)
7a7158ae7 Health artifacts refresh Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com> Claude-Session: https://claude.ai/code/session_01TV3UHcYF6XK8Tv2D5kJ5mj
90dcf41f9 Nightside Ice turn-1 rulings recorded; heat dial build filed
21e5f59a3 WEEPING_STONES_FIRST_SCRIPT_1: first north-star script for WeepingStones (47 components, tier weepingstones_solo)
fdef1627d WeepingStones About.xml: remove two false statements (stocked pools "OFF by default", jobs "STILL OWED")
0c94ed68c Ledger sync: slime seeker tool item
18669c79a LEANING_SCRUB_FIRST_SCRIPT_1: first north-star script for LeaningScrub (43 components, never run live) Tier baroque_wave0 (LeaningScrub ships composed in mandrake.rm.biomes, so EXPECT_MODS is that id). The Lean is UNCOVERED: needs a Scrub-biome map site. Offline only: selftest proves each check red under a broken fake game; live shapes are unproven.
34011ad43 Rites rulings 2026-10-01: rites everywhere, Charged Reed, pyre merged into waking
2a85fd309 GELATINOUS_SLIME_FIRST_SCRIPT_1: first north-star script (39 components, 10/10 settings), offline-proven
53e2f369a Pyrelands suite: pen the warmth pair, record room_heat results
dc4bbe167 Ledger sync: ExplosiveGrowth probe-tool item
9739a6002 ExplosiveGrowth first north-star script: 33 chains, 51 walk lines, tier explosivegrowth_solo
ae74fb663 BACTA_FIRST_SCRIPT_1: first north-star script for Bacta (35 components, 8 chains, mock-proven)
27419f367 Nightside Ice bedazzle sitting: review, roster fill, GPT five, rites, turn-1 card
0516a3d46 WARCASKET_FIRST_SCRIPT_1: Warcasket first north-star script + walk; fix two MOD defects MOD: RM_Warcasket had no tickerType (apparel default Never), so the compound-failure comp never ticked; ToxicEnvironmentResistance sat in statBases, not equippedStatOffsets, so the pawn stat never rose. Guards: compound_failure_fires, toxin_cover.
5d5f7b546 Debug process: keep the bridge busy (owner ruling), file bridge-utilization metric item
736a2a36c Bedazzle: grandfathered order + GPT five-ideas step; file BIOME_TIER_CLEANUP_1
b80b24bc0 Rites register: drop wind-hour from the Weeping Stones row
4541ee03a HARNESS: offline lint of bridge calls against declared tool schemas (LINT_CALLS_1)
054fc56fe Biome rites pass: 23 found rites for the ten other bedazzle biomes
... 84 more: git log --oneline 66e940092..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-01T22:14:03Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/ledger/events/FOUNDRY.jsonl   <<< WHOSE? >>>
 M infrastructure/state/queue/BENCH.md   <<< WHOSE? >>>
 M infrastructure/state/queue/FOUNDRY.md   <<< WHOSE? >>>
?? deployed/config/ModsConfig.before-tier-graffiti_solo.xml   <<< WHOSE? >>>
?? deployed/config/ModsConfig.before-tier-pyrelands.xml   <<< WHOSE? >>>
```

