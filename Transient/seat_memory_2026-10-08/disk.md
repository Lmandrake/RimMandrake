# Disk clean-up 2026-10-08 (SEAT_MEMORY_CLONES_DRIVES_1)

## df before
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdd       1007G  337G  620G  36% /
/dev/sdd       1007G  337G  620G  36% /

## Moved to quarantine (rename, same fs): /home/mandrake/rm/_quarantine/2026-10-08/home-mandrake-<path flattened>/
Checks before each move: `git status --porcelain`, branches, stash, `git log --branches --not --remotes`, /proc/*/cwd and /proc/*/fd scan (none in use for any candidate).
Nothing was deleted; quarantine frees no space until the owner rules it can be deleted (~87 GB there).

| clone | porcelain | stash | unpushed | note |
|---|---|---|---|---|
| rm/_fwY_base | 0 | 0 | none | **alternates -> foundry** |
| rm/drain, rm/fwx, fwx2..5 | no .git (scratch trees) | | | last touched 10-02 / 10-05 |
| wt/impl-{drain,freeze,launch,p8,triage} | 0 | 0 | none | full clones, no alternates |
| wt/impl-{p01,p4,p5,p5-art,p7,pub} | 1 untracked `Transient/modcheck/fixtures.json` (generated; the same path is tracked in origin/main) | 0 | none | |
| ~/.cache/warscar_push | 0 | 0 | 4 commits not in its remotes, but `git cherry origin/main` after fetch shows 0 unique patches (all landed) | **alternates -> bench** |
| ~/.cache/bench | no .git: 5.9 GB of scripts/logs/objects.git (artpipe_back_to_5.sh, pushrc, sheet_timer*, census.json) | | | last touched 10-05 |

Alternates note: _fwY_base and warscar_push keep working after the rename (alternates are absolute paths to the live clones), but a `git gc`/prune in foundry/bench could break them. Acceptable now they are quarantined junk.

## HELD BACK (not moved), for the owner
- `rm/_fwY_gate`: UNCOMMITTED work: modified `RM_SluiceGateSettings.cs`, new `RM_SluiceGate.cs`, `RM_SluiceGateMath.cs`, a `Transient/belt_fwlogistics_gate_20261005.md`; none of them in origin/main. (alternates -> foundry)
- `rm/_fwY_blood`, `_fwY_quarry`, `_fwY_tanker`: clean except one untracked `Transient/belt_fwlogistics_<name>_20261005.md` report each, absent from origin/main. Rescue the 3 small .md files (and the gate .cs) and these four are movable. (alternates -> foundry)
- `rm/reconcile` (alternates -> bench): `main` has 12 commits whose patch-ids are not in origin/main (Rust Cathedral / Abyss sitting 2 / Slime / Blue Desert sheet ingests, scaled-review gate rebuild); plus untracked fixtures.json. Cannot prove they landed re-written.
- `~/.cache/pyrelands_replay_1607507` (alternates -> bench): 2 patch-unique commits (f48797f41 Contagion sheet closed, eb90adf08 sheet decisions refresh).
- `~/.cache/stillsand_s2_replay`: 3 patch-unique commits (the same two plus 6d39812ec Blue Desert rebuild state).
  These may have landed under other shas with edits; confirm per commit, then move.

## /home/mandrake/wt/gitlab (inspected only, NOT moved)
30 GB, not a git repo, no README/marker. Last modified 2026-10-01 23:45. It is a jj/git-storage experiment scratch: scripts e1..e4 (timing `git status` on drvfs vs ext4, `jj git fetch`/`jj new` non-ff push tests, worktree trials) plus copies `e4` 17 GB, `seat` 5.9 GB (a repo copy), `wtfull0` 4.1 GB, `e2_a/b/c`, `dl`. Looks like throwaway output of the git-workflow redesign (2026-10-01); owner rules.

## Mirror
- `rm-mirror.timer` stopped; no rm-mirror.service, git process or open fd in mirror.git; deleted only the 42 `objects/pack/tmp_pack_*` (72 GiB); `git fsck --connectivity-only` clean; timer restarted (active).
- Mirror pack state afterwards: 45 packs, garbage 0.
- WHY they accumulated (inference, not proven): journal shows every sync "Finished" successfully (no failed units, no OOM, no timeout; 0 kernel OOM lines 10-06 12:00-23:00). The stale temp packs are 1-3.4 GB each (a full repack-sized output, not a partial fetch) and sit at the same minutes as runs whose CPU time is 3-8x wall time with 2.4-4.9 GB memory peaks (e.g. 10-03 23:25 `4.9G peak, 29.6 s CPU / 11.7 s wall`). Mirror sets `gc.auto=256` and 45 packs is near `gc.autoPackLimit` 50, so `git fetch` spawns a detached auto-gc/repack; the oneshot unit then ends and systemd's default KillMode=control-group kills the still-writing repack, leaving its tmp_pack_*. Recommended fix (not applied): in mirror.py use `git -c gc.autoDetach=false fetch ...` (or `git config gc.auto 0` and run `git repack -d -q` on a separate weekly unit), and give the unit `MemoryMax=6G` since peaks reach 4.9 GB. 45 packs will keep triggering it until a repack consolidates them.

## /tmp leaked test dirs
Found ns_mock_* 3465, gs_* 2000, bacta_st_* 736, nsjudge_st* 184 (mtime 10-07/10-08: 3101 + 364 for ns_mock_*). None older than 1 day, so none deleted (and none were held open). /tmp is 388 MB of 18 GB now.

## fstrim / df
`sudo -n fstrim -v /` refused (interactive authentication required): no passwordless sudo, not run. The ext4.vhdx on C: will not shrink until trim/compact is run by the owner.

## df after (mirror garbage removed; quarantine still holds its bytes)
/dev/sdd       1007G  266G  691G  28% /
