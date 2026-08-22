# B58 — two of three criteria met, and the third fails for a nameable reason

**CHECK, 2026-08-22 ~01:45 PDT. 578 mods, dev-quicktest map.** Six `RimMandrakeJawa_Kind`
spawned into `PlayerColony` and read back with `jawa/pawn_get`.

## (a) no `OuterRim_Jawa` xpath failure — **PASS**
`Player.log` (155 MB, this session's load): **0 occurrences of `OuterRim_Jawa`.**
Total `Failed to find a node with the given xpath` in the whole log: **5**, and all five
belong to third-party mods — Jewelry, Biomes! Caverns, and three from
`3534254491` (Intimacy - Gender Works). **None are Jawa_Patches.** ⇒ baseline 0, as asked.

## (c) the player's Jawa carries the 35-gene xenotype — **PASS**
**6 of 6 report `MandrakeJawa`**, `xenotypeApplied: true`. Not the 24-gene
`RimMandrakeJawa`. The absorbed clause also holds: all six are **male, bald**, on narrow
pointy / average head types, and the load threw no dead-xenotype reference.

## (b) hood and rustic robes and NOTHING else — 🔴 **FAIL**

What six player Jawas actually spawned wearing:

    2x  Apparel_Pants · DV_Apparel_HaySunhat · VAE_Apparel_Tunic · VAE_Handwear_Gloves
    1x  Apparel_BasicShirt · Apparel_Pants · Apparel_Tuque · VAE_Handwear_Gloves
    1x  Apparel_BasicShirt · Apparel_Pants · DV_Apparel_HaySunhat
    1x  Apparel_BasicShirt · Apparel_Pants · DV_Apparel_HaySunhat · VAE_Handwear_Gloves
    1x  Apparel_Pants · DV_Apparel_HaySunhat · VAE_Apparel_Tunic

**Not one hood. Not one robe.** Jeans on all six — the criterion says "No jeans" — plus a
**hay sunhat** on four of them and a **tuque** on one.

## 🔴 Why: the two repairs landed on two DIFFERENT defs

Both exist, and both are `defaultFactionDef: PlayerColony`:

| PawnKindDef | `apparelRequired` | `apparelTags` | xenotype |
|---|---|---|---|
| `RimMandrake_Jawa` | ✅ `guy762_Robes_jawa`, `guy762_JawaHood` | `IndustrialBasic` | — |
| **`RimMandrakeJawa_Kind`** | 🔴 **none** | `IndustrialBasic` | ✅ `MandrakeJawa` 1.0 |

- `SpeciesStartingGear_Tuning.xml:108-114` patches `PawnKindDef[defName="RimMandrake_Jawa"]`
  and gives it the robe and hood.
- `JawaXenotype_Repoint.xml:45-51` patches `PawnKindDef[defName="RimMandrakeJawa_Kind"]`
  and gives it the right xenotype.

⇒ **Neither kind has both.** The item's own spec says of the gear file *"its OPS already
named `RimMandrake_Jawa`; only the header still described the dead target"* — that reading
was right about the file and wrong about the target. `RimMandrake_Jawa` is a real def and
the patch matches it, so nothing logs; but criterion (c) identifies
**`RimMandrakeJawa_Kind`** as "THE PLAYER'S JAWA", and that is the one with no robe.

🔑 **A matching patch that hits the wrong def is the worst class of failure here** — it
validates clean, logs nothing, and the defect is only visible by looking at a pawn.

## Wider context, measured in the same pass
`apparelRequired` is set on only **12 of 71** Jawa-family kinds. Every `Jawa_Spawn_*`
species (13 of them) and `Jawa_Colonist` are `PlayerColony` with `apparelTags:
['IndustrialBasic']` and no required apparel — so **the player's non-Jawa colonists also
arrive in generic industrial clothing.** `Jawa_TradeMoot_*` require `guy762_Robes_jawa`
but **no hood**. See `design/Jawa/worldbuilding/faction_equipment_clusters.md` Finding 2.

Equipment: all six spawned bare-handed, which is **correct** — `RimMandrakeJawa_Kind` is one
of the 15 kinds `jawa/pawnkind_audit` classes `byDesign_noWeaponTags`.
