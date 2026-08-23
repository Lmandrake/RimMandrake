## spec

🔴 **An ancient soldier can afford six weapons, and one of them is a bow.** The owner's
read on 2026-08-23 — *"the ancients should have WAAAY more money to spend on their
equipment"* — is correct, and here is the arithmetic behind it.

```
AncientSoldier          weaponMoney 300~900      weaponTags ["Gun"]                combatPower  85
AncientSoldier_Leader   weaponMoney 500~1400     weaponTags ["IndustrialGunAdvanced"]  cp 130
AncientSoldierBoss      weaponMoney 2100~7500    weaponTags ["AMHP","Gun"]         combatPower 225
```

**75 weapons carry the `Gun` tag. Of the 51 that expose a MarketValue, only SIX cost
≤900 and only THREE cost ≤300:**

| weapon | value | source |
|---|---|---|
| `guy762_holdout` | 60 | KotOR |
| `guy762_bpistol` | 100 | KotOR |
| `guy762_slugrifle` | 100 | KotOR |
| `JawaIon_Blaster` | 420 | ours |
| **`MA_CapryakScatterbow`** | **520** | **Mythic Ages: Megafauna Bestiary** |
| `IW_Gun_IonPistol` | 800 | |

⇒ **That is the entire affordable pool for a spacer-era ancient.** Everything that reads
like ancient kit sits above the ceiling, so the generator reaches for whatever is cheap —
and `MA_CapryakScatterbow` carries `["Gun", "NeolithicRanged…"]`, so a **bow from a
megafauna mod is tagged as a gun** and lands inside the budget.

**Observed live**, six sleepers thawed from a real ancient-horror complex: two
`MA_CapryakScatterbow`, two `VWE_Gun_ChargePistol`, one `VWE_Gun_RocketLauncher`, one
unarmed slave. **A third of the squad came out of cryosleep holding a scatterbow.**

## Two separable defects

1. **The budget is too low for the tag.** `AncientSoldier` at `combatPower 85` gets
   300~900, while `Jawa_Empire_Grunt` at a comparable `combatPower 87` gets 650~780 for a
   much narrower tag set. ⚠️ **Raising it is a difficulty change, not a cosmetic one** —
   better-armed ancients hit harder, and `RAKATA_SLEEPERS_LOOK_RIGHT_1` insisted the
   Rakata work must not alter how ancients fight. Any change here is a deliberate
   difficulty decision and should be recorded as one.
2. **`MA_CapryakScatterbow` is tagged `Gun`.** A neolithic-looking scatterbow in the
   industrial/spacer gun pool will keep surfacing on every low-budget `Gun` kind, not
   just ancients. Fixing the tag is narrower than moving anyone's money.

## verify

- Ten sleepers thawed from ancient caskets: none holds a scatterbow, and the mix reads
  as ancient kit.
- Whatever changed — budget, tag, or both — is written down as a difficulty decision with
  the owner's assent.

## criteria

An ancient soldier comes out of a cryptosleep casket holding something a spacer-era
soldier would plausibly have been sealed in with.
