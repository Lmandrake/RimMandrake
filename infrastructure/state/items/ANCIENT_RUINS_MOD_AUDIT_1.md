# ANCIENT_RUINS_MOD_AUDIT_1 — the mall-maps mod: cut, keep, or learn from

Owner, at the Scarlands sitting 2026-09-06 (verbatim on the filing event): likely
to remove — "strange mall maps and other nonsense that really isn't very star wars
at all" — but audit deeply first.

## ⚠️ Step zero: identify the mod

It is NOT the Scarlands biome — `Scarlands`, its `AncientRuins_Scarlands` layouts,
craters and junk gen-steps are **vanilla Odyssey** (verified via source index,
`Defs/Odyssey/`). The target is the separate ancient-ruins content mod on the
owner's list (the one adding mall/metro/urban special maps — Ancient Urban Ruins
or kin). Pin the exact packageId from `ModsConfig.xml` and the live mod list
before any other step; do not audit by name-guess.

## The three questions, in order

1. **Anything redeemable?** Contact-sheet its content (rimworld-content-moderation
   skill) — maps, items, factions/pawns — graded against the Star Wars register.
2. **The ThingDef load**: full inventory of what it adds (measure off the dump,
   post-inheritance), which defs anything else references, and what a cut breaks
   (Cherry Picker vs full removal; the tag→surviving-item index after any cut).
3. **The generation tech**: HOW does it make so many interesting maps and items —
   custom GenSteps/LayoutDefs/prefab systems worth learning (or lifting patterns
   from) for our own injected locations (Scarlands sites, MOISTURE_FARM_TEMPLATES,
   structure_injection_roster) before the mod goes.

Removal itself, if ruled, is a separate item with a load-order/save-impact check
(rimworld-start-prep skill; a subscribed-not-installed module changes disk, not
the list).
