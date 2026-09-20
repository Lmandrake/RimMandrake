# DESERT_SIGNATURE_FLORA_1 — author ultracactus, staggerseed, and shade plants

## what is wrong

desert.md §4b names three RUT_Desert plants that have no def and no ledger
item:

- the **ultracactus** (owner's name, stands) — "harvestable from open ground
  nothing else uses" (§7), needs no C#.
- the **staggerseed** — a cycle plant with a prepared-seed dish.
- the **defending shade plants**.

## why it matters

Three named, owner-approved plants central to the desert's food and defense
identity do not exist as defs.

## the work

- **Ultracactus** — author now. ThingDef, pale green, buried look,
  `fertilityMin` 0.05 so it takes Sand, with a harvest item. Pure XML, no C#,
  no name card needed — this is the only one of the three that can ship on
  its own today.
- **Staggerseed** — needs C# (corpse-dispersal mechanic + a euphoric hediff
  from the prepared-seed dish). File it as a separate item, gated on a name
  card to the owner — unlike the ultracactus, it has no owner-given name yet.
- **Defending shade plants** (2-3 ThingDefs) — need thorn/contact damage with
  no native RimWorld `CompProperties` equivalent. File as a design item, not
  authored directly.

## Watch out

Do not block the ultracactus on the other two — it is the only one of the
three that is pure-offline, no-C#, no-name-card work. Its own item/subtask can
close independently. Staggerseed's name card is a separate, smaller ask than
the cards in `EXTREME_DESERT_UNRULED_VERMIN_1` or
`SURRA_GRASS_FERTILITYMIN_1` — do not bundle it with theirs when presenting
to the owner.

## verify

An `RSW_` ultracactus ThingDef exists with the stated `fertilityMin` and a
harvest item, wired into RUT_Desert; a staggerseed item and a shade-plants
design item both exist under `infrastructure/state/items/`.

## criteria

The desert's three named signature plants each have either a shipped def or a
filed, correctly-scoped successor item.
