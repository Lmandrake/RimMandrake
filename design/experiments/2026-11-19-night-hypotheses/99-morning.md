# Morning summary, 2026-11-19

For Mandrake. Item `RIMMANDRAKE_TRY_NIGHT_HYPOTHESES_ON_RUNNING_FACTORY_BETTER`. A detached designer (Fable) wrote
this. Nothing live was changed. No run was launched. Each figure is tagged in the files beside this one.

## The one thing to know first

The token figures in the Conductor log are too high. A resumed run reports the spend of its whole session.
So the log counts the earlier runs again. This was true for 26 of 26 resumed runs [measured].
The log showed 374 million weighted tokens since Wednesday midnight. About 81 million of that was counted twice.
Last night's figures of "303.5 million" and "52.8 million on review tickets" have the same fault.
I filed a ticket with a test: `RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED`. I did not fix it.

## Where helper tokens go

I read 106 helper sessions from the last 25 hours. They spent 310 million weighted tokens [measured].

- 42% paid to read old context again.
- 36% paid to bring new text into context. For Fable this share is 49%.
- 22% paid for output.
- 15% paid for the starting rules alone. Each helper starts with 68,000 tokens before it does any work.

New text is the expensive part. For Fable, new text costs 80 times more than old text read again.

## The ten hypotheses, one line each

| hypothesis | this morning |
|---|---|
| Cut a helper when its context gets large. | Refuted. A replay showed cuts cost more. |
| Let helpers share one starting context. | Not tested. It could save about 14 million a day. |
| Give each helper only the rules of its role. | Cost measured at 15% of spend. Value not tested. |
| Do not read large files whole into context. | Fact measured. Large reads are half of all tool text. |
| After a long stop, start fresh. Do not resume. | Cost measured. A cold resume costs 0.5 million. |
| Make a "left open" note name who acts next. | True, but too small to build. It wastes 0.4%. |
| Split the Conductor log into acts and records. | Supported. Half the entries ask for nothing. |
| Act on a card's recommendation, and let you undo. | Refuted. You change the answer 4 times in 10. |
| Give factory work a fixed share of tokens. | Numbers measured. The decision is yours. |
| Check a fix only when it surprises its builder. | Not tested. It is the boldest idea. |

## What the experiments showed

1. **Cutting runs.** I replayed each session with a restart at 100,000 or 150,000 tokens. Five of six settings
   cost more, up to 2.5 times more. One setting saved 4%. Starting a run is expensive. Long runs are not the fault.
2. **Relaunches.** The automatic relaunch works. 11 of 18 relaunched runs finished real work. 4 found nothing to
   do, and those 4 cost little.
3. **Resumes.** 16 runs resumed after the cache went cold. They paid 12.5 million to load their context again.
   Most followed the 8:24 PM stop and the 10:15 PM resume.
4. **The log.** 126 of 354 entries repeat a run that the log already reported. 47 more say the alarm clears alone.
5. **Cards.** You chose the recommended option 57% of the time. In 22% of answers you wrote your own answer.
6. **Tickets.** Runs filed 66% of the week's 1,309 tickets. Tickets grew on six days of seven.
7. **Game or factory.** 58% of helper tokens went to the factory. 42% went to game design. None built mod code.
   This count is for one day. It does not include Maturation Pipeline runs.
8. **A null result.** A 5-minute cache would cost the same as the 1-hour cache. I recommend no change.

## What I would try next

- **Share the starting context.** Launch two one-turn helpers from one fixed path. Read what the second one
  writes. This is the cheapest test with the largest possible gain. It needs your word, because it launches runs.
- **Fresh start against cold resume.** At the next long stop, resume half the lanes and restart the other half.
- **Large reads.** Count how much of each large file a session uses later. This is a replay. It costs little.
- **A filtered log tail.** Hide the repeated lines from the Conductor for ten turns. Check that no answer changes.

## What I would NOT do, and why

- **Do not cut helpers short to save tokens.** The replay shows that it costs more.
- **Do not turn cards into notices.** You overrule the recommendation too often for that to be safe.
- **Do not build a rule for idle relaunches.** The rule would cost more than the 0.4% it saves.
- **Do not trim the rulebook yet.** The rules cost 15%, but I did not measure what they prevent.
- **Do not make second readers read less.** You ordered full reads, and you already caught trimmed ones.
- **Do not trust a token total that includes resumed runs.** Wait for the ticket's fix.
- **Do not set a factory budget from one week of data.** The Wednesday sweep changed the week's result.

## Where to read more

`00-hypotheses.md` gives each hypothesis in full. `01-context-rent.md`, `02-relaunch-and-log.md` and
`03-cards-tickets-and-product-share.md` give the measurements. The scripts are in `tools/`.
Folder: `D:\Luke\dev\RimMandrake\design\experiments\2026-11-19-night-hypotheses\` (after the mirror syncs).
