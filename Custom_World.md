# Custom_World.md — How to Build a Crafted RimWorld (living playbook)

_Our working recipe for authoring storytelling-centric worlds, reverse-engineered from Mr Samuel Streamer's published configs + mod-lists and adapted to our anti-exponential Jawa / crashed-Factory-ship gravship run. This file grows as we uncover more. Full evidence + per-file citations live in `samuel_streamer_study/02_TECHNIQUE_ANALYSIS.md`._

**Last updated:** 2026-08-02

---

## The core principle (the one thing to internalize)

**Big library, small curated surface.** You may install a large mod library, but you then *subtract* aggressively so the world presents a small, coherent, on-theme surface. The theme is defined as much by what you delete as by what you add. This is mechanically identical to our anti-exponential pillar — so Samuel's whole method is pillar-compatible.

**OUR run WILL be a large library (confirmed 2026-08-02).** The user likes a lot of flavor / QoL / graphics / sound / UI / cosmetic-content mods, and that is fully endorsed and expected. This is NOT a contradiction of the pillars: **the anti-exponential principle constrains scalable progression *trees*, not mod *count*.** Cosmetic and convenience mods don't add a competing exponential economy — they ARE the "invariant foundation layer." So our discipline is precisely Samuel's: run the big library we enjoy, then use the director mods (**Cherry Picker** to delete off-theme *functional* defs, **Faction Filter** to control spawns) to keep the *gameplay surface* lean and coherent. The one thing we keep small is the set of scalable progression ladders (gravship + VFE-Factory, and nothing else); the flavor layer around them can be as rich as we want.

**Separate invariant plumbing from variable theme.** Freeze a foundation layer (QoL/UI/performance/graphics) once; swap only the theme layer to make a new world. This is why he ships packs fast — and it's how we reconcile "lots of mods" with "constrained progression."

---

## The director-mod toolkit (the machinery, stable across themes)

These ~10 "director" mods do the world-shaping. Learn these, not the content mods.

| Purpose | Mod (Workshop ID) | What it does for us |
|---|---|---|
| **Who lives in the world** | Sensible Factions / "Faction Filter" (3531306011) | Allow-list the exact factions that may spawn; pick the player faction. Suppress everything off-theme. |
| **Remove off-theme content** | Cherry Picker (3521312241) | Delete xenotypes/factions/scenarios/things from generation AND menus. Our anti-exponential enforcer. |
| **Planet biome mix** | Choose Biome Commonality (2582875043) | Re-weight which biomes exist (default 1.0; >1 amplify, <1 rarefy). |
| **Local map contents** | Map Designer (2111424996) | Tune densityRuins/Danger/Animal/Ore + per-ore commonality. Sculpt what a tile physically holds. |
| **Wild animal roster** | Choose Wild Animal Spawns (2564042934) | Control which fauna appear (theme flavor). |
| **Custom named characters** | Backstory Constructor (2907131508) | Author personas: hand-written lore + skillGains table + workDisables map. Characters, not colonists. |
| **Custom races** | native `savedXenotype` export | Vanilla xenotype editor → save `.xml` → import. No special mod needed. |
| **Scenario delivery** | starting save + ScenarioDef pruning | Bake generated world + placed factions + authored pawns + map into a save. Configs reproduce rules; save reproduces authored state. |

---

## The build recipe (step by step)

1. **Write the one-sentence premise.** One legible hook (e.g. "Jawa scavengers repair a crashed industrial gravship and must decide what to leave behind"). Everything else serves or is deleted.

2. **Pick the invariant foundation.** Freeze our QoL/UI/perf layer once (analog to his Foundation Pack). Don't re-litigate it per playthrough.

3. **Cast the factions (Sensible Factions).** Decide the emotional register (besieged? social? scavenger-lonely?) and allow-list only the factions that produce it. For us: Outer Rim Empire + Separatists as live enemies, a couple of trade/neutral outlanders, suppress the rest.

4. **Shape the planet (Choose Biome Commonality).** Tilt toward biomes that bake the theme in. For a scarcity-scavenger run: amplify desert/wasteland/harsh, rarefy lush/safe.

5. **Shape the tile (Map Designer).** Set densities deliberately. For a crashed-ship salvage world we likely want **ruins UP** (salvage everywhere), ore/components UP (feed the Factory), danger tuned to taste. (Contrast: in Warlock he *zeroed* ruins/danger — the setting dictates the direction.)

6. **Prune with Cherry Picker.** Delete every off-theme xenotype/faction/scenario the library drags in. Narrow the scenario picker to only our start. This is the 7-question test made mechanical.

7. **Author the characters (Backstory Constructor).** 3–5 named founding crew, each with lore tying them to the crashed Factory ship + skill/work-disable tables so they *play* their role. Recurring recognizable cast.

8. **Amputate the vanilla baseline (optional, cautious).** NoVanillaWeapons/Apparel makes modded content the *only* content → world stops feeling like "RimWorld + mods." Risky for the item economy; test first.

9. **Bake the scenario into a starting save.** Generate the world with all the above applied, place the crashed gravship, drop the authored crew, save. Distribute save + mod-list + configs together.

---

## Storytelling tricks (the "why it's memorable" layer)

- **Constraint as engine:** one scarce resource or one hard rule generates the drama (Thirst=water, Twilight=10 humans left, Degeneration=tech runs backwards). The mechanic *is* the story.
- **Subtractive theming:** theme = what you delete, not just what you add.
- **Faction alignment = casting:** the roster sets the mood.
- **Named characters carry lore AND mechanics** simultaneously.
- **Immersion by amputation:** remove the vanilla default so the setting stands alone.

---

## Applying to OUR Jawa gravship run — status board

| Technique | Fit | Our plan | Status |
|---|---|---|---|
| Bounty Hunter (#24) as reference | ⭐ High | Uses our exact Outer Rim modules + nomad stack — validated faction/nomad reference (load-order diff DROPPED: RimSort handles ordering) | REFERENCE |
| Sensible Factions | High | Cast Empire+Separatists as pursuers/enemies + few neutrals | TODO |
| Cherry Picker kill-list | ⭐ High (pillar core, now MORE central) | With a large library, this is THE tool that keeps the functional surface lean. **Draft kill-list written → `cherry_picker_killlist.md`** (scenarios, off-theme xenotypes, Two-Empires collision, lightsaber recipe, deferred vanilla-weapon deletion) | DRAFTED — confirm defNames in-game |
| Large flavor/QoL/graphics library | ✅ Endorsed | Install freely — cosmetic/convenience mods are the invariant foundation, not a pillar risk. Only functional/balance/progression content gets curated | ONGOING |
| Choose Biome Commonality | High | Harsh/scarce planet profile | TODO |
| Map Designer | High | Ruins UP (salvage), ore/components UP for the Factory | TODO |
| Backstory Constructor | ⭐ High (creative) | Draft 3–5 founding Jawa/survivor personas | TODO |
| Scenario-as-starting-save | ⭐ High | **DECIDED (user, 2026-08-03): SAVE-BASED model.** Author the start as a starting save (Streamer's model), NOT a portable scenario def. Rationale: user wants an *exceptionally* interesting hand-crafted world, which normally means enormous time in the mod/world/scenario UIs — the goal is to have CoWork do that authoring by editing game files directly where feasible. Consequence: Cherry Picker may delete ALL vanilla scenarios (no base scenario needs preserving). | DECIDED — now pursue file-level authoring |
| NoVanillaWeapons/Apparel | ⚠️ Lean NO | **Audit DONE (2026-08-03): recommend AGAINST.** Outer Rim weapons are charge-TIER reskins (not stronger), so amputating vanilla would delete the scrappy low-tech early arc a scavenger start wants + soft-push everyone onto Durasteel/Tibanna Ultra-tech blasters (mildly anti-scarcity). Keep vanilla for the low end; let SW gear be mid/high flavor; **VWE-Makeshift now ADOPTED (WS 2419690698, 1.6 confirmed)** supplies the authentic junk bottom-tier — which further weakens the amputation case (we get a crude scrap tier without deleting anything). | UNBLOCKED — user's final call, evidence says don't amputate (reinforced by Makeshift adoption) |
| VWE-Makeshift (junk/scrap weapons) | ⭐ High | **ADOPTED (2026-08-03).** WS 2419690698, 1.6 confirmed via About.xml; deps Harmony+VEF Core (already in stack). No-table/no-steel craftable, unreliable-by-design = the Jawa scavenger floor tier. Passes 7-q + §19.5 trivially. | ADOPT — clean, in-theme, in-stack deps |

## Must DIVERGE from him (pillar conflicts)
- **The Force psycast** — violates our psycast ban. Skip.
- **SaveOurShip2** — competes with VGE (our sole gravship layer). VGE is our ship. Skip.
- **His 300–680 mod scale** — take his *directors + method*, not his content volume.
- **MSSFP haunts/reformation-points** — his personal flavor, not our theme.

## Open questions / missing info
- His **starting saves** (not yet downloaded — we pulled lists+configs only) would reveal exactly how scenario parts, custom pawns, xenotypes, and map edits are assembled. If we commit to the save-based model, Bounty Hunter's + Gravtasm's starting saves are the highest-value next pull.
- Whether Sensible Factions cooperates cleanly with VGE's pursuer mechanic (needs a compat check).
