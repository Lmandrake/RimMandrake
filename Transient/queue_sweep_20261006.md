# FOUNDRY PROPOSED sweep 2026-10-06 (read-only; no ledger writes) — COMPLETE: 138 rows. Totals: BLOCKED-LIVE 63, OPEN-OFFLINE 46, OWNER-GATED 22, BUILT 7, STALE 0.

Source: `rimflow queue FOUNDRY` PROPOSED section = 138 items (the separate BLOCKED section holds more "proposed (BLOCKED)" items; not swept).
Classes: BUILT / STALE / OWNER-GATED / BLOCKED-LIVE / OPEN-OFFLINE. Conf = confidence in the class (HIGH/MED/LOW).
Rites tabled: ledger note on SALVATION_RITES_UNIFICATION_1, 2026-10-03T22:34Z: "build order and re-review TABLED (typed): rites wait until the biome mod is fully complete and checked out; keep the item alive, blocked on a fully functional biome mod."
Key trap: many `needs: owner` items were RULED 2026-10-03 (question cards) -> they are OPEN-OFFLINE, not owner-gated.

| ID | class | conf | evidence / what remains |
|---|---|---|---|
| RAKATAN_ARCHOTECH_MACHINES_1 | OPEN-OFFLINE | MED | BENCH note 2026-10-04: "Open spec questions all answered"; spec f9478c297; probe `AncientMachine|RakatanRelic` in src finds only FlowWorks/cherrypick (no relic system). Build the relic/ancient-machine layers. |
| PIT_SUPERDEEP_COLLAPSE_1 | OPEN-OFFLINE | HIGH | Umbrella, design ruled; FOUNDRY note 2026-10-05 v2 promotion 5d5e6cc12; "Ladder ART still placeholder"; live bars remain. Not done. |
| DEEPS_FAUNA_MECHANICS_2 | BLOCKED-LIVE | HIGH | 477f1c132 "offline part done"; live proof of grabber/soulchime/drinker owed. |
| STATUE_ART_EXPANSION_1 | OPEN-OFFLINE | MED | Umbrella: ledger note "Close this umbrella when the children are done"; children UTINNI_STATUES_SKELETON/ART_WIRING/SHKAAR_FLAME_IDOL closed, FLAME_STATUES_MOD_BUILD_1 steps 4-5 landed (3a86952f5) but still open. Close umbrella when last child closes (flame fuel via Sump/Helixia not confirmed). |
| MINERALS_WHERE_THEY_BELONG_1 | OWNER-GATED | HIGH | BENCH note 2026-10-04: "per-biome CSV numbers need an owner review sheet before shipping"; sheet built 1424554b8, "no approvals". |
| WYYYSCHOKK_IDENTITY_COLLISION_1 | OPEN-OFFLINE | HIGH | Owner ruled 2026-10-03 (card): "retire the RSW_Wyyyschokk copy ... repoint the trophy recipe and tolerance patch". Probe `RSW_Wyyyschokk` still in 11 src files (TrophyCraft recipes, AnimalTolerances_Ashkarr.xml). Do the retire+repoint. |
| SURFACE_RIVER_WEIRS_1 | BUILT | MED | Slice 1 eab81a095 + slice 2 456d00ca2 "River Works slice 2 - bank works moved from TerminalBiomes; weir, levee, silt table, ferry" (new mod src/RimMandrake/RiverWorks). Offline only, numbers PROVISIONAL; live proof/deploy owed. Hopper/untended-weir clause unverified. |
| EMPIRE_ESCALATION_LADDER_1 | OPEN-OFFLINE | HIGH | Design 749d14425 + owner rulings 2026-10-03; probe `EscalationLadder|ProbeRung` 0 files in src (sanity: RM_Ollathrix 31 files). Not built. |
| LONGSHADE_SHADE_EXTRAS_1 | OWNER-GATED | HIGH | Owner deferred 2026-09-29 ("Will consider the rest later."); keep/cut sheet ed5641505 has no verdicts. |
| WATCHER_CREATURES_MOD_1 | OPEN-OFFLINE | HIGH | All four piinnok questions ruled 2026-10-03 (BENCH reassign "build per ...watcher_creatures_kit_design"); probe `WatcherKit|CompWatcher|RM_Watcher` 0 files; `Piinnok` only a comment in RM_CompSandSwim.cs. |
| PYRELANDS_NORTHSTAR_TRIAL_1 | BLOCKED-LIVE | HIGH | Parent of GREEN_MINIMAL/FULL/SHIP; live rungs. |
| NORTHSTAR_FAST_DRIVER_1 | BUILT | MED | src/RimMandrake/Utils/northstar_driver exists; GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1 note 2026-10-01: "First live driver run on graffiti_solo ... 723 calls, ~100 s"; FlowWorks v2 live GREEN 74P/0F 2026-10-05. Title's "live proof owed" is met; judge pass was the loose end. |
| PYRELANDS_GREEN_MINIMAL_1 | BLOCKED-LIVE | HIGH | 2026-10-01 note: gate A/B CLEAN, site 1 built; suite not GREEN. |
| PYRELANDS_GREEN_FULL_1 | BLOCKED-LIVE | HIGH | Depends on GREEN_MINIMAL_1; full-list live run. |
| PYRELANDS_SHIP_READINESS_1 | OPEN-OFFLINE | HIGH | Note 890e15602: "Remaining: Barbslinger item, code review CLEAN, settings gate, composed deploy. NEXT: full-file review of src/RimMandrake/Pyrelands/Source/*.cs." |
| STILLSAND_SUN_LIVE_VERIFY_1 | BLOCKED-LIVE | HIGH | "UNMEASURABLE by state read, SHADEGRID_BRIDGE_READER_1 unbuilt" (2026-10-01 round 2). |
| FLOWWORKS_NORTHSTAR_TRIAL_1 | OWNER-GATED | MED | Note 2026-10-05: minimal v2 live GREEN 74/0 -> PENDING-OWNER-REVIEW; GREEN_FULL not attempted. |
| FLOWWORKS_NORTHSTAR_BASELINE_RUN_1 | BLOCKED-LIVE | LOW | verify events db2f05c21 (2026-10-05), 8fb5106e8 (2026-10-06) recorded after the 10-01 block note; likely done by later runs but no close note read. Check before closing. |
| FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1 | OWNER-GATED | HIGH | "v2 LIVE GREEN 74P/0F/0 UNBUILT ... modcheck = PENDING-OWNER-REVIEW" (cf92c1716). |
| FLOWWORKS_NORTHSTAR_GREEN_FULL_1 | BLOCKED-LIVE | HIGH | Gated on GREEN_MINIMAL owner review; "no saved copy of the 639-mod full list exists". |
| FLOWWORKS_NORTHSTAR_SHIP_1 | BLOCKED-LIVE | MED | Chain tail behind GREEN_FULL. |
| GRAFFITI_NORTHSTAR_TRIAL_1 | BLOCKED-LIVE | HIGH | Parent; WIRED 541852456; hashed-section prose awaits owner re-validate. |
| GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1 | BLOCKED-LIVE | HIGH | First live run 10/10 state bars; visual bars not judged, owner sheet owed. |
| GRAFFITI_NORTHSTAR_GREEN_FULL_1 | BLOCKED-LIVE | HIGH | Full-list run behind MINIMAL. |
| GRAFFITI_NORTHSTAR_SHIP_1 | BLOCKED-LIVE | MED | Chain tail (needs deploy). |
| STILLSAND_CONTENT_LIVE_PROOF_1 | BLOCKED-LIVE | HIGH | Round-1 note: RM_Oorrik NRE, soorrak flight NRE (since fixed per FIXES_LIVE_PROOF round 2); content bars partly done, owner-eye art check outstanding. |
| STILLSAND_EVENT_CREATURES_LIVE_1 | BLOCKED-LIVE | HIGH | Round 2: Krayt/Muurrok fire; "(3) FAILED: beam accepted 4x in Clear". Not done. |
| STILLSAND_PRECIOUS_CAVES_LIVE_1 | BLOCKED-LIVE | HIGH | Round 2: 10/10 caves pass; only the "Rock island" letter BODY unread -> one bar left, nearly closable. |
| STILLSAND_RETURN_REMAINDER_1 | OPEN-OFFLINE | MED | Spec 5 DONE 8cb08ae09 (note 2026-10-03); other specs of the remainder unverified. |
| GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1 | BLOCKED-LIVE | MED | Spec = NEEDED_TOOLS in northstar_driver/site.py; needs JawaBench build+deploy with game down. |
| STILLSAND_SKELETONS_REMAINDER_1 | OPEN-OFFLINE | LOW | Filed only; no progress note. Not verified against src. |
| STILLSAND_DUNE_GALE_LIVE_1 | BLOCKED-LIVE | HIGH | Round 2: incident fires; "NOT proven: exposure ~0.2 (no ShadeGrid reader) ... carried pawns". |
| CRACKEDLANDS_LEDGES_OF_MERCY_1 | OPEN-OFFLINE | MED | FOUNDRY note 2026-10-04: numbers ruled, "ship first-guess numbers marked PROVISIONAL"; no ledge/refuge-anchor code in FloodedCanyon/Source (file list: CanyonFlood, RecedeAftermath, TarruqHushPatch...). Build ledges+carvings. |
| CRACKEDLANDS_FIVE_BEATS_AUDIO_1 | BLOCKED-LIVE | HIGH | Mechanism + tarruq call built 33222b7f3; FOUNDRY needs-note "Only live bars remain (tarruqSilenced state read; joint listen with owner)". Bespoke audio source still owner-side. |
| CRACKEDLANDS_THREE_HEIGHT_FLORA_1 | OWNER-GATED | MED | Spec: "art to an owner review sheet before any def ships"; probe `QirraMat|TalusClasp` 0 files (sanity: RM_Veqma exists per prose). |
| CRACKEDLANDS_SALVAGE_CLAIM_CREW_1 | OWNER-GATED | MED | Open owner questions (RM scavenger faction, negotiate offers, frequency); probe `ClaimStake|RivalCrew|SalvageCrew` 0 files; scatter already built in RM_MapComponent_RecedeAftermath. |
| CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1 | OWNER-GATED | MED | Prose: "One clause of the pick is still owed" (overlay vs mote vs drop), tagged needs: owner; no ruling note found. |
| CRACKEDLANDS_ENRICHMENT_QUICKTEST_1 | BLOCKED-LIVE | HIGH | Parent a222f3d36 verified only by build+selftests; "each quicktest-proven" owed here. |
| STILLSAND_FIXES_LIVE_PROOF_1 | BLOCKED-LIVE | HIGH | Round 2 note proved 1,2,4(0 NREs; filed SOORRAK_INSTANT_JOB_LOOP_1),5; "Only the letter wording keeps this open" (item 3 UNMEASURED). Nearly closable. |
| CAULDRON_ENRICHMENT_VISUALS_1 | OPEN-OFFLINE | MED | Owner rulings 2026-10-03 (dewfall green ban lifts; footprints persist ~1 day) -> "build per ...cauldron_enrichment_audio_visuals_spec_2026-10-02.md"; prose: art needed, none in artpipe at filing. Art-bound. |
| VEXXITH_CLOSED_LOOP_BUILD_1 | OPEN-OFFLINE | HIGH | "Item fully ruled" 2026-10-03; probe `Vexxith.*Door|AcidProof|AcidImmun` 0 files in src. Build acid patch, vessels, liners, scab-scrapers, acid-proof door. |
| CAULDRON_ENRICHMENT_LIVE_PROOF_1 | BLOCKED-LIVE | HIGH | Filed only; criteria are quicktest state reads. |
| LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1 | OPEN-OFFLINE | HIGH | Owner ruled 2026-10-03: build all six forms; probe `Hoard.*venom|VenomvineHoard` 0 files in src (Sworn hits are unrelated PawnFlavor backstories). Art for six owed. |
| LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1 | OPEN-OFFLINE | MED | Approved as drafted 2026-10-03; BENCH note "RM_NamerSweetlineTree is written but undeployed. NEXT: deploy with LeaningScrub." Def exists (RM_LeaningScrub_Namers.xml); only deploy remains. |
| LEANINGSCRUB_ENRICHMENT_QUICKTEST_1 | BLOCKED-LIVE | HIGH | Filed; state-read checks, "nothing has been proven live yet". |
| FORGE_ENRICHMENT_QUICKTEST_1 | BLOCKED-LIVE | HIGH | Parent 774d5c764; "nothing has loaded in a game". |
| FORGE_SPUNSTONE_SOURCES_1 | OPEN-OFFLINE | HIGH | Ruled 2026-10-03 (foundry salvage caches second source; floatstone door + structural parts); probe `Floatstone.*Door|FloatstoneDoor` 0 files; SpunstoneStudy exists (RM_FoundTechStudy.cs) so the source half may partly exist. |
| FORGE_DHOKKUR_WAYS_1 | OPEN-OFFLINE | LOW | Only "dormant graphic swap" built per prose; clues/groan/path memory owed; no ruling note on the owner questions found -> may be owner-gated. |
| LONGSHADE_MIDDENS_DESIGN_1 | OPEN-OFFLINE | MED | Ruled 2026-10-03 (regrowing heap, vanilla items, vrekka builds heaps); `Midden` in LongShade src only as a sound/comment hit; vrekka only in biome roster. Build. |
| SHADECRAFT_LESSONS_DESIGN_1 | OPEN-OFFLINE | HIGH | Ruled 2026-10-03; probe `ShadeLesson|ShadecraftLesson` only in modcheck required_checks.json, no defs. |
| GLOOMCAST_WAKE_RIDERS_1 | OPEN-OFFLINE | MED | Ruled 2026-10-03: tebbra and gennok follow gloomcast shadow; RM_ShadowFollowerExtension exists but RM_Tebbra/RM_Gennok in RM_LongShade_Fillers.xml do not carry it (only Dakkra/Pirrik do). |
| LONGSHADE_ENRICHMENT_QUICKTEST_1 | BLOCKED-LIVE | HIGH | Offline build 2026-10-01; quicktest owed. |
| LIVE_ROUND2_FIXES_PROOF_1 | BLOCKED-LIVE | MED | Needs deploy + Stillsand quicktest for beam/soorrak/rimplace fixes; note STILLSAND_FIXES round 2 already covered soorrak+rimplace, beam still unproven. |
| ABYSS_LIGHTFALL_BROOD_WRECK_1 | OPEN-OFFLINE | MED | Ruled by owner 2026-10-01 (brood, summing, wreck); spec/cast bible exist; build not seen. |
| NORTHSTAR_EVERYWHERE_PROGRAM_1 | BLOCKED-LIVE | HIGH | Program parent of the FIRST_SCRIPT children; scripts mostly built (validation.py for every child mod exists, checked), live runs owed. |
| ABYSS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/Abyss/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| CAULDRON_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/Cauldron/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| CONTAGION_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/Contagion/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| CREATURE_BEHAVIORS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/CreatureBehaviors/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| DIVING_INTERACTION_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/DivingInteraction/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| FEVER_WOOD_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/FeverWood/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| GELATINOUS_SLIME_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/GelatinousSlime/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| LEANING_SCRUB_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/LeaningScrub/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| MIASMA_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/Miasma/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| SCARLANDS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/Scarlands/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| STILLSAND_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/Stillsand/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| THE_FORGE_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/TheForge/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| WEEPING_STONES_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimMandrake/WeepingStones/validation.py (script BUILT, e.g. CAULDRON 995528e70 '42 components, never run live'); criteria require one recorded live run through northstar_driver. |
| FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/FungalSoilTrade/validation.py (script BUILT); live run owed per item criteria. |
| GREENTIDE_RAID_ANT_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/GreentideRaidAnt/validation.py (script BUILT); live run owed per item criteria. |
| KYBER_TRADE_PLOT_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/KyberTradePlot/validation.py (script BUILT); live run owed per item criteria. |
| PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/PropaneLakeMechanics/validation.py (script BUILT); live run owed per item criteria. |
| PYRELANDS_MECHANICS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/PyrelandsMechanics/validation.py (script BUILT); live run owed per item criteria. |
| RIVER_COLORS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/RiverColors/validation.py (script BUILT); live run owed per item criteria. |
| RUST_CATHEDRAL_ROACHES_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/RustCathedralRoaches/validation.py (script BUILT); live run owed per item criteria. |
| SCARLANDS_LADDER_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/ScarlandsLadder/validation.py (script BUILT); live run owed per item criteria. |
| SCAVENGER_EVENTS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/ScavengerEvents/validation.py (script BUILT); live run owed per item criteria. |
| SHIP_SHIELDS_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/ShipShields/validation.py (script BUILT); live run owed per item criteria. |
| SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/ShokkweaveEconomy/validation.py (script BUILT); live run owed per item criteria. |
| WILDSTEAM_EGG_BOUNTY_FIRST_SCRIPT_1 | BLOCKED-LIVE | MED | validation.py exists at src/RimUtinni/WildsteamEggBounty/validation.py (script BUILT); live run owed per item criteria. |
| NORTHSTAR_ADVERSARIAL_REVIEW_1 | OWNER-GATED | HIGH | Standing item; spec: "A standing item the owner triggers" (owner typed 2026-10-01 "I will periodically release adversarial agents"). |
| BIOME_TIER_CLEANUP_1 | OPEN-OFFLINE | HIGH | FOUNDRY note 2026-10-04: "(b) Fever Wood part DONE at b1948944c"; other biomes/parts of the three-part cleanup not reported done. |
| NORTHSTAR_SITUATIONAL_ROLLOUT_1 | BLOCKED-LIVE | HIGH | Note 2026-10-02: "12/14 suites measured ... abort path unproven live". |
| NORTHSTAR_COMPANION_GAPS_1 | BUILT | MED | Note 2026-10-02 "BUILT, not deployed: jawa/pawn_census, pawn_roles, incident_queue_peek/remove, damage_log, thing_lineage" in JawaBenchSituationalTools.cs, commit 88f41d25f. Deploy (build.py --gm with game down) + live proof owed. |
| GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1 | BLOCKED-LIVE | MED | Needs the Hutt test site live (offline half of the site is built, 186d24833); bridge test. |
| NINEFOLD_FAVOUR_ODDS_BUILD_1 | OWNER-GATED | HIGH | Rite build (Nine Faults/Left Behind) = tabled rites 2026-10-03; probe `NineFaults|FavourOdds|GodFavour` 0 files in src. |
| HUTT_SLAVE_PIT_TEST_SITE_1 | BLOCKED-LIVE | HIGH | FOUNDRY note 2026-10-04: "Offline half built 186d24833 (HUTT_SLAVE_PIT_SITE_BUILD_1): generic buyer pit in KeelHoist (RM_PitBuyer.cs ...)"; live run owed. |
| PYRELANDS_STRUCK_GLASS_RITE_BUILD_1 | OWNER-GATED | HIGH | Rite, tabled 2026-10-03; probe `StruckGlass|Struck_Glass` 0 files. |
| NORTHSTAR_VALIDATION_SKILL_1 | OPEN-OFFLINE | MED | FOUNDRY note: "skipped on purpose ... skills are edited only in fresh-context curation sessions" -> needs a curation session, not a builder pass. |
| SUMP_EFFIGY_RITE_BUILD_1 | OWNER-GATED | HIGH | Rite (Rite B, Mob'Unloo's Price), tabled 2026-10-03; no rite def in src (`MobUnloo|Effigy` hits are unrelated/other content). |
| EXCAVATION_WALL_ART_1 | OPEN-OFFLINE | HIGH | 2026-10-06 note: carrier built a26e3d875 (SectionLayer_RMExcavationWalls, procedural until textures land); art queued in artpipe, textures not landed. |
| WEBWORK_FELLED_NOON_RITE_1 | OWNER-GATED | HIGH | Rite, tabled; `FelledNoon` 0 files. |
| GREENTIDE_BASE_PORT_BUILD_1 | OPEN-OFFLINE | MED | Free tier needs Roil/Breaklight/wet-bulb/blower/causeways/greatbole as RM_; RM_Greentide src has Roil 6 files, Breaklight 1, Blower 1, Causeway 4, WetBulb 0 (full set still lives in UtinniPatches RUT_*). Partial/none; confirm before building. |
| GREENTIDE_CEDED_ROOM_RITE_1 | OWNER-GATED | HIGH | Rite, tabled; `CededRoom` 0 files. |
| WARSCAR_OPEN_BOAST_RITE_1 | OWNER-GATED | HIGH | Rite, tabled; `OpenBoast` 0 files. |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1 | OPEN-OFFLINE | MED | BENCH 2026-10-02 card confirms mynock wiring; src/RimMandrake/RustCathedral has `mynock` 0 files, `overhead` 0 files (line-cycle 1, coolant eel 7 present). Remaining pieces unbuilt. |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1 | OPEN-OFFLINE | MED | `HullBolt|HullPet` 0 files in src; ship-side realisation/Regard may be tabled with rites. |
| RUSTCATHEDRAL_WORN_BIT_ARC_1 | OPEN-OFFLINE | MED | Borehulk droid built separately (db013a05e RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1); drill-unbolt/refurbish/free-or-keep arc not found. Campaign wiring may ride the tabled rites. |
| RUSTCATHEDRAL_MENDING_WELD_RITE_1 | OWNER-GATED | HIGH | Rite, tabled; `MendingWeld` 0 files. |
| RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1 | OWNER-GATED | HIGH | Rite, tabled; `StrangersOverhaul` 0 files. |
| FEVERWOOD_BROOD_RANSOM_1 | OPEN-OFFLINE | MED | Card 2026-10-02 settled Sporefall tank access; no ransom mechanism in src (`BroodRansom` hits unrelated). Campaign tank piece may need the Sporefall map. |
| WEEPINGSTONES_CONDENSER_QUESTS_1 | OPEN-OFFLINE | MED | RM_WalkingCondenser.cs exists but no condenser quest scripts in src. |
| GELATINOUSSLIME_JOINING_WATER_RITE_1 | OWNER-GATED | HIGH | Rite, tabled, and its god is "Pomp, unresolved"; `JoiningWater` 0 files. |
| MIASMA_RECALL_WRITTEN_OFF_RITE_1 | OWNER-GATED | HIGH | Rite, tabled; `WrittenOff|Written-Off` 0 files. |
| NORTHSTAR_ISHKO_PILOT_1 | BLOCKED-LIVE | HIGH | Steps 1-4 done (mock GREEN 8/8, 1441e651b); "Step 6 is live and needs the bridge". |
| UTINNI_DISCOVERY_ACHIEVEMENTS_1 | OWNER-GATED | MED | Atlas framework built (b972b32cc; e9f896fbf "Atlas built; live run, owner eyes, art, lore sitting owed"); owner eyes/lore sitting pending. |
| WEEPINGSTONES_NET_FLEEING_FLIER_1 | BLOCKED-LIVE | LOW | No prose; bridge-tagged bug (NET job vs fleeing skarrin). Unverified. |
| FALL_LINE_MUTATOR_PLACEMENT_1 | BLOCKED-LIVE | LOW | No prose; bridge world_* edits on frozen world. Unverified whether done. |
| FEVERWOOD_HIVE_GUARD_CHAMBER_1 | OPEN-OFFLINE | MED | Prose: "build LAST, after a reacting hive is played"; hive reaction built (18668e795). Sequenced, not blocked. |
| UNFINISHED_LINE_TITHE_BEAT_1 | OPEN-OFFLINE | MED | Split from DROID_MASS_PRODUCTION_QUEST_CHAIN_1, owner rulings 2026-10-03; spine built (src/RimUtinni/UnfinishedLine exists), beat 4 not seen. |
| UNFINISHED_LINE_WORLD_FOUNDRY_1 | OPEN-OFFLINE | MED | Same parent; rulings 2026-10-03; Enclave regrowth/volunteer droids not verified in src. |
| WARSCAR_PILGRIM_CAMP_SITES_1 | OWNER-GATED | LOW | No prose; title: "needs the authored tiles along the Ashfall Road" (world authoring is the owner's). |
| SEABED_DESCENT_ASCENT_1 | BLOCKED-LIVE | MED | bridge-tagged flight to RM_SeabedLayer and back; ship-flight proof is live/with-owner. |
| FLOWWORKS_QUARRY_DIGGING_1 | OPEN-OFFLINE | HIGH | FOUNDRY note 2026-10-06: "FlowWorks half BUILT c858125a8"; the River Works half (sluice box + panning) and the mineral registry dependency remain. |
| NORTHSTAR_PARTIAL_GAPS_FILL_1 | OPEN-OFFLINE | HIGH | Standing item ("Standing item"); round-5 progress note 2026-10-04, 67 PARTIAL scripts, continues. |
| RUSTCATHEDRAL_GOODWILL_FLOOR_1 | BLOCKED-LIVE | LOW | Bridge-tagged finding about the hum band vs mechanoid goodwill; no fix read. |
| ARMOURY_PROJECTILE_DAMAGE_TOOL_1 | BUILT | MED | Note 2026-10-04: "Built f7a8a8602: jawa/projectile_damage ... NOT deployed" + chain ranged_ladder_landed; deploy+live assert owed. |
| ARMOURY_KOTOR_BOLT_GUARD_1 | BLOCKED-LIVE | HIGH | Needs-note: "offline half done ... only the live bar ranged_patch_damage_is_live remains (deploy Armoury ... reads 33)". |
| BELT_WATER_HARNESS_1 | BUILT | MED | a1b4b5943 "bland_world: paint_pond/restore_pond + SUITE_WATER (Miasma, Greentide) wired in the runner (BELT_WATER_HARNESS_1)"; live proof not read. |
| BLUEDESERT_FLORA_PLANT_REFUSAL_1 | BLOCKED-LIVE | HIGH | Note 2026-10-04: "Offline half done ... Tile.MinTemperature/MaxTemperature are lazy caches"; fix rides TILE_TEMP_CACHE_RESET_TOOL_1 + live retest. |
| DEEP_LAYER_BELT_HARNESS_1 | BLOCKED-LIVE | MED | 6c7ab2b36 "deep_proto.py: unproven route to a Lantern Deep pocket map". |
| TILE_TEMP_CACHE_RESET_TOOL_1 | OPEN-OFFLINE | MED | JawaBenchCacheTools.cs only audits caches (world_cache_audit, 216548f04); no reset tool found; then deploy. |
| SOLAR_MIRRORS_MOD_DESIGN_1 | OPEN-OFFLINE | HIGH | "Fully ruled 2026-10-04 (note): core + all four extensions"; probe `Heliostat` only RM_SunLance (Stillsand), no Solar Mirrors mod. Build. |
| JAWABENCH_DLL_STALE_REBUILD_1 | BLOCKED-LIVE | MED | Needs build.py --gm --apply with game DOWN (deployed DLL 2026-10-02 lacks 8 tools). Game currently UP. |
| FRAMERATE_DURING_NORMAL_PLAY_1 | OWNER-GATED | LOW | Owner-tagged observation; needs a play session with him / live measurement. |
| MESSYCONDUIT_CABLE_PILE_LOOK_1 | OPEN-OFFLINE | MED | Owner spec 2026-10-04 three rules; no completion note. |
| MESSYCONDUIT_STYLE_PER_BUILD_DESIGN_1 | OPEN-OFFLINE | MED | Owner decisions by card 2026-10-04 (architecture B, merge rule) recorded in messyconduit_style_per_build_design.md; build not seen. |
| GIMMESOMESLACK_NORTHSTAR_VALIDATE_1 | OWNER-GATED | HIGH | OWNER note 2026-10-06: "CONDITIONALLY ACCEPTED ... not validated; north star stays DRAFT"; 9 matrix FAILs untraced. |
| LEANINGSCRUB_SHEET_ART_REDO_1 | OPEN-OFFLINE | MED | Ingested owner decisions.json; wiring/variants/design asks outstanding. |
| RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1 | OPEN-OFFLINE | MED | Title: "no mechanism exists, design owed"; owner quote 2026-10-05. |
| FLOWWORKS_VISUAL_PRINCIPLES_1 | BUILT | LOW | FLOWWORKS_PIT_OCCUPANT_HIDDEN_BY_LIP_1 refers to the "DLL with visual principles 1-5" read in live shots 2026-10-06; wall carrier a26e3d875. Residual defects tracked separately. Verify before closing. |
| MYNOCK_FLIPBOOK_FRAMES_1 | OPEN-OFFLINE | MED | Art owed; find of `*mynock*flying*` under src/RimStarWars returned nothing. |
| FLOWWORKS_CHECKOUT_SCOPE_1 | OPEN-OFFLINE | HIGH | Filed 2026-10-06 from northstar review finding 7; walk edits owed. |
| FLOWWORKS_TANK_LOOP_ROW_WRONG_1 | OPEN-OFFLINE | MED | Row asserts a nonexistent mechanic; fix the row (bridge tag is for rerun only). |
| FLOWWORKS_CONFINEMENT_TOGGLE_VESTIGIAL_1 | OPEN-OFFLINE | MED | Probe `channelConfinementEnabled` still in Flood_FlowWorks.cs + settings (14 files); decide retire/rewire. |
| FLOWWORKS_PIT_OCCUPANT_HIDDEN_BY_LIP_1 | OPEN-OFFLINE | LOW | Owner-tagged draw-offset visual defect from live shots 2026-10-06. |
| FLOWWORKS_PIT_FALL_ONLY_FORCED_1 | OPEN-OFFLINE | MED | 790fd4e8d (11:49 PDT, after the 16:27Z filing) built colonist half: "colonists never path into an open pit ... only forced arrivals fall"; enemies-fall-if-concealed half unverified. |
| FLOWWORKS_SLUICE_TWO_DOORS_1 | BUILT | LOW | 6359e69b5 (2026-10-03) "FLOWWORKS_DOOR_FAMILY_1: stuffable sluice + security grate that pass liquid closed" predates the 2026-10-06 filing; filed from playtest finding #9, so may describe a gap not in the def. Verify in FlowWorks_Doors.xml. |
