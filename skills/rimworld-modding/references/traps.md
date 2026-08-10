# traps.md — the running log of earned lessons

Every entry here cost a real debug cycle. Read this at the start of a RimWorld
task; append to it at the end of one. Format and promotion rules are in
SKILL.md §9 — the short version is that an entry earns its place by naming the
**class of situation it recurs in**, and once it would change default behaviour
it gets promoted into the skill body and deleted from here.

**Already promoted into SKILL.md — do not re-log these:** `--` forbidden in XML
comments · `PatchOperationRemove` deletes every match · `MayRequire` checks the
mod not the def · `GameComponent` needs `(Game game)` · `modDependency` does not
imply load order · exceptions in `ExecuteToExecuteWhenFinished` abort the
post-load queue · compatibility patches must load last · read the `wanter` before
calling an unresolved cross-reference benign · `LoadFolders.xml` makes a mod's def
set depend on the whole mod list · the validator cannot see patch-created nodes
and does not check `Defs/`.

---

### The same mod stayed dead through two correct fixes, for three different reasons
_2026-08-10 · Choose Wild Animal Spawns, across three consecutive loads_

**Symptom:** `Error in static constructor of ChooseWildAnimalSpawns.Main`, three
loads running, always thrown from `BiomeDef.CommonalityOfAnimal`. Twice in a row
it was the *identical* exception type at the *identical* stack frame:
`ArgumentNullException: Value cannot be null. Parameter name: key`.

**Cause:** three unrelated bugs that happen to converge on one line of engine
code — `cachedAnimalCommonalities.Add(key, value)`.

| Load | Exception | What was actually wrong |
|---|---|---|
| 1 | `ArgumentException` duplicate key | `Armadillo` registered from both directions |
| 2 | `ArgumentNullException` key | the **BiomeDef** was null (our own `<li>` bug) |
| 3 | `ArgumentNullException` key | the **PawnKindDef** was null (a dangling `wildAnimals` entry) |

**Fix:** each one separately. The third was five unresolved `BiomeAnimalRecord`
entries injected by a compat patch guarded on the mod rather than the def.

**Generalises to:** the existing lesson was "an exception that changes *type* at
the same frame is a different bug." That is too weak. **An exception that keeps
the same type at the same frame can also be a different bug** — a single
`Dictionary.Add` is reachable from every source that feeds the dictionary, so the
frame identifies the *victim*, never the cause. Chasing "is it still broken?"
across loads is the wrong question; the right one is "what is null *this* time,
and who put it there." Diff the surrounding evidence between loads instead of
comparing the exception line, and never assume a re-appearing error is the old
one persisting just because a fix landed in the same area.

---

### Scanning a Workshop tree for defs counts every version folder a mod ships
_2026-08-10 · found when our own validator gave dangerous advice_

**Symptom:** `validate_patch.py` reported that a `PatchOperationRemove` xpath
"matches 7 nodes and this operation applies to ALL of them", and advised adding a
positional predicate like `[1]`. At runtime the true count is **1**.

**Cause:** the scan walked `steamapps/workshop/content/294100` and parsed every
`Defs/**.xml` under it — 33,173 files. Beasts of the Rim ships seven version
folders, `1.0` through `1.6`, each with its own `Races_Animal_Armadillo.xml`.
RimWorld loads exactly one of them. The other six are inert files on disk that
only an offline tool can see. Inactive mods were being counted too.

**Fix:** scope the scan to the real load set — parse `ModsConfig.xml` for the
active packageIds, map each to its folder via `About/About.xml`, and resolve
which subfolder supplies defs through `LoadFolders.xml` (honouring both
`IfModActive` and `IfModNotActive`), falling back to `<moddir>/<version>`. Report
matches grouped by mod so a genuine two-mods-define-this case stays visible.

**Generalises to:** any offline analysis of a game's content directory. The
filesystem is a superset of the load set, usually by a large factor, and the gap
is not random — it is concentrated in exactly the mods that have been around long
enough to accumulate version folders, which are also the popular ones you are
most likely to be patching. **A tool that over-counts is worse than one that does
not count**, because a confident wrong number gets acted on: here it recommended
a change that would have made a correct destructive patch wrong. Before trusting
any "how many things match" figure, ask which population it was computed over.

---

### An `<li>` written into a dictionary-keyed field deleted seven biomes
_2026-08-10 · found in our own patch, one restart after shipping it_

**Symptom:** three Core biomes and four modded ones stopped existing. ~950
`Could not resolve cross-reference: No RimWorld.BiomeDef named Desert/
AridShrubland/ExtremeDesert/ZBiome_Badlands/… found to give to
AnimalBiomeRecord`, plus `Failed to find RimWorld.BiomeDef named Desert. There
are 59 defs of this type loaded.` Choose Wild Animal Spawns died again — but with
`ArgumentNullException: Value cannot be null. Parameter name: key` from
`BiomeDef.CommonalityOfAnimal`, where the *previous* load had thrown
`ArgumentException: duplicate key` from the same line.

The only honest evidence pointing at the cause was seven quiet lines:
`Could not resolve cross-reference: No Verse.WeatherDef named li found to give to
RimWorld.WeatherCommonalityRecord` — one per patched biome.

**Cause:** our patch added weather in list form,
`<li><weather>SW_Sandstorm</weather><commonality>8</commonality></li>`, but
`<baseWeatherCommonalities>` is dictionary-keyed: `<Clear>18</Clear>`. The engine
read the element name `li` as the WeatherDef name, failed, and discarded the
entire BiomeDef. Everything downstream that referenced those biomes then had a
null where a BiomeDef should be.

**Fix:** `<SW_Sandstorm>8</SW_Sandstorm>`. Verified against Core's
`Biomes_WarmArid.xml` and against the modded biomes too — the shape is set by the
field's C# type, so it is identical in every mod. Also promoted a value-shape
check into `validate_patch.py`, which compares `<value>`'s children against the
live node's existing children.

**Generalises to:** three things, and the third is the one that matters.

1. Shape errors in a `<value>` are **destructive, not inert**. Every other patch
   mistake in this log fails to apply; this one deletes working content. Check
   the node's existing children before every Add or Replace.
2. A crash that changes its *exception type* at the same stack frame
   (`ArgumentException` → `ArgumentNullException`) is a different bug, not the
   old one persisting. Read the type, not just the location — the temptation is
   to conclude "still broken" and re-fix what you already fixed.
3. **A fix can be correct and still make things worse.** The animal patch worked
   exactly as designed; the damage came from an older, unvalidated file that
   shipped alongside it in the same mod folder. When deploying a mod, validate
   *everything in the folder*, not just the file you changed — the blast radius
   is the mod, not the diff.

---

### An animal registered into a biome from both directions crashes the biome's animal table
_2026-08-10 · found while auditing 1,168 animals across a 562-mod stack_

**Symptom:** `System.ArgumentException: An item with the same key has already
been added. Key: Armadillo`, thrown from `BiomeDef.CommonalityOfAnimal`. Three
unrelated mods broke at once and none of them was the cause: Choose Wild Animal
Spawns died in its static constructor, Giddy-Up logged "error calling
AllWildAnimals … Skipping", and Biome Compatibility Project threw inside the
post-load queue and took the rest of the queue with it.

**Cause:** an animal can reach a biome two ways — the biome's `<wildAnimals>`
list, or the animal's `<race><wildBiomes>` list. Both paths `Add()` into one
dictionary keyed on PawnKindDef. Same animal + same biome from both sides =
duplicate key. Here, Beasts of the Rim redefined vanilla `Armadillo` and added
`wildBiomes` entries for biomes Core already listed it in; separately, the Titans
mod listed `TropicalSwamp` **twice inside its own** `wildBiomes`.

**Fix:** remove the **animal side** (`<wildBiomes>`), never the biome side. The
biome's own list keeps the animal spawning there at the biome's commonality, so
nothing is lost. For the self-duplicate, `.../TropicalSwamp[2]` with the same
predicate in the conditional test.

**Generalises to:** any engine field that is a `Dictionary<Def, X>` populated
from two directions — the exception names the *key*, never the mod, so the log
gives you no attribution. When three mods break simultaneously with an error none
of them own, suspect shared engine state rather than any of the three. Detect
these ahead of time by cross-referencing both directions offline; a
duplicate-scan across all animal and biome defs takes seconds and found exactly
three bad pairs in a stack of 1,168 animals.

---

### A blanket find-and-replace to fix XML comments corrupted every comment terminator
_2026-08-10 · found while fixing `--` inside comments_

**Symptom:** after replacing `->` with `=>` across a patch file to remove double
hyphens, the file parsed even worse. Every `-->` had become `-=>`.

**Cause:** the comment *terminator* contains the arrow you're replacing.

**Fix:** rewrite the file cleanly rather than pattern-replacing into it. Use
`===` for separator rules and the word "to" or `→` for arrows, then validate with
a real parse plus an explicit check that no comment body contains `--`.

**Generalises to:** any automated edit whose search string is a substring of the
syntax it lives inside. Before a blanket replace in markup, ask what the pattern
collides with structurally — and prefer a parse-and-rewrite over a text
substitution whenever the file has a grammar.

---

### RimSort sort rules saved into Community Rules vanish silently
_2026-08-10 · found while forcing a framework to load before its consumer_

**Symptom:** a load-order rule was created and appeared to save; on reopening it
was gone, and the load order was unchanged.

**Cause:** the rule had been added to the **Community Rules** database, whose
configured source was `None`. With no backing database there is nowhere to write,
and the save is discarded without an error.

**Fix:** put local rules in **User Rules**, which is the personal, always-writable
layer. Community Rules is for contributing upstream, and requires a configured
database source.

**Generalises to:** tools with layered config where one layer is remote-backed.
When a setting won't persist, check which layer received it before assuming the
tool is broken.

---

### RimSort's local and workshop folder paths were swapped, so custom mods were never scanned
_2026-08-10_

**Symptom:** hand-authored mods in `RimWorld/Mods/` never appeared in the mod
list, no matter how correct their `About.xml` was.

**Cause:** in RimSort's settings, `local_folder` held the *Workshop* path and
`workshop_folder` was empty.

**Fix:** point `local_folder` at `<RimWorld>/Mods` and `workshop_folder` at
`steamapps/workshop/content/294100`.

**Generalises to:** "my new mod doesn't show up" — verify the manager is looking
where you're writing *before* debugging the mod itself. The mod folder and the
scanned folder are two separate assumptions and only one of them is yours.

---

### A field silently moved off its class in 1.6, and eight races carried the stale version
_2026-08-10_

**Symptom:** `XML error: <wildness> doesn't correspond to any field in type
RaceProperties`, eight times, from one mod.

**Cause:** the field moved in 1.6. The mod was carrying pre-1.6 defs. The value
is dropped and the def loads anyway, so the races existed but with wrong
behaviour rather than none.

**Fix:** the mod was abandoned; it was removed. Where a mod is worth keeping, a
`PatchOperationRemove` on the stale node silences the error, and the real
behaviour has to be re-established wherever the field went.

**Generalises to:** "doesn't correspond to any field" is a **version drift**
report, not a typo report. It means the mod predates the game. Treat the count as
a severity signal — eight instances means eight defs are quietly wrong, not that
one line is untidy.

---

### A mod shipped an assembly referencing an AssetBundle it never packaged
_2026-08-10 · Star Wars KotOR Resources & Materials_

**Symptom:** `Unable to open archive file: …/SWCP-UnityAssets/…/SWCPshaders`,
then a `NullReferenceException` in `BuildableDef.ResolveIcon` inside
`LongEventHandler.ExecuteToExecuteWhenFinished`.

**Cause:** upstream packaging omission — the bundle is absent from the Workshop
upload *and* the GitHub repo. Confirmed by clean redownload, by reading the repo
tree (no `.gitignore` excluding it), and by searching all 1,211 installed mods
for any `*UnityAssets*` directory (zero matches, so no companion mod supplies it).

**Fix:** none locally; reported upstream, requesting both the bundle and a
null-check that degrades to "no custom shaders" instead of throwing into the
post-load queue.

**Generalises to:** before concluding "my install is broken", check the
distribution. Three cheap checks in order — clean redownload, the upstream repo
tree, then a filesystem-wide search for the missing artefact across every
installed mod — separate a local problem from a shipping problem, and the third
one also rules out a companion mod being the real supplier.

---

### Subscribed to a Workshop item that Steam has removed
_2026-08-10_

**Symptom:** `Created WorkshopItem for <id> but there is no folder for it`,
repeated each launch.

**Cause:** the item was taken down from the Workshop. The subscription persists;
the content can never download.

**Fix:** unsubscribe. Nothing else clears it.

**Generalises to:** a stable "no folder for it" line is an *account* state
problem, not a game state problem, and no amount of verifying files will fix it.

---

### Bulk Workshop metadata: use the Steam Web API, not the item pages
_2026-08-10 · found while auditing ~125 mod IDs_

**Symptom:** parallel fetches of `steamcommunity.com/sharedfiles/filedetails/`
returned HTTP 429 and the audit stalled.

**Cause:** rate limiting on the public item pages.

**Fix:** one POST to
`api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/` with
`itemcount` plus `publishedfileids[0..n]` returns all of them in a single
unthrottled call.

**Also, and separately:** when parsing that response, match the result code with
a regex that captures the digits. A substring test for `success":1` also matches
`success":15` (Access Denied), which reported a failed item as a success. A
correctness bug in the checker is worse than the thing it was checking.

**Generalises to:** batch endpoints exist for most metadata APIs and are the
first thing to look for when a per-item loop hits limits. And when testing
numeric codes in raw text, anchor the match — `1` is a prefix of a lot of things.

---

### A Windows path in a Python docstring broke the file
_2026-08-10_

**Symptom:** `SyntaxError: (unicode error) 'unicodeescape' codec can't decode
bytes … truncated \UXXXXXXXX escape` on a module that contained no obvious
escape.

**Cause:** the module docstring documented a path containing `\U` (as in
`...\Utils\`). Docstrings are ordinary strings and process escapes.

**Fix:** forward slashes in documentation paths, or make the docstring raw.

**Generalises to:** any Windows path written into a non-raw Python literal.
`\U`, `\N`, `\x` and `\u` are the ones that raise; the rest silently become
control characters, which is worse.

---

### "Mods with Missing Publish Field ID" in RimSort is not an error
_2026-08-10 · seen on first scan of a hand-authored local mod_

**Symptom:** a freshly deployed local mod appears in RimSort under the heading
**Mods with Missing Publish Field ID**, with a blank Published File ID and
`Source: Unknown`. Reads like a validation failure on a mod you just wrote.

**Cause:** `About/PublishedFileId.txt` is written by Steam when a mod is
*uploaded to the Workshop*. A local mod has never been uploaded, so the file
correctly does not exist. RimSort groups by provenance, not by health.

**Fix:** none. Do not hand-create `PublishedFileId.txt` — a fabricated ID points
the updater at someone else's Workshop item, which is a genuinely bad outcome in
exchange for silencing a non-warning.

**Generalises to:** mod managers surface *provenance* categories next to *error*
categories in the same panel. Before treating a heading as a defect, ask whether
it describes where the mod came from rather than what is wrong with it. The
useful signal in that screen was the opposite of the alarming one: the mod being
listed at all proved the local-folder scan path was finally configured right.
