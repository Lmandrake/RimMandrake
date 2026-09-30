# LEANINGSCRUB_MECHANICS_BUILD_1 tranche 1 report

## Notes
RimSage connected (decompiled 1.6 source consulted for every seam below).
Brief said the csproj had no .cs yet — stale: `RM_LeaningScrubMod.cs` already ships (settings +
venomvine gate). csproj has `EnableDefaultCompileItems false` → every new .cs needs `<Compile Include>`.

## Seams (RimSage-verified)
- `WeatherDef.windSpeedFactor/windSpeedOffset` → `WindManager.WindManagerTick` (offset>0 remaps wind into [offset, max]).
- `JobGiver_Wander.TryGiveJob(Pawn)` — Stall freeze prefix returns a `Wait_Wander` job.
- `IncidentWorker.ChanceFactorNow(IIncidentTarget)` — consulted by `StorytellerComp.IncidentChanceFinal`; RaidEnemy does not override it.
- `CompPowerPlantWind.DesiredPowerOutput` (protected getter, `cachedPowerOutput`, wind capped 1.5).
- `CompBreakdownable.DoBreakdown()` public.
- `Plant.TickLong` → comps' `CompTickLong` then growth code that dereferences `Map` — so a comp must NOT destroy its plant inside CompTickLong (smother maturity runs from a MapComponent).
- `FloatMenuOptionProvider` subclasses auto-registered by `FloatMenuMakerMap`.

## Part 1 Stall/Gale — LANDED 145bcaa00
- `Defs/WeatherDefs/RM_LeaningScrub_Weather.xml`: RM_ScrubWind, RM_ScrubWindFog (ban 5: windSpeedOffset keeps every ordinary day windy; replace Clear/Fog in the biome), RM_Stall (windSpeedFactor 0, no ambient), RM_Gale (offset 1.5, Ambient_Wind_Storm, accuracy 0.8, move 0.9).
- Biome commonalities: ScrubWind 28 / ScrubWindFog 40 / Stall 3 / Gale 7 (DryThunderstorm, GrayPall, Overcast untouched).
- `RM_WindCalendar.cs`: Stall freeze (wild animals ≤ bodySize 0.5 get Wait_Wander), Gale deafen hediff `RM_GaleDeafened` (Hearing −0.5, Talking −0.35, unroofed only), turbine surge ×1.3 + breakdown MTB 3 days, raid ChanceFactorNow ×2 during Gale. All six knobs in Mod Settings.
- NOT built from Part 1: "stallhawk rises" (RM_Zellik behaviour) and "movers lit up" concealment penalty — both need the Part 8 concealment field to exist first; a penalty on a stat nobody has is a no-op.

## Part 9 Twitcher lash — LANDED 3a85e4347
- `RM_TwitcherLash.cs`: `RM_MapComponent_TwitcherLash` every 30 ticks walks spawned pawns (not downed/flying), checks own + 8 adjacent cells for a plant with `RM_CompLash`; poised & grown ≥0.5 → one RM_VenomvineScratch strike (8 dmg, AP 0.1, instigator = plant), then spent 2500 ticks. Ready-tick Scribed on the plant comp; inspect line "Poised" / "Spent, drooping: strikes again in …". Reusable on any plant def (biome-kit).
- Settings: on/off, damage ×, recovery ×. Droop retint art still a follow-on derive.

## Part 4 smother-craft — LANDED 8a6173ca9
- Items `RM_FuzzFiber` (RM_Fuzz now harvests it), `RM_SmotherBlanket` (recipe at hand/electric tailor bench: 40 fiber + 15 RM_SweetlineWool), `RM_DeadVenomvine` (patched into every refuelable fuelFilter that lists WoodLog). Placeholder textures = tinted vanilla Cloth/WoodLog; bespoke art owed.
- `RM_SmotherCraft.cs`: right-click FloatMenuOptionProvider on any plant carrying `RM_CompSmotherable` (4 forms inline + thicket by patch) → job carries a blanket, 600-tick throw, claim start tick Scribed on the plant comp, inspect countdown. `RM_MapComponent_SmotherClaims` matures claims (default 30 days) → plant removed, dead venomvine = yieldCount × growth (min 0.3).
- Not modelled: "burns long and hot" (refuelables count units, not heat); a visible blanket overlay on the stand.

## Part 2 Lean — LANDED 0a62c26a1
- `RM_TheLean.cs`: `RM_LeanExtension` on RM_LeaningScrub; `RM_MapComponent_Lean` locks a heading per map (Scribed). Scent: JobGiver_AnimalFlee postfix — wild non-predator flees a humanlike standing upwind (≤45° of downwind, range 16). Vanilla wild animals never flee people, so this is new behaviour, not a multiplier. Fire: Fire.TrySpread prefix — 50% of spreads pick only downwind adjacent cells, else vanilla.
- Spec wording "hunt from upwind or spook" is physically inverted; built as scent-carries-downwind (approach from downwind to stay unsmelt).
- Not built: windbreak calm wakes (feed ripple/fog-harvest, which don't exist), predators hunting by scent.
- Legibility gap for the owner: nothing shows the heading (engine plant sway is not directional); a readout would be an instrument under the trim law, so left as a question.

## Status
Tranche 1 done: parts 1, 9, 4, 2 landed. Build 0 errors after every part; selftests 76/78 each time (only the known selftest_deployed_biome_refs failure + 1 unmeasured). Not deployed, not live-tested.

## Remaining (parts 3, 5, 6, 7, 8 + leftovers) — not attempted, why
- Part 3 vaporator + V-blight: a new building (needs art), a research/discovery hook tied to the Part 8 dead-farmstead ruins, an owned crust TerrainDef + capped/healing cone terrain morph, and the animals-raid-the-oasis job targeting. Largest remaining piece; its "taught by a ruin" half depends on Part 8.
- Part 5 calling-pyre + fire-stamping giants: fire census MapComponent + fire-keyed mental state on the thunderstep herd (RSW_ShrublandGiant lives in RimStarWars, so the RM-tier herd species must be settled first), roofed-fire exemption; the Ideology ritual + three precepts is a RitualBehaviorDef/PreceptDef authoring job on top.
- Part 6 ripple concealment: a stat/hit-chance seam reading plant cover + weather; also unblocks Part 1's two leftovers (Stall "movers lit up" penalty, stallhawk rising).
- Part 7 soundscape: needs SoundDefs over audio clips (no clips chosen/imported); the Stall already goes silent (no ambientSounds).
- Part 8 inhabited injections: FOUNDRY set-piece list + GenStep/PlacedSetPieces authoring.
- Leftovers: blanket overlay graphic on a smothered stand; bespoke art for fuzz fiber / smother-blanket / dead venomvine; twitcher droop retint.
