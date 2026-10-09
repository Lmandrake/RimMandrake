# FLYER_FLIPBOOK_ART_1 — every flyer gets a wing-beat flip-book

**Census (2026-10-05, parse of every `src/**/*.xml` def, own ThingDefs only):** 64 creatures have
`MaxFlightTime > 0` (directly or through a ParentName in our XML); **36 have no PawnKindDef carrying
`flyingAnimationFramePathPrefix`** (and no patch adding one). They fly with no wing-beat: correct behaviour,
plainer look. Sanity probe: `RM_FireHawk` reads as HAS (5-frame set wired), `RSW_Mynock` and `RM_FireWasp` as MISSING.
Patch-side flight on donor defs: none found by that sweep, so treat it as unmeasured rather than zero.

Missing (36): RM_Blisterfloat, RM_Chellow, RM_Dustflutter, RM_Dwommo, RM_FeverSwarm, RM_FireWasp, RM_FleetFlier,
RM_Gorekite, RM_Grimewing, RM_Illoth, RM_Jossur, RM_Krannock, RM_Mirrik, RM_Murrelith, RM_Pirrik, RM_Sivvern,
RM_Skellarn, RM_Skellick, RM_Skerrel, RM_Skinflap, RM_Skiralim, RM_Soorrak, RM_Sparkleech, RM_Suush, RM_Thavrik,
RM_Thozzik, RM_ThozzikColony, RM_ThozzikColonyQueen, RM_ThozzikQueen, RM_ThozzikSpawned, RM_Vrisk, RM_Yammeth,
RM_Zellik, RSW_Mynock (also `MYNOCK_FLIPBOOK_FRAMES_1`), RUT_EmperorVulture, RUT_FleetFlier.

## The shape (CLAUDE.md, flyers section)
A whole-animal directional flip-book: `<prefix><N>_<north|east|south>` for N = 1..8, frame 1 has the wings tucked,
frame 5 has them fully spread, and the cycle returns to tucked. Wire it on the PawnKindDef only once the frames exist.
Never a Spastic wing render-tree. Verify flight by a `Pawn_FlightTracker` state read, never by an unattended live
visual hunt.

## How the jobs are made (artpipe has no multi-frame contract)
artpipe cannot express "frame N of a sequence". `derive_from` must also name a finished artpipe job, so it cannot point
at an installed picture. Pattern used for the Pyrelands pair
(`Transient/biome_ffar/pyrelands_flyer_flipbook_jobs_2026-10-05.json`, 48 jobs):
- frame 1 east attaches the grounded pick as `canon_reference`, and its prompt says it is the accepted individual;
- frame 1 south and north use `derive_from` frame 1 east;
- frame N of each facing uses `derive_from` frame N-1 of the same facing (a chain, so drift can accumulate; check frame 8 against frame 1).

## Progress
- Pyrelands, 2026-10-05: RM_FireHawk (8 new frames, replacing the old 5-frame set once he picks) and RM_FireWasp
  are queued as `pyrelands_{firehawk,firewasp}_flight8_<N>_<facing>`. Progress and the exact XML to add:
  `Transient/biome_ffar/pyrelands_close_progress_2026-10-05.md`.
- Blocking the owner's review: a NEW biome-mode sheet cannot pass `scaled_review_gate.py` on its first build.
  The gate's check_sheet step requires a decisions file, and `art_sheet.py` writes that file only after the
  gate passes. `art_sheet.py` also has no per-row sections or frame-strip layout for flip-books. Owed by the
  art-tool owner.

NEXT: once the `pyrelands_*_flight8` jobs are done, build the flyer review sheet, take his picks, install them, then wire `flyingAnimation*`.
