# The Pyrelands — definition sheet

> 🧊 **FROZEN — `BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07.** The rulings in this
> sheet are frozen: **amendments add detail; they never change a ruling.** The
> unfreeze path is an owner ruling at a sitting, recorded on the item that
> changes it; contradiction cards from the freeze review amend under this rule.


_Owner + BENCH, 2026-09-07, two rounds and ratified ("write it up!"). Defines
`ZBiome_Grasslands` (More Vanilla Biomes donor, thin — the identity was already
ours). **The biome's name is THE PYRELANDS** — ruled 2026-08-15
(`hydrology_and_fire_ecology.md`, the naming section); common name **the burning
savanna**. Thematic handle: **the standing burn** — and its image: **a grassland
that has been on fire for twenty-five thousand years, and a people walking the
flame-line collecting a debt.**_

🔑 **This sheet is an assembly on ruled fire canon** — `hydrology_and_fire_ecology.md`
R-H3/R-H4/R-H9 (2026-08-15) and the **FireEcology mod already built** at
`src/RimStarWars/FireEcology/` (scorch-fruit, BlackRain, ash terrains, fulgurite,
firefoam). What this sitting added: the water answer, the Rakatan crop, the four
igniters, the three families, the Tribes' flame harvest and fire raids, and the
Sun-Debt reconciliation.

## 0. The measurements everything rests on

MEASURED off the live CSV: **226 tiles** scattered across **Dune Sea 107,
Pyrelands 63, Anvil 36, Dew Belt 12, Kiln 6, Hollow Verge 2** — the region wears
the name already. Sun median **+56°** (arc 17–57); temp median 53.6 °C
(28..65); elevation ~245 m, mostly flat (136/226); rivers 9 tiles; **rain zero
on 207 of 226**, with Dew Belt outliers to 1,529 mm. The 6 Kiln tiles brush the
sacred dead-flat ground (`sacred_sites_pass_1.md`'s Zizzik/Mob'Unloo contest) —
cross-reference only; that site's canon is its own.

Donor inventory: thin (the More Vanilla Biomes pattern) — vanilla flora/fauna
**evicted and replaced** wholesale; the identity comes from our own ruled canon
and the FireEcology kit, not the donor.

## 1. What it is

Grass to the horizon, gold and dry and growing too fast — and somewhere on the
map, always, **the burn**: a standing fire that has migrated across this
country forever, trailing black land that greens again in days. Dry
thunderstorms walk above it. Birds carry burning twigs ahead of it. Great
shimmering beasts wade through it warm as stoves. And the Deep Desert Tribes
follow its edge with baskets and torches, farming the one crop on Ash'karr
that only fire can open.

## 2. Planetary position

Mid-to-deep dayside scatter (sun +33° to +73°), lobed across the hot flats:
**maximum energy × the engineered grass.** The anomaly is the crop itself
(§3) — which is why the biome reads as one species from horizon to horizon,
and why it exists in country this dry at all.

## 3. Driving forces

**The ruled loop** (owner, 2026-08-15 — R-H3/R-H4, kept verbatim in spirit):

```
freakish growth  ->  standing dry grass, constantly renewed
no rain          ->  it never gets wet
lightning        ->  it lights
fire             ->  dry thunderstorms  ->  more lightning
```

**The fire lights the storm, and the storm lights the fire.** The savanna does
not burn once — it runs a standing burn that migrates across itself forever.
🔴 *Allowed, not simulated*: RimWorld already ships dry thunderstorms,
lightning, and fire spread; the weather table and the flora stats permit the
loop and the engine does the rest.

**The water answer (ruled this sitting): taproot AND feral crop.** The
quickgrass is a **Rakatan-engineered forage crop gone feral** — roots driven
to the water table by design, regrowth in days by design, dominance by
design. The war left a lawn, still working as built. 🔑 **And the theme is
ruled with it** (owner, verbatim in intent): *the Rakatans genetically
modified things — and this is NOT a "genetic tech is bad" argument; it's what
you do with it.* An engineered landscape of generosity, twenty-five millennia
after its gardeners died.

**The permitted rain**: rare, bursty, violent, under unusual wind patterns
(ruled) — and the FireEcology mod already ships its best form:
`RSW_FE_BlackRain`, the filthy downpour dragged out of a fire's own
convection column, *"the one time it truly rains here"* — a storm the fire
makes and the fire dies by. The Dew Belt outlier tiles carry the ordinary
kind.

**The receipts**: R-H9 stands — the endless ash, churned by the violent
floods, becomes the tar (the making here, the collecting at `the_sump.md`).
And the **nightside mirror** stands: Pyrelands↔Propane Lakes, fire-as-danger
against fuel-as-danger, opposite poles of one design.

## 4. How the biology adapted — the fire food-web

**Four igniters** keep the burn alive: lightning (the ruled storm-loop),
**the fire-hawks**, **the furnace-beasts**, and deliberate hands (§8).

- ⭐ **The fire-hawks** (ruled: "absolutely"): raptor-analogs that **carry
  burning twigs to spread the fire deliberately**, flushing prey ahead of
  the flame-line — real Earth behavior (Australia's firehawks), promoted to
  the biome's signature. The burn has shepherds.
- ⭐ **The furnace-beasts** (owner): migratory megafauna on a **thermal
  circuit** — weeks basking in the deep dayside, dense mineral-laden hide
  banking heat like a storage furnace, then walking out across the grass
  **radiating**: shimmering, stove-warm to stand near (travelers follow the
  herds for warmth), and at the discharged end of the circuit their
  bed-down grounds **smolder alight**. Fire-hawks shadow the herds, waiting.
- **The three families** (all ruled): **fire-followers** — hunters working
  the flame edge and the flushed panic; **burrowers** — grazers that let
  the fire pass over and emerge into the fertilized ash; **ash-grazers** —
  the great herds eating the regrowth sprint. The planet's herd country at
  last, justified by the crop.
- The chain, whole: *beast or bolt or bird ignites → hawks spread →
  burrowers dive → the burn passes → scorch-fruit cracks open → Tribes and
  ash-grazers harvest the black → the quickgrass sprints back → the storm
  re-arms.* One machine, four trophic levels, one weather system.

## 5. Always true

- The burn exists somewhere on the biome, always; only its address changes.
- The grass grows obscenely and roots to the water table; the land never
  stays black a week.
- The storms are dry, except when the fire wrings BlackRain out of its own
  smoke.
- Scorch-fruit opens only in the burn and spoils within a day — the harvest
  belongs to whoever walks the flame-line.
- The Tribes farm the fire on their schedule, and an unplanned burn is an
  act of war.
- The herds are the wealth, the hawks are the arsonists, and the
  furnace-beasts are welcome company in the cold and terrible company in
  the dry.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No permanent settlement canon in the burn's path but the Tribes'
   moving camps** — resident factions stay off these tiles; the fire owns
   the deed (road traffic and camps only).
2. 🔴 **No ordinary rain in the weather table** — Clear, dry thunderstorms,
   and BlackRain; the Dew Belt outliers are tile-weather, not biome
   default.
3. 🔴 **No fire-immune flora blanket** — the grass burns by design; a
   fireproof native plant def violates the engine (the scorch-fruit pod's
   sealed casing is the one sanctioned exception).
4. 🔴 **No scorch-fruit that keeps** — spoilage stands; a preserved or
   stockpiled form breaks the harvest's meaning (processed foods at the
   roster's discretion, never the raw fruit).
5. 🔴 **No tame furnace-beast** — you can follow one; nothing on this
   planet keeps one.
6. 🔴 **No vanilla-Earth flora or fauna** (standard eviction).

## 7. Uniquely available

- ⭐ **The flame harvest** — scorch-fruit (`RSW_FE_Plant_ScorchFruit` /
  `RSW_FE_ScorchFruitYield`, already built): sweet, smoky, prized for
  having been worth the risk, gone in a day. The player can walk the
  burn-line too — the Tribes notice how you do it.
- **The herds** — the planet's richest grazing economy: meat, hides, and
  the pastoral game the dryland ladder never allowed.
- **Fulgurite** (`RSW_FE_Fulgurite`) — lightning-glass, "worthless to sell,
  satisfying to find": the beachcombing of a thunderstorm country.
- **Warmth on the hoof** — a furnace-beast herd is a walking hearth;
  caravans route with them toward the cold country.
- **Ash-flush farming** — fields burned on purpose (Firebreak +
  ScorchableGround, already built) yield the regrowth sprint; the §231
  doctrine ("burn it first — farm the fire") as player agriculture.
- **The fire itself** — daughters of the eternal flame, carried as the
  Tribes carry them.

## 8. Inhabited objects — the fire-farmers

🔴 **The Deep Desert Tribes are the fire-farmers of the ruled §231 pattern**
(`hydrology_and_fire_ecology.md`: *"they set fires deliberately, on their
schedule... they are not victims of the fire, they are its farmers — and
they will treat an unplanned burn as an act of war"*).

- **The flame harvest**: controlled burns on the Tribes' schedule; the
  burn-line walked for scorch-fruit; sacred fire carried away — every
  Tribes hearth a daughter of the Pyrelands flame. The Impids (the Tribes'
  fire-callers, `faction_roster_v2.md`) lead the burns.
- ⭐ **Fire raids** (found and canonized): an unplanned burn — a careless
  camp, a raider's torch, a player's mistake — is answered as arson-justice:
  short, furious Tribes raids against whoever broke the schedule.
- ⭐ **The Sun-Debt reconciliation** (ruled this sitting, propagates at the
  canon sitting): **the Tribes worship no sun — they worship the
  repayment.** Ground-fire is the thief's plunder finally brought within
  reach: the sun poured its theft into the grass, and when the grass burns
  the debt is being paid back to the land. **The flame harvest is
  collection.** One line, and the Sun-Debt, the Impid fire-callers, and the
  pilgrimage lock together.
- **On the ground**: moving harvest camps, burn-scheduling cairns, firebreak
  lines cut and maintained (the mod's Firebreak terrain), the blackened
  bands around the Tribes' managed ranges — and the old scars of fire raids
  where somebody once burned without asking.

## 9. Artistic theme

**"Gold grass, black bands, and a horizon that is always smoking somewhere."**

- **Light:** hard high sun over gold; the burn-line's orange wall; dry
  lightning at the storm's base; BlackRain's filthy grey curtain, rare and
  total.
- **Palette:** grass-gold, ash-black in migrating bands, regrowth's
  shocking week-old green, fulgurite white in the black.
- **Silhouette language:** horizon-flat with walking interruptions — herd
  masses, a furnace-beast's shimmer-blur, hawk spirals over the flame-line,
  the Tribes' file of harvesters against the smoke.
- **Motion:** wind in grass always; the burn's slow advance; the sprint of
  regrowth measured in days.
- **Sound:** grass-hiss, distant thunder with no rain in it, the burn's
  crackle arriving before its light, hawk-screams — and after BlackRain,
  the loudest silence on the dayside.

---

## Owed

- `PYRELANDS_MECHANICS_1` (to file) — the burn-line as a persistent
  migrating map presence + where-is-the-burn intelligence; fire-hawk
  twig-carrying; furnace-beast thermal circuit (heat aura, bed-down
  ignition); flame-harvest and fire-raid events (unplanned-burn detection);
  the ruled weather table.
- **Roster** — rides the full assignment pass: fire-hawks, furnace-beasts,
  the three families, the quickgrass and scorch-fruit flora (FireEcology
  defs reconciled, not duplicated).
- ⚠️ **FireEcology deploy collision** — a recorded lesson says two mods
  named "FireEcology" in different tiers once collided silently in the
  deploy tool; verify the folder-name collision is resolved before this
  biome's kit ships.
- **Canon sitting (Wednesday)** — the Sun-Debt reconciliation line into
  `faction_religions.md` §4; the genetic-tech theme line into the Rakata
  spec; the flame harvest/fire raids into the Tribes' dossier.
- **Cross-flow ledger**: R-H9 → `the_sump.md` (making here, collecting
  there); the nightside mirror → `the_propane_lakes.md`; the Kiln overlap →
  `sacred_sites_pass_1.md`; furnace-beast warmth routes → nightside travel
  canon.
