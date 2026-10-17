# Thirst and fluids, pass 2a: blind solutions (naive reviewer, 2026-10-17)

Written **before** reading `design/RimMandrake/thirst_fluids_design_2026-10-17.md`. Inputs: the item
`infrastructure/state/items/THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT.md` (owner's verbatim rulings), the
2026-10-16 thirst and sprinkler designs, and the code under `src/RimMandrake/FlowWorks/Source/{Thirst,LiquidTypes}`.
Paths are relative to `/home/mandrake/rm/bench` (`D:\Luke\dev\RimMandrake` is the mirror).

## 0. What the code does today, against the rulings (MEASURED 2026-10-17, by reading the source)

| ruling | code today | gap |
|---|---|---|
| R1 no non-potable auto-gathered | `WorkGiver_FillBottle` is an unconditional opportunistic scanner; `TryFindFillCell` calls `TryFindLiquidCell(... requireFreshWaterOnly: false ...)` (`RM_LiquidBottleUtility.cs:110-117`). Any empty bottle/bucket/barrel near salt, brine, slime or acid gets filled | **violated** |
| R2 buckets/barrels drinkable as fallback | design §3 (2026-10-16) says "bucket / barrel not drunk directly"; containers are whole items with no litre count (`RM_BottledLiquidExtension`: `liquid`, `dirty`, `size` only) | missing; and a 15 L bucket cannot be sipped without a contents count |
| R3 tap mood debuff unless hardy/wild | `JobDriver_RM_DrinkFromTank` exists; no thought on it | missing |
| R4 slime only if no potable | 4 slime rows (`RM_Liquid_Slime{Red,Green,White,Yellow}`) carry **no** `thirstQuality`, so `QualityOf` returns null and they are never drunk | safe today, but no last-resort path at all |
| R5 salt = mental break only | `RM_Liquid_SaltWater` and `RM_Liquid_Brine` are `Fouled`; `JobGiver_RM_Drink` takes Fouled sources whenever they rank best (`RM_ThirstMath.Acceptable` only gates Toxic) | **violated**: a pawn beside the sea drinks salt water as routine |
| R6 traffic (crops, machines) | sprinklers draw from the pipe net (`Source/Sprinklers/*`); hoses exist (`Source/Hose/*`); machines draw via `RM_LiquidNet` | thirst never competes with these: nothing reserves drinking water |

Registry census (parsed as XML, 21 rows): Potable 6 (fresh + five coloured), Fouled 2 (salt, brine), Toxic 1,
unset 12 (incl. four slimes, acid, boiling, icy). No "laxative" or diarrhoea hediff exists anywhere in `src/`.

## 1. The shared core every solution needs (not a solution choice)

- **A source class, separate from quality.** Quality (Distilled/Potable/Fouled/Toxic) says how the water is;
  the rulings add a second axis, *what the pawn may do with it*: `Routine` (auto-drink, auto-gather),
  `LastResort` (slime: drink only when the colony has no potable water the pawn can reach), `BreakOnly`
  (salt, brine: never chosen by `JobGiver_RM_Drink`; only a mental state drinks it), `Never` (acid, boiling).
  One new `LiquidDef` field `drinkClass`, data per registry row, so a new liquid is classified by XML.
- **Auto-gather = `drinkClass == Routine`.** Everything else fills only on an order. Fixes R1 at one call site.
- **Salt water break** (`MentalStateDef RM_SaltDrinkBreak`): eligible when thirst is 0 and `RM_Dehydration`
  ≥ 0.4 and no Routine source is reachable. Pawn walks to salt terrain/container, drinks; gets
  `RM_Thought_SaltRelief` (+8, 4 h) and a fake +0.3 on the need that **reverts** over 6 h, then
  `RM_Hypernatremia` (severity climbs with each salt drink; confusion → seizure → coma; tendable; cured by
  potable water over time). Realism: sea water dehydrates; the relief is a lie, which reads well in a log.
- **Slime drink:** `RM_SlimeLaxative` (24 h, −Moving, filth trail, hunger ×1.5) + `RM_Thought_DrankSlime`
  (−20, 2 days) + a per-kind effect read from the row's existing fields, so nothing is hand-listed:
  red (`damageOnContact AcidBurn`) → internal acid burn on the stomach; green (`damageOnImmersion Rotting`) →
  infection/food-poisoning roll; white (`flammable`) → "fire belly", heat-stroke risk ×; yellow (nothing) →
  laxative only. With GelatinousSlime loaded, its `IngestionOutcomeDoer_SlimeDose` (cures poisons, adds
  Slimification) is the "properties" for *its* slime; soft-reference, never a dependency.
- **Tap debuff:** `RM_Thought_DrankFromTap` (−2, 0.5 day) fired by tank/bucket/barrel drink drivers;
  `nullifyingTraits` Ascetic, Tough; nullified by `RM_ThirstHardyExtension` on genes/xenotypes; skipped
  for pawns whose faction tech is Neolithic or below, wild men, and prisoners from such factions.
- **Dbh mode:** DBH's own drinker runs, so the rulings hold only through data: `WaterExt.SeekForThirst`
  true only on Routine bottles; `dbh_water` terrain tag only on Routine terrain. Slime fallback and the
  salt break are Own-mode features (stated, not hidden).

The solutions differ in **how water moves and how the "no potable anywhere" test is answered** — the hard
part, because it drives traffic and is evaluated on every thirsty pawn.

## Solution A — One drink ladder, items stay items (smallest change)

Extend `JobGiver_RM_Drink` into a fixed ladder; each rung tried only when every earlier rung is empty:
1. potable bottle (inventory, then map) · 2. potable terrain edge (slow, no debuff) · 3. potable **tap**:
tank, bucket or barrel (debuff) · 4. slime (LastResort) · 5. nothing → dehydration progresses → break roll.

- Buckets/barrels get a `CompLiquidLitres` (decilitre int, saved). Drinking takes 1.5 L; at 0 the item
  swaps to the empty def via `MakeContainer` (dirty stage applies). The same comp lets a bucket feed a
  machine or a sprinkler partially. Filled bottles stay whole (1.5 L = one drink).
- "No potable water available" = a `MapComponent_PotableCensus` recomputed every 250 ticks and on
  tank/item change: counts reachable-from-home Routine litres (bottles + tank stock + bucket/barrel litres +
  any potable terrain). Slime rung opens only when the census is 0 *for this pawn's region*.
- Orders: a `Designator_FillWith` on an empty container or tank intake (pick the liquid). Bills on
  machines/sprinklers that need non-potable stock use the same order. Auto-fill = Routine only.
- Traffic: unchanged item hauling. Crops: sprinklers on pipes (ruled). Machines: pipe net or a
  "load from container" job (refuel-shaped, reads `CompLiquidLitres`).

**For:** fits every existing job; easy to verify (one chooser, one census); DBH story is pure data.
**Against:** item traffic grows linearly with colonists (every drink is a walk); the census is one more
map component; tap ranks *below* terrain, so a colony on a river never feels the tap debuff (arguably correct).

## Solution B — Water as plumbing: taps and bottles, no free-standing water in base

Thirst is satisfied at **drinking points**: a new 1×1 `RM_Tap` that sits on a pipe like a sprinkler head
and dispenses from the net (a fountain/cooler in Modern/Futuristic looks). Bottles are for *away*: caravans,
work far from a tap, prisoners, patients. Buckets and barrels are storage that a pawn *may* drink from
when no tap/bottle exists (debuff). A tap counts as "bottle-quality" (no debuff) — or, if the owner reads
"tap on a tank or barrel" literally, a **tap on a tank** takes the debuff and only a cup-station
(`RM_Tap` + a stack of empty bottles nearby, "pour a glass") is debuff-free.

- Net reservation: each liquid net keeps a **drinking reserve** (litres, gizmo on the tank); sprinklers,
  hoses and machines draw only above it (sprinklers already planned a "reserve floor" for VFE; this makes it
  universal and ruled-by-thirst). Thirst never loses to crops silently.
- "No potable" test is per-net: the pawn's reachable nets' potable litres above zero, plus bottles.
  Cheap: nets already cache stock (`RM_LiquidNet`).
- Gathering: pumps and hoses fill tanks; bottles are filled **at taps** (a `FillBottle` job at a tap, not
  at a shore). Shore gathering survives for outposts and potable terrain only.

**For:** the colony's water becomes one number per net, which makes the crop/machine/thirst contest visible
and tunable; traffic shrinks (pawns walk to the nearest tap, like a nutrient dispenser); gives pipes a
reason to exist for every colony. **Against:** new building + art (four looks); a bigger departure from
the 2026-10-16 design (bottles demoted to travel kit); early game before pipes falls back to Solution A's
rungs anyway, so A's code is still needed.

## Solution C — Containers carry a use-policy (storage-settings model)

Every tank, barrel and bucket stack (and each empty-container stockpile) gets a **use filter**, like
vanilla storage settings: allowed liquids × allowed uses {Drinking, Crops, Machines, Washing, Any}.
- Gathering obeys the filter: an empty container auto-fills only with liquids its filter allows, and the
  default filter is "Routine liquids, Drinking". Non-potable gathering happens when the *player* widens a
  filter — that is the order (R1), persistent instead of one-shot.
- Consumers obey it too: a sprinkler draws only from Crops-allowed stock, a machine from Machines-allowed,
  pawns drink only from Drinking-allowed; slime in a Drinking-allowed tank is still LastResort.
- The tap debuff and break/slime rules are as in §1.

**For:** one mental model for all traffic, mirrors RimWorld's own stockpile UI; supports "this barrel is
the farm's, that one is ours" without new buildings; scales to future liquids. **Against:** heavy UI work
(a filter tab on items and buildings), easy for players to misconfigure into a thirst death, and per-item
filters on stackable buckets fight stack merging (filter must live on the stockpile zone, not the item).

## Trade-off table

| | A ladder | B plumbing | C policy |
|---|---|---|---|
| new code | small | medium (tap, reserve) | large (filter UI) |
| fits 2026-10-16 design | yes | partly (bottles demoted) | yes |
| crop/machine vs thirst contest | invisible | visible, reserve | visible, by filter |
| traffic per colonist | high | low | medium |
| R1 enforcement | order designator | taps fill; shores Routine only | filter |
| failure a player can cause | none new | over-spends reserve | thirst death by filter |

## Recommendation (blind)

**A now, B's drinking reserve next, C never as a whole.** A satisfies all six rulings with the least new
surface and is the base layer B needs anyway. The one idea from B worth adopting early is the per-net
**drinking reserve**, because crops and machines will otherwise drain the water the thirst rules protect.
C's filter is the right *long-term* answer for machine loading, but only at zone level.

## Open questions for the owner (card material)

1. Is a pipe-fed tap a "tap on a tank" (debuff) or the civilised way to drink (no debuff)?
2. Salt break: may a pawn drink salt from a *stored* container, or only from the sea/shore?
3. Hardy list: Ascetic and Tough, or more (Undergrounder? Nimble? a gene)? Who counts as "wild and uncivilized"
   — wild men, Neolithic factions, or an ideoligion meme?
4. Does the slime last resort let a colonist walk off-map/out of zone to reach potable water first, or is
   "available" limited to the home area?
