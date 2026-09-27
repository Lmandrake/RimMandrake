## spec
Owner-said: "Retire-after-harvest." Harvest then retire VQE Cryptoforge:
(1) reproduce the SALVAGE_PALETTE-cited props (the original filing said 18;
a 2026-09-26 pass said 21; **re-verified 2026-09-26 (later same day) at
22** unique defNames tagged "Vanilla Quests Expanded - Cryptoforge" in
`SALVAGE_PALETTE.md`, each needing its own sprite — see the item's own
note below) as owned RUT_/RSW_
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

## NOT done, and why — steps 1, 4 need their own passes; step 5 is now DONE

- **Step 5 (IceCrawler/Megamidge fauna-sheet ruling) — DONE, verified against
  the live decisions record, FOUNDRY 2026-09-26.** The prior session's "needs
  the owner's live review" was already stale the day it was written: both
  rows were ruled at the "homeless disposition sitting," frozen 2026-09-10
  (same day this item was filed) —
  `design/Jawa/worldbuilding/review/round2/decisions_propagated.json` (the
  LIVE register per `creature-art-register-retired-2026-09-11`) carries
  `homeless:VQE_IceCrawler` and `homeless:VQE_Megamidge` both
  `"decision": "out"`, note `"CUT at the disposition sitting (homeless
  disposition sitting, frozen 2026-09-10)"`; the raw
  `homeless_disposition_register.decisions.json` agrees (`"decision":
  "cut"` for both). **"Applying" it needed no further edit**: `grep -rl
  "VQE_IceCrawler\|VQE_Megamidge" src/` returns nothing — the only live
  reference was the `MegafaunaYield.xml` patch this item's own step 3
  already deleted this session. Nothing left to do here.
- **Step 1 (owned-art props) — count corrected AGAIN, still not started.**
  A same-day-earlier pass counted **21** via a looser grep and missed
  `VQE_AncientBlackBox_Off` (a distinct defName in the cost table, line
  406, separate from the base `VQE_AncientBlackBox` at line 81 — a real
  22nd row, not a duplicate). Precise re-extraction
  (`grep -oP '^\s*\|\s*`\K[^`]+(?=`\s*\|\s*Vanilla Quests Expanded -
  Cryptoforge)'`, deduped, every hit's source line individually checked —
  no false matches, no duplicates) gives **22** unique defNames, each
  appearing exactly once in `SALVAGE_PALETTE.md`. Full list: `VQE_Ancient{
  Airlock, Airlock_Large, BlackBox, BlackBox_Off, FloorHeater, Landmine,
  ShieldedTurret, ShipLandingBeacon, SpacerAutocannon, TransmitterBeacon,
  WargamingTable}`, `VQE_Blueprints­Bench`, `VQE_Busted{ShieldedTurret,
  SpacerAutocannon}`, `VQE_CryptoAncientTerminal{,Bank}`,
  `VQE_ForcedAncientAirlock{,_Large}`, `VQE_FrozenEmptyCryptosleepPod`,
  `VQE_Jammed­AncientAirlock{,_Large}`, `VQE_RuinedHospitalBed`. The
  previous session's guess that airlock/turret state-variant pairs "almost
  certainly" share one piece of art is **checked and FALSE**: the donor's
  own `Buildings_Structure.xml` gives `VQE_AncientAirlock` a distinct
  `AncientAirlock_Top` texture, `VQE_JammedAncientAirlock` its own
  `AncientAirlock_Locked`, and the `_Large` variants their own
  `LargeAncientAirlock_*` set — every state is genuinely separate art, not a
  shared asset with a tint. So this is honestly **22 separate sprites**,
  each needing the full `generating-rimworld-sprites` workflow — a
  dedicated art pass, not a tail-end task (still correct, now on firmer
  evidence). **Confirmed 2026-09-26: none of the 22 defNames exist anywhere
  in the art pipeline yet** — zero hits in `registry.jsonl`, `done/`,
  `_artsrc/`, or any `Transient/*.decisions.json` — so nothing here would
  be duplicated by queuing, but writing 22 real, non-generic, citation-safe
  prompts (this is a Workshop-art citation swap — the donor's own textures
  must not be used as reference) is real design-adjacent work in its own
  right. Not attempted this session either, for the same reason as before:
  rushing 22 pieces risks shipping placeholder-quality art against the
  project's own standard, and a single quick pass is the wrong shape for
  writing 22 distinct visual briefs well.
- **Step 4 (ModsConfig removal, cold-load check, canonical resave)** needs a
  real restart, which this session is explicitly not authorized to run
  (offline authoring only). Unaffected by anything above; still owed
  entire, including the `futureQuests` `VQE_Cryptoforge_Chapter1` check.

## verify
Steps 2/3: `validate_patch.py` 0 errors (done); reference copy exists and
is documented (done). Step 5: confirmed against the live decisions record
and a live-source grep (done). Steps 1/4: not started.
