# The Sump — definition sheet

> 🧊 **FROZEN — `BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07.** The rulings in this
> sheet are frozen: **amendments add detail; they never change a ruling.** The
> unfreeze path is an owner ruling at a sitting, recorded on the item that
> changes it; contradiction cards from the freeze review amend under this rule.


_Owner + BENCH, 2026-09-07, two rounds and ratified ("YES! Ship the Sump! It's
ready."). Defines `AB_TarPits` (Alpha Biomes). **The biome's name is THE SUMP**
(owner's pick). Thematic handle: **the trap that remembers** — and its image:
**black glass under a sun that never rises, holding a million years of the
unlucky, perfectly.**_

🔑 **The tar's origin is RULED** (owner, 2026-08-15, `hydrology_and_fire_ecology.md`
R-H9): **the tar pits are what the Pyrelands leave behind** — the burning
savanna's endless ash, churned with the violent floods, compressed over eons
into gooey, biologically rich tar. The Sump adds the second half the frozen map
demands: the Pyrelands MAKE the tar; **drainage carries it down and nightward
over geological time, and the Sump — at 1 m elevation, the lowest ground on the
planet — is where it all collects.** The cold past the terminator is the trap's
lid: nothing evaporates back. ⚠️ R-H9's "interspersed at the Pyrelands margin"
did not survive the painted map (all 62 tiles sit at the night edge) — noted
for the freeze review; the make-here/collect-there reading is this sheet's
reconciliation.

## 0. The measurements everything rests on

MEASURED via `src/RimMandrake/Utils/biome_sheet_stats.py` (canon CSV + the 8
overlay plans): **42 tiles just past the terminator on the night side** — sun
median **−10.6°** (below the horizon: permanent deep twilight), temp
p10/median/p90 −4.3 / 1.2 / 14.9 °C (max 20.3), **elevation median 1 m** (max
218), dead flat, **2 water tiles**, no rivers, no rain. Regions: **Nightspill
23, Glass Reach 11**, plus scraps (Damp 4, Twilight Sea 1, Scour 1, Twilight
Crags 1, Sunreach 1). Glass Reach is earned where the sheets cool smooth and
shine under the horizon-glow.

Donor inventory (Alpha Biomes): **corrected** — "sun-baked mud" inverts to cold
tar in the dark. **Kept** — movementDifficulty 4 (tar-mire), the
**subterranean bumbledrone hives** (BENCH's call, roster-pending: warm
heat-huddled colonies tunneling beneath the insulating tar, aggressive at
their entrance mounds — a second "something beneath," in miniature),
forageability 0.8 re-pointed at the edge-flora. **Corrected** — animalDensity
3.5 drops to sparse-but-strange; plantDensity 0.25 fits the edge-ring pattern
(§4). **Evicted** — the vanilla-Earth roster.

## 1. What it is

The planet's oil sump: the lowest basin on Ash'karr, filled by every slow black
flow off the twilight slopes for geological time. Flat black pools and cooled
glassy sheets under permanent dusk, ringed with low waxy plants that glow
faintly where the Junker stations keep their lamp-gardens. Mice run the tar
without a thought. Nothing else touches it — because the tar takes slowly,
keeps perfectly, and everything that ever blundered in is *still in there*.

## 2. Planetary position

Night edge (arc 85–105, sun just below the horizon) × **drainage + cold trap**:
gravity delivers the Pyrelands' product (R-H9) to the planetary low; the chill
keeps it. The bottom rung of the hydrocarbon ladder that continues nightward —
the Blue Desert's chemistry, then the Propane Lakes' liquid sea: three rungs,
one family of cold carbon (`the_blue_desert.md`, `the_propane_lakes.md`).

## 3. Driving forces

- **The tar arrives and never leaves** — made by fire half a world away,
  collected here, sealed by cold.
- **The tar preserves** — anoxic, chill, patient: it entombs all who fall into it,
  preserving their hard structures far into the future (§7).
- **The tar defends** (owner): wonderfully, twice — nothing crosses it
  willingly, and **it can be lit into a terrible smoky horror nothing can
  cross.** From that one fact flows the biome's whole economy (§7b).
- **The tar is partly alive** (§4's last resident).

## 4. How the biology adapted

- ⭐ **The tar beasts** (owner, prior canon confirmed): slow, huge things IN
  the tar, **oozing more of it themselves, accreting it, speeding the
  decomposition of other organics into itself** — feeding on the unfortunate.
  **The third of the Patient family** — with the sarlacc
  (`sarlacc_spec.md`, the type specimen) and the Fever Wood's deep thing:
  *huge, buried, patient feeders; big things hiding beneath the small,
  unmoving until they do.* A formal design family now — their art, dread and
  mechanics should rhyme. Mechanically: dormant set-pieces; deep digs,
  explosions, or greedy pumping wake one, and a woken tar beast is a slow,
  unstoppable, station-eating catastrophe you evacuate ahead of, not fight.
- ⭐ **Sump-mice** (owner): splay-footed, oil-shedding mouse-analogs that
  **run easily over the tar without a thought** — the prey base, the charm,
  and the instrument: mice cross tar freely *except where they won't*. A
  stretch of black the mice detour around is a beast's back. Junkers read
  mouse-lines the way sailors read water.
- ⭐ **The edge-flora** (owner): exotic plants growing ONLY at the pit
  margins, **feeding directly on the tar's energy rather than the sun** —
  chemotrophs under a sun that never rises (the nightside lush rule working
  as written). Signature: **wick-plants** — slow-burning stems harvested as
  candles and lamp-stock; the stations keep cultivated wick-gardens, so the
  biome's only living light is farmed fire-in-waiting.
- **The bumbledrones** — the donor's warm under-layer, kept (§0).

## 5. Always true

- The tar takes slowly, keeps perfectly, and sells it all back to whoever
  digs.
- Mice run the black; where they won't, you don't.
- Every pool is older than every civilization that ever drew from it.
- The stations reek for miles, and their lamps are the only lights.
- Lit tar is a wall of smoke and flame nothing crosses; burnt tar is spent
  tar — demand never ends.
- Something under the deepest black is digesting at its own pace.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No whole Assailant or Rakatan in the tar, ever** (owner: they were
   too powerful) — the wounded and killed sank, so **partial remains only**,
   §GM-tier finds; and **booby traps of that era are MORE likely than
   either** — the dig tables weight accordingly.
2. 🔴 **No tar beast as a fightable spawn** — set-pieces woken by cause,
   evacuated ahead of, never a raid-roster entry.
3. 🔴 **No sun-driven flora** — every native plant here is chemotrophic on
   the tar; a photosynthesis story violates the sheet.
4. 🔴 **No rain, no surface water defs** — the only liquid is tar
   (`LIQUID_TYPES_MOD_1` owns its grades).
5. 🔴 **No warm-climate donor flavor** — "sun-baked" and its kin are
   stripped; this is cold country.
6. 🔴 **No vanilla-Earth flora or fauna** (standard eviction).

## 7. Uniquely available

- ⭐ **What the tar keeps** — excavation as core gameplay: every dig a lottery
  across deep time. Bones and hides of ages the bestiary never named,
  sunken machines, sealed casings — and, per the ruling, **armed booby
  traps preserved in perfect working order**. Every dig is treasure or a
  click. The tar preserves everything, including intentions.
- ⭐ **Tar by the barrel** — the export is *being left alone*: moat-tar for
  everyone on the planet who wants solitude (the droid enclaves above all —
  a tar ring says it perfectly; Moisture Farmer compounds; hermits; the
  paranoid rich).
- **Bitumen** — waterproofing, adhesive, torch-fuel, and **asphalt: the
  Ashfall Road's material now has its source** — the ancients paved from
  these pits, and re-paving stretches is a player project with a supply
  chain.
- **Wick-plant harvest** — candles and lamp-stock; light as a crop.
- **Chitin and honey-wax** from the bumbledrone under-layer (roster call).

## 7b. Playing the Sump — the moat trade

- **The poured moat** (buildable): tar terrain placed as a perimeter —
  raiders path around it or mire in it; **on command it lights** into a
  long-burning wall of flame and smoke that blocks sight and passage, its
  column visible for a day's travel. Consumable by design.
- **The Junker stations** — pumping derricks nodding in the twilight,
  gathering gangs in tar-stiff coats, holding ponds, barrel yards, the
  literal reek (owner) — the biome's only industry, law, and light. Their
  caravans (already canon on the Cracked Lands roads) now have a home
  terminus. Everyone at the derricks knows which ponds you don't pump deep.
- **Player play**: dig the tar, farm the wicks, pump and barrel, read
  the mouse-lines — and never dig past the click you were warned about.

## 8. Inhabited objects

- **The stations** — Junker derricks, holding ponds, barrel yards,
  wick-gardens, stilt bunkhouses upwind of themselves (it doesn't help).
- **The dig fields** — mapped claims, abandoned shafts, the flagged strips
  where something clicked once.
- **Old losses** — half-swallowed machinery from every era of digging;
  derricks the tar took back; the station that pumped the wrong pond.
- **The glass reaches** — cooled sheet-tar plains, walkable, faintly
  shining, mouse-tracked.

## 9. Artistic theme

**"Black glass under horizon-glow, ringed in farmed lamplight."**

- **Light:** permanent deep dusk — the sun a glow below the horizon; the
  wick-gardens and derrick lamps as warm points; a lit moat somewhere far
  off as an orange smear on the underside of the sky.
- **Palette:** every black (wet, glassy, matte), horizon amber, lamp gold,
  the waxy grey-greens of the edge-flora, rust of the derricks.
- **Silhouette language:** dead-flat horizontals broken by nodding derricks
  and flagged dig-claims; the mouse-lines' faint tracery; one wrong smooth
  bulge in the black.
- **Motion:** mice, derrick-nod, lamp-flicker — and the pools, never. Until.
- **Sound:** derrick-creak and pump-thud carrying miles in cold air;
  mouse-skitter on glass tar; underfoot, rarely, a bubble the size of a
  room, rising slowly.

---

## Owed

⭐ **C# kit spec DRAFTED 2026-09-11** (`SUMP_MECHANICS_1`):
`kits/sump_kit_spec.md` — 6 mechanics engine-mapped, 2 ruled-comp reuses,
5 new RM_ classes; 3 owner cards open (rides `KIT_SPECS_CARD_SITTING_1`).

- `SUMP_MECHANICS_1` (to file) — the poured-moat buildable + command
  ignition, the dig-lottery tables (traps weighted first, per ruling), tar
  beast set-piece logic (wake causes, station-eating, evacuation frame),
  mouse-line telegraphy, wick-garden crop.
- **Roster** — rides the full assignment pass: tar beasts (Patient-family
  register with `sarlacc_spec.md` and the Fever Wood's deep thing),
  sump-mice, edge chemotrophs, bumbledrone verdict.
- **Cross-flow ledger**: R-H9 (`hydrology_and_fire_ecology.md`) is the
  tar's ruled origin — the Pyrelands sheet carries the making, this sheet
  the collecting; the margin-interspersal seam flagged for the freeze
  review; the Ashfall Road's asphalt sources here
  (`ASHKARR_WORLD_DEFINITION` roads); the hydrocarbon ladder
  (`the_blue_desert.md`, `the_propane_lakes.md`); Junker identity per
  faction canon at the sitting; `LIQUID_TYPES_MOD_1` gets tar grades.
