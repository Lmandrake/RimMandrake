# BENCH_REBOOT_HANDOFF_202610021935 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610020812`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Five of the seven grandfathered biomes scored today had the same rot: creatures the owner ratified weeks ago were never built (their art is finished in artpipe and unwired), invented-name content sits in the campaign tier instead of the free `RM_` mod (Q11a), and campaign patches wholesale-Replace a free list or gate on a donor/frozen-twin def. Every remaining sitting (Weeping Stones, Gelatinous Slime, Miasma) must check all three before scoring; the owner wants these fixed biome by biome, never as a sweep.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Weeping Stones card is prepared but not yet asked** — review at `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\weepingstones_bedazzle_review_2026-10-02.md` §7. Top finding: the campaign Oasis patch adds Earth palms incl. the date palm he banned 2026-09-09.
2. **Git is healthy** — both clones level with origin, push guards installed as git-native hooks (`core.hooksPath=infrastructure/githooks`), auto-gc off in both clones; worktree pool code deleted.
3. **Ledger title drift**: `SUMP_SINKING_RITE_BUILD_1`'s filed title still says "Heat down"; its spec is correct (Heat untouched, next Imperial probe/raid pushed 5x). Titles are not editable by rimflow note.
4. **Owner rulings today worth knowing**: per-god rite cap raised to FIVE; Ozzik, Ohm, Zizzik at five; Ishko holds the Sinking.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `WEEPINGSTONES_SCORING_SITTING_1` — review, GPT consult and draft card committed; NEXT: re-read §0 to him and put the §7 card (build first / giant / new marks / rite) as question cards, then ticket out like the Fever Wood (`feverwood_bedazzle_review_2026-10-02.md` §8).
- `BEDAZZLE_TOP_SHAPE_PROGRAM_1` — track (a) at 7 of 12 done today+earlier (Webwork, Greentide, Rust Cathedral, Rot, Fever Wood closed); NEXT: after Weeping Stones, prepare Gelatinous Slime then Miasma with an Opus agent copying `feverwood_bedazzle_review_2026-10-02.md`'s shape.
- `NORTHSTAR pilot (no item yet)` — owner order: finish all bedazzle scoring sittings, THEN Northstar on IshkoDarkLandmarks per `design/RimMandrake/northstar_pilot_scoping_2026-10-02.md`; NEXT: when Miasma closes, file `NORTHSTAR_ISHKO_PILOT_1` from that doc's ordered steps.
- `GIT_WORKFLOW_MIGRATION_1` — pool/rescue bars removed with the pool code; NEXT: on 2026-10-05 measure manual rebases/day and Claude writes to D:\ for 3 days, record in the plan §4, close the item.
- `LONGSHADE_BEDAZZLE_CONTENT_1` — Part 8 ruled on the sheet; 8 revision art jobs queued (`longshade_revise_2026-10-02.csv`); NEXT: when `RM_Maidenbloom_b`/`RM_Tazzok_b`/`RM_Shadespire_b`/`RM_Skarrok_b` render, build a review sheet for him.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Concurrent subagent git reads take index.lock; a failed `./publish` commits none of its paths. (filed: lessons/20261002T193524Z-BENCH-background-subagents-running-read-only-git.md)
- Grandfathered biomes hide ratified-but-unbuilt creatures, campaign-tier invented content and wholesale-Replace patches. (filed: lessons/20261002T193524Z-BENCH-bedazzle-scoring-sittings-2026-10-02.md)
- Subagents mis-state rite gods (twice claimed the Sinking was unassigned); verify god/cap claims against the register before a card. (see: `design/Jawa/salvation_rites_2026-10-01.md` B14)

## Closed since the last handoff (7)

- `SUMP_BEDAZZLE_SITTING_1` — 58ae8dd57fa2
- `BEDAZZLE_FLORA_EXPANSION_1` — 054d01e7cf32
- `WEBWORK_SCORING_SITTING_1` — 74f4a9f53
- `GREENTIDE_SCORING_SITTING_1` — 298f6c262
- `RUSTCATHEDRAL_SCORING_SITTING_1` — 17de8c314
- `ROT_SCORING_SITTING_1` — 5f5cd1aab
- `FEVERWOOD_SCORING_SITTING_1` — 0700d1c41

## Filed and still open (45) — the next seat's queue

- `PROPERTY_CLAIM_ERASE_API_1` — RimProperty: ClearForeignClaims API, wipe other parties' stored claims on a Thing or in bulk (Sump Sinking rite)
- `SUMP_SINKING_RITE_BUILD_1` — Sump Rite A, the Sinking: one valuable into the tar; Heat down, fewer raids, claims wiped; beast-sleeps and trap-fizzle riders
- `SUMP_EFFIGY_RITE_BUILD_1` — Sump Rite B, Mob'Unloo's Price: good thing + hated effigy; Empire held off 5x on this map, faction's next group tarred
- `SUMP_SOLVENT_WAKE_BUILD_1` — Sump solvent wake: pour solvent on a tar bulge, the tar beast wakes instantly manhunter; feeds Sh'kaar and Zizzik
- `BLUEDESERT_FLORA_EXPANSION_BUILD_1` — Build 4 admitted Blue Desert flora: Qeshra, Kethevar, Vashpuk, Lisqueth (+ roe, char-lace items)
- `CRACKEDLANDS_FLORA_EXPANSION_BUILD_1` — Build 6 admitted Cracked Lands flora incl. Zennaq lightning-draw C# (RM_FloodedCanyon)
- `CAULDRON_FLORA_EXPANSION_BUILD_1` — Build 6 admitted Cauldron flora: Tsevrix, Ixalith, Fexxil, Sessarix, Kissaveth, Selvix
- `CRACKEDLANDS_PLANT_LIST_OWNED_1` — Cracked Lands owns its plant list: delete the campaign wholesale replace, move twisting thorns to RM_, drop 3 donor plants
- `WEBWORK_BASE_PORT_BUILD_1` — Webwork free tier: port anchor/web/gutter RUT_->RM_, wire the creeping front, free-tier thrixweave
- `WEBWORK_HEAT_SHADE_BUILD_1` — Webwork: declare overhead heat kind; ollathrix sun-scald reads the shade grid (tree shade)
- `WEBWORK_DEAD_GIANT_BUILD_1` — Webwork giant: wrapped urraveth skeleton, read bone by bone, loaded bones creak and collapse
- `WEBWORK_TRACTION_LANCE_BUILD_1` — Traction lance: capstan sibling on one shared pull, learnable at Webwork or Sump, fabric tether
- `WEBWORK_FELLED_NOON_RITE_1` — Rite: The Felled Noon for Sh'kaar (found in Webwork; fell tallest tree at noon, owners gather at shade line)
- `GREENTIDE_BASE_PORT_BUILD_1` — Greentide free tier gets Roil, Breaklight, wet-bulb, dry-air blower, root causeways and living greatbole (RUT_ to RM_)
- `GREENTIDE_FREE_ROSTER_OWNED_1` — Free Greentide owns its animal list: sulleth, dhollock, yammeth, RM_ swinger and fruit; campaign op 1 Replace deleted
- `GREENTIDE_THURROCK_HERD_BUILD_1` — The thurrock: tree-felling giant herd on the built Shatterer aura (no moult)
- `GREENTIDE_STELLOCK_LACE_BUILD_1` — Stellock lace: study a self-sealing branch, craft a cartridge that stops all bleeding on a pawn anywhere
- `GREENTIDE_CEDED_ROOM_RITE_1` — The Ceded Room, for Ozzik: cede a room built outside the ship to the jungle; scales with room quality
- `WARSCAR_OPEN_BOAST_RITE_1` — The Open Boast, for Ozzik, found in the Warscar: a public boast, a warned challenge raid, once per colony
- `RUSTCATHEDRAL_FREE_NAMES_TIDY_1` — Rust Cathedral free mod: rename 19 RUT_ defNames and two Utinni namespaces to RM_ (eel catch to RM_CoolantEelCatch)
- `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` — Rust Cathedral: line-cycle, hum reading, living coolant eels, overhead-sun heat, cooked strays, mynocks
- `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1` — Rust Cathedral giant: the borehulk, a colossal peaceful mining droid with a worn-out drill (three drill states)
- `RUSTCATHEDRAL_WORN_BIT_ARC_1` — The Worn Bit: unbolt the borehulk's drill, Junkers refurbish it, restore the giant; keep it to mine or free it
- `RUSTCATHEDRAL_HULL_BOLTS_BUILD_1` — Hull bolts: living bolts ride the ship for good as hull pets and the Cathedral's ears; reveal and dilemma
- `RUSTCATHEDRAL_MENDING_WELD_RITE_1` — The Mending Weld, for Rekko: rebuild a broken stretch of old structure into a whole room (Rust Cathedral rite)
- `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` — The Stranger's Overhaul, for Ohm: repair a free droid, capture it mid-repair or release it (Rust Cathedral rite)
- `ROT_RM_CAST_MIGRATION_1` — Move the ten ratified Rot creatures into the free mod as RM_ defs: hybrid descriptions, illoth flight, RSW_ rows retired
- `ROT_WOUND_SHARING_WIRING_1` — Wire wound-link and kin-mending onto the five Rot creatures whose descriptions promise it
- `ROT_SPORE_ALLERGY_PORT_1` — Our own spore allergy (people and animals) replaces the Alpha Biomes pair in the free Rot
- `ROT_MOD_SETTINGS_WIRING_1` — Make every control on the Rot's Mod Settings screen actually change the game
- `ROT_TIER_LEAKS_FIX_1` — Regate FungalSoilTrade from AB_MycoticJungle to RM_TheRot; take the Force off the free pale tree
- `ROT_HWELGRUE_GIANT_BUILD_1` — The hwelgrue: a huge slow maggot giant that eats whatever lies down and passes polished salvage castings
- `ROT_STILL_ALIVE_SWALLOW_1` — Still Alive In There: the hwelgrue swallows the downed; muffled knocking tells who is inside and how long
- `ROT_SWALLOWED_NAVIGATOR_1` — Swallowed Navigator: core pings the ship, log reveals salvage sites; extracted it boosts range; ship guns ruin it
- `ROT_GUT_MOTHER_VAT_1` — The Gut-Mother: a vat grown anywhere from the hwelgrue's sac returns implants and gear from corpses; starters trade
- `ROT_UNJOINING_DRAUGHT_1` — The Unjoining Draught: a brutal purge driving out parasites, symbionts and metalhorrors, anywhere
- `ROT_UNJOINING_RITE_1` — The Unjoining, for Ta'Baa: a symbiont-joined colonist purged until it dies, just before the clan leaves
- `FEVERWOOD_RM_CAST_COMPLETION_1` — Fever Wood: build the seven ratified creatures; the skreth brood as the free second front of the lure
- `FEVERWOOD_ANT_THEFT_RAIDBACK_1` — Fever Wood: kurreth carry thornbugs off alive; letter, track, column camp and hive raid-back
- `FEVERWOOD_CROWN_SOUND_HEAT_1` — Fever Wood: crown ambient sound for the sentinel hush to cut; heat kind ambient
- `FEVERWOOD_DIANOGA_GIANT_MAP_1` — Fever Wood campaign: map the dianoga over all six sekkulaath limbs, not just the tank
- `FEVERWOOD_TIER_LEAKS_FIX_1` — Fever Wood: donor-only patches (ancient danger, label, fish) onto RM_FeverWood; three Biomes! ports out of roster
- `FEVERWOOD_BROOD_RANSOM_1` — Fever Wood giant story: ransom of its young (world tally, release gift, young cask trade, Sporefall tank)
- `FEVERWOOD_OIL_BOIL_WEATHER_1` — Fever Wood weather: the oil boil (hot still days, doubled seep oil, spark flash fire wakes the deep)
- `WEEPINGSTONES_SCORING_SITTING_1` — Weeping Stones scoring sitting: nine-mark rescore, GPT five ideas, turn-1 card (prepared, not yet asked)

## Commits

```
d10bf6e4c Close FEVERWOOD_SCORING_SITTING_1 (follow-ups ruled); Sump's two rites added to the register (ticketed without rows); Weeping Stones review + GPT consult prepared
0700d1c41 Fever Wood turn-1 ticket-out: 7 FOUNDRY items, 3 art jobs; skreth 'not owner-ruled' line in FEVERWOOD_TWO_FRONT_LURE_TUNING_1 was false
c7db7658d Close ROT_SCORING_SITTING_1
5f5cd1aab Rot follow-ups written into specs, 9 hybrid redraw jobs; Fever Wood turn 1 ruled
50d447f5c Rot follow-ups ruled (hybrid art of our own creatures, unique drive core, percentage range, Contagion allergy); Fever Wood review + GPT consult
8ad17b944 Messy Conduit: Jawa as matte-black Star Wars variant (no white), load-proportional bundles (1-10 strands, Kirchhoff flow), owner-photo excursions with wall pile-up; design doc 8.10/8.11
71af11425 Rot turn-1 ticket-out: 11 FOUNDRY items, Unjoining in the register (Ta'Baa at four), 14 art jobs
c8d93370a ledger: Rot new marks ruled
5fa1be552 Rot new-marks redo: six pitches (two per mark)
cf908d22b Close RUSTCATHEDRAL_SCORING_SITTING_1
17de8c314 Freed borehulk answers favours, not orders; mynocks confirmed as Cathedral+Warscar migrants (cards 10:44)
9d12f11a3 Rust Cathedral turn-1 ticket-out: 7 FOUNDRY items, two rites in the register (Ohm at five), 14 art jobs; Rot turn-1 rulings
2a3096162 Messy Conduit phase 0: 12 style x messiness mock-ups, swatches, break strips; reusable procedural renderer + selftest
07d3f090e The Rot scoring sitting: review, GPT consult, draft card (Rite A is Ishko's, not unassigned)
b6c7d6383 ledger: file ROT_SCORING_SITTING_1
5dd5c9ed6 ledger: Rust Cathedral giant hook = The Worn Bit
d71c3933b Rust Cathedral mining-droid giant: five plot-hook pitches
c5b4e6311 ledger: Rust Cathedral turn 1 ruled
759ea51d7 Rust Cathedral scoring sitting: review, GPT consult, draft card (cap lines read at five)
df22fa2d4 Messy Conduit: overlay model assessment (owner idea): invisible conduit + cosmetic wire layer, break sparking, wires over walls; phase plan and risk register
... 68 more: git log --oneline 2c9f09707..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : UP  → corrected to DOWN, measured now
- Bridge: for     FlowWorks oscillation fix + Northstar v2 (owner: pause lifted, bridge his gift)

Working tree clean apart from untracked `Transient/`.

