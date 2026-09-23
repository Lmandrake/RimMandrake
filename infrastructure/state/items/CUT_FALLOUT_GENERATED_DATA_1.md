# CUT_FALLOUT_GENERATED_DATA_1 — Load C fallout from the Caverns + Polluted Lands cuts

Source: `Transient/harvest_loadC_triage_2026-09-19.md`. 7 sub-tasks (a)-(g). This pass
(FOUNDRY, 2026-09-19) closed 4 cleanly, partially closed 1, found 1 blocked on a stated
precondition, and found 1 is not a repo file at all. Live-load confirmation that the
patch-failure count actually dropped is explicitly OWED regardless — nothing here was
verified against a running game, per this pass's own scope (offline defect-cleanup).

## (a) AnimalTolerances_Ashkarr.xml regen — BLOCKED, precondition not landed

Item text: "once cast_assignment.csv/BiomeCast purge lands." MEASURED 2026-09-19:
`design/Jawa/fauna/cast_assignment.csv` still has 29 `BMT_` hits and
`design/Jawa/fauna/BiomeCast_Ashkarr.xml` (the design-side roster, not the deployed
patch) still has 10. The precondition has not landed. Regenerating
`AnimalTolerances_Ashkarr.xml` now would bake in the same 592-entry-with-stale-species
problem the item is trying to fix. Not attempted. Owed: the animal-side purge (same
shape as (b) below, but for creatures — a separate, larger pass).

## (b) Flora-side BMT_ purge — PARTIALLY DONE (19 of 24 dead refs fixed at the source)

Checked the sibling-item overlap first, as instructed: `BIOME_FLORA_GENERATOR_REPAIR_1`
(closed) rebuilt `biome_flora.py`'s `FAMILIES` dict against the renamed RUT_ biome keys
and got `--check` from 80 problems to 2; `PROPANE_LAKES_ROSTER_STALE_1` (closed) fixed
those last 2 (a stale `AB_PropaneLakes` roster key). Both landed BEFORE Caverns itself
was retired, so neither touched the BMT_ plant residue this item is about — no overlap
in the actual fix, but their closing notes explain exactly why the FAMILIES-vs-roster
sync mechanism exists and matters here.

Fixed (commit `f2db9fb56`): 18 BMT_ plant defNames in `the_rot.json` and 1 in
`weeping_stones.json`, renamed to the RUT_ ports that already exist as real ThingDefs
(confirmed via `grep -rl "defName>NAME<" src/RimUtinni/`, not guessed) — the exact same
18-name rename `CAVERNS_PARITY_BUILD_1` hand-applied straight to the deployed
`BiomeFlora_Ashkarr.xml` on 2026-09-18, which a later `--write`
(`POLLUTED_LANDS_FLORA_PORT_1`) silently reverted because the roster JSON / `FAMILIES`
dict (the generator's real source) still said `BMT_`. Fixed at the source this time, so
the next successful `--write` keeps it. Also cut 2 more with no existing port
(`BMT_GiantLeaf` in `the_greentide.json` commonality 1.0 and `the_fever_wood.json`
commonality 0.8 — both top-weighted understory slots) into each roster's
`flora_purged` array with a reason; port/replace is owed, cutting was the safe default
used already for POLLUTED_LANDS_FLORA_PORT_1's 13 filler rows.

Deliberately NOT touched: `RUT_TheForge`'s `BMT_FireLavender`/`BMT_Sagecrust`/
`BMT_HeatsinkFungus` (3 refs). These are "flash-interval flora" explicitly picked for a
50-352 °C tolerance band; the Rot's `RUT_Sagecrust` port was picked for a COLD biome
(median -18.8 °C) and its temperature tolerance is not verified to cover the Forge's
range. Reusing it blindly risks a wrong-climate plant silently failing to grow in an
extreme-heat biome — a design call, not a mechanical rename. Left for a follow-up pass.

**`--write` refused for an UNRELATED reason found during this pass, FIXED 2026-09-20**:
`DUMP_ROOT/defs.sqlite` had **0 rows** in its `defs` table (`captured_utc
2026-09-19T02:35:03Z` build, empty). Every biome/plant in `FAMILIES` therefore read "not
in defs" regardless of correctness (170 problems reported, almost all noise from this).
FOUNDRY ran `measure build` against the live 2026-09-20T07-47-24Z capture (the 617-mod
session that was up that day): MEASURED 77,387 defs, 531 types, 0 absent/shadowed/
ambiguous/orphan/partial/failed. `biome_flora.py --check` now runs cleanly and reports
exactly **3** problems — all three are the RUT_TheForge trio named just above
(`BMT_FireLavender`/`BMT_Sagecrust`/`BMT_HeatsinkFungus`), confirming this pass's own
diagnosis was correct and complete. **That one content call (port-or-cut, above) is now
the ONLY thing blocking `--write`.** Also found: `RUT_TheRot.xml`'s own hand-authored
`wildPlants` block is already correctly `RUT_`-renamed (per its own
`FUNGALFOREST_RAID_MERGE_1` header), so the still-stale deployed
`BiomeFlora_Ashkarr.xml` patch (`PatchOperationReplace`, unconditional) is not merely
failing to fix anything — it is **actively clobbering that already-correct content back
to broken `BMT_` names on every load**, which is worse than inert. Once the TheForge
call lands, `--write` + `--doc` + `validate_patch.py` + deploy is a single short pass
that should retire all 21 flora crossref lines in `FULL_LOAD_RESIDUE_TRIAGE_1` (5) at
once.

## (c) Config/Mod_3532608331_DeepStorageMod.xml — NOT A REPO FILE, not touched

Confirmed: this is a live Windows Config file at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\`,
not tracked in this repo (`git status`/`git log` show nothing for it; no deploy script
under `src/RimMandrake/Utils/` reads or writes it — checked
`gen_furniture_register.py`/`harvest_log.py`, the only two repo files that even mention
DeepStorage, and neither touches this Config file). RimWorld was ALSO confirmed running
(`tasklist.exe`) during this pass, which per the ground rules ("do NOT touch the
bridge") and plain risk (the game may rewrite its own mod-settings file on next
save/exit, silently reverting any offline edit) makes this a genuinely live-game
action, not an offline cleanup. Matches the triage doc's own conclusion. Not attempted.
Owed: a one-time settings clean (strip the ~95 dead `BMT_`/`TYR_` `<li>` entries), same
mechanism as the 2026-08-22 cleanup, done by whoever is at the keyboard with the game
either closed or in its settings screen.

## (d) Absorbed_Kotorweapons_BiomesCaverns injector — DONE

Deleted the file (targeted Caverns' own `BMT_CrystalsGenerator` GenStepDef directly —
with Caverns gone that GenStepDef doesn't exist, so FindMod-guarding it would guard
nothing salvageable) and removed its `PACKS` tuple from
`gen_additionalmods_absorption.py` so a regenerate won't recreate it (same precedent as
that generator's own prior ModularWeapons2 removal). Commit `63a82618a`.

## (e) WeaponTags_Renormalise.xml — DONE

Removed 10 dead `PatchOperationConditional` blocks (BMT_BlastSpore/BunkerClaw/
CaveSpiderHead/CrystalMantisClaw/FungalMantisClaw/PustuleHornetStinger/
ResourceBlueCrystal/RoyalRhinoHorn/ThrumbungusShroom/Toxwood) — both Caverns- and
Polluted-Lands-owned defNames confirmed via `plant_pool.csv`'s source column, both mods
retired, both match+nomatch branches permanently fail. Deleted outright (not
FindMod-guarded) matching this file's own established precedent for permanently-retired
donors (its 2026-08-31/2026-09-06 header comments). Commit `63a82618a`.

## (f) Waterline_Lane1.xml — DONE

Removed 5 dead nested-Conditional blocks (BMT_MucklurkerCatfish/TaintedTurtle/
MutatingTumorfishSpawn/Fry/Adult, 52 lines) — all Biomes! Polluted Lands fish, same
permanently-inert shape. Commit `63a82618a`.

Both (e) and (f) validated with `validate_patch.py --live <today's DefDump capture>
--mods-config <live ModsConfig.xml>`: 0 errors on both edited files (162 warnings
total, all pre-existing intentional add-if-missing `nomatch` shapes, unrelated to this
fix).

## (g) The Salvation.rid / MandrakeJawa.xtp modIds — DONE

`build_salvation_rid.py` does NOT touch `modIds` (it edits description/name text only
via `SIMPLE_EDITS`) so it was not the right tool, contrary to the item note's
suggestion — investigated rather than assumed. Stripped the two `<li>` entries
(`biomesteam.biomescaverns`, `biomesteam.biomespollutedlands`) directly from all three
copies that actually carry them: `src/Jawa/ideoligion/The Salvation.rid`,
`src/Jawa/ideoligion/MandrakeJawa.xtp`, and `deployed/config/xenotypes/MandrakeJawa.xtp`
(CRLF+BOM, handled separately). All three re-verified as valid XML with zero remaining
hits. Commit `cd3b1ce78`. Noted but out of scope: the `deployed/` copy's blastdoor
async-fix packageId (`mandrake.blastdoorframeasyncfix`, missing the `rsw.` tier) is
stale versus the `src/` copies (`mandrake.rsw.blastdoorframeasyncfix`) — a separate,
pre-existing staleness, not touched here.

## Owed, in order

1. Live cold load to confirm the patch-failure count actually dropped (explicitly out
   of scope for this offline pass).
2. ✅ DONE 2026-09-20 (FOUNDRY): `measure build` refreshed `DUMP_ROOT/defs.sqlite`
   against the live 2026-09-20T07-47-24Z capture — 77,387 defs, 0 gaps.
   `biome_flora.py --check` now runs and reports exactly the 3 RUT_TheForge problems
   named in (b)/§5 above, nothing else.
3. ✅ DONE 2026-09-20 (FOUNDRY, two parallel agents + one reconciling fix): the
   TheForge trio's port-or-cut decision resolved itself — `BMT_FLORA_ABSORPTION_1`
   (closed same day) authored real `RUT_FireLavender`/`RUT_HeatsinkFungus` and
   confirmed `RUT_Sagecrust` already existed; `RUT_GiantLeaf` likewise ported for both
   Greentide and FeverWood. What was actually still broken: the *hand-authored*
   `Defs/BiomeDefs/RUT_*.xml` base files still named the dead `BMT_` defNames
   directly — the generator (`biome_flora.py --write` → `BiomeFlora_Ashkarr.xml`,
   a `PatchOperationReplace`) only ever overwrites that content at load time, it
   never edits the base file, so `--check` (which compares roster vs. `FAMILIES`,
   never vs. the base XML) couldn't see the base file was still stale. Fixed all 14
   dead `BMT_` plant cross-refs directly in the base files across all 8 biomes
   (Greentide, FeverWood, TheForge, WeepingStones, Scarlands, Miasma, PoisonForest,
   CrackedLands): 9 repointed to their existing RUT_ ports, 4 Miasma rows cut
   outright (already-purged in the roster — the mangal family covers the tree
   identity, no port needed), 1 (`TreeTwistingThornwood`) already ported and
   repointed. Zero `BMT_` plant names remain in any `<wildPlants>` table (confirmed
   by direct regex scoped to that tag, not a raw grep). `biome_flora.py --write` was
   NOT run — nothing needed it, since the generated patch layer was already correct;
   only the redundant/misleading base-file copy needed sync. `validate_patch.py
   --live` clean on every touched file; selftests 66/66 both before and after.
   Commits: `fe98d2ed9`, `8725fb338`, `61c6a9233`.
   ⚠️ NOT re-verified against a live cold load — `FULL_LOAD_RESIDUE_TRIAGE_1` entry
   (5)'s 38-line crossref count (which names several of these same defNames) needs a
   fresh load to confirm it actually drops; that count comes from the game's own
   `BiomePlantRecord` resolution, a different instrument than `biome_flora.py --check`.
4. (a): the same purge as (b) but for `cast_assignment.csv` — BUT see
   `BIOME_CAST_PATCH_DEAD_NAMES_1` (filed 2026-09-20) first: `BiomeCast_Ashkarr.xml`
   may be entirely dead code (targets pre-`BIOME_OWNERSHIP_WAVE_1` biome defNames that
   no longer exist on any live BiomeDef), in which case there is nothing to purge —
   confirm that item's finding before spending time on (a) or on
   `AnimalTolerances_Ashkarr.xml`. ⚠️ Note: `cast_assignment.csv` is showing as
   uncommitted-modified in the shared working tree as of this session — check whether
   a concurrent window already has this in flight before touching it.
5. (b) is now fully DONE — see item 3 above. Nothing left in this subtask.
6. (c): a one-time hand clean of the live `Mod_3532608331_DeepStorageMod.xml` settings
   file, done at the keyboard.

## (a) — DONE 2026-09-23 (FOUNDRY): `cast_assignment.csv` regenerated, 0 `BMT_` defNames left
Re-verified fresh rather than trusting the 2026-09-19/20 numbers: `BIOME_CAST_PATCH_DEAD_NAMES_1`
(closed 2026-09-20) already found `BiomeCast_Ashkarr.xml` fully dead and deleted it, so the
precondition item §4 named is moot — that consumer no longer exists. `ANIMAL_TOLERANCES_JOIN_BROKEN_1`
(closed 2026-09-20) already made `animal_tolerances.py`'s regen merge-safe (`pin_orphans()`), so
that consumer was never actually at risk from a stale `cast_assignment.csv`. `ROSTERS_TO_CAST_
BIOMECAST_DEFS_STALE_1` (closed 2026-09-20) already rebuilt `rosters_to_cast.py`'s biome-name join
and regenerated the CSV once from clean rosters. **What was actually still open**: the file on disk
had drifted stale again since that 2026-09-20 regenerate — `ROSTER_DEAD_BMT_NAMES_SWEEP_1` (still
`proposed`, BENCH/MACBENCH, committed `949635655` earlier TODAY) renamed every live `BMT_` roster
row to its `RSW_` port or moved it to `evictions`, and `fall_line.json`'s injection layer was
deleted outright per an owner ruling (`fall_line.md §8a`, 2026-09-20) — neither had been synced
into the derived CSV yet.

Ran the sole sanctioned generator, `python3 design/Jawa/fauna/rosters_to_cast.py` (no `--out`, so
it wrote the real file directly — its own docstring forbids hand-editing the CSV). Verified the 41
BMT_→RSW_ renames and 7 drops (`BMT_ChemSnail`×2, `BMT_GlowBat`, `BMT_Pillbug`, `BMT_GiantSlug`,
`BMT_GiantSnail`, `BMT_CaveSpider` — all six confirmed `disposition: cut-for-real` in the roster's
own `evictions` array, citing the owner's 2026-09-20 "Yes cut the 6 fauna" ruling, not a call made
here) are exactly what the already-clean rosters justify — not a decision, a sync. Result: **0 of
353 rows carry a `BMT_` defName** (was 58 rows / 47 unique names). The ~66-row net drop beyond the
BMT_ count (419→353) is `fall_line.json`'s already-ruled, already-committed injection-layer
deletion (Mynock/OuterRim droids/Rat/Scavrat/etc. out of Desert/AridShrubland/ExtremeDesert) showing
up in the same regenerate — confirmed via `git log`/roster diff before writing, not assumed.
Commit: pending in this session.

Not run this pass, deliberately: `animal_tolerances.py` regen/redeploy (its `pin_orphans()` guard
already protects the live deployed patch from narrowing even with this CSV change — no urgency, and
`deploy_custom_mods.py --apply` is expensive-list ceremony this pass avoided to not collide with the
concurrent cold-load pass another window is running on the bridge today).

## Flora blocker (item 3 above) — RE-VERIFIED CLEARED, `--write` still blocked by unrelated content
`measure build` was stale (last capture 2026-09-21, current capture 2026-09-23T21-58-37Z) — rebuilt
fresh (78,489 defs, 0 gaps). `biome_flora.py --check` no longer reports the TheForge 3-plant
problem at all — confirms item 3's 2026-09-20 fix (RUT_FireLavender/RUT_HeatsinkFungus authored,
RUT_Sagecrust confirmed pre-existing) is holding. **`--write` still refuses**, but on 7 entirely
different problems (`RUT_FuelSnows`/`RUT_Umbra` FAMILIES-vs-roster mismatches, `RUT_AridShrubland`/
`RUT_BlueDesert` authored-def-vs-roster drift) — none BMT_/cut-fallout shaped. All 7 trace to biomes
already owned by other live, separately-tracked items (`BIOME_MOD_SPLIT_EXECUTION_1`,
`TERMINALBIOMES_RM_MOD_BUILD_1`, `DESERT_FAMILY_PORT_EXECUTION_1`, `NIGHTSIDEICE_RM_MOD_BUILD_1`,
`STILLSAND_RM_MOD_BUILD_1`, `LEANINGSCRUB_RM_MOD_BUILD_1`) — the ongoing biome-mod-split migration,
mid-flight per CLAUDE.md's standing biome-painting ruling. Not this item's content to fix; left
untouched rather than guessed at. `--write`/`--doc` and `FULL_LOAD_RESIDUE_TRIAGE_1`(5)'s live
crossref re-confirmation both stay owed, gated on those other items landing and a cold load — out
of scope for this offline pass.
