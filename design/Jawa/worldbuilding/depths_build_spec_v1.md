<!-- status: RULED — both §0 questions answered by the owner 2026-08-31 (question cards).
     Executes: depths_concept.md §11 v1 slice. Grounded in DEPTHS_ODYSSEY_VERIFY_1's
     source verdicts and the two donor surveys (depths_concept §10, mods/underwater_donor_scan_2026-08-31.md). -->
# The Depths — v1 "Dive expeditions" build spec

Everything here follows from three settled inputs: the concept
(`depths_concept.md`, owner-seeded twice), the Odyssey source read
(`infrastructure/state/items/DEPTHS_ODYSSEY_VERIFY_1.md` — verdict: **clone job,
not patch job**; triggers data-driven, consumers hardcoded), and the donor scans.
The C# surface is small and bounded: one MapComponent, one GenStep, one Harmony
weapon gate. Everything else is defs.

## 0. The two rulings — RULED by the owner, 2026-08-31

1. ✅ **Dive stat: INDEPENDENT (`RM_PressureRating`) — ratified.** The reskin ships
   fastest (zero C#) but merges number spaces: every vacsuit in the campaign
   becomes a working dive suit, spacewalking and diving stay coupled forever, and
   §7-of-concept's adapted-race genes would also zero *vacuum* harm. This
   campaign runs live space content (gravship, Odyssey), so the collision is
   real, and the companion DLL is required for the lure clock and weapon gate
   anyway — the marginal cost of the independent stat is one more Harmony-free
   StatDef plus the exposure logic we already own. Recommendation: independent.
2. ✅ **The short-sight cap: routed through CAI fog of war — owner's ruling,
   verbatim:** *"We had already been wanting to pull in the cai fog of war.
   That mod needs full exploration. It promised much improved pawn combat
   experiences and real fog of war. Go ahead and do a deep dive now both for
   general gameplay as well as wrt underwater needs. It's a big integration so
   be thorough."* ⇒ The dive is DONE
   (`design/Jawa/mods/cai_fog_deep_dive_2026-08-31.md`) and the owner ruled
   **Route B: CAI combat AI + NWN Real Fog of War** (CAI's own fog off; S&D
   dropped). The lamp-cone rides NWN's glow-native fog (Apache-2.0 —
   absorbable if we ever need to own it): permanent-dark seafloor + lamps
   should produce the cone through its `NightVisionEffectiveness`/glow model,
   with a per-map view-range clamp as the fallback if configuration alone
   overshoots. Verified during `FOW_ROUTE_B_INTEGRATION_1`'s quicktests; v1's
   dark/lure mechanics (§2, §3) do not wait on it.

## 1. Mod shape and naming (three-tier, per NAMING_SCHEME_PLAN)

| package | tier | carries |
|---|---|---|
| `mandrake.rm.depths` | RimMandrake framework | the C# (MapComponent, GenStep, weapon gate), stats, hediffs, base defs, dive gear, arrival mode |
| `mandrake.rsw.seabeasts` | RimStarWars | the six creature roles incl. the Naboo trio, SW weapon flavor (discharge/harpoon as blaster-age gear) |
| `mandrake.rut.ashkarrseas` | RimUtinni | the three named seas' site placement, the Deepwater faction's campaign identity, Oomo's shore rite |

Prefixes `RM_`/`RSW_`/`RUT_`; C# namespace `RimMandrake.Depths`. "Jawa" appears
in lore text only.

## 2. The dive-site map (defs + one small GenStep class)

- `WorldObjectDef RM_DiveSite` on sea tiles; source read confirms
  `SpaceMapParent` picks its generator from `def.mapGenerator` — start by
  reusing it before writing any MapParent subclass.
- `MapGeneratorDef RM_Seafloor` family via ParentName inheritance (the
  `Space`→`Asteroid` pattern): `RM_Seafloor_WreckField` is the one v1 site type.
- **`GenStep_Seafloor` (C#, small)** — the seafloor analog of `GenStep_Space`'s
  hardcoded terrain fill: silt base, reef outcrops, wreck scatter (reuse the
  scrapfield scatter grammar), lightkelp stands. This is the only mapgen C#.
- Permanent dark: the map's `BiomeDef` (a dedicated `RM_SeafloorBiome`,
  `inVacuum` **false** — we are not lighting vacuum machinery, see §3) with no
  sky light; confirm via quicktest that a pocket-map biome can zero ambient
  glow, else force it with a permanent local `GameConditionDef`.

## 3. The exposure stack (defs + the one MapComponent)

No room diffusion in v1 — a dive site is uniformly submerged open water, which
is *simpler* than Odyssey's room graph. `MapComponent_Depths` (companion DLL)
ticks per-pawn:

- **Oxygen**: `HediffDef RM_Drowning`, severity rises when
  `RM_WaterBreathing == 0` and suit air is out; `RM_AirSupply` as an apparel
  stat consumed over ticks (the dive clock made visible). Suit off / air out →
  drowning ramp, GravTide-shape formula but ours:
  `exposure = (1 − gearSeal) × (1 − RM_WaterBreathing)`.
- **Pressure**: `RM_PressureRating` (apparel, shallowest-piece-decides via a
  StatWorker reading a `DefModExtension`, the pattern §2-of-the-source-read
  confirms works) vs the site's fixed depth band; deficit drives
  `RM_PressureSickness`.
- **Drag**: `StatPart_WaterDrag` injected onto vanilla `MoveSpeed` by patch
  (GravTide-proven shape), zeroed by the adapted gene.
- **The lure clock**: the same component counts lit glowers + discharge events
  into `lurePressure`, and above thresholds fires descent incidents (§5). This
  is Visibility's sibling dial (concept §9) — build it as its own class so the
  shared core can be extracted later.
- **Genes** (Biotech): `RM_Gene_WaterBreathing`, `RM_Gene_PressureAdapted`,
  `RM_Gene_DepthSight`, `RM_Gene_Swimmer` — each zeroes exactly one lever
  above. This is why every lever is a stat: a gene that offsets a stat is XML.

## 4. Weapons in water (one Harmony patch + defs)

- `RM_UnderwaterWeaponExtension { inWaterFactor }` read by Harmony patches on
  `Verb.EffectiveRange` / projectile damage (the GravTide-proven target list,
  code written fresh). Default factor near zero — carrying surface guns below
  is the mistake the game teaches once. Melee unaffected.
- New weapons (RSW flavor): `RSW_HarpoonCaster` (silent, AP, no lure),
  `RSW_ArcProjector` (the discharge: map-scoped water AoE stun/burn in radius,
  Electrofishing-pattern comp rewritten ours, big `lurePressure` spike),
  `RSW_SonicConcussor` (mid-tier). Balance under Law 3 alongside the beasts.
- Electrified water hazard rides the same AoE comp aimed at pawns standing in
  water — powered wreck nodes on the map use it as a trap.

## 5. Descent (pure data + incidents)

`PawnsArrivalModeDef` reusing vanilla **`EmergeFromWater`** worker — the source
read's best find: descent arrivals are data-only. Incidents: `RM_DescentRaid`
(predator packs arrive by column, lure-weighted), `RM_SalvageFall` (the rain of
wrecks — goodwill-free loot events). The leviathan is an incident, not a
pawn-kind raid: one per sea, named at the RUT layer.

## 6. Creatures (defs + the art pass already running)

Six roles per concept §6, sized under Law 3, born normalized (no retrofit):
opee (silt ambusher, bs 1–2) · colo claw fish (harpooner, bs 2–4) · sando
(leviathan, bs 12–20, ONE, named) · shoal grazer (0.1–0.5) · scavenger swarm
(0.2) · colossal filter-feeder (30+, graze-anchored neutral). Art:
SW_SEA_MONSTERS_ART_1 mockups in flight. Lane-1 borrowed fauna stay
patch-only per the license table in the source-read item.

## 7. The Deepwater faction (defs)

`FactionDef RUT_DeepwaterCompact` (the roster's Deepwater Compact made real in
the deep): settlements permitted on sea tiles, trade caravans surface-side,
pawns carrying the §3 genes. v1 = present, visitable, trading. The
Empire-refuge arc is v2 by concept §11 — but the faction's worldview text
plants it now.

## 8. Build order, each step quicktest-provable on the 22s minimal list

1. `mandrake.rm.depths` skeleton + stats/hediffs/genes (offline validate).
2. `MapComponent_Depths` exposure only → quicktest: unsuited pawn on a forced
   seafloor map drowns on the predicted curve; suited pawn doesn't; gene pawn
   ignores it. (Bridge spawns; spawn MANY per the confound rule.)
3. `GenStep_Seafloor` + site defs → generate the wreck-field site, LOOK.
4. Weapon gate + the three new weapons → quicktest damage table vs prediction.
5. Lure clock + descent incidents → forced-fire via `jawa/fire_incident`,
   read the REPLY's faction/kind fields, never the request's.
6. Faction + creatures + RUT sea placement → cold-load run-sheet item, batched.

## 9. What v1 explicitly does not build

No swimming/pathing on open sea tiles (SwimmingKit is dead; sites sidestep it),
no room flooding, no moon pools, no underwater base-building, no sight-radius
cap (§0.2), no refuge storyline, no sound-lure. All v2, all already registered.
