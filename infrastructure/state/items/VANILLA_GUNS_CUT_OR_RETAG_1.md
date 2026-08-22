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
