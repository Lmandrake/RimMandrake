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

---

## ⚠️ THE TABLE ABOVE IS SUPERSEDED — DECIDE, 2026-08-23, from the 581-mod capture
🔴 **Both budgets in the spec were already fixed before this item was re-read.** `AncientArsenal_Ashkarr.xml`
raised them and the 2026-08-23T22:49:51Z capture — the first that matches the live mod list — reads:

| kind | spec said | **actually live** | tags | cp |
|---|---|---|---|---|
| `AncientSoldier` | 300~900 | **1200~2600** | `["Gun"]` | 85 |
| `AncientSoldier_Leader` | 500~1400 | **2500~6000** | `["IndustrialGunAdvanced"]` | 130 |
| `AncientSoldierBoss` | 2100~7500 | 2100~7500 | `["AMHP","IndustrialGunAdvanced","Gun"]` | 225 |

**Defect 1 (the budget) is CLOSED, and the numbers are right.** Re-measured pools, priced entries only:

- `Gun` — 76 defs, 51 priced, min 60 / p25 1400 / median 1800 / p75 2800. At the old 300~900 a soldier
  could afford **6 of 51**; at 1200~2600 he can afford **12 to 36**. He now buys from the middle of his own
  pool instead of its floor.
- `IndustrialGunAdvanced` — 55 defs, 47 priced, **min 1400**, median 18,800. ⚠️ The leader's OLD 500~1400
  could not afford a single weapon in its tag pool at any roll below the maximum; 2500~6000 reaches 9–12.
- `AMHP` — **carried by zero weapons**, so it contributes nothing to the boss; the boss draws on `Gun` and
  `IndustrialGunAdvanced` and its untouched 2100~7500 is fine. No change wanted.

⚠️ **25 of the 76 `Gun` defs expose no `MarketValue` at all** and are UNMEASURED here, not free — RimWorld
derives value from stuff and components when a def declares none. Any future budget claim must say so.

## 🔴 Defect 2 was patched, the patch did NOTHING, and it said nothing
**The scatterbow still carries `Gun` in the capture taken after the fix was deployed.** The money operations
in the same file took; this one did not, and no error was logged.

**Mechanism, read rather than inferred.** `MA_CapryakScatterbow`'s own def declares only
`<weaponTags><li>NeolithicRangedAdvanced</li></weaponTags>` and sets `ParentName="BaseHumanMakeableGun"`.
That Core abstract (`Data/Core/Defs/ThingDefs_Misc/Weapons/BaseWeapons.xml:86`) is where `<li>Gun</li>` lives,
and list inheritance **appends the parent's items when defs resolve — after patching**. So the xpath
`.../weaponTags/li[text()="Gun"]` had no node to match, and `PatchOperationConditional` returns true on no
match. 🔑 **This is the general trap, not a one-off: you cannot patch away an INHERITED list item by its
value, and the failure is invisible.**

✅ **Fixed by severing the append instead** — `PatchOperationAttributeSet` putting `Inherit="False"` on the
child's `weaponTags` node. AttributeSet touches only the attribute, so any tag another mod's patch already
appended to that node (`VEE_HunterNeolithicWeapon` is one) survives.

## What is left
Deploy and one live reading — **`ANCIENT_SCATTERBOW_TAG_SEVER_1`, filed for BUILD.** Until a capture taken
after that deploy shows `MA_CapryakScatterbow` without `Gun`, this fix is authored, not proven.
