# RimMandrake git workflow review — 2026-10-01

Asked by Lukas ("tell me how these worktrees are better… the original git trauma might have been better"). Claude's brief and GPT-6.1 Sol (ultra, via the Codex app CLI) reply, verbatim. Evidence: RimMandrake git log 09-18..10-01 and `design/RimMandrake/git_workflow_fix_2026-10-01.md`.

## Synthesis (Claude, after reading GPT)

- Worktrees as deployed (on drvfs, unbounded, never recycled) were worse than the shared tree by every measure available: throughput -33%, recovery commits 2.4%→4.2%, 68 stranded branches, /tmp at 100%. One confounded week.
- GPT corrected Claude's lean: "one git writer per checkout" with subagents editing in the parent tree is still many writers per tree. The invariant is **one exclusive owner per writable workspace, bounded write slots (~4), one validated integration lane**.
- Agreed target: two seat clones + a small pool of persistent ext4 worktrees (never drvfs/tmpfs), recycled only after recovery; writing tasks queue when slots are full; D:\ becomes a Windows build-staging checkout pinned to a candidate sha.
- `./publish` is salvageable: replace per-path 3-way merge with `git merge-tree --write-tree`, persist submission→accepted-sha receipts and teach the handoff gate to read them (fixes the "unpushed forever" refusals); retire shared-tree `--catchup`; validate the candidate before push.
- Coordination files: one immutable file per event/lesson (generated views for reading). `merge=union` is acceptable only as a stopgap for strictly append-only, order-insensitive JSONL — never for multi-line Markdown like LESSONS_INBOX.
- jj: pilot only, after ownership/integration are fixed.
- First change: harness-enforced exclusive workspace ownership with a bounded slot pool.

## Brief sent

## Second opinion wanted: which multi-agent git workflow should this project actually use?

I want your honest, adversarial judgment, not reassurance. Please disagree with my lean if it is wrong.

### The project and its real flow
- RimMandrake: a RimWorld mod project. One git repo, ~28,500 tracked files, 3.2 GiB packed, ~180-270 commits/day, pushed to GitHub over SSH.
- Machine: Windows desktop; all agents run in WSL2 (Ubuntu). The canonical checkout lives on the Windows drive (`D:\` = `/mnt/d`, drvfs/9p): `git status` takes ~2 s normally, 52 s measured under load. WSL ext4 home has 870 GB free and is fast. `/tmp` is an 18 GB tmpfs. 14 cores, 35 GB RAM.
- Agents: two long-lived Claude Code windows ("seats"): BENCH (orchestrator, sits with the owner) and FOUNDRY (pulls a work queue autonomously, owns `src/`, builds, deploys into the one live RimWorld game). Plus subagents spawned freely by both: often 4+ concurrent writers. Seats never message each other; coordination goes through an append-only event ledger in git (`infrastructure/state/ledger/events/<SEAT>.jsonl`, sharded per seat) plus append-only markdown inboxes such as `LESSONS_INBOX.md`.
- One shared physical game: a lock (`rimflow bridge take/release`) guards the live game and its mod config. Build output is deployed while the game is down.
- No `.gitattributes` exists, so there is no union merge driver on the append-only files.

### History: three regimes
1. **Shared checkout (until ~2026-09-24):** everyone commits in the one D:\ checkout and index. Incidents: on 09-25 a refused `git merge` ran git's internal stash, hard reset and re-apply; a peer's `index.lock` made the re-apply fail, and **215 uncommitted files vanished with nothing in the reflog**. On 09-18 a subagent's `reset --hard` ate 3 staged files. On 09-26 a sync script dropped a peer's commit. Bare `git commit` swept other agents' staged files. Answer: hooks forbidding reset, stash and merge in the shared tree, plus path-scoped commits only.
2. **Worktrees (from 09-25 as the main mode):** any subagent touching more than a couple of files gets `isolation: worktree`. The harness puts it under `.claude/worktrees/` **on drvfs**, as a full 28k-file checkout of about 4 GB each. Measured on 10-01: 130-132 registered worktrees and 146 local branches, 68 never merged, holding 257 unique commits. Manual worktrees in /tmp filled the 18 GB tmpfs to 100%. More than 100 dead worktrees had to be trimmed, and a prune dry-run over them took over 10 minutes and timed out. Worktree pushes hit credential-manager failures. The shared tree fell **303 commits behind origin** with about 2,250 untracked files, so `pull --rebase` and `reset --keep` refused. Agents constantly report "I can't push safely from here." An agent OOM-killed with an unpushed commit in a locked worktree stranded it. Throughput in the worktree week was 178 commits/day against 268 the week before and 217 over 43 days. Commits whose subjects are about recovery, lock, stash or conflict rose from 2.4-2.6% to 4.2%. (One week of data, and agent count may differ.)
3. **New fix, shipped 10-01: `./publish`, plumbing with no checkout.** It builds a commit in a private temp index on top of `origin/main`, does a per-path 3-way merge, unions ledger shards by line, retries push races up to 8 times without force, and prints `PUBLISHED <sha>`. `--catchup` moves the shared tree forward per path with a compare-and-swap on HEAD. The first day already shows two failure modes:
   - Work published by `./publish` lands on origin under **new shas**, while the agent's original local commits (e.g. `4e2b103f3`, `e55ff18da`) stay in the shared tree as "unpushed". Retiring them needs a reset or ref move, which is forbidden in the shared tree. So every unpushed-work checker, including the handoff gate, refuses forever even though nothing is actually unsaved.
   - `./publish` refused four lessons because `LESSONS_INBOX.md` had been appended upstream in overlapping lines. Concurrent appends to the end of a file read as a 3-way conflict.

### My (Claude's) current lean
The root defect in every regime is **the wrong number of writers per checkout**: too many in one (regime 1), or too many short-lived heavy checkouts (regime 2). Regime 3 routes around the checkout, but leaves it diverged.
- **One writer per checkout, and few checkouts.** Each seat gets its own normal clone. FOUNDRY keeps D:\ because the Windows build reads it; BENCH gets an ext4 clone. Each has its own index and a plain `pull --rebase && push`. Because exactly one agent writes each tree, reset and ref moves become safe again, and the forbidden-operation hooks can relax there.
- **Subagents do not get their own checkouts by default.** Read-only work needs none. A writing subagent edits disjoint paths in its parent seat's tree, and the seat commits with explicit pathspecs. Alternatively it returns a patch. A worktree is used only for long isolated builds, comes from a small fixed pool of reusable worktrees on ext4 (never drvfs or tmpfs), and is reset to origin/main on reuse.
- **Make append-only coordination files conflict-free by construction.** Either use one file per event or lesson (as Lodestar's `journal/` does), or set `merge=union` in `.gitattributes` for the jsonl shards and inboxes. Either removes the overlapping-append refusals in rebase and in publish alike.
- **Keep `./publish` only as a fallback**, or retire it. Its own failure (orphan local commits that a checker cannot clear) is a symptom of publishing from somewhere other than where the commit was made.

### Questions
1. Is "one writer per checkout, few checkouts" right, or is there a better known pattern for N concurrent LLM agents on one repo with a single physical deploy target? Cite real practice: merge queues, stacked diffs, git-butler virtual branches, jj (Jujutsu) workspaces, patch-queue models.
2. Is the plumbing publisher (regime 3) salvageable, e.g. by having it fast-forward the agent's own ref afterwards, or is it an architectural dead end? What are its hidden risks? (A per-path 3-way merge into origin/main with no build or test run is my concern.)
3. Should writing subagents edit inside the parent seat's tree on disjoint paths, return patches, or use pooled worktrees? Which fails least badly when the agent is OOM-killed mid-task?
4. `merge=union` versus one file per event for the jsonl ledger and the markdown inboxes: which is safer? (Union can duplicate or interleave lines. Is that acceptable for append-only logs?)
5. Would jj (Jujutsu, with its operation log and first-class conflicts) materially solve this for agents, or add a new class of confusion?
6. Am I missing a failure mode in my lean?

Please give a ranked recommendation and the single most important change to make first.

## GPT-6.1 Sol reply

Your lean is mostly right, but it contains a contradiction: **writing subagents in the parent’s tree means there are still multiple writers per checkout.** Having one seat own Git commands does not make rebase, reset, builds, or recovery safe around those writers.

I would use this invariant: **one exclusive owner per writable workspace, bounded write concurrency, and one validated integration lane.**

**The single most important change first: enforce exclusive workspace ownership in the harness, including subagents.** When all workspace slots are occupied, queue writing tasks. Do not reduce checkout count by putting concurrent writers together.

My ranked recommendation is:

1. **Two independent seat clones, with a small pool of persistent ext4 worktrees for substantive writing tasks, feeding one integrator.** Start with roughly four total writer slots; adjust for memory and build pressure. Each task gets a branch, exclusive workspace ownership, and durable checkpoints. FOUNDRY can own integration and deployment while both seats submit work through refs and ledger events.
2. **Two seat clones with writing serialized within each seat; subagents return durably saved patches.** This is simpler and a reasonable first deployment if maintaining parallel write throughput is less important than reducing operational complexity.
3. **Concurrent disjoint-path editing inside a seat’s checkout, only as a supervised exception.** It requires stopping every editor before synchronization, destructive commands, or release builds. That coordination burden undermines the simplicity you want.

Your worktree week demonstrates **bad placement and uncontrolled lifecycle**, not that isolation was wrong. Four roughly 4 GB checkouts are inexpensive against 870 GB free. Worktrees have separate indexes and HEADs while sharing repository objects, refs, and usually configuration; separate seat clones provide a useful additional administrative boundary. [Git worktree documentation](https://git-scm.com/docs/git-worktree)

I would also make `D:\` a **Windows build staging checkout pinned to a candidate revision**, if the build needs Windows-local files. Keep Linux authoring and the pool—including their underlying Git object stores—on ext4. Merely having a Windows build read the source does not require every agent’s development checkout to live on drvfs. Microsoft recommends keeping files on the filesystem native to the tools doing the work. [WSL filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems)

The established practices support this architecture:

| Practice | What it contributes here |
|---|---|
| Merge queue | Validates the combination of a submission, current main, and earlier queued work. This supplies the integration boundary your proposal lacks. [GitHub documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) |
| Topic branches and patch queues | Separate contribution from acceptance. Git itself documents using both maintainer merges and contributor patch submissions. [Git workflows](https://git-scm.com/docs/gitworkflows) |
| Stacked diffs | Express dependencies between tasks. They help when B requires unpublished A; they do not isolate concurrent filesystem writers. [Graphite documentation](https://graphite.com/docs/restack-branches) |
| GitButler virtual branches | Separate changes within a shared checkout, but retain shared filesystem, generated files, dependencies, and runtime state. Its agent documentation recommends worktrees where those need isolation. [GitButler parallel agents](https://docs.gitbutler.com/ai-agents/parallel-agents) |

You do not need a PR for every microcommit. Queue completed tasks or sensible batches. GitHub’s native merge queue has repository eligibility restrictions; a local integrator can implement the same principle. Neither implementation requires the seats to message each other directly.

**The publisher is salvageable, and changed SHAs are not evidence of an architectural dead end.** Patch application, rebasing, and squash merging routinely change commit identity. Your defect is that publication and acceptance tracking disagree about what constitutes saved work.

I would salvage its submission and push machinery, but replace bespoke per-path integration with Git’s complete merge machinery where possible. `git merge-tree --write-tree` performs a real merge without touching the working tree or index, including rename detection and file/directory conflicts. Git documents a `merge-tree → commit-tree → update-ref` pipeline. [Git merge-tree documentation](https://git-scm.com/docs/git-merge-tree)

“Fast-forward the agent’s ref afterwards” works only with appropriate ancestry:

- If submission `S` diverges from upstream `U`, and published commit `P` has only parent `U`, then `S → P` is **not** a fast-forward.
- A genuine merge commit with parents `U` and `S` makes it possible—but only when integrating the complete submission. Adding `S` as a parent while publishing selected portions falsely represents the omitted work as merged.
- If you prefer rebasing or squashing, preserve the submission ref and record a durable **submission ID/source SHA → accepted SHA** receipt. Teach the handoff gate that protocol.

Moving a checked-out branch ref alone also leaves the index and working files unreconciled. Even a legitimate fast-forward belongs at an exclusive owner’s synchronization boundary.

The publisher’s important hidden risks, based on your description rather than a code audit, are:

- **Mutable input:** a private index does not prevent collecting files from different moments while agents edit them. Publish an immutable submitted commit.
- **Incomplete integration:** independent blob merges can miss rename/delete, mode, binary, symlink, and directory/file interactions.
- **Untested composition:** clean textual merges can break cross-file assumptions. Every push-race retry can produce a new candidate requiring validation.
- **Unsafe catchup:** HEAD compare-and-swap protects a ref value, not working-file bytes or a sequence of file replacements. A crash can leave a partially transitioned tree. [Git update-ref documentation](https://git-scm.com/docs/git-update-ref)
- **Ambiguous success:** the remote may accept a push before the client loses its connection. Retrying needs a stable submission ID and remote reconciliation.
- **Bypassed policy:** plumbing needs explicit validation rather than assuming the ordinary commit-hook workflow ran. [Git hooks documentation](https://git-scm.com/docs/githooks)

The appropriate sequence is: persist submission → construct and persist candidate → materialize and validate that candidate → push without force → reconcile acceptance → record receipt → synchronize the producer at an exclusive boundary.

I would retire shared-tree `--catchup`. I would also avoid maintaining two publication routes to main: ordinary seat pushes plus a fallback publisher recreate competing integration policies.

**For OOM recovery, persistent exclusive workspaces fail least badly.**

| Subagent mode | After an OOM kill |
|---|---|
| Exclusive persistent worktree | Checkpoints and unfinished files remain attributable to one task; other tasks stay isolated. |
| Incrementally saved patch against a pinned base | Saved progress survives; unapplied work remains separate from the parent. |
| Patch returned only in the final response | The deliverable may disappear before submission. |
| Shared parent-tree edits | Files may survive, but the parent inherits mixed, potentially incomplete work. |

Use patches for small changes that do not need a mutable build environment. Save them incrementally on durable storage, with their base revision. Use pool slots for substantial implementation and testing.

**Pool reuse must follow recovery, not agent exit.** Ensure the old process and descendants cannot resume writing; preserve commits, dirty changes, and relevant untracked files; then reconcile acceptance before resetting the slot. Branch lifetime need not equal workspace lifetime: you can recycle a checkout while retaining its task ref. `git worktree lock` protects against pruning/removal; it is not an editor ownership mutex. [Git worktree documentation](https://git-scm.com/docs/git-worktree)

One owner also does not make `reset --hard` safe for that owner’s unfinished work. Reflogs record reference changes, not arbitrary unsaved file versions. Relax blanket bans only alongside preservation and exclusive ownership rules. [Git reset documentation](https://git-scm.com/docs/git-reset), [Git reflog documentation](https://git-scm.com/docs/git-reflog)

**For coordination records, prefer one immutable file per event or lesson.** Give each record a unique ID; reject an existing ID with different content. Publish complete records and represent corrections as subsequent records. Generate consolidated JSONL and Markdown views for readers.

This preserves lesson boundaries and makes duplicate submissions detectable. It also avoids treating the position of a line as event identity or chronology.

`merge=union` is an acceptable temporary mitigation for tightly constrained JSONL: one complete event per line, final newlines, strict append-only enforcement, schema validation, and consumers that tolerate arbitrary order and deduplicate by event ID. It is unsuitable if replay depends on file order. Git explicitly warns that union can leave added lines in arbitrary order and requires verification. [Git attributes documentation](https://git-scm.com/docs/gitattributes)

I would not use union for multi-line Markdown lessons: conflict regions can combine pieces without preserving the intended lesson structure. If individual event files eventually create excessive file-count overhead, use uniquely named immutable segments. The essential property is that two producers never append to the same published object.

**jj would materially improve recovery of recorded repository states, but I would adopt it after fixing ownership and integration.** Automatic working-copy snapshots, operation history, and first-class conflicts address real Git pain. They still do not protect edits overwritten before snapshotting, shared build state, or the physical game. [jj working-copy documentation](https://docs.jj-vcs.dev/latest/working-copy/), [operation log](https://docs.jj-vcs.dev/latest/operation-log/), [conflicts](https://docs.jj-vcs.dev/latest/conflicts/)

Its hazards are relevant to autonomous agents:

- The operation log spans the repository and its workspaces; naïve “undo my last operation” can target another workspace’s operation. [Maintainer discussion](https://github.com/jj-vcs/jj/discussions/9604)
- Current compatibility docs list Git attributes and hooks as unsupported, and Git staging is ignored. Existing Git policies would need explicit replacement; harness policies are a separate matter. [jj Git compatibility](https://docs.jj-vcs.dev/latest/git-compatibility/)
- Default snapshotting automatically tracks unignored new files. Your 2,250 untracked files make ignore and tracking policy a prerequisite.
- Its push semantics allow protected rewrites rather than providing plain Git push’s default fast-forward-only behavior. Protect main independently. [jj push reference](https://docs.jj-vcs.dev/latest/cli-reference/#jj-git-push)

A single isolated pilot is worthwhile. A project-wide migration now would mix workflow repair with a new command and recovery model.

Three additional failure modes deserve attention:

- **Mergeable coordination is not exclusive coordination.** Both seats can read stale ledger state and claim the same task. Unique event files eliminate textual conflicts, but claims still need serialized allocation or an ownership protocol resolved before work begins.
- **The game lock does not identify the deployed source.** Build from a frozen candidate, record source SHA, artifact identity, and relevant configuration, then deploy that artifact under the lock. Prevent an older queued artifact from silently replacing a newer deployment.
- **“Unmerged” and “unpushed” ancestry checks are not acceptance checks.** Some of those 257 unique commits may represent already accepted changes under different SHAs. Do not reclaim them solely from branch ancestry, and do not treat patch similarity alone as proof of complete acceptance.

Your throughput figures justify intervention, but cannot identify the winning architecture from one confounded week. Measure completed accepted tasks, integration latency, recovery effort, and lost work alongside commits/day. The strongest evidence you supplied favors bounded isolation with durable recovery—not concurrent editing inside fewer trees.