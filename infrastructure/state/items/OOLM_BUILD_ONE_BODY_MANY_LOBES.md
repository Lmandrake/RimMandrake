# OOLM_BUILD_ONE_BODY_MANY_LOBES

Oolm: clonal mineable lobes, one body per colony (defs + C#). Filed by `NIGHTSIDE_ICE_NEW_LIFE_1` at ticket-out (delegated: design).

## spec
1. Build `RM_Oolm` in `src/RimMandrake/SleepingIce/` per the roster draft `design/Jawa/worldbuilding/biomes/nightside_ice_roster_draft_2026-10-05.md` §2.2 (In play, Reads in-game, Description, Build cost), as amended below.
2. Judge verdict **CHANGE** (`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`, organism `oolm`).
   Changes the build must carry:
   - Define oolm explicitly as the sessile clonal stage or colony form of the sohl lineage, rather than an independent species produced by sohl fragmentation.
   - Track colony identity rather than treating every lobe anywhere on the map as automatically one individual.
   - Drop the material-dependent wall-insulation promise from the small build, or budget and validate the required heat-transfer implementation separately.
   - Describe mining hardening as a passive physical response; do not introduce vibration sensing or awareness of remote mining.
   Judge factual flags that touch it:
   - Oolm's vanilla insulation claim conflates stuff insulation stats with material-dependent wall heat transfer. Declaring StuffProperties does not by itself implement the promised insulating walls; the XML-plus-tiny-comp estimate omits that work.
   - The proposed oolm comp counts lobes remaining, but the stated behaviour depends on lobes mined from a particular colony. Those are different measurements, especially if lobes are destroyed, spawned or belong to different pan margins.
3. Backlog place: bedazzle §8 new (after row 7); do not jump the ruled order (rows 2 → 3 → 4 → 5 → 6 → 7). Depends on: sohl fragment hook needs SOHL_BUILD_ONE_MOVE_TOTAL.
4. A Mod Settings on/off toggle for it (every mod ships superb Mod Settings); default on = shipped behaviour; off degrades gracefully.
5. Art: re-queue through the art-evaluation pipeline from the draft's art brief (or check `artpipe_state.py find` for existing art first); install only judge-KEEP art via `art install`.
6. The mod's functional script gains a row that proves it (debug_process.md).

## criteria
- `RM_Oolm` def(s) load with no error on the minimal list; the SleepingIce selftest covers its C# logic offline.
- Every judge change listed above is visible in the def/C# or recorded as dropped with a reason.
- A Mod Settings toggle exists and is honoured.
- One live-proof line proves it appears and behaves on a Sleeping Ice quicktest map.
