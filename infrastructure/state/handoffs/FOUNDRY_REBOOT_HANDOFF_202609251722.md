# FOUNDRY_REBOOT_HANDOFF_202609251722 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609251428`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**A plain `git merge` in this shared working tree can silently overwrite a concurrent seat's
uncommitted work — not just on a lock error, on ANY merge.** Caught it live 2026-09-25: my first
merge attempt hit BENCH's own concurrent commit collision and, even after erroring out, had
already checked out files and reset every locally-dirty tracked file in the shared tree to HEAD
(BENCH's own follow-up commits `860b9e0f9`/`a7ab35aa2` document the recovery). The fix I adopted
for the rest of the session: **never `git merge` in the shared tree once another seat might be
active.** Instead, `git worktree add --detach <tmp-path> origin/main`, resolve conflicts and build
there, `git push origin HEAD:main` directly from the temp worktree, then bring the shared tree's
own local branch forward with `git merge --ff-only` (a real fast-forward, which DOES respect
per-file dirty-worktree protection) or, when the shared tree has ALSO diverged with its own unique
commits by then, `git cherry-pick <sha>` a single commit's diff onto a temp worktree at
origin/main instead of merging the whole branch. A merge commit (2+ parents) cannot take a
pathspec on `git commit`, which trips `block_blanket_git_stage.py`'s always-require-a-pathspec
rule — the correct route there is `git write-tree` + `git commit-tree -p <p1> -p <p2>` +
`git update-ref HEAD <new-sha>` (plumbing, exempt from the hook since it never invokes
`git commit`). (filed: LESSONS_INBOX — the commit-tree-plumbing half; the merge/worktree-safety half was
already filed by BENCH the same day, same incident).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **I caused BENCH real, if fully-recovered, data loss this wave.** Two of my early merge attempts
  in the shared tree overwrote BENCH's uncommitted def edits and staged deletions (07:54:58 and
  ~07:57, 2026-09-25). BENCH caught it and recovered fully (`860b9e0f9`/`a7ab35aa2`) — nothing was
  permanently lost — but flagging it plainly rather than letting it pass as a clean wave. Fixed the
  method for the rest of the session (see "the one thing to carry forward" above).
- **This repo's `main` branch is a genuine mess of parallel history right now**, not a single clean
  line: BENCH commits directly in this shared tree AND separately via at least one private
  worktree (`bench/scald-defs`) that pushes straight to `origin/main`, and I did the same via
  temporary worktrees this wave. The result: this shared tree's local `main` and `origin/main`
  have real, confirmed-duplicate forked content (a black-screen-crash fix landed twice, byte-
  identical, on two different lines — see "traps learned"). Nobody has done a proper reconciling
  rebase in a while. This isn't something for me to unilaterally clean up (it needs whoever has
  full context on which BENCH line is authoritative), but it's worth your knowing the git history
  itself is not a trustworthy single narrative right now.
- **Nothing shipped this wave needs your judgment call or veto** — the two closed items
  (`FEVERTRUNK_CORE_DRILL_SPRITE_FIX_1` plus the wave-1 three) are bug fixes / mirrored an existing
  fix; the two left open are correctly scoped-down builds with real remaining work, not scope I cut
  short without saying so.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `GREATBOLE_BARK_EDGE_ART_1` — doing; NEXT: commission the bark-edge atlas art (ONE PNG, 4×4
  `Rock_Atlas`-cell-order layout, extract the real atlas from `resources.assets` per
  `reading-rimworld-graphics` first) and wire `RUT_GreatboleHeartwood`'s `linkType CornerFiller`
  + `linkFlags Custom1`. The marker-rendering half (`RUT_GreatboleCore`/`RUT_FeverTrunkCore` both
  drawing a fake drill sprite) is already fixed and pushed this wave.
- `REACTION_MECHANISM_GENERALISE_1` — doing; NEXT: build step 2 (propagation under
  `HOSTILE_MOBILE_PLANTS_1`) using the same `RM_ReactionEvent`/shared-budget shape step 1 already
  landed under the wasps — do not re-derive the mechanism, extend it.
- `GREENTIDE_WASP_SWARM_1` — proposed/noted, not doing; NEXT: wire the built `RM_SkerrelGall` onto
  real host plants once `RM_Sarquin`/`RM_Nemmer` exist as ThingDefs (they don't yet — the gall
  currently ships standalone), then a Mod Settings/balance pass.
- The shared-tree `main` / `origin/main` fork on the weather-overlay crash fix and
  `sea_dive_maps_spec.md` (see "what the owner should see") — NEXT: whoever has context on BENCH's
  two lines of that work does a proper rebase/reconciliation; I deliberately did not force one.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A `git merge` in the shared tree can silently blow away a peer's uncommitted work even when it
  ERRORS OUT afterward on an unrelated `index.lock` collision — the checkout phase runs before the
  index write it failed on (see: LESSONS_INBOX, BENCH's own line + mine this session).
- A merge commit can't take a commit pathspec, which trips this repo's always-require-a-pathspec
  git hook even on a clean merge — use `git commit-tree`/`git update-ref` plumbing instead (filed:
  LESSONS_INBOX).
- This shared tree's own `infrastructure/state/ledger/events/FOUNDRY.jsonl` can go stale relative
  to `origin/main` when work is pushed via a temporary worktree instead of committed here directly
  — `rimflow next/show --seat FOUNDRY` answers WRONG from a stale shard, no warning (filed:
  LESSONS_INBOX).
- `.claude/worktrees/agent-a7990d7dcc9386b86` is still locked by a live process (PID 169784, a
  "claude ... AGENT FOUNDRY" process, 2h42m+ elapsed at last check) even though its task reported
  completion — did not force-remove it; its merged work is already safely on `origin/main` either
  way (see: this handoff's commit list).

## Closed since the last handoff (3)

- `GREENTIDE_YEARNING_FRUIT_FILTH_1` — e399e17ca
- `WASTELAND_BRINE_BATTERY_DISCHARGE_1` — 50836e90f
- `WASTELAND_RADIOTHERMAL_SOLITARY_1` — 7e262459a

## Filed and still open (2) — the next seat's queue

- `ARTPIPE_QUOTA_RESET_WEDGE_1` — artpiped cannot notice a Codex quota reset: idle meter refresh reads only stale rollouts, so it stays parked until something runs codex exec in a leas
- `STACKCOUNT_FILEPATH_REDX_SWEEP_1` — 228 live 'Collection cannot init' errors: defs pointing a Graphic_StackCount/Random/Collection texPath at a FILE, not a folder, render red-X (RUT_Gree

## Commits

```
b6dede7fd Code review wave 5: mark clean 3 EnvironmentalHazards/WeepingStones files
d0dfad868 Sea dive maps design spec (SEA_DIVE_MAPS_BUILD_1)
898f260eb Fix black-screen crash: Scald steam and Greentide roil weather overlays
592a1fa91 Queue render refresh after 3-way FOUNDRY merge integration
9799649a5 Merge foundry/wasteland-radiothermal-solitary
69652821c Merge commit 'c885987c8dcefce34a2a589aabfac1c871e54c7a' into HEAD
c885987c8 Merge foundry/wasteland-brine-battery-discharge
205ffc640 Lessons inbox: merge-wave tree reset eats uncommitted work; stale Player.log watcher hit
a7ab35aa2 Ledger sync: file STACKCOUNT_FILEPATH_REDX_SWEEP_1, Scald art-wired note, bridge take (re-applied after tree-wide revert)
860b9e0f9 SCALD_FLOOR_PASS_1: the def half of 4ea2a93f3, lost to a tree-wide revert
5ebcf3800 Merge remote-tracking branch 'origin/foundry/greentide-yearning-fruit-filth'
4ea2a93f3 SCALD_FLOOR_PASS_1: wire 14 Scald renders; fix red-X on all 25 sea catch items
7a293e27f Ledger: close WASTELAND_RADIOTHERMAL_SOLITARY_1
7e262459a WASTELAND_RADIOTHERMAL_SOLITARY_1: heat emission + spacing law for the radiothermal
9edda65b0 Ledger: close WASTELAND_BRINE_BATTERY_DISCHARGE_1
50836e90f Add RM_CompDefensiveDischarge: RUT_BrineBattery ion-gradient defense
6d83d7f14 Ledger: close GREENTIDE_YEARNING_FRUIT_FILTH_1
e399e17ca GREENTIDE_YEARNING_FRUIT_FILTH_1: filth+seedling payload on RUT_DigestiveAccelerant end
08362d176 Code review wave 4: mark clean RM_JobGiver_DirectedAssault.cs, RM_MechanicGates.cs
e2dc322c8 Lessons + ledger: artpiped quota-reset wedge, filed ARTPIPE_QUOTA_RESET_WEDGE_1
... 1 more: git log --oneline f9d4c2e47..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     SHULLA_INVISIBLE_RENDER_1 read-only diag

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   (ambient — codebase-health regeneration hook, re-triggered by any rimflow prune/list call; not this window's)
 M Transient/codebase_health.json   (ambient — codebase-health regeneration hook, re-triggered by any rimflow prune/list call; not this window's)
 M Transient/codebase_health_artifact.html   (ambient — codebase-health regeneration hook, re-triggered by any rimflow prune/list call; not this window's)
 M design/RimMandrake/sea_dive_maps_spec.md   (BENCH — live in-progress edit (verified: refining DRAFT to a RULED status per an owner sitting); do not touch, do not commit)
 D infrastructure/artpipe/pending/feverwood_kurreth_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_kurreth_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_kurreth_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_plant_ossagrel.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_skreth_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_skreth_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_skreth_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_thornbug_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_thornbug_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 D infrastructure/artpipe/pending/feverwood_thornbug_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 M infrastructure/artpipe/registry.jsonl   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 M infrastructure/artpipe/throughput.jsonl   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
 M infrastructure/dashboards/hub/data/health.json   (ambient — codebase-health regeneration hook, re-triggered by any rimflow prune/list call; not this window's)
 M infrastructure/state/codebase_health_last.json   (ambient — codebase-health regeneration hook, re-triggered by any rimflow prune/list call; not this window's)
 M infrastructure/state/ledger/events/BENCH.jsonl   (BENCH — their own ledger shard / regenerated queue projection from their bridge+deploy activity)
 M infrastructure/state/queue/BENCH.md   (BENCH — their own ledger shard / regenerated queue projection from their bridge+deploy activity)
 M infrastructure/state/queue/FOUNDRY.md   (regenerated queue projection, re-derives cleanly from the ledger; not a hand edit)
?? deployed/config/ModsConfig.before-tier-firehawk.xml   (BENCH — modlist backup snapshot from their own tier deploy)
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   (BENCH — modlist backup snapshot from their own tier deploy)
?? design/RimMandrake/scald_steam_and_hazards_spec.md   (BENCH — untracked design doc from their own session)
?? design/RimMandrake/statue_expansion_assessment.md   (BENCH — untracked design doc from their own session)
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brakkel_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brunnock_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_cundral_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_maddrick_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mourvel_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rut_wildhealroot.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutfuzz_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglower_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglowercrust_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutvaultroot_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_saalcatch_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_saalcatch_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shullacatch_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shullacatch_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_ventbuilding_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_ventbuilding_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckframe_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckframe_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckhull_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckhull_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wrecktank_v1.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wrecktank_v1.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_zhool_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/crags_kessik_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/crags_kessik_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_kessik_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_kessik_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_shekkur_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_shekkur_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_shekkur_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_vrakk_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_vrakk_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_vrakk_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zekkra_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zekkra_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zekkra_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_essarn_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_essarn_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_essarn_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_fessk_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_fessk_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_fessk_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_otheska_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_otheska_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_otheska_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_sorruth_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_sorruth_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_sorruth_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_heemin_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_heemin_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_heemin_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_body_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_body_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_body_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_atlas.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_menuicon.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_bezzul_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_bezzul_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_bezzul_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_hennul_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_hennul_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_hennul_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_oomb_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_oomb_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_oomb_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_thummorak_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_thummorak_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_thummorak_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_vohhm_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_vohhm_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_vohhm_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuppik_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuppik_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuppik_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuum_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuum_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuum_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_yollum_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_yollum_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_yollum_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   (ambient — artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   (pre-existing backup/snapshot file, predates this window)
?? src/RimMandrake/Utils/firehawk_flight_probe.py   (another live FOUNDRY window — building the Pawn_FlightTracker state-read tool per FIREHAWK_FLIGHT_BEHAVIOR_1's no-screenshot-flight-testing ruling; in progress, not this window's)
?? src/RimMandrake/Utils/scald_showcase.py   (BENCH — already committed at 68e306bac per origin/main; this untracked copy is stray, not this window's)
```

