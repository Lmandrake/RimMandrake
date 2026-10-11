# FOUNDRY_HANDOFF_202610111255 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610101109`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The seat clone `/home/mandrake/rm/foundry` was replaced 2026-10-11 ~03:45 by a fresh clone (the old one, 244 commits behind and dirty, is kept whole as `/home/mandrake/rm/foundry_old_20261011`; it holds untracked design files under `design/RimMandrake/mod_audit/` and `mod_deepdive_*` that may be unpublished work — look before deleting). Ledger events written by `rimflow` land in the seat clone's shard: commit that one path, `git pull --rebase origin main`, `git push origin HEAD:main` as THREE SEPARATE Bash calls (the pre-push hook refuses a compound command, judging HEAD before the pull). Agents work in their own `--filter=blob:none` clones (each ~14 GB once selftests stage; delete finished ones after checking `git log @{u}..` and untracked item/design files — the item prose for PACK_ANIMALS_RESTORE_EMPTY_SADDLES was lost that way once).

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Questions awaiting him (cards asked 2026-10-11 ~01:40; answered ones are enacted): (1) CRACKEDLANDS_FULL_RENAME_1 — built in `scratchpad/w4` clone, NOT pushed, blocked on his typed words to move 13 owner-kept PNGs (ART_VERSION_WRANGLING_1 guard); the branch is stale against origin. (2) FLOOD_SWITCH_OFF_PROVE_SPILLS_GO_NOWHERE — with 'Spilled liquid fills channels properly' off, spills place almost nothing: accept and fix the tooltip, or give 'off' a real meaning. (3) P14 mission tank goal: on a truncated tank listing even a FAIL reads UNMEASURED — keep? (4) TAR_GLASS_EDGE_DECIDE_INSIDE_THE_CHANNEL for BENCH. (5) CANON_MATERIALS L9 reading: uses that were ALREADY hard stay hard; the 2026-10-03 duranium-for-large-frames / doonium-for-cores rule was never in any recipe so those are preferences now — confirm, else ~65 recipes change. (6) TITAN_BREAKTHROUGH: a tame titan never smashes its own faction's buildings (agent's call) — lift? (7) RECLAMATION woken-count default 10 is a placeholder. (8) Stygium formation weight 0.0833 in Lantern Deeps is provisional. (9) Rakata/FlowWorks GREEN-MIN must be recorded under tier `fw_gss_sitting` (not donor-clean: Alpha Biomes cannot be forbidden). (10) FlowWorks `## north star` is still DRAFT — his validation. (11) Art review sheets ready, nothing installed: `Transient/icon_outline_batch4_sheet_20261010.html`, `Transient/sluice_panning_warden_sheet_20261010.html`; Dakkra rest N/S installed (749ada8f0); canon materials art (5 jobs) and RM_MineShaft_v1, rot_ambrosyx_v1, RM_Meal_SlimeAmbrosyx_v1 render queued. (12) The owner-said guard was tightened (ab1dab8b6 + provenance/tamper/shard-write hooks): 23 of 572 past `--owner-said` commands would now be refused — cite ONE of his messages in backticks; hooks take effect from the next session. (13) Skorra: cut was Leaning Scrub only; art held for a review sheet.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG` — new mod `mandrake.rm.mineshaft` built offline (4a6a9a837), Mines 2.0 not yet retired; NEXT: with the game down, deploy mineshaft+Armoury, swap Mines 2.0 and its LK compat off the live list and FULL.LATEST, record in retired_mods.json, delete RSW_MineShaftCanonGate.cs, re-save the canonical save once.
- Live sitting for FlowWorks+GimmeSomeSlack — 106 criteria owed (74 fit one sitting); NEXT: follow `Transient/flowworks_gss_owed_20261011.md` (deploy first: the game runs old FlowWorks f70d2283b / GSS 9536a39f7 DLLs; use `modset_builder.py --tier fw_gss_sitting`; NEVER run modcheck run blind — it rewrites ModsConfig).
- `CANON_MATERIALS_BUILD_1` — 9 PASS, L10 live load owed; NEXT: one minimal-list load after deploying Armoury (RSW_MineShaftCanonPolicy, RSW_BeskarSmelt.cs Harmony, zeroed-ore gates).
- `AMBROSYX_SOURCE_BUILD_DISH_BEFORE_SHROOM` / `GELATINOUSSLIME_PIT_SOLVENT_1` — built offline; NEXT: live check the Rot spawns RM_AmbrosyxFungus and the slime pit cooks RM_Meal_SlimeAmbrosyx.
- `PACK_ANIMALS_RESTORE_EMPTY_SADDLES` — free-tier carriers shipped (b165a4683); 42 biome rows still need per-biome sittings; NEXT: take them one biome at a time at each sitting (do not sweep).
- Art events log — rotated (aa99f1aeb): `art/events/BENCH.jsonl` 962 KB + `archive/`; NEXT: any script reading `art/events/*.jsonl` by glob must use `artledger.shard_files`; BENCH's clone should pull before appending.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A hook checks HEAD before a compound command runs, so `git commit && git pull --rebase && git push` is refused even when it would pass; split it (filed: LESSONS, 20261011T125553Z-FOUNDRY-pre-push-pretooluse-ledger-hook-judges.md).
- `selftest_winstage` shared one staging folder across clones (fixed 00b23418f: per-clone hash); set `WINBUILD_ROOT=/mnt/d/Luke/dev/_rmbuild/<name>` anyway (filed: LESSONS, 20261011T125554Z-FOUNDRY-subagent-report-that-ends-handoff-ready.md).
- A subagent report ending 'HANDOFF READY' is its own artifact, not a handoff (filed: LESSONS, 20261011T125554Z-FOUNDRY-subagent-report-that-ends-handoff-ready.md).
- Deleting a scratch clone loses untracked item prose: check `git status` for untracked items/design files, not just unpushed commits (filed: LESSONS, 20261011T125554Z-FOUNDRY-before-deleting-scratch-clone-check-untracked.md).

## Commits

```
0ed71b372 Add repair_torn_art_events.py (torn art-events tail -> quarantine) and allow-list it in the shard-write hook
d93d8006e Code review: Pyrelands validation.py CLEAN at a542f6539
b43cefb18 Pyrelands validation: teardown survives a FAIL, fulgurite bound sound, live breaker gate
9da1f79ae Notes: pickAS owner-said writer census, shard-write hook replay, what stays open
33db770cf Refuse direct writes to ledger, art-ledger and code-review shards (new PreToolUse hook)
ec10fae93 Live proofs: guard the Verse.Log 10,000-message cap; v2 full-list staging
c4eee0027 Prove owner-said quotes in modcheck validate/review and art.py install/purge
96893677f Pyrelands validation: fulgurite bound by strike lower bound, settings restored to prior values
6af7e0c13 Owner-said review: note A36/A37 closures and remaining residuals
3c41b9a8c Prove owner-said quotes where consumed: rimflow, broadcast.py, apply_blanket_ruling.py (closes A36)
4badee467 Owner-said matcher extracted to owner_said_provenance.py (hook behaviour unchanged)
04c528b9c Hook: refuse any agent write to a session transcript (closes A37)
c8142298b Ledger: FOUNDRY shard sync (Pyrelands readiness)
6b77a0a7d Pyrelands: six C# files marked clean after full-file review; pickAP notes
2f500a246 Pyrelands burrow: a timed-out burrow cools down before re-burrowing
9add2e52a Pyrelands review: drop shadowed startTick, correct false settings text, two validation fixes
84ad811d3 lessons: staggered checks defeat a per-tick cache; fresh-consumer power-up gap
ab1dab8b6 Owner-said guard: whole-word, one-text matching; close 17 forgery routes
a3f4ea11f Ledger: FOUNDRY shard sync (Pyrelands switch)
a820b692e Pyrelands: the Baroque Biomes "Pyrelands" toggle now stops its mechanics, not only worldgen
... 203 more: git log --oneline 1dc9674f5..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

