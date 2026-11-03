# FRISSIM_BUILD_WAITS_FOR_THAW

Frissim: flightless inclusion insects released by thaw (defs + C#). Filed by `NIGHTSIDE_ICE_NEW_LIFE_1` at ticket-out (delegated: design).

## spec
1. Build `RM_Frissim` in `src/RimMandrake/SleepingIce/` per the roster draft `design/Jawa/worldbuilding/biomes/nightside_ice_roster_draft_2026-10-05.md` §1.3 (In play, Reads in-game, Description, Build cost), as amended below.
2. Judge verdict **KEEP** (`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`, organism `frissim`).
   Judge factual flags that touch it:
   - Frissim refreezing is described inconsistently: §4 makes inclusion insects dormant outside thaw pulses, but the draft kills them when the ice refreezes. Default to renewed dormancy; actual deaths must leave readable remains rather than silently removing pawns.
   - The insect-fall is specifically a deposited, freeze-dried dayside swarm (§4c.2), not automatically a release of native frissim. Keep those populations and their food permissions distinct.
   - The small cost estimates are conditional: frissim needs its thaw/calving infrastructure, wyrmlets need feeding and readable submergence behaviour, and ice-kept-dead theft needs the larder and recovery system. Those dependencies are not already completed merely because shivven movement is built.
3. Backlog place: bedazzle §8 row 2 (thaw/calving); do not jump the ruled order (rows 2 → 3 → 4 → 5 → 6 → 7). Depends on: release rides the thaw-pulse/calving mechanism (bedazzle §8 row 2, not yet an item).
4. A Mod Settings on/off toggle for it (every mod ships superb Mod Settings); default on = shipped behaviour; off degrades gracefully.
5. Art: re-queue through the art-evaluation pipeline from the draft's art brief (or check `artpipe_state.py find` for existing art first); install only judge-KEEP art via `art install`.
6. The mod's functional script gains a row that proves it (debug_process.md).

## criteria
- `RM_Frissim` def(s) load with no error on the minimal list; the SleepingIce selftest covers its C# logic offline.
- Behaviour matches the draft section as written.
- A Mod Settings toggle exists and is honoured.
- One live-proof line proves it appears and behaves on a Sleeping Ice quicktest map.
