# FORGE_VOICES_AUDIO_1 — bespoke audio for the four voices

Split from `FORGE_GPT_ENRICHMENT_1` §3. `TheForge/Defs/SoundDefs/RM_ForgeVoices.xml` ships the four voices, the
cracking pulse, a phase stinger and the dhuvvox nodule click as **vanilla clips retinted by pitch**: the
geothermal run loop, the steam-geyser vent, the hiss jet, the UI tick and bell, off-map thunder and the rock
collapse. The code binds to the defNames only.

## owed now

`selftest_sound_paths.py` fails on four of the placeholder clips because they are packed in `resources.assets`.
Each needs its `VANILLA_PACKED` entry, with its donor SoundDef (verified in RimSage 2026-10-01):
`Electricity/GeothermalPlant/Run/GeothermalPlantRun_Loop1a` from `GeothermalPlant_Ambience`,
`Misc/Steam_Geyser/SteamGeyser_Venting` from `GeyserSpray`, `Misc/Hiss/HissJet` from `HissJet`, and
`Misc/RockCollapse` from `Roof_Collapse`. The parent's worker was told not to touch the grader. Whoever owns that
selftest should add the entries, or this item replaces the clips.

## owed

Recorded or sourced clips for the still-heat turbine throb (loop), vent cough, boiling-rain hiss (loop), basalt
tick, glass singing, deep cracking pulse, phase stinger and nodule click. Replace the grains in place and keep the
defNames. The consult also proposed "tower harmonics", a layer over the throb, if the owner wants it.
