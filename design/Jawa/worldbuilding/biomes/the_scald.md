# The Scald — definition sheet

> 🧊 **FROZEN — `BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07.** The rulings in this
> sheet are frozen: **amendments add detail; they never change a ruling.** The
> unfreeze path is an owner ruling at a sitting, recorded on the item that
> changes it; contradiction cards from the freeze review amend under this rule.


_Owner + BENCH, 2026-09-07, two rounds and ratified ("Write it up!"). Defines
**`RUT_TheScald`** — the BiomeDef FOUNDRY authored in the liquid-biomes
reconciliation (312 `Lake`-painted tiles, region `Scald`), whose `wildAnimals`
shipped deliberately empty awaiting exactly this sitting. **The name THE SCALD
stands** (deep in canon everywhere). Thematic handle: **the boiler of the
dayside** — and its image: **a sea of fire's making, fouled at heart, whose
clean breath waters the world.**_

🔑 **The three seas are three biomes** (owner, this sitting: "this cannot be the
same biome as the Twilight or Grey seas... they are not boiling") — already
satisfied in engine: `RUT_TwilightSea` and `RUT_GreySea` exist with
`terminator_sea.md` as their sheet; the Scald is its own def and now its own
sheet. ⚠️ The two terminator seas' sheet predates the enrichment standard —
their enrichment pass is the next sitting (owner: "we do need to then do the
two seas").

## 0. The measurements everything rests on

Per `LIQUID_BIOMES_MAP_1_RECONCILIATION.md` (MEASURED there): **312 tiles, one
crater** — centre (35,185), radius 10.5, in the **Anvil substellar band (arc
0–30, air +58..+70 °C)**: the hottest lake in the hottest place. Ruled depth
−30 m; live-measured **−350 m**. **A terminal pan: eight rivers end in it;
none leave.** The Greentide's twin groves flank it; the Cracked Lands' storms
are its grandchildren.

Already built (FOUNDRY, the reconciliation pass): six `RUT_ScaldWater*`
terrains to the boiling-lift spec's ruled values — **cyan glow (2,154,229),
burn on traversal, the HotSpring comfort thought** (the water that hurts
nicely), avoidWander, the thirst-mod water tag. The boiling-lift mechanic
itself is ruled at `design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md` (R-B,
2026-08-15).

## 1. What it is

A crater sea that boils. Volcanic heat rises under it and the substellar sun
stands over it, and between the two the water never rests — a roiling,
steaming, mineral-fouled expanse ringed by geysered shores, its steam
climbing forever to the border peaks. In its depths, rainbow sheets of
bacteria and algae coat everything in oddly fuzzy welcome blankets; huge
creatures walk the bottom munching the mats; silver shoals dart above them;
and jellyfish-analogs sail the bubble-lines like little solar sails. **A
place of roiling wonder** (owner) — and the reason anything on the dayside
drinks at all.

## 2. Planetary position

The substellar basin (arc 0–30) × **volcanic crater + terminal pan**: the one
standing water the deep dayside permits, because fire keeps it and the
mountains fence it. The heart of the dayside's hydrology (§3).

## 3. Driving forces

- 🔴 **Fouled heart, clean breath** (owner's ruling): the Scald is
  **non-potable — fouled, not toxic** — far too much salt and mineral
  gathered in a pan that has boiled forever. But **through the distillation
  of its constant boiling it produces the cleanest water on the planet upon
  the peaks of its border mountains, to nourish everything everywhere.**
- **The full chain, named**: the Scald boils fouled → the steam rises clean
  → the border peaks condense it → **the Contagion sterilizes it** (the
  rain-receiving highs are its country by its own placement ruling; R-H7's
  rivers leave its valleys clean) → the rivers carry it → the dayside
  drinks. The planet's water purification runs through the weapon: **the
  Contagion is the filter stage of the distillery.** Nobody planned it. It
  works anyway.
- **Volcanic heat keeps it boiling** (owner) — Sh'kaar's fire cooks the
  lake; the sun merely helps.
- **Eight rivers in, none out** — the pan keeps the salts and returns the
  water as sky.

## 4. How the biology adapted — the roiling wonder

**The admission test: thrives in heat that kills everything else, and joins
the dung-and-mat economy.**

- **The welcome blankets** (owner): rainbow sheets of thermophile bacteria
  and algae coating everything in the depths, oddly fuzzy, banded by
  temperature — **the planet's third rainbow**, completing the triptych:
  the Scarlands' rainbow lies, the Miasma's hopes, the Scald's is the
  oldest truth. The mats at the margins are the planet's **pigment
  source** — rainbow dyes from the most ancient life there is.
- **The bottom-walkers** (owner): huge creatures walking the crater floor
  at −350 m, where the boil gentles to mere heat — armored, slow,
  pastoral: the Scald has **herds**, submerged, mowing the mats as the
  Pyrelands' grazers mow the burn. **Their feces are the food** —
- **The silver shoals** (owner: "as always there are"): darting clouds
  working the dung-fall — the water column's whole budget, and the
  strangest entry the fish roster will ever take.
- ⭐ **The bubble-sailors** (owner): jellyfish-analogs **riding the trailing
  lines of boiling bubbles as their propulsion — like little solar sails**
  — tacking up the vent columns, drifting down, riding again. The biome's
  signature silhouette and kindest resident; pilgrims read their traffic
  the way sailors read gulls.

## 5. Always true

- The water burns to touch and comforts as it burns (the built terrains'
  double truth).
- The sea is fouled; the steam is clean; the peaks are the tap of the
  world.
- The boil never stops — fire below guarantees what the sun cannot.
- The mats coat, the walkers mow, the dung feeds, the silver darts, the
  sails ride: one economy, wholly submerged.
- Two faiths hold the shore and read the same scald as opposite proofs.
- Eight rivers arrive; nothing leaves but sky.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **The Scald is never potable** — no def, tech, or story renders its
   body drinkable; only its distilled breath. (Fouled, not toxic: it
   sickens and disgusts, it does not poison.)
2. 🔴 **Never the terminator seas' biome** — three seas, three defs; no
   shared roster, weather, or terrain with `RUT_TwilightSea`/`RUT_GreySea`.
3. 🔴 **No boiling-immune traversal for free** — crossing scald water
   always costs (the built burn values stand); no native land predator
   hunts the water.
4. 🔴 **No macro-life in the boil itself** — the walkers live at depth
   where it is merely hot; nothing swims the roiling surface layer but
   bubbles and sails.
5. 🔴 **No drained, cooled, or tamed Scald** — the boil is load-bearing
   for the whole dayside; nothing in any register switches it off.
6. 🔴 **No vanilla-Earth flora or fauna** (standard eviction).

## 7. Uniquely available

- ⭐ **The steam-catch** — condensers at the rim's lower vents harvesting
  the cleanest water on the planet, below the Contagion's line: the tap of
  the world, and the Deepwater Compact's headwater interest (whoever holds
  catch-rights holds the monopoly's source).
- **Rainbow pigment** — mat-harvest dyes; the artistic economy's raw color
  (sibling to the Miasma's attar: one restores beauty, one supplies it).
- **The silver harvest** — margin-fishing in water that burns and comforts
  in the same step.
- **The baths** — the cool margins as the planet's one sacred spa: the
  HotSpring thought made pilgrimage (§8).
- **The boiling-lift** — the ruled R-B mechanic layer, spec on file.

## 8. Inhabited objects

- ⭐ **The two-faith shore**: the sacred geography's hinge — Sh'kaar's rim
  site stands ("a forge, not a shore — the water here was never meant for
  drinking, only boiling") while every water-pilgrim knows the rain that
  fills the oases was boiled here first. **The margins hurt and heal
  simultaneously, and both faiths claim it as proof of their own
  reading** — the forge tempers; the water embraces. Bathing rites at the
  cool edges; the witness-trail up the rim; two churches, one shore, no
  concession.
- **The steam-catch works** — condenser lines, cistern heads, the
  Compact's watch on the rights.
- **Geyser fields** at the shore (the vapor law's second densest ground
  after the Forge).
- **The groves** — the Greentide's twin flanks, with the Wildsteam's
  jungle seats a day's walk from the sacred baths they quietly prefer to
  their own Miasma pilgrimage's odds.
- **Wrecks in the shallows** — what the pan swallowed over millennia,
  cooked clean, visible through cyan glow on a still day: salvage priced
  in burns.

## 9. Artistic theme

**"Cyan glow under white steam — the sea that is also a forge."**

- **Light:** steam-diffused substellar glare above; the water's own cyan
  luminescence below (the built glow); rainbow mat-bands where the shallows
  clear; geyser backlight.
- **Palette:** boiling white, scald cyan, thermophile rainbow, basalt rim
  black, the peaks' cloud-cap.
- **Silhouette language:** the crater rim's arc; steam columns as the
  planet's tallest soft structures; bubble-sail flotillas; a
  bottom-walker's back breaking the surface at the deep center, rare and
  enormous.
- **Motion:** perpetual roil, geyser rhythm, sail-traffic, the slow herds
  below.
- **Sound:** the boil's endless breath, geyser percussion, steam-hiss on
  rim stone — and underneath, felt through the feet at the shore, the
  volcanic engine that keeps the whole dayside alive.

---

## Owed

- `SCALD_MECHANICS_1` (to file) — steam-catch industry, margin fishing +
  bath recreation, bubble-sailor and walker set-pieces, geyser fields, the
  boiling-lift integration (spec already ruled), wreck-salvage in burning
  shallows.
- **Roster** — rides the full assignment pass: the four sorts into
  `RUT_TheScald`'s waiting empty `wildAnimals`; mats as flora/terrain
  dressing; `FISH_BY_BIOME_1`'s strangest table.
- ⚠️ **The two seas' enrichment** (owner, this sitting: "we do need to then
  do the two seas") — `terminator_sea.md` predates the enrichment standard;
  the Twilight and Grey Seas get their pass at the next sitting.
- **Salinity ruling recorded** — FOUNDRY's flagged freshwater-default
  question is now answered: fouled mineral broth, not toxic, never
  potable; terrain fields update accordingly at the roster/patch item.
- **Canon sitting (Wednesday)** — the water-chain (Contagion as filter
  stage) into the hydrology doc; the two-faith shore into the sacred
  pass; the steam-catch into the Deepwater dossier.
- **Cross-flow ledger**: the Greentide's flanking groves; the Cracked
  Lands' storms as grandchildren; `VAPOR_EMITTER_PLACEMENT_1` (second
  epicenter); the Forge (native fire, sibling engine); the pigment/attar
  artistic economy.
