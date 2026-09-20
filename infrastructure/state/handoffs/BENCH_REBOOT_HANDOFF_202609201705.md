# BENCH_REBOOT_HANDOFF_202609201705 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609192149`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 **Three separate defects found today share ONE shape: content that is correct
from inside the mod and wrong from inside the game.** Every one passed its own
item's `## verify`, because each verify checked its own artifact and none checked
what the player actually receives.

- `RUT_BlueDesert` — 1,029 tiles, zero fauna, zero flora. Its owner-ratified
  hydrocarbon biology was commissioned and never built (`BLUE_DESERT_LIFE_AUTHORING_1`).
- The Slime's gene machine — opens, works, hands the player **the wrong genes**.
  1 of 34 GeneDefs built; a universal placeholder archive ships in place of the
  owner's accepted list (`SLIME_GENE_ARCHIVE_BUILD_1`). Nothing errors.
- The Pyrelands — every mechanic built, onto `RM_FE_Pyrelands`, which carries
  **0 of 21,872 tiles** (`PYRELANDS_WRONG_BIOME_DEF_1`).

⇒ **When judging whether a biome is done, ask what the player's tiles carry — not
what the mod contains.** A sheet's Owed list is design intent, not a ledger item;
diff the two before believing anything is finished.

🔑 **And the corollary, which nearly cost a whole build:** a dead donor reference
does NOT mean the content is gone. 21 desert droids read as unportable — donor
absent from the mod list AND from disk — and were in fact **already ours**, absorbed
into Droidworks as `RSW_DW_OuterRim_*`. A one-line-per-entry repoint fixed all 21.
**Check whether we already own a port before concluding anything needs authoring.**
This repo absorbs donors routinely (`BMT_FAUNA_ABSORPTION_1`, `CAVERNS_PARITY_BUILD_1`,
Droidworks) and the absorbed def usually keeps a recognisable name.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- 🔴 **23 drafted creature names await his taste.** `check_pseudo_sw_name.py` proves
  they are coinages and do not collide with canon — it cannot prove they are GOOD.
  His first batch was rejected outright (23/23 were English compounds); the second
  batch is in the final assistant turn of this session and in `NONCANON_BEAST_RENAME_1`.
- 🔴 **Three real gameplay losses shipped deliberately, flagged.** The port dropped
  donor-framework comps per the standing rule, and three were mechanics, not flavour:
  **Ferroclaw** (ex-Terramorph) loses steel-eating; **Voltmaw** (ex-TetraSlug) and
  **Cindermite** (ex-Fuelmite) lose chemfuel ejection. Rebuilding them in our own C#
  is unfiled — his call.
- ⚠️ **13 unguarded `BMT_` plant references across 7 biomes may be a live mapgen
  defect, not a backlog.** `WYYYSCHOKK_FERALISK_MERGE_1` removed `AA_Dunealisk`
  because *"an unresolved cross-ref in wildAnimals is a known crash"*. These are the
  `wildPlants` equivalent. **Nobody has verified the two tables behave the same** —
  that check decides whether this is urgent. FOUNDRY holds it.
- ⚠️ **`RUT_ExtremeDesert` now has ONE wildPlant across 3,969 tiles** after
  `AB_GiantStikehr` was cut as misplaced (correctly — it is a Forsaken Crags
  mist-mushroom). Sparse is that sheet's intent; one species may be past it.
- ⚠️ **6 vanilla rows folded into the port** on his "replace everything", incl. plain
  `Rat`. Consistent with the desert cards' Earth-organism ban, but it is a bigger
  step than porting a donor and he approved it in one sentence, not row by row.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `DESERT_FAMILY_PORT_EXECUTION_1` — **91 of 102 species ported**, defs committed at
  `14f0ee419`, 251 art jobs filed, `validate_patch.py` clean. **NOT deployed, and the
  biome tables are NOT rewired** — they still name the donor defs.
  NEXT: land the art as the daemon clears it (review by eye — 4 of 61 Rot renders were
  bad and only an eye caught them), then rewire the three desert biome tables to the
  `RSW_` names and drop the `MayRequire`.
- `DONOR_DEFS_PORT_TO_OURS_1` — owner ruled **replace everything**; ~190 species beyond
  the desert are ruled but untouched. Three port sheets are frozen with all rows
  `replace` (`port_swac`, `port_alphaanimals`, `port_tail`).
  NEXT: run the same three-batch port shape against the SWAC sheet's 36 rows.
- `BMT_FLORA_ABSORPTION_1` — **FOUNDRY is working it.** My corrections are appended to
  the item (9 of 14 are Polluted Lands not Caverns; sources ARE vendored; 13 of 14
  unguarded). NEXT: leave it alone unless FOUNDRY asks.
- `NONCANON_BEAST_RENAME_1` — standard written and enforced; 23 names drafted, unruled.
  NEXT: get his verdict on the 23, then wire label+description together on each def.
- `DESERT_FAMILY_VERDICT_PASS_1` — superseded in practice by the blanket REPLACE ruling.
  NEXT: close it or fold it into `DESERT_FAMILY_PORT_EXECUTION_1`; do not re-serve its sheet.
- `BIOME_ROSTER_DEAD_SPECIES_REFS_1` — desert family now measures **0 dead refs**; the
  2 `BMT_GiantLeaf` rows remain. NEXT: build the lint (~20 lines, `run_selftests.py`)
  that fails when a roster entry names an inactive mod — that is the only part that
  stops this recurring.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- **A blanket ruling is not a sitting.** The owner ruled 4 sheets in single sentences;
  recording that as per-row clicks would forge `savedBy`. `apply_blanket_ruling.py`
  stamps `owner-blanket-ruling` and REFUSES to flatten a file a real sitting wrote.
  (see: `src/RimMandrake/Utils/apply_blanket_ruling.py`)
- **My own naming ear failed twice.** 23/23 drafts were English compounds. The fix was
  to measure the 37 coined canon creature names and make the shape checkable.
  (see: `src/RimMandrake/Utils/check_pseudo_sw_name.py`, `NONCANON_BEAST_RENAME_1`)
- **A prefix rule misreads the largest donor.** `mlie.starwarsanimalcollection` ships
  BARE defNames (`Bantha`, `Rat`, `Plant_TookeTrap_Wild`), so a census bucketed it as
  vanilla Core and reported the desert as "40 vanilla entries". Read `MayRequire`.
  (see: `infrastructure/state/facts/biome_rosters.md`)
- **Biome wild tables are ELEMENT-KEYED, not `<li>`-keyed.** A `<li>` parser returns
  zero rows for every biome — a failure that reads as a finding. Hit this exact way.
  (see: `infrastructure/state/facts/biome_rosters.md`)
- **Donor sources are vendored in-repo** at `vendor/mod_sources/` — `BiomesCaverns_src`,
  `BiomesPollutedLands`, `AlphaBiomes_src`, `StarWarsAnimalCollection_src`. Checking
  the Workshop folder and concluding "not on disk" is the wrong instrument.
  (filed: LESSONS_INBOX)
- **`measure find --type ThingDef <name>`** answers "does this def resolve live?" in a
  second; a `grep -rl` over the vendored tree timed out at 120 s. Use the dump.
  (see: `~/.claude/skills/measuring-large-artifacts`)

## Closed since the last handoff (6)

- `TEMP_TERRAIN_DLC_GATE_1` — bd7834ff8
- `MYCOID_COLOSSUS_ART_MISROUTE_1` — 1ea5c3f079442d8550d7adcf15846a01df6a4d8c
- `MYCOID_COLOSSUS_NORTH_RECOMPOSE_1` — 6d93614a0
- `DETERMINISTIC_CHECKER_WAVE_1` — 1ab5aed3bff54d3b676b19213e5e045b85b4c483
- `CAVERNS_PARITY_BUILD_1` — ad1ab9336
- `ROT_ART_WAVE_1` — 6144aac19

## Filed and still open (14) — the next seat's queue

- `GRASSLANDS_TILES_CSV_STALE_1` — ASHKARR_WORLDMAP_tiles.csv disagrees with GRASSLANDS_CAST_DEAD_BIOME_1's live measurement on Grasslands vs Pyrelands tile count
- `BAZAAR_STOLEN_GOODS_PROPERTY_1` — Stolen goods as a trade mechanic: RimProperty integration, the scanner registry, and the transponder reader
- `FALLZONE_LOST_CARGO_QUESTS_1` — Injected wreckage in the fall zone leads to quests about lost cargo of interest
- `WORLD_REMAKE_FINAL_STEP_1` — Remake the world from scratch as the LAST act before the official first play session - expected, not a failure; worldmap + gravship + founders are the
- `DESERT_FAMILY_VERDICT_PASS_1` — Desert family flora/fauna verdict pass (RUT_ExtremeDesert 3969 + RUT_Desert 2390 + RUT_BlueDesert 1029 = 7388 tiles, a third of the planet and where t
- `BLUE_DESERT_LIFE_AUTHORING_1` — Author the Blue Desert's commissioned hydrocarbon life - Swallowers, Burners, Pickers and the transparent fractal flora - 1029 tiles currently carryin
- `SLIME_GENE_ARCHIVE_BUILD_1` — Build the Slime's campaign gene archive: the owner-ACCEPTED 33-target + 25-rider lists (frozen 2026-09-06) exist as design only - 1 of 34 GeneDefs is 
- `PYRELANDS_WRONG_BIOME_DEF_1` — The Pyrelands content is wired to RM_FE_Pyrelands, which has ZERO tiles on the frozen world - the biome the player actually visits is ZBiome_Grassland
- `ROT_ROSTER_DEAD_DONOR_NAMES_1` — The Rot's fauna roster still names 17 BMT_ species from Biomes! Caverns, a donor mod NOT in the 621-mod active list - they can never spawn, so the ros
- `DONOR_DEFS_PORT_TO_OURS_1` — Port EVERY donor def we use to our own thing defs - owner ruling 2026-09-20; two mods (starwarsanimalcollection 160 entries, alphaanimals 102) carry 2
- `NONCANON_BEAST_RENAME_1` — Rename every non-canon beast to a pseudo-Star-Wars equivalent - owner ruling 2026-09-20; applies to donor creatures with Earth or generic names that s
- `BIOME_ROSTER_DEAD_SPECIES_REFS_1` — 23 species entries across 5 live biome defs name mods that are NOT in the active list - MayRequire-guarded so no crash, they simply never spawn; inclu
- `DESERT_FAMILY_PORT_EXECUTION_1` — Port all 109 desert-family species to our own defs and our own art - owner ruled every row REPLACE 2026-09-20; ~99 donor + 6 vanilla to re-author, 4 a
- `BMT_FLORA_ABSORPTION_1` — BMT_FAUNA_ABSORPTION_1 did fauna only - 14 Biomes! Caverns FLORA defs are still referenced across 8 biome tables with no RSW_ equivalent, from a mod a

## Commits

```
dd2d5c530 rimflow: sync ledger (desert port wave, naming standard, BMT flora findings)
d910bb274 NONCANON_BEAST_RENAME_1: make the pseudo-Star-Wars standard checkable
14f0ee419 DESERT_FAMILY_PORT_EXECUTION_1: port 91 desert species to our own RSW_ defs
68bddb37a BMT_FLORA_ABSORPTION_1: second instrument confirms the correction, exact packageIds
a1531df09 BMT_FLORA_ABSORPTION_1: three things I wrote in it were wrong - correcting for FOUNDRY
6274bc4af FOUNDRY reboot handoff 2026-09-20 1638
72ff0f807 File BMT_FLORA_ABSORPTION_1: the absorption did fauna only, 14 flora left stranded
ca49354b3 rimflow: sync ledger (BIOME_ROSTER_DEAD_SPECIES_REFS_1, DESERT_FAMILY_PORT_EXECUTION_1 filed)
5a0b0f5c0 Repoint 21 desert droids at our own Droidworks defs - they were never unportable
32d3d3803 Owner ruling: replace everything - all donor species become ours
11f43da58 Star Wars Animal Collection port sheet: the 36 species outside the desert family
38569e7d9 File DESERT_FAMILY_PORT_EXECUTION_1: owner ruled all 109 desert rows REPLACE
a4fae45c5 Fix 9 mis-cited DROIDWORKS_ item IDs in DROID_PROGRAM_STATE_2026-09-06.md
f022b2575 artpipe: re-channel 20 stranded pending jobs from gemini to codex
a00b4a524 Fix stale gate: BirthHatchDemo's extraction gate closed 2026-09-09
4b647e35a File BIOME_ROSTER_DEAD_SPECIES_REFS_1: 23 species that silently never spawn
ba1f239c2 STALE_GATE sweep (design/): fix 6 live-gate citations pointing at closed/dropped/superseded items
5db958dd8 STALE_GATE sweep (FOUNDRY, infrastructure/observed/world/src scope): fix 3 defects
8942782ae Fix stale gate citation in FISH_BESTIARY_BUILD_1: TWILIGHT_DEEP_WATER_LAYER_1 closed
85c8d3b22 rimflow: sync ledger (DONOR_DEFS_PORT_TO_OURS_1, NONCANON_BEAST_RENAME_1 filed)
... 179 more: git log --oneline 0ba047881..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-20T15:58:28Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   <-- code_review_status.py's health publisher — regenerates itself, not a seat's
MM Transient/codebase_health.json   <-- code_review_status.py's health publisher — regenerates itself, not a seat's
 M Transient/codebase_health_artifact.html   <-- code_review_status.py's health publisher — regenerates itself, not a seat's
 M deployed/config/ModsConfig.before-tier-pits.xml   <-- pre-existing at session start, not touched this wave
 M design/Jawa/mods/biome_flora.py   <-- FOUNDRY — live work on BMT_FLORA_ABSORPTION_1, mid-edit, leave alone
 M design/Jawa/worldbuilding/biomes/rosters/the_fever_wood.json   <-- FOUNDRY — live work on BMT_FLORA_ABSORPTION_1, mid-edit, leave alone
 M design/Jawa/worldbuilding/biomes/rosters/the_forge.json   <-- FOUNDRY — live work on BMT_FLORA_ABSORPTION_1, mid-edit, leave alone
 M design/Jawa/worldbuilding/biomes/rosters/the_greentide.json   <-- FOUNDRY — live work on BMT_FLORA_ABSORPTION_1, mid-edit, leave alone
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/nuitae_a_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/nuitae_b_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/yumbulbs_a_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/yumbulbs_b_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_dewback_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_grmolebear_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_kreetle_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_megatardi_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_orray_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_rutcathedralroach_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_rutscarroach_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/facingrepair_wyyyschokk_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_scratches_p1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_scratches_p2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_scratches_p3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_tally_p1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_tally_p2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_tally_p3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_0.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_4.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_vandal_regen_v1_5.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_warn_p1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/graffiti_warn_p2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 D infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
MM infrastructure/artpipe/registry.jsonl   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
MM infrastructure/artpipe/throughput.jsonl   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
 M infrastructure/dashboards/hub/data/health.json   <-- pre-existing at session start; BENCH did not write it this wave
 M infrastructure/state/CODE_REVIEW_STATUS.json   <-- pre-existing at session start; BENCH did not write it this wave
 M infrastructure/state/codebase_health_last.json   <-- code_review_status.py's health publisher — regenerates itself, not a seat's
D  infrastructure/state/items/DROID_TILES_SOURED_TERRAIN_1.md   <-- another seat's item churn (closures moved to items/closed/)
 D infrastructure/state/items/MYCOID_COLOSSUS_ART_MISROUTE_1.md   <-- another seat's item churn (closures moved to items/closed/)
D  infrastructure/state/items/RESEARCH_TRIO_RETIRE_1.md   <-- another seat's item churn (closures moved to items/closed/)
D  infrastructure/state/items/TWILIGHT_DEEP_WATER_LAYER_1.md   <-- another seat's item churn (closures moved to items/closed/)
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   <-- pre-existing at session start; BENCH did not write it this wave
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   <-- pre-existing at session start; BENCH did not write it this wave
?? deployed/config/ModsConfig.before-tier-bridge.xml   <-- pre-existing at session start, not touched this wave
?? deployed/config/ModsConfig.before-tier-diving.xml   <-- pre-existing at session start, not touched this wave
?? deployed/config/ModsConfig.before-tier-oracle.xml   <-- pre-existing at session start, not touched this wave
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   <-- pre-existing at session start, not touched this wave
?? deployed/config/ModsConfig.before-tier-visibility.xml   <-- pre-existing at session start, not touched this wave
?? deployed/config/ModsConfig.before-tier-warlab.xml   <-- pre-existing at session start, not touched this wave
?? infrastructure/artpipe/active/desert_swaca_bantha_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/barbslinger_redesign_v1_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/barbslinger_redesign_v1_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/barbslinger_redesign_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_gembug_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_gembug_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_gembug_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_gembug_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_gembug_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_gembug_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_glowbulb_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_glowbulb_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_glowbulb_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_grabber_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_grabber_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_grabber_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_grabber_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_grabber_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_grabber_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_megapleura_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_megapleura_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_megapleura_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_mossbeetlelarvae_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_shatterjaw_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_soulchime_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_soulchime_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/deeps_soulchime_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_anooba_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_anooba_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_anooba_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_anooba_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_anooba_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_anooba_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_bantha_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_bantha_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_bantha_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/desert_swaca_bantha_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_dewback_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_grmolebear_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_kreetle_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_megatardi_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_orray_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_rutcathedralroach_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_rutscarroach_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/facingrepair_wyyyschokk_v1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_scratches_p1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_scratches_p1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_scratches_p2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_scratches_p2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_scratches_p3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_scratches_p3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_tally_p1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_tally_p1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_tally_p2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_tally_p2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_tally_p3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_tally_p3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_0.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_4.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_vandal_regen_v1_5.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_warn_p1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_warn_p1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_warn_p2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/graffiti_warn_p2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_bolotaur_v3_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_fulgurite_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_fulgurite_v3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v3_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v3_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/offbiome_gualaar_v3_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_deep_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_heavy_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_light_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/pyrelands_ash_trace_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agarilux_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agariluxprime_v3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agariluxprime_v3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_arpeau_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_brightbell_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_bryolux_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_glowstool_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_greylady_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_greylady_v3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_greylady_v3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_nuitae_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_palemoss_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_paletree_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_paletree_v3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_paletree_v3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_recurvedstropharia_v3.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_sagecrust_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_sagecrust_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_shinecap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_shinecap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_skulltop_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_skulltop_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_slimypholiota_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_slimypholiota_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_swarmling_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_swarmling_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_swarmling_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_swarmling_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_swarmling_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_swarmling_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_violetwimple_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_violetwimple_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpawn_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpawn_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpawn_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpod_v2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpod_v2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpod_v2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpod_v2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpod_v2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wildpod_v2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_witchesoyster_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_witchesoyster_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wrinklecap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rot_wrinklecap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_agelesscap_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_agelesscap_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_falsefruit_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_falsefruit_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_1_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_1_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_1_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_2_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_2_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_2_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_3_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_3_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_3_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_4_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_4_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_4_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_5_east.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_5_north.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_firehawk_flying_5_south.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_furnacecap_plant_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_gene_furnaceblood_icon_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_grownfurnace_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_grownfurnace_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveingredient_agelesscap_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveingredient_euphoriccrown_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveingredient_regenerantveil_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_liveprep_toxicinjection_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_livingfurnacecap_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_palemoss_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_palemoss_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_paletree_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_paletree_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_regenerantveil_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_regenerantveil_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_mycoid_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_nightwake_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_quickflesh_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_symbiont_sheenblood_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_tea_agereversal_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_tea_bioregeneration_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/done/rut_tea_pleasure_v1.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Ashworm_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Ashworm_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Ashworm_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Barbthorn_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Barbthorn_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Barbthorn_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Cindermite_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Cindermite_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Cindermite_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Dunegrass.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Dunestalker_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Dunestalker_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Dunestalker_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_EmberCarpet.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandhorn_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandhorn_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandhorn_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandmaw_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandmaw_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandmaw_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandstrider_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandstrider_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sandstrider_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Scrubgrass.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Spinerat_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Spinerat_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Spinerat_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Spineroller_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Spineroller_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Spineroller_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sporemass_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sporemass_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sporemass_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sporepaw_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sporepaw_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Sporepaw_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Stareling_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Stareling_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Stareling_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Starvine.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Stoneback_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Stoneback_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Stoneback_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_SweetbarkTree.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_VellaraBloom.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Voltmaw_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Voltmaw_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Voltmaw_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/RSW_Whirlbloom.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_corinathoth_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_corinathoth_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_corinathoth_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_eopie_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_eopie_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_eopie_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_frilledgorg_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_frilledgorg_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_frilledgorg_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gizka_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gizka_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gizka_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gorg_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gorg_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gorg_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gutkurr_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gutkurr_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_gutkurr_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_hrumph_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_hrumph_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_hrumph_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_igitz_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_igitz_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_igitz_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_iriaz_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_iriaz_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_iriaz_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_iridonianreek_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_iridonianreek_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_iridonianreek_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_jamel_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_jamel_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_jamel_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_jimvu_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_jimvu_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_jimvu_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kreetle_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kreetle_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kreetle_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kwi_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kwi_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kwi_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kybuck_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kybuck_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_kybuck_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_longtailgorg_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_longtailgorg_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_longtailgorg_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_lothcat_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_lothcat_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_lothcat_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_massiff_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_massiff_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_massiff_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_mudhorn_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_mudhorn_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_mudhorn_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_mynock_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_mynock_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_mynock_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_nuna_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_nuna_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_nuna_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_pufferpig_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_pufferpig_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_pufferpig_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_ronto_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_ronto_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_ronto_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_scavrat_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_scavrat_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_scavrat_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_scurrier_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_scurrier_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_scurrier_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_shyrack_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_shyrack_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_shyrack_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_skalder_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_skalder_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_skalder_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_sketto_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_sketto_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_sketto_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_urusai_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_urusai_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_urusai_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_womprat_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_womprat_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_womprat_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_worrt_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_worrt_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_worrt_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_wraid_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_wraid_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desert_swaca_wraid_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_bolotaur_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_bolotaur_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_bolotaur_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_cannok_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_cannok_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_cannok_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_clodhopper_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_clodhopper_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_clodhopper_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_convor_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_convor_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_convor_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_falumpaset_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_falumpaset_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_falumpaset_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_feralgrazer_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_feralgrazer_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_feralgrazer_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_feralnerf_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_feralnerf_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_feralnerf_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_graniteslug_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_graniteslug_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_graniteslug_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_grank_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_grank_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_grank_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_horax_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_horax_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_horax_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_jakobeast_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_jakobeast_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_jakobeast_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_krykna_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_krykna_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_krykna_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_nerf_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_nerf_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_nerf_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_pikobis_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_pikobis_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_pikobis_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_plant_bloddle.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_porg_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_porg_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_porg_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_qormot_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_qormot_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_qormot_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_runyip_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_runyip_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_runyip_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_shaak_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_shaak_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_shaak_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_strill_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_strill_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_strill_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_teemuss_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_teemuss_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_teemuss_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_uvak_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_uvak_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_uvak_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_varactyl_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_varactyl_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_varactyl_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_voorpak_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_voorpak_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_voorpak_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_vulptex_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_vulptex_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_vulptex_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_warwyrm_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_warwyrm_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_warwyrm_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_whisperbird_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_whisperbird_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_whisperbird_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_zeer_east.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_zeer_north.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/artpipe/pending/desertportb_zeer_south.json   <-- artpipe daemon — NOT BENCH's; it runs continuously and owns this tree
?? infrastructure/state/.rimflow_conc_97j8px_9/   <-- pre-existing at session start; BENCH did not write it this wave
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   <-- pre-existing at session start, not touched this wave
?? src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_CavernsFlora.xml   <-- pre-existing at session start; BENCH did not write it this wave
?? src/RimUtinni/UtinniPatches/Textures/Things/Plant/FireLavender/   <-- pre-existing at session start; BENCH did not write it this wave
?? src/RimUtinni/UtinniPatches/Textures/Things/Plant/GiantLeaf/   <-- pre-existing at session start; BENCH did not write it this wave
?? src/RimUtinni/UtinniPatches/Textures/Things/Plant/HeatsinkFungus/   <-- pre-existing at session start; BENCH did not write it this wave
```

