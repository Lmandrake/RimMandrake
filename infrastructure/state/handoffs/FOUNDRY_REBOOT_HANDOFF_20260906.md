# FOUNDRY_REBOOT_HANDOFF_20260906 — READ FIRST on wake

## spec

RESTART HANDOFF 2026-09-06 (FOUNDRY, pre-agent-restart). Read this whole
file before doing anything else this session — it is the state and the
ranked open list, not just a summary.

## State

Bridge FREE. Working tree clean except pre-existing BENCH-owned BeastLairs
edits (not mine, leave alone) and routine auto-rendered files
(`codebase_health_last.json`, `queue/BENCH.md`). Game was last left UP on
`gravship_scratch_d` (a disposable test save) after a full launch-travel-land
round trip proved `GRAVSHIP_LANDING_CRUSH_1`'s fix live; current game process
state at restart time not re-checked — verify fresh (`./game`).

## Closed tonight

- **GRAVSHIP_LANDING_CRUSH_1** — owner ruling: retired our custom mod,
  switched to Land On Anything (`nep.landonanything`), settings forced
  (`allowedToSqishRoofs`/`allowedToLandOnAnyTerrain`=false) and proven
  durable via a `reload_mod_settings` round-trip from disk. Full
  launch/travel/land cycle live-verified end to end, including a real
  obstacle-crush (two placed walls, zero survivors in a rect-scan of
  28,031 things at the landing site).
- **REGISTER_CORPSE_CROSSCHECK_1** — two real `gen_creature_register.py`
  bugs root-caused and fixed (illusory corpse cross-check explained by
  humanlike-exclusion ordering; "flies" flag was keyed on
  `flightSpeedFactor`, a universal default, not the real `canFlyInVacuum`
  gate).
- **WEAPONTAGS_RENORMALISE_STALE_DEFS_1** — two dead `guy762_brifle_*`
  defName refs removed, verified against disk (the def dump is 3-mods
  stale), not guessed.

## Eleven agents completed and independently verified overnight

1. **Blocked-item sweep** — re-verified every stale `block` event against
   current state. Found `HELIX_TELLUROX_SHELL_LOAD_CRASH_1`'s block premise
   is dead (BENCH's own 2026-09-04 note already overturned the crash
   attribution, the real fix is deployed at `3468e2a0`) but correctly did
   **not** unblock it — ownership sits with `OWNER` since a 2026-09-04
   transfer, and the cross-seat-ownership guard means only he/BENCH can
   action it. Left a note recommending the unblock.
2. **Armoury hand-authored review** — all clean, plus a stale-path fix in
   `JawaArmoury.csproj`.
3. **Property/Graffiti review** — 46 files, all clean; re-verification of
   an already-solid prior pass, no new bugs.
4. **Tellurox art** — resolved by tracing the already-promoted
   `karrask_opt3.png` mockup directly (chroma-keyed, sized to Cindermare's
   own drawSize convention) instead of attempting fresh generation —
   avoided repeating 5 historically-failed generation attempts.
5. **Small-pool cleanup** — `weapon_tag_audit.py`, SeasWaterline, Doctrine
   About.xml all clean; found and fixed the WeaponTags bug (closed above).
6. **Generator/hand-edit desync investigation** — filed
   `ARMOURY_LEATHER_GEN_DESYNC_1` and `PAWNFLAVOR_MEGAFAUNA_GEN_DESYNC_1`.
   **Do not fix either blind**: the real fix needs editing shared
   generator input data (`animals.csv`, `pawn_flavor_phase2_prose_draft.json`)
   to exclude 4 mods whose retirement is only HALF done — repo-side
   patches say retired, but the live `ModsConfig.xml` still has all 4
   active. This needs the owner to actually execute the ModsConfig
   deactivation first; editing generator inputs for still-active mods
   would be premature and could break real live content.
7. **Sarlacc design draft** —
   `design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md`: three
   life-cycle stages (swimmer/anchored/cistern, dead=throat), a
   press-not-stomach physics model, dungeon concept, deep-desert
   standing-water carve-out, and nine open forks flagged for the owner.
   Deliberately NOT built as game content — review material only.
8. **Tiles-frozen-stamp investigation** (`TILES_STAMP_VERIFY_1`) — caught
   that the original filing conflated two unrelated things (the actual
   stale-stamp cause is 14 legitimate 2026-08-23 surgical edits, not the
   "~1650 shrubland→Desert repaint" which turned out to be
   `WORLDMAP_DESERT_BAND_REPAIR_1`'s own not-yet-executed proposal, measured
   against a different file entirely). Did NOT restamp — only the owner
   re-freezes. Built `warn_if_stale()` tooling wired into 3 reader scripts.
   Exact restamp command left in the item.
9. **Tree-graphics build** (`TREE_GRAPHICS_OWNERSHIP_1`) — `RUT_SweetlineTree`
   def built and validated; found and neutralized the BetterTrees
   rescaling mechanism (new defName is immune by construction; shipped an
   immunity patch as insurance anyway). Art generation BLOCKED all night —
   14 failed Codex attempts, same timeout signature, a persistent
   `codex.exe`/`codex-code-mode-host.exe` pair unchanged for hours. NOT
   killed — not provably dead, not mine to touch (real risk of destroying
   another window's live work if it's actually busy, not wedged).
10. **235-file Armoury vendor-pool review** — 225 clean, 4 real bugs fixed
    (swapped sound clips, a silently-ignored lowercase `inherit="False"`,
    a dead empty comps tag, 5 ThingDefs carrying a live unresolvable comp
    despite being on their own exclusion manifest), 3 new items filed:
    `KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1`,
    `KOTORCORE_ABSORPTION_MISSING_TEXTURES_1`,
    `KOTORWEAPONS_ABSORPTION_CONTENT_NITS_1`.
11. **Final art-generation retry** — confirmed Codex still blocked, same
    signature as #9, correctly stopped rather than forcing further
    retries.

## Session-process fixes made (apply going forward, not just tonight)

1. **Two agents claimed "committed and pushed" while leaving
   `infrastructure/state/CODE_REVIEW_STATUS.json` and/or
   `ledger/events.jsonl` uncommitted.** Caught both; this is now a
   standing post-completion check (`git status --short` on both files
   after every agent, not just review waves).
2. **Item detail files were being written to
   `infrastructure/state/queue/items/` instead of the canonical
   `infrastructure/state/items/`** — `rimflow show` only reads the latter,
   so misplaced files silently render as "no sections." Fixed 4 of 5
   misplaced files; left `DROID_SYSTEM_EMBRACE_1.md` exactly alone since
   it belongs to BENCH (the cross-seat-ownership hook correctly refused
   my first attempt to touch it — flagged via a note instead of moved).
3. **A bare `git commit` with no pathspec commits the WHOLE staged index**,
   not just what was just `git add`ed — caught this sweeping up another
   window's unrelated staged deletion of `src/RimMandrake/RustChrome/`
   earlier in the evening (restored, fixed). Always commit with explicit
   pathspecs in this shared worktree.

## Still open, ranked

1. **Codex image generation** — check whether the lock/process at
   `/mnt/c/Users/Mandrake/.codex/thread-writer-locks/` has cleared before
   retrying `TREE_GRAPHICS_OWNERSHIP_1`'s art (exact prompt/canvas already
   written into the item).
2. **`HELIX_TELLUROX_BUILD_1` + `TREE_GRAPHICS_OWNERSHIP_1`** both need a
   live bridge check once the game is up (spawn/render/butcher
   confirmations, spec'd in each item's own verify section) — can close
   `HELIX_TELLUROX_SHELL_LOAD_CRASH_1` on the same relaunch per the sweep
   agent's finding (see #1 above).
3. **`ARMOURY_LEATHER_GEN_DESYNC_1` / `PAWNFLAVOR_MEGAFAUNA_GEN_DESYNC_1`**
   — owner-scope call on the 4-mod retirement completion, see #6 above.
4. **`SARLACC_NATIVE_HABITAT_1`** draft + nine forks await owner review.
5. **`WORLDMAP_DESERT_BAND_REPAIR_1`** — untouched, needs the owner
   present (frozen world map).
6. **`BEHEMOTH_TEXTURE_MISSING_LIVE_1`** — investigated, likely a benign
   vanilla pack-overlay probe, not our bug; low priority.
7. **The 3 new KOTORWEAPONS/KOTORCORE absorption items** from the vendor
   pool review — all need game-up to verify.

## criteria

This is a handoff record, not a task with completion criteria — close it
once its content has been read and superseded by the next session's own
handoff, per this project's "superseding a doc means writing into it"
convention.
