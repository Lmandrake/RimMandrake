## (a) Adversarial review

The core rule is sound: when a live behavioural bug can be reproduced automatically, leave behind a red-then-green regression check. The proposal buries that rule under an unproven framework.

### What will fail in practice

- **It confuses debugging with harness development.** If an existing script misses a bug, rung 3 requires fixing the harness before touching the mod. That is wrong during urgent or poorly understood failures. Sometimes the fastest path to understanding the symptom is an exploratory probe, source instrumentation, or manual reproduction. The regression check should precede the final fix when practical—not necessarily all investigation.

- **Tier B is falsely described as cheap.** A 15-line plan is irrelevant if the site recipe, deterministic setup, cleanup, and observability take hours. The proposal acknowledges a 544-line site and 858-line preflight, then still mandates promotion at the first live debug. Agents will either waste a day or create worthless checks to satisfy the rule.

- **“Two probes” is not a meaningful limit.** One probe can contain hundreds of RPC calls; two can be repeatedly renamed or bundled. The unit is undefined and therefore unenforceable.

- **“Red for the reported reason” lacks an oracle.** A failed assertion may correlate with the symptom without detecting it. Agents under delivery pressure will write convenient proxy checks, then declare faithful reproduction. For visual, timing, save/load, and emergent AI defects, a state predicate may be actively misleading.

- **“One cause per rerun” wastes bridge time.** Isolation matters when changes interact, but making it a default converts a 100-second run into ritual. Independent source fixes can be batched while retaining attribution through targeted checks.

- **Rung 2 mishandles unrelated failures.** “Record it, carry on” conflicts with the standing stop rule if the failure previously passed. The proposal must distinguish a new, previously unmeasured failure from a regression of a previously passing check.

- **Owner-present BENCH is an enormous loophole.** Most valuable debugging may happen there. Exempting it because “interactive is the point” allows the precise knowledge-loss problem the process is intended to prevent.

- **The harness-down exception is circular.** A broken driver can justify raw probing indefinitely while the harness repair expands. It needs an expiry and an authority for renewal.

- **The policy assumes deterministic checks are always possible.** Rare storyteller events, AI scheduling, performance degradation, graphical composition, save corruption, and cross-mod interactions may require statistical, manual, or destructive reproductions. Forcing them into Boolean bars will create false confidence.

- **Full result and response retention will rot quickly.** Live fixtures may contain map IDs, generated pawn IDs, ordering dependencies, and transient game state. Replaying them as truth can freeze accidental implementation details. Full GPT prompts and answers in source history will add speculative noise. Commit the durable check and distilled reasoning; retain bulky evidence outside normal code history with a stable reference.

- **Pyrelands is a bad sole treatment pilot.** It is both biome-scale and harness-immature. Any result will confound process cost with construction of the instrument.

- **The proposal text itself is not approvable as written.** It contains encoding corruption in section references, arrows, temperatures, and thresholds. One kill threshold is unreadable. Policy must not depend on guessing damaged text.

### Over-engineering

Items 2–7 in the harness roadmap are a product backlog, not prerequisites for adopting the process. `@diagnostic`, classifications, historical diffs, fixtures, framing analysis, resume logic, hook warnings, model routing, elaborate briefs, and commit conventions collectively cost more than the behaviour being piloted.

Static schema lint is independently valuable because it already found 22 invalid call sites. Build it as an ordinary reliability improvement, not as evidence that the debugging policy works.

### Missing controls and bad incentives

The process rewards artefacts rather than truth:

- Agents can split or merge “finding kinds” to improve the trend.
- They can label failures HARNESS or SITE to protect a mod score.
- “Promotion rate” can be raised with shallow checks.
- “Script-first rate” measures compliance, not effectiveness.
- “Escapes” cannot be counted unless discovery opportunities and follow-up periods are defined.
- “Time to red” encourages an easy proxy assertion instead of a faithful reproduction.
- “Sessions” and “findings” have no stable boundaries.
- There is no ad-hoc baseline, so “2× baseline” cannot be calculated.
- A 100% promotion target is incompatible with genuinely visual, intermittent, or non-reproducible findings.

Measure time and outcomes, not labels: hands-on minutes, bridge occupancy, cold loads, faithful reproductions, total resolution time, later recurrence, and checks actually reused.

### GPT escalation

The “hypothesis, not verdict” rule is right but too narrowly implemented. GPT suggestions need not become script checks: the correct discriminator may be source inspection, log comparison, mod-set bisection, or a schema query. Require every material GPT claim to be independently tested with the strongest appropriate instrument.

The trigger is gameable. Three trivial hypotheses can be manufactured, while 45 minutes is too late for an inexpensive second opinion. Escalate when either:

- 20 minutes produces no new discriminating evidence;
- two genuinely distinct causal hypotheses are refuted; or
- the evidence contradicts the current model of the system.

The brief should include expected versus actual behaviour, last-known-good state, exact mod/game/companion versions, event timeline, first exception, relevant result rows, state provenance, source excerpts, changes since known-good, and constraints. Ask GPT for ranked hypotheses and the cheapest discriminating test for each.

Do not couple escalation to an image-generation helper’s CLI discovery code. Give it a maintained wrapper. Do not automatically commit the whole exchange. Retain a referenced transcript if required, but commit only conclusions that survived testing. After two GPT cycles without increased information, escalate to the owner.

## (b) Sharper boundaries and exception criteria

The mandatory rule should apply only when all of these are true:

1. The issue requires live evidence after source and static checks.
2. The primary symptom is machine-observable behaviour, not appearance or subjective tuning.
3. A relevant plan and deterministic setup already exist.
4. Running the relevant plan does not require a cold load, mod-list change, unsafe unattended flight, or destruction of valuable owner state.
5. A faithful assertion can reasonably be created in no more than 30 minutes.

When those conditions hold: run the existing relevant check first; if blind, obtain a faithful red reproduction before the final fix; retain the red/green evidence and durable check.

The rule does not lead for:

- load failures: first exception in `Player.log`;
- static def, XML, patch, or API-shape defects;
- visual quality and subjective tuning;
- performance investigations without a stable benchmark;
- intermittent or statistical behaviour until a reproducible seed or sampling method exists;
- cold-load, mod-list, compatibility-matrix, and save-migration work;
- world/map/art authoring;
- unsafe unattended flyer behaviour;
- initial exploration of an unknown symptom;
- mods without an executable setup.

For a mod without a plan, do not mandate construction of a north star. Add the smallest regression test only when the reproduction is stable and the expected future value exceeds the cost. A second incident may prompt that decision, but should not mechanically force a generated-map harness.

Use an exception gate that an autonomous agent cannot renew:

> Raw live exploration is permitted for one 20-minute window only if the agent records one factual code before the first call: `NO_RELEVANT_PLAN`, `NON_MACHINE_ORACLE`, `HARNESS_FAILED` with the failing self-test ID, `OWNER_SUPERVISED_TUNING`, or `EMERGENCY_RECOVERY`. The window ends at 20 minutes or when a stable reproduction is found. FOUNDRY cannot self-renew it; renewal requires BENCH/owner approval.

Count one exploratory window, not “probes.” When it ends, the agent must either promote a reproducible check, return to source/static work, or stop with evidence. Owner-present work should be exempt from automation, but not from capturing a durable lesson afterward.

A prior-pass-now-fail result always stops the run. A newly introduced diagnostic failure stops only if it invalidates the current reproduction, threatens state, or is owner-classified as release-blocking.

## (c) Minimal viable process and pilot

### Adopt on day one

1. Preserve SOURCE as the default and classify only enough to choose the instrument.
2. For an eligible live behavioural defect with an existing relevant plan, run that plan first.
3. If it reproduces the symptom, retain the failing result.
4. If it is blind, allow one recorded 20-minute exploratory window.
5. Before the final fix, create a faithful regression check when feasible within 30 minutes.
6. Retain a red/green pair, check ID, and commit reference.
7. Enforce existing invariants: one bridge driver, first load exception, prior-pass regression stop, and no unattended live flyers.
8. Record exception code and minutes spent. No new framework is needed.

Defer `@diagnostic`, classifications, fixtures, result-history automation, `--only`, resume, framing preflight, hooks, full policy rollout, tier backfill, and GPT-transcript commits. Implement schema lint separately because its value is already demonstrated.

### Pilot

Run for 10 eligible incidents or 14 days, whichever is longer, with a four-week cap.

Scope:

- Graffiti for a mature, fast plan.
- Two explicitly bounded Pyrelands chains only after their setup passes existing self-tests.
- BEHAVIOUR defects requiring live evidence.
- Exclude load, purely static, visual-only, owner tuning, cold-load, and flyer cases from the denominator.
- Record recent comparable incidents as a retrospective baseline; if no credible timestamps exist, state that the pilot measures absolute burden rather than pretending to provide a speed comparison.

For every incident record:

- hands-on minutes to trustworthy reproduction;
- total minutes to resolution;
- bridge occupancy and cold-load count;
- harness-authoring versus mod-fixing minutes;
- whether a faithful red-before-green check was produced;
- exception code and duration;
- regressions or recurrences within 14 days;
- whether the new check is run again and whether it finds anything.

Adopt the process only if at least 70% of eligible incidents obtain a faithful reproduction within 30 minutes, median total resolution time is no worse than 1.5× the credible baseline, and harness work consumes under 40% of pilot effort.

Kill or substantially rework the mandatory version if any two hold:

- fewer than half of eligible incidents obtain a faithful red check;
- median resolution time exceeds 1.5× baseline;
- harness work exceeds 50% of total effort;
- exceptions are required in more than one-third of eligible incidents;
- a promoted check falsely passes its original symptom;
- no added check is reused during the pilot or 14-day follow-up.

Do not require the pilot to discover a new mod defect that source would miss. This process mainly preserves known reproductions; discovery is a separate claim.

## (d) Questions for the owner

1. **What is the binding scope?**

   - A. Existing-plan, machine-observable live behaviour only.
   - B. All live behavioural debugging.
   - C. Every debugging class, including load and visual work.

2. **What should happen when no relevant plan exists?**

   - A. Debug normally; add a small regression check when clearly economical.
   - B. Build a regression script on the second live incident.
   - C. Build a plan before any live debugging.

3. **How much harness work may precede fixing the mod?**

   - A. 30 minutes, then stop or obtain approval.
   - B. 60 minutes.
   - C. No fixed cap.

4. **Who may renew an exploratory exception?**

   - A. Owner only.
   - B. BENCH, with a ledger reason.
   - C. The driving agent.

5. **Does owner-supervised BENCH work owe a durable check afterward?**

   - A. Yes, whenever the lesson is machine-observable.
   - B. Only for release-blocking defects.
   - C. No; notes are sufficient.

6. **What governance applies to regression checks?**

   - A. They remain separate from hash-locked owner bars.
   - B. They automatically become bars.
   - C. The owner approves each promotion.

7. **What should an unrelated script failure do?**

   - A. Stop only if it previously passed or invalidates the reproduction.
   - B. Stop on every failure.
   - C. Record it and always continue.

8. **When should GPT be invoked?**

   - A. After 20 minutes without new discriminating evidence or two refuted hypotheses.
   - B. At the current 45-minute/three-hypothesis threshold.
   - C. Only when BENCH or the owner requests it.

9. **How should GPT evidence be retained?**

   - A. Referenced transcript plus committed tested conclusion.
   - B. Full prompt and answer committed.
   - C. Only the resulting check and a short note.

10. **What pilot failure threshold is acceptable?**

   - A. Use the proposed 30-minute, 1.5× time, and 50% harness-cost limits.
   - B. Choose stricter limits before starting.
   - C. Run a descriptive pilot with no adoption decision.