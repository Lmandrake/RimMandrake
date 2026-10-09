**Recommend C first, with a smaller spine.** The strongest evidence is the survival of hooks, timers and existing surfaces. Beauty can improve adoption; it cannot compensate for unreliable freshness. The supplied history actually lists **six** retired interfaces. I can assess the proposed visual language, but not the unattached mockups.

**Shared interaction and visual rules**

- Separate **work state**, **attention state** and **data freshness**. A running task can simultaneously need attention; stale telemetry must never appear healthy.
- Red: confirmed OOM kill, unexpected process loss, or unrecovered failure preventing assigned work. Memory pressure is not an OOM kill. Process disappearance establishes “session ended unexpectedly,” not “terminal crashed.” Clean exits are neutral.
- Amber: explicit unanswered request. Ordinary idle is neutral. Suspected stuck work is dim amber, labelled “no observed progress,” with age and evidence.
- Use warm brown surfaces, cream typography, restrained brass accents and aligned timestamps. Pulse only the relevant indicator: slow breathing for activity; brief red blinking on a new incident, then steady red. Provide persistent-flash opt-in, reduced motion and a motion-off control.
- **Ack** means noticed; **resolved** means cleared. Snooze suppresses delivery until a timestamp, not visibility. Deduplicate desktop/phone acknowledgements by incident ID; re-alert only on escalation or a new occurrence.

**Artifact links, shared across concepts**

Represent outputs as typed references: repository, commit SHA, relative path, MIME type, availability and optional authenticated HTTPS URL. Desktop offers **Open locally / Open published / Copy path**; phone offers HTTPS or “desktop only,” with an embedded summary or thumbnail where useful. Pin repository links to commits. Untracked files need explicit upload or remain local; a commit alone does not make an artifact phone-accessible. A browser needs a narrowly scoped local opener, not arbitrary shell commands.

**A · Lantern**

Use stable rows keyed to work attempts, with seat labels as secondary metadata. Show a fixed attention shelf, bounded live roster and collapsible completions; avoid sorting or sliding rows while someone is clicking. Expansion reveals the last meaningful event, request text, evidence and links. Offer keyboard ack/snooze, click-through mode, dock/undock and a conspicuous stale badge.

A done row should retain its position briefly, change icon/text in place, then enter history without animation during interaction. Persist placement and acknowledgements across restarts.

**Biggest risk:** maintaining a Windows–WSL–browser lifecycle becomes another unattended project. Autostart, close-to-tray and push fallback are prerequisites; topmost is only presentation.

**B · Return Ledger**

Define an edition by explicit lower and upper source cursors, generation time and completeness. Include unresolved older incidents even when they precede “since you left.” Separate “seen” from alarm acknowledgement. Generate the factual digest deterministically; an optional lede must link back to supporting events.

Make it beautifully readable: strong typography, generous spacing, compact evidence previews, no ambient motion. New red incidents still require external push. Phone seen/ack writes must reach the same authoritative store used by desktop.

Same-URL updates are documented, but publishing has contextual approval conditions; unattended operation requires a lifecycle proof. Artifact storage also does not establish a working writeback path into WSL. [Claude Code Artifact documentation](https://code.claude.com/docs/en/artifacts)

**Biggest risk:** publishing becomes the same republishing dependency that killed Hub. A prompt gap is also an unreliable presence signal; use explicit “I’m back” initially.

**C · Marquee**

Read a cached projection; never scan transcripts inside the statusline. Reserve width, truncate labels predictably and prioritize **unacknowledged red → explicit waiting → live work → completed count**. Show fleet freshness separately. Use glyphs and restrained color without continuous terminal blinking.

Toasts should say what happened, what needs doing and where to respond. Group related incidents; cancel waiting notifications when answered. Deliver amber only after a short grace period. Keep done events in the digest rather than notifying individually. Provide `since`, `ack`, `snooze` and source-detail commands.

**Biggest risk:** notification fatigue causes the owner to disable the only useful part. Measure actionable precision before adding phone delivery.

**The pulse spine needs redesign**

1. **Schema:** replace `{key,kind,who,text,since,link}` with versioned events containing `event_id`, `source`, source cursor, `occurred_at`, `observed_at`, host/boot identity, session/process identity, work/attempt ID, event type, severity, confidence, structured payload and evidence references. Text and color belong in projections.
2. **Identity:** seat names are labels. Processes need host + boot ID + PID + kernel start time. Sessions and resumed sessions need separate process incarnations. Work needs a ledger item ID; retries need attempt IDs. Never infer ownership from proximity or a display name.
3. **Dedupe/order:** preserve source offsets or IDs across restart. Handle truncated/rotated files and incomplete final lines. Correlate hook, OOM and process-loss observations into one incident while retaining evidence. Do not hash message text alone. Late observations must not regress newer state.
4. **Run → done:** append a completion transition for the same attempt; update its projected row. Preserve history and distinguish implemented, verified, failed and cancelled. A stopped response is not task completion: documented `Stop` means Claude finished responding. [Hooks reference](https://code.claude.com/docs/en/hooks)
5. **Durability:** hooks write to a local spool and return quickly; publishing/network failure must never impede an agent. One reducer owns writes, checkpoints source cursors and atomically replaces snapshots. Keep acknowledgements, snoozes and delivery retries durable.
6. **Freshness:** expose last successful collection, per-source freshness and last meaningful progress separately. `statusUpdatedAt` is not a heartbeat; transcript silence is not proof of a stall.
7. **Watcher:** systemd can restart the collector but cannot detect WSL being unavailable from outside. A Windows scheduled check should verify an advancing generation timestamp and issue one “monitor unavailable” incident, with sleep/resume grace. Never generate a fleet of false crash alerts during telemetry loss.
8. **Compatibility:** isolate internal session-file parsing behind versioned adapters. Validate fixtures after upgrades; preserve unknown fields; quarantine parse failures and show degraded coverage. Documented hooks plus process checks remain the fallback. Validate actual question-card behavior; `idle_prompt` does not prove an unanswered question. [Notification semantics](https://code.claude.com/docs/en/hooks#notification)

**D · Attention Inbox**

A genuinely different option is a persistent queue of **decisions and failures**, surfaced through Windows Notification Center and phone push. Each card has “what needs you,” consequence, target and ack/snooze/open actions. Resolved requests disappear; completions accumulate into one return card.

It has no ambient roster. It is potentially better when unattended blockers dominate the cost: success means clearing the queue. Its risk is building reliable cross-device state synchronization. Prototype desktop-only using existing notifications.

**The strongest case against building**

Remote Control already provides the roster; ledger and memwatch already preserve outcomes. The missing value may be only **harness-kill alerts and a deterministic `since` command**. A comprehensive joined dashboard introduces uncertain classifications, maintenance and another thing requiring trust. Neither more events nor prettier pixels proves saved time. The quoted day estimates omit lifecycle, delivery and compatibility work.

**Measure before building**

Use 7–14 days of existing logs; manually annotate a small sample. Prompt gaps are candidate away periods, not established absence.

| Metric | Cheap baseline |
|---|---|
| Return orientation time | Replay sampled log windows; time the owner finding failures, blockers and outputs. |
| Blocker response delay | Annotate explicit questions/permission requests and subsequent human answers in transcripts; report median/p90. |
| Failure recovery delay | Join memwatch/StopFailure timestamps to restart, reassignment or resumed work. |
| Actionable alert precision | Replay proposed rules against logs; owner labels each candidate actionable/duplicate/irrelevant. |
| Usable output coverage | Audit distinct completed items for valid desktop and phone references. The 49/260 figure counts events, not outcomes. |
| Upkeep burden | Count manual refresh/start/recovery prompts and estimate minutes from transcripts and journals. |

Missing historical signals are **unknown**, not zero.

**Priority order**

1. Baseline the metrics and validate question, clean-exit, kill and PID-reuse detection.
2. Extend existing memwatch coverage; add durable, deduplicated explicit-blocker alerts.
3. Add deterministic `rimflow since`, typed output references and explicit seen cursors.
4. Add C’s cached strip, then phone delivery if alert precision holds.
5. Build D or B only if measured return friction remains. Build A last.

**Kill criterion:** after a two-week pilot, freeze expansion if neither orientation time nor blocker/failure delay improves by 30%, actionable alert precision falls below 90%, or upkeep exceeds 15 minutes/week. Retain only independently useful alerts and `since`.