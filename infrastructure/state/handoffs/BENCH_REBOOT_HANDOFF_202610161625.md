# BENCH_REBOOT_HANDOFF_202610161625 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610160621`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner's own account of ExplosiveGrowth (2026-10-16, verbatim on EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS) outranks every doc: dry-adapted alien plants barely grow until they get water, then grow x10; 'bursting' was an agent's misreading he found fascinating and accepted as exploration; later adapted to a REDUCED factor in permanently wet areas and FRUIT instead of bursting. Today's code drifted from all three (flat x4 everywhere incl. deserts, jungle x10, soak x10 stacking, default top splits+reseeds). Nothing more is built on ExplosiveGrowth until he rules the consensus. His standing order for it: consensus (running) -> BENCH's own deep design pass (hydroponics, sprinklers, hand-watering, wild plants, economy, perf, shared biome tuning classes; ground moisture: wet vs mud vs dry-next-to-water) -> GPT enrichment + skeptical review (gpt_consult.py) -> reach out to him with cards. Also decouple map plant DENSITY from growth SPEED.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Sprint S0 is RULED (all 12, on BIOME_SPRINT_PROVE_SCRUB_SETS_PACE): note Contagion keeps Dive AND Bodyprints in THIS sprint (owner reversed the defer); Ratchet: Pyrelands + GSS signed off, FlowWorks NOT ('We still need to resolve items on FlowWorks very much').
- Venomvine card is ready (4 questions in design/RimMandrake/venomvine_design_2026-10-16.md); he deferred it until after the ExplosiveGrowth consensus.
- Codex UAC dialog: template + shared home re-synced TWICE today to the latest sandbox-user provisioning (backup C:\Users\Mandrake\.codex_sandbox_backup_20261016). Not verified against his Codex desktop app — if a dialog appears, restore the backup. The facings redraw batch (233 pending) is STOPPED until a Codex call runs without 'sandbox setup required'.
- Liquids are now litres (1 level = 1,000 L, deep square 4 kL; barrel 208 L, bucket 15 L, bottle 1.5 L): his calls flagged — Chemfuel/astrofuel items still 200 L each; machine rates kept old balance (solar still 6,000 L/day).
- Hose/pump connection mockup sheet awaits him: http://localhost:35259/?t=5cQKurOK_hGH7Dhxi9E70Q (hefty 2x1 pump changes placement; hose 0.65x).
- Pit ladder art sheet awaits him: http://localhost:36179/?t=kxi6u8T-d6C9Cgjf1-kkQg (agent flags south-wall ladder and E/W reads weak).
- RustCathedral garbled comment: 'Fix the RustCathedral comments in the next RustCathedral rebuild — yes or no?'
- With Star Wars loaded, both a Baroque base plant and its canon twin spawn (Webwork ruling) — he was told, not asked.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK` — built 5bf8ec2b94 (two press bills + right-click; gizmo removed), not deployed; NEXT: at the next deploy, run the lacquer_bill validation chain and confirm a bill returns the same item with +1 coat.
- `PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE` — RUT/RSW plants reconciled (6a1183226c), 7 non-canon bases built (7aa0506443) with owner-picked art installed (813af30a49); NEXT: deploy biomes/UtinniPatches/SWBestiary/LongShade, remove the old AshkarrFlora folder from the game Mods dir and ModsConfig, then load once and grep Player.log for missing plant defs.
- `REVIEW_MAP_LABELS_FIX_ORPHANS_ADOPTED` — stations 8/9 notice lines now numbered in review_map.py; NEXT: on the next FW review map load run review_map.py --labels and confirm '8:'/'9:' labels show.
- `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS` — consensus agent RUNNING at handoff, writing design/RimMandrake/explosive_growth_consensus_2026-10-16.md (timeline, model, delta, watered/ground-moisture taxonomy, density-vs-speed decoupling); NEXT: when that doc lands on origin, do BENCH's deep design pass (as an opus subagent), then gpt_consult.py skeptical review, then cards to the owner.
- `VENOMVINE_BUILD_SCRUB_GROWS_TEETH` — design doc done (fa04d1f55c); NEXT: after the ExplosiveGrowth consensus, put its 4 card questions to the owner.
- `ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL` — 168 rescaled + feet re-seated, pilot 10 installed (17b63dfb21); batch of 233 STOPPED (facing_regen_batch.py, state in Transient/facing_regen_batch_2026-10-16/state.json); NEXT: run one codex_image probe on the shared home, confirm its .sandbox log has no 'sandbox setup required', then `python3 src/RimMandrake/Utils/art/facing_regen_batch.py run` (single worker).
- `RESTART_DEPLOY` (no item; see Transient/ratchet_live_runsheet_2026-10-16.md + Transient/biome_sprint_live_order_2026-10-16.md) — today's ~20 offline builds are undeployed (water levelling, tar tool, slime, rock dig, pit lip/ladder/spikes, 8 map controls, lacquer, GSS spark, tank styles, containers, litres, plant draw order, bases, pen companion); NEXT: at the next owner-present game-closed window follow the ratchet run-sheet's deploy list, then walk FW stations 1, 2, 3 (tar tuning), 11, 12, 45, 51 with him.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Codex sandbox UAC storm: each elevated setup re-provisions the machine sandbox users, so parallel isolated CODEX_HOMEs each re-prompt (filed: lessons 20261016T144632Z; guard in codex_image.check_sandbox_fingerprint)
- --per-ruling / --owner-said rimflow acts record under the OWNER shard even with --seat BENCH; agents then leave OWNER.jsonl dirty and ./publish refuses (reset --keep) — commit OWNER.jsonl with the BENCH shard (see: this handoff)
- A shared-source change (_Shared/PatchApplier.cs) without rebuilding all ~39 DLLs blocks every push via DLL_SOURCE_STAMP_GUARD_1 (see: 4d93839d87)
- pkill -f from a Bash call matches its own shell and kills it (exit 144) — use ps|grep [x]|awk|kill (filed: memory pkill-f-matches-my-own-shell)
- zsh does not word-split $VAR in git pathspecs — use --pathspec-from-file (see: instrument_traps.md zsh no word-split)

## Closed since the last handoff (5)

- `FURNACE_WARMTH_FIX_NO_SIGN_TO_READ` — 536e6c3d01
- `FURNACE_AURA_FIX_WARMS_THROUGH_WALLS` — 536e6c3d01
- `FIREHAWK_EMBER_FIX_WALKS_ITS_TWIG` — 536e6c3d01
- `SCORCH_FRUIT_FIX_LANDS_ON_FIREBREAK` — 536e6c3d01
- `TAPCLAMP_REDRAW_BITES_DOWN_AT_LAST` — c4bd7af75a

## Filed and still open (27) — the next seat's queue

- `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` — FlowWorks: water flows from higher water surface to lower (fill-depth), gap >=2 units, so flat channels level and edge drains empty; replaces GRAVITY-
- `TAR_LOOK_TUNE_THICK_AND_SLOW` — Tar surface: water ripple plus a thick, slow, glossy look, tuned live with the owner; needs a live look-tuning bridge tool so tuning costs no restarts
- `GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT` — Tall plants (giant mushrooms on the FW review map) overlap wrongly: a more-southern plant must draw in front of a more-northern one
- `FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY` — FW review station 11: forced canyon flood is torn down next tick on a non-canyon map (Active false: featureInOtherBiomes off); with it flipped on live
- `SLIME_CROSSING_BUILD_SLIPPERY_SLOPE` — FlowWorks slime: nearly uncrossable and slow to climb out of (owner: 'so slippery it is nearly uncrossable'); build the mechanic + review-map station 
- `PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE` — Census every plant def in RUT/RSW mods: generic -> move into Baroque Biomes; genuine SW canon -> reskin of a non-canon Baroque base; owner examines th
- `DIG_ROCK_TUNE_STONE_FIGHTS_BACK` — Canal digging: through rock yields rock chunks at the vanilla rock-wall mining rate and takes much more work; chunks very rare through non-rock ground
- `PIT_LIP_FIX_BOAR_HANGS_OUT` — Pit near-lip occlusion: a pawn lying (asleep/downed) in a pit's southern cell draws over the south lip instead of being hidden by it
- `REVIEW_MAP_LABELS_FIX_ORPHANS_ADOPTED` — Review map notice lines for stations 8 and 9 float with no number
- `SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR` — Sluice gate and every canal water-blocking structure auto-rotate after placement like vanilla doors (orient across the channel/between its walls)
- `LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK` — Lacquer worn items via a press bill plus right-click the press, no pawn gizmo
- `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS` — FlowWorks dev-placed Source and Sink objects (any liquid, set rate; minimal look; not buildable) for map makers, review/test maps and Inhabited
- `PIT_LADDER_REDRAW_HUNG_ON_THE_WALL` — Pit ladder mounts on a pit wall like a door (placed on the edge, faces into the pit), with a slid-up state (prisoners below can't reach) and a slid-do
- `FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES` — Dev map controls (FlowWorks): flow meter, level holder, timer switch, map-edge setter, current painter, liquid thermostat; all map controls incl. Sour
- `FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS` — Dev map controls (Baroque Biomes): flood trigger aimed at a canal (fixes FW review station 11) and soak zone for ExplosiveGrowth; same insignificant-r
- `DEWBACK_ART_RECONCILE_ONE_LIZARD_MANY_CARDS` — Dewback art is split across several texPaths/sheet cards (RimStarWars/SWBestiary/Dewback, swanimals/Dewback via ArtFold, Dessicated, DesertVehicleResk
- `PIT_SPIKES_SHRINK_HALF_A_MAN` — RM_Spikes art fills the whole pit cell vertically; redraw: spikes about half a man tall, mostly pointing up (review station 45)
- `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS` — Bottles, buckets, barrels: four tech styles each (Junker oddly shaped, Industrial generic water bottle, Modern multicoloured soda bottle, Futuristic h
- `GSS_CORD_SILENCE_PHANTOM_SPARK` — GSS draws a second, dangling sparking cord at a pump fed by an adjacent conduit (vanilla adjacency): only the one real connection should draw; also FW
- `TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH` — FlowWorks tanks (liquid tank, universal cargo tank, etc.) get the four-look style switch like hose reels and the rest
- `HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY` — Liquid connection visuals: pump heftier than the hose, hose diameter a bit thinner, visible connectors wherever hoses/pipes/tanks/reels/pumps join (in
- `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS` — Re-base all FlowWorks liquid accounting to litres (deep square ~4,300 L; barrel 208 L, bucket 15 L, bottle 1.5 L); convert saves; show depth in metres
- `CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD` — Cauldron suite: add rows for Filter-Works converting, ruins at mapgen, Oomo shrine, gas drift (ruled scope, no rows today)
- `CAULDRON_FLECKS_FILL_SEVEN_STILL_BLANK` — Cauldron: draw the 7 missing overlay textures (2 assay flecks, 5 dew variants); O-TEX fails on them
- `EXPLOSIVE_SCOPE_ROW_PROVE_NEEDS_QUIET_LIST` — ExplosiveGrowth scope_native_only is UNMEASURED on biomes_sprint (campaign layer loaded); prove it on explosivegrowth_solo
- `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS` — ExplosiveGrowth deep dive: what it is configured to do now, the original design, and where to take it (owner has serious concerns)
- `VENOMVINE_BUILD_SCRUB_GROWS_TEETH` — Venomvine: LeaningScrub's integral plant - grows abundantly, tall and dangerous; design pass over its many variants, then build in this sprint

## Commits

```
c4068a8965 Ledger: owner's ExplosiveGrowth intent (verbatim)
fa04d1f55c Venomvine design: islands, tree height, own creep outside Explosive Growth, 15 forms as rooms; 4 card questions
5a08d49279 Dhoggur swell proven live: dhoggur_swell 12/12 PASS; harness fixes (hit must land, own manhunter declared, action prefixes, float readback)
f61afb36a8 Ledger: sprint S0 rulings 1-12, Venomvine and ExplosiveGrowth rethink items
9e34476558 Explosive growth deep dive: today's build, the original design, gaps, four directions
b903992251 Donor-off L1 round 2026-10-16: results, item prose, ledger note; bridge released
37199ecfb9 RM_Dhoggur: claws link FrontLeft/RightPaw (QuadrupedAnimalWithPaws has no *Leg groups; 4 config errors at load)
51a448ec35 Lessons x8 (L1 save load, water-body bug, instruments); FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW closed
f7f2a6d309 FlowWorks: fix vanilla WaterBodyTracker count drift when water changes type (the 'soil throw'); setting, default on
c7beb1cf36 L1 save: SAVE_LOAD grades the state read; donor refs split to SAVE_DONOR_REFS, UNMEASURED when the log tap is lossy; match the referenced name only
54f642f2b6 L1 save row: load_game passes ignoreModCompatibility and reads its reply; Deep Orbit joins donor_off_phase0 (save's Orbit2 layer)
cf5a7abcd7 DHOGGUR_SWELL_PROVE_LIVE_POKE_THE_BEAR: name the swollen-art jobs and sheet
cb24533a4a Dhoggur swollen/angry art: artpipe job forgeslot_dhoggur_swollen_v1 (E/S/N) on review sheet, not installed
0766a01795 Ledger: close DHOGGUR_USE_DECIDE_SNUFFLING_FOR_A_JOB (swell built, 3536bca79), file DHOGGUR_SWELL_PROVE_LIVE_POKE_THE_BEAR
9df25cd9fc Dhoggur: chemical swell when harmed (x3 size/health/bite, fire spit, manhunter, 1/3 day, 1-day cooldown from its end) + dhoggur_swell script
3536bca791 Dhoggur: chemical swell when harmed (x3 size/health/bite, fire spit, manhunter, 1/3 day, 1-day cooldown from its end) + dhoggur_swell script
81f59db409 Ratchet release: GSS 1.0.0 repackaged (DLL from 2b215d4589, hash in CHANGELOG); pilot verdict section H final; live run-sheet; ledger closes
00ac655f03 GSS: SettingsLoaded comment no longer claims AfterExpose re-reads every forced-off field (owner filter landed)
2909c1f773 Code review: 10 files clean (PatchApplier owner filter, GSS toggles, TribesOrNull)
31086c0395 Ledger: LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS built (note, lease renewals)
... 230 more: git log --oneline 40d2e43779..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : UP  → corrected to DOWN, measured now
- Bridge: for     Dhoggur swell live proof + Forge DLL deploy; owner handed bridge

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/census.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M Transient/biome_ffar/census.md   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.decisions.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M Transient/biome_ffar/scale_ground_measured.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M Transient/mc_human_review/KEYSHEET.md   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M Transient/mc_human_review/keysheet.html   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M conversations/2026-10-12-1403-b0ee9afc.md   conversation records: the hourly sweep commits them
 M conversations/2026-10-13-0007-b342a8ee.md   conversation records: the hourly sweep commits them
 M conversations/2026-10-16-0354-4af4c7c7.md   conversation records: the hourly sweep commits them
 M deployed/config/ModsConfig.before-tier-bridge.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
 M src/RimMandrake/FlowWorks/northstar/review/map/COVERAGE.md   derived: review_map.py --plan regenerates (agents left it, mixed with in-flight work)
 M src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md   derived: review_map.py --plan regenerates (agents left it, mixed with in-flight work)
 M src/RimMandrake/FlowWorks/northstar/review/map/keysheet.html   derived: review_map.py --plan regenerates (agents left it, mixed with in-flight work)
 M src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? conversations/2026-10-02-1217-54206aec.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-02-1952-4b4a687b.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-02-2332-d58606e4.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-03-1458-7ed5ddfd.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-04-2105-400ef7dc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-04-2219-962263b0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-05-1426-fab8a134.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-06-0601-5ab77072.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-06-1305-ecebcb6f.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0058-b305fb53.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0059-c857706d.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0120-033b16fc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0547-d6861da6.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-1520-6a6f7a30.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0001-cc216258.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0158-8aeef5fc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0215-c4ae9260.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0217-3acaea39.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1348-bac7589f.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1411-2294fe53.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1411-3ffd55d0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1413-52caf5c0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1413-658e0588.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1414-b4b8553c.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1428-de9591de.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-09-0450-85e0a0f9.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-09-1308-818639f9.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0040-5e2fd376.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0049-58eabd09.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0440-c71b568d.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-1341-91d07ad1.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-2102-71d8c9eb.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-0052-2f152d1c.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-1934-f086ce1a.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-1953-24347684.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-2000-edefebc8.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-12-0625-88710e84.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-13-1146-7444c21a.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-15-1939-5e86e9cb.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-16-0628-abd280e4.md   conversation records: the hourly sweep commits them
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-flowworks.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/RM_WallFace_North.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/RM_WallFace_Side.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GSS   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230218.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230455.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230639.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231027.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231203.json   not ours / pre-existing or another BENCH agent's derived output: left untouched
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   not ours / pre-existing or another BENCH agent's derived output: left untouched
```

