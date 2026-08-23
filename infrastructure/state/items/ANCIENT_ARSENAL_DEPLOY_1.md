## spec
🔴 **DECIDE authored the renormalization; the deploy is BUILD's** — owner's ruling 2026-08-23.

**Deploy `src/Jawa/Jawa_Patches/Patches/AncientArsenal_Ashkarr.xml`** (committed `641f959c`),
4 operations. Rulings and the measurements behind them: `ANCIENT_SOLDIER_WEAPON_BUDGET_1`.

| change | from | to |
|---|---|---|
| `MA_CapryakScatterbow` | `["Gun","NeolithicRangedAdvanced"]` | loses `Gun` |
| `AncientSoldier` weaponMoney | 300~900 | **1200~2600** |
| `AncientSoldier_Leader` weaponMoney | 500~1400 | **2500~6000** |
| `AncientSoldierBoss` weaponTags | `["AMHP","Gun"]` | **gains `IndustrialGunAdvanced`** |

🔴 **THIS IS A DELIBERATE DIFFICULTY CHANGE, on the owner's instruction** — *"the ancients
should have WAAAY more money to spend on their equipment"*. Better-armed ancients hit harder.
⚠️ It **supersedes** `RAKATA_SLEEPERS_LOOK_RIGHT_1`'s constraint that the Rakata work must not
alter how ancients fight; that item has been told so in its own file.

## Watch out
🔴 **`AMHP` is carried by ZERO weapons and always was.** `AncientSoldierBoss` listed
`["AMHP","Gun"]`, so half its tag set matched nothing and it silently drew from `Gun` alone —
**capped at 4,800 however much money it was given**. That is why the boss gets a POOL and not a
raise: more money bought literally nothing. ⭐ `AMHP` is LEFT in place — it is harmless, and a
mod may supply it later.
⚠️ **The parent item's own table was wrong in two places and the patch does not follow it.** It
blamed three KotOR guns priced 60–100; they carry `SpacerGun`, **not `Gun`**, and were never in
this pool. The real affordable set at 300~900 was THREE weapons, not six.
⚠️ **The `Gun` pool tops out at 4,800** (72 tagged, 48 priced, p25 1,500 / median 2,000 / p75
2,800). Budgets above that ceiling do nothing on their own.

## verify
Validated offline at **0 errors** against the live def dump; all four defNames exist. The three
warnings are the intentional add-if-missing `Conditional`/`nomatch` pattern.
**In game:** thaw ten sleepers from ancient cryptosleep caskets — **none holds a scatterbow**,
and the mix reads as spacer-era kit. Zero red errors naming `AncientArsenal_Ashkarr`.

## criteria
- [ ] Ten sleepers thawed, zero scatterbows.
- [ ] An ancient soldier holds something a spacer-era soldier would have been sealed in with.
- [ ] No red errors.
