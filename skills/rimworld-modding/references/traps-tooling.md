# traps — our own tooling, and offline analysis

`validate_patch.py`, the live def dump, the generators, greps, censuses and the Drive mount.

**Read this when a tool told you something and you are about to act on it.** Nearly
every entry is the same shape: **a script reported confidently, and answered a
different question than the one asked.**

Admission test and entry format: `references/traps.md`.

---

### A live def dump has no abstracts
**Symptom:** a `--live` check flags abstract templates (`Name=` with no `defName`, e.g. `Force_LightsaberBase`) as "does not exist in the LIVE game" on a correct patch.
**Cause:** DefDatabase never registers abstract defs — they exist only to be inherited from.
**Fix:** validate only `[defName="X"]` identities against the live index; never `[@Name="X"]`.
**Recurs when:** any check treating the def dump as the set of all defs.

### `--defs` inherits the LIVE `ModsConfig.xml`
**Symptom:** 14 correct Ideology xpaths all report "matches 0 nodes".
**Cause:** the tool derives its load set from the live `ModsConfig.xml`. Another seat had cut it to a 3-mod spike, so Ideology was not loaded.
**Fix:** pass an explicit snapshot — `--mods-config <file>`. Read the "N active mods → M def files" line before trusting any verdict.
**Recurs when:** any tool that auto-detects "current config" in a shared tree.

### Workshop-tree scans count every version folder a mod ships
**Symptom:** validator says a `PatchOperationRemove` xpath "matches 7 nodes, applies to ALL"; the true runtime count is 1.
**Cause:** a naive walk visits `1.0`–`1.6`; RimWorld loads exactly one.
**Fix:** resolve the load set from `ModsConfig.xml` + `About.xml` + `LoadFolders.xml` before counting.
**Recurs when:** any directory walk over a workshop tree.

### The version-folder fix over-corrected and hid 667 root defs
**Symptom:** 96 defs appear to have a broken `ParentName`, but `Player.log` is clean and the mods work.
**Cause:** the fix above made the version folder *exclusive*, so root-only base defs (`AdaptiveStorageBase`) vanished. RimWorld loads root **and** versioned.
**Fix:** emit both, root first so version overrides win.
**Recurs when:** a static checker disagrees with a clean log — trust the log, suspect the checker.

### A validator honouring `LoadFolders.xml` can still triple-count
**Symptom:** "matches 3 nodes IN ONE MOD", the same filename listed three times; runtime match is 1.
**Cause:** the resolver correctly returns root + `1.6`, but the file walker is a plain `os.walk` that then descends into `1.4/` and `1.5/`.
**Fix:** exclude other version folders when walking a resolved root.
**Recurs when:** a recursive walk re-admits candidates the resolver already rejected.

### Vanilla textures are NOT on disk — every check for a Core texture path is blind
**Symptom:** a texture-existence check reported two Jawa `GeneDef`/`XenotypeDef` `iconPath`s as missing — `UI/Icons/Genes/Gene_Hair`, `UI/Icons/Xenotypes/Pigskin` — against the full 574-mod load set, at ERROR level. Both look like ordinary Biotech paths.
**Cause:** `Data/Core`, `Data/Biotech`, `Data/Royalty`, `Data/Ideology` ship **`About/`, `Defs/` and `Languages/` only**. There is no `Textures/` folder anywhere under `Data/`; every vanilla texture lives inside a Unity asset bundle. So a *correct* vanilla path and a *typo* are indistinguishable from the filesystem, and the confident answer is the wrong one. A third path in the same mod, `UI/Icons/Genes/Gene_Terrified`, resolved only by accident — a Workshop mod redistributes the Ideology texture tree.
**Fix:** grade the verdict by namespace. A miss whose first path segment matches a top-level folder in the mod's **own** `Textures/` is an ERROR (nothing else can supply it). Any other miss is a WARNING that says why it cannot be decided. `validate_patch.py` detects the condition rather than assuming it: it looks for `Textures/` under the `ludeon.rimworld` mod folder and only hardens to ERROR if vanilla art really is loose.
**Generalises to:** any offline check that asks "does this game asset exist" — sounds, UI, bundles. **The absence of a file is only evidence when you have established the file would have been there.** Measured 2026-08-13.

### Blanket find-and-replace eats the markup syntax it lives inside
**Symptom:** three instances in one session — replacing `->` also hit the `-->` comment terminator; a pasted `--->` closed a real comment early; escaping `<li>` in prose also hit the real `<li>1.6</li>` in `<supportedVersions>`.
**Cause:** markup is self-similar; the string you are escaping is also structural syntax elsewhere.
**Fix:** scope the edit to one region (extract → transform → reinsert). Parse **every** XML in the mod folder afterwards, `About.xml` included. Since 2026-08-13 `validate_patch.py <mod root>` does exactly that: `<Patch>`, `<Defs>` and `About.xml` each get the checks that fit them, instead of every def file being reported as "expected `<Patch>`".
**Recurs when:** any sed or find-and-replace across a markup file.

### The patch validator cannot evaluate `text()` — lxml can
**Symptom:** "xpath uses a feature this checker cannot evaluate" for `text()`, `contains()`, `starts-with()`.
**Cause:** `xml.etree.ElementTree` implements only a subset of XPath 1.0.
**Fix:** shipped — uses `lxml` when importable, ElementTree as fallback. ⚠️ **INERT until installed:** `python.exe -m pip install --user lxml`. lxml needs `remove_comments=True`, or comment nodes break code that sorts child tags as strings.
**Recurs when:** `validate_patch.py` on ops with predicates.

### A generator that reads the live dump eats its own output
**Symptom:** re-running a working retune generator would revert already-retuned weapons (28→99→34), silently.
**Cause:** the live dump is post-patch, so it contains *our* values; a generator mapping old→new reads its own new value as the old one.
**Fix:** `src/RimMandrake/Utils/patch_provenance.py` — structure may come from the live dump, values may not. Anchor via `OurWrites.baseline(xpath, live_value)`; `unknown` → skip, never guess.
**Recurs when:** any generator whose input includes its own past output.

### `stat()` on the Drive mount returns a stale size
**Symptom:** a freshly written zip reads 62,505 bytes via `stat()`; `git add` stages 62,956 — a delta matching CRLF corruption exactly.
**Cause:** `G:` is a Google Drive mount; directory-entry metadata lags the write. The bytes were fine.
**Fix:** hash or read bytes to verify a write on `G:`. Never trust `st_size` there.
**Recurs when:** deploy diffing, or any "did the file change" check on a network mount.

### The def dump is `{defType, defs, count}`, not a bare list
**Symptom:** `for d in json.load(open('ThingDef.json'))` yields string keys; `isinstance(d, dict)` is always False and the index comes out empty.
**Fix:** index `raw['defs']`. `statBases` and `description` are absent from the dump by design.
**Recurs when:** any snippet that iterates a dump file directly.

### A grep for a mod's name matches the mod working perfectly
**Symptom:** triage flags `RimAI` RED with 5 hits on a load where it is healthy — the hits are `SettingsManager: Initialized successfully` and `All Parts Boot OK`.
**Cause:** the check greps the mod's name and expects zero, which only holds for mods that are silent when healthy.
**Fix:** match failure *signatures* — `RimAI\.Core.*Exception|assembly RimAI`.
**Recurs when:** any log-triage rule keyed on a mod name.

### Parallel `find` into one redirect corrupted the index
**Symptom:** a texture sweep reports 80 broken textures; the real number is 8, and every phantom names a file that exists.
**Cause:** `xargs -P 16` with 16 workers writing to one shell redirect; concurrent writes interleave and splice paths — ~1.6% of 56,947 lines.
**Fix:** one output file per worker, concatenated after.
**Recurs when:** any parallel pipeline sharing a single redirect.

### `grep -c '<li>' ModsConfig.xml` counts the expansions too
**Symptom:** returns 578 where the true active count is 573.
**Cause:** `<knownExpansions>` sits beside `<activeMods>` and adds one `<li>` per DLC.
**Fix:** `ET.parse(CFG).getroot().find('activeMods')` and take its length.
**Recurs when:** any whole-file grep over a config with sibling list sections.

### `grep` for a packageId is case-sensitive; `ModsConfig.xml` is lowercased
**Symptom:** `grep -c "PeteTimesSix.ResearchReinvented"` returns 0 for an active mod. Grepping a workshop number returns the same false 0.
**Cause:** RimWorld lowercases packageIds on write, and the file stores packageIds only — never workshop numbers.
**Fix:** resolve the real packageId from `About.xml`'s **direct child** (the first `<packageId>` is usually a dependency), then compare casefolded against parsed `<activeMods>`.
**Recurs when:** proving a mod is absent. Validate the check against a mod known to be present first.

### A self-matching hash check green-lit 14 deletions
**Symptom:** a dedup check before deleting 14 files reports all 14 `DUPLICATE`, each naming *itself* as the safe copy.
**Cause:** the keep-set glob swept in the deletion targets.
**Fix:** build the keep-set only from where the shipped product lives, excluding targets by construction. Print *what* a match matched.
**Recurs when:** any dedup whose source and target globs can overlap. A unanimous, instant, hoped-for result is suspicious.

### One wrong operator became a week-long "impossible" claim
**Symptom:** two docs stated for a week that a save's `shortHash` cannot be reversed to a defName offline.
**Cause:** the probe used `StableStringHash & 0xFFFF`; RimWorld's formula is `(ushort)(StableStringHash(name) % 65535)`.
**Fix:** verified against the dump's own `shortHash` — BiomeDef 66/66, RoofDef 6/6, TerrainDef 1227/1238.
**Recurs when:** the dump already holds ground truth. Check against it before declaring anything impossible.

### `ls -la` columns mean different things per row
**Symptom:** an awk filter on the month column counts 15 "frozen pre-2026" files; the true count is 9.
**Cause:** `ls` prints a year for old files and a time for recent ones, sharing the month column — `Feb` matches both years.
**Fix:** `os.path.getmtime()` and bucket by real year. Never parse `ls` for dates.
**Recurs when:** any shell parse of `ls` output.

### A deploy check compared the commit, not the tool surface
**Symptom:** `src/RimMandrake/bridgetools/build.py` says "built from a DIFFERENT COMMIT… deploy to make them agree". Running `--apply` would have silently deleted `jawa/fire_incident` and `jawa/send_letter`, because the default build has `--gm` off while the deployed DLL had it on.
**Cause:** the check compares commit SHA (provenance); the risk is in tool surface (capability). A dirty-tree build also stamps HEAD's SHA while containing uncommitted code, so SHA equality never proved the bytes either.
**Fix:** `tool_surface()` diffs `jawa/*` names in the artifact; `--apply` refuses any tool-count reduction without `--allow-tool-removal`.
**Recurs when:** any "is this the same code" check — compare the artifact, never a stamp. `harvest_log.py` took three fixes to close the same defect: mtime alone, then mod-count alone, then count **+** a time anchor.

### The interpreter, not the data, rewrote 13,158 rows
**Symptom:** regenerating the offline inventory after unsubscribing one mod produces a 12,383-line diff naming mods that are still installed.
**Cause:** two effects stacked — WSL `python3` emits forward slashes where Windows `python.exe` emits backslashes, and `loadOrder` is positional, so removing one mod renumbers everything after it.
**Fix:** regenerate with `python.exe src/RimMandrake/Utils/refresh.py --offline`. Diff identity columns only (`cut -d, -f1-5`), never positional ones.
**Recurs when:** any regenerated artifact compared across interpreters.

### A def can exist in the game and in NO file
**Symptom:** `grep -r '<defName>CarpetMarine</defName>'` across Data, all workshop mods and local Mods returns zero — for a terrain the game, the save and the build plan all reference.
**Cause:** Core ships `Carpet` as a `TerrainTemplateDef`; `TerrainDefGenerator_Carpet.ImpliedTerrainDefs()` generates one `TerrainDef` per structure `ColorDef` at load.
**Fix:** confirm against the live dump or `jawa/get_def` before calling a def absent.
**Recurs when:** any `Implied*Defs` generator — the mirror image of abstracts: in the dump, never in the XML.

### "Empty output" is not a result
**Symptom:** four instances in one session — a silent compile probe read as "compiles clean" (it had failed on a wrong `dotnet` path, filtered out by grep); a push-retry loop found no "rejected" string and reported success while still unpushed; a subagent reported "clean, empty output" when the file had not been written yet; an unquoted `--include=*.xml` was glob-expanded by zsh.
**Cause:** absence of output read as a negative result, when it meant "not finished", "not run", or "asked the wrong question".
**Fix:** assert on a positive success token (`grep -q "Build succeeded"`), never the absence of a negative one. Wait on a completion marker the producer writes. Quote globs.
**Recurs when:** any check whose pass condition is silence.

### `len()` answers for any container, so the wrong number is plausible
**Symptom:** a build plan reported 36 calls (6 foundation + 4 terrain + 26 spawn); the real total is 31 — foundation is ONE call.
**Cause:** `foundation` is a dict of 6 fields, so `len()` returned the field count. `terrain` and `spawn` really are lists, so the same expression was right twice and wrong once, with no error.
**Fix:** check the type before counting.
**Recurs when:** sibling keys accessed uniformly but not of uniform type.

### A field xref that scans three opcodes reports "no writers" for a field with writers
**Symptom:** `xref.py Thing debugRotLocked` returned "REFERENCED BY 3 methods" — `set_Rotation` and the two debug-action closures — and omitted `Thing::ExposeData`, the method that makes the flag survive a save and load.
**Cause:** the scanner matched `ldfld` (0x7B), `stfld` (0x7D) and `ldsfld` (0x7E) only. CIL has six field opcodes; the missing three are `ldflda` (0x7C), `ldsflda` (0x7F) and `stsfld` (0x80). **`ldflda` takes the field's ADDRESS, which is how `Scribe_Values.Look(ref x, …)` reaches a field — so every save/load path in the game was invisible to the tool.**
**Fix:** match all six, and annotate each hit with which opcodes it used — `[ldfld]` is a reader, `[ldfld, stfld]` is a writer, and "three readers, no writer" is a different claim from "three methods touch it". Count method bodies that fail to parse and say so; a silent skip is a missing caller the reader will believe does not exist. Fixed in `90f1c62`.
**Recurs when:** any byte-pattern scan over IL. The failure is silent and one-directional — it can only ever under-report, and a short list reads exactly like a complete one. Applies equally to `strings`-based def and tool censuses: matching a subset of the encodings a fact can take yields a confident wrong answer, never an error.

### An artifact that records an OUTCOME cannot answer a question about a CAPABILITY
**Symptom:** five confirmed instances in two days, each a tool answering confidently — "does this mod ship X?" put to the def dump, "does this mod support X?" put to a `Mod_*.xml`.
**Cause:** the def dump records what the game **loaded**, not what a mod **ships**. A `Mod_*.xml` records what was **changed**, not what is **supported**. Both are outcomes standing in for a capability, and the substitution is invisible because the field exists and holds a plausible value.
**Fix:** to know what something CAN do, read the thing that **defines** it. Before trusting any comparison, answer two questions — (1) *what artifact does this compare?* (2) *what can that comparison NOT distinguish?* Question 2 is operational: construct the case where the thing changes and your field does not. Cannot build one → it is a gate. Can → it is a proxy in the artifact's clothes.
**Recurs when:** any check whose input is a dump, a log, a diff or a settings file rather than the source. ⚠️ Naming the failure shape does not inoculate the document that names it — three agents hit this in one evening, each while holding the lesson.

### Take the RULE from a precedent, never the NUMBER
**Symptom:** the only shipped example ships **90 `HiddenConduit` / 50 `PowerConduit`**, and matching that 64%-hidden split was recommended for our ship. Ours came out **1 hidden / 184 exposed**.
**Cause:** the precedent is a small dense ship where conduit runs under rooms; ours is a long open keel with almost nothing on it. The ratio is an artifact of density, not a design rule — real field, authoritative source, **wrong instance**. The mirror image of the entry above, which is a wrong *field*.
**Fix:** implement the rule instead — hidden wherever a keel tile carries a building or node, exposed otherwise, with a selftest asserting no node sits on exposed conduit. Before copying a figure from a precedent ask *what produced this number, and is that thing true here?* If it is a density, scale or workload artifact, take the rule and recompute the number.
**Recurs when:** any figure lifted from a shipped example, a benchmark run, or another mod's defs. A number from a valid source is only valid under that source's conditions.

### A blind string replace becomes an ABORT INSTRUCTION when it crosses into a filename or an expected observation
**Symptom:** a rename sweep across 18 docs turned `Directorate` into `Galactic Empire` everywhere it appeared. Most hits were prose and harmless. Two were not: a **filename** (`ImperialDesertDirectorate.xml` → `ImperialDesertGalactic Empire.xml`, a file that cannot exist) and an **expected-observation string** in an operator checklist, which then read *"STOP before generating unless the label says 'Imperial Desert Galactic Empire'"* — a string nothing in the game can produce. **It had propagated into a second, independent file before anyone noticed.** The instruction it created was: abort a correct, irreversible world generation.
**Cause:** the sweep was written for prose and applied to everything. In prose a wrong word is cosmetic and self-correcting — a reader shrugs. **In a path it is a file that does not exist, and in an expected observation it is a gate that can never pass.** Both convert silently from "slightly wrong wording" into "do not proceed", and neither looks wrong in a diff, because the replacement is exactly the string you asked for.
**Fix:** before any multi-file replace, **grep the target string for the two contexts that are not prose** — `grep -n '<term>' | grep -iE '\.xml|\.md|/|expect|must (read|say)|label reads'` — and hand-edit those. Afterwards, re-grep the *replacement* for `\.xml` and for double articles (`the the`, `a a`), which are the fingerprints of a substitution that landed mid-phrase. **A sweep is finished when you have read its hits, not when the command exits 0.**
**Recurs when:** any rename that touches operational files as well as design ones — checklists, expected-failure lists, deploy plans, queue items citing paths. ⚠️ **The danger scales with how operational the file is**, and design seats sweep design files by habit, which is exactly how it reaches a checklist nobody thought they were editing. **Generalises to** any find-and-replace over a mixed tree: prose forgives, paths and assertions do not.

### A SETTING that suppresses behaviour and a DELETION that removes the def are not interchangeable
**Symptom:** twenty-one Cherry Picker keys were written to stop Anomaly content appearing — and every one was redundant, because the DLC's own `Disabled` playstyle already suppresses incidents, study, the threat budget, thing-sets and trader stock. Worse, the deletions would have destroyed the exact asset library the owner had just ruled must stay reachable for reskinning. **Two levers pointed at the same outcome; only one of them was reversible.**
**Cause:** both levers produce the same *observable* result — the thing stops appearing — so they read as alternatives with different costs. They are not alternatives. **A setting changes behaviour and preserves the def; a deletion removes the def and everything downstream of it, including uses you have not thought of yet.** The failure is invisible at the moment of choosing because the goal, stated as "make X stop happening", is satisfied by either.
**Fix:** before writing any removal list, ask **"is there a setting that already does this?"** — and check what that setting *already covers*, since the answer is frequently "all of it". Then ask the second question: **"do I need this def to still exist for anything else?"** A donor asset, a reskin target, a def another mod references. **Prefer the setting whenever both reach the goal**, on two grounds: it is reversible, and it keeps the asset.
**Recurs when:** any suppression task where a config toggle and a def-removal tool both exist — biomes (a planet-type blacklist versus deleting the `BiomeDef`), factions (the worldgen page versus removing the `FactionDef`), incidents (`baseChance 0` versus deleting the `IncidentDef`). ⚠️ **Scoping beats deleting for the same reason:** a per-planet-type biome blacklist leaves every quest and background-biome reference resolving, where deleting the def breaks them. **Generalises to** every "turn X off" request: *suppress, scope, then delete — in that order, and usually you stop before the third.*

### `strings` scans 7-bit ASCII, so a deployed message reads as ABSENT
**Symptom:** `strings -a "<mod>.dll" | grep -F "No target. jawa/damage takes"` returned nothing on a DLL that demonstrably contained that literal. The fix was recorded as "built, NOT deployed", queued for a shutdown window, and **carried as fact for a day** — while it had been live in the game copy the whole time. What made it convincing is that the *same command in the same run* found `jawa/order_pawn`, `spawnedCount` and `countAllIncludingHidden`, so the scan looked like it was working.
**Cause:** a .NET assembly stores those two kinds of string in two heaps with two encodings. **Metadata names** — types, methods, fields, and attribute arguments such as a tool's registered name — are UTF-8 in `#Strings`, which a 7-bit scan reads fine. **Method-body literals** — every message, refusal and error text — are UTF-16LE in `#US`, where each character is followed by a NUL byte, and plain `strings` sees no run long enough to print. Which heap a string lands in is decided by whether it is an attribute argument or a code literal, **never by what you happen to be verifying**, so the working half and the blind half sit side by side in one output.
**Fix:** `strings -a -el` for any message, and run **both** scans on a mixed check. State the claim to match what you actually ran: `strings -a` proves a **tool NAME** shipped; only `strings -a -el` proves a **message** shipped. ⚠️ Neither proves behaviour — a name present in the binary says the method was compiled in, not that it works. When the fix has a distinctive literal, that literal is the cheapest deploy proof there is; when it does not, add one.
**Recurs when:** any binary-verification shortcut on a managed assembly — confirming a deploy, dating a build, checking whether a patch shipped, `grep`ping an assembly for a defName. ⚠️ **Re-bit on 2026-08-13 with this entry already written in the rimbridge skill**, which is why it now lives here too: it recurs because the failure is a *silent absence*, and absence is what you were looking for. Full worked case: `skills/rimbridge/references/traps.md`. **Generalises to** every text scanner with an implicit encoding assumption — `grep` over UTF-16 logs, `strings` over any wide-char binary, an ASCII search of a resource blob. **A negative from a tool that cannot see the encoding is not evidence of absence.**

### `jawa/get_def` returns `extra: null` for def types it does not model, and it reads as "absent"
**Symptom:** `jawa/get_def MapGeneratorDef Base_Player` came back `success: true` with `extra: null`. Searching the response for a genStep defName found nothing, which reads as "our genStep is not registered" — a defect about to be filed against the wrong seat.
**Cause:** the bridge models `extra` for some def types (`BiomeDef` returns full `terrainPatchMakers`) and not others. A type it does not model returns `null`, not an error and not an empty list.
**Fix:** answer genStep membership from the def dump (`DefDump/defs/MapGeneratorDef.json`), which carries the real `genSteps`. Treat `extra: null` as "not answered", never as "not present".
**Recurs when:** any `jawa/get_def` call whose conclusion is a NEGATIVE — absent field, missing entry, unregistered def.
