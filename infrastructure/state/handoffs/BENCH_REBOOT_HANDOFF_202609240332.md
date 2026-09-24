# BENCH_REBOOT_HANDOFF_202609240332 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609210158`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 **Before authoring ANY liquid terrain, read FlowWorks' registry first**: `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidBodyDefs/RM_LiquidBodyRegistry.xml` and the `LIQUID_ROWS` table in `src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py`. The ManyWaters absorption is real and shipped: propane, brine, acid, tar, coolant, ichor and more each already have an `RM_<X>Shallow`/`RM_<X>Deep` suite with bottles and a body registration. A def builder this window authored `RUT_PropaneShallow` on top of the existing `RM_PropaneShallow`; the OWNER caught it, not the build. What actually blocked fishing was one word in that generator row (`waterBodyType None`, now `Saltwater`) — never hand-edit the generated `RM_<X>.xml`; edit the table and regenerate (it changed only the intended 2 lines this time; still diff after every run).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **`mandrake.rm.seashores` is NOT in his mod list and NOT live-proven.** Deployed to the Mods folder, not enabled. Enabling it (after Harmony) is his list; then a cold load and a map on a land tile beside the Scald or the Propane Lake proves the shore (`[RM_SeaShores] healed N tiles` log line, water on the map, a fishing zone accepted, a catch from the sea's own table). ~577 land tiles qualify by the 2026-09-12 RECORD, not the live planet.
- **UtinniPatches is NOT deployed** for any of this session's defs (19 catches, 2 rare tables, the propane recipe, four sea-def extensions): its deploy plan carries five other biome files with a peer's uncommitted drift (`RUT_AridShrubland/FeverWood/Greentide/Miasma/Webwork.xml`) and the tool has no per-file option. Someone deploys the whole mod knowingly.
- **Propane row flipped to `waterBodyType Saltwater`** on his card — `RM_PropaneShallow`/`RM_PropaneDeep` are now fishable and still non-potable. `waterBodyType` appears nowhere in `src/RimMandrake/FlowWorks/Source/`, so nothing in FlowWorks keyed on it being `None`.
- **Three no-fish rulings superseded on his word 2026-09-24** (Grey Sea, Propane Lake, "is fishing the right verb for fuel") — `design/Jawa/worldbuilding/sea_catch_rosters_2026-09-24.md` § Superseded rulings.
- **The quote-provenance guard refused his verbatim words twice** in a session opened by `/clear`; both rulings are recorded under BENCH quoting him (filed: LESSONS_INBOX).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `BIOME_MOD_SPLIT_EXECUTION_1` — inherited in `doing` from the 2026-09-23 BENCH sitting, untouched this window; all 22 child tickets carry MEASURED STATE, 21/24 wiring-ready, step 5 Desktop-only; NEXT: take the child tickets one biome per sitting with him, TERMINALBIOMES first (it now inherits this window's sea work), never a sweep.
- `SEA_FLOOR_AND_CATCH_PASS_1` — (a)–(c) built as `mandrake.rm.seashores` (`fb352d7c6`); all four catch tables built (Grey 7 / Twilight 10 / Propane 7 / Scald 8, `9f3ecb17f`+`2017bdc1b`); propane refinery bill `RUT_Make_ChemfuelFromPropaneCatch`; propane shore on FlowWorks' suite (`f392edb17`); NOTHING live-proven; NEXT: on his word enable `mandrake.rm.seashores` in the list, deploy UtinniPatches knowingly, cold load, generate a map beside the Scald and read the healer log line, then place a fishing zone — after that the floor animals (pairing rule: one swarm per shoal, one single per catch; 19 new species owe one each) and 34 catch icons (artpipe holds none; check `_artsrc/` again before queuing).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- The quote-provenance guard cannot see typed turns after `/clear`, and refuses any command whose TEXT merely contains the flag's name (filed: LESSONS_INBOX).
- `git add <deleted-path>` after `git rm` errors and kills an `&&` chain — put the deleted path on the `commit` pathspec only (filed: LESSONS_INBOX).
- A peer's `git pull --rebase --autostash` reverted a builder's in-progress edits twice mid-build; it waited and re-applied. With peers' dirty files in the tree, `git merge origin/main` tolerates unrelated dirty paths where `pull --rebase` refuses (see: CLAUDE.md > Git).
- `deploy_custom_mods.py` has no per-file option: a mod plan carrying a peer's drift cannot be deployed partially (filed: LESSONS_INBOX).
- A def builder reads the sea def and the donor terrain and never the liquid registry (see: the one thing above; filed: LESSONS_INBOX).

## Closed since the last handoff (3)

- `SLIME_STANDALONE_MOD_1` — 1197642c9
- `STONEBACK_DEFNAME_COLLISION_1` — 4b068ea5d
- `SKILL_SIZE_SPLIT_PASS_1` — adea63eab

## Filed and still open (49) — the next seat's queue

- `STILLSAND_RM_MOD_BUILD_1` — Phase A: build RM_Stillsand as its own RimMandrake mod (mandrake.rm.stillsand) — the Stillsand (extreme desert; campaign label "the Dune Sea" stays a 
- `LONGSHADE_RM_MOD_BUILD_1` — Phase A: build RM_LongShade as its own RimMandrake mod (mandrake.rm.longshade) — the Long Shade (the livable desert)
- `THEROT_RM_MOD_BUILD_1` — Phase A: build RM_TheRot as its own RimMandrake mod (mandrake.rm.therot) — the Rot - absorbs mandrake.rut.rotsporekit (151 files)
- `WASTELAND_RM_MOD_BUILD_1` — Phase A: build RM_Wasteland as its own RimMandrake mod (mandrake.rm.wasteland) — the Wasteland - owns the RUT_WastelandBrine terrain family
- `NIGHTSIDEICE_RM_MOD_BUILD_1` — Phase A: build RM_NightsideIce as its own RimMandrake mod (mandrake.rm.nightsideice) — the Nightside Ice - thin by design, but a Lantern Deeps host su
- `FORSAKENCRAGS_RM_MOD_BUILD_1` — Phase A: build RM_ForsakenCrags as its own RimMandrake mod (mandrake.rm.forsakencrags) — the Forsaken Crags
- `BLUEDESERT_RM_MOD_BUILD_1` — Phase A: build RM_BlueDesert as its own RimMandrake mod (mandrake.rm.bluedesert) — the Blue Desert - BLUE_DESERT_LIFE_AUTHORING_1 builds INTO this mod
- `LEANINGSCRUB_RM_MOD_BUILD_1` — Phase A: build RM_LeaningScrub as its own RimMandrake mod (mandrake.rm.leaningscrub) — the Leaning Scrub (was arid shrubland, a vanilla label)
- `POISONFOREST_RM_MOD_BUILD_1` — Phase A: build RM_PoisonForest as its own RimMandrake mod (mandrake.rm.poisonforest) — the Poison Forest
- `RUSTCATHEDRAL_RM_MOD_BUILD_1` — Phase A: build RM_RustCathedral as its own RimMandrake mod (mandrake.rm.rustcathedral) — the Rust Cathedral - absorbs rustcathedralhum/roaches/walls
- `GREENTIDE_RM_MOD_BUILD_1` — Phase A: build RM_Greentide as its own RimMandrake mod (mandrake.rm.greentide) — the Greentide - twin pair, mod EXISTS (123 vs 287 lines)
- `WEEPINGSTONES_RM_MOD_BUILD_1` — Phase A: build RM_WeepingStones as its own RimMandrake mod (mandrake.rm.weepingstones) — the Weeping Stones
- `PYRELANDS_RM_MOD_BUILD_1` — Phase A: build RM_Pyrelands as its own RimMandrake mod (mandrake.rm.pyrelands) — the Pyrelands - twin pair, mod EXISTS; defName rename done at 84d42c6
- `CONTAGION_RM_MOD_BUILD_1` — Phase A: build RM_Contagion as its own RimMandrake mod (mandrake.rm.contagion) — the Contagion
- `WEBWORK_RM_MOD_BUILD_1` — Phase A: build RM_Webwork as its own RimMandrake mod (mandrake.rm.webwork) — the Webwork
- `GELATINOUSSLIME_RM_MOD_BUILD_1` — Phase A: build RM_GelatinousSlime as its own RimMandrake mod (mandrake.rm.gelatinousslime) — the Slime - twin pair, mod EXISTS; TITANOSLIME_SLIME_BIOM
- `MIASMA_RM_MOD_BUILD_1` — Phase A: build RM_Miasma as its own RimMandrake mod (mandrake.rm.miasma) — the Miasma
- `THEFORGE_RM_MOD_BUILD_1` — Phase A: build RM_TheForge as its own RimMandrake mod (mandrake.rm.theforge) — the Forge
- `FEVERWOOD_RM_MOD_BUILD_1` — Phase A: build RM_FeverWood as its own RimMandrake mod (mandrake.rm.feverwood) — the Fever Wood
- `THESUMP_RM_MOD_BUILD_1` — Phase A: build RM_TheSump as its own RimMandrake mod (mandrake.rm.thesump) — the Sump
- `TERMINALBIOMES_RM_MOD_BUILD_1` — Phase A: build RM_TheScald/RM_PropaneLake/RM_TwilightSea/RM_GreySea as its own RimMandrake mod (mandrake.rm.terminalbiomes) — FOUR biomes in ONE mod, 
- `LANTERNDEEPS_RM_MOD_BUILD_1` — Phase A: build RM_LanternDeeps as its own RimMandrake mod (mandrake.rm.lanterndeeps) — the Lantern Deeps - an INJECTION layer, no RUT_ twin; skips Pha
- `ROSTER_DEAD_BMT_NAMES_SWEEP_1` — 14 ported-but-unwired BMT_ roster rows across 8 rosters: per-species wire-or-drop, never bulk-wire
- `BIOME_SPECIFIC_FAUNA_LAW_1` — 52 species are wired into more than one biome: adjudicate each against the biome-specific law's in-game-reason carve-out
- `KORRUM_ART_REGEN_1` — The korrum has no art of ours: texPath still points at Alpha Animals' own texture; 3 jobs re-keyed and quota-blocked to ~2026-09-26
- `STONEBACK_BOKKA_ART_STANDARD_1` — Judge the bokka's 2026-09-11 ported art against modern standards before regenerating (owner asked, did not order a regen)
- `SEA_FLOOR_AND_CATCH_PASS_1` — Every sea describes BOTH its floor (animals you meet by diving) and its catch (fish from the shore): the floor half is unbuilt across all four seas
- `SW_FAUNA_NEVER_IN_RM_TIER_1` — Route every Star Wars fauna row out of RM_-tier biome defs into the Utinni patch layer (97 rows, 12 biomes) — owner ruling Q11, taken by question card
- `GREENTIDE_RISK_REWARD_EXCHANGE_1` — The jungle is terrifying, and pays accordingly
- `GREENTIDE_GRENADE_WEAPONS_1` — Jungle grenades: stench, seeding and toxin
- `GREENTIDE_FRENZY_DISEASE_1` — The Frenzy - a disease you infect yourself with on purpose
- `CONTAGION_GENOME_ORGAN_GROWING_1` — Grow a colonist's organs inside a Contagion amoeba
- `FEVERWOOD_ANT_HIVE_DUNGEON_1` — Ant hives are reactive procedural dungeons
- `REACTION_MECHANISM_GENERALISE_1` — One reaction mechanism for four consumers: event object, shared budget, pluggable response, suppression
- `GREATBOLE_HARVEST_LADDER_1` — The greatbole harvest: 40/60/70 thresholds, the fruit's three products, and the grubs that contest it
- `FEVERWOOD_FLORA_ROSTER_1` — The Fever Wood gets 18 invented plants of its own, replacing 7 donor placeholders
- `FEVERWOOD_BOUGH_SOIL_TERRAIN_1` — The crown cannot grow anything: boughway is fertility 0, so bough-soil is owed
- `FEVERWOOD_TENTACLE_BESTIARY_1` — Six tentacle types, the drive-off ladder, and a severed limb you can harvest
- `FEVERWOOD_SAP_SUCKER_GUILD_1` — Three sap-suckers, three defences, and the host plant that feeds them
- `FEVERWOOD_ALIEN_BIRD_CHORUS_1` — Alien birds whose chorus falls silent only for the water, and some of them steal
- `FEVERWOOD_TWO_FRONT_LURE_1` — Staked living bait, and two raiders who arrive one after the other
- `FEVERWOOD_DIANOGA_PRISON_1` — A prison tank, not a pen: it teaches, it produces, and it can get out
- `GREENTIDE_TERROR_REPLACEMENT_1` — Something new and terrifying for the Greentide, replacing the dianoga
- `MIASMA_FLORA_ROSTER_1` — 19 invented Miasma plants: the rainbow blooms, our own mangals, and a carnivorous clade
- `MIASMA_FAUNA_FLOOR_ROSTER_1` — The Miasma arthropod floor, the fever-swarm, and the stranded as a condition
- `MLIE_ABSORPTION_BIOME_WIRING_1` — 98 live biome rows still name the bare donor for 73 creatures we already ported
- `SEA_BEASTS_TIER_RULING_1` — 11 of the 18 sea beasts are invented originals filed as Star Wars IP
- `STARWARS_DONOR_PORT_LABEL_COLLISIONS_1` — label_collision_check.py finds 62 label collisions between donor SW-animal-collection defNames and their RSW_ ports, both simultaneously cast -- DUPLI
- `WARDEN_MOTHER_BEFRIENDING_1` — The warden mother: lumbers in water, cannot reach land, befriended by freeing the young she cannot

## Commits

```
84aa218ff Ledger sync: SEA_FLOOR_AND_CATCH_PASS_1 propane-suite note; two lessons filed
f392edb17 SEA_FLOOR_AND_CATCH_PASS_1: propane shore uses FlowWorks propane suite; duplicate RUT_PropaneShallow deleted (owner card)
fdd63cb72 Merge remote-tracking branch 'origin/main'
f9dca8846 Ledger sync: SEA_FLOOR_AND_CATCH_PASS_1 card answers note
d5acd7993 SEA_FLOOR_AND_CATCH_PASS_1: propane catch refinery bill (owner card), three card answers recorded
efd136422 Handoff: correct a reference to a commit the rebase skipped
32860682b Handoff: four times this sitting the answer was already built
8aafd8c8e FOUNDRY handoff 202609240213: wave summary, traps filed to LESSONS_INBOX
2017bdc1b SEA_FLOOR_AND_CATCH_PASS_1: remaining sea catch table edits (Twilight/Scald items+rare tables, Grey/Propane biome comments)
e09117c76 chore: health publisher artifacts regenerated (unblocks rebase, final)
766176ee0 Ledger/state sync: finish QUICKTEST_RIVER_WATER_MISSING_1 close-move, sync LESSONS_INBOX
9f3ecb17f SEA_FLOOR_AND_CATCH_PASS_1: four seas' catch tables built — 19 new catches, 2 new rare tables, RUT_PropaneShallow
449188bd9 SEA_FLOOR_AND_CATCH_PASS_1: sea catch rosters — four seas, seven-plus catches each (owner brief 2026-09-24)
497b0efed Connection to the sea is the gate, and that predicate shipped nine days ago
fa4e3358a No ships to sink, no time to grow up, and canals make her reach the player's
8e666ea10 She dies of age, and the young she could not reach inherit her
e3fb906aa chore: health publisher artifacts regenerated
435553401 The warden mother cannot reach her own young, and that is the whole mechanism
c29c8cec9 Bridge release: batch live-verify pass complete (items 1-8 + 11 real work, item 10 partial, item 9 untouched -- needs a multi-restart bisection out of scope for this session).
5c1aa709d MOD_OPTIONS_RETROFIT_1: live spot-check of 8 mods' Mod Settings (all 3 tiers) via jawa/mod_settings_field -- all 8 resolve cleanly, 5 round-trip toggle-verified. Real evidence the retrofit's settings layer is sound; not a full 46-mod census.
... 270 more: git log --oneline 623675abc..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T01:17:37Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   the health publisher — auto-regenerated on every rimflow/code_review_status call, not a seat's
 M Transient/codebase_health.json   the health publisher — auto-regenerated on every rimflow/code_review_status call, not a seat's
 M Transient/codebase_health_artifact.html   the health publisher — auto-regenerated on every rimflow/code_review_status call, not a seat's
 D infrastructure/artpipe/pending/RSW_Cindermite_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Cindermite_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Cindermite_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Dunegrass.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Dunestalker_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Dunestalker_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Dunestalker_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandhorn_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandhorn_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandhorn_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandmaw_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandmaw_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandmaw_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandstrider_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandstrider_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Sandstrider_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Spineroller_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Spineroller_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Spineroller_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Stareling_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Stareling_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Stareling_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_SweetbarkTree.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_VellaraBloom.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Voltmaw_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Voltmaw_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/RSW_Voltmaw_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 D infrastructure/artpipe/pending/rm_greatbole_v1.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 M infrastructure/artpipe/registry.jsonl   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 M infrastructure/artpipe/throughput.jsonl   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
 M infrastructure/dashboards/hub/data/health.json   the health publisher — auto-regenerated on every rimflow/code_review_status call, not a seat's
 M infrastructure/state/codebase_health_last.json   the health publisher — auto-regenerated on every rimflow/code_review_status call, not a seat's
 M infrastructure/state/queue/BENCH.md   rimflow render output, regenerated by every ledger write — not a seat's
 M infrastructure/state/queue/FOUNDRY.md   rimflow render output, regenerated by every ledger write — not a seat's
 M src/RimMandrake/Utils/codebase_health_publish.py   the health publisher — auto-regenerated on every rimflow/code_review_status call, not a seat's
?? infrastructure/artpipe/active/canon_shiro_v1_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/daemon_run_20260923_owner_100pct.log   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Cindermite_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Cindermite_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Cindermite_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Cindermite_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Cindermite_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Cindermite_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunegrass.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunegrass.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunestalker_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunestalker_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunestalker_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunestalker_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunestalker_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Dunestalker_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandhorn_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandhorn_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandhorn_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandhorn_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandhorn_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandhorn_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandmaw_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandmaw_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandmaw_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandmaw_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandmaw_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandmaw_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandstrider_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandstrider_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandstrider_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandstrider_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandstrider_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Sandstrider_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Spineroller_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Spineroller_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Spineroller_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Spineroller_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Spineroller_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Spineroller_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Stareling_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Stareling_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Stareling_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Stareling_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Stareling_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Stareling_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_SweetbarkTree.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_SweetbarkTree.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_VellaraBloom.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_VellaraBloom.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Voltmaw_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Voltmaw_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Voltmaw_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Voltmaw_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Voltmaw_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/RSW_Voltmaw_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_boma_v1_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_boma_v1_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_boma_v1_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_boma_v1_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_boma_v1_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_boma_v1_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_dewback_v1_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_dewback_v1_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_dewback_v1_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_dewback_v1_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_insectomorph_v1_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_insectomorph_v1_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_insectomorph_v1_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/canon_insectomorph_v1_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_convor_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_convor_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_falumpaset_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_falumpaset_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_falumpaset_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_falumpaset_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_falumpaset_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_falumpaset_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralnerf_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralnerf_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralnerf_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_graniteslug_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_graniteslug_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_graniteslug_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_grank_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_grank_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_grank_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_grank_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_grank_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_grank_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_horax_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_horax_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_horax_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_horax_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_horax_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_horax_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_jakobeast_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_jakobeast_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_jakobeast_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_krykna_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_krykna_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_krykna_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_nerf_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_nerf_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_nerf_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_pikobis_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_pikobis_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_pikobis_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_plant_bloddle.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/rm_greatbole_v1.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/done/rm_greatbole_v1.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/RSW_Voltmaw_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/RSW_Voltmaw_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_krissek_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_krissek_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_krissek_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_krissek_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_krissek_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_krissek_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/canon_dewback_v1_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/canon_dewback_v1_south.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.manifest.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_shiro_v1_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_shiro_v1_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_vornskyr_v1_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_vornskyr_v1_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_vornskyr_v1_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_whisperbird_v1_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_whisperbird_v1_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_whisperbird_v1_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_zakkeg_v1_east.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_zakkeg_v1_north.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/artpipe/pending/canon_zakkeg_v1_south.json   the artpipe daemon (continuous; done/pending/failed/active/registry/throughput/log are its own) — not a seat's, left untouched
?? infrastructure/state/.rimflow_conc_97j8px_9/   another window's rimflow concurrency lock — left untouched deliberately
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   another window (2026-09-11 preswap backup) — left untouched deliberately
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   FOUNDRY — mod-list backups from its quicktest/cold-load batches, left untouched
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   FOUNDRY — mod-list backups from its quicktest/cold-load batches, left untouched
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   FOUNDRY — mod-list backups from its quicktest/cold-load batches, left untouched
```

