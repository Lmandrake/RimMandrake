# Aurora research for Auroral Umbra (RUT_Umbra)

Researched 2026-10-19 (file dated 2026-10-20 per the order). Rule: we study, we do not copy code or textures.
Source tags: [LOCAL] = read from the installed game's Data folder or RimSage source mirror on 2026-10-19; [WEB] = URL cited, retrieved 2026-10-19 through search summaries or page fetch.

## 0. Bottom line

- **No mod found that draws a real aurora (curtains, ribbons) in RimWorld.** Only one candidate draws any aurora visual (Dynamic Atmosphere, "aurora ovals over the poles", which is a WORLD-view feature, unverified). We design our own.
- **Why our GameCondition cannot brighten the ground (confirmed in source [LOCAL]):** `SkyManager.CurrentSkyTarget()` blends every game condition with `SkyTarget.LerpDarken`, which takes `Mathf.Min` of glow and of each colour channel. A condition can never raise glow above the weather's value. Vanilla's own aurora asks for glow `max(sunGlow, 0.25)` but is clamped by that Min, which matches the wiki's remark that the vanilla aurora "does not actually affect the light level" [WEB https://rimworldwiki.com/wiki/Events, via search summary].
- **Three SkyTarget routes that do NOT darken-clamp (confirmed in the same source):** (1) the WeatherDef's own `skyColors*` and `Worker.CurSkyTarget` (plain `Lerp`); (2) `WeatherEvent.SkyTarget` (plain `Lerp`, `CurrentlyAffectsSky`); (3) a Thing with `CompAffectsSky` whose `CompProperties_AffectsSky.lerpDarken` is false (plain `Lerp`, `LerpFactor` 0 to 1, has auto fade-in/hold/fade-out). These are the brightening hooks.

## 1. What vanilla does [LOCAL, paths under C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data]

- `Core\Defs\GameConditionDefs\GameConditions_Misc.xml` line 163: GameConditionDef `Aurora`, class `GameCondition_Aurora`, `canBePermanent` true, `allowUnderground` false, `canAffectAllPlanetLayers` true, silenced by Anomaly `UnnaturalDarkness`.
- `Core\Defs\Storyteller\Incidents_World_Conditions.xml` line 38: IncidentDef `Aurora`, `IncidentWorker_Aurora`, baseChance 1.2, minRefireDays 15, duration 0.125 to 0.35 days. Worker only fires on a player home map that is not always-dark and where the aurora will not end soon.
- `Core\Defs\ThoughtDefs\Thoughts_Situation_Special.xml` line 157: `ThoughtWorker_Aurora` gives the "beautiful aurora" thought (+14 per the wiki).
- C# `Source/RimWorld/GameCondition_Aurora.cs` (RimSage mirror): eight colours (greens, teal, blue, violet/magenta) cross-faded by `curColorTransition`; 280 ticks per transition if timed, 3750 if permanent. `SkyTarget`: sky colour = `Lerp(white, colour, 0.075) * brightness`, overlay colour = `Lerp(white, colour, 0.025) * brightness`, glow = `max(sunGlow, 0.25)`, brightness = `max(0.73, sunGlow)`. **Vanilla draws no curtains at all; it only tints the sky by 7.5 percent** and returns 0 gaze/glow factors on always-dark maps (so vanilla aurora is explicitly disabled in always-dark places like ours).
- `Source/Verse/SkyManager.cs`: `MatBases.LightOverlay.color = curSky.colors.sky` is how the whole map is tinted; `curSkyGlowInt = curSky.glow` is the map glow floor; `UpdateOverlays` draws `SkyOverlay` objects from the weather worker and from `GameCondition.SkyOverlays(map)` with alpha = lerp factor.
- `Source/Verse/SkyOverlay.cs`: static helpers `DrawWorldOverlay(map, mat, altitude, layer)` (whole-map plane via `Graphics.DrawMesh(MeshPool.wholeMapPlane ...)` at `AltitudeLayer.Weather`) and `DrawScreenOverlay(mat, ...)` (camera-sized plane). `Source/Verse/WeatherOverlayDualPanner.cs`: the vanilla scrolling-texture overlay: one or two textures panned by `SetTextureOffset` each tick, colour set by `SetOverlayColor`. This is the proven pattern to subclass or imitate.
- Vanilla weather xml (`Core\Defs\WeatherDefs\Weathers.xml`) sets night sky colours per `skyColorsNightEdge`/`NightMid` (sky, shadow, overlay, saturation) - e.g. Clear night sky (0.482,0.603,0.682).
- Other Data hits for "aurora" (Odyssey `Script_SpaceSites.xml`, name rule packs, tales, romance words) are text only.

## 2. Candidate mods

| mod | author / id | versions | what it renders | source / licence | verdict |
|---|---|---|---|---|---|
| Dynamic Atmosphere | Astryl; Steam 3808191148 https://steamcommunity.com/sharedfiles/filedetails/?id=3808191148 | 1.6, 1.7 (per search summary) | "Shader-driven sky" for world view and colony maps; cloud shadows, rain, snow, lightning; "aurora ovals over the poles during an aurora" | No source link found. Page fetch failed (HTTP 429), so the above is from search summaries only. Page may carry a "removed" banner - UNVERIFIED either way. Skymods mirror https://catalogue.smods.ru/archives/483995 returned 403. | **Study #1, but only to see what it draws; cannot read its code unless it ships a DLL we may decompile for study (licence unknown, do not copy).** Related: Dynamic Planets https://steamcommunity.com/sharedfiles/filedetails/?id=3808196059 |
| [XND] Memorable Auroras (Continued) | XeoNovaDan original; continued by MLIE/emipa606; Steam 2270039395 https://steamcommunity.com/sharedfiles/filedetails/?id=2270039395 ; GitHub https://github.com/emipa606/XNDMemorableAuroras | 1.0 to 1.7 folders | Nothing visual. Harmony patch making the aurora thought last a day (+5) | **MIT** (fetched 2026-10-19) | Useful only as the mood hook; no rendering to study |
| Lighting and Weather Graphics Mod | Mazisky; https://rimworldbase.com/lighting-and-weather-graphics-mod/ | listed 1.7 but says not updated to 1.7; last update 2023-12-18; 1.4 via MediaFire | Darker, bluer nights and more colourful days via weather colour defs; no aurora | No source, no licence stated | Study #3 for night colour numbers only; stale |
| Realistic Lighting and Shadows / Tilt the Planet | listed at https://catalogue.smods.ru/archives/386478 , https://top-mods.com/mods/rimworld/graphics/14746-realistic-lighting-and-shadows.html | 1.6 | Sun/moon positions, shadows | not checked | Not aurora; skip |
| Ambient Light - RimWorld | Steam 3574400467 https://steamcommunity.com/sharedfiles/filedetails/?id=3574400467 | ? | ambient lighting (fetch 429, contents unread) | unknown | UNREAD - re-fetch later |
| Weird Weather Effects | itepastra https://github.com/itepastra/Weird-Weather-Effects | 1.4 folder | gameplay weathers (blizzard, fire rain...); rendering method not stated on page | no licence stated | Marginal; read its code for a custom WeatherDef/overlay example |
| SeasonalWeather | AaronCRobinson https://github.com/AaronCRobinson/SeasonalWeather | ? | weather def changes | unread | skip |
| Remove Weather Overlays / Toggles | YipNZ https://steamcommunity.com/sharedfiles/filedetails/?id=2471914077 ; https://www.nexusmods.com/rimworld/mods/286 | - | patch overlay drawing off | - | Compatibility warning: players may hide our overlay with these |
| Vanilla Weather Expanded | Vanilla Expanded team; https://github.com/Vanilla-Expanded | - | extra weathers/events; no aurora or starfield found in search | per repo | not an aurora source |

Top 3 to study: (1) Dynamic Atmosphere (only aurora visual, unverified), (2) vanilla `WeatherOverlayDualPanner` + `Fog`/`Rain` overlay defs in Core (we can read all of it, proven), (3) Memorable Auroras (MIT, mood hook) / Lighting and Weather Graphics (night colour set).

## 3. Local install check [LOCAL, 2026-10-19]

- Workshop folder `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100` holds 1270 entries. A grep of `About.xml` for "aurora" matched only `1874676885` (SZ_Atmospheric Events, author void, "castable atmospheric effects", 1.6 listed) - a pandora's-box-style spell mod, matched in About text; its defs were not read, so whether it draws an aurora is UNKNOWN. None of the mods above (Dynamic Atmosphere 3808191148, Memorable Auroras 2270039395) were checked by id directory; the grep only covered About.xml text, so absence from the grep does not prove they are not installed. NEXT for a follow-up: `ls ...\294100\3808191148 ...\2270039395`.
- Game `Mods` folder grep for aurora/northern light in xml failed under zsh glob (the `--include` form errored), so our own mods were not grepped here. Our weather code lives in `src/RimMandrake/WeatherSuite` and `src/RimUtinni/AshkarrWeatherSuite`; not read for this note.

## 4. What I could not find

- No Steam, Nexus, Ludeon-forum or Reddit page for a RimWorld mod that draws aurora curtains or a night-sky starfield (searches 2026-10-19: aurora/northern lights/starfield/animated sky, Steam + GitHub + forums + Reddit wording). The search tool returned Steam Workshop and a few GitHub hits only; direct Ludeon forum, Nexus and ModDB pages were not fetched successfully.
- Dynamic Atmosphere details beyond one summary sentence (page 429, mirror 403); no source repo located.
- No licence for any visual mod; assume all rights reserved.

## 5. Design appendix - our own aurora

Common layer, all designs: Umbra is permanent night, so no sun/dusk blending is needed. Sky glow floor and sky tint come from a **non-darken route** (section 0); curtains are drawn by our own `SkyOverlay` subclass imitating `WeatherOverlayDualPanner` (own code, own materials).

Brightening hook (pick one, same for all designs):
- H1 (preferred): put the glow/sky colour in the **WeatherDef** that Umbra's biome forces (weather's `skyColorsNightMid` etc. and a custom Worker if needed). Plain Lerp, can exceed vanilla night. Bounded: glow 0.18 to 0.35; keep sky colour channels ≤ 0.9.
- H2: an invisible map Thing with `CompAffectsSky` (`lerpDarken` false), one per map, animated by our code via the comp's LerpFactor/`StartFadeInHoldFadeOut`. Lets us pulse glow with the aurora.
- H3: `WeatherEvent` with `CurrentlyAffectsSky`; fine for pulses, awkward for permanence.

### Design A - Layered scrolling curtains (lowest risk, ship first)
- Class `RimUtinni.Umbra.AuroraOverlay : SkyOverlay`: 3 to 5 quads drawn by `Graphics.DrawMesh` via `SkyOverlay.DrawWorldOverlay` at slightly different altitudes (all on `AltitudeLayer.Weather` + small offsets) with additive materials (`Material` from a `ShaderDatabase` additive/transparent shader; shader name must be verified in the game's shader list before use - UNVERIFIED).
- Per-layer motion in `TickOverlay`: UV offset scroll (like DualPanner) plus per-curtain sinusoidal sway `offset.x += A*sin(2*pi*t/T + phase)` with T 900 to 3000 ticks, and alpha breathing `0.35 + 0.25*sin(...)`. Slow colour drift: lerp each layer's `material.color` through a palette (green 0.15,1,0.4 -> teal 0,1,0.75 -> violet 0.7,0.2,1 -> rose 1,0.3,0.6) over 3750+ ticks, phase-shifted per layer.
- Camera: use world-space plane so curtains pan with the map (feels distant but anchored); ground tint from H1.
- Assets (seamless-tiling horizontally, PNG RGBA, additive so black = transparent):
  - `Aurora_Curtain_A.png`, `_B.png`, `_C.png`: 1024x512 each (vertical streaky rays fading at top and bottom, different ray density)
  - `Aurora_Glow_Band.png`: 1024x256 soft horizontal band (the diffuse base layer)
  - `Aurora_Corona.png`: 512x512 radial "crown" for a zenith burst (optional)
  - `Aurora_Stars.png`: 1024x1024, sparse star points on black, no tiling seams (see D below for twinkle).

### Design B - Screen-space aurora with ground wash
- Same overlay, but curtains drawn with `DrawScreenOverlay` so they stay in the "sky" at a fixed screen position regardless of camera pan (looks like real sky above the horizon: top 40 percent of screen only, via a mesh of that height). Ground wash: a second world overlay, huge soft low-frequency blobs (colour = current curtain colour, alpha ≤ 0.10) slowly drifting, drawn additive so it lights terrain softly without per-cell glow grid work.
- Risk: screen-space overlays ignore zoom, so curtains look the same size at all zooms (fine for sky). Must check it also draws during pawn-frame/gravship cameras (vanilla uses layer `GravshipExclude`).
- Assets: Curtain_A/B at 2048x512 (wider because they stretch across the screen), `Aurora_Wash.png` 512x512 soft-noise (gray, tintable), plus stars as in A.

### Design C - Ground glow via real light sources
- Keep A for visuals; for the ground use a handful (4 to 12) of invisible `ThingWithComps` with `CompGlower` (`glowRadius` 14 to 20, `glowColor` set from the current aurora colour, rolled across the map in a slow wave) so cells get true coloured light and pawns/plants render lit. Colour changes through `CompGlower.GlowColor`/`UpdateLit`. Source of vanilla `CompGlower`: `Source/Verse/CompGlower.cs` [LOCAL].
- Cost: glow grid recalculation on every colour change - keep changes to ≤ 1 per 60 ticks and fewer lights; bounded by design (cap radius, cap count). Must be measured with the live game before trusting.
- No extra art beyond A.

### Star field (all designs)
- A static world overlay with `Aurora_Stars.png` (1024x1024, ≤ 400 stars, 1 to 3 px, 3 tints: white, pale blue, pale amber) at alpha 0.8, plus a second layer `Aurora_Stars_Twinkle.png` (same size, different stars) whose alpha oscillates 0.3 to 1.0 on a 200 to 600 tick sine with per-overlay phase. No daylight: keep celestial sun glow at 0 on Umbra (biome/world already dark).

### Recommendation
Ship A + H1 (glow in the forced WeatherDef) first, add the stars; test B's screen-space variant as an alternative skin; do C only if ground light under A+H1 looks flat. Every choice needs a live look (owner reviews visuals in game).

### Open questions before building
- Confirm additive shader name available in 1.6 (read `ShaderDatabase` via RimSage).
- Check whether Umbra's current WeatherSuite is a WeatherDef or only a GameCondition (not read here).
- Check the `GravshipExclude` render layer behaviour for our overlay.
