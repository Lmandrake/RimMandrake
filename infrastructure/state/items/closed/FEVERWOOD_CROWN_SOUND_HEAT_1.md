# FEVERWOOD_CROWN_SOUND_HEAT_1 — give the crown its ambient sound (so the sentinel's silence cuts something) and declare its heat kind

Caused by `FEVERWOOD_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.feverwood`. Design:
`feverwood_bedazzle_review_2026-10-02.md` §1 (Heat; "Built but hollow"), §4 row 0, §8; sheet
`the_fever_wood.md` §9 (*"the crown hums with work (taps, herds, boardwalk steps, steam); the ground is the
quietest wet place on the planet"*) and §6k (*"that silence is the loudest warning"*). Ruling: **build first:
land the decided work plus the giant's story** (decision taken by question card 2026-10-02 11:12 PDT);
heat kind **ambient** (the card's recommended option text: *"set its heat as still, shadeless heat"*),
under the one-heat law (owner, 2026-09-29/30: *"It can't be a new "kind" of heat."*).

## What exists

- `RM_MapComponent_SilenceCue` (`BeginSustainedHush`/`EndSustainedHush`) hushes `map.Biome.soundsAmbient`
  while a sentinel is up (`RM_MapComponent_TentacleWatch.ChorusSilenced`). `RM_FeverWood` declares **no**
  `soundsAmbient`, so the hush cuts nothing today.
- The pattern for a biome bed with no new audio: `src/RimMandrake/Webwork/Defs/SoundDefs/RM_WebworkSoundscape.xml`
  (sustained SoundDef reusing shipped DLC/Core clips, wired through `soundsAmbient`, no C#).
- `RM_SunHeatExtension` (`RimMandrake.CreatureBehaviors`), shape in
  `src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml` l.31 (`heatKind ambient`, `heatOffsetC`).
  The system is `SOLAR_HEAT_EXPOSURE_1`'s.

## spec

1. **The crown sound:** a sustained `SoundDef` `RM_FeverWood_CrownHum` (collision-checked 0) in
   `src/RimMandrake/FeverWood/Defs/SoundDefs/`, built from clips already shipped (Core/DLC jungle insects,
   bird calls, wood taps; read each `clipPath` from the installed game's SoundDefs, never guessed), declared
   in `RM_FeverWood`'s `<soundsAmbient>`. A busy, working sound: taps, herd noise, steps, steam, and the
   four birds' calls. A later audio pass may swap clips without touching anything else.
2. **The silence works:** with a sentinel up, `RM_MapComponent_SilenceCue` hushes that sound; when it goes
   down, the sound returns. No new C# expected; if `SilenceCue` reads the list at map load only, fix that.
3. **The heat kind:** `RM_SunHeatExtension` on `RM_FeverWood` with `heatKind ambient` (still, shadeless
   heat: shade does nothing, only insulation or leaving helps). `heatOffsetC` is an `// INVENTED` first
   value for the owner-watched tuning, same posture as the Greentide's. Vanilla temperature only, no new
   hediff. Add the Fever Wood to `SOLAR_HEAT_EXPOSURE_1`'s close-note list of extreme-heat biomes.

Depends on: nothing. Feeds: `FEVERWOOD_OIL_BOIL_WEATHER_1` (the hottest still days read the same heat).

## criteria

- `jawa/get_defs` `SoundDef/RM_FeverWood_CrownHum`: `foundCount` 1; every `clipPath` in it resolves (no
  `Could not find` for it in `Player.log` after load).
- Loaded `RM_FeverWood.soundsAmbient` contains `RM_FeverWood_CrownHum` (def read, not a substring).
- Live on a Fever Wood quicktest map: the ambient sustainer for it is playing (a `[Tool]` read of
  `Find.SoundRoot` / the map's ambient sustainers lists it); after a debug-spawned
  `RM_Sekkulaath_Sentinel`, `ChorusSilenced` = true and the sustainer is hushed (volume 0 or ended); after the
  sentinel is removed, it plays again.
- Loaded `RM_FeverWood.modExtensions` contains an `RM_SunHeatExtension` with `heatKind` = `ambient`.
