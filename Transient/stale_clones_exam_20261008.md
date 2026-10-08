# Stale clones exam 2026-10-08 (SEAT_MEMORY_CLONES_DRIVES_1, Phase 3)

Read-only: nothing deleted, moved or gc'd. origin/main = `7a9793fff` (fetched at exam time).
Method: per clone `git status --porcelain`, `stash list`, `log --branches --not --remotes`, `for-each-ref refs/heads`,
`.git/objects/info/alternates`, then `git cherry origin/main <branch tip>` and `merge-base --is-ancestor`, run with
`GIT_ALTERNATE_OBJECT_DIRECTORIES` pointing at foundry's objects so the clones could see the new tip without being written.
Caveat: "not in remotes" uses each clone's stale remote-tracking refs; the authoritative test is the cherry/ancestor line.

## Findings that change the plan
1. **The `wt/impl-*` clones, `rm/_fwY_base`, `rm/drain`, `rm/fwx*`, `.cache/warscar_push`, `.cache/bench`, `wt/gitlab` are ALREADY
   quarantined** (renamed, not deleted) under `/home/mandrake/rm/_quarantine/2026-10-08/` (106 GB by deduplicated `du`). Paths below
   are the quarantine paths. `/home/mandrake/wt/impl-*` no longer exists.
2. **Per-clone `du` overstates**: the 11 impl clones are local clones sharing hardlinked pack files. `du` on each alone says 9.1-9.4 GB;
   `du` over all of them lists 4.1-4.4 GB each (first arg takes the shared bytes). Deleting one frees only its unshared part; the
   space returns when the LAST sibling goes. Quarantine total 106 GB is the real figure (matches df 337G -> 266G used after the
   mirror cleanup; free 691G).
3. **ALTERNATES SOURCES (never gc/repack/prune/delete): `/home/mandrake/rm/foundry` and `/home/mandrake/rm/bench`**, and
   `/home/mandrake/dev/Lodestar` (feeds `.cache/lodestar_push_2061745`, out of scope here). Dependents found by scanning every
   clone: foundry <- `_fwY_blood/gate/quarry/tanker`, `_quarantine/.../_fwY_base`; bench <- `rm/reconcile`,
   `.cache/pyrelands_replay_1607507`, `.cache/stillsand_s2_replay`, `_quarantine/.../.cache-warscar_push`. Remove the dependents
   first; the sources stay regardless.
4. **Prior survey claims verified**: mirror.git has 0 `tmp_pack_*` (139 pack files, 5.9 GB; claim of deleting 42 holds);
   quarantine list, held-back list, alternates map and 12/2/3 patch-unique counts all reproduced. /tmp: 396 MB used of 18 GB, 3503
   `ns_mock_*` dirs still present (test-runner leak, untouched).
5. **The HOLD clones' unique commits are NOT proof of loss**: 10 of the 12 `reconcile` commits and the Contagion commit
   `f48797f41`/`eb90adf08` have same-subject twins on origin/main under different shas (rebased and re-written). But content
   comparison of each commit's files against origin/main differs (later edits), so equivalence is not provable by git alone ->
   HOLD, owner/BENCH to confirm.

## Table
| path | size (du) | unpushed work | alternates | verdict |
|---|---|---|---|---|
| `_quarantine/2026-10-08/home-mandrake-wt-impl-{drain,freeze,launch,p8,triage}` | 4.1-4.4 G each (9.1 G alone) | N: clean, no stash, branch `main` only, 0 commits off remotes | none | SAFE-TO-REMOVE |
| `_quarantine/.../home-mandrake-wt-impl-{p01,p4,p5,p5-art,p7,pub}` | 4.2-4.3 G each | N: only untracked `Transient/modcheck/fixtures.json` (path is tracked in origin/main, generated); 0 commits off remotes | none | SAFE-TO-REMOVE |
| `_quarantine/.../home-mandrake-rm-_fwY_base` | 6.2 G | N: clean, HEAD `f26080fa0` is an ancestor of origin/main | foundry | SAFE-TO-REMOVE (it is a dependent, not a source) |
| `_quarantine/.../home-mandrake-.cache-warscar_push` | 5.9 G | N: 0 unique patches vs origin/main (the 4 off-remote commits all landed) | bench | SAFE-TO-REMOVE |
| `_quarantine/.../home-mandrake-rm-drain`, `-rm-fwx2/4/5`, `-rm-fwx`, `-rm-fwx3` | 3.5 G; 1.1/1.2/1.2 G; 24-25 M | no `.git` (scratch trees, last touched 10-02/10-05); contents not inspected beyond that | n/a | SAFE-TO-REMOVE (owner already treated as scratch; nothing git-tracked to lose) |
| `_quarantine/.../home-mandrake-.cache-bench` | 5.9 G | no `.git`; scripts/logs/`pushrc/` (`artpipe_back_to_5.sh`, `sheet_timer*`); not git work | n/a | SAFE-TO-REMOVE after a glance at `pushrc/` (not opened) |
| `_quarantine/.../home_mandrake_wt_gitlab` | 30 G | not a git repo; jj/git timing experiments (10-01) | n/a | HOLD (owner rules; previous survey said so) |
| `/home/mandrake/rm/_fwY_blood` | 6.2 G | N commits (HEAD `709ca162a` in origin/main); **Y uncommitted**: untracked `Transient/belt_fwlogistics_blood_20261005.md`, absent from origin/main | foundry | HOLD until the .md is copied out |
| `/home/mandrake/rm/_fwY_quarry` | 6.2 G | as blood: untracked `belt_fwlogistics_quarry_20261005.md` | foundry | HOLD until the .md is copied out |
| `/home/mandrake/rm/_fwY_tanker` | 6.2 G | as blood: untracked `belt_fwlogistics_tanker_20261005.md` | foundry | HOLD until the .md is copied out |
| `/home/mandrake/rm/_fwY_gate` | 6.2 G | **Y uncommitted**: modified `RM_SluiceGateSettings.cs`; new `RM_SluiceGate.cs`, `RM_SluiceGateMath.cs`, `belt_fwlogistics_gate_20261005.md`; none exist in origin/main or in foundry's tree | foundry | HOLD (real work; commit it from here or copy out) |
| `/home/mandrake/rm/reconcile` | 6.1 G | **Y**: branch `main` `5e0bf5cb7`, 20 ahead of origin/main, 12 patch-unique (Rust Cathedral / Abyss s2 / Blue Desert s3 / Slime / scaled-review gate ingests; two have no same-subject twin: "Rust Cathedral sheet ingested" `101aa20132`); branch `rec` fully landed; untracked fixtures.json | bench | HOLD, with ALTERNATES dependency |
| `~/.cache/pyrelands_replay_1607507` | 5.9 G | **Y**: `main` 8 ahead, 2 patch-unique (`f48797f41`, `eb90adf08`); same-subject twins `4f8ba82b4`, `556b020e5` exist on origin/main; branch `replay` landed | bench | HOLD (likely landed; confirm) |
| `~/.cache/stillsand_s2_replay` | 5.9 G | **Y**: `main` 11 ahead, 3 patch-unique (the two above + `6d39812ec` "Blue Desert sheet rebuild state", no twin; 2 files differ from origin/main); `replay` landed | bench | HOLD |
| `/home/mandrake/rm/foundry`, `/home/mandrake/rm/bench` | live seats | n/a | none | ALTERNATES-SOURCE, never touch |
| `/home/mandrake/rm/mirror.git` | 5.9 G | n/a | n/a | already clean (0 tmp_pack); fix for recurrence (gc.autoDetach=false, MemoryMax) still unapplied |
| `rm/aside_20261007` 8 M, `rm/ul_wip_backup` 40 K, `rm/{a,b}` 25 M files, `wt/{exetest,lodestar-p5,p7test,x1}` <40 M | tiny | not examined (no value in the space) | n/a | leave |

## Proposed removal commands (NOT RUN; ordered; frees ~85 GB deduplicated, 30 GB more if gitlab is ruled out)
Precondition each time: `pgrep -af '_quarantine'` empty (no process cwd/fd inside). Use `rm -rf` on explicit full paths only.
```
Q=/home/mandrake/rm/_quarantine/2026-10-08
# 1. alternates dependents first (sources foundry/bench are never touched)
rm -rf $Q/home-mandrake-rm-_fwY_base $Q/home-mandrake-.cache-warscar_push
# 2. standalone full clones (hardlink-shared: space returns progressively, fully after the last)
for d in impl-drain impl-freeze impl-launch impl-p01 impl-p4 impl-p5 impl-p5-art impl-p7 impl-p8 impl-pub impl-triage; do rm -rf $Q/home-mandrake-wt-$d; done
# 3. scratch trees (no .git)
rm -rf $Q/home-mandrake-rm-drain $Q/home-mandrake-rm-fwx $Q/home-mandrake-rm-fwx2 $Q/home-mandrake-rm-fwx3 $Q/home-mandrake-rm-fwx4 $Q/home-mandrake-rm-fwx5
# 4. after glancing at pushrc/
rm -rf $Q/home-mandrake-.cache-bench
# 5. only after owner ruling: rm -rf $Q/home_mandrake_wt_gitlab
```
Then record in the item: the list above plus `df -h /` before/after. The HOLD rows stay until: 4 FW logistics .md files and the
gate .cs trio are copied to foundry and committed; reconcile/replay commits are confirmed landed or rescued; then remove
`_fwY_*` and reconcile and both replay dirs (dependents) in any order. foundry/bench never.
