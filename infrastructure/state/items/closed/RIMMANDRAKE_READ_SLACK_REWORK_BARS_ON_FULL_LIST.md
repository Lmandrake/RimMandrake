# RIMMANDRAKE_READ_SLACK_REWORK_BARS_ON_FULL_LIST

## spec
The Fable rescue's bars were each read live only on tier gimmesomeslack_flowworks (12 mods), through 298de5b1bf,
1d580847bd and 68e558999c:
- every cord end on its stub's line and slope;
- the sparking wall end (owner 2026-11-16);
- cords drawn under items (depth by shader family);
- the off-screen live flip laid again;
- the pipe-pole build menu.

The walk's own recipe (cords, soak, ui, save_reload) reads none of them. The leaf walk_scavenger_base gives as its
tier_reason "breadth failures show only on his full list". So on the full list nothing reads the reworked bars.
Found by the 2026-11-17 walk audit (D:\ClaudeWork\rimmandrake\conductor\gss_full_walk_audit_20261117.md).

Work: in the same full-list sitting as the walk, run the live tests that already exist. Do not build a new walk scene;
these tests are the readers:
- northstar/live_stub_joins.py
- northstar/live_flip_fresh.py
- northstar/live_pipe_pole_menu.py (god mode off)
- the proof_all scene rows end_kind_and_slope (SC_floor_end_*) and cords_under_items / under_verdict

## criteria
- Live (needs the game; the owner's full list, >=300 active mods read from ModsConfig/active_mods evidence): each of
  the four PASS. Each run row records active_mod_count and the mod sha. A FAIL there that does not reproduce on the
  12-mod tier is split MOD vs mod clash before it is closed.
- Offline before the sitting: the run sheet names all four commands with the full-list tier.

## verify
live, full list: python.exe src/RimMandrake/GimmeSomeSlack/northstar/live_stub_joins.py; live_flip_fresh.py; live_pipe_pole_menu.py; proof_all.py --live rows SC_floor_end_* and cords_under_items

## refs
file: src/RimMandrake/GimmeSomeSlack/northstar/live_stub_joins.py
file: src/RimMandrake/GimmeSomeSlack/northstar/live_flip_fresh.py
file: src/RimMandrake/GimmeSomeSlack/northstar/live_pipe_pole_menu.py
tier: full
full-why: interaction: the walk leaf walk_scavenger_base is tier live_full ("breadth failures show only on his full list"); visit 1 met this on the 316-mod list
