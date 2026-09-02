# BENCH handoff (2026-09-02, session 014vwgD9 — written for the reboot)

Owner was at the bench, went AFK mid-session, came back. He reboots this window
next. Everything below is committed and pushed through `8bead41e`.

## Live state NOT in git — verify it, do not trust it
- **Game is UP**, `programState=Playing`, **Ash'karr** (the real campaign world —
  `jawa/world_info_get` says so; check before assuming a map is scratch), fresh
  250×250 desert map, `ticksGame` ~1, paused, full mod list (**593 active**,
  fingerprint `0d594d931ddff722`, 0 missing).
- **Bridge is FREE.** `infrastructure/state/BRIDGE` is the one-line answer;
  `rimflow bridge who` re-derives it. FOUNDRY was told it could take it.
- **The map holds 21 built structures** (the review layout) plus 3 colonists.
  Nothing on it is saved except `REVIEW_tile_structures_21.rws`.
- **FOUNDRY is live and editing `design/Jawa/templates/*.lua`** — it committed
  `3e154906` mid-session and had 7 template files dirty. Expect `.git/index.lock`
  contention; **wait for it, never delete it.**

## 🔴 The one thing that must not be lost: FOUR COMPILED, UNDEPLOYED FIXES
Full detail and per-fix proof steps are in
`infrastructure/state/items/COLD_LOAD_RUN_SHEET_2.md`. A DLL cannot be written
while the game runs, so all four wait on the shutdown window:

```
python.exe src/RimMandrake/bridgetools/build.py --gm --apply     # inventory_transfer + spawn_pawn
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod StructureInjections --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod RimDefDump --apply
```

🔴 **`--gm` is not optional** — without it the plan drops ~35 player-acting tools.
⚠️ **Three repo DLLs are now NEWER than the game's copies.** "Repo file is newer,
so it must be deployed" reads exactly backwards until those commands run.

## Closed this session
- **`SAVEGAME_PURGE_KEEP_B_1`** — 32 files, 888 MB → 43 MB, the two `*_b` kept.
- **`BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1`** — cause proven, and it was
  **vanilla, not a mod**: a map thing's `holdingOwner` is `map.spawnedThings`, so
  `TryAddOrTransfer` hits `ThingOwner`'s `owner is Map` guard and moves 0, always.
  The whole mod shortlist is cleared. Fixed in source.
- **`SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1`** — it is the **world-pawn redress
  path**. `GeneratePawn` leaves `forceGenerateNewPawn` false, so it recycles a
  planet resident. The rate is a POOL, not a probability (16/300 → 0/200 as it
  drained), which is why every recorded percentage disagrees. **Stop quoting a
  rate.** Batch spawns were consuming real Ash'karr world pawns. Fixed in source.
- **`RIMPLACE_GENSTEP_LIVE_PROOF_1`** (filed and closed) — GenStep_RimplacePlan
  proven live, 130/130 terrain, 69/69 things, 192/192 roof, plus a synthetic
  foundation plan. Discharges `TILE_STRUCTURE_DESIGNS_1`'s live-verify criterion.
- **`BRIDGE_PAWN_THOUGHTS_CARAVAN_GAP_1`** — its fix was already deployed and only
  unproven; formed a caravan and read `TravelCompanions` off a member. Met.

## Open threads
1. **Rebuild the review save when FOUNDRY lands.** `REVIEW_tile_structures_21.rws`
   is a snapshot from before FOUNDRY's template edits; 7 templates were dirty.
   Owner knows. ~5 minutes with the bridge. Key: `items/TILE_STRUCTURE_REVIEW_SAVE_1.md`.
2. **`WILD_ANIMALS_PADDED_LISTS_1` — the bridge half returned a NEGATIVE.** Nothing
   Harmony-patches `wildAnimals`. The padder is a direct def mutation at load, so a
   patch inventory can never name it. Next step is a **null test on the 13-mod
   minimal list**, not more searching.
3. **`WEAPONS_DONOR_RETIREMENT_1`** — measured live: the five "accepted residual
   risk" apparel defs all resolve to `mandrake.rsw.armoury`, not kotorweapons, so
   that accepted cost does not exist. kotorcore is still blocked on
   `guy762.KotORDroids`.
4. **LoadTracer is still ENABLED in ModsConfig** (carried over from the previous
   handoff, never answered). It is a DIAGNOSTIC — pull it before real play.
5. **Load-error census** of the fresh `Player.log` — still offered, still not filed.
   ⚠️ `harvest_log.py` currently REFUSES because the def dump is from an earlier
   run. After the RimDefDump deploy that is one bridge call to fix, not a reload.

## New this session, and both are doctrine now
- **Bridge handoff**: `infrastructure/state/BRIDGE` + `rimflow bridge who/take/release`,
  `./bridge bench|foundry|free` for the owner. It **errs toward allowing** — a take
  is refused only while the holder has been active inside 45 minutes, `--force`
  always works. CLAUDE.md § "The bridge is passed through one file".
- **Review options ship as a savegame** (owner, by card): one map with all options
  on a grid, an item file giving the grid key, saves kept until he says delete.
  CLAUDE.md § "Options he must LOOK at ship as a savegame". 🔴 Back up the Saves
  folder's keepers and stat it after — `save_game` has overwritten the current slot.
