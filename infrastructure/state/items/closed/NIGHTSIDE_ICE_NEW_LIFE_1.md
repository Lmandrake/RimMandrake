# NIGHTSIDE_ICE_NEW_LIFE_1 — the Nightside Ice's strange life: sheet sitting, then defs and C#

Decision taken by question card (owner, 2026-10-05): "Design the strange life".

Draft: `design/Jawa/worldbuilding/biomes/nightside_ice_roster_draft_2026-10-05.md` (every row DRAFT).
Authority: `design/Jawa/worldbuilding/biomes/sleeping_ice.md` §4, §4c, §5/§6, roster consequences;
turn-1 rulings in `nightsideice_bedazzle_review_2026-10-01.md` §8 (kesshet passed, not re-pitched).

## spec

1. **Sheet sitting.** Put the draft before the owner on a review sheet: the six ruled organisms
   (sohl, shivven, frissim, wyrmlet, dhorrumak, hessarund) with their existing art, and the four new
   ones (saallen, oolm, neshkoll, the ice-kept dead) with the art queued in
   `Transient/biome_ffar/nightsideice_newlife_jobs_2026-10-05.json` (artpipe ids
   `nightsideice_newlife_*_v1`). Ask the draft's §3 questions. Record rulings here.
2. **Build** (FOUNDRY, after the ruling): defs and C# per the draft's §4 cost table, in the owner's
   ruled backlog order (bedazzle §8 rows 2–7). File per-organism build items at ticket-out.

## criteria

- Every organism in the draft carries the owner's keep/cut/change ruling.
- Each admitted organism has a build item or is folded into an existing backlog row by name.

## rulings (delegated: design, 2026-11-03)

Judge: GPT via `src/RimMandrake/Utils/gpt_consult.py`, no maker context; brief, inputs and full verdict in
`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`.

| organism | verdict | build item |
|---|---|---|
| sohl | KEEP | `SOHL_BUILD_ONE_MOVE_TOTAL` |
| shivven | KEEP | built: `NIGHTSIDEICE_SHIVVEN_BUILD_1` (closed) |
| frissim | KEEP (flightless, not food) | `FRISSIM_BUILD_WAITS_FOR_THAW` |
| wyrmlet | KEEP | `WYRMLET_BUILD_SHIVVEN_HAND_ME_DOWNS` |
| dhorrumak | KEEP | `DHORRUMAK_BUILD_BIGGEST_LAST` |
| hessarund | CHANGE: no research role, no behaviour | `HESSARUND_BUILD_JUST_A_RIDGE` |
| saallen | CHANGE: scraping lowers breach weight only | `SAALLEN_BUILD_BLISTERS_ON_CUE` |
| oolm | CHANGE: clonal stage of the sohl lineage, per-colony identity, no insulation promise | `OOLM_BUILD_ONE_BODY_MANY_LOBES` |
| neshkoll | KEEP (lean is approximate: Rot4) | `NESHKOLL_BUILD_POINTS_AT_LEAKS` |
| the ice-kept dead | CHANGE: warmth must have a real source; theft leaves a sign; tablet optional | `ICEKEPT_DEAD_BUILD_CUT_OUT_COLD` |

§3 answers: Q1 admit all four (three with changes); Q2 names kept; Q3 UNSURE, shipped shivven art stays;
Q4 frissim flightless and not harvested as food; Q5 UNSURE, default one top-down spent-body graphic;
Q6 one shared catalyst-crust resource. Art for the four new organisms: the 2026-10-05 renders are gone from
disk (jobs `nightsideice_newlife_*_v1` in artpipe `done/`, never collected); each build item re-queues its art.
