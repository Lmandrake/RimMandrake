## 1. Wrong / Unsafe, Ranked

1. **Phase 5: pooled slots push directly to `main`.**  
   This violates the earlier “one validated integration lane” recommendation. Six slots plus two seats doing `pull --rebase && push` is still a mainline race, just on ext4. It reduces filesystem trauma, not integration risk.

2. **Phase 5: automatic rescue-push of dead dirty slots is unsafe.**  
   X1 says dirty/unpushed rescue was written but **not exercised**. Auto-committing and pushing dirty work can publish junk, partial edits, secrets, generated churn, bad binaries, or unrelated untracked files. Rescue should first preserve locally or to an explicit archive ref after classification.

3. **Phase 1: success bar overclaims.**  
   The cited replay improvement to **13.6%** includes removing `CODE_REVIEW_STATUS` and generated-ish residue. Phase 1 only removes rows 1–4 plus ledger union. `CODE_REVIEW_STATUS`, DIRTY_LOOP, artpipe, lessons remain later. The plan’s “K=5 ≤ 15%” may still be close, but the evidence quoted does not exactly match the phase.

4. **Phase 6: D:\ mirror freeze is late.**  
   The highest-risk incidents came from the shared writable D:\ tree. The plan delays freezing it until after clones, hooks, pool, artpipe, and FOUNDRY migration. That leaves the old hazard alive too long.

5. **Phase 2.4 / Phase 1: generated views leaving git before consumer migration is brittle.**  
   Hooks, hub artifact, `rimflow`, GitHub browsing, remote owner workflows, and agent prompts all depend on this being installed everywhere. The plan treats regeneration as easy; the evidence only supports conflict reduction, not operational continuity.

6. **Phase 2.2: PID-only slot ownership is weak.**  
   X1 fixed the immediate `getppid()` trap, but PID liveness alone has PID-reuse and descendant-writer hazards. Lock records need process start time/session id, transcript, slot generation, and probably a “no descendants still writing” check.

7. **Phase 2.6: keeping emergency `./publish` preserves two integration policies.**  
   The plan says plain git replaces it, then keeps plumbing for emergencies. That is exactly how policy drift returns unless the fallback is severely fenced and produces the same validation/receipt semantics.

## 2. Evidence Not Supporting Plan Assertions

- It does **not** prove dirty-slot rescue works. X1 explicitly says that path is unmeasured.
- It does **not** prove 3 slots/seat is the right capacity. Pool-full behavior was measured, not throughput, memory pressure, or queue latency.
- It does **not** prove direct slot pushes to main are safe under real agent behavior.
- It does **not** prove render hooks are reliably installed, run, or accepted by all consumers.
- It does **not** prove `dotnet.exe` works from UNC/ext4; the plan correctly marks this unmeasured, but later phases depend on the result.
- It does **not** prove ledger `merge=union` is semantically safe in the real readers; Phase 0 still needs to verify ordering, IDs, trailing newlines, and dedupe.
- It does **not** prove archive-not-review of 68 branches is harmless. It preserves reachability, not acceptance.

## 3. Missing

- A real **integration lane**: candidate materialization, test/build policy, source SHA, deploy artifact identity, acceptance receipt, and serialized main update.
- A stale task-claim protocol. Textual merge fixes do not stop two agents from claiming the same work.
- Slot recovery rules for untracked files, ignored files, large files, generated files, and partially written files.
- PID reuse / process-tree / session identity handling.
- Push ambiguity handling: remote accepted push but client timed out.
- Windows path audit beyond listed tools: Explorer scripts, editors, launchers, game tooling, symlinks, watchers, hardcoded `D:\`, UNC-hostile libraries.
- Migration hazard for Claude memory/settings/hooks before first ext4 launch.
- Rollback procedure after `git rm --cached` of generated artifacts if agents depend on GitHub-visible files.
- Branch/archive namespace policy: who can delete archive refs, how long retained, how searched.
- Hook distribution enforcement via `core.hooksPath`, not manual clone hygiene.

## 4. Phase Order

Not quite.

I would reorder:

1. **Phase 0 stays first.**
2. **Immediately freeze or strongly guard D:\ writes** before broader cleanup, even if full mirror conversion waits.
3. **Move BENCH to ext4 clone early** to stop new drvfs damage.
4. Then **Phase 1** generated/ledger reduction.
5. Then **FOUNDRY ext4/build route/DLL rule**.
6. Then **pool**, after rescue and integration semantics are hardened.
7. Then drain/archive old worktrees.
8. Retire old verbs last.

The plan optimizes conflict rate before eliminating the known destructive shared-tree hazard. That is backwards for safety.

## 5. Owner Decisions

1. **Run Phase 1 now:** qualified yes, but only after Phase 0 verifies ledger semantics and after consumers of queue views are migrated or warned. Do not claim the full replay number unless Phase 1 scope matches it.

2. **Move both seats to ext4 and make D:\ read mirror:** yes. This is the strongest supported decision.

3. **3 persistent full slots per seat:** maybe. The evidence supports bounded ext4 slots, not the number 3. Start with 2/seat or 3/seat behind telemetry and queueing.

4. **Archive, don’t review, 68 unmerged branches:** yes for reachability cleanup; no if interpreted as “accepted or irrelevant.” Archive first, classify later. Do not infer acceptance from ancestry or patch similarity alone.

5. **No Jujutsu, not even pilot:** yes for RimMandrake now. The measured jj hazards are directly relevant.

## 6. Single Change

Add a serialized **integration gate** and forbid pooled slots from pushing directly to `main`.

Slots and seats should push task refs/submission refs; one integrator materializes candidates, validates, records `source_sha → accepted_sha`, then advances `main`. Without that, the redesign fixes storage and checkout ownership while leaving mainline acceptance as a race.