# Mod audit check, group 4 (batches 14-16)

Checker: claude-opus-5.5, 2026-10-10, offline. Rows: `check_group_4.jsonl` (one per mod; amendments live there, the
assessor files are untouched).

## Counts

| batch | mods | AGREE | AMEND | CHALLENGE |
|---|---|---|---|---|
| 14 (third party) | 48 | 39 | 8 | 1 |
| 15 (ours, RM) | 41 | 23 | 18 | 0 |
| 16 (ours, RSW/RUT) | 61 | 48 | 11 | 2 |
| **total** | **150** | **110** | **37** | **3** |

Every facts number the assessors quoted (patched_by, dependants, dependencies, texture proxy, disk, log counts)
was re-compared by script against `facts/mod_facts.jsonl`: **0 numeric mismatches**. The errors are in
interpretation, item lookups, and claims nobody opened the source for.

## Systematic first-pass errors

1. **"No item file found, so treat as unfiled."** Five cited items exist in the ledger without a prose file:
   `FLAME_STATUES_MOD_BUILD_1` (built, L0), `CRYSTAL_INGEST_EXECUTION_1` (done), `EVENT_TRACE_PROPS_LIBRARY_1`
   (doing), `SOLAR_MIRRORS_MOD_DESIGN_1` (superseded by `SOLAR_MIRRORS_BUILD_1`), `WASTELAND_BEDAZZLE_SITTING_1`
   (done). Globbing `items/` is not the ledger; RUBRIC §5.8 says to use `rimflow show`.
2. **Owner cards that are already answered.** Seven needs_owner questions already have a ruling or a standing
   process: VSR Rexamined (ruled retired 2026-09-11), AURAD (forbidden by name in forbidden_mods.md), Alpha Biomes
   scheduling (donor_retirement_plan §3/§5, Q12), explosive growth x10 and planetary crop x4 (owner-ruled design;
   the numbers are tuning), acoustic scanner (the owner picked the banded design by card), and two tier questions
   (Ninefold, SacredGraffiti: NAMING_SCHEME_PLAN rulings).
3. **"Fix mods for absent donors" marked dead without looking at what they carry.** `msedroidfix` and
   `kotorbandoliernorthfix` hold the **only north-facing art** for things we ship (Droidworks' MSE droid; Armoury's
   absorbed bandoliers). Their dependencies are absent, so that art does not load today.
4. **Stale CLAUDE.md north-star claims repeated as fact.** `modcheck status` today: FlowWorks checklist DRAFT
   (not VALIDATED), WreckedMachines RED/DRAFT, and Graffiti not listed.
5. **Shipping status of the 38 absent own mods.** Only 14 are owner-ruled clean-load additions. The other 24 are
   "src mods in neither list", yet several rows treat them as ruled adds. KEEP for those means keep the source;
   whether they ship is undecided.
6. **Grep and attribution artefacts accepted as evidence.** "Stillsand mentions trystan" was the substring
   `entryStandable`. LuminousPigment's "patches kas.strongerscaling / meaningfulparties" edges are shared-defName
   artefacts: every op targets Core. rut.patches was charged severity 3 for 15 `VAEWaste_*` PawnKindDef errors
   that no def of ours can raise.

## The 10 highest-impact corrections

1. **`gravenwitch.vsrexamined` — list regression, not a question.** It was ruled retired 2026-09-11
   (STAT_NORM_WAVE3_RETIRE_1), together with `jellypowered.survivaltools`. Both are back in FULL.LATEST. Drop the
   card and execute the ruling (also check the survivaltools row in its own batch).
2. **`mandrake.rsw.msedroidfix`: ELIMINATE becomes a merge.** Move `MSE_north.png` into Droidworks, then delete.
3. **`mandrake.rsw.kotorbandoliernorthfix`: merge.** Move its 20 north PNGs into Armoury, then delete.
4. **`trouperton.trystantravellersshuttleschematics`: REPLACE-NOW becomes KEEP-TEMPORARILY pending the card.**
   Building our own shuttles contradicts the stated reason (they compete with the gravship). The Stillsand
   evidence was a false match.
5. **`mandrake.rm.gimmesomeslack`: the deploy filter does not exist.** `deploy_custom_mods.py` EXCLUDE_DIRS does
   not exclude `northstar/`, which is why 76 MB of test JSON is in the game's Mods folder. Other mods are likely
   affected.
6. **`mandrake.rut.researchretag`: both config errors are our own defect.** `RR_LateralThinking` and
   `RR_Organization` are declared by us with `researchViewX -2.00`. The 1.6 engine rejects negative coordinates
   (RimSage, `ResearchProjectDef.cs:401`).
7. **`mandrake.rm.pyrinth`: the absorption is done; the list swap was never made.** CRYSTAL_INGEST_EXECUTION_1 is
   done, but `det.epochspyrinth` is still on FULL.LATEST, `mandrake.rm.pyrinth` is not, and biomes still patches
   the donor.
8. **`mandrake.rut.patches`: log severity 3 becomes U.** The VAEWaste errors are unattributed.
9. **`danzinagri.facialanimationcompatabilityproject`: ELIMINATE becomes KEEP-TEMPORARILY.** This makes it
   consistent with `reel.facialanims`. Face changes need his permission, and the face-style card already covers
   it.
10. **`mandrake.rm.ninefold`: the tier is ruled but the split is not done.** The ruling is "RM engine + RUT
    Salvation pack" (2026-09-08), but `God.cs` and the 20 tilt defs still name the Nine inside the RM mod.

Also notable:
- `rustcathedralroaches` is already independent: its verdict becomes KEEP, and the donor edges live in the
  RUT_RustCathedral twin and Doctrine.
- `greentideraidant` still carries the Earth label "giant ant", which THEY_MOD_REPLICATION_1 says must be coined.
- `rut.weathersuite` (the Ash'karr PlanetGeometryDef) is absent while its engine ships.

## Ruling conflicts found

- **Rulings vs FULL.LATEST:** FULL.LATEST contradicts STAT_NORM_WAVE3_RETIRE_1 (two retired mods are back) and
  CRYSTAL_INGEST_EXECUTION_1 (the donor is still listed, the replacement is not).
- **Warcasket vs the sea floor:** the Warcasket ruling (2026-09-28) says "alternative to ... ocean access", but
  the 2026-09-26 sea-floor ruling is "ship or nothing". The card stands.
- **Vehicles:** the V2_DREAMS §0b vehicle-raid test ("drop the frameworks") and §0c (the Neolithic cart reskin in
  progress) both hinge on `smashphil.vehicleframework`. Ask them as one card.
- **Ancient Urban Ruins:** forbidden_mods.md (keep Hit Point, forbid AURAD) vs ANCIENT_RUINS_MOD_AUDIT_1 (cut the
  family). They agree on AURAD and conflict only on AURVL and the base mod. Note that AURVL declares AURAD as a
  hard dependency.
- **CLAUDE.md north-star section is stale:** FlowWorks is listed VALIDATED there, but DRAFT is measured today.

## Not checked (stated, not guessed)

- Placed Things in the campaign save, for any ELIMINATE (UNMEASURED throughout).
- Graffiti north-star hash.
- The ledger state of WEBWORK_EGG_BLACKMARKET_BUILD_1 and STATUE_ART_EXPANSION_1.
- The Bazaar memory ruling text.
