# GREENTIDE_MECHANICS_1 — C# mechanics kit spec (engine mapping)

Drafted 2026-09-11 against the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_greentide.md` (§4b, §4c, §5, §7b, §8b, Owed)
and the RULED comp kit in
`design/Jawa/worldbuilding/alpha_family_source_review.md` §4 (owner, 2026-09-11:
all six RM_ comps IN; build item `ALPHA_MECHANICS_KIT_1`). This spec maps the
sheet's mechanics onto the engine — it invents no lore. Anything marked
**INVENTED** is a tuning parameter this spec had to pick a starting value for;
anything marked ❓ is an engine claim not verified against source and must be
checked before build.

**Source verification basis**: claims below marked *(verified)* were read from the
RimSage source index this session (`mcp__rimsage__search_source` /
`read_csharp_symbol`). ⚠️ That index returned no hits for Odyssey-era systems
(no lava-damage terrain, no falling-tree machinery), consistent with a 1.5-era
decompile — every "vanilla has no X" claim below is therefore "no X **in the
indexed source**" and carries an implicit ❓ against the live 1.6 assembly.
Re-run the named searches against the current game DLLs before spending C#.

**Naming**: generic mechanisms are `RM_` (`RimMandrake.*` namespaces); Greentide
content defs exposing them are `RUT_` (`RimMandrake.Utinni.*`). Per the ruled §4
resolution, one C# implementation per mechanic, tuned per-biome by XML only.

**Two standing anchors used throughout**:

- `BiomeDef.biomeMapConditions : List<GameConditionDef>` *(verified,
  `Source/RimWorld/BiomeDef.cs:131`)* — vanilla applies a list of permanent
  GameConditions to every map of a biome, from XML alone. This is how the
  Greentide's standing conditions (wet-bulb, the Roil lock) attach with zero
  bespoke bootstrap code.
- `GameCondition` virtuals *(verified, `Source/RimWorld/GameCondition.cs`)*:
  `ForcedWeather()` (line 345), `TemperatureOffset()`, `AnimalDensityFactor(Map)`,
  `PlantDensityFactor(Map)` — everything the ruled
  `RM_GameCondition_EnvironmentalWeather` needs is a supported virtual, not a fight
  with the engine.

Scoreboard: **12 mechanics** · **4 ruled-comp reuses** (EnvironmentalWeather ×2,
BiomeGlowMultiplier, PeriodicAreaAttack, + ActiveGasEmitter optional) · **9 new
RM_ classes** (1 L, 6 M, 2 S) · XML-only content on top of all of it.

---

## M1. Wet-bulb overwhelm + the gear tree (§4b)

**Player experience.** At 45 °C in saturated air your pawns cook even under
shade — a "Wet-bulb overwhelm" hediff ramps toward collapse regardless of roof,
because sweat does nothing here. Sealed/wicking gear slows it; a blower-dried
room stops it entirely. The desert's shade-and-cooling kit is useless; the
trader sells you the other tree.

**Engine route.** New `RM_GameCondition_WetBulb : GameCondition`, attached via
`biomeMapConditions` *(verified)*. On interval, ramps severity of a hediff
(`RUT_WetBulbOverwhelm`, XML: escalating consciousness/moving stages → collapse)
on every pawn on the map, cribbing the severity-adjust shape of
`HediffGiver_Heat.OnIntervalPassed` *(verified, `Source/Verse/HediffGiver_Heat.cs`
— `HealthUtility.AdjustSeverity` driven by ambient temp vs
`pawn.SafeTemperatureRange()`)* but with three gates the vanilla giver lacks:
(1) severity gain × `(1 − RM_WetBulbProtection)`, a new `StatDef` summed from
apparel; (2) zero gain in a "dried" room (registered by M2's blower comp in a
per-map component); (3) species exemption list (the elevated-thirst races and
native fauna are immune — XML list on the condition def).

*Why not a ruled comp*: `RM_GameCondition_EnvironmentalWeather` damages
**unroofed** pawns on an interval — wet-bulb is the exact inverse (roof doesn't
help), is a severity ramp not damage, and needs the stat + dried-room gates.
A new condition class is honest; it shares no field semantics with the ruled one.

**Content (RUT_, XML only)**: `RUT_WetBulbOverwhelm` HediffDef;
`RM_WetBulbProtection` StatDef (RM_ — the desert's opposite-kit gear and any
future wet biome want it too); 2–3 `RUT_` apparel defs (wicking wrap, sealed
suit, dry-hood) carrying the stat. **INVENTED**: severity rates (start:
collapse in ~1.5 in-game days unprotected, indefinite hold at protection ≥0.8);
stat name.

**Effort**: **M** (condition + stat part + room gate). Gear XML: S.
**v1: ships** — this is the biome's survival thesis.

## M2. The dry-air blower (§4b)

**Player experience.** A fueled/powered doorway machine gushing hot dry air
downward: plants stop growing into that doorway, animals shy off, and the room
behind it reads "dried" — the wet-bulb clock stops indoors. When it runs out of
fuel, the green notices within hours. Every Greentide structure shimmers at the
door.

**Engine route.** `RUT_DryAirBlower` ThingDef (building) composed of vanilla
comps — `CompPowerTrader`/`CompRefuelable` (XML choice), `CompHeatPusher`
*(verified, `Source/Verse/CompHeatPusher.cs`)*, `CompFlickable` — plus **one new
comp**, `RM_CompDryFieldEmitter : ThingComp`:

1. **Dries the room**: registers its room (via `Thing.GetRoom()`) in
   `RM_MapComponent_DryRooms`, which M1's condition reads. Room-based, so one
   blower per structure suffices (matches the sheet's "dries the room behind it").
2. **Repels encroachment**: writes suppression into the
   `EXPLOSIVE_PLANT_GROWTH_1` engine's suppression grid over a doorway arc
   (**INVENTED**: radius 3, 90° arc facing outward). The growth engine is the
   parent item; this kit only defines the write. "Dry heat is the one alien
   thing" — the blower and M8's grazing write into the same grid.
3. **Repels animals**: ❓ no verified vanilla "wild-animal avoid grid" —
   vanilla's `AvoidGrid` is faction-pathing, and whether wild fauna consult
   anything similar needs a source read before build. Fallback that needs no
   engine favor: a periodic scan (interval 250 ticks) applying a short
   `RUT_DryAirAversion` hediff (flee-inducing mental state) to non-immune wild
   animals in the arc. Decide at build time, whichever the source supports.

*Why not a ruled comp*: nothing ruled touches rooms or the growth grid;
`RM_CompActiveGasEmitter` emits things, it doesn't suppress them.

**Effort**: **M**. **v1: ships** (load-bearing for M1's dried-room gate; the
sheet's "fire is not the tool" makes it the only defense line).

## M3. Scald damage + steam devils (§4c)

**Player experience.** A wandering white column of boiling vapor spins off the
river — a steam devil. It scalds what it crosses (a wet burn that armor built
for flame doesn't stop), knocks weak trees down, and drags the ground-fog up
into itself. Rare, visible from far off, and it does not care about your walls'
flammability.

**Engine route.** Two pieces:

- **Scald**: `RUT_Scald` DamageDef — XML only. `armorCategory` is a def field
  *(verified, `Source/Verse/DamageDef.cs:77`)*: point it at a new
  `RM_ScaldArmor` DamageArmorCategoryDef so heat/flame armor stats don't apply
  (only dedicated wet-kit gear grants the new armor stat). Not a Flame-class
  damage → no ignition, so "ignores flammability" is free. ❓ verify no
  DamageWorker override is needed for the armor stat to resolve (vanilla wires
  armorCategory → armor StatDef; confirm the linkage field on
  DamageArmorCategoryDef before build).
- **Steam devil**: `RUT_SteamDevil` ThingDef with new class
  `RM_WanderingVortex : ThingWithComps`, cribbed structurally from vanilla
  `Tornado` *(verified, `Source/RimWorld/Tornado.cs` — `Tornado : ThingWithComps`;
  wandering-cell logic, area damage, sustainer, fleck column all live there —
  read it fully at build time, reimplement in our own words per the license
  posture)*. Ours parameterizes damage def (Scald), wander speed, lifetime, and
  fires M6's shared fall routine on trees below a health/size threshold
  (**INVENTED**: trees under 50% max HP or non-giant defs fall). Spawned by an
  IncidentDef weighted into the biome and, rarely, by the Roil condition itself.

*Why not a ruled comp*: the vortex is a moving Thing, not a hediff-carrier or a
condition; `RM_HediffComp_PeriodicAreaAttack` assumes an afflicted pawn.
Tornado is the correct vanilla crib and vanilla already proves the shape.

**Effort**: **M** (vortex). Scald XML: S. **v1: ships** (the biome's signature
event; also the named carrier of the Scald def every other piece references).

## M4. The Roil — standing ground-fog weather (§4c)

**Player experience.** A hot, roiling, waist-deep fog hides the floor while the
canopy stands clear. Shooting past a few tiles is guesswork, movement is
cautious, and the things that hunt inside it (M7, M5) are invisible until they
aren't. It is always on; its absence (M5's Breaklight) is the event.

**Engine route.** Almost entirely reuse + XML:

- `RUT_RoilWeather` WeatherDef — `accuracyMultiplier` and `moveSpeedMultiplier`
  are native WeatherDef fields *(verified, `Source/Verse/WeatherDef.cs:47–49`)*
  (**INVENTED**: accuracy 0.7, move 0.95). Overlay: new
  `RM_WeatherOverlay_GroundFog` cribbing `WeatherOverlay_Fog :
  WeatherOverlayDualPanner` *(verified, `Source/RimWorld/WeatherOverlay_Fog.cs`)*
  with the panner textures authored bottom-heavy so the fog reads as hugging the
  floor while treetops draw above it. ❓ true per-layer occlusion ("hides the
  floor but not the canopy" as a mechanic rather than art) has no verified
  vanilla hook — v1 ships the *visual* ground-hug + flat accuracy penalty; a
  real height-layered visibility system is deferred, likely never (the sheet's
  wording is experiential, not a fog-of-war demand).
- **The lock**: reuse ruled **`RM_GameCondition_EnvironmentalWeather`** as a
  permanent `biomeMapConditions` entry *(both hooks verified above)* — weather
  forced to `RUT_RoilWeather` via `ForcedWeather()`, no damage fields set. Its
  recheck already fights vanilla's `WeatherDecider` rotation (that is what the
  donor's AcidRain did; ours does it as a supported virtual instead).
- **The steam deflects the sun**: reuse ruled **`RM_HarmonyPatch_BiomeGlowMultiplier`**
  with `RM_BiomeGlowMultiplierExtension { multiplier: 0.75 }` (**INVENTED**
  value) on the Greentide BiomeDef — permanent bright-overcast, "livable for
  anything that needs moisture," and vanilla's darkness chain prices it for free.
- **Underlight rain** (ambient drip): cosmetic — rain sound layered into the
  biome's `soundsAmbient` *(verified, `Source/RimWorld/BiomeDef.cs:59`, consumed
  by `AmbientSoundManager`)* plus drip flecks in the Roil overlay. No mechanic,
  no C#. The "fire answer stays dead" is enforced by the flora roster's
  flammability ban (§6.3), not by code here.

**Effort**: **S** (one overlay class + XML; the two heavy pieces are ruled kit).
**v1: ships.**

## M5. Breaklight — clarity as the disaster (§4c)

**Player experience.** The inversion breaks: the fog blanket lifts at once and
the biome stands naked under the full +45° sun for a few hours. Temperatures
spike, the wet-bulb clock pauses but a dry-heat clock starts, accuracy snaps to
full — and everything wild heads for shade.

**Engine route.** Reuse ruled **`RM_GameCondition_EnvironmentalWeather`** as a
rare IncidentDef-triggered condition preset: forces `RUT_BreaklightClear`
WeatherDef (clear, harsh palette), `tempOffset` +12 °C (**INVENTED** — stacks
on the ~45 °C ambient into vanilla heatstroke territory via the untouched
`HediffGiver_Heat`), duration 3–8 hours (**INVENTED**). Two hookups:

- **Glow override**: the biome's 0.75 multiplier must read 1.0 during
  Breaklight. Small extension **to the ruled patch** (not a new comp): the
  glow-multiplier postfix checks the map for an active condition carrying
  `RM_GlowMultiplierOverrideExtension` and prefers its value. One extension
  class, benefits every future dark biome with a "clearing" event.
- **Wet-bulb pause**: M1's condition reads Breaklight's presence and idles
  (dry air — the multiplier switches off, exactly the sheet's physics).
- ❓/deferred: "everything scrambles for shade" as visible animal AI (a
  seek-shade JobGiver during the condition) — v1 ships the heat + weather +
  light snap only; the scramble is flavor AI, deferred.

**Effort**: **S** (preset XML + the one override extension). **v1: ships**
(minus the scramble AI).

## M6. Three-feller tree fall (§4, §5)

**Player experience.** Trees here fall — a creak, a crack, and a giant comes
down across ten tiles, crushing what it lands on and leaving greenwood to
haul. Gnawers chew them down, overgrown giants crack under their own speed,
and a Shatterer puts one through your wall on purpose. Distant crashes are the
biome's percussion; a fall next to you is a hit.

**Engine route.** No falling-tree machinery exists in the indexed source
(searched `FallingTree|TreeFall`; only `MinifiedTree` transport exists —
*verified absence, with the 1.5-index ❓ above*). Build once, pay three times,
exactly as the sheet orders:

- **`RM_TreeFallUtility.FellTree(Plant tree, Rot4 dir, FallCause cause)`** —
  static routine: pick fall direction (away from feller / random), deal Blunt
  damage in a length-scaled swath (**INVENTED**: length = plant size × k,
  damage 30–120 by tree class), spawn `RUT_Greenwood` items along the swath
  (giants also drop `RUT_Hardwood` at the heart cells — §7's price-gap story),
  destroy the plant, play crash sound + dust flecks. Distant-crash ambience:
  the sound def alone at map volume does this for free.
- **Feller 1 — cracked from within**: `RM_CompCrackFall : ThingComp` on giant
  tree defs — past a growth/age threshold, MTB roll per day
  (**INVENTED**: MTB 8 days at full growth) → creak warning sound, then
  `FellTree` a few hundred ticks later.
- **Feller 2 — shattered from the side**: the Shatterer's tree-breaking rides
  ruled **`RM_HediffComp_PeriodicAreaAttack`** — its per-`ThingCategory`
  multiplier table (plants ×N, buildings ×n) is already the right shape; a
  rampaging/rutting Shatterer gains the hediff, and any tree its aura drops
  below the threshold routes through `FellTree` (small hook: the fall utility
  subscribes via a damage-watcher on tagged tree defs, or the comp exposes an
  on-kill callback — decide at build against the comp's final shape in
  `ALPHA_MECHANICS_KIT_1`).
- **Feller 3 — gnawed from below**: a Gnawer `ThinkNode_JobGiver` issuing a
  chew-at-base job (fresh ~30-line implementation, same shape as the donor's
  `JobGiver_Mine` per the review's "write it directly per creature" note),
  ending in `FellTree`. The Gnawer *creature* rides the roster pass; the job
  class ships here so the roster only supplies XML.

**Effort**: **M** (utility + crack comp + job; feller 2 is ruled kit + a hook).
**v1: ships** — §5 says "trees fall constantly"; the biome doesn't read without it.

## M7. Lunger ambush (§4, §6.6)

**Player experience.** Deep water is never safe. The Lunger is submerged and
literally invisible until the lunge — crossing a river is the scariest routine
act in the biome, and bridges/causeways are precious because of it.

**Engine route.** Reuse vanilla invisibility wholesale:
`HediffComp_Invisibility` *(verified, `Source/Verse/HediffComp_Invisibility.cs`;
`InvisibilityUtility.GetInvisibilityComp`, renderer integration in
`PawnRenderer` all stock)* — the Revenant/Sightstealer machinery. ⚠️ its ctor
calls `ModLister.CheckRoyaltyOrAnomaly` *(verified, line 153)* — fine on the
owner's DLC-complete install, but it makes the Lunger def Anomaly-or-Royalty
gated; acceptable, note it in the mod's About.

New small comp `RM_CompAquaticAmbusher : ThingComp` on the Lunger kind:
while the pawn stands on deep-water terrain and has no melee target →
`BecomeInvisible()`; target acquired in lunge range (**INVENTED**: 5 cells) →
`BecomeVisible()` + a lunge job (fast move-and-melee; first strike gets a damage
multiplier, **INVENTED**: ×1.5). Hunting AI stays vanilla predator ThinkTree —
the comp only manages visibility + the opener. §6.6's "no safe standing water"
is then a spawn rule (Lunger density on water cells), not code.

*Why not a ruled comp*: `RM_Ability_TargetedHediffAffliction` afflicts targets;
this manages the caster's own stealth state — different shape.

**Effort**: **M** (small comp, but water-state + job wiring needs live testing).
**v1: ships** (a hard ban depends on it).

## M8. Churnmud: swallow + mire (§8b)

**Player experience.** The ground between the giants is torn mud: brutally slow,
it swallows what you drop (dig it back out), and the unlucky pawn mires —
slowed, then stuck, until pulled free. Under the Roil you can't see which mud
is the hungry kind.

**Engine route.** `RUT_Churnmud` TerrainDef (high pathCost — XML) plus two
small new pieces (no verified vanilla harm-on-terrain machinery in the index —
❓ re-check the 1.6 assembly for Odyssey terrain-hazard hooks first; if 1.6
added one, use it and delete piece 1):

1. **Mire**: `RM_MapComponent_TerrainMire` — interval scan of pawns standing on
   terrains carrying `RM_MireExtension` (DefModExtension: severity/tick,
   escape-chance curve); applies escalating `RUT_Mired` hediff (moving penalty →
   immobilized). Cleared by leaving the terrain or by an adjacent pawn's
   pull-free job (reuse vanilla rescue/carry interaction shape ❓ — verify a
   crib exists, else a simple custom JobDef). Animals native to the biome are
   immune (XML list).
2. **Swallow**: `RM_MapComponent_MudSwallow` — items lying on mire-extension
   terrain for N ticks (**INVENTED**: ~2500, so battlefield drops vanish but
   hauling is safe) despawn into a per-cell buried registry (Scribe-saved); a
   `RUT_DigOut` designation + job spawns them back with work scaled to time
   buried (**INVENTED**). Sheet's "swallows dropped items (dig them back out)"
   verbatim — nothing is destroyed.

Both components are generic RM_ (extension-driven) — the Webwork's quicksand
inventory note is the second customer.

*Why not a ruled comp*: nothing ruled touches terrain-standing effects; the
donor's quicksand was worldgen-only (review §3 says its runtime sinking was
never found).

**Effort**: **M** (two small components + jobs). **v1: mire ships; swallow
ships in minimal form** (bury + dig, no decay while buried).

## M9. Root causeways — map-gen (§8b)

**Player experience.** The giants' roots are the roads: raised, firm, fast
lanes radiating from each great tree, winding over hidden mud. All natural
pathing follows them; so do the fights.

**Engine route.** New `RM_GenStep_RootCauseways : GenStep`, ordered after
terrain gen (`GenStep_Terrain` *(verified, `Source/RimWorld/GenStep_Terrain.cs`)*
is the anchor; `GenStep_TerrainPatches` shows the post-pass pattern): pick
Greatbole/giant-tree anchor points, trace 3–6 wandering spline paths outward per
anchor (**INVENTED** counts), paint `RUT_RootCauseway` TerrainDef (low pathCost,
raised sprite) in 1–2 wide lanes over the churnmud basins; connect nearest
anchors so the network spans the map. Pathing preference is then free — vanilla
pathfinding already prefers cheap terrain; no AI work.

Deferred, explicitly: **"the roads slowly move between visits"** — needs
persistent map mutation over absences and interacts with the growth engine's
save state; park it on `EXPLOSIVE_PLANT_GROWTH_1`'s v2 list, not here.

**Effort**: **M**. **v1: ships** (static network; movement deferred).

## M10. Grazing suppresses encroachment (§4)

**Player experience.** A penned herd of Brakes is a living defense: where they
graze, the green stops crawling toward your door. Lose the herd, and the jungle
notices within days.

**Engine route.** A hook, not a system: grazing events write suppression into
the **same `EXPLOSIVE_PLANT_GROWTH_1` suppression grid** the blower (M2) writes.
Implementation is a Harmony postfix on plant-consumption (❓ exact seam —
`Plant` ingestion/`FoodUtility` path; identify the single choke-point method in
source at build time) recording cell + radius 1 suppression with a decay of a
few days (**INVENTED**). The kit item owns the postfix; the growth engine owns
the grid and its decay math. Zero new defs — any plant-eater suppresses, which
is exactly the sheet's ecology ("a jungle that must be eaten").

**Effort**: **S** (given the parent engine exists — hard dependency, build
after it). **v1: ships with/after `EXPLOSIVE_PLANT_GROWTH_1`.**

## M11. The silence cue (§9)

**Player experience.** The loudest biome on the planet goes quiet moments
before the apex predator arrives. Players learn to fear a silent jungle.

**Engine route.** `RM_MapComponent_SilenceCue`: predators tagged with
`RM_SilenceAuraExtension` trigger, on hunt-job start within player-home range, a
fade-out of the biome's ambient sustainers for a window, then restore.
`AmbientSoundManager` spawns those sustainers from `Biome.soundsAmbient`
*(verified, `Source/RimWorld/AmbientSoundManager.cs:58`)* — but they are
camera-scoped, and ❓ no verified route to duck a live `Sustainer`'s volume
externally (end-and-respawn may pop audibly; a volume ramp needs a source read
of `Sustainer`/`SoundParams`). Honest sizing: an audio-polish mechanic with an
unverified seam.

**Effort**: **M**. **Deferred to v1.1** — the only sheet mechanic deferred
whole. It is §9 *artistic theme*, not §5 *always true*; no other mechanic
depends on it, and shipping it badly (popping audio) reads worse than absence.

## M12. The Greatbole — mineable living tower (§7b)

**Player experience.** A terrain-scale living tree you dig INTO: chambers of
heartwood, naturally roofed, superbly insulated, invisible from outside. And it
heals: unclaimed tunnels regrow shut over days — a creak of warning, then the
tree crushes and ejects whatever stands in the way — unless you paint the walls
with toxin sealant. Wild boles come pre-tunneled, and something still lives
there.

**Engine route.** Not a Plant at all — a **structure of mineable edifices**
with a component-driven life:

- `RUT_GreatboleHeartwood` ThingDef: `mineable = true` *(verified,
  `Source/Verse/ThingDef.cs:280`)*, `building.mineableThing = RUT_Hardwood`
  *(verified, `Source/RimWorld/BuildingProperties.cs:267`)* — vanilla mining,
  designations, yields, roofing all free. The bole's footprint spawns as a
  blob of these (map-gen: part of M9's GenStep picking bole sites) under a
  natural-roof patch, plus a `RUT_GreatboleCore` marker building holding the
  tree's identity and its component state. Exterior art: an over-sized
  `RUT_GreatboleCrown` drawn above (multi-cell visual, no collision beyond the
  heartwood blob) ❓ — verify large-graphic draw route (building drawSize vs a
  skyfaller-style overlay) at build.
- **`RM_MapComponent_LivingRegrowth`** (generic RM_ — any future living-dungeon
  wants it): per registered bole, on a slow interval, pick interior cells that
  are empty, enclosed by the bole's footprint, and **not sealed** → schedule
  regrowth (days, **INVENTED**: 3–6 per cell). If the cell holds a pawn/item/
  building when regrowth lands: creak warning (message + sound, ~1 in-game hour
  ahead), then periodic Blunt crush damage and forced ejection to the nearest
  open cell (pawns pushed, items popped, player buildings damaged then
  destroyed) — "the tree pushing you out like a splinter," implemented as
  direct per-cell effects, no hediff needed.
- **Sealant**: `RUT_ToxinSealant` — a paintable per-cell mark (cheapest honest
  route: a floor-like TerrainDef applied over the chamber floor by a normal
  construction job consuming the sealant item; the component treats
  sealant-floored cells as unclaimed-by-the-tree). A lapsed job = unsealed
  cells = "your storeroom is being slowly digested," exactly the sheet.
  **INVENTED**: sealant is crafted from §7 sap/resin — flag to owner (card 2).
- **Wild-bole dungeons** ("something painted its chambers first, and still
  lives there"): map-gen variant — pre-carved chamber layouts, part sealed,
  spawned occupant. Layout + occupant content rides the roster/template passes;
  the *capability* (carve + seal at gen time) ships here.

*Why not a ruled comp*: nothing ruled owns terrain/edifice lifecycle; this is
the kit's one genuinely new system, and the sheet already priced it as the
campaign's most alien base-type.

**Effort**: **L** (the regrowth/crush/seal component and its save state; the
mineable half is nearly free). **v1: ships core loop** (mine, regrow, creak,
crush, seal); wild-dungeon population deferred to roster/template items.

---

## Optional reuse note — steam sources

`VAPOR_EMITTER_PLACEMENT_1` (sheet's Owed list) can take ruled
**`RM_CompActiveGasEmitter`** unchanged for river-bank steam-vent props (a
harmless white gas def, pure atmosphere) — zero new C#, pure content. Listed so
the reuse is counted, not to grow this item's scope. Likewise the review's §5
note that `RM_Gas_Transmuting` could serve a Greentide spread visual belongs to
`EXPLOSIVE_PLANT_GROWTH_1`, not here.

## New-C# roster (what this kit adds beyond the six ruled comps)

| Class | For | Effort |
|---|---|---|
| `RM_GameCondition_WetBulb` (+ `RM_WetBulbProtection` StatDef part) | M1 | M |
| `RM_CompDryFieldEmitter` + `RM_MapComponent_DryRooms` | M2 | M |
| `RM_WanderingVortex` (Tornado crib) | M3 | M |
| `RM_WeatherOverlay_GroundFog` + glow-override extension | M4/M5 | S |
| `RM_TreeFallUtility` + `RM_CompCrackFall` + gnaw JobGiver | M6 | M |
| `RM_CompAquaticAmbusher` | M7 | M |
| `RM_MapComponent_TerrainMire` + `RM_MapComponent_MudSwallow` | M8 | M |
| `RM_GenStep_RootCauseways` (+ bole placement) | M9 | M |
| grazing Harmony postfix | M10 | S |
| `RM_MapComponent_SilenceCue` | M11 (deferred) | M |
| `RM_MapComponent_LivingRegrowth` + Greatbole defs | M12 | L |

All RM_ classes live in the ruled kit's home
(`src/RimMandrake/EnvironmentalHazards/`, packageId
`mandrake.rm.environmentalhazards`, per review §4) or a sibling RM_ mod if
FOUNDRY splits by weight; RUT_ content defs live in the Greentide's content mod.
Total: 1 L, 6 M, 2 S new (M4's S and M10's S), + 1 M deferred; four ruled-comp
reuses ride `ALPHA_MECHANICS_KIT_1`'s build.

## Build order

1. **`ALPHA_MECHANICS_KIT_1` lands first** (external dependency): needs
   `RM_GameCondition_EnvironmentalWeather`, `RM_HarmonyPatch_BiomeGlowMultiplier`,
   `RM_HediffComp_PeriodicAreaAttack` finished shapes.
2. **M4 Roil + M5 Breaklight** — near-pure reuse; the biome instantly *feels*
   different, and every later live test happens under the right weather/light.
3. **M1 wet-bulb + M2 blower** — one unit (M1's dried-room gate is M2's
   component); the survival thesis becomes playable; gear XML alongside.
4. **M3 Scald + steam devil** — Scald def early (M11-adjacent defs reference
   it), vortex after.
5. **M6 tree fall** — utility first, then crack comp, then the
   PeriodicAreaAttack hook (feller 2), then the gnaw job.
6. **M8 churnmud** then **M9 causeways** (M9's GenStep paints over M8's
   terrain and sites M12's boles — strict order).
7. **M12 Greatbole** — the L item, after its map-gen anchor (M9) exists.
8. **M7 Lunger comp** — independent; slot anywhere after 2, before roster pass.
9. **M10 grazing hook** — with/after `EXPLOSIVE_PLANT_GROWTH_1` (its grid must
   exist; M2's suppression write shares the dependency — if the growth engine
   slips, M2 ships with the write stubbed and the room-dry + heat halves live).
10. **M11 silence cue** — v1.1, after a source read of `Sustainer` volume.

Cross-item dependencies restated: `EXPLOSIVE_PLANT_GROWTH_1` (M2, M10),
`ALPHA_MECHANICS_KIT_1` (M4, M5, M6), `VAPOR_EMITTER_PLACEMENT_1` (optional
consumer, no dependency), roster pass (creatures for M6/M7's comps to ride),
salinity map-gen (separate Owed item — deliberately NOT in this kit).

## What needs an owner card (short — the lore is ruled)

1. **Churnmud swallow scope**: does mud under a player stockpile zone swallow
   stored items, or is zoned/home-area ground exempt? Pure griefing-tolerance
   tuning; the sheet doesn't say. (Default drafted: no exemption — dig or floor
   it.)
2. **Toxin sealant recipe**: drafted as crafted from §7 sap/resin (INVENTED
   economic link). One-line confirm, since it prices the Greatbole base-type.
3. **Breaklight scramble + silence cue deferrals**: v1 ships Breaklight without
   the seek-shade AI and defers the silence cue whole to v1.1. Both are §9
   texture, not §5 law — confirm the deferrals are acceptable for the first
   playable.
