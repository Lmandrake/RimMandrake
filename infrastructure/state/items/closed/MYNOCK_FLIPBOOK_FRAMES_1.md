# MYNOCK_FLIPBOOK_FRAMES_1 — wing-beat flight frames for RSW_Mynock

`RSW_Mynock` flies (MaxFlightTime 30, see `src/RimStarWars/SWBestiary/Defs/ShipVermin/ThingDefs_Races/RSW_Mynock.xml`) but ships no
`flyingAnimationFramePathPrefix` frames, so it flies with no wing-beat. Owed: a whole-animal directional flip-book
(`<prefix><N>_<direction>`, N = 1..8, directions north/east/south; Sparrow is the template in
`~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md`), derived from the owner's accepted mynock and its new facings
(jobs `warscar_Mynock_v2_*`, Warscar sheet 2026-10-05; canon entry `design/RimStarWars/canon_references/mynock`), then wire
`flyingAnimation*` on its PawnKindDef. Never blocks flight. Verify flight by a state read of `Pawn_FlightTracker`, never an
unattended live visual hunt (CLAUDE.md, flyers).
