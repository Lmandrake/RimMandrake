# Agentic Workflows for the RimWorld Scenario Project

## Purpose

This project is too large, interconnected, and changeable to be managed effectively through either continuous human hand-holding or unconstrained peer-to-peer agent activity.

The central architectural problem is:

> **AI workers can now generate changes faster than a single human can maintain shared truth across the project.**

The solution should maximize parallel autonomous work while preventing design drift, stale decisions, duplicated effort, backwards progress, and accidental redefinition of the project.

The strongest general principle is:

> **Do not make peer-to-peer agent conversation the backbone of the project. Make shared state the backbone.**

Parallelism is valuable. Distributed authority is much more dangerous.

---

## Three Leading Architectures

### Option 1 — Chief Architect / Lead Orchestrator

A single durable lead agent acts as the primary interface to the human and delegates bounded tasks to specialist workers.

```text
                         HUMAN
                           |
                           v
                    PROJECT STEWARD
              /-----------|-----------\
             v            v            v
         Research       Builder      Designer
             \            |            /
              \-----------+-----------/
                          |
                          v
                       Checker
                          |
                          v
                       Steward
```

The workers normally do not communicate directly with the human or one another. They receive scoped task packets and return structured results.

#### Strengths

- Very coherent.
- Easy for one human to understand.
- High parallel throughput.
- Relatively simple to implement.
- Reduces the need for the human to route every task.
- A single place exists for planning and project interpretation.

#### Weaknesses

- The Steward can become a cognitive bottleneck.
- A misunderstanding by the lead agent may propagate widely.
- A permanently huge conversational context will eventually become unreliable.
- The architecture still depends heavily on one agent maintaining an accurate project model.

#### Key implementation rule

The Steward should **reconstruct its working context from canonical project state**, not depend on conversational memory.

This is a strong option and substantially better than coordinating many independent chat sessions manually.

---

### Option 2 — Governed Blackboard / Autonomous Peer Agents

Multiple specialist agents operate largely independently against a shared structured project state or “blackboard.”

They communicate primarily by reading and writing typed project objects rather than conversational messages.

```text
       WORLD            CONTENT
          \              /
           \            /
        +----------------------+
        |  PROJECT BLACKBOARD  |
        |                      |
        | decisions            |
        | tasks                |
        | claims               |
        | evidence             |
        | dependencies         |
        | tests                |
        | contradictions       |
        +----------------------+
          /        |         \
         v         v          v
       BUILD     CHECK       LORE
```

A proposed design change might be represented as:

```text
ChangeProposal CP-184
subject: Deepwater Compact
current_rule: ...
proposed_rule: ...
cause: implementation limitation
affected:
  - religion definitions
  - faction defs
  - settlement roster
  - equipment normalization
risk: WORLD_CREATION_BLOCKING
evidence: ...
```

Agents can inspect and react to this shared state, but only designated authority can accept changes to canonical project truth.

#### Strengths

- Extremely high autonomous throughput.
- Very little human routing.
- Strong potential for automatic dependency handling.
- Well suited to large amounts of independently parallel work.
- Can react dynamically as tasks become available.

#### Weaknesses

- Considerably harder to engineer correctly.
- Coordination bugs become architectural bugs.
- Local agent decisions can still create globally incoherent results.
- Observability, concurrency, ownership, stale-state detection, and conflict resolution become major engineering problems.
- Less suitable where correctness depends on subjective design judgment.

#### Recommendation

This is probably **too ambitious as the immediate next architecture**.

It may become attractive later, after the project has a robust state model, change protocol, validation system, and dependency graph.

---

### Option 3 — Control Plane + Autonomous Execution

This is the recommended architecture.

It combines the coherence of a central authority with the throughput of many autonomous workers.

The key separation is between:

1. **What the project currently means.**
2. **Work being attempted under that meaning.**

```text
                           HUMAN
                             |
                   consequential decisions
                             |
                             v
                 +----------------------+
                 |     CONTROL PLANE    |
                 |                      |
                 |        DECIDE        |
                 | canonical truth      |
                 | change arbitration   |
                 +----------+-----------+
                            |
                     project state N
                            |
                            v
        +---------------------------------------+
        |            EXECUTION PLANE            |
        |                                       |
        | BUILD-1    BUILD-2    BUILD-3 ...     |
        |     \         |         /             |
        |      \--------+--------/              |
        |               CHECK                   |
        |                 |                     |
        +-----------------+---------------------+
                          |
                 result / discovery
                          |
                          v
                         REP
                  reconciliation and
                     propagation
                          |
                 +--------+--------+
                 |                 |
                 v                 v
              continue       ChangeProposal
                                  |
                                  v
                                DECIDE
```

This preserves the useful existing names **DECIDE / BUILD / CHECK / REP**, but gives them stricter meanings.

---

## Recommended Agent Roles

### DECIDE — Project Control Plane

DECIDE is **not merely a planner**.

It owns canonical project truth.

Responsibilities:

- Maintain accepted design decisions.
- Resolve contradictions.
- Accept, reject, or defer ChangeProposals.
- Version project state.
- Determine whether an implementation discovery requires a design change.
- Identify decisions requiring human judgment.
- Protect irreversible project gates.

Only DECIDE may change authoritative project design.

A BUILD agent may discover that something is difficult or impossible, but it must **not silently rewrite the design to make implementation easier**.

---

### BUILD — Parallel Execution Workforce

BUILD should be plural.

Multiple builders can operate simultaneously wherever dependencies allow.

Each builder receives a bounded task packet containing:

- Objective.
- Governing project-state version.
- Allowed scope.
- Dependencies.
- Acceptance criteria.
- Files or systems it may modify.
- Forbidden changes.
- Validation requirements.
- Risk classification.
- Escalation conditions.

Builders should work in isolated branches/worktrees or equivalent sandboxes where practical.

BUILD returns structured evidence rather than merely saying that a task is complete.

---

### CHECK — Independent Evaluation

CHECK should be institutionally separate from BUILD.

The creator of a change should not be its sole judge.

CHECK responsibilities include:

- Static validation.
- Schema/reference validation.
- Consistency checking.
- Regression checking.
- Automated gameplay or integration testing where possible.
- Visual review against explicit rubrics.
- Detecting silent failures.
- Detecting accidental scope expansion.
- Producing evidence of pass/fail rather than subjective confidence.

The project should use a **validation pyramid** so that cheap tests eliminate most errors before the expensive 25-minute full RimWorld load is used.

A possible hierarchy:

1. Static syntax/schema checks.
2. Reference and inheritance checks.
3. Project consistency and dependency checks.
4. Targeted automated game tests.
5. Full-mod-list RimWorld load.
6. Human visual or creative acceptance where necessary.

The 25-minute load should be treated as a scarce resource and batched accordingly.

---

### REP — Reconciliation and Propagation

REP should not merely produce reports.

Its principal job is to make the repository conform to accepted project truth.

When DECIDE changes a ruling, REP should:

- Find affected artifacts.
- Identify stale tasks.
- Invalidate work built against superseded assumptions.
- Update canonical specifications.
- Locate contradictory statements.
- Update indexes and dependency records.
- Determine what can be transformed automatically.
- Escalate ambiguous consequences.
- Verify that the new decision has propagated.

This directly addresses one of the project's most damaging failure modes:

> A decision changes, but portions of the repository continue operating under the previous decision.

REP is therefore the project's **drift-control mechanism**.

---

## Strongly Type Interfaces, Not Personalities

Agent personas can be useful for specialization, but elaborate personalities are not the primary safety mechanism.

The important things to strongly type are:

- Authority.
- Inputs.
- Outputs.
- Scope.
- State version.
- Evidence.
- Change rights.
- Escalation paths.

For example, a BUILD task should contain explicit fields such as:

```text
task_id
objective
project_state_version
scope
dependencies
acceptance_criteria
allowed_files
forbidden_changes
validation_method
risk_class
escalation_conditions
```

Its result should contain:

```text
changed_artifacts
tests_performed
evidence
assumptions
failures
new_dependencies
change_proposals
```

A design change should be a first-class object:

```text
proposal
    id
    triggering_evidence
    current_rule
    proposed_replacement
    affected_scope
    affected_artifacts
    reversibility
    world_creation_impact
    rationale
    alternatives
    confidence
```

And DECIDE should produce:

```text
decision
    accepted | rejected | deferred
    supersedes
    effective_project_version
```

A persuasive paragraph should never silently redefine the project.

**The accepted state transition changes the project.**

Everything else is commentary or evidence.

---

## Treat the Project as an Evolving State Machine

The project does not follow a simple workflow:

```text
goal -> decomposition -> implementation
```

Instead it behaves more like:

```text
goal N
   |
   v
implementation
   |
   v
discovery
   |
   v
goal N+1
   |
   v
invalidate or revise dependent work
   |
   v
implementation
```

The architecture must therefore make evolutionary design an explicit supported behavior.

Implementation discoveries should flow upward as ChangeProposals.

Accepted decisions should flow downward as new canonical state.

Dependent work must automatically become stale when its assumptions are superseded.

---

## Human Role

The human should **not** be the project router.

The system should not routinely require the human to decide:

- Which agent should handle something.
- Which agent should talk to which other agent.
- Which documents need updates.
- Whether ordinary implementation work is complete.
- What task should happen next.

The human's scarce attention should be reserved for decisions that actually require human judgment.

Examples include:

- Changes to established fiction.
- Changes affecting world creation.
- Changes to power/progression rules.
- Destructive abandonment of significant completed work.
- Multiple equally defensible creative alternatives.
- Visual/aesthetic judgments.
- Decisions that remain unresolved after bounded autonomous investigation.

When escalation is necessary, DECIDE should produce a compact **decision packet** rather than drag the human through a long conversational discovery process.

Example:

```text
Problem:
X cannot be implemented as currently specified.

Evidence:
...

Option A:
Preserve fiction; higher implementation cost.

Option B:
Simplify mechanic; no visible player difference.

Option C:
Change canon in a specific way.

Recommendation:
B

Affected if accepted:
7 artifacts
3 queued tasks

Reply:
A / B / C / modify
```

The human becomes the **creative authority and exception handler**, not the full-time manager of artificial workers.

---

## Special Treatment of Irreversible World Creation

World creation should be treated like a formal release gate.

No world-generation action should occur until a machine-generated readiness dossier shows:

- Required factions complete.
- Required religions complete.
- Critical definitions validated.
- No unresolved world-creation blockers.
- No stale dependencies.
- Relevant integration tests passed.
- Required visual reviews complete.
- Explicit human authorization obtained.

The unresolved blocker count should be **zero** before world creation is offered as an action.

---

## Comparative Summary

| Criterion | Chief Architect | Governed Blackboard | Control Plane |
|---|---:|---:|---:|
| Coherence | Excellent | Moderate–High | **Excellent** |
| Parallel throughput | High | Excellent | **Very High** |
| Human-time efficiency | High | Excellent | **Excellent** |
| Supports evolving design | High | Excellent | **Excellent** |
| Ease of implementation | Excellent | Low | **Moderate–High** |
| Drift resistance | High | Potentially High | **Excellent** |
| Failure containment | High | Moderate | **Excellent** |
| Irreversible-gate safety | High | Moderate | **Excellent** |
| Recommended for this project | Good | Later | **Best** |

Approximate preference:

- **25% — Chief Architect**
- **10% — Governed Blackboard**
- **65% — Control Plane**

---

## Recommended Direction

Adopt the **Control Plane architecture** and stop repeatedly redesigning the organizational topology.

Keep the organizational model deliberately simple:

> **DECIDE = authority**  
> **BUILD = scalable labor**  
> **CHECK = independent evidence**  
> **REP = propagation and drift repair**

Put the sophistication into:

- Canonical project state.
- Typed task contracts.
- Decision and change protocols.
- Dependency tracking.
- State versioning.
- Automatic invalidation.
- Acceptance criteria.
- Validation infrastructure.
- Observability.
- Escalation rules.

The governing principle is:

> **Do not create an organization chart of clever AI personalities. Create a small control system around a canonical evolving project model, then place large amounts of parallel agent labor beneath it.**

This preserves most of the productivity advantage of autonomous agents without forcing the human either to supervise every decision or periodically discover that autonomous workers have pushed the project backward.
