# Custom_World.md — How to Build a Crafted RimWorld (living playbook)

_Our working recipe for authoring storytelling-centric worlds, reverse-engineered from Mr Samuel Streamer's published configs + mod-lists and adapted to our anti-exponential Jawa / crashed-Factory-ship gravship run. This file grows as we uncover more. Full evidence + per-file citations live in `research/RimMandrake/samuel_streamer_study/02_TECHNIQUE_ANALYSIS.md`._

**Last updated:** 2026-08-05 (comedy/levity layer + no-crater assumption added)

---

## The core principle (the one thing to internalize)

**Big library, small curated surface.** You may install a large mod library, but you then *subtract* aggressively so the world presents a small, coherent, on-theme surface. The theme is defined as much by what you delete as by what you add. This is mechanically identical to our anti-exponential pillar — so Samuel's whole method is pillar-compatible.

**OUR run WILL be a large library (confirmed 2026-08-02).** The user likes a lot of flavor / QoL / graphics / sound / UI / cosmetic-content mods, and that is fully endorsed and expected. This is NOT a contradiction of the pillars: **the anti-exponential principle constrains scalable progression *trees*, not mod *count*.** Cosmetic and convenience mods don't add a competing exponential economy — they ARE the "invariant foundation layer." So our discipline is precisely Samuel's: run the big library we enjoy, then use the director mods (**Cherry Picker** to delete off-theme *functional* defs, **Faction Filter** to control spawns) to keep the *gameplay surface* lean and coherent. The one thing we keep small is the set of scalable progression ladders (gravship + VFE-Factory, and nothing else); the flavor layer around them can be as rich as we want.

**Separate invariant plumbing from variable theme.** Freeze a foundation layer (QoL/UI/performance/graphics) once; swap only the theme layer to make a new world. This is why he ships packs fast — and it's how we reconcile "lots of mods" with "constrained progression."

---

## 🅿️⭐ PARKED — GREAT IMPORTANCE: Per-Faction Definition to the "Samuel Streamer level"

**Status:** MECHANISM DESIGNED (2026-08-05) → `faction_authoring_mechanism.md`. The *how* is now built: the 3-layer pipeline (Curation → Generation → Instance/placement), the 5 differentiation axes mapped 1:1 to real FactionDef fields (verified against Outer Rim's own 1.6 source), the per-faction dossier template, and the diff-forcing step. Still PARKED on *execution* (filling the roster), which is gated on the Sensible Factions casting decision below. Workaround in the design doc: fill dossiers for the ~4 already-decided factions now without waiting on full casting.

**The ask, in one line:** define *each faction* in our world to the depth Samuel Streamer achieves — so every faction feels **distinct, thematic, and uniquely capable/restricted** as appropriate, rather than a generic re-skin of "hostile outlander #3."

**Why this is high-leverage (the decision translation).** Everything else in this playbook shapes the *stage* — biomes, tiles, salvage density, the pursuit timer. Factions are the *cast*, and a crafted world lives or dies on whether its cast reads as a set of genuinely different powers with their own doctrine, arsenal, economy, and behavior. This is the difference between "a Star Wars mod is installed" and "the Empire, the Hutts, the Separatist remnants, and the desert scavenger clans each feel like a distinct faction you'd describe differently to a friend." It's plausibly the single biggest lever on how *authored* the world feels — which is exactly the user's stated goal (an *exceptionally* interesting hand-crafted world).

**What "the Samuel Streamer level" concretely means here (evidence-grounded, from `02_TECHNIQUE_ANALYSIS.md`).** His faction distinctiveness is not one mod — it's a *stack of levers applied per-faction*: casting by allow-list (Sensible Factions), subtractive identity (Cherry Picker), a recognizable per-faction arsenal/apparel signature (qualitative capability, §19.5 — scavengers get scrap, the Empire charge-tier), coherent raid/movement doctrine (Faction T&V / Raid Cooldown / CAI-5000), economy/interaction, and named leadership+lore (Backstory Constructor). → **The full lever list mapped 1:1 to real FactionDef fields lives in `faction_authoring_mechanism.md` §2 (with the source evidence in §0).** Not restated here so there's one place to update.

**The gap this parks (the honest scope).** We have the *machinery* catalogued (the director-mod toolkit below) and several *individual* faction decisions already made (Empire-as-pursuer, Hutt trade layer, Bounty Hunters as Act-II pursuer). What we do **not** yet have is a **systematic per-faction design pass** that runs every faction in our final roster through a consistent template so each is deliberately differentiated on every axis above. That template + the filled-in pass is the parked deliverable.

**Proposed shape when we take it up (so future-us starts fast, not from zero):**
1. **Lock the roster first** (depends on the Sensible Factions casting decision — still TODO in the status board below). Can't define factions we haven't cast.
2. **Build a per-faction template** → the field list + the diff-forcing step are defined in `faction_authoring_mechanism.md` §4.
3. **Fill it per faction**, then **diff across factions** to force contrast — if two factions' profiles read the same, one isn't pulling its weight.
4. **Cross-check the whole set against the pillars** (no faction hands the player an exponential ladder; danger is qualitative) and the 3-act arc (which factions carry which act's pressure).

**Dependencies:** the Sensible Factions roster decision (TODO) gates step 1; the §19.5 arsenal audits (Outer Rim done; Bounty Hunters + Faction T&V in-turf ambush still open) feed the arsenal/doctrine fields; the in-game Cherry Picker defName confirmation feeds the "what we delete" field.

**Principal risk if skipped or done shallow:** the world reverts to "lots of Star Wars mods installed" instead of "a cast of distinct powers" — the exact failure mode Samuel's method exists to prevent, and the one most visible to anyone watching or playing.

**Related material already on disk:** the director toolkit (below), `cherry_picker_killlist.md` (the subtractive-identity draft), the Bounty Hunter #24 reference list in `research/RimMandrake/samuel_streamer_study/`, and the per-faction decisions scattered in `context.md` (Empire-pursuer, Hutt trade, Droid Depot) — the parked pass would *consolidate* those into the per-faction template rather than leaving them scattered.

**Highest-value enabling pull (optional, when we commit):** Samuel's actual *starting saves* (Bounty Hunter's + Gravtasm's) — not yet downloaded — would show exactly how he assembles placed factions + leader pawns + faction-specific map edits in practice, turning several `[inference]` items above into `[evidence]`.

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
| **Scenario delivery** | authored `ScenarioDef` + companion DLL over the live bridge | ~~Bake generated world + placed factions + authored pawns + map into a save.~~ 🔴 **SUPERSEDED 2026-08-19 — there is no bake step.** Owner, 2026-08-18: *"Please don't write to the savegame file anymore."* Two offline `.rws` writers passed every invariant check and still killed the game on load; nine save-writing scripts were deleted 2026-08-19. **The ENGINE writes the save, when the owner saves his game.** Route: vanilla worldgen runs untouched → a companion DLL stamps the hand-authored tiles, factions and pawns into the LIVE world over the bridge before any map exists → the owner saves. Scenario parts get in by starting the game from an authored `ScenarioDef` (ruling R-S2 in `design/Jawa/worldbuilding/SCENARIO_SETTINGS_SPEC.md`, reversed 2026-08-19). Full route: `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §12. Configs reproduce rules; the resulting save reproduces authored state. |

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
- **Comedy is emergent + diegetic, not bolted-on (user, 2026-08-05; mods 1.6-confirmed via Fetcher `2026-08-05_jawa_flavor_confirm_1p6`):** the funny in a crafted RimWorld comes from *emergent social* (Vanilla Social Interactions Expanded `2439736083` + growth-arc-choice mods like RandomGrowthChoices `3413983862`, both verified in Samuel's Gravtasm list) + *speech bubbles carrying the setting's voice* (Interaction Bubbles `1516158345` **driven by SpeakUp `2502518544`, a Social Interaction Framework that renders player-authored lines** — so the Jawa trade-babble is *written* content, not a vanilla-def hack) + *the belief system itself* (comedic ideoligion precepts via VIE-Memes `2636329500` + Alpha Memes `2661356814`, the latter confirmed 1.6 at v4.0). Avoid meme/crossover gag-packs that shatter the theme. (NB on AI-dialogue: an LLM that *reframes* SpeakUp's already-raised text into a Jawa register — e.g. `johndroper/RimDialogueClient` — is ON-plan as a flavor layer over hand-authored anchor lines; under investigation 2026-08-05. Only *originator*-style AI chatter is deprioritized. See required_mods.md 🃏 COMEDY §(1) LLM-REFRAME sub-bullet.) The register is set by the cast (small greedy scavengers) — so the humor reinforces the world instead of breaking it. Full plan in `required_mods.md` 🃏 COMEDY / LEVITY LAYER + `design/Jawa/worldbuilding/jawa_society.md` §2.7.

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
| NoVanillaWeapons/Apparel | ⚠️ Lean NO | **Audit DONE (2026-08-03): recommend AGAINST.** Outer Rim weapons are charge-TIER reskins (not stronger), so amputating vanilla would delete the scrappy low-tech early arc a scavenger start wants + soft-push everyone onto Durasteel/Tibanna Ultra-tech blasters (mildly anti-scarcity). Keep vanilla for the low end; let SW gear be mid/high flavor. (VWE-Makeshift was once the junk bottom-tier here; it is deprecated for v1 as bullet guns, so vanilla low-tech carries the floor alone — which if anything makes amputation *worse*, not better.) | UNBLOCKED — user's final call, evidence says don't amputate |
| VWE-Makeshift (junk/scrap weapons) | — | **DEPRECATED FOR v1 (owner, 2026-08-15).** WS 2419690698; balance was never the problem (passes 7-q + §19.5 trivially). All six weapons are bullet guns and v1's weapons are blasters. Six ThingDefs cut via Cherry Picker; the mod stays installed and stays on the list for a later mod-removal pass. A salvage-built tier reskinned as blasters is a v2 idea. | CUT for v1 — off-theme, not unbalanced |

## Must DIVERGE from him (pillar conflicts)
- **The Force psycast** — violates our psycast ban. Skip.
- **SaveOurShip2** — competes with VGE (our sole gravship layer). VGE is our ship. Skip.
- **His 300–680 mod scale** — take his *directors + method*, not his content volume.
- **MSSFP haunts/reformation-points** — his personal flavor, not our theme.

## Open questions / missing info
- His **starting saves** (not yet downloaded — we pulled lists+configs only) would reveal exactly how scenario parts, custom pawns, xenotypes, and map edits are assembled. If we commit to the save-based model, Bounty Hunter's + Gravtasm's starting saves are the highest-value next pull.
- Whether Sensible Factions cooperates cleanly with VGE's pursuer mechanic (needs a compat check).
