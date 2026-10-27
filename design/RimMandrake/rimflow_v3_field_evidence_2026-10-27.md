# RimFlow v3 against what others actually ended up using (2026-10-27)

Owner, 2026-10-27: *"Compare our v3 design to what they actually ended up using, not the propaganda of what might
work. Any evidence based out comes to compare to at Anthropic or Reddit or GitHub literature?"*

Desk research by BENCH (web search, one sitting). Evidence grades: **[R]** rigorous (RCT, peer-reviewed, large
survey); **[P]** a practitioner's own report with numbers; **[V]** vendor or commentary, unverified. Rigorous evidence
on multi-agent *coding loops* is thin; most of what exists is [P] and [V]. No Reddit thread surfaced with measured
outcomes; practitioner blogs stand in for it.

## What the field converged on

| pattern | evidence | where v3 stands |
|---|---|---|
| **Generator + clean-context reviewer.** The reviewer reads the diff fresh, with no shared context; the coder filters its findings. Cognition runs this in production (Devin Review: ~2 bugs/PR, ~58% severe). | [P] Cognition, "Multi-Agents: What's Actually Working" (2026-04) | **Matches.** Arbiter/Auditor are non-maker; today's GPT reviews found real bugs in every round. |
| **Deterministic oracles carry the load.** Anthropic's 16-agent C compiler (≈2,000 sessions, ≈$20k) stood on very high-quality tests and CI tuned to how models fail; agents got separate subprojects. MAST: final-stage low-level checks alone are inadequate; verification failures are ~1/4 of multi-agent failures regardless of model. | [P] Carlini/Anthropic (2026-02); [R] MAST, NeurIPS 2025 | **Matches in design, weak in fact:** only 15 of 47 runnable claims have full test coverage, so most claims fall to the AI Arbiter (≈52/day vs capacity 12). |
| **Single writer; extra agents add intelligence, not actions.** Parallel-writer swarms make conflicting implicit decisions and "still don't see meaningful adoption"; Claude Code's own subagents are read-only reporters. | [P] Cognition (2025-06, 2026-04); [V] Claude Code architecture write-ups | **Partly.** Lanes help (FlowWorks → BENCH), but helpers write concurrently in one shared clone; today alone: index.lock collisions, a commit built by commit-tree to avoid sweeping another agent's hunks, a runbook edit shipped inside another agent's commit. |
| **Manager → children (map-reduce-and-manage).** Works, but managers over-prescribe without codebase context and children wrongly assume shared state. | [P] Cognition | **Matches** BENCH-as-orchestrator; the briefs-with-paths habit is the known mitigation. |
| **Durable progress files + git as memory** across fresh sessions (initializer, progress log, JSON task list, clean state per session). | [P] Anthropic, "Effective harnesses for long-running agents" (2025-11) | **Matches:** handoffs, ledger, items. |
| **Simple loops beat elaborate ones surprisingly often.** The "Ralph" loop (one prompt, fresh context, repeat) shipped real work cheaply; it failed without a spec. Anthropic: teams spent months on multi-agent architectures, then found better single-agent prompting did as well. | [P]/[V] Huntley, The Register (2026-01); [V] Anthropic statements | **Warning for v3:** its value over v2 must be measured, not assumed (now built: `v3_vs_v2.py`). |
| **Cost scales with agents.** Multi-agent research ≈15× chat tokens; token use explains ~80% of performance variance. Gas Town (Yegge): several Max accounts, creator warns against serious use. | [P] Anthropic multi-agent research system; [V] Gas Town coverage | v3 adds six AI roles of process on top of a v2 already ~70% process commits. |

## What contradicts or is unproven in v3

1. **Management roles have no evidence base.** Nothing found shows a planning/producing layer (Producer), a
   conductor between owner and workers (Conductor) or an innovation role (Innovator) paying for itself in coding loops.
   The patterns with evidence are reviewer, escalation, map-reduce manager and read-only research. Treat these three
   roles as hypotheses with kill criteria, judged by the v3-vs-v2 rule.
2. **Perceived productivity lies.** METR's RCT: experienced developers were 19% *slower* with AI while believing they
   were ~20% faster [R]. DORA 2025 (~5,000 people): AI raises throughput but instability keeps rising [R]. Agents'
   own reports of improvement are not evidence; the guard measures (rework, owner waits) are the right instinct.
3. **AI judges have a real false-positive rate.** LLM code reviewers: ~14–22% false positives and ~14–17% false
   negatives in one 2025 study; static analysers keep FP under 1–10% [V/R mixed]. An AI Arbiter at 52 claims/day will
   wrongly flag several a day. Advisory-first is right; measure its precision against the Auditor before binding.

## What this suggests (BENCH's reading, not ruled)

- **Spend on oracles, not judges.** The field's winner is test coverage. Raising isolated-evidence coverage (15/47
  today) cuts AI Arbiter load and cost more than any capacity tuning.
- **One writer per area, physically.** The evidence says concurrent writers in one tree is the failure mode. Worktrees
  are OFF by owner card (2026-10-02); a per-helper scratch clone that publishes by rebase is the alternative the house
  rules already allow.
- **Keep the proof.** The v3-vs-v2 check is exactly what the field lacks; it should be allowed to kill roles.

## Sources

- Anthropic, "How we built our multi-agent research system": https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic, "Effective harnesses for long-running agents": https://anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Anthropic / Carlini C compiler coverage: https://www.theregister.com/2026/02/09/claude_opus_46_compiler/ , https://www.infoq.com/news/2026/02/claude-built-c-compiler/
- Cognition, "Don't Build Multi-Agents": https://cognition.com/blog/dont-build-multi-agents
- Cognition, "Multi-Agents: What's Actually Working": https://cognition.com/blog/multi-agents-working
- MAST, "Why Do Multi-Agent LLM Systems Fail?": https://arxiv.org/abs/2503.13657
- METR RCT coverage: https://thezvi.substack.com/p/on-metrs-ai-coding-rct
- DORA 2025: https://dora.dev/insights/dora-2025-year-in-review/ , https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025
- Ralph loop: https://www.theregister.com/2026/01/27/ralph_wiggum_claude_loops/
- Gas Town: https://maggieappleton.com/gastown , https://shipyard.build/blog/claude-code-multi-agent/
- LLM code review accuracy: https://www.augmentcode.com/guides/ai-code-review-accuracy
