# Art scripts re-review + conflict triage — 2026-10-09 (BENCH helper, owner asleep)

## 1. Re-review of `enact.py` and `ingest.py`

- `enact.py`: unchanged since the clean mark (`code_review_status` still said CLEAN). Re-read in full anyway: nothing found.
- `ingest.py` (changed at c272dca94): full read, zero significant findings. Marked clean (record in `infrastructure/state/code_review/BENCH.jsonl`). `selftest_enact.py`: ALL PASS.
- Can the stale-letter exemption let a changed picture through? Only if every one of these holds, so no fix made:
  - The exemption needs the snapshot in force at his last click (newest committed/on-disk version built at or before the click) to name the SAME shas, per facing, for that letter on that row (or on its `carriedFrom` row) as the current snapshot. A differing row or letter in the click-time snapshot returns False at once (stays CONFLICT).
  - Unknown always means stale: no click stamp, no click-time snapshot, row/column missing, git history unreadable.
  - Residual gap (very unlikely, noted not fixed): `snapshot_versions` sees only committed revisions plus the file on disk. An UNCOMMITTED rebuild between two commits that changed the letter and was later reverted to the older shas would be missed. Also the click time is the latest of decidedAt/at/variantsAt, so a page loaded before a rebuild and clicked after is judged against the newer one.
- Minor, non-blocking: `ruling_status()` calls `build_plan` without `stale`, so a sheet's status panel does not show a stale row as a conflict (enact does). Display only; no picture installed.

## 2. Conflict triage (preview only, `art.py enact <file> --no-deploy`, nothing applied)

Buckets: (a) benign protection (live elsewhere / owner-kept, not purged); (b) stale letter; (c) by-name pick ambiguous; (d) pick would overwrite a picture he kept; (e) other.
6 sheets are not ruled yet and enact refuses them (generator prefill): cauldron, floodedcanyon, theforge, therot, wasteland, weepingstones.

| sheet | a | b | c | d | e |
|---|--:|--:|--:|--:|--:|
| abyss | 2 | 4 | 2 | | |
| blue_desert | 1 | | | | |
| contagion | | | | 3 | |
| deep_desert | 3 | | | | |
| desert | | | 1 | | 2 |
| feverwood | | | | 2 | |
| gelatinousslime | | | | | 2 |
| greentide | 56 | 1 | 1 | | |
| greysea, lanterndeeps, nightsideice, pyrelands, thechill | none | | | | |
| leaningscrub | | 2 | | | 3 |
| miasma | | | | | 4 |
| rustcathedral | 3 | | | | |
| thescald | 2 | | | | |
| thesump | 1 | | | | |
| twilightsea | 10 | 2 | | | |
| warscar | | 4 | | | |
| webwork | | | | | 2 |
| **total** | 78 | 13 | 4 | 5 | 13 |

All 13 stale rows (b) are rows whose letter did not exist in the sheet he saw (new or renamed row), so they are unverifiable, not proven changed.

## What he must decide (buckets b to e)

**b. Re-click on the current sheet** (the letter he used did not exist in the sheet he saw; nothing was applied for these):
- abyss: GiantFibreStalk (A), GlowingGrass (E), Nevarithia (A), SicklyGlowMushroom (A)
- greentide: Beldon (H, J)
- leaningscrub: Durrok (A), Mullgoth (A)
- twilightsea: DancingSkresh (A), GrippingTerror (A)
- warscar: Bileworm, ElectricGryllotalpa, ElectricTick, JuggernautBeetle (all A)

**c. Your pick is a "by name" picture and the row has several graphics. Which graphic does it replace?**
- abyss: Nightling pick E (2 graphics); ShadowCharger pick G (3)
- desert: Nerf pick E (3)
- greentide: PekoPeko pick N (3)

**d. Your pick would overwrite a picture you kept on purpose. Keep the old one or replace it?**
- contagion: ContagionIkee pick B vs the picture you kept by hand (all 3 facings)
- feverwood: Halquin and Maulith pick B both land on one picture you kept on the other row. Which animal gets it?

**e. Other:**
- gelatinousslime: Bellows and Readerbloom - you picked A but also deleted that picture. Pick another, or redraw?
- leaningscrub: Scurrier - pick B was deleted by you (3 facings). Pick another, or redraw?
- webwork: Cravvet - pick B east was deleted by you. Same question.
- desert: GreatDevourer is marked both "lives at the RSW level" and "Not SW". Which tier?
- miasma: Blixus (north, south, swim) and OpeeSeaKillerJuv (south) redraws failed 3 times. Spec needs a look, not another retry.
- webwork: Plant_TookeTrap_Wild redraw failed 3 times. Same.

Raw per-sheet previews: scratchpad `*_sheet_*.txt` (not kept).
