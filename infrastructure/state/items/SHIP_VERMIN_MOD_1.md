# SHIP_VERMIN_MOD_1 — one mod for everything that infests a ship

Owner, 2026-09-11 card sitting (on the Scarlands mod-placement card),
verbatim: 'gather all the "ship infesting" critters together into a single
mod "ShipVermin" that allows the mechanics, creatures, and future cool ideas
to emerge. Some are cute, some are hideous, some live inside, some can live
outside in vaccuum (the mynock for example).'

## spec
- New RimMandrake-tier mod "ShipVermin" (packageId per
  `design/NAMING_SCHEME_PLAN.md`; supersedes the drafted
  `mandrake.rm.hullvermin` name question in `scarlands_kit_spec.md` card 1 —
  the concept is ruled, the exact packageId is the builder's per the naming
  grammar). It owns: the vermin/AI C# classes from the Scarlands kit, the
  `RSW_Mynock` clone (ruled: our own kind, not a donor patch — the RSW_
  species def may live in the SW tier with the ShipVermin mechanics riding
  it; follow the naming grammar), and the boarding/breeding/gnaw mechanics.
- Ruled pressure curve: "Nuisance unless there are many" — individual vermin
  cheap, meanness scales with population.
- Design axes the owner named: cute↔hideous register per species;
  inside-hull vs vacuum-capable (mynock lives outside).
- The webwork kit's JobGiver/MapComponent creature-behavior classes go to
  the same separate behaviors family (ruled 2026-09-11), not
  `mandrake.rm.environmentalhazards`.

## verify
Mod exists with About.xml; mynock boards, breeds and gnaws under the ruled
curve on a quicktest gravship; no vermin class remains in
environmentalhazards.

## criteria
One home for ship-infesting critters that future species can land in without
a new mod each time.
