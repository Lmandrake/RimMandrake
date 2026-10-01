# FOUNDRY_REBOOT_HANDOFF_202610011154 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610010319`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Nothing built tonight has been PROVEN in game beyond two live rounds (Transient/LIVE_SESSION_2026-10-01.md and LIVE_SESSION_2_2026-10-01.md); the live-proof items are `STILLSAND_FIXES_LIVE_PROOF_1` and `LIVE_ROUND2_FIXES_PROOF_1` (each lists the exact Player.log string that decides it). The game folder holds main at 7caa6b5c9 only, and the shared tree is dirty and behind, so a fresh deploy runs `deploy_custom_mods.py --apply` and `--compose biomes --apply` from a clean worktree of origin/main (`D:\Luke\dev\RimMandrake-wt-livedeploy`, `git checkout --detach origin/main` first), game DOWN.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Decisions filed for you: `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1`, `LEANINGSCRUB_SWEETLINE_GUARDIAN_1`, `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1`, `LONGSHADE_MIDDENS_DESIGN_1`, `GLOOMCAST_WAKE_RIDERS_1`, `CRACKEDLANDS_LEDGES_OF_MERCY_1`, `CRACKEDLANDS_WOOLAMANDER_FLIGHT_1`.
- `SHADECRAFT_LESSONS_DESIGN_1`: every lesson named is Long-Shade-only, which contradicts the ruling that shade gear works in other hot biomes — a Stillsand colony could never learn the sun shield.
- I picked the sap-sucker numbers myself on your 'I pick numbers' card (nectar/sap Mass 0.045 to match Core Milk; the rest kept and re-labelled TUNED); veto freely.
- Two agents handled `selftest_sound_paths.py` differently: Cracked Lands added four vanilla clips to its allowlist, Forge left four unlisted (`FORGE_VOICES_AUDIO_1`).
- The sun-heat patch makes open sun read as dangerous heat, which sends wild animals (4 of 6 soorraks) off the map.
- 27 dead gates now repointed to mandrake.rm.biomes means patches that never ran now apply; round 2 showed no new load errors.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `CONTAGION_GROWN_LIMBS_BUILD_1` — started; Pillar Arm + Lash built (e713b8036), REST_1 closed at 5f3c5438f, live smoke loaded clean, still `doing`; NEXT: read the five limbs' defs back by state read on a quicktest, then `rimflow close CONTAGION_GROWN_LIMBS_BUILD_1 --sha e713b8036`
- `SOORRAK_INSTANT_JOB_LOOP_1` — blocked on evidence; vanilla and RM code ruled out, instant-job logging landed in 246950f7d; NEXT: capture the `[RM CreatureBehaviors] instant job loop: RM_Soorrak` line on the next live run and fix the job it names

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `rimflow close --sha` silently falls back to HEAD after a failed commit, and rebases leave dead shas on closed items (filed: LESSONS_INBOX)
- With a peer's index.lock in the shared tree, commit from a private worktree off origin/main; the ledger shard union goes by plumbing (filed: LESSONS_INBOX)
- Gates naming retired biome packageIds are silently dead; 27 repointed (filed: LESSONS_INBOX)
- Shared tree still has FOUNDRY.jsonl modified and items/FEVERWOOD_SAP_SUCKER_TUNING_1.md deleted, both already published in 7ba336b4d — `git checkout -- ` those two paths or its `shared_sync` reset aborts (see: this handoff)

## Closed since the last handoff (31)

- `FEVERWOOD_SAP_SUCKER_TUNING_1` — 9af41986b3207fec2ba2b8497210aa3ee06ca296
- `CHILL_CRYOPONICS_GROWER_1` — c04221efdafa67e389b20edc365fe4a171d5bb35
- `CHILL_FLOOR_GROWING_BED_1` — c04221efdafa67e389b20edc365fe4a171d5bb35
- `STILLSAND_SAND_SWIM_KIT_1` — d1c711fcb
- `STILLSAND_BEDAZZLE_CONTENT_1` — 8132caca2a5ce905e8cfc77160885b34f0cc2227
- `STILLSAND_SUN_FROM_LATITUDE_1` — 37bad33986b3338695a7bb03ad7409c95b11ae47
- `STILLSAND_EVENT_CREATURES_1` — 136c287f5
- `STILLSAND_PRECIOUS_CAVES_1` — 6236731d6
- `STILLSAND_GLARE_BLIND_GOGGLES_1` — a3dce483a
- `STILLSAND_MIRAGE_CONDITION_1` — 6106d6a2d
- `SELFTEST_RUNNER_SPEED_1` — 8fd48835b
- `STILLSAND_WIND_SUN_BEARING_1` — 4398421d4
- `STILLSAND_STILL_COOLING_DRAUGHT_1` — 568fa9d2c
- `STILLSAND_RETURN_RITUAL_1` — c1aa656de
- `STILLSAND_GLASS_LENS_CHAIN_1` — 86e2b0fc9
- `STILLSAND_SKELETONS_TRACKS_1` — 3843ba1f4
- `STILLSAND_DEAD_GATE_SWEEP_1` — 4430a2ec6
- `CONTAGION_GROWN_LIMBS_REST_1` — 5f3c5438f
- `STILLSAND_LOAD_DEF_ERRORS_1` — 937aba350
- `STILLSAND_DUNE_GALE_1` — 76bf78a91
- `CRACKEDLANDS_GPT_ENRICHMENT_1` — a222f3d36
- `CAULDRON_GPT_ENRICHMENT_1` — e04968bdb
- `OORRIK_PAWNGEN_NRE_1` — c86ba25f6
- `SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1` — 2d1886be8
- `SOORRAK_FLIGHT_JOBSTART_NRE_1` — 99163e0e7
- `RIMPLACE_GENSTEP_NRE_1` — bb2631aaa
- `LEANINGSCRUB_GPT_ENRICHMENT_1` — 8e3d24e35
- `FORGE_GPT_ENRICHMENT_1` — 774d5c764
- `LONGSHADE_GPT_ENRICHMENT_1` — d4193b9e6
- `MUURROK_BEAM_NO_DAMAGE_1` — f591714e5
- `RIMPLACE_STUFFLESS_THING_ROWS_1` — a204c05b1

## Filed and still open (98) — the next seat's queue

- `FOOTPRINT_TRACK_GRID_1` — One footprint grid for the planet: capped TrackGrid + section layer + cell-entry postfix in CreatureBehaviors, invisible pawns recorded, erase API; Wa
- `WARSCAR_FREE_TIER_BODY_1` — Warscar free-tier body: chatrak (+ chatrak plate leather), totchak body, tetchik, wreck-lichen; pallbearer and scar roach to RM (save-checked); glower
- `WARSCAR_SETTLING_WEATHER_1` — Warscar Settling: calm-triggered war fallout, settled film that keeps tracks on the shared grid, wind wipes it, the lift front, war dust, buried ordna
- `WARSCAR_AEROSOL_SCREEN_1` — Warscar projectors and aerosol screen: lift ShipShields particulate core to RM, broad polluted-biome screen balanced by cost, live/dead rings, salvage
- `WARSCAR_SNAP_MARK_1` — Warscar chatrak snap (scaria incubation with visible stages) and the mark made a trade (RM port, stat pay, loosened panels, no stacking)
- `WARSCAR_TOTCHAK_WAKES_1` — Warscar totchak: dormant in the Last Line, demolition wake, eats ruin walls then player walls, lies down again
- `WARSCAR_GEIGER_CHOIR_1` — Warscar Geiger choir: tetchik tick, wind on metal, Settling silence, projector hum, pool boil; the tetchik in a jar pollution counter
- `WARSCAR_HOSPICE_DESERTERS_1` — Warscar hospice: kneeling chassis rings, deserter histories, five-stage cradle revival into an overseer-free servitor, named failed wrecks, a deserter
- `WARSCAR_OLD_TONGUE_1` — Warscar old tongue: inscribed panel sets read by Intellectual 8 unlock hospice protocols, projector calibration, the pool phase reader
- `WARSCAR_RAINBOW_POOLS_1` — Warscar rainbow pools: reaction-liquor registry row, phase cycle with colour-blind icons, tap and four reagents, journal and phase reader, glower crus
- `WARSCAR_PILGRIM_CAMPS_1` — Warscar pilgrim camps (RUT): camp prefabs and journals that call AdvanceStage(Scarlands); rung texts from the owner-edited drafts
- `WARSCAR_TURRETS_TRACK_1` — Warscar turrets still track: verbless aim comp on broken turrets, refit into a working old-line turret
- `WARSCAR_CHOTRIX_BUILD_1` — Chotrix: the Warscar's invisible hunter (cloak-lacquer eater, prints on the track grid) + permanent cloak lacquer (owner card 2026-09-30)
- `FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1` — Harmony postfix on Pawn_MindState.CheckStartMentalStateBecauseRecruitAttempted so a failed tame triggers the sap-sucker refusal (opus; add Harmony ref
- `CONTAGION_GROWN_LIMBS_ART_1` — Art for Pillar Arm and Lash (replace Anomaly placeholder textures) plus item icons; check _artsrc and artpipe done first
- `REPO_RENAME_SYMLINK_RETIRE_1` — Retire the Rimworld -> RimMandrake symlink: repoint every old-path reference, then remove the link
- `STILLSAND_SAND_SWIM_REMAINDER_1` — Sand-swim kit remainder: thumper, sand fishing, the Listening, wake track records, drift depth, Drazzik/Sarlacc reconciliation, live criteria
- `PYRELANDS_NORTHSTAR_TRIAL_1` — Pyrelands north-star trial: carry the biome template to SHIPPED (parent; depends on BIOME_MOD_UNIFICATION_1)
- `NORTHSTAR_FAST_DRIVER_1` — Ultra-fast Python bridge driver for north-star validation (core built, live proof owed)
- `NORTHSTAR_PHASE_LADDER_1` — North-star phase ladder standard: DRAFT, VALIDATED, WIRED, GREEN min, GREEN full, SHIPPED
- `PYRELANDS_NORTHSTAR_WIRING_1` — Wire every Pyrelands bar with shows= and fix suite bugs (composed mandrake.rm.biomes packaging)
- `MODCHECK_COMPOSED_BIOMES_LIST_1` — modcheck builds a test list from the retired dev packageId for composed biomes (no closure, biome silently absent)
- `PYRELANDS_GREEN_MINIMAL_1` — Pyrelands north star GREEN on the pyrelands tier (pre-flight gates, 2-ring scratch sites, K-pooled census)
- `PYRELANDS_GREEN_FULL_1` — Pyrelands north star GREEN on the full list (fresh full-list mapgen on a scratch save, never quicktest)
- `PYRELANDS_SHIP_READINESS_1` — Pyrelands SHIPPED rung: Ashwallow/Emberscythe art, code review CLEAN, settings gate mechanics, composed deploy
- `STILLSAND_SUN_LIVE_VERIFY_1` — Live-verify Stillsand sun from latitude on quicktest maps at two latitudes: no night, shadow length by latitude, roof protects above 55 deg only, far-
- `FLOWWORKS_NORTHSTAR_TRIAL_1` — FlowWorks north-star trial: VALIDATED -> WIRED -> GREEN-minimal -> GREEN-full -> SHIPPED
- `FLOWWORKS_NORTHSTAR_WIRE_1` — FlowWorks north star WIRED: rewrite validation.py, every bar and toggle claimed
- `FLOWWORKS_NORTHSTAR_SITE_PREP_1` — FlowWorks trial site: golden save, manifest, preflight that refuses a dirty site
- `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` — FlowWorks trial: first live BASELINE run on the minimal tier, timed, verify recorded
- `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` — FlowWorks north star GREEN on the minimal tier
- `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` — FlowWorks north star GREEN on the full mod list
- `FLOWWORKS_NORTHSTAR_SHIP_1` — FlowWorks SHIPPED: settings superb, art complete, code review CLEAN, deployed
- `PITS_STALE_DEPLOY_COLLISION_1` — Stale mandrake.rm.pits active on the live list beside FlowWorks: 22 of 22 defNames collide
- `GRAFFITI_NORTHSTAR_TRIAL_1` — Graffiti north-star trial: pipeline pilot to first GREEN (parent of WIRED/GREEN_MINIMAL/GREEN_FULL/SHIP)
- `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1` — Graffiti: GREEN on MINIMAL+graffiti via fast driver, owner sheet review
- `GRAFFITI_NORTHSTAR_GREEN_FULL_1` — Graffiti: GREEN on the owner's FULL list (fresh launch, full-list driver mode)
- `GRAFFITI_NORTHSTAR_SHIP_1` — Graffiti: SHIPPED - art complete, settings superb, CLEAN, stamped, deployed
- `STILLSAND_CONTENT_LIVE_PROOF_1` — Prove the built Stillsand cast live (atlas, zuurrik on blood) and swap four placeholder renders
- `STILLSAND_EVENT_CREATURES_REMAINDER_1` — Stillsand event ladder remainder: sarlacc roots, krayt den quest, krayt horn, Debt weighting
- `STILLSAND_EVENT_CREATURES_LIVE_1` — Live-prove the krayt attack and muurrok on a Stillsand quicktest, and live-fire the Long Hunger
- `ABYSS_DARK_BUILD_1` — The Abyss: the Dark (real air, heat clears it), the Unveiling, ghorrumak storm call, strength slider
- `ABYSS_HIDDEN_SHIP_PROBES_1` — The Abyss: hidden-ship cover; probe droids still come and must be avoided
- `ABYSS_GHARREK_BUILD_1` — New creature gharrek, the gust-feeder (RM_Gharrek)
- `ABYSS_DURRGAK_BUILD_1` — New creature durrgak, the placer (RM_Durrgak)
- `ABYSS_KRIZZAK_BUILD_1` — New flying creature krizzak, the light-thief (RM_Krizzak)
- `ABYSS_ETCHCAP_BUILD_1` — New plant etchcap, the gourmet fungus (RM_Etchcap)
- `STILLSAND_PRECIOUS_CAVES_LIVE_1` — Precious caves: ten live Stillsand quicktest maps
- `STILLSAND_CAVE_AS_PLACE_1` — Stillsand cave: preservation, drip, biosilica walls, tribal mark
- `STILLSAND_CAVE_TIER_ROWS_1` — Precious cave rows: krayt den, sarlacc seep, debt cave
- `DEPLOYED_BIOME_REFS_ROTSPOREKIT_1` — selftest_deployed_biome_refs fails: 19 wildPlants/wildAnimals entries in deployed RUT_TheRot/RUT_Contagion/RUT_Miasma name defs absent because mandrak
- `STILLSAND_SAND_SIEVE_CHORE_1` — Stillsand sand sieve as a pawn chore: glass sand to fine sand with a carried sieve (feasible, no building)
- `STILLSAND_SOLAR_STILL_1` — Stillsand solar still and wringing still: sun-gated lens condenser distilling brine, wet organics and the dead
- `STILLSAND_SUN_LANCE_1` — Stillsand sun lance: heliostat mirror turret that heats and never ignites
- `STILLSAND_GEOPHONE_1` — Stillsand biosilica geophone: rumble markers from the sand-swim query
- `STILLSAND_GLASS_CHAIN_REMAINDER_1` — Stillsand glass chain remainder: krayt lens, goggles recipe, fulgurite art, art wire-in, live proof
- `STILLSAND_SUN_GOGGLES_ART_1` — Wire the sun goggles' own icon and worn art when it lands
- `STILLSAND_RETURN_REMAINDER_1` — Stillsand Return remainder: live proof, the visible Return line, cave debt stones, more water sources, stale stillsand MayRequire sweep
- `GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1` — JawaBench tools the Graffiti trial cannot fake: thing_graphic, spawn_variant, running_mods, glow_at, site_state
- `STILLSAND_SKELETONS_REMAINDER_1` — Stillsand skeletons remainder: tracks on the footprint grid + dune eraser, dune burial, skeleton/skull art wiring, giant bone yield, ribs shadow, gian
- `PYRELANDS_WALKLINT_FINDINGS_1` — run_selftests reports 3 walklint findings in design/validation_walks/RimMandrake/Pyrelands.md (found by STILLSAND_SKELETONS_TRACKS_1 full run 2026-10-
- `SHADEGRID_BRIDGE_READER_1` — Bridge tool to read the shade grid and pinned sun (sun elevation, heat kind, exposure per cell, sky glow)
- `STILLSAND_DUNE_GALE_LIVE_1` — Stillsand dune gale: live proof (mass delta, sun off, one emergence, carry letters, dust devil) + water skins, track-grid hook, hiss
- `CRACKEDLANDS_LEDGES_OF_MERCY_1` — Ledges of Mercy (from CRACKEDLANDS_GPT_ENRICHMENT_1 §1): refuge ledges, carvings, chime-line anchors, visitors+trained animals seek ledges at the warn
- `CRACKEDLANDS_FIVE_BEATS_AUDIO_1` — Bespoke audio for the five beats (6 SoundDefs on vanilla-clip placeholders) + the tarruq's call; owner: audio source
- `CRACKEDLANDS_THREE_HEIGHT_FLORA_1` — Qirra mats + talus clasps (names swept clean): art to review sheet before defs; owner: what 'pry cracks wider' does, harvests, veqma shade-line law
- `CRACKEDLANDS_SALVAGE_CLAIM_CREW_1` — Floodline salvage claim stakes + rival crew visitor lord (scatter already built); owner: RM scavenger faction, what negotiate offers, frequency
- `CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1` — Peakstorm Light: dust briefly reverses (no WeatherDef field; overlay vs mote event vs drop)
- `CRACKEDLANDS_ENRICHMENT_QUICKTEST_1` — Quicktest-prove the Cracked Lands enrichment tranche by state reads: five beats, peakstorm odds, recede feast cohort/migrants, salvage decay
- `CRACKEDLANDS_WOOLAMANDER_FLIGHT_1` — RSW_Woolamander is a ruled Cracked Lands flier-commuter but has no MaxFlightTime/canFlyIntoMap; owner: does it fly?
- `STILLSAND_FIXES_LIVE_PROOF_1` — Live proof for the five 2026-10-01 live-session fixes
- `CAULDRON_VENT_ENRICHMENT_HOOKS_1` — Cauldron enrichment pieces that hang on vents: weather vent multipliers + vent-local exposure + falter, vexxiss vent-drinking, vent-keyed gardens
- `CAULDRON_ENRICHMENT_AUDIO_1` — Cauldron enrichment sounds: vexxiss bellow, metal-tree harvest noise, directional vapour-bank hisses
- `CAULDRON_ENRICHMENT_VISUALS_1` — Cauldron enrichment visuals: dewfall chemical beads, dewfall plant saturation, assay flecks on old trees, vexxiss mineral-ringed footprints
- `VEXXITH_CLOSED_LOOP_BUILD_1` — Vexxith closed loop: acid immunity hook, plate-only recipes, poor-walls/weapons stance - three open questions
- `CAULDRON_ENRICHMENT_LIVE_PROOF_1` — Quicktest-prove the offline-built Cauldron enrichment: assay grade line, vexxiss poisoned-water letter, nettles on toxic shores
- `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` — Pitch further venomvine forms to the owner (he typed "Might need even more"); rule before any art
- `LEANINGSCRUB_SWEETLINE_GUARDIAN_1` — Sweetline tree guardian: what creature, dormant pawn or incident, what counts as harm
- `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1` — Sweetline tree naming register (current RM_NamerSweetlineTree vocabulary is a placeholder)
- `LEANINGSCRUB_SWEETLINE_VISITORS_1` — Sweetline travellers camp and pilgrims leave tokens: who, mapgen or incident, token def
- `LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1` — Shed vissler arms draw real scavengers: which species, food or lure job
- `LEANINGSCRUB_RUNWAY_BLOOM_VISUALS_1` — Runway bloom visuals: ribbonwhip sway and burrower exit holes (which species burrow?)
- `LEANINGSCRUB_ENRICHMENT_QUICKTEST_1` — Quicktest-prove dripping regrow, crown mob, runway bloom, named sweetline trees by state read
- `FORGE_ENRICHMENT_QUICKTEST_1` — Quicktest-prove the Forge enrichment tranche on a Forge map: keel brace fuel saving, spunstone reveal, phase voices, dhuvvox clock
- `FORGE_KEELWORK_REMAINDER_1` — Floatstone keelwork remainder: glassy ring at launch, brace art, and whether payload means substructure support
- `FORGE_SPUNSTONE_SOURCES_1` — Spunstone bonding remainder: foundry salvage as a study source, and what the high-speed doors and advanced structural parts are
- `FORGE_VOICES_AUDIO_1` — Bespoke audio for the four voices of the Forge (vanilla clips retinted as placeholders)
- `FORGE_WHITE_PLUME_FRONTS_1` — White plume fronts: moving quench-steam fronts that obscure shooters, soak ground, raise vanilla heatstroke; vapour-adapted exempt
- `FORGE_SKY_PASTURES_1` — Sky pastures: render the vapour-column grid, ash spirals, column-aware hunting and jossur stoops, flier-selected column highlight
- `FORGE_DHOKKUR_WAYS_1` — Dhokkur ways: outcrop disguise clues, rain-wake groan, path memory on glass-polished tracks, walls shoved not annihilated
- `FORGE_DHUVVOX_SWARM_REMAINDER_1` — Dhuvvox clock remainder: nodules as Things vs sealed pawns, swarm aggregation, slowing sound
- `LONGSHADE_MIDDENS_DESIGN_1` — Lee-side middens: owner to rule what a midden is, what searching yields, the clean-patch tell, the vrekka
- `SHADECRAFT_LESSONS_DESIGN_1` — Shade gear learned by study: lesson-to-piece mapping, and Long-Shade-only lessons vs the cross-biome gear ruling
- `GLOOMCAST_WAKE_RIDERS_1` — Gloomcast shadow: which small grazers actively follow it, and whether feeding leaves a scar distinct from dung
- `LONGSHADE_ENRICHMENT_QUICKTEST_1` — Quicktest the Long Shade enrichment: gloomcast moving shade, camera heat soundscape, Shipfall Commons, grove hum
- `RUST_CATHEDRAL_HUM_UNMAINTAINED_1` — Rust Cathedral hum PerTick sustainers never maintained: silent two ticks after start
- `SOORRAK_INSTANT_JOB_LOOP_1` — Wild soorrak sits in Wait_MaintainPosture forever: its next job succeeds instantly every cycle
- `LIVE_ROUND2_FIXES_PROOF_1` — Prove the three live-round-2 fixes in game (beam, soorrak loop log, rimplace stuff)

## Commits

```
7ba336b4d Ledger sync: FOUNDRY shard events held in the shared tree (bridge take/release, sap-sucker close) + closed item prose
6ffc5e609 Ledger sync: close RIMPLACE_STUFFLESS_THING_ROWS_1; note SOORRAK_INSTANT_JOB_LOOP_1
8e556c5b4 Ledger sync: close MUURROK_BEAM_NO_DAMAGE_1; file LIVE_ROUND2_FIXES_PROOF_1
a204c05b1 RIMPLACE_STUFFLESS_THING_ROWS_1: the plan loader supplies the default stuff
246950f7d SOORRAK_INSTANT_JOB_LOOP_1: log the job that ends the tick it starts
098afa66d Ledger sync: FOUNDRY claims three live-round-2 defects; progress skeleton
f591714e5 MUURROK_BEAM_NO_DAMAGE_1: the mirror beam casts from a job so its warmup survives
ace0863d3 FOUNDRY live session 2026-10-01 round 2: Stillsand live proofs, 3 defects filed
3d2cabb83 Ledger: close LONGSHADE_GPT_ENRICHMENT_1 at d4193b9e6; file its five follow-ups
d4193b9e6 LONGSHADE_GPT_ENRICHMENT_1 §1: Shipfall Commons; pirrik can ride the gloomcast again
4f306af5d LONGSHADE_GPT_ENRICHMENT_1 §3: heat you can hear, keyed to the camera
dd22747e3 Ledger sync: LONGSHADE_GPT_ENRICHMENT_1 claimed and started
24bf0e9b8 LONGSHADE_GPT_ENRICHMENT_1 §2: the gloomcast casts real moving shade
e72d2a79b Ledger: close FORGE_GPT_ENRICHMENT_1 at 774d5c764
3c30d28f5 Health artifacts regenerated by the selftest run
774d5c764 FORGE_GPT_ENRICHMENT_1: keel brace, spunstone study, four voices, dhuvvox clock
f11e435fd Ledger: close LEANINGSCRUB_GPT_ENRICHMENT_1 at 8e3d24e35
8e3d24e35 LEANINGSCRUB_GPT_ENRICHMENT_1: dripping regrow, crown Stall cloud, runway bloom, named sweetline trees
7caa6b5c9 Ledger: close the five 2026-10-01 live-session defects
7cb256f8d Ledger sync: FOUNDRY live-session fixes; file STILLSAND_FIXES_LIVE_PROOF_1
... 100 more: git log --oneline dcf56567a..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-01T10:57:55Z

Working tree clean apart from untracked `Transient/`.

