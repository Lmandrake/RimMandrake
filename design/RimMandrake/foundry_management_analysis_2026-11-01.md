# How FOUNDRY is being managed, measured against v2

Item FOUNDRY_THROUGHPUT_MEASURE_V2_GAP, 2026-11-01. All days are UTC. Your words: *"We seriously need to analze and
optimize how Foundry's being managed. It is significantly under-performing compared to how v2 used to do things."*

**The answer.** You are right about the output, and the cause is mostly not how FOUNDRY's window is driven. There are
two gaps with two different causes, and my first draft blurred them until the outside read caught it.

- **Game commits fell from 197 a day to 31.** That is allocation. The seats work as many hours as in v2, but the trial
  held FOUNDRY for three days, BENCH spent its hours on tooling, and fresh tokens fell from 51M to 39M a day. This gap is
  already closing: 1 November reads 89 a day.
- **Live proof fell from 30 L2+ passes a day to 7, and today to 2.** That is the bridge lane. Hours holding the bridge
  fell from about 15 a day to 2.5, because BENCH stopped driving at the cutover and nothing took the lane on. This gap is
  not closing. It is what I could fix from here, and I did.

Fresh windows, one ticket per ring, the Sonnet window and the wake cadence directly cost under 2 hours a day together.
That bounds the time they burn. It does not bound what ringing one offline ticket at a time does to FOUNDRY's priorities,
and that is part of the bridge-lane cause below.

## The table

v2 is the best v2 week, 20 to 26 October (7 days). v3 is 29 October to 1 November (3.9 days). Every figure is per day.
Ranks order the fixes by what can move now. By size of the commit gap alone, ranks 2 and 3 are the larger causes.

| Rank | What v2 did | What we do | Measured gap | Cause | Fix | Expected gain |
|---|---|---|---|---|---|---|
| 1 | Someone drove the game nearly all day | The bridge sits free most of the day; 549 owed live checks wait | Bridge held 14.6 h to 2.5 h; game UP events 20.9 to 2.8; L2+ passes 29.7 to 6.9 (MEASURED) | The live lane has no owner that gets rung for it; the rule in FOUNDRY.md is one line nothing checks | DONE here: every ring tells FOUNDRY to keep one live helper running while the bridge is free; a new reading watches bridge hours | If the owed items are ready to run and the budget pays: 8 h a day of bridge gives 18 to 23 L2+ passes a day, about 3 times now (ESTIMATE, from the MEASURED 2.3 to 2.9 passes per bridge hour). This is proof, not new game output |
| 2 | BENCH drove the game too, and held the bridge most of 22 to 28 October | BENCH does tooling; 355 tooling commits and 10 game commits from its clone in 3.9 days | BENCH bridge commands 781 to 108; BENCH hours 38.8 to 34.8 (MEASURED) | Your cutover ruling moved game work to FOUNDRY, but about 35 BENCH hours a day stayed on, on tooling | YOUR CHOICE 1 below | Moving half of those hours to game work: about 60 more game commits a day (ESTIMATE, weak) |
| 3 | No trial | FOUNDRY built the arena | FOUNDRY clone 29 to 31 October: 268 tooling commits, 48 game (MEASURED) | Your trial-prep bar of 30 October, lifted 31 October, trial still has priority | None. It was your order and it is ending. 1 November already reads 19 game, 18 tooling | Already coming back (MEASURED) |
| 4 | Ledger commits 237, verify runs 72 | Ledger commits 454, verify runs 171 | Selftest commands, FOUNDRY plus BENCH, 1467 to 1854 (MEASURED) | The earned-close gates and the seat rules. They are bars, so they stay | None. Not loosened | None claimed |
| 5 | FOUNDRY kept pulling from its queue | One ring, one ticket | About 29 rings a day, about 2 min idle before each: about 1 h a day (ESTIMATE) | Cadence | None now; too small to be worth a change | Under 1 h a day (ESTIMATE) |
| 6 | Long windows | Restart at the 110k backstop | 8 kills in 4 days, about 4 min each: 32 min in all, 6 of the 8 today (MEASURED) | Restart cost | None | Under 0.5 h a day (ESTIMATE) |

## The numbers, on like terms

| Per day | v2 best week | v2 ending 25 Oct | Last 7 days | v3 | Today (0.9 d) |
|---|---|---|---|---|---|
| Items closed, all seats | 130.9 | 71.3 | 170.6 | 147.7 | 163.3 |
| of which game or mod work | 107.6 | 58.6 | 78.8 | 21.3 | 26.7 |
| Game commits | 196.6 | 182.9 | 83.5 | 30.8 | 88.9 |
| Tooling commits | 61.6 | 42.9 | 143.8 | 149.7 | 202.2 |
| Design commits | 49.0 | 51.1 | 20.7 | 20.8 | 38.9 |
| Ledger commits | 236.9 | 182.1 | 421.9 | 454.4 | 631.1 |
| Game share, ledger left out | 64% | 66% | 34% | 15% | 27% |
| Mods touched in the window | 113 | 100 | 92 | 51 | 45 |
| Live runs passed at L2 or higher | 29.7 | 32.7 | 7.1 | 6.9 | 2.2 |
| FOUNDRY hours with any activity | 11.4 | 11.3 | 11.4 | 15.9 | 23.6 |
| FOUNDRY helper hours | 28.5 | 25.9 | 22.9 | 27.9 | 40.8 |
| FOUNDRY fresh tokens, millions | 24.0 | 22.6 | 14.7 | 17.7 | 19.5 |

All MEASURED from git, the ledger and the transcripts. Today's row is divided by 0.9 days, and Relentless made most of
today's game closes (12.2 of 26.7 a day) while FOUNDRY made 10.0.

| Per day, FOUNDRY and BENCH together | v2 best week | v3 |
|---|---|---|
| Hours, window plus helpers (5-minute gap rule) | 65.8 | 67.3 |
| Fresh tokens, millions | 51.1 | 39.4 |
| Fresh tokens per game commit, millions | 0.26 | 1.28 |
| Fresh tokens per closed item, millions | 0.41 | 0.47 |
| Bridge commands | 1226 | 288 |
| Selftest commands | 1467 | 1854 |

Relentless is on top of these from 1 November: 26.0M fresh tokens and 31.8 hours that day.

**How the hours split.** FOUNDRY's window was active 9.2 h a day against 6.7 in v2, and some part of the seat was
active 15.9 h against 11.4. The remainder is dark or waiting. Wait-loop commands (`sleep`) rose from 59 to 97 a day and
lease renewals from 15 to 22, both small. Restarting cost 32 minutes in 4 days. I cannot split waiting from idle more
finely than that: the record has no reading for a window that is thinking versus one that is parked.

## What is not the cause

Each of these was on your list or in the brief, and each was tested.

- **Ring to take.** Median 9 seconds, p90 14, worst 32, over 114 rings in the journal. A separate audit today read 20
  seconds to 2 minutes on 3 rings. Either way it is small.
- **Idle to next ring.** 110 to 123 seconds in today's audit. At 29 rings a day that is about 1 hour.
- **The tick.** Median 123 seconds, p90 373 seconds. The 6-minute ticks are real, and they cost minutes.
- **The Sonnet window.** FOUNDRY's window ran on Sonnet in v2 as well: 1.3M fresh tokens a day then, 1.4M now. The heavy
  work was already in Opus helpers, and still is (16.2M then, 14.4M now). The model is not a change, so it cannot
  explain the gap.
- **Helper capacity.** 27.9 helper hours against 28.5. The peak did fall, from 16 at once to 9, but the hours did not.
  Your override gives FOUNDRY 8 slots until 4 November.
- **Relentless taking the good work.** It leaves 728 proposed offline items for FOUNDRY, and it cannot take live work at
  all. It is not starving FOUNDRY. It is adding output FOUNDRY would not have made.
- **Fresh-window cold start.** One sample: about 72k tokens on the first turn. But "fresh per ticket" is not what runs.
  It is a 110k backstop, with 8 kills in 4 days, so this cost is small today. It would grow if windows really were per
  ticket, so that is worth knowing before anyone tightens the backstop.

## What the live lane explains, and what it does not

Passes at L2 or higher per bridge hour barely moved: about 2.3 in v2 and about 2.9 in v3. So when someone drives, FOUNDRY
tests about as well as it ever did. Inside the hours it drives, it has not got worse. That stable rate does not show
that more bridge hours will give proportionally more passes, because the hours we have now may be the easiest ones.

The live lane does not explain game commits. On 1 November commits came back to 89 a day while L2+ passes fell to 2. So
the two moved apart, and I withdraw the first draft's claim that the live game throttles everything.

| Bridge hours held | 20 | 21 | 22 | 23 | 24 | 25 | 26 Oct | | 29 | 30 | 31 Oct | 1 Nov |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FOUNDRY | 9.0 | 6.9 | 0 | 3.6 | 0 | 0 | 0 | | 3.1 | 0 | 1.2 | 3.1 |
| BENCH | 0 | 4.4 | 22.2 | 15.7 | 14.4 | 10.1 | 16.3 | | 0 | 1.3 | 0.2 | 0.5 |

A hold is capped at 6 hours in this count, so a forgotten lock cannot inflate it. A held lock is not proof of driving:
that is the weak spot in this table, and the bridge command counts (1226 to 288) are there as a cross-check.

BENCH was the main driver of the last v2 week, not FOUNDRY. So part of what reads as FOUNDRY under-performing is that
two seats' game work became one seat's job on paper, and the second seat's hours did not go with it.

The work is waiting: 549 items owe a live check: 175 at L1, 286 at L2, 49 GREEN-MIN, 5 GREEN-FULL, 22 at L3, 12 at L4.
The built-and-waiting items are old, median 21 days. So v2 did not clear this pile either. Some of it may be stale.

FOUNDRY.md already says one helper should work the bridge when it is available. Nothing rings for it, nothing measures
it, and the ring text never mentions it. A ring hands over the top item from `next`, and 68 of 115 rings were offline
items. Of the 46 live tickets, 27 led to a FOUNDRY bridge take within 2 hours.

## How far to trust this

- **The v2 week is the best week, so the gap is a ceiling.** Game commits a day: September 58.5, 1 to 19 October 159.7,
  20 to 26 October 196.6, the whole v2 run from 20 August 95.8, v3 30. Against the v2 average the gap is 3 times, not 6.
  October's own pace was real and sustained, though.
- **The v3 window holds your trial bar.** 29 to 31 October is partly your order. 1 November is the first free day: 80
  game commits and rising, but only 3.6 bridge hours and 2 L2+ passes. So output is coming back through Relentless and
  offline work, and the live gap is not.
- **Commits are not value.** A commit counts the same for a one-line fix and a whole mod, and v2 may have been churning.
- **Sound closes are UNMEASURED on like terms.** v2 reads 0.0% reopened and v3 3.1%, today 12.2%. That is not a real
  comparison: a failed run could only reopen a closed item from 17:30Z today, when the earned-close rule began. The v2
  zero is the instrument. A fair test of what survived would need reading closed items against later fixes, and I did
  not do it.
- **Live tests are counted by passes at L2 or higher,** because a failed or partial run is not comparable across the rule
  change.
- **FOUNDRY's own v2 commits cannot be separated.** History was rewritten about 28 October and the old seat clones are
  gone, so v2 commit counts are for the whole repo. FOUNDRY's window commit commands went 277 to 235 a day, about flat.
- **10-26 is a mass-close day** (461 closes), which is why the table also shows the week ending 25 October.
- **Game or mod work in closes** defaults to game when no commit identifies it, which may flatter v2. Commits are the
  firmer measure.
- **The token budget limits fix 1.** The system account reads 16% left with 2.9 days to reset, and the allocator is in
  PAYDOWN. Live helpers spend tokens, so the gain above is what the lane can carry, not what the budget will pay for.

## What changed

All reversible. No bar loosened, no ruling changed, no goodbye changed.

| Change | Before | After |
|---|---|---|
| FOUNDRY ring text, `seats.FOUNDRY.extra` in `dispatcher_schedule.json` | no `extra` key; rings named only the ticket | `extra` present, sending the bridge-lane line in each FOUNDRY ring |
| `infrastructure/agents/FOUNDRY.md`, the Bridge lane | one line, "when available" | names the lane as first to staff, with its reading |
| New reading `process.bridge_h_24h` and `process.bridge_h_7d` in the ops watch process family | no reading existed | 3.63 and 45.94 hours, MEASURED at 13:46 PST |
| Rule `BRIDGE_LANE_LOW`: flags `process.bridge_h_7d` under 56 hours a week. A flag, no alarm | no rule | not firing yet: the 7 days still hold BENCH's long holds of 25 and 26 October, so expect it to fire within two days unless the lane is staffed |

The new helper takes one of FOUNDRY's existing slots. It adds no slot, so it can displace offline work. That is the point,
and with the account at 16% it is also the cost.

Owed: `src/RimMandrake/Utils/ops_watch.py` was already DIRTY on the review ledger before this work and stays DIRTY.
Measuring whether this worked is filed as FOUNDRY_LIVE_LANE_MEASURE_ON_OFF.

## Choices for you

**Choice 1: what BENCH's hours are for.** I recommend (b).

- (a) Leave it. BENCH stays on tooling and the system's game output rests on FOUNDRY and Relentless.
- (b) Freeze new tooling on BENCH until the trial verdict, except breakage and work you order. That cuts spend while the
  account is low and leaves FOUNDRY as the live seat, so your cutover ruling stands.
- (c) Let BENCH drive the bridge again when FOUNDRY is not. That changes the cutover ruling, and it is the fastest way
  back to v2's bridge hours.

**Choice 2: the 549 live checks.** I recommend (a): the L1 reads are the cheapest and run in one sitting.

- (a) Work them cheapest first, as FOUNDRY.md says, and let staleness show up as the runs fail.
- (b) Have an agent sort them for staleness first. That costs tokens to save tokens, and the pile might shrink a lot.

## The outside read

GPT read the first draft cold (consult-20261101-134305-1984404). It was told to be skeptical, and it was mostly right.
The draft above is already changed for what follows.

1. **"Activity is not causality: the trial could have caused both drops."** Partly right. The trial and the commit drop
   go together, and I now give the trial that gap. For live proof the trial is not enough: on 1 November, with the bar
   lifted, commits recovered and L2+ passes did not.
2. **"You compared a selected peak with 3.9 trial-heavy days."** Right, and already disclosed: against the whole v2 run the
   commit gap is 3 times, not 6. Today's 89 is close to that average of 96, so on commits alone v3 may already be back to
   v2's ordinary pace, with Relentless doing a good part of it.
3. **"The same hours are not the same capacity."** Right. Fresh tokens fell 23%, peak helpers fell from 16 to 9, and more
   selftests ran. I dropped the claim that the seats work as they did in v2 and kept only that hours match.
4. **"The mechanics may cause the neglect you say they do not."** Right, and this is the best point. 68 of 115 rings were
   offline, and only 27 of 46 live tickets led to a bridge take. Two minutes of idle bounds the direct time only. One
   ticket per ring is part of why the lane went unstaffed, which is why the fix is in the ring text.
5. **"The fix promises an intermediate number."** Right. Passes are not game value, the pile's readiness is unknown, and
   cheapest first starts on 175 L1 reads, which the L2+ measure does not count. I count L1 too from here on. At 16% of
   budget the helper could also displace building. So the gain is marked as conditional, and I claim no game output from it.

GPT's better account is that one combined change of allocation and measurement did this, and it is a fair summary of
the two gaps above. It named the test that would settle it: game items surviving one uniform acceptance gate per million
total tokens, in comparable periods with the live helper on and off. That cannot be done on past data, because the
earned-close rule only began today. Seven days from now the helper's on and off stretches can be compared, and that is
the item filed above.
