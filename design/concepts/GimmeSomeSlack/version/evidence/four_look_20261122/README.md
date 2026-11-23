# Gimme Some Slack 0.1.1: the staged short look at the four changes (2026-11-22)

Item: `RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS`. Built by
`src/RimMandrake/GimmeSomeSlack/review/four_changes_look.py --stage` on ArchBig, his full list (ModsConfig 315; 314 load:
`koth.isid` is in the list but not installed, so the walk save loaded with the mod check bypassed), GSS build from
09594beb08 (DLL md5 3145565130df, deployed 9:10 PM PST), from his walk save `GSS_011_VISIT2_WALK_20261121`.

Keeper save: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_GSS_011_FOUR_CHANGES_LOOK_20261122.rws`
(11.9 MB, 9:38 PM PST), paused, with its label sidecar.

| station | what it is | capture | what the run saw |
|---|---|---|---|
| A  KINKS ROUNDED | walk station 3 kept as built (the same Modern cords he judged, blue) | `a_kinks_pile_close.jpg` | both power strips and the wall plate: every cord bends in a smooth curve; no hook at a strip, socket or plate |
| B  SWITCH LAMP | three new runs 8 cells apart: closed + powered, open + powered, closed + battery empty | `b_switch_trio.jpg`, `b_lamp_*.jpg` | probe `switchlights`: Green, Red, Dark; by eye the same, the lens small beside the switch body |
| C  RESTYLE... | walk station 10 (Scrapper run) kept, plus a new Industrial run that touches nothing of it (conduit, switch, lamp, mast, lamp mast, wall bracket) | `c_*.jpg`, `menu_1_reach.jpg`, `menu_2_looks.jpg` | 2 runs (cstyles); the real gizmo opens "This item: this power switch only / All connected: 16 pieces, 1 lamps / All on map: 93 pieces, 8 lamps you own"; a real OS click on All connected opens the ten looks; This item > Futuristic by click repainted only the switch, then clicked back to Industrial |
| D  GUST SWAY | walk station 6 (overhead, four looks) kept | `d_overhead_four_looks.jpg` | AerialProbe census `swayLook` = Gust; sway itself shows only unpaused (UNRUN: no agent watched it move) |

Polish (no ticket): "1 lamps" (plural on a count of one); the look menu marks no entry "(current)"; the Scrapper,
Industrial and Futuristic swatches are dark on the dark menu (the icons item
`RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU` already holds the icons).

`stage_reads.json.txt` is the staging run's own read-back line.
