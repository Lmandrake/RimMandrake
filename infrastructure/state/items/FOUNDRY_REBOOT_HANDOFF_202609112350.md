# FOUNDRY_REBOOT_HANDOFF_202609112350 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609111128`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
<<< WRITE THIS >>>

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
<<< WRITE THIS >>>

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ART_REGEN_WAVE2_QUEUE_1` — <<< WRITE THIS >>>
- `LOCKJAW_ART_WIRE_IN_1` — <<< WRITE THIS >>>

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
<<< WRITE THIS >>>

## Closed since the last handoff (20)

- `BIOME_TEXT_PORT_1` — 441c4bf6c
- `ART_REGEN_WAVE1_WIRE_IN_1` — c2641b9d2
- `ART_REGEN_WAVE3_QUEUE_1` — 105c4746b27590c0e82ee0a94a849a214b80c4e3
- `PYRELANDS_FACING_COMPLETE_1` — 830202d99
- `ART_REGEN_REGISTRY_1` — a223c9568
- `ART_REGEN_WAVE2_WIRE_IN_1` — 21721c6a4
- `SHIP_VERMIN_MOD_1` — 565b9156f
- `SCENARIO_DURATION_CUT_1` — f490557ec
- `ART_REGEN_WAVE4_QUEUE_1` — 111b49013
- `SHOKK_RSW_MOD_1` — 19fbedbfb
- `GREENTIDE_STANDALONE_MOD_1` — c71fb0fbf
- `TIER_GRAMMAR_TEXT_FIXES_1` — e35831086
- `ART_REGEN_WAVE5_QUEUE_1` — 8bad11cae
- `DONOR_PROPER_NOUN_SCAN_1` — aaa0b45e1
- `ART_REGEN_WAVE4_WIRE_IN_1` — 8840fed2c
- `ABSORPTION_FIX_NEWLINE_ESCAPES_1` — d029308ef
- `DONOR_FACTION_PROPER_NOUN_RENAMES_1` — 8e1ea6c3d
- `ART_REGEN_WAVE6_QUEUE_1` — 8dd4378d5
- `STAGED_LORE_PROOF_SPIKE_1` — 6994d339c
- `ART_REGEN_WAVE7_QUEUE_1` — 51d28d4

## Filed and still open (3) — the next seat's queue

- `ART_REGEN_WAVE2_QUEUE_1` — Queue art regen for 4 more decided fauna redo rows from the 2026-09-10 sitting (wave 2)
- `ART_REGEN_WAVE4_SOURCE_DECISION_1` — Wave 4 art source: draw from the 338 art:improve rows, or rule on the 14 move rows?
- `JAWA_PHRASING_RSW_TIER_CARD_1` — Card: is Jawa-clan phrasing allowed at RSW tier, or must it stay RUT-only?

## Commits

```
3ccdaefd6 Ledger sync: resolve stash-pop conflict on events.jsonl (append-only, both sides kept)
a774199a2 Sync artpipe daemon state: waves 4-7 job files consumed, registry/throughput updated
f5f15319e Remove research/game_design — the corpus lives in GameDesignContent now
f2bfb4a4d BENCH handoff 202609111500: ~30 rulings landed+propagated, three text-voice laws in canon, Nine Voices corpus blessed, dungeon text corpus provisional, text-lore census closed, art-registry+hub designed
cbb558019 Close ART_REGEN_WAVE7_QUEUE_1 against 51d28d4
51d28d4ac Wave 7 art regen: 7 more art:improve creatures, canon-checked against star_wars_canon_names.md
57ed66205 Ledger: close STAGED_LORE_PROOF_SPIKE_1 against 6994d339c
6994d339c STAGED_LORE_PROOF_SPIKE_1: live proof that mandrake.rm.lorestages actually swaps text
22404bef0 Dungeon text corpus landed under the three-voice law: Assailant set AGREED (Cathedral reveal = owner verbatim), V6 + ring letters re-registered; remaining sittings enumerated
b80b14914 Code review round 4: mark 4 files CLEAN
6b397e6dd artreg.py: simplify target_spend's status ternary (round 4 code review)
9f7b1a7d2 Combined live verification: faction renames, lightsaber names confirmed; Norse FactionDef gap found
42816b723 Canon: three text-voice laws recorded (narrator butler-ghost diegetic register, game-fact voice with no atmosphere, Cathedral semi-lucid god-mind bursts) - owner verbatims 2026-09-11; god readouts marked register-superseded
5e7fb167b Close ART_REGEN_WAVE6_QUEUE_1 against 8dd4378d5
8dd4378d5 File wave 6 art:improve queue, canon-checked against the new reference doc
3291bcbd2 Fix lightsaber name generator: Final Fantasy VI -> genuine Star Wars names
0e681a6f3 METRICS: a rubric with real citations, and a widely-used instrument discredited
117aabadc SCIFI_DERELICT: Traveller's Twilight's Peak read in full, plus the SEARCH degradation cause
e72a5773a Add permanent Star Wars canon name reference, merged from local raid + Wookieepedia research
2b40a2506 Star Wars canon name list: local disk raid (owner ruling 2026-09-11)
8e1ea6c3d Draft 5 of 6 SW-canon renames for DONOR_FACTION_PROPER_NOUN_RENAMES_1
c4d078ed2 DUNGEON_DESIGN_RESEARCH_1: 8.8 MB of primary source text harvested
0ae680879 DUNGEON_DESIGN_RESEARCH_1: first seven domain findings from the fan-out
6cadd01c4 Cut Big and Small - Races (redmattis.bigsmall) via Cherry Picker: no SW canon fit
b20ff1f2e DUNGEON_SETPIECE_TEXT_1: V6 progress recorded, remaining sittings enumerated
d26dab8f3 V6 vault text drafted and owner-accepted-for-now (provisional, spec §3.10); narrator silent-god readouts parked as DRAFT awaiting bless
2d2284be5 Ledger: GOD_LINES_ORACLE_PACKS_1 closed at the blessed corpus
a0c0fafba Nine Voices v1 line corpus BLESSED: 54 unsigned pidgin lines, six slots per god, hook wiring notes; narrator stays impersonal alongside
d029308ef Fix 4 dead absorption content fixes: expected_old used real newlines, donor ships literal backslash-n
ba6779316 Add web-research half of canon Star Wars name list (creatures, factions, planets, minor characters)
0cac9e7de Code review round 3: mark CreatureBehaviors assembly + ShipVermin's Alert/patch CLEAN
31e9db1cd CreatureBehaviors: fix stale/inaccurate doc claims found in review round 3
8840fed2c ART_REGEN_WAVE4_WIRE_IN_1: record live verification result
9fa637b8e Wire ART_REGEN_WAVE4 art into 7 creatures: Ronto/Anooba/Dewback (SW-canon) + Grithe/Kroffa/Grutt/Puffmite (reimagined)
29365b030 STAGED_LORE_PROOF_SPIKE_1 filed: owner wants live proof before the build/no-build ruling
b298751a4 BESTIARY_ARMOURY_DESC_BACKFILL_1: patch the one residual placeholder wave 1 missed
294f2896f RSW tier goes Jawa-neutral per owner ruling: Reboot research + Karrask reworded; text lore report corrected (real backfill debt was 57, now closed)
5745a97c0 Correct the wave-1 count: 57 descriptions written (55 Armoury + 2 SWBestiary), 84 concrete defs resolved
b8da9f097 Description backfill wave 1: 55 placeholder/missing descriptions in RSW Armoury + SWBestiary
69c8e427b Close DONOR_PROPER_NOUN_SCAN_1
aaa0b45e1 DONOR_PROPER_NOUN_SCAN_1: instrumented donor-stack proper-noun scan, bounded rename backlog filed
cdbb3efdb Ledger sync: ART_REGEN_WAVE5_QUEUE_1 close event
8bad11cae ART_REGEN_WAVE5_QUEUE_1: queue 7 creatures from the art:improve pool
a57332414 Ledger: close TIER_GRAMMAR_TEXT_FIXES_1, file JAWA_PHRASING_RSW_TIER_CARD_1
e35831086 TIER_GRAMMAR_TEXT_FIXES_1: fix 3 confirmed tier-grammar text violations
ad591fd7a Confirm creaturebehaviors fix + capture full list with all 4 new mods
c9adc71a7 Closes: GREENTIDE_STANDALONE_MOD_1
c71fb0fbf loadsweep: add greentide_batch.txt for creaturebehaviors+greentide sweeps
b028b2685 Fix creaturebehaviors crash: RM_Alert_VerminPopulationBase was a reflection leaf
6b6321941 rimflow: close SHOKK_RSW_MOD_1
19fbedbfb Lesson: mandrake.rm.creaturebehaviors crashes every map-add path
9ab8b5f6c SHOKK_RSW_MOD_1: drop invalid tendAllowed field found by live load
b977b7598 Close ART_REGEN_WAVE4_QUEUE_1: jobs filed and daemon confirmed consuming
111b49013 ART_REGEN_WAVE4_QUEUE_1: queue 7 creatures from the art:improve pool
7ebffaa6b AA_Lockjaw2 (grey) south facing seeded and PASSED: LockjawArtOverride now complete
5f4e06222 Fix build break in shared CreatureBehaviors (RM_MapComponent_SilenceCue)
75115178c RSW_Mynock: reuse the existing regenerated Mynock art (IKEE_MYNOCK_ART_REGEN_1)
b3c042e5d Record owner's 'improve' art semantics ruling (2026-09-11)
9539d99aa Ledger: TEXT_LORE_LOAD_CENSUS_1 closed at the report commit (owner-said Fan out)
55c77ef69 Text lore load report: 38 engine surfaces, our-tier debt (1830-entry backfill, 3 tier violations), donor proper-noun backlog, locked-vs-deferred triage, 5 tickets filed
701ac7477 TEXT_LORE_LOAD_CENSUS_1 filed with owner rulings: full player-readable scope + tier-generic variants, frozen=locked triage, Oracle prompt packs in scope
1f360598e Greentide: use the terrain's own mireDecayPerTick when decaying RM_Mired
7112e7851 Ledger: MINDSTONE_LEGENDS_ENTRIES_1 closed (authoring done, wiring rides staged-lore/dungeon items)
a1d9050a2 Mindstone legends-sitting corrections propagated: Kindled never made (no in-world knowledge), Working Dead zombie droids, Sentinel surface = lost self-repairing strays (trickle feeds caches/vaults only), hard late-game knowledge gate
bdf80d545 GREENTIDE_STANDALONE_MOD_1: Greentide as its own RimMandrake-tier mod
08c3f3210 Mindstone arc legends: five entries authored with the owner (traveler register), scoping table, late-game Junkers gate, Sentinel self-repair correction banked
6a9fd46bf SHOKK_RSW_MOD_1: extract the Shokk into its own RimStarWars-tier mod
565b9156f SHIP_VERMIN_MOD_1: quicktest proof screenshot (mynock board/breed/gnaw live)
20cf6d921 SHIP_VERMIN_MOD_1 fix: patch file must sit under Patches/, not Defs/Patches/
21721c6a4 ART_REGEN_WAVE2_WIRE_IN_1: wire 4 creature art redos (Frostmite, Spidercat, Insectomorph, Megatardi)
1365f9bfa SHIP_VERMIN_MOD_1: ShipVermin mod + shared CreatureBehaviors assembly + RSW_Mynock species
9b60d0ed5 LOCKJAW_ART_WIRE_IN_1: wire and ship AA_Lockjaw3 (brown) improved art
77f9adf34 Ledger: FAUNA_GRAPHS_SITTING_1 closed, FAUNA_LORE_DIVERSIFICATION_1 filed
85f46ea6b Fauna graph sitting ruled from the owner's phone: K 12-15x all 326, tolerance = envelope +15C, products proportional now, size-first then FAUNA_LORE_DIVERSIFICATION_1
a223c9568 ART_REGEN_REGISTRY_1: artreg.py — sole writer of the art registry event log
830202d99 PYRELANDS_FACING_COMPLETE_1: fill in missing south/north facings for RUT_FireHawk and RUT_FurnaceBeast
ce31d8964 File ART_REGEN_WAVE4_SOURCE_DECISION_1: owner ruling needed on wave-4 art source
e524ae1e7 Close ART_REGEN_WAVE3_QUEUE_1: redo+in pool confirmed exhausted, no jobs filed
105c4746b File and block LOCKJAW_ART_WIRE_IN_1: finished art is east-only for 2 of 3 Lockjaw variants
70040f9ec Code review round 2: mark 3 RimStarWars C# files CLEAN
f490557ec Age-register pass: numeric durations out, era language in (owner ruling 2026-09-11)
fa9b341b1 Ledger sync: KIT_SPECS_CARD_SITTING_1 closed at cf0632c39; 5 items filed; BMT ruling + refreshed blocker recorded
cf0632c39 Card sitting 2026-09-11 propagated: all 30 owner rulings landed at their home docs
941b1f44a Art regen registry + dashboard hub designed and ruled: event ledger above the art queue (done=committed, retry cap 3, repurpose first-class), single multi-tab hub artifact with per-tab freshness
76f4e4e49 Ledger: close ART_REGEN_WAVE1_WIRE_IN_1
c2641b9d2 ART_REGEN_WAVE1_WIRE_IN_1: verify loose-PNG-over-AssetBundle override mechanism live
6507258d4 Close BIOME_TEXT_PORT_1
441c4bf6c Port campaign biome descriptions onto live donor BiomeDefs (BIOME_TEXT_PORT_1)
31ce86972 Mark weapon_affordability.py, weapon_pool_join.py, selftest_lore_stages.py CLEAN
61dd3f0e3 Fix duplicate-weapon overcount in weapon_affordability.py's per-kind tag join
1dfd4b36f ART_REGEN_WAVE1_WIRE_IN_1: wire 5 SW-canon creature art redos (Kreetle, Horax, Fambaa, Dragonsnake, Zakkeg)
6afca3f53 Handoff amendment: the uncommitted Armoury regens are from the failed-validate refresh run, deliberately left for a clean regen
0dda17232 BENCH handoff 202609110430: worldmap review complete (verdict YES), crash saga resolved, owner's morning stack staged
21b5fb52f Mechanoid origin canon drafted: mindstone race, Cathedral's children, wild cousins — 5 contradiction + 4 name cards await the owner
8287fb96b Queue hygiene: CANON_LORE_PROPAGATION_1 superseded by CANON_DRAIN_1 (gate now MET); MECHANOID_ORIGIN_CANON_1 claimed, design lane launched
22431bd39 Worldmap review COMPLETE (all 4 phases): FINAL verdict YES pending owner read; 4 plot leaks all donor residue, BIOME_TEXT_PORT_1 filed; scenario-duration nit carded
1abb083d0 Phase 2 STARE judged: YES hardens — river/road shape risk clears, all weaknesses S-cost polish; report addendum appended
999dc7a1e Phase 2 STARE capture: 30 world shots (18 global segments + 12 feature closeups) from the loaded canonical save, downscaled for the repo
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-11T22:50:28Z

Uncommitted (say for each whether it is yours or another seat's):

```
M design/Jawa/canon_reintegration_plan.md
 M design/Jawa/reconciled_lore/01_campaign.md
 M design/Jawa/reconciled_lore/02_world.md
 M design/Jawa/worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md
 M design/Jawa/worldbuilding/depths_concept.md
 M design/Jawa/worldbuilding/faction_world_spec.md
 M design/Jawa/worldbuilding/hydrology_and_fire_ecology.md
 M design/Jawa/worldbuilding/the_forgotten_war.md
 M design/Jawa/worldbuilding/tidally_locked_world.md
 M design/Jawa/worldbuilding/what_the_machines_are.md
 M design/Jawa/worldbuilding/worldgen_interactive_build_concepts.md
 M design/Jawa/worldbuilding/worldgen_interactive_def.md
 M infrastructure/state/items/BIOME_FREEZE_FABLE_REVIEW_1.md
M  src/RimStarWars/Armoury/Patches/Armour_Leather.xml
M  src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml
M  src/RimStarWars/Armoury/Patches/Armoury_TorpedoSpeed.xml
M  src/RimUtinni/ScavengerEvents/Assemblies/RimMandrake.Utinni.ScavengerEvents.dll
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
```

