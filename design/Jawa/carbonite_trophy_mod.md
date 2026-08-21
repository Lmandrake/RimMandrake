<!-- status: aspirational -->
# Custom Carbonite Trophy Mod — PARKED DESIGN (author fresh for 1.6)

**Status:** ⭐ GREENLIT concept, PARKED for authoring. User 2026-08-06: the donor Outer Rim carbonite is "so much lamer than the carbonite I thought we might have… make our own that would be SO MUCH COOLER."
**Owner:** ours to build. No donor does this — see "Why not the donor" below.
**Pillar posture:** economy/logistics sink, NOT a power spike. Must pass the 7-question test by construction (raises no player *combat* ceiling; it's a costed conversion of prisoner + materials → a good).

---

## Why not the donor (premise correction, SRC-audited 2026-08-06)

The "carbonite" in **Outer Rim Core** (`Hediff_Carbonite.cs` + `Ability_CryobanProjector.xml` + `Damage_CryoBan`) is a **cryoban WEAPON**: it shoots a freeze cone/projectile that applies a **timed** `Hediff_Carbonite` driven by `HediffComp_Disappears` — the pawn is frozen in a `Stance_Frozen` for `ticksToDisappear`, then **thaws automatically**. It is a combat crowd-control freeze (a fancy EMP/cryo-grenade), *not* a permanent sellable slab, not a display piece, not a captive-disposal system. There is **no tradeable carbonite-slab ThingDef and no permanent freeze building anywhere on disk** [grep-confirmed across all Outer Rim modules]. So the evocative "Han Solo frozen on Jabba's wall" fantasy is entirely unbuilt — which is exactly why building our own is worth it.

---

## The vision (what makes ours cooler)

Turn a **captured/downed pawn** into a **permanent carbonite slab** — a physical, haulable, placeable, tradeable object that is simultaneously: a captive-disposal sink, a wealth-conversion good, a **wall-mountable trophy** (beauty/impressiveness for a throne-room or Hutt-palace aesthetic), and a **reversible stasis vault** (thaw later for ransom, interrogation, or to reclaim a pawn). It is diegetically pure Star Wars and mechanically a logistics puzzle, not a stat boost.

### Core object: the Carbonite Slab (ThingDef, a Building or minifiable item)
- Holds a **fully preserved pawn** inside it (store the pawn like a corpse/casket holds its occupant — pawn suspended, ages 0, no needs, no rot).
- **Haulable + minifiable** so you can carry it, store it, load it on the gravship, sell it, or install it on a wall as decor.
- Carries **beauty + impressiveness** stats scaled by the occupant's value → doubles as throne-room / Hutt-court decoration. A frozen Imperial officer on your wall is a flex.
- **Market value = f(inputs consumed + occupant's own market value + a grade multiplier)** — a *conversion*, never minting free wealth (see anti-exponential guard).

### The freezing station (Building) + recipe (RecipeDef → JobDriver at the station)
Freezing is a **deliberate, costed operation at a powered building**, never a free right-click:
- **Consumes the pawn** (must be downed or a prisoner; the pawn is removed from the colony and sealed into the slab).
- **Consumes materials** (design target, tune at authoring): steel + plasteel for the slab casing; a **cryo/coolant reagent** (chemfuel, or a custom "carbonite compound" you refine) as the freezing medium; **components** (industrial; **advanced components** for high-value or Force-sensitive targets).
- **Draws heavy power** during the freeze cycle (a running carbonite chamber pulls a big wattage spike; brownout risk = a real logistics cost).
- **Takes work + skill** (a crafting/intellectual bill with a time cost, so it occupies a colonist).

### Reversibility: the thaw (the loop that makes it more than a trash can)
- A **thaw bill** at the same station releases the pawn **alive** (optionally with a temporary "hibernation sickness" debuff — carbon-freezing sickness / temporary blindness, canon nod to Han Solo).
- Enables the full loop: **capture → freeze (store/sell/display) → later thaw for ransom, recruitment, interrogation, organ harvest, or release.** A frozen enemy commander becomes a bankable asset you cash later.
- Selling a slab = permanent disposal + payout; thawing = you keep the pawn. You choose per-slab.

### Grades (rarity gating, keeps it special-occasion)
- **Common captive** → cheap freeze, modest slab value.
- **Named officer / bounty target / Force-sensitive** → costlier freeze (advanced components, more coolant), rarer, **much higher** slab value + impressiveness. High-tier freezes are a *project*, not a grind.

---

## Hutt synergy (why it fits the campaign economy)

Slabs are the ideal **Hutt-market good**: the Hutt Cartel's "tradeable-regardless-of-standing" verb means you can always fence a frozen captive to them even when hostile. Carbonite trophies become a **signature Jawa→Hutt revenue stream** — the Jawa scavenge/capture, freeze, and sell bodies-as-goods to the slugs. Thematically and economically coherent with the desert-scavenger identity.

---

## Danger / cost hooks (optional, to keep it from being a pure win)

To keep it anti-exponential and *interesting*, layer in downside risk:
- **Freeze malfunction:** a botched freeze (low skill / interrupted power) can kill or maim the occupant → you lose the captive and the materials. Skill + stable power matter.
- **Slab is a target:** a valuable slab raises colony wealth (raid-scaling) and can be **stolen** by raiders or reclaimed by the faction whose officer you froze — an "extraction raid" to free their frozen hero. Turns a trophy into a liability worth defending.
- **Thaw shock:** thawed pawns arrive with a temporary debuff (blindness/weakness), so a thaw-for-combat cheese is blocked.
- **Upkeep option:** slab optionally needs power to stay frozen; cut the power (raid, brownout) and it slowly thaws on its own → mini-crisis.

---

## Anti-exponential guard (7-question posture)

1. **Raises player combat ceiling?** No — it's an economy/logistics building, no weapon/stat buff to the player.
2. **Free wealth?** No — value tracks consumed inputs + the occupant's own market value; it's a conversion, gated behind components + power + skill + a live captive.
3. **Trivializes a challenge?** Partly *removes* the prisoner-management chore (a sink for pawns you'd execute/release) — acceptable, and the malfunction/theft hooks add offsetting risk.
4. **Compounding?** No feedback loop — each slab costs fresh inputs; no snowball.
5. **Gated?** Yes — research + powered building + material cost + skill.
6. **Reversible cost?** Selling is permanent disposal; thawing returns the pawn minus a debuff — both are deliberate trade-offs.
7. **Danger is compositional?** Yes — wealth-scaling raids + extraction raids + malfunction make it a *decision under risk*, not a button. ✅ PASSES.

---

## Implementation notes (feasibility — mostly XML + a little C#)

- **Storing a pawn in a Thing** mirrors vanilla `Building_Casket` / cryptosleep-casket + corpse-container patterns — well-trodden C#. A small `ThingComp`/`Building` subclass holds the occupant `Pawn` and suspends needs/aging.
- **Freeze & thaw** are `RecipeDef`s with custom `JobDriver`s at the station (donor pattern exists: Droid Depot ships `JobDriver_RestrainDroid` + `Recipe_RemoveBolt` — same shape, portable as a template).
- **Beauty/impressiveness by occupant value** = statOffsets computed in the comp; standard.
- **Visuals**: a carbonite-slab texture with the frozen-pawn silhouette overlay (Core already has a `CarboniteFreezing` overlay material to reference for the shader look).
- **Scope**: this is a **small-to-medium C# mod** (one building, one comp, two recipes/jobdrivers, a handful of ThingDefs/RecipeDefs/ResearchProjectDef). Not a giant undertaking. Bulk of the defs are XML; the pawn-container + suspend-needs logic is the only real C#.
- **Deps**: none hard-required; can lean on VEF if convenient but designable standalone. Author under our own packageId for 1.6.

## Open decisions (pick at authoring)
- Exact freezing reagent (plain chemfuel vs a refined "carbonite compound" you must produce — the latter adds a supply-chain step, more anti-exponential).
- Slab as **building-only** vs **minifiable item** (recommend minifiable so it's haulable/sellable/shippable — more useful).
- Whether frozen slabs require **standing power** to stay frozen (adds the brownout-thaw crisis) or are **passive-permanent** (simpler). Recommend a mod setting.
- Whether to add an **"extraction raid"** incident when you hold a named enemy's frozen officer (great story hook; medium C#).

---

# BUILDABLE SPEC — implementation architecture

Grounded in real RimWorld 1.6 classes (verified against vanilla + the Droid Depot 1.6 source we already have as a template). This is the from-XML-and-a-little-C# build plan. Def prefix: **`SWC_`** (Star Wars Carbonite) to avoid any `OuterRim_*` collision. **For final concrete numbers (costs, inputs, power, slab behavior) the CANONICAL SPEC below governs; this section owns the class/def/JobDriver architecture.**

## Design pivot after reading vanilla hooks: the slab IS a container Thing
The cleanest real implementation is a **minifiable Building that contains a Pawn**, exactly like vanilla `Building_CryptosleepCasket` (which already stores a live pawn, suspends needs, and survives save/load via `ThingOwner`). We subclass that pattern so the engine does the hard part (pawn suspension, serialization) for free.

## Defs to author

### 1. `SWC_CarboniteChamber` — ThingDef (Building, the freezing station)
- `thingClass` = `SWC.Building_CarboniteChamber` (subclass of `Building_Casket`/`Building_WorkTable` hybrid — see C# below).
- Powered (`CompPowerTrader`, high `basePowerConsumption` ~600–1000W during a freeze cycle), needs research `SWC_CarboniteFreezing`.
- Has a **bill stack** (like a worktable): the "Freeze prisoner into carbonite" recipe and the "Thaw carbonite slab" recipe are bills here.
- `designationCategory` = Misc/Production; `costList` steel+components+advanced components to build.

### 2. `SWC_CarboniteSlab` — ThingDef (minifiable Building OR item) that CONTAINS the pawn
- `thingClass` = `SWC.Building_CarboniteSlab : Building_Casket` — inherits `ThingOwner` pawn storage, needs-suspend, save/load.
- `comps`: `CompQuality` (freeze skill sets quality → beauty), a custom `CompProperties_CarboniteSlab` (holds occupant metadata for label/value/trade), optional `CompPowerTrader` (only if "standing power to stay frozen" setting is on).
- `statBases`: `Beauty` + `MarketValue` computed dynamically in the comp (see value logic); `Mass` heavy (it's a slab); `Flammable` false.
- `minifiedDef` so it's haulable/storable/shippable/**sellable**; `tradeability` Sellable.
- `tickerType` Rare (cheap; only matters if power-decay setting is on).
- Wall-mountable variant flag for the trophy/decor use (or just let it be placed like a statue — beauty applies either way).

### 3. `SWC_FreezeInCarbonite` — RecipeDef (bill at the chamber)
- Targets a **downed pawn or prisoner** brought to the chamber (WorkGiver hauls the pawn in, like `JobDriver_RestrainDroid` hauls its target — that exact toil chain is our template: GotoPawn → carry → wait-with-progressbar → apply).
- `ingredients`: Steel 50 + Plasteel 20 (casing) + Components 2 (advanced 1 for high-value/Force targets) + a **coolant reagent** (Chemfuel 75, OR custom `SWC_CarboniteCompound` if we do the supply-chain option).
- `workAmount` high (long job, occupies a skilled colonist); `skillRequirements` Crafting/Intellectual.
- **Effect (custom `RecipeWorker` / job end):** despawn the pawn, spawn a `SWC_CarboniteSlab` whose `ThingOwner` now holds that pawn; stamp quality from worker skill; compute value.
- **Malfunction roll:** on low skill / power interruption, chance to injure/kill the occupant → lose captive + materials (anti-cheese).

### 4. `SWC_ThawFromCarbonite` — RecipeDef (reverse bill)
- Bill on a slab placed at/near the chamber: consumes work + a little power, releases the pawn **alive** from the slab's `ThingOwner`, destroys the slab, applies `SWC_HibernationSickness` hediff (temp).

### 5. `SWC_HibernationSickness` — HediffDef (pure XML)
- Temporary, self-healing over ~1 day: `WorkSpeedGlobal`/`MoveSpeed` penalty + short **blindness** stage (canon Han-Solo nod). Blocks thaw-for-instant-combat cheese. Pure XML, no class.

### 6. `SWC_CarboniteFreezing` — ResearchProjectDef (pure XML)
- Gates the chamber. Prereq ~ Microelectronics + a mid-tier tech; modest cost.

## The only real C# (small)
- **`Building_CarboniteSlab : Building_Casket`** — override label ("So-and-so, frozen in carbonite"), `GetInspectString` (shows occupant), and `MarketValue`/`Beauty` getters computed from occupant. Casket base already handles the `ThingOwner<Pawn>`, needs-suspension, and save/load. ~60–100 lines.
- **`CompCarboniteSlab`** (or fold into the building) — computes value = `f(materialsConsumed + occupant.MarketValue + qualityMultiplier)`; exposes occupant for trade/label; optional power-decay tick (thaw if unpowered).
- **Freeze recipe worker + WorkGiver/JobDriver** — reuse the Droid Depot `JobDriver_RestrainDroid` toil chain (Goto→Carry→Wait-with-progressbar→apply) as the literal template; on completion, do the pawn→slab swap. ~80–120 lines.
- **(Optional) `IncidentWorker_ExtractionRaid`** — if we hold a named enemy's frozen officer, their faction raids to reclaim the slab. ~100 lines, deferrable.
Total bespoke C#: roughly **200–320 lines** across 2–3 classes + one optional incident. Genuinely small.

## Value logic (anti-exponential, restated concretely)
`slabMarketValue = (steelCost + plasteelCost + componentValue + coolantValue) + occupant.MarketValue * gradeMult`
where `gradeMult` ≈ 1.0 common / 1.5 named / 2.0+ Force-user. Selling nets roughly inputs+captive value (a **conversion**, not minted wealth); the profit margin is deliberately thin so it's a disposal-with-dignity sink, not a money printer. Higher grades pay more but cost advanced components + are rare → special-occasion, not a grind. ✅ 7-question PASS retained.

## Dependencies & load
- **No hard mod dep required** — builds on vanilla `Building_Casket`/`CompQuality`/`RecipeDef`. Optionally reference VEF for convenience, but standalone is cleaner.
- Author under our own `packageId` (e.g. `mandrake.sw.carbonite`), `supportedVersions` 1.6, load after Core/Galactic Diversity (so it can freeze modded xenotypes incl. Jawa — the Casket pattern is race-agnostic, so unlike RHS this DOES work on Jawa).
- Textures: one slab graphic (grey carbonite with pawn-silhouette overlay — reference Core's `CarboniteFreezing` overlay look) + a chamber building graphic.

## Build order (Task B → implementation)
1. Research + chamber ThingDef + slab ThingDef (XML) with a stub `Building_CarboniteSlab`.
2. Freeze recipe + JobDriver (port the RestrainDroid toil chain) → prove pawn→slab swap works in dev mode.
3. Thaw recipe + `SWC_HibernationSickness`.
4. Value/beauty comp + quality-from-skill + trade wiring.
5. Danger hooks: malfunction roll → then (optional) power-decay setting → then (optional) extraction-raid incident.
6. §-balance pass + Hutt-market tie-in verify.

---

# CANONICAL SPEC — concrete design (user directives)

This section owns all concrete numbers; the implementation-architecture section above owns the class/def structure.

## Station: **Class 3 Carbon Freezing Chamber** (`SWC_CarboniteChamber`)
- Diegetic name is now fixed: **"Class 3 Carbon Freezing Chamber."**
- **Integrated control panel** (part of the same building, not a separate def) maintains stasis and runs the **unfreeze/restore** operation — thaw is driven from the chamber's controls, restoring contents to their previous state.
- **Build cost = ~2× a cryptosleep casket (DECIDED).** Vanilla cryptosleep casket ≈ Steel 100 + Component 4 (🔎 re-confirm exact 1.6 values at authoring), so target ≈ **Steel 200 + Components 8** (plus a little plasteel/adv-component flavor if desired). Anchor the `costList` to whatever the casket actually costs in-game rather than the numbers here, so "twice a casket" stays true if vanilla shifts.
- **Power (DECIDED): duty-cycled, not constant.**
  - **While actively freezing/thawing:** heavy draw ≈ a working **electric smelter** (vanilla ≈ **400 W**, 🔎 confirm 1.6). This is the brownout-risk logistics cost.
  - **Otherwise (idle/maintaining):** **inert — only a tiny trickle draw** (a few W, e.g. ~10–50 W for the control panel), not the full cycle load.
  - Implement as a `CompPowerTrader` whose `PowerOutput` is switched between the low idle value and the smelter-equivalent value by the active bill (vanilla smelters/nutrient-paste do exactly this — `PowerConsumption` swapped on/off with work state).
- Once a slab is frozen, **the slab itself needs no power thereafter** (passive-permanent is the DECIDED default — no standing-power-to-stay-frozen requirement). The duty-cycle above is the *chamber's* draw, distinct from the slab.

## Freeze recipe inputs (`SWC_FreezeInCarbonite`) — DECIDED
Per unit: **a lot of Chemfuel** (the carbon-bearing bulk medium — tune high, e.g. ~75–150) **+ 2 Components + 2 Steel + 1 Plasteel + 1 Uranium + the target (a Pawn or a material stack).** Chemfuel is the bulk carbon feedstock; Uranium ×1 is the stasis-core element. Advanced-component upgrade for high-value/Force targets is an optional grade input.

## Two freeze targets (NEW — the slab is now general-purpose)
1. **Pawn freeze** (the trophy/vault use): downed pawn or prisoner → `SWC_CarboniteSlab` containing that pawn. Also an effective **emergency stasis for a dying/injured pawn** — like a sleep casket but requiring **no power once frozen** (freeze to halt bleed-out/infection, thaw when you can treat them).
2. **Stack freeze** (NEW): freeze **a full stack of ANY material** into a single slab object. Frozen contents **do not decay** with time or weather, and **volatile items stay frozen in time** — e.g. explosives/chemfuel/rotting food are suspended, not merely stored. A preservation + hazard-safing vault, not just a captive sink.

## The Carbonite Slab (`SWC_CarboniteSlab`) — properties DECIDED
- **Appearance:** a **black monolith** ("Carbonite Slab").
- **Value:** ≈ **occupant/contents value + one hypersleep (cryptosleep) casket's worth** (the stasis apparatus premium). Restates the anti-exponential conversion: contents value passes through, plus a fixed apparatus value, not minted wealth.
- **Contents shown:** the slab's **label + description/inspect string display what's frozen inside** (which pawn, or what item×count).
- **Near-indestructible:** very high HitPoints. **Does NOT release its contents when destroyed** — a broken slab yields only **burning debris** (contents are lost/incinerated, so smashing is not a free extraction route; use the control panel to thaw).
- **Debuff on thawed pawns (`SWC_HibernationSickness`):** reduces functionality for **~half a day**, **blinds** them, and causes **disorientation** for the duration. Self-healing. Blocks thaw-for-instant-combat cheese; canon Han-Solo nod.

## Placement / storage (NEW — furniture behavior)
- **On display = Furniture.** Placed like a **Wardrobe/dresser**: **rotatable** and set flush **against a wall** (edifice-style footprint, wall-adjacent orientation). Beauty + impressiveness apply here (throne-room / Hutt-court trophy).
- **Minifiable** (retained), and when minified can be **stacked 5 high** in a dedicated **Carbonite storage rack** (`SWC_CarboniteRack`) — a new storage building that holds up to 5 minified slabs in one cell (vertical display/warehouse).

## New/changed defs implied by v3
- `SWC_CarboniteRack` — storage Building holding 5 minified slabs (Building_Storage variant with a 5-cap + vertical stacking graphic).
- Slab gains a **wall-adjacent, rotatable furniture** placement worker (like `PlaceWorker` for wall furniture) + Furniture `designationCategory`.
- Stack-freeze path: recipe/JobDriver accepts an **item stack** as the target (in addition to a pawn); slab comp stores either a `Pawn` (via `ThingOwner`) **or** an item stack (count+def) and reports it in the label.
- Slab HitPoints set very high; on `Destroy`, spawn burning debris and **do not** eject `ThingOwner` contents.

## Reconciled open decisions (now closed)
- Standing power to stay frozen → **NO** (passive-permanent). Brownout-thaw crisis dropped for the base slab.
- Slab as building-only vs minifiable → **both** (placeable furniture AND minifiable for the rack/trade).
- Reagent → **Chemfuel** (bulk) + Uranium (core); custom "carbonite compound" supply-chain shelved as optional.
- Extraction-raid incident → still optional/deferrable.
