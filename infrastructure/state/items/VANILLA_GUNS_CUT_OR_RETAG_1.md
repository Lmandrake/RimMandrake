## 🔴 RULED 2026-08-22 — (b), AND IT IS NOT A PROPOSAL: IT IS ALREADY THE ARCHITECTURE

**⛔ Do NOT un-cut the vanilla firearm line.** Option (b) was chosen, built and shipped
before this item was filed, and the item's framing as an open a-vs-b choice is stale.

`src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml` is **1,972 lines, 156
PatchOperations, 465 xpath targets**, granting the vanilla tag vocabulary to the surviving
blasters: `IndustrialGunAdvanced` ×110, `AssaultRifle` ×104, `SimpleGun` ×100,
`NeolithicMeleeDecent` ×80, `ShortShots` ×44, `GunHeavy` ×40, `Revolver` ×40. 🔑 **It fixes
this at the WEAPON end, not the kind end** — which its own header gives as the reason:
*"Fixing it at the weapon end also fixes every future pawn kind, where patching 49 kinds
would not."*

### The blast radius is two kinds, not forty-nine

The 49 in `weapon_tag_audit.py`'s docstring is the number **before** that file existed.
Measured live against the 22:44:59Z dump: **12 kinds have every weapon tag empty**, and of
those —

| kind | verdict | why |
|---|---|---|
| `Mech_Pikeman` · `Drone_Sentry` · `Tribal_Archer_Fire` | **already fixed, awaiting the cold load** | `MECH_WEAPONS_UNCUT_1` and `FIRE_ARCHERS_GET_BOWS_1` are both `done`; the patch is in the tree at `WeaponTags_Renormalise.xml:1958`. The dump predates the deploy |
| `BS_CrossbowDvergr` · `BS_Crossbowman` · `BS_DvergrTraditionalist` · `OuterRim_ImperialTrader` · `VFEP_Footsoldier` | **NOT REACHABLE** | every FactionDef referencing them has `startingCountAtWorldCreation = 0`, zeroed by our own `JawaFactionSlate/Patches/OnlyOurFactions.xml` across 48 factions. They cannot generate in this world |
| `DP_ArtilleryPirate` · `DP_RocketPirate` | **FALSE POSITIVES, BY DESIGN** | ⛔ do not "fix" these. The mod ships `DP_CannonNoEquip` / `DP_RocketNoEquip` as Primary equipment with `destroyOnDrop=true`, `tradeability=None` and **no `weaponTags` at all**, at `weaponMoney` 99999. Their stablemate `DP_PirateCaptain` uses `DP_ZeusCannonTag`, which *is* carried — so the mod tags what it wants drawn and deliberately did not tag these two |
| **`VEE_Hunter` · `VEE_TribalHunter`** | 🔴 **GENUINELY DISARMED AND REACHABLE** | referenced by no FactionDef at all — spawned by `IncidentDef VEE_HuntingParty`, so they are faction-independent and the faction slate cannot stop them. `VEE_HunterIndustrialWeapon` and `VEE_HunterNeolithicWeapon` are each on **zero** ThingDefs |

### Why (b) and not (a), stated so it is not re-argued

Un-cutting eight vanilla guns would reverse a curation decision the owner made on purpose,
to repair **two incident-spawned hunters**. The owner reversed exactly one slice of this cut
— *"we should not be turning off Mech weaponry"* — and that reversal was a mechanism fix for
a faction that cannot function without its own weapons. ⛔ **Reading a narrow reversal as a
broad one is the failure this queue has already closed three items about today.**

### ⚠️ A premise tension exists and this ruling does NOT settle it

Two documents say the weapons floor is vanilla, and they are not struck:
`design/RimMandrake/Custom_World.md:110` (2026-08-03 audit — *"keep vanilla for the low end;
let SW gear be mid/high flavor"*, and it recommends AGAINST amputation) and
`design/Jawa/mods/required_mods.md:730` (2026-08-15 — *"v1's floor is vanilla low-tech and
Outer Rim's cheap end"*). The Cherry Picker cut removes eight vanilla **industrial** guns,
which may or may not be what "low-tech floor" meant. 🔑 **That question does not block this
item** — the retag architecture holds either way — but it is real, it is unresolved, and it
is the owner's. Raised in `queue/HUMAN.md`, not decided here.

### What BUILD does

`VEE_HUNTERS_GET_WEAPONS_1`, filed. Nothing else.

---

## spec
🔴 **A scope decision only DECIDE or the owner can make, and 32.5% of vanilla combat kinds
spawn bare-handed until it is made.**

`RESTORE_VANILLA_GUN_TAGS_1` reports ten vanilla industrial guns with empty `weaponTags`
and calls the cause unknown — *"Something strips them at load"*. **It is not unknown.**
Measured 2026-08-21 against the live Cherry Picker config, ten for ten:

| gun | in the cut list | `weaponTags` |
|---|---|---|
| `Gun_Revolver` `Gun_Autopistol` `Gun_BoltActionRifle` `Gun_PumpShotgun` `Gun_MachinePistol` `Gun_HeavySMG` `Gun_AssaultRifle` `Gun_SniperRifle` | **yes** | `[]` |
| `Gun_IncendiaryLauncher` `Gun_ChargeRifle` (the item's own control group) | **no** | intact |
| `Gun_Needle` `Gun_Scattergun` | **no, as of today** | `[]` in the dump only because it predates `MECH_WEAPONS_UNCUT_1` |

This is `BUILDABLE.md` 4 — Cherry Picker **neuters** rather than deletes, leaving the
`ThingDef` present with its tags stripped.

⇒ **The empty pools are the cherrypick working as designed.** `weapon_tag_audit.py`'s own
docstring records the intent: *"This campaign cut the entire vanilla firearm line in favour
of blasters and disarmed 49 pawn kinds doing it."* Restoring the tags reverses that design,
which is why BUILD will not do it on a bug report.

**The two options, and they are genuinely different games:**

**(a) Un-cut the vanilla firearm line.** Delete the eight `<li>` from the Cherry Picker
config as `MECH_WEAPONS_UNCUT_1` did for two. Cheapest to execute, immediate. ⛔ But it puts
revolvers and assault rifles back in the campaign's hands, against the blaster premise. The
owner reversed exactly one slice of this cut — *"we should not be turning off Mech
weaponry"* — and did not touch the rest, which reads as deliberate.

**(b) Leave them cut and re-point the affected kinds at surviving blaster tags**, in
`src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`. The mechanism is already built
and twice proved — the three Ancient kinds, and `Tribal_Archer_Fire` on 2026-08-21. Keeps
the design; costs one op per kind. 🔑 **This is the option consistent with everything
already shipped.**

⚠️ **Whichever is chosen, `weaponMoney` is NOT the lever and that is measured, not argued:**
across all 48 authored kinds, zero have a `weaponMoney.min` below their cheapest eligible
weapon, and `jawa/pawnkind_audit` reports zero `cannotAfford`.

## verify
The decision is recorded, and the losing option is struck in `RESTORE_VANILLA_GUN_TAGS_1`
so nobody works it as a mystery again.

## criteria
A seat picking this up knows which of (a) or (b) to build, without re-deriving the cause.
