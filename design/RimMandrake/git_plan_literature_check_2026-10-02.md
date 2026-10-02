# Git plan literature check (2026-10-02)

Checks `git_workflow_plan_2026-10-01.md` against web literature. Verdicts: SUPPORTED / CONTESTED / UNSUPPORTED.

## 1. Untrack generated artifacts + regenerate via hooks
Verdict: CONTESTED (untracking SUPPORTED; hook-based regeneration is the fragile half)
- Hooks are not versioned/cloned; with `core.hooksPath` set, `.git/hooks` is ignored silently; relative hooksPath resolves per-worktree and can point at a dir that exists only in the main checkout: https://github.com/fmanimashaun/claude-skills/issues/1204 , https://github.com/apmantza/pi-lens/issues/3674 , https://github.com/fmanimashaun/claude-skills/issues/1199
- AGAINST (directly relevant): Claude Code itself rewrites the shared `core.hooksPath` to an absolute `.git/hooks` path on worktree creation, silently disabling repo-managed hooks for the whole clone: https://github.com/anthropics/claude-code/issues/66993 . The plan's pool hook + `core.hooksPath=src/.../git_hooks` collides with exactly this.
- Hooks skipped by plumbing: post-merge/post-checkout fire only on porcelain merge/checkout; `./publish` plumbing and `git fetch && git reset --hard` (the mirror) fire neither post-merge nor post-checkout (reset runs no hook), so rendered views would go stale there. (From githooks docs: https://git-scm.com/docs/githooks ; not searched further.)
- `git rm --cached` migration: when the untracking commit is pulled, every other clone/worktree has the file DELETED from its working tree (git records a deletion): https://konadu.dev/git-rm-cached-stop-tracking-files-keep-local-copies . Fine for regenerable files only if the hook then runs; with many worktrees/clones, some will have no generator run until next merge. Plan has no "regenerate on first use / lazy render" fallback.
- SUPPORTED: general advice is generated output should not be tracked; plan's own precedent (4 earlier views already gitignored) agrees. Safer pattern: make readers generate on demand (rimflow next/show already do) instead of relying on hooks.


## 2. merge=union for append-only JSONL vs one-file-per-event
Verdict: CONTESTED (safe only under strict preconditions the plan lists but does not enforce)
- FOR: widely used for append-only logs; E2 zero conflicts agrees. https://github.com/choiceoh/stkernel/pull/1222 , https://github.com/medici-finance/assay/issues/588
- AGAINST: union does not dedupe; a line on both sides survives twice and compounds on the next merge (mesh merge duplicated logs): https://github.com/bzdOS/hubd/releases/tag/v0.9.3 ; an in-place edit on one side + append at the same anchor keeps old AND new line (silent): https://dev.to/rulestack/two-writers-one-append-only-ledger-the-git-conflict-one-gitattributes-line-fixed-and-the-files-55j0 ; unsound for append-only ledgers, "land the guard not the change": https://github.com/thestoryportal/arhugula-harness/pull/1563 ; with parallel (agent) authorship the silent problem outweighs the loud one, recommends one-file-per-entry (towncrier style) + validation gates: https://github.com/btclib-org/.github/issues/21 ; also loses a line at one anchor: https://github.com/btclib-org/portanode/pull/462 . Union also gives no ordering guarantee (git docs).
- Scale of one-file-per-event: git handles many small files in the object DB fine, but 250/day = ~90k files/yr in the working tree, which is the very drvfs-slow cost the plan is escaping, and git-bug/git-appraise avoid this by storing events as commits/refs not working-tree files (reftable/refs scaling caveats: https://github.blog/open-source/git/highlights-from-git-2-45/). Neither extreme is clearly right; middle path = per-seat shard + sharded by day/month file (bounded conflicts, small files).
- Plan's 'preconditions checked in Phase 0' (id dedupe, order by ts) is precisely the mitigation the literature demands; it must be a permanent reader invariant plus a CI/hook lint (dup id with different content), not a one-time check. Ledger shards are per-seat so same-seat two-window case is the only exposure.


## 3. ext4 clones vs Windows-drive; Windows tools on \\wsl.localhost
Verdict: SUPPORTED for ext4 clones; CONTESTED for the Windows-build route (plan correctly flags UNMEASURED)
- Microsoft/community consensus: keep code on the Linux filesystem for Linux tools; cross-boundary (9P) is slow for many small ops: https://dev.to/nomurasan/why-wsl2-is-slow-on-mntc-and-how-to-find-the-exact-operation-costing-you-time-40o7 , https://lorbic.com/wsl2-performance-tax-go-windows/
- Reverse direction is ALSO slow: Windows tools reading \\wsl.localhost are 10-20x slower than native Windows repos: https://github.com/desktop/desktop/issues/22044 ; 9P vs Samba benchmark: https://allenkuo.medium.com/windows-wsl2-i-o-performance-benchmarking-9p-vs-samba-file-systems-cf2559be41ac
- Windows dotnet/MSBuild/cmd with UNC paths: cmd.exe refuses UNC cwd and falls back to C:\Windows; dotnet SDK/OmniSharp/NuGet have UNC path bugs: https://github.com/dotnet/vscode-csharp/issues/3099 , https://github.com/dotnet/sdk/issues/19169 , https://github.com/NuGet/Home/issues/13989 , https://github.com/dotnet/msbuild/issues/7001 , https://github.com/microsoft/terminal/issues/17998 . So the plan's expectation that Phase 0 may fail and `_rmbuild` rsync is needed is well founded; treat rsync-to-D: as the default, not fallback. Alternative: install a Linux dotnet SDK in WSL (Unity/Mono net472 targets for RimWorld mods build with reference assemblies on Linux) - plan does not consider it.
- Note the mirror/rsync build route reintroduces drvfs I/O cost for the build tree (rsync of project dir on each build) but only the project, not the repo.


## 4. Bounded worktree pool for parallel agents
Verdict: SUPPORTED (persistent pool for heavy repos); CONTESTED on hook mechanics and on rescue-at-allocation
- Mainstream (Conductor, Claude Code, Cursor, Claude Squad, Maestro) is one worktree per agent/task, ephemeral; known problems are disk bloat and stale worktrees (Cursor user: 9.82 GB in a 20-min session on a ~2 GB repo): https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution , https://dev.to/jamilxt/three-ai-agents-one-laptop-the-git-worktree-trick-that-makes-parallel-coding-work-h5e
- Persistent, pre-warmed, fixed pool is an explicitly recommended pattern for heavy repos and build caches (warm bin/obj): https://github.com/quangdang46/treehouse_rust (pool with durable TTL leases, cleanup on every exit, safe gc) , https://github.com/Servant-Software-LLC/Guardrails/issues/255 . Matches plan's 3 full slots/seat. Pool sizes in the wild are not standardised; plan's 3/seat is a guess, no literature value.
- Claude Code official: worktrees created by a WorktreeCreate hook carry no git marker so the built-in sweep never removes them; sweep otherwise skips dirty/unpushed worktrees and holds `git worktree lock` while an agent runs; hook paths: `${CLAUDE_PROJECT_DIR}` does not follow the worktree, `cwd` does; non-interactive `-p` never cleans up and leaves locks: https://code.claude.com/docs/en/worktrees . Supports plan's self-managed liveness/recycle design; suggests adding `git worktree lock` per slot (plan uses pid files only).
- AGAINST/risk: Claude Code issue #66993 (worktree creation rewrites shared core.hooksPath) - see claim 1. Claude Code also refuses worktrees whose git identity resolves into the main checkout and never resumes into 'network spelling' paths (so \\wsl.localhost paths are refused): same docs page. The plan's slots are linked worktrees of the seat clone under /home/mandrake/rm/pool, which is fine, but the isolation checks block edits/git redirected to the main checkout - the slots must not be reached via cd into the seat clone.
- Resetting a slot with `checkout -B` leaves ignored files (bin/obj, stale untracked output); literature treats that as a feature (warm cache) AND as the main correctness risk (stale build outputs); plan does not say whether `git clean -fdx` or only `-fd` runs at recycle.


## 5. Read-only mirror via timer on drvfs
Verdict: CONTESTED (workable but the cited failure class is real and unaddressed)
- Git on /mnt (9p/drvfs) is documented to corrupt/lock the index: `git reset --hard HEAD` corrupting the index on a mounted FS (does not repro on ext4): https://github.com/microsoft/WSL/issues/11619 ; transient `index.lock` from multithreaded `core.preloadindex` over 9p, workaround `-c core.preloadindex=false -c index.threads=1`: https://github.com/open-gsd/gsd-path/pull/262 , https://github.com/open-gsd/gsd-path/issues/207 . The plan's timer runs `git fetch && git checkout --detach` on exactly this mount, concurrently with Windows-side readers (Explorer, Steam, antivirus, Windows git). A 5-min timer plus on-demand `./mirror sync` can race itself (use flock) and a failed checkout leaves a half-updated tree.
- Mixed Windows/WSL git on one worktree has CRLF/filemode/safe.directory pitfalls: https://jessehouwing.net/tips-tricks-git-under-wsl-and-windows/ . Mirror is checked out by WSL git only so autocrlf must match the clones' (else the mirror shows spurious diffs).
- Alternative the literature points at: don't keep a .git-bearing mirror on D: at all; export (`git archive`/`git worktree`-less rsync of a tree from the ext4 clone) to a plain directory, or `git --work-tree` with a bare repo on ext4, so no index lives on drvfs. Plan keeps a full .git on drvfs.


## 6. archive/* rescue/* refs as drain
Verdict: SUPPORTED (with a ref-namespace caveat)
- Archiving unmerged branches instead of deleting is standard practice; most write-ups use TAGS `archive/<name>` with a recovery window (e.g. 90 days) because they stay out of the branch list: https://medium.com/@vbabak/how-to-deal-with-stale-branches-on-the-github-b49727480872 , https://github.com/debrief/debrief/issues/5229 . Deleting an unmerged branch makes commits unreachable and GC-able, which is the failure being avoided.
- Caveat: plan pushes to `refs/heads/archive/*` (branches). 68+ extra branches clutter GitHub's branch UI and clones with default refspec fetch all of them into every seat clone and slot (the 257 unique commits and objects land in every clone). Tags (`refs/tags/archive/*`) or a custom `refs/archive/*` namespace (not fetched by default, git hosts accept arbitrary refs/ pushes but GitHub may hide non-heads/tags) avoids that. Large-refcount performance only bites at ~tens of thousands of refs (https://github.blog/open-source/git/highlights-from-git-2-45/), not 68.
- Rescue refs created automatically at each slot recycle (`rescue/<name>-<utc>`) have no stated expiry; literature uses time-boxed retention + a sweep.


## 7. Rejecting jj
Verdict: SUPPORTED (for this repo, now)
- Current literature is bullish on jj for multi-agent work (first-class conflicts, many workspaces on one commit, no same-branch restriction): https://wavect.io/blog/git-worktrees-vs-jujutsu-ai-coding-agents/ , https://geirsson.com/jj-workspaces , https://www.joshualyman.com/2026/02/demystifying-jujutsu-jj-workspaces/ ; the same sources hedge: jj does not remove transfer/materialization cost, and per jj's compatibility doc (Sept 2026) partial clones are unsupported, so cold starts can get worse; pilot only if agents lose time shaping parallel changes into reviewable history. The plan's problem is filesystem/ownership, not history shaping, so rejection fits. Codex app requests jj-workspace support (https://github.com/openai/codex/issues/26648): tooling is still git-first.
- Caveat: plan says 'not even a pilot' as a permanent ruling; literature frames it as 'revisit later'. Soften to 'not now'.

## Top 5 weakest (per literature)
1. Hook-driven regeneration (post-merge/checkout) is fragile: hooksPath/worktree quirks, Claude Code overwriting core.hooksPath (anthropics/claude-code#66993), and plumbing/reset paths (publish, mirror) fire no hooks; make readers render on demand.
2. `merge=union` silently duplicates/compounds lines and mishandles in-place edits; needs a permanent id-dedupe reader invariant plus a lint (or per-day shard files), not a one-time Phase 0 check.
3. A full .git mirror on drvfs repeats the documented 9p index-corruption/index.lock class (microsoft/WSL#11619); use a plain exported tree or bare repo on ext4, and flock the timer.
4. Windows tools on ext4/UNC paths are documented-broken for cmd/dotnet/NuGet: make the `_rmbuild` rsync (or a Linux dotnet SDK) the default and decide before Phase 3.
5. Archive as `refs/heads/archive/*` branches bloats every clone's default fetch; use tags or a non-default namespace with expiry, and give rescue refs a retention rule.

Overall: direction (ext4 clones, untrack generated files, bounded persistent pool, no jj for now) SUPPORTED; mechanisms around hooks, union merge and the drvfs mirror CONTESTED.
