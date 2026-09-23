# The Rot — mechanics kit spec

Drafted 2026-09-17 against the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_rot.md` (§3–§7b, Owed — the AUTHORITY; this
spec maps its mechanics onto the engine and invents no lore). Structure and voice
follow `greentide_kit_spec.md` / `scarlands_kit_spec.md`. Anything marked
**INVENTED** is a tuning value this spec had to pick; anything marked ❓ or
UNMEASURED is an engine claim not fully verified and must be checked before build.
Claims marked *(verified)* were read from the RimSage source index THIS session
(2026-09-17, `mcp__rimsage__search_source`/`read_file`) — same caveat as the
Greentide spec: the index may trail the live 1.6 assembly; re-run the named
searches before spending C#.

**Naming law**: generic mechanisms `RM_` (`RimMandrake.*`), Rot content defs
`RUT_` (`RimMandrake.Utinni.*`), packageIds `mandrake.rm.*`/`mandrake.rut.*`.
"Jawa" is lore text only. No worldgen of any kind — everything below is map-gen
or runtime on the one frozen world.

**Ruled-comp reuse baseline**: the six RM_ comps of `ALPHA_MECHANICS_KIT_1`
(closed 2026-09-11, sha `ddd8d379f`, mod `mandrake.rm.environmentalhazards`),
referenced as **RC1–RC6** (RC1 gas family `CompActiveGasEmitter`/`Gas_Damaging`/
`Gas_Transmuting`, RC2 `HediffComp_PeriodicAreaAttack`, RC3 biome glow multiplier
patch + `RM_GlowMultiplierOverrideExtension`, RC4
`GameCondition_EnvironmentalWeather` + `EnvironmentalWeatherExtension` — which
since `MIASMA_MECHANICS_1` also carries `hediffToApply`/`carrierHediff` fields,
RC5 scaled death explosion + `GameCondition_ArmLatentHazard`, RC6 targeted
hediff ability). Also live and reusable: `RM_HediffComp_SeverityFloor`,
`RM_HediffComp_EnvironmentalExposure`, `RM_CompBeastWakeRelay`,
`RM_Hediff_SunScald` (`mandrake.rm.creaturebehaviors`), and the
`RUT_MiasmaWeatherLock.xml` pattern for attaching a permanent condition via the
BiomeDef's own `<biomeMapConditions>` — pure XML, decompile-confirmed by the
Miasma pass.

Scoreboard: **9 mechanics** · heavy RC reuse (RC1 ×2, RC4 ×3, RC5 optional) ·
**~5 new RM_/RUT_ C# classes** (1 L, 2 M, 2 S) · the rest XML on verified
vanilla comps.

---

## player experience

You land warm. That is the first wrong thing — the tile said −19 °C and the
glow-moss under your boots is damp and body-warm, while the air a meter up
frosts your breath. Build on the mat and the jungle heats your rooms for free;
build off it and the nightside cold owns you. Then the sky exhales: not rain —
the Sheen, a cloying reproductive sleet that gloss-coats your walls, your
crops, your colonists, and anyone who breathes it unadapted starts down the
road to a fungal infection. Your first economy is the freezer war: everything
you harvest here is still alive, still metabolizing, pushing heat into the very
freezer trying to keep it — and anything raw left outdoors is simply gone by
tomorrow, digested. Your first expedition is a tea: the age-reversing,
scar-healing brews of this place cannot be bottled, shipped or stored — you
walk to a guarded grove, fight or sneak past a mushroom that has killed
better-prepared visitors, brew in your vessel at the shrine some earlier party
left, and drink it while it lives. Stay long enough and you stop resisting the
biome and join it: a symbiont under the skin instead of a filter over the
mouth, a herd whose wounds redistribute across bodies until nothing quite
dies, and a pale tree that grants a whisper of the Force and the strong
feeling you should find a teacher. The Rot is the planet's gut. It is
generous, warm, and always, patiently, digesting you.

## what already exists (do not re-ticket)

- **`RUT_TheRot.xml` BiomeDef is live**
  (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml`): donor worker
  class, donor weather commonalities deliberately kept (its own header: the
  donor Rain/RainyThunderstorm/FoggyRain rows ARE the Sheen mechanically;
  renaming the WeatherDefs was explicitly "separate, un-owed content" — that
  content is THIS kit's M1). `plantDensity 0.6` is flagged interim in the same
  header, pending a quicktest tune.
- **`RotSporeKit` (`mandrake.rut.rotsporekit`) is live and cold-load-verified**
  (`FUNGALFOREST_RAID_MERGE_1` closed 2026-09-10, sha `1ad5a21d3`;
  `ROTSPOREKIT_ENABLE_DECISION_1` closed same day): ~70 RUT_ defs — the §7b
  spore-warfare kit (RUT_ToxicSpores/RUT_StunningSpores DamageDefs,
  RUT_SporesBuildup/RUT_SporeFlesh/RUT_HediffSkulltopSpores hediffs, the
  thrumbungus + mantis-scythe weapons), fungal materials/terrain/bridges,
  buildings (fungiponics, glow torches), research, drugs, 19 flora + Skulltop,
  with real donor art. `RUT_SporeCloud`'s `conditionClass` points at our own
  `RimMandrake.EnvironmentalHazards.GameCondition_EnvironmentalWeather` since
  `ROT_SPORECLOUD_PORT_1` (done; the donor class survives only in the def file's header
  comment). Gate 3 of `BMT_FAUNA_ABSORPTION_1`'s donor retirement is discharged.
- **Fauna is NOT this kit's business.** The roster rides
  `BIOME_FAUNA_ASSIGNMENT_SITTING_1`; the owner's 2026-09-11 ruling on
  `BMT_FAUNA_ABSORPTION_1` CUT the 7 BMT_ stragglers still sitting in
  `RUT_TheRot.xml`'s `wildAnimals` (ChemSnail, CaveSpider, GiantSlug,
  GiantSnail, Pillbug, GlowBat) — deleting those entries is that item's
  propagation, not ours. This kit only ships comps a roster pass can later
  attach by XML (M7).
- **Already filed elsewhere, referenced not duplicated**:
  `FUNGAL_SOIL_TRADE_1` (soil dug and shipped, distress response),
  `BIOME_LABEL_CAMPAIGN_NAMES_1` (the "Mycotic Jungle" label),
  `VAPOR_PLACEMENT_CLEANUP_1` (helixien re-seat to junker sites here),
  `GENEPACK_MODS_PLUNDER_1` (genepack mod review; its 2026-09-06 measurement —
  neither mod ships a GeneDef, closest numbers are `IgniFurnace`/`IgniWarm`
  hediffs — is the source M3's gene ticket builds against),
  `ALPHA_FAMILY_SOURCE_REVIEW_1` (the generic defender-plant line; RC1 is its
  ruled outcome and M6 consumes it).
- **Reserved, hard ban 5**: the living-gene-reactor belongs to the Slime
  (`AB_GelatinousSuperorganism`). Nothing below touches gene extraction beyond
  locally-beneficial genepack content.

## M1 — The Sheen: weather reskin + exposure ladder (§3, §4b, bans 3)

**Player experience.** It never rains water here — it can't (ban 3). The
common sky-state is Sheen-fall: the jungle's own reproductive sleet, cloying
and glossy. Unroofed, unadapted pawns accumulate Sheen coating; let it climb
and it seeds `RUT_SporeFlesh` — the ported "mycelia have invaded the body"
disease that numbs pain and slows bleeding while it drains. The biome's border
is enforced by its own breath: gear slows the clock, only symbiosis (M4) stops
it.

**Engine route — mostly XML, one standing ban fixed.**

- **Reskin (fixes a live ban-3 text violation)**: three new `RUT_` WeatherDefs
  cloning the donor rows the BiomeDef currently uses — `RUT_SheenFall` (from
  Rain), `RUT_SheenStorm` (from RainyThunderstorm), `RUT_SheenMist` (from
  FoggyRain) — with sheened labels/descriptions, and
  `RUT_TheRot.xml`'s `baseWeatherCommonalities` repointed at them. Same
  commonality numbers (source: the live def). Keep `rainRate` behavior so
  fires still douse — the Sheen is wet, it just isn't water. ❓ UNMEASURED:
  whether any vanilla text surfaces "rain" for a cloned WeatherDef beyond
  label/description — sweep the def's string fields at build.
- **Exposure**: reuse **RC4** as a permanent condition
  (`RUT_SheenExposureLock`, attached via the BiomeDef's own
  `<biomeMapConditions>`, exactly the shipped `RUT_MiasmaWeatherLock.xml`
  shape — pure XML, no weather forcing, no damage fields). Its
  `hediffToApply` drives `RUT_SheenCoating` severity on unroofed pawns
  **only while a Sheen weather is current** — ❓ verify
  `EnvironmentalWeatherExtension` can gate application on current weather; if
  it cannot, that is one small additive field on the extension (the
  Miasma/Scarlands passes both extended it the same way, precedent stands).
- **The ladder**: `RUT_SheenCoating` HediffDef (XML) — cosmetic gloss at low
  severity (inspect string: "sheened"), and its top stage carries
  `hediffGivers`/severity spill into **`RUT_SporeFlesh`** (already ported,
  `RotSporeKit/Defs/HediffDefs/`) — the sheet's own "ready-made Sheen
  infection". ❓ the exact spill mechanism (stage `hediffGivers` vs a
  `RM_HediffComp_EnvironmentalExposure` reuse) is a build-time pick; both
  exist.
- **Adaptation gates**: severity gain ×(1 − protection). Gear: reuse the
  toxic-environment-resistance shape — a `RUT_SheenProtection` StatDef on
  apparel (the ported chitin spider helmet is the first carrier). Symbiont:
  `RUT_SheenSymbiosis` hediff (M4) zeroes gain outright. Native/hybrid fauna:
  exemption list on the condition def (XML).

**INVENTED**: unprotected coating → SporeFlesh onset in ~1.5 in-game days of
continuous exposure; full gear ≈ 4×  slower; symbiont = immune.
**Reuse**: RC4 (+ possibly 1 additive extension field). New C#: none expected.
**Effort: S–M** (XML-heavy). **v1: ships** — it is the biome's border law.

## M2 — The rot clock: the gut digests (§3, §5, §7 "instant composting")

**Player experience.** Raw meat dropped outdoors is gone within a day, for
certain. Corpses melt into the mat. Filth barely accumulates. Your enemies'
dead clean themselves up; so does your unroofed larder. Walls and a roof (and
M5's overbuilt freezer) are the only argument the gut listens to.

**Engine route.** Vanilla rot is `CompRottable.TickInterval` →
`GenTemperature.RotRateAtTemperature(parent.AmbientTemperature)` *(verified,
`Source/RimWorld/CompRottable.cs:101`)* — temperature-only, no map/biome seam,
and the method is static with no map context, so a Harmony patch there would
be global. The honest seam is that **`CompRottable.RotProgress` is a public
settable property** *(verified — `RotImmediately`/`PostSplitOff` write it)*:

- **`RM_MapComponent_AcceleratedRot`** (new, generic, extension-driven — any
  future digester biome reuses it): on a 250-tick interval, for every spawned
  Thing with `CompRottable` that is **exposed** (unroofed, OR outside a fully
  walled room — exact predicate below is an owner card), add
  `bonusRotProgress = delta × (multiplier − 1)`. The biome opts in via a
  `RM_AcceleratedRotExtension` on its BiomeDef (multiplier, exposure
  predicate, corpse multiplier). Cheap: `map.listerThings` by def-has-comp
  group, no per-cell scan. ❓ UNMEASURED: the right lister group key for
  "has CompRottable" — resolve at build (`ThingRequestGroup.Refrigerator`? no
  — read `ListerThings` groups; worst case iterate haulables + corpses).
- **Corpses**: same component, higher multiplier — the sheet's instant
  composting. Dessication follows vanilla staging automatically since we only
  accelerate progress.
- **Filth**: same component thins spawned filth on a slow interval
  (`filth.ThinFilth()` ❓ verify method name at build; vanilla rain already
  thins filth, this is that on a timer). Skip filth inside player home area
  rooms — cleaning stays a chore indoors, INVENTED scope choice, carded.

**INVENTED**: exposed-rottable multiplier ×12 (a 1-day meat clock against
vanilla's ~2 days unrefrigerated at warm temps — source for the target:
sheet §3 "gone within a day, for certain"); corpse multiplier ×20; filth
half-life ~2 days outdoors.
**Reuse**: none applies (RC comps don't touch items). New C#: 1 map component
(**M**, mostly bookkeeping). **v1: ships** — an Always-true.

## M3 — Metabolic warmth: the mat, the grown furnace, the heat gene (§3, §7)

**Player experience.** The tile says −19 °C; the ground says otherwise. A room
floored by the living mat is warm without a heater — the jungle is your
furnace, as long as you build ON it. Off the mat, Frostcaps rules apply. And
two prizes ride the same physics: a cultivable mushroom that is palpably a
heater, and — richest of all — the gene that lets a body do what the fungi do.

**Engine route — three pieces, smallest honest versions.**

- **The warm mat**: RimWorld has no per-cell ground temperature — heat is
  per-room/outdoors. So the mechanic is room-scoped, which is exactly how the
  player meets it: **`RM_MapComponent_WarmGround`** (new, extension-driven):
  for each enclosed, roofed room whose floor is ≥ N% unbuilt mycotic terrain
  (`AB_MycoticGrass`/`AB_MycoticSoilRich`/RotSporeKit mycelial terrains —
  list on the extension), push heat toward a target equilibrium
  (`GenTemperature.PushHeat`, the `CompHeatPusher` mechanism *(verified,
  `Source/Verse/CompProperties_HeatPusher.cs` — heatPerSecond +
  max-temperature cap)*). Floor over the mat with dead material and the
  heating stops — the trade is comfort vs. sterility (and the mat under your
  bedroom is ALIVE, which M1's Sheen and the sheet's art direction get to
  say). Outdoor "warmth" stays what the worldmap already painted.
- **The grown furnace**: ⭐ the sheet's lean-in, all-XML loop.
  `RUT_FurnaceCap` plant (sowable, RotSporeKit growing tech) harvests into
  `RUT_LivingFurnaceCap` items; a `RUT_GrownFurnace` building (built FROM
  those items, no power, no fuel) carries vanilla `CompHeatPusher`
  *(verified)* + `CompLifespan` *(verified, `Source/Verse/CompLifespan.cs`)* —
  it is alive, so it dies: after ~15 days (**INVENTED**) it expires and you
  replant. Ban-4 compliant by construction: the furnace is a live
  preparation you cultivate, not a stockpilable machine. ❓ UNMEASURED: no
  verification was done that a PLANT can carry a ticking heat comp — this
  route deliberately avoids needing it (the heater is a building).
- **The heat gene**: `RUT_Gene_Furnaceblood` GeneDef (authored — MEASURED
  2026-09-06 via `genepack_mods_plunder.md`: no donor GeneDef exists) whose
  hediff carries a small permanent `CompHeatPusher`-equivalent comfort band —
  numbers calibrated against the consumables mod's `IgniFurnace`/`IgniWarm`
  hediffs (named source, read them at build). Shipped as local genepack
  content (§7 "Local genepacks", ban 5 compliant: beneficial-to-here). ❓
  whether a pawn hediff can push room heat needs a source check
  (`CompHeatPusher` is a ThingComp; a HediffComp analog may be new small C#)
  — v1 fallback that needs nothing: the gene widens
  `ComfyTemperatureMin` (a plain gene statOffset, vanilla `Gene_` machinery).

**INVENTED**: mat room equilibrium +18 °C over outdoor, cap 21 °C; furnace
heatPerSecond ≈ vanilla campfire class, 15-day lifespan; gene −20 °C comfy
floor.
**Reuse**: vanilla comps. New C#: `RM_MapComponent_WarmGround` (**M**);
possibly a tiny HediffComp for the gene (**S**, or zero with the fallback).
**v1: mat + furnace ship; gene ships at fallback strength** (statOffset), the
heat-pushing gene body is v2 polish.

## M4 — Live preparations: teas and symbionts (§7, bans 4)

**Player experience.** The Rot sells nothing to go. Its teas — age-reversal,
bioregeneration, the pleasure brew — and its symbiont parasites are alive:
refrigerate one and it dies, wait too long and it dies. You come to the biome,
you brew in your vessel at the grove, you drink or implant it NOW. This is
luciferium pulled apart into bargains you can read before signing.

**Engine route.** The come-here-and-brew law is TWO vanilla comps, both
verified, both pure XML on every live-prep item:

- **`CompTemperatureRuinable`** *(verified,
  `Source/RimWorld/CompTemperatureRuinable.cs` — the egg/fermenting-barrel
  comp)* with `minSafeTemperature` ≈ +8 °C (**INVENTED**): a fridge RUINS it.
  Refrigeration kills, exactly the sheet — and vanilla already renders the
  "ruined" inspect state, stack merging, the works.
- **`CompLifespan`** *(verified)* with expiration ≈ 2.5 days (**INVENTED**):
  delay kills. Between the two comps, ban 4 (no stockpilable teas/symbionts)
  is enforced by the engine, not by discipline — a linter can check both
  comps are present on every def tagged live-prep.
- **The teas** (3 ThingDefs, ingestible):
  - *Age-reversal*: needs one small C# —
    `RM_IngestionOutcomeDoer_AgeReversal` (vanilla age reversal lives in the
    biosculpter's cycle worker, not in any ingestible outcome ❓ verify at
    build; the doer subtracts N days of biological age, capped at adult).
    **RULED (card 1, 2026-09-17)**: 5 years on the first cup; a pawn benefits
    only once per year (`RUT_AgeReversalSated` hediff, 1-year duration, blocks
    repeat cups); very hard to obtain — keep ingredient yields scarce.
  - *Bioregeneration*: XML if `HediffComp_HealPermanentWounds` (the
    luciferium healer ❓ verify class name at build) can ride a temporary
    hediff; the tea grants `RUT_Bioregenerating`, ~5 days, healing one
    permanent wound/scar per interval.
  - *Pleasure brew*: pure XML — chemical-joy outcome + a strong short
    thought.
- **The symbionts** (3 hediff pairs, ratified in the sheet; implantation =
  ingesting the live symbiont item):
  1. `RUT_Sym_Quickflesh` — accelerated healing (stage
     `naturalHealingFactor` ❓ verify stage-field name) **/** hunger rate
     ×2.2 (stage `hungerRateFactor`, vanilla field).
  2. `RUT_Sym_Nightwake` — `RestFallRateFactor` ×0 *(verified — the stat
     exists and Anomaly ships a ×0 user, `Hediffs_Global_Misc.xml:1128`)*
     **/** permanently reduced mental-break threshold + occasional
     `mentalStateGivers` — always a little psychotic, in vanilla vocabulary.
  3. `RUT_Sym_Sheenblood` — `RUT_SheenSymbiosis` (M1 immunity — you have
     JOINED the biome) **/** sun intolerance: severity/burn while in direct
     sunlight — reuse `RM_Hediff_SunScald`
     (`mandrake.rm.creaturebehaviors`, already shipped) if its shape fits ❓,
     else a small clone.
  - The two Slime-serving exports (`the_slime.md`): the mycoid
    slimification-resistance symbiote is symbiont #4 in the same XML shape
    (its resistance hediff is read by the Slime's own kit, not built here);
    the intentionally toxic injection is a live-prep item whose only consumer
    is the Slime kit — ship the items, let the Slime kit wire the effects.
- **The brew station**: `RUT_BrewingVessel` building (RotSporeKit research
  row) with RecipeDefs taking M6's grove-harvested live ingredients →
  live-prep items. Placed by players; §8's semi-permanent grove shrines are
  map-gen dressing (v2, see boundary).

**Reuse**: 2 vanilla comps, RM_Hediff_SunScald, RM_HediffComp_SeverityFloor
(symbiont withdrawal floors, if wanted). New C#: the age-reversal doer (**S**).
**Effort: M** overall (much XML, one S doer). **v1: ships** — §7 is the
biome's entire why-go.

## M5 — Living harvest: produce that fights the freezer (§5)

**Player experience.** Everything harvested here keeps metabolizing: your
fungal food pushes heat into the room storing it. A normal freezer fills with
Rot produce and quietly climbs above freezing; you overbuild — double coolers,
small rooms — or you eat fresh and let M2 take the rest. (And per M4, the
GOOD stuff can't go in the freezer at all.)

**Engine route.** One small generic component, not per-item ticking:
**`RM_MapComponent_LivingProduce`** — on a rare interval, for each room,
sum `stackCount` of stored things whose defs carry
`RM_LivingProduceExtension` (a DefModExtension: heatPerUnit), and
`GenTemperature.PushHeat` the total into that room. Items need no tickerType
change and stacks cost one add, not 75 *(design choice — item ticking is the
❓-laden route; this avoids it entirely)*. The extension goes on RotSporeKit's
food/crop defs by XML patch. Native produce only — vanilla imports stay inert.

**INVENTED**: heatPerUnit tuned so ~200 units of produce ≈ one campfire —
a stocked freezer needs roughly double cooling. Numbers are the quicktest's
to settle.
**Reuse**: M2's component pattern; could even live inside the same map
component class family. New C#: **S**. **v1: ships** — an Always-true and
the freezer war is a defining colony rhythm.

## M6 — Guardian groves: potency implies guardianship (§4, §7, ban 8)

**Player experience.** Nothing worth taking here is undefended (ban 8). The
three tea-source mushrooms are the biome's armed nobility: approach one and it
answers — a suffocating spore cloud in the Agarilux Prime's own style, hybrid
defenders arriving through the mycelial network, or a mat that grips your
ankles while the false fruiting body you reached for turns out to be bait.
Getting a tea ingredient is an expedition with a plan, not a right-click.

**Engine route — three guardian patterns, one per tea source, maximal RC
reuse.** The donor already proves the exemplar: `AB_AgariluxPrime` runs
`AlphaBiomes.CompProperties_GasProducer`, radius 8, gas `AB_MycoticSpores`
(sheet §4, MEASURED there) — it stays donor-owned and untouched.

- `RUT_AgelessCap` (age-reversal source, **INVENTED** name): **RC1**
  `CompActiveGasEmitter` + `Gas_Damaging` with a `RUT_ChokingSpores` gas def
  riding the ported `RUT_ToxicSpores` DamageDef — our own Prime-pattern
  defense, zero new C#.
- `RUT_RegenerantVeil` (bioregeneration source, **INVENTED** name): network
  alarm — harvesting/damaging it wakes nearby hybrid fauna. Reuse
  **`RM_CompBeastWakeRelay`** (already shipped in
  `mandrake.rm.environmentalhazards`) ❓ verify its trigger semantics fit
  plant-parents at build; fallback is a 30-line comp raising manhunter on
  tagged nearby pawns (the vanilla plant-harm → `Messages` +
  `MentalStateDefOf.Manhunter` route).
- `RUT_EuphoricCrown` (pleasure-brew source, **INVENTED** name): the grasping
  mat + the lure. A small ring of `RUT_FalseFruit` mimic plants around the
  real one; harvesting a mimic applies `RUT_MatGrip` (short immobilize hediff,
  XML) and pings the alarm. **RC2** `HediffComp_PeriodicAreaAttack` is NOT
  the shape (it rides an afflicted pawn) — the grip is just a
  harvest-triggered hediff via `CompUseEffect`-style plant hook ❓ the exact
  plant-harvest hook needs a build-time source read (Plant.PlantCollected is
  the candidate seam).
- All three yield `RUT_LiveIngredient_*` items (M4 comps on them — even the
  ingredients die if delayed/refrigerated, so the brew run is one trip).

**Spawning**: wildPlants entries at Prime-like rarity (0.01–0.05,
**INVENTED**) — no map-gen work needed; §8's guardian thickets as designed
set-pieces are v2 dressing.
**Reuse**: RC1, RM_CompBeastWakeRelay, ported DamageDefs. New C#: at most the
alarm fallback + harvest hook (**S–M**). **v1: ships with at least patterns 1
and 2**; the mimic-lure (pattern 3) may slip to v1.1 without breaking ban 8
(the alarm covers its plant).

## M7 — Health-sharing: the herd bleeds as one (§4)

**Player experience.** Wound one of the connected creatures and the herd
answers arithmetic: the injury redistributes across nearby bodies until the
load is survivable. Tame them and it works for you — your caravan's beast of
burden survives what should have killed it, because six others each took a
cut. The softer species just knit faster near kin. Everything here is
unusually connected; now you can feel it.

**Engine route — the kit's one genuinely new system, two ruled variants.**

- **Variant (a), true wound-splitting — `RM_CompWoundLink`** (new C#, the L
  piece): pawns whose race carries the comp + a shared link tag
  (`RM_WoundLinkExtension`: tag, radius, share fraction, min-severity gate).
  On `PostApplyDamage` ❓ (`Pawn.PostApplyDamage`/`Notify_DamageTaken` — pick
  the seam from a source read; MUST be the post-damage notification, not a
  pre-damage interception, so armor/deflect math stays vanilla), if the hit
  exceeds the gate: enumerate linked pawns in radius, move a fraction of the
  injury as fresh `Hediff_Injury` instances of the same def onto their
  equivalent body parts (cut/burn semantics preserved; brain and destroyed
  parts excluded — **INVENTED** exclusion list), reducing the victim's
  injury severity by the amount moved. Tamed animals participate (sheet: ⭐
  works on tamed — your herd bleeds as one). No death-cheating: a hit that
  would gib the victim outright still can (share happens post-application on
  the surviving pawn's injuries).
- **Variant (b), tend-aura — `RM_HediffComp_KinMending`** (new C#, S): a
  passive hediff on the softer species; while ≥ N linked kin are within
  radius, adds healing-rate factor + tend-quality-equivalent to natural
  recovery (implementation candidate: adjust injury `Severity` on interval —
  the same public-severity route M2 uses on rot).
- Which species gets which variant is the fauna sitting's XML decision; this
  kit ships both comps content-blind (the Greentide M6 pattern: the C# here,
  the roster supplies XML).

**INVENTED**: share fraction 60% spread evenly, radius 12, gate ≥ 8 severity;
aura: +50% healing at 2+ kin.
**Reuse**: none fits (RC comps are hazard-shaped). New C#: **L** (a) + **S**
(b). **v1: ships** — it is the biome's thesis ("everything here is
connected") made mechanical, and the admission-test fauna are already tagged
for it in the sheet.

## M8 — The pale tree: a door ajar (§7, ban 6)

**Player experience.** A reskinned pale giant, sacred to Wildsteam, aligned
with the Light side. Meditate at it long enough and it grants a psylink — a
faint one, a few gentle powers — and the unshakable feeling that you should
find someone who actually knows what this is. No economy, no ladder. A door
ajar.

**Engine route.** A Royalty anima reskin, almost entirely XML:

- `RUT_PaleTree` ThingDef cloning `Plant_TreeAnima`'s comp stack:
  `CompPsylinkable` — and the restriction mechanism is a verified def field:
  **`requiredSubplantCountPerPsylinkLevel` is a `List<int>`** *(verified,
  `Source/RimWorld/CompProperties_Psylinkable.cs`)*, and **the owner ruled cap
  2 (card 4, 2026-09-17)**: a TWO-entry list caps the tree at psylink level 2
  forever — a real minor kit of level-1/2 psycasts, nothing higher. Ban 6 (no
  psycast economy, no VPE) is enforced by the cap, not a whitelist; a
  per-power whitelist would need C# and is explicitly NOT built (owner card).
- `CompSpawnSubplant` with a `RUT_PaleMoss` subplant (glow-moss — biological
  light, the biome's law); meditation focus stays `Natural` ❓ or a cloned
  focus def if Wildsteam flavor wants its own — cosmetic call at build.
- Wildsteam sacred-grove wiring (worship, pilgrim paths) is the sheet's Owed
  `FACTION_SPEC.md` line — not this kit.

**Reuse**: vanilla anima machinery wholesale. New C#: none. **Effort: S.**
**v1: ships** (it is cheap and the campaign's only Force door on the
nightside); DLC note: Royalty-gated content, `MayRequire` on the injected
defs where cross-mod, and per the standing law any patch gating uses
`PatchOperationFindMod` or MayRequire on the injected `<li>` itself — never
on a patch `<Operation>` (INERT, measured 2026-09-17).

## M9 — Spore cloud C# port: retire the last donor class (§7b)

**Player experience.** Unchanged — the big fungi still occasionally vent a
region-blanketing suffocation cloud (the ported `RUT_SporeCloud` incident).
What changes is whose code runs it.

**Engine route.** `RUT_SporeCloud`'s `conditionClass` was ported off
`BiomesCaverns.GameCondition_SporeCloud` at `ROT_SPORECLOUD_PORT_1` (done); this section
records the route that was taken. The donor behavior —
"any living thing not under a roof will be slowly suffocating" — is exactly
**RC4's shape**: `GameCondition_EnvironmentalWeather` damages/afflicts
unroofed pawns on an interval (the AcidRain donor pattern it was built from).
Port = point `conditionClass` at RC4's class with an
`EnvironmentalWeatherExtension` config (hediff route: severity-ramp a
`RUT_SporeChoke` hediff on unroofed breathers; or reuse the ported
`RUT_SporesBuildup` hediff directly — prefer the latter, it exists and its
text is already right). ❓ one build-time check: RC4's extension applies to
pawns — confirm "animal life" coverage (the donor letter says animals die
outdoors) and whether mechanoids/vacuum-safe races are correctly exempt
(extension exemption list).

Expected: **zero new C#** — an XML conditionClass swap + extension block.
If a field is missing, it is one additive field on the shared extension
(precedent: Miasma, Scarlands both did this).
**Effort: S.** **v1: ships first** — it unblocks another item's ruled
retirement and is the cheapest live proof of the kit.

## mod settings (standing law, owner 2026-09-12 — goes in every ticket)

`RotSporeKit` is currently data-only; this kit gives it a `Source/` assembly
anyway (M2/M3/M5 map components live somewhere Rot-owned — see homes note
below), so the settings screen rides the same DLL: `RUT_RotMechanicsMod :
Mod` with one toggle per mechanic, **defaults = shipped behavior, all ON**:

| toggle | off means |
|---|---|
| Sheen exposure (M1) | weather stays reskinned (cosmetic), no coating hediff |
| Accelerated rot (M2) | vanilla rot rates; composting off |
| Warm mat (M3) | rooms need heaters like anywhere; furnace/gene untouched |
| Live preparations (M4) | teas/symbionts keep both comps but min-safe-temp gate relaxed — still expire (ban 4 never fully off; label the toggle "viability: strict/lenient") |
| Living produce heat (M5) | produce is inert in freezers |
| Guardian defenses (M6) | tea sources become plain harvestables ⚠️ violates ban 8 — the toggle ships but its label says "breaks the biome's law, for accessibility" |
| Health sharing (M7) | creatures fight and heal alone |
| Spore cloud incident (M9) | incident weight 0 |

All-off = a pale fungal reskin biome with donor flora — degrades gracefully.
Numeric tuning sliders only where a number IS the experience: rot multiplier,
mat warmth, share fraction. Each ticket below carries its own toggle as an
acceptance criterion.

**Homes**: generic `RM_` classes → `mandrake.rm.environmentalhazards`
(`src/RimMandrake/EnvironmentalHazards/`) or `mandrake.rm.creaturebehaviors`
(M7's comps — creature-shaped, that mod's charter); Rot-specific glue,
content defs, settings → `RotSporeKit` (`src/RimUtinni/RotSporeKit/`,
`mandrake.rut.rotsporekit`, namespace `RimMandrake.Utinni.RotSporeKit`).
BiomeDef edits → `UtinniPatches`.

## v1 / v2 boundary

**v1 (the tickets below)**: M1 Sheen ladder · M2 rot clock · M3 mat + grown
furnace + gene-at-fallback · M4 teas (bioregen + pleasure; age-reversal if the
doer is cheap) + all 3 symbiont pairs · M5 living produce · M6 guardian
patterns 1–2 · M7 both comps · M8 pale tree · M9 spore-cloud port.

**v2 / explicitly deferred, never silently**: guardian pattern 3's mimic-lure
polish · §8 map-gen dressing (grove shrines/brewing stations as found
set-pieces, digestion-site ruins, Wildsteam pilgrim paths — wants the
set-piece GenStep family, `RM_GenStep_PlacedSetPieces` exists as the tool) ·
the heat-pushing gene body (v1 ships statOffset fallback) · the gourmet
line + bovine-beetle milk economy (content wave, no new mechanics) ·
Slime-facing symbiont EFFECTS (the Slime kit's side) · Wildsteam faction
wiring (`FACTION_SPEC.md`) · per-power psycast whitelist (declined unless
carded otherwise).

**Dead, not deferred** (standing rulings): fungal power generator (CUT,
"that's stupid") · cultivable blastpod (wild-only stands) · any gene-reactor
mechanic here (ban 5, reserved for the Slime) · water rain in any form.

## owner cards — ALL SIX RULED, owner at the bench 2026-09-17

Nothing here is open. Each ruling below is the authority over any older draft
number elsewhere in this file or in a ticket spec.

1. **Tea potency — RULED, stronger than the draft but hard-gated.** 5 biological
   years off on the first cup, but a pawn can benefit **only once per year**, and
   the tea is **darned hard to obtain even with pilgrimage** (guardians + the
   live-prep death clock + scarce ingredients are the gate; keep yields low).
   Reason: a pilgrimage industry, rate-limited so it never becomes routine.
   Engine: the doer subtracts 5 years (capped at adult) and applies a
   `RUT_AgeReversalSated` hediff lasting 1 in-game year; a sated pawn gets
   nothing from another cup. Supersedes the "1 year, diminishing within a
   season" draft in M4 and in the ROT_LIVE_PREPARATIONS_1 filing spec.
2. **Rot scope — RULED as drafted.** Only walled+roofed rooms are exempt from
   accelerated rot; a lean-to won't save your meat. Reason: the biome's law
   bites colonists, not just corpses (his Greentide precedent: "the biome makes
   you engineer"). ROT_DECAY_HARVEST_1's built predicate already does this — no
   code change.
3. **Warm mat — RULED as drafted, free forever, and that's final for v1 AND the
   design.** His words: it doesn't make enough heat to trivialize the deep dark;
   it's likely the only way to tolerate the night side at all without spending
   all your power on heating. "Very Star Wars." The starving-mat variant stays a
   v2 card only if he raises it — do not build toward it.
4. **Pale tree — RULED cap 2, reversing the draft.** Two entries in
   `requiredSubplantCountPerPsylinkLevel`: a real minor kit, not just a door
   ajar. Power whitelisting stays declined. Supersedes "one-entry list / cap 1"
   in M8 and the ROT_PALE_TREE_1 filing spec. This was the only ticket gate —
   ROT_PALE_TREE_1 is now UNGATED.
5. **Sheen gear — RULED as drafted.** Gear only slows the exposure clock (4×),
   never full immunity. His reason: incidental exposure every time you go in and
   out — you just can't totally sterilize everything. The symbiont remains the
   only true immunity.
6. **Guardian toggle — RULED, toggle ships with the confession label — and the
   ruling grew a mechanic.** The confession is framed as the pawn's **new
   conscience**: a pawn carrying the Rot symbiont takes a **mood debuff when the
   colony sells the Rot's treasures** (teas, live ingredients, the grove's
   prizes) — "selling a part of yourself." Engine: a trade hook that, on selling
   items tagged as Rot treasures, gives a memory ThoughtDef to colony pawns with
   the symbiont hediff. Lands in ROT_LIVE_PREPARATIONS_1 (the symbiont owner).

## FOUNDRY ticket breakdown

Filing notes for BENCH: all `--for FOUNDRY`, all target v1. Dependency order
as numbered — 1 is independent and cheapest; 2–4 independent of each other;
5 wants 6's ingredients but can stub them; 7 independent; 8 UNGATED (card 4
ruled 2026-09-17, cap 2). Every ticket: (a) Mod Settings toggle per the table above is an
acceptance criterion; (b) any cross-mod gating uses `PatchOperationFindMod`
or MayRequire on the injected `<li>` itself — **never MayRequire on a patch
`<Operation>` (INERT, measured 2026-09-17, killed a cold load)**; (c) offline
build + `validate_patch.py`, then a quicktest/minimal-list live check per
`rimworld-load-round` — no cold loads.

1. **`ROT_SPORECLOUD_PORT_1`** — S — needs: deploy
   --title "Port RUT_SporeCloud off the donor's compiled GameCondition to RC4's GameCondition_EnvironmentalWeather (unblocks BMT_FAUNA_ABSORPTION_1 gate 3)"
   --spec: In `src/RimUtinni/RotSporeKit/Defs/GameConditionDefs/RUT_RotSporeKit_SporeCloud.xml`, replace `conditionClass` `BiomesCaverns.GameCondition_SporeCloud` (MayRequire'd donor class) with `RimMandrake.EnvironmentalHazards.GameCondition_EnvironmentalWeather` (`src/RimMandrake/EnvironmentalHazards/Source/GameCondition_EnvironmentalWeather.cs`) plus an `EnvironmentalWeatherExtension` modExtension block configured to severity-ramp the existing `RUT_SporesBuildup` hediff on unroofed pawns (animals included; exempt mechanoids). If the extension lacks a needed field, add it additively (precedent: Miasma/Scarlands extensions). Proof: quicktest map, dev-trigger `RUT_SporeCloud`, unroofed pawn gains RUT_SporesBuildup and roofed pawn does not; note on `BMT_FAUNA_ABSORPTION_1` that gate 3 is clear. Settings: incident-weight toggle.
2. **`ROT_SHEEN_WEATHER_1`** — M — needs: deploy
   --title "The Sheen: RUT_ weather reskin defs + permanent exposure condition + SporeFlesh ladder (fixes the live ban-3 'Rain' violation)"
   --spec: New `RUT_SheenFall`/`RUT_SheenStorm`/`RUT_SheenMist` WeatherDefs in RotSporeKit cloning Rain/RainyThunderstorm/FoggyRain with sheened labels/descriptions (keep rainRate so fire-dousing survives); repoint `RUT_TheRot.xml` `baseWeatherCommonalities` (UtinniPatches, same commonality numbers). New `RUT_SheenExposureLock` GameConditionDef (RC4 class, `canBePermanent`, listed in the BiomeDef's `biomeMapConditions` — copy `RUT_MiasmaWeatherLock.xml`'s shape) applying `RUT_SheenCoating` HediffDef severity to unroofed pawns during Sheen weathers, gain ×(1−`RUT_SheenProtection` StatDef, carried by the ported chitin helmet), zeroed by `RUT_SheenSymbiosis` hediff (def ships here, granted by ticket 5), top stage seeds the existing `RUT_SporeFlesh`. Proof: quicktest — unprotected pawn outdoors in Sheen-fall reaches SporeFlesh in ~1.5 days; helmeted pawn ~4× slower; roofed pawn clean. Settings: exposure toggle (reskin stays).
3. **`ROT_DECAY_HARVEST_1`** — M — needs: deploy
   --title "The gut digests: RM_MapComponent_AcceleratedRot (exposed rottables/corpses/filth) + RM_MapComponent_LivingProduce freezer-heat"
   --spec: Two extension-driven map components in `src/RimMandrake/EnvironmentalHazards/Source/`: (1) `RM_MapComponent_AcceleratedRot` — 250-tick interval, adds RotProgress (public property, verified) to spawned CompRottable things outside walled+roofed rooms, ×12 items / ×20 corpses (sliders), slow outdoor filth thinning; biome opts in via `RM_AcceleratedRotExtension` on RUT_TheRot (UtinniPatches patch). (2) `RM_MapComponent_LivingProduce` — rare-interval per-room PushHeat summed from stacks of defs carrying `RM_LivingProduceExtension` (patch onto RotSporeKit food/crop defs; heatPerUnit so ~200 units ≈ one campfire). Proof: quicktest — raw meat dropped outdoors gone within 1 in-game day, meat in a walled+roofed room rots at vanilla rate, a stocked 5×5 freezer with one cooler climbs above 0 °C. Settings: separate toggles for rot and produce-heat. Card 2 RULED 2026-09-17: walled+roofed exemption confirmed — the built predicate stands.
4. **`ROT_WARM_MAT_1`** — M — needs: deploy
   --title "Metabolic warmth: RM_MapComponent_WarmGround mat-floored room heating + RUT_GrownFurnace plant/building loop + RUT_Gene_Furnaceblood (fallback strength)"
   --spec: (1) `RM_MapComponent_WarmGround` (EnvironmentalHazards): enclosed+roofed rooms with ≥60% floor of terrains listed in `RM_WarmGroundExtension` (AB_MycoticGrass, AB_MycoticSoilRich, RotSporeKit mycelial terrains) get PushHeat toward +18 °C over outdoor, cap 21 °C. (2) RotSporeKit content: `RUT_FurnaceCap` sowable plant → `RUT_LivingFurnaceCap` item → `RUT_GrownFurnace` building with vanilla CompHeatPusher (campfire-class heat) + CompLifespan ~15 days, no fuel/power. (3) `RUT_Gene_Furnaceblood` GeneDef, v1 = ComfyTemperatureMin −20 °C statOffset (calibrate flavor text against IgniFurnace/IgniWarm hediffs per genepack_mods_plunder.md); ship in Rot genepack loot only (ban 5: locally-beneficial). Proof: quicktest — mat-floored room reads warm with no heater, stone-floored twin reads cold; furnace heats then expires ~day 15. Settings: warm-mat toggle + warmth slider.
5. **`ROT_LIVE_PREPARATIONS_1`** — L — needs: deploy
   --title "Live preparations: brewing vessel + three teas + three symbiont pairs, all dying-if-stored (CompTemperatureRuinable + CompLifespan on every item)"
   --spec: RotSporeKit content + one small C# doer. Every live-prep ThingDef carries CompTemperatureRuinable (minSafeTemperature +8 °C — a fridge ruins it) and CompLifespan (~2.5 days) — ban 4 enforced by engine; add a selftest/linter check that every def tagged RUT_LivePrep has both comps. `RUT_BrewingVessel` building + RecipeDefs from `RUT_LiveIngredient_*` (stub the ingredients as trader/harvest items if ROT_GUARDIAN_GROVES_1 hasn't landed). Teas: bioregeneration (temporary hediff carrying the luciferium healer comp — verify class name HediffComp_HealPermanentWounds at build), pleasure brew (chemical joy + thought, pure XML), age-reversal (`RM_IngestionOutcomeDoer_AgeReversal`, −5 biological years capped at adult, once per pawn per year via a 1-year `RUT_AgeReversalSated` hediff — card 1 RULED 2026-09-17). Symbionts (ingestible → permanent hediff pairs, exact ratified bargains): Quickflesh (naturalHealingFactor up / hungerRateFactor 2.2), Nightwake (RestFallRateFactor ×0 / lowered break threshold + occasional mentalStateGivers), Sheenblood (grants RUT_SheenSymbiosis from ticket 2 / sunlight-scald — reuse RM_Hediff_SunScald if it fits, else clone small). Plus symbiont #4 mycoid slimification-resistance hediff (inert marker; the Slime kit reads it) and the toxic-injection item (inert payload, ditto). Proof: quicktest — a tea in a freezer shows Ruined; one expires uneaten at ~2.5 days; each symbiont shows both sides of its bargain on a test pawn. Settings: viability strict/lenient.
6. **`ROT_GUARDIAN_GROVES_1`** — M — needs: deploy — after or parallel with 5
   --title "Guardian groves: three tea-source mushrooms that defend themselves (RC1 spore gas, mycelial alarm, grasping-mat lure)"
   --spec: RotSporeKit plants at Prime-like wildPlants rarity (0.01–0.05, UtinniPatches): `RUT_AgelessCap` with RC1 CompActiveGasEmitter + Gas_Damaging (`RUT_ChokingSpores` GasDef on the ported RUT_ToxicSpores DamageDef); `RUT_RegenerantVeil` with a wake-the-network alarm (reuse RM_CompBeastWakeRelay if its trigger fits plant parents, else a small comp: harm → manhunter on tagged fauna in radius); `RUT_EuphoricCrown` ringed by `RUT_FalseFruit` mimics whose harvest applies `RUT_MatGrip` (short immobilize hediff) + the alarm (find the harvest seam — Plant.PlantCollected candidate). Each yields its `RUT_LiveIngredient_*` (comps per ticket 5). AB_AgariluxPrime stays donor-owned, untouched. Proof: quicktest — harvesting each defended plant unprotected visibly hurts/traps/summons; ingredients feed ticket 5's recipes. Settings: guardian toggle, confession label per card 6 RULED 2026-09-17 — framed as the pawn's new conscience; the companion sell-treasures mood debuff lands in ticket 5.
7. **`ROT_HEALTH_SHARING_1`** — L — needs: deploy
   --title "Health-sharing comps: RM_CompWoundLink wound-splitting + RM_HediffComp_KinMending tend-aura, content-blind, tamed included"
   --spec: In `mandrake.rm.creaturebehaviors` (`src/RimMandrake/CreatureBehaviors/Source/`): (1) `RM_CompWoundLink` + `RM_WoundLinkExtension` (tag, radius 12, share 60%, gate ≥8 severity) — on post-damage notification (pick the seam from a source read; post-application only, armor math untouched), move injury fraction to same-tag pawns in radius as fresh injuries on equivalent parts (brain/destroyed parts excluded), reduce victim accordingly; wild and tamed alike. (2) `RM_HediffComp_KinMending` — passive hediff comp, +50% natural-healing severity adjustment while ≥2 same-tag kin in radius. No Rot defs edited: attach nothing — the fauna sitting (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`) assigns variants by XML later. Proof: dev quicktest with two spawned tagged pawns (spawn several — one pawn's result is RNG, `spawn-many-for-bridge-tests`): shoot one, verify injury appears on the other and victim's total drops; aura variant heals measurably faster beside kin. Settings toggle in the creaturebehaviors settings screen.
8. **`ROT_PALE_TREE_1`** — S — needs: deploy — UNGATED (card 4 ruled: cap 2)
   --title "The pale tree: Plant_TreeAnima reskin, psylink capped by a one-entry requiredSubplantCountPerPsylinkLevel list, RUT_PaleMoss subplants"
   --spec: RotSporeKit: `RUT_PaleTree` ThingDef cloning Plant_TreeAnima's comp stack with CompPsylinkable's `requiredSubplantCountPerPsylinkLevel` a TWO-entry list (cap = level 2 — card 4 RULED 2026-09-17) and `CompSpawnSubplant` spawning `RUT_PaleMoss` (glowing, biological light); Wildsteam-flavored label/description (lore text only — no Jawa/faction identifiers in defNames); rare wildPlants entry on RUT_TheRot (UtinniPatches). Royalty-dependent: gate injected `<li>` entries with MayRequire on the li or PatchOperationFindMod — never on a patch Operation. Proof: quicktest with Royalty active — pawn meditates, link progresses, psylink caps at the ruled level and no level-2+ psycast is learnable from it. Settings: spawn toggle.

**Not tickets, on purpose**: fauna attachment (the sitting's), BMT_ wildAnimals
deletions (`BMT_FAUNA_ABSORPTION_1`'s), soil trade (`FUNGAL_SOIL_TRADE_1`),
biome label (`BIOME_LABEL_CAMPAIGN_NAMES_1`), §8 set-piece dressing and the
starving-mat system (v2, cards 3), gourmet line (content wave).
