## spec
Blackstar Company is authored as a patch onto vanilla `FactionDef[defName="Pirate"]`.
That def is declared `<FactionDef Name="PirateBandBase" ParentName="FactionBase">`
(`Core/Defs/FactionDefs/Factions_Misc.xml:510`) — **it is simultaneously the concrete
pirate faction and the abstract root every other pirate def inherits from.**

⇒ **Six FactionDefs now read `fixedName: Blackstar Company`** — `Pirate`,
`CannibalPirate`, `PirateYttakin`, `PirateWaster`, `DV_PirateKeshig`,
`AG_XenohumanPirates` — measured off the 2026-08-21 dump.

On the generated world, **four of them exist at once and every one is called
"Blackstar Company"** (`jawa/list_factions`, 37 visible factions). Three of the four
have their own separate Ideo object, all named `the Contract`; two are identical and
the third carries `AnimalPersonhood` and `Raider`, which nobody authored. So the four
companies do not even share a doctrine.

⚠️ `Galactic Empire` has the same collision on a smaller scale: `Empire` and
`OuterRim_GalacticEmpire` both carry that `fixedName`, and both generated.

## the design question, which is DECIDE's and not BUILD's
Is "the Blackstar Company" **one mercenary outfit**, or **the generic name every
pirate on Ash'karr wears**? The spec reads as one outfit. The game will field four
identically-named factions with divergent faiths, on a world that is generated once
and frozen.

Both answers are buildable and they need different work:
- **one outfit** ⇒ the reskin must move off the shared root onto a def that nothing
  inherits from, or the inherited `fixedName` must be overridden on each child
- **every pirate** ⇒ the faiths need reconciling so four factions of one name are not
  running three different ideoligions, and the world map needs to not read as four
  copies of one company

## criteria
A ruling in `OWNER_DECISIONS.md` or the ledger saying which reading is intended, and
one item filed for BUILD carrying it.

## why it is on the pre-worldgen path
Faction identity and ideoligions are read at world creation and cannot be retrofitted.
Related and mechanically identical: `JUNKERS_STRUCTURE_MEME_LOST_1`, which is the same
inheritance leak reaching a faction that is not a pirate at all.
