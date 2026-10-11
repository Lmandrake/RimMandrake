# WARSCAR_OLD_TONGUE_1 — the old tongue: the manuals are on the walls

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.8 (ruled IN turn 2; the
tech chain adopted at the GPT card: readings unlock **specific steps**, never generic lore).

## spec

1. **`RM_InscribedPanel`** in three subtypes, each with its own glyph art (hospice, projector, pool),
   placed on ruin walls and projector bases by the rings genstep; plus plain "rest" panels.
2. **Reading:** a work job gated on **Intellectual 8**, using Biotech
   `CompProperties_CompAnalyzableUnlockResearch`; sets defined by `ResearchProjectDef.requiredAnalyzed`:
   **hospice protocols** (2 panels) → lower cradle failure, oddities at diagnosis;
   **projector calibration** (3) → the screen's calibrated mode, later fabricated projector cores;
   **phase reading** (3) → the pool phase reader. "Rest" panels: `CompStudiable` + an `IThingStudied`
   comp (vanilla `CompStudyUnlocks` shape) granting research points; every third reveals a sealed cache
   or a buried chassis. Verify: whether analysis consumes the panel; whether a set of 3 needs 3 distinct
   defs.
3. **One lore-gate surface:** panels do not advance the lore ladder (the pilgrim camps do).
4. **Campaign:** each transcription is also an Antiquities artifact for the Reading Station
   (`RUT_Antiquities`); Ascendant Helix / Deepwater Compact buy them at a premium. A trade, not a gate.
5. **Readable signs:** a read panel shows a chalk mark (graphic swap); unread panels of a needed set are
   listed in the research tooltip with their map location.
6. **Mod Settings:** panels per map · reveal chance · skill gate.

## criteria

- Reading the two hospice panels unlocks the protocols project; the three projector panels unlock
  calibration; the three pool panels unlock the phase reader.
- A pawn below Intellectual 8 cannot take the job.
- A read panel swaps to its chalk-marked graphic.

## built (offline, 2026-10-11 pass; first slice e95f75751)
- Rest panels are read by the SAME transcribe job and Intellectual gate as the set panels (a `restPanel` flag on
  `CompInscribedPanel`), not a separate `CompStudiable` study: one job, one gate, one chalk path. A read gives
  research points to the current project (refused with a reason when none is chosen); every 3rd rest panel read
  game-wide reveals a sealed crate or a slagged/posed kneeling chassis nearby.
- Every read drops `RM_OldTongueTranscription`; the Utinni layer
  (`src/RimUtinni/Antiquities/Patches/RUT_OldTongueTranscription.xml`) makes it an Antiquities artifact and lists the
  Helix and Deepwater as premium buyers. The premium is a `Tradeable.GetPriceFor` postfix (the engine has no XML lever
  for a buy-side premium).
- The research tooltip of each `RM_OldTongue_*` project lists the unread panels of its set (map and cell).
- PROVISIONAL numbers: 150 research points per rest panel, 2 rest panels per map, a find every 3rd read, transcription
  MarketValue 40, premium x1.5. Settings: rest panels per map, rest points, find interval, transcriptions on/off,
  premium on/off.
- Art queued, not generated: `RM_InscribedPanel_Rest`, `RM_OldTongueTranscription`.
- Projector calibration has no consumer yet: `RM_OldTongue.ProjectorCalibrated` is unread until the screen work uses it.
