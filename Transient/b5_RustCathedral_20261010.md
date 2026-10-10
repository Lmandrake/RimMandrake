# b5 RustCathedral SettingsKit retrofit (2026-10-10)

Changed (src/RimMandrake/RustCathedral/): Source/RustCathedral/RM_RustCathedralMod.cs, Source/Hum/RustCathedralHumSettings.cs,
Source/Walls/RustCathedralWallsSettings.cs, the three csprojs (SettingsKit Compile Includes, ..\..\..\_Shared\SettingsKit), Assemblies/ 3 DLLs + .srchash (winbuild).
Layout: Mod window = 3 tabs (The Cathedral / The hum / Walls), each a full kit screen (own search, scroll, per-group reset). Scribe keys unchanged (main still scribes hum_/walls_ keys).

Groups (scope, audited against read sites)
- Main: Biome rarity (WORLDGEN-AFFECTING) NewMapsOnly (BiomeWorker.GetScore); Cathedral roaches Now (think node); borehulk on new maps (WORLDGEN-AFFECTING) NewMapsOnly (GenStep); Borehulk grinding Now (comp tick); Canal eels and dried-out dead on new maps (WORLDGEN-AFFECTING) NewMapsOnly (2 GenSteps); Not wired yet Now.
- Hum: hum/standing Now; Living bolts Now; The canals Now; Drilling the deep metal NextPulse (read at incident CanFireNow + vanilla infestation gate = storyteller roll); Under the plate Now; How long the roll lasts NextPulse (min/max read when a roll starts); Bolts on the hull Now.
- Walls: Wall tiers and sacred walls (WORLDGEN-AFFECTING) NewMapsOnly; Live Pattern Metal Now (Harmony postfix per call).

Dead settings (read by nothing): crossBiomeEnabled, crossBiomeEverywhere, crossBiomeBiomeList, crossBiomeCoverage -> collapsed "Not wired yet (these change nothing)". Only crossBiomeEnabled had a control; the other three have none (saved keys kept).
False/imprecise labels fixed: Hum screen header claimed everything "applies to every map immediately" - the deep-drill switch is a storyteller-roll read (NextPulse) and line-cycle length applies from the next roll; text now says so. Borehulk grind/roach text had no scope claim; old Walls "new maps only" for the live metal gate was not claimed (it was under a separate Live play label) - kept correct.
No simple screens kept; every class got the full kit.

MODS entries: see below (selftest 200/200 ok incl. planted defects, with these 3 added; scratch file deleted).
    "RustCathedral": ("RustCathedral/RM_RustCathedralMod.cs", "RustCathedral/RM_RustCathedral.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly", "Cathedral roaches": "Now",
        "The borehulk on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly", "Borehulk grinding": "Now",
        "Canal eels and dried-out dead on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Not wired yet (these change nothing)": "Now"}, ()),
    "RustCathedral#Hum": ("Hum/RustCathedralHumSettings.cs", "Hum/RimMandrake.RustCathedral.Hum.csproj", {
        "The hum and the Cathedral's standing": "Now", "Living bolts": "Now", "The canals": "Now",
        "Drilling the deep metal": "NextPulse", "Under the plate": "Now", "How long the roll lasts": "NextPulse",
        "Bolts on the hull": "Now"}, ()),
    "RustCathedral#Walls": ("Walls/RustCathedralWallsSettings.cs", "Walls/RimMandrake.RustCathedral.Walls.csproj", {
        "Wall tiers and sacred walls (WORLDGEN-AFFECTING)": "NewMapsOnly", "Live Pattern Metal": "Now"}, ()),
(selftest csproj/cs paths are relative to RustCathedral/Source; run_mod's src join works for these.)

Build: winbuild Hum, Walls, RustCathedral in order: 0 errors, 0 warnings each; DLL + .srchash copied to Assemblies.
