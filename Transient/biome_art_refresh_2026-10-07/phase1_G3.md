# Phase 1 G3

## greysea_sheet_2026-10-05
Leads: 6 keep_not_live (all "kept variant" columns) + 1 redo_done. Method: sha lookup in the art ledger (purged / PROTECTED / in art store), def graphicClass from Defs XML. Every lead is a kept *variant* (extra column), not the picked column; the picked columns for all rows are live.

| row / lead | class | evidence |
|---|---|---|
| RM_Hessal variant B (3 facings) | EXECUTED | His same decision (`redo`) lists B's three shas in `purge`; ledger shows all three PURGED. Redo `greysea_hessal_redo_v2_{east,south,north}` is done and installed 2026-10-07 (live east 4734cb7e6327, north fc44b1eebd04, south 8b8abf76fc7f, ruling-protected). |
| RM_Hessal redo_done | EXECUTED | Same job set as above; `art.py variants RM_Hessal` shows install:2026-10-07 from the artpipe v2 outputs. |
| RM_HessalCatch variant B (single 547bd7f30ce8) | UNEXECUTED-MECHANICAL (optional; def has no variant slot today) | Kept (ruling `69700bf8b9073c15df5a`, PROTECTED, bytes in art store) but not installed: def `RM_HessalCatch` in `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_GreySeaCatch.xml` is `Graphic_Single` texPath `Things/Item/RM_GreySea/RM_HessalCatch`. Precedent for item variants: Scald `RM_BladderboilCatch` is a Graphic_Random folder (`_a.._d.png`). See wiring recipe below. Live pick D (8b9a2497323a) is correct. |
| RM_NissikCatch variant B | EXECUTED | B sha 16bfec8bf02f is in his own `purge` list for the row and is PURGED in the ledger (kept then purged in the same decision). Pick C is live (60568da65d17). |
| RM_Sorruth variant B (east, south) | EXECUTED | Decision is `hold` + "cut don't need"; B shas PURGED; close progress section 3: `<RM_Sorruth>` removed from RM_GreySea wildAnimals, def left cast nowhere. |
| RM_SorruthCatch variant B | EXECUTED | Same: `hold`/cut, shas PURGED, `<RM_SorruthCatch>` removed from fishTypes. |
| RM_SorruthCatch variant C | EXECUTED | sha 17d18ad7721b PURGED (in row's purge list); row cut. |

Wiring recipe for RM_HessalCatch B (only if he wants the variant visible in game; none of it was run here). No `retire` verb exists in art.py, so use a new sibling folder and leave the flat file unread (the ElderSando precedent in the Scald close):
1. In `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_GreySeaCatch.xml` set RM_HessalCatch graphicData to `Graphic_Random`, `<texPath>Things/Item/RM_GreySea/RM_HessalCatch_v</texPath>`.
2. `python3 src/RimMandrake/Utils/art/art.py install src/RimMandrake/TerminalBiomes Things/Item/RM_GreySea/RM_HessalCatch_v/RM_HessalCatch_a.png 8b9a2497323a8f4cabaed3c07893cc3903390ce77632332f1489b7a13be70f5b --ruling <id of his D keep on RM_HessalCatch; find in art.py status RM_HessalCatch>`
3. `python3 src/RimMandrake/Utils/art/art.py install src/RimMandrake/TerminalBiomes Things/Item/RM_GreySea/RM_HessalCatch_v/RM_HessalCatch_b.png 547bd7f30ce8549f7da3c9d98c6129f7d98dbe7d82affeaa9f6dfe2880c9ba54 --ruling 69700bf8b9073c15df5a`
4. placeholder_detect + resolver check over the new folder. (Mod arg form: the ledger's live key is `src/RimMandrake/TerminalBiomes`; if install rejects it, try bare `TerminalBiomes`; `--dry-run` first.)
Optional polish; the creature and catch rows themselves are done.

## thechill_sheet_2026-10-05
Leads: 1 keep_not_live.

| row / lead | class | evidence |
|---|---|---|
| RM_Oovanam variant B (east/north/south) | EXECUTED | Kept as variant, then purged: B shas 5ea9060ecb91 / 673f71514662 / c52f12d551a7 all PURGED in the ledger and gone from the art store; pick C installed (close progress: "he kept B as a variant, then purged B's shas on the catch row; B is gone, C installed"). `RM_Oovanam` is Graphic_Single in `RM_TheChillFauna.xml` so there was no variant slot anyway. |


## twilightsea_sheet_2026-10-05
Leads: 18 keep_not_live (all variant columns, one `_byname`), 3 redo_done, 1 redo_nojob, 7 purge_on_disk shas. Picked columns are all live (the audit's keep_not_live list holds no pick). General finding: every kept creature variant is a ledger PROTECTION only; the creature defs (`RM_TwilightSeaFloorLife.xml`) are `Graphic_Multi` (one body graphic per facing), which has no random/variant slot, so no install path exists or is needed. Variant A on these rows is the previous in-game picture (labelled IN GAME), now replaced by pick B; its bytes are held in the art store, PROTECTED.

| row / lead | class | evidence |
|---|---|---|
| RM_Aluun variant C (v2) | EXECUTED | Pick B installed (live east bcd9d78558e3); C = 8bee7d9d3474/341334f0c670/5f2802b2959d, keep ruling `9e9e89dd4a7ce7e43ab9`, PROTECTED, in store. Def is Graphic_Multi: no slot. |
| RM_AluunCatch variant D (v2, east 8bee7d9d3474...) | UNEXECUTED-MECHANICAL (optional; item has no variant slot today) | Keep ruling `77d6e41534d317ab951e`, PROTECTED, not installed. `RM_AluunCatch` in `ThingDefs_Items/RUT_TwilightFish_Niim.xml` is Graphic_Single `Things/Item/RM_TwilightSea/RM_AluunCatch`. Recipe: set `Graphic_Random` + texPath `Things/Item/RM_TwilightSea/RM_AluunCatch_v`; `art.py install src/RimMandrake/TerminalBiomes Things/Item/RM_TwilightSea/RM_AluunCatch_v/RM_AluunCatch_a.png bcd9d78558e398a9b3fb6b72a3418a7b40c4f86e6ffc437188b58e15afd93f62 --ruling <his C keep id from art.py status RM_AluunCatch>` then the same with `RM_AluunCatch_b.png 8bee7d9d34749900b7d6830a927e2e2fa300133945824c0b90362813b9263e7c --ruling 77d6e41534d317ab951e`. Flat file stays unread. |
| RM_Kellu variants A, D | EXECUTED | Pick B live; A = previous in-game and D = history, shas d72c5ee8ae13/df5297877277/a9fe5f6b95b6 (+ single 58c185999691) PROTECTED in store; Graphic_Multi, no slot. |
| RM_Liiru variants A, D | EXECUTED | Same shape: shas b2189d737d1f/7f16b5f654fe/49a3c188292b (+ single bd35e352fc18) PROTECTED; no slot. |
| RM_Nuudal variant C | EXECUTED | Only sha 9ad77b19928c (single), and it is in his own `purge` list: PURGED. |
| RM_Nuudal variant D | EXECUTED | east/north/south 2efb4de65c84/0bb78436b4b2/292ac98987cf are PROTECTED and already live in 2 locations (D shares bytes with in-game files); its single 9ad77b19928c is PURGED per his purge list. |
| RM_Oobo variants A, D | EXECUTED | 262c39558da9/3e0c0d12f90f/e79e85090b4e PROTECTED in store; D's single accd71f021bb PURGED per his purge. No slot. |
| RM_Oobo variant C | EXECUTED | Only sha accd71f021bb, PURGED per his purge list. |
| RM_Pallu variants A, D | EXECUTED | 40237eec51a4/cbd2dfec048d/1929d1e09d08 PROTECTED; single 40b271f052c5 PURGED per his purge. |
| RM_Pallu variant C | EXECUTED | Only sha 40b271f052c5, PURGED. |
| RM_Tikkarr variants A, D | EXECUTED | f8d8ded8cce1/5547d51276b8/bf87dd55ac3a PROTECTED; D's single 420df41324d7 PURGED per his purge. |
| RM_NoothelmPlant `_byname` B and variant B (sha 610a8fe01edf) | EXECUTED | His words: "keep art (b) for a new plant in the Sump". Held PROTECTED in store (rulings `2095e8741b30ec14e32b`, `88e7721f74a0a52c9677`) and filed as item `TWILIGHT_ART_REUSE_ELSEWHERE_1` item 4 (waits for the Sump sitting). Not a variant of this def, so no slot is expected. |
| RM_NoothelmPlant redo (audit said no job) | UNEXECUTED-MECHANICAL (job exists and is done) | Audit false positive: job id is `twilightsea_noothelm_redo_v1_south`, in artpipe `done/`, output sha 73002ab0d5511deb5a87df52fb311fba13e80cc621a5188cf12290a63452216d, registered and in the store, not yet installed. Live texPath is the shared vanilla `Things/Plant/Echeveria/EcheveriaA` (also used by 4 other defs: never overwrite it). Steps: (1) in `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TwilightLightPlants.xml` change RM_NoothelmPlant `<texPath>` (graphicClass already Graphic_Random) to `Things/Plant/RM_TwilightSea/RM_NoothelmPlant`; (2) `python3 src/RimMandrake/Utils/art/art.py install src/RimMandrake/TerminalBiomes Things/Plant/RM_TwilightSea/RM_NoothelmPlant/RM_NoothelmPlant_A.png 73002ab0d5511deb5a87df52fb311fba13e80cc621a5188cf12290a63452216d --reason artpipe-collect` (path pattern copied from Hoolimbre). |
| RM_Lunoowa redo_done (3 facings done) + purge_on_disk (4 shas) | NEEDS-OWNER | Redo job `twilightsea_lunoowa_redo_v1_{east,north,south}` is done (shas c92efefcfb63be2cd2644bcb18c4c1cab669d54df57846c973fff4b6ad8bcaae / d7fb2fa999542fbac62c11142f3aca90ab9a2ebb3be04fd6bb423ac7777322a3 / c7f6499aa29d5678ec601b82df69d9e7a799d582065bf4df3db01c6f36bb4dc2) but not installed, and the live files are the very bytes he both purged and kept: his decision purges e9546fb2d655/7e4dcc9b12fd/077c92d255c5 (and 92592a786b3e, the flat placeholder live only as the cut `RM_Sorruth.png`) while ALSO listing variant C, whose east/north/south are those same bytes. So the live files are PROTECTED and a mechanical install is refused. Ask: does the redo replace them (purge wins)? If yes: art.py install of the three redo shas over `Things/Pawn/Animal/RM_Lunoowa/RM_Lunoowa_{east,north,south}.png` using his verbatim typed Lunoowa note as the authorization, then `art.py purge <sha> --release-keep` for the three Lunoowa shas; 92592a786b3e will still refuse while `RM_Sorruth.png` is live (art.py has no retire verb). |
| RM_Hollu purge_on_disk (3 shas aa3ee7b59ba2, 38823bb69505, 6c9626f9fbc6) | UNEXECUTED-MECHANICAL | Progress file: "Hollu keeps its old A art until the waveglass redo lands (purge refused as live)". Redo `twilightsea_hollu_redo_v3_{east,north,south}` is now done and in the store; live Hollu files are NOT protected. Pick B was executed (Dancing Skresh created from B). Commands (mod `src/RimMandrake/TerminalBiomes`, rel prefix `Things/Pawn/Animal/RM_Hollu/`): install `RM_Hollu_east.png daee5fdf09f2a30e991182aa57820809e333a13194b9663ce807f1980762148f`, `RM_Hollu_north.png 67eb266a15d740927796c088181e951cb081b2684fbdcf9f72263842408f2c08`, `RM_Hollu_south.png cc35fe627cff773128ce069c8b5ed06d454e66b8f48e7b6dd76af39e526323df`, each with `--reason artpipe-collect`; then `art.py purge <full sha> --release-keep` (with his verbatim Hollu note as authorization) for aa3ee7b59ba2a46649d550d9de6270e2db113674dde93e147158050fcb540027, 38823bb69505fa9ddfd8e27ea4fb1c5d580723d81cc442a21729129354cea015, 6c9626f9fbc6dc4d4bb510223060a494cc61c4198c4548bfe8d1f6f4b06d593e. Unreviewed render (same as the Hessal v2 precedent); then re-run `sea_shadows.py apply`. |
| RSW_Faa redo_done | NEEDS-OWNER | Redo `twilightsea_faa_canon_redo_v1_{east,north,south}` done (east de4e3175..., north 574b6f62..., south 62620106...), no west facing generated; live SWBestiary Faa files are PROTECTED (variant A kept, and the old bytes are owed to the new "Scaa Lumsigh" fishable per `TWILIGHT_ART_REUSE_ELSEWHERE_1` item 1, which says install the old bytes at the new texPath BEFORE overwriting). Not mechanical: needs the Lumsigh def first and his selection of the new render. |
| RSW_Mee redo_done | NEEDS-OWNER | Only east passed; `twilightsea_mee_canon_redo_v1_north` and `_south` are in artpipe `failed/` (canon check FAIL 3/4 after one corrected retry; output PNGs exist in `_artsrc`). Live SWBestiary Mee is PROTECTED and the old bytes are owed to a new Greentide river fishable (item 2). He must choose: accept the failed-canon north/south or regen. No regen proposed: finished (if failed-check) art exists. |

Note (not a lead): `RM_HolluCatch` is an agentInference row (not his ruling); its redo `twilightsea_hollucatch_redo_v1_east` is done (7e2f9be59fef173cb24d629557f70b2e03277eb038dd5d4c5160f1a2056447f2) and the catch still draws vanilla `JadePlantB`.


## thescald_sheet_2026-10-05
Leads: 0 keep_not_live, 2 redo_done, 1 redo_nojob. All three are false positives; every Scald redo is executed.

| row / lead | class | evidence |
|---|---|---|
| RM_Crowncarpet redo_done | EXECUTED | Jobs `scald3_crowncarpet_{a,b,c}` finished and are live as `src/RimMandrake/LuminousPigment/Textures/Things/Plant/RM_Crowncarpet/RM_Crowncarpet_{a,b,c}.png` (shas e78c1ebf58d5/87945bb8d369/f2223e7c768c, ledger live). All 6 of his purge shas are PURGED. Def is Graphic_Random on `Things/Plant/RM_Crowncarpet` (mod is LuminousPigment, so `art.py variants RM_Crowncarpet` shows no TerminalBiomes live, which is why the audit saw no install). |
| RSW_SandoAquaMonster redo_done | EXECUTED | Redo outputs are live in SWBestiary: east 0f492d4f0603, north e38a8d815a79, south c82bbf707bfa are byte-identical to the `scald3_sandoaquamonster_*` outputs; west 395a0d6f6bfd derived (mirror) 2026-10-07. His other request (move out of the Scald to the Twilight Sea) is done per the close progress (cut from RUT_TheScald, cast in RM_TwilightSea 0.03). |
| RM_Thuum redo_nojob | EXECUTED | Audit false positive (job-id mismatch). `scald3_shimmereel_*` failed, `scald4_shimmereel_{east,north,south}` is in `done/` and installed 2026-10-07 (live f36a956233bd / 1ca1f36e13f2 / 0804febcebf0, artpipe provenance); his purge shas acaf7b136ce5 and 24b0cc141fd6 are PURGED. Rename to "shimmer eel" done (progress file). |


## Summary

| sheet | leads | executed | unexecuted-mechanical | needs-owner | proposed-regen |
|---|---|---|---|---|---|
| greysea | 7 | 6 | 1 (HessalCatch B, optional variant) | 0 | 0 |
| thechill | 1 | 1 | 0 | 0 | 0 |
| twilightsea | 23 | 17 | 3 (AluunCatch D optional variant; Noothelm redo install + texPath; Hollu redo install + purge) | 3 (Lunoowa keep-vs-purge conflict; Faa; Mee failed canon north/south) | 0 |
| thescald | 3 | 3 | 0 | 0 | 0 |

Notes: (a) Lead counts treat Lunoowa's redo and its purge_on_disk shas as one lead and count Hollu once. (b) No regen proposed anywhere: every redo subject already has finished art in artpipe `done/` (Mee north/south are in `failed/` on a canon-check score but PNGs exist). (c) Variant keeps on creatures are not installable by design (Graphic_Multi/Single has no variant slot); only item/plant defs can take a Graphic_Random folder. (d) Nothing was run that writes; all commands above are proposals. Hollu and Noothelm installs are unreviewed renders (Hessal v2 precedent). (e) The `artpipe_state.py find` command exceeded 120 s and was not used; artpipe state was read directly from `D:\Luke\dev\_artpipe\done|failed|_artsrc`.
