# Oasis-Maker Machines — spec (OASIS_MAKER_MACHINES_1)

**Status: DRAFT for owner review, 2026-09-24.** Redirect of Weeping Stones shine
option 3 ("The Machines That Weep") — the four-state restorable-vane draft in
`design/Jawa/worldbuilding/biomes/weeping_stones_shine_options_2026-09-24.md` is
SUPERSEDED by this; it is mined here only for register and flavor.

> Owner ruling (typed, 2026-09-24, binding): "machines that create oases slowly when
> placed near shaded terrain near rocks. Placement is key. We should guide it with
> green red area selections. Like placing water based generators. I know there was a
> mod that used to grow terraforming slowly so we could base it on that. Makes
> obtaining the ancient machines a treasure type. Unfortunately it's not very
> important for the Jawa utinni scenario but it's a nice mod component. We would need
> to weave it into some quests to obtain or sabotage them."

Tier: **RimMandrake** (`RM_`) — nice mod component, not Utinni-critical.
Bounds: map-scale terrain conversion only (⛔ no worldgen, no planet repaint).
R21: condensate fiction — the machine combs water from moving air against cold
stone; zero rain terms anywhere in label, description or letter text. The dead
option "Born and Dying Water" (owner: "nah too much") stays dead: the machine
GROWS an oasis; there is no oasis-death, overdraw, or water-ledger simulation.
Feature-gated per the biome-kit Mod Settings law; cross-biome enable on the
standard kit screen (it is an `RM_` machine — it works on any map that has shade
and rock, not only in the Weeping Stones).

## 1. The fantasy

The ancients did not find their oases. They made them. Somewhere in the machine —
nobody alive knows where — is the memory of how: how to read the cold face of a
stone, how to comb the moving air until it gives up what it carries, how to feed
one wet thread into the ground until the ground remembers being alive. The
Weeping Stones' vane arrays are the ones that never stopped. This is the rarer
thing: one that *stopped*, and was carried away whole.

Dormant, it is a treasure in the oldest sense — a dense, verdigrised, comb-finned
mass that turns up in sealed vaults and dead settlements and the deep rooms of
ancient complexes, worth a fortune to anyone who understands what it is and
nothing at all to anyone who doesn't. It does not hum. It does not glow. It waits.

Placed — placed *right*, in the blue shade of standing rock, where cold stone can
be its condensation sink — it wakes, and then, slowly, at the patience of a thing
that has already waited an age, it begins to weep. Damp gravel where there was
sand. Soil where there was gravel. Green creeping outward in rings, and at last a
still eye of water at the center with the machine standing over it like a shrine.

§9's sacred ambiguity is the register and stays ambiguous: the description never
rules on whether it is alive. Colonists name what they see — *it drinks the wind;
it is teaching the ground to drink* — and the art carries the upright-comb
silhouette, bone-white and verdigris, so that at distance it reads as one more
crested thing standing at the water. Was the machine built, or grown? The mod
never answers.

## 2. The machine

One ThingDef, three states, one comp.

- **`RM_OasisMaker`** — building, 2×2, minifiable (that IS the treasure form: the
  minified thing is what sits in loot tables and quest rewards). Market value
  treasure-class (~3000–4000, tune later). Upright-comb art per §9; verdigris on
  bone. Flammability 0, high HP — ancient plasteel-grade shell.
- **States** (one enum on the comp, scribed):
  1. **Dormant relic** — minified / just placed, pre-validation. Inspect string:
     "Dormant. It is waiting for cold stone and shade."
  2. **Attuning** — placed on valid ground, first 2 days. Nothing converts yet;
     a faint sheeting-damp effecter on nearby rock is the only tell. (Gives the
     player a cancel window and makes the wake-up an event, not a toggle.)
  3. **Working** — converting, ring by ring. Inspect string reports current ring,
     placement quality, and estimated days to next ring.
- **Power/fuel: NONE — recommended and asserted.** It is ancient; it works or it
  doesn't. Its only "fuel" is placement: cold shaded stone. No power net, no
  refueling job, no breakdown comp. (A machine this rare that also demands a
  power grid stops being a treasure and becomes a workshop appliance. If the
  owner wants a running cost, the right knob is slower rings, not wattage.)
- **Growth model — ring-by-ring terrain ladder**, driven by the comp on rare
  ticks (no MapComponent needed; progress is scribed on the comp and dies with
  the thing):
  - Each cell climbs one rung at a time, Fertile Fields-style stepwise ladder,
    but on machine time instead of colonist labor:
    `Sand/SoftSand → Gravel → Soil → RichSoil` (margin band), and inside the
    innermost ring `Soil → Mud/Marsh → WaterShallow` for a 3×3-ish pool under
    and beside the machine. Only natural loose terrains convert — never floors,
    never constructed terrain, never existing water, never stone (stone is the
    machine's anchor, not its meal).
  - **Rings advance outward**: ring r starts only when ring r−1 is fully
    climbed. Base rate: ring 1 complete in ~3 days; each subsequent ring costs
    ~1.5× the previous (bigger circumference, same one thread of water), so a
    full-quality oasis takes roughly a season and a half to two seasons — slow
    enough to be a colony landmark event, fast enough to enjoy in one game.
  - **Radius cap: 6–9 cells, set by placement quality** (§3). At cap the machine
    keeps its pool topped up fictionally but converts nothing further —
    inspect string flips to "The oasis is made."
  - **What stops it:** reaching cap; being uninstalled (conversion halts, all
    terrain converted so far STAYS — no reversal, per the Born-and-Dying ban);
    being destroyed (same — the oasis outlives its maker, which is exactly the
    dead-ring-around-a-silent-machine image from §8 run forward). Losing its
    shade/rock (roof collapse, mining out the anchoring stone) drops it back to
    Dormant until validity returns; it never un-makes anything.

## 3. Placement — the whole game

The owner's sentence is the design: *near shaded terrain near rocks, guided with
green/red area selections, like placing water-based generators.*

- **Validity inputs.** Shade comes from
  `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs` —
  verified on disk: `public float ShadeAt(IntVec3)` returning a 0–1 score off
  nearby shade-casters (≥80% fill or large plants), with `Recompute()` and
  periodic refresh. Rock is a plain scan: natural rock edifice or rough-stone
  terrain cells. Concrete rule sketch (all numbers tuning knobs in Mod
  Settings):
  - Within R=8 of the placement cell: **shadeScore** = count of cells with
    `ShadeAt ≥ 0.5`; **rockScore** = count of natural rock/rough-stone cells.
  - **Hard floor (refuse to place):** shadeScore ≥ 8 AND rockScore ≥ 15.
  - **Quality above the floor:** `quality = f(shadeScore, rockScore)` mapped to
    0.5×–1.5× ring speed and radius cap 6/7/8/9. Poor-but-legal ground makes a
    small slow oasis; a perfect blue-shade canyon notch makes the storybook one.
- **Refuse vs degrade — BOTH, split at a floor, and here is why.** Pure
  refuse-to-place (watermill style) makes placement a lock-and-key puzzle with
  one answer; pure degradation lets a player plop it in open sand and get a sad
  trickle, which betrays "placement is key." The split keeps the owner's verb:
  red means *no* (the machine will not wake in open nothing — that fiction
  belongs to the seep oases, §2b, whose engine is underground and is not this
  machine), green means *yes, and how green matters*.
- **Overlay.** `RM_PlaceWorker_OasisMaker` — vanilla reference
  `PlaceWorker_WatermillGenerator` (green/red cell painting at placement time);
  our own precedent for a validity PlaceWorker is
  `src/RimMandrake/EnvironmentalHazards/Source/RM_PlaceWorker_OnRequiredVentComp.cs`
  (config-driven `AllowsPlacing`, fails safe). While the ghost is held:
  - GREEN field: the projected conversion footprint at the quality the current
    cell would earn (so the player literally watches the future oasis grow and
    shrink as they slide the ghost around — this is the game).
  - Cyan/edge tint on the contributing shade and rock cells, so the player
    learns WHY a spot is good.
  - RED: footprint when below the hard floor, plus `AcceptanceReport` text
    naming the missing ingredient ("needs more shaded ground nearby" / "needs
    standing rock nearby").
  - Perf note: score is recomputed per ghost move; R=8 is ~200 cells of array
    reads, fine at mouse rate, but cache the rock scan per-map like ShadeGrid
    caches shade.
- **Dependency decision owed:** ShadeGrid lives in CreatureBehaviors. Either
  (a) soft-depend and fall back to a local one-shot shade sampler, or (b) copy
  the ~100-line sampler into this mod and stay standalone. Recommend (b) —
  kit-family law prefers standalone biome-kit pieces, and the grid is small.

## 4. Terramorph study — what is actually on disk

Reported as found, not guessed:

- **There is no mod named "Terramorph" on this machine.**
  `/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/TerramorphArtOverride`
  is OURS (`mandrake.rut.terramorphartoverride`) and is an art override for
  `AA_Terramorph`, a *creature* in Alpha Animals (`sarg.alphaanimals`) — not a
  terraforming mod. The shine-options doc's parenthetical "Base identified:
  Terramorph" traced to this and is a misidentification.
- **The slow-terraforming mod the owner remembers is on disk as *Fertile Fields
  1.6*** (Rainbeau Flambe / Jamaican Castle, `jamaicancastle.RF.fertilefields`,
  `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3225843229/`)
  — the only slow-terrain-conversion mod among the four `terraform` hits in all
  1271 workshop folders (the others: Character Editor, an icons mod, Advanced
  Biomes (Continued) which adds biomes at worldgen, not conversion).
- **Its mechanism, read from `1.6/Defs/Terraformers.xml` + `Source/`:** a
  `DesignationDef` per target terrain plus a custom `RFF_Code.TerraformationDef`
  holding explicit multi-step PATHS — origin terrain → an ordered chain of
  intermediate `Terraform_X-Y` steps (e.g. `WaterDeep → WaterShallow →
  RockyDirt → Stone`). Each step is a buildable frame with work and resource
  cost; colonists construct it and the terrain converts on completion; the next
  step auto-queues. So: **designation + colonist labor + stepwise terrain
  ladder** — no comp tick, no radius rings; "slow" comes from work amounts and
  queued steps.
- **What we take as pattern:** the stepwise terrain LADDER — terrain climbs
  through graded intermediates one rung at a time, which is what makes growth
  legible and reversal-free. **What we do differently:** the driver. Ours is a
  machine's own clock (comp rare-tick) radiating rings, not colonist jobs; no
  designations, no resource cost per cell, no player-chosen target terrain.
- **License: NOT STATED on disk.** No LICENSE file; `About.xml` and `README.md`
  carry no license grant. We take the *pattern* only (def-driven step ladders —
  which our design re-derives with none of their code or defs); if anyone ever
  proposes porting actual Fertile Fields code or XML, that needs a real license
  check with the authors first.

## 5. Acquisition — treasure, woven into quests

Treasure-class means the machine is never shelf goods:

- **Where found:** ancient-complex/ancient-danger loot tables (rare weight —
  roughly ancient-relic tier); quest rewards (below); on Ash'karr, the natural
  home is a Weeping Stones dead-ring site. **Traders: never, initially.** A
  treasure you can buy is a purchase. (Mod Setting can re-enable a very rare
  exotic-goods appearance for people who want it; default off.)
- **Quest hook stubs — explicitly deferred to the quest passes** (these are
  paragraph stubs, not QuestScriptDef work):
  1. **The Silent Ring.** A map event/quest points to a dead oasis — the §8
     rung-4 image, a dry ring of bones around a silent machine — with the
     machine intact and dormant at its center, guarded by whatever moved in
     when the water left. Extract it (uninstall + haul under pressure) and the
     dead place has given up its heart; the reward IS the machine.
  2. **The Weeping Thief.** A rival settlement is growing an oasis — their
     machine, working, rings half-made. A faction (or your own greed) wants it
     stopped: sabotage it where it stands (relations hit with the owners,
     reward from the rival), or steal it mid-growth — the half-made oasis
     stays behind, theirs, a permanent green scar that remembers you.
  3. **The Broker's Price.** A drought-broken settlement offers everything it
     has left for a working oasis-maker delivered and placed. Deliver it and
     gain an ally who owes you their water forever; keep it, and the quest's
     failure letter is written from the place that dried up waiting.
- Sabotage symmetry: OUR placed machine is a legitimate raid/quest target too —
  a working oasis-maker on the colony map should raise stakes, not just value.
  Deferred with the rest.

## 6. Build size

| Piece | Size | Notes |
|---|---|---|
| ThingDef + minified treasure item + comb art (3 facings) | **S** | art per §9 palette; generating-rimworld-sprites pipeline |
| `RM_CompOasisMaker` — states, ring ladder, scribed progress, stop/frozen rules | **M** | the ladder itself is simple; save/load of per-ring progress and the never-reverse guarantee need care |
| `RM_PlaceWorker_OasisMaker` + shade/rock scoring + projected-footprint overlay | **M** | **the honest hard part**: a live projected-footprint ghost that re-scores per mouse move and visibly grows/shrinks — vanilla PlaceWorkers paint static radii; ours paints a *function of the cell* — plus the ShadeGrid dependency decision (§3) |
| Loot-table weave (ancient complex reward weights) | **S** | XML patch weights |
| Mod Settings screen (enable, rates, floor numbers, trader toggle) | **S** | standard kit screen |
| Quest weaves (3 stubs) | **deferred** | quest passes; rimworld-quests skill applies |

Total without quests: one M-heavy sitting plus an art pass. No new frameworks.

## 7. Questions for the owner

Category-level first; nothing here re-asks the ruling.

1. **Does the finished oasis hold real water?** Recommended yes — a small
   `WaterShallow` pool at center, which makes it compose with the greenlit fish
   husbandry work (`WEEPING_STONES_FISH_HUSBANDRY_1`: a made oasis is a
   stockable pool). Alternative is stopping at rich soil + moist ground, which
   is safer but half the miracle.
2. **Permanence when interrupted:** drafted as "everything converted so far
   stays, forever" (uninstall, destruction, loss of shade all just STOP it).
   Confirm that half-made oases as permanent map scars are wanted — it is the
   stronger fiction, and it is what makes the theft quest good.
3. **Scarcity model:** ruin/quest-only with traders off by default — confirm,
   or allow the very-rare exotic trader appearance from the start?
4. **Stacking:** multiple machines on one map each grow their own oasis
   (drafted; no interaction, overlapping rings simply merge). Any appetite for
   a cap, or is more treasure simply more oasis?
