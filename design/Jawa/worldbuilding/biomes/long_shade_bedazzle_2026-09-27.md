# The Long Shade — bedazzle to full-mod status (2026-09-27)

**Intent:** the design proposal that takes the livable desert (`RUT_Desert` → `RM_LongShade`, mod `mandrake.rm.longshade`) from a donor-cast biome def to a full standalone RM_ mod — cast partition, invented replacements, flora, marquee rewards, feasibility, ship row, and the card agenda for the owner's sitting. Prepared for a sitting; nothing here is ruled.

_DESIGN pass, 2026-09-27, written against the frozen sheet `desert.md` (amendments add
detail, never change a ruling), `LONGSHADE_RM_MOD_BUILD_1`, `rosters/desert.json`, the
Desert accent of `noncanon_beast_names_poison_miasma_desert_scar_rot_dune_waste_cracked.md`
batch 4c, and normalized against `the_twilight_deep_bedazzle_2026-09-26.md`,
`fever_wood_rm_cast_proposal_2026-09-24.md` and `greentide_risk_reward_2026-09-22.md`.
Tier law: `biome_mod_architecture.md` §7 Q11/Q11a/Q12. Nothing here is a def; nothing here
is filed; every DRAFT name awaits the owner._

**State correction this pass rests on (MEASURED from `src/`, 2026-09-27):**
`LONGSHADE_RM_MOD_BUILD_1`'s STATE table (steps 1–3 "OWED", measured 2026-09-23) is
**stale**. The mod exists: `src/RimMandrake/LongShade/` carries `About/About.xml`, a built
DLL, `Defs/BiomeDefs/RM_LongShade.xml`, and the whole `RM_Vorrel*` family (plant, fruit,
dish, hediffs, recipes, thoughts) moved in and renamed per Q8. The twin `RUT_Desert.xml`
is frozen (header dated 2026-09-24), and
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_LongShade.xml` routes all 51 RSW_ fauna
rows AND the 6 RSW_ flora rows onto `RM_LongShade`. Phase A steps 1–4 are done; this
document is the layer above the split — what the biome is FOR, and what the sitting rules.

## 1. Thesis

**The Long Shade is the biome where position is the whole game.** Its neighbours have
already claimed the other registers: the Stillsand is the desert where time does not pass
and a shadow is property held for life; the Pyrelands boom and burn on a fire calendar;
the seas are dives, leases and hosts. The Long Shade is the one place on the dayside a
colony can actually *live off* — and the sheet built its entire biology from one number,
the distance from this shadow to the next.

Three facts of the frozen sheet are the whole personality, and every idea in this
document is one of them made playable:

- **The sprint economy.** Rest, dash, rest. Body size maps to dash range, so the
  landscape is sorted by size; rest is thermal accounting, not fatigue. Nothing is
  nocturnal because there is no night — activity has a *map*, not a rhythm.
- **Nothing pursues.** Predator and prey both solve positional problems: the predator
  bursts from shadow and is bounded by the trip *back*; the herbivore navigates to a
  patch beyond that return radius. Every patch is a commons holding both at once,
  stratified centre-to-rim. The chase does not exist here.
- **Shade is the only currency — and a roof mints it.** Building a roof manufactures the
  scarce resource, and the moment you do, your base is the best harbour on the route.
  The sheet calls this "the player consequence the biome's gameplay is built on", ending
  with something whale-sized that has walked this line for a very long time and does not
  know you have moved in.

Against the register table the Twilight doc set up: the Grey's reward is a preserved
thing, the Twilight's a living process, the Scald's an industry. **The Long Shade's
reward is a POSITION** — a rim, a staging post, a toll point, the lee of a rock, the best
roof for miles. You do not dig it out, tend it, or get admitted to it. You *hold ground*,
and everything alive contests it with you, politely and permanently. Its emotional shape
is **appraisal, then tenure**: first the player counts distances the way every animal
here does, then they own the address everything else needs.

⇒ **The test for any Long Shade idea: can you point at the ground it happens on — and is
it still worth holding tomorrow?** If a reward is not anchored to a rim, a patch, a gap
or a shadow, it belongs to another biome; if it arrives as a windfall or a boom, it
violates the biome's own law of steadiness (ban 4) and belongs to the Pyrelands. Every
idea in §4 passes both halves; §4's cost lines say what each takes.

## 2. Cast partition table

All **53** fauna rows of the frozen `RUT_Desert.xml` (= the 51-row Utinni patch + the 2
inline `JOE_` rows on `RM_LongShade`), partitioned per Q11/Q11a/Q12. The naming census is
batch 4c of the Desert naming doc (its "36 SWAC canon kept" + 15 in-scope rows + bokka +
feral grazer = 53 checks out against the def exactly). **Verdicts here are
recommendations for the sitting, not rulings.**

Key: **canon** = genuine Star Wars name, stays in the Utinni patch layer forever (Q11).
**→RM** = invented-name port; Q12 says this sitting decides its move to the RimMandrake
tier. **inline** = already native on `RM_LongShade`.

### 2a. The 36 canon rows — stay in `WildAnimals_LongShade.xml`, no action

| band | rows (commonality) |
|---|---|
| huge-herd | Bantha 0.8 · Ronto 0.4 · Skalder 0.3 |
| herd | Jamel 0.4 (Wookieepedia page verified this pass) · Eopie 0.3 · Hrumph 0.3 · IridonianReek 0.3 · Jimvu 0.3 · Kwi 0.3 · Uvak 0.3 · Varactyl 0.3 · Zeer 0.3 · Falumpaset 0.2 · Jakobeast 0.2 · Nerf 0.2 · Shaak 0.2 · TeeMuss 0.2 · FeralGrazer 0.1 (canon Legends, census-corrected 2026-09-24) · Runyip 0.1 |
| herd-small | Nuna 0.2 · Iriaz 0.1 |
| burst-predator | Wraid 0.4 · Gutkurr 0.4 (both owner-slowed to 4.4, legal under ban 3) |
| ambush-small | Kreetle 1.3 · Sketto 0.8 · Gorg 0.4 · LongtailGorg 0.4 · Worrt 0.2 · FrilledGorg 0.2 · Clodhopper 0.1 · Gizka 0.1 · Krykna 0.1 · Voorpak 0.05 |
| ambush-flier | Shyrack 0.6 — **already a real flyer** (`MaxFlightTime` 30, MEASURED in its def; the roster's "flier claim UNMEASURED" note is stale) |
| megafauna | Horax 0.01 |

Uvak also carries `MaxFlightTime` 60 (MEASURED) — the flyers-fly rule is already
satisfied on both canon flyers; no flight work is owed by this sitting.

`RSW_WraidAlpha` 0.15 (the 37th SW-tier row) is an invented *variant of a canon species*
— per the naming rules a variant takes the canon variant shape, so it stays SW-tier
beside its parent. It already carries `RM_CompHeatBurstPredator` (MEASURED): the sheet
§4's burst-grab-retreat flagship is **built and wired**.

### 2b. The 14 invented-name rows — Q12 says THIS sitting moves them to the RM tier

| row (comm.) | name state | evidence | recommendation |
|---|---|---|---|
| `RSW_Bokka` 0.5 | **bokka**, RULED | one home = Long Shade (owner 2026-09-22, recorded in the roster json) | →RM (`RM_Bokka`) |
| `RSW_Ossik` 0.4 | **ossik**, RULED (batch 2 port name) | port of AA_DesertAve, the navigator | →RM |
| `RSW_Kudda` 0.2 | **kudda**, RULED | ⚠️ dual-homed with the Stillsand *by the roster's own law field* — agenda Q6 | →RM, home question to the owner |
| `RSW_Thurra` 0.05 | **thurra**, RULED | port of AA_Gigantelope | →RM |
| `RSW_Vosska` 0.05 | **vosska**, RULED | sand-burrow ambusher (legal off pavement, ban 6) | →RM |
| `RSW_Khorrak` 0.035 | **khorrak**, RULED | flat terrain-mimic (§4 "flat and oriented") | →RM |
| `RSW_Ommok` 0.025 | **ommok**, RULED | slow sand-filter, reads the buried canopy | →RM |
| `RSW_Ulgga` 0.015 | **ulgga**, RULED | slow soft-sand burrower-predator | →RM |
| `RSW_Jellypot` 0.7 | **pommik**, DRAFT (batch 4c) | donor coinage; sits in a shadow and waits — "own a shadow" in one def | →RM; rename rides the batch-4c ruling |
| `RSW_TruffleMole` 0.5 | **pikkut**, DRAFT | ⚠️ wired in BOTH deserts; owner's "desert & extreme desert" note is a CANDIDATE set per his 2026-09-22 correction — agenda Q6 | →RM, home question |
| `RSW_GreatDevourer` 0.5 | **hakkro**, DRAFT | owner's note "relative of the Sarlacc wandering the desert"; kinship goes in the description | →RM |
| `RSW_Groundrunner` 0.5 | **dobbak**, DRAFT | docile mining bear-mole | →RM |
| `RSW_MatureFleshbeast` 0.5 | **vukkoroth**, DRAFT | "immature sarlacc" per the owner's note | →RM |
| `RSW_ShadeWhale` 0.015 | ⚠️ "shade whale" is an English compound, unruled | our own §4c flagship; **fully wired** (MEASURED): `RM_ShadeSeekingWanderExtension` + `RM_FilterFeedExtension` + `RM_CompProperties_DungSeeder` — the item's "filter-feeding C# unbuilt" line is stale | →RM; name offer **thommak** (DRAFT, checker-clean, 0 Wookieepedia hits) — agenda Q5 |

Already inline on `RM_LongShade` (no move needed): `JOE_Landopus` 0.5 (**ippok** DRAFT)
and `JOE_Cephalope` 0.5 (**qorrax** DRAFT) — non-SW donor absorptions, Q9. ⚠️ Cephalope
carries a live CONFLICT: the 2026-09-09 roster *evicted* it under ban 3 (predator, spd
8.8 MEASURED — the fastest thing in the biome) and the owner's round-2 review *imported*
it at 0.5. Both entries stand in `desert.json` today. Agenda Q7.

### 2c. What the free tier looks like after the move — and the holes

If the sitting ratifies 2b, `RM_LongShade` standing alone carries **16 fauna**: a
navigator, a grain-feeder, five subsurface/flat specialists, two shadow-sitters, a
digger, two sarlacc-kin, the megafauna flagship, the two JOE natives, and the bokka.
Rich in the weird bands — and **empty in exactly the bands the sheet calls the campaign's
livelihood**:

| hole (free tier) | why it matters | invented replacement (all DRAFT, Desert accent: doubled consonant, -a/-ik/-ok, 5–7 letters; all pass `check_pseudo_sw_name.py` 6/6, `src/` label sweep clean, Wookieepedia probe 0 exact hits) |
|---|---|---|
| huge-herd / mobile shade wall | every huge-herd row is canon; §4's "a herd is a mobile shade structure" has no free-tier bearer, and §7 names herd beasts the campaign's pack stock | **sollak** (`RM_Sollak`, bs ~4.0) — leggy tower-shouldered giant; standing herds shade each other; `packAnimal true`; carries `RM_ShadeSeekingWanderExtension` (shipped) |
| herd / draught endurer | all ~17 herd rows canon; free tier has **zero pack animals** (all five `allowedPackAnimals` are canon, MayRequire-guarded) | **gennok** (`RM_Gennok`, bs ~2.4) — slow strong endurer that navigates patch to patch, never sprints; `packAnimal true`; plain stats + shade-seeking, no new C# |
| herd-small | Nuna/Iriaz canon; the dense-patch small-life stratum (§4's size-sorting law) is unrepresented | **tebbra** (`RM_Tebbra`, bs ~0.35) — quick close-country grazer confined to dense-patch hills; shade-seeking wander only |
| burst-predator | Wraid/Gutkurr canon, WraidAlpha canon-derived; the free tier has **no predator embodying the biome's signature mechanic** | **dakkra** (`RM_Dakkra`, bs ~1.6) — bursts from shadow, grabs, retreats to cool; carries `RM_CompHeatBurstPredator` (shipped — WraidAlpha's wiring is the copy template) |
| the glitter-birds | owed by the sheet itself (§4c, "Owed": name and def) — tiny shadow commensals living in the whale's shade | **pirrik** (`RM_Pirrik`, bs ~0.1) — real flyer (`MaxFlightTime`, Core stat); v1 = shade-seeking + spawn-weighted near the flagship; true follow-the-whale C# deferred. ⚠️ Wookieepedia fuzzy near-miss *Pirrip* — flag for taste |

Two coins were struck during drafting for real collisions and replaced: *rukka* (live Rot
plant label "rukka cap") and *zhurra* (ruled crags stem *zhurrakor*). The ambush-flier
band (Shyrack's) is left canon-only deliberately — agenda Q4 asks whether it needs a
free-tier bearer or whether pirrik's flock reads close enough.

Pyramid check: of the five, only sollak exceeds bs 2; smalls dominate, and the biome's
45.0%-small pyramid pressure (the roster's own worst-in-sweep reading) is eased, not
worsened.

## 3. Flora

The sheet's §4b flora is further along than any doc records — three of its four named
plants are BUILT and wired (MEASURED from `src/` this pass):

| plant | state | tier | what remains |
|---|---|---|---|
| **the cycle plant — vorrel** | ✅ **BUILT IN FULL, and already in the RM mod**: `RM_Vorrel` / `RM_VorrelFruit` / `RM_VorrelSeedDish` + hediffs + recipes + thoughts in `src/RimMandrake/LongShade/Defs/`, corpse-dispersal via `RM_HediffComp_SeedPassage` and the stagger via `RM_HediffComp_ShadeStagger` (both shipped C#) | RM ✅ | nothing structural — §4.6 gives it its economy register. Name is RULED (`STAGGERSEED_SHIPPING_NAME_1`) |
| **leachmoss** (the racing moss) | ✅ BUILT (`RM_Leachmoss`, environmentalhazards), inline on `RM_LongShade` at 1.5 | RM ✅ | nothing |
| **venomvine** (holds territory by injury) | ✅ BUILT (`RM_Venomvine` + `CompContactVenom` + `MapComponent_ContactVenom`), inline at 0.25 | RM ✅ | nothing |
| **ultracactus** (the buried canopy) | ✅ BUILT (`RSW_Ultracactus`, pure XML) — but riding the **Utinni patch**, so the sheet's own signature plant is absent from the free mod | ⚠️ tier question | agenda Q2: canon status UNCERTAIN — a Wookieepedia search for "ultracactus" hits *The Rise of Skywalker: The Visual Dictionary*, so the word may be genuine canon. If invented (the sheet says "the owner's own"), it moves to `RM_Ultracactus` and anchors the free tier |

The other five patched flora rows partition the same way as the fauna: **canon** —
`RSW_Plant_Chakroot_Wild` 0.3 and `RSW_Plant_HubbaGourd_Wild` 0.2 (both named in Q11a's
own canon list; stay Utinni forever). **Invented/donor-coinage, tier candidates** —
`RSW_SurraGrass` 0.6 (Wookieepedia: no page; nearest hit is a sourcebook — UNCERTAIN,
verify at the sitting), `RSW_VellaraBloom` 0.12 (donor coinage, 0 hits — the *vellara
bloom* rule-8 precedent: offer a rename, don't force one), `RSW_DommoTree` 0.06 (0 hits —
invented; →RM candidate).

**Two NEW flora proposals**, both sheet-derived:

1. **The dew-line flora — `RM_Dewfringe`** (working name, flora naming here runs
   descriptive-English like leachmoss/venomvine). §8's dew line made real: a thin pale
   band-plant that grows ONLY on shade-boundary cells — the rim, not the area. Harvest:
   a small water/plant-matter yield, the densest growth in the biome, and the visible
   "faint living halo" every patch should wear. **Needs small C#**: a growth gate or
   PlaceWorker reading `RM_MapComponent_ShadeGrid.ShadeAt` boundary adjacency — the grid
   is shipped; the gate is ~50 lines on the pattern `RM_Leachmoss`'s spawn gate already
   uses. Ban-8 guard: pale, rim-only, never green in quantity (agenda Q10 confirms the
   ceiling).
2. **The free tier's forage — `RM_UltracactusPad`** (or a pad item on whatever the
   ultracactus becomes). 🔴 The standalone mod has a real hole here: `RM_LongShade`'s
   `foragedFood` is `RSW_RawHubbaGourd` behind `MayRequire` — **standalone, foragedFood
   resolves unset and forageability 0.25 goes inert** (the exact mechanism
   `DESERT_FORAGEDFOOD_INERT_1` measured on the donor def). Pure XML once the
   ultracactus tier lands. Agenda Q3.

Which need C#: dewfringe only (small). Everything else in this section is XML or done.

## 4. The marquee — rewards, experiences, interactions

Each idea: the pitch · what the player does · what they get · what it costs · engine
surface · what it reuses · rank against the finished neighbours · build cost. All names
`RM_`, invented, placeholders. The shade grid is the keystone under every one of them —
`RM_MapComponent_ShadeGrid` is **shipped** (roofed cells read as FULL shade; open cells
score falloff from adjacent shade-casters — which means player construction already
speaks the grid's language).

### 4.0 If we only build three

| rank | idea | one line | why it is in the three |
|---|---|---|---|
| **1** | **§4.1 The best harbour on the route** | Build a roof and everything alive correctly identifies you as the finest shelter for miles — ending with the thommak on your doorstep. | It is the sheet's own declared player consequence, it converts the biome's one currency into the campaign's central base-defence inversion (your walls keep out an ecosystem, not raiders), and the expensive halves are already shipped: the grid reads roofs as full shade, `RM_ShadeSeekingWanderExtension` walks animals to shade, `RM_CompDungSeeder` pays out where the giant rests. What's left is a scorer and a ladder of incidents. |
| **2** | **§4.2 The smoke calendar** | The biome's seasons arrive sideways from fires you never see — shade for everybody, then ash that feeds the ground and locks the sand. | "The calendar of this biome is set by fires it cannot see" is the sheet's strangest sentence and no other biome can have it. One weather family flips hunting, crossing, farming and the subsurface threat map at once — maximum play-state change per def. |
| **3** | **§4.3 The dew line** | The most valuable ground in the biome is a rim, not an area. | Cheapest keystone payoff: it makes the shade grid *legible* every day (you can see where shade ends because life is standing on the line), and it bends base architecture itself — thin buildings out-farm square ones, a shape incentive no other biome gives. |

**If a slot must be cheaper, swap §4.4 The middens in for §4.2** — it is the smallest
build in the document and the most Jawa: the shade is the dig site.

### 4.1 The best harbour on the route — the roof-consequence ladder

**Pitch.** You are manufacturing the scarce resource. Everything notices.

**What the player does.** Builds under roofs, as any colony does — and the biome begins
to arrive, in order of dash range. First tebbra and pommik take up residence in your
outbuildings' shadows. Then herds stage in the lee of your walls before attempting the
next gap — reliable game, delivered. Then a dakkra takes tenancy in the woodshed shadow
and waits, as its species does, for something to arrive overheated. And one day the
region's thommak — which has walked this patch-line longer than your colony has existed
— alters its route to include the largest harbour it has ever seen. It radiates the
crossing's furnace-heat into your courtyard, drops megafauna dung that seeds young
plants and creatures around it (shipped behaviour), and leaves. It will be back. Its
pirrik flock never left its shadow.

**What they get.** The livelihood the sheet promises (§7 "reliable game… a food web
steady enough to hunt as a livelihood"), walking to the door on its own legs; dung-pulse
harvests at home; the sight of the biome's whole hierarchy arranged across their own
ground, centre-to-rim. And the standing choice: the thommak is the route's circulatory
system — kill the visitor for a mountain of meat and you strand its passengers and
starve every patch it was due to fertilise (§4c, verbatim law).

**What it costs.** The harbour is a commons, and the biome's law says a patch holds
predator and prey together. Your courtyard now contains dakkra. Doors matter; pen walls
matter; the deep cool centre of your own base is the contested ground now. And the
thommak's visit is not free — bs ~15 walks where it likes, and a fence is not an
argument it understands.

**Engine surface.** A small MapComponent scoring player-roofed contiguous area against
the map's natural patch sizes (reads the shipped grid); a ladder of 3–4 `IncidentDef`s
gated on score bands (small-life arrival → herd staging → predator tenancy → thommak
visit); the visit worker pathing the flagship to the largest roofed rim and firing its
existing `RM_CompDungSeeder` on departure. The Twilight's gardener events (§3.6 there)
are the same shape and can share review.

**Reuses.** `RM_MapComponent_ShadeGrid` (roofs = full shade, shipped),
`RM_ShadeSeekingWanderExtension`, `RM_CompDungSeeder`, `RM_CompHeatBurstPredator`,
vanilla herd AI.

**Rank.** The Grey's base-threat is being kept; the Twilight's is being unwelcome; the
Greentide's is the jungle growing into your doorway. The Long Shade's is *hospitality
you cannot decline* — the only biome where your own architecture recruits the ecosystem.

**Cost.** Small–medium C# (one scorer component + 3–4 incident workers), no new art
beyond what the cast already owes.

### 4.2 The smoke calendar — haze, ash-pulse, and the locked sand

**Pitch.** Relief arrives sideways, from fires beyond the horizon — and it changes the
rules twice.

**What the player does.** Reads the sky. A **smokehaze** front arrives (weather): the
sun dims, every shadow lengthens, and for a few days the whole biome is shade — herds
cross the uncrossable gaps, hunting is a harvest, caravans move like it is a holiday,
and the player's own pawns can work the open ground. It should read as *relief, not
threat* (§9). Then the ash settles: an **ashfall pulse** (game condition) fertilises —
a real growth surge on ground that is otherwise meagre — and simultaneously packs the
sand hard: burrowing shuts down map-wide, vosska and ulgga go dormant or surface, and
the soft-ground/hard-ground bargain flips until the wind unpacks it.

**What they get.** The biome's only seasons: a crossing window, a hunting window, a
sowing window, and a stretch where the ground itself cannot bite. Planning against the
smoke IS the herder-camp fantasy the sheet's §8 names ("'seasonally' meaning *by smoke*,
not by calendar").

**What it costs.** Symmetry — everything else moves and feeds during the haze too, so
raider-analogue pressure and predator activity rise exactly when you want to be
outside; and the ash lock also disables the player's own use of soft-sand safety
against the surface predators.

**Engine surface.** One `WeatherDef` family (pure XML — Pyrelands' `AshFall` /
`Cinderfall` are the shipped shape); a `GameConditionDef` carrying our shipped
`RM_GlowMultiplierOverrideExtension` for the dimming; a small hook giving the shade
grid a global haze multiplier (⚠️ the grid has no such input today — ~30 lines);
an ash-pulse condition boosting plant growth (⚠️ UNMEASURED which vanilla
`GameCondition` virtual carries plant growth factor — read it off Volcanic Winter's
decompile before pricing); and the sand-lock as a map-component flag the burrowers'
comps check (`RM_MapComponent_TerrainMire` is the terrain-state precedent).

**Reuses.** Pyrelands weather XML, `BiomeGlowPatches` + the glow override extension,
the shade grid, TerrainMire's shape.

**Rank.** The Greentide's Roil is permanent oppression; the Pyrelands' fire is local
and lethal. The Long Shade's weather is *imported generosity* — the only biome whose
best days are another biome's disasters.

**Cost.** Medium: two conditions + one weather family + two small C# hooks; one
UNMEASURED gate (plant-growth virtual).

### 4.3 The dew line — the rim is the real estate

**Pitch.** Temperature drops sharply at the shadow boundary, so dew forms on the line —
and the most valuable ground in the biome is a one-cell ring.

**What the player does.** Farms rims. Dewfringe (§3) and the densest wild growth stand
on the shade boundary; the player learns to read every rock's halo, and their own
buildings grow halos too — so base design bends toward long thin shade-casters over
square keeps, and a wall becomes an agricultural instrument. Water (FlowWorks-relevant)
can be condensed off the line; the vorrel's "protected water pockets" sit where dew
lines close a full ring. (The **Oasis Maker** machine already ships — its
`RM_OasisPlacementScorer` carries a copy of the grid's ShadeAt algorithm — so
*manufactured* water pockets are live content this idea plugs into rather than new
work.)

**What they get.** The only fertile ground in a 0.05-plantDensity biome, food and water
in a rainless place, and a base whose *shape* is a farming decision — plus the visual
signature: every patch wearing its faint living halo.

**What it costs.** Rims are perimeter by definition — farming them means working the
half-exposed edge where the hierarchy puts the weak, with everything else that values
the line standing on it too.

**Engine surface.** The dewfringe growth gate (§3, small C#); optionally a dew-line
terrain fertility overlay derived from the same boundary test; a FlowWorks condenser
hook is optional and separately priced.

**Reuses.** The shade grid (the boundary is one query), Oasis Maker, FlowWorks.

**Rank.** The Twilight's prime ground is a golden well that expires; the Grey's is
wherever the brine has not reached. The Long Shade's is a *line* — no other biome makes
geometry itself the farmland.

**Cost.** Small.

### 4.4 The middens — the shade is the dig site

**Pitch.** The wind never reverses. Everything that blows across this desert ends up in
a shadow — nutrients, bones, debris, wreckage.

**What the player does.** Digs the lee of every rock. Mapgen seeds **midden mounds** on
the shaded lee of shade-casters: minable heaps yielding organic matter, bone, scrap
steel and slag — and rarely a real find (a component cache, an ancient corpse with
gear, a stasis-worthy artefact). The bigger the shade-caster, the older and richer its
midden. Settlement-scale patches hold settlement-scale middens — which is exactly where
the settlements already are, so the richest digs are under somebody's floor.

**What they get.** The scavenger livelihood on the biome's own logic — a Jawa reading
of ground no other biome can offer: archaeology sorted by shadow. Steady, small,
locatable wealth (never a windfall — ban 4's spirit).

**What it costs.** Every midden is inside a shade patch, and every shade patch is a
commons: the dig site has tenants.

**Engine surface.** One `GenStep` placing mound things on lee cells (the grid knows
the shade side; `RM_GenStep_RootCauseways` is the shipped in-house genstep pattern);
mound `ThingDef`s with `mineableThing`/`mineableScatterCommonality` tables — the
Greatbole's mineable heartwood is the in-house mineable-thing precedent.

**Reuses.** Shade grid, genstep pattern, vanilla mining.

**Rank.** The Grey's dig is jacketed salvage in brine; the Warscar's is a battlefield.
The Long Shade's is *aeolian archaeology* — the planet's own sorting machine has been
running for a million years and the player just has to know where it files things.

**Cost.** Small (XML + one genstep).

### 4.5 The last patch before the gap — named gaps, staging posts, toll points

**Pitch.** A stretch too broad for most things to cross is a landmark, a border, and a
story — this biome's river. The last patch before it is the most contested real estate
in the biome.

**What the player does.** Settles (or seizes) a staging post. Mapgen lays the local map
as patch-chains with one *wide gap* — a band of open pavement nothing small can cross —
and the world map names the great gaps as authored places (with the owner, at a
worldmap sitting; roads already run along patch-chains per §8). At a staging post,
everything must stop: herds mass (game), caravans arrive (trade and tolls), and
everything overheated arrives with no alternative (the sheet's "worst moment available"
— fight, take the rim, or push on — now happening at the player's door on schedule).

**What they get.** Position as income: the toll-point fantasy, the caravan traffic, and
the biome's story engine firing at their address rather than somewhere out on the
route.

**What it costs.** Everything needs the staging post, including what you cannot feed or
fight; and a base built on the one crossing is a base everything routes through by
definition — the harbour ladder (§4.1) runs hotter here than anywhere.

**Engine surface.** A `GenStep` variant giving patch scatter a gap-and-chain structure
(medium — this is the one place mapgen itself is touched); world-side, the named gaps
are authored map places (⛔ no worldgen — authoring THE map, the `worldview.py` loop,
owner present per the standing worldmap-docs rule). Caravan/toll interactions ride
vanilla caravan arrival + trade.

**Reuses.** Genstep pattern, vanilla caravans, §4.1's ladder.

**Rank.** Rivers and lanes elsewhere carry you somewhere; the Long Shade's gap is the
place *nothing* carries you — the only geography on the planet defined by what cannot
cross it.

**Cost.** Medium (mapgen), plus an owner worldmap sitting for the names.

### 4.6 The prepared vorrel table — the delicacy that is a near-miss

**Pitch.** A dish that is a controlled near-miss with a lethal parasite — and the
margin for error is the flavour.

**What the player does.** Everything here is BUILT except the economy register: grows
or gathers vorrel fruit (raw = the parasite: seeds hatch in the belly, the victim
staggers toward shade and dies in it — `RM_HediffComp_SeedPassage` +
`RM_HediffComp_ShadeStagger`, shipped), prepares the seed dish (recipe shipped),
serves euphoria (thoughts shipped). What this idea ADDS is the Star Wars cuisine
export: the prepared dish as a high-value trade good on the Rot's live-prep template —
one careful vessel, no bulk recipe, short shelf life — so the money is in the skill
and the freshness, never in a warehouse.

**What they get.** The campaign's cuisine track anchor from this biome; a kitchen
gamble (a botched prep is not a bad meal, it is the parasite); and the corpse-loop as
lived fiction — every animal that dies of the raw fruit colonises a shadow with new
vorrel.

**What it costs.** The plant only grows at protected water pockets (0.1 commonality —
scarcity is the price floor), and prep failure costs a colonist a very bad day.

**Engine surface.** Trade/market XML + one failure-chance hook on the recipe (small);
the live-prep constraints copy `RUT_RotSporeKit_LivePrepRecipes.xml`'s shipped shape
verbatim.

**Rank.** The Twilight's delicacy is alive and tended; the Rot's is a pilgrimage. The
Long Shade's is *risk cuisine* — the only luxury on the planet that can kill the cook's
customer.

**Cost.** Near zero.

### 4.7 Walking with the thommak — the moving harbour

**Pitch.** A megafauna IS a mobile shade patch — the only one that exists. Travel with
it.

**What the player does.** A caravan that falls in beside a crossing thommak inherits
its shadow: crossing heat-load paused while adjacent, gaps otherwise uncrossable made
crossable at the giant's pace. The pirrik flock has done this its whole life; the
player is just the newest passenger.

**What they get.** The biome's one alternative to the staging-post routes — slower,
safer, and going wherever the whale is going, not where you are.

**What it costs.** The route is the whale's; and a caravan in a whale's shadow is
standing next to bs ~15 when the raid, the dakkra, or the storm arrives.

**Engine surface.** Caravan-side this is world-map abstraction (an escort state on a
moving world object), which is real new C# with no shipped precedent in-house —
**priced honestly: this is the expensive one**, and v1 can ship the *map-scale*
version only (pawns adjacent to the flagship read full shade — one grid hook) and
leave world-scale escort to a later wave.

**Reuses.** Shade grid (map-scale), the flagship's shipped wander.

**Rank.** Nothing else on the planet lets you borrow an animal's survival adaptation
by standing in the right place. The most Long Shade sentence in the document.

**Cost.** Small (map-scale v1) / large (world-scale escort — defer).

## 5. Weather / terrain / mechanics feasibility

*(to fill)*

## 6. Ship contribution row

*(to fill)*

## 7. Card agenda

*(to fill)*
