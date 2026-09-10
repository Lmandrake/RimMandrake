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
That spec is the **ambient tier** and stands untouched. This design adds the
**event tier on top**: a plant that gets *soaked* enters a temporary charged
state whose multiplier stacks on the baseline. 🄸 INVENTED: the stack is
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
| `river_steam` | Greentide rivers + the steam | **permanent soak — the biome's weather** (sheet §4: "this is EXPLOSIVE_PLANT_GROWTH_1's daily home") |
| `slime_flood` | Slime floodwater | soaks on its way through |
| `miasma_axis` | fresh side only | the surge line decides which half blooms |
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

## 3. The terminal moment

### The default: the Burst 🄸 INVENTED (proposed for ruling)

An overgrown plant **bursts** — a wet, violent seed-discharge: a visible pop
with a shockwave of chaff and sap, the plant collapses to a spent husk, and a
ring of ground around it is *sown* — sprouts erupt over the following hour.

- **SEES**: swell → tremble → pop; chaff cloud; the husk; the ring greening.
- **DROPS**: the plant's produce at a premium yield, scattered (fruit, seed
  pods, plant matter — biome roster's call), plus the husk as low-grade fuel.
- **THREATENS**: minor blunt/cut damage and knockdown in the burst radius 🄸
  (lethality ceiling is owner Q1); the sown ring does not respect zones —
  sprouts come up in fields, floors, and doorways, and on this planet they
  grow ×4 the moment they exist. The burst is never just fireworks: every
  burst is an encroachment event.

One burst is a startle; the recurring "great moment" is **synchrony** — every
plant a flood soaked charges on the same clock, so a soaked landscape goes up
like popcorn over an afternoon, a rolling wave of pops the player watches from
whatever high ground they kept.

### Per-biome variants — where a sheet's character demands one

| biome | terminal moment | sees / drops / threatens |
|---|---|---|
| **Cracked Lands — the Bloom** (§10b, half-designed there) | the flood's soak runs the default Burst at carpet scale: bloom-crop erupts from the wet mud, charges in synchrony, and seed-storms the pans — then the whole carpet dies to dust on the dry (boom-bust on the flood's clock, sheet-ruled) | SEES: mud → green carpet → chaff white-out → dust. DROPS: **the bloom harvest** — the market-drowning crop, fresh exactly as long as the mud (sheet §11). THREATENS: the carpet wakes the Spenders and pulls every flier and ambush predator in the region — harvesting the bloom means working inside a feeding frenzy on a floor the sheet says never to live on. |
| **Greentide — the Fall and the Fruit** (permanent soak) | no burst-per-plant — here the ladder is trees: grow → crack → **FALL**. The treefall crash IS the biome's recurring terminal moment (sheet: three fellers, one fall event), and the understory's top is **fruiting overload** — the fruit that yearns to be eaten, dumped in gluts 🄸 | SEES: growth inch-by-inch over an hour (sheet §5), doors blocked, canopies toppling. DROPS: greenwood beyond counting; hardwood from fallen giants; the fruit gluts. THREATENS: falling trees crush; **plants grow into and block your doors** (sheet-ruled); the roads move. The blower doorway is the counter-tool, already ruled. |
| **Webwork — the Churn** (drank a river; sheet §4c already rules it) | the engine in **self-consuming mode**: thicket surges close gaps and open new ones; the terminal moment is a path dying around you | SEES: the wall closing. DROPS: nothing — the Webwork's payoff is elsewhere. THREATENS: entombment; the safe path you mapped is temporary. (No new rule — this row just names the sheet's own use of this engine.) |
| **Pyrelands — the Green Flash → the Cure** 🄸 | river-margin floods (R-H1) soak the burn scar: regrowth at watchable speed — then the terminal moment is not a burst but **the cure**: green → gold → standing tinder in hours, and R-H4's fire loop owns the rest | SEES: black scar → green sprint → gold. DROPS: the ash-fertility harvest window (R-H5), grazers following the flush. THREATENS: what you just watched grow is next week's fuel — the bloom IS the fire's supply line, and it grew around your buildings. |
| **Fever Wood — the Nectar Flush** 🄸 (owner Q3) | the giant stillness must hold: no bursting, no surface spectacle. A soak-strike into the mud (a pool disturbance, an oil-seep event) runs the growth **inside the giants** — bark visibly swelling, boughways thickening and re-routing (the sheet's "byways slowly vary", accelerated on screen), and the thornbugs flush with nectar | SEES: the wood itself moving — quiet, creaking, wrong. DROPS: a nectar glut at the herd-groves. THREATENS: a boughway that re-routes under a standing pawn; and a flush is loud news — both raiders smell it. Never touches the pools; ban 5 (no rain, no flowing water) holds. |

**Carve-outs**: terminator/poison forest (R-G3 — never soaks, stays stunted);
the Rot and all fungal biomes (the Sheen is not water — taxonomy); every
saline shore. The exceptions are what make the rule readable, same argument
as R-G3.

## 4. The player verbs — trigger, harvest, survive, weaponize

All 🄸 INVENTED as concrete proposals; the extract's three uses are already
sheet-ruled (Greentide §7).

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

## 7. Owner rulings (2026-09-10 morning batch — all four answered)

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
not soak-triggered: jungle, river and miasma biomes carry visible ever-shifting
growth with a groaning audio bed at all times. Proposed biome mapping (BENCH):
the_greentide (the river), the_miasma, the_rot and the_fever_wood (the
jungles). This is atmosphere on top of the soak mechanic, and for the Fever
Wood it sits alongside — and by the owner's later word tempers — the frozen
sheet's "giant stillness" register: the stillness now groans and shifts.
