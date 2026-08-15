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
- [ ] **DLCs active:** ALL official DLC is present and enabled (standing build assumption — design never gates on "if DLC X present"). Royalty ✅(techprint gate), Ideology ✅(Jawa ideoligion + Scavenger role), Biotech ✅(Jawa genes + native pollution/wastepack mechanics), Odyssey ✅(gravship layer) all ENABLED. Anomaly OWNED and enabled but its **content is set to ZERO** — owner's ruling 2026-08-13, no longer "OFF/minimal" and no longer conditional. Not uninstalled: the DLC stays enabled so its **assets remain available to us**. See the carve-out at the Anomaly intensity row below.
- [ ] **Mod list finalized in RimSort** and load-ordered (RimSort handles ordering — no manual diff).
- [ ] **Frameworks present & 1.6-current:** Harmony, VEF Core, HAR, JecsTools Unofficial 1.6,
  neronix17.toolbox (Outer Rim), EBSG (if KotOR armor), Prepatcher (CAI-5000 dep). Verify each
  shows 1.6 in RimSort before first launch.
- [ ] **Compat mod present & loads LAST:** `mandrake.jawa.patches` (folder
  `src/Jawa/Jawa_Patches/`) — home for our TraderKind buy-filter widen + any authored patches.
- [ ] **Red-error check:** boot once to a menu with full list; resolve any red errors (esp. Outland
  Genetics presence — the Jawa def hard-references its genes) BEFORE worldgen.
- [~] **RimBridgeServer** installed only when we're ready to drive live-map enrichment (Tier 2b).
  Not required for the initial start. (See `rimbridge.md`.)

## 1. Storyteller & difficulty
- [x] **Storyteller: RANDY RANDOM** (Claude's pick, delegated by user 2026-08-08). Rationale: the
  campaign is an *unpredictable nomad/escape arc*, not a legible base-builder — Randy's un-curated
  event mix matches "keep moving, react to what the galaxy throws at you," and it pairs correctly with
  the Custom "fewer, heavier, smarter" raid distribution (§1 difficulty) so severity stays controlled
  even while *timing* is chaotic. Cassandra's rising-tension curve assumes a settled base to escalate
  against, which fights the premise. (Phoebe rejected — too gentle for the pursued-by-Empire stakes.)
  Reversible in-game if Randy's variance feels too swingy in playtest.
- [~] **Difficulty = Custom** (DECIDED in principle, `world_interest_and_mech_danger.md`/context §19.9):
  the "fewer, heavier, smarter" enemy distribution starts here BEFORE any mod — lower raid
  *frequency*, raise raid *points*, disable enemy flee%, disable adaptation-difficulty decay. Set
  exact sliders at the machine.
- [x] **Commitment (permadeath) mode:** **OFF — reload allowed** (user, 2026-08-04).
- [ ] 🔴 **Anomaly/monolith intensity: ZERO.** Owner's ruling 2026-08-13, and it is
  settled — not "off/minimal", not a preference to revisit at the settings screen.
  **The Anomaly narrative does not run in this campaign.**

  ⭐ **The carve-out, and it is the reason the DLC stays enabled:** its **creatures
  and abilities are ours to reskin and reuse for our own purposes.** Zeroing the
  content switches off the *storyline* — the monolith, the entity events, the
  Forsaken arc — and does nothing to the defs. A reskinned Anomaly creature dropped
  into our own content is unaffected by this setting and is explicitly permitted.

  ⇒ **Never read "Anomaly is at zero" as "Anomaly assets are off-limits."** They are
  a def library we own and have paid for. What is switched off is the DLC telling
  its own story on top of ours.

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
- [~] **Body-size spectrum:** small end covered by the Jawa's `Outland_BodyScale_Small`. **Size
  authority = LARGE PAWNS `3777700657` (already adopted); do NOT also run Big-and-Small (Claude's
  recommendation, user 2026-08-08 — see reasoning below). [ ] Confirm at machine.**
  - **Advice (recommendation, not established fact): keep Large Pawns, skip Big-and-Small.**
    - **Big-and-Small (RedMattis)** is a *deep framework*: a full gene/size system (arbitrary body
      scales, size-linked stats, riding, food/space scaling, tons of dependent content). Powerful, but
      it's a heavy framework other mods hook into — and it directly overlaps our Jawa `Outland_BodyScale_Small`
      gene and the "genetics stays FIXED / no gene-tinkering" anti-exp rule (§3). Adopting it invites a
      second size *system* competing with the Outland genes for authority = exactly the "pick ONE size
      authority" conflict already flagged in required_mods batch-2.
    - **Large Pawns** is *narrow*: it makes certain pawns visually/mechanically bigger. It gives us the
      one thing we actually want — a size *contrast* on the roster (a big Gamorrean/Wookiee-kin towering
      over the little Jawa) — without importing a whole gene framework or fighting the fixed-genetics rule.
    - **Net:** the campaign needs *visual/stat size contrast*, not a size-genetics sandbox. Large Pawns
      delivers the contrast at a fraction of the complexity and dependency surface. Only revisit
      Big-and-Small if a later must-have mod hard-depends on it. **⚠️ Watch:** don't co-run them — two
      size authorities double-scale pawns.
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
    permanent darkness, needs Caveworld Flora) / Biomes! Caverns (WS 2969748433) / the Odyssey
    **Glowforest** perma-dark surface biome. Verify supportedVersions shows 1.6 in RimSort before adopting.
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
- [~] **Weapons:** Outer Rim mid/high flavor over a vanilla low-tech floor; do NOT amputate vanilla
  weapons (§19.5 audit GREEN — SW guns are charge-tier reskins, not power creep). **The VWE-Makeshift
  junk tier is deprecated for v1** — bullet guns, and v1's weapons are blasters. DECIDED.
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

## 13. In-Game Verification (throwaway dev-world, before the real save)

*Merged from the retired `in_game_verification_checklist.md` (2026-08-06). How to use: subscribe the candidate mods → boot a throwaway dev world → enable Development mode → run these checks → NEVER run an unverified mod on the real seed save first. The DUPLICATE items already tracked in the §-sections above and the 🔎 snapshot are not repeated here; these are the unique at-the-machine tests.*

- [ ] **CAI-5000 LoadFolders sanity check.** CAI-5000's `LoadFolders.xml` maps only a `v1.4` block even though About.xml declares 1.6 (a fallback-load pattern) — almost certainly fine, but worth a glance. Load with CAI-5000 active, confirm no "content not loading for 1.6" warnings in the log, and confirm CAI behavior actually engages in a spawned fight (mechs/raiders use cover + flank). If behavior engages, the fallback-load is working.

- [ ] **Odyssey surface-biome enumeration** (feeds `biome_terrain_palette.md` A1/A6). In Development mode open the biome list (or check `BiomeDef`s) and capture defNames for the 5 Odyssey surface biomes: glowforest, lava fields, toxic scarlands + the 2 unnamed ones → fill the defName columns in the palette.

- [ ] **Toxic terrain-souring source** (the §4 rogue-android water-poisoning / terrain-souring tool, design §3(c)). STE's About.xml couldn't be read (Steam 429'd every fetch); 1.6 is inferred from a translation mirror only.
  - If subscribing **Sustainable Toxic Environment (WS 3254886145)**, confirm its own supportedVersions shows **1.6** in RimSort and it loads clean — the direct evidence the mirror-inference stands in for.
  - **Test the zero-mod path first:** generate an Odyssey **toxic scarlands** tile and check whether its native polluted terrain + toxic buildup can carry the "fouled ground / poisoned water on an android holding" role with no mod at all. Also check Advanced Biomes' `PoisonSoil`/`PoisonMud`/`NuclearWaste` floors. If either works, STE is optional.
  - Guardrail: whatever's adopted, confirm there is **no player-facing recipe/ability** that turns it into a usable poisoning tool — enemy-side terrain-shaping only.

- [ ] **Standing pattern for any Workshop-only mod** (no auditable source → judge in-game). For **Mechanoids: Total Warfare (3555799437)**, **Tribbles! Continued (2672501251)**, **Mini Gravships Lite (3538850569)**, on the throwaway world: confirm the **1.6** version tag + clean load (no red errors); **Tribbles** — confirm they function as a threat/infestation and are **NOT ranchable** (no breeding-for-resources loop; if they can be penned + bred, Cherry-Pick or leave wild-only); **Mini Gravships Lite** — confirm it **coexists with VGE** (does not redefine gravship structures/engine) before anywhere near the real save. *(GravTech 3545374124 is already in `forbidden_mods.md` — no test needed, it's out.)*

- [ ] **Native Odyssey sandstorms** (the sea-of-desert ④-threat weather; native content would make a weather mod / the extracted SW-Biomes weather unnecessary). On a desert / ExtremeDesert dev tile, use Development mode ("make weather"/incident tools) to trigger every weather def; enumerate sand/dust/haze types + read effects (visibility, accuracy, movement, temperature). **Decision rule:** if native sandstorms carry the role, mark the extracted SW-Biomes weather + any weather-mod candidate OPTIONAL/redundant in `required_mods.md` + `biome_terrain_palette.md`; if not, keep the extracted weather path.

- [ ] **Odyssey Landmarks — enumerate which types generate** (the two-tier set-piece model, context.md 2026-08-05: native Landmarks generate the tile *type*, then Ancient Urban Ruins/CQF/the bridge author the content). Open the `LandmarkDef` list (Development mode def inspector, or generate several worlds and inspect) and enumerate every Landmark type that actually generates, with defName + which biomes/terrains weight it + commonality (so Tier-2 pacing ~every 2-3 tiles can be tuned against real spawn rates — feeds the deferred arc-closing-rate playtest). Cross-check against `sw_Sarlacc` and any other mod-added `LandmarkDef`s so authored beats don't collide.

- [ ] **⭐ Faction Territories & Vassalage — the conditional accept audit** (HIGH PRIORITY; F&T WS 3626725895 is FULL ACCEPT but *conditional on this in-game check* — it's additive flavor, not the pursuit spine, so **cut-on-sight if TPS suffers**). Details in the `required_mods.md` Faction Territories entry.
  - **Dependency:** subscribe **Map Mode Framework** (F&T's listed "Required item") + Harmony. Confirm F&T shows the **1.6** tag and loads with no red errors on splash / in Player.log. Without Map Mode Framework it won't run.
  - **Vassals OFF posture:** in F&T settings, **disable the vassal system** before testing (recent comments call it buggy + "too OP"; author appears inactive). Confirm the setting exists and sticks.
  - **Coverage guardrail:** a user report says >~30% world coverage breaks the mod. Confirm our small-world scenario keeps planet coverage well under that; note the actual coverage % we generate at.
  - **TPS/lag test (decisive):** run a throwaway world with our roster at 3× for several in-game days; watch for the reported "severe lag spikes every couple of seconds" + repeating F&T exceptions in the log. **Decision rule: if TPS degrades or the log spams F&T errors, cut it** — not load-bearing.
  - **Territory behavior sanity:** confirm territory regions draw around faction settlements and in-turf ambush/patrol density rises inside a faction's ground. Watch for reported bugs (friendly troops loitering on the player map eating food / fighting each other; wrong-tech-tier bases spawning during map-gen).
  - **§19.5 in-turf ambush audit** (no public source to read): confirm in-turf ambush raises **qualitative** threat (better-positioned/more-coordinated attackers on held ground), NOT inflated raid points. Tune per-faction ambush/caravan density so Imperial turf bites hardest on Empire-held tiles; keep the *primary* pursuit timer on the orbital model, not on territory.

- [ ] **⭐ Relationship-complexity stack — install-time load + version audit** (ADOPTED; `required_mods.md` "Relationship-complexity stack" §, `jawa_xenotype_and_religion.md` §4.3b). The stack = **Way Better Romance** (backbone) + **Romance On The Rim** + **Intimacy - Friends n' Lovers** (+Gender Works) bridged by **Romance & Intimacy On The Rim (R_IOTR)** + More Slavery Stuff (already in stack).
  - **1.6 tags:** WayBetterRomance (`divineDerivative.Romance`) + R_IOTR (`mianreplicate.romanceandintimacyontherim`) are **About.xml-confirmed 1.6** (no re-check needed). **Confirm in RimSort that these still show 1.6:** Romance On The Rim (WS `2654432921`), Intimacy - Friends n' Lovers (WS `3498422643`), Intimacy - Gender Works (WS `3534254491`, needs Biotech), Polyamory Beds (WS `3276496684`) — all four had their Steam pages 429'd during verification, so their 1.6 tag is store-text-only until seen in RimSort.
  - **No double romance-overhaul:** WayBetterRomance's About.xml lists Rational Romance / Psychology / Everyone Is Queer / Open Polyamory etc. as incompatible — confirm none of those are also active. (Open Polyamory is already rejected: it deletes jealousy AND is 1.2-only.)
  - **Load order:** R_IOTR after both Romance On The Rim and Intimacy (it bridges them); WayBetterRomance per its own guidance. Confirm no red errors on splash / in Player.log.
  - **Jealousy-slider tuning (the design intent):** in WayBetterRomance settings, set the cheating/jealousy opinion slider to "turbulent but playable" — jealousy stays ON (the chosen chaos), not deleted. Note the value used.
- [ ] **Plant Speed Modifier — growth-speed audit** (ADOPTED candidate for the §3(f) global-overgrowth mechanic; WS `3660866466`). Confirm in RimSort it shows **1.6** (Steam 429'd — store-text only so far) AND test in the dev world that its slider affects **wild** plants, not crops-only. If it fails either, fall back to `Mersid/Rimworld_FastPlantGrowth` (GitHub) or the own-Harmony `Plant.GrowthRate` route (desert_world_design §3(f) route 2).

- [ ] **Source-audit provenance notes** (reference facts, relocated here so they aren't lost): NWN Real Fog-of-War is 1.6-capable despite a stale About.xml; CaveBiome + Biomes! source-pull status; STE 1.6 inferred from a translation mirror only; Cherry Picker cull lists still to be finalized in-game. Cross-reference the fuller notes in `required_mods.md` where they exist.

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
  hidden-bypass check; Cherry Picker cull lists; CAI × Total Warfare compat; romance stack RimSort 1.6 tags (RotR/Intimacy/Polyamory Beds) + WBR jealousy-slider tuning; Plant Speed Modifier 1.6 + wild-plant scope.
- **Newly decided (2026-08-07):** relationship-complexity stack ADOPTED (WayBetterRomance backbone +
  R_IOTR bridge, both 1.6-confirmed; RotR + Intimacy depth; jealousy ON; Open Polyamory rejected).
