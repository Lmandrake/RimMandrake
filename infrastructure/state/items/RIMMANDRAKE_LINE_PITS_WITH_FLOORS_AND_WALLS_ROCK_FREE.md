# RIMMANDRAKE_LINE_PITS_WITH_FLOORS_AND_WALLS_ROCK_FREE

## spec

Owner, live look 2026-11-14 about 11:30 AM to 12:10 PM PST (finding 12, the next-version half, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`):

> "We definitely want floor types at the bottom of pits (next version), as well as wall types too (next version). In the next version, these will reduce or encourage drainage into the surrounding land and give the pits enhanced hit points against enemies harming/destroying their way in and out of a pit with shovels. Digging into solid rock ground would then be represented by these same types: digging a pit into rock gets you free rock walls/floor, while soil is looser and lossier and easier (all next version)."

The work: pit floor types and pit wall types.
- Each type sets drainage into the surrounding land (less or more seepage) and hit points against enemies digging in or out with shovels.
- A pit dug into rock gets rock walls and a rock floor for free. A soil pit is looser, loses more water, and is easier to dig.

Related work:
- The FIX half of finding 12 goes to `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE`: the floor name on mouse-over, and the floor surviving a fill.
- The existing ground classes in `RM_GroundClassMath` (Rubble, Ice, slumping ground) are the natural place where "rock gives free walls" starts.
- `RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION`.

Design Version class: Divergent (next version), in his own words.

Build effort: large.

Acceptance test: none yet. The design (which types, their numbers, and how enemies dig) is not settled. Once it is, an offline selftest of drainage per type and wall hit points per ground class is a fair first check.
