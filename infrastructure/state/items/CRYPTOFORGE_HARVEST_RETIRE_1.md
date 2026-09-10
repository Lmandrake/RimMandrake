## spec
Owner-said: "Retire-after-harvest." Harvest then retire VQE Cryptoforge:
(1) reproduce the 18 SALVAGE_PALETTE-cited props as owned RUT_/RSW_
ThingDefs with OWNED art (citation swap — Workshop art is not ours to
ship); (2) copy the 38 KCSG StructureLayoutDef XMLs into design/ as
authoring reference, strip to owned symbols before any shipping use; (3)
delete our two FindMod-gated patches (Armoury_RangedDamage.xml VQE bullet
block, MegafaunaYield.xml VQE_Megamidge block) in the same change as
removal; (4) remove from ModsConfig, cold-load check, resave canonical per
the donor-retire pattern; (5) fauna sheets: IceCrawler/Megamidge ruled
out-of-canon, coordinate with the owner's live review before applying.
BENCH note (same day): the campaign save's own `GameComponent_QuestChains`
already schedules `VQE_Cryptoforge_Chapter1` at tick 1800000 (~day 30) —
step 4's resave must also confirm no VQE_ entry survives in `futureQuests`.

## done this session — steps 2 and 3
- **Step 3**: both FindMod-gated patches removed. `Armoury_RangedDamage.xml`
  — the whole `PatchOperationFindMod` block gated on "Vanilla Quests
  Expanded - Cryptoforge" (2 bullet-damage `PatchOperationReplace`s for
  `VQE_AncientShieldedTurret_Bullet`/`VQE_AncientSpacerAutocannon_Bullet`).
  `MegafaunaYield.xml` — the `VQE_Megamidge` MeatAmount/BoneAmount blocks;
  removing them left their `PatchOperationFindMod` group empty, so the
  whole now-empty group was removed too rather than left as a shell.
  `validate_patch.py`: 0 errors on both files.
- **Step 2**: the actual count is exactly 38 `KCSG.StructureLayoutDef`
  entries across 11 `CryptoforgeMaps_*.xml` files (not 38 files — verified
  by counting `<KCSG.StructureLayoutDef>` tags, not assumed), found under
  the donor's `Defs/CustomGenDefs/{Cryptoforge,Cryptoforge_Bow,
  Cryptoforge_Stern,ScanningBase}/`. Copied verbatim (plus
  `CryptoforgeSettlementLayout.xml`, the wiring file, for context — 12
  files, 808K total) to
  `design/Jawa/worldbuilding/donor_harvest/cryptoforge_kcsg/`, with a
  README stating plainly they are grid-grammar reference only, not
  shippable until every cell's third-party SymbolDef is stripped/repointed
  (same pattern as `gen_vault_layouts.py`'s existing wrapper symbols).

## NOT done, and why — steps 1, 4, 5 need their own passes
- **Step 1 (18 owned-art props)** is a real content-authoring task, not a
  mechanical cut — each of the 18 SALVAGE_PALETTE-cited Cryptoforge props
  needs a correctly-sized, validated, RimWorld-styled sprite (the
  `generating-rimworld-sprites` skill's whole workflow), not a quick
  reskin. Rushing 18 pieces in the tail of an unrelated belt session risks
  shipping placeholder-quality art. ⚠️ Note for whoever picks this up: the
  palette table under "Vanilla Quests Expanded - Cryptoforge" actually
  lists **22** unique defNames in `SALVAGE_PALETTE.md`, not 18 — some are
  almost certainly state-variant pairs sharing one piece of art (e.g.
  `AncientShieldedTurret`/`BustedShieldedTurret`,
  `AncientAirlock`/`ForcedAncientAirlock`/`JammedAncientAirlock`) rather
  than 22 separate sprites, which is probably where "18" came from — but
  that needs confirming against the donor's own texPaths before assuming
  it, not guessing from the name pattern.
- **Step 4 (ModsConfig removal, cold-load check, canonical resave)**
  needs a real restart. Held back this session for the same reason as
  `RUT_SCAVENGEREVENTS_BUILD_1` and `BOOM_FAMILY_CUT_1` — the owner was
  mid-session on the live campaign map throughout, and a cold load would
  have pulled the game out from under him. The `futureQuests`
  `VQE_Cryptoforge_Chapter1` check BENCH flagged is folded into this step,
  not done separately.
- **Step 5 (IceCrawler/Megamidge fauna-sheet ruling)** explicitly needs the
  owner's live review per the item's own text — not applied.

## verify
Steps 2/3: `validate_patch.py` 0 errors (done); reference copy exists and
is documented (done). Steps 1/4/5: not started.
