# RimPulse — GPT review (2026-10-22)

- **Date:** 2026-10-22, ~22:00 PDT
- **Model:** gpt-6.1-sol, reasoning effort high (`src/RimMandrake/Utils/gpt_consult.py` defaults, via codex.exe)
- **Files sent (inlined):** `design/RimMandrake/rimpulse_intent_2026-10-22.md` (as committed in `2714adbf5`), `src/RimMandrake/Utils/pulse/pulse_core.py`, `src/RimMandrake/Utils/pulse/pulse.py`, `src/RimMandrake/Utils/pulse/widget/index.html`
- **Asked for:** (1) review against the need, (2) skeptical analysis, (3) ranked improvements, (4) alternative concepts.
- GPT's answer follows **verbatim**; FOUNDRY's triage is the last section. Claims GPT made about the code were spot-checked against the source before triage (amber_soft dropped from the strip, `c.agents` never drawn, waiting seats get chip state `run`, 14-day ruling cutoff, digest has no look rows, telemetry reds toasted as "window lost", ack defaults to `actionable`, kernel harness warns not drawn): all confirmed.

---

## 1. Review: does the design meet the stated need?

**Not reliably. RimPulse detects activity better than it explains what the returning owner needs to know.** The two red pills are a symptom of that mismatch.

The build has useful foundations: automatic collection, PID reuse checks, rimflow’s own replay for owner items, explicit seat questions, and kernel OOM attribution. But it does not yet provide a dependable account of what is ready, what requires the owner, and what happened during his absence.

The measurements below are reported by the supplied document. I have reviewed the supplied code, not independently verified runtime state.

**What is waiting for me to LOOK AT? — G1: fails as a dependable answer.**

`classify_looks()` combines two different things:

- Artifacts deliberately handed over through `hand()`.
- Any discovered review-sheet server that responds to a probe.

A live server is not evidence that an artifact is ready for the owner. Neither path checks prereview. A sheet can even be labelled `never reviewed` and still enter the list.

The reported sheet bug follows directly from the code. `read_sheets()` supplies the server log’s mtime. `classify_looks()` treats that as the artifact’s revision time. Pulse’s probes update the log. That makes old material appear new and resets its opened state.

Other gaps matter too:

- The collapsed strip contains no look count or newest artifact.
- `section()` counts a sheet group as one item. Its count mixes groups and individual artifacts.
- Old hand-offs remain eligible indefinitely. `hand()` does not check that their targets still exist.
- `make_digest()` excludes `look` rows entirely. The return digest cannot answer the first question.
- The widget marks an artifact seen after attempting to open it. `openLink()` does not confirm success. In browser fallback mode, a local path may merely be copied to the clipboard.

The owner can find some artifacts here. He cannot trust the list as “reviewed things now waiting for my eyes.”

**What NEEDS RULING? — G2: partly met for live questions; poorly met for the backlog.**

`owner_rulings()` correctly uses rimflow’s replay. That is a good choice. It avoids inventing a second interpretation of item state.

But faithfully displaying `needs == owner` does not establish that an item still requires the owner under the new delegation policy. The reported 59 items need a policy audit.

The presentation also works against G2:

- `section()` sorts rulings newest first. It does not identify the oldest or most blocking decision.
- Older items fold after three days.
- `classify_ledger()` silently excludes owner rulings after 14 days. An unresolved decision can disappear without being settled.
- There is no structured indication of what is blocked, which seat is blocked, or why only the owner can decide.
- `classify_sessions()` turns finished-and-idle into “waiting for you.” That is an inference, not evidence of a reserved decision.
- Acknowledging an explicit question removes it from the active asks list even if the seat remains blocked.

The explicit question path is the strongest part. `session_extras()` extracts question text, and the expanded widget pins explicit asks above ordinary rulings.

The collapsed path weakens it again. `renderStrip()` replaces every explicit amber label with `◐ asks`, losing the seat name. It also filters out `amber_soft`, despite `build_strip()` emitting it and the owner having requested finished-and-idle signalling.

**What ISSUES happened while I was away? — G3: not met.**

The current model is a set of classified rows. It is not an account of an absence.

`classify_kernel_oom()` can explain the immediate mechanism: an OOM kill at a cgroup cap. It cannot say whether the affected work recovered. `classify_sessions()` can detect a vanished process, but “process gone, session file left” is a symptom, not a cause.

There is no incident lifecycle connecting:

> happened → affected work → recovery evidence → current consequence → owner informed.

Consequently:

- Recovered OOMs remain red.
- Expired incidents disappear from the current view.
- Multiple symptoms of one failure can produce separate alarms.
- Events outside the selected time window are lost from the account.
- Failures such as artpipe job failures are reduced to cumulative background counts.

`make_digest()` reconstructs its report from the current snapshot. It does not read incident history. It can miss a problem that occurred and recovered entirely during the absence.

It can also miss a still-active old red because it filters reds using `r["since"] >= since - 3600`.

There is one correction to the document: **acknowledgement does not immediately remove an incident from the supplied implementation.** Acked alarms remain in rows and move into the acknowledged fold. `make_digest()` does not exclude them either. The problem is still real, but more specific: there is no coherent historical view, and acknowledgement changes visibility without describing recovery.

**Are both agents alive and working? — G4: partly met.**

`read_sessions()` checks process start time as well as PID. That protects against PID reuse.

The remaining guarantees are weaker:

- A missing BENCH or FOUNDRY session produces no explicit “expected seat missing” state. Its chip simply disappears.
- A dead session never previously observed alive is not reported as lost.
- `classify_sessions()` assigns explicit waiting seats a chip state of `run`. A blocked agent can therefore look active.
- `build_chips()` supplies subagent counts, but `chipHTML()` never displays `c.agents`.
- Working-row text, including the current item, is not rendered in the widget body.
- Transcript movement is only a proxy for useful progress.
- `current_items()` uses its own recent-event heuristic rather than rimflow’s replay. Its item attribution can diverge from actual item state.

G4 is better served than the three primary questions, but “both alive and working” is still stronger than the evidence.

**Can I trust freshness and coverage? — G5: not met end to end.**

`Collector.gather()` catches exceptions around sources. That is useful fault isolation. However, several readers absorb failures themselves:

- `read_jsonl_tail()` returns an empty list on read failure.
- `read_bridge()` returns `None`.
- `read_telemetry()` treats a missing file as absence.
- `read_artpipe()` returns error counts and `ok=False` without raising.
- `read_sessions()` skips malformed session files.

The wrapper can then report `ok=True`. “The reader returned” is being confused with “the expected source is reporting valid data.”

The widget compounds this:

- `LIGHTS` omits hands, subagents and bridge.
- `srcState()` explicitly treats an absent, never-reported game probe as healthy.
- `classify_game()` does not reject an old probe. An old “running” result can remain a running row.
- A fresh read of an old telemetry payload can produce a green collector light beside a “telemetry blind” warning.
- **Collapsed mode hides the freshness toolbar.** If HTTP keeps serving an old snapshot, polling updates `lastMsg`, `online()` stays true, and there is no stale pill in the strip.

The health timer eventually helps with an old global snapshot. It does not prove source coverage.

**The “must never” criteria**

| Criterion | Assessment |
|---|---|
| **N1 — No deduction** | Violated. `build_strip()` discards cause. Amber pills discard the seat and question. Rows can ellipsize the explanation behind a hover tooltip. |
| **N2 — Explained red, with current state** | Violated. No recovery state exists. An OOM cause is available in expanded text, but its current consequence is unknown. |
| **N3 — No crying wolf** | Violated or unproven. Flapping telemetry, inferred owner waits and long-lived recovered reds all undermine precision. Owner-labelled precision is unmeasured. |
| **N4 — No hidden real problems** | Violated. Decisions expire, warnings can disappear on source failure, and strip overflow silently clips content. `render()` omits kernel harness warnings from the body. |
| **N5 — Never healthy while stale** | Violated. Collapsed freshness, missing-source handling and stale game probes provide concrete counterexamples. |
| **N6 — No upkeep** | Partly met mechanically. The timers run automatically. Semantic freshness still depends on agents remembering `hand()` and maintaining accurate owner assignments. The week-long hand-off gap is evidence of failure. |
| **N7 — No focus stealing** | Unverified. The supplied HTML cannot establish the native window’s focus behaviour. That guarantee belongs to the omitted launcher and toast implementation. |
| **N8 — Nothing reaches him unread** | Violated. Neither `hand()` nor `classify_looks()` enforces prereview. Server discovery bypasses it altogether. |

## 2. Skeptical analysis

**The core abstraction is wrong for an away dashboard.**

The system centres on “what rows classify as red or amber now.” The owner needs “what changed during my absence, and what does that mean for me now?”

More collectors will not fix that mismatch. They will produce more rows.

**Red currently mixes severity, history and unread status.**

An OOM is an event. A stopped daemon is a current condition. “You have not seen this” is an awareness state. They need separate fields.

Keeping an old OOM red until acknowledgement makes recovery look like ongoing failure. Clearing it on recovery without retaining history would hide what happened. Both are bad. The current model makes choosing between them unnecessarily hard.

**Crying wolf will make genuine incidents invisible in practice.**

The reported telemetry churn and 577 toasts are warning signs. So are the noise-labelled lost-window alarms, even though those labels came from an agent.

The widget continuously animates every red pill. It gives yesterday’s understood failure much the same visual urgency as a new failure. Warn pills also use red styling.

Once the owner learns that red often means “old event” or “something agents already handled,” a real blocked agent must compete with trained dismissal.

There is another weak assumption: `classify_kernel_oom()` unconditionally marks seat kills `toasted_elsewhere=True`. Pulse suppresses its own notification because memwatch is expected to notify. It has no evidence that delivery happened.

**Silence is too easily interpreted as health.**

A missing telemetry file becomes no telemetry rows. A missing session directory can become no sessions. An old game probe can remain positive. A ledger read problem can turn pending decisions into an empty list.

The distinction must be:

> No problems reported by a healthy source.

versus:

> This source cannot currently tell us.

Small green lights do not rescue a feed that silently deletes its evidence.

**The system monitors its own bookkeeping more successfully than the owner’s work.**

It counts implemented events, closures, acknowledgements, prompt timing and live servers. These are convenient signals. They are not necessarily useful outcomes.

Examples:

- `✓ 43` is a tally of deduplicated ledger rows, not 43 owner-ready results.
- `1018 failed` is a lifetime-looking artpipe stock, not failures during this absence.
- A responding sheet server says nothing about whether its contents deserve attention.
- “First prompt after a red” says nothing about whether the owner saw that red.

The monitored quantities are easier to collect than the desired answers.

**Several claims deserve less confidence.**

| Claim | Why I distrust it |
|---|---|
| “Every source is reporting.” | Some readers return empty or invalid results without raising. The wrapper marks those calls successful. |
| “To rule is honest.” | Honest to the ledger, yes. Honest to the current delegation policy, unproven. |
| “Amber worked.” | The reported ages show state transitions. They do not establish useful notification or correct owner involvement. |
| “Question age” measures response time. | `alarm_close` can result from disappearance or classification changes. It does not record that the owner answered. |
| “Red time-to-notice” | `_notice_metrics()` observes another prompt, not noticing. It also reuses grouped incident IDs across occurrences. |
| “Alert precision” | `ack()` defaults acknowledgement to `actionable`. The UI describes ack as “Seen it.” Those are different judgements. Actor identity is absent. |
| “0 failing selftests” | Useful regression evidence, but the tests are not supplied. This does not demonstrate collapsed readability, source-loss behaviour or a useful return experience. |
| “Pure core” | Not fully. Classification reaches filesystem-dependent helpers such as `item_link()` and `win_path()`. |
| Low restart count means reliability | `spine_restart` counts watchdog actions, not all systemd restarts or interrupted monitoring periods. |

The document deserves credit for exposing broken measurements. Those measurements still cannot support a success claim.

**The reliability machinery has avoidable weaknesses.**

`ack()` and `seen()` each start another `tick()` thread. Gathering happens outside `_lock`, so concurrent ticks can mutate caches and publish snapshots out of order.

`make_digest()` writes `state.json` from another process. The lock is process-local. Both processes also use the same temporary filename in `save_json()`. Atomic replacement protects against partial files; it does not prevent lost updates or competing temporary-file operations.

Deploying the monitor from an actively edited BENCH clone adds another ambiguity: committed, deployed and running are three different states.

**The build has accumulated complexity before proving the return experience.**

There are multiple watchdog paths, two delivery surfaces, telemetry sparklines, sheet discovery, transcript heuristics and metrics. Meanwhile, one of the three primary questions is absent from the digest.

The highest-value work is semantic repair and subtraction. It is not another dashboard feature.

## 3. Improvement recommendations, ranked by value/cost

Costs: **S** = localized change; **M** = several components or a bounded workflow change; **L** = substantial new infrastructure.

1. **Make the collapsed view tell the truth immediately.**  
   **Change:** In `build_strip()` and `renderStrip()`, retain subject and cause: `BENCH tool OOM · 6 GB cap`. Until recovery is modelled, say `recovery unknown`. Preserve the seat on asks. Add reviewed-look and owner-decision counts. Show snapshot staleness independently of HTTP connectivity. Replace silent overflow with a visible overflow control.  
   **Value:** Repairs the surface the owner actually uses.  
   **Cost:** M.  
   **Check:** At the real collapsed width, the owner can identify each alarm’s subject and cause within ten seconds. A frozen snapshot served over healthy HTTP always produces a visible stale warning.

2. **Separate incident history, current health and acknowledgement.**  
   **Change:** Add persistent incidents with occurrence IDs, first/last occurrence, impact, recovery evidence and owner acknowledgement. Keep grouping keys separate from occurrence identity. Feed them from `collect_snapshot()` and `Collector.tick()`. Recover only on relevant evidence: a replacement process alone does not prove interrupted work resumed.  
   **Value:** Fixes the central “still broken or happened earlier?” ambiguity.  
   **Cost:** M.  
   **Check:** A kill followed by verified recovery leaves one historical incident marked recovered. A later kill creates a new occurrence. Ack changes neither health nor recovery evidence.

3. **Rebuild `make_digest()` around the three questions.**  
   **Change:** Include reviewed looks, reserved decisions and incidents intersecting the absence window. Include recovered incidents and older failures still active now. Separate new changes from existing backlog. Display the exact reporting interval. Use a persisted return checkpoint; label inferred intervals as inferred.  
   **Value:** Produces a useful return brief from existing delivery machinery.  
   **Cost:** M.  
   **Check:** A fixture containing a new artifact, a blocked decision, an old ongoing fault and a recovered fault reports all four exactly once.

4. **Audit the owner backlog against the delegation policy.**  
   **Change:** Re-triage the 59 reported items. Require a reserved-policy reason, the actual decision, an agent recommendation and any blocked work. Group families only when one ruling genuinely settles them. Remove silent age exclusion from `classify_ledger()`. Rank blocked work first, then oldest unresolved decisions.  
   **Value:** Reduces the owner’s reading and decision burden.  
   **Cost:** M.  
   **Check:** Every remaining owner item maps to a reserved category. No unresolved decision disappears because it turned 14 days old. The top entry names any agent currently blocked on it.

5. **Give artifacts stable revisions and enforce prereview.**  
   **Change:** Replace log mtime in `read_sheets()` with a content revision or manifest. Extend `hand()` with artifact revision, reviewer, prereview result and review time. Validate targets. Admit only reviewed revisions to the owner queue. Support explicit withdrawal or supersession while preserving opened history. Do not silently expire material merely because it was clicked or became old.  
   **Value:** Makes “to look at” mean something dependable.  
   **Cost:** M.  
   **Check:** Probes leave ordering and opened state unchanged. A new revision reopens once. Unreviewed revisions never enter the owner queue. Missing targets show a delivery problem.

6. **Make source coverage explicit.**  
   **Change:** Give each reader distinct results for valid data, valid empty data, unavailable and invalid. Track last successful observation separately from producer freshness. Configure expected sources. Apply probe expiry in `classify_game()`. Keep unavailable-source notices visible when collapsed.  
   **Value:** Prevents false reassurance.  
   **Cost:** M.  
   **Check:** Removing a required session directory, corrupting telemetry or stopping game probes produces visible unknown coverage. None appears as healthy emptiness.

7. **Cut noisy alert types before adding new ones.**  
   **Change:** Add persistence thresholds and recovery hysteresis to flapping telemetry. Group repeated occurrences into an episode while retaining counts. Keep contained selftest kills out of owner alarms unless containment failed or required work was lost. Fix `toastNew()` titles so telemetry reds are not called “window lost.”  
   **Value:** Restores the meaning of interruption.  
   **Cost:** M.  
   **Check:** Replay the reported flapping sequences. Short oscillations produce no notification storm. Sustained faults still alert within a declared detection target. Evaluate precision separately for each alert type.

8. **Represent expected seats and actual blockers directly.**  
   **Change:** Maintain explicit BENCH and FOUNDRY states: working, waiting for owner, idle, missing or unknown. Derive blocking from an actual request, not idle duration. Keep the owner’s soft-idle signal, but label it “finished/idle.” Display subagent counts already supplied by `build_chips()`.  
   **Value:** Makes agent presence useful context.  
   **Cost:** M.  
   **Check:** Missing seats remain visible. Waiting seats never appear simply “working.” An idle parent with live subagents does not signal finished.

9. **Use one state writer and one collection loop.**  
   **Change:** Have ack, seen and digest commands send mutations to the daemon. Remove click-triggered collection threads. Queue mutations and serialize publication. Make snapshot and event ordering explicit.  
   **Value:** Removes state races and unnecessary collection bursts.  
   **Cost:** M.  
   **Check:** Concurrent ack, seen, digest and timer operations preserve every accepted change. Snapshot timestamps never move backwards.

10. **Deploy a known revision and expose it.**  
    **Change:** Run the daemon from a stable deployed location. Include backend revision and start time in `/api/now`. Distinguish code on disk from code loaded by the running process. Keep the existing widget version mechanism.  
    **Value:** Makes fixes and incident evidence attributable.  
    **Cost:** S–M.  
    **Check:** A deployed change reports the expected backend revision after restart. FOUNDRY work does not depend on an unnoticed BENCH pull.

11. **Repair metrics and measure comprehension.**  
    **Change:** Rotate logs. Deduplicate historical records. Report explicit time coverage instead of an arbitrary byte tail. Rename prompt timing to `time_to_next_prompt`. Record acknowledgement actor separately from usefulness judgement. Add a small return exercise: ask the owner the three questions after ten seconds of viewing.  
    **Value:** Prevents false claims of success and tests the actual need.  
    **Cost:** M.  
    **Check:** Historical totals reconcile with distinct incidents. Agent acknowledgements cannot count as owner precision labels. Return-question accuracy improves across representative sessions. Apply the adopted 90% precision and upkeep limits.

12. **Add only failures with an owner-relevant consequence.**  
    **Change:** Emit structured events from build, selftest, artpipe and digest jobs. Include task, cause, recovery attempts and remaining impact. Promote failures when required work remains blocked, output is lost or owner action is reserved. Keep routine recovered attempts in history.  
    **Value:** Expands coverage without turning normal agent iteration into alarms.  
    **Cost:** M.  
    **Check:** A recovered build failure appears in the return history without urgent red. A persistently blocked required build names the affected task and current consequence.

## 4. Alternative concepts worth exploring

**1. An automatic return brief — my first choice**

A short text card:

- **Look:** reviewed artifacts added since the last checkpoint.
- **Rule:** actual owner decisions, with blocked work first.
- **Issues:** what failed, why, and whether it recovered.
- One final line gives seat state and coverage.

Keep collectors, artifact links, incident storage and digest timers. Replace `make_digest()`’s row dump with this format. Remove completion-event detail from the main brief.

The trade-off is less continuous visibility. Urgent failures still need a separate alert path.

**I would try this first because it directly matches the owner’s sentence and can reuse the existing system.** Deliver it automatically through an agreed return signal or existing surface. Requiring him to remember “I’m back” would repeat the adoption problem. The approved widget can remain available during the trial.

**2. A two-seat hand-off inbox written by the agents**

BENCH and FOUNDRY each maintain a small structured hand-off:

> Ready for your eyes. Decisions reserved for you. Problems encountered and current consequences.

Artifacts carry prereview evidence. Decisions carry recommendations. Machine incident collectors supplement the agents’ accounts.

Keep rimflow integration, kernel evidence and freshness monitoring. Replace transcript interpretation and sheet-server discovery with explicit seat output.

This answers the three questions in language close to the work. It also removes much of the guessing.

The weakness is omission. Agents may forget or produce polished but incomplete reports. Publication should therefore attach to task completion and reserved-decision events. Missing seat reports must be visible.

**3. A persistent one-line state of the world**

For example, with illustrative numbers:

> 3 reviewed looks · 1 ruling blocks BENCH · BENCH tool OOM, recovered · both seats active · coverage complete

Each phrase opens the corresponding list.

Keep classification inputs, explicit decisions and incident state. Kill decorative chips, sparklines and the done tally on this surface.

It provides the fastest answer to “where should I start?” Its limitation is depth: the linked brief must still explain decisions and incident causes.

The collapsed widget could evolve into this without changing its approved physical form.

**4. A chronological “while you were away” journal**

A readable timeline might show:

> 19:40 BENCH tool killed at its 6 GB cap.  
> 19:43 BENCH resumed the task. No owner action needed.  
> 20:05 FOUNDRY published a reviewed contact sheet.  
> 20:18 BENCH requested a reserved ruling; task remains blocked.

Pin current looks and unresolved rulings above the timeline.

Keep event capture, links and source health. Replace transient alarm rows with durable events and explicit consequences.

This is strongest for explaining failures and recovery. It also puts artifacts and decisions in context. Its cost is reading volume. Group retries and show short summaries before detail.

**5. Push notifications plus a return bundle**

Use Windows notifications, or explore phone delivery if the owner chooses it.

Push only urgent unresolved incidents and genuine owner blockers. Bundle reviewed artifacts, recovered issues and lower-priority changes into a return brief.

Keep backend collection and incident state. Remove dependence on a permanently visible window.

This answers urgent “needs ruling” and “issues” questions immediately. The bundle answers all three when he returns.

The trade-off is interruption. Phone push remains an exploration here; the supplied document says it has not been approved. Delivery, duplicate suppression and acknowledgement would need explicit behaviour.

**6. A hybrid: quiet beacon, automatic brief, urgent alerts**

Use three small components:

- A quiet beacon showing counts, any current blocker and coverage.
- An automatic return brief answering all three questions.
- Rare alerts for urgent failures and reserved decisions.

Agents supply reviewed hand-offs and decision context. Collectors supply machine evidence and coverage.

Keep the widget as the beacon, plus timers, links and incident collection. Remove detailed backlog, historical failure counters and telemetry charts from the owner’s default view.

This preserves the owner’s chosen floating surface while giving it a narrower job. Its main risk is duplicated information across surfaces. All three must read the same incident, decision and artifact records.
---

## FOUNDRY triage

Sorted by FOUNDRY (helper session, 2026-10-22). "Needs owner" = it touches a ruling of his (the 2026-10-08
floating-widget / concept C cards, the 2026-10-10 Layout D card, phone push still unruled) — `delegation_policy.md`
§2 item 4. Every "file as item" is filed for FOUNDRY, `--why "delegated: ..."` where it is ours to decide.

### Recommendations (section 3)

| # | GPT recommendation | Verdict | Reason / where it went |
|---|---|---|---|
| 1 | Collapsed view tells the truth (cause in pills, seat on asks, stale shown when collapsed, overflow visible) | **file as item** (extends existing) | Widened `RIMPULSE_RED_PILLS_FIX_NAME_THE_CAUSE` by note; same strip, same code (`build_strip`, `renderStrip`). Form stays Layout D. |
| 2 | Incident history separate from current health and ack; "recovered" state | **file as item** | `RIMPULSE_INCIDENTS_BUILD_RECOVERED_NOT_RED`: the central defect behind the two pills. |
| 3 | Rebuild the digest around the three questions | **file as item** | `RIMPULSE_DIGEST_REBUILD_THREE_QUESTIONS`; digest exists and he ruled its timing, the content is ours. |
| 4 | Audit the 59 owner items against delegation §2; no silent 14-day expiry | **file as item** | `OWNER_ASKS_AUDIT_FIFTY_NINE_DEEP` (the audit) — removing the 14-day cutoff rides with it. |
| 5 | Stable sheet revisions; prereview gate on "to look at" | **file as item** ×2 | Bug `RIMPULSE_SHEETS_FIX_OWN_PROBE_REOPENS_THEM` (measured: probe writes the log whose mtime is the sheet time); gate `RIMPULSE_LOOKS_BUILD_UNREAD_NEVER_LISTED` (CLAUDE.md "Nothing reaches the owner unread"). |
| 6 | Explicit source coverage (empty vs unavailable; probe expiry) | **file as item** | `RIMPULSE_SOURCES_FIX_SILENCE_READS_HEALTHY`. |
| 7 | Cut noisy alerts: hysteresis on telemetry, fix toast title | **file as item** | `RIMPULSE_ALERTS_FIX_TELEMETRY_CRIES_WOLF` (measured 475 / 344 re-opens, warn median life 21 s). |
| 8 | Expected seats explicit; waiting never shown as working; show subagent counts | **file as item** | `RIMPULSE_SEATS_FIX_WAITING_LOOKS_BUSY`. Soft-idle amber stays (his 2026-10-08 ruling), relabelled only. |
| 9 | One state writer, one loop | **file as item** | `RIMPULSE_STATE_FIX_TWO_WRITERS_ONE_FILE` (digest process and daemon both write `state.json`; ack/seen spawn extra ticks). |
| 10 | Deploy a known revision; expose it in `/api/now` | **file as item** | `RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE`. |
| 11 | Repair metrics: rotate, dedupe, time coverage, ack actor, a 10-second return test | **file as item** | `RIMPULSE_METRICS_FIX_253MB_OF_ECHOES`. The "ask him the three questions after 10 s" exercise is folded in as an optional joint check, not a gate. |
| 12 | Add only failures with an owner-relevant consequence | **file as item** | `RIMPULSE_FAILURES_BUILD_ONLY_THE_STUCK`, after #2 (needs the incident model). |
| — | Correction: ack does not remove a row; harness warns not drawn | **adopt now** | Fixed in `rimpulse_intent_2026-10-22.md` §(d) item 9 in the same commit as this file. |
| — | "Pure core" is not pure (`item_link`, `win_path` touch disk) | **reject** | True but harmless: selftests drive it with fixtures and pass; not worth a change on its own. |
| — | N7 focus stealing "unverified" | **reject** | `lantern.pyw` (not sent) owns it: `focus=False` + `SWP_NOACTIVATE`; no complaint since 2026-10-08. |

### Alternative concepts (section 4)

| # | Concept | Verdict | Reason |
|---|---|---|---|
| A1 | Automatic return brief (GPT's first choice) | **needs owner** | Changes the primary surface he chose by card 2026-10-08. The digest rebuild (#3) builds its content either way, so the card can be asked with a real brief to look at. |
| A2 | Agents write a two-seat hand-off inbox | **needs owner** | Changes how both seats report to him; the `hand()` verb already exists and went unused for a week, so adoption is the real question. |
| A3 | One-line state of the world | **file as item** (inside #1) | It is the collapsed strip done right — no change of form; noted on `RIMPULSE_RED_PILLS_FIX_NAME_THE_CAUSE`. |
| A4 | Chronological "while you were away" journal | **file as item** (inside #2/#3) | The incident history is its data; the digest can render it. |
| A5 | Push plus return bundle | **needs owner** | Phone push is unruled (`PHONE_PUSH_ENABLED = False`, 2026-10-08). |
| A6 | Hybrid: quiet beacon + automatic brief + rare alerts | **needs owner** | Keeps his widget but narrows its job and removes sparklines/backlog from the default view — a change to the Layout D ruling. Best asked together with A1 as one card. |
