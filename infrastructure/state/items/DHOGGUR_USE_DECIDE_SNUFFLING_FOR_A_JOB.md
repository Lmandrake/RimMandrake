# DHOGGUR_USE_DECIDE_SNUFFLING_FOR_A_JOB — what is a dhoggur FOR? (open question for the owner)

Follows `FORGE_SLOT_DECIDE_NEEDS_A_DESCRIPTION` (closed). Owner, by card 2026-10-16: the dhoggur fills the Forge's
small-ground slot (replacing `AA_CrescendoAnole` at 0.5), described in his words as *"a bizarre creature that
constantly snuffles and digs at the ashy minerals freshly deposited by volcanic sputter. Very tough heat resistant
hide."* The jobbosh is dropped (insufficiently alien). His sheet note on the dhoggur: *"Seems cool, but no
description, no assignment ability, no ability to say use this?"*

## built (plain vanilla animal, no mechanics)

`src/RimMandrake/TheForge/Defs/ThingDefs_Races/RM_Dhoggur.xml`: description from his words; tough hide as stats
only (ArmorRating Sharp 0.35 / Blunt 0.25 / Heat 1.0, comfy to 120 °C); `trainability None`; diet vanilla
`VegetarianRoughAnimal` (it does NOT eat ash minerals in code). Art: installed `RM_Dhoggur` east/south/north.
Numbers PROVISIONAL. Not deployed.

## open question — PROPOSALS ONLY, nothing below is decided or built

How should a player use or assign a dhoggur? Options for him to pick from (or write his own):

- **A. Wild only, a hunt/hide animal.** No new mechanic: its value is the tough heat-resistant leather. Would need
  its own leather def (heat-resistant hide) instead of `Leather_Plain`. Smallest change.
- **B. Tamable "ash prospector".** Tamed and set to a zone, it digs fresh sputter-ash and turns up a small mineral
  yield (e.g. a chunk of the Forge's spunstone feedstock) after each burst, like a vanilla animal producing a
  resource on a timer. Gives the "assignment ability" his note asks for; needs a comp (vanilla
  `CompProperties_Spawner`-style) and trainability.
- **C. Trained "sputter sniffer".** A trained dhoggur snuffles toward fresh deposits, so it warns of / marks where
  the next sputter landed (a work-free indicator, e.g. a letter or a marked cell). Ties into the Forge cycle clock.
- **D. Pack/haul animal in the heat.** Its hide lets it carry loads through Forge heat where colonists cannot linger.
  Pure vanilla (`packAnimal`, trainability), no new code; less on-theme with the snuffling.

## NEXT

`DHOGGUR_USE_DECIDE_SNUFFLING_FOR_A_JOB` — def built as a plain wild animal; NEXT: ask him by question card which of
A–D (or his own) the dhoggur's use is, then build only that.
