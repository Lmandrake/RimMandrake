# One place for owed work: the ways forward

For Mandrake. Sunday 2026-11-22, 7:35 PM PST. Nothing here is built. Evidence: `plight.md`, `research.md` and
`gpt_analysis.md` beside this page. Counts are from tonight's census unless marked.

## The answer

**Keep writing debts down. Add a second pair of hands that works them without the Conductor window. Add a count of
what never reached the list. Do not write everything down, and do not build a hard stop.**

Your idea is half right, and the right half is the half we never built.

- **"Write the debt down the moment it is owed" already exists and mostly works. Keep it.** The Conductor filed 190
  owed acts in a week and closed 142, half of them within 2.1 hours `[measured]`.
- **"Nobody lets go of an item until its record is reconciled" exists nowhere.** 25 of the 48 debts open tonight were
  written down and then left for over a day `[measured]`. A week ago the lost debts were mostly unwritten. Now the
  lost debts are mostly written and left.
- **"Everything, in one place" would hurt.** The cause is not a missing record. One window is the only thing that acts
  on a record: the Conductor window receives about 95 finished helper runs a day `[measured]`, talks with you, and
  restarts several times a day. A bigger list would grow faster and drop the same.

**Your idea, judged.** Novelty: low; it is the textbook answer, and we built its first half a week ago. Insight: high
on the point our own designs kept missing: a record with no duty to finish it is a tidier place to lose things.
Complexity: capture is cheap; the hard stop is the risky half. The one measured hard stop on an agent that I found
looped for 50 minutes, and your rule of 2026-11-20 exists because our gates stopped real work over paperwork.

## Five ways

| | what it is, and what you see | the agent: when owed, at pick-up, at stop | gain, cost, how it fails | effort; what it deletes |
|---|---|---|---|---|
| **1. Your idea, literally** | Every owed thing goes in one store at once; a gate refuses to let an agent end until its item is closed or updated. You see one long list. | Files everything; claims; is blocked at stop. | Nothing is unwritten. Every remark becomes an item, on top of 100 to 300 a day now. The agent passes the gate with a cheap note: the record is reconciled and the work is not. | Small. Deletes nothing. |
| **2. A second pair of hands** | A timed program and a narrow fresh helper, not the Conductor window, work the owed list several times a day: close what is done, launch what says "launch", bring back a wait when its date passes, write a ruled answer into the page builders read. It obeys your holds. You see a short "we owe you" list on Fleet Now. | Files as today; the helper claims; ends done, dropped with a reason, or left with its blocker named. | A Conductor restart stops being where debts fall; the culls you order end. Costs tokens for work that today silently does not happen. Fails if the helper grows into a second overloaded Conductor, or closes debts on paper. | 1 to 2 helper runs `[guess ~65%]`; tested with planted debts and a helper killed mid-debt. Deletes the hand sweeps and the queue duty of carry items and handoff pointers. |
| **3. The machinery writes the record** | A program writes the record at each hand-over (run launched or ended, card asked or answered, wait due). A finished run's result stays "returned, not answered" until its asker answers. You see three program-built lists. | Remembers nothing; claims; at stop confirms a note the tool drafted. Nothing blocks. | The run-to-Conductor drops (9) and the silent waits (21) show on the day. It shows drops and does not remove them. | 2 helper runs `[guess ~65%]`. Deletes the log tail as the way results arrive. |
| **4. The mod owns its work** | As a studio tracks the shot: each mod and each pipeline part carries its own open work, with one holder across sessions. You see one card per mod. | Writes into the mod's list; the holder resumes and updates it. | Fewest hand-overs; matches your rulings of 2026-10-31 and 2026-11-16. Work that crosses mods has no owner; 34 small lists can rot unseen. | Weeks. Deletes the 1,597-item open pool and most "needs" lists. |
| **5. The no-home count** | A program counts needs where they start (ended runs, cards, waits come due, alarms, the words you typed) and checks that each has a home. You see "not filed anywhere: N" on pages you already read. | No change. | Shows what was dropped; prevents nothing. Noisy: of 51 typed messages a program called homeless in 3 days, about 7 were real `[guess ~70%]`. | 1 helper run. Deletes the retired board. |

Way 5 with parts of Way 3 is tonight's second proposal, set out in full in
`design/specs/2026-11-22-one-view-of-open-work/proposal.md`. I would build its check as it stands.

## Your seven questions

- **Everything, or a threshold?** A threshold, by kind. A debt between actors is recorded. A creative wish goes into
  its mod's direction. An observation not worth a touch gets one polish line or nothing.
- **A hard stop, against "a fault of form never stops the work"?** Both hold in this form: at stop the tool writes the
  record and the agent confirms; a watcher flags a claimed item with no progress and hands it on. Nothing blocks. It
  fails when a note is confirmed without thought, so we measure the act, not the note.
- **Completeness, proven?** In part, and the page says which part. Way 5 proves that each need a program can list has
  a home, not that the home covers the whole need. A source no program reads (words typed on SteveDesktop, a thought
  lost in a killed run) reads "not measured", never zero. Three lists are fine if each states its scope.
- **The 24 stores.** Four stay as stores: the ledger, each mod's folder, your rulings, the machine readings. The five
  pages you read become views with one rule for "needs you". Handoffs, carry items and the Conductor log keep their
  judgement and lose their duty as queues. The retired board and the six dead stores go.
- **The Conductor as bottleneck.** Ways 2 and 3 take delivery and draining off the window. It keeps talking with you.
- **Mods' records, or one record?** Both. Bars and gaps stay with the mod. Promises, launches and questions to you go
  in the ledger.
- **Creative work.** "The swamp should feel more dead" is not a debt. It goes into the mod's direction at once and
  becomes owed work only when the Designer turns it into a bar.

## Recommendation

**This week: Way 2 on the Conductor's owed list only**, with waits that return by themselves, **beside the second
proposal's no-home check.** The second proposal shows drops and repairs four hand-overs, but it leaves the draining
to the Conductor window and puts off its one change that drains ("Dispatch launches the debts that are launches").
I would do that change first and widen it to every debt a helper may pay. No migration of the 1,597 open items.

**The measurement, read again Sunday 2026-11-29 at this hour:** debts ripe for over a day with no act that evidence
shows. At the census **25**, audited against the real files before the comparison. (The second proposal's run has
since closed the 9 debts that were already done or stale and paid one of the 25; the owed list reads 38
`[measured 7:33 PM]`.) Beside it: waits past their date with no event (21 of 37).

**Then:** Way 3; Way 4 for each mod as it next advances; and two of GPT's ideas: give builders the design plus your
current answers so no agent copies a ruling, and test each mechanism by killing a helper or restarting the Conductor
on purpose. Way 1's hard gate: never.

## What I am unsure of, and where I disagree

- **Unsure:** whether the Way 2 helper stays narrow (Cursor reports that one agent with every job stalled and called
  itself done too early `[read]`); whether a fresh helper can act on an old debt without rebuilding days of context
  (GPT's main doubt, and yours on 2026-11-20: "You have that view right now. Will the fixer?"); and how any of this
  holds after three months. I found no report of that.
- **With you:** I reject "everything" and the hard stop. I keep your core: a picked-up item is never let go in silence.
- **With GPT:** asked blind, GPT chose Way 2 alone for week one and called a source count a week spent measuring a
  known failure. I keep the count: Way 2 works only what reached the list, and you asked to see what never did. GPT
  corrected me twice and I accept both: capture of real debts stays mandatory, and no debt is forced to a decision
  at 24 hours.
