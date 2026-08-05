# setup_checklist.md — Game Setup Decision Checklist (work through live)

_Gravship Expedition campaign · RimWorld **1.6 + Odyssey** · "Crashed Factory ship / Jawa
stowaways" theme. This is the **live checklist** we walk through before generating the first
save. Check items off as they're settled. Governed by the anti-exponential principle
(gravship + VFE-Factory are the ONLY scalable progression trees) and §19.5 (no arms race)._

**Started:** 2026-08-04. **How to use:** each item is `[ ]` open / `[x]` decided / `[~]`
decided-but-verify-in-game. A **DECIDED** line records the choice + where it's authored; an
**OPEN** line is a decision still to make together. Sources of truth referenced: `required_mods.md`
(mod stack), `forbidden_mods.md` (anathema), `jawa_xenotype_and_religion.md` (xeno + ideoligion),
`world_interest_and_mech_danger.md` (threats/biome interest), `save_authoring_pipeline.md`
(how the start gets built), `Custom_World.md` (director-mod toolkit), `desert_world_design.md`
(consequential-landing risk/reward per terrain — the "why land here?" design layer).

> **Delivery reminder:** the campaign start is authored as a **starting SAVE**, not a portable
> scenario def (decided 2026-08-03). Tier 1 = I author defs/patches (~80%); Tier 2 = surgical
> save-edits of legible nodes; Tier 3 = the irreducible in-game steps you do (subscribe → load →
> worldgen → embark → save). Many checklist items below are Tier 3 "do at the machine" choices.

---

## 0. Pre-flight: environment & mod load
- [ ] **DLCs active:** ALL official DLC is present and enabled (standing build assumption — design never gates on "if DLC X present"). Royalty ✅(techprint gate), Ideology ✅(Jawa ideoligion + Scavenger role), Biotech ✅(Jawa genes + native pollution/wastepack mechanics), Odyssey ✅(gravship layer) all ENABLED. Anomaly OWNED and enabled but **content set OFF/minimal** (benched — not fun to user), not uninstalled — this is a deliberate content-tuning choice, not a DLC-absence.
- [ ] **Mod list finalized in RimSort** and load-ordered (RimSort handles ordering — no manual diff).
- [ ] **Frameworks present & 1.6-current:** Harmony, VEF Core, HAR, JecsTools Unofficial 1.6,
  neronix17.toolbox (Outer Rim), EBSG (if KotOR armor), Prepatcher (CAI-5000 dep). Verify each
  shows 1.6 in RimSort before first launch.
- [ ] **Compat mod present & loads LAST:** `mandrake.gravship.compat` (folder
  `custom_patches/GravshipCompat/`) — home for our TraderKind buy-filter widen + any authored patches.
- [ ] **Red-error check:** boot once to a menu with full list; resolve any red errors (esp. Outland
  Genetics presence — the Jawa def hard-references its genes) BEFORE worldgen.
- [~] **RimBridgeServer** installed only when we're ready to drive live-map enrichment (Tier 2b via
  RimMaster). Not required for the initial start. (See `rimbridge.md`.)

## 1. Storyteller & difficulty
- [ ] **Storyteller:** OPEN. Leaning Randy vs Cassandra — Randy suits an unpredictable nomad run;
  Cassandra gives a legible escalation curve. Decide together.
- [~] **Difficulty = Custom** (DECIDED in principle, `world_interest_and_mech_danger.md`/context §19.9):
  the "fewer, heavier, smarter" enemy distribution starts here BEFORE any mod — lower raid
  *frequency*, raise raid *points*, disable enemy flee%, disable adaptation-difficulty decay. Set
  exact sliders at the machine.
- [x] **Commitment (permadeath) mode:** **OFF — reload allowed** (user, 2026-08-04).
- [ ] **Anomaly/monolith intensity:** set to OFF/minimal (per DLC decision).

## 2. Ideology (Jawa ideoligion) — mostly authored, confirm in creator
- [~] **Fixed ideology** (no fluid development) — DECIDED (`forbidden_mods.md`).
- [~] **Ideoligion:** "The Articles of Passage" / in-fiction "Keepers of the Second Hand".
  **Memes: Nomad (primary) + Tunneler (secondary)** — DECIDED (`jawa_xenotype_and_religion.md` §2.6).
  - [x] Final call: **Nomad primary** + Tunneler secondary (user, 2026-08-04).
- [~] **Roles (two, non-multiplying):** Leader = Chief/Captain (self-limit its production-buff
  ability); Moral Guide = "Keeper of the Articles". DECIDED. No Production/Combat specialist roles.
- [~] **Scavenger role:** Ideology Scavenger Role (WS 3565039115) adopted — restrictive identity,
  not a multiplier. [ ] In-game: read its granted travel/grave-rob abilities for any hidden labor bypass.
- [~] **Precepts:** ruins-as-pilgrimage; trade permissive/celebrated; ration-as-sacred (nutrition
  paste acceptable + low expectations); organic cannibalism abhorrent / droid-salvage free; hooded
  apparel desired (`OuterRim_DesertGarb`/`_DesertHood`/`_Cloak`/`_Hood`); "repair the discarded,
  don't mass-produce new hands". DECIDED — set in the Ideology creator.
- [~] **Rituals (cohesion only, no material payouts):** The Reckoning (salvage/launch rite),
  machine-retirement funeral, leader speeches. DECIDED.
- [~] **Relic:** exactly ONE, modest — "The First Fusioncutter". DECIDED.

## 3. Races & xenotypes
- [~] **Player crew xenotype = Jawa (`OuterRim_Jawa`)** from Outer Rim Galactic Diversity 1.6 —
  adopt unchanged (DECIDED, `jawa_xenotype_and_religion.md`). [ ] Verify genes resolve clean in a
  dev world (esp. the 3 `Outland_*` genes — magnitudes are inferred until installed).
- [~] **Genetics stays FIXED** — no gene extractors/assemblers/xenogerms/breeding-for-genes
  (anti-exponential). DECIDED.
- [~] **Reflavored vanilla xenotypes KEPT as SW species:** Yttakin→Wookiee-kin, Pigskin→Gamorrean,
  Genie→savant, Neanderthal→brute merc, Impid→desert alien (labels/RP only). DECIDED.
- [~] **Body-size spectrum:** small end covered by the Jawa's `Outland_BodyScale_Small`. [ ] Decide
  whether to add a dedicated large/small race + body-size-gene mod (Big and Small / RedMattis) for
  the full spectrum, or leave as-is.
- [ ] **Cherry Picker xenotype cull:** confirm the kill-list (Sanguophage + fantasy/wrong-universe
  races) against installed defs before deleting (`cherry_picker_killlist.md` §2, all 🔎 in-game).
- [~] **SW beasts / creature layer:** Alpha Animals is the adopted baseline (qualitative wildlife
  danger). SW-specific fauna (bantha/dewback/tauntaun) 🔎 **pending Fetcher** (`2026-08-04_starwars_beasts_terrain`);
  zero-risk fallback = label-only reskin of a fitting Alpha Animal. Guardrail: no fast-breeding
  ranchable meat/leather/milk animal (exponential printer). See `desert_world_design.md` §2–3.

## 4. Factions
- [~] **Empire fusion:** vanilla Royalty Empire (aristocratic core) + Outer Rim Galactic Empire
  (military) = ONE unified Empire; titles reskinned to Imperial ranks (labels only, non-progression
  for player). DECIDED.
- [~] **Antagonist = the Empire pursues the Jawas.** Mechanism (recommended B): Empire as a
  permanently-hostile LIVE faction (Outer Rim Empire + VFE-Deserters) with escalating raids/quests —
  NOT the hardcoded `ScenPart_PursuingMechanoids` (no config toggle to swap the pursuer). DECIDED.
  [ ] Decide whether to also de-emphasize/disable vanilla pursuing-mechanoids at scenario setup.
- [ ] **Faction roster / counts at worldgen:** OPEN — how many of each hostile/neutral/trader
  faction to seed. Use Sensible Factions / Faction Filter to control spawns (Streamer method).
- [ ] **Trader-faction density:** high (Jawa "trade a lot") — ensure enough trading factions are
  seeded so caravans/orbital traders are frequent. (Trader *behavior* mods in §9.)

## 5. World map generation (Tier 3, at the machine)
- [ ] **Planet coverage / world size:** OPEN — pick coverage %. (Nomad run wants enough tiles to
  keep moving; balance against gen time.)
- [ ] **World seed:** OPEN — generate a few, use **Map Preview** (WS 2800857642) to shortlist.
- [ ] **Rainfall/temperature/population world sliders:** OPEN.
- [~] **World-map fog-of-war:** RimWorld Exploration Mode (WS 2941608795) adopted — discover tiles
  gradually. DECIDED (`required_mods.md`).
- [~] **Landform variety:** Geological Landforms + Biome Transitions + Vanilla Landmarks Expanded
  adopted (each landing feels distinct). DECIDED.

## 6. Landing site / terrain & biome (Tier 3)
- [~] **DESIGN INTENT — consequential landing (four-axis schema):** every terrain must define exactly
  four axes — **① Abundant** (surplus you come for) + **② Scarce/missing** (denied → creates the next
  need) + **③ Exotic** (rare located wealth to covet/trade) + **④ Major threat** (qualitative §19
  danger that also times your exit) — so landing is need-driven, not tourism. Full framework +
  per-terrain table in **`desert_world_design.md`** §2/§2A (deep desert=salvage/no-water,
  oasis=water/raid-magnet, volcanic=components/eruptions, coast=biomass/killer-plants, river=
  fertile-corridor/everyone-uses-it, salt-flat=build-pad/zero-sustain). DECIDED as the design north
  star (user, 2026-08-04; Draw/Toll/Exit framing retired in favor of the four axes 2026-08-04).
  [ ] Author the resource-distribution scheme (Map Designer per-biome ore/ruins) — buildable NOW,
  needs no external mod.
- [~] **Consequence mechanics (threat axis ④):** water-thirst, heat/sandstorm, dynamic dangerous vegetation,
  volcanic hazards. 🔎 **pending Fetcher** (`2026-08-04_desert_world_terrain_factions`) for 1.6 mods;
  AUTHOR/RimBridge fallback if no clean mod. Guardrail: never pair thirst with a free-water building.
- [ ] **Starting biome:** OPEN. Theme leans **desert/arid** (Tatooine/Jawa fit, `MaxTemp` gene,
  water-scarcity narrative). Confirm the first landing biome + tile.
- [~] **Biome interest tooling:** Choose Biome Commonality + Map Designer to tune scarcity/variety
  profile (no new mod needed). Alpha Biomes adds ~10 alien biomes alongside the grounded strand.
  DECIDED as available; [ ] set commonality so landings aren't samey/cluttered.
- [~] **Desert terrain flavor:** terrain *quantity* already solved by the stack; gap is desert
  *density* (sand/salt/hardpan variants). A cosmetic floor-type mod is balance-neutral — adopt if
  1.6-confirmed (🔎 Fetcher). Guardrail: reject farmable-anywhere / passive-resource terrain.
- [ ] **Map size:** OPEN.
- [ ] **Terrain features to expect/allow:** ore/geysers via worldgen; saber-crystal deposits only
  if explicitly in scope (containment — see §8).
- [~] **Low-visibility layer — dark biomes + fog of war (DESIGN ADOPTED, `desert_world_design.md` §3(e)):**
  a rare "vision is the scarce resource" strand — perpetual-dark biomes + a line-of-sight fog that hides
  threats until a colonist sees them. Pillar-clean (info/environment-side, no buildable/economy).
  Route = MOD, ≈ zero new dependency; no AUTHOR fallback needed. **Three in-game checks before locking:**
  - [ ] **(1) Fog-of-war source — DON'T run two.** CAI-5000 (already in the stack for smart raid AI)
    BUNDLES its own fog of war → likely gets the LOS-fog layer FREE with AI built to path through it.
    Decision: enable CAI-5000's built-in FoW and confirm it behaves, **OR** disable it and use
    **(NWN) Real Fog of War Continued** (WS 3391128917) instead — but never both at once. NWN's edge:
    symmetric FoV (players + AI + animals + mechs all have LOS, so it doesn't blind only the player) and
    FoV shrinks with the Sight stat + **darkness** + weather (stacks with dark biomes + our SW sandstorm/
    red-fog weather → near-blind for everyone in a dark storm). Pick one; shake down in-game.
  - [ ] **(2) Confirm a 1.6 dark-biome mod.** Candidates: **CaveBiome** (emipa606, appears 1.6-live,
    permanent darkness, needs Caveworld Flora) / Biomes! Caverns (WS 2969748433) / vanilla **Glowforge**
    perma-night biome. Verify supportedVersions shows 1.6 in RimSort before adopting.
  - [ ] **(3) Ocular Forest low-light check.** `AB_OcularForest` is already in the stack and confirmed
    weird/transdimensional, but NOT confirmed to impose low light — verify in-game whether it actually
    darkens the map (if yes, it doubles as a dark biome; if no, it's just flavor).
  - [ ] **Commonality discipline:** keep dark biomes RARE (same scarcity rule as the other alien biomes —
    if they're everywhere the tension collapses). Set commonality low in Choose Biome Commonality/Map Designer.

## 7. Scenario (authored into the starting save)
- [~] **Arrival method = Gravship** (`ScenPart_PlayerPawnsArriveMethod` = Gravship). DECIDED.
- [~] **Starting crew = 3 Jawa** (matches the Gravtasm teardown model; pawn story/traits/skills
  hand-tuned via Tier-2 save-edit). DECIDED — final backstories/skills to author.
  - [ ] Draft the 3 Jawa personas (Backstory + skills + passions) — pillar-fit, no min-maxing.
- [~] **Starting industrial state:** ONE inherited provisioning line (conveyor oven + minimal
  hoppers/conveyors) the crew can operate but not replace (VFE_BasicFactories locked). DECIDED
  (`required_mods.md`). [ ] Decide oven vs automated-smelter start (survival- vs salvage-dependence).
- [ ] **Starting research:** OPEN — set `ScenPart_StartingResearch` (keep minimal; progression is
  quest-gated).
- [ ] **Starting things/resources & counts:** OPEN — author `ScenPart_StartingThing_Defined` counts.
- [ ] **Intro text** (`ScenPart_GameStartDialog`): write the crashed-Factory-ship premise.
- [~] **Cherry Picker may delete ALL vanilla scenarios** (save-based delivery, no base to preserve).
  DECIDED — confirm before culling.

## 8. Progression gates & containment (pillar enforcement)
- [~] **Techprint gate:** Configurable Techprints (WS 2876747024, needs Royalty) gates
  `VFE_BasicFactories` / `VFE_ComplexFactories` / Odyssey Advanced Gravtech as quest-only. DECIDED
  (Phase-A prototype). [ ] Verify none of those research defNames END IN A DIGIT (engine limit) —
  if one does, that gate needs the custom XML mod instead.
- [~] **Fuel leash:** VGE's native chemfuel→astrofuel refine (70→35, 5000 work, gated BasicGravtech)
  already throttles jumps; custom throttle patch likely redundant. DECIDED — tune in Phase-A playtest.
- [~] **Lightsabers = quest-earned ONLY**, craft recipe disabled (containment; `CompDeflector`
  arms-race vector). DECIDED. [ ] Cherry-Pick the saber craft recipe to enforce.
- [~] **Droid Depot self-limited:** DroidBrain treated as rare/salvage-gated + built droids
  draft-locked out of work queue (no droid economy). DECIDED.
- [~] **Weapons:** keep vanilla low-tech + Outer Rim mid/high flavor + VWE-Makeshift junk tier; do
  NOT amputate vanilla weapons (§19.5 audit GREEN — SW guns are charge-tier reskins, not power
  creep). DECIDED.
- [~] **No-durability-loss** via No Durability (WS 3260461453); recycling via VFE-Factory's
  Automated Smelter (no standalone recycler). DECIDED.

## 9. Trader behavior
- [~] **Keep trader FREQUENCY high** (Jawa trade a lot) + heterogeneous/unreliable stock + universal
  buyers. Mechanisms: Trading Options, MultipleTraders (everything-buyer kind), Tech Level
  Enforcement/WorldTechLevel filter, + our own TraderKindDef buy-filter widen in the compat mod.
  DECIDED (`required_mods.md`). [ ] Author the buy-filter patch; confirm tech-tier filter settings.

## 10. Threats & world interest (mostly mod-config, set at difficulty/worldgen)
- [~] **Smarter AI:** CAI-5000 (Krkr.rule56; deps Harmony+Prepatcher; CE only a loadAfter, safe).
  DECIDED first layer. [ ] **Note:** CAI-5000 also bundles a fog-of-war feature — the enable/disable
  decision (CAI's built-in FoW vs NWN Real Fog of War, never both) lives in §6's low-visibility layer.
- [~] **Qualitative mech/threat roster:** Reinforced Mechanoids 2 (enemy-side only, leave Gestalt
  unresearched), Mechanoids: Total Warfare (compat-test vs CAI first), Odyssey Mech Raid Adjustment
  (pursuit cadence dial), Vanilla Events Expanded, Alpha Animals (Cherry-Pick the ranch-able breeder),
  More Dangerous Game. DECIDED as adopted. [ ] Run the CAI × Total Warfare throwaway-world compat test.
- [~] **No raid-point inflation / no player mech ladder** (§19.5): Dire Raids, MultipleRaids,
  MoreMechanoidsWorkModes excluded. DECIDED (`forbidden_mods.md`).

## 11. Storage / hauling / UI (adopt freely — no balance impact)
- [~] Storage: LWM's Deep Storage + Adaptive Storage Framework + RimFridge (pick one fork). Storage
  footprint cap concept accepted, exact ratio TBD. DECIDED-ish. [ ] Set the storage-ratio cap value.
- [~] Hauling/teardown: Pick Up And Haul (fork) + Common Sense (fork) + Allow Tool. DECIDED.
- [~] UI/QoL: Dubs Mint Menus, RimHUD, Numbers, Interaction Bubbles, Camera+, Replace Stuff,
  Quality Builder, Map Preview. DECIDED (cosmetic/convenience — the invariant foundation layer).

## 12. Final pre-generation gate
- [ ] All §1–§7 OPEN items resolved (or consciously deferred to Phase-A playtest).
- [ ] Dev-world smoke test: boot a throwaway world, confirm Jawa xenotype + ideoligion + factions
  resolve with no red errors; spot-check a few key defNames against the ACTUALLY-loaded 1.6 folders.
- [ ] Backup discipline ready for the Tier-2 save-edit pass (timestamped backup → edit →
  parse-validate → reload-test).
- [ ] Then: Tier-3 in-game steps (subscribe → load → worldgen → embark → save) → produce the seed
  save we polish.

---

### Decision-status snapshot (for the "where are we" glance)
- **Largely locked (author/verify):** DLCs, gravship layer (VGE sole), industrial core (VFE-Factory),
  Jawa xenotype, ideoligion memes/roles/precepts/relic, Empire fusion + antagonist mechanism,
  weapons stance, durability/recycling, trader behavior, threat roster, storage/hauling/UI stack.
- **Still OPEN to decide together:** storyteller pick;
  full-body-size race mod yes/no; faction roster counts; planet coverage/seed/world sliders;
  starting biome + map size; starting research + starting things/counts; oven-vs-smelter start;
  storage-ratio cap value; the 3 Jawa personas.
- **Newly decided (2026-08-04):** permadeath OFF (reload allowed); ideoligion memes = Nomad primary
  + Tunneler secondary.
- **Verify-in-game (🔎):** Outland gene magnitudes; techprint-defName-digit check; Scavenger role
  hidden-bypass check; Cherry Picker cull lists; CAI × Total Warfare compat.
