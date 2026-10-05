# Tonight progress 2026-10-05 (BENCH helper)

## 1 requeue — DONE
Eight jobs failed on worker_error ("constrained to final schema only"), not quota, so requeue_quota_failures.py (matches the quota sentence only) would not move them. Same effect by hand, precedent = its own move: failed/<id>.json -> pending/, manifest parked in _requeued_manifests/ (stamp 20261005T0828): abyss_bulgra_v1, abyss_etchcap_b_v1, abyss_etchcap_c_v1, abyss_cindermare_facings_v1 east/north/south, abyss_drokattak_v2_north, plus RM_Virr_var2 (Blue Desert, same error). bulgra and Virr_var2 are already active. Daemon not touched.

## 2 queue drain estimate
At 08:50: ~243 pending + 5-6 active (the gap-fill agent added ~190 jobs). Measured ok rate: 27/h (last 1 h), 16.5/h (last 2 h), 18/h (last 4 h). Drain: ~9 h at 27/h (about 18:00 PDT) to ~15 h at 16.5/h (about 23:40). Not tonight in full; Abyss jobs (priority-10 class) go first.

## 3 four sheets rebuilt (--refresh, --sheet-only, same files and URLs, decisions files untouched, check_sheet 0 FAIL each)
- Abyss: new names shown on the 17 ported donor rows ("<new> (new name; was AA_x)"); the 8 old crags_* sets shown on their rows (vrakk, dhukk, hulggarok, kessik, brekkugar, gruzz, shekkur, ulkhorr); new renders join each row by job family as they land. Mapping lives in src/RimMandrake/Utils/art/sheet_row_overrides.json (read by art_sheet.py).
- Blue Desert: Thunderbeast v4 (C) and Vapaad canon v1/v2 shown; Vashpuk/Virr variants shown as they landed.
- Long Shade, Stillsand: refreshed with all landed renders.
- Letters: every previously ruled letter still resolves to the same pictures (checked against the ruled snapshot; Blue Desert's only differences are pictures he purged).

## 4 donor rule (owner: every donor row also needs a render of ours; donor art stays as past art)
Abyss: 12 rows still wait for a render of ours (AA_CrepuscularBeetle, DarkVandal, Darkbeast, DuskProwler, Murkling, Nightling, ShadowCharger; AB_GiantGamma, GiantStikehr, WildRadagast; AG_Gamma, AG_Septimum). All are covered by jobs already queued or active; no new jobs needed, so no fourth_sitting_donor_jobs file. Blue Desert, Long Shade, Stillsand: 0 donor rows without a render of ours.
