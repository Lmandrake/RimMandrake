# RIMMANDRAKE_BUILD_TEMPORARY_WORK_BUNDLE_MONITOR_DAILY

## What the card said

<!-- answered 2026-11-25T19:15:39Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** The daily monitor is a program that reads the last day's run records. It reports three things. First: how much work went through Work Bundles (one run that fixes many tickets of one mod or subsystem in one context) against single-ticket runs. Second: how efficient each kind was. Third: how often a run set work down, or a mod moved back a stage, without a sincere attempt to fix in place. (Hard to read? Type STE, Binding or Both for a rewrite.) When the monitor finds a bad pattern, what should the monitor do with it?
**Picked:** Wake the Conductor to decide
**Its description:** Why: keep a judgment between finding and fix. Buys: I can reject a wrong diagnosis before anything changes. Costs: it needs my window each day, and the pipeline is supposed to run without it.
**His words:** (4) is acceptable here. We should call this explicitly the Temporary Work Bundle Monitor, because we're not intending to keep it longer than is necessary to evaluate this change to the pipeline. Its recommendations should go to you, Conductor, because you are Fable and much smarter and with a broader pipeline context. However, the monitor should absolutely have done its homework, provide evidence and measurements, and offer three options for repair with its recommendation made clear. This will hopefully reduce the amount of time you need to spend on it, and it's only one a day. If the Monitor continues to be useful as a more general Pipeline Monitor / Upgrade system, we should fold it instead into Operations in a more formal manner. Agreed?
**Other options:** Start the repair itself (Recommended) · Report only · File one ticket per pattern

**Question:** A set-down is a ticket that a run filed in place of doing the work itself. I measured 25 set-downs in the last 12 hours, and about 16 showed no sincere attempt. A backward move is a mod sent back to an earlier stage. A program can count these, but only a reader can judge whether the attempt before each one was sincere. Who should judge sincerity for the daily monitor?
**Picked:** An LLM reads every one (Recommended)
**Its description:** Why: the volume is small, about 50 a day. A Sonnet judge reads each set-down and backward move with the run's transcript and gives a verdict and the cause (which brief, gate or role allowed it). Buys: a full picture by role. Costs: roughly 50 short judge calls a day. Recommended: a sample would hide which role is the source.
**Other options:** An LLM reads a sample of ten · Reuse the in-run filer's verdicts · Counts only, no judge

**Question:** The monitor compares Work Bundles with single-ticket runs. Every measure below can be shown, but one becomes the headline number that decides whether bundles are working. Spend is in weighted tokens. Which measure should be the headline for efficiency?
**Picked:** Tokens per ticket that stays closed (Recommended)
**Its description:** Why: a closed ticket that reopens was not fixed. Counts a ticket only if it is still closed three days later. Buys: rewards real fixes, not fast closes. Costs: the number arrives three days late for each day's work. Recommended: it cannot be improved by closing tickets carelessly.
**Other options:** Tokens per ticket closed · Tokens spent before the first new act · Stage moves forward per day, per mod

**Question:** The monitor's daily result needs one home that you actually look at. The Maturation Pipeline page is the static status page that already shows each mod's stage and the second pipeline. The daily digest is the file a program builds each day with the calls made for you. Where should the monitor's result appear?
**Picked:** Pipeline page plus a digest line (Recommended)
**Its description:** Why: you already read both. A short section on the Maturation Pipeline page holds the numbers; the digest carries one line with the day's change and what the monitor did about it. Buys: no new page to remember. Costs: the pipeline page grows by one section. Recommended: it adds no new place to look.
**Other options:** Its own page · Digest only · The fleet page

**Owed by this card** (the close names where each was done or filed): needs my window each day
