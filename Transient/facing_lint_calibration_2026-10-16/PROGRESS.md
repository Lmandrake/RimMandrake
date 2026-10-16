# Facing-lint calibration (ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL) - 2026-10-16
All counts MEASURED by `python3 src/RimMandrake/Utils/art/facing_scale_lint.py calibrate | lint --repo` (outputs here: before_roster.*, after_roster.*, calibration_before/after.json, scoped_counts.txt).

## 1. Lint as found (commit 3791e139ea)
- Roster (all mandrake pictures, repo copies): 1006 pictures, 470 FLAG / 251 ok / 285 UNMEASURED = 65.2% of measured flagged. Item scope (Baroque + SWBestiary): 458 FLAG of 701 measured (65.3%).
- Vanilla: bands were vanilla p2.5..p97.5 of the depth-model ratio, so vanilla flagged ~5% PER FACING, but ELEVATION art (our ground-camera art) was judged against the vanilla INTER-QUARTILE range re-centred on 1: ~50% of any population by construction. Plan-blind (one band for fish, snake, bird, quadruped), and the feet test (viewpoint) misread legless/splayed bodies.

## 2. Vanilla + DLC corpus (base game, ludeon.* AssetBundle extract, resources.assets)
127 animals with all three facings (Core + Royalty/Ideology/Biotech/Odyssey; Swimming_* poses and dessicated excluded). Body plan from the PawnKindDef's race BodyDef parts (src/RimMandrake/Utils/art/facing_body_plan.py; the vanilla kind->texture link is read from the game's own Data/*/Defs XML because the DefDump is post-patch, e.g. Rat is retextured FancyRat).
Plan census: quadruped 87, flyer/bird 23, insect 8, lowslung(lizard/turtle) 5, biped 2, serpent 1, blob 1, fish 0.
LIMIT: vanilla has NO fish, one serpent, one blob, two bipeds; plans with n<8 borrow the all-vanilla band. Fish/serpent/blob are therefore not independently calibrated (only 'all vanilla').

## 3. Thresholds
Per-plan band = vanilla's observed ENVELOPE (min..max of S/N height over the depth model) widened by 2%. Percentile tails cannot reach 5%: 2.5% tails flag 22/127 (17%) of vanilla itself, 0.25% tails 10/127 (7.9%), because each animal has four ratios with their own extremes.
Selection by leave-one-out (each vanilla animal judged against the envelope of the others): margin 0% -> 7.9%, 2% -> 4.7% (chosen). In-sample 0%.
Elevation (ground-camera) art: same plan band re-centred on the plan median (expected ratio 1). Viewpoint: plans quadruped/biped/flyer keep the 2+ feet test; fish/serpent/blob/lowslung/insect are elevation by convention for mandrake.* art (the feet test misreads them).
Bands (d_south / d_north): quadruped 0.63-1.33 / 0.64-1.23; flyer 0.71-1.31 / 0.85-1.22; insect 0.67-1.17 / 0.63-1.15; all-vanilla 0.63-1.50 / 0.54-1.42.

## 4. Roster after (repo copies)
All: 349 FLAG / 372 ok / 285 UNMEASURED (48.4% of measured; was 65.2%). Item scope: 336 FLAG of 701 (47.9%; was 458, 65.3%).
New field beyond_vanilla: FLAG that is also too big against vanilla's own top-down envelope for its plan = 76 pictures (71 in item scope). The other ~270 are over the owner's ground-camera standard (S/N = E height) but inside what vanilla ships.
By plan (measured): quadruped 151 FLAG/140 ok (32 beyond vanilla); insect 84/78 (33); serpent 55/35 (4); lowslung 35/30 (3); flyer 12/50 (2); biped 6/33 (2); fish 5/0; blob 1/6.
KEY FINDING: 99% of flagged facings are S/N TOO BIG (the owner's complaint, real), yet vanilla's own raw S/E height ratio is median 1.30 (S) / 1.40 (N) for quadrupeds; our roster's quadruped median is 1.23 / 1.26 - LOWER than vanilla. So the rest of the 48% is a standards question, not a lint bug: "ground-camera S/N = E" is the owner's standard; vanilla itself does not meet it. Calibrating to vanilla cannot both pass vanilla and flag the owner-approved cases (see 5).

## 5. Known positives (OLD art = 3791e139ea^ S/N + unchanged east; fixtures src/RimMandrake/Utils/art/fixtures/facing_known_positives/)
- FireWasp (insect): old S/N 1.65 -> FLAG both; new 0.99 -> pass.
- Anooba male (quadruped): old S 1.57 / N 1.50 -> FLAG both; new pass.
- Furnace beast (quadruped): old S 1.29 / N 1.26 -> FLAG on NORTH only (S 1.295 is inside the quadruped band 1.35 once re-centred); new pass. The Furnace SOUTH is the one case the calibrated lint no longer flags.
- Counter-check: judged as pure vanilla top-down (no ground-camera standard), FireWasp old is NOT flagged and the fixed FireWasp is flagged too small - which is why the ground-camera standard is kept for our art.

## 6. Selftest / commits
selftest_facing_scale_lint.py: 37 PASS 0 FAIL (adds calibration rate, plan populations, 12 body-plan rules, real-race classification, 3 known positives).
