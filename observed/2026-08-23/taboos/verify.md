# The taboo pass — apparelDisallowTags on every faction. BUILD, 2026-08-23

Closes the gap named after the stormtrooper lockdown: `apparelDisallowTags` existed only on
the four Empire kinds, so every other faction could still turn up in someone else's uniform.

**45 kinds across 11 faction families** now refuse the signature families they are not.
Combined with the Empire's four, **all 49 authored combat kinds are covered.**

## the rule, and the guard that makes it safe

A culture must never turn up in another culture's uniform. The banned list per kind is:

    TABOO_POOL  −  the faction's own signature tags  −  every tag its apparelRequired items carry

Both subtractions matter. Without the second, `Jawa_Blackstar_Heavy` would have been told to
refuse `MNCFactionArmor` while being *required* to wear Mandalorian plate that carries it —
a kind refusing gear it cannot decline.

✅ **Verified after the edit: 0 kinds have a disallow entry that collides with their own
`apparelTags` or with any tag on their `apparelRequired` items.**

## the pool
`ImperialStormtrooper` · `ImperialArmy` · `ImperialOfficer` · `ImperialApparel` ·
`WarcasketAll` · `WarcasketVeteran` · `Warcasket` · `KotORDroidArmorT1/T2/T3` · `DroidArmor` ·
`ORTusken` · `SaV_apparel_tusken` · `SaV_apparel_jawa` · `MNCFactionArmor` · `Royal`

These are the families that carry a visible cultural identity. Generic tags
(`IndustrialBasic`, `KotORArmor_mid`) are deliberately NOT in the pool — they are the common
stock every faction is allowed to draw from, and banning them would strand kinds.

## what it prevents, concretely
- a **Tusken** in Imperial plate, or in a warcasket
- a **Jawa** in a warcasket — the robes-and-hoods ruling now has a second lock behind it
- a **droid** wearing Jawa robes
- an **Imperial officer** in Mandalorian merc armour
- a **Junker** in stormtrooper white

⚠️ **This does not police WEAPONS.** A Tusken can still draw a blaster if a tag reaches one.
The weapon side is governed by `weaponTags` + budget, and is a separate pass if wanted.

⛔ **And it cannot fix a bad `apparelRequired`.** Required items ignore both budget and
disallow. If a kind is required to wear the wrong thing, this layer will not catch it.
