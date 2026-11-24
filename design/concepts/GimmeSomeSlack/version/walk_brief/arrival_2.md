# Gimme Some Slack 0.2.0: the fast walk (arrival 2, 2026-11-24)
written_by: rm-detached-bench-rimmandrake-close-slack-version-all-real-1795546503

Form repair, 2026-11-24 after the walk, by rm-detached-bench-rimmandrake-record-slack-version-pass-af-1795559048 (the run that
records the pass): the written_by line and the four headings were added. The writer is the close-out run, which wrote this file
in 1e22ca37eb, before his walk. That run made no stage move and no in-game row; it also made the fixes that the table
lists, so this file is not a cold read of those fixes. The text under the headings is from this file as he had it and from that run's last message;
the repair added no judgement. He walked this save at about 12:19 PM PST on 2026-11-24 and passed it (OWNER:1795551645304319538).

## What to open

Game: **ArchBig**, small list (10 mods), paused. Save: `GSS_020_CLOSE_WALK_20261124`
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\GSS_020_CLOSE_WALK_20261124.rws`).
Captures: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_CLOSE_SLACK_VERSION_ALL_REAL_WORK_ONE_RUN_ONE_CONTEXT\`. Station 36's
capture was taken and not opened; stations 12, 32 and 33 have no capture of the final state from that run.

## What changed since his last look

His last look: the walk of 2026-11-24 at about 10:10 AM PST (build ad72a3cec3, not passed). Fixes: 5bfe7b4d0e and 125ecabe86
(stations 33 and 12), 8c13ce0390 and 1e22ca37eb (the rest). Eight stations, each with a label, in the south-west quarter of the map.

| station | where (x, z) | what changed | the fault to look for |
|---|---|---|---|
| 33 wall lamps | 20-52, 74-86 | every wall lamp points out of its wall; a wall plate draws behind a lamp | a lamp head inside its wall |
| 12 wall and rock entries | station 12 | a cord goes into the black of its wall plate or rock hole | a cord that stops short of the hole |
| 32 one line, every piece | 20-52, 60-70 | the far span through the middle pole is gone | a span from the west mast straight to the wall bracket |
| 34 battery, four looks | 16-46, 24-34 | a battery wears its run's look; one lies east-west | a vanilla battery; select a cord, Restyle, All connected: the menu reads "1 lamp, 1 battery" and marks the look that is current |
| 35 three poles, two spans | 50-68, 30 | three poles built together wire as a line | a third span from the first pole through the middle one |
| 36 pole lamp takes the cord end | 72-78, 24-32 | the cord that ends beside a lamp wired to a pole plugs into the lamp | a loose sparking end beside the lamp |
| 37 switch glow out | 84-92, 26-34 | a closed Futuristic switch with no power shows no cyan | cyan on the east switch |
| 38 fallen wire | 96-108, 26-32 | fallen wires drop and lie in curves | a wire that runs straight between two sharp corners |

Not on the map: a wire from a gravship to the ground now snaps at take-off (it coiled before), 8c13ce0390. When he walked, its check was
offline only. After the walk, visit 4 flew it three times: PASS 3 of 3 (`D:\Luke\dev\RimMandrake\design\concepts\GimmeSomeSlack\version\in_game\visit_4\SUMMARY.md`).

## Known, not fixed: you need not report these

- Fallen wires: 13 of 640 measured lays still turn sharply at the foot of the drop (160 before).
- The yellow charge bar covers each battery look's gauge window.
- The other lines are on the Polish list, with no ticket: `D:\Luke\dev\RimMandrake\design\concepts\GimmeSomeSlack\version\polish.md`.
- No raid bar is open and no bar moved to the next version.

## What I noticed first

From the close-out run's last message; it is not a cold read:
- The unlit Futuristic switch pictures were redone after the art judge said REDO, and were not judged a second time.
- The snap checks were written with the fix and were not seen red first. Visit 4 has seen them red since.
- One art option, nothing installed over your pick: the Modern switch with a graphite lever instead of the red one beside the red
  lamp, `option_modern_switch_lever.png` in the captures folder.
