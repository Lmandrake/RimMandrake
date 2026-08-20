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
distant tiles are out of radius. **Verified geometrically (2026-08-06, by `verify_coverage.py` + `geom_check.py`, both
retired 2026-08-20 — the live coverage verifier is `src/RimMandrake/mapsynth/ship_designs.py`):** with the engine mounted mid-keel and all 6 extenders chained along the spine, the
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
- **Factory machines:** present as **broken scrap** in their wings. **[DECIDE A — RESOLVED by user 2026-08-06: the "SACRED SCRAP" rule.]** Destroyed/derelict factory machines are **sacred scrap that cannot be touched, cleared, deconstructed, or reprocessed until they are *repaired*.** You may not salvage a broken machine for materials, nor bulldoze its rubble to build fresh on the cleared floor — the wreck is inviolate until the crew *restores* it in place. This **forecloses option (i)** (clear-and-rebuild) for the machines themselves and mandates a variant of **(ii): a real damaged/immovable building state that can only be *repaired* into function**, never demolished or harvested. [inference] cleanest implementation = a "wreck" ThingDef per machine (or a damaged state) that (a) has **no deconstruct designation** and **no clear/haul-away**, (b) is repaired-in-place by a construction/repair job consuming feedstock, and (c) yields *nothing* if merely destroyed further. This is stronger than the earlier "recommend (i)" note and **overrides it.** Design pay-off: it hard-couples "restore the ship" to "restore *these specific* machines" — you can't strip the wreck for a quick material windfall, which both reinforces the anti-exponential feedstock discipline (no free salvage bolus from your own hull) and gives the Jawa reverence a mechanical teeth. See the ideoligion precept in `jawa_xenotype_and_religion.md` Part 4 and the "sacred relic" framing in `context.md` §D.
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

**[DECIDE B] — RESOLVED 2026-08-06 → #15 "Falcon Halo (hollow)".** The silhouette is now locked to the
hull chosen from the topology menu in `ship_designs.md` (which owns the full comparison and the verified
numbers). It is a clean working cargo **wheel** — a thin rim band holding one big cargo hold plus the
core systems set into the band (thrusters aft, fuel port, water starboard), with **seven circular
function-pods sunk half-into the outer rim** (the six factory wings + habitat, each an isolatable repair
unit), a **hollow shrine-heart** at dead centre (grav-engine core + scrap-totem shrine reached by a
single rear causeway), and a **Millennium-Falcon mandible arm** forking forward off the rim with the
two **shuttle pads capping the prong tips** and an offset starboard **command cockpit**. Verified
liftable: 4,057 / 4,800 tiles (743 headroom), 7 extenders, all 14 regions, single contiguous piece;
largest cargo of the whole set (1,443).

The wing/heat logic below was drafted for the earlier spinal-freighter sketch; it still governs, but
map it onto the wheel: the rim-embedded pods are the "wings" (hot wings B/E sit on the outboard rim
where their gaps vent straight to the biome; food C near habitat R; precision E/F share the rim band
that carries the metal/chemical buffers), and the **rim band is the utility spine** repaired first. The
next deliverable is the tile-level interior blueprint drawn on #15.

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
- **Late game (sealed + flying):** heat is a permanent managed budget. **[DECIDE C — RESOLVED by
  user 2026-08-08: BOTH (iii)].** Cooling end-state = a dedicated **radiator/vac-barrier bay** (a wing
  deliberately kept vacuum-exposed as a heatsink via Odyssey oxygen pumps / vac barriers) **AND** a
  **hard overclock cap** — standing "200% routine, 500% supervised burst only" policy (matches
  Factory_lore §5 operating policy). Neither alone; the bay handles the standing load, the cap keeps
  bursts from overwhelming it.

> This is the payoff of the whole premise: **"seal the ship" and "run the factory" are in direct
> tension**, and resolving it *is* the mid-game. A conventional colony never feels this.

---

## 4. Repair as the progression gate (the anti-exponential spine)

Restoration order — each step is a **physical repair** (re-plate floor, seal walls, rebuild the wing's
machines) gated by salvage feedstock / components / quests, *layered on top of* the research tiers
(VFE_BasicFactories → VFE_ComplexFactories) rather than replacing them.

> **⚠️ PROGRESSION SOURCE = QUESTS + TRADE, not research (user ruling 2026-08-06; full detail in `required_mods.md` PARKED thread 1).** The Jawa start at a low salvage-tech baseline; the jump to ship/factory capability is closed *primarily by acquiring capability from the world* — quest-earned techprints/data cores, traded blueprints/components, salvaged working parts — **not by grinding the bench.** So read every "research" gate in the table below as **quest/trade-unlocked**: keep the VFE tiers as gates, but gate their *start* behind an earned techprint/data core (Configurable Techprints or the custom XML mod). Recommend a thin research path (repair/smelting only) + quest/trade for everything advanced.
>
> **⚠️ THE JAWA ARE INDUSTRIAL-TIER, NOT TRIBAL (user ruling 2026-08-07).** They already *repair and run inherited industrial machines* to survive — that is the whole fantasy of this repair spine. Use the **`OuterRim_Jawa` (Industrial) pawnkind, NOT `OuterRim_JawaTribal`.** The "low baseline" means *salvage-tier industrial scavengers who don't originate advanced tech*, NOT stone-age tribals. Pawn tech level chiefly affects generated gear/apparel; keep it Industrial so the fiction (Jawa keep the machines running) and the mechanics agree.
>
> **⚙️ THE THREE-GATE PROGRESSION CHAIN for BIG capability jumps (user, 2026-08-07).** Advanced research (factory tiers, gravtech, droid manufacture, advanced weapons) is deliberately *hard*, gated in three sequential steps: **(1) obtain a TECHPRINT** for the tech (buy from the owning faction / loot it off that faction in battle / earn it as a quest reward — see the three acquisition routes below); **(2) build a PROTOTYPE** of the thing at the appropriate bench (Research Reinvented's `PrototypeConstruction`/`PrototypeProduction` opportunity, 1.6-native — VERIFIED in `mod_sources/ResearchReinvented-main/…/ResearchOpportunityTypes_Prototype.xml`); **(3) complete the RESEARCH** at the bench, which now merely *applies* the earned knowledge. **Tuning guardrail (recommendation, not yet locked):** apply the full three-gate ceremony ONLY to big capability jumps; let mundane survival tech use one gate or none, so the early game isn't paperwork. **Three techprint-acquisition routes, each mapped to a win-path:** (a) **BUY** from the owning faction — factory prints from Hutts/traders, weapons from Bounty Hunters, droid/brain prints from Free Droid Enclaves or Ascendant Helix (Configurable Techprints assigns faction stock) → the *transactional/Hutt* path; (b) **LOOT** as a treasure-drop from defeating that faction's forces/outposts → the *tyrannical/droid-army* path (raid the droids for their brains AND their build-prints); (c) **QUEST-REWARD** authored CQF data cores that guarantee the *critical-path* prints so pacing never dies on RNG → the *solidary/coalition* path (the earned droid-build right IS the Enclaves gifting you droid prints). Buy + loot supply optional accelerants/breadth; quests guarantee the spine. **Dependency:** ✅ **1.6 VERIFIED (Fetcher `2026-08-07_techprint_progression_mods`, 2026-08-07):** Configurable Techprints Workshop page (WS 2876747024) declares "Mod, 1.3, 1.4, 1.5, **1.6**" (updated 2025-07-19; the local GitHub About.xml was merely stale) and explicitly supports "prevent it from generating in trader's stock **to make it quest-only**" — the exact lever this scheme needs (requires Royalty, already in-stack). Research Reinvented (WS 2868392160) also Workshop-confirmed 1.6. CT + Research Reinvented + custom gravtech-gating all touch research → compat check still required before locking (`required_mods.md` line 570). ⚠️ **Balance caveat (from RR's own page):** a player can build the prototype then *stop* research early to bank the item and save ~50% research time — so the prototype step is NOT a hard gate on its own; **the TECHPRINT must remain the true lock.** 💡 **Alternate/companion found:** **Techprint Expansion (WS 2910923103)** ships pre-built compat locking VFE-Mechanoids "Factory Basics" + Spacer tech behind techprints out-of-the-box — may do some Gate-2/3 locking without manual config; needs its own 1.6 check.

### 4-bis. THE TECH-GATE LADDER — four weight-bands + faction-ownership map (user ACCEPTED, 2026-08-07)

Tech is grouped into **four gate-weight bands** (difficulty rises with narrative weight; the full three-gate ceremony is reserved for ~4–5 marquee unlocks, not sprinkled everywhere):

- **Gate 0 — Free (start knowledge).** Turn-1, no gate: hull/floor repair, rough smelting, basic power (batteries + the one starting line), simple cooking/preservation, patch-job furniture, salvaged sidearms/basic melee. The "keep ourselves alive + melt scrap" floor that preserves agency.
- **Gate 1 — Research-only (one gate).** Ordinary survival/comfort, bench-only, no techprint: cooling, hydroponics/desert farming, basic medicine + hospital, textiles, walls + simple turrets, water/moisture infra.
- **Gate 2 — Techprint + research (two gates).** Real industrial capability: **VFE Basic Factories**, component fabrication, mid-tier Outer Rim weapons/armor, advanced medicine, gravtech *repair* (flightworthy). Must acquire the print first; no prototype step.
- **Gate 3 — Full three-gate (techprint → prototype → research).** Campaign-defining capstones, deliberately hard + few: **VFE Complex Factories** (the sanctioned late scaling tree), **droid manufacture**, advanced gravtech / persona-core ship systems, top-tier weapons. These are the win-path capabilities — hardest by design.

**⛔ HARD CARVE-OUT (no gate exists):** droid-**brain fabrication** is owned by NO ONE and sold/researched by no path — brains stay externally-sourced only (win-path anti-exponential guardrail, [[three_win_paths]]). Faction-locking governs *where tech lives*; this is a tech that deliberately *does not exist for sale or research.*

**FACTION-OWNERSHIP MAP (user ACCEPTED, 2026-08-07) — "only the appropriate factions have certain technologies."** Two distinct mechanisms, BOTH required or the lock leaks:
1. **Who can GIVE the techprint** (buy/loot/quest source) — clean lever: Configurable Techprints assigns per-faction stock + can force quest-only.
2. **Who FIELDS/uses the tech in-world** (so enemies' gear + loot are consistent) — *separate mechanism*: lives in each faction's PawnKindDef `weaponTags`/`apparelTags` matched against ThingDef tags + faction tech level, NOT in Configurable Techprints. **✅ 1.6 MECHANISM VERIFIED (Fetcher `2026-08-07_faction_equipment_fielding_1p6`):** pawns spawn only with weapons/apparel whose tags their PawnKindDef allows, AND RimWorld **wealth-gates** (poor pawns won't field expensive gear even if tagged — a *free* tiering assist for us). Vanilla tag vocab confirmed (wiki `Property:WeaponTags`/`ApparelTags`: `SpacerMilitary`, `IndustrialMilitaryAdvanced`, `Neolithic`, `Royal`, …). Note: apparel is also forceable via ideology, but **weapons must go through `weaponTags`**. Config-driven tool so we don't hand-edit every PawnKindDef: **Faction Weapons and Apparel Set (WS 3635005747)** — per-faction weapon/apparel pools, works with mod factions. **✅ ADOPTED as the PRIMARY equipment-fielding tool — 1.6 VERIFIED (Fetcher `2026-08-07_techprint_faction_equip_verify`, Workshop page fetched): tagged "Mod, 1.6", updated 2026-01-28, HARMONY-ONLY dependency (no Royalty), 31.9k subs.** In-game mod-settings UI: add a faction (+), edit its equipment pool; once configured, that faction's pawn generation is fully handled by the mod. Has an **"Ignore Wealth" toggle** — so our wealth-gating tiering assist is default-ON but can be overridden if a faction should field above its wealth band. Also has a per-pawnkind "Unit Mode" for fine-grained overrides. ⚠️ Watch-items (comments, unconfirmed): occasional "naked pawns" / a right-click glitch in some builds → smoke-test after configuring. **Fallback = TotalControl** (feldoh, GitHub; 1.6 via the "Rimsential – Total Control: Continued" fork WS 3063465133) — more powerful (roles/hair/colors/caravan animals per-pawnkind-per-faction) but heavier; use only if we need that granularity or hit the bugs above. Outer Rim's own trooper loadouts are source-inspectable (GitHub O21-Outer-Rim, 1.6 branch, `PawnKinds_ArmyTroopers.xml`) if we need to see exactly what the Empire fields.

Domain → owning faction (canon-justified):
- **Geonosian Foundry Hive → factory/industrial + droid MANUFACTURE** (canon: built the Separatist droid army) — owns VFE Complex Factories + droid-build prints.
- **Free Droid Enclaves → droid tech from the inside** (chassis, repair, brain-*recovery*/liberation) — the Path-3 allied-liberation source; moral mirror of raiding the Foundry (Path 2).
- **Ascendant Helix → medicine, genetics, cloning** (canon cloners/geneticists).
- **Blackstar Company → weapons + armor** (blaster/armor prints; the Heat-spawned faction).
- **Empire → gravtech / ship systems + top-tier military** (owns orbit + shipyards) — the HARDEST prints, routed through the only permanent enemy → leaving is earned.
- **Hutts → the FENCE for everything** (not an origin; black-market reseller of any-domain prints at a markup) — the diegetic escape valve so nothing is *totally* unobtainable if you pay the transactional/Path-1 price.
- **Deepwater Compact → water/moisture infrastructure** (their identity). Homestead / Tusken / Wookiee stay tech-neutral (survival-tier) — not every faction is a vendor.

Payoff: the ownership map *is* the win-path structure — Empire owns the hardest tech + you fight them; Hutts fence anything for silver (Path 1); Foundry-vs-Enclaves splits raid (Path 2) vs ally (Path 3); Consortium + Bounty Hunters supply specialist breadth.

⚠️ **Two leakage risks to guard (tuning items, not blockers):** (i) generic "everything-buyer" traders (MultipleTraders in `setup_checklist`) could stock prints regardless of faction — check the lock against generic traders, not just faction bases; (ii) loot-drop rules must match the trade-lock or defeating any enemy leaks prints.

| Phase | Repair unlocked | What lights up | Gate (diegetic) | Pillar effect |
|---|---|---|---|---|
| **0. Crash** | Keel + 1 small wing (green substructure), grav engine | Power, 1 starting BASIC line (**[DECIDE D] RESOLVED → SMELTER**, per required_mods "one line" rule) | — (start state) | Dependence without economy |

> **💡 The grav-controller = a persona core = LifeDawn's awakening (design idea, context.md §D).** The inciting "leader restored the central Grav controller into the old GravEngine" beat can *be* the reactivation of a vanilla **persona core** (the dormant superhuman AI already required to leave the planet). Restoring it wakes the ship's personality; voice it with a **CQF DialogTree** on a talkable ship-core building (offline, authored). Keep it a single earned/quested core (pillar-clean); craftable-core mods (Nanogel Persona Core WS 3550797935 etc.) are a later pick pending 1.6 verify. Full reasoning + mod list in context.md §D.
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
- **[DECIDE B]** silhouette — ✅ **RESOLVED 2026-08-06 → #15 "Falcon Halo (hollow)"** (see §2 and
  `ship_designs.md`). No longer open.
- **[DECIDE C]** — ✅ **RESOLVED 2026-08-08 → BOTH** (radiator/vac-barrier bay + hard overclock cap;
  see §heat doctrine). No longer open.
- **[DECIDE D]** — ✅ **RESOLVED 2026-08-08 → SMELTER first** (salvage dependence, not the oven). The
  single starting BASIC line is the smelter: it makes the crew dependent on *feeding scrap in*, which
  is on-theme for scrappers and couples cleanly to the sacred-scrap repair economy. (Oven/survival-food
  dependence declined.) Propagate to required_mods "recommended starting state" + phase-0 table.
- **[DECIDE E]** — 🔵 **DEFERRED by user 2026-08-08: "decide how to handle derelict portions as we
  go."** Do NOT hard-commit full-saturation-vs-permanent-derelict now; treat as a play-time call.
  Design leaning (non-binding) still favors keeping 1–2 wings derelict for the anti-exp/aesthetic
  payoff, but it's explicitly a runtime decision, not a locked gate.
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

---

## ⏳ The "one true blocker" on a pre-broken ship may have dissolved

_Filed by a retired seat, 2026-08-13; recorded here by another retired seat so the v2 wreck is scoped
against what exists rather than what was true this morning. **Not a reopening —
the owner ruled "build it finished" and that stands.**_

**`Gravship Crashes` (ACTIVE, load 158) ships a `BrokenSubstructure` TerrainDef.**
A purpose-made damaged-substructure terrain, already in the stack. This section
called placing a pre-broken ship the one true blocker, on the reasoning that
broken substructure had to be faked by demolishing an intact ship.

**Three things landed the same day and they compose:** floors survive the export
round trip · a ship layout can be authored as XML directly · and a terrain that
already reads as broken now exists. ⇒ **A wreck becomes data, not a demolition
job.**

🔴 **One question decides whether it is a tool or a trap: does
`BrokenSubstructure` carry the `Substructure` tag?**

- **With the tag** — it connects, counts toward capacity, and is walkable.
  **Visually ruined, structurally sound.** That is the good case and it makes an
  authored wreck trivial.
- **Without it** — it is decorative floor that *breaks the gravship field*. A
  completely different tool, useful for scenery and useless for a flyable hull.

⚠️ **Unverified. Do not scope a wreck against it until a retired seat answers.** Related
terrains may form a small palette — Transparent Substructure and BTD Gravship
Blueprints ship substructure affordances too.

### Why this matters more than a wreck
**The campaign's opening image is a clan that found a hulk.** If a damaged hull is
*data* rather than a demolition job, then **the ship the player starts on can look
salvaged from the first frame** — patched plating, dead sections, floor that was
never repaired. That is the single cheapest piece of atmosphere available to this
project, and it is the one the player looks at every session.

### ⭐ OWNER'S RULING — the no-tag branch is not a dead end, it is decor

> *"If substructure doesn't carry the tag, then it's nice decor to put on top of
> the gravship for flavour, should be routed to a retired seat as an ingredient in the
> design."*

**So there is no losing branch. Both answers are useful:**

| | with the `Substructure` tag | without it |
|---|---|---|
| what it is | **structural** — connects, counts toward capacity, walkable | **decorative** — breaks the field, so it cannot sit under the flying hull |
| where it goes | anywhere in the hull; the ship can carry visible damage and still fly | **anywhere the field does not need to reach** |
| what it buys | a shipping hull that looks salvaged from frame one | ⭐ **the wreck the ship was cut out of** |

⭐ **The no-tag version has the better image, and it should be built either way.**

> **The starting map holds the rest of the hulk.** Broken substructure, dead
> sections, a hull the clan could not save — and the flyable ship is the part
> they *got working*. The first thing the player sees is the ninety percent that
> stayed on the ground.

**That is the campaign's premise in a single frame**, it costs one terrain and
some placement, and it is immune to the tag question entirely — the broken floor
never has to fly, because narratively it never will again.

**Routed to a retired seat as a design ingredient**, per the owner. Not a blocker on
anything; an asset to build with.

#### 🔴 RULED — the hulk is the clan's quarry, and stripping it is the opening arc

**A retired seat asked whether the rest-of-the-hulk is fixed scenery or salvageable.
It is salvageable, and it is not close.**

**A wreck the clan cannot pick over is a painting of the thing the game is
about.** The Jawa premise is *strip what nobody else can reach*; putting an
enormous unstrippable hulk in the opening frame would show the player the fantasy
and then deny it. That is worse than not having the wreck at all.

**What it should be:**

- ✅ **Walkable, and lived in.** The clan's first base is inside it. That is where
  a salvage clan would obviously live.
- ✅ **Buildable on.** Rooms get patched into the dead sections.
- ✅ **Strippable for materials** — steel first, components and plasteel rare.
- ⛔ **Never regrows.** Once a section is gone it is gone.

⭐ **Big but SLOW.** High total yield, high work cost, poor rate. **The clan should
be chewing through its own dead ship for years**, not clearing it in a season. A
windfall here kills the scarcity pillar in year one; a slow seam funds the early
game honestly.

⭐ **And it gives the starting map an ENDING with no scripting at all.** When the
hulk is stripped there is nothing holding the clan to that tile. **The map itself
tells the player when to leave** — which is exactly the "reason to move on" the
campaign has been trying to author.

**The arc, in three words: live in it → strip it → leave.**

#### ⚠️ Pipeline note — this is MAP GENERATION, not ship authoring

**A retired seat's structural point, recorded so it cannot be mis-scoped:** the hulk sits
on the **starting map**, so it is authored like row 4's terrain overrides — a
`GenStep` or map-gen patch, or placed live over the bridge. **It does not ride
the gravship export XML**, which only carries what stands on connected
substructure.

🔴 **If this is ever scoped as "part of the ship layout" it will quietly never
happen.** Different pipeline, different tool, different owner. It is also
provable on a quicktest map today, exactly like row 4.

#### 🔴 REVISED — "big but slow" was wrong. Depth by CAPABILITY, not by work rate

**A retired seat priced my own ruling and it does not survive contact with RimWorld's
work queue:** a poor yield-per-work rate on a huge hulk means the salvage
designation sits in the backlog for years, competing with everything else the
clan does. **The practical rate is not the one we tune — it is whatever labour is
left over.** An arc nobody prioritises is an arc nobody experiences, which is the
failure this seat exists to catch.

**So the limiter changes. Each salvage job is ORDINARY speed. The hulk is deep
instead.**

> **The wreck opens in tiers, and the gate is what the clan can DO, not how long
> it takes.**

| tier | what it is | gate |
|---|---|---|
| **outer plating** | steel, and lots of it | **none — day one.** This is the early economy |
| **inner structure** | more steel, some components | a tool the clan has to make first |
| **the deep sections** | components, plasteel, the one or two real prizes | **research or equipment the clan does not have for a long time** |

⭐ **This is strictly better than a slow grind, for three reasons:**

1. **Every job completes.** Nothing rots in the queue, so the player actually
   does it, so the arc actually lands.
2. ⭐ **The player RETURNS to the wreck as they grow** — and each return pays
   better. A landmark you revisit at three different capability levels is worth
   far more than one you chew through once.
3. **The "leave" trigger lands at the right moment.** You crack the deep sections
   about when you are equipped to go, so the map empties exactly as you outgrow
   it. **That timing was luck under the slow-grind version; it is designed under
   this one.**

#### The two layers — terrain buys the image, buildings carry the economy

**A retired seat's structural finding, and it splits the design whether we like it or
not:** `BrokenSubstructure` is a **TerrainDef**. Terrain has no `costList` and
cannot be deconstructed for yield — the only removal is a designator that returns
**nothing**.

| layer | def type | what it delivers | what it must never do |
|---|---|---|---|
| **broken floor** | Terrain | the **image** and the walkability | carry any economy — it cannot |
| **the salvage** | **Buildings** standing on it | **all** yield, all tiering, all tuning | be pretty and empty |

**Precedent is already in the stack:** *Salvage Rubble* patches a `costList` onto
vanilla `RubblePile`. We would be doing the same thing to the ~170 pre-rusted
wreck props the game already ships.

⛔ **Filter the prop palette first.** Many `Ancient*` props descend from
`NonDeconstructibleAncientBuildingBase` — **removable only by explosives.** Place
one of those in the hulk and the clan *cannot strip it*, which breaks the entire
ruling. **Deconstructible defs only.**

#### ✅ SETTLED — the gate is GEOMETRY, and the last prize is BURIED. No C#.

**A retired seat found that my capability gate does not exist as a field: RimWorld has no
research or tool requirement on deconstruction.** Expressing it literally would
cost a C# comp in the companion DLL. **Declined.** Two better routes were offered
and both are taken.

**Route A — geometry gates the tiers.** Nothing is locked. **The deep sections
are BURIED behind the shallow ones.** Outer plating is reachable on day one;
inner structure only once the plating is gone; the holds only behind both.

⭐ **This is better than a research gate, not merely cheaper.** A research gate
says *"you may not touch this yet"* — a permission. **Geometry says "you have not
got there yet" — a place.** In a game about digging through a wreck, the second
is the right sentence every time, and it means the hulk is **explorable rather
than unlockable**.

It also costs nothing, adds no dependency, and **cannot be patched out from under
us by another mod** — geometry is not a field anyone can override.

**Route B — the last prize is genuinely underground.** Plasteel and components go
**beneath** the wreck as a **deep resource deposit**, which RimWorld already gates
behind a **ground-penetrating scanner plus a deep drill** — research *and*
equipment, shipped and balanced by Ludeon.

⭐ **The fiction is the best part: the clan strips the hull for years and then
finds what it was CARRYING.** The wreck's last secret is under it.

⭐ **And the scanner turns that prize into a promise.** The player can *see* the
deposit long before they can reach it — a target on the map they are working
towards. **That is far stronger than a surprise**, and it is the thing that keeps
a clan on a tile they have otherwise exhausted.

**Sequence, whole: plating → structure → drill → leave.**

⛔ **No hard gate, no comp, no companion-DLL dependency.** A permanent maintenance
cost is not worth buying something geometry provides for free.

#### ⭐ RULED — the fragment on the ground is the CARBONITE BAY

**A retired seat asked which fragment stayed behind. It is the passenger hold — and the
choice writes three other things for free.**

**The ship is `LifeDawn`, a first-wave colony ship** (`faction_roster_v2.md:370`).
So the fragment left on the sand should be **the part that made it a colony ship**:
the carbonite bay, where the colonists were carried.

> **The clan flies the vessel. What stayed on the ground is what the vessel was
> FOR.**

**Why this one and not a stern or a flank:**

1. ⭐ **The breach is not damage — it is THEFT, and that is better.** The roster
   already says the Hutts had the hulk *"stripped and slowly scrapped"* in their
   yard. **The scrappers cut into the passenger hold to take the cargo.** So the
   torn edge a retired seat wants is not a crash scar we have to justify; it is the hole
   the previous thieves made, and the clan walks out of it every morning. **The
   Jawas are the second set of scavengers on this wreck.**
2. ⭐ **Recognisable silhouette, which was a retired seat's third criterion.** Rows of
   carbonite slabs read instantly and read as nothing else. A stern section is
   anonymous; a bay of upright slabs is not.
3. **It interleaves naturally.** Slab racks, deck, gaps, more racks — the motif
   breaks itself up, so the broken-floor terrain never becomes a solid field of
   wallpaper.
4. **Carbonite is already a project concept** (`design/Jawa/carbonite_trophy_mod.md`)
   and the deck plan already names a carbonite bay at stage 7.

### 🔴 The slabs are mostly empty. A few are not.

**The Hutts took the ones worth taking. What is left is what nobody wanted.**

- **Mostly empty racks** — the bay was already picked over before the Jawas got
  here. Bleak, and it explains why the clan could claim it at all.
- ⭐ **A few slabs still occupied.** Not a system, not v1 — **a question standing
  in the player's base from the first hour.** Somebody is still in there. The
  clan can leave them, sell them, or eventually wake them.

**That is the single best thing this fragment buys**: the starting map ships with
an unresolved moral object in it, at zero mechanical cost, and it costs nothing
to ignore. A player who never touches it still walks past it every day.

⚠️ **Nothing about the occupied slabs is v1.** They are set dressing until
someone builds them. **Do not scope a wake-up quest to make the image work** —
the image works because the question is unanswered.

**Crop guidance for a retired seat:** ≤1,200 cells, breach facing the colony, slab rows
running across the fragment so the broken deck shows between them.

#### 🔄 RE-RULED — it is a CRYPTOSLEEP hold, not a carbonite bay

**A retired seat is right and the correction improves the fiction.** There is **no
carbonite slab prop anywhere on disk** — Outer Rim's "carbonite" is a cryoban
*weapon* (a timed freeze that thaws), and our own carbonite mod is **greenlit,
parked and unbuilt** (`design/Jawa/carbonite_trophy_mod.md`, audited 2026-08-06).
Building a mod to make an image work is exactly backwards.

⭐ **And caskets are better fiction than slabs, not merely cheaper.**

> **Carbonite is Hutt tech — a thing done *to* people. Cryptosleep is what a
> colony ship is *for*.**

`LifeDawn` is a first-wave colony vessel. Its passenger hold carries **sleepers**,
and that makes the fragment on the sand the hold of a colony **that never
landed**.

⭐⭐ **And the part I was going to have to author is native behaviour.** Vanilla
ancient caskets already contain sleeping pawns. **"Mostly empty, a few are not"
is what the game does by itself** — the unresolved question stands in the
player's base for free, with no scripting and no wake-up quest, exactly as
specified.

**Everything else in the ruling survives untouched:** the breach is still Hutt
theft, the Jawas are still the second scavengers, the rows still run across the
crop and still interleave the broken deck.

🔴 **Name the right def. `AncientCryptosleepCasket` is deconstructible;
`AncientCryptosleepPod` is PERMANENTLY UNDECONSTRUCTIBLE.** Placing the pod
breaks the strippable ruling outright. **Casket, always.**

**And it is the richest salvage in the ruins kit — Steel 180 + Uranium 5 each** —
so the v2 tiered economy lands on this fragment perfectly.

⚠️ **Know what you are placing: vanilla sleepers can wake hostile.** That is a
feature, not a hazard to design out — the first casket the clan cracks may fight
back, which is the correct lesson about opening things you do not understand.
**It is also a strong argument for leaving them shut in v1.**

⭐ **A free v2 hook, if the carbonite mod is ever built:** a handful of carbonite
slabs *among* the caskets — **the ones the Hutts had already prepared to move.**
Costs nothing now, and it explains the scrappers' interrupted work.

#### ✅ BUILT `00a1398` — and two calls answered

**619 cells of 1,200. 31 caskets in three banks, 6 mech chunks, 45/55 broken-to-
intact from value noise — irregular patches, no repeats.** The crop is the only
unbroken 51–55-wide band in the whole hull, so **it is a hold because the
geometry says so**, not because we labelled it.

**Call 1 — the breach cannot be aimed at the colony without C#. DECLINED.**

`GenStep_Scatterer` picks its own spot and takes no argument about the player
start; aiming it needs a custom GenStep reading `MapGenerator.PlayerStartSpot`.
**Not worth a code dependency, and the narrative survives without it** — ⭐ **the
player places the colony, not us.** They will build beside the hulk and use the
opening because it is the way in. **The behaviour I wanted arrives from player
behaviour rather than from placement**, which is the better source anyway. Pinned
rotation (breach always east) is enough.

**Call 2 — the yield is 3,030 steel · 77.5 uranium · 90 gravlite. NO CUT YET.**

That is roughly twice a whole scrapfields scatter, one-off and non-renewing.
**My instinct says high; my instinct has not played it.**

- **Steel ~3,000 is the early economy, and that is the design** — the wreck is
  meant to replace mining for the opening act.
- ⭐ **90 gravlite is the best number in the set.** Substructure costs 1 gravlite
  + 4 steel per tile, so **the hulk pays for ~90 tiles of deck** — salvage
  converting directly into ship. That is the campaign's thesis in a number.
- ⚠️ **Uranium 77.5 is the one to watch.** It is the only material here outside
  the campaign's stated economy, and the only one that could read as a ladder.

**Ruling: ship it as built and MEASURE it.** Nerfing a number nobody has played
is worse than watching it once. **If it is cut, cut yield per casket, not casket
count** — 31 in three touching banks is what makes it read as a hold at play
zoom, and readability was the whole point of the pick.

**Two notes carried:**
- **Caskets carry an explosive comp (radius 2.66, flame) and can chain in a
  touching row — when DESTROYED, not when deconstructed.** ⭐ Keep it. *"Do not
  fight inside the hold"* is a lesson the map teaches for free.
- ⚠️ **Nobody has seen the caskets.** Vanilla art is in AssetBundles, so defs,
  sizes and yields are verified on disk and **the look is not.** First live
  sighting is the only outstanding check.
