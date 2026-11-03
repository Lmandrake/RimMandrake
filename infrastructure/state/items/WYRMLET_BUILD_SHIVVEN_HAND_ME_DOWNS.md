# WYRMLET_BUILD_SHIVVEN_HAND_ME_DOWNS

Wyrmlet: the apex young, foreshadow rung of the ladder (defs + C#). Filed by `NIGHTSIDE_ICE_NEW_LIFE_1` at ticket-out (delegated: design).

## spec
1. Build `RM_Wyrmlet` in `src/RimMandrake/SleepingIce/` per the roster draft `design/Jawa/worldbuilding/biomes/nightside_ice_roster_draft_2026-10-05.md` §1.4 (In play, Reads in-game, Description, Build cost), as amended below.
2. Judge verdict **KEEP** (`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`, organism `wyrmlet`).
   Judge factual flags that touch it:
   - The small cost estimates are conditional: frissim needs its thaw/calving infrastructure, wyrmlets need feeding and readable submergence behaviour, and ice-kept-dead theft needs the larder and recovery system. Those dependencies are not already completed merely because shivven movement is built.
3. Backlog place: bedazzle §8 row 6 (apex ladder); do not jump the ruled order (rows 2 → 3 → 4 → 5 → 6 → 7). Depends on: reuses RM_Shivven.cs submerged movement; surfaces on frissim release.
4. A Mod Settings on/off toggle for it (every mod ships superb Mod Settings); default on = shipped behaviour; off degrades gracefully.
5. Art: re-queue through the art-evaluation pipeline from the draft's art brief (or check `artpipe_state.py find` for existing art first); install only judge-KEEP art via `art install`.
6. The mod's functional script gains a row that proves it (debug_process.md).

## criteria
- `RM_Wyrmlet` def(s) load with no error on the minimal list; the SleepingIce selftest covers its C# logic offline.
- Behaviour matches the draft section as written.
- A Mod Settings toggle exists and is honoured.
- One live-proof line proves it appears and behaves on a Sleeping Ice quicktest map.
