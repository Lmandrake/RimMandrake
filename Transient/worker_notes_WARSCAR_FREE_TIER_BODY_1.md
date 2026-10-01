# worker notes WARSCAR_FREE_TIER_BODY_1

- Nothing pre-built in src/ (searched). Art: glower/crust/pallbearer/scar-roach copied into Scarlands/Textures from artpipe _artsrc; chatrak/totchak/tetchik/lichen/scrapings are flat placeholder PNGs (real art queued per cast bible 8).
- Plan: Defs/ThingDefs_Races/RM_WarscarFauna.xml; C# MapComponent_WreckLichen + Harmony (tetchik glower gate on WildAnimalSpawner.CommonalityOfAnimalNow; chatrak plate dye gate on CompColorable.set_DesiredColor); settings filter wildAnimals at startup.
- Deviation: tetchik gate is a Harmony postfix, so it IS listed in wildAnimals (gated to glower cells).
