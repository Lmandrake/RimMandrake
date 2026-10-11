# CANON_MATERIALS_BUILD_1, phase 4 offline pass (L6 trade goods, L9 question), 2026-10-11

Script: `src/RimStarWars/Armoury/prove_canon_materials.py`. Output: `Transient/canon_materials_prove_output_phase4_20261011.txt`.
Tally: PASS 8, PARTIAL 1 (L9, waiting on the owner), OWED 1 (L10), FAIL 0. Nothing deployed and nothing loaded.

## L6: stygium and coaxium defined, trade stock, stygium donor conversion
Correction to the brief: `RSW_Duranium` was already defined (phase 2, `Defs/ThingDefs/RSW_Duranium.xml`). Only stygium and
coaxium were missing.

- **`RSW_Stygium`** (`Defs/ThingDefs/RSW_Stygium.xml`): the description says it is the only thing that can cloak a ship.
  Stats are the donor item's (2980 / 0.2 / stack 25), carried over so the 1:1 conversion moves no value. PROVISIONAL.
  It carries no reward tag; the donor's `RewardStandardLowFreq` would have been a second source.
- **`RSW_Coaxium`** (`Defs/ThingDefs/RSW_Coaxium.xml`): the description carries the canon hazard (kept cold or it explodes).
  The mechanic waits for its consumer (§3.6). MarketValue 60, Mass 0.5, stack 50 are PROVISIONAL. Its art is chemfuel's
  sprite tinted cold blue.
- **Trade** (`Patches/RSW_CanonMaterialsTrade.xml`): each of the six materials gets one `StockGenerator_SingleDef` row in
  `Orbital_Exotic` and in Outer Rim's Czerka orbital trader (Conditional). A negative minimum in `countRange` means the
  material is only sometimes stocked. Decompiled 1.6 confirms how: `RandomCountOf` draws from the range, and
  `TryMakeForStockSingle` returns null for a count of 0 or less. The same row also makes the trader buy the material.
  Counts are PROVISIONAL: metals -20~30, coaxium -10~10, stygium -4~2.
- **The Bazaar** is the trade window, not a stock source. `bazaar_trade_window_design.md` §8 says it never generates or
  patches stock, so whatever the orbital traders carry is its stock. If "Bazaar stock" meant something more (a Bazaar
  settlement, a caravan kind), that is an owner reading and it is not built.
- **Stygium donor conversion** (`Patches/RSW_StygiumConvert.xml`):
  - It strips the `SecondaryMineableYield` extension from `KOTOR_StygiumCrystal`, so a formation already on a map yields
    nothing. The C# null-checks the extension, and the def stays loadable for saves.
  - It removes the formation from every GenStepDef.
  - It points the consumers at `RSW_Stygium`: the two stealth-belt costLists keep their counts 1 and 4 (SetName), and the
    lightsaber hilt part's `requiredComponent` is replaced.
  - It removes `guy762_crystalitem_stygium`.
  - Two edits at source go with it. `RUT_LanternstoneKotorCrystals.xml` has its two Lantern Deeps formation rows deleted,
    because that patch may run after ours. A save alias was added in `RM_MaterialMerges_Aliases.xml`.
  - The save was not checked for the donor item. The alias covers it either way.
- **Decision taken here, reversible:** the stygium formation no longer generates anywhere, including the Lantern Deeps.
  §3.6 says stygium has no local source. Keeping it as a crystal that looks like a source but yields nothing seemed worse
  than removing it.
- **validate_patch** (`Transient/canon_materials_validate_patch_phase4_20261011.txt`):
  - Two ERRORs say the hilt-part and SetName xpaths match 0 nodes. That is the validator not loading those two deployed
    Armoury files.
  - lxml matches both xpaths in the deployed files: 1 hilt part, plus belt costList entries. The 2026-10-11 capture also
    shows `guy762_SWForceLightsabers_CrystalPart_stygium.requiredComponent = guy762_crystalitem_stygium` and
    `guy762_stealthbelt`/`_exchange` costLists naming it.
  - Treat these as a validator blind spot, not dead operations. L10's load is the live proof.

## L9: the conflict, written as one question for the owner
The question is written into the item (`## open question for the owner (L9)`): should the four jobs the 2026-10-09 15:01
card made hard stay required, or remain preferences as the earlier hold says? The item gives the trade-offs of
required, preferences and mixed. Nothing that depends on the answer is built. L9 stays PARTIAL, so `rimflow implemented`
was not run. L10 is still owed.

## Checks added to prove_canon_materials.py
Each check is red on a planted defect in `--selftest`:
- `l6_defs_check`: all six defined, with a label, a description and sellable tradeability. Stygium must say it cloaks
  ships, and coaxium must carry its hazard. The trade-only pair may have no reward tag, leavings or mineable.
  - Planted: a stygium with a stealth-only text and a reward tag.
- `trade_check`: replays the trade patch on orbital fixtures. Each of the 6 materials must be stocked in both traders,
  sometimes empty and sometimes not, and existing stock must be untouched.
  - Planted: an empty patch gives 12 findings.
  - Planted: a stygium row of `1~2` reads as "every visit".
- `sole_source_check`: no src XML outside the def, trade, convert and alias files may name stygium or coaxium.
  - Planted: a coaxium recipe product.
- `stygium_convert_check`: replays the conversion on fixtures shaped like the donor defs. It also checks the Lantern Deeps
  source, the save alias, and a census showing every src file that names the donor stygium is covered.
  - Planted: an empty patch, a Lantern Deeps row, a missing alias, and an uncovered file.
- `replay()` now simulates `PatchOperationSetName`.
