# BENCH_REBOOT_HANDOFF_202610102358 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610102057`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Art review is STILL PAUSED (owner 2026-10-10 ~14:00), and the focus is validation, debugging and mod maturity.** This session turned his first answer, *"(1) … Analyze GimmeSomeSlack for any additional unworked items. Then go to FlowWorks and do the same."*, into 8 filed tickets plus 4 rulings. The sweep is at `Transient/unworked_items_2026-10-10.md`. Biggest structural ruling: the **hose reel moves from GimmeSomeSlack into FlowWorks**, and GSS becomes cables, conduits and electricity only.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Selftests are GREEN** (0 fail, 0 crash; 290 pass + 91 skipped-unchanged + 2 deployed-tier). The previous handoff's "297/369, ~70 unaccounted" was cache skips, not hidden failures.
- **Four rulings recorded as items**: the hose reel moves to FlowWorks (typed); power theft, if caught, drains goodwill steadily like living too close to a settlement (typed); unroutable cords dive into the wall and out (card); the 12 unused liquid terrains stay as a palette (card, item closed).
- **Story card 14b** (the second launch, typed) is recorded in `design/Jawa/story_sitting_cards_2026-10-10.md`.
- **Owed with the game DOWN** (bridge was FREE at wrap but the game was running): TheRot redeploy (new oyster/pale-tree contact cells), the JawaBench companion DLL, and the Ollopom beauty DLL. All are filed for FOUNDRY.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `ROT_FOOTPRINT_PATCH_DEPLOY_NEW_OYSTER_CELLS` — filed for FOUNDRY; NEXT: with the game closed, deploy TheRot + `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`, then `run_selftests.py --tier deployed`.
- `OLLOPOM_BEAUTY_DEPLOY_WAITING_ON_GAME_CLOSE` — filed for FOUNDRY; NEXT: in the same game-down window, `deploy_custom_mods.py --compose biomes --apply` then `--mod SWBestiary --apply`.
- `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST` — owner-ruled, unbuilt; NEXT: FOUNDRY design pass for the move (reconcile with `RM_LiquidHose`) before any code.
- `POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK` / `UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS` — owner-ruled, unbuilt; NEXT: FOUNDRY builds; the cord dive needs the owner's eyes in game.
- `GSS_PROOF_ALL_RETRY_AFTER_THIRTY_FIXES` / `GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED` / `LAVA_LIQUID_BUILD_PROMISED_BY_CARD` / `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` — filed for FOUNDRY; NEXT: claim in that order (live proof run first while the fix waves are fresh).
- `ART_REVIEW_PAUSE` — owner ruling, no item; NEXT: touch no art until he lifts it; then ask him for comments on the Greentide Peko-peko preview row.
- `WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE` / `CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE` / `WARLAB_GARRISON_DESIGN_EARLY_BLAST` / `SEKKULAATH_RISING_DESIGN_CRATER_EVENT` — BENCH's, untouched (validation first); NEXT: draft each as a short option card when he wants design time.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- run_selftests skips tests unchanged since their last PASS; a low PASS count is skips, so read the `evidence:` line (filed: lessons 20261010T235838Z).
- Landing via a scratch clone leaves the seat clone behind origin, so RED runs become stale-tree artifacts; sync with explicit-path stash + pull --rebase (filed: lessons 20261010T235838Z).
- Pushing the same ledger commit twice (scratch clone, then rebase) leaves byte-identical duplicate events; legal by invariant 2, and the reader-invariant test now collapses them (see: d792cd312).
- `rimflow file --owner-said` writes to OWNER.jsonl, not BENCH.jsonl; commit that shard too (see: dd73e8269).

## Closed since the last handoff (2)

- `LIQUID_PALETTE_DECIDE_KEEP_ALL_TWELVE` — 3eef924d2
- `WITCHES_OYSTER_MASK_RESTORE_PIN_DRIFTED` — 2390b186b

## Filed and still open (7) — the next seat's queue

- `GSS_PROOF_ALL_RETRY_AFTER_THIRTY_FIXES` — GimmeSomeSlack: one live proof_all (carry, relay, maze, style) after the 10-06 and 10-09 fix waves; see Transient/unworked_items_2026-10-10.md
- `GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED` — GimmeSomeSlack: settings-flip proofs for the ~20 untested aerial and hose settings; see Transient/unworked_items_2026-10-10.md
- `LAVA_LIQUID_BUILD_PROMISED_BY_CARD` — FlowWorks: add the lava liquid the owner promoted by card 2026-09-24 (missing from the liquid registry); see Transient/unworked_items_2026-10-10.md
- `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` — FlowWorks rivers: prove the 11 river settings toggles owed in validation.py, and the 10 untested river-walk lines (flier/flood lines need the owner wa
- `UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS` — GimmeSomeSlack: an unroutable cord draws diving into the wall and re-emerging (GPT read A7; decision taken by question card 2026-10-10); diagrams in T
- `OLLOPOM_BEAUTY_DEPLOY_WAITING_ON_GAME_CLOSE` — Deploy the built Ollopom outdoor-beauty DLL (da4180f3f) when the game is closed: deploy_custom_mods.py --compose biomes --apply, then --mod SWBestiary
- `ROT_FOOTPRINT_PATCH_DEPLOY_NEW_OYSTER_CELLS` — With the game down: redeploy TheRot (f66497eb2 regenerated RotGiants_HugeFootprint.xml with Witches Oyster b/c + Pale Tree variant contact cells) and 

## Commits

```
87a24b3bc Ledger: close WITCHES_OYSTER_MASK_RESTORE_PIN_DRIFTED (fixed at 2390b186b)
d792cd312 Reader-invariant test: baseline must collapse identical events too
52c863b12 Tool snapshot lacked jawa/map_comp_timing (91f9c0a14); refreshed offline from C# source
72db6bd92 Mod audit: two scripts hard-coded the LocalLow path instead of importing game_paths
f66497eb2 Rot giant footprints: regenerate with the fixed mask tool (Witches Oyster b/c, Pale Tree variants)
f466e8b8b Ledger: owner-quoted items for hose migration and power theft
6deed5c62 Mod audit: owner rulings C01-C04 (decisions taken by question card)
a853fdd76 Mod audit: re-merge on regenerated facts; lost Cherry Picker backstory cuts action; GPT package refreshed
b51a41ef5 Mod audit facts: labelled dependants, Textures-only memory, Cherry Picker shells, gated defs, rejected sources
efbf28b38 Two new scripts hard-coded the LocalLow path instead of using game_paths
2390b186b HugeThings mask tool ignored a patched graphicClass; repin Witches Oyster and Pale Tree variants
3c13deaf2 Ledger: file the Ollopom beauty deploy so it survives the handoff
6a291fbf2 FOUNDRY: HugeFootprints proof closed, awareness criteria verified, bridge released
00a2089da Ledger: OWNER shard sync (ROT_GIANTS_DENSITY_JUDGE close)
5af889844 HugeFootprints fix proven live on the Rot (62.6 -> 0.98 ms/tick, 13 -> 58 TPS); awareness meters measured
61257ac70 Mod audit: GPT_PACKAGE.md generator and first package (pre facts regen)
413385236 Mod audit: merge checker amendments into MASTER_REGISTRY; 23 owner cards; no-decision actions
a1c8d8933 Mod audit check group 1: 152 mods checked
bf2593f2e Mod audit check group 4: 150 mods checked
fe013d0f9 Mod audit check group 1: 111 mods checked
... 76 more: git log --oneline eebc08b54..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-10T23:13:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/abyss_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/blue_desert_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/cauldron_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/contagion_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/deep_desert_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/desert_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/feverwood_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/feverwood_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/floodedcanyon_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/floodedcanyon_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/gelatinousslime_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/greentide_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/greysea_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/greysea_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/lanterndeeps_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/leaningscrub_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/miasma_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/nightsideice_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/pyrelands_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/rustcathedral_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/sheets_state.json   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/thechill_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/theforge_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/theforge_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/therot_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/thescald_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/thesump_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/twilightsea_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/warscar_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/wasteland_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/wasteland_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/webwork_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/weepingstones_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/modcheck/fixtures.json   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
 M infrastructure/state/ledger/events/BENCH.jsonl   — BENCH: served review-sheet HTML/logs/state (art paused; HTML commits are hook-blocked by design)
?? conversations/   — pre-existing untracked leftovers from earlier sessions, not this window
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   — pre-existing untracked leftovers from earlier sessions, not this window
?? deployed/config/ModsConfig.before-tier-flowworks.xml   — pre-existing untracked leftovers from earlier sessions, not this window
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   — pre-existing untracked leftovers from earlier sessions, not this window
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   — pre-existing untracked leftovers from earlier sessions, not this window
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   — pre-existing untracked leftovers from earlier sessions, not this window
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   — pre-existing untracked leftovers from earlier sessions, not this window
```

