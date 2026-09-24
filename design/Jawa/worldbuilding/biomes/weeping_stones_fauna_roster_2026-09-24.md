# The Weeping Stones — fauna roster

_Drafted by a Fable design subagent, 2026-09-24, against the frozen sheet, for
`WEEPING_STONES_DESIGN_SITTING_1`._

**Status: DESIGN PROPOSAL. Nothing authored.**

Subject: the `RM_WeepingStones` biome mod (RM_ tier per Q12–Q15; live def today is
`RUT_WeepingStones`). Companion doc: `weeping_stones_flora_roster_2026-09-24.md`.
Frozen sheet: `weeping_stones.md` — §4–§6 and §10 are the grading standard; its
rulings bind and this roster adds detail, never changes one. The ruled roster
JSON (`rosters/weeping_stones.json`, 2026-09-09) is INPUT: its ten kept/imported
rows, its 24 evictions, and the **RULED dewback move from LavaField (owner,
2026-09-06)** all stand; nothing here re-adjudicates any of them.

## READ FIRST — the two-tier shape of this cast

Q11a (`biome_mod_architecture.md` §7): the tier line is IP, not flavour. The
sheet's §10 natives (tirbak, sillik, mirrik, ssurr, vhakk, burrak) are
**invented** — they are `RM_` tier, cast inline, franchise-free. The ruled keeps
(Dewback, Fanback, Bantha, Eopie …) are **canon or donor content** — they ride
the Utinni patch layer, added on top. 🔴 The free mod is NOT a thin fallback:
the invented rows below are a complete ecosystem on their own — prey base,
grazers, industry, display, apex — and the canon herd only enriches it.

**The laws every row obeys:**

- **§5 comb rule (hard, drives every sprite):** every native carries a raisable
  crest, fin, or comb in its silhouette — the wind-comb shape, fanned open when
  the wind runs, then licked dry; dew-grooves running to the mouth.
- **§6 ambush ban:** no roster entry whose hunting story is the pool margin.
  Violence lives on the approaches and in scarcity, never at full water.
- **The truce (§4):** at the water it holds completely — MAD or peace. Ruled
  cheap-for-v1: spawn/flavor suppression of predator hunts near water; the
  honest behavior mod is v2.
- **R21:** condensate, never rain. **R17:** fliers cross biomes by design — a
  cross-biome flier appearance is not a contradiction.
- **One-home law (owner, 2026-09-21):** each native names why it cannot live
  elsewhere; the pilgrim ring is the sheet's own in-fiction visitor mechanism,
  annotated per row, and existing multi-homed rows are annotated, never cut.

### The silhouette brief is the specification

The FORM column is what art is commissioned against; every silhouette is a comb
variant and every row must read distinctly top-down against pale stone.

## At a glance

| the weep-faces | the pools | the approaches | the sky |
|---|---|---|---|
| **sillik** — the prey base, licking the film | **ssurr** — the fan-dancer; romance made animal | **vhakk** — the warden; the margin made flesh | **mirrik** — the dew-smoke swarm (flier) |
| | **murrin** — the pool fish (rides FISH_BY_BIOME_1) | **burrak / burradar** — the well-diggers | *(Utinni: Dactillion, the flier mount)* |
| | *(Utinni: Dewback, Fanback, the pilgrim herds)* | **tirbak** — the walking cistern on the caravan roads | |

## 1. The rulings this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **Sorts-of-animals frame: residents / pilgrims / margin** | sheet §10 | every row names its ring; pilgrimage density is mostly *visitors* |
| **The comb convergence** | sheet §4/§5 | every FORM below is a crest, fin, or comb — no exceptions |
| **No ambush-at-water predator** | sheet §6 | the one apex hunts the approaches by *design*, not restraint; drinks in rotation |
| **The truce, cheap for v1** | sheet §4 + Owed | vhakk row names the built mechanism candidates; honest behavior is v2 |
| **Seven proposed natives are candidates, not commitments** | JSON confidence, RULED | this doc is the candidate detail the sitting judges — still not authored |
| **Dewback move from LavaField** | RULED, owner 2026-09-06 | recorded in §3, untouched |
| **Fish live in the true pools** | JSON `fish` ruling (YES) | one candidate row, explicitly riding `FISH_BY_BIOME_1` |
| **One animal, one biome** | owner 2026-09-21 | one-home note per native; pilgrims annotated as the sheet's own mechanism |
| **Fliers fly for real** | flier law 2026-09-19 (core `MaxFlightTime`) | mirrik marked flier; Dactillion's flier claim stays UNMEASURED (register flag broken, JSON) |
| **The free mod stands rich alone** | Q11a | eight invented rows, no donor, no canon needed |

## 2. Rows — the invented natives (RM_ tier, 8 rows)

Ecosystem pyramid: two abundant small rows (sillik 0.8, mirrik 0.6), two
small-medium (ssurr, murrin), then the large rows thin out (tirbak 0.15, burrak
0.12, vhakk 0.08, burradar 0.02). Small outnumbers large in kind and in count.

### 2a. The prey base — `RM_Sillik` (row 1)

| field | value |
|---|---|
| defName / label | `RM_Sillik` / sillik — *weep-mouse* (sheet §10 name, collision-checked there) |
| silhouette FORM | **tiny flat-bodied climber pressed to vertical stone, whisker-comb fanned around the muzzle** |
| look, one line | A palm-sized silver-grey licker that lives ON the vertical weep-faces themselves, spread flat against the rock, muzzle-comb combing the water film — whole faces stippled with them at wind-hour. |
| ring / niche | **Resident; the prey base** (sheet §10). It harvests the thinnest water in the biome — the film itself — so it needs no pool and never joins the crowd: the one native the truce barely touches. |
| size band / commonality | tiny (bs ~0.2) / **0.8** — the most common animal here |
| one-home note | its whole physiology is the weep-film — vertical wet stone that recharges daily exists nowhere else on the planet (Cracked Lands seeps are flood-fed, not daily) |
| mechanisms | ✅ mostly built: **`RM_JobGiver_FilterFeedTerrain`** (CreatureBehaviors) is terrain-keyed feeding — point it at weep/shade cells; **`RM_MapComponent_ShadeGrid` + `RM_JobGiver_WanderInShadeGrid`/`RM_JobGiver_SeekShade`** keep it living on stone-shade real estate (§4). Wall-clinging is ART, not engine (no climb mechanic owed). |
| art | **OWED** — must read at stipple density on pale stone, like the Sump mouse reads in lines |

### 2b. The dew-smoke — `RM_Mirrik` (row 2) — FLIER

| field | value |
|---|---|
| defName / label | `RM_Mirrik` / mirrik — *dew-smoke* (sheet §10 name) |
| silhouette FORM | **a smudge of motes with mesh-wing glints — the swarm IS the silhouette; single sprite: cruciform mesh-wing insect** |
| look, one line | Thumb-sized insects with water-combing mesh wings that mist-dance over the pools at wind-hour — from any distance, smoke rising off the water that flows the wrong way. |
| ring / niche | **Resident; pollinator and industry.** Pollinates the blade-flora; its cocoons are the **dewsilk** source (sheet §11 — the biome's signature trade good). The swarm at wind-hour is the biome doing its actual living (§10b). |
| size band / commonality | tiny (bs ~0.15) / **0.6** |
| 🔴 flier law | it flies in the fiction ⇒ it flies in the game: core `MaxFlightTime`/`FlightCooldown` stats + race flight fields (Locust shape). No flip-book frames blocks nothing — flight ships plainer without them. |
| one-home note | its wing-mesh only pays where the air itself carries water daily; anywhere drier the mesh is dead weight — R17 note: it may *drift* on the wind as flavor, but it homes here only |
| mechanisms | ✅ swarm population cycles: **`RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation`** (CreatureBehaviors) already do exactly this for the Fever Wood grubs — reuse, don't reinvent. Dewsilk = cocoon item def + tamed-hive harvest (defs only, no new C#). |
| art | **OWED** — plus `RM_Dewsilk` item art |

### 2c. The fan-dancer — `RM_Ssurr` (row 3)

| field | value |
|---|---|
| defName / label | `RM_Ssurr` / ssurr — *fan-dancer* (sheet §10 name) |
| silhouette FORM | **slender reptile, ONE enormous half-circle crest-fan folded flat or blazing open — closed it is a blade, open it is a wheel** |
| look, one line | A hound-sized crest-fan reptile whose breeding displays happen at the pools — harmless, spectacular, beloved; the fan doubles as its dew-comb at wind-hour, so courtship and drinking are the same gesture. |
| ring / niche | **Resident; the romance-and-ritual ruling (§4) made animal.** The pools are places of play, bonding, and breeding — the ssurr is that sentence with legs, and the tamable charmer of the biome. |
| size band / commonality | small-med (bs ~0.7) / **0.35** |
| one-home note | its display *is* pool-ritual — the behavior has no meaning without truce water; nowhere else has water you can turn your back on |
| mechanisms | ✅ **`RM_CompTameSootheAura`** (CreatureBehaviors) is a built soothe-aura — a natural fit for the beloved/bonding register if the sitting wants it mechanical; otherwise defs only. Display = graphic states / flavor v1, no C# owed. |
| art | **OWED** — the fan open/closed is the whole sprite brief |

### 2d. The walking cistern — `RM_Tirbak` (row 4)

| field | value |
|---|---|
| defName / label | `RM_Tirbak` / tirbak — *tanker* (sheet §10 name) |
| silhouette FORM | **massive round-backed colossus with a row of dorsal rain-fins like a ship's ventilation cowls** |
| look, one line | A placid colossus that drinks once per wind-cycle and carries it for days, dorsal fins fanned to the wind as it walks — the caravan mount of the oasis string. |
| ring / niche | **Resident-pilgrim; the caravan economy.** Replaces the donor's muffalo/dromedary/elephant pack slot (sheet §10). The beast the desert roads were beaded for (§8). |
| size band / commonality | huge (bs ~3.5) / **0.15** |
| one-home note | it is *infrastructure of the oasis string* — its drink-once-per-cycle body only works where reliable pools sit a caravan-leg apart; pack caravans take it everywhere, which is travel, not homing (R17 spirit) |
| mechanisms | none blocking (JSON agrees): packAnimal + caravan stats; "carries water for days" is fiction v1 since colonists carry water as items — an inspired v2 could hang a comp on it, not owed now |
| art | **OWED** |

### 2e. The well-diggers — `RM_Burrak` and `RM_Burradar` (rows 5–6)

| field | `RM_Burrak` (row 5) | `RM_Burradar` (row 6) |
|---|---|---|
| label | burrak — *well-digger* (sheet §10 name) | burradar — the elder form |
| silhouette FORM | **low broad digger, claw-combs held like twin rakes before it** | **the same animal grown vast and high-shouldered, claw-combs worn to stumps, back silted with weep-mat green** |
| look, one line | A bear-sized wallower that digs catch-basins that outlive it — abandoned burrak digs are how new micro-oases start. | The elder that digs the deep wells; a working oasis tolerates one the way a town tolerates its engineer. |
| ring / niche | **Resident; the biome's terraformer.** Its digs are the natural bottom rung of the succession ladder (§8 rung 1). | **Rare landmark animal** — one per region, known individually, half-sacred. |
| size band / commonality | large (bs ~2.2) / **0.12** | huge (bs ~4) / **0.02** |
| one-home note | digging catch-basins is only a living where the wind refills them — the trade is dew-country-only | rides the burrak's |
| mechanisms | dig-catch-basin terrain edits are **v2 per the ruled JSON** (`mechanic_load`). If v2 lands: ✅ **`RM_CompDungSeeder`** (CreatureBehaviors — an animal already seeding growth behind itself) and ✅ **`RM_MapComponent_LivingRegrowth`** (EnvironmentalHazards — terrain-gated regrowth) are the built patterns to extend; do not write a third terrain-editing system. v1: wallow = filth + flavor. | rides row 5 |
| art | **OWED** | **OWED** — same rig, aged |

### 2f. The warden — `RM_Vhakk` (row 7)

| field | value |
|---|---|
| defName / label | `RM_Vhakk` / vhakk — *the warden* (sheet §10 name) |
| silhouette FORM | **long low courser, a single blade-crest running nape to tail like a dorsal keel** |
| look, one line | The margin made flesh: it never hunts at water — by design, not restraint; it drinks in strict rotation like everything else — and owns the approaches instead. Its patrol is the oasis's outermost wall. |
| ring / niche | **The margin; the one native apex.** §6's ambush ban satisfied structurally: its hunting story IS the approaches. A predator special on the def is legal (the JSON's Dewback note establishes this reading). |
| size band / commonality | large (bs ~1.8) / **0.08** — apex-rare, pyramid intact |
| one-home note | its niche is *enforcing the geometry of pilgrimage* — approach-lanes converging on truce water exist only here |
| mechanisms | truce v1 is RULED cheap (sheet Owed): spawn/flavor suppression of hunts near water. ✅ The built shape to reuse is **`RM_MapComponent_DreadField` + `RM_JobGiver_DreadAvoidWander`** (EnvironmentalHazards, the Sump's avoid-field): inverted, a water-radius field predators' hunt jobs avoid. Also note **`RM_TenantTruceExtension`** (empty marker DefModExtension, EnvironmentalHazards) — the truce-marker *pattern* exists; a `RM_WaterTruceExtension` marker + one JobGiver filter is the whole v1. |
| art | **OWED** |

### 2g. The pool fish — `RM_Murrin` (row 8)

| field | value |
|---|---|
| defName / label | `RM_Murrin` / murrin *(NEW coinage — not collision-checked; see Questions)* |
| silhouette FORM | **deep-keeled little fish, one tall dorsal comb-fin breaking the surface in rings** |
| look, one line | A hand-length pool fish whose comb-fin cuts the surface at wind-hour — the pools' rings-within-rings, alive. A silent pool with no murrin rings is the first sign an oasis is dying (§10b's dead-oasis image, underwater). |
| ring / niche | **Resident; the pool's own life.** The JSON's fish ruling is YES — fish live in the true pools, riding pool terrain, not world water. |
| size band / commonality | tiny / pool-terrain only | 
| 🔴 lane note | species selection is **owed to `FISH_BY_BIOME_1`** (JSON's own note). This row is a *candidate carried to that item*, not a casting here. Constraints carried: nothing pollution-flavored, nothing that makes the pool a hunting story. Pools are map-scale terrain, so this is likely a FishDef (+ optional pond critter) — the sea-biome two-def law is about seas; whether it binds pools is FISH_BY_BIOME_1's call. |
| mechanisms | FishDef (Odyssey `MayRequire`) per the Scald precedent | 
| art | **OWED** (deferred with the row) |

## 3. Kept and ruled rows (INPUT — never re-adjudicated here)

All ten stand exactly as the ruled JSON has them; this table only adds tier
routing and dependency flags. **Every row here is canon or donor content ⇒
Utinni patch layer** (Q11a): patched into the biome's `wildAnimals` from
`UtinniPatches`, never a dependency of `RM_WeepingStones`.

| def | comm. | ring (JSON) | tier routing | donor/canon flag |
|---|---|---|---|---|
| `Dewback` | 0.4 | large-resident | Utinni patch | 🔑 RULED move from LavaField (owner 2026-09-06) — genuine canon (films); donor def, port owed if the donor retires (`MLIE_FAUNA_ABSORPTION_1` lane) |
| `Fanback` | 0.5 | large-resident (⭐ the gift — literal fan-back) | Utinni patch | donor (SW Animal Collection); ⚠️ canon status UNVERIFIED — verify via Wookieepedia search API before any canon claim; donor defName is not evidence |
| `ColossusToad` | 0.4 | medium-resident | Utinni patch | donor; canon status UNVERIFIED |
| `Ollopom` | 0.7 | small-resident (pool-crowd prey) | Utinni patch | donor; canon status UNVERIFIED |
| `Boma` | 0.15 | large-margin predator | Utinni patch | donor; genuine canon (KotOR-era beast) — cite check still cheap to run |
| `Dactillion` | 0.15 | flier-mount | Utinni patch | donor; genuine canon; flier claim UNMEASURED (JSON) — if it flies in fiction it must fly for real (flier law) when its def is touched |
| `AA_Eyeling` | 0.1 | omen (this IS the ikee) | Utinni patch | 🔴 donor (Alpha Animals) — the ikee is OUR fiction wearing a donor def; strongest candidate on this list for an RM_ port since the *identity* is invented |
| `Bantha` | 0.1 | pilgrim (primary home Desert, owner card 3) | Utinni patch | canon; multi-home is the pilgrim mechanism — annotated, never cut |
| `Jamel` | 0.1 | pilgrim | Utinni patch | donor; canon status UNVERIFIED; pilgrim annotation as above |
| `Eopie` | 0.1 | pilgrim | Utinni patch | canon; pilgrim annotation as above |

The JSON's 24 evictions (pollution bodies, cave register, ambushers, the
Rancor) stand; dispositions were homeless-reserve/cut there and are not
reopened here.

## 4. Donor dependencies to flag

- **Every §3 row is donor-def content today.** The RM_ mod depends on none of
  them (they ride Utinni patches with `MayRequire`), but the *campaign* still
  hard-depends on the donor mods until ports land — same shape as
  `MLIE_ABSORPTION_BIOME_WIRING_1`. The sitting should rank ports; `AA_Eyeling`
  → `RM_`/`RSW_` ikee first (invented identity, donor body).
- `AA_Eyeling` (Alpha Animals), `Fanback`/`ColossusToad`/`Ollopom`/`Jamel` etc.
  (SW Animal Collection family) — per-row donor attribution is asserted from
  prefix/register only and is **owed verification at port time**.
- No invented row (§2) touches any donor def. The RM_ mod stands alone.

## Questions for the owner

**Category-level first:**

1. **Does the RM_ tier need its own pilgrim ring?** Without the Utinni layer,
   the free mod has no visiting herds (Bantha/Jamel/Eopie are all
   canon/donor) — yet "pilgrimage density, mostly visitors" is the biome's §4
   identity. Q11a says the free mod must look the same. Invent 1–2 RM_ herd
   pilgrims (homed in an RM_ desert biome, visiting here), or accept that
   pilgrims are campaign-only?
2. **Does the RM_ tier want its own flier?** The only mount-flier (Dactillion)
   and the flier mount niche are Utinni-side; the mirrik is a swarm, not a
   sky presence. An invented ridge-flier is easy to add if the free mod's sky
   should not be empty — or R17 lets other biomes' RM_ fliers visit instead.
3. **Fish: is `FISH_BY_BIOME_1` still the lane,** with row 8 carried there as
   this biome's candidate — or does this sitting cast pool fish directly now
   that pools are the biome's heart?
4. **Burrak/burradar: one def with life stages, or two defs?** The sheet's
   elder-form ladder reads as a life stage (which would also be the one-home
   law's own carve-out pattern); two defs is cheaper and vanilla-shaped.

**Per-row:**

5. `RM_Ssurr` — should the beloved/bonding register be mechanical
   (`RM_CompTameSootheAura` reuse) or pure flavor v1?
6. `RM_Vhakk` — confirm the truce v1 build shape: water-radius hunt
   suppression via the DreadField pattern (named in row 7), i.e. predators
   simply never receive hunt jobs within N cells of pool terrain. Cheap,
   already-shaped, but it will protect *prey at the pool* from the player's
   tamed predators too — acceptable?
7. `RM_Mirrik` — dewsilk: fabric-tier positioning (vs devilstrand/synthread)
   is unowned; does the sitting set it or does it ride the item-economy pass?
8. `RM_Tirbak` — commonality 0.15 makes the caravan colossus scarce; if the
   oasis-string trade read should dominate the biome's big-animal silhouette,
   raise to ~0.25 and drop Dewback's Utinni add to compensate (Dewback's 0.4
   is the ruled number, so the *adjust* would need his word — flag only).
9. `RM_Murrin` and the flora coinages — name collision check against
   `creature_names_ashkarr.md`/`Alien_Bestiary.md` clade roots is OWED (the
   six §10 names were checked on the sheet 2026-09-06; murrin is new today).
10. `AA_Eyeling` → ikee port: file it from this sitting (RM_ or RSW_ tier —
    the ikee fiction is ours, so RM_ reads right), or leave it riding Alpha
    Animals until the absorption wave reaches it?

---

_Every row honours the §5 comb rule, the §6 bans (no ambush-at-water, no
Earth-nameable, no pollution bodies in sacred water), R21 (condensate), R17
(fliers cross biomes), and the one-home law with a stated reason per native.
The pyramid holds: 4 small/tiny rows above 0.3; 4 large rows at 0.15 and below._
