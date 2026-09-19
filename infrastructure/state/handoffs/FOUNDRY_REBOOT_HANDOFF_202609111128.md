# FOUNDRY_REBOOT_HANDOFF_202609111128 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609110804`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`NURSERY_JUVENILES_CRASH_1`'s real root cause was NOT the two 2026-09-10
"cross-mod ParentName" lesson entries this window found and corrected in
`LESSONS_INBOX.md` — those were wrong (same mod, same file even, still
collided) and the crash came BACK after being "fixed" on that theory once
before. The actual mechanism: RimWorld's `ParentName` resolves via the
`Name=` attribute in a FLAT namespace, not scoped by def type — a ThingDef
and its paired PawnKindDef sharing the same `Name=` (not `defName`, which is
fine) is a dormant landmine until something actually `ParentName`s against
it. Confirmed straight from `Player-prev.log`'s XML error, not inferred.
Fixed and deployed this window; live re-verify still owed next full load.

## What the owner should see

- The live ModsConfig.xml flagged `UNRECOGNISED` (neither FULL 599 nor
  MINIMAL) on the first two game-state broadcasts this window, before
  settling to a recognized 570-mod list with 0 missing on disk. If 570 was
  not the intended list, `modlist_swap.py --restore --apply` is the fix —
  not run here since it wasn't clearly wrong and the load was already
  in progress.
- `OUTERRIM_DROIDDEPOT_PATCH_GUARD_1` (filed, blocked): `Neronix17.OuterRim.
  DroidDepot` is inactive in the current mod list, so 4 of our own weapon-tag
  patches log harmless-but-real config errors. Open question only the owner
  can answer: is DroidDepot meant to stay retired (in which case the 4
  operations should be DELETED, not guarded — "inaccurate material is
  deleted, not superseded-in-place"), or is its absence incidental to this
  session's list?
- Two background art-regen agents (per the new standing instruction) queued
  and the daemon finished: 6 proven-missing textures (AA_ShadowCharger,
  AA_Thunderox) plus 5 Star-Wars-canon "redo" creatures (Kreetle, Horax,
  Fambaa, Dragonsnake, Zakkeg), all done. NOT yet wired into any mod's
  Textures/ tree — that's a separate, undone step (`infrastructure/artpipe/
  README.md`'s own scope line). ~24 more "redo" rows from the 2026-09-10
  sitting remain unqueued on purpose — they need real design calls (biome
  reassignment, a rename+redefine) neither agent would guess at.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `NURSERY_JUVENILES_CRASH_1` — root-caused, fixed, deployed (`deploy_custom_mods.py --mod SWBestiary --apply`, VERIFIED in sync). Left `doing` deliberately: the only thing left is a LIVE confirm on the next full load (defs parse only at startup) that AlphaGenes' sweep is clean and RUT_Miasma's 9 wildAnimals refs resolve. Next action: after the next full RimWorld restart, `harvest_log.py` and check for the AlphaGenes NRE / ModsConfig-reset pattern; if clean, `rimflow close --sha <the fix commit, 05974eeb4>`.
- `WAR_LAB_CRATER_HOOK_1` — new C# assembly built and pushed (`RimMandrake.Utinni.StructureInjectionsRUT`), 47/48 selftests pass. NOT deployed — needs the game DOWN (new DLL). Next action: on the next DOWN window, deploy the assembly, then on the following UP, quicktest the ignition trigger (no in-game trigger wired yet — call `WarLabCraterMutation.Ignite()` via a debug hook or wire `CompIgniteCraterOnDestroy` onto a test thing), confirm world_commit's cache regen and save/load persistence, then close.

## Traps learned

- A background subagent using the `Monitor` tool to watch a slow external
  process re-fires a full-context notification on every tick it wakes for,
  even a purely silent "still waiting" one — cost ~130k tokens per ping in
  this session for zero new information, across several rounds, even after
  explicitly instructing it to batch into one final report. Killed it with
  `TaskStop` and checked the underlying state directly instead. Filed as
  product feedback (queued locally, not sent). Prefer checking a
  long-running daemon's state directly over asking a subagent to babysit it
  with Monitor when the daemon itself persists independently (like
  `artpiped.py`, pid stays alive across turns).
- `DEPLOY_HOLD.txt`'s own format doc says paths are relative to
  `custom_patches/`, but the `NURSERY_JUVENILES_CRASH_1` hold entry a prior
  session wrote used a full repo path
  (`src/RimStarWars/SWBestiary/Defs/...`) instead — it never actually
  matched anything, so `deploy_custom_mods.py` was never honoring it as a
  hold at all (confirmed: the dry-run plan showed it as a plain `+`, not
  `H`). Worked in this case since the fix was ready to ship anyway, but a
  malformed hold entry is a silent no-op, not a safety net — worth a sweep
  of the whole file for the same mistake sometime.
- LESSONS_INBOX.md already had two entries (2026-09-10) about this same
  crash with an incorrect root cause ("cross-mod ParentName" / "parents and
  children must share a mod") — corrected in place this window rather than
  left to mislead a future skill-curation pass. A lesson that sounds
  plausible and cites a real symptom is not automatically the right
  mechanism; this one's fix apparently didn't hold (the crash was filed
  again 2026-09-11), which is itself a hint that a lesson claiming to have
  found the mechanism is worth re-verifying before trusting it, especially
  against the actual crash log rather than a summary of it.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (2) — the next seat's queue

- `NURSERY_JUVENILES_CRASH_1` — Nursery juveniles crash EVERY game start once inheritance works: AlphaGenes ImpliedGeneDefs sweeps PawnKindDefs and element.RaceProps (race.race gette
- `OUTERRIM_DROIDDEPOT_PATCH_GUARD_1` — WeaponTags_Renormalise.xml logs 8 config errors when OuterRim DroidDepot isn't active

## Commits

```
7cb24b811 OUTERRIM_DROIDDEPOT_PATCH_GUARD_1: investigated, blocked pending a dedicated dump cycle
0f40a5151 WORLDMAP_REVIEW_REPORT drafted: provisional verdict YES pending the in-game STARE — 5-row punch list, all S/M, evidence-tagged throughout
05974eeb4 NURSERY_JUVENILES_CRASH_1: fix the ParentName Name= collision, deploy
eceea4f53 Worldmap review: rivers/roads findings — 11 river components all reaching termini, R1 8/9 pass (one inflow arm), 47 road components, 18 off-road settlements
b2370efbe Worldmap review: mutators/landmarks + settlements/biomes findings, biome render + offline STARE notes (Mycotic 10% = nightside fungal belt, coherent)
84e1aff3d File OUTERRIM_DROIDDEPOT_PATCH_GUARD_1: root-caused UP-harvest log finding
1ee7f59ea WORLDMAP_FINAL_REVIEW_1 Phase 0: all layers exported live from the loaded canonical save (43 files); bridge released; Phase 1 lanes launched
9070bc5fd Bisect verdict: nursery juveniles convicted (clean load without them, RESET 0, config 43 vs 95); NURSERY_JUVENILES_CRASH_1 filed; game UP on the full 570 list
e32234e24 DEPLOY_HOLD: nursery juveniles pulled from game copy while bisecting the AlphaGenes startup NRE
49869c49f Recovery: mods-config reset diagnosed (torn config during racing edits + AlphaGenes NRE), list restored from FULL.LATEST (570), FOUNDRY's closed port content deployed (90+421 files), game relaunched
7e73179ec PYRELANDS_WORLD_SWITCH_1: write the missing item file
5e2f5084e WAR_LAB_CRATER_HOOK_1: worldmap-tile crater mutation, in-process (build)
fd630fcda Full-auto load+export driver for the worldmap review
5abad7903 Nursery-fix reboot: pre-restart log harvested, deciders written, game cycled via Steam (standing authorization)
158fe3ef6 Lesson: cross-mod ParentName orphans defs and bricks game start
4044724f2 Nursery juveniles fix remainder: strip MayRequire (same-mod now), fix stale path comment in RUT_Miasma; hand-deployed to game copies, live at next restart
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     WORLDMAP_FINAL_REVIEW_1 Phase 2: STARE screenshot capture (~30 shots), release on completion

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimStarWars/Armoury/Patches/Armour_Leather.xml
 M src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml
 M src/RimStarWars/Armoury/Patches/Armoury_TorpedoSpeed.xml
 M src/RimUtinni/ScavengerEvents/Assemblies/RimMandrake.Utinni.ScavengerEvents.dll
?? defs.sqlite
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/done/aa_shadowcharger_v1_east.json
?? infrastructure/artpipe/done/aa_shadowcharger_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_shadowcharger_v1_north.json
?? infrastructure/artpipe/done/aa_shadowcharger_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_shadowcharger_v1_south.json
?? infrastructure/artpipe/done/aa_shadowcharger_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_thunderox_v1_east.json
?? infrastructure/artpipe/done/aa_thunderox_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_thunderox_v1_north.json
?? infrastructure/artpipe/done/aa_thunderox_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_thunderox_v1_south.json
?? infrastructure/artpipe/done/aa_thunderox_v1_south.manifest.json
?? infrastructure/artpipe/done/dragonsnake_v1_east.json
?? infrastructure/artpipe/done/dragonsnake_v1_east.manifest.json
?? infrastructure/artpipe/done/dragonsnake_v1_north.json
?? infrastructure/artpipe/done/dragonsnake_v1_north.manifest.json
?? infrastructure/artpipe/done/dragonsnake_v1_south.json
?? infrastructure/artpipe/done/dragonsnake_v1_south.manifest.json
?? infrastructure/artpipe/done/fambaa_v1_east.json
?? infrastructure/artpipe/done/fambaa_v1_east.manifest.json
?? infrastructure/artpipe/done/fambaa_v1_north.json
?? infrastructure/artpipe/done/fambaa_v1_north.manifest.json
?? infrastructure/artpipe/done/fambaa_v1_south.json
?? infrastructure/artpipe/done/fambaa_v1_south.manifest.json
?? infrastructure/artpipe/done/horax_v1_east.json
?? infrastructure/artpipe/done/horax_v1_east.manifest.json
?? infrastructure/artpipe/done/horax_v1_north.json
?? infrastructure/artpipe/done/horax_v1_north.manifest.json
?? infrastructure/artpipe/done/horax_v1_south.json
?? infrastructure/artpipe/done/horax_v1_south.manifest.json
?? infrastructure/artpipe/done/kreetle_v1_east.json
?? infrastructure/artpipe/done/kreetle_v1_east.manifest.json
?? infrastructure/artpipe/done/kreetle_v1_north.json
?? infrastructure/artpipe/done/kreetle_v1_north.manifest.json
?? infrastructure/artpipe/done/kreetle_v1_south.json
?? infrastructure/artpipe/done/kreetle_v1_south.manifest.json
?? infrastructure/artpipe/done/zakkeg_v1_east.json
?? infrastructure/artpipe/done/zakkeg_v1_east.manifest.json
?? infrastructure/artpipe/done/zakkeg_v1_north.json
?? infrastructure/artpipe/done/zakkeg_v1_north.manifest.json
?? infrastructure/artpipe/done/zakkeg_v1_south.json
?? infrastructure/artpipe/done/zakkeg_v1_south.manifest.json
?? src/RimStarWars/Armoury/Textures/Things/Item/Resource/Crystal/
```

