# GPT blind answer: pipeline control surface

- Consult id: consult-20261118-103923-596267-fd188b
- Model: gpt-6.1-sol
- Time: 2026-11-18 10:39 PST (answered in 288s)
- Tokens: unknown
- Input: 00-problem.md only (blind)

---

I would choose a **single local control service that owns launch authorization, scheduling, and allowance accounting**, with a small imperative CLI.

The cause is split authority: several programs can start work, while authorization, holds, and accounting live in different records. A journal entry, another configuration flag, or a nicer wrapper cannot fix that while independent launchers retain authority.

Two designs can remove that cause. They share an enforcement boundary and accounting rules, but differ substantially in how the pipeline operates.

The commands below are proposed interfaces, using `cedar` as an example unit.

**Design A: a command service with one scheduler.** Every existing entry point becomes a producer of requests. Only the control service can authorize and launch work.

The tick submits “evaluate due work.” Autonomy submits a work proposal. A steward reports its result and requests a successor. Designer chains, judges, road-back builders, and scheduled roles do the same. None can launch a successor directly.

A deterministic scheduling function evaluates those requests, pipeline state, controls, and allowances. A transactional launch outbox hands authorized work to one launcher.

State lives on the dispatch host:

- A local SQLite database contains the authoritative event ledger, current projections, reservations, queue order, and launch outbox.
- JSONL shards and repository documents become exports. Publishing through git is outside the command path.
- Other clones use the service API. Their local configuration cannot authorize work.
- Configuration changes are versioned events, including policy changes and scheduling changes.

The CLI makes synchronous transactions through a local Unix socket. An acknowledgment means the change is durable and effective. No LLM, repository build, or publish script participates.

This design preserves stage-specific scheduling logic, but moves it into one deterministic decision engine. It dominates when the immediate priority is reliable control with the least migration.

**Design B: a declarative workflow reconciler.** Replace the separate orchestration programs with a versioned workflow specification and a desired-state reconciler.

The specification defines stages, transition conditions, role recipes, allowance policies, scheduling rules, and dependencies. Workers only execute assigned tasks and report observations. A builder cannot chain a designer; a steward cannot decide to launch a judge. Those transitions belong to the workflow.

Operators change desired state: paused, enabled, ordered, eligible after a timestamp, or assigned a particular allowance limit. The reconciler computes the necessary actions.

State consists of:

- A versioned desired-state document in the control database.
- An append-only ledger of observations and operator decisions.
- Rebuildable observed-state projections and an execution outbox.
- Repository exports of the workflow and desired state, for review and recovery.

Applying a document validates it and installs one revision atomically. A malformed change leaves the previous revision intact. One-off actions such as voiding a run are ledger transactions, not persistent booleans that reconciliation could repeatedly apply.

This removes bespoke orchestration code rather than centralizing it. It dominates when the workflow will keep expanding and the team is prepared to migrate its stage semantics into a declarative model.

The operator surfaces would look like this:

| Need | Design A: imperative control | Design B: desired state |
|---|---|---|
| Read one unit, including blockers and balances | `pc show cedar` | `pw status cedar` |
| Read everything compactly | `pc status` | `pw status` |
| Pause new work globally | `pc pause --reason maintenance` | `pw apply --set global.mode=paused --reason maintenance` |
| Resume globally | `pc resume` | `pw apply --set global.mode=running` |
| Stop one unit and cancel its active work | `pc hold cedar --cancel --reason owner` | `pw apply --set units.cedar.mode=stopped --reason owner` |
| Release that unit | `pc release cedar` | `pw apply --set units.cedar.mode=ready` |
| Disable an item | `pc disable cedar` | `pw apply --set units.cedar.enabled=false` |
| Enable an item | `pc enable cedar` | `pw apply --set units.cedar.enabled=true` |
| Add queue membership | `pc queue add build cedar` | `pw queue edit build --add cedar` |
| Remove queue membership | `pc queue remove build cedar` | `pw queue edit build --remove cedar` |
| Change order | `pc queue move build cedar --before fern` | `pw queue edit build --before fern cedar` |
| Replace an entire queue atomically | `pc queue replace build cedar fern` | `pw apply --set 'queues.build=["cedar","fern"]'` |
| Change an eligibility time | `pc defer cedar --until 2026-11-18T14:00:00-08:00` | `pw apply --set units.cedar.not_before=2026-11-18T14:00:00-08:00` |
| Change a consumable limit | `pc allowance set cedar blind.cycle --limit 3 --scope visit=7 --reason owner` | `pw apply --set units.cedar.visits.7.allowances.blind_cycle=3 --reason owner` |
| Grant a one-use exception | `pc exception cedar judge.look --uses 1 --reason owner` | `pw once grant cedar judge.look --uses 1 --reason owner` |
| Void a run and reverse its allowance effects | `pc void R123 --reason system-launch-failure` | `pw once void R123 --reason system-launch-failure` |
| Correct an alarm classification | `pc classify E456 --as infrastructure --reason evidence` | `pw once classify E456 --as infrastructure --reason evidence` |
| Forecast | `pc next --horizon 10m` | `pw preview --horizon 10m` |
| Inspect provenance | `pc trace R123` | `pw trace R123` |

In Design B, `queue edit` is a convenience operation that constructs and atomically applies a new desired-state revision. It does not create another queue authority.

Both surfaces need these precise semantics:

- **Pause:** prevent new starts; active work continues.
- **Pause with `--cancel`:** prevent starts, revoke pending starts, and terminate active work. Output distinguishes cancellation requested from cancellation completed.
- **Hold:** temporarily block a unit’s launches and stage advancement. Results arriving from active work are recorded.
- **Disable:** exclude an item until explicitly enabled.
- **Queue changes:** change membership or priority, but cannot override dependencies, holds, or eligibility.
- **Exceptions:** change a specified entitlement or rule. They cannot silently override global pause or launch authorization.

A normal acknowledgment should be something like:

```text
OK rev=842 cedar held active=0 pending=0 event=E842
```

One-unit status should answer the original six-command investigation in one bounded response:

```text
cedar stage=blind held=yes active=0 next=blocked:hold
looks=1 available=1 reserved=0; blind=2 available=2
queue=build:3 rev=842
```

**Both designs require the same hard launch boundary.** This is essential work, not optional hardening.

Only the launcher service may create pipeline execution units and obtain agent API access. Existing launch identities lose broad `systemd-run` privileges and raw provider credentials. Workers receive scoped run identities and access the provider through a gateway that checks authorization.

Every listed path must be converted:

| Existing path | Required replacement |
|---|---|
| Dispatch tick | Submit scheduler wake-up |
| Autonomy step | Submit proposal |
| Steward chain | Report completion and proposed successor |
| Separate Designer dispatcher | Submit proposal, or become a workflow edge |
| Judge launcher | Request judge task |
| Road-back builder | Report failed check; scheduler selects repair |
| Scheduled role run | Submit scheduled request |

Calling the old launcher directly must fail at the permission or credential boundary. A code convention saying “always call this wrapper” is insufficient.

Launches use a transactional outbox, deterministic run IDs, and fenced authorization:

1. In one transaction, check controls and eligibility, reserve allowances, and create the launch intent.
2. The launcher rechecks the fence before admission.
3. The runtime gateway validates the run before its first billable action.
4. Recovery reconciles the same run ID with its existing execution unit instead of creating another run.

Pause and admission must be serialized. A pause acknowledgment must account for in-flight admissions and revoke unstarted intents. An already admitted run appears as active; `--cancel` additionally revokes its execution authorization.

This guarantee assumes the pipeline’s service identities obey those permissions. A host administrator can deliberately bypass host controls; ordinary pipeline agents must not have that authority.

**Consumables should be reservations followed by eligible settlement.**

Do not decrement a counter when a launch is attempted.

For each resource and scope:

```text
available =
    granted entitlement
  + explicit adjustments
  - effective settled charges
  - live reservations
```

The resource registry defines its unit, scope, reservation point, eligible outcome, and settlement quantity. Examples:

| Resource | Scope | Eligible settlement |
|---|---|---|
| Owner-granted judge look | Owner grant / unit | A completed, valid judgment |
| Blind cycle | Stage visit | A valid completed challenge cycle |
| Automatic in-game run | Stage visit | An eligible completed acceptance attempt |
| Steward run | Product version | An eligible completed steward result |
| Design-chain allowance | Explicit local calendar day | An eligible completed chained design run |
| Stage spending allowance | Stage visit | Policy-defined eligible cost |

A valid judgment rejecting the product may consume a look. A missing executable, failed system call, unauthorized launch, cancellation caused by a stop, invalid agent result, or voided run does not.

For trustworthy accounting:

- Reserve before launch, preventing concurrent overspend.
- Settle only after the outcome is classified.
- Infrastructure failures release reservations automatically.
- Ambiguous outcomes remain unsettled pending classification.
- A void event reverses an existing charge or prevents a future one.
- Late results cannot charge a voided run.
- Repeating the same settlement or void is idempotent.
- Voiding active work revokes it; its reservation stays unavailable until execution is fenced off or confirmed stopped.

The command `pc void R123 --reason …` performs the entire correction. The operator should never need a second “refund” command.

An exception creates a scoped grant:

```text
pc exception cedar judge.look --uses 1 --reason owner
```

That grant is reserved and settled like any other entitlement. If the resulting run is voided, the exception remains unused. Optional expiry and role restrictions belong on the grant.

“Launch retries” and “refusal counts” need cleanup in the model. Infrastructure retry attempts and observed refusals are facts, not automatically consumable entitlements. Record them permanently; use separate backoff and circuit-breaker policies to stop runaway failures. Reclassification changes their policy consequences without erasing what happened.

Likewise, distinguish **allowance consumption** from **actual vendor cost**. Voiding a run restores its entitlement, but cannot undo money already billed. Preserve actual cost separately and enforce a physical spending guard against it.

The ledger remains append-only because corrections are new events:

```text
RunReserved → RunStarted → OutcomeRecorded → AllowanceSettled
                                            → RunVoided → SettlementReversed
```

Each event carries sequence number, command ID, actor, reason, target and scope, run reference, policy version, and relevant causal references. Commands accept reusable request IDs so transport retries cannot duplicate grants.

Database event rows are authoritative; projections are disposable. JSONL exports preserve event IDs and ordering. A checksum chain and external backups make modification detectable; append-only permissions alone are not tamper-proof storage.

**A forecast must execute the scheduler, not describe it.**

Both designs should expose one deterministic function:

```text
decide(state, logical_time, admitted_inputs, policy_version)
    → ordered decisions
```

Production and forecasting use that exact function. Queue tie-breaking, timer behavior, concurrency limits, timezone rules, and backoff are explicit inputs or persisted state. The function does not read the wall clock, filesystem, or network.

`next` takes an atomic snapshot, then advances a simulated clock through scheduled events. It reports the snapshot revision, policy version, assumptions, and decision reasons.

There is an unavoidable distinction: “the operator does nothing” does not mean “nothing changes.” Agents finish, dependencies fail, machines restart, and external services respond. No forecast can guarantee those unknown outcomes.

Therefore the output must distinguish:

```text
rev=842 policy=19 horizon=10m
+00:22 admit fern/build, assuming no intervening external events
cedar blocked throughout: hold
maple waits for R120; successor depends on its unknown outcome
```

The guarantee is:

> Given the same state, times, policy, and admitted input events, forecast and production produce identical decisions.

Every production decision logs those inputs and its decision hash. Replaying the forecast with subsequently observed events must reproduce production exactly. When reality diverges from the original forecast, the service identifies the first intervening event.

A forecast cannot promise successful process execution. It can promise what the scheduler will decide under its stated inputs. Calling conditional decisions unconditional “WILL start” would recreate the trust problem.

**Effort and command cost differ materially.** These are planning estimates, not measurements of the supplied system.

| Dimension | Design A | Design B |
|---|---|---|
| Usable initial implementation | Approximately 3–5 engineer-days | Approximately 1–2 engineer-weeks |
| Full launch-path migration, recovery, and tests | Approximately 1–2 engineer-weeks total | Approximately 2–4 engineer-weeks total |
| Ordinary command latency target | 10–100 ms locally | 20–250 ms, including validation/reconciliation |
| Compact acknowledgment | 15–40 output tokens | 20–60 output tokens |
| One-unit status | 60–150 output tokens | 80–180 output tokens |
| Ten-minute forecast | Target under 250 ms for this fleet | Target under 500 ms for this fleet |
| Forecast output | 100–300 tokens by default | 100–300 tokens by default |

These commands use **zero model inference**. The output-token figures describe text entering the Conductor’s context. Cancellation completion depends on process shutdown; the command can promptly acknowledge a pending cancellation.

Design A’s main failure modes are service unavailability, stale projections, missed legacy launch paths, and bugs in centralized scheduling. Fail closed on new launches; rebuild projections from events; test permissions and entry points directly. Its chief long-term risk is turning the scheduler into a large collection of special cases.

Design B’s main failure modes are incorrect workflow translation, reconciliation loops, invalid desired states, and incompatible workflow revisions affecting active runs. Validate before apply, pin running tasks to a workflow revision, and require explicit migration rules. Its strength is that sequencing and eligibility become inspectable data.

I pick **Design A now**, with a scheduling kernel that could later support Design B. There are roughly twelve units and several existing launchers; obtaining one authority is more urgent than rewriting the workflow language.

**The first hour should deliver a narrow vertical slice.**

Build:

- A local event store and projections for global pause and per-unit holds.
- `pc status`, `pc pause`, `pc hold`, and `pc release`.
- A launcher adapter that checks those controls transactionally and records accepted or denied admission.
- A fake runtime exercising that adapter, including the pause race.
- A migration flag that rejects resume while any known launch path remains unmanaged.

The immediate production action is to disable legacy launch triggers and leave the pipeline paused during migration. If the common credential/launcher boundary cannot be secured within that hour, do not claim a universal pause guarantee yet. The hour still produces a working control transaction and a clear migration gate.

Do not spend that hour building a dashboard, rewriting journals, or putting commands through the publish suite. Add allowance settlement, voiding, and exceptions in the next vertical slice, before re-enabling consumable work.

**The acceptance tests must prove both policy and enforcement.**

1. **Every entry point:** exercise tick, autonomy, steward chain, Designer dispatcher, judge, road-back builder, scheduled roles, and direct legacy invocation. Under pause or unit hold, each produces zero runtime admissions and zero provider requests.

2. **Direct bypass attempts:** under every pipeline service identity, attempt direct unit creation, old launch scripts, raw agent CLI execution, and direct provider access. Permissions or missing credentials must prevent execution.

3. **Pause races:** pause before reservation, after reservation, during outbox delivery, during process startup, and before first provider access. No unadmitted work starts after acknowledgment; already admitted work is reported accurately.

4. **Allowance races:** two simultaneous requests for one look yield at most one reservation. Infrastructure failure, duplicate callbacks, void-before-result, void-after-settlement, and late success after void never consume that look.

5. **Exception idempotency:** retry the same command across a simulated lost response. Exactly one grant exists, with one attributable command and reason.

6. **Crash recovery:** crash after every database/outbox/runtime handoff. Restart produces neither duplicate execution nor leaked reservations. An uncertain execution remains reserved until reconciled.

7. **Forecast equivalence:** for generated states and event streams, simulation and production decision execution produce identical ordered decisions. Replay must also reproduce the audited production log.

8. **State authority:** alter old hold JSON, journals, configuration copies, and another git clone. None can authorize work. Their obsolete control roles must be removed or explicitly rejected.

9. **Ledger reconstruction:** rebuild every balance, hold, queue, and run status from events and compare with live projections, including all corrections.

10. **Architecture enforcement:** CI rejects new direct launch calls outside the launcher package. Production permissions remain the stronger backstop.

The release criterion is concrete: every legacy path has been exercised against the real launch boundary, and no agent identity possesses an alternative route to execution.
