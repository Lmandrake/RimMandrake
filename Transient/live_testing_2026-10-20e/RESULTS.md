# Dev start save on the 374 list — tomorrow's setup proof (FOUNDRY live helper, 2026-10-20e)

**Tomorrow starts here:** game is UP on the owner's 374 list with `ASHKARR_DEV_START_2026-10-20` loaded and PAUSED at tick 3 — healthy (0 exceptions of ours, 3200 ticks clean, 12 colonists, ship + engine, Ikee bonded to First-Hatched); expect 7 VEF "New faction" dialogs on every load until you decide them (below).

Bridge taken 01:20 PDT (`rimflow bridge take --for "dev start save on 374"`). Game was DOWN; ModsConfig = owner's 374 (== FULL.LATEST, not edited).

## Status
- [x] bridge take
- [x] cold load 374 (748 s, first exception identical to 20b)
- [x] load ASHKARR_DEV_START_2026-10-20.rws (26 s, compatible 83/83)
- [x] save censuses (class / def / adoption) vs 374 — offline, done 01:28 (below)
- [x] 3205 ticks at Superfast: 0 exceptions, ~280 TPS
- [x] colonists / ship / Ikee bond
- [x] FOUNDERS copy load (13 s)
- [x] screenshots
- [x] end state UP+paused on DEV_START; bridge released

## Offline save censuses against the live 374 ModsConfig (01:28)
Saves sha256 before any load: `dev_saves_sha_before.txt`. Files: `class_census_*.txt`, `def_census_*.txt`, `adoption_*.md`.

| save | class census | def census (things) | adoption check |
|---|---|---|---|
| ASHKARR_DEV_START_2026-10-20 | 0 unresolved class sites | 6786 things, **0 unresolved THING defs**; 73 other refs / 22 defs (Aptitude* passion-style names) | exit 1: **5 unresolved names**, 142 hits — Thing `Horax` x1 (Star Wars Animal Collection, a record ref), VSE `Major` x55 / `Minor` x84 / `Foreman` x1, `Paste` x1; kindDefs 31 distinct all resolve; world grids clean |
| ASHKARR_DEV_FOUNDERS_2026-10-20 | 0 | same 0 unresolved THING defs | exit 1: same 5 names, 133 hits |

On PAINT 83 the same START save had 96 unresolved names (Alpha Memes rituals, AA_Eyeling, ...); the 374 list carries
those mods, so the residue drops to 5. Exit 1 = the tool's "0 unresolved" bar, not a load blocker (record/passion names).

## Cold load, 374 list (live ModsConfig untouched: 374, byte-equal FULL.LATEST)
- Launch 01:21 PDT via `launch_ready.py` (Steam); **READY 748 s** (pid 15824, port 5174) — 20b baseline 771 s. Receipt `launch_receipt.txt`.
- **First exception = `Exception in ConfigErrors() of CannibalPirate` NRE — identical to 20b.** Exception events 3 (CannibalPirate,
  PirateYttakin ConfigErrors, `brtrue NULL`), **ours 0, 0 new signatures** vs 20b `playerlog_menu.txt` (`harvest_menu_donorfree.txt`).
- xref 0, our texture misses 0, config errors 13 (ours 0), patch failures 3 (ours 0), Scribe 7 at menu (the user's custom
  xenotype files naming retired Alpha Genes — same 7 as 20b). `harvest_log.py`: same RED rows as before (Scribe 7; 'RimAI Core
  booted' MISSING — 0 RimAI lines in 20b too). Menu log copy: `playerlog_menu.txt`.

## Load ASHKARR_DEV_START_2026-10-20 on 374 (01:34)
- `rimworld/load_game_ready` (readiness playable, compatibility check ON): **compatible, 83 recorded mods, 0 missing**; playable in
  **26 s** wall clock (final reload 11 s). Game tick 3 (the save sits right after landing). `load_start.json`, `playerlog_start_load_delta.txt`.
- 🔴 **7 forcePause VEF `Dialog_NewFactionSpawning` dialogs block time on every load** (factions on 374 absent from the PAINT world):
  Splinter colony (RF Rumor Has It, "non-spawning, probably ignore"), **Gamorrean Clan** (Orc Clan + Xenotype), Tribal Hostiles and
  Hostile Faction (Dungeon Pack), **Junkers** and Mercenaries (VFE Pirates), Roaming monstrosities (VGE). Answered **"Do nothing"**
  each time (no world change; they will ask again). Add / never-ask is the OWNER's call (the world freezes with its faction set).
  `faction_dialogs.py` answers them all with "Do nothing" in one call.
- Exceptions/errors in the load, by class:
  - **Ours (2, non-fatal):** `Failed to find any textures at RimStarWars/SWBestiary/Dewback/DewbackPack` (RSW_Dewback 'Geonosis' is a
    pack animal on 374; the pack-graphic variant was never made — the Wave B "DewbackPack unused-variant" call no longer holds; not on PAINT);
    `[JawaRules] pawnkind-redress-fix` corrected a recycled world pawn (warning, self-healed).
  - **Saved data written on PAINT (not fixable by mods):** 32 x `Could not get load ID ... /sourcePrecept` + 32 x `same load ID twice`
    on the Jawa robes/hoods/suits of all 12 colonists (also 64 on the PAINT S14 reload — pre-existing); Precept_Ritual /
    RitualOutcomeEffectWorker PostLoadInit NREs x2 (The Salvation rituals, also on PAINT); `Could not find think node` x4.
    🔴 **New on 374: 475 x `Tried loading non-compressible thing as compressed thing`** (ChunkSandstone 205, ChunkSlate 203,
    ChunkSlagSteel 50, Blueprint_LinoTile_White 17): a 374 mod makes chunks non-compressible, so **every rock/slag chunk the PAINT save
    compressed is dropped** (live `ChunkSlate` count 0). Cosmetic loss only; once saved on 374 it is gone for good.
  - **Third-party (known):** RimFridge `StartedOrLoadedGame` NRE + `RimFridge_PowerFactorSetting` miss (same as PAINT R1/G18/S14);
    `InputLegacyModule` FileNotFoundException (reflection-only scan).
  - Mods not on the list: none (compatibility 0 missing; class census 0; adoption 5 names, none surfaced as a load error).
- Read-only state (`colonists.json`, `player_pawns.json`, `ikee_relations.json`):
  12 colonists, none downed/dead — 6 scenario Jawa (Bluil, Braddock, Kob, Kwenulih, Prugetikk, Susir) + 6 founders (Twice-Kin, The Hands,
  First-Hatched, Keeper, Captain, The Long Pot on the deck row 172..182,61). **5 founders load DRAFTED** (Wait_Combat; The Long Pot is
  not) — they stand still until undrafted. **Ikee 'Dylan' (RSW_Ikee15964): Bond -> First-Hatched only.** Dewback 'Geonosis' at 184,61.
  Ship: `GravEngine23134` at 186,62 (800/800 HP); 1973 artificial buildings in the ship rect 145,18,92,86.

## 3205 ticks at Superfast, no player actions (01:37)
- tick 3 -> 1409 at 6.7 s -> 3136 at 12.9 s -> paused at 3208: **~280 TPS** (78% of the 360 target, 12 colonists, fresh map). `tick_series.txt`.
- Log delta (`playerlog_tick_delta.txt`, 1576 lines): **0 exceptions, 0 errors** — only social chatter ("too far to join the
  conversation", MCR MoodChain debug lines). After: 12 colonists, 0 downed, 0 dead; Ikee bond unchanged; alerts: Major break risk,
  Need colonist beds, Bedroom unhappiness (a fresh colony).

## ASHKARR_DEV_FOUNDERS_2026-10-20 on 374 (01:39)
- Compatible, playable in 13 s; same 7 faction dialogs (answered "Do nothing"); 12 colonists. Same error classes as START plus
  `Pawn First-Hatched has relation "Bond" with null pawn` and `Could not resolve reference ... Thing_AA_Eyeling` (the dropped Eyeling).
  **Ikee is bonded to Braddock here** — this copy predates the S12 rebond; START is the one to use.

## Screenshots (D:\ClaudeWork\screenshots\2026-10-20\)
- `devstart_374_ship_hub__cell_rect.png` — the ring hub: grav engine, Dewback, 5 drafted founders in the corridor (best; opened).
- `devstart_374_ship__cell_rect.png` — the whole ring ship from above, after 3200 ticks (colonists have moved aboard).
- `devstart_374_colony__cell_rect.png` — the landing area west of the ship (shipping-container ruins; colonists had left it).
- `devstart_374_faction_dialog.png` — the first VEF "New faction" dialog.

## End state
- Final: `ASHKARR_DEV_START_2026-10-20` reloaded fresh (tick 3; the ticked session was discarded, nothing saved), the 7 dialogs answered
  "Do nothing", **game UP and PAUSED**, camera on the ship hub. No save written by this run: the DEV saves' sha256 still match
  `dev_saves_sha_before.txt`; no new file in Saves. ModsConfig untouched. Bridge released.
- Owner decisions owed: the 7 new factions (add / ignore / never ask); whether losing the compressed chunks matters (it does not block work).
- Claimable: DewbackPack texture (or drop packAnimal's pack graphic for RSW_Dewback); undraft-on-splice for founders in import_founders.py.
