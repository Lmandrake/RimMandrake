# In-Game Verification Checklist — RimWorld 1.6 Gravship Campaign

_Things that can only be confirmed on a running 1.6 install with the relevant mods subscribed. Everything here was source-audited as far as it can be from GitHub/Workshop metadata; these are the residual "confirm at the machine" items. Companion to `required_mods.md`, `forbidden_mods.md`, `world_interest_and_mech_danger.md`, `jawa_xenotype_and_religion.md`._

**Created:** 2026-08-03
**How to use:** subscribe the mods, load a **throwaway dev-mode world** (not the real campaign save), enable Development mode (Options → check "Development mode"), and work down the list. Log anything unexpected. Do NOT run these on the real save first.

---

## 1. CAI-5000 × Mechanoids: Total Warfare — combat-logic compatibility (HIGHEST PRIORITY)

**Why:** both mods touch/reconstruct vanilla combat logic. Two mods rewriting the same pathfinding/targeting layer can silently conflict. This is the one test gating the "RM2 vs Total Warfare vs both" decision.

**Setup:** throwaway world with **CAI-5000 (`Krkr.rule56`) + its deps (Harmony, Prepatcher)** + **Mechanoids: Total Warfare (WS 3555799437)** both active. RimSort to order.

**Steps:**
- Boot the game and watch the loading splash for red errors. Open the log (Development mode → "Open the log file", i.e. Player.log) and search for exceptions naming `rule56`, `CAI`, `TotalWarfare`, or Harmony patch conflicts.
- Use the dev-mode "Make raid" / mechanoid-cluster tools to spawn a mech attack. Watch whether mechs (a) path intelligently / use cover (CAI working) AND (b) show Total Warfare's escalation/units. Both behaviors should coexist.
- Watch for the tell-tale failure: mechs freeze, path erratically, or the log spams per-tick exceptions during combat.

**Decision rule:** if they collide, **CAI-5000 (behavior) is the keeper** → drop Total Warfare and use **RM2** (pure content, no AI override) as the mech-danger source instead. If they coexist cleanly, "both" is viable but run only ONE escalation driver at full strength.

## 2. Reinforced Mechanoids 2 — Gestalt Engine Cherry-Pick (enemy-side discipline)

**Why:** source audit confirmed RM2 ships a **player-buildable Gestalt Engine** (building + "gestate matriarch" recipe, gated behind research `RM_ReinforcedMechanoids`). That's player-mechanitor content = the automation/progression ladder the anti-exponential pillar restricts. We want RM2's *enemy* mechs + faction, not the player toy.

**Steps (pick one approach):**
- **Simplest:** just never take the `RM_ReinforcedMechanoids` research — the Gestalt Engine stays unbuildable. Zero config. (Risk: it sits in the research tree as temptation / a scenario or reward could unlock it.)
- **Clean removal:** use **Cherry Picker** to delete the Gestalt Engine building def + the "gestate matriarch" `RecipeDef`. Confirm the def names in-game via Cherry Picker's browser (they'll be under RM2/Mlie) — do NOT guess; read them off the list. Deleting the building + recipe should leave the enemy mechs untouched.
- After removal, spawn an RM2 mech raid in dev mode to confirm enemy content still works and no red errors from the deleted defs.

## 3. Outland Genetics — Jawa gene-stat confirmation

**Why:** the 1.6 build is Workshop-only; GitHub source is stale (1.4/1.5), so three Jawa gene magnitudes are currently **inferred, not verified**.

**Steps:**
- Subscribe **Outland Genetics (WS 2910172297)** + its deps (Biotech, VEF Core, Tabula Rasa/`neronix17.toolbox`). Confirm the mod shows **"1.6"** in its Workshop/mod-list version tag and loads with no red errors.
- In dev mode, open the gene defs (Character Editor mod, or dev "gene" inspector) and read the actual stats for:
  - `Outland_BodyScale_Small` — confirm the body-size value and its knock-on effects (carrying capacity, melee, hit-box). Inferred as "smaller body, less carry capacity, harder to hit."
  - `Outland_Pos1Metabolism` — confirm it's **+1 metabolic efficiency** (lower hunger rate). Inferred on-theme scarcity bonus.
  - `Outland_Eye_Orange` — cosmetic, no action, just confirm it renders the orange-eye look.
- Update `jawa_xenotype_and_religion.md` §gene-table with the real numbers, removing the "inferred / 🔎 confirm" tags.

## 4. CAI-5000 — LoadFolders sanity check

**Why:** minor. CAI-5000's `LoadFolders.xml` maps only a `v1.4` block even though About.xml declares 1.6 (a fallback-load pattern). Almost certainly fine, but worth a glance.

**Steps:** load with CAI-5000 active, confirm no "content not loading for 1.6" warnings in the log, and confirm CAI behavior actually engages in a spawned fight (mechs/raiders use cover + flank). If behavior engages, the fallback-load is working.

## 5. Ideology Scavenger Role — ability audit (low-risk)

**Why:** ADOPTED 2026-08-03 as a restrictive-identity role for the Jawa ideoligion. Its subtractive design (can't craft/sow/store knowledge; only walk/burrow/pry/carry/flee/endure) passes the anti-exponential test. The one thing unread at audit: it grants a few travel/grave-robbing *abilities* the Workshop page hides behind image blocks.

**Steps:**
- Subscribe **Ideology Scavenger Role (WS 3565039115)** (needs Ideology DLC). Confirm the **1.6** tag and clean load.
- In the ideoligion editor, assign the Scavenger role and read each granted ability. Confirm none is a **labor bypass** (instant-mine, free/teleport-haul, auto-deconstruct). Movement/escape/dig-speed buffs are on-theme and fine; a "produce X for free" ability would need Cherry-Picking out.

## 7. Fog of war — CAI-5000 built-in vs NWN Real FoW (RUN ONLY ONE)

**Why:** the LOS-fog "you only see it when you see it" layer (design `desert_world_design.md` §3(e)). CAI-5000 (already in the stack) **bundles its own fog of war** → possibly free with AI built to path through it. Running two fog mods at once is the failure mode to avoid.

**Steps:**
- With CAI-5000 active, enable its fog-of-war option in mod settings and load a dev world. Confirm: map is hidden outside colonist LOS, threats reveal only when seen, and — critically — **enemies/animals are NOT blind while you are** (symmetric behavior; watch a dev-spawned raid path normally through fog). Check the log for FoW-related exceptions.
- If CAI's FoW is absent, buggy, or player-only, disable it and test **(NWN) Real Fog of War Continued (WS 3391128917)** instead. Confirm symmetric FoV + that FoV visibly shrinks in darkness/weather (test at night and during the SW sandstorm weather if extracted).
- **Decision rule:** prefer CAI-5000's built-in FoW (zero new dep). Only add NWN if CAI's is unsatisfactory — **never enable both.**

## 8. Dark biomes — Odyssey Glowforest / CaveBiome / Ocular Forest low-light

**Why:** the "vision is the scarce resource" strand (design §3(e), palette §A6). Keep dark tiles RARE.

**Steps:**
- **Enumerate the 5 Odyssey surface biomes** off the loaded def list (Development mode → open the biome list, or check `BiomeDef`s) and capture defNames for glowforest, lava fields, toxic scarlands + the 2 unnamed ones → fill the defName columns in `biome_terrain_palette.md` A1/A6.
- Generate a **Glowforest** tile and confirm it reads as perpetual-dark / low-light (this is the zero-mod dark biome). If adopting a mod instead, confirm **CaveBiome** (needs Caveworld Flora) or **Biomes! Caverns (2969748433**, needs Biomes! Core) shows a **1.6** tag and loads clean.
- **Ocular Forest check:** generate an `AB_OcularForest` tile and observe whether it actually imposes low light. If yes, it doubles as a dark biome for free; if no, it's flavor-only (update the palette note).
- Set dark-biome commonality LOW in Choose Biome Commonality / Map Designer.

## 9. Toxic terrain-souring source — STE 1.6 vs Odyssey toxic scarlands (zero-mod path)

**Why:** the §4 rogue-android water-poisoning / terrain-souring tool (design §3(c)). STE's own About.xml couldn't be read (Steam 429'd every fetch); 1.6 is inferred from a translation mirror only.

**Steps:**
- If subscribing **Sustainable Toxic Environment (WS 3254886145)**, confirm its **own supportedVersions shows 1.6** in RimSort and it loads clean — this is the direct evidence the mirror-inference stands in for.
- **Test the zero-mod path first:** generate an Odyssey **toxic scarlands** tile and check whether its native polluted terrain + toxic buildup can carry the "fouled ground / poisoned water on an android holding" role with no mod at all. Also check Advanced Biomes' `PoisonSoil`/`PoisonMud`/`NuclearWaste` floors for the same. If either works, STE is optional.
- Guardrail check: whatever's adopted, confirm there is **no player-facing recipe/ability** that turns it into a usable poisoning tool — it stays enemy-side terrain-shaping only.

## 10. Standing pattern for any Workshop-only mod

The "adopt but Workshop-only" items — **Mechanoids: Total Warfare (3555799437)**, **Tribbles! Continued (2672501251)**, **Mini Gravships Lite (3538850569)** — can only be judged in-game (no auditable source). For each, on the throwaway world:
- Confirm the **1.6** version tag and clean load (no red errors).
- Tribbles: confirm they function as a threat/infestation and are **NOT ranchable** (no breeding-for-resources loop). If they can be penned + bred, Cherry-Pick or leave wild-only.
- Mini Gravships Lite: confirm it **coexists with VGE** (does not redefine gravship structures/engine) before anywhere near the real save.

_(GravTech WS 3545374124 was moved to `forbidden_mods.md` on 2026-08-03 — craftable gravcores + Singularity Reactor break the gravcore scarcity gate + anti-exponential pillar. No in-game test needed; it's out.)_

## 11. Native Odyssey sandstorms — confirm the zero-mod weather path (desert threat axis)

**Why:** the sea-of-desert design leans on a sandstorm-class weather threat (visibility + movement penalty, part of the ④ threat axis). Odyssey may ship a native sandstorm/dust weather that makes a dedicated weather mod (or the extracted SW-Biomes weather in `GravshipCompat`) unnecessary. Recorded from the 2026-08-05 autonomy review (native content beats a mod dependency where it exists).

**Steps:**
- On a throwaway dev world, generate a **desert / ExtremeDesert** tile and use Development mode ("make weather" / incident tools) to trigger every available weather def. Enumerate which ones are sand/dust/haze-type and read their effects (visibility, accuracy, movement, temperature).
- Confirm whether a native Odyssey sandstorm exists and whether it's strong enough to serve the desert ④-threat / vision-scarcity role on its own.
- **Decision rule:** if native sandstorms carry the role, mark the extracted SW-Biomes weather + any weather-mod candidate as OPTIONAL/redundant in `required_mods.md` and `biome_terrain_palette.md`. If not, keep the extracted weather path.

## 12. Odyssey Landmarks — enumerate which types generate (Tier-2 set-piece backbone)

**Why:** the two-tier set-piece model (`context.md` 2026-08-05) delivers major "crashed ship"-class beats by having native Odyssey **Landmarks** generate the tile *type*, then Ancient Urban Ruins / CQF / RimMaster author the content on it. We need the actual list of `LandmarkDef`s that spawn so the arc's Tier-2 beats can be mapped to real tile types (abandoned colonies, ancient garrisons, city ruins were seen on the wiki — confirm in-game).

**Steps:**
- On a dev world, open the `LandmarkDef` list (Development mode → def inspector, or generate several worlds and inspect world-tile landmarks) and **enumerate every Landmark type that actually generates**, with defName + which biomes/terrains weight it.
- Note commonality of each so Tier-2 pacing (~every 2–3 tiles) can be tuned against real spawn rates — this feeds the deferred arc-closing-rate playtest.
- Cross-check against the Sarlacc (`sw_Sarlacc`) and any other mod-added `LandmarkDef`s already in the stack so authored beats don't collide with mod landmarks.

---

## Quick reference — dependencies to have subscribed for these tests

- **CAI-5000** (`Krkr.rule56`) → **Harmony + Prepatcher** (Prepatcher is a new dep). CE is loadAfter-only, not required.
- **RM2** (`Mlie.ReinforcedMechanoid2`) → Harmony + Biotech + VEF Core.
- **Outland Genetics** (`Neronix17.Outland.Genetics`) → Biotech + VEF Core + `neronix17.toolbox`.
- **(NWN) Real Fog of War Continued** (WS 3391128917) → Harmony. Only needed if CAI-5000's built-in FoW is rejected (§7). _Source note (2026-08-04): the GitHub `emipa606/NWNRealFogOfWar` repo's `About.xml` lists only 1.2–1.4, but the repo ships a full `1.6/` folder (DLL + patches) with a `v1.6` block in `LoadFolders.xml` — it IS 1.6-capable; the About tag is just stale. Source pulled + verified into `mod_sources/NWNRealFogOfWar`._
- **CaveBiome** (emipa606) → **Caveworld Flora**; **Biomes! Caverns** (2969748433) → **Biomes! Core** (§8). _Source note (2026-08-04): CaveBiome + Caveworld Flora sources pulled + 1.6-confirmed into `mod_sources`. Biomes! Core + Biomes! Caverns GitHub archives 404'd on the guessed `biomes-team/main` path — repo names re-queried (Fetcher `al`); Biomes! Polluted Lands (BiomesTeam.BiomesPollutedLands, 1.5/1.6) pulled successfully as a reference for the team's repo layout._
- **Sustainable Toxic Environment** (WS 3254886145) → Biotech (pollution mechanics). Test the Odyssey toxic-scarlands zero-mod path first (§9).
- **Cherry Picker** (WS 3521312241) → for the RM2 Gestalt removal + any Tribble/GravTech trims.
