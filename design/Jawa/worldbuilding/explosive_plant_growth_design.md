# EXPLOSIVE_PLANT_GROWTH_1 — design draft: the soak, the charge, and the top

_Fable draft, 2026-09-09. PROPOSAL for an owner sitting — nothing here is built,
deployed, or ruled. Sources: `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md`;
`biomes/the_cracked_lands.md` §10b (frozen); `flood_witness_event_design.md`
(beats 4–5, the `RUT_BloomBurst` hook); `biomes/the_greentide.md` §4/§5/§7
(frozen); `biomes/the_fever_wood.md` (frozen); `biomes/the_webwork.md` §4c;
`biomes/the_pyrelands.md`; `PLANT_GROWTH_SPEC.md` (live, DECIDE-owned);
`hydrology_and_fire_ecology.md` R-H1/R-H3/R-H4; `water_taxonomy.csv`._

**Every rule this document invents is marked 🄸 INVENTED.** Everything unmarked
traces to a frozen sheet, a ruled spec, or the item file. The owner's brief,
verbatim from §10b: *"'OMG, what's going to happen?' should be the feeling near
any water-soaked plant"* — visible growth, intimidating, and a terminal moment
designed to recur: *"a great moment again and again."*

---

## 0. Where this sits against standing rulings — nothing is contradicted

`PLANT_GROWTH_SPEC.md` already rules the planetary baseline: every plant grows
×4 (trees ×2.5, terminator ×0.4) via one Harmony postfix on `Plant.GrowthRate`.
That spec is the **ambient tier** and stands untouched everywhere except the three wet
biomes below. This design adds the **event tier on top**: a plant that gets *soaked*
enters a temporary charged state whose multiplier stacks on the baseline.

🔴 **A THIRD TIER, ruled by the owner 2026-09-21: the wet biomes run a higher AMBIENT
rate.** The Greentide, the Miasma and the Fever Wood grow at **×10 instead of the planetary
×4, always, with no soak involved** — verbatim: *"It's the same always-on, but stronger:
x10 instead of x4 growth here."* That is what carries his standing register (*"the
uncomfortable groaning swelling of ever shifting growth"*), and 🔴 **it replaces
soak-bursting in those biomes entirely** — *"x10 is enough"*, because standing water there
would otherwise fire a top over and over. Those plants still Churn (§3); they never Burst.

⚠️ **Two different ×10s live in this document and they are not the same number.** The
ambient ×10 above is a biome's standing growth rate. The soak multiplier below is an event
multiplier that stacks on ×4. Do not collapse them. 🄸 INVENTED: the stack is
multiplicative (soaked ≈ ×10 on top of the ambient ×4 → ~×40 vanilla-relative
— a 3-day plant finishes in under two in-game hours, which is the "watch it
happen" speed). The spec's R-G5 exempt list (anima, Gauranlen, ambrosia,
quest-timed plants) carries over whole: **an exempt plant never soaks.** The
terminator exception carries too — see §1.

## 1. The soak trigger — which waters count

🄸 INVENTED (the roster below is proposed; the taxonomy rows are ruled data).
**SOAKED is a state, not a rate**: a plant acquires it when qualifying water
arrives in quantity — standing in or adjacent to a qualifying wet cell, hit by
a qualifying rain, flooded, irrigated, or splashed with the extract. It decays
back to ambient as the ground dries (hours to a day).

Qualifying, per `water_taxonomy.csv`:

| kind | route | note |
|---|---|---|
| `crack_flood` | the flood — the canonical soak; its row already says `soak->explosive plant growth` | the Cracked Lands bloom |
| `river_steam` | Greentide rivers + the steam | ⚠️ **No longer a permanent soak.** Owner 2026-09-21 replaced permanent-soak-in-the-wet-biomes with the standing ×10 ambient rate (§0). The Greentide is this mechanic's daily home as *growth*, never as a repeating detonation. |
| `slime_flood` | Slime floodwater | soaks on its way through |
| `miasma_axis` | fresh side only | the surge line decides which half blooms ⚠️ the Miasma is a ×10 biome (§0) and therefore never detonates — read "blooms" as Churn, not Burst |
| `red_water` | Contagion rain, and the sterilized descent into dayside rivers (R-H7) | rain-fed soak at the peaks |
| `scald_melt` | peak runoff | floods with a schedule (R-H1) |
| player irrigation | any potable/fresh water spent onto ground | the player verb, §4 |
| Greentide extract | the bottled invocation (sheet §7, ruled) | soak in a jar |

**Never qualifying**: every saline row (`sea_twilight`, `scald_water`,
`waste_brine`, `deep_brine`, `poison_standing`) — salt kills the trigger; the
three not-waters (`sheen_milk`, `rime_etchfall`, `propane_lake`) — the Rot's
fungal surge is its own sheet's business, not this engine; and **trace
condensation never soaks** (`fog_condensate` in dew quantities) — this is
R-G3's terminator exception restated: the poison forest's identity is that its
water arrives as trace, so it stays stunted even under this mechanic. 🄸
INVENTED: quantity threshold — a soak needs *wet ground*, not wet leaves.

## 2. The cycle the player watches

Soak → **charge** → **the top**. During the charge the plant visibly gets
bigger on screen — past its normal full size into an **overgrown** state (🄸
INVENTED: up to ~2× normal visual scale), with escalating tells in fixed
order, the Cracked Lands' own sensory grammar (ground before sky): the ground
darkens and sprouts, the plant swells, its hue deepens and shifts wrong, it
begins to *tremble*, and the last seconds carry a rising creak/strain sound.
Then the top arrives — §3. The tells are the survival grammar (§5): a player
who reads them has time to act; one who doesn't is standing next to it.

## 3. The terminal moment — RESHAPED BY THE OWNER 2026-09-21

🔴 **There are now TWO tops, not one.** Broad swelling, rare drama (owner, 2026-09-21):
nearly every plant visibly swells when soaked, so wet green is always unnerving; only a
designed minority actually detonates. What the majority does is the **Churn**.

### The Churn — the DEFAULT top, RULED 2026-09-21 (owner)

An overgrown plant **splits and dies**, drops its fruit, and **sows sprouts around itself**
which grow and split in their turn. Owner, verbatim: *"add sprouts next to it that keep
going to keep the churn. And the fruit. So I guess this is a reversing back to the fruit
burst at the top, plus the plant dies and makes babies too. Endless churn. That's good."*

- **SEES**: swell past natural size → strain → the plant cracks open and slumps → fruit on
  the ground → a ring of new sprouts already rising.
- **DROPS**: the plant's produce, and the husk.
- **THREATENS**: nothing directly. No shockwave, no damage, no knockdown. The pressure is
  the churn itself — the ground keeps producing plants that produce plants.
- 🔴 **The Churn RESPECTS built ground** (owner, 2026-09-21). Sprouts take fields,
  stockpiles and open dirt; they do not come up on floors or inside buildings. ⇒ **Only the
  Burst violates your walls, and that is what makes the Burst the great moment.**
- 🔑 It is meant to read *"strange and alien and almost frightening"* (his words), not
  pretty and not rewarding-on-a-timer.

### The Burst — the RARE top, RULED 2026-09-20 (owner), unchanged in content

An overgrown plant **bursts** — a wet, violent seed-discharge: a visible pop with a
shockwave of chaff and sap, the plant collapses to a spent husk, and a ring of ground
around it is *sown* — sprouts erupt over the following hour.

- **SEES**: swell → tremble → pop; chaff cloud; the husk; the ring greening.
- **DROPS**: the plant's produce at a premium yield, scattered, plus the husk as low-grade
  fuel.
- **THREATENS**: minor blunt/cut damage and knockdown in the burst radius (lethality
  ceiling is §7.1); **the sown ring does not respect zones** — sprouts come up in fields, on
  floors and in doorways, and on this planet they grow the moment they exist.
  🔴 **RULED 2026-09-20**, chosen over a pop that sows nothing and over a zone-respecting
  middle. That indifference is the mechanic — growth is pressure, not scenery.

The recurring "great moment" is **synchrony**: every plant a flood soaked charges on the
same clock, so a soaked landscape goes up like popcorn over an afternoon.

### 🔴 What decides which — WATER SCARCITY (owner ruling, 2026-09-21)

**A plant adapted to rare water bursts. A plant that lives permanently wet churns.** The
dry-adapted plant gets one chance in years and spends everything on it; the wet-living
plant has no reason to. ⇒ **the driest places hold the most violence**, and the wet jungles
hold none.

This is the same axis as his 2026-09-20 reframing (§8) — behaviour rides the plant's own
identity and adaptation, never the tile it stands on. It is a RULE, not a hand-picked list,
so a player can learn it and a builder can derive it.

⛔ **The per-biome variant table that stood here is DELETED** (owner, 2026-09-09 —
inaccurate material is removed, not bannered). It was superseded as a structure on
2026-09-20 and is now superseded in content too. Its evidence about which plants want which
behaviour survives in `design/RimUtinni/explosive_plant_growth_roster.md`.

### The variants that survive, as plant properties

| key | what the plant does at the top | ruled |
|---|---|---|
| `CHURN` | **the default** — split, die, fruit, sow sprouts that respect built ground | 2026-09-21 |
| `BURST` | the rare violent top, sown ring ignores zones | 2026-09-20 |
| `SLIME` | a top whose ring turns the ground to slime rather than sprouts | 2026-09-20 |
| `TINDER` | a Burst whose debris is fuel — husk, chaff, a ring of quickgrass | 2026-09-20 |
| `RUPTURE` | the contaminated top — see below | 2026-09-21 |
| `FLUSH` | the Fever Wood's interior nectar flush, no surface spectacle | 2026-09-10 |

⚠️ `GLUT` is **retired as a separate key**: the fruit dump is now part of the default Churn,
so a fruit-glutting plant is simply a Churn plant with a heavy produce yield. Owner,
2026-09-21: *"Churn, fruit glut, let it be strange and alien and almost frightening. Just
not explosive in the wet jungles."*

### 🔴 RUPTURE — the contaminated plants, RULED 2026-09-21 (owner)

The question he redirected on 2026-09-20 is answered. A contaminated plant does not burst;
it **ruptures, and turns toward the work of the bioweapon at open throttle**. Verbatim:

> *"Ruptures and turns towards the work of the Bioweapon contagion overdrive. Emits red
> slimes, occular entities, and more little sprouts around it. Red gas/fog in a cloud. Vile.
> Extra mutation hediffs for player caught in this without 100% vac protection."*

- **SEES**: a swelling that goes wrong-coloured, then a rupture rather than a pop — a
  spreading red gas/fog cloud, not a scatter of chaff.
- **SPAWNS**: red slimes and ocular entities, plus little sprouts around it. The plant is
  not reproducing so much as **manufacturing** — which is what the Contagion is
  (`the_contagion.md`: *the weapon at open throttle*; the Helix call it the Overdrive).
- **THREATENS**: the cloud carries **extra mutation hediffs for any pawn in it without 100%
  vacuum protection**. Sealed suits are the answer; nothing else is.
- 🔑 This is the one top that is *vile* rather than merely dangerous, and it is the reason
  the Contagion is somewhere you visit in a suit and leave.


**Carve-outs**: terminator/poison forest (R-G3 — never soaks, stays stunted); the deep
desert (`deep_desert.md` §6 HARD BAN 4 — no fast growth at all); the Rot and all fungal
biomes (the Sheen is not water — taxonomy); every saline shore. The exceptions are what
make the rule readable, same argument as R-G3.


## 4. The player verbs — trigger, harvest, survive, weaponize

🔴 **RULED 2026-09-21: all four verbs are IN, but two of them are deliberately hard.**
Owner, verbatim: *"Support (2) but this would be VERY hard to weaponize and trigger
properly. Support players who try."*

⇒ **Harvest and survive are first-class.** **Trigger and weaponize are possible, expensive
and unreliable** — they are not a toolkit and must never become a convenient button. The
design goal is that a player who works at it can pull one off and feel clever; a player who
expects it to work on demand is disappointed. ⛔ Do not tune trigger/weaponize toward
reliability; do not add aiming aids, previews or guaranteed outcomes. Blowback stays.

The extract's three uses are already sheet-ruled (Greentide §7); everything else below is
🄸 INVENTED as a concrete proposal.

- **TRIGGER — irrigation as a tool and a weapon.** Spending fresh water onto
  ground soaks it: a deliberate bloom on demand. **Cost: the water**, and on
  Ash'karr water is currency (`water_doctrine.md`) — soak-farming a field
  means literally pouring the colony's wealth on the ground, which is exactly
  the tension the water economy wants (owner Q2 asks whether that pump is
  intended). The **Greentide extract** is the concentrated form: force a
  crop, rush a treeline, sabotage a doorway — the sheet's own three verbs —
  expensive, imported, and it charges plants to burst, not just to grow.
- **HARVEST — the jackpot window.** A charged, overgrown plant harvested
  *before* the top yields swollen premium produce — at the risk that it goes
  off in the harvester's face. After the top: normal gleaning of the drop.
  The bloom-crop economy is this at market scale — when a canyon blooms the
  market drowns in it, then nothing for years (sheet-ruled).
- **SURVIVE — read the tells, or defuse.** The §2 tell ladder is the chime
  system in miniature: attention is always enough. Active defenses: **cut a
  charging plant** (defuses it, forfeits the jackpot, and the last swing is a
  gamble); keep ground dry — dry heat repels (Greentide-ruled: the blower),
  and 🄸 salted ground refuses the soak (taxonomy-consistent, permanent
  fertility cost); and never build where water pools — the Cracked Lands'
  NEVER-the-floor rule generalized.
- **WEAPONIZE — the growth does not check faction.** Splash extract or water
  on a raid approach and let the bursts and the sown tangle do the work; rush
  a treeline across a siege lane; sabotage an enemy door the way the sheet
  says yours can be. **Cost**: the same water/extract economy, plus blowback
  — a weaponized soak keeps growing after the fight, toward *your* walls.

## 5. The mechanism sketch — honest about the engine

**Growth math** — cheap and already solved: vanilla plants tick Long (every
2000 ticks); `PLANT_GROWTH_SPEC.md`'s postfix on `Plant.GrowthRate` is the
funnel, and SOAKED is one more branch in that same patch reading a
soak-state (🄸 a map grid or a comp — build's call), plus a small MapComponent
that sets/decays soak from the §1 water sources.

**The visual is the hard part, and here is the truth**: most RimWorld plants
are not drawn per-frame — they are **printed into the map's static mesh
sections**, and a plant's on-screen size only changes when its section is
rebuilt (mesh-dirty). Growth already scales the printed size
(`visualSizeRange`); the steppiness the item warns about is the rebuild
cadence, not the growth rate. So two approaches, proposed as a hybrid:

1. **Staged re-print (the default, ships everywhere)**: soaked plants dirty
   their mesh section on a visible cadence (order of every few in-game
   minutes), giving *time-lapse* growth — stepped, but at soak speed the
   steps land every few real-time seconds and read as relentless. Cost: mesh
   section rebuilds, which is the whole perf question.
2. **Dynamic draw (the close-up layer)**: a capped number of charged plants
   nearest the camera switch to real-time drawing with per-frame scale
   interpolation — smooth swelling and the tremble animation, paid per draw
   call. The cap is a config constant, tuned by the perf gate.

The overgrown state (past-100% scale, hue shift) needs a graphic override
beyond `visualSizeRange`'s cap; the burst itself is an effecter + filth +
damage pulse + sprout-spawn — all vanilla-shaped pieces. ⚠️ Per the standing
rule, **every member named here (`GrowthRate`, `visualSizeRange`, the
mesh-dirty API, section layers) must be verified against the 1.6 assembly
before any patch is written** — this is design, not a build sheet.

### 🔴 The perf gate — measured BEFORE any density promise (the item's own warning)

On a jungle-density quicktest map (~90 s to stand up; Greentide-like plant
fill), measure TPS and frame-time across the matrix **{number of concurrently
soaked plants} × {re-print cadence} × {dynamic-draw cap}**, against the same
map with the mechanic off. 🄸 Proposed pass bar for the sitting: ≤10% TPS loss
at speed 3 with a full-map soak (the flood case — the worst case is the
showcase case). **No sheet, item, or spec promises a soak density until this
table exists.** The measurement is the deliverable of the first build step,
not an afterthought.

### The contract with FLOOD_WITNESS_EVENT_1

`RUT_BloomBurst` (IncidentDef, this item's) is the map-scale invocation: it
soaks every floor cell the flood wetted, spawns bloom-crop sprouts on the
fresh soil, and runs the §2→§3 cycle in carpet synchrony over the following
day — beats 4–5 of the flood design, exactly as drafted there (the quest
passes nothing but the map; intensity, terminal moment and harvest rules are
this item's). If this item ships first, the incident is real when the quest
arrives; if the quest ships first, its stub degrades gracefully as that
design already specifies.

## 6. Intimidation calibration — the owner's line

What keeps the watching *dangerous* rather than cute:

- **Every soaked plant is a countdown.** Not "some plants do a thing" — any
  water-soaked plant WILL reach a top, so the sight of wet green is itself
  the threat. The feeling is dread of an outcome, not delight in an animation.
- **It grows toward your things.** Sown rings ignore zones; doors block;
  Pyrelands regrowth is fuel around your walls. The mechanic's damage is
  mostly *encroachment*, which reads as intent.
- **Overgrown is wrong-looking**: past-natural scale, wrong hue, trembling,
  the strain-creak — body-horror staging, not sparkle. Sound does half the
  work (the Greentide's rule that silence is the scariest signal applies:
  🄸 the last half-second before a burst is silent).
- **Synchrony makes it a weather**, not a critter: a valley going off in
  waves is a spectacle with the scale of the flood that caused it.
- **The player never fully owns the clock.** Irrigation triggers it, but the
  big performances arrive on the water's schedule — flood, surge, storm —
  so mastery is reading and positioning, never scheduling. Attention is
  always enough to survive it (the flood design's law, shared); comfort
  never is.

## 7. Owner rulings

### 2026-09-20 — the default Burst, and it sows

**The Burst's sown ring ignores the player's zones.** He was offered three shapes —
sow-and-ignore-zones, a pop that sows nothing, and a middle that sows only outside built
ground — and took the first. So a Burst is always an encroachment event: sprouts come up in
fields, on floors and in doorways, and grow the moment they exist.

⚠️ **The Burst is no longer the DEFAULT top** — it was on 2026-09-20 and is not now. The
default is the Churn (§3, owner 2026-09-21), and the Burst is the rare violent top reserved
for dry-adapted plants. Everything above about the Burst's *content* still stands; only its
reach changed.

⇒ What this settles beyond §3: the SURVIVE verbs in §4 are load-bearing rather than
optional flavour, because the player must have an answer — cut the charging plant, keep
ground dry, salt it, or never build where water pools.

### 2026-09-10 morning batch — all four answered

1. **Burst lethality: injury+knockdown ceiling.** The default Burst cannot
   down-to-death or kill; lethality is reserved for flagship performances
   (the flood carpet, a sabotaged doorway). Ruled at one stroke with the
   flood design's Q1. Note: `troopersmith1.deathrattle` is live in the mod
   list (MEASURED, ModsConfig 2026-09-10), so even flagship-lethal outcomes
   resolve through Death Rattle's dying-state rescue window rather than
   instant death — that mod is the existing protection layer; do not build a
   second one.
2. **The irrigation pump: working as intended.** Water→food conversion IS
   the sharpened water economy. No brake, no diminishing returns.
3. **The Fever Wood: Nectar Flush variant IN.**
4. **The shipping look: stepped default + smooth close-up cap.** The perf
   gate still runs before any density promise.

### Ambient register ruling (owner, 2026-09-10, verbatim intent)

*"All the jungle and river and miasma tiles should have the uncomfortable
groaning swelling of ever shifting growth."* — a STANDING ambient register,
not soak-triggered.

🔴 **Given a number and a biome list on 2026-09-21:** the register is the **×10 ambient
growth rate** (§0), and it runs in **the Greentide, the Miasma and the Fever Wood** — the
owner picked those three and **excluded the Rot**, because the Rot is fungal, the Sheen is
not water, and its surge is its own sheet's mechanic. For the Fever Wood this sits
alongside — and by his word tempers — the frozen sheet's "giant stillness": the stillness
now groans and shifts.

## Addendum 2026-09-12 — four small proposals salvaged from a superseded duplicate draft

Deleted draft (git holds it); these are PROPOSED, nothing here is ruled:
- Ranged soak delivery: a mortar-style water-charge shell and a thrown
  seed-bomb that starts a surge on impact (WEAPONIZE currently covers only
  hand-splashing).
- A named punishment for missing the bloom harvest window (toxic spore cloud
  or a vermin/Spender swarm) — the boom-bust economy currently prices the
  miss at zero.
- A first-encounter Alert/letter the first time a colony-owned plant reaches
  the tell (the SURVIVE verb names the tells but no notification mechanism).
- Buildables for the trigger verbs: irrigation-channel/sprinkler for SOAK, a
  cistern-breach building for FLOOD.

---

## 8. Owner rulings, 2026-09-20 — and one that changes the SHAPE of §3

Four questions were put to him off the proposed per-biome variant roster
(`Transient/explosive_growth_variants.md`). Three were answered as asked. The fourth
was not, and it is the important one.

### 🔴 THE MODEL CHANGED: the variant belongs to the PLANT, not the biome

Asked whether a clear-sky Burn should defuse a charging plant in the Contagion, he
declined the framing. Verbatim:

> *"It's less about the biome and more about the plants IN that biome having different
> behaviors. Still comes out to differences between biomes, but it really should be
> driven all by plant genetics / identity / adaptation to the intense sunlight and lack
> of water. So this is about 'plants that are contaminated'."*

⇒ **§3's "per-biome variants" is the wrong axis.** A biome does not have a terminal
moment; **a plant** does. Biome-level difference is an *emergent consequence* of which
plants grow where — it is the output, never the input.

🔑 **What this makes right, and what it makes wrong:**

- ✅ The three rulings below still stand — but each is now a property of the plants
  concerned, not a rule attached to a map tile. "The Greentide fruit-glut" means *the
  river-jungle plants* glut; a jungle plant growing elsewhere still gluts, and a
  non-jungle plant growing in the Greentide does not.
- ⛔ **Do not author a per-biome variant table.** The roster in
  `Transient/explosive_growth_variants.md` is superseded as a *structure*; its content
  survives as evidence about which PLANTS want which behaviour.
- 🄸 The natural implementation is a small set of **plant traits** — contaminated,
  fire-adapted, slime-fed, permanently-soaked — carried on the plant def and read by
  the growth mechanism. Trait names above are INVENTED; the *principle* is his.
- 🔑 This aligns with `SPECIES_TRAITS_OVER_APTITUDES_1`, where he made the same move
  for species: *"we should consider deeply making better traits that might do a better
  job of capturing these fine points and nuances."* Same instinct, different subject.

**"Plants that are contaminated"** is his own phrase for the Contagion case and is the
worked example: the behaviour rides the plant's contamination, not the sky above it.
Whether sunlight/water adaptation defuses a charge is now a question about a plant
trait, and is **NOT yet ruled** — it was asked as a biome question and he redirected it.

### RULED as asked

| case | ruling |
|---|---|
| **Greentide** | ⚠️ **Retired 2026-09-21.** The fruit dump is now part of the default Churn, so there is no separate fruit-glut behaviour; those plants are Churn plants with a heavy produce yield. The intent — keep the Burst rare and frightening — is carried by the water-scarcity rule instead. |
| **Slime** | **Slime comes up, not sprouts.** The burst still pays its harvest, but the ring it sows turns the ground to slime — farming there becomes a decision, not free food. |
| **Pyrelands** | **Burst leaves dry tinder** — husk, chaff, a ring of quickgrass, all fuel. Growth loads the fire loop instead of fighting it. CHEAP: the normal Burst with different debris. 🔑 `TINDER` **is a Burst**, so under ruling 4 it only lands on plants whose own identity is dry-adaptation — which the Pyrelands' burn-scar flora are. A wet-living plant cannot carry it. |

⚠️ Each is recorded above as a plant property, per the reframing.

### Carve-out §3 omits — MEASURED 2026-09-20

**`RUT_ExtremeDesert` (the deep desert) must not soak or fast-grow at all.**
`biomes/deep_desert.md` §6 HARD BANS item 4 is explicit and linter-checkable:
*"No fast growth. The planet's freakish-growth fact does NOT apply here — the same
deliberate exception the terminator gets (R-H2b)."* The design doc never mentions it.
Mapping `deep_desert` → `RUT_ExtremeDesert` is by elimination: three desert sheets
(`deep_desert`, `desert`, `the_blue_desert`) against three desert BiomeDefs
(`RUT_ExtremeDesert`, `RUT_Desert`, `RUT_BlueDesert`); the sheet names no defName
itself.

---

## 9. The 2026-09-21 sitting — the owner reshaping the whole capability

He opened it with a worry: *"I fear that this entire capability has become distorted, and
I'd like to restore its original intention."* Seven rulings came out of it. They are recorded
in place above; this is the index.

| # | ruling | where |
|---|---|---|
| 1 | **Broad growth, rare drama.** Nearly every plant swells when soaked; only a designed minority detonates | §3 |
| 2 | **The Churn is the default top** — split, die, fruit, sow sprouts, repeat. Endless | §3 |
| 3 | **The Churn respects built ground; only the Burst violates it** | §3 |
| 4 | **Water scarcity decides who bursts** — dry-adapted plants burst, permanently-wet plants churn | §3 |
| 5 | **Contaminated plants RUPTURE** — red gas, red slimes, ocular entities, sprouts, mutation hediffs without full vac protection | §3 |
| 6 | **The wet biomes run ×10 ambient and never detonate** — Greentide, Miasma, Fever Wood | §0, §7 |
| 7 | **All four player verbs, but trigger and weaponize stay very hard** | §4 |

**What this does to the original intention.** His two founding lines were *"intimidating
anywhere water soaks a plant"* and *"a great moment again and again"*. The design had been
answering the first by making 95 plants burst, which was quietly killing the second. The
Churn/Burst split answers both: wet green is always unnerving because you cannot tell which
plant is loaded, and the detonation stays rare enough to still be an event.

### 🔴 What this OWES — the roster must be rebuilt

`design/RimUtinni/explosive_plant_growth_roster.md` assigns 58 plants `BURST` and 13 `GLUT`
under the old model. Both keys are now wrong at that scale: `GLUT` is retired into the
default, and under ruling 4 a plant only bursts if its own identity is dry-adaptation.
⇒ **The roster is regenerated against water-scarcity, not edited.** Expect the great
majority of the 95 to land on `CHURN`. Nothing is built from the old roster.
