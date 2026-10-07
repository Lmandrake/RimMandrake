# Pyrelands sheet close (second pass) — 2026-10-07

Owner typed (2026-10-07): "Please immediately accept the Pyrelands sheet, wire in, deploy, purge, etc. whatever you need to do with all that art. There are as yet unaccepted changes from last time. Please Enact them all fully so I don't have to keep reauditing this. Firehawk is being handled separately"
RM_FireHawk skipped entirely (separate agent).

One line per milestone.

## 1. Decisions read
18 rows. New clicks since the 10-05 close (at 2026-10-07): purge-only on RM_Barbslinger (A), RSW_Dalgo (B), RSW_Orray (F), RM_Flamefang (A, keep variants A+B). No new notes, no redo decisions. Earlier unfinished business: FireWasp 8-frame flight set (his note 'Needs flyer art now') — 23/24 frames done, frame 8 east failed in worker; requeued as pyrelands_firewasp_flight8_8r_east (Transient/biome_ffar/pyrelands_close_jobs_2026-10-07.json).
## 2. Ingest
`art.py ingest`: 3 rulings (Orray F + its kept variants A/G at the new click), 56 purges executed (Barbslinger, Dalgo, Orray, Flamefang B), 1 refused: Gizka female south `3599473822d4` (live at GizkaArtOverride GizkaW_south.png; no ruling covers a replacement — needs his words). Every pick on the sheet is live (ledger check, FireHawk excluded); Iriaz D is an unclicked prefill and the Leaning Scrub sheet (10-06) ruled the live art keep.
## 3. FireWasp flight (installed unreviewed — his note "Needs flyer art now")
23 of 24 frames collected via artpipe_state collect into src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/FireWasp/FireWasp_Fly_<N>_<dir>.png. Contact (looked: same wasp, wings tuck→spread→tuck): Transient/biome_ffar/pyrelands_close_2026-10-07/firewasp_flight_contact.png. PawnKindDef RM_FireWasp wired: 7 frames for now (frame 8 east requeued; bump to 8 when it lands), 2 ticks/frame, drawSize 1 as multiplier (scales with life stage).
## 4. Checks
placeholder_detect file: 128/128 real (all Pyrelands PNGs except FireHawk, plus the sheet's ArtOverride/Baroque PNGs). texPaths: 26, all resolve (9 are vanilla). No _west.png in any Pyrelands creature folder, so no mirror needed.
## 5. Pushed 7b3df8349 (unit 1, via merge-tree/commit-tree; other agents' dirty files in this clone).
## 6. Deploy NOT run: --compose biomes plan (51 add/change lines) carries other agents' UNCOMMITTED files — untracked wreck PNGs in Abyss/Contagion/FeverWood/LongShade/Miasma/Stillsand/TheRot/Wasteland, Slime plant variants, Duumma surfaced art. Rerun once those are committed.
## 7. Selftests 223/223 pass.
## 8. Open
- Frame 8 east job `pyrelands_firewasp_flight8_8r_east` still pending in artpipe. NEXT: collect it to FireWasp_Fly_8_east.png (`artpipe_state.py collect`), set RM_FireWasp flyingAnimationFrameCount 7 -> 8.
- Gizka female south (`3599473822d4`, GizkaW_south.png, the 80% recolour alternate) stays live: his purge needs a replacement and no ruling covers one. NEXT: get his typed words to install his pick A onto GizkaW_*.
- Deploy waits on other agents' uncommitted biome files.
