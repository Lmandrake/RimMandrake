# ship_deck_plan.md — The Ruined Vessel: deck plan + repair-progression design

_Deep-think design pass, 2026-08-06. Turns the **hulk-ship reframe** (required_mods.md parked Thread 1)
into a concrete deck architecture. Rests on three verified inputs: the **substructure cap**
(500 + 6×250 = 2,000 connected tiles, Fetcher 2026-08-06), the **8-cell modular campus** and per-machine
footprints from `Factory_lore.md`, and the **anti-exponential pillar** (concept.md / forbidden_mods.md).
This doc owns the WING MAP + repair gate. `Factory_lore.md` still owns intra-cell layout craft;
`required_mods.md` owns the adoption/restriction decisions._

> **Status:** design proposal, not locked. Decisions flagged **[DECIDE]** need your call. Everything
> else is a *recommended default* derived from the constraints, with alternatives noted.

---

## 0. The core insight (why this premise is strong)

`Factory_lore.md`'s central finding is that the best "uses-everything" factory is **not one tangled
belt hall** — it's an **8-cell modular campus**: independent cells, each with its own inputs, outputs,
bill targets, power switch, and heat plan, joined by filtered warehouse trunks and a separate utility
spine. That architecture was derived purely from *operational* concerns (routing, heat, spoilage).

It happens to be the ideal skeleton for a **derelict you repair wing by wing**:

- A cell = a **wing** = an independently repairable, independently isolatable unit. A derelict fails
  wing-by-wing; you restore it wing-by-wing. The mod's "one local switch per cell / disable cells
  during emergencies" *is* the fiction of powering up a dead section of a wreck.
- The **utility spine** (power, boosters, heatsinks, firebreaks, maintenance corridor) = the ship's
  **central keel** — the one thing that must be alive before any wing can run.
- The **~2,000-tile cap** means the ship is a **fixed-size sandbox**. You cannot grow the hull; you can
  only make more of a *fixed* hull functional. This is the anti-exponential pillar expressed as
  architecture, not as a rule you have to remember.

**Verified budget headroom (computed 2026-08-06):** the 18 machines are 261 tiles of raw footprint;
at a realistic ~2.5× factor (factory floor + hoppers + belts + access) the full campus is **~650 tiles**.
A full ship — factory ~650 + living ~650 + systems ~250 + carbonite ~60, +15% circulation — lands at
**~1,850 tiles against the 2,000 cap: ~150 tiles of headroom.** The decisive consequence:

> **A fully-restored ship nearly saturates the substructure cap.** Restoration isn't open-ended — it
> literally *runs out of ship*. That is a gift: the endgame is naturally bounded, and every wing you
> light up costs tiles you can't get back. Choices to leave a wing derelict become permanent trade-offs,
> which is exactly the "decide what to leave behind" pillar.

**Two constraints, not one — the tile budget is necessary but NOT sufficient.** Substructure connects
only if it lies within a connection *radius*: the grav engine reaches **19 tiles**, each of up to 6
field extenders reaches **16 tiles**, and every extender must itself sit inside the already-connected
field (a chain rule). So a design can pass the 2,000-tile capacity check and still fail to fly because
distant tiles are out of radius. **Verified geometrically (2026-08-06, `player_maps/verify_coverage.py`
+ `geom_check.py`):** with the engine mounted mid-keel and all 6 extenders chained along the spine, the
1,732-tile layout is **100% covered (0 tiles out of radius)**, chain rule satisfied, and the farthest
tile is **15.81 tiles** from its nearest node — just inside the 16-tile extender limit. Consequences
baked back into the design:

- **The keel MUST carry the engine + all extenders**, and they must be spaced ≤ ~32 tiles apart along
  the spine (two radius-16 disks) so their fields overlap and chain. This is *why* the keel is repaired
  first — it's not just utility routing, it's the literal connection backbone.
- **No wing may extend more than ~15 tiles laterally from the keel centerline.** Beyond that, its outer
  tiles fall outside any spine-mounted extender's radius and would show red / won't lift. The current
  wings top out at 15 tiles — they are at the geometric limit, so widening a wing means *moving an
  extender off the keel into that wing*, which then can't reach the opposite side. Wings grow by adding
  *length* along the hull, never width past the radius.
- **The scale drawing** (`ship_deck_plan_scale_map.png`) renders this: engine (yellow G) + 6 extenders
  (blue) on the keel with their radius-19/16 coverage disks shown as the pale halo enclosing every tile.

---

## 1. The hull at t=0 (starting state)

A **large** hull — seed it near the upper tile band so the *shape* is impressive from turn one — but
mostly **dead**. Concretely:

- **Substructure:** present across the whole footprint but **~40–55% disconnected** — showing RED on the
  grav engine, i.e. gaping holes and severed wings that **won't lift**. The engine + keel + one small
  wing are connected (green); everything else is red until repaired. This is a *verified* mechanic:
  disconnected substructure displays red and isn't carried by the ship.
- **Hull walls:** large sections **missing** — open to the desert (temperature bleed, sightlines, raid
  ingress). Sealing the hull is early-game pressure #1.
- **Factory machines:** present as **broken scrap** in their wings. **[DECIDE A]** whether "broken" is
  (i) *decorative rubble/filth* you clear then build fresh on the cleared floor (simplest to author), or
  (ii) a real **damaged/deconstructable** building state that yields partial materials on repair (richer,
  needs a damaged-variant def or a "wreck" ThingDef per machine). Recommend **(i) for v1** (author as
  rubble + a few salvageable component stacks), keep (ii) as a stretch if we build the custom mod anyway.
- **Grav engine:** intact but the ship is **grounded** — not enough connected substructure to lift.
  First strategic goal = reconnect enough deck to fly. Natural, diegetic tutorial.

**Why grounded-first is good:** it forces the crew to treat the crash site as a temporary base, live
under the desert/thirst pressure (desert_world_design.md) with holes in the hull, and *earn* mobility.
It also sidesteps the authoring problem of a flying-but-broken ship — a grounded wreck is just a map.

---

## 2. The wing map (campus cells → ship wings)

Six production wings (Factory_lore cells A–F) + keel + habitat. Proposed spatial topology, keel-centric:

```text
        ┌───────────────────────────────────────────────────────────┐
        │  BOW: COMMAND CORE  (pilot console, grav engine, scanner)   │
        └───────────────────────────────────────────────────────────┘
   WING F (precision)          ║ K ║          WING E (advanced materials)
   medicine granulator         ║ E ║          assembler / alloy forge / neutro
   machining bay               ║ E ║          ⚠ HOTTEST WING (5×5 forge)
        ▲                       ║ L ║               ▲
   WING D (textile/ammo)       ║   ║          WING B (bulk / dirty / hot)
   autoloom / ammo press       ║ = ║          smelter / masonry / mincer /
        ▲                    power, boosters,   cremator / biofuel refinery
   WING C (food)             heatsinks, fire-        ▲
   oven / cannery /          break, maint.      WING A (raw extraction)
   distillery                corridor           autofarmer / drill / fishfarm
        ▲                       ║ ║                   ▲
        └────────── HABITAT RING (quarters, dining, ──┘
                    hospital, freezer, prison, rec)
        ┌───────────────────────────────────────────────────────────┐
        │  STERN: THRUSTERS + CHEMFUEL TANKS + main power generation  │
        └───────────────────────────────────────────────────────────┘
```

Design rules baked into the placement (all from Factory_lore §1.4 zoning + thermal §5):

- **Hot wings (B, E) outboard.** Smelter, alloy forge (hottest machine), crematorium, drill sit against
  the **hull edge** so their heat can dump to the exterior — and, early on, through the *unsealed holes*.
  (See §3, heat doctrine.) Keep them **away from food (C) and habitat**.
- **Food wing (C) adjacent to habitat + freezer**, far from crematorium/corpse lines (B). Belt runs from
  raw buffers to oven/cannery stay short and roofed (spoilage).
- **Precision wings (E, F) flank the keel** so they draw from the metal/chemical buffers on the spine
  with minimal belt length; Assembler↔Alloy Forge↔Machining Bay all want the same plasteel/component
  buffer (E and F share a wall, not their input hoppers — they *compete* for components per Factory_lore).
- **Keel is the utility spine**: power conduits, switches, the 3-booster / 4-heatsink banks (9.9-tile
  link radius reaches into flanking wings), firebreak, maintenance corridor. **This is repaired first.**
- **Raw extraction (A)** at the "ground" end (stern-adjacent) — drill/autofarmer/fishfarm want exterior
  access (fields, water, deep resources) and their output feeds *up* the ship into B and C.

**[DECIDE B]** overall silhouette. Options: **(1)** long spinal "keel + ribs" freighter (drawn above —
best for the wing/heat logic); **(2)** compact saucer (denser, but hot wings can't all be outboard);
**(3)** asymmetric wreck (some wings simply *gone*, never rebuilt — leans hardest into "decide what to
leave behind"). Recommend **(1)**; it makes heat, belt-length, and "sever a wing" all legible.

---

## 3. Heat doctrine — the sharpest tension, and its elegant resolution

The single hardest problem with a factory *on a sealed ship*: VFE-Factory generates **exponential heat**
at overclock, heatsinks only **−25%** (max 4, and "do not assume four heatsinks make 500% thermally
trivial" — Factory_lore §5), and a sealed hull **has no outdoors to vent to**. On flat ground you just
open a wall to the biome.

The hulk premise resolves this on a **timeline** rather than fighting it:

- **Early game (holes open):** the missing walls are a **feature** — the hot wings (B, E) vent straight
  to the desert through their own gaps. Heat is free to dump; the *cost* is everything else a hole
  brings (cold nights, heat of day, raiders, no atmosphere control). So early industry is *possible but
  exposed*.
- **Mid game (sealing the hull):** as you patch walls to gain temperature control, defense, and flight,
  you **lose your free heat dump**. Sealing a hot wing forces you to *simultaneously* solve its cooling —
  vents to a dedicated radiator bay, exterior heatsink louvres, or simply **capping overclock**. This is
  a genuine, emergent engineering decision the player earns, not a scripted gate.
- **Late game (sealed + flying):** heat is a permanent managed budget. **[DECIDE C]** the cooling
  end-state: (i) a dedicated **radiator/vac-barrier bay** (Odyssey has oxygen pumps / vac barriers —
  a wing deliberately kept vacuum-exposed as a heatsink), (ii) accept a **hard overclock cap** (e.g.
  never above 200% except the drill in burst), or (iii) both. Recommend **(iii)**: radiator bay + a
  standing "200% routine, 500% supervised burst only" policy (matches Factory_lore §5 operating policy).

> This is the payoff of the whole premise: **"seal the ship" and "run the factory" are in direct
> tension**, and resolving it *is* the mid-game. A conventional colony never feels this.

---

## 4. Repair as the progression gate (the anti-exponential spine)

Restoration order — each step is a **physical repair** (re-plate floor, seal walls, rebuild the wing's
machines) gated by salvage feedstock / components / quests, *layered on top of* the research tiers
(VFE_BasicFactories → VFE_ComplexFactories) rather than replacing them.

| Phase | Repair unlocked | What lights up | Gate (diegetic) | Pillar effect |
|---|---|---|---|---|
| **0. Crash** | Keel + 1 small wing (green substructure), grav engine | Power, 1 starting BASIC line (**[DECIDE D]**: oven *or* smelter, per required_mods "one line" rule) | — (start state) | Dependence without economy |
| **1. Survive** | Seal habitat ring; connect enough deck to consider flight | Living quarters, freezer, defense against hole-ingress | Steel + gravlite panels (substructure = 1 gravlite + 4 steel/tile) | First scarcity wall |
| **2. Salvage loop** | Wing B (smelter first) | Salvage → metal; the engine of everything | VFE_BasicFactories research + rebuild scrap | Bounded: feedstock = what you scavenge |
| **3. Provision** | Wing A + rest of C | Food security (farm/fish → oven/cannery) | Refrigerated routing built; Odyssey fishfarm | Food stays pressured (desert) |
| **4. Fly** | Reconnect ≥ target substructure; stern thrusters | Ship lifts — mobility unlocked | Enough green deck + fuel (VGE astrofuel) | Mobility earned, not given |
| **5. Fabricate** | Wing E | Components, plasteel, gravlite (⚠ gate the forge gravlite recipe too) | VFE_ComplexFactories + Fabrication + quest/techprint | The one sanctioned scaling tree opens — *late* |
| **6. Specialize** | Wings D + F | Medicine, ammo, textiles, gear | Strict target bills; component competition with E | Cap approached — trade-offs bite |
| **7. Saturate** | Last derelict wings / carbonite bay | Optional luxury/trophy capacity | Tiles run out (~150 headroom) | **Hard ceiling reached** |

Two anti-exponential guarantees fall out of this for free:

1. **Feedstock-bound, not footprint-bound.** You can rebuild a wing, but you can't feed it without
   salvage/exploration. The factory converts *exploration + salvage → ship*, never *ship → more ship*.
2. **The tile cap is the final ceiling.** Phase 7 literally runs out of substructure. There is no
   phase 8. **[DECIDE E]**: do we *want* the player to be able to reach full saturation, or should the
   design ensure 1–2 wings are permanently uneconomical to restore (so the ship is *always* a wreck in
   part)? Recommend the latter for theme — a Jawa hulk should never be pristine.

---

## 5. Integration with the rest of the campaign

- **Desert / thirst (desert_world_design.md):** the grounded-wreck early game happens *in* the desert
  scarcity layer — holes in the hull mean the water/thirst doctrine hits hardest before you seal up.
  Food wing C's cannery is the "make scarce windfalls last across dry crossings" tool.
- **Jawa lore (jawa_xenotype_and_religion.md Part 4):** repairing an inherited hulk *is* the Jawa
  fantasy (scavenger-mechanics, not engineers). Gourmet-reverence → the cannery/oven wing is the
  "aspirational cuisine against scarcity" layer. Droid-mourning / acquisition lore colors who crews
  which wing.
- **Carbonite (carbonite_trophy_mod.md):** the carbonite bay is a Phase-7 luxury wing — trophy/vault
  capacity that costs precious end-cap tiles, a deliberate "spend hull on horror-decor vs. more
  production" choice.
- **VGE fuel leash:** Phase-4 flight depends on astrofuel (chemfuel → astrofuel, lossy) — Wing B's
  biofuel refinery + the stern chemfuel tanks are the flight economy.
- **Factions (faction_roster_v2.md):** open holes = early raid ingress; the Empire-as-pursuer pressure
  gives a reason the crew *can't* just sit and slowly repair forever.

---

## 6. Open decisions (collected)

- **[DECIDE A]** broken machines = decorative rubble (v1, simple) vs. real damaged/deconstructable state.
- **[DECIDE B]** silhouette: spinal freighter (rec.) / saucer / asymmetric-wreck.
- **[DECIDE C]** late-game cooling: radiator-bay / overclock-cap / both (rec. both).
- **[DECIDE D]** the single starting BASIC line: oven (survival dependence) vs. smelter (salvage
  dependence). Ties to required_mods "recommended starting state."
- **[DECIDE E]** allow full saturation, or guarantee 1–2 wings stay permanently derelict (rec.).
- **Authoring unknown (still the load-bearer):** how to place a large pre-broken ship as the start
  save — scenario building-lists can't do a whole ruined ship; likely hand-edited scenario/save.
  Routes to `save_authoring_pipeline.md` + `first_live_access.md`. This is the one true blocker between
  design and execution.

---

## 7. Bottom line (decision translation)

**The decision this doc serves:** whether to adopt the hulk-ship premise as the campaign's spine and
commit to a spinal-freighter, 8-wing, repair-gated deck. **Recommendation: yes** — it strengthens the
anti-exponential pillar (fixed hull, feedstock-bound growth, hard tile ceiling), turns the factory's
worst problem (heat on a sealed ship) into the mid-game's best tension, and fits Jawa lore natively.

**Viable alternatives:** a small-ship-that-grows (rejected — reintroduces footprint scaling the pillar
forbids); a single-hall factory (rejected — Factory_lore shows it fails operationally and gives no
wing/repair structure).

**Principal risk:** authoring a large pre-broken ship as a start state (the one real blocker) — mitigated
by the grounded-wreck-is-just-a-map insight and the save-authoring pipeline.

**Dependencies:** verified substructure math; Factory_lore layout craft; desert/VGE/faction layers.

**Missing info that would help:** in-game confirmation of (a) how disconnected substructure + holes
actually render/behave at scale, (b) real heat numbers per machine at 200%/500% to size the radiator bay,
(c) whether a damaged-machine state is feasible without a custom mod. All are **[DECIDE]**/verify-at-machine.

**Recommended next step:** you resolve [DECIDE A–E] (or just B + D, the load-bearing two), then I draft
the actual tile-level wing blueprints (like the coastal_mesa maps) against the 2,000-tile budget.
