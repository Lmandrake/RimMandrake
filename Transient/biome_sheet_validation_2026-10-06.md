# Biome sheet validation 2026-10-06

Gate = `scaled_review_gate.py check` per sheet (covers canon images + Must show beside each row = req 5, donor column kept = req 4, no donor-only row without an art job = req 3). Decisions = `remap_decisions.py`: letters are stable, every used letter still names the same art; no orphans anywhere.

| sheet | gate | failing reqs | decisions unchanged | remapped | orphaned | served URL |
|---|---|---|---|---|---|---|
| abyss_sheet_2026-10-04 | PASS |  | 45 | 0 | 0 | http://localhost:42221/?t=___EEMoO2QcppfmJQaI2Ug |
| blue_desert_sheet_2026-10-04 | PASS |  | 37 | 0 | 0 | http://localhost:45233/?t=jMzcW8ulHgZBr1C6qhaa_Q |
| cauldron_sheet_2026-10-04 | FAIL | 13 | 57 | 0 | 0 |  |
| contagion_sheet_2026-10-04 | PASS |  | 35 | 0 | 0 | http://localhost:43397/?t=NMjAyC28d7KGB7pPD96mTQ |
| deep_desert_sheet_2026-10-04 | PASS |  | 47 | 0 | 0 | http://localhost:37603/?t=t45k8GQ3rUd1irxGf2wDug |
| desert_sheet_2026-10-04 | FAIL | 3,4,14 | 63 | 0 | 0 |  |
| feverwood_sheet_2026-10-05 | FAIL | 14 | 46 | 0 | 0 |  |
| floodedcanyon_sheet_2026-10-05 | FAIL | 3,5,14 | 27 | 0 | 0 |  |
| gelatinousslime_sheet_2026-10-05 | PASS |  | 13 | 0 | 0 | http://localhost:45117/?t=dRSEtE4IvhfZavZ-AfydCA |
| greentide_sheet_2026-10-05 | FAIL | 3,7,14 | 81 | 0 | 0 |  |
| greysea_sheet_2026-10-05 | PASS |  | 27 | 0 | 0 | http://localhost:44669/?t=J_ZXfQeWtDqycr8HAoDHqA |
| lanterndeeps_sheet_2026-10-05 | PASS |  | 30 | 0 | 0 | http://localhost:38059/?t=oX3JwP638NkkUgDfwz1D8Q |
| leaningscrub_sheet_2026-10-05 | FAIL | 2,3,4,5,14 | 99 | 0 | 0 |  |
| miasma_sheet_2026-10-05 | FAIL | 3 | 72 | 0 | 0 |  |
| nightsideice_sheet_2026-10-05 | PASS |  | 3 | 0 | 0 | http://localhost:40203/?t=2W3mCmiEKvcfk0FZXJLTCQ |
| pyrelands_sheet_2026-10-05 | PASS |  | 20 | 0 | 0 | http://localhost:38687/?t=jSg6QSfkAnAHwepOv1AAsQ |
| rustcathedral_sheet_2026-10-05 | PASS |  | 4 | 0 | 0 | http://localhost:46367/?t=LOmhIfz6mNqFAexH78UyOw |
| thechill_sheet_2026-10-05 | PASS |  | 22 | 0 | 0 | http://localhost:46283/?t=VwB746NKj_PfyqwUezoYPQ |
| theforge_sheet_2026-10-05 | FAIL | 3 | 26 | 0 | 0 |  |
| therot_sheet_2026-10-05 | FAIL | 3,4,5 | 59 | 0 | 0 |  |
| thescald_sheet_2026-10-05 | PASS |  | 25 | 0 | 0 | http://localhost:45237/?t=TEOCoJFqsWTNtD19rI3RFw |
| thesump_sheet_2026-10-05 | PASS |  | 16 | 0 | 0 | http://localhost:40751/?t=frI6wDWPo9g8_XcUhofvFA |
| twilightsea_sheet_2026-10-05 | PASS |  | 34 | 0 | 0 | http://localhost:39617/?t=wdJBetL0IKneb_QYlS-9rw |
| warscar_sheet_2026-10-05 | PASS |  | 18 | 0 | 0 | http://localhost:45611/?t=h2o0D7nMnupEB2wYnRTjOQ |
| wasteland_sheet_2026-10-05 | FAIL | 4,5 | 22 | 0 | 0 |  |
| webwork_sheet_2026-10-05 | PASS |  | 23 | 0 | 0 | http://localhost:38561/?t=LxgfLxpV-95jdm72OZ2jbg |
| weepingstones_sheet_2026-10-05 | FAIL | 3,14 | 55 | 0 | 0 |  |

Req meanings: 3 = donor-only/placeholder rows with no pending job; 4 = donor-sourced row lacks its donor column; 5 = canon block missing; 13 = blank render in browser; 14 = decisions/link check.
Sheets that FAIL keep their previous HTML (no variant default yet). Cauldron rebuilt fine but its re-check was still running at write time.
