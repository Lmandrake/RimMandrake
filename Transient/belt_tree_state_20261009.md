# Foundry tree state, 2026-10-09 ~00:00 PDT (origin/main 230cd250e at fetch; local HEAD efe67213a is behind)

Method: `git fetch origin`, then `git diff origin/main -- <path>` per modified tracked path. Re-measured at the end; the tree is moving (an acceptance sitting and a full-file reviewer are active), so anything with mtime under 15 minutes is IN FLIGHT. Rule for all rows: never stash/reset/checkout; land only with `/home/mandrake/.seat-tmp/land.sh -m "<msg>" <paths>` (it builds from origin in a temp index and ignores local HEAD/index).

Why so many "modified" files: local HEAD (efe67213a) trails origin, and helpers landed by plumbing. Where the working tree equals origin, `git status` is only showing HEAD staleness.

## (a) IDENTICAL to origin/main: no work to land, modification is only a stale HEAD artifact
Safe next command for every row: none needed. Cleans itself only when HEAD advances; do NOT `checkout`/`reset` (peers are editing nearby). If HEAD must catch up, a peer-safe route is a fast-forward in a private clone, not this tree.

| path | note |
|---|---|
| design/RimMandrake/GIT_WORKFLOW.md | landed in 4eb7fc4de (land.sh hardening) |
| infrastructure/state/code_review/FOUNDRY.jsonl | identical at last check (0 min mtime: reviewer appends constantly, re-check before relying) |
| src/RimMandrake/DivingInteraction/Assemblies/RimMandrake.DivingInteraction.dll and .srchash | landed cb93dae7a |
| src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ChillGardenDefense.cs | landed cb93dae7a |
| src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs, RimMandrake_FlowWorks.csproj | landed 8780b6ca0 (SettingsKit link) |
| src/RimMandrake/FlowWorks/Source/TakenByLand/RM_TakenByLand.cs | landed 332761896 |
| src/RimMandrake/FlowWorks/northstar/selftest_flowworks_northstar.py, site_spec.py | landed 230cd250e |
| src/RimMandrake/Utils/modset_builder.py | landed 8a84a6fae (tier acc_20261009b) |
| src/RimUtinni/WasteRun/Assemblies/*.dll, .srchash, Source/WasteRunProof.cs | landed cb93dae7a |

## (b) Differs from origin/main by content
| path | what differs | owner / state | safe next command |
|---|---|---|---|
| src/RimMandrake/CreatureBehaviors/Source/RM_ShadeHop.cs | adds static `EmptyPawns` array instead of allocating `new Pawn[0]` per call | full-file reviewer; mtime 2 min: IN FLIGHT | wait; later `land.sh -m "ShadeHop: reuse empty lure array" src/RimMandrake/CreatureBehaviors/Source/RM_ShadeHop.cs` |
| src/RimMandrake/DivingInteraction/Source/BrineEncasementUtility.cs | `edifice?.Destroy()` moved after the pawn is safely held (+comment) | reviewer; mtime 1 min: IN FLIGHT. Its DLL on origin (cb93dae7a) may not contain this edit | wait; then land the .cs together with a rebuilt DivingInteraction dll + .srchash (winbuild.py) in ONE land.sh call |
| src/RimMandrake/FeverWood/Source/RM_MapComponent_TentacleWatch.cs | partial-grant remainder retried via `pendingGiftRolls`; seed cell skipped if it holds an edifice | reviewer; mtime 2 min: IN FLIGHT (FeverWood dll/.srchash also modified, 0 min) | wait; land .cs + FeverWood dll + .srchash together after rebuild |
| src/RimMandrake/FeverWood/Assemblies/RimMandrake.FeverWood.dll, .srchash | rebuilt binary (not in the first scan; appeared during this pass) | in flight, mtime 0 min | do not touch; same land.sh call as the .cs above |
| src/RimMandrake/Stillsand/Source/RM_HorizonWarning.cs | Harmony prefix passes the entry spawn cell via `__state` to the postfix (worker may rewrite parms.spawnCenter) | reviewer; mtime 2 min: IN FLIGHT | wait; land with Stillsand dll if one is rebuilt |
| src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_MapComponent_Aerial.cs | appeared mid-pass | reviewer; mtime 0 min: IN FLIGHT | do not touch |
| src/RimMandrake/Cauldron/Assemblies/RimMandrake.Cauldron.dll and .srchash | rebuilt binary, no source change vs origin; mtime 22 min, no active writer; likely a leftover build after c7bfa8aed (VEXXITH_CLOSED_LOOP_BUILD_1) | orphan build output | check it matches source: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Cauldron` (dry run). Land only if the srchash matches the current Source; otherwise leave |
| src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll and .srchash | rebuilt after 332761896 (TakenByLand) and the SettingsKit link; mtime 10 min | FlowWorks helper, possibly still building | wait 15 min of quiet, then `land.sh -m "FlowWorks: rebuild dll for TakenByLand + SettingsKit" src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash` |
| Transient/modcheck/fixtures.json | one line: `{"tick": 2501,"ids":[]}` becomes `{"tick": 300,"ids":[]}`; a modcheck run writes it | acceptance sitting 2, mtime 6 min | leave; it is run output, safe to discard only after the sitting ends (`git diff origin/main -- Transient/modcheck/fixtures.json`) |

## (c) Ledger shards
| shard | finding | safe next command |
|---|---|---|
| infrastructure/state/ledger/events/FOUNDRY.jsonl | working tree = origin (4612 lines) plus exactly 1 extra line, appended at the end, prefix identical: `{"event":"bridge","state":"taken","purpose":"FOUNDRY sitting 2","ts":"2026-10-09T06:52:06Z"}`. Pure append, lint-clean. Live (mtime 2 min). | `land.sh -m "FOUNDRY ledger: bridge taken, sitting 2" infrastructure/state/ledger/events/FOUNDRY.jsonl` (do it after the sitting's own release event so the pair lands together) |
| infrastructure/state/ledger/events/BENCH.jsonl | NOT modified in this tree, so NOT_APPEND is not an edit. Local copy has 1379 lines; origin has 1403. `ledger_lint.py` (worktree vs origin) reports 24 NOT_APPEND findings because the 24 origin-only lines (BENCH reclaim/needs/close events from commits d2881629f, 09eaf0844 and neighbours) are absent locally. `ledger_lint.py --rev origin/main` reports 0 findings, and no commit in the last 40 touching BENCH.jsonl removes a line. | None. Never commit or land this local file. Landing by land.sh from a temp index on origin is safe. If a hook or `git push` reports NOT_APPEND on BENCH, the cause is pushing local HEAD instead of using land.sh; to read current state use `git show origin/main:infrastructure/state/ledger/events/BENCH.jsonl`. |

## Untracked, not under Transient/ (real work vs noise)
| path | verdict | safe next command |
|---|---|---|
| src/RimMandrake/Utils/land.sh, land_README.md | already on origin (landed 4eb7fc4de); untracked here only because HEAD is behind | none |
| src/RimMandrake/_Shared/SettingsKit/ | 4 files already on origin (8780b6ca0); local copy untracked | `git diff --no-index` not needed; verify with `for f in $(git ls-tree -r --name-only origin/main src/RimMandrake/_Shared/SettingsKit); do git diff --quiet origin/main -- $f && echo same \|\| echo DIFF $f; done` |
| infrastructure/state/items/SHIPVERMIN_FREE_TIER_BEASTS_1.md | item prose NOT on origin, mtime ~31 h. Real work, but item files are written through rimflow | `python3 src/RimMandrake/rimflow/cli.py show SHIPVERMIN_FREE_TIER_BEASTS_1` to see whether the ledger knows it; if yes, land it with `land.sh -m "item prose: SHIPVERMIN_FREE_TIER_BEASTS_1" infrastructure/state/items/SHIPVERMIN_FREE_TIER_BEASTS_1.md` |
| src/RimMandrake/SacredGraffiti/Assemblies/SacredGraffiti.dll.srchash | not on origin, mtime ~29 h; a stamp for a DLL that is tracked. Real but stale | `python3 src/RimMandrake/Utils/code_review_status.py check` is irrelevant; instead rebuild with `winbuild.py SacredGraffiti` and land dll plus srchash together, or leave |
| src/RimMandrake/FlowWorks/northstar/extension_result_20261008T212615.json | run output, 148 min old, not on origin | leave, or land under Transient/ if wanted |
| conversations/ | untracked scratch directory, 2 h old | leave |
| deployed/config/ModsConfig.before-tier-*.xml, ModsConfig.pre-*.xml, ns_flowworks_backup.*.json | modset_builder backup snapshots (many, up to ~14 h old), not on origin | leave; they are restore points, never delete during a sitting |

Count: 24 modified tracked paths at first pass, 32 by the end (FeverWood dll pair and GimmeSomeSlack Aerial appeared; code_review became identical). Re-run `python3 /home/mandrake/.seat-tmp/cls.py` for the live table.
