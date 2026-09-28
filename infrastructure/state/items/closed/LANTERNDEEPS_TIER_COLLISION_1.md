# LANTERNDEEPS_TIER_COLLISION_1 — the live Lantern Deeps has no repo copy, and its successor would delete it

Found 2026-09-26 by BENCH while preparing `BIOME_LOAD_PROOF_WAVE_1`. Nothing has been
deployed for this mod; the hazard was caught before `--apply`.

## what is true (MEASURED 2026-09-26)

| | |
|---|---|
| Live mod list | **628 active** (parsed from `activeMods`, not grepped) and it contains `mandrake.rut.lanterndeeps` |
| That mod's files | exist **only** at `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\LanternDeeps` |
| Its repo copy | None in the current tree, but **all 82 files are in git history, byte-exact** (MEASURED 2026-09-26, FOUNDRY): 81 at `8a2b2364b:src/RimUtinni/LanternDeeps` (the tree `1f1c368f7` deleted when it built the RM mod, plus its C# source and csproj), the DLL as blob `73566ff39` in `6ce1ccf9c` (on origin/main). The 28 non-art files are also committed at `infrastructure/state/rescued/LanternDeeps_RUT/` |
| The successor | `mandrake.rm.lanterndeeps`, in the repo at `src/RimMandrake/LanternDeeps` — 96 tracked files, its own 51 textures under `Textures/RM_LanternDeeps/` |
| Its deploy target | `Mods\LanternDeeps` — **the same folder name** |
| Is the successor active? | No. `mandrake.rm.lanterndeeps` is absent from `ModsConfig.xml` |

## the hazard, concretely

`deploy_custom_mods.py --mod LanternDeeps --apply` writes the repo's
`About/About.xml` over the game's. That single file carries the packageId. The moment
it lands:

1. `mandrake.rut.lanterndeeps` **no longer exists anywhere on the machine** — not in
   the game folder (overwritten), not in the repo (never there).
2. It is still listed in `ModsConfig.xml`, so it becomes a listed-but-missing mod.
3. The canonical campaign save references `RUT_LanternDeeps` defs — the biome, the
   two entrance buildings, the lanternstone terrain and walls, the cave flora. Those
   resolve through that mod and nothing else.
4. ⚠️ **This is the `Could not load reference to` class, which no mod change fixes** —
   the save itself holds the dead names. See the `rimworld-savegame` skill on the
   difference between that and a def-loader cross-reference error.

⛔ **So this is not a deploy that merely needs care. It is a deploy that must not
happen until the migration is done properly.**

🔑 Two standing lessons this is an instance of: *"Deploy tool needs unique mod names —
collides silently"*, and *"a BiomeDef deletion needs a live-tile check; a grep of the
`.rws` for the old defName lies because `tileBiome` is shortHash-encoded."*

## a second finding, same root

`deploy_custom_mods.py --pull LanternDeeps` **pulled the old tier's content into the new
tier's folder** — 28 paths including `About/About.xml` (reverting the packageId to
`mandrake.rut.lanterndeeps`), a parallel `Textures/RUT_LanternDeeps/` tree, the old DLL
and 27 `RUT_*` defs and patches sitting beside their `RM_*` successors.

`--pull` is documented as the rescue for `-` lines and is correct for a hand-edited
deployed copy — but it is **wrong whenever the deployed folder is a different mod that
happens to share the folder name**, and it gives no warning. BENCH reverted it the same
minute: `About.xml` restored from git, the 28 untracked paths moved aside (not deleted)
to the session scratchpad. `git status src/RimMandrake/LanternDeeps` is clean.

⚠️ **Whoever takes this item: do not re-run `--pull` on this mod.**

🔴 **CORRECTION 2026-09-28 (FOUNDRY) — the "reverted" claim above is FALSE as of
right now.** `deploy_custom_mods.py --mod LanternDeeps` reports the live
`Mods\LanternDeeps` folder **"in sync (79 files)"** with `mandrake.rm.lanterndeeps`
— the full RM successor, not the reverted RUT About.xml this section describes.
The deployed `About.xml`'s own mtime is **2026-09-26 16:43:22 -0700**, ~47 minutes
after this item was filed — so either the "same minute" revert never actually
landed, or a second `--apply` re-deployed the RM mod afterward and nobody updated
this record. `ModsConfig.xml` still lists the OLD `mandrake.rut.lanterndeeps`
packageId (unchanged), so the game has read `mandrake.rut.lanterndeeps` as a
listed-but-missing mod for two days — exactly this item's own hazard scenario —
and it is why `rimworld/load_game_ready` on the canonical save now refuses with
`save.missing_mods`, naming `vanillaquestsexpanded.cryptoforge` (expected, FOUNDRY
retired it this session), `mandrake.rut.rotsporekit` (separate, unrelated — its
own mod folder is untouched, just toggled off in ModsConfig, trivial re-enable),
and `mandrake.rut.lanterndeeps` (this hazard). Nothing was lost — steps 1/2's
rescue materials (git history + `infrastructure/state/rescued/`) are exactly
where this item's own "what is owed" said they'd be. Proceeding to complete step 4
(ModsConfig swap) and verify per step 5, in the load round already underway for
CRYPTOFORGE_HARVEST_RETIRE_1 step 4 — NOT resaving without the owner's word, per
step 7.

## what the canonical save holds (MEASURED 2026-09-26, FOUNDRY)

`Saves\CANONICAL_ASHKARR_START_2026-09-12.rws` (canon.yml `planet.start_savegame`),
parsed with `ElementTree.iterparse` against every defName in both tiers (39 RUT, 38 RM);
sanity probe `Steel` 917, `Human` 864 hits.

| reference | count |
|---|---|
| `<def>` of any RUT or RM LanternDeeps defName (placed Things, plants, buildings) | **0** |
| `RUT_LanternDeepGenerator` anywhere (a generated Deep pocket map) | **0** — no Deep has ever been entered in this save |
| `Class=` naming either assembly's types (MapComponents, GenSteps) | **0** |
| `savegame/meta/modIds` → `mandrake.rut.lanterndeeps` | 1 |
| VanillaTradingExpanded `TradingManager.priceHistoryRecorders` keys+values: `RUT_Lanternstone`, `RUT_PufferTendrils`, `RUT_SmoothedLanternstoneWall`, `RUT_BuiltLanternstoneWall`, `RUT_BuiltSmoothedLanternstoneWall` | 5 + 5 |
| `RUT_LanternDeeps` biome on world tiles | UNMEASURED (shortHash); the def is pocket-map-only, reached solely through the generator |

⇒ **The save's hold on the RUT mod is price-history bookkeeping only.** After a swap
those 5 keys fail to resolve; the engine's `Scribe_Collections` dictionary loader logs
`Null key while loading dictionary` and `continue`s (read from decompiled
`Verse/Scribe_Collections.cs` ~L400) — assuming VTE saves it through that loader, which
is the ordinary pattern but UNMEASURED. Plus the usual mod-mismatch prompt on load.

## what else was found

- 🔴 **Coexistence (the earlier guess) is the WORSE route.** Both tiers active at once:
  RM still defines a SoundDef named `RUT_DeepHum` — same defName as the RUT mod's — and
  both scatter entrances on the same RUT_ host biomes (`aa9ef0947`), so every qualifying
  map would get two sets. It would also need the RM src folder renamed to dodge the
  shared `LanternDeeps` deploy folder.
- ⚠️ **Already live today:** `RUT_LanternDeepKyberScatter` is defined twice in the
  running game — by the deployed `UtinniPatches` (`mandrake.rut.patches`) and by the RUT
  LanternDeeps mod. The swap removes the second definition.
- ✅ **Fixed this pass:** RM `About.xml` declared `loadAfter mandrake.rut.patches` while
  `mandrake.rut.patches` declares `loadAfter mandrake.rm.lanterndeeps` — a cycle. RM's
  side was unnecessary (the host-biome check is a runtime defName compare) and is gone.
- The live DLL carries every class of the 10 source files at `8a2b2364b`, including
  `LanternDeepsHarmony` / `Patch_MapPlantGrowthRateCalculator_BuildFor` (the classes in
  `Patch_PocketMapGrowthRate.cs` — a filename, not a class name).

## migration plan — in-place swap with a folder-move rollback (one cold load)

Needs: game DOWN, bridge held, owner's list otherwise untouched.

1. Back up `ModsConfig.xml` (`modlists/` snapshot) and stat it.
2. **Move, never delete**, `…\RimWorld\Mods\LanternDeeps` → `…\RimWorld\Mods_retired\LanternDeeps_RUT_<date>`
   (outside `Mods`, so the game cannot see it). Stat both sides: 82 files.
3. `deploy_custom_mods.py --mod LanternDeeps` — the plan must be all `+` into an empty
   folder, zero `-` lines — then `--apply`. ⛔ Never `--pull`.
4. In `ModsConfig.xml`, remove `mandrake.rut.lanterndeeps` (index 574 of 630 today) and
   insert `mandrake.rm.lanterndeeps` **before** `mandrake.rut.patches` (index 572), which
   declares loadAfter it. Parse the file; never grep it.
5. Cold load. Decide in advance: PASS = the only log lines naming `RUT_Lantern*` /
   `RUT_PufferTendrils` / `RUT_*LanternstoneWall` are the 5 price-history resolve
   failures; the canonical save loads; `RM_LanternDeepEmergence`/`Mineshaft` resolve;
   no duplicate-def error naming `RUT_LanternDeepKyberScatter` or `RUT_DeepHum`.
6. **Rollback** (any FAIL): delete the deployed RM folder, move `Mods_retired\LanternDeeps_RUT_<date>`
   back to `Mods\LanternDeeps`, restore the `ModsConfig.xml` backup. Byte-exact fallback
   if the moved folder is lost: `git archive 8a2b2364b src/RimUtinni/LanternDeeps` +
   the DLL blob from `6ce1ccf9c`.
7. On PASS, resave only on the owner's word (the canonical save is frozen); retire the
   `Mods_retired` copy after that.

## what is owed

- [x] Decide the migration route — above.
- [x] Establish what the canonical save actually holds — above.
- [x] Get `mandrake.rut.lanterndeeps` into the repo — it is, byte-exact, in history.
- [ ] Execute the swap (steps 1–7) in a load round. Not done unattended: it rewrites
      the live Mods folder and `ModsConfig.xml`.
- [ ] Only then: `LanternDeeps` joins `BIOME_LOAD_PROOF_WAVE_1`.
- Observation, not owed here: RM still ships a `RUT_`-prefixed defName (`RUT_DeepHum`,
  referenced by `RM_DeepCalm`) — a tier-prefix leftover.

## what is NOT owed
- No worldmap repaint. A biome of ours on zero tiles is the expected mid-migration
  state (`BIOME_PAINT_ONCE_AT_THE_END_1`).
- No fix to `deploy_custom_mods.py` is assumed. Whether `--pull`/`--apply` should refuse
  on a packageId mismatch between repo and game copy is a real question, but it is a
  separate call and not a prerequisite for the migration.
