<!-- status: live -->
> ## 🔴 CORRECTION 2026-08-20 — "VPE IS KEPT INSTALLED" IS NOT TRUE OF THE LIVE MOD LIST
> `ModsConfig.xml` parsed as XML holds **578 `activeMods` as of 2026-08-20** and **none** matches
> `vpsy` or `psycast`. **`VanillaExpanded.VPsycastsE` is not active.** It is subscribed and on disk
> (`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2842502659`) with all three
> dependencies active (Royalty, Harmony, VEF Core); nothing forced it out and **no doc records a
> decision to drop it**. The 2026-08-06 ruling was written and never executed.
>
> **What this does and does not change:** the *rule* in the "Player psycasting — NO" entry below is
> **unaffected** — the player-side ban stands on its own. What is wrong is the parenthetical claim of
> **state**: the ENEMY-SIDE EXCEPTION describes a substrate that is not loaded, so THE FORCE has **no
> mechanism in the running game today**.
>
> 🔴 **Re-activating VPE is the OWNER's decision and he has not made it.** He owns the mod list.
> This is a finding, not an agreement and not an action. Full detail and the measurement live at the
> top of `design/Jawa/mods/required_mods.md`.
> "Faction Filter" never existed; the live equivalents are **Sensible Factions** (3531306011) and **Faction Control** (2882785581).

# Forbidden Mods — Gravship Expedition Campaign

_Anathema list. Mods (and whole categories) that break the campaign's design pillars: mobility, scarcity, exploration, hard logistical choices, deciding what to leave behind. Each entry names the pillar it violates so future judgment calls stay principled._

**Litmus test:** Does the mod change what is *physically possible* (capacity, automation, permanence) rather than merely how pleasant the game is to operate? If it raises the CEILING, it's a candidate for this list. If it only improves the interface, it belongs in `required_mods.md` instead.

**Mod COUNT is not the constraint — the capability CEILING is (clarified 2026-08-02, user's call).** The campaign will run a LARGE mod library — the user likes a lot of flavor, QoL, graphics, sound, UI, and cosmetic-content mods, and that is fully endorsed. The anti-exponential principle governs *scalable progression trees*, not the number of mods installed. A mod that adds textures, animations, UI panels, décor, ambient sound, alternate hairstyles, more plant/rock variety, or interface convenience does NOT create a competing exponential economy and is welcome in any quantity. This is exactly the "invariant foundation layer" that crafted-world builders freeze under every theme (see `Custom_World.md`). What stays constrained is unchanged: mods that add a parallel progression/optimization ladder, raise the automation/capacity/permanence ceiling, or trivialize scarcity/fuel/mobility. Judge each mod on the 7-question test below — pure flavor/QoL/graphics pass trivially; only ceiling-raisers get scrutiny.

---

## Storage — infinite / pocket-dimension density

- **Deep Storage Unit / quantum storage / networked-infinite storage / pocket-dimension containers** — any mod where one tile holds effectively unlimited items ("the dimensional vortex in a cabinet").
  - **Violates:** scarcity; deciding what to leave behind. Deletes the core "what do we abandon before launch?" decision. Note the distinction from LWM's Deep Storage, which is allowed *because* it's capped by ship floor-area, not made infinite per-tile.

---

## Anything that makes staying permanently optimal

_(Category guard — the campaign's prime directive is "movement should solve problems." If staying forever is ever optimal, the gravship is irrelevant.)_

- **Auto-defense / mega-turret / killbox-enabling mods** that let a static position trivialize raids.
  - **Violates:** mobility. Original notes already ban giant static killboxes; mods that supercharge them are forbidden by extension.
- **Large-scale automation** (auto-crafters, mass drones, self-running production chains) that removes the pressure to move on for resources.
  - **Violates:** mobility, scarcity. Makes the ship a self-sufficient factory rather than a vessel that must forage.
- **Project RimFactory** (and comparable deep-logistics/automation overhauls) — excluded from the first campaign (2026-08-02).
  - **Violates:** mobility, scarcity, anti-exponential principle. Its deeper logistics/automation risk turning the campaign into a stationary factory-engineering game. **Vanilla Furniture Expanded - Factory was chosen precisely because it stops short of this** — conveyors + Basic→Complex tiers + deck-space competition WITHOUT a full self-running economy.
- **Industrial Rollers – Conveyor belts & Automation (WS 784327493)** — excluded (2026-08-03). Re-evaluated at user's request as possible *support* for going deep into VFE-Factory; declined.
  - **Violates:** anti-exponential principle (Q5 — parallel base-wide haul network trivializes hauling labor). **Can't support VFE-Factory:** VFE-Factory already ships its own native conveyor layer (surface + underground conveyors, splitter/filter, HaulFromConveyor job); Rollers keys to vanilla stockpiles with no shared input/output comp, so it can't feed or extend VFE machines — only run a disconnected parallel belt network. It's architected to pair with Project RimFactory (above). Go deep via VFE's own underground conveyors + splitter + Basic→Complex tiers instead.

---

## Anything that trivializes fuel

- **Infinite / free / trivialized gravship fuel mods.**
  - **Violates:** scarcity; the fuel "leash" that balances mechanoid pursuit. Fuel must stay a strategic resource with an emergency-launch reserve.

---

## Reward-spoiling information mods

- **Mods that reveal exact loot/reward contents of a destination before you go.**
  - **Violates:** exploration. Target info level = know WHY a place is interesting, NOT what rewards wait. (Smart Odyssey's tile-mutator info is fine — it explains *why*, not *what*.)

---

## Mods that make explorable structures cheeseable from outside

- **"Ancient Ruins All Deconstructible" / "Ancient Urban Ruins All Deconstructible"** (Workshop 3361061429 and merged variants).
  - **Violates:** exploration (Type-1 dungeon integrity). It's the direct INVERSE of what we want — makes ruin structures freely deconstructible so you can strip them from outside without entering. We are deliberately using the OPPOSITE mod (**Ancient Urban Ruins Hit Point**, which gives walls real HP) to force entry. Do NOT run both — the "All Deconstructible" mod defeats the enforcement, and combining with Hit Point causes -1 HP object bugs.

---

## Excluded player-progression systems (anti-exponential principle, 2026-08-02)

_The governing rule: **the gravship and its onboard industrial system are the campaign's ONLY scalable progression trees.** Every other RimWorld advancement system interacts multiplicatively (better research → better production → stronger fighters → more artifacts/rewards → …), and when several mature together the ship stops being the center of the campaign. These systems may still EXIST, but only as fixed backgrounds, cultural constraints, singular quest-earned exceptions, irreplaceable story assets, new vulnerabilities, or mutually-exclusive choices — never repeatable optimization economies._

**7-question evaluation test — before adding ANY mod/DLC subsystem/reward type, ask:** (1) deepen the gravship/industrial tree, or create a parallel ladder? (2) impose a dependency, or merely remove a limitation? (3) can it scale indefinitely via trade/research/breeding/crafting/repeated quests? (4) make crew composition/recruitment less important? (5) bypass fuel, deck space, expedition risk, production time, injuries, mood, or scarcity? (6) reducible to a single authored exception rather than a general system? (7) make the ship MORE important, or LESS necessary? If the answers point toward broad optionality/self-sufficiency → restrict or exclude.

- **Player psycasting — NO.** No psylink neuroformers, no psytrainers, no anima-tree linking, no royal-title advancement pursued for psylinks, no quest rewards granting psychic progression, no meditation-as-XP-leveling mods. **Note the scope: this is a *player*-side ban, not a mod-level ban of Vanilla Psycasts Expanded.** ~~VPE is KEPT installed as the NPC-only "THE FORCE" substrate~~ — **corrected 2026-08-20: VPE is NOT in the 578 active mods.** The player-side ban is unaffected and stands; the "kept installed" half is a statement of state that was never true of the live list. See the enemy-side exception below and the correction at the top of this file.
  - **Violates:** it's a flexible parallel advancement tree that bypasses exactly what the campaign preserves (positioning, fire/heat emergencies, hauling, extraction, crowd control, social difficulty, light/environment, travel logistics), and shifts the narrative center off the ship. Royalty stays installed for factions/equipment/enemies/quests; the player just doesn't use the psychic path.
  - **⭐ ENEMY-SIDE EXCEPTION — VPE IS KEPT, NPC-ONLY (finalized 2026-08-06; authoritative statement in `required_mods.md` "THE FORCE SYSTEM — FINALIZED", lines ~428–436, one-line summary at `faction_roster_v2.md` §"Global system 5"):** ~~Vanilla Psycasts Expanded stays installed as the *sole* Force substrate.~~ **⛔ NOT LIVE as of 2026-08-20 — VPE is absent from `activeMods`, so this exception currently has no substrate and grants nothing.** The design intent below is unchanged and re-reads correctly the moment the owner re-activates the mod — which is **his** call, not made. Vanilla Psycasts Expanded was ruled the *sole* Force substrate. The dark-side tree is restricted to the Empire's Sith-race elite (Empire pawnGroupMakers only, via Sensible Factions (3531306011) / Faction Control (2882785581)); a curated set also drives factionless/homestead Jedi. **Players and the Jawa faction get NO Force-acquisition path whatsoever** — which is exactly why it passes the anti-exponential 7-question test (NPC-only powers raise no player ceiling). So "no player psycasting" and "VPE installed" are both true and non-contradictory: the ban is on the player *acquiring* it, not on the mod existing.
  - **Possible future exception (NOT current ruleset):** one fixed non-scaling "Listener" character (single sensing/minor ability, no psylink levels, no new powers, quest-acquired).
- **Player genetics laboratory — NO.** No gene extractors/assemblers/processors/banks, no genepack economy, no custom xenogerms, no archite-capsule optimization, no routine genetic-upgrade purchase, no crew-optimizing breeding programs.
  - **Violates:** turns pawn weaknesses into temporary engineering defects and erases recruitment tradeoffs. Xenotypes ARE welcome — but as FIXED biology per individual/population (advantages + liabilities you must accept). Genetics may appear as story content (fixed xenotype factions, rescue/refugee quests, a burdensome-but-valuable recruit, biome-adapted populations, one irreversible late-game treatment with a major drawback).
- **Monster-fusing / animal-cloning as a PLAYER SYSTEM — NO; but the CREATURE CONTENT is welcome (Genetic Rim reframed, user 2026-08-04).** The player must not have access to hybridization/splicing/cloning **buildings, recipes, or research** — that path is an exponential *monster-printer* (fails 7-q #3 breeding/crafting scaling, #4/#7 by making the ship less central). **BUT** the mod's big hybrid creatures are legitimate threat content and MAY be spawned enemy/wild-side (dev-mode / RimBridge / save-authoring), exactly like the discoverable-only oil pump and non-buildable terrain treasures: content is fine, the player-buildable *engine* is not.
  - **Enforcement (structural, not willpower):** "I'll just not build the gene-labs myself" works but is fragile (buildings still sit in the build menu; some hybrids breed). Preferred method = **Cherry Picker out the player-facing buildings + recipes + research, keep the creature ThingDefs** → converts it from a progression tree into a pure bestiary. Plus the standard grazer guardrail: a spawned hybrid must not be tamed-and-bred into a meat/leather printer.
  - **✅ CHERRY-PICK FEASIBILITY CONFIRMED FROM SOURCE (2026-08-04). The 1.6-current mod is Vanilla Genetics Expanded (`VanillaExpanded/VanillaGeneticsExpanded`, About lists 1.4/1.5/1.6; the original `juanosarg/GeneticRim` is frozen at 1.0–1.2).** Its structure is *cleanly separable* — the player engine and the creatures live in different files with almost no cross-reference:
    - **STRIP (player engine):** 13 buildings all prefixed `GR_` in `ThingDefs_Buildings/Buildings_Production.xml` + `Buildings_MechBuildings.xml` (`GR_GenePod`, `GR_ElectroWomb`/`GR_LargeElectroWomb`, `GR_TissueGrinder`, `GR_GeneticsTinkeringTable`, `GR_GeneticExtractionTable`, `GR_GeneRecombinator`, `GR_NutrientVat`, `GR_TissueGrowingVat`, `GR_Mechahybridizer`, `GR_Mechafuse`, `GR_BiomechanicalLabBeacon`, `GR_MechahybridAntenna`); the 7 research projects in `ResearchProjectDefs/ResearchGenetic.xml` (`GR_GeneticAlteration/Engineering/Duplication/Compatibility/Mechahybridization/Research` + `GR_HybridImplantology`); and their genome/extraction recipes.
    - **KEEP (creature content, ~120 races in `ThingDefs_Races/`):** the Thrumbo-crosses (`GR_Thrumbear`, `GR_Thrumbospider`, `GR_Mechathrumbo`…), the `GR_Paragon*` apex line, `GR_FleshMonstrosity`, `GR_ArchotechCentipede`, the Boom/Muffalo/Feline/Canine/etc. hybrid families.
    - **Verified safe:** the race defs carry **no hard reference back to the lab buildings/research** (only `Races_Animal_Failures.xml` uses the mod's own `CompProperties_GeneticFailure`/`DieUnlessReset` comps, which are lab-spawn-only failure pawns — leave those out or accept they simply won't spawn without the lab; either way no load error on the keeper races).
    - **BONUS — enemy-side spawn paths already ship:** an incident **`GR_HybridRaid`** (in `Storyteller/Incidents_Map_Threats.xml`) sends hybrids as raiders, and quest sites **`GR_AbandonedLab` / `GR_BiomechanicalLab`** populate maps with roaming hybrids to fight + loot. So with the player engine stripped, the hybrids still arrive as organic threats — no dev-mode/RimBridge authoring strictly required (though those remain available for curated placement).
    - **🧬 NARRATIVE OWNER:** these hybrids and lab-ruin sites are attributed to the **Arkanian–Kaminoan Gene Consortium** (`faction_roster_v2.md` §9) — its escaped experiments and derelict facilities. The XML triggers above still fire on their own (the sites are not faction-owned in code); the ownership is lore that a save/RimBridge pass can later reinforce by staging them as Consortium escape/retrieval events.
  - **Governing distinction for the WHOLE monster roster:** wild/found/spawned giant creatures = threat (welcome — Megafauna, Alpha Animals, Star Wars Animal Collection, Jurassic-Dinos-Only, selective Anomaly, Genetic-Rim-as-bestiary); a *player-operable* breeding/fusing/cloning engine that manufactures them = ladder (banned). Reskinned beasts add no economy so they're always fine.
- **VFE-Insectoids 2 (WS `3309003431`, `OskarPotocki.VFE.Insectoid2`) — player insect-jelly/hive engine BANNED; enemy faction + creatures KEPT (Cherry-Pick list CONFIRMED FROM SOURCE, 2026-08-04, `VFE-Insectoids2-main/1.6`, supportedVersions 1.5/1.6).** Same pattern as VGE: a threat faction bundled with a player exponential engine. This audit came back the *cleanest of any so far* — the entire player economy sits in one Architect category and one 3-node research chain, so the cut is nearly surgical.
  - **STRIP — 3 research projects** (`ResearchDefs`): `VFEI2_BasicHivetech` (cost 1000, no prereq) → `VFEI2_StandardHivetech` (1000) → `VFEI2_ExoticHivetech` (2000). This linear chain gates 27 of the 30 player buildables and nothing else in the keep set — removing it alone disables almost the whole engine.
  - **STRIP — 30 player-buildable ThingDefs** (all in DesignationCategoryDef `VFEI2_Insectoids`, `Buildings_Insectoid.xml` unless noted): the jelly/creep production core — `VFEI2_JellyFarm` (bioreactor spawner: generates insect jelly from minerals+nutrition), `VFEI2_TendrilFarm` (PlantFarm), `VFEI2_Creeper` (mineral/nutrition extractor Spawner+Terraform), `VFEI2_Jellyspreader` + `VFEI2_RoyalJellyspreader` (Refuelable jelly-terrain pumps), `VFEI2_JellyMorpher` (FueledSpawner jelly→royal-jelly), `VFEI2_JellyMorpher`; the player-hive spawners `VFEI2_ArtificialBasicHive`/`ArtificialSorneHive`/`ArtificialNuchadusHive`/`ArtificialChelisHive`/`ArtificialKemianHive`/`ArtificialXanidesHive`; the buildable wild-hive variants `VFEI2_KemianHive`/`ChelisHive`/`XanidesHive`/`NuchadusHive`; the utility/decor pods `VFEI2_LargeGlowPod`/`GlowPodFormation`/`GlowPodSpire`/`StaticPod`/`FoamPod`/`HeatPod`/`DeepHeater`; `VFEI2_Hivenode`, `VFEI2_Petroglypher`, `VFEI2_Thornpod`, `VFEI2_InsectoidCocoon`; and the 3 craftable insect-spawner chunks `VFEI2_InfestedShipChunk`/`InfestedShipPart`/`InfestedShipModule` (each carries `CompProperties_InsectSpawner` — a player insect printer, these are the 3 NOT gated by research so must be cut explicitly).
  - **STRIP — 5 surgery recipes** (`RecipeDefs`): `VFEI2_AdministerSornePherocore`/`AdministerNuchadusPherocore`/`AdministerChelisPherocore`/`AdministerKemianPherocore`/`AdministerXanidesPherocore` (convert a colonist into a hive Empress via `Recipe_Administer*Pherocore` — the player command-the-swarm mechanic).
  - **KEEP — all enemy/threat content:** the insectoid FactionDef, PawnKindDefs/creature ThingDefs (`ThingDefs_Races`), natural non-buildable hives & broods, the storyteller, incidents/quests, and the enemy siege turrets `VFEI2_Vilelobber`/`VFEI2_Thornworm`/`VFEI2_Thornspitter` — **verified to carry NO `designationCategory`**, so they spawn enemy-side but never appear in the player build menu. **Verified safe:** nothing in the keep set hard-references the stripped research, so the cut is load-clean.
  - **Method + maintenance:** Cherry Picker the 3 research + 30 buildings + 5 recipes (or XML `PatchOperationRemove` by defName). **Re-audit every VFE-Insectoids 2 update** with the standing check: *enumerate all defs whose effective `designationCategory` resolves to `VFEI2_Insectoids`, plus all `VFEI2_*Hivetech` research, and diff against this list* — a new buildable would silently re-open the ladder.
  - **AVOID entirely (no Cherry-Pick worth it):** "Hive Creature-Insect" (WS `3610200843`) and "Hive Queen Brood [1.6]" (WS `3757057546`) — these mods ARE the player insect-printer with nothing separable to keep.
- **Fluid ideology — NO.** Use a FIXED ideology (the "Articles of Passage" / **Shipborn**-centered ship constitution), not fluid-ideology development.
  - **Violates:** development points + newly-added memes are another progression ladder. Ideology's job here is identity/obligation/taboo/ritual, not a stream of specialists/recruits/powers/optimized production. **No ideology production or combat specialist roles** (Captain + a moral-guide role like Keeper of the Articles are fine; avoid roles that multiply production/research/shooting/plants/animals/medical/labor). **Rituals create cohesion, not material rewards** (no ritual-generated recruits/animals/goodwill/quest sites/psylinks/artifacts). At most ONE culturally-important relic with modest mechanical value.
- **Royal permits as a progression route — NO.** No royal court aboard, no title-farming for permits, no repeated permit-based solutions, no honor farming, no throne-room escalation. The Empire stays an external faction/patron/rival/quest source.
- **Mechanitor progression — NO (current).** The ship already IS the automation system; a mech labor force = a second automation tree solving hauling/construction/mining/cleaning/farming/combat/manufacturing.
  - **Possible future exception:** ONE inherited utility mech — fixed task set, no gestation, no bandwidth expansion, no resurrection/replacement, no combat-mech army. An irreplaceable asset, not a workforce.
- **Broad transhumanist optimization — NO.** Avoid the Transhumanist meme and routine biosculpting. Ordinary prosthetics + selected bionics OK, but advanced replacements should be salvaged/quest-earned/rare/hard-to-install. The ship is not a mass-production clinic for perfect bodies.
- **Multiple independent "hero power" systems — NO.** The category guard behind all of the above.

## Real Ruins — cut for stability (2026-08-02, user's call)

- **Real Ruins** (Workshop 1552146295) — CUT. Not a design-pillar violation (it actually fits the archaeology strand well); excluded purely on **stability**: user has repeatedly hit incompletely-resolved objects and other game-breaking bugs from its remote-fetch of oversized/half-broken player bases (save bloat, load hangs).
  - **Coverage retained without it:** the grounded/salvage strand runs on authored/local content — **Ancient Urban Ruins** (+ Ancient Urban Ruins Hit Point enforcer) and **Dungeon Pack** — which carry no server-fetch risk.
  - **Resolves** the doc §4.4 "Alpha Biomes OR Real Ruins, not both" choice in favor of **Alpha Biomes** (IN).

## Randomized research / major research overhauls — avoid (2026-08-02)

- **Randomized-research and large research-overhaul mods.**
  - **Violates:** deterministic quest gates + can conflict with Configurable Techprints and the custom progression mod. The campaign needs *authored* scarcity, not another layer of random access.

## Broad frameworks that are hard to audit — not core deps (2026-08-02)

- **Custom Quest Framework** (Workshop 2978572782) — experimental only; its in-game quest editor is attractive but it's a broad framework with uncertain interaction surfaces. The small dedicated local mod is easier to audit/reproduce/remove. Do not adopt as a core dependency.
- **Microelectronics Chip Quest** (Workshop 3573473727) — do NOT install for this campaign; use its source as an *implementation pattern* only (quest-site research unlock).

---

## Combat overhauls — Combat Extended forbidden (2026-08-02, user's call)

- **Combat Extended** (and equivalent total combat overhauls) — **FORBIDDEN.** Reasons: (1) enormous compatibility surface — it patches essentially every weapon/pawn, including all adopted Vanilla Expanded content, raising the audit/breakage burden the campaign is trying to minimize; (2) it over-arms the PLAYER as much as the enemy (ammo/AP/bipods), pulling against the "qualitative danger, not a player-power arms race" thesis (doc §19.5, eval criterion 11); (3) added risk on frequently-regenerated temporary maps. **The danger goal is met instead via smarter AI (CAI-5000), qualitative VFE factions, and tuned vanilla Custom difficulty — NOT a lethality overhaul.** Keep base game vanilla-lethal. (Enemy-danger design: doc §19.9.)

## Water / sanitation simulation — heavy Dubs Bad Hygiene forbidden; THIRST-only add-on ACCEPTED (rev. 2026-08-04, user's call)

- **Dubs Bad Hygiene — the FULL sim (plumbing, sewage, washing, toilets, contamination, central heating, atmospheric water generator, pipe grids)** — **FORBIDDEN for this playthrough.** A full second need-management sim that competes for attention with the campaign's actual focus systems (VFE-Factory industrial core, VGE astrofuel/heat/substructure). Reasons: (1) large framework = compat/audit surface the campaign minimizes, layered on top of VGE which already owns power/heat/substructure; (2) heavy micro-labor for little payoff; (3) doesn't even deliver the scarcity fantasy — its **atmospheric water generator pulls water from air for *free* once built**, so water becomes a solved problem, the opposite of a desert-crew's "precious water" tension. This is the "all that crap" we do NOT want (user, 2026-08-04).
- **Gravship Water Systems** (TEFNUT/ocarina0001 et al.; local source in mod_sources/gravship-water-systems-main) — **FORBIDDEN by extension.** It is NOT standalone: every component is a `DubsBadHygiene.*` class (CompProperties_Pipe/WaterStorage/sewage, references BadHygiene.dll, `DBHLite="true"`). It's purely a bridge teaching DBH *plumbing* to work on gravships — inert without full DBH, and it re-introduces exactly the free-water plumbing we're rejecting. Falls with heavy DBH.
- **ADOPTED instead — "Dubs Bad Hygiene - Thirst" add-on (WS 2582878800) on top of DBH Lite.** This is the *only* piece of DBH we take. It adds the **Thirst need** plus a handful of low-tech water items (drinking fountain, kitchen sink, water bottles + tribal graphic, pet bowl, animal trough) and — critically — **does NOT include the atmospheric water generator or the plumbing/pipe/sewage grid.** So thirst becomes a *real* mechanical need while water stays *scarce* (hauled, found, rationed), which is exactly the desert-crew "precious water" fantasy the narrative-only approach only gestured at. **Verify on source-inspection (pending Fetcher 2026-08-04d):** confirm the Thirst add-on ships no free-water generator building and that DBH Lite carries no hidden plumbing — if it sneaks one in, that building gets Cherry-Picked out. Guardrail unchanged: **never pair thirst with a free-water building.**
- The Jawa xenotype heat/thirst liability, the ideology water-rationing precept, and RP all sit on top of this real Thirst need (they do not substitute for one — water scarcity is mechanical, not narrative-only).

## Star Wars theme layer — what's IN vs OUT (2026-08-02)

_The "crashed Factory ship / Jawa stowaways" theme is ADOPTED (see required_mods.md → Star Wars Theme Layer). These are the exclusions within that layer, for coherence with the anti-exponential principle:_

- **Dedicated Force-Psycast MODS** (JodemLee TheForce_Psycast; Lee's "Force-Psycast" [discontinued]; Ryoma's Force) — **FORBIDDEN as add-on mods** (user agreed "I don't need the Force at all"; DROPPED per `required_mods.md`). *Clarification (2026-08-06):* the ban here is on these *dedicated Force mods*, NOT on VPE itself. "THE FORCE" in this campaign is delivered NPC-only through **Vanilla Psycasts Expanded, which is KEPT** (Empire Sith elite + factionless/homestead Jedi; players & Jawa excluded — see the player-psycasting entry's enemy-side exception and `required_mods.md` lines ~428–436). We don't need a separate Force mod because VPE already provides the substrate; adding one would just be a redundant reskin.
- **Freely-craftable lightsabers** — the *weapon* is IN but **acquisition is quest/loot-only** (user's call): disable the basic component-bench craft recipe so the whole class is earned, not mass-produced. Reason: a freely-craftable deflect-everything melee weapon is exactly the player arms-race that forbade Combat Extended (§19.5). Rare story asset, not a production line.
- **Star Wars weapon/armor stat-creep** — any Outer Rim/KotOR gear that significantly out-classes vanilla equivalents is a candidate for exclusion pending the def-level balance audit (§19.5 "qualitative danger, not a player-power arms race"). Reskins ≈ vanilla stats are fine; outliers get trimmed.

## Mythological Creatures! — UNSUBSCRIBED (2026-08-13, user's call)

**Owner's words: _"primitive, off-genre, and poorly implemented."_** Workshop
`3520377015`, packageId not to be re-added. This is a *fantasy monster* pack —
goblins, trolls, unicorns, a bigfoot — in a Star Wars campaign, and that alone
would settle it. The audit below is recorded because it was already done, and
because it names what a replacement would have to beat.

**All three charges hold up on the defs, measured 2026-08-13 from the live dump:**

_Primitive._ Eight of the eleven creatures are the same four-tool humanoid
(two fists, a bite, a head-butt) with the numbers scaled. Goblin and goblin
warrior differ only by a statline. Slime — **your most common spawn at
commonality 0.400** — is `trainability: None`, speed 3, one 4-power attack, and
does nothing else at all.

_Poorly implemented._ Two concrete defects:

- **Unicorn is `trainability: None` but `packAnimal: True`.** A pack animal you
  cannot train is not a functioning pack animal.
- **Seven of eleven carry `meatDef: Meat_Human` and `leatherDef: Leather_Human`**
  — imp, gnome, goblin, goblin warrior, troll, giant and one other. Butchering a
  troll yields literal human meat and human leather, with the cannibalism mood
  hit attached. That is an unsignalled trap, not a design choice.

_And the two ideas that WERE interesting are unreachable here._ **Gnome shears
75 Silver per 5 days; a second creature shears 5 Gold per 5 days** — Core's real
`Silver` and `Gold`, i.e. a literal money printer, which on its own would have
made this a ceiling-raiser under the anti-exponential principle. Both sit at
**commonality 0 on Desert, ExtremeDesert, AridShrubland and DesertOasis**, so on
this world they could only ever arrive by trader. The mod's best mechanic and
its worst balance risk are the same feature, and neither reaches the campaign.

**What is genuinely lost, so nobody re-litigates it as nothing:** the
**skeleton** — `baseHungerRate: 0`, so it never eats, ever; lifespan 2000,
wildness 0.5, Advanced trainability. A free, immortal, zero-upkeep hauler,
obtainable here at commonality 0.025. If a zero-upkeep animal is ever wanted,
that is the shape to look for — and it should be judged against the ceiling test
first, because "costs no food" is exactly the sort of thing that raises it.

⚠️ **Follow-up is game-gated and is filed in `TODO.md`.** Steam will not delete
the folder while RimWorld holds it open, so **the folder** is not authoritative
until a clean exit. Do not report "the removal didn't land" before then.

❌ **The `ModsConfig.xml` half of that warning was WRONG and is removed. The game
does NOT rewrite `ModsConfig.xml` on exit.** Measured by a retired seat, 2026-08-13: the file
carried mtime **17:26**, the game ran **17:30 → 21:10**, and the mtime was
**unchanged** after a clean exit — 3h40m of play, including a mod-settings
session, wrote nothing. RimWorld writes that file when the **mod list is changed
in-game**, not on shutdown. **Consequence: `ModsConfig.xml` on disk IS
authoritative while the game runs, and an edit made mid-session is not going to
be clobbered at exit — it is going to be ignored until the next start.** The
thing that *does* silently rewrite it is RimSort; read the mtime before writing.
_(Last of six copies of this claim; the three skills files were fixed in
`a43b610`, this one was missed because the mod list is BUILD's exclusively.)_

## Competing gravship overhauls — Mini Gravships forbidden (2026-08-02)

- **Mini Gravships** (Workshop 3527312835) — **FORBIDDEN.** It is a second gravship overhaul (buildable grav engine, modular engines, conduits-in-structures, ship power gain/usage, gravship turrets) and its own load-order note says "load above other gravship mods for best compatibility" — i.e. it patches the same substructure/engine/power system. **Violates the VGE-sole-gravship-layer decision** (Option A): only one mod may own the gravship layer, and that's Vanilla Gravship Expanded. High conflict risk if stacked.
  - **Mini Gravships Lite** (Workshop 3538850569) — not a conflict (engine/structure/power changes stripped, built to coexist), but **redundant** with VGE, which already owns those systems. Skip as unnecessary.
- **Wrong-franchise total conversions** — **Rimframe: Vatgrown Horizon** (Workshop 3605390246) is a **Warframe** total-conversion (Grineer faction etc.), NOT a Star Wars aesthetic layer as its "aesthetics" framing suggested. Excluded on THEME coherence + bulk-content grounds, not a pillar/stability ruling — it belongs to a different universe than the curated Jawa/SW identity.

## GravTech — craftable gravcores + exponential ship growth (FORBIDDEN, 2026-08-03)

- **GravTech** (Workshop 3545374124, by Alsariul; "Mod, 1.6" tag, Odyssey-required) — **FORBIDDEN.** Source-audited from its Workshop description: adds a **Grav Forge** that *lets you create gravcores* and craft equipment/ship parts from them, buildable **grav engines**, grav weapons/turrets/apparel, gravity implants, advanced ship parts, an asteroid collector, and a **Singularity Reactor** ("miniature black hole… expand [the ship] by another thousand cells").
  - **Violates:** scarcity (destroys the **quest-only gravcore scarcity gate** — the whole campaign leans on gravcores being found, not manufactured) AND the anti-exponential principle (the +1000-cell Singularity Reactor is unbounded ship growth; Q3/Q7 fail). Clean decline.
- **GravTech — companion / VGE-compat addon** (Workshop 3737033254, by ScorpXiion) — **DECLINE with the parent.** Described as *"deepens compatibility between GravTech and Vanilla Gravship Expanded"* — adds a Gravjumper Computer, Maintenance Device, and advanced oxygen for the early game. That utility subset looked salvageable, but it is an **addon bridge to the parent GravTech** and (reasonable inference — fetch resolved to a 122-item collection page, not the About.xml, so not yet dependency-confirmed) almost certainly **depends on** the parent, dragging the whole gravcore-crafting economy in with it. Not separable in practice → decline the pair. **Workaround if ever wanted:** the two useful buildings (Maintenance Device / Gravjumper) could in principle be Cherry-Picked *in* while Cherry-Picking the Grav Forge + Singularity Reactor + grav-engine recipes *out* — but only if a source pull confirms the companion can load without the parent's craft economy. Low priority; VGE already covers gravship maintenance.
- **GravTech — Big cannons addon** (by Alsariul, in the same collection) — **FORBIDDEN by extension** (Big Cannons combat content on top of the forbidden parent). Never in scope.

## Drone/automation workforce rewards — Drone Factory payload restricted (2026-08-02)

- **Vanilla Quests Expanded – Drone Factory** (Workshop 3733951755) — **ADOPTED for the quest chain; the Dronetech workforce PAYLOAD is banned-by-discipline** (user's call 2026-08-02). Official copy: reverse-engineering Dronetech grants "the ability to construct your own mechanized workforce" + unlock "8 additional drone schematics, further specializing your automated workforce." That persistent player automation-workforce = the mechanitor/automation ban and duplicates VFE-Factory as the sole industrial tree.
  - **What's IN:** the QUEST CHAIN (derelict drone scrapyards → rogue awakening transmitter → escalating drone SIEGES → strike a robotics warehouse) — pillar-positive exploration + qualitative escalating enemy.
  - **What's OUT (self-limit, load-bearing):** building an automated drone workforce. Raids + sieges yes; at most 1–2 flavor drones; NEVER a workforce. The whole mod sits next to a standing temptation — this line is the guardrail. Verify **VFE-Mechanoids dependency** before load. (Same discipline shape as Droid Depot.)
- **Ancient Mining Industry** (Workshop 3141472661) — **ADOPTED for exploration; the buildable production line is off-limits by self-restraint.** The player-buildable mining→screening PRODUCTION LINE is a 2nd industrial tree shadowing VFE-Factory → **do not build it.** The 12+ ancient-mine EXPLORATION missions are the reason to install it and are fine. Value (exploration) is separable from risk (buildables). Requires Ideology DLC for quest content.

## Watch-list (not banned, but require restriction — see required_mods.md)

- **Pick Up And Haul + Allow Tool** — allowed, but so efficient they can undercut "accept losses during emergency launches." Not forbidden; countered via pursuit-timer tuning.
- **Bulk *gameplay-content* packs (hundreds of new items/buildings/weapons that shift balance).** The original "avoid hundreds of content mods" note applies specifically to packs that add large volumes of *functional* content (weapons, production buildings, gear that changes the power/economy curve), which dilute the curated exploration focus and expand the balance-audit surface. **This does NOT apply to flavor/QoL/graphics/sound/UI mods, which are welcome in large numbers** (clarified 2026-08-02 — see the "Mod COUNT is not the constraint" note at the top). The discipline: a big library is fine; a big *functional-content* surface needs curation. Samuel Streamer's method (see `Custom_World.md`) is the model — run a large library, then use **Cherry Picker** to delete off-theme functional defs and **Sensible Factions (3531306011) / Faction Control (2882785581)** to control spawns, so the curated *surface* stays coherent even when the *library* is large.

## AI dialogue layer — Powerful AI Integration pair DROPPED (2026-08-11, user's call)

- **Powerful AI Integration** (Workshop 3744421283, `codex.dynamicrolesstoryteller`, author Artas48) — **FORBIDDEN.**
- **Dynamic AI Sculptures** (Workshop 3753149685, `codex.dynamicaisculptures`, same author) — **FORBIDDEN, and must never be re-added alone.** It declares a hard `modDependency` on the above, so the two are a pair.

**Why.** It silently killed every speech bubble in the colony. Its
`Patch_PlayLog_Add_AutoDialogue` patches `Verse.PlayLog.Add`, which is the exact
method Interaction Bubbles postfixes to capture text. In its default *Built-in*
bubble-renderer mode it consumes the log entry and renders through its own
timing queue — so with no AI model configured, nothing was drawn and nothing was
logged. **No exception, no warning, no clue.** SpeakUp, JawaVoice and RimTalk all
went mute because Bubbles is their renderer.

**It is not, strictly, an incompatibility.** The mod ships a *Bubble renderer*
setting with an Interaction Bubbles option, and the author documents it: *"Built-in
is recommended… avoids Interaction Bubbles rendering glitches. Interaction Bubbles
is kept as a legacy option."* Do **not** file a community incompatibility rule
against it — that would be a false report. It is a default that collides with our
stack. We dropped it because the AI-art payoff was a long shot and the dialogue
lane is already crowded, not because it is broken.

**Cost of finding this: eight game loads and four disproved hypotheses** — a
RimTalk prefix, CAI 5000's fog-grid patch, Camera+ altitude distortion, and Tribal
Furniture's duplicate `Assembly-CSharp`. What finally worked was cutting to a
25-mod minimal load, confirming bubbles drew, then re-adding only the 13 mods that
touch a method Bubbles depends on. See `skills/rimworld-modding/SKILL.md` §2.

⚠️ **If it is ever reconsidered:** its own description warns *"do not remove this
mod from an already-started save without a backup"* — it persists conversation
memory and relationship state into the save. Adopt only on a fresh colony.

**The dialogue lane is now: SpeakUp + JawaVoice + Interaction Bubbles.** RimTalk
remains parked and also displays through Bubbles.

---

## Disaster / catastrophe systems — Natural Disasters DECLINED for v1 (2026-08-19)

- **Natural Disasters** (WS `3785601028`, `cardo0909.naturaldisasters`, 1.6-only, 46 MB) — **DECLINED for v1. Not anathema — it is a good mod that is wrong for THIS planet.** Evaluated on the owner's request the day he subscribed; subscribed but never activated.
  - ✅ **It passes the 7-question test outright, and passes the compat test better than most.** No progression ladder, no scaling, no bypass of scarcity or fuel; it *lowers* the ceiling. **Q7 is emphatically "more important"** — a world that periodically tries to kill you where you stand is the purest argument for a gravship. And technically it is clean: **no Harmony at all** (`0Harmony` is not in the assembly reference table; no Prefix/Postfix anywhere), so 🔑 **zero collision risk with Alien Worlds' Tidally Locked patches on `GenCelestial` and `CalculateOutdoorTemperatureAtTile`** — which was the danger we opened the evaluation worried about. No DLC or mod dependencies. Scheduling is its own `WorldComponent`, not `IncidentDef`s.
  - 🔴 **It does not contain the thing we actually need.** The eleven disasters are Earthquake · Flood · Tsunami · Hurricane · SevereFreeze · Tornado · Wildfire · Landslide · Avalanche · VolcanicEruption · Sinkhole. **There is no sandstorm, no dust storm and no heat event.** `desert_world_design.md:170` has had "heat / sandstorm / weather hazard — MOD, to be confirmed" pending since 2026-08; **this is not that mod**, and the gap is closed another way (see below).
  - 🔴 **Four of the eleven contradict ruled world physics, and they cannot be switched off individually.** Measured from the IL of `CanAffectMap`: there is **no per-disaster enable field and no per-type weight override** in the settings, the preset def, or the custom profile. The only levers are all-on / all-off and a global frequency multiplier.
    | disaster | why it is wrong here |
    |---|---|
    | `ND_Earthquake`, weight **100**, **no gate at all** | R-W4 rules this world has **zero plate tectonics** — and that ruling is load-bearing, because it is what explains both the enormous volcanoes and why the Forsaken ruins survived. The highest-weight disaster in the mod directly contradicts it |
    | `ND_Flood` — fires with **no water present** (a closed depression counts as a "rainfall basin") and forces `RainyThunderstorm`/`FoggyRain` via `GameCondition_DisasterRain` | rainfall is **banned planet-wide** (owner, 2026-08-19). A disaster that *forces rain* contradicts a v1 ruling made the same day |
    | `ND_SevereFreeze` — rejects only maps below −18 °C, so it fires here; drops temperature 12–34 °C and lays a **snow/ice field** | snow in the terminator band of a tidally locked desert |
    | `ND_Avalanche`, `ND_Hurricane` | inert — need snow depth ≥ 0.18 and `rainfall ≥ 400` respectively. Dead weight rather than wrong |
    ⭐ The ones that would genuinely suit us — `ND_VolcanicEruption`, `ND_Sinkhole`, `ND_Landslide`, `ND_Wildfire` — are exactly the four we cannot take on their own.
  - 🔴 **It bakes into the save, and we SHIP a save.** `WorldComponent_NaturalDisasters` scribes 25 keys, `MapComponent_NaturalDisasters` 19 including a **`terrainMutationJournal`**, and it writes 15 permanent `TerrainDef`s (collapse chasm, sinkhole chasm, cooled lava rock, fault scarp — several `Impassable`). **Adding mid-campaign is safe; removing after any disaster has landed is NOT** — unresolvable def references on load. ⇒ shipping it makes the mod a **permanent hard dependency of every player's save, forever**, in exchange for content that fights the setting.
  - ⚠️ **One hard overwrite to note if it is ever reconsidered:** `1.6/Patches/ND_FloodRescueCompatibility.xml` does a `PatchOperationReplace` on `WorkGiverDef[DoctorRescue]/giverClass`. Any other mod replacing that giver loses.
  - **The only salvage route, and it is unproven:** Cherry Picker the unwanted `NaturalDisasterDef`s. ⛔ Not recommended — the cherrypick is FROZEN for v1, these are custom defs consumed by a scheduler rather than `IncidentDef`s, and **nobody has measured what the scheduler does when a def it expects is missing.**
  - **v2 reconsideration trigger, stated so it is checkable:** if the author adds per-disaster toggles OR a sandstorm/heat event, re-evaluate. Both are plausible in a mod this young.

  ✅ **AND THE GAP IT WAS MEANT TO FILL IS ALREADY CLOSED — measured 2026-08-19, 73 live `WeatherDef`s.** The stack ALREADY ships **`Sandstorm`**, **`SW_Sandstorm`**, **`SW_DrySandstorm`**, **`VEE_DustStorm`**, **`VGE_DustCloud`**, **`SandWorm_AbnormalSandstorm`** and **`AB_VolcanicAsh`**. ⇒ **The desert-hazard requirement is a `weatherCommonalities` authoring job on our own biomes, not a mod acquisition** — read at RUNTIME, no worldgen involvement, nothing scribed into the save, and it is the exact pattern already specced for the Pyrelands ash storm. `desert_world_design.md:170` should be closed against this, not against a new mod.
