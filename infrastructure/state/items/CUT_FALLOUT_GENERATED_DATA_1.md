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

**`--write` still refuses, for an UNRELATED reason found during this pass**:
`DUMP_ROOT/defs.sqlite` (`measure`/`dumpdb.py`'s output, `captured_utc
2026-09-19T02:35:03Z`) has **0 rows** in its `defs` table. Every biome/plant in
`FAMILIES` therefore reads "not in defs" regardless of correctness (170 problems
reported, almost all noise from this). `biome_flora.py`'s write path also reads plant
labels straight from this same empty dict, so a bypass would crash outright, not just
skip validation — there is no safe way to force a regen right now. This is a
pre-existing infra defect, not caused by this item's edits; a `measure build` re-run
(or equivalent) is owed before `BiomeFlora_Ashkarr.xml` can actually be regenerated and
the ~20 deployed BMT_ patch failures actually go away in a live load.

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
2. `measure build` (or equivalent) to refresh `DUMP_ROOT/defs.sqlite` — currently 0
   rows, blocking `biome_flora.py --write` regardless of roster correctness.
3. Once defs.sqlite is refreshed: run `biome_flora.py --write`, diff
   `BiomeFlora_Ashkarr.xml` against HEAD, confirm it's exactly the (b) renames/cuts with
   no other drift, deploy.
4. (a): the same purge as (b) but for `cast_assignment.csv`/`BiomeCast_Ashkarr.xml`
   (creature side), then `animal_tolerances.py --write` to regenerate
   `AnimalTolerances_Ashkarr.xml`.
5. (b) residual: a climate-aware port-or-cut decision for `RUT_TheForge`'s 3
   heat-tolerant BMT_ plants (FireLavender/Sagecrust/HeatsinkFungus), and separately a
   port decision for `BMT_GiantLeaf`'s two understory slots.
6. (c): a one-time hand clean of the live `Mod_3532608331_DeepStorageMod.xml` settings
   file, done at the keyboard.
