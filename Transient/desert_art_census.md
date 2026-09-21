# Desert family art census — DESERT_FAMILY_PORT_EXECUTION_1

Census only. No art generated, queued, or deleted by this pass.

Source sheet: `Transient/desert_family_review_2026-09-20.decisions.json` (109 rows, blanket owner ruling: replace).
Ported defs scanned: every `.xml` under `src/RimStarWars/SWBestiary/` and `src/RimUtinni/` (763 files, 2272 `<defName>` occurrences), ThingDef AND PawnKindDef blocks both parsed for `<texPath>`.

## 🔴 Headline finding: the artpipe daemon is ALREADY running this exact wave, right now

`infrastructure/artpipe/registry.jsonl` carries **251 `target` entries with `source: "DESERT_FAMILY_PORT_EXECUTION_1"`**, first `registered` at **2026-09-20T09:41:56-07:00** (epoch 1789922516.97) and still running as of this census — the newest registry line in the whole file (epoch 1789950315, `rmleachmoss_v1`) postdates it. This means **someone/something already queued `fill_queue.py` for nearly this entire item, concurrently with this census.** As captured at the moment of this scan:

- **24 rows: GENERATED, validator verdict PASS on all 3 directions** — real renders already sitting in `_artsrc/`/`done/` today, just not yet reviewed by the owner or wired into the defs.
- **1 row (Kybuck): GENERATED, MIXED verdict** (2 pass / 1 fail) — south+east usable, one direction needs a retry.
- **52 rows: QUEUED but not yet generated** — a job exists in the pipeline for them; they will very likely be GENERATED_PASS soon if you re-run this census later. **Do not file `fill_queue.py` for these — a job already exists; re-filing would duplicate work in flight.**
- **4 rows: not part of this wave at all** (`RSW_ImperialToad`, `RSW_Jellypot`, `JOE_Landopus`, `RSW_MossBeetle` — the four "already ours" defs from `BMT_FAUNA_ABSORPTION_1`/`SHIP_VERMIN_MOD_1`-adjacent absorptions). These are genuinely untouched by any art job.

**Because a job is already in flight for 77 of the 81 rows, `verdict` below uses a fourth state, `IN-FLIGHT`, for the 53 GENERATED/QUEUED-but-unreviewed rows that are neither HAS ART (nothing to review/wire yet) nor OWED (a job already exists — queuing again would duplicate).** Only genuinely untouched rows are marked OWED.

## 🔴 Second finding: `RSW_MossBeetle` (row `A_RSW_MossBeetle`) already has an owner ruling — CUT

`Transient/deeps_flora_fauna_review_2026-09-18.decisions.json` (a Deeps-biome review sheet, owner-approved 2026-09-19) carries:

```
"RSW_MossBeetle": {"decision": "cut", "note": "", "prefill": "keep", "at": "2026-09-19T06:01:01.840Z"}
```

`RSW_MossBeetle` is the SAME defName the desert sheet ports as row `A_RSW_MossBeetle` ("already ours" per the item doc). The owner ruled to CUT this species entirely one day before the desert blanket-replace ruling. **This is a scope conflict, not an art question** — flagging it here rather than silently generating or leaving stale art for a species he already cut. (`RSW_MossBeetleLarvae` is a separate defName, ruled `regen` the same sitting — not this row.)

## 4 rows carrying OUR OWN art already (not counted in the 81)

| defName | texPath | art file on disk |
|---|---|---|
| `RSW_Plant_Chakroot_Wild` | `Things/Plant/RSW_Plant_Chakroot_Wild` | `RSW_Plant_Chakroot_WildA.png` — confirmed on disk |
| `RSW_Plant_HubbaGourd_Wild` | `Things/Plant/RSW_Plant_HubbaGourd_Wild` | `RSW_Plant_HubbaGourd_WildA.png` — confirmed on disk |
| `RSW_Plant_Bloddle` | `Things/Plant/RSW_Plant_Bloddle` | `RSW_Plant_BloddleA.png` — confirmed on disk |
| `RSW_Mynock` (row `A_Mynock`) | `RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock` | `Mynock.png` (49KB) — confirmed on disk, from `SHIP_VERMIN_MOD_1` |

⚠️ The item doc said "3 rows carry our own art"; this scan found a 4th (`RSW_Mynock`), already fully wired with its own texPath — not a donor path at all, so it needed no census entry below. Correcting the doc's count is a job for whoever next touches that file.

## The 81 rows pointing at donor art

| our defName | donor texPath in use | existing art found? (path + where) | owner already ruled? | verdict |
|---|---|---|---|---|
| `RSW_Kreetle` | `swanimals/Kreetle/Kreetle, swanimals/Kreetle/Kreetle_Dessicated, +2 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_kreetle/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_FrilledGorg` | `swanimals/FrilledGorg/FrilledGorg, swanimals/FrilledGorg/FrilledGorgA, +7 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_frilledgorg/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Gorg` | `swanimals/Gorg/Gorg, swanimals/Gorg/GorgA, +9 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_gorg/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Iriaz` | `swanimals/Iriaz/Iriaz, swanimals/Iriaz/Iriaz_Dessicated` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_iriaz/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_LongtailGorg` | `swanimals/LongtailGorg/LongtailGorg, swanimals/LongtailGorg/LongtailGorgA, +8 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_longtailgorg/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Scavrat` | `swanimals/Scavrat/Scavrat, swanimals/Scavrat/Scavrat_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_scavrat/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Bantha` | `swanimals/Bantha/BanthaW, swanimals/Bantha/BanthaW_j, +2 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_bantha/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Eopie` | `swanimals/Eopie/Eopie, swanimals/Eopie/EopieA, +6 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_eopie/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Lothcat` | `swanimals/Lothcat/Lothcat_Dessicated, swanimals/Lothcat/Lothcat_f, +1 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_lothcat/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Mudhorn` | `swanimals/Mudhorn/Mudhorn, swanimals/Mudhorn/Mudhorn_Dessicated, +2 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_mudhorn/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Ronto` | `swanimals/Ronto/Ronto, swanimals/Ronto/Ronto_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_ronto/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Scurrier` | `swanimals/Scurrier/Scurrier_Dessicated, swanimals/Scurrier/Scurrier_f, +1 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_scurrier/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Sketto` | `swanimals/Sketto/Sketto, swanimals/Sketto/Sketto_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_sketto/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Igitz` | `swanimals/Igitz/Igitz, swanimals/Igitz/Igitz_Dessicated, +2 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_igitz/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_ImperialToad` | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/GoetoToad/Dessicated_GoetoToad, swanimals/BiomesTeam/BMT_Caverns/Things/Animal/ImperialToad/ImperialToad` | None found — no artpipe job, no `_artsrc`/`done` entry, no review-sheet ruling | No | OWED |
| `RSW_Jellypot` | `Things/Pawn/Animal/Spelopede/Dessicated_Spelopede, swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Jellypot/Jellypot` | None found — no artpipe job, no `_artsrc`/`done` entry, no review-sheet ruling | No | OWED |
| `RSW_Urusai` | `swanimals/Urusai/Urusai, swanimals/Urusai/Urusai_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_urusai/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_WompRat` | `swanimals/WompRat/WompRat, swanimals/WompRat/WompRat_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_womprat/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Kybuck` | `swanimals/Kybuck/Kybuck, swanimals/Kybuck/Kybuck_Dessicated` | PARTIAL — generated today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_kybuck/*`); 2 of 3 directions PASS, 1 FAIL | Not yet — awaiting_verdict | IN-FLIGHT |
| `RSW_Massiff` | `swanimals/Massiff/Massiff, swanimals/Massiff/Massiff_Dessicated` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_massiff/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Shyrack` | `swanimals/Shyrack/Shyrack, swanimals/Shyrack/Shyrack_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_shyrack/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `JOE_Landopus` | `Things/Pawn/Animal/landopus/dessicated_landopus, Things/Pawn/Animal/landopus/landopus, +1 more` | None found — no artpipe job, no `_artsrc`/`done` entry, no review-sheet ruling | No | OWED |
| `RSW_Pufferpig` | `swanimals/Pufferpig/Pufferpig, swanimals/Pufferpig/Pufferpig_Dessicated, +1 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_pufferpig/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Sandstrider` | `Things/Pawn/Animal/AA_DesertAve/AA_DesertAve` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Sandstrider/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Anooba` | `swanimals/Anooba/Anooba_Dessicated, swanimals/Anooba/Anooba_f, +1 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_anooba/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Corinathoth` | `swanimals/Corinathoth/Corinathoth, swanimals/Corinathoth/Corinathoth_Dessicated` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_corinathoth/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Gizka` | `swanimals/Gizka/Gizka, swanimals/Gizka/GizkaW, +1 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_gizka/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Gutkurr` | `swanimals/Gutkurr/Gutkurr, swanimals/Gutkurr/Gutkurr_Dessicated` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_gutkurr/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Jamel` | `swanimals/Jamel/Jamel, swanimals/Jamel/Jamel_Dessicated` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_jamel/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Nuna` | `swanimals/Nuna/Nuna_Dessicated, swanimals/Nuna/Nuna_f, +1 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_nuna/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Worrt` | `swanimals/Worrt/Worrt, swanimals/Worrt/WorrtA, +6 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_worrt/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Wraid` | `swanimals/Wraid/Wraid, swanimals/Wraid/Wraid_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_wraid/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Spineroller` | `Things/Pawn/Animal/AA_Needleroll/AA_Needleroll` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Spineroller/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Hrumph` | `swanimals/Hrumph/Hrumph, swanimals/Hrumph/Hrumph_Dessicated, +2 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_hrumph/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_IridonianReek` | `swanimals/IridonianReek/IridonianReek, swanimals/Reek/Reek_Dessicated, +2 more` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_iridonianreek/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Jimvu` | `swanimals/Jimvu/Jimvu, swanimals/Jimvu/Jimvu_Dessicated` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_jimvu/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_Kwi` | `swanimals/Kwi/Kwi, swanimals/Kwi/Kwi_Dessicated` | YES — generated + validator PASS today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_kwi/*`), sitting in `_artsrc/`/`done/`, awaiting owner review | Not yet — awaiting_verdict (owner has not looked) | IN-FLIGHT |
| `RSW_MossBeetle` | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/MossBeetle/Dessicated_MossBeetle, swanimals/BiomesTeam/BMT_Caverns/Things/Animal/MossBeetle/MossBeetle` | None generated (not in current wave) | **YES — `deeps_flora_fauna_review_2026-09-18` (approved 2026-09-19): decision `cut`** | RULED |
| `RSW_Skalder` | `swanimals/Skalder/Skalder, swanimals/Skalder/Skalder_Dessicated, +1 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desert_swaca_skalder/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Uvak` | `swanimals/Uvak/Uvak, swanimals/Uvak/Uvak_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_uvak/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Varactyl` | `swanimals/Varactyl/Varactyl_Dessicated, swanimals/Varactyl/Varactyl_f, +1 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_varactyl/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Zeer` | `swanimals/Zeer/Zeer, swanimals/Zeer/Zeer_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_zeer/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Spinerat` | `Things/Pawn/Animal/AA_Cactipine/AA_Cactipine` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Spinerat/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Falumpaset` | `swanimals/Falumpaset/Falumpaset, swanimals/Falumpaset/FalumpasetA, +5 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_falumpaset/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Grank` | `swanimals/Grank/Grank, swanimals/Grank/Grank_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_grank/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Jakobeast` | `swanimals/Jakobeast/Jakobeast, swanimals/Jakobeast/Jakobeast_Dessicated, +2 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_jakobeast/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Nerf` | `swanimals/Nerf/Nerf_Dessicated, swanimals/Nerf/Nerf_f, +3 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_nerf/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Qormot` | `swanimals/Qormot/Qormot, swanimals/Qormot/Qormot_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_qormot/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Shaak` | `swanimals/Shaak/Shaak, swanimals/Shaak/Shaak_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_shaak/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Strill` | `swanimals/Strill/Strill, swanimals/Strill/Strill_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_strill/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_TeeMuss` | `swanimals/TeeMuss/TeeMuss, swanimals/TeeMuss/TeeMuss_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_teemuss/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_WarWyrm` | `swanimals/WarWyrm/WarWyrm, swanimals/WarWyrm/WarWyrm_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_warwyrm/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Cannok` | `swanimals/Cannok/Cannok, swanimals/Cannok/Cannok_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_cannok/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Stareling` | `Things/Pawn/Animal/AA_Eyeling/AA_Eyeling` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Stareling/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_KraytDragon` | `swanimals/KraytDragon/KraytDragon_Dessicated, swanimals/KraytDragon/KraytDragon_f, +3 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_kraytdragon/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Whisperbird` | `swanimals/Whisperbird/Whisperbird, swanimals/Whisperbird/Whisperbird_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_whisperbird/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Barbthorn` | `Things/Pawn/Animal/AA_NeedlePost/AA_NeedlePost` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Barbthorn/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Sporepaw` | `Things/Pawn/Animal/AA_Wildpawn/AA_Wildpawn` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Sporepaw/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Bolotaur` | `swanimals/Bolotaur/Bolotaur, swanimals/Bolotaur/Bolotaur_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_bolotaur/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Clodhopper` | `swanimals/Clodhopper/Clodhopper, swanimals/Clodhopper/Clodhopper_Dessicated, +1 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_clodhopper/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_FeralGrazer` | `swanimals/FeralGrazer/FeralGrazer, swanimals/FeralGrazer/FeralGrazer_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_feralgrazer/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_GraniteSlug` | `swanimals/GraniteSlug/GraniteSlug, swanimals/GraniteSlug/GraniteSlug_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_graniteslug/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Krykna` | `swanimals/Krykna/Krykna, swanimals/Krykna/Krykna_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_krykna/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Pikobis` | `swanimals/Pikobis/Pikobis, swanimals/Pikobis/Pikobis_Dessicated, +1 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_pikobis/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Runyip` | `swanimals/Runyip/Runyip, swanimals/Runyip/Runyip_Dessicated, +4 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_runyip/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Convor` | `swanimals/Convor/Convor, swanimals/Convor/Convor_Dessicated, +1 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_convor/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Vulptex` | `swanimals/Vulptex/Vulptex, swanimals/Vulptex/Vulptex_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_vulptex/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Sandhorn` | `Things/Pawn/Animal/AA_Gigantelope/AA_Gigantelope, Things/Pawn/Animal/AA_Gigantelope/AA_Gigantelope_baby` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Sandhorn/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Dunestalker` | `Things/Pawn/Animal/AA_SandProwler/AA_SandProwler` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Dunestalker/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Voorpak` | `swanimals/Voorpak/Voorpak, swanimals/Voorpak/Voorpak_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_voorpak/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_FeralNerf` | `swanimals/FeralNerf/FeralNerf, swanimals/FeralNerf/FeralNerf_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_feralnerf/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Porg` | `swanimals/Porg/Porg, swanimals/Porg/Porg_Dessicated, +3 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_porg/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Ferroclaw` | `Things/Pawn/Animal/AA_Terramorph/AA_Terramorph` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Ferroclaw/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Sandmaw` | `Things/Pawn/Animal/AA_SandSquid/AA_SandSquid` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Sandmaw/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Sporemass` | `Things/Pawn/Animal/AA_Wildpod/AA_Wildpod` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Sporemass/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Tuskcoil` | `Things/Pawn/Animal/AA_MammothWorm/AA_MammothWorm` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Tuskcoil/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Horax` | `swanimals/Horax/Horax, swanimals/Horax/Horax_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_horax/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_KowakianMonkeyLizard` | `swanimals/KowakianMonkeyLizard/KowakianMonkeyLizard, swanimals/KowakianMonkeyLizard/KowakianMonkeyLizardA, +5 more` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_kowakianmonkeylizard/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_GreaterKraytDragon` | `swanimals/GreaterKraytDragon/GreaterKraytDragon, swanimals/GreaterKraytDragon/GreaterKraytDragon_Dessicated` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_greaterkraytdragon/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Voltmaw` | `Things/Pawn/Animal/AA_TetraSlug/AA_TetraSlug` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`RSW_Voltmaw/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |
| `RSW_Plant_Nysyllin_Wild` | `swplants/Nysillin` | Job QUEUED today under `DESERT_FAMILY_PORT_EXECUTION_1` (`desertportb_plant_nysyllin_wild/*`) — not yet rendered | N/A — nothing to review yet | IN-FLIGHT |

⚠️ **`RSW_Ferroclaw` (row `A_AA_Terramorph`) has a SECOND, earlier art job outside this wave**: `aa_terramorph` (source `ART_REGEN_WAVE5_QUEUE_1`), south+east PASS, north FAIL then retried as `aa_terramorph_v1_north_r2` — sitting in `_artsrc/`/`done/` since before this item started. Its own-wave job (`desertportb_ferroclaw`) queued today may be redundant with it; worth reconciling before either is wired in, rather than treating them as two separate art needs.

## Counts

- HAS ART (usable now, real render already on disk, own-art rows not part of the 81): **4**
- RULED (owner already judged — do not re-queue): **1** (`RSW_MossBeetle`, cut)
- IN-FLIGHT (job already queued/generated today under this same item — do NOT re-queue): **77** (24 GENERATED_PASS + 1 GENERATED_MIXED + 52 QUEUED_NOT_GENERATED)
- OWED (genuinely nothing exists or queued, safe to queue later): **3** (`RSW_ImperialToad`, `RSW_Jellypot`, `JOE_Landopus`)

**safe to queue: 3**

Total rows examined: 81 donor-art rows + 4 own-art rows = 85 (matches the item doc's 85-of-109 def-port figure).
