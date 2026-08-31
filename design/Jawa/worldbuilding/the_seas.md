<!-- status: draft — BENCH synthesis of the three-arm seas fan-out, 2026-08-31. Owner: "We simply must fill the seas!" Companion concept: depths_concept.md. Data: the in-stack survey, the web survey, beast_roster.csv (which found the seas empty). -->
# The Seas of Ash'karr — the filling program

_Three facts frame everything (MEASURED against `1742630eb6253187`): the
seas are **sealed** — `WaterDeep`/`WaterOceanDeep` are Impassable and no mod
in 584 changes it; the seas are **faunaless** — Ocean and Lake have empty
wildAnimals; and the stack already holds a **misplaced SW aquatic cast**:
Dianoga and Dragonsnake exist and never spawn anywhere, KwazelMaw ("giant
aquatic slugs") spawns in ExtremeDesert 0.35, Mott in LavaField 0.7 —
collection defaults nobody curated. Art for ~10 waterline creatures already
exists in the stack._

## Lane 1 — the WATERLINE (patch-only, fillable now)

Shore, shallows, and surface life with zero new mechanics:
- **Repatriate the misplaced**: KwazelMaw and Mott out of the fire deserts
  into Lake/DesertOasis/coastal biomes; give Dianoga (standing water,
  wrecks, the ship's own sumps — the trash-compactor monster is a *hazard*,
  not a biome animal) and Dragonsnake their first spawns. Fambaa, Fanback,
  Blixus complete the cast of seven.
- **Borrow the neighbors**: the BMT fish family (Mucklurker catfish, the
  tumorfish, TaintedTurtle) and Alpha Animals' coastal amphibians for the
  shallows; Megasquid and DA_LeviathanCrab as the big silhouettes offshore.
- **Odyssey fishing makes the seas HARVESTABLE today**: fish are items, not
  pawns — `Fish*` tile mutators + fishing zones + FishShadow flecks give
  living-looking, workable water with vanilla machinery. And
  **`Fishing_Sacred` is a shipped PreceptDef** — Oomo's sea-devotion is one
  precept away.

## Lane 2 — REASONS TO GO (the tilemap earns visits)

- **Theology first**: the seas are **Oomo's country** (the tile→god
  annotation in `sacred_sites_pass_1.md` already implies it). The
  breeding-sanctuary Body-vision *requires* water; a shore-rite (the owner's
  ritual system) and a fishing precept make pilgrimage mechanical. The deep
  is **Ishko's second country** — the one dark the unsetting sun cannot
  enter (see depths_concept.md's light economy).
- **Rekko's tithe**: sunken wreck sites on sea tiles — the sea as the
  galaxy's largest scrap-heap; salvage expeditions by boat (Vehicle
  Framework has watercraft support) before diving exists.
- **Quests/vaults**: a Forsaken vault beneath the water (the dungeons arc
  already specs vault variety); leviathan-hunt quests once Law 3 beasts
  swim.
- **Unique resources**: lightkelp (the Depths' safe light), fish as the
  non-farming food lane (Jawa don't farm — Ta'Baa/Oomo approve of taking
  what swims).

## Lane 3 — THE DEPTHS (the mod nobody has shipped)

Full concept: `depths_concept.md`. The web survey confirmed the lane is
EMPTY — no underwater colony exists in the ecosystem, and the community
knows Odyssey's chassis makes it possible. The in-stack survey inventoried
the complete clone template: `VacuumResistance` stat → pressure resistance;
`VacuumExposure/VacuumBurn` hediffs → drowning/pressure; the vacsuit apparel
line (child sizes included) → dive suits; orbital map generation → seafloor
sites; orbital arrival families → descent arrivals. **A clone job, not an
invention job.** Water-locked creatures have proven open-source prior art
(SwimmingKit + TerrainMovementKit, the pair under Biomes! Islands' full
seaweed→sardine→shark ecosystem) — study, not adopt-blind (1.6 status
UNVERIFIED, Steam rate-limited the check).

## The art pass (owner: "We will totally do that")

**SW sea monsters exist in NO mod anywhere** — the Naboo trench trio (opee
sea killer, colo claw fish, sando aqua monster) is unclaimed IP-space, the
same vacancy shape as the snare/pitfall register. The escalation gag
("there's always a bigger fish") is *the* iconic SW ocean beat and it maps
perfectly onto beast-normalization Law 3: a sando at leviathan bodySize
under the 12–15×bs hit curve is a genuine world event. Creature slots by
role are in depths_concept.md §4; generating-rimworld-sprites is the
pipeline; tier per the naming scheme: framework RimMandrake, SW cast
RimStarWars, Ash'karr placement RimUtinni.

## Sequencing & gates

1. **Waterline pass** — patch-only, buildable now (SEAS_WATERLINE_PASS_1).
2. **Odyssey source read** — one offline rimsage session on the vacuum
   pipeline; decides patch-mod vs companion-DLL for the Depths and gates
   its build spec (DEPTHS_ODYSSEY_VERIFY_1). Include the SwimmingKit 1.6
   check and Lane-1 license checks (Steam rate-limited the web arm).
3. **SW sea-monster art pass** — with the owner (SW_SEA_MONSTERS_ART_1);
   normalization Law 3/Law 4 apply from birth (born at the right bodySize,
   the right lethality, the right hide).
4. The Depths v1 slice builds only after 2 and 3 exist to feed it.
