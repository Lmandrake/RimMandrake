# rimworld_file_lore.md — technical manual for editing RimWorld save / scenario / def files

_Purpose: a **self-teaching reference** so that any future session can successfully edit RimWorld savegames (`.rws`), scenarios, and mod def/patch XML for this campaign. Records concrete file names, XML node structures, safe-vs-fragile regions, gotchas, and lessons learned by doing. **Keep this updated** every time we learn something new about how these files work. Distinguish what we've **verified from actual files** (✅) vs **inference/assumption** (🔎) vs **not yet confirmed** (❓)._

**Started:** 2026-08-03. RimWorld **1.6 + Odyssey**.

---

## 0. Golden rules (non-negotiable, learned the hard way)

1. **A wrong defName in a save's thing-ID reference graph is unforgiving** — it can silently corrupt or hard-fail a load. NEVER guess a defName; confirm it against the actually-installed mod files first.
2. **Always: timestamped backup → edit → parse-validate the XML → reload-test in game.** No exceptions for save edits.
3. **Legible low-linkage nodes are safe to hand-edit** (scenario text, pawn story/skills, faction names). **The thing-ID reference graph and raw map cell/region data are the fragile region** — prefer engine/mod-assisted routes (dev-mode spawn, Map Designer, quest/site generators) over raw XML injection there.
4. **Prefer a maintained mod or an engine route over raw save injection** whenever both achieve the goal.
5. **Mods rename defs between versions.** A def confirmed in a 1.5 folder is NOT proof of the 1.6 defName. Always read the version folder that will actually load (see LoadFolders below).

---

## 1. File types & where they live

- **`.rws` savegame** — plain, human-readable XML. This is the OUTPUT we polish for the save-based world-delivery model. Root is `<savegame>` containing `<meta>` (game version, mod list + mod IDs, modSteamIds) and `<game>`.
- **Scenario** — baked inside a save at `<game><scenario>`; also exportable as a standalone scenario def. For our campaign we author it inside a save (save-based model), not as a portable def.
- **Mod def XML** — `<ModDir>/<version>/Defs/**/*.xml`, wrapped in `<Defs>...</Defs>`. Each def is a typed node (`<ThingDef>`, `<ResearchProjectDef>`, `<AbilityDef>`, mod-namespaced types like `<ModularWeapons2.ModularPartsDef>`, etc.).
- **Patches** — `<ModDir>/<version>/Patches/*.xml`, wrapped in `<Patch>`, using `PatchOperation*` ops. Our own patches live in the compat mod `mandrake.gravship.compat` (folder `custom_patches/GravshipCompat/`), which loads LAST.
- **About** — `<ModDir>/About/About.xml` = packageId, supportedVersions, modDependencies, loadAfter/loadBefore. THE authoritative version + dependency source.
- **LoadFolders.xml** — `<ModDir>/LoadFolders.xml` maps which subfolders load per game version (e.g. `<v1.6><li>1.6</li></v1.6>`). ✅ Lesson: a mod can declare About supportedVersions=1.6 but have a LoadFolders that only maps a v1.4/1.5 block — meaning it falls back to older content. Read LoadFolders to know which folder ACTUALLY loads, don't assume it's the folder named after the version.

---

## 2. Save (.rws) anatomy — verified from Gravtasm's 1.6.4633 save ✅

- **`<game><scenario>`** — the whole scenario:
  - `<name>`, `<summary>` — free text, safe to edit.
  - `<parts>` — list of `<li Class="ScenPart_*">` nodes. Types seen: `ScenPart_ConfigureStartingPawns` (pawn count), `ScenPart_StartingResearch`, `ScenPart_StartingThing_Defined` (a thingDef + `<count>`), `ScenPart_PlayerPawnsArriveMethod` (value `Gravship`), `ScenPart_GameStartDialog` (intro text), and modded parts like `LoanMod.ScenPart_Loan`. Each is legible and editable.
- **Factions** — the player's starting crew live in a faction named `GravshipCrew` (loadID seen = 16). Factions are referenced elsewhere by loadID.
- **Pawns** — each pawn has:
  - `<story>` — `<childhood>`/`<adulthood>` (backstory defNames), `<traits>`, plus appearance nodes (hair, skin, body). Editable.
  - `<skills>` — 12 `<li>` skill records, each `<def>` + `<level>` + `<passion>` (None/Minor/Major). Editable — this is how you hand-tune a crew.
  - Xenotype referenced by **mod defName**; `<customXenotypeDatabase>` is EMPTY when the xenotype is a mod def (ideal — our Jawa is a mod def, not a save-embedded custom xenotype).
- **`<meta>`** — lists `<modIds>` + `<modSteamIds>` + `<modNames>`. A save will complain / degrade if loaded against a different mod set. Keep the mod list in sync.

### 2a. ITEMS & their flavor — VERIFIED ✅ (2026-08-05, Gravtasm save, `Utils/Savegame_detailed_items.py`)
An **item/Thing** is any XML element with BOTH a `<def>` and an `<id>` direct child (weapons, apparel, chunks, plants, filth, buildings, pawns…). **A `.rws` parses cleanly with `xml.etree.ElementTree` — full 14MB file in ~0.4s**; prefer ElementTree over regex for READING so each flavor field stays bound to its own item (regex is fine only for quick counts). Gravtasm: 14,752 items / 166 defs (plant 7027, filth 4992, chunk 1667, building 466, apparel 166, pawn 42, weapon 26…). Per-item flavor children (all optional, present only when the item has them):
  - `<title>` = **unique/legendary item NAME** (e.g. *Ash Raven*, *The Vulture*, *Suffering*, *Torment* — named weapons on the crew). Rare; 4 in Gravtasm, each on a pawn.
  - `<quality>` = Awful/Poor/Normal/Good/Excellent/Masterwork/Legendary (Gravtasm: 227 quality items, incl. 1 Masterwork FFF_RegalSuit on the captain).
  - `<stuff>` = material defName (Steel, Hyperweave, Synthread, Leather_*, modded stuffs like AG_Ultima/RG_DinosaursHideHeavy).
  - `<health>` (current HP), `<stackCount>`, `<pos>(x,0,z)`.
  - `<taleRef><seed>` = procedural-**art** reference. ⚠️ **Only the SEED is stored, not the rendered art-description prose** — the readable "story" of an art piece is regenerated in-engine from the seed (same live-game requirement as the terrain shortHash). Tool reports the seed for later cross-ref.
  - **Held items** are linked to their owner by walking up to the nearest enclosing pawn `<name>` node (first/nick/last).
- **Narrative / story TEXT** lives in `<text>` (letters, messages, archived comms — e.g. `ScenPart_GameStartDialog` debt intro, `StandardLetter`, `Message`) and `<description>` (scenario summary, quest text, ideo/backstory prose). Both are legible free text, safe to read; the source-class is the enclosing `<li Class="…">`. Gravtasm: 30 narrative blocks.

### 2c. IDEOLIGIONS (religions) — VERIFIED ✅ (2026-08-05, Gravtasm save, `Utils/Savegame_ideoligions.py`)
Ideoligions live **fully-expanded inside the save** under `<game><ideoManager><ideos><li>` — each `<li>` is one complete religion (not merely a def reference), so the `.rws` is a **self-contained authoritative source** for the campaign's faiths. Legible, **safe-to-READ** node (same tier as scenario / pawn-story text). Gravtasm: **14 ideoligions.** Per-ideo children:
  - `<name>` / `<adjective>` / `<memberName>` (e.g. *Techno-Fidelism* / *fidelist* / *Fidelor*), `<leaderTitleMale>`/`<leaderTitleFemale>` (e.g. "Archic Boss").
  - `<description>` = the procedurally-**generated origin myth**, stored as **full readable prose** — ⚠️ unlike item `taleRef` seeds and terrain shortHashes, **no live-game regeneration needed** (e.g. The Cult's Hiseunos/Vana-Metric myth is verbatim in the save, complete with `<color=#…>` deity-name markup).
  - `<culture>` (Kriminul, Astropolitan, Sophian, Benefactor…), `<iconDef>`/`<colorDef>`/`<primaryFactionColor>` (visual identity).
  - `<memes>` = list of meme defNames = the ideo's **structural pillars** (e.g. `Structure_Archist`, `Transhumanist`, `HumanPrimacy`; many modded — `VME_*`, `AM_*`, `MI_*`).
  - `<foundation Class="IdeoFoundation_Deity">` → `<def>`, `<place>` (sacred place name), `<deities>` (each `<li>` = `<name>`/`<type>`/`<gender>`; often empty for deity-less ideos).
  - `<precepts>` = big list of `<li Class="Precept_*">`. Classes seen: `Precept_RoleSingle`/`Precept_RoleMulti` (roles → `<name>`+`<def>`, `restrictToSupremeGender`), `Precept_Ritual` (name + `ritualExpectedDesc` flavor blurb + `sourcePattern`), `Precept_Building` (sacred buildings), `Precept_Relic`, `Precept_Weapon`, `Precept_RitualSeat`, `Precept_GravshipLaunch`, `IdeologyVirtues.Precept_Virtue`, and **Class-less `<li>`** = an **issue position** (stance on slavery/execution/body-mod/etc.; `<def>`+human `<name>`). Gravtasm ideo[0]: 92 precepts = 56 issue positions + 19 rituals + 3 roles-single + 2 roles-multi + 3 buildings + 2 relics + …
  - `<id>` = the ideo's load id. **Pawn membership:** a pawn points at its faith via `<ideo>Ideo_<id></ideo>`; tally those for a follower/prominence count (Gravtasm: Rules of Acquisition 8, Techno-Fidelism 6, …). NOT a full faction↔ideo map (no simple faction-ideo node in this save).
  - **Tool:** `Utils/Savegame_ideoligions.py` → `<stem>_ideoligions.md` (roster table + per-religion section) + `.json`.

### Fragile regions (do NOT hand-edit casually) ❓/🔎
- The **map thing list + cell/region/pathing data** — every Thing has a unique load ID and cross-references (jobs, reservations, rooms). Injecting or deleting nodes here by hand risks dangling references. This is the **Tier 2b live-map enrichment** frontier — treat via engine/mod-assisted spawning first, raw injection only with heavy backup+reload discipline and small increments.

### 2b. In-play MAP grids — VERIFIED ✅ (2026-08-05, Gravtasm 1.6.4633 save, `Utils/Savegame_mapview.py`)
The map is a single block under `<maps><li>`: `<uniqueID>`, `<generatorDef>Base_Player`, `<mapInfo><size>(225, 1, 225)</size><parent>WorldObject_134</parent>`. So map size = **(W, 1, H)**, W·H cells (here 225×225 = 50,625). READING these is safe (parse-only); WRITING them stays in the fragile region.
- **Terrain grid** `<terrainGrid><topGridDeflate>` = base64 of a **raw DEFLATE** stream → decode with `zlib.decompress(base64.b64decode(blob), -15)` → **W·H little-endian uint16**, one code per cell (row-major, `idx = z*W + x`). ⚠️ Each uint16 is a `ShortHashGiver` **shortHash**, NOT a 0..N legend — cannot be reversed to a defName from save text alone (need the exact load order, OR the live game via RimBridge `get_cell(s)_info`, OR an offline "load mods once, dump `TerrainDef.shortHash→defName`" legend). Same blocker already documented for the biome grid (`<tileBiomeDeflate>`) in `save_authoring_pipeline.md`. Sibling grids in the same `<terrainGrid>`: `underGridDeflate`, `foundationGridDeflate`, `tempGridDeflate`, `colorGridDeflate`.
- **Roof grid** `<roofGrid><roofsDeflate>` = SAME encoding (base64 raw-DEFLATE → LE uint16); `0` = unroofed. (Gravtasm: only ~2.1% roofed.)
- **Things** are `<def>…</def><id>…</id> … <pos>(x, 0, z)</pos>` — position is `(x, 0, z)`, **origin bottom-left** (flip z for image rows). A regex `<def>/<id>/…/<pos>` sweep bins them cheaply (Gravtasm: 14,384 things, 72 distinct defs — desert-diagnostic: SaguaroCactus/PincushionCactus/Agave/TreeDrago/ChunkSandstone, plus `GravshipHull`×48, `Wall`×394, 1 Human pawn).
- **Present as map children:** `pollutionGrid`, `gasGrid`. **Absent** in this save: `elevationGrid`, `fertilityGrid`.
- **Tool:** `Utils/Savegame_mapview.py` renders terrain+roof+pawns to a PNG and emits a legend JSON. First successful map-preview probe (2026-08-05) — proves we can read/understand the in-play map, not just the scenario/pawn nodes.

---

## 3. Weapon / damage model (how RimWorld expresses weapon power) ✅

Critical for balance audits and for judging what loot is safe to inject.

- A ranged **weapon ThingDef** carries: `<verbProperties>` with `range`, `warmupTime`, `burstShotCount`, `ticksBetweenBurstShots`, `defaultProjectile` (a projectile defName), and accuracy stats (`AccuracyTouch/Short/Medium/Long` via statBases, or per-verb `accuracyMedium` etc.). It also has `RangedWeapon_DamageMultiplier` in statBases — **this is a MULTIPLIER, not the base damage.**
- **The actual per-hit damage + armor penetration live in the referenced PROJECTILE def** (`<ThingDef ParentName="BaseBullet">` with `<projectile><damageAmountBase>` and `<armorPenetrationBase>`). To judge a gun's real damage you MUST read its projectile def, not just the weapon.
- Vanilla reference points: assault rifle 11 dmg ×3 burst / ~25% AP / range 32; charge rifle 11 dmg / 35% AP; bolt-action 25; sniper ~30; longsword melee 18.
- Melee weapons: damage via `<tools>` list (each tool has `power` + `cooldownTime` + capacities). Lightsaber arms-race vector = `CompDeflector` with `baseDeflectChance` (0.99 = near-bulletproof vs ranged for a high-Melee wielder).

### KotOR-specific lesson (in progress) ✅/❓
- KotOR Weapons & Armor's upgrade "abilities" (power blast / sniper kit / rapid-fire trigger) are **bounded extra attack verbs** defined as `AbilityDef`s attached via `ModularWeapons2.ModularPartsDef`, each gated behind research `guy762_ResearchKotOR_advupgrade`, each with fixed `maxCharges` / cooldown. They are alternate fire modes, NOT stacking stat multipliers → not an exponential ladder. (Good sign for §19.5, pending the base projectile numbers.)
- ✅ **RESOLVED: KotOR projectile defs live in a DEPENDENCY, not the weapon mod.** `KotORBlasterBolt_*` / `KotORIonBolt_*` / `KotORSlugBolt` are referenced by `defaultProjectile` in KotOR Weapons & Armor but DEFINED in **KotOR Resources & Materials** (`guy762.MM.KotORCore`, WS 3254370945). General lesson: **a weapon mod often ships only the weapon ThingDef + a `RangedWeapon_DamageMultiplier`, delegating the base projectile (damage + AP) to a shared "resources/core" dependency.** To get real per-shot damage you must read the dependency's projectile source, not the weapon mod. The multiplier bounds the ceiling (KotOR's are ≤1.2 = charge-tier).
- ✅ **LESSON: content can MIGRATE to a dependency between versions.** KotOR 1.6 DELETED its own lightsaber weapon defs (present as `kotorlightsaber_*.xml` in the 1.5 folder) and now delegates all lightsabers to the `lee.theforce.lightsaber` dependency. So reading the 1.5 folder would have given the WRONG picture for 1.6. Always read the version folder that actually loads (per LoadFolders) AND check the version-specific dependency block (`modDependenciesByVersion`), because deps differ per version too.

---

## 4. Patch operation patterns (for the compat mod) 🔎

- Wrap target-mod-specific patches in `PatchOperationFindMod` or `PatchOperationConditional` so a missing/renamed target is a silent no-op, not a red error.
- `PatchOperationAdd` to add a child node (e.g. add `<designationCategory>` to make something buildable); `PatchOperationReplace` to swap a value; `PatchOperationRemove` to strip.
- One concern per patch file, commented. Verified field names against the version that will load (not a stale older-version folder).
- ✅ Lesson from the Slingshot work: a def confirmed only against a mod's 1.5 source must be re-verified on 1.6 before the patch is trusted — the def may be renamed or gone.

---

## 5. Extraction / investigation workflow lessons ✅

- To read a mod authoritatively, **download the full repo/branch zip and extract locally** (XML-only; strip textures/sounds to save space), then grep for real defNames. Piecemeal raw-file fetching fails because you have to guess paths and file layouts change between versions (KotOR 1.6 renamed `WeaponRanged_KotOR*.xml`; path guesses 404'd repeatedly until the full zip settled it).
- GitHub access notes (Fetcher environment): `raw.githubusercontent.com` and `api.github.com/git/trees/<branch>?recursive=1` work; `api.github.com/repos/.../contents/` is rate-limited (429); Steam Workshop `filedetails` pages chronically 429. Branch archive zip endpoint (`github.com/OWNER/REPO/archive/refs/heads/BRANCH.zip`) works.
- The recursive git tree endpoint truncates at a ~50KB character cap — for big repos, prefer the branch zip.
- Local mod source trees for this campaign live in `~/GDrive/Personal/Rimworld/mod_sources/` (~23 mods, assets stripped).

---

## 6. Quick index of verified names (see concept_defnames.md for the full list)
Save structure landmarks: `<game><scenario>`, `ScenPart_ConfigureStartingPawns`, `ScenPart_StartingThing_Defined`, `ScenPart_PlayerPawnsArriveMethod` (=Gravship), faction `GravshipCrew`, pawn `<story>`/`<skills>`. Weapon model: `verbProperties`, `defaultProjectile`, `RangedWeapon_DamageMultiplier` (multiplier), projectile `damageAmountBase`/`armorPenetrationBase`, melee `<tools>`, `CompDeflector.baseDeflectChance`.

---

## 7. Running "things I still need to learn" list
- ✅ **RESOLVED (2026-08-04): Tier 2b live-map enrichment now has a real route — RimBridgeServer.**
  Rather than hand-injecting into the fragile map thing-graph, drive the *running* game via
  RimBridgeServer's GABP/MCP tool surface (`spawn_thing`, `execute_debug_action`,
  `apply_architect_designator`, `find_random_cell_near`/`flood_fill_cells` for valid cells,
  `get_cell(s)_info` to read). Its architecture enforces **main-thread ownership**, so
  mutations go through RimWorld's own main-tick/long-event paths — the exact engine-route this
  file prefers over raw XML. So we largely *don't need* to solve raw thing-list injection.
  Full detail in `rimbridge.md`; agent design in `RimMaster.md`; source in
  `mod_sources/RimBridgeServer-main/` (esp. `docs/tool-reference.md`).
- ✅ **RESOLVED: dev-mode spawn CAN be scripted** — RimBridgeServer exposes the whole debug-
  action tree (`search_debug_actions` + `execute_debug_action` by stable path) and Architect
  designators programmatically, plus JSON/`run_lua` scripting for multi-step sequences. Map
  Designer is mostly map-gen-time (not live), but blueprint mods (New Blueprint WS 3534166729)
  can stamp structures the bridge then triggers.
- ✅ RESOLVED: KotOR projectile base damage/AP live in the KotOR Resources & Materials
  dependency (`guy762.MM.KotORCore`), not the weapon mod (see §3). Weapon workstream closed.
- 🔎 How Odyssey gravtech research defNames are spelled (for the techprint gate + the "no defName ending in a digit" Configurable-Techprints limit).
- ✅ **PARTLY RESOLVED (2026-08-05): raw `.rws` map GRID structure is now decoded** (terrain
  `topGridDeflate`, roof `roofsDeflate` = base64 raw-DEFLATE→LE uint16 shortHashes; things =
  `<def>/<id>/<pos>(x,0,z)`). See §2b + `Utils/Savegame_mapview.py`. READING is safe/proven;
  the remaining unknown is the fine cross-reference graph (jobs/reservations/rooms) for safe
  WRITING — still LOW priority since RimBridge is the preferred live-map WRITE route.
- 🔎 Terrain/biome shortHash→defName reversal still needs the exact load order (or live game).
  Candidate one-time helper: load the campaign mod set, dump every `TerrainDef.shortHash`.
