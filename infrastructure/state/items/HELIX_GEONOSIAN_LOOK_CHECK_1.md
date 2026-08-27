
## spec
`JawaFactionRoster.xml` was regenerated and deployed 2026-08-27 (md5
`1cd8faf90b9c44439ea0211e98599525`, byte-identical). `PrestigeCombatGear` was removed from
all four `Jawa_Helix_*` kinds — its 22 carriers are Alpha Genes Forsaken cloaks, Alpha Mechs
Mechlord suits, Biomes! Caverns beetle chitin and Cryptoforge plate, and not one is Star
Wars. Evidence: `infrastructure/state/evidence/AUTHORED_FACTIONS_WEAR_ANYTHING_1.txt`.
🔑 **Defs parse only at startup — invisible until the next cold load.**

## verify
Spawn 10 of each and LOOK, then read the apparel:
```
Jawa_Helix_Grunt  Jawa_Helix_Heavy  Jawa_Helix_Specialist  Jawa_Helix_Leader
Jawa_Geonosian_Grunt  Jawa_Geonosian_Heavy  Jawa_Geonosian_Specialist  Jawa_Geonosian_Leader
```

## criteria
- [ ] No Helix pawn wears an `AG_Forsaken*`, `AM_*Prestige*`, `BMT_Apparel_Armor*phract*`
      or `VQE_Crypto*` piece. Those four families are the whole of the removed pool.
- [ ] Every Helix pawn wears at least one `guy762_*Armor*` piece — the `KotORArmor_mid` /
      `KotORArmor_heavy` pools are all they have left, so an empty torso here means the
      removal over-narrowed and the fix is to widen, not to put the tag back.
- [ ] 🔴 Geonosians wear at least as much as they did before. See Watch out.

## Watch out
- 🔴 **The Geonosian is the one that can regress, and its cause is MONEY, not tags.**
  `apparelMoney` is 60~200 across the four kinds; their only armour tag is `ORChitinArmour`,
  whose three carriers (`OuterRim_ChitinCuirass` · `_Helmet` · `_Pauldrons`) inherit
  `OuterRim_MediumArmorFabricatedBase` — medium fabricated armour. **Affordability is
  UNMEASURED and cannot be measured offline:** these defs declare no `MarketValue` and the
  engine computes it from the recipe, the same property this project already recorded for
  Outer Rim weapons. If Geonosians arrive wearing less than before, the fix is the money
  number (DECIDE's), not the tag.
- ⚠️ **A constrained pool can leave a pawn wearing LESS than an unconstrained one.** That is
  the failure mode for every kind here, and it is silent — no log line, no error. This is a
  LOOK defect and only a look finds it.
- ⚠️ **`validate_patch.py` ran without `--defs`**, so `ParentName` resolution and
  `Class`-attribute checks were SKIPPED — UNMEASURED, not passed. A cold load is the first
  thing that resolves them.
- 🔑 The item this closes, `AUTHORED_FACTIONS_WEAR_ANYTHING_1`, listed 22 unconstrained
  kinds. **That table was stale by three days.** All 68 authored kinds now carry live tags;
  do not re-derive from the old table.

## fingerprint correction — CHECK, 2026-08-27
🔴 **The md5 in the spec above (`1cd8faf9…`) is STALE.** The live file is
`65c636e20c9ebe444e8d1fc6d0c8609f`, in the repo and the game copy alike (still
byte-identical to each other, so the deploy is intact).

`038a2efe` re-generated the roster after this item was written. It changed **7 lines,
all `combatPower`** — Helix Specialist 164→224, Helix Grunt 87→101, Helix Heavy 98→140
among them. **The premise of this item survives:** `PrestigeCombatGear` still appears
0 times in the file, and every `apparelTags` block and `apparelMoney` range is
unchanged. Verify by look as written.

🔑 **One correction to the Watch out:** Geonosians are not down to a single tag. Every
Geonosian kind carries `ORChitinArmour` **and `KotORClothing_civilian_prole`**, so an
unaffordable chitin set leaves them clothed, not naked. Current ranges, measured:
Grunt 60~72 · Heavy 80~96 · Specialist 100~120 · Leader 200~240.
