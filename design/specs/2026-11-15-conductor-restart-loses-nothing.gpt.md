# GPT adversarial read, verbatim

For `design/specs/2026-11-15-conductor-restart-loses-nothing.md` §4. Asked 2026-11-15 ~6:15 PM PST through `src/RimMandrake/Utils/gpt_consult.py` (Codex, effort high), with the spec draft (`0639e8226d`), the instrument output (`/tmp/crl/owed_out.txt`), `src/RimMandrake/rimflow/roles/conductor_restart.md` and `src/RimMandrake/rimflow/roles/conductor.md`. The question is reproduced first, then the answer unedited.

## Question

You are an adversarial reviewer. Context: a multi-agent system has one "Conductor" Claude Code window that talks to the owner and launches helper agents. The window restarts often (context-limit backstop, a "HANDOFF READY" handoff, account switches). The owner suspects restarts lose work items and wants owed work written down as tickets, at the moment it is owed, in a place that is actually seen.

Attached: (1) my spec with a 7-day measurement of 27 restarts and a 4-element design (E1 owed view, E2 promise check at turn end, E3 results become owed items at their source, E4 handoff pointers filed as owed items); (2) the per-owed-thing first-mention instrument output (owed_out.txt: "first … +Nh" = first later window that names it; it measures SEEN, not DONE); (3) the restart mechanics doc; (4) the Conductor role file.

Please answer, concretely and briefly (numbered, under ~900 words):
A. Attack the MEASUREMENT: where could it be wrong (undercount or overcount of losses)? What is the single cheapest extra check that would most change the conclusion?
B. Attack the DESIGN element by element: for E1-E4, the most likely way it fails in practice (false positives that train the window to rubber-stamp, the owed list itself growing into another unread 23k-line queue, items closed without the act being done, duplicate owed items, races between processes appending to the same ledger shard, the Stop-hook blocking at the wrong moment such as during the owner's goodbye or a context-limit kill). For each, the smallest mitigation.
C. Approaches I missed that are SMALLER or more robust than mine (e.g. structured output from the window instead of regex detection; a different discharge rule; expiry; making the successor prove it read each owed item). Say which of my elements you would cut.
D. Is there any element whose cost exceeds the measured loss (9 of 76 owed things lost or late in 7 days)? Recommend a build order of at most 4 tickets.
Do not restate the spec. Be specific to these files.

## Answer

1. **A — The measurement supports a tracking defect, but leaves the loss rate uncertain.** `owed_out.txt` contains **four `NEVER` rows**, implying **72/76 seen**, versus the spec’s 70/76. Reconcile that first. The role requires successors to reproduce the predecessor’s reply verbatim. Excluding the wake’s reprint alone could still count the successor’s mandatory quotation as recognition. Numerous `first text +0.0h` entries need that distinction.

   Undercounts include promises before the last two replies, omissions among the unverified “carried” items, and results arriving after death. Overcounts include an already-asked question awaiting the owner, conditional launches whose conditions were unchecked, and work subsequently invalidated by retirement. T13 demonstrates that `NEVER` can accompany completed work. T25 is unfinished at cutoff, so its eventual outcome remains censored. Restart-relative “over two hours” also conflates unattended, blocked and actionable time. T19 establishes an in-window failure mechanism. The restart-kind comparison cannot establish causation.

2. **A — The cheapest extra check is a small completion audit.** Randomly select ten “carried” items and require a concrete action artifact and timestamp for each. Explicitly exclude copied predecessor text. This directly tests the largest unsupported claim, that recognition usually became execution. Auditing the already-known failures again would change less.

3. **B — E1 risks creating the next unread queue.** Forty oldest entries can become forty blocked requests, hiding actionable work. Replacing the ordinary queue also hides existing obligations such as the clone-writer item, whose kind is unchanged.

   Smallest mitigation. Initially promote the known outstanding debts, retain ordinary queue coverage at scheduled checks, and render actionable entries alongside a compact waiting count with retrievable details. Waiting entries need a named trigger or next-check time. Do not reset their original age. Resolve `CONDUCTOR`/`BENCH` through the existing alias logic and verify that `kind: owed` cannot enter builder allocation accidentally.

   Visibility needs an action rule. On each wake, select an actionable debt and record its next step or concrete blocker. Another recital of forty titles will reproduce T25.

4. **B — E2 has both trivial bypasses and expensive false positives.** A target item ID does not record the owed launch, as T16 demonstrates. One unrelated `kind owed` event exempts every other promise that turn. Questions, quoted handoffs and “never written” historical descriptions can trigger needless filings. Blocking once prevents loops, but permits rubber-stamping or omission on the second stop.

   The existing `handoff_restart.py` Stop hook creates ordering risk. A promise block can postpone `HANDOFF READY`; a file-mode scan after shard publication can create unpublished debt immediately before the kill.

   Smallest mitigation. Start with advisory detection and explicit structured debt references, matched per act. Bypass blocking during goodbye, handoff and backstop. Capture before the existing publish/recheck path. Measure false positives before introducing any blocking.

5. **B — E3 is strongest where a program knows an explicit decision is required.** Every failed detached run and every `LEFT OPEN:` can generate noise, including failures already recovered or already assigned elsewhere. “Read and decide” supplies weak completion criteria.

   Smallest mitigation. Begin with maturation’s explicit Conductor-call event. Include the requested decision and result location. Use a stable event-and-act key. “Check then append” is insufficient under concurrent writers. Serialize uniqueness checking and append through the existing ledger writer, including shard publication coordination. Reconcile durable result records after crashes so “result written, debt filing failed” remains recoverable.

6. **B — E4 makes a validation command perform repeatable mutations.** Repeated `handoff.py --check` calls can duplicate debts when NEXT wording changes. Deduplicating solely by parent suppresses distinct acts. Closing the parent still must never discharge a relay or decision.

   Smallest mitigation. Handoff pointers explicitly reference existing owed IDs. Keep `--check` a validator. Convert legacy pointers once after review. Give each owed act its own completion condition and evidence. Preserve unresolved relay debt when its build closes.

7. **C — Use an explicit debt protocol and stronger discharge.** A small structured turn record containing act, parent, trigger and completion condition is easier to validate than tense-sensitive regex. It still needs occasional transcript audits because the model can omit commitments.

   Discharge should cite the actual artifact. A launch uses a run ID, a page uses its path or commit, a decision uses its recorded ruling, and a relay uses the outgoing message reference. Reading, acknowledging and closing the parent are insufficient. Asking the owner can complete the asking act; awaiting his answer needs separate waiting state.

   Avoid automatic expiry. The role explicitly preserves genuine old work. Require evidence for cancellation or supersession. Cut E2’s blocking detector and E4’s automatic NEXT inference.

8. **D — Build four tickets, in this order.** Engineering and interruption costs are unmeasured. E2’s kill-time machinery has the weakest cost case. E3 addresses T26, whose missed decision remains unmeasured.

   1. **Reconcile and audit measurement.** Fix counts, quotation exclusion and ten carried outcomes.
   2. **Ship E1 with evidence-backed discharge.** Include initial debt promotion and actionable/waiting rendering.
   3. **Add explicit turn capture and handoff references.** Advisory detection only.
   4. **Add source capture for explicit Conductor decisions.** Include concurrency protection and crash reconciliation.

   These recommendations use the supplied documents. The instrument and ledger implementation were unavailable for verification.