# Cauldron enrichment — audio & visuals spec (2026-10-02)

**SPEC ONLY** — no defs, code, art jobs, items or ledger verbs were made in this pass.
Covers `CAULDRON_ENRICHMENT_AUDIO_1` (three sounds) and `CAULDRON_ENRICHMENT_VISUALS_1`
(four visuals), both filed by FOUNDRY 2026-10-01 from `CAULDRON_GPT_ENRICHMENT_1`. Where they
were promised: the bedazzle review's sitting outcomes (`cauldron_bedazzle_review_2026-09-28.md`
§"Ruled at the sitting" item 1, the soundscape reversal: *"rushes, groans, sighs, rumbles,
gurgles, hisses, dull slow roars"*), its terrain note (*"the 'mineral rings and beaded
condensate' of the sheet is unexpressed"*), and the dewfall weather (*"every wet surface is a
dosed surface"*).

Engine facts below marked **MEASURED** were read from the decompiled 1.6 source through RimSage
in this pass. **UNMEASURED** means it could not be read from code.

---

## 1. What ships today (read before inventing)

Mod: `src/RimMandrake/Cauldron/` (`RimMandrake.Cauldron.dll`).

| Piece | Where | Relevance |
|---|---|---|
| 4 WeatherDefs `RM_ScatterDusk` · `RM_VentBloom` · `RM_VapourBank` · `RM_Dewfall` | `Defs/WeatherDefs/RM_CauldronWeathers.xml` | The triggers for the hisses, beads and saturation. Ambients are vanilla `Ambient_Wind_Clear/Storm/Fog`; vent bloom uses `WeatherOverlay_GrayPallFog` (no green, §6). Dewfall has **no overlay and no visible effect at all** today. |
| `RM_CompVexxissBehaviour` (fire warden, poisons water, letter) | `Source/RM_CompVexxissBehaviour.cs` | Already scans for `Fire` every 250 ticks (`TryWardFire`). **The bellow hooks here.** |
| `RM_Vexxiss` race | `Defs/ThingDefs_Races/RM_CauldronFauna.xml` | Has **no** `soundCall` / `soundAngry` / `soundWounded` / `soundDeath` on any life stage. The colossus is completely silent today. Art is 512×512, `drawSize` 7.0 adult. |
| `RM_TwistingThornwood`, `RM_TreeMartyr` | `Defs/ThingDefs_Plants/RM_CauldronFlora.xml` | `<soundHarvesting>Recipe_Smith</soundHarvesting>` as a TUNED stand-in. Art: 256×256, `Graphic_Random` (a/b). |
| `RM_CompMetalYield` + assay grade | `Source/RM_CompMetalYield.cs` | Grade already computed (`ExpectedMetalNow()` / full); shows only in the inspect pane. The assay flecks read from this, they add no new state. |
| 7 accent plants (crystal flower, blood bouquet, red bugloss, keening cordax, giant toxic flower, giant agaritox, raven nettle) | flora XML | texPaths wired, **no textures on disk** — only DarkCrust, Martyr, Thornwood and Xithess have art. The saturation visual needs base art first. |
| `RM_CauldronSoil` / `RM_CauldronSoilRich` | `Defs/TerrainDefs/RM_Cauldron_Terrains.xml` | `<takeFootprints>true</takeFootprints>`. **This does nothing here** (see V4). |
| `RM_CauldronSettings` | `Source/RM_CauldronMod.cs` | 11 settings already: metal yield, assay grade, vent bloom exposure, three vexxiss toggles, water letter, condensate gardens. New toggles go in this same screen. |

**Soundscape precedents elsewhere in `src/RimMandrake` (reuse, don't re-invent):**
- `TheForge/Source/RM_ForgeVoices.cs` + `Defs/SoundDefs/RM_ForgeVoices.xml`: on-camera
  sustainers + **positional vent one-shots** (`PlayOneShot(SoundInfo.InMap(new TargetInfo(cell, map)))`),
  and a **muted-player fallback**: when `Prefs.VolumeMaster/Game/Ambient` is ~0 or a setting is on,
  each voice is also named in a message. The Cauldron should copy this shape, not invent one.
- `CreatureBehaviors/Source/RM_MapComponent_ProximitySoundscape.cs`: a generic
  layered-sustainer system keyed by a `DefModExtension`.
- `FloodedCanyon/Defs/SoundDefs/RM_CanyonBeats.xml`: the house convention for **placeholder
  audio**, which is a vanilla clip retinted by pitch and distance. The defNames are what code
  binds to, and later only the grains get swapped.

**Sound pipeline: none exists.** `src/RimMandrake/Utils` has `extract_mlie_sounds.py` (a one-shot
UnityPy extraction of a donor mod's clips) and `selftest_sound_paths.py` (a guard that every
`<clipPath>` resolves). Nothing generates, licenses or records audio. Two other items are already
blocked on the same question: `CRACKEDLANDS_FIVE_BEATS_AUDIO_1` and `RUST_CATHEDRAL_MECHANICS_1`.
⚠️ **The absorbed clip libraries in `src/RimStarWars/` (SWBestiary 589 creature clips, Armoury
KotOR clips) are Star Wars tier.** Wiring one into the `RM_` Cauldron would make a franchise-free
mod depend on the IP tier. So **Cauldron placeholders use Core clips only**, which are always
present.

---

## 2. Audio

### A1. The vexxiss bellow ("warden of the breath")

- **Trigger:** in `RM_CompVexxissBehaviour.TryWardFire`, at the moment it **commits** to a new
  fire target (BeatFire or AttackMelee job issued), if this fire is not the one it last bellowed
  at and its per-pawn cooldown (INVENTED: 600 ticks) has elapsed. One bellow announces the
  warden's move, so the player hears it **before** the giant turns toward the fire.
- **Mechanism (MEASURED):** a one-shot `SoundDef` (`context MapOnly`, not `onCamera`) played with
  `PlayOneShot(SoundInfo.InMap(pawn))`. `SampleOneShot.TryMakeAndPlay` places a non-camera source at
  the maker's cell with `spatialBlend = 1` and min/max distance from `distRange`. That makes it a
  positional sound. Separately, give the race ordinary vox through `LifeStageAge.soundCall /
  soundAngry / soundWounded / soundDeath`. **MEASURED:** `Pawn_CallTracker.TryDoCall` only calls
  when the pawn is inside the camera view rect expanded by 10 cells, awake, not downed and not
  fogged. The interval is `race.soundCallIntervalRange` (default 2000–4000 ticks), and for a
  colossus it should be longer (INVENTED 6000–12000).
- **Readable without audio:** at the same moment, a `FleckMaker.ThrowMetaIcon`-style fleck or a
  `MoteMaker.ThrowText` "bellows" over the vexxiss. Muted players get the same event (Forge rule).
- **Assets:**

  | Asset | Spec | Brief |
  |---|---|---|
  | `Sounds/Cauldron/Vexxiss/Bellow_1..3` | .ogg, mono, 2.5–4 s, 44.1 kHz | A slow, mineral, **drawn-in-then-out** roar. It is a giant that breathes vents: a deep inhale rasp into a cavernous grinding exhale, with no animal snarl. |
  | `Vexxiss/Call_1..3`, `Angry_1..2`, `Wounded_1..2`, `Death_1` | .ogg mono, 1–3 s | The same voice family: grinding slag, a low groan, the death as a long collapsing exhale. |
  | **Placeholder** | Core `Pawn/Animal/Thrumbo/Thrumbo_Call` / `Thrumbo_Angry` folders, `pitchRange` ~0.55–0.65 | A pitched-down thrumbo reads as "bigger and older". Core also has `Pawn_Gorehulk_Call` (Anomaly), which is wetter and less suitable. |
- **Performance:** event-driven, at most one per vexxiss per 10 s. Negligible.
- **Mod Settings:** `vexxissBellowEnabled` (default on), nested under "Vexxiss puts out fires".

### A2. Metal-tree harvest

- **Trigger:** felling/harvesting `RM_TwistingThornwood` / `RM_TreeMartyr`. This is the existing
  `PlantProperties.soundHarvesting` sustainer, plus `soundHarvestFinish` for the fall.
- **Mechanism:** pure XML with no code. It is an owned sustainer `SoundDef` (`sustain True`,
  `MapOnly`, `PrioritizeNearest`) with **two subSounds**: the vanilla chop folder as one layer and
  a metallic ring/scrape layer on a slower `sustainIntervalRange`. That keeps "a tree being cut"
  readable while metal answers each stroke. A second def handles the finish: the trunk falls and
  then rings. **MEASURED:** vanilla `Harvest_Tree` uses folder
  `Interact/Work/Construct/Trees/Tree_Chop`, `Harvest_Tree_Finish` uses `.../Tree_Felled`, and
  `Interact_ConstructMetal` uses `Interact/Work/Construct/Metal`. Optional, and a one-line build
  cost: scale the metal layer's volume by assay grade via a `SoundInfo` parameter. Defer it unless
  the owner wants harvest to *sound* rich.
- **Assets:**

  | Asset | Spec | Brief |
  |---|---|---|
  | `Sounds/Cauldron/MetalTree/Chop_1..6` | .ogg mono, 0.4–0.8 s | An axe biting into **plated wood**: a dull wooden thunk with a bright, short metallic ring on top, like hitting a nail-studded post. |
  | `MetalTree/Felled_1..2` | .ogg mono, 2–3 s | The trunk comes down as a crack, a heavy crash, then a long **tinny shiver** of plates settling. |
  | **Placeholder (better than today's `Recipe_Smith`)** | Layer A `Tree_Chop` folder at pitch 0.9–1.0, layer B `Interact/Work/Construct/Metal` at pitch 0.7–0.8, volume ~60 % | `Recipe_Smith` is a blacksmith at an anvil and does not read as felling at all. Two vanilla layers reads as "chopping something metal". |
- **Performance:** a standard sustainer, one per active harvester. Negligible.
- **Mod Settings:** none needed. Cosmetic sound has no gameplay to gate. The owner may want one
  global "Cauldron audio" master toggle (see Q1); if so this falls under it.

### A3. Directional hisses in a vapour bank

- **Trigger:** while `map.weatherManager.curWeather == RM_VapourBank` (and weakly during the
  vent bloom), a MapComponent schedules a hiss every INVENTED 3–9 s of real time at a random cell
  **inside the camera view expanded by ~15 cells**. Prefer vent cells once
  `CAULDRON_MECHANICS_BUILD_1` part 3 spawns vent ThingDefs. The fog hides the source, so the
  sound has to supply the direction.
- **Mechanism:** a positional one-shot, `PlayOneShot(SoundInfo.InMap(new TargetInfo(cell, map)))`,
  exactly as `RM_ForgeVoices` plays its vent coughs. **MEASURED:** non-camera sources get
  `spatialBlend = 1` at the cell's world position, with `distRange` as Unity min/max distance.
  ⚠️ **"Directional" = Unity 3D panning relative to the AudioListener, and where that listener
  sits is a scene/prefab fact, not in decompiled C# (no `AudioListener` placement in `Verse/*.cs`;
  only `AudioListener.volume` in `PrefsData`). Whether the hisses audibly pan left/right is
  UNMEASURED** and needs a listen in a joint session. Fallback if they do not pan: distance
  attenuation alone still gives near/far.
- **Bundle it, don't duplicate:** this scheduler is the same organ as `CAULDRON_MECHANICS_BUILD_1`
  part 1 (The Engine Underfoot: ambient floor plus one-shot groans clustering near vents, and the
  falter-silence before a bloom). **Build one `RM_MapComponent_CauldronSoundscape`** with a
  per-weather table, and make the vapour-bank hisses one row of it. The falter-silence must also
  mute the hisses, because the silence is the alarm.
- **Readable without audio:** the hiss itself is ambience, not a warning, so no fallback is owed.
  The falter-silence's fallback belongs to the soundscape item (seismograph / message).
- **Assets:**

  | Asset | Spec | Brief |
  |---|---|---|
  | `Sounds/Cauldron/Vapour/Hiss_1..6` | .ogg **mono** (3D panning needs mono), 0.8–2.5 s | A **chemical gas** leak, not steam (§6 bans steam and geysers): a thin, dry, pressurised hiss with a sour, wavering edge, some ending in a soft gurgle or sigh. Several lengths for variety. |
  | **Placeholder** | Core `Misc/Hiss/HissSmall` and `Misc/Hiss/HissJet`, pitch 0.6–0.9 | Both are Core clips (`World_Sustainers_Misc.xml`). ⚠️ Do NOT use `Misc/Steam_Geyser/SteamGeyser_Venting` here even though the Forge does: it is literally a geyser, which §6 bans for this biome. |
- **Performance:** at most one one-shot every few seconds, `maxSimultaneous` 3. The scheduler
  checks weather on a 60-tick hash and does no cell scan beyond one random pick. Negligible.
- **Mod Settings:** `cauldronSoundscapeEnabled` (shared with the Engine Underfoot), default on.

---

## 3. Visuals

**Palette gate first.** Sheet §6 (`cauldron.md`): *"⛔ No green foliage. Low-light phototrophs are
black/purple/red; green here is a rendering error."* and *"Anything green is a visitor, a mistake,
or dying."* The item asks for *"green-amber"* accents and *"brilliant chemical colour"*. **No
saturation or bead art can be briefed until the owner rules (Q2).** The briefs below assume
"purple, blood-red, glass-white, and amber with no green" unless he says otherwise.

### V1. Dewfall chemical beads

- **Trigger:** while `curWeather == RM_Dewfall`, a MapComponent tick (INVENTED every 250 ticks)
  spawns beads on N random **unroofed, outdoor, standable** cells (INVENTED N=6, map-wide cap ~400
  live beads). Beads evaporate over INVENTED 0.5–1 day.
- **Mechanism (MEASURED fields):** a `FilthDef` (ThingDef with `<filth>`), spawned with
  `FilthMaker.TryMakeFilth`. `FilthProperties` has `disappearsInDays` (FloatRange, so self-clearing),
  `rainWashes`, `placementMask`, `cleaningSound` and `maxThickness`. A filth is a real Thing, so it
  shows a label on hover. That makes "every wet surface is a dosed surface" readable: the tooltip
  can say *chemical dew*. Rejected alternative: a `WeatherOverlay` subclass (screen-space sheen)
  is C# rendering work, and it cannot tell roofed from unroofed cells.
- ⚠️ **Gameplay side-effect to decide with the beads:** filth inside the home area becomes a
  cleaning job, and dewfall could become a chore tax. Mitigate with `placementMask`/spawn only
  outside the home area, or `disappearsInDays` short enough that cleaning never queues. Whether
  beads actually **dose** (a contact hediff) is a mechanic, out of scope here, and not invented.
- **Assets:**

  | Asset | Spec | Brief |
  |---|---|---|
  | `Textures/Things/Filth/RM_DewBeads_a..c` | 128×128 RGBA, `Graphic_Random` | Scattered **round condensate beads** in clusters of 5–15, each with a bright specular pin and a coloured rim. Mostly transparent; reads as "wet and wrong" at one-cell zoom. Colour per Q2. |
  | **Placeholder** | vanilla `Things/Filth/Spatter` texture, `color` tinted | Zero art cost to wire and test the mechanic. |
- **Performance:** filth are ticked Things, so cap them and let `disappearsInDays` drain them.
  The spawn tick is O(N) random picks.
- **Mod Settings:** `dewfallBeadsEnabled` (default on), plus a density slider (0.25–2×).

### V2. Dewfall saturates the garden accents

- **Trigger:** `RM_Dewfall` starts or ends. It applies to the accent plants (crystal flower, blood
  bouquet, red bugloss, keening cordax, giant toxic flower; the owner picks which).
- **Mechanism (MEASURED):** `Plant.Graphic` already swaps graphics by condition: it returns
  `def.plant.pollutedGraphic` when the cell is polluted (Biotech) and `leaflessGraphic` when
  leafless. Plants are **printed into the map section mesh** (`Plant.Print`), not drawn per frame,
  so a swap needs a remesh. Build: a `DefModExtension` `RM_DewfallGraphicExtension { texPath }` on
  each accent plant, plus a Harmony postfix on `Plant.Graphic` returning the dew variant while the
  map's weather is dewfall. On the transition, call `map.mapDrawer.WholeMapChanged(MapMeshFlagDefOf.Things)`
  **once** (INVENTED; the exact flag should be confirmed against the 1.6 `MapMeshFlagDefOf` at build).
  Zero-art alternative: brief glint flecks (`FleckMaker.Static`) over visible accent plants during
  dewfall. That is cheaper, but it reads as sparkle rather than saturation.
- ⚠️ **Blocked on base art:** 5 of the 7 accent plants have **no texture on disk** today, and a
  dew variant must be painted against its base. Order: base art first (existing
  `CAULDRON_RULED_CONTENT_1` / flora work), then dew variants.
- **Assets:** one dew variant per chosen accent plant at the base's own size (256×256, matching
  the existing Cauldron plant art). Brief: *the same plant, same silhouette, colours pushed to full
  chroma and wet-glossed, as if the dew had developed a photograph.* Validate the silhouette
  against the base (`generating-rimworld-sprites`).
- **Performance:** one full Things remesh per weather transition (two per dewfall). That is a
  one-frame hitch on a 250 map and is the same operation snow coverage changes trigger. Per-frame
  cost is zero.
- **Mod Settings:** `dewfallSaturationEnabled` (default on).

### V3. Assay flecks on old metal trees

- **Trigger:** none, it is static. A mature `RM_TwistingThornwood` / `RM_TreeMartyr` shows metallic
  flecks whose density follows the existing assay grade (`RM_CompMetalYield`), in 3 bands
  (INVENTED: below 0.33 = none, below 0.66 = light, above that = heavy).
- **Mechanism (MEASURED trap):** the obvious hook, `ThingComp.PostPrintOnto`, **never fires on a
  plant**. `ThingWithComps.Print` loops comps' `PostPrintOnto`, but `Plant.Print` overrides it
  wholesale with no `base.Print` call and no comp loop. Two working routes:
  (a) **Harmony postfix on `Plant.Print`** that prints one extra plane (`Printer_Plane.PrintPlane`)
  of a fleck-overlay texture for the plant's grade band. It is static and costs nothing per frame,
  because it is baked into the section mesh with the plant.
  (b) Graded `Graphic` swap via the same `Plant.Graphic` postfix as V2: three full variant textures
  per tree. That is more art and doubles with `Graphic_Random` a/b.
  **Recommend (a).** The remesh trigger is free, since vanilla already re-prints a plant as it
  grows (its drawn size follows growth). Also check the band again when settings change.
- **Readable:** this is a visual echo of a number already in the inspect pane. Gated with
  `assayGradeEnabled`, so turning off the grade turns off the flecks.
- **Assets:**

  | Asset | Spec | Brief |
  |---|---|---|
  | `Textures/Things/Plant/RM_AssayFlecks/Flecks_Light`, `Flecks_Heavy` | 256×256 RGBA overlay, matching tree art size and registration | Mostly-transparent **scatter of small bright metal glints and scab-plates**, weighted to the lower trunk where the tree excretes metal. Silver-grey, tarnished bronze, and a cold blue-violet sheen. No green. It must sit over **both** a/b variants of both trees, so keep it trunk-centred and loose. |
  | **Placeholder** | vanilla `Things/Mote/` sparkle-type texture, tinted | For wiring only. |
- **Performance:** static mesh. Zero per-frame cost.
- **Mod Settings:** ride `assayGradeEnabled`; optionally a separate `assayFlecksEnabled`.

### V4. Vexxiss mineral-ringed footprints

- **Vanilla footprints cannot do this (MEASURED).** `PawnFootprintMaker.TryPlaceFootprint` places
  vanilla's `Footprint` fleck only when **all three** hold: `RaceProps.makesFootprints` (default
  false; Core sets it on humanlikes), `terrain.takeFootprints`, and **`snowGrid.GetDepth >= 0.4`**.
  The Cauldron never snows (its weathers set `snowRate 0`), so the `takeFootprints true` on both
  Cauldron soils is **inert**. Nothing leaves prints there today.
- **Trigger:** the vexxiss moves. `RM_CompVexxissBehaviour.CompTick` (pawns tick Normal, so CompTick
  fires) checks horizontal distance moved since the last print, at INVENTED 1.5 cells (scaled for
  bodySize 6), and places a print, alternating left and right.
- **Mechanism, two options (Q3):**
  (a) **FleckDef** `RM_Fleck_VexxissPrint` (template: vanilla `Footprint`, `altitudeLayer MoteLow`),
  spawned with a rotation through `FleckMaker`/`FleckCreationData`. It costs nothing and is not a
  Thing. Vanilla's fades in ~5 s (solid 2.2 + fade 2.6). It can be made to linger longer, but a
  fleck is never saved, so it vanishes on reload.
  (b) **FilthDef** `RM_Filth_VexxissPrint` with `disappearsInDays` ~1. A real, saved trail the
  player can **follow to the giant**, and it has a hover label. It costs a few dozen Things per
  vexxiss crossing.
  **Recommend (b)**, because the bench rule says every animal effect is readable, and a trail you
  can track is the readable version. Also: on water cells the existing poisons-water swap already
  marks its passage, so prints only on land.
- **Assets:**

  | Asset | Spec | Brief |
  |---|---|---|
  | `Textures/Things/Filth/RM_VexxissPrint` (or `Mote/`) | 128×128 RGBA, drawn at ~2–2.5 cells | One huge **hoof-pad print** pressed wet into dark soil, ringed by **crystalline mineral crust**: concentric pale rings (salt-white, rust, violet) where the metal-laden body moisture dried. Rotatable, so draw it facing north. |
  | **Placeholder** | vanilla `Things/Mote/Footprint`, scaled ×3, tinted | Zero-art wiring. |
- **Performance:** (a) negligible. (b) bounded by one rare animal and `disappearsInDays`.
- **Mod Settings:** `vexxissPrintsEnabled` (default on).

---

## 4. Build plan (FOUNDRY)

Sized as four tranches. Each is shippable on placeholders and swaps assets later by path, so
nothing waits on Q1.

| # | Tranche | Size | Content |
|---|---|---|---|
| 1 | **XML-only audio** | S, about 1 h | Owned harvest sustainer + finish defs on vanilla grains (A2). Vexxiss vox (`soundCall/Angry/Wounded/Death`, pitched thrumbo) + `soundCallIntervalRange`. `selftest_sound_paths.py` must pass. |
| 2 | **Vexxiss code** | S | Bellow one-shot + cooldown + visual "bellows" mote in `TryWardFire` (A1). Footprint placement in `CompTick` (V4, fleck or filth per Q3). Two settings. Rebuild with `winbuild.py Cauldron`, and add any new `.cs` file to the csproj. |
| 3 | **Weather MapComponent** | M | `RM_MapComponent_CauldronSoundscape` with a per-weather table: the vapour-bank hiss scheduler (A3), designed so `CAULDRON_MECHANICS_BUILD_1` part 1 adds its floor, groans and falter-silence as more rows. The dewfall bead spawner (V1) can share the weather poll. Settings: soundscape, beads + density. |
| 4 | **Plant rendering** | M | Harmony postfix on `Plant.Print` for assay flecks (V3). Postfix on `Plant.Graphic` + one-shot remesh for dew saturation (V2). **V2 waits on accent-plant base art and Q2.** V3 needs only the two overlay textures. |

**Asset sourcing split:**
- **Sound (no pipeline: needs the owner's sourcing decision, Q1):** bellow ×3, vexxiss vox ~8,
  metal chop ×6, felled ×2, vapour hiss ×6, about 25 clips. All mono .ogg.
- **Art jobs (existing artpipe; run `artpipe_state.py find` first per the art-reuse rule):** dew
  beads ×3 (128²), assay fleck overlays ×2 (256²), vexxiss print ×1 (128²), dew variants × chosen
  accent plants (256², after base art). **No art job may be queued until Q2 rules the colours.**

**Verification:** placeholder audio is "audibly distinct in a joint session" (A3's panning is
UNMEASURED until then). Visuals use a review savegame per the savegame rule: one map in dewfall
with beads, saturated accents, graded trees at three growth stages, and a vexxiss trail.

---

## 5. Questions for the owner

**Q1. Where should the Cauldron's ~25 sounds come from?** Nothing in the repo makes or licenses
audio, and two other biomes (Cracked Lands, Rust Cathedral) are stuck on the same question.
- **Keep pitched vanilla sounds for now.** Ships this week and costs nothing. But it sounds like
  RimWorld with a cold, not like a new place, and a thrumbo under the vexxiss may be recognisable.
- **Licensed sound libraries** (e.g. CC0/royalty-free packs). They sound real and are legally
  clean, but someone has to pick each clip by ear, and every pack needs a provenance record.
- **AI-generated sound effects.** These can be briefed per clip like our art and scale across
  every biome. It would be a new tool to set up, and the quality is uneven, so each clip still needs
  your ear.
- **Build a small sound pipeline once** (generate or select → normalise → mono .ogg → path check)
  and use it for all three stuck biomes. This costs the most upfront and pays back across the
  planet.

**Q2. What colours can the dew and the saturated flowers use?** The Cauldron's own law says
nothing green (*"green here is a rendering error"*), but the enrichment asked for "green-amber"
accents and "brilliant chemical colour".
- **No green, ever:** purple, blood-red, glass-white and amber only. This keeps the biome's
  strongest visual rule intact, at the cost of a narrower palette.
- **Green allowed only in the dew itself**, because chemical, not living. Dew drops could flash a
  toxic green-amber for contrast while the plants stay in law. This is striking, but it bends a
  hard ban.
- **Lift the ban for dewfall only**, so the whole garden briefly blooms in "wrong" colours. That
  is the most dramatic option, and it makes "green is a mistake" an event rather than a law.

**Q3. Should the vexxiss's footprints fade in seconds, or stay as a trail you can follow?**
- **Fade in seconds** (like vanilla snow prints). Purely cosmetic, zero cost, and gone on reload.
- **Stay for about a day as a trail.** You can track the giant across the map, hover a print to
  see what made it, and the trail survives saving. It adds a few dozen map objects while it
  walks.
