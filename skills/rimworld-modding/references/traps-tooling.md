# traps — our own tooling, and offline analysis

`validate_patch.py`, the live def dump, the generators, greps and censuses.

**Read this when a tool told you something and you are about to act on it.** Nearly
every entry is the same shape: **a script reported confidently, and answered a
different question than the one asked.**

What goes in, and what does not: `references/traps.md`.

---

### A live def dump has no abstracts
**Symptom:** a `--live` check flags abstract templates (`Name=` with no `defName`, e.g. `Force_LightsaberBase`) as "does not exist in the LIVE game" on a correct patch.
**Cause:** DefDatabase never registers abstract defs — they exist only to be inherited from.
**Fix:** validate only `[defName="X"]` identities against the live index; never `[@Name="X"]`.
**Recurs when:** any check treating the def dump as the set of all defs.

---

### `--defs` inherits the LIVE `ModsConfig.xml`
**Symptom:** 14 correct Ideology xpaths all report "matches 0 nodes".
**Cause:** the tool derives its load set from the live `ModsConfig.xml`. Another seat had cut it to a 3-mod spike, so Ideology was not loaded.
**Fix:** pass an explicit snapshot — `--mods-config <file>`. Read the "N active mods → M def files" line before trusting any verdict.
**Recurs when:** any tool that auto-detects "current config" in a shared tree.

---

### Resolving a mod's real file set from a workshop tree — three ways to get the count wrong
**Symptom:** three separate wrong hit-counts from the same walk. A `PatchOperationRemove` xpath reported as "matches 7 nodes, applies to ALL" where runtime matches 1; 96 defs reported with a broken `ParentName` against a clean `Player.log`; "matches 3 nodes IN ONE MOD", the same filename listed three times, runtime match 1.
**Cause:** in order — (1) a naive walk visits every version folder a mod ships, `1.0`–`1.6`, and RimWorld loads exactly one; (2) making the version folder *exclusive* then hides root-only base defs (`AdaptiveStorageBase`), because RimWorld loads root **and** versioned; (3) a resolver can correctly return root + `1.6` and a plain `os.walk` behind it still descends into `1.4/` and `1.5/`.
**Fix:** resolve the load set from `ModsConfig.xml` + `About.xml` + `LoadFolders.xml`, emit **root first then the version folder** so version overrides win, and exclude the other version folders when walking the resolved root.
**Recurs when:** any directory walk over a workshop tree. A static checker disagreeing with a clean log is the tell — the log is the measurement, the checker is the model.

---

### Vanilla textures are NOT on disk — every check for a Core texture path is blind
**Symptom:** a texture-existence check reported two Jawa `GeneDef`/`XenotypeDef` `iconPath`s as missing at ERROR level — `UI/Icons/Genes/Gene_Hair`, `UI/Icons/Xenotypes/Pigskin` — against the full 574-mod load set. Both look like ordinary Biotech paths.
**Cause:** `Data/Core`, `Data/Biotech`, `Data/Royalty`, `Data/Ideology` ship **`About/`, `Defs/` and `Languages/` only**. There is no `Textures/` folder anywhere under `Data/`; every vanilla texture lives inside a Unity asset bundle. A *correct* vanilla path and a *typo* are indistinguishable from the filesystem. A third path in the same mod, `UI/Icons/Genes/Gene_Terrified`, resolved only by accident — a Workshop mod redistributes the Ideology texture tree.
**Fix:** grade the verdict by namespace. A miss whose first path segment matches a top-level folder in the mod's **own** `Textures/` is an ERROR (nothing else can supply it). Any other miss is a WARNING that names why it cannot be decided. `validate_patch.py` detects the condition rather than assuming it: it looks for `Textures/` under the `ludeon.rimworld` mod folder and only hardens to ERROR if vanilla art really is loose.
**Recurs when:** any offline check that asks "does this game asset exist" — sounds, UI, bundles.

---

### The patch validator cannot evaluate `text()` — lxml can
**Symptom:** "xpath uses a feature this checker cannot evaluate" for `text()`, `contains()`, `starts-with()`.
**Cause:** `xml.etree.ElementTree` implements only a subset of XPath 1.0.
**Fix:** shipped — uses `lxml` when importable, ElementTree as fallback. ⚠️ **INERT until installed:** `python.exe -m pip install --user lxml`. lxml needs `remove_comments=True`, or comment nodes break code that sorts child tags as strings.
**Recurs when:** `validate_patch.py` on ops with predicates.

---

### A vanilla def's XML is not what the game loaded — read the dump, even for Core and DLC
**Symptom:** Anomaly's `Factions_Misc.xml` writes `<styles><li>Horaxian</li></styles>` for the Horax cult. The resolved def dump shows `AM_Horaxian`. Authoring a faction against the shipped XML produced a `styles` entry that does not exist at runtime, and a missing `StyleCategoryDef` is a silent no-op, not an error.
**Cause:** Alpha Memes `PatchOperationReplace`s the whole `styles` list. Vanilla XML is an *input* to the load, not a record of it — with several hundred mods active, any Core or DLC def may have been rewritten, and list-valued fields are rewritten wholesale rather than merged.
**Fix:** quote `DefDump/defs/<DefType>.json` for every defName you copy, including Core and DLC ones. Where the dump and the XML disagree, the dump is what the game has.
**Recurs when:** copying any vanilla def as a template — `FactionDef`, `PawnKindDef`, `ThingDef`, `ScenarioDef`. ⚠️ **Worst on list-valued fields** (`styles`, `memes`, `pawnGroupMakers`, `comps`), where `PatchOperationReplace` destroys the original silently and the copied name still *looks* vanilla.

---

### A generator that reads the live dump eats its own output
**Symptom:** re-running a working retune generator would revert already-retuned weapons (28→99→34), silently.
**Cause:** the live dump is post-patch, so it contains *our* values; a generator mapping old→new reads its own new value as the old one.
**Fix:** `src/RimMandrake/Utils/patch_provenance.py` — structure may come from the live dump, values may not. Anchor via `OurWrites.baseline(xpath, live_value)`; `unknown` → skip, never guess.
**Recurs when:** any generator whose input includes its own past output.

---

### The def dump is `{defType, defs, count}`, not a bare list
**Symptom:** `for d in json.load(open('ThingDef.json'))` yields string keys; `isinstance(d, dict)` is always False and the index comes out empty.
**Fix:** index `raw['defs']`. `statBases` and `description` are absent from the dump by design.
**Recurs when:** any snippet that iterates a dump file directly.

---

### `grep -c '<li>' ModsConfig.xml` counts the expansions too
**Symptom:** returns 578 where the true active count is 573.
**Cause:** `<knownExpansions>` sits beside `<activeMods>` and adds one `<li>` per DLC.
**Fix:** `ET.parse(CFG).getroot().find('activeMods')` and take its length.
**Recurs when:** any whole-file grep over a config with sibling list sections.

---

### `grep` for a packageId is case-sensitive; `ModsConfig.xml` is lowercased
**Symptom:** `grep -c "PeteTimesSix.ResearchReinvented"` returns 0 for an active mod. Grepping a workshop number returns the same false 0.
**Cause:** RimWorld lowercases packageIds on write, and the file stores packageIds only — never workshop numbers.
**Fix:** resolve the real packageId from `About.xml`'s **direct child** (the first `<packageId>` is usually a dependency), then compare casefolded against parsed `<activeMods>`.
**Recurs when:** proving a mod is absent. Validate the check against a mod known to be present first.

---

### The interpreter, not the data, rewrote 13,158 rows
**Symptom:** regenerating the offline inventory after unsubscribing one mod produces a 12,383-line diff naming mods that are still installed.
**Cause:** two effects stacked — WSL `python3` emits forward slashes where Windows `python.exe` emits backslashes, and `loadOrder` is positional, so removing one mod renumbers everything after it.
**Fix:** regenerate with `python.exe src/RimMandrake/Utils/refresh.py --offline`. Diff identity columns only (`cut -d, -f1-5`), never positional ones.
**Recurs when:** any regenerated artifact compared across interpreters.

---

### A def can exist in the game and in NO file
**Symptom:** `grep -r '<defName>CarpetMarine</defName>'` across Data, all workshop mods and local Mods returns zero — for a terrain the game, the save and the build plan all reference.
**Cause:** Core ships `Carpet` as a `TerrainTemplateDef`; `TerrainDefGenerator_Carpet.ImpliedTerrainDefs()` generates one `TerrainDef` per structure `ColorDef` at load.
**Fix:** confirm against the live dump or `jawa/get_def` before calling a def absent.
**Recurs when:** any `Implied*Defs` generator — the mirror image of abstracts: in the dump, never in the XML.

---

### A deploy check compared the commit, not the tool surface
**Symptom:** `src/RimMandrake/bridgetools/build.py` says "built from a DIFFERENT COMMIT… deploy to make them agree". Running `--apply` would have silently deleted `jawa/fire_incident` and `jawa/send_letter`, because the default build has `--gm` off while the deployed DLL had it on.
**Cause:** the check compares commit SHA (provenance); the risk is in tool surface (capability). A dirty-tree build also stamps HEAD's SHA while containing uncommitted code, so SHA equality never proved the bytes either.
**Fix:** `tool_surface()` diffs `jawa/*` names in the artifact; `--apply` refuses any tool-count reduction without `--allow-tool-removal`.
**Recurs when:** any "is this the same code" check — compare the artifact, never a stamp.

---

### A field xref must match all SIX CIL field opcodes, or every save/load path is invisible
**Symptom:** `xref.py Thing debugRotLocked` returned "REFERENCED BY 3 methods" — `set_Rotation` and two debug-action closures — and omitted `Thing::ExposeData`, the method that makes the flag survive a save and load.
**Cause:** the scanner matched `ldfld` (0x7B), `stfld` (0x7D) and `ldsfld` (0x7E) only. The missing three are `ldflda` (0x7C), `ldsflda` (0x7F) and `stsfld` (0x80). **`ldflda` takes the field's ADDRESS, which is how `Scribe_Values.Look(ref x, …)` reaches a field.**
**Fix:** match all six and annotate each hit with the opcodes it used — `[ldfld]` is a reader, `[ldfld, stfld]` a writer. Count method bodies that fail to parse and print the count; a silent skip reads as a missing caller.
**Recurs when:** any byte-pattern scan over IL, and equally any `strings`-based census — matching a subset of the encodings a fact can take yields a confident wrong answer, never an error.

---

### `jawa/get_def` returns `extra: null` for def types it does not model, and it reads as "absent"
**Symptom:** `jawa/get_def MapGeneratorDef Base_Player` came back `success: true` with `extra: null`. Searching the response for a genStep defName found nothing, which reads as "our genStep is not registered".
**Cause:** the bridge models `extra` for some def types (`BiomeDef` returns full `terrainPatchMakers`) and not others. A type it does not model returns `null`, not an error and not an empty list.
**Fix:** answer genStep membership from `DefDump/defs/MapGeneratorDef.json`, which carries the real `genSteps`. Treat `extra: null` as "not answered", never as "not present".
**Recurs when:** any `jawa/get_def` call whose conclusion is a NEGATIVE — absent field, missing entry, unregistered def.

---

### A grep over `Data/` proves no shipped def uses a field — never that the engine ignores it
**Symptom:** `JawaScrapfields.xml` omitted `clusterSize` on the reasoning that it has "zero hits for clusterSize" across the whole `Data/` tree and so is "a field the engine does not read on this class".
**Cause:** `Data/` holds only the defs Ludeon shipped. `Verse.GenStep_ScatterThings` declares `[public] int clusterSize`, plus private `clusterCenter`, `leftInCluster` and a static `ClusterRadius` — the engine reads it; no shipped def happens to set it.
**Fix:** answer "does the engine read this field" from the assembly (`ilprobe/meta.py <Type>`), never from a grep over defs. A def-tree grep answers a different question: is there precedent.
**Recurs when:** any decision to omit an XML field, or to call one unsupported, that rests on a grep over `Data/` or the Workshop tree rather than on the class's field list.

---

### A `timeout`-wrapped scan that gets killed leaves a PARTIAL result that looks complete
**Symptom:** `timeout 100 grep -rl QuestScriptDef <workshop>/ --include=*.xml` returned 75 files across 14 mods and exited without complaint. The real answer was **368 files across 64 mods** — all three Vanilla Quests Expanded modules were among the missing, and the census built on it would have been wrong by a factor of four.
**Cause:** `timeout` kills the child and the pipeline still exits cleanly, so a truncated stdout is indistinguishable from a finished one. This mount runs ~210 files/sec against ~1,246 mods, so any fixed wall-clock cap over the workshop tree is a coin flip on completeness.
**Fix:** assert a **known positive** is present before believing the result, and prefer `grep -rl` narrowing plus a background run over a wall-clock cap. Report the count you *scanned* alongside the count you matched. ⚠️ `head -5` on the pipeline cuts it a second time and only one cut is yours.
**Recurs when:** any bounded sweep over the Workshop tree, the game `Data/` tree or the def dump. **Version folders compound it:** a mod shipping 1.0–1.6 inflates its own count 3–8x, so a truncated scan can be both short AND double-counted.

---

### Suppress, scope, then delete — a setting and a def-removal are not interchangeable
**Symptom:** twenty-one Cherry Picker keys were written to stop Anomaly content appearing. Every one was redundant, **and** they would have deleted the asset library the owner had ruled must stay reachable for reskinning.
**Cause:** Anomaly's own `Disabled` playstyle already suppresses incidents, study, the threat budget, thing-sets and trader stock — the whole observable outcome, with every def still loaded. A deletion reaches the same observable outcome and takes the def and everything downstream of it.
**Fix:** before writing any removal list, check what the shipped setting already covers; the answer is frequently "all of it". Then ask whether the def is a donor, a reskin target, or referenced by another mod. Scoping beats deleting for the same reason — a per-planet-type biome blacklist leaves every quest and background-biome reference resolving, where deleting the `BiomeDef` breaks them.
**Recurs when:** any suppression task where a config toggle and a def-removal tool both exist — biomes (planet-type blacklist vs deleting the `BiomeDef`), factions (worldgen page vs removing the `FactionDef`), incidents (`baseChance 0` vs deleting the `IncidentDef`).

---

### The two primary RimWorld documentation domains both 403 `WebFetch`
**Symptom:** `WebFetch` against `rimworldwiki.com` and `ludeon.com` returns 403, which looks like "there is no documentation" rather than "the fetch was refused".
**Cause:** those hosts refuse the fetcher, not the request.
**Fix:** `curl -sL https://r.jina.ai/<url>` gets through. ⚠️ **Check the date before spending the read** — the only two quest-authoring tutorials are an undated wiki page marked "Under Review" and a 2021 wiki written for **1.3**. Four of their claims are false on 1.6: `isRootRandomSelected`, `NaturalRandomQuestChance` and `QuestPointsCurve` are **absent from the assembly** (the live field is `randomlySelectable`), and copying a Vanilla Expanded quest def wholesale yields a quest that never fires, because VE sets no `rootSelectionWeight` and schedules through a VEF mod extension.
**Recurs when:** any web research on RimWorld internals. **The def dump is the current documentation** — `DefDump/defs/<DefType>.json` is generated by the running 1.6 game, and the assembly is the arbiter for whether a field exists at all. Treat an undated page as pre-1.4.
