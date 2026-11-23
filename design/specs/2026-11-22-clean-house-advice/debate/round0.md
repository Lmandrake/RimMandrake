# Round 0: GPT's skeptical re-examination of the clean-house advice

One call, `gpt-6.1-sol` at high effort, 2026-11-22 about 4:20 PM PST, through `src/RimMandrake/Utils/gpt_consult.py`.
It saw `context_pack.md` and the eight files that it lists, whole (208,832 characters). The prompt asked it to attack
the diagnosis and the recommendation, and to name four to six distinct viewpoints of its own choosing. It was not
given a list of viewpoints.

## What was added after Round 0, and why

GPT named six viewpoints. The brief named examples that GPT did not cover as their own programme; two of them are
strong enough to argue, so they were added as advocates in Round 1:

| slug | thesis | why added |
|---|---|---|
| `rebuild-small-core` | Write a new, small factory core from zero (a few thousand lines) behind the existing mods, game driver and ledger history, and prove it with the old system as the oracle. | GPT's first review (`../gpt_review.md` §3 and §4) argued that the study priced a bounded rebuild unfairly; no Round 0 viewpoint makes the whole-core case |
| `shrink-the-fleet` | The volume comes from too many agents, seats, concurrent runs and requests; cut the process (fewer helpers, one lane, slower pace) and let the code shrink because less is asked of it. | The brief's example "shrink the agent count and process instead of the code"; the owner's act of 2026-11-18 4:25 PM ("asked to slow the work", still in force in the pipe status) points this way; no Round 0 viewpoint argues it |

`supervised-mod-sprint` covers the brief's example "stop machinery work entirely and only ship mods", and
`replace-durable-slice` covers "adopt an outside workflow engine now" in a bounded form, so neither was added again.

## One renamed slug

GPT named one viewpoint `artisan-mod-sprint`. In this project "Artisan" is the name of a retired pipeline era, so
the slug is renamed `supervised-mod-sprint` in every file of this debate, GPT's text included. Nothing else in GPT's
text is changed. The viewpoint is GPT's: supervised routing by the Conductor, not the retired Artisan loops.

## A correction to the pack that Round 0 saw

The pack said that the "asked to slow the work" act was from the same minute as the debate request. It is control act
`ct_000026` of 2026-11-18 (`./pipe why ExplosiveKnockback`). GPT's Part B point 9 ("a request to slow work whose full
text was not read") rests on the wrong date; its substance (holds and pauses must be separated from execution time)
stands. The pack is corrected; Round 2 was told.

## GPT's answer, verbatim

**PART A — Attack the diagnosis**

The pack establishes real contradictions in operational state. It does not establish one cause for all the redundancy, missing studies and machinery work.

**1. Why studies did not return**

**Supported:** delivery and closure were unreliable. The door study explicitly awaited relay, then another run closed its owed item as trash. That is stronger evidence than a missing delivery record: a pending obligation was discarded.

But “the work was done; only the return failed” is contradicted by the study’s own table. The simple-loop comparison still owed its GPT check and never produced a verdict. The spring clean closed with ten promoted skills not exported. Producing a document or build did not necessarily complete the request.

**Alternative reading:** some “missing studies” were unfinished assignments closed as completed; others were implemented without returning the requested explanation. These are completion and request-tracking failures, not merely a busy Conductor forgetting delivery. `[guess ~70%]`

The pack also does not establish that cards caused the owner to miss a diagnosis. It records the cards, not whether their accompanying conversation explained the findings.

**Cheap discriminator:** reconcile the original request against the actual deliverables and return messages for the five already sampled studies. Record separately: requested work completed, findings explained, decisions requested, implementation completed, later superseded. Read the messages themselves. This distinguishes failed delivery from incomplete work and deliberate abandonment.

**2. “The same generic service built again by each run”**

**Supported narrowly:** seven account readers handle the same command output differently; spend readers interpret the same unstamped record differently; bridge readers consult obsolete records. These are concrete cases of competing interpretations of one fact.

The broader claim outruns that evidence. Several status pages can legitimately show different projections. Different judges can legitimately use different evidence. Multiple launch entry points need not contain multiple launch implementations. The sweep also found no existing stale-item policy: that candidate proposes a new capability rather than consolidating a duplicate.

Most importantly, the sweep establishes competing implementations, not their origin. It did not trace whether independent runs invented them or whether callers were left behind during migrations.

**Alternative reading:** incomplete cutovers explain much of the observed duplication. The bridge already had an authoritative lock, but two readers still used its predecessor. `dispatch_overlay` repaired one caller of three. That is migration incompleteness rather than repeated invention. `[guess ~70%]`

**Cheap discriminator:** for the sweep’s candidates, classify each home as an authoritative writer, derived view, adapter, obsolete reader or independent implementation. Trace the introduction of the conflicting readers in git. Separately count new duplicate creation and incomplete cutovers. Those findings call for different remedies.

**3. “The generator is still on: each failure is answered with an addition”**

**Supported:** several studies produced rules, gates and tickets; the root rule file grew after its drain; the next-step repair covered only one caller.

**Contradicted as an absolute:** removal has both rules and implementations. `CLAUDE.md` directs agents to delete false material, remove unsupported limits, drop findings not worth touching, and delete checks no bar needs. The retirement index documents removal of whole runners, hooks, modules and tests. “Nothing has a path to removal” is false.

A corrective rule is also not automatically evidence of useless accumulation. “Only affected checks rerun” limits work imposed by earlier machinery.

**Alternative reading:** the problem is selective removal and incomplete replacement: old eras are removed aggressively, while changes inside the current era accumulate without completing their cutovers. `[guess ~65%]`

**Cheap discriminator:** inspect the repair commits associated with the recorded interventions. For each, record whether it added a capability, replaced one, removed one, or left a migration incomplete—and whether the same failure recurred. Commit ratios cannot answer that question.

**4. “Nobody owns the architecture”**

**Supported:** the supplied documents do not provide a current component map with authoritative homes and interfaces.

**Not established:** absence of ownership. The Conductor is explicitly the steward, reads evidence at stage changes, decides after three cycles, launches helpers and carries the owner’s authority. The project has a designated coordinating authority. What is missing is evidence that this authority performs architecture integration.

The study’s inference that 121 specification folders are “121 patches” is also unsupported by their count.

**Alternative reading:** architecture responsibility exists but is divided poorly between the Conductor, local boundary pages and self-repairing helpers. The failure is integration across components, not an unassigned title. `[guess ~65%]`

**Cheap discriminator:** reconstruct who authorized and integrated the sweep’s conflicting implementations. Ask whether anyone checked all callers before declaring each replacement complete. If ownership was explicit but cutovers remained partial, another architecture seat will not by itself fix the failure.

**5. The rate of owner requests**

**Supported:** thirteen of the twenty-one study requests occurred in four days. That establishes a burst, not overload.

The new causal question is direction. The owner says he keeps asking because studies do not return. Repeated requests may be retries of an unresolved concern rather than independent demand exceeding capacity. `[guess ~65%]` Counting them as separate arrivals could count the consequences of failed follow-through as its cause.

The proposed limit also targets **undelivered** studies. If helpers finish promptly but completed reports await attention, that limit controls the wrong queue.

**Cheap discriminator:** group requests by the concern they repeat, then timestamp request, helper completion, return, reaction and subsequent repeat request. Measure where waiting occurs. Distinguish owner reading time from time spent obtaining an answer that was already requested.

**6. The “laboratory versus factory” tension**

**Supported as an objective conflict:** `PURPOSE.md` explicitly values both good mods and experiments in agent autonomy. The owner’s latest complaint demands greater dependability.

**Not supported as the explanation for the redesigns:** the pack lists retired systems but does not establish which changes were experiments, responses to operational failures, or replacements of ideas that never went live. The retirement index includes all three kinds of material.

There is also a substantive conflict the study understates. The owner asked how to preserve productive joint discovery and authorized the Conductor to intervene after repeated cycles. Treating every hand act as a defect of automation risks classifying intended stewardship as failure.

**Alternative reading:** the project lacks an explicit distinction between experiments that yielded useful knowledge and changes that merely kept operations running. Machinery spend therefore mixes research output with maintenance burden. `[guess ~70%]`

**Cheap discriminator:** classify the recorded hand acts as scheduling work, recovery, authorized policy decisions or creative judgment. For each retired design, identify its stated question and recorded conclusion. If no conclusion exists, calling the churn “research” is insufficient; if valuable conclusions exist, counting all machinery work as diversion is insufficient.

---

**PART B — Attack the recommendation**

**The most likely failure is that cleanup becomes another broad machinery campaign, while its measurements cannot identify what helped.** `[guess ~75%]` The plan simultaneously changes launchers, lists, pages, worker output, leases and decision rules; introduces observation; and runs an engine experiment. The pack supplies no measured capacity or integration budget for doing these together.

The specific weaknesses follow.

1. **Freeze does not resolve conflicting instructions.**

   The proposed publish gate refuses a new file lacking a system designation. Existing rules say faults of form must be repaired without stopping work, and owner or Conductor acts must not be refused for missing provenance. Section 8 likewise proposes refusing reports without a summary.

   These are concrete policy conflicts. `[guess ~75%]` Agents could spend the freeze repairing its enforcement or routing around it. First specify which existing instructions change; attaching another gate does not settle their precedence.

2. **Observe would measure a deliberately restricted and changing workload.**

   Six biome mods and Graffiti are held; several others are off. Meanwhile the plan replaces launchers and other paths during observation. “Unused” would mean unused under that particular selection of enabled mods and evolving machinery.

   There is an additional technical mismatch: recording loaded modules at process exit does not cover a process killed before recording—the very failure mode the plan intends to exercise. `[guess ~85%]` A missing observation could therefore indicate interrupted recording rather than unused code.

   Record coverage by machine, process outcome and revision. Use the census to identify candidates for investigation, not as sufficient grounds for parking them.

3. **Thin line starts too late to test much of the proposed Core.**

   Pyrelands is already in in-game acceptance. Its remaining forward stages are the walk brief, which has no veto, and the owner’s walk. Completing those stages would not exercise Designer admission, offline building or the blind-review loop.

   It could demonstrate useful progress while leaving the launcher and earlier routing largely untested. `[guess ~85%]` Test those paths explicitly rather than making progress through Pyrelands stand for coverage of the whole pipeline.

4. **“Every hand act becomes a core fix” may automate authority the tick does not possess.**

   The recorded categories include coverage releases, ceiling releases and stop clears. Existing rules reserve some discretionary acts to the Conductor window and require its decision after three cycles.

   Before turning these interventions into defects, determine whether each was unnecessary clerical work or an intended policy decision. Otherwise the plan can reduce intervention counts by changing who is permitted to decide, rather than improving execution.

5. **The proposed consolidation order crosses several state boundaries at once.**

   The work record remains three stores. Turning lists into views while replacing launch paths changes both how work starts and how its completion is represented. Today’s account-parser and alias consolidations do not establish the effort or reliability of those migrations.

   A one-hour architecture response target also leaves integration ownership unclear: answering “where does this belong?” is different from proving every caller has moved. `[guess ~70%]`

6. **Typed output lacks an agreed consequence for invalid output.**

   The pilot requires malformed, cut-off and doubled results to become “could not look.” Existing rules say paperwork faults must not make a substantive mod verdict unknown.

   An incomplete result may justify that outcome; a duplicate valid delivery may need deduplication; a repairable formatting error may need repair. Collapsing these cases would create new disagreements about when evidence counts. `[guess ~75%]` Settle that contract before choosing an SDK.

7. **The engine Trial has an arbitrary continuation rule and an unstable comparator.**

   Why must the current tick fail **two** tests? A library could eliminate one consequential failure and still be rejected. Conversely, five passing fake-worker tests do not show that the library handles this project’s account switching, holds, blind boundaries or landing protocol.

   “Under a tenth of the tick’s size” also compares unlike scopes unless both implementations contain the same policy and adapters. The tick is being repaired during the Trial, so its version must be pinned.

   Use the Trial to answer a named recovery defect. Its current thresholds can reject a useful replacement or advance an irrelevant one. `[guess ~80%]`

8. **“No rebuild” does not constrain operational disruption.**

   Replacing the runner, record views, status interface, lease mechanisms and routing rules in place can still produce a broad migration. Conversely, replacing one recovery mechanism behind an unchanged interface need not recreate the factory.

   Bound changes by affected behavior and rollback scope. The label “Strangle” supplies no such bound.

9. **Day 14 has no established comparison.**

   The deciding per-stage measures start as UNMEASURED. The workload includes explicit holds, owner-dependent acceptance and a request to slow work whose full text was not read. The status snapshot also mixes a 4:15 reading with later updates.

   Establish a consistent baseline and separate eligible execution time from intentional pauses. Without that, lower throughput could reflect the owner’s choices, and lower interventions could reflect less eligible work. The bundled changes would still prevent attributing an improvement to Core, consolidation, workload reduction or observation.

---

**PART C — Distinct viewpoints**

These are competing two-week programs. Confidence tags mark judgments, not measured probabilities.

| Slug | One-sentence thesis | What it would do first | Strongest evidence for it | Strongest evidence against it |
|---|---|---|---|---|
| `freeze-strangle-core` | Restrict machinery growth and progressively give the existing tick sole control of routine execution. `[guess ~60%]` | Establish the architecture map and freeze, then instrument and advance Pyrelands while consolidating launchers. | The sweep found conflicting operational answers, including an “automatic” next step that persisted through a six-hour pause. | Most of its deciding baseline is UNMEASURED, and its proposed thin line starts at in-game acceptance. |
| `repair-current-runtime` | Keep the present structure for two weeks and repair only demonstrated failures on advancing mods’ paths. `[guess ~70%]` | Reconstruct current blockers and recent interventions for FlowWorks and Pyrelands; finish incomplete cutovers before starting new abstractions. | Several demonstrated faults are identifiable caller defects: obsolete bridge readers and an overlay applied to only one of three callers. | The overlay itself shows that narrow repairs can leave the same fault elsewhere. |
| `supervised-mod-sprint` | Temporarily accept supervised orchestration so agents and the Conductor can finish mod work without first perfecting automation. `[guess ~60%]` | Choose one advancing mod, retain its bars and independent judges, and have the Conductor explicitly route its next acts; automate nothing new. | The owner explicitly values the productive interaction of spotting and resolving problems together and asked how to preserve it. | Seventy-one of the first ninety-six hand acts were classified as decisions also made by the tick: supervision already carries substantial coordination work. |
| `replace-durable-slice` | Stop extending bespoke recovery and spend the fortnight testing and replacing one bounded orchestration slice with an outside runtime. `[guess ~55%]` | Identify an actual interrupted-run failure, freeze its current behavior, and build a competing implementation using the same adapters and acceptance evidence. | The study names custom machinery for killed runs, abandoned runs, spend-stop continuation and orphan clones. | The pack demonstrates account parsing, model resolution and stale-reader failures that an execution engine would not itself remove; their contribution relative to recovery is UNMEASURED. |
| `consolidate-facts-only` | Consolidate conflicting fact readers while preserving scheduling policy, worker protocols and storage boundaries for two weeks. `[guess ~65%]` | Verify all callers of today’s six consolidations, then address the next observed disagreement; leave semantic workflow changes alone. | Seven readers of account status produce different answers on the same warning-prefixed output. | The sweep explicitly gives only a low-confidence inference that one next-step module would eliminate the recorded hand acts; slow execution may be the cause instead. |
| `controlled-live-research` | Treat the next fortnight as a bounded experiment comparing existing automation with supervised agent work on real mod tasks. `[guess ~60%]` | State one research question, hold acceptance criteria fixed, and compare execution traces, weighted tokens and owner involvement under the two modes. | `PURPOSE.md` explicitly makes machinery experimentation a project output and the game its instrument. | The owner’s current complaint is that fixing is displacing building, and earlier comparisons sometimes ended without a verdict. |

```viewpoints
freeze-strangle-core | Restrict machinery growth and progressively give the existing tick sole control of routine execution.
repair-current-runtime | Keep the present structure for two weeks and repair only demonstrated failures on advancing mods’ paths.
supervised-mod-sprint | Temporarily accept supervised orchestration so agents and the Conductor can finish mod work without first perfecting automation.
replace-durable-slice | Stop extending bespoke recovery and test and replace one bounded orchestration slice with an outside runtime.
consolidate-facts-only | Consolidate conflicting fact readers while preserving scheduling policy, worker protocols and storage boundaries for two weeks.
controlled-live-research | Compare existing automation with supervised agent work through a bounded experiment on real mod tasks.
```

**PART D — Current judgment**

I favor `repair-current-runtime` for the next two weeks. `[guess ~70%]` The strongest evidence concerns specific contradictory readers and incomplete cutovers, while the prevalence of recovery failures, unused machinery and owner-capacity overload remains UNMEASURED. Finish those cutovers, advance eligible mod work, and classify interventions before deciding which authority or mechanism to replace. I would switch toward `replace-durable-slice` if execution traces showed repeated recovery failures dominating eligible blocked time and a competing slice handled those same failures correctly. I would switch toward `supervised-mod-sprint` if most remaining interventions proved to be useful judgment rather than preventable coordination work.