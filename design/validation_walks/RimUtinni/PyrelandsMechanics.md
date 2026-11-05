# RimUtinni: Pyrelands Mechanics — validation walk
subject: src/RimUtinni/PyrelandsMechanics  (packageId `mandrake.rut.pyrelandsmechanics`)
deps: `mandrake.rm.pyrelands` (the burn line, fire clock and scorch-fruit), UtinniPatches (the Deep Desert Tribes reskin of TribeCivil)
list: a tier carrying RM Pyrelands, UtinniPatches and this mod, all five DLCs, a Pyrelands home map on a world holding the Deep Desert Tribes, not hostile
status-hint: concept `design/concepts/PyrelandsMechanics/` (Designer stage 3). Script: `src/RimUtinni/PyrelandsMechanics/validation.py`, first script PYRELANDS_MECHANICS_FIRST_SCRIPT_1. The rite has never been run live end to end.

Sources: `About/About.xml`, `Source/PyrelandsFireRite.cs`, `Source/LordJob_RUT_FireRite.cs`, `Source/JobGiver_RUT_HarvestScorchFruit.cs`, `Source/IncidentWorker_FlameHarvest.cs`, `Source/IncidentWorker_FireRaid.cs` (owed removal), `Source/PyrelandsMechanicsMod.cs`.

## must be true
- The rite, the visit and the fruit defence each have a Mod Settings switch, and all off leaves an ordinary Pyrelands map. → mod_static settings chain
- Every shipped def resolves in the running game. → shipped_defs chain

## north star
state: DRAFT
validated-hash:

Drafted by the Designer, 2026-11-05, from the root paragraph the owner approved by card (OWNER:1793895903357725756) and
his card answers OWNER:1793898835366988441 and OWNER:1793898838472369653. DRAFT, binds nothing until he validates it.

### must show

**The fire rite**
- [ ] `pmech_rite_party_walks_in` — on a Pyrelands map, now and then a scheduled burn arrives with a small Deep Desert
      Tribes party walking in off the sand, with a letter naming them.
- [ ] `pmech_rite_lights_line` — the party lights the grass line where they stand, and it walks on like any front.
- [ ] `pmech_rite_harvests_behind_front` — the party picks scorch-fruit in the black behind the front, never stepping
      into a burning cell, and none of them burns.
- [ ] `pmech_rite_leaves_with_fruit` — the party walks off the map carrying the scorch-fruit it picked.

**The visit**
- [ ] `pmech_visit_picks_and_leaves` — when a lot of fire is already standing, a peaceful Tribes group walks in to the
      burn, picks scorch-fruit in the black behind it and walks off the map carrying it.

**The fruit defence**
- [ ] `pmech_fruit_defence_warns_then_drives` — a colonist picking scorch-fruit in the Tribes' own scar during a rite
      or visit gets a warning naming the Tribes; if the colonist keeps picking, nearby harvesters attack that colonist
      until it leaves the scar, then go back to the fruit. Goodwill does not change and no raid follows, even if the
      colonist fights back.
- [ ] `pmech_fruit_defence_scar_only` — picking scorch-fruit anywhere outside the Tribes' own scar draws no reaction
      from them.
- [ ] `pmech_attack_brings_raids` — attacking the Tribes openly turns them hostile, and they raid the colony afterwards,
      possibly again later.

### cannot show
- [ ] `pmech_cannot_arson_tally` — a raid, a goodwill loss or a warning caused by the colony's own fires.
- [ ] `pmech_cannot_animal_blame` — the Tribes counting anything an animal does (a fire-hawk's twig, a furnace-beast's
      bed) against the colony.
