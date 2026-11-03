# SAALLEN_BUILD_BLISTERS_ON_CUE

Saallen: seam crust that blisters when warmed and marks the breach ring (defs + C#). Filed by `NIGHTSIDE_ICE_NEW_LIFE_1` at ticket-out (delegated: design).

## spec
1. Build `RM_Saallen` in `src/RimMandrake/SleepingIce/` per the roster draft `design/Jawa/worldbuilding/biomes/nightside_ice_roster_draft_2026-10-05.md` §2.1 (In play, Reads in-game, Description, Build cost), as amended below.
2. Judge verdict **CHANGE** (`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`, organism `saallen`).
   Changes the build must carry:
   - Make scraping remove the crust and its additional breach-placement weight only. Warm, unfloored open ice must remain eligible for breaches.
   - Replace "remove that risk" with an explicit statement that scraping reduces this local preference while cooling or flooring provides the established defence.
3. Backlog place: bedazzle §8 heat-dial follow-on (new, after row 7); do not jump the ruled order (rows 2 → 3 → 4 → 5 → 6 → 7). Depends on: cell temperature comp + RM_BreachCracks.cs placement weight.
4. A Mod Settings on/off toggle for it (every mod ships superb Mod Settings); default on = shipped behaviour; off degrades gracefully.
5. Art: re-queue through the art-evaluation pipeline from the draft's art brief (or check `artpipe_state.py find` for existing art first); install only judge-KEEP art via `art install`.
6. The mod's functional script gains a row that proves it (debug_process.md).

## criteria
- `RM_Saallen` def(s) load with no error on the minimal list; the SleepingIce selftest covers its C# logic offline.
- Every judge change listed above is visible in the def/C# or recorded as dropped with a reason.
- A Mod Settings toggle exists and is honoured.
- One live-proof line proves it appears and behaves on a Sleeping Ice quicktest map.
