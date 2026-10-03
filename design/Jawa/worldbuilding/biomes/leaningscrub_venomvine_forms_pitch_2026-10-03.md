# Leaning Scrub — further venomvine forms, a pitch for the owner (2026-10-03)

Item: `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` (from `LEANINGSCRUB_GPT_ENRICHMENT_1` part 1).
Owner, typed on the 2026-09-30 card: *"I really like the different kinds of venom vine. Might
need even more."* **This is design only.** Nothing below has a def, a line of code or an art job.
He rules first; each admitted form is then filed as its own build item, and only then is art queued.

## 1. What exists today (measured 2026-10-03 against `src/` and the artpipe state dir)

Six venomvine defs ship. All are `PlantBaseNonEdible`, Flammability 0.1 (sheet ban 9: no
flammable living flora), Nutrition 0, never auto-cut, and all share one venom.

| def | where | what it does in play | wild commonality |
|---|---|---|---|
| `RM_Venomvine` | `D:\Luke\dev\RimMandrake\src\RimMandrake\EnvironmentalHazards\Defs\ThingDefs_Plants\RM_Venomvine.xml` | The **Desert** form, not ours here: scattered stands, pathCost 60. One scratch on entry, then one per hour while a pawn stays. | Desert roster |
| `RM_VenomvineThicket` | same file | **Base thicket**, the man-high black wall. pathCost 90, 500 HP, harvestWork 1400. Body-size gate: under 0.8 passes freely, 0.8–1.5 threads slowly (a person can force a way in), 1.5 and up cannot enter. | 0.15 |
| `RM_DrippingVenomvine` | `D:\Luke\dev\RimMandrake\src\RimMandrake\LeaningScrub\Defs\ThingDefs_Plants\RM_LeaningScrubVenomvineForms.xml` | **Dripping stand.** Harvest yields 3 `RM_RawVenom`. The stand drops back to 30% growth and beads again instead of dying (a Mod Setting). | 0.05 |
| `RM_TwitcherVenomvine` | same file | **Twitcher.** Lashes once at anything in or next to it (8 damage), then droops, spent, for an hour. A map-level sweep drives it (`RM_TwitcherLash.cs`), since plants only tick every ~33 s. | 0.05 |
| `RM_HollowVenomvine` | same file | **Hollow stand.** Dead grey galleries with a wider free band, so the small runway animals use it as streets and a Jawa-sized pawn can crawl through. No scratch comp. | 0.04 |
| `RM_CrownVenomvine` | same file | **Crown stand.** Rare black column (800 HP, growDays 20), the plain's only flower. During the Stall it pulls up to 30 wild `RM_Dustflutter` within 40 cells into a grey cloud on it. | 0.002 |

**Shared machinery every new form can reuse:**
- `CompProperties_ContactVenom` + `MapComponent_ContactVenom` (EnvironmentalHazards). The scratch and the
  venom `RM_VenomvineVenom` (thorn venom, which sheds 0.5/day): minor at 0.05, serious at 0.30, grave at
  0.60, lethal at 1.0 behind a Mod Setting.
- `ContactVenomImmunity`: a marker on a RACE, so a creature opts out of every venom plant (whole species only).
- `RM_CompBodySizeBarrier`: the small/thread/blocked bands.
- `RM_CompProperties_Smotherable` on all five Scrub forms. A blanket turns a stand into a banked claim with
  a countdown, and it matures into `RM_DeadVenomvine` fuel (yield 25–120 by form).
- One Mod Setting gate key (`RM_MechanicGateExtension`) governs passability for all five.

**Art.** Finished artpipe jobs exist for `RM_DrippingVenomvine`, `RM_TwitcherVenomvine`,
`RM_HollowVenomvine`, `RM_CrownVenomvine`, `RM_VenomvineThicket_v2`, `RM_RawVenom` and the
`RM_Thornhold` nester (`artpipe_state.py find venomvine`, state dir `D:\Luke\dev\_artpipe`). The forms
file says each is wired into its own `Graphic_Random` folder. I found no `.decisions.json` ruling on
venomvine art outside the two assignment registers, which rule placement, not art.

**The visual laws every new form must keep** (from `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\arid_shrubland.md`
§4, §6 and §9, frozen 2026-09-07):
- **Near-black islands** on silver-green fuzz.
- **Man-height or more.** It is the only thing that breaks a person's sightline here.
- **Leaning sunward** like everything else.
- **Each form has its own accent** on the shared near-black (the forms file's own rule).
- **No green**, and **nothing that burns readily while alive**.
- **The wild has no voice, only posture**, so no form may sing, ring or call.
- **No Earth-nameable look-alike.** No briar, bamboo or bramble silhouette.

**What other biomes' hazard plants already own** (from a census of plant comps across `src/`). A new form
must not copy any of these:
- grabbing and digesting creatures: the Miasma (`RM_CompProperties_PlantPredator`)
- gas clouds and spore alarms: Rot-Spore groves
- exploding pods: the Chill, the Deep
- static charge: the Blue Desert
- falling limbs: the Greentide
- static contact spines: the Grey Sea's brine crown and sphere plant

Venomvine already owns contact venom, the size gate, the lash, and the timed harvest.

## 2. Six candidate forms

Each form is one distinct "room" with one mechanic. Each is behind its own Mod Setting, defaults to
shipped behaviour, and degrades to a plain thicket when switched off. None vanishes anything without a
readable sign.

### A. Rearing venomvine — the stand that stands up

**Look (art brief):** A thicket form in the same near-black, leaning sunward like all the others at rest.
It has two states. At rest the canes lie in long sunward sweeps, like the base thicket but laid lower
and flatter. Reared, every cane snaps upright **against** the lean, so a black fan stands straight up
on a plain where nothing else does. Accent: pale bone-grey underside banding that only shows when the
stand is reared. That makes the rear readable at a distance as a pale flash.

**In play:** Anything that pushes into the stand makes the whole stand rear for about two in-game hours.
- A reared stand is a **visible flag**: the player gets a light alert, and any pawn inside the stand is
  revealed (it cannot hide or sneak in there).
- Raiders threading a hedge of it announce themselves.
- A colonist sneaking in to rob a scrap nest announces themselves too, to anything that is watching.
- **Counterplay:** the Gale. When the canopy is whipped to white noise, a rear cannot be told from the
  wind, so the alert is suppressed. That fits the sheet's line that *raids ride the gales*. In the Stall
  the rear is doubly loud.
- **Engine:** a sweep like the twitcher's watches for entry, and the plant swaps to a reared graphic
  state for a while. Small C#, on the pattern already built.

**Why it differs:** It is the only form whose weapon is **information**, not injury. It is also the
biome's ripple law ("the roof that hides you reports you") made into a plant. No other biome has a
plant that betrays you rather than hurting you. The twitcher strikes; the rearing stand tells.

### B. Walking venomvine — the stand that moves with the wind

**Look (art brief):** A long, low, wedge-shaped stand. Its tail is old, near-black, man-high cane. It
tapers sunward into a leading edge of thin new runners laid flat along the ground and pointing sunward.
Accent: the new runners are a dull rust-ochre, soft-looking and thornless. They read clearly as "young
end" against the black tail.

**In play:** In each Gale, a walking stand puts new runners one or two cells **downwind (sunward)** of
its leading edge, and the oldest tail cells can die back into `RM_DeadVenomvine`.
- Across a long game, a stand **crawls across the map** in the wind's direction.
- **Threat:** a colony downwind finds a venom wall creeping toward its fields.
- **Opportunity:** plant one upwind of where you want a wall, and the wind builds your hedge-fort for you.
- **Counterplay:** the soft leading-edge runners are safe and quick to cut (no venom until mature), so
  trimming the front is a cheap, regular chore. Smothering the tail stops the walk.
- **Readable sign:** the rust-ochre front, and fresh runners after every Gale.
- **Hard cap:** total walking-stand cells per map, so a long game is never overgrown.

**Why it differs:** It is the only form that **moves on the map**. Every other hazard plant on the
planet is fixed where it spawned. It turns the biome's one constant, the wind, into a slow front line
the player farms or fights.

### C. Hoard venomvine — the stand that keeps what it catches

**Look (art brief):** A squat, very dense black knot, man-high, with canes coiled inward like a fist
rather than leaning out. Accent: small cold glints scattered through the interior, which are metal,
glass and wire caught deep in the cane. Nothing else in the biome reads as metallic. It looks like a
scrap nest with no bird, and that is the point.

**In play:** Any loose item that lies in or touches the stand is slowly **grown in**. After a few hours
it disappears from the ground into the stand's keeping. This covers:
- dropped gear, and the gear of anything that died in it
- scrap the scrap-nest birds drop
- a raider's lost weapon

The inspect panel lists what it holds. Cutting or smothering the stand gives everything back on the spot.
- **Readable sign:** each held item adds a glint, and the inspect line names it.
- **Counterplay:** keep loose items out of it, or treat it as a treasure chest. A Jawa reason to brave
  venom without any bird at all.
- **Engine:** a held-items list on the comp, saved with the game, filled by a slow sweep.

**Why it differs:** The scrap-nest birds *steal* treasure and the Miasma's predator plants *eat*
creatures. This plant **keeps objects and gives them all back**, and it never kills on its own. It is the
Leaning Scrub's treasure economy (§7 "Scrap nests") without a creature in the loop.

### D. Quench venomvine — the stand that puts fire out

**Look (art brief):** Thick-caned, near-black, with swollen joints every hand-span along each cane, like
knuckles. Accent: the swellings carry a faint wet slate-blue sheen. After it fires, the knuckles are
collapsed and cracked and the cane is scorched, a clear "spent" state.

**In play:** When fire touches the stand, its knuckles burst and soak the surrounding cells in wet sap
that **puts out fire** nearby. Each stand fires once, then slowly recovers over days.
- Pyroculture fire-walls stall against it, and so does the calling-pyre.
- A hedge-fort grown from it does not burn.
- **Counterplay:** burn it twice. The first fire spends it.
- **Readable sign:** the spent, collapsed state and the wet sap on the ground.
- **Engine:** cheap. Vanilla's fire-foam popper (an explosive comp that spawns fire-foam when triggered) on
  a plant is a known pattern here; the Chill and Deep plants already carry explosive comps.

**Why it differs:** It is the first plant on the planet that **fights fire**. That goes straight at the
sheet's strongest theme, *fire implies folly*, along with the giants' fire-stamping and the fire-wall
raids. Every other hazard plant attacks creatures; this one attacks an act.

### E. Sworn venomvine — the hedge-fort strain that spares its own

**Look (art brief):** A cultivated-looking form: the same near-black, but **cut and trained**. Canes are
bound in lines and the top is flat and level, so it is unmistakably grown on purpose. Accent: small knots
of pale, undyed fibre tied along the canes, the planters' marks. It is the only venomvine that looks
tended. Wild stands of it are those a dead settlement left behind.

**In play:** The only venomvine **the player can sow**. It sits behind a research step, the Leaning
Scrub's discoverable craft. Its thorns **spare any pawn wearing its sap-mark**:
- Make the mark from `RM_RawVenom`, the dripping stand's harvest, as a short-lived anointing.
- Marked pawns walk through sworn hedge without a scratch. Raiders, animals and unmarked guests take the
  full venom.
- **Result:** the hedge-fort of the sheet (§7 *transplantable fortification*, §8 *hedge-forts*) becomes
  a real player defence with a gate made of a smell. Re-anointing is a running cost that ties into the
  dripping stand's harvest.
- **Counterplay:** raiders who carry looted mark go through. Local settlements' sworn hedges spare *their*
  people, not yours.
- **Readable sign:** a visible mark condition on the pawn, with its expiry.
- **Engine:** the venom sweep checks one more thing per pawn. Today immunity exists only per species.

**Why it differs:** Every other hazard plant on the planet is neutral and hurts everyone. This is the
only one that **takes sides**, and it is player technology, not scenery. The owner likes powerful tech:
this is the biome's signature defence.

### F. Shedding venomvine — the stand that throws its thorns downwind

**Look (art brief):** A tall, ragged near-black stand whose sunward face is stripped bare, showing pale
scarred cane where thorns have torn away. Downwind of it, the ground carries a fan of rust-coloured
thorn litter. Accent: the litter itself, a V of rust on silver-green, like a tiny echo of the
vaporator V-blight.

**In play:** In each Gale the stand **sheds thorns** onto the cells downwind of it, in a V up to ~8
cells long.
- The thorns lie as litter, and walking on it scratches with the same venom, weaker.
- **Counterplay:** the litter is ordinary filth that colonists sweep with the normal cleaning job, so
  the hazard becomes a chore. Or route around the V. It also fades on its own over a few days.
- **Readable sign:** the rust V on the ground, visible from any zoom.

**Why it differs:** It is the only form whose hazard **leaves the plant** and changes the floor. It is
temporary, cleanable area denial shaped by the wind.

### Considered and left out

- A grabbing or strangling stand: the Miasma owns that.
- A spore or venom-mist stand: Rot-Spore owns gas.
- A glowing stand: the crown already holds the plain's one flower, and glow breaks the near-black islands.
- A ringing or whistling stand: it breaks *"the wild has no voice, only posture"*. Form A takes the same
  idea in posture instead.
- A stand that drinks vaporator output: good fiction, but the vaporators and V-blight it would steal
  from are still unbuilt. Revisit when they ship.

## 3. Recommended set: E, A, C (with D as the cheap fourth)

1. **E — Sworn.** The strongest idea. It turns the sheet's hedge-forts into a real, researchable player
   defence, and it gives the dripping stand's harvest a lasting use.
2. **A — Rearing.** It turns the biome's ripple law into a plant and makes threading a hedge a
   stealth problem. The Gale masking it ties straight into "raids ride the gales".
3. **C — Hoard.** A Jawa treasure chest that fights back. It makes braving venomvine pay without
   another creature in the loop.

**D — Quench** is the cheapest of the six to build (mostly a vanilla mechanism) and the best fit for
the fire theme. If he wants "even more", it is the natural fourth.

**B — Walking** is the most dramatic, but it needs careful caps to stay out of the way over a long game.

**F — Shedding** overlaps the most with what the twitcher and contact venom already do.

Art cost: each admitted form is one new plant render, plus one extra state for A (reared) and D (spent).
The roster cost is small. Every form here would be rare (0.01–0.05), like the four existing forms.

## 4. Questions for the owner (plain language)

1. **How many new kinds of venomvine do you want?**
   - Two (Sworn + Rearing): the fewest new pictures to make, each kind stays special.
   - Three (add Hoard): a treasure reason to go into the vines.
   - Four (add Quench): fire-proof hedge walls too.
   - All six: the vines become the whole story of this biome, but each kind is rarer to meet and more
     pictures are owed.
2. **Who should the sworn hedge let through?**
   - Only people marked with its sap, whoever they are: simple and fair, and raiders can steal the mark.
   - Only your own marked colonists, and never raiders even if they carry it: a safer wall, less drama.
   - Locals' sworn hedges spare their people too, so a local village's walls are a real obstacle to you:
     more world, more work.
3. **Should the hoard stand also keep the gear of whatever dies inside it?**
   - Yes: a grim treasure chest that grows richer the more things die in it.
   - Only items dropped or thrown in, never from the dead: cleaner, less treasure.
   - No hoard at all; leave treasure to the scrap-nest birds.
