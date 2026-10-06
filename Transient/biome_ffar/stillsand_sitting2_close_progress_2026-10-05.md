# Stillsand sheet — sitting 2 close (2026-10-05)

Owner: "Finished Stillsand." Decisions: `Transient/biome_ffar/deep_desert_sheet_2026-10-04.decisions.json` (biome RM_Stillsand), 18 rows stamped 2026-10-06T05:34-05:36Z (22:34-22:36 PDT), writeCount 163.

## Read as a group — DONE
Every note on these rows is the SAME text as sitting 1 (78fde209c), carried over by the sidecar; what is new is the pick. Sitting 1's structural work already exists:
- Oommok x2 (68e5fb2ad) and WarWyrm +50% (a89376420) were applied for these same notes, so sizes were NOT scaled again (same call as the Abyss sitting-2 Wickwood).
- Soorrak already has real flight (MaxFlightTime 30, Locust shape).
- Duumma's corpse wiring (4160b08cd) pointed at an RM_Duumma_Corpse texture that was never installed (only the east render finished; north/south failed), so the corpse was drawing a missing texture.

## Ingest — DONE
reviewStatus stamped with sitting-2 evidence. `art.py ingest`: 48 rulings, 57 purges. 7 purges were refused, all on sitting-1 rows that are still live (Gizka, RSW_Ikee->Ogleknot, Vozzik). 0 unresolved.
RM_KneelOllim A got NO ruling event: the row is purgeTouched with no decidedAt, so ingest reads it as a purge-only touch. His A is already the in-game picture, so no install was needed.
Req-9 check against the jobs file: all sitting-2 redo rows are covered. The only rows it flags are the sitting-1 RSW_ tier moves (RSW_LightPipeNub, RSW_Ollim, RSW_Vozzik), whose jobs belong to sitting 1.

## Installs — DONE (30, all `art.py install --ruling`, all `placeholder_detect` = real)
- RM_Oommok C, RM_ShadeMite B, RM_Soorrak D (Stillsand). RSW_GraniteSlug C and RSW_WarWyrm C (SWBestiary). RSW_GreaterKraytDragon E (GreaterKraytDragonArtOverride). 3 facings each.
- RSW_Plant_Bloddle A-G -> `RSW_Plant_Bloddle{A..G}.png` and RM_Glasscrust B-F -> `RM_Glasscrust{B..F}.png`: these are his kept variants (the `variants` field). Both defs were already Graphic_Random.
- Already live, so no install: RM_Aurrok A, RM_KneelOllim A, RM_UltrissPad A. RM_Ollim hold = no change.
- Not installed: RSW_Kreetle I is an east-only render, so it is used as the derive source instead. KraytDragon _j B and _m C, and Scurrier _m B, are already in game.

## Size changes — none (already applied in sitting 1, see above)

## Duumma answer
Q: "What does it look like when it's attacked?" A: Until now it looked like the half-buried dome in every state, including attacked and dead, because the dome was its only body graphic and the corpse art had never landed.
Now the dome is its sand (swimming) graphic, and a surfaced barrel body is queued as its body and corpse graphic. Gap: on sand it still shows the dome while standing still and being hit (noted on STILLSAND_SAND_SWIM_REMAINDER_1).

Def (`RM_Stillsand_Fillout.xml`): added RM_SandBuriedGraphicExtension, moved the dome to swimmingGraphicData, and removed the broken corpseGraphicData. bodyGraphicData stays on the dome until the surfaced art is installed. NEXT is on the item.

## Jobs queued — DONE (47 jobs from 37 rows), `Transient/biome_ffar/stillsand_sitting2_jobs_2026-10-05.json`
- Aurrok v3: less dinosaur, keeps the fins, derived per facing from A.
- Oommok v3: organic, dirty plating, no ears, derived from C.
- ShadeMite grey: a repaint of the B art via `reference`, no def colour.
- Soorrak v3: same 1024 canvas, which is already correct for drawSize 4.5. D filled the frame edge to edge (bbox 19..1015), so the re-render pulls it in.
- Duumma surfaced body (3 facings). LightPipeNub v2 (fresh, no note).
- Variants: Bloddle 4, Glasscrust 4, KneelOllim 5.
- Canon: GraniteSlug v3 (from C), GreaterKrayt v3, KraytDragon v3 (four-legged, `_f`), Kreetle v2 (from I), Scurrier v3, WarWyrm v3 (from C).
Every row carries his note verbatim as owner_note. No facing words in any prompt.

## Canon entries — DONE
- greaterkraytdragon: `## ruling` recorded verbatim. The defName line was wrong (it said the species was not in this repo), now corrected to RSW_GreaterKraytDragon.
- sith_wyrm (RSW_WarWyrm): `## ruling` recorded verbatim.
- graniteslug, kraytdragon, kreetle, scurrier: entries already existed and are wired via `canon`.

## Soorrak flight — DONE
Flight was already wired. FLYER_FLIPBOOK_ART_1 exists (filed by Pyrelands) and lists RM_Soorrak. A rimflow note there says to chain its flip-book off the v3 pick. No live testing.

## Validation
validate_patch on RM_Stillsand_Fillout.xml: OK, 0 errors. run_selftests 191/192. The one failure, bridgetools `selftest_tool_metadata`, was already failing before this work and nothing here touches it.

## Commits
(see report)
