CherryPicker 1.6 cascades a race ThingDef cut to every PawnKindDef of that race: canArriveManhunter=false, combatPower=float.MaxValue, isGoodBreacher=false (decompiled ModSettings/DefUtility, 2026-11-26). So any C# worker that selects animals by canArriveManhunter (VEE AnimalTransportPodCrash, vanilla AggressiveAnimalIncidentUtility fallbacks) cannot pick a cut race; one that selects by race.packAnimal (VEE CaravanAnimalWI) still can, and needs its IncidentDef cut.
item: VANILLA_BEAST_LEAKS_EXCISE_ESCAPEES_AT_LARGE
home: design/Jawa/worldbuilding/cherrypick_resolved.md
