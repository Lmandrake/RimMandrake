# DeepCalm ambient sound report — 2026-09-18

## Source clip

Two clips, both shipped in the Anomaly DLC (owned expansion, active per
`infrastructure/state/modlists/ModsConfig.FULL.20260819_201527.xml`
`knownExpansions`), no new audio asset:

- `Ambience/Undercave/Undercave_Ambience_Loop_A` — Anomaly's own `Ambient_Undercave`
  SoundDef (`Data/Anomaly/Defs/SoundDefs/World_Sustainers_Misc.xml`) uses this as
  its cave-drone loop. Fits "the hum".
- `Building/VoidNode/VoidNode_Ambience_Loop_A` — Anomaly's `VoidNode_Ambient`
  SoundDef (`Data/Anomaly/Defs/SoundDefs/Buildings_Misc.xml`), an eerie sustained
  psychic tone. Layered quieter with a slow attack/release, fits "rising to a
  Chorus" as a periodic intensification over the hum rather than a second
  distinct sound.

## SoundDef

New file: `src/RimUtinni/LanternDeeps/Defs/SoundDefs/RUT_DeepAmbience.xml`

- `RUT_DeepHum` — sustain SoundDef, one subSound, `AudioGrain_Clip` at the
  Undercave clip path, `pitchRange 0.85~0.95` (slightly lowered per option (b)),
  `SoundParamSource_AmbientVolume` mapping, `randomStartPoint`.
- `RUT_DeepChorus` — sustain SoundDef, one subSound, `AudioGrain_Clip` at the
  VoidNode clip path, quieter (`volumeRange 2~4`), `sustainAttack/Release 4` for
  a slow swell, same ambient-volume param mapping.

Shape copied field-for-field from Anomaly's own `Ambient_Undercave`/
`VoidNode_Ambient` (sustain/context/priorityMode/subSounds/grains/paramMappings),
so it matches a proven-working vanilla pattern rather than inventing one.

**Verification of the reuse mechanism (no clip extraction possible — RimWorld
audio ships packed in `Data/<DLC>/AssetBundles/`, not loose files, confirmed by
`find` on disk):**
1. The clip-path strings above are copied verbatim from Anomaly's own shipped,
   already-working SoundDefs — proof those exact paths resolve.
2. Cross-content-pack `SoundDef` reference (a WeatherDef in one pack naming a
   SoundDef declared in a different pack) is already live in the base game:
   Anomaly's `BloodRain` WeatherDef lists Core's `Ambient_Wind_Fog` and
   `Ambient_Rain` in its own `ambientSounds`. That is the same DefDatabase
   lookup our `RUT_DeepCalm.ambientSounds` performs.
3. What is *not* directly proven on disk (audio is packed, unlike textures) is a
   SoundDef in a THIRD pack pointing its own `clipPath` at another pack's clip —
   I could not find a cross-pack raw-clipPath example to grep. This rides on
   RimWorld's `ContentFinder<T>` being pack-agnostic (the same mechanism
   documented for `texPath` reuse), which is a reasonable but not disk-proven
   inference. Worst case if wrong: a silent missing-clip warning, not a def
   discard or a crash (AudioClip refs are lenient) — hence flagged for his EARS,
   not treated as a live risk.

## Weather wiring

`src/RimUtinni/LanternDeeps/Defs/Weather/RUT_DeepCalm.xml`: added
```xml
<ambientSounds>
  <li>RUT_DeepHum</li>
  <li>RUT_DeepChorus</li>
</ambientSounds>
```
and replaced the stale "No ambientSounds" comment (which described the OLD
donor-.ogg blocker) with a note pointing at the new SoundDef file and the
design target.

## Validation

- `python3 -c "import xml.etree.ElementTree as ET; ET.parse(p)"` — both files
  parse clean.
- `validate_patch.py` on both files against the full 632-mod load set (Core+DLC
  + Workshop `294100` + `src`): refuses a verdict — 120 of 632 active mods
  (mostly our own generated/deployed-elsewhere `mandrake.rm.*`/`mandrake.rut.*`
  packages) have no folder under any of the three `--defs` roots given, so the
  load set is incomplete and the tool won't call it clean. This is a load-set
  coverage gap in the environment, not a finding against these two files: our
  change has 0 `<Patch>` operations, no `ParentName`, and no `texPath` — the
  only checks that incompleteness could actually invalidate. `Class="AudioGrain_Clip"`
  is a real vanilla class, confirmed by grepping several shipped Anomaly
  SoundDefs using it identically.

## Deploy

`deploy_custom_mods.py --mod LanternDeeps` (plan only) shows 4 lines of drift:
```
+  Defs/SoundDefs/RUT_DeepAmbience.xml   (mine, new)
~  About/About.xml                       (not mine)
~  Assemblies/RimMandrake.Utinni.LanternDeeps.dll   (not mine)
~  Defs/Weather/RUT_DeepCalm.xml         (mine, edited)
```
`deploy_custom_mods.py` is mod-scoped, not file-scoped — there is no flag to
apply only the XML lines. Since the plan includes the other worker's in-flight
`.dll` and the game is running, I did **not** run `--apply` (per instruction:
do not touch the `.dll` while the game is up). **Deploy did not happen.** The
XML changes are only in the repo; whoever next deploys LanternDeeps (once the
`.dll` is safe to push, i.e. a restart) will carry these two files along.

## Open

- **Owner's EARS**: after LanternDeeps is deployed (XML+dll together, next safe
  window) and the game is loaded on a list that includes it, walk into a
  Lantern Deeps pocket map (or use the bridge to teleport/build one) and just
  listen for ~30 seconds — confirm a steady low cave hum is audible and that it
  periodically swells with a subtler eerie tone (the "Chorus"), then check
  Options > Audio doesn't need retuning (both layers use
  `SoundParamSource_AmbientVolume`, so they ride the ambient volume slider like
  every other vanilla weather).
- The cross-content-pack raw-`clipPath` reuse (SoundDef in our mod pointing at
  an Anomaly-packed clip) is inferred from RimWorld's pack-agnostic
  `ContentFinder<T>` behavior (same mechanism proven for `texPath` reuse), not
  directly disk-verified — audio ships packed in `AssetBundles`, unreadable
  without extraction tooling this task doesn't have. Worst case if wrong: a
  silent missing-clip warning in `Player.log` (not a def discard, not a crash).
  If the in-game listen test comes back silent, grep `Player.log` for
  `RUT_DeepHum`/`RUT_DeepChorus`/`Undercave`/`VoidNode` first.
- Deploy is still owed (see above) — flag to whoever picks up LanternDeeps next.
