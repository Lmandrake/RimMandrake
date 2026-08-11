# concept.md — Portable Campaign Brief

_The one-page orientation to the Gravship Expedition campaign. Premise, pillars, the sanctioned
progression trees, and the shape of the mod stack — enough for any file or agent to act correctly
without reading the 176KB `context.md` narrative log. **Keep this short and current.**_

**RimWorld 1.6 + Odyssey.** Personal campaign. **Build assumptions (user 2026-08-04):** ALL official DLC is present and enabled (Royalty, Ideology, Biotech, Anomaly, Odyssey) — never add "if the campaign is running DLC X" checks; assume every DLC mechanic (pollution, genes, rituals, deathrest, anomaly entities, gravships) is available. This is a **single-player build for the user's own consumption only** — do not design for other players, mod-list portability, or public-release robustness; optimize purely for the user's intended experience. (Note: "portable" in these docs' filenames/notes means *portable across our own files/agents*, not distributable to other players.) Companion files: `context.md` (full narrative log),
`required_mods.md` / `forbidden_mods.md` (authoritative mod verdicts), `concept_defnames.md`
(verified defName/ID vocabulary), `setup_checklist.md` (live setup decisions),
`desert_world_design.md` (the consequential-landing / terrain design layer — why land HERE?),
`save_authoring_pipeline.md` (how the start is built), `rimbridge.md` + `RimMaster.md` (live-edit
tooling). This file is the portable brief those others assume.

---

## 1. Premise
A **crashed Factory ship / Jawa stowaways** story (Star Wars flavor). The gravship is *someone
else's* crashed industrial vessel — a working (if damaged) gravship running the VFE-Factory
production line — that **Jawa scavenger-mechanics have inherited and are repairing.** The onboard
industry is the diegetic reason the hull was worth boarding. Feel: Firefly / Battlestar Galactica /
Oregon-Trail-in-space / a scientific expedition crossing an unexplored world.

**Core loop:** Land → choose objectives → temporary camp → explore → gather → improve the ship →
enemy pressure rises → decide what to leave behind → launch → repeat. The entire permanent colony
lives aboard the ship; planetary camps are disposable. Small crew (~3 to start, ~4–8 steady).

## 2. Design pillars (the "why" behind every ruling)
Mobility · scarcity · exploration · hard logistical choices · **"decide what to leave behind."**

**Governing rule — the anti-exponential principle:** the **gravship + its onboard VFE-Factory
industrial system are the ONLY sanctioned scalable progression trees.** Everything else must be a
fixed identity, a finite/quest-gated reward, or pure flavor — never a parallel ladder that scales
indefinitely. This is why psycasting, genetics-lab breeding, the mechanitor ladder, fluid-ideology
development, and royal-permit ladders are all forbidden as *player* systems.

**§19.5 — no arms race:** enemy danger comes from *qualitative capability* (smarter AI, coherent
tactics, distinct rosters), NOT stat inflation or raid-point bloat. Any weapon/loot must clear the
same bar: qualitative interest, not power creep.

**Mod COUNT is not the constraint — the capability CEILING is.** A LARGE library is endorsed:
flavor, QoL, graphics, sound, UI, cosmetic content pass trivially (the "invariant foundation
layer"). Only *ceiling-raisers* get scrutiny.

## 3. The 7-question test (apply before adding ANY mod / subsystem / reward)
1. Does it deepen the gravship/industrial tree, or create a **parallel ladder**?
2. Does it impose a dependency, or merely **remove a limitation**?
3. Can it **scale indefinitely** via trade/research/breeding/crafting/repeated quests?
4. Does it make crew composition/recruitment **less important**?
5. Does it **bypass** fuel, deck space, expedition risk, production time, injuries, mood, or scarcity?
6. Is it reducible to a **single authored exception** rather than a general system?
7. Does it make the ship **MORE important, or LESS necessary**?

Answers pointing toward broad optionality / self-sufficiency → restrict or exclude.

## 4. Stack shape (identity, not the full list — see `required_mods.md`)
- **Ship layer:** Vanilla Gravship Expanded (VGE) = **sole** gravship overhaul. Astrofuel refined
  from chemfuel (2:1 loss, power-hungry) = the built-in fuel leash.
- **Industrial core:** Vanilla Furniture Expanded – Factory (native VGE integration; astrofuel).
- **Progression gate:** Configurable Techprints makes factory/gravtech research **quest-only**.
- **Theme layer:** Outer Rim (factions/species incl. `OuterRim_Jawa` xenotype), Nomad Scavenger
  look, Star Wars Xenotypes, Fully Functional Lightsabers (**quest-earned only, craft disabled**),
  VWE-Makeshift (junk scavenger weapons). Empire = fused vanilla Royalty + Outer Rim Galactic
  Empire, and is the **pursuing antagonist** (as a live hostile faction).
- **Enemy interest:** CAI-5000 (smarter AI) + Reinforced Mechanoids 2 + qualitative rosters;
  Custom difficulty tuned "fewer, heavier, smarter." No raid-point inflation, no player mech ladder.
- **World interest:** Geological Landforms, Biome Transitions, Alpha Biomes, Ancient Urban Ruins +
  Dungeon Pack, Exploration Mode (world fog-of-war).
- **Curation method (Streamer-style):** big library, small curated *surface* — Cherry Picker
  deletes off-theme functional defs; Faction/Sensible Factions controls spawns. Cosmetic library
  stays rich.
- **Delivery:** the start is authored as a **starting SAVE**, not a portable scenario def.

## 5. Ideology (see `jawa_xenotype_and_religion.md`)
Fixed ideoligion "The Articles of Passage" (Keepers of the Second Hand): memes **Nomad + Tunneler**,
two non-multiplying roles (Chief/Captain + Keeper of the Articles), cohesion-only rituals, one
modest relic. Secular animist scrapper culture — **not** a Force faith (psycasts forbidden).

## 6. Hard "never" list (quick reference; full reasons in `forbidden_mods.md`)
Combat Extended · psycasts / The Force · genetics-lab breeding & gene-shopping · mechanitor ladder ·
fluid ideology · GravTech gravcore-crafting family · Mini Gravships (competes with VGE) · raid-point
inflation mods · player automation that trivializes hauling (e.g. Industrial Rollers) · repairing
gear (use No Durability + VFE smelter instead) · ritual loot payouts · production/combat specialist
roles.

## 7. Consequential-landing design layer (see `desert_world_design.md`)
The world is a **desert sea to cross, not a place to settle** — landing is a decision under scarcity, not tourism. Every terrain is defined by a **four-axis schema:** ① **Abundant** (the survival surplus you come for), ② **Scarce/missing** (the denied resource that creates your next need), ③ **Exotic** (rare covetable wealth — terrain treasures, gems, fossils/amber, oil infra), ④ **Threat** (one qualitative §19 danger that times your exit). Closed loop: Abundant fills a need → Scarce creates the next → Exotic tempts lingering → Threat forces departure. No tile is self-sufficient (§3A resource-partition scheme), so the slices only add up if you keep moving — which *is* the campaign.

**Terrain treasures (§3B):** pre-placed, workable, NON-player-buildable extraction sites (quarry / well / deep-drill / salvage wreck / placer / oil derrick). You can *operate* what you find but never *build* one, so wealth is bound to the place, not the colony — and the pursuit forces you off before you can strip it dry. This inverts a classic exploit (buildable quarries) into a scarcity engine. **Generalized infinite-generator principle:** an infinite-rate generator (e.g. a regenerating oil well) is pillar-safe as a treasure *iff* it's discoverable-only/non-buildable AND sits on a tile whose ④ threat enforces a bounded dwell — extraction is then capped by dwell-time × cargo, not by generator count.

**Water = the master-resource (see also §(a) + §3A of the design doc).** Water is a first-class *common* resource each terrain rates, backed by DBH **Lite + Thirst-only** (real Thirst need, NO plumbing grid, NO free-water generator — full DBH + Gravship Water Systems stay FORBIDDEN). Three physical forms set a tile's rating and its fill route: **surface** (river/oasis/coast — pumpable), **groundwater** (aquifer — well + haul to a tub), **none** (deep desert / salt flat = ✗). The gravship carries **storage, not generation**: a minifiable **Water Butt** (100-cap) as the onboard reservoir + bottled water in cargo. You top off on water-rich tiles and ration the finite reserve crossing dry ones — a ✗-water tile physically cannot be camped, which is the exit engine expressed as a gauge.

**Faction registers (§4):** Empire = the singular escalating *military* pursuer (the hunter). Hutts = *economic/criminal* power — trade you can't trust (bounty/extortion, situationally hostile). Rogue androids = *territorial* threat tied to specific tiles. **Android water-denial doctrine:** because androids don't drink, water-denial is free for them and fatal for you — so they settle the ✗-water terrains on purpose (the terrain is their moat) and **poison/pollute** the tiles they hold (fouled water gives tox buildup instead of relief; polluted ground via native Biotech mechanics). A captured android tile *can* be temporarily cleansed (Biotech cleanup), which is fine — the Empire pursuit is the real timer, so it's a reclamation project you rarely get to finish.

## 8. Tooling note
Live-map enrichment after arrival is done via **RimBridgeServer** (engine-route, main-thread-safe)
driven by the **RimMaster** agent — an *authoring/GM tool only*, never in-fiction player power.
Web retrieval in this environment goes through the **Fetcher** system (direct web is unreliable).
