I would give each mod a continuing owner, preserve its working session where useful, and make recovery from session loss routine. The pipeline becomes that owner’s checklist, with independent assessments at explicit gates.

The owner’s diagnosis fits the stale-answer and repeated-investigation failures. It does not establish that context loss caused all the wasted work. Unbounded admission, weak launch rules, and pipeline maintenance generating more pipeline maintenance can continue with perfect memory.

**Both options should use the following ledger contract.**

One versioned mod has one authoritative ledger: a small SQLite database containing append-only events and immutable evidence attachments. Source code remains in Git; events identify exact commits and build hashes.

A minimal event envelope is:

```text
mod_id, version, sequence, event_id, schema_version
event_type, actor_id, run_id, timestamp
caused_by, supersedes
code_commit, spec_hash, payload, evidence_hashes
```

Typed payloads cover:

- Ownership assignment, run start/end, budget and interruption.
- Locked specification and bars, with stable bar IDs.
- Actions, observations, hypotheses, experiments and explicit refutations.
- Findings, fixes, verification and judge verdicts.
- Questions, owner answers, decisions and supersessions.
- Gate satisfaction, invalidation, blocking and completion.

“Monotonic” must mean **history only grows**, not that conclusions remain true or stages only advance. A refuted hypothesis remains recorded as refuted. A code change can invalidate an earlier pass. Current state is calculated from those events. This follows [event sourcing](https://martinfowler.com/eaaDev/EventSourcing.html): retained history supports reconstructed state and disposable projections.

**Single writer:** one recorder process alone writes the database. Everyone else submits typed commands. It validates permissions, expected sequence and idempotency keys. One holder has a renewable execution lease; fencing tokens reject writes from an expired holder even if its process survives. The dispatcher cannot launch another holder while that lease remains valid.

The recorder must accept owner answers and sealed judge reports directly; the holder cannot suppress or rewrite them. Semantic ownership does not confer ownership of the evidence.

`stage.json`, journals, exam results, coverage verdicts, test tables, reboot briefs, ticket notes and status pages become **generated, read-only views**. Each carries its ledger sequence. Global tickets retain identifiers and links, not competing mod state. A startup packet contains current decisions, open findings, refuted causes, pending questions, next action and evidence references. It is bounded and regenerable; nobody rereads the entire history.

**Blindness is enforced by access.** A fresh judge receives an immutable candidate, locked bars, required environment and a neutral test entry point. It cannot access the builder’s narrative, hypotheses or previous verdicts. It submits a sealed report containing bar IDs, reproduction steps, evidence and candidate hash. Only then does the holder receive it.

Judges assess; the holder repairs. Optional judge patches are proposals made after sealing the verdict. A repaired candidate goes to another fresh judge. Count every assessment cycle, and require two consecutive independent passes on the same final candidate. Independence reduces shared narrative bias; it cannot eliminate shared model weaknesses.

**Questions are ledger objects**, with a stable ID, exact question, scope, blocking status and any permitted default. Record the owner’s answer verbatim with provenance. Deduplicate against answered questions before asking; reopening requires a stated new fact. Superseding an answer is explicit. The steward surfaces blocking questions and meaningful exceptions, rather than relaying every run report.

**Option 1: a resident builder for each admitted mod.**

The long-term holder is a named builder identity with a preferred continuing Claude Code session, working directory and branch. Stage changes resume that session. Detached, capped execution remains possible, but the timer resumes the holder rather than appointing a new stage worker.

Before context exhaustion—initially around 140k tokens, adjusted from measurements—the builder stops at a safe checkpoint, records unfinished work and commits code. A replacement session assumes the same identity and lease from the generated packet. Unexpected exhaustion uses the same recovery path; startup reconciles unrecorded working-tree changes before trusting any gate.

Stage allocation:

- **1:** independent Designer establishes and locks spec/bars, taking builder input.
- **2, 3, 6:** holder performs preflight, build and live acceptance.
- **4/5:** fresh blind judges assess; holder fixes.
- **7:** steward independently checks evidence completeness and readiness.
- **8:** owner walks the mod; holder handles resulting rework.

This applies the [DRI ownership principle](https://handbook.gitlab.com/handbook/people-group/directly-responsible-individuals/): one accountable owner drives delivery across specialist contributions. Here that is an operational role; the human retains ultimate authority.

**Trade-off:** strongest continuity for debugging and design judgment, with the smallest change to the owner’s preferred workflow.

**Failure modes:** accumulated anchoring, stale beliefs surviving in warm context, checkpoint omissions and excessive concurrent resident mods. Warm memory must yield to newer ledger decisions.

**Cost:** comparatively little reconstruction, but potentially expensive large-context turns. Retain per-run caps plus a cumulative per-mod spend limit and an escalation point for repeated judge failures. A minimal two-judge round has a $30 ceiling under the existing caps; retries add cost.

**Smallest first step:** pilot one mod. Reconcile its existing files into baseline events, make those legacy files read-only, then run build → blind feedback → repair using the same builder session.

**Option 2: a durable mod actor with replaceable executors.**

The long-term holder is a persistent software actor: identity, ledger, mailbox, execution lease and deterministic transition rules. Every LLM run starts cold. Continuity resides in the actor’s recorded plan and decisions, not conversational memory.

A wakeup processes new events, chooses one bounded action and creates an executor packet. The executor returns observations, code changes and a proposed next action. The recorder validates and commits them. A timer with no new event or eligible action launches nothing.

Stage responsibilities and judge isolation remain as above, but stages 2, 3 and 6 may use different executors. None independently owns the mod; the actor remains accountable for unresolved findings, questions and eventual acceptance.

**Trade-off:** easier recovery, reproducibility and predictable bounded contexts. It scales to many dormant mods without maintaining their sessions.

**Failure modes:** packet generation omits decisive context; meaningful engineering judgment gets squeezed into narrow actions; the actor becomes another elaborate orchestration project. This option solves durable responsibility, but deliberately gives up much of the owner’s desired working-memory continuity.

**Cost:** smaller prompts can help, but repeated reconstruction can erase that saving. Highest initial engineering cost: mailbox processing, replay, crash reconciliation and transition validation all need care.

**Smallest first step:** put one existing cold-run workflow behind a ledger-backed actor. Replace ticket-prose dispatch with one generated packet and suppress duplicate launches. Expand only after proving recovery and progress.

[Anthropic’s published guidance on long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) supports incremental work, durable progress artifacts and deliberate startup recovery across context windows. It does not establish that either indefinitely warm sessions or fresh workers are universally superior.

**I would choose Option 1 and enforce a small WIP limit immediately.**

Start with two admitted mods, one holder each, one shared live-game reservation, and a separately bounded maintenance allowance. Count mods awaiting review or live testing as unfinished work. [Kanban’s WIP guidance](https://kanbanguides.org/open-guide-to-kanban/2025.7/) bears directly here: finishing worker subtasks across many items is weaker evidence of flow than finishing valuable items.

Keep the 60-second timer as a readiness check. Permit launches only for an eligible recorded action. A blocked mod waits; an unchanged failure does not trigger another investigation without new evidence.

The ledger needs enforcement, not merely an instruction to write everything down. Acceptance should be denied when evidence is missing, stale or attached to another candidate.

Measure live-accepted versions, elapsed time, total spend, repeated causes, reopened questions and owner interruptions. “Offline done, live unrun” is an intermediate state. The evening does not prove live access would have prevented the failures, but every mod stopping there is sufficient reason to investigate downstream capacity and scheduling.

Pilot this on one mod before migrating the fleet. Success is that a restarted holder avoids a refuted cause, respects an existing owner answer, incorporates blind feedback and carries the same version into live acceptance.