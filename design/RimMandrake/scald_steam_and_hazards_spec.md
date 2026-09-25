# The Scald — steam weather and boiling-water hazards (design spec)

Item: `SCALD_STEAM_WEATHER_DESIGN_1`. Design only; nothing here is built. Written 2026-09-25
against the live source tree and the RimSage 1.6/Odyssey decompile (every engine claim below is
tagged MEASURED or UNMEASURED in §10); the owner's rulings of the same day are folded in (§9 lists
them; §4, §5, §7 state the decided form). Build step 1 is §8. Companion docs: `infrastructure/state/items/SCALD_MECHANICS_1.md`
(kit history), `design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md` (S1–S6),
`design/Jawa/worldbuilding/biomes/the_scald.md` (FROZEN sheet).

## 0. Why this exists (owner's words and the live finding)

Owner, 2026-09-25: *"It's worth talking about how we can make the Scald steam weather really
beautiful and interesting (and deadly without protective gear)."* And from the same live review:
*"Everything appears to be burning. Is that the boiling water? Likely should make its own creatures
immune to that. Do we already have the water's dangerous nature (and the protections available to
the player) wired in?"*

Answers, verified against source:

- **Yes, it is the boiling water.** Every pawn standing on a `RUT_ScaldWater*` cell takes vanilla
  `Burn` injuries from `HediffGiver_Terrain` (§4) — that is the shulla's "Burn needs tending".
  Nothing is on fire; the injury is simply labelled *burn*.
- **The water's danger is wired; the protections are not.** The six boil terrains carry
  `burnDamage`/`burnIntervalTicks`; the `RUT_Scald` DamageDef, `RM_ScaldArmor` category and
  `RM_ArmorRating_Scald` stat exist but **no apparel in the repo carries that stat**, no research
  unlocks any, and the terrain burn does not even use that damage type (§4).
- **No native is immune.** `RM_Noohm`/`RM_Shulla` inherit vanilla's `OrganicStandard` giver set
  and burn like a colonist (§6).
- **The steam weather does nothing to a pawn** beyond `accuracyMultiplier 0.9`. It is presentation
  only, and its overlay is currently vanilla's fog material borrowed wholesale (commit `70607e667`)
  because the mod's own path could never load (§3.1).

## 1. Hard bans from the frozen sheet, restated

`the_scald.md` §6, binding on every mechanic below:

1. **Never potable** — no protection, salve or building may make the body drinkable. Only the
   distilled breath (the steam-catch) is water.
2. **Never the terminator seas' biome** — nothing here is shared with `RUT_TwilightSea`/`RUT_GreySea`.
3. **No boiling-immune traversal for free** — crossing scald water always costs; the shipped burn
   values stand. ⇒ every protection in §5 has a price (research, materials, speed, heat) and
   **gear never reaches zero** (a floor on the exposure clock, §3.3). Native immunity (§6) is
   not traversal-for-free: natives are the water's own life, not a route the player can wear.
4. **No macro-life in the boil itself** — no creature this spec adds swims the surface layer.
5. **No drained, cooled or tamed Scald** — no building reduces the boil; the still day (§3.2) is a
   pause in the *breath*, never in the *boil*.
6. **No vanilla-Earth flora or fauna.**

Not a ban, and worth saying: the sheet's *"the sea is fouled; the steam is clean"* (§3, §5) is
about **purity**, not harmlessness — clean live steam scalds. `RUT_ScaldSteamLock.xml`'s header
reads "the steam is clean" as "no damage fields"; that was a build choice, not a ruling, and
this spec revises it. The sheet's own §5 line *"the water burns to touch and comforts as it burns"*
stays exactly as shipped.

## 2. What is already built (read before inventing)

| Piece | Where | State |
|---|---|---|
| Six boil terrains, burn 1–2 / 300–240 ticks, cyan glow, `HotSpring` thought, `avoidWander` | `TerminalBiomes/Defs/TerrainDefs/RUT_ScaldWater.xml` | shipped |
| Cool margin ring, burn 0, the one drink source | `.../RUT_ScaldMargin.xml` | shipped, unplaced on the map |
| `RUT_ScaldSteam` WeatherDef — sky colours, `Ambient_Wind_Fog`, accuracy 0.9 | `TerminalBiomes/Defs/WeatherDefs/RUT_ScaldSteam.xml` | shipped |
| `RUT_WeatherOverlay_ScaldSteam` — dual panner on vanilla's fog material | `EnvironmentalHazards/Source/RUT_WeatherOverlay_ScaldSteam.cs` | shipped, borrowed art |
| `RUT_ScaldSteamLock` — `RM_GameCondition_WeatherPulse`: steam forced, still day (Clear) MTB 96 h for 12–24 h; gate `Scald.S1` | `TerminalBiomes/Defs/GameConditionDefs/RUT_ScaldSteamLock.xml` | shipped |
| `RUT_Scald` DamageDef (`Burn` hediff, armorCategory `RM_ScaldArmor`) + `RM_ArmorRating_Scald` stat | `TerminalBiomes/Defs/DamageDefs/`, `EnvironmentalHazards/Defs/` | shipped, **zero apparel carriers** |
| `RUT_SteamDevil` wandering vortex dealing `RUT_Scald` | `TerminalBiomes/Defs/ThingDefs_Misc/RUT_SteamDevil.xml` | shipped |
| `RM_HediffComp_EnvironmentalExposure` — weather-gated severity clock with `protectionStat`, `minDriveFactor` floor, `immunityHediff`, `immuneThingDefs` | `EnvironmentalHazards/Source/RM_HediffComp_EnvironmentalExposure.cs` | shipped; consumers Miasma, Rot Sheen |
| `GameCondition_EnvironmentalWeather.carrierHediff` — grants a hediff to every eligible pawn so the comp above can run | `.../GameCondition_EnvironmentalWeather.cs` | shipped |
| `HazardTargeting.SumApparelStat` + the `RM_WetBulbProtection`/`RM_SheenProtection` stat shape (0..1, summed over worn apparel) | `EnvironmentalHazards/Defs/StatDefs/`, `TheRot/Defs/StatDefs/` | shipped; the chitin spider helmet is the worked gear precedent |
| `RM_ScaldWalkerChitin` — a Scald-specific plated material already dropping from the dive hunt | `DivingInteraction/Defs/ThingDefs_Items/` | shipped, no consumer recipe |
| `RM_MechanicGates` + Terminal Biomes' Scald sub-toggles S1/S2/S4/S5/S6 | `EnvironmentalHazards/Source/RM_MechanicGates.cs`, `TerminalBiomes/Source/RM_TerminalBiomesMod.cs` | shipped |
| Natives `RM_Noohm`, `RM_Shulla` (`ComfyTemperatureMax 95`, plain `AnimalThingBase`) | `TerminalBiomes/Defs/ThingDefs_Races/RM_ScaldFauna.xml` | shipped, burn like anyone |

⇒ Of the mechanisms this spec needs, **the exposure clock, the protection-stat aggregation, the
carrier grant, the damage type, the settings seam and the native material all exist.** New work is
XML wiring, three apparel defs (wrap, boil-suit, rind coat), one research def, textures, one small
overlay-material class, a ~10-line species gate on the steam devil (§6), and one optional
WeatherEvent.

## 3. The steam weather as an experience

### 3.1 Look — overlay, sky, glow, plumes, sound

**Target (sheet §9):** *cyan glow under white steam* — a bright, near-white haze that the water's
own cyan light bleeds up through, thickest over open water, never a grey blind.

**Overlay material — the route, MEASURED.** Three facts settle it:

- `MatLoader.LoadMat(path)` is `Resources.Load("Materials/" + path)` — Unity Resources only, no
  mod folder is ever searched. A mod path returns null and `MaterialAllocator.Create(null)` throws
  in the static initializer (the black-screen crash). **Never call it with a mod path.**
- `MaterialAllocator.Create(Material src)` is `new Material(src)` — a full copy carrying the
  source's **shader and every property**. `WeatherOverlayDualPanner.TickOverlay` pans by property
  id `_MainTex` and, if present, `_MainTex2`; `SkyOverlay.DrawWorldOverlay` draws it on
  `MeshPool.wholeMapPlane` at the Weather altitude.
- `SkyOverlay.ForcedOverlayColor` is honoured by `SkyManager` (line 117: forced colour replaces the
  sky's overlay colour for that overlay). Anomaly's `WeatherOverlay_BloodFog` tints exactly this way.

So the custom look is: **copy vanilla's fog material, swap its two textures for ours, tint it.**

```csharp
[StaticConstructorOnStartup]                       // main thread, after textures load
public class RUT_WeatherOverlay_ScaldSteam : WeatherOverlayDualPanner {
    private static readonly Material SteamMat = BuildMat();
    private static Material BuildMat() {
        Material m = MaterialAllocator.Create(MatLoader.LoadMat("Weather/FogOverlayWorld")); // vanilla path: safe
        Texture2D t1 = ContentFinder<Texture2D>.Get("Weather/RM_ScaldSteam_A", false);       // mod textures
        Texture2D t2 = ContentFinder<Texture2D>.Get("Weather/RM_ScaldSteam_B", false);
        if (t1 != null) m.SetTexture("_MainTex", t1);
        if (t2 != null && m.HasProperty("_MainTex2")) m.SetTexture("_MainTex2", t2);
        return m;                                   // textures absent ⇒ vanilla fog look, never a throw
    }
    public RUT_WeatherOverlay_ScaldSteam() {
        worldOverlayMat = SteamMat; /* pan speeds as shipped */
        ForcedOverlayColor = new Color(0.88f, 0.97f, 0.97f);   // white with the cyan bleed
    }
}
```

Two `Textures/Weather/RM_ScaldSteam_{A,B}.png` are owed to the art pipeline: tileable, soft,
white-on-transparent billows with a faint cyan underside; the fog originals are the size/tiling
reference (extract via `reading-rimworld-graphics`). **Fallback is graceful by construction**:
with no textures the class is exactly today's shipped look. UNMEASURED and to be checked on the
first live run: whether vanilla's fog material declares `_MainTex2` (the `HasProperty` guard makes
the answer harmless either way), and that `ForcedOverlayColor` on a *world* overlay reads as a tint
rather than a wash at the shipped alpha.

A shader of our own (AssetBundle, `ContentFinder<Shader>.TryFindAssetInModBundles` — MEASURED to
exist in `ShaderDatabase.TryLoadShader`) is the v2 route for real depth/distortion; not needed
for v1.

**Sky colours** — native `WeatherDef.skyColors*` (MEASURED fields). Retune the shipped values
toward the sheet: day `sky (0.90,0.97,0.97)`, `overlay (0.80,0.92,0.92)`, saturation 0.8 so the
cyan water reads *through* the haze; night-side entries can stay (the Scald is substellar and never
sees night, but a valid set is required). `maxGlow` stays 1.

**Steam off the water — zero C#, the biggest visual win.** `TerrainDef.fleckData` +
`throwFleckChance` are consumed by `SteadyEnvironmentEffects` on every steady-tick cell (MEASURED);
Odyssey's `HotSpring` ships `AirPuff` at 0.25 with drifting velocity. Add to all six boil
terrains (`RUT_ScaldWater.xml`): `<fleckData><fleck>AirPuff</fleck> <velocityAngleRange>-30~30
<velocitySpeedRange>0.2~0.6 <scaleRange>2~4 <rotationSpeedRange>-20~20</fleckData>` and
`<throwFleckChance>0.35</throwFleckChance>` (deep) / `0.25` (shallow) — INVENTED; deeper water
breathes harder. The margin ring gets a gentle `0.08`. Sheet §9's "steam columns as the planet's
tallest soft structures" are the vents: `RUT_ScaldVent` is a `Building_SteamGeyser` and already
spouts vanilla's geyser effecter and `GeyserSpray` sound when the S4 gate is on.

**Vent-flash (optional, one small class).** `WeatherDef.eventMakers` + a `WeatherEvent` subclass
(MEASURED: `WeatherEventMaker` instantiates `eventClass(map)` at `1/averageInterval` per tick;
`WeatherEvent_LightningFlash` is the template — a `SkyTarget` override brightens the whole sky for
15–60 ticks and plays a sound). `RUT_WeatherEvent_VentFlash`: a brief white-out brightening
(`SkyColorSet` near white, saturation 1.05, no shadow vector) + `GeyserSpray` one-shot — the sheet's
"geyser percussion", felt map-wide. `averageInterval` 9000 (INVENTED ≈ every 4 in-game hours).
Gate: `RM_MechanicGates.Enabled("Scald.S1.flash")` checked in `FireEvent`.

**Sound.** `Ambient_Wind_Fog` stays as the loop until a bespoke "boil's breath" SoundDef lands
(a low continuous hiss-roll; real audio content, owed). `GeyserSpray` (vanilla, MEASURED) is the
percussion.

### 3.2 Rhythm — pulses, lock, clear spells

Keep the shipped two-state lock: **steam** (forced base) and **the still day** (Clear, MTB 96 h,
12–24 h). Nothing here needs a third state — the danger pulses through the pawn's *exposure*
(§3.3) rising and falling as they go out and come in, not through weather variety. The still day
becomes strategically loud once exposure exists: it is the window to salvage wrecks, cross the
shallows and work the vents without the clock running. Tuning stays INVENTED as shipped;
`WeatherPulseExtension` is untouched.

### 3.3 What it does — exposure, visibility, work and move

**`RUT_ScaldExposure` — the steam clock.** One HediffDef carrying
`HediffCompProperties_EnvironmentalExposure` (existing class, XML-only wiring), granted to every
flesh pawn on the map by a second permanent biome condition `RUT_ScaldSteamCarrier`
(`GameCondition_EnvironmentalWeather` with **only** `carrierHediff` set — its `ConfigErrors`
accept that, MEASURED — no `forcedWeather`, so it never fights the pulse lock).

```xml
<li Class="RimMandrake.EnvironmentalHazards.HediffCompProperties_EnvironmentalExposure">
  <onlyDuringWeather>RUT_ScaldSteam</onlyDuringWeather>   <!-- still day and roofs: clock stops -->
  <severityPerDayExposed>0.6</severityPerDayExposed>      <!-- INVENTED: ~1.7 days unprotected to the top stage -->
  <severityPerDayUnexposed>-0.35</severityPerDayUnexposed><!-- roofed/still: heals off in ~3 days -->
  <protectionStat>RM_ScaldProtection</protectionStat>     <!-- summed over worn apparel, 0..1 -->
  <minDriveFactor>0.08</minDriveFactor>                   <!-- Ban 3: gear never zeroes the clock -->
  <immuneThingDefs><li>RM_Noohm</li><li>RM_Shulla</li></immuneThingDefs>  <!-- §6 -->
</li>
```

Stages (INVENTED; labels are player-facing): **0.15 damp** — no effect, a warning line;
**0.35 scalded skin** — pain 0.15, manipulation −10%; **0.6 steam-burned** — pain 0.35, breathing
−30%, moving −20%, consciousness −10%; **0.85 boiled** — breathing −60%, consciousness −40%,
`lethalSeverity 1.0`. "Deadly without gear" means: a colonist who lives under the open sky here
dies in under two days; one who sleeps roofed and works outside in shifts limps along at stage 2;
one in a boil-suit (§5) can work a full day at the vents and come in clean.

`RM_ScaldProtection` — new StatDef cribbing `RM_WetBulbProtection` exactly (`ArmorRatingBase`,
`maxValue 1`, quality part). It is the *steam* stat; `RM_ArmorRating_Scald` stays the *damage*
stat for `RUT_Scald` hits (steam devils, §4 option b). Two stats, two jobs, both on the same garments.

**Visibility.** `accuracyMultiplier` 0.9 → **0.75** and `maxRangeCap` **24** (both native fields,
MEASURED) — steam thick enough to matter in a fight, still far from Fog's 0.5. **Move** stays 1.0
(the sheet: the air never slows a step; the water does). **Work**: no global work penalty —
the hediff stages carry it, so a protected pawn works normally.

## 4. The boiling water — danger model

**What actually happens, MEASURED** (`Verse/HediffGiver_Terrain.cs`): every 60 ticks, for a spawned
pawn whose race carries a giver set containing `HediffGiver_Terrain` (Core's `OrganicStandard`,
inherited by every animal and humanlike), if the cell's terrain has `burnDamage > 0` and
`Rand.MTBEventOccurs(burnIntervalTicks, 1, 60)` fires, it applies `DamageDefOf.Burn` for
**`Mathf.Max(burnDamage, 3)`** to a Bottom/Outside body part. Consequences for the shipped defs:

- The authored 1 (shallow) / 2 (deep) are **silently 3 in play** — the engine floors at 3. The
  *rate* still differs (mean one hit per 300 vs 240 ticks). Fix the labels, not the numbers: write
  `burnDamage 3` on the shallow terrains so the def says what it does (Ban 3: the *cost* stands;
  this states it honestly), and **`burnDamage 4` on the deep terrains** — ruled 2026-09-25 (§9
  ruling 9): depth bites harder. Odyssey's `LavaShallow` is 3 per 120 for scale.
- The damage is plain `Burn` → `armorCategory Heat` → **`ArmorRating_Heat` on worn apparel already
  reduces it.** So a vanilla devilstrand duster *is* a wading aid today; the `RUT_Scald`/
  `RM_ScaldArmor` "heat armor does nothing" premise applies only to the steam devil.
- `avoidWander` keeps idle pawns out; `extraNonDraftedPerceivedPathCost` (inherited from
  `WaterShallowBase`) makes the pathfinder prefer land. Neither stops a *swim* path
  (`KnownDangerAt` is edifice-only — `SCALD_MECHANICS_1` spike finding 4).

**Design — terrain burn is the water's mechanic, and it stays plain `Burn`/Heat.** Ruled
2026-09-25 (§9 ruling 2). It is vanilla, per-cell, immediate, already tuned, and already the
owner's "burns to touch"; heat armor is the wading protection, which is a real cost (devilstrand,
hyperweave, the boil-suit's own `ArmorRating_Heat`, the Royal Rind's). No retype to `RUT_Scald`:
`RM_ArmorRating_Scald` is the steam devil's stat only. Zero code for the water.

**The steam clock and the water clock are separate and additive**: wading in the steam takes burn
hits *and* runs the exposure clock. A pawn hauling salvage out of the shallows on a steam day is
the intended worst case; the same job on the still day is burns only.

**Fire.** Nothing ignites. `Burn` is `Flame`-parented but `HediffGiver_Terrain` calls `TakeDamage`
directly with no ignition (`ignitePawnsIntervalTicks` is unset on our terrains). The Scald never
sets a pawn alight.

## 5. The player's protections — gear, research, buildings, real costs

**The ladder, in the owner's words (typed, 2026-09-25):** *"Industrial research for a boil-suit,
but advanced vacsuit-types should be able to handle it too. And then there's the Royal Rind from
the fruit of the great Bole."* Three rungs, then: **Royal Rind gear** (§5a, biological, from the
Greentide), the **boil-suit** (Industrial research), and **sealed vacsuit-types** (Spacer, patched).

**This ladder is the heat column of the two-axis gear matrix** the owner ruled 2026-09-25
(*"vac/liquid (no air), extreme heat/cold (temp threat). Those are the two axes… Cheap tier,
moderate tier, then delux set (all the way to space)"*) — `exposure_gear_matrix_spec.md`, whose
§4a places each rung in its cell and adds the liquid column (air bladder, rebreather) this ladder
never had. The numbers below stand; the matrix cites them rather than restating them. The dive
clock on the Scald floor is the matrix's `RM_DiveProtection`, a separate stat from
`RM_ScaldProtection` (the steam clock) — the sealed items carry both.

Every row has a price; none reaches immunity (Ban 3). Protection numbers are INVENTED and sum
across worn apparel; the comp clamps to 1 and floors the clock at 8%.

| Protection | What it does | Cost | Where it comes from |
|---|---|---|---|
| **A roof** | stops the steam clock entirely (`onlyUnroofed` is the comp's own gate); exposure heals indoors | building it, staying under it | free, vanilla |
| **The still day** | clock stops map-wide for 12–24 h | waiting; ~4 days between | shipped lock |
| **`RUT_ScaldMargin` cove** | the one water with no burn | must be sited as an isolated cove (bridge authoring, owed) | shipped def |
| **`RM_Apparel_ScaldWrap`** (Neolithic) — hooded oil-waxed cloak, Shell layer, Torso/Neck/Head | `RM_ScaldProtection 0.45` (≈2× slower clock), `ArmorRating_Heat 0.30` | 30 cloth + 12 `RM_ScaldWalkerChitin` (the dive-hunt drop finally has a use); `Insulation_Heat −10` (it is hot inside), `MoveSpeed −0.15` | tailoring bench, no research |
| **Royal Rind gear** (§5a, **Neolithic** — ruled) — `RM_Apparel_RindCoat` (proposed name), Shell, Torso/Neck/Shoulders/Arms | `RM_ScaldProtection 0.60`, `ArmorRating_Heat 0.45`, plus **extreme heat and cold insulation** from the material (numbers INVENTED; steam protection sits between wrap and boil-suit) | the greatbole's fruit — a nasty grub fight or Fruitfall patience (`greatbole_harvest_spec.md` §2d, §3b); no research | tailoring bench, once the rind material exists |
| **`RM_Apparel_BoilSuit`** (Industrial) — sealed hood-and-suit, Middle+Shell, full body | `RM_ScaldProtection 0.85` (≈7× slower), `ArmorRating_Heat 0.55`, `RM_ArmorRating_Scald 0.60` (steam devils) | research **`RM_ScaldWorking`** (Industrial — **ruled**, §9 ruling 3; 1200 pts, prereq `ComplexClothing` INVENTED); 60 cloth + 20 chitin + 30 steel + 2 components; `MoveSpeed −0.35`, `Insulation_Heat −20`, Beauty −3, cannot wear with other Shell | machining table |
| **Odyssey vacsuit + helmet** — **ruled in** (§9 ruling 4) | patch `RM_ScaldProtection 0.35 + 0.30` and `RM_ArmorRating_Scald 0.4` onto `Apparel_Vacsuit`/`Apparel_VacsuitHelmet` (MayRequire Odyssey) — a sealed suit is a sealed suit; any later "advanced vacsuit-type" (a donor's sealed suit, a Spacer hardsuit) gets the same patch shape | already `MoveSpeed −1.25`; Spacer tech, `OrbitalTech` research | patch in TerminalBiomes |
| **Tending** | burns are ordinary injuries; `RUT_ScaldExposure` is not tendable, only waited out indoors | medicine, bed time | vanilla |

### 5a. The Royal Rind — the biological rung (ruled in; no def exists)

The owner named it (§5 quote) and `greatbole_harvest_spec.md` §3b already rules its three uses:
*protection against our own killing biomes — the Contagion, the Scald, the Miasma*; a vacuum
garment gated behind the expansion that supplies that mechanic; and a top luxury material. Its
price is stated there too: *"those grubs are NASTY to deal with"* — difficulty, not scarcity.

**What exists today (MEASURED 2026-09-25, `grep` of `src/` and `design/`):** no `RoyalRind`,
`GreatboleFruit` or rind-apparel def by any spelling; `RM_SapResin` and `RM_ToxinSealant`
(`src/RimMandrake/Greentide/Defs/ThingDefs/RM_Greentide_Items.xml`) are the greatbole's only
shipped products and are the shape to copy. The fruit item and the butcher-table recipe are owed
by the Greentide build (`greatbole_harvest_spec.md` §9 items 4–5), not by this spec.

**What this spec specifies (all names proposed, none shipped):**

- **`RM_RoyalRind`** — a stuff-capable material item (`Leathery` stuff category so vanilla leather
  apparel recipes accept it), rendered from `RM_GreatboleFruit` at the butcher table alongside the
  steaks and seeds. Lives in the Greentide mod (`RM_` tier — the greatbole is franchise-free).
  Carries, as **stuff stat offsets/factors**, the biome-protection stats: `RM_ScaldProtection`
  (this spec), `RM_WetBulbProtection` (`EnvironmentalHazards/Defs/StatDefs/`, exists) and a
  Miasma stat that does **not exist yet** — `RUT_MiasmaExposure.xml` sets no `protectionStat`
  (MEASURED 2026-09-25), so the Miasma gets one in the same shape when rind lands. ⇒ *any* garment made of rind protects,
  scaled by its coverage — one material, three biomes, exactly §3b's promise, and no bespoke
  garment is strictly required.
  **Ruled 2026-09-25:** rind clothing *"would render you immune to heat and cold to extreme
  levels"* — so the stuff also carries large `Insulation_Heat` and `Insulation_Cold` offsets
  (magnitudes INVENTED at build time; "extreme" means a rind-clad pawn is comfortable at the
  Scald's ambient and on the nightside alike). Temperature is insulation, not the steam clock:
  the clock is still `RM_ScaldProtection` under the clamp and the 8% floor (Ban 3).
- **`RM_Apparel_RindCoat`** — the one bespoke garment worth shipping: a full-coverage shell made
  only of rind, so a player who has fought the grubs once has a whole answer. **Neolithic**
  (ruled): tailoring bench, no research — the fight for the fruit is the whole gate. Table row above.
- **The vacuum use** is the vacuum end of the matrix's no-air axis (`exposure_gear_matrix_spec.md`
  §1; Odyssey-gated via `MayRequire`, and the franchise-free protection must not depend on it —
  `greatbole_harvest_spec.md` §3b's ban stands). On the matrix rind fills **both** moderate
  temperature cells (heat and cold) — ruling 7 below.
- **Rind stacks with the other rungs** under the same clamp and 8% floor; rind + vacsuit helmet
  and rind + boil-suit both clamp at 1.0. Ban 3 holds: it is a fight to get and never zeroes
  the clock.

Rind protects the steam clock as well as the wading burn, and its garments are Neolithic — both
ruled (§9 rulings 7–8).

Deliberately **not** offered: any drink, salve or bath that lowers exposure (Ban 1 patrol — a
"steam remedy" made from the lake would be the body made useful), and any building that
clears the steam from an area (Ban 5). A roof *is* the building answer.

Stacking check: wrap + vacsuit helmet = 0.75 → clock at 25%; boil-suit alone 0.85 → 15%;
boil-suit + helmet 1.0 clamps → floor 8%. Nothing goes below the floor by design.

## 6. Native immunity — the engine route

**Water (terrain burn) — XML only, MEASURED.** `HediffGiver_Terrain` is a list entry in the
`OrganicStandard` `HediffGiverSetDef`, reached via `RaceProperties.hediffGiverSets`; Ideology's
`Races_Animal_Special.xml` line 107 already overrides that list with `<hediffGiverSets
Inherit="False" />`. So: one new `RM_OrganicScaldNative` HediffGiverSetDef = `OrganicStandard`
with **`HediffGiver_Terrain` removed** and everything else copied (bleeding, hypothermia, heat,
the birthday chronics are irrelevant to 3-year animals but harmless), and on both native races:

```xml
<race> ... <hediffGiverSets Inherit="False"><li>RM_OrganicScaldNative</li></hediffGiverSets> </race>
```

Ships in `RM_ScaldFauna.xml`; the set def lives beside it in TerminalBiomes. No C#, no Harmony,
no per-tick check; the giver simply never runs for them. `ComfyTemperatureMax 95` already covers
`HediffGiver_Heat`. ⚠️ Any future Scald native (walkers, sails) takes the same line — put it in the
file header as the rule. Exact defs and files: §8 step 1.

Why not a gene: the natives are animals, and `hediffGiverSets` is the race-level switch the engine
already honours. **Note, not a build step (owner, 2026-09-25, §9 ruling 10):** a *humanlike*
Scald native would need a gene — the shape of `RM_Gene_Furnaceblood` (`TheRot/Defs/GeneDefs/`) or
`Jawa_MessImmunity.xml`'s patched-on gene (`UtinniPatches/Defs/GeneDefs/`) — and *"we don't have
any plans for that at this time."* Nothing is cast, nothing is owed; if one is ever cast, that gene
is where the water immunity goes.

**Steam (exposure clock)** — `immuneThingDefs` on the comp (§3.3) and on the carrier condition
(`HazardTargeting.Affects` reads both, MEASURED). Data, not a hediff, so nothing to save.

**Steam devil — NOT gated today.** `RM_WanderingVortexExtension` (MEASURED 2026-09-25) carries
`damageDef`, radii, intervals, `damageAmountRange`, `armorPenetration` and **no immune list**;
`RM_WanderingVortex.DamageCell` calls `TakeDamage` on every Thing in the cell with no species
check. So a shulla in a steam devil's path is scalded like anyone. Making natives immune here is a
small C# change, not XML: add `List<ThingDef> immuneThingDefs` / `List<PawnKindDef>
immunePawnKinds` to the extension and, in `DamageCell`, skip a `Pawn` for which
`HazardTargeting.Affects(pawn, PawnTargetKind.Flesh, ext.immuneThingDefs, ext.immunePawnKinds)`
is false. Then `RUT_SteamDevil.xml` lists `RM_Noohm`/`RM_Shulla`. Build order: step 3.

UNMEASURED and flagged for the live pass: `avoidWander true` on the water is per-terrain, not
per-race, so natives may refuse to *wander* onto their own lake even when immune (the shulla is
`waterSeeker true`, which pulls the other way). If they hug the shore, the fix is a terrain-level
question (a Scald-native `avoidWander false` variant is Ban-3-safe only if pathing cost still
deters colonists) — raise it then, not now.

## 7. Mod Settings toggles

All in `RM_TerminalBiomesMod.cs`'s existing Scald block (registered through `RM_MechanicGates`,
same `Scald.S*` key pattern; defaults = shipped behaviour; all-off leaves a working, plain biome):

| Toggle | Key | Off means |
|---|---|---|
| S1 — standing steam sky (exists) | `Scald.S1` | vanilla weather rotation |
| S1a — custom steam overlay art | `Scald.S1.art` | vanilla fog material (today's look), textures ignored |
| S1b — vent-flash sky pulses | `Scald.S1.flash` | no flashes, no percussion |
| S7 — steam exposure | `Scald.S7` | carrier condition stops granting; existing hediffs heal off (`RM_MechanicGateExtension` on `RUT_ScaldSteamCarrier`; `GameCondition_EnvironmentalWeather` needs the same `RM_MechanicGates.Enabled(def)` early-return `WeatherPulse` already has — 3 lines) |
| S7 — exposure rate | slider 0.25×–3× | multiplies `severityPerDayExposed` (read live through the gate predicate; needs a `rateKey` hook in the comp — or ship v1 without the slider and use the shared `hazardDamageMultiplier`, which the comp does not read today) |
| S8 — boiling water burns (**ruled allowed, default ON**, §9 ruling 5) | `Scald.S8` | Harmony prefix on `HediffGiver_Terrain.OnIntervalPassed` skips terrains tagged `RM_ScaldBurn`. Labelled *"world-affecting: the lake stops hurting"*; Ban 5 is honoured by the default, and the settings text says the sheet does not endorse turning it off |

Native immunity is a def, not a mechanic — no toggle.

## 8. Build order — small shippable steps

### Step 1 — native immunity to the water (XML only; two files, one new, one edited)

Every name below was read from the live source or the decompile on 2026-09-25, not guessed.

**New file** `src/RimMandrake/TerminalBiomes/Defs/HediffGiverSetDefs/RM_OrganicScaldNative.xml`
(the folder does not exist yet — TerminalBiomes has no `HediffGiverSetDefs/`; create it):

```xml
<HediffGiverSetDef>
  <defName>RM_OrganicScaldNative</defName>
  <hediffGivers>
    <!-- Core's OrganicStandard (Defs/Core/HediffGiverSetDefs/HediffGiverSets.xml) minus HediffGiver_Terrain -->
    <li Class="HediffGiver_Bleeding"><hediff>BloodLoss</hediff></li>
    <li Class="HediffGiver_Hypothermia"><hediff>Hypothermia</hediff><hediffInsectoid>HypothermicSlowdown</hediffInsectoid></li>
    <li MayRequire="Ludeon.RimWorld.Odyssey" Class="HediffGiver_VacuumBurn"><hediff>Hypothermia</hediff></li>
    <li Class="HediffGiver_Heat"><hediff>Heatstroke</hediff></li>
    <!-- the age/birthday givers (HeartAttack, Carcinoma, BadBack, Frail, Cataract, HearingLoss,
         Dementia, Alzheimers, Asthma, HeartArteryBlockage) are copied verbatim from OrganicStandard -->
  </hediffGivers>
</HediffGiverSetDef>
```

`OrganicStandard`'s full list (MEASURED, RimSage): Bleeding, Hypothermia, VacuumBurn (Odyssey),
Heat, **Terrain**, RandomAgeCurved(HeartAttack), and Birthday × Carcinoma, BadBack, Frail,
Cataract, HearingLoss, Dementia, Alzheimers, Asthma, HeartArteryBlockage. Copy all but Terrain.

**Edited file** `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_ScaldFauna.xml` — both
`ThingDef ParentName="AnimalThingBase"` blocks (`RM_Noohm`, `RM_Shulla`) currently declare **no**
`hediffGiverSets`, so they inherit `AnimalThingBase`'s `<hediffGiverSets><li>OrganicStandard</li>`
(MEASURED: `Defs/Core/ThingDefs_Races/Races_Animal_Base.xml`). Add inside each `<race>`:

```xml
<hediffGiverSets Inherit="False">
  <li>RM_OrganicScaldNative</li>
</hediffGiverSets>
```

`Inherit="False"` is required — without it the list *merges* and `OrganicStandard`'s
`HediffGiver_Terrain` still runs. Precedent: Ideology's `Races_Animal_Special.xml:107` (MEASURED)
and, for the plain declared form, our own `RM_BlueDesertFauna.xml` / `RUT_PropaneLakeFauna.xml`.
The two `PawnKindDef`s in the file are untouched. Put the rule in the file header: *every Scald
native takes `RM_OrganicScaldNative`.*

**Proof** (Desktop, minimal list + TerminalBiomes): `quicktest` on `RM_TheScald`, spawn one
`RM_Shulla` and one `RM_Noohm` on a `RUT_ScaldWater*` deep cell and a colonist beside them, step
3000 ticks; natives carry no `Burn` hediff, the colonist does. Control the instrument: the colonist
burning proves the terrain giver ran at all.

**Not in step 1:** the steam devil (§6 — needs C#, step 3) and the steam clock (`immuneThingDefs`
lands with the hediff in step 4).

### Steps 2–9

2. **Steam off the water + honest burn numbers** (XML, `RUT_ScaldWater.xml`, one live look):
   `fleckData`/`throwFleckChance` on the six terrains, `burnDamage 3` shallow / `4` deep (ruled).
   Deploy, `quicktest`, screenshot.
3. **Steam-devil species gate** (C#, ~10 lines): `immuneThingDefs`/`immunePawnKinds` on
   `RM_WanderingVortexExtension`, the `HazardTargeting.Affects` skip in `RM_WanderingVortex.DamageCell`,
   natives listed on `RUT_SteamDevil`. Proof: a shulla under a devil for its whole lifetime takes 0 damage.
4. **Exposure clock** (XML only, three defs): `RM_ScaldProtection` stat, `RUT_ScaldExposure`
   hediff (with `immuneThingDefs` = the natives), `RUT_ScaldSteamCarrier` condition wired onto
   `RM_TheScald.biomeMapConditions` by the same add-if-missing patch shape as the lock; the 3-line
   gate early-return in `GameCondition_EnvironmentalWeather`. Proof: colonist unroofed 1 day →
   stage 2; roofed → heals.
5. **Gear** (XML): wrap, boil-suit + `RM_ScaldWorking` research, vacsuit patch; art via artpipe
   (check `_artsrc/` first). Proof: boil-suit pawn at the vents all day ends at stage 0–1.
   **Royal Rind** waits on the Greentide's fruit item and butcher recipe; when those land, add the
   rind stuff stats and `RM_Apparel_RindCoat` (§5a) in the same XML pass.
6. **Overlay material** (C#, one class rewritten): the copy-and-swap material, `ForcedOverlayColor`,
   two textures; sky colour retune; accuracy/range. Proof: live look with the owner — this is the
   one step that needs his eyes.
7. **Vent-flash** WeatherEvent + eventMakers + `Scald.S1.flash` gate.
8. **Settings**: S1a/S1b/S7/S8 toggles, the S8 Harmony prefix, settings text.
9. Sound: bespoke breath loop when audio content exists; not blocking.

Steps 1, 2, 4 and 5 are XML and each is a same-day quicktest; 6 is the only render risk and it
degrades to today's look if a texture is missing.

## 9. Owner rulings (2026-09-25) and open questions

Ruled by question card, 2026-09-25 (decisions taken by card; the one typed line is quoted in §5):

1. **Unprotected in the steam: dead in under two days.** §3.3's clock stands as specced.
2. **Wading burns stay ordinary `Burn`/Heat.** §4 option (a) is the design; option (b) is dropped.
3. **The boil-suit is Industrial research.** §5's `RM_ScaldWorking` stands.
4. **Advanced vacsuit-types protect.** The Odyssey vacsuit patch in §5 stands, and any later
   sealed suit of that class takes the same patch.
5. **A lake-burn toggle is allowed, default ON.** Ban 5 is honoured by the default, not by
   refusing the toggle — §7 S8 ships.
6. **The Royal Rind (greatbole fruit) is a protection source.** Designed in §5a; no def exists yet.

Typed by the owner, 2026-09-25, answering this spec's four follow-ups — verbatim: *"To make
clothing out of the Royal Rind would render you immune to heat and cold to extreme levels, yes.
Neolithic, yes. Yes, deep water should burn harder. Yes, a native would need a gene, but we don't
have any plans for that at this time"*:

7. **Rind clothing protects the steam clock too, and grants extreme heat AND cold insulation** (§5a).
8. **Rind gear is Neolithic** — tailoring bench, no research; the ladder reads rind → boil-suit →
   vacsuit by tech level (§5) — on the gear matrix (`exposure_gear_matrix_spec.md` §4a) that is
   moderate → moderate → deluxe: rind and the boil-suit share a tier and differ in which cells
   they fill.
9. **Deep boil water burns harder: `burnDamage 4` deep, 3 shallow** (§4).
10. **A humanlike native would take a gene, not a race set — and none is planned.** A note in §6,
    not a build step.

### Open questions

None. Every question this spec raised has been ruled.

## 10. Evidence ledger (MEASURED / UNMEASURED)

MEASURED (RimSage decompile, 1.6 + Odyssey/Anomaly/Ideology, 2026-09-25): `HediffGiver_Terrain`
body incl. the `Max(burnDamage,3)` floor and `DamageDefOf.Burn`; `OrganicStandard` giver list;
`Races_Animal_Special.xml:107` `Inherit="False"` precedent; `Burn` DamageDef `armorCategory Heat`;
`MatLoader.LoadMat` = `Resources.Load`; `MaterialAllocator.Create(Material)` = `new Material(src)`;
`WeatherOverlayDualPanner` pans `_MainTex`/`_MainTex2`; `SkyOverlay.ForcedOverlayColor` consumed at
`SkyManager.cs:117`; `WeatherOverlay_BloodFog` sets it; `ShaderDatabase.TryLoadShader` falls back
to mod AssetBundles; `WeatherDef` fields `accuracyMultiplier`, `maxRangeCap`, `eventMakers`,
`skyColors*`, `maxGlow`, `weatherThought`; `WeatherEventMaker`/`WeatherEvent_LightningFlash` shape;
`TerrainDef.fleckData`/`throwFleckChance` consumed in `SteadyEnvironmentEffects`; `HotSpring`'s
fleck block; `GeyserSpray` SoundDef; `Apparel_Vacsuit` stats. Repo source read in full:
`RM_HediffComp_EnvironmentalExposure`, `GameCondition_EnvironmentalWeather` (+extension),
`RM_GameCondition_WeatherPulse` (+extension), `HazardTargeting`, `RM_MechanicGates`, the Scald
terrain/weather/condition/damage/armor defs, `RM_ScaldFauna.xml`, the Rot Sheen gear precedent.
Added 2026-09-25 (rulings pass): `AnimalThingBase` carries `hediffGiverSets: OrganicStandard`
(`Races_Animal_Base.xml`) and `RM_Noohm`/`RM_Shulla` declare none of their own;
`RM_WanderingVortexExtension` has no immune list and `RM_WanderingVortex.DamageCell` damages every
Thing in the cell; TerminalBiomes has no `HediffGiverSetDefs/` folder; no Royal Rind / greatbole
fruit def exists anywhere in `src/` or `design/`; `RM_SapResin`/`RM_ToxinSealant` are the
greatbole's only shipped products; the gene precedents are `RM_Gene_Furnaceblood` and
`Jawa_MessImmunity.xml`.

UNMEASURED (settle on the first Desktop live run): fog material declares `_MainTex2`;
`ForcedOverlayColor` tint strength on a world overlay; `avoidWander` vs immune water-seeking natives;
whether `ArmorRating_Heat` on apparel is applied to a Bottom/Outside terrain burn on an animal with
no apparel (it is not — animals wear nothing — but colonists' boots do count).
