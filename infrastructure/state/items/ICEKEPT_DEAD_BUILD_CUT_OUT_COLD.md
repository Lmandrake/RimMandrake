# ICEKEPT_DEAD_BUILD_CUT_OUT_COLD

Ice-kept dead: bodies held in clear ice, cut out for corpse and gear (defs + C#). Filed by `NIGHTSIDE_ICE_NEW_LIFE_1` at ticket-out (delegated: design).

## spec
1. Build `RM_IceKeptDead` in `src/RimMandrake/SleepingIce/` per the roster draft `design/Jawa/worldbuilding/biomes/nightside_ice_roster_draft_2026-10-05.md` §2.4 (In play, Reads in-game, Description, Build cost), as amended below.
2. Judge verdict **CHANGE** (`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`, organism `ice_kept_dead`).
   Changes the build must carry:
   - Make tunnelers respond to an actual heat source used during extraction, a still-living occupant, or explicitly modelled residual warmth. A cold exposed corpse must not automatically emit heat.
   - Preserve extracted corpses and gear, and connect any theft to a visible drag/submergence sign and the recoverable larder.
   - Treat the ledger tablet as an optional proposed prop, not a confirmed requirement of the Cold Ledger rite; the supplied ruling establishes only the rite's admission.
   Judge factual flags that touch it:
   - Frissim refreezing is described inconsistently: §4 makes inclusion insects dormant outside thaw pulses, but the draft kills them when the ice refreezes. Default to renewed dormancy; actual deaths must leave readable remains rather than silently removing pawns.
   - A cold corpse does not become a thermal beacon merely because it is exposed. The draft must identify and implement the actual source of warmth.
   - The supplied Cold Ledger ruling does not specify a ledger tablet, an item drop or a corpse-loot requirement. Those details remain proposals.
   - The small cost estimates are conditional: frissim needs its thaw/calving infrastructure, wyrmlets need feeding and readable submergence behaviour, and ice-kept-dead theft needs the larder and recovery system. Those dependencies are not already completed merely because shivven movement is built.
   - Map-local GenSteps are allowed and are not prohibited planet worldgen. Likewise, subzero ice softening is not inherently liquid water; implementing an actual melt pool would violate §6.
3. Backlog place: bedazzle §8 row 2 (thaw/calving); do not jump the ruled order (rows 2 → 3 → 4 → 5 → 6 → 7). Depends on: corpse spawner (ancient-casket shape); shivven theft rides the larder (bedazzle §8 row 5, not yet an item).
4. A Mod Settings on/off toggle for it (every mod ships superb Mod Settings); default on = shipped behaviour; off degrades gracefully.
5. Art: re-queue through the art-evaluation pipeline from the draft's art brief (or check `artpipe_state.py find` for existing art first); install only judge-KEEP art via `art install`.
6. The mod's functional script gains a row that proves it (debug_process.md).

## criteria
- `RM_IceKeptDead` def(s) load with no error on the minimal list; the SleepingIce selftest covers its C# logic offline.
- Every judge change listed above is visible in the def/C# or recorded as dropped with a reason.
- A Mod Settings toggle exists and is honoured.
- One live-proof line proves it appears and behaves on a Sleeping Ice quicktest map.
