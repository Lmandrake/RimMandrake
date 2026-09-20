# BENCH_REBOOT_HANDOFF_202609202015 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609201705`. Everything below is committed and pushed.
**Game and bridge state is the last section — read it before touching the game.**

## The one thing to carry forward

🔴 **Four instruments lied with confident numbers today, and every one failed in the
direction that costs work.** This is the session's whole shape.

- `_def_bindings_2026-09-09.md` — **25 of 29 rows** named a biome def with ZERO
  painted tiles. It is the table an agent consults to pick an owning BiomeDef, so it
  is *how* `PYRELANDS_WRONG_BIOME_DEF_1` happens. Regenerated, 27 rows, closed.
- `_validate.py`'s hardcoded `PAINTED_DEFS` — **19 red errors, 19 of 19 FALSE**,
  every one naming a live painted biome. Now derived from the world CSV.
- `plant_pool.csv` (Aug 23) + `creature_register_rows.json` (Sep 5) — **38 more red
  errors, 0 of 38 real.** ~90% of that validator's output was noise, which is what
  made its 5 genuine errors invisible.
- A flora art audit reported **"3 already done, 141 owed"** and asserted no donor
  prefixes existed in the set. 115 of 148 carry one. Re-measured: **96 done, 37
  owed.** Filing the full set would have regenerated 96 existing renders.

🔑 **And three of my OWN queries lied the same way** — a batched SQL `IN`-list said 12
defs were absent from the dump (per-name check: 0), and two `comps`/`get_def` filters
reported 0/16 and "comp discarded" when the raw call showed `"success": true`.

⇒ **When a count is round, alarming, or convenient, check ONE case by hand before
believing it.** Every wrong number today would have read as a finding.

## What the owner should see

- 🔴 **The founders are not in the repo.** Of the three artifacts ruled to survive the
  world remake, the worldmap and gravship are committed; the **founders exist only
  inside `CANONICAL_ASHKARR_START_2026-09-12.rws`** in the Steam-Cloud Saves folder.
  `CharacterEditor/` holds no presets. A founder scrub ran 2026-09-20 — active
  editing, no repo copy. `FOUNDERS_EXPORT_TO_REPO_1`.
- ⚠️ **He ruled two deliberate "errors" IN, and both will be found again by a sweep.**
  `Gungan` keeps `poor intellectual` (*"half joke and half rebuke"* of the films), and
  the Fall Line `Rat` stays as a white-lab-rat-from-a-wreck joke. Both violate rules
  their own sheets enforce. **Do not let a correctness pass clean either up.**
- ⚠️ **37 flora art jobs are owed but 20 of them are `BMT_Plant_*`** — exactly
  FOUNDRY's live `BMT_FLORA_ABSORPTION_1` scope. BENCH recommended holding those 20
  and filing the other 17; **he has not answered that.**
- ⚠️ **Six flora moves were left unapplied** — three source FOUNDRY-locked
  `the_forge.json`, and two of those have a *measured-false* mapped target and need a
  real destination named rather than guessed.

## What is half-done, and where it stops

- `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1` — mitigated, not finished. SWBestiary +
  both biome tables ARE deployed and verified live (16/16 defs, 3/3 comps).
  NEXT: add the selftest that resolves biome refs against the **DEPLOYED** folders,
  not the repo — resolving against the repo is what made the original bug invisible.
- `SHEET_ORPHAN_CONSUMPTION_1` — 4 of 5 channels executed and verified; the 148-flora
  channel is measured but **nothing queued**.
  NEXT: file the 17 non-BMT flora art jobs; hold the 20 `BMT_Plant_*` until
  `BMT_FLORA_ABSORPTION_1` lands.
- `XENOTYPE_CANON_CORRECTION_1` — all non-cosmetic fixes landed. The appearance half
  is untouched and gated.
  NEXT: the owner's ordered sequence — **dossier → his web verification → skin colour
  → grid screenshot → head shapes → grid again.** Do not skip to the art.
- `ROSTER_VALIDATOR_STALE_REFS_1` — measured, **deliberately not fixed**.
  NEXT: refresh `plant_pool.csv` and the creature register AFTER
  `BMT_FLORA_ABSORPTION_1` lands — and check both for curated rows a generator cannot
  rebuild before running one.
- `SPECIES_TRAITS_OVER_APTITUDES_1` — the reach test is ruled (ALL members → GeneDef;
  most/many → TraitDef). NEXT: build the list of species with a truth no number can
  hold and put THAT to him. ⛔ Do not start writing genes.
- `LIVE_ITEM_GLOB_DRIFT_1` / `DEAD_BIOME_DEFS_IN_PROSE_1` — filed, unclaimed. ⚠️
  Another window appears to be mid-move on the closed-item half; check before acting.

## Traps learned

- **`MayRequire` tests whether the MOD is ACTIVE, not whether the DEF is PRESENT.** It
  does not protect a ref against a stale deployed build of an enabled mod. BENCH
  deployed biome tables on that wrong reasoning and left 18 dangling refs.
  (see: `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1`)
- **An artpipe slug is not a defName** — it lowercases, DROPS the donor prefix, may add
  a wave prefix, and appends `_v<n>`. `AB_Aaklac` → `aaklac_v1`. A defName-based
  membership test finds nothing and reports it as "owed".
  (see: `SHEET_ORPHAN_CONSUMPTION_1`)
- **A donor defName absent from the live set does NOT mean the content is gone.** 5 of
  7 "missing" species were ours under `RSW_` names; 3 were already DONE. Same trap as
  the 21 desert droids. **Always check the `RSW_` form before reporting an absence.**
- **`ModsConfig.xml` is not evidence about the owner's stack while a test tier is
  live.** A check during FOUNDRY's 14-mod flight test read `rotsporekit` INACTIVE; it
  is active in the real 618. Read `ModsConfig.FULL.LATEST.xml`.
- **`harvest_log.py` refuses when the def dump belongs to a different run — that is the
  tool working.** An undercount prints as better-than-baseline and is indistinguishable
  from a pass.
- **A subagent brief built from stale item text wastes the agent.** Half of one brief
  was already done in two earlier commits the item never recorded.

## Closed / superseded this wave

`DESERT_PORT_DUPLICATE_DEFS_1` · `BIOME_BINDINGS_TABLE_STALE_1` ·
`SURRA_GRASS_FERTILITYMIN_1` · `DESERT_PACK_ANIMALS_FOR_TRADERS_1` ·
`DESERT_FAMILY_VERDICT_PASS_1` (superseded) · `PORTED_BEAST_MECHANICS_REBUILD_1`

## Owner rulings landed this wave — all recorded in their items

Desert names (22 labels) · Fall Line fauna are ARRIVALS not biome fauna · surra grass
stays off sand · both deserts get traders · port both devourers · the silver tree is
**ollim** · wide gaps use existing kit turned up · Ocular Overdrive IS the Contagion ·
six aptitudes confirmed individually (five changed, Gungan kept) · Sith label AND
defName · Bothan canon supplied · `mandrake.rut.salvation` · ship floor reaches
Refurbished but LATE · **no hull sockets** · mobile structures named · Rekko's endgame
is not a grade float · gene-vs-trait reach test · all five sheet channels.

## Game / bridge / tree state at wrap

- running : RUNNING — **FOUNDRY holds the bridge** since 2026-09-20T19:39:36Z for a
  flip-book flight-animation test on a minimal quicktest list.
- 🔴 **`ModsConfig.xml` currently reads 14 mods. That is FOUNDRY's test tier and is
  CORRECT.** BENCH restored the full 618 at 18:28Z; FOUNDRY swapped after. ⛔ Do not
  "restore" it — that kills a live test. The real list is
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`.
- BENCH holds no bridge and nothing mid-edit. All subagents reported.
- ⚠️ Uncommitted in the shared tree, NOT BENCH's: four staged item deletions
  (`DESERT_BURST_PREDATOR_FLAGSHIP_1`, `DROID_TILES_SOURED_TERRAIN_1`,
  `RESEARCH_TRIO_RETIRE_1`, `TWILIGHT_DEEP_WATER_LAYER_1`) plus
  `MYCOID_COLOSSUS_ART_MISROUTE_1` — another window moving closed prose to
  `items/closed/`. Left untouched deliberately.
- Also uncommitted and not BENCH's: `CODE_REVIEW_STATUS.json`,
  `dashboards/hub/data/health.json`, `ModsConfig.before-tier-pits.xml`, the artpipe
  tree.
