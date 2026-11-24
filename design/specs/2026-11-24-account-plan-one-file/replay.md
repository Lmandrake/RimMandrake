# Replay Tue Nov 10 12:00 AM PST to Tue Nov 24 2:00 PM PST

Made by `account_plan_replay.py` in 18 s. Readings: 9057 lines of the series; old passes: 5673 lines; switches: 22; old plan files: 18.

## Passes

Passes compared: 4095. Same decision: 3182. Different with a named cause: 913. UNEXPLAINED: 0.

- **PLAN_DATA** (397 passes in 3 episodes): the old engine's line at that pass is not the line of its committed plan file of that time (the file in the timer's clone differed)
  - 252 passes to Thu Nov 12 1:50 PM PST: `Wed Nov 11 4:55 PM PST  old normal (100.0% left, line 30) | plan normal: steven live at 100% (line 52%, warning at 52%): it stays, about 48 h to its warning at 1 points an hour. Next: system at about Fri Nov 13 2:25 PM PST. Week ahea`
  - 1 passes to Tue Nov 17 5:50 AM PST: `Tue Nov 17 5:50 AM PST  old stop (56.0% left, line 62) | plan soft: steven at 56.0% must be left: the stop waits while live runs finish (the live runs are UNMEASURED (systemd could not be read), so they count as live); no new st`
  - 144 passes to Wed Nov 18 6:55 PM PST: `Wed Nov 18 7:00 AM PST  old normal (44.0% left, line 0) | plan normal: steven live at 44% (line 25%, warning at 25%): it stays, about 14.6 h to its warning at 1.3 points an hour. Next: none (no account can take over: it waits for a`
- **NO_REFUSAL_ABOVE_THE_WARNING** (312 passes in 7 episodes): the old engine refused new work above the warning line (its soft zone, or a reset that was near); the plan refuses only at the warning line
  - 257 passes to Wed Nov 11 5:10 AM PST: `Tue Nov 10 7:45 AM PST  old soft (4.0% left, line 2) | plan normal: lukas live at 4% (line 2%, warning at 2%): it stays, about 8 h to its warning at 0.3 points an hour. Next: system at about Wed Nov 11 12:15 PM PST. Week ahead: `
  - 10 passes to Sun Nov 15 11:45 AM PST: `Sun Nov 15 11:00 AM PST  old soft (3.0% left, line 1) | plan normal: system live at 3% (line 0%, warning at 2%): it stays, about 0.5 h to its warning at 2 points an hour. Next: lukas at about Sun Nov 15 12:00 PM PST. Week ahead: `
  - 7 passes to Tue Nov 17 3:30 AM PST: `Tue Nov 17 3:00 AM PST  old soft (4.0% left, line 2) | plan normal: lukas live at 4% (line 2%, warning at 2%): it stays, about 0.8 h to its warning at 2.5 points an hour. Next: system at about Wed Nov 18 12:00 PM PST. Week ahead`
- **RESCUE** (146 passes in 1 episodes): the plan leaves an unfinished account to save points from a reset, worth a switch, with no run live
  - 146 passes to Fri Nov 13 8:15 AM PST: `Thu Nov 12 1:55 PM PST  old normal (89.0% left, line 1) | plan switch -> steven: rescue: leaving system for steven now betters the week ahead by 17 points (switch now: 3.4 points erased, 3 switches; stay: 13.4 points erased, 2 switches); the`
- **WARNING_LINE** (42 passes in 8 episodes): the plan ends an account at its warning line; the old engine of that day ended it at its line
  - 1 passes to Sun Nov 15 8:50 AM PST: `Sun Nov 15 8:50 AM PST  old normal (5.0% left, line 1) | plan soft: system at 5% on a 10.1-min-old reading, within 3 points of its 2% warning line: the level cannot be confirmed after a poll, so no new start until it is read`
  - 3 passes to Sun Nov 15 12:00 PM PST: `Sun Nov 15 11:50 AM PST  old soft (2.0% left, line 1) | plan soft -> lukas: system at 2.0% is at or under its 2% warning line: the switch waits while live runs save and end (the live runs are UNMEASURED (systemd could not be read), so t`
  - 1 passes to Tue Nov 17 5:55 AM PST: `Tue Nov 17 5:55 AM PST  old soft (2.0% left, line 0) | plan soft -> system: lukas at 2.0% is at or under its 2% warning line: the switch waits while live runs save and end (the live runs are UNMEASURED (systemd could not be read), so th`
- **UNREADABLE_LEVEL** (8 passes in 2 episodes): the level could not be read at that pass; the two engines treat a blind meter differently
  - 2 passes to Sat Nov 14 1:20 AM PST: `Sat Nov 14 1:15 AM PST  old soft (52.0% left, line 1) | plan normal: system reads ESTIMATE; its last level was 52%, above its 3% warning line: it stays`
  - 6 passes to Sun Nov 22 11:25 AM PST: `Sun Nov 22 11:00 AM PST  old soft (86.0% left, line 2) | plan normal: lukas reads ESTIMATE; its last level was 86%, above its 2% warning line: it stays`
- **STAY** (8 passes in 1 episodes): the old engine left an account that was not finished, for the order or for a reset; the plan stays
  - 8 passes to Tue Nov 24 2:00 PM PST: `Tue Nov 24 1:25 PM PST  old drain -> steven (20.0% left, line 1) | plan normal: lukas live at 20% (line 1%, warning at 2%): it stays, about 4.8 h to its warning at 3.8 points an hour. Next: steven at about Tue Nov 24 6:25 PM PST. Week ahead`

## Measures

| run | points erased at resets | by account | switches | of them off an unfinished account | burn that found no account | refused-start minutes for a switch above the line |
|---|---|---|---|---|---|---|
| actual (measured) | 6.0 | {'lukas': 3.0, 'steven': 0.0, 'system': 3.0} | 11 | not recorded | not recorded | 39 (8 drain passes) |
| old rule (modelled) | 18.0 | {'lukas': 8.0, 'steven': 10.0, 'system': 0.0} | 16 | 8 | 20.0 of 698.0 | not modelled |
| new plan, idle (modelled) | 7.0 | {'lukas': 4.0, 'steven': 0.0, 'system': 3.0} | 13 | 4 | 21.0 of 698.0 | 0 |
| new plan, busy (modelled) | 7.0 | {'lukas': 4.0, 'steven': 0.0, 'system': 3.0} | 11 | 2 | 21.0 of 698.0 | at most 2 x 2 h (one drain for each rescue) |
| new plan, busy, a rescue never refuses a start (rescue.drain_h null) (modelled) | 50.0 | {'lukas': 4.0, 'steven': 43.0, 'system': 3.0} | 8 | 0 | 67.0 of 698.0 | 0 |
