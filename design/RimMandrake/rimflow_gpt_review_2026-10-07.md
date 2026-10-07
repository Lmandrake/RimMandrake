Rimflow needs one additional state, a real reservation mechanism, and a source check before dispatch. Its central error is treating **implementation completion, acceptance, and active work as the same lifecycle**. Changing `offline` to `bridge` alone would hide some duplicate work while preserving that error.

I would choose **A over C**: keep one item, record when its implementation is complete, and track its remaining acceptance obligations on that item.

1. **The root causes, ranked**

**First: the item has no enforceable boundary between implementation and acceptance.** A builder finishes its actual assignment but cannot record that fact authoritatively. Meanwhile, acceptance has neither a clearly responsible seat nor an admission policy matched to bridge capacity. Adding `built` solves the representation problem; it cannot solve a verification queue whose arrival rate exceeds its service rate. Those rates are currently unmeasured.

**Second: publication and tracker completion are separate operations with no recovery protocol.** The prescribed sequence depends on agents remembering several independent writes. Commits, notes, trailers, and ledger transitions can disagree indefinitely. Context loss between operations makes this inevitable. The missing importer is one symptom; the deeper problem is that dispatch never reconciles those disagreements.

**Third: ownership is being used as both assignment and execution control.** FOUNDRY owning an item says nothing about which of its subagents is executing it. `claim` advertising work and `start` hiding it produce opposite failure modes. The thirty-minute contest rule is not a reservation: it neither excludes concurrent workers nor establishes when work becomes available again.

**Fourth: completion is simultaneously too strict in doctrine and too weak in code.** Agents face an expansive, sometimes live-only definition of done, while `close --sha HEAD` can declare completion without demonstrating anything. The system rewards agents that ignore doctrine and strands agents that follow it. Free-text, unversioned criteria make the contradiction harder to resolve.

**Fifth: the ledger preserves history but does not necessarily preserve causality.** Sorting concurrent events by timestamps and verb rank gives deterministic replay, not necessarily correct transitions. A delayed claim could overwrite a later execution state unless transition guards prevent it. An `flock` does not coordinate separate clones, and `merge=union` does not provide atomic reservations. This becomes important as soon as leases are introduced.

Several claims in the document need qualification:

- **The “~115 already-built” items are candidates, not established completions.** That number appears to be 99 doing/offline plus 16 ready/offline with commit-subject matches. They are a subset of the 472, not an additional population.
- A subject naming an item proves association, not full implementation. “4 of 7 owed” is direct evidence of partial completion.
- A commit existing locally does not establish that it was pushed, merged into the intended branch, or remains present in current source.
- Searching only **since the last ledger event**, as option D proposes, would miss a build followed by a note or repeated claim. Search from item creation, or from an explicit reconciliation checkpoint.
- “Last event” age measures tracker activity, not progress. Notes and repeated claims can make abandoned work look fresh.
- The stated snapshot is ~01:20 UTC, but examples include events at 01:21 and 01:25. Label those as later observations.
- The 14-of-15 dispatch result and near-100% handoff pickup need denominators, selection rules, and dispatch timestamps. Current state alone cannot establish what was already built when a dispatch occurred.
- “No satisfying event” is not a reason to exclude offline items from staleness checks. Publication is precisely the satisfying event the system should recognize.

2. **The minimal redesign**

Keep the existing lifecycle and add **`built`**, defined as: *the implementation scope is complete, supported by offline evidence, and published to the designated source target*. It does not assert live acceptance.

| State | Meaning | What dispatch may offer |
|---|---|---|
| `proposed` | Work suggested; scope may be thin | Inspect, define, or begin it under existing policy |
| `ready` | Implementation or corrective work remains; no active reservation | A specific implementation action |
| `doing` | Implementation action has a valid execution lease | Nothing to another worker |
| `built` | Implementation complete; acceptance obligations remain | A specific acceptance action |
| `done` | All required criteria satisfied or explicitly waived | Nothing |
| `dropped` / `superseded` | Existing terminal meanings | Nothing |

The transitions should be:

```text
proposed/ready → doing → built → done
                    ↘ done       [no outstanding acceptance criteria]

doing --lease expires/releases→ ready

built --confirmed defect + corrective scope→ ready
```

A failed feature check records the defect and returns the item to corrective work. A failed test setup leaves it `built`, with the environmental impediment recorded. Terminal items remain final; later defects become new linked items.

**Change these fields and events:**

| Change | Required behavior |
|---|---|
| Separate `owner_seat` from `lease` | Ownership assigns responsibility; a lease reserves one action |
| `claim` | Acquires a lease and starts the action; never makes an active item offerable |
| `implemented --sha …` | Records scope version, offline evidence, publication target, and outstanding criteria; enters `built` or directly `done` |
| Extend `verify` | Attach results to criterion IDs, implementation/scope version, tested artifact, and configuration |
| Guard `close` | Require satisfied criteria; remove the default-to-HEAD shortcut |
| `reconcile` | Record examined commits/source, complete/partial/unrelated verdict, and explicit remaining work |
| `renew` / `release` | Update or release a specific lease token |
| Transition guards | Reject stale ownership, scope, or lease revisions |

For a deliberate acceptance waiver, require an explicit OWNER event naming the criterion and reason. Do not silently convert missing evidence into a pass.

`implemented` must validate that its commit is reachable from the designated published target. A local SHA is insufficient. If publication is unavailable, retain the candidate SHA and dispatch **publish/reconcile**, rather than another implementation action.

A **single ledger event** should record implementation completion and its outstanding obligations. Do not make “mark built” and “retag needs” separately forgettable operations.

**Split criteria by responsibility and capability.**

Store a small structured acceptance manifest in the ledger; keep detailed explanations in prose:

```text
scope_version: 1

O1: implementation and installation complete
    phase: implementation
    needs: [offline]

O2: relevant compile/static checks pass
    phase: implementation
    needs: [offline]

L1: specified interaction observed
    phase: acceptance
    needs: [deployed, game-up, bridge]
```

Owner review can be an acceptance criterion requiring `[owner]`. Art installation that can be performed offline remains implementation work. Such an item is **partial**, not `built`.

`needs` should describe the **next outstanding action**, derived from its criterion or corrective scope. Capabilities can be combined: `bridge` availability alone does not establish that the right artifact is deployed.

This preserves the owner’s prohibition on a start-completeness gate. Thin items can still be started. But entering `built` requires a stated scope and evidence that its implementation obligations are complete. It does not require three prose headings.

**Make `next` a guarded dispatcher.**

Keep `rank()` pure over its inputs. Make the command prepare those inputs and reserve the selected action. Use `next --peek` for an advisory, read-only view; normal agent dispatch should atomically reserve.

Before offering implementation, `next` should:

1. Replay the ledger and check terminal state, owner, target, effective dependencies, and active leases.
2. Check structured implementation records. `built` items never enter the implementation pool.
3. Load a batched git index keyed by the relevant source heads. Match exact item IDs in trailers and subjects, including commits predating later notes or claims.
4. For an unrecorded match, inspect the commit and current target source: changed files, relevant symbols/assets, partial-work language, and whether the implementation survived later changes.
5. If completion is uncertain, offer **reconcile this item**, with the evidence attached—not “build this item.”
6. Offer implementation only with an explicit remaining action. A partial item should say “implement the remaining three forms,” not repeat its original broad specification.
7. Reserve that action under the dispatcher lock, rechecking the item revision and source inputs before returning it.

A subject match is a reconciliation trigger. It is not an automatic close. A recorded “unrelated” or “partial” verdict prevents repeatedly investigating the same commits; new relevant commits trigger another check.

For the source check, use the designated integration/release branch, not arbitrary `HEAD`. Record which remote ref was checked. When remote freshness cannot be established, say so and avoid asserting publication.

**Make trailers useful without making them magical.**

Introduce an explicit `Implemented:` trailer consumed by an idempotent reconciliation command. Existing `Closes:` trailers are completion claims to evaluate under the new evidence rules. Neither should bypass source or criteria checks.

A publish command can perform the normal reconciliation. `next` provides recovery when that command was skipped. No commit-blocking hook is needed.

**Claims should be leases.**

Use an opaque token containing a run/session identity and worker nonce; subagents do not need permanent identities.

- Default duration: **45 minutes**, renewed every **10 minutes**.
- Only the token holder can renew, release, or finish that execution.
- Renewal requires the lease still to be valid; an expired worker must reacquire before continuing.
- Lease expiry uses lease timestamps, not notes or arbitrary item activity.
- After expiry, unfinished implementation becomes dispatchable only after source reconciliation.
- Expiry never turns `built` back into unbuilt work.
- Reassignment explicitly revokes the old lease.

All workers sharing an owner seat must use **one authoritative reservation lock/store**. On one machine, that can be the existing CLI with a canonical local lock. Separate clones cannot safely allocate reservations by independently appending files and later merging them. Fix that deployment assumption before promising exclusivity.

The item lease and existing bridge lock remain separate: reserving acceptance work does not grant control of the game.

**Fix dependencies and views.**

Replace the generic blocked interpretation with two cases:

- Explicit dependencies: automatically reevaluate them.
- Manual impediments: retain a reason and responsible seat until explicitly resolved.

A dependency should specify whether it needs the predecessor **built** or **done**. Compilation against a predecessor’s implementation should not wait for its live acceptance. Closing one dependency must not clear unrelated blockers.

Show four useful queues: implementation available, active leases, built awaiting acceptance, and impeded work. Handoffs should link to these projected actions rather than become another source of state.

3. **A safe, cheap migration**

Do not blanket-close 115 items, and do not rewrite hundreds of prose files first.

**Take one reproducible snapshot** of ledger inputs, item prose, source target, and inspected remote refs. Generate a reconciliation manifest for all 472 open items with proposed changes and evidence.

Use four buckets:

| Bucket | Migration action |
|---|---|
| Implementation complete, supported by source | Import as `built`; attach known remaining acceptance criteria |
| Partially implemented | Preserve shipped slices; state the remaining implementation action |
| No relevant implementation found | Keep proposed/ready; offer an explicit action |
| Unclear, obsolete, or contradictory | Route to reconciliation; drop/supersede only with a substantive reason |

Start with the six open `Closes:` candidates, then SHA-bearing notes, then subject-only matches. Inspect current source before accepting any of them. Treat the 115 offline candidates as a shortlist.

Append provenance-bearing migration events; preserve history. `built` is safer than terminal closure when live obligations or scope remain uncertain. Close offline-only items only where their actual criteria are demonstrated.

For legacy `doing` items, end the fiction that they have active workers. Reconcile them, then place them in `built` or `ready` with no lease. Do not simply requeue all 232 for implementation.

Batch checks at one source snapshot. A shared compile can support many compile criteria; it cannot prove every feature. Generate small acceptance manifests from existing prose and inspect ambiguous cases. Avoid a global prose-format conversion.

Then assign **BENCH responsibility for acceptance triage** using the existing bridge. Group compatible checks into the same deployment/game session. Prioritize the next release, unobserved high-risk mechanisms, and dependencies that acceptance actually blocks. Existing owner play can supply evidence when its artifact, configuration, and observed criterion are recorded.

Measure three quantities initially: implementation completions, acceptance completions, and duplicate implementation dispatches. If acceptance arrivals exceed completions, reduce admission or explicitly defer particular obligations. A state name cannot eliminate that capacity constraint.

4. **Answers to the five questions**

**Q1 — A or C?** Choose **A**. One item with implementation and acceptance stages keeps responsibility and evidence together. Spawn a separate item only when the follow-up has an independently useful scope—such as a discovered defect or broader test investigation. Mandatory proof successors would inflate the board without increasing bridge capacity.

**Q2 — Ledger purity or direct git checks?** Use **both, at different boundaries**. Structured ledger events are authoritative workflow facts; git is authoritative source evidence. Publish reconciliation supplies the normal events, and dispatch performs a cached source check to recover missed ones. Preserve pure ranking, not blindness at dispatch.

**Q3 — Definition of done and backlog ownership?** Builders finish by satisfying implementation criteria and recording `built`. `done` still requires the item’s acceptance criteria or explicit waivers. BENCH owns acceptance triage; the existing bridge holder executes selected checks. Reuse observations across items only when they demonstrate the relevant criteria for the tested implementation and configuration.

**Q4 — Minimal claim design?** Separate owner assignment from a tokenized, expiring action lease. Acquire it atomically when dispatching. Claims hide active execution; expiry triggers reconciliation before redispatch. The source check handles work published before a reboot or lost completion event.

**Q5 — Structurally missing?** Yes: dependency satisfaction levels, causal transition guards, an accountable acceptance queue, and evidence tied to scope/artifact versions. Automatically surface items when their actual dependency conditions become satisfied; do not indiscriminately unblock them because one referenced item closed.

5. **The first three things this week**

1. **Stop duplicate dispatch.** Add git/source reconciliation before implementation offers, atomic execution leases, and explicit remaining-action output. Change `claim` so active work immediately stops being advertised.
2. **Make implementation completion representable.** Add `built` and one evidence-bearing `implemented` event; derive remaining needs, expose acceptance work, and rewrite the contradictory doctrine and close-warning behavior together.
3. **Reconcile the existing board and run one acceptance batch.** Import supported completions, recover partial scopes, retire fictitious active work, and use an existing game session to establish actual acceptance throughput.

I would explicitly **not** build a new tracker, orchestration service, dashboard, mandatory proof-item factory, blanket three-section completeness gate, commit-blocking hook, or automatic closer based on commit subjects. I would also postpone sophisticated priority scoring. The immediate requirement is that a dispatched action accurately describes work that remains.