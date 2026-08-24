# The 2026-08-24 pre-reboot live harvest — 285 pawns rolled, 5 items answered

**Method:** every authored `PawnKindDef` spawned **5 times into its own faction** on the live
map and read back with `jawa/pawn_get`. Script: `src/RimMandrake/Utils/rimbench/roll_arm_harvest.py`.
Data: `roll_arm_harvest.json` (49 roster kinds) · `roll_arm_harvest_rest.json` (22 others).

🔑 **Rolled, not computed.** `jawa/pawnkind_audit` checks `weaponMoney.max` — the CEILING.
Generation rolls inside the range. That difference is the whole finding below.

---

## 🔴 1. The audit says everything is fine. The rolls say 21 pawns spawned bare.

| instrument | verdict |
|---|---|
| `jawa/pawnkind_audit` (69 kinds, 1830 weapon pairs, 400 tags) | `cannotAfford: 0` · `emptyTagPool: 0` · `healthy: 54` · *"every kind that intends to arm can"* |
| **5 rolls per kind, live** | **21 of 285 pawns bare**, across **16 of 49** roster kinds |

⇒ **`PAWNKIND_AUDIT_TAGLESS_BLIND_1` is confirmed, and it is worse than filed.** The audit does
not merely mis-classify a tagless combat role — **it returns a clean bill of health on kinds that
demonstrably field bare pawns.** Do not use it to answer "is this kind armed"; it cannot see a roll.

⚠️ **No kind is 0/5.** `ROLE_KINDS_ARMED_5_OF_5_1`'s literal claim — all 48 spawn holding
something — is TRUE per kind and FALSE per pawn. Worst: `Jawa_Homestead_Heavy` **3 of 5 bare**.

## 🔴 2. Two separate causes, and the bigger one was scoped far too narrowly

Backstories of the 21 bare pawns versus the 264 armed, resolved through `jawa/get_defs`:

| cohort | distinct backstories | of which disable `Violent` |
|---|---|---|
| **bare** | 32 | **10** |
| **armed** | 256 | **0** |

**Zero overlap.** A violence-disabled backstory is *sufficient* to produce a bare pawn — not one
of 264 armed pawns carried one.

⚠️ **But it is not necessary, and the strong form is FALSE:** **13 of 21** bare pawns (62%) are
violence-disabled; the other **8 can fight and still rolled bare** — that is the `weaponMoney`
roll, and it is a different defect with a different fix.

🔑 **`EMPIRE_BLACKSTAR_ALWAYS_WILLING_1` names the wrong two factions.** The pacifist rolls landed
on **Droid ×3, Wildsteam ×2, Geonosian ×2, TradeMoot ×2, Homestead, Hutt, Gamorrean and Empire ×1**.
It is a roster-wide defect that happens to have been noticed on the Empire.

## ✅ 3. `MECH_AND_ARCHER_ARMED_1` — met live

`Mech_Pikeman` **5/5** · `Drone_Sentry` **5/5** · `Tribal_Archer_Fire` **5/5**. The offline half was
measured 2026-08-23; this is the live half it was waiting on.

## ✅ 4. `ORDERS_DESIGNATORS_ENUMERATE_ZERO_1` — REFUTED live

`rimworld/list_architect_designators` on the Orders category returns **64 designators**, and `Open`
is among them, `visible: true`, `actionable: true`. Reproduced three ways — stable id
(`architect-category:orders`), raw defName (`Orders`), and with `includeHidden`.

🔑 **The likely cause of the original zero is that the architect menu is MAP-SCOPED** and the zero
was taken on the world screen. ⚠️ Note what a wrong parameter name does here: `category` instead of
`categoryId` returns *"A category id is required"* — a loud refusal, **not** a zero. So the zero was
real; it was just answering about a game with no map.

## 5. Baselines captured for the reload (the BEFORE half of two before/after pairs)

- `MA_CapryakScatterbow` **still carries `Gun`** — `["Gun","NeolithicRangedAdvanced","VEE_HunterNeolithicWeapon"]`.
  The `Inherit="False"` sever is committed and NOT deployed, so this is the pre-deploy state
  `ANCIENT_SCATTERBOW_TAG_SEVER_1` must be scored against.
- `Flamebow` = `["Neolithic","NeolithicRangedFlame","NeolithicRangedBasic","NeolithicRangedDecent"]`,
  `Gun_Needle` = `["MechanoidGunLongRange"]`, `Gun_Scattergun` = `["SentryDroneGunShortRange"]` — the
  un-neutered signature holds.
- **Exactly one faction is named "Blackstar Company"** (`Pirate`, 4 settlements). ⚠️ This world has
  only ONE pirate faction, so it **cannot** show the `PirateBandBase` leak
  `BLACKSTAR_NAME_MUST_NOT_LEAK_1` describes. Absence of evidence here is not evidence.

## What the roster actually fields

66 distinct weapons and 118 distinct apparel defs across 285 pawns. **22 pawns spawned with no
apparel at all.** The generic pool is visibly in play — `VFEP_Warcasket` ×11 and `guy762_JediCloak_light`
×22 on a Jawa desert roster — which is `AUTHORED_FACTIONS_WEAR_ANYTHING_1` seen from the live side.
