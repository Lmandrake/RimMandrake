# HESSARUND_BUILD_JUST_A_RIDGE

Hessarund: the living ridge, a mineable landform yielding catalyst crust (defs). Filed by `NIGHTSIDE_ICE_NEW_LIFE_1` at ticket-out (delegated: design).

## spec
1. Build `RM_Hessarund` in `src/RimMandrake/SleepingIce/` per the roster draft `design/Jawa/worldbuilding/biomes/nightside_ice_roster_draft_2026-10-05.md` §1.6 (In play, Reads in-game, Description, Build cost), as amended below.
2. Judge verdict **CHANGE** (`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`, organism `hessarund`).
   Changes the build must carry:
   - Remove the proposed new cold-rejection research role. Retain catalyst crust as the ruled mining yield; ordinary integration into existing crafting does not require a new biome-specific technology.
   - Keep the ridge entirely without behaviour, as required by bedazzle §8, row 2.
   Judge factual flags that touch it:
   - The displayed build table is not the ratified execution order: it begins with row-7 hessarund work before row-2 thaw/calving and row-4 sohl. Follow bedazzle §8's ordered backlog and explicitly schedule new work without jumping it.
3. Backlog place: bedazzle §8 row 7 (ice forms); do not jump the ruled order (rows 2 → 3 → 4 → 5 → 6 → 7). Depends on: mineable plate + map GenStep line; no behaviour (bedazzle §8 Q2).
4. A Mod Settings on/off toggle for it (every mod ships superb Mod Settings); default on = shipped behaviour; off degrades gracefully.
5. Art: re-queue through the art-evaluation pipeline from the draft's art brief (or check `artpipe_state.py find` for existing art first); install only judge-KEEP art via `art install`.
6. The mod's functional script gains a row that proves it (debug_process.md).

## criteria
- `RM_Hessarund` def(s) load with no error on the minimal list; the SleepingIce selftest covers its C# logic offline.
- Every judge change listed above is visible in the def/C# or recorded as dropped with a reason.
- A Mod Settings toggle exists and is honoured.
- One live-proof line proves it appears and behaves on a Sleeping Ice quicktest map.
