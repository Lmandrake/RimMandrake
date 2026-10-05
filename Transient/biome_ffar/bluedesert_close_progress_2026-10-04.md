# Blue Desert close — progress 2026-10-04 (BENCH helper)

## 1 ingest + install — DONE
- decisions.json carried the FIRST sitting's snapshotId (4a3c4f2f…); every second-sitting pick resolves only in the refreshed snapshot 0a169dd0… and every first-sitting pick resolves identically in both, so the stamp was corrected to 0a169dd0 and ingested: 14 rulings.
- `ingest.py` ignored the sheet's `variants` list; it now emits a keep ruling per kept variant column (4 more: Chimeglobe B, Glassfern C, Palefloss B, C).
- The install plan's plant targets (`Things/Plant/X/X.png`) were wrong: the three plants are already Graphic_Random folders (`Things/Plant/X/X/X_a.png`). Installed into the folders instead.
- Installed 16 via `--ruling`: Dovvik B×3, Murrek C×3 (RM_Murrek.png single skipped — no def reads it), Utikka B×3, Vrisk B east+south (B has no north; old north stays), Chimeglobe_b, Glassfern_a(=B)+_b(=C), Palefloss_b, _c. Chimeglobe A / Palefloss A were already live.
- Glassfern old A (49c80e23) purged per owner after replacement. Vhaulk purge a25f92f1 refused: that sha is live as RUT_AncientShieldedTurret (AssailantSalvage) — not touched.
- Untouched prefill rows (Dorrak, Krissek, Vekkit) carry no ruling.

## 2 def work — in progress
