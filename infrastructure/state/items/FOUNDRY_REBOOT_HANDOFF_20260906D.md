# FOUNDRY_REBOOT_HANDOFF_20260906D — READ FIRST on wake (late evening, 2026-09-06)

Follows `FOUNDRY_REBOOT_HANDOFF_20260906C`. Owner-requested agent reboot.
Everything below is committed and pushed. **Game/bridge state is the last
section — read it before touching the game.**

Owner's instruction for the whole session, verbatim: *"Efficiently fan out with
sub agents to make progress."* Three waves, 15 subagents, **16 items closed**.

## 🔑 The one thing to carry forward: generators anchored on their own output

Five separate defects this session, all the same shape — **a generator's idea of
"the original value" came from somewhere its own writes could reach, or from a
snapshot that had moved on.** None of them logged anything. If you touch a
generator, this is the first thing to check.

| generator | anchored on | what it did |
|---|---|---|
| `gen_megafauna_yield` | the live dump — the game **with its own patch applied** | churn-guard matched each value against its own last write and **dropped 77 ops**; Muffalo wool 120→72, Megasloth 200→120 |
| `gen_armour_patch` | a frozen `observed/` dump predating a retirement | re-emitted `FindMod` blocks for four retired mods |
| `gen_armoury_patch` | our own post-patch values | flattened seven blaster bolts to 33, destroying Low<Mid<High |
| `gen_armoury_patch` | `patch_ledger.json`, where **87 originals are `-1`** | ops on those xpaths oscillate in/out on alternate runs — `PATCH_LEDGER_MINUS_ONE_OSCILLATES_1`, still open |
| a run of `gen_megafauna_yield` | a **minimal-13-mod-list** dump | collapsed the file 32 groups → 4; found uncommitted in the tree and reverted, bad output kept at `Transient/MegafaunaYield_MINIMAL_LIST_REGEN_BAD_2026-09-06.xml` |

**Three defences now exist. Use them.**
1. **`--out DIR`** on `gen_armour_patch.py`, `gen_armoury_patch.py`,
   `gen_megafauna_yield.py`. Always run to a temp dir and diff at the level of
   **xpath SETS** — line diffs are useless, groups reorder. Never regenerate in
   place until the diff is understood. A verifier last session had to
   `git checkout` after running a generator with no `--out`.
2. **`infrastructure/state/facts/retired_mods.json`** + `Utils/retired_mods.py` —
   one exclusion list, read by both dump-eating generators.
   `selftest_retired_mods.py` fails if any of 675 patch XMLs names a retired mod.
3. **Before any dump-eating run: read `manifest.json` in the capture and confirm
   `modCount` is the full list.** `Core/Biotech/Anomaly/Odyssey` as the only mod
   groups is the signature of a minimal-list run.

⚠️ **The property nobody asserts yet** is idempotence: two consecutive `--out`
runs producing identical output would have caught all five. That is the criterion
on `PATCH_LEDGER_MINUS_ONE_OSCILLATES_1` — worth doing generally.

## Closed this session (16)

**Generator/desync family:** `ARMOURY_LEATHER_GEN_DESYNC_1` (548432d9),
`MEGAFAUNAYIELD_GEN_BEHIND_1` (589d9c9b), `ARMOURY_GEN_HANDEDIT_DESYNC_1`
(f95eacfc), `ARMOURY_SWMODS_MODNAME_GAP_1` (62fbc541),
`ARMOURY_MELEEPOWER_STALE_1` (da3a06e8 — **false alarm**, the XML was current and
the README prose was stale).

**Live defects found and fixed:** `BEHEMOTH_TEXTURE_MISSING_LIVE_1` (74a53711),
`ARMOURY_ABSORBED_KOTORCORE_DUPES_1` (a24cda4d), `LOAD_CONFIG_ERROR_SWEEP_1`
(7f781d1e), `DOCTRINE_LOADAFTER_STALE_1` (bf99382b).

**Diagnosis / mechanism named:** `WILD_ANIMALS_PADDED_LISTS_1`,
`DROID_DONOR_PATCH_GATE_1` (validation-only), `DROID_RETIREMENT_ORDER_ASSERT_1`
(0f430178), `TILES_STAMP_VERIFY_1` (104bb236), `RESEARCH_VALIDATOR_BUILD_1`
(already built, re-verified).

Plus `selftest_one_path_seam.py`, failing since `dafe7fb6` — two rimbench files
went round the LocalLow seam instead of through `game_paths`.

## 🔴 Three findings the owner should see (all in COLD_LOAD_RUN_SHEET_4)

1. **Seven `RSW_*_Blaster_Bolt` damages moved off a flat 33 to
   24/25/26/26/28/29/30**, restoring Low<Mid<High. That is what the doctrine
   computes from pristine anchors and it corrects HEAD's flattening — but
   **nobody has RULED on the numbers.** He may want them different. Shipped
   deliberately with the flag raised, not slipped in.
2. **918 KotOR defNames revert to the donor's own content at the next load.**
   `Absorbed_KotorCore` was deployed against its own header while
   `guy762.mm.kotorcore` is still active; ours silently won all 918
   (`DefDatabase.AddAllInMods` `Remove()`s before `Add()`ing a cross-mod
   duplicate, so nothing ever logged), and 99 differ in a real leaf value. We
   were shipping a frozen 2026-08-31 snapshot **over the donor's own newer
   defs, for no gain.** 117 files undeployed, hold written into
   `src/DEPLOY_HOLD.txt`. If a KotOR item's art, sound or stat looks different
   next session, that is this, and it is intended.
3. **`mlie.choosewildanimalspawns` is gone from his live list.** That mod was
   padding every biome's `wildAnimals` to exactly 1024
   (`ChooseWildAnimalSpawns.Main.ApplyBiomeSettings()`, a whole-field `Traverse`
   overwrite of `AllBiomes`); the symptom vanished with it — 08-29 capture had
   all 81 biomes at 1024, the current one has none, max 205. **If the
   unsubscribe was accidental, the padding comes back.**

## What is half-done, and where it stops

`handoff.py --check` names four items started in this window and still open. Three
are the previous seat's map-generator thread, unchanged by me — `MACRO_GENERATOR_V0_1`,
`MAPGEN_GL_SHEET_1`, `MAPGEN_PAINTER_V1_1`; handoff C is their authority and nothing
this session touched them.

The fourth is mine and deliberate: **`DEV_LOG_AUTOOPEN_SUPPRESS_1`**. The Harmony
prefix on `Verse.Log.TryOpenLogWindow` already existed, is built and **deployed**, and
gained a `testerror` action so it can be proven. Not closed because the criterion is
unmet and the reason matters: **JawaBench's init is LAZY** — it fires on the first
`jawa/` tool call, so in a plain play session with nothing driving the bridge the
prefix may never install and errors will still pop. Next action is run-sheet entry 2,
and it must be taken BEFORE touching the bridge or the test invalidates itself.

## Filed and ready to pull (7)

`ARMOURY_LOADAFTER_STALE_1` — **the biggest**: Armoury declares 3 `loadAfter`
packageIds against ~40 mods its patches target. · `PATCHMODS_LOADAFTER_SWEEP_1`
(StarWarsPatches, UtinniPatches; do it as one sweep + a selftest) ·
`PATCH_LEDGER_MINUS_ONE_OSCILLATES_1` · `ARMOURY_SUBSTRING_RUNG_TRAP_1` ·
`DOCTRINE_LOADAFTER_STALE_1`'s siblings · `RESEARCH_TAB_VIEWCOORD_COLLISION_1`
**needs reopening** — the fix at `14cf4186` did NOT take; three logs captured
hours after it deployed still show the collision, and the mechanism traces to
vanilla's own `ResearchProjectDef.GenerateNonOverlappingCoordinates()`, which a
static viewCoord edit may not be able to beat.

`FLUID_CANAL_DEBUG_SURFACE_1` is now `needs game-up` — see run sheet entry 1.

## Traps learned (also for LESSONS_INBOX)

- **ASCII `strings` cannot see .NET string literals** — they are UTF-16LE. Three
  whole-tree sweeps for `wildAnimals` found nothing while a DLL was overwriting
  that exact field. Use `strings -el` and confirm with `ilspycmd.exe -t`. A clean
  ASCII sweep of a managed binary is **not** evidence of absence.
- **A dump's `duplicateDefName`/`duplicateOwners` fields do not exist** in the
  2026-09-05 capture — `measure find` returns MEASURED 0. I put that instrument
  in an item spec and it was wrong. The DefDatabase holds only the winner, so
  the dump's `package_id` per defName **is** the empirical answer to who wins.
- **A cross-mod duplicate defName logs NOTHING.** `AddAllInMods` `Remove()`s then
  `Add()`s; the "Adding duplicate" `Log.Error` is unreachable for that case.
- **`zsh` does not word-split unquoted vars** — `git commit -- $PATHS` passes one
  giant pathspec and fails. Write the paths out.
- **A batched `git add`/`commit` can silently half-succeed** on an `index.lock`
  collision with BENCH. One of my two commits landed and the other left its files
  staged. **Always `git status` after a batched commit.**
- `DebugActionType.ToolMap` is **not** a separate menu — `DebugTabMenu_Actions`
  adds those to the same `Actions` root with a `T: ` label prefix.

## New this session: handing off is now a command

Owner asked for it mid-session: *"Is there a way for an agent to automatically
prepare for agent reboot when it finishes a big wave... Then it could just say
HANDOFF READY at the end and I could reboot myself while keeping things in cache."*
Plus: *"It should be fired especially when it says 'Ok, that's all I have for now,
waiting for new items'... and then NOT do so again unless new work does come in."*

```
python3 src/RimMandrake/Utils/handoff.py          write the skeleton (it gates first)
python3 src/RimMandrake/Utils/handoff.py --check  gates + unfilled-section scan
```

Doctrine is in `infrastructure/agents/FOUNDRY.md` and `CHARTER.md`. Three things
worth knowing before you use it:

- **The trigger is the sentence "that's all I have for now."** Do not report an
  empty queue and then sit on a warm context — report it BY handing off.
- **It gates before it writes**: unpushed commits, a bridge you still hold, and
  items you started this window that are neither closed nor written into "What is
  half-done". Being NAMED in the handoff discharges the last one — some work is
  legitimately mid-flight, and a gate you cannot satisfy honestly teaches you to
  pass `--force`.
- **Say HANDOFF READY once.** With no closes, filings or commits since the last
  handoff it prints ALREADY HANDED OFF and writes nothing.

⚠️ Two bugs in its first draft are recorded in `selftest_handoff.py`, both of the
kind that leave a gate looking fine while doing nothing: it selected the
uncommitted handoff it was writing as its own window start, and the doing-check had
no window at all and named 47 items from three sessions back. **A gate that fires
every time is a gate nobody reads.** The selftest's assertions are mostly about the
gate being silent when it should be, because that is the half that broke.

## Game / bridge / mod-list state at wrap

- **Game: DOWN** (`./game` reads NOT RUNNING / recorded DOWN). Never started this
  session; every item was worked offline.
- **Bridge: FREE** since 21:32, never taken.
- **Deployed this session** (all need a restart to take): `StarWarsPatches`
  (Behemoth pack art), `Armoury` (4 patch files, **and 117 files UNDEPLOYED**
  from `Defs/Absorbed_KotorCore`), `Doctrine` (MegafaunaYield + About),
  **JawaBench companion DLL** rebuilt `--gm` and deployed with the new
  `jawa/type_visibility` tool.
  ⚠️ `build.py` needs **`--gm`** or it reports 20 tools LOST and refuses — the
  deployed copy was built with it.
- **Uncommitted and NOT mine**: `src/RimStarWars/BeastLairs/About/About.xml`,
  `.../RSW_BeastLairs_Buildings.xml` (present at session start, another seat's),
  and `infrastructure/state/codebase_health_last.json` (generated state).
- **Selftests 39/40** — `selftest_cli.py` times out under cross-window
  contention; `selftest_one_path_seam` was fixed this session, and
  `selftest_retired_mods`, `selftest_retirement_order` and `selftest_handoff`
  are new.
- **`COLD_LOAD_RUN_SHEET_4` has six readings queued** for the next full-list load.
  Read it before launching anything.
