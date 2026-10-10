# The Rot sheet: independent verification, 2026-10-10

This was a read-only check. Nothing was fixed or deployed. It covers commits 7b75022a2 and cfc102d2d, and b006a3f43 (RM_TollukCap, 02:03, before the sheet was ruled). They were checked against `Transient/biome_ffar/therot_sheet_2026-10-05.decisions.json` and the snapshot he ruled on (`infrastructure/state/art/sheets/therot_sheet_2026-10-05.snapshot.json`, id cf064b3a064be0fd).

**Method.** Every candidate sha was looked up byte-for-byte in two places: every PNG under `src/`, and the deployed `Mods/RimMandrake.Biomes`, `UtinniPatches` and `MandrakePatches`. Every PNG in each plant's Graphic_Random folder was then also compared by decoded pixels against every sheet candidate. Byte checks alone miss re-encoded copies, and that is how the Brightbell failure below hides. Art jobs were read from `D:\Luke\dev\_artpipe` (pending, active, done, failed and _withdrawn). Descriptions and labels were compared per def between `7b75022a2^` and `7b75022a2`. Game drift was taken from `deploy_custom_mods.py --compose biomes` as a plan only (log: `~/.seat-tmp/BENCH/rot_verify_compose_dry.log`).

**Totals.** 57 rows. 14 have no `at` and were never clicked: the 13 named in the progress file plus RSW_ShiroTrap, which carries prefill sub-picks only. That leaves 43 ruled rows: **PASS 23, FAIL 5, OPEN 15** (genuine owner questions).

## FAIL

| row | he asked | what exists | path |
|---|---|---|---|
| RM_Brightbell | pick C, ✕ B (465c0328) | **His ✕'d B is live**, re-encoded: `Brightbell_p3a.png` is pixel-identical to rot_brightbell_v3a (465c0328), mean diff 0.0. The byte-sha audit cannot see it. It is in both src and the game copy. The game also still has the retired cartoons `Brightbell_B.png`/`Brightbell_C.png`. | `src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/Brightbell/Brightbell_p3a.png` |
| RM_VioletWimple | variants of his pick (prefill A) | `rotvar_violetwimple_a_v1`/`_b_v1` use A (cf994f6d = `BMT_VioletWimpleA`) as reference. That cartoon was retired by owner card 2026-10-09 (1eab83286) and exists only as a stale game file that `--prune` will delete. The live folder holds D/B/C (`VioletWimple_A`, `_p3a`, `_p3b`). | `D:\Luke\dev\_artpipe\pending\rotvar_violetwimple_*.json` |
| RM_Wrinklecap | same | `rotvar_wrinklecap_a/b_v1` use A (e3b8c484 = `Wrinkle1.png`) as reference. It was retired on 10-09 and survives only in the game copy. | `D:\Luke\dev\_artpipe\pending\rotvar_wrinklecap_*.json` |
| RM_Pusmelon | pick B only | B is installed as `Pusmelon_A.png`. **`BMT_PusmelonB.png`, a picture never shown on the sheet, still draws** in src and the game. The un-picked A, `BMT_PusmelonA`, still draws in the game until a prune. | `src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/Pusmelon/` |
| RM_Sagecrust | pick C only | C is installed as `Sagecrust_A.png`. **`BMT_SagecrustB.png`, never shown on the sheet, still draws.** The un-picked A, `BMT_SagecrustA`, is in the game until a prune. | `src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/Sagecrust/` |

## PASS (23)

Agaripod (B is in the fold slot, and `Agaripod_ArtFold.xml` rebinds the donor texPath to it; gromma kept, new description) · AnimaColossus (see notes) · MycoidColossus · AgariluxPrime (grath elder kept, description rewritten around its danger) · Bryolux (2 jobs, description untouched as asked) · AgelessCap (A+B) · Arpeau (A/B/C live; ✕'d D/E absent) · BlastpodShroom · Brogg (all four `alternateGraphics` tints removed from RM_Brogg; new description) · EuphoricCrown (B) · FalseFruit (B) · FlakespireFungus · FruitingBodies (jobs only, description untouched) · GreyLady (B) · Hwelgrue · Illoth (✕ B absent) · Nuitae (A+B+C; ✕ D/E absent) · PaleTree · RegenerantVeil (A+C; ✕ B absent) · Shinecap (A-E) · Skulltop · RM_Thozzik (✕ B bytes are absent from src and game; only the ledger purge is outstanding) · Snoruuk (v1 done, v2 pending; references are donor A south plus the canon jpg, never ✕'d art).

Every row he asked for a description on was rewritten: 31 rows, with the AB_Agarilux row written onto RM_TollukCap. No description was changed outside what he asked for. The 24 "two variants" rows each have exactly 2 jobs (48). Except for the two FAILs above, each job uses his pick or prefill as reference, and none uses a purged picture.

## Notes on specific rows

- **AA_AnimaColossus.** The label `pluur'va` is exact. "Tripple the cell length" was done as drawSize ×3 on the three `bodyGraphicData` stages (4/5/6 → 12/15/18). That reading is plausible: the same file sizes other Rot giants by drawSize ("vorrugath (15 wide)"), and bodySize is untouched. But `dessicatedBodyGraphicData` drawSize is still 4/5/6, so the corpse will draw at a third of the size. "Regenerate the name" was read as regenerating the description. The south job is done; the east and north jobs were withdrawn. The south job uses B east/north as reference. B was only default-ticked as a variant, not explicitly kept by him, but he did not ✕ it.
- **AA_AngelMoth (OPEN).** The letter is prefill only. He ✕'d B south, so "otherwise accept" means accepting B east/north. Pending job `rotrow_angelmoth_south_v1_south` uses B east/north as reference, which is correct. B east/north are not installed yet; the def still draws the donor art. The rename is still owed.

## Stale files in the game copy: confirmed 22, all under `Mods\RimMandrake.Biomes\Biomes\TheRot\Textures\RotSporeKit\Things\Plant\`

ArpeauGreen_A/B · BMT_BleedingToothA/B · Brightbell_B/C · CavernalMorel_A/B · BMT_PusmelonA · BMT_SagecrustA · BMT_SeadewA-D · ShinecapImmature_a/b · BMT_VioletWimpleA/B · Wrinkle1-4.

Besides these, the deployed TheRot matches the repo (no `~`/`+` lines). UtinniPatches `RUT_TheRot.xml` has no drift. The 5 `~` lines in the plan are WeepingStones, not this sheet. The game ran during the deploy, so it needs a restart to see any of this.

⚠️ For two never-clicked rows, the prefill "A IN GAME" is one of these stale files: BleedingTooth A = `BMT_BleedingToothA` and Dewshrooms A = `BMT_SeadewA`. Pruning removes his prefill picture. That is consistent with the 10-09 retirement card, but he has not ruled either row.

## Scope concerns

1. **Duplicate installs.** The `_p3a`/`_p3b` files from baea6351b (01:00, before the sheet) are pixel-identical to the sheet's v3a/v3b candidates. Installing those same pictures again under new names doubled their Graphic_Random weight against his pick: Arpeau B/C, Nuitae B/C, Shinecap b/c/d/e, Brightbell C, MortalMorel B. MortalMorel_p3b, which is his default-ticked C, is also live.
2. **Pictures never shown on the sheet still draw beside his picks.** CrimsonCap_b-f, BoomshroomGrown_B/C, Flakespirefungus_b, FruitingBodyA-C, plus the Pusmelon and Sagecrust FAILs above. The sheet showed "1 of N random variants" and only one column. This predates the enact.
3. **Variant-job grading defect.** The whole owner note goes into each job's canon grader, so a single render gets graded against "make two other variants" and against "rename". `rotvar_ab_giantagarilux_b_v1` FAILED for exactly that reason (`failed/` manifest). 30 more such jobs are pending or active and are exposed to the same failure.
4. Nothing on the roster was cut and none was asked for. The roster and UtinniPatches diffs are comment-only.

## Owner questions: confirmed genuine

- **14 renames.** AngelMoth, AgaricusDomeCap, Agarilux/TollukCap, ArbuscularMycorrhiza, DribblingCap, GiantAgarilux, GlowingAgarilux, Glowstool, LilacBeacon, SlimyPholiota, WitchesOyster, CrimsonCap, MortalMorelPlant, Pusmelon. No note supplies a name, so none is a missed application. But each note is an imperative ("Rename", "Redo name", "Improve name"), not a question. "No coined names" was a BENCH brief, not his ruling, so all 14 renames are simply undone. These questions also exist only in the ledger and the progress file, not in CONFLICTS.
- **Thozzik.** ThozzikQueen and ThozzikSpawned ("Redundant?") are genuinely his questions. The RM_Thozzik ✕ "conflict" is not: what keeps B alive is ThozzikSpawned's `variantsDefault` tick, which is the machine's, not his. His explicit ✕ should win, and B is already off disk anyway.
- The 13 never-clicked rows are untouched by today's commits, both defs and textures.
