# traps.md — the running log of earned lessons

Every entry here cost a real debug cycle. Read this at the start of a RimWorld
task; append to it at the end of one. Format and promotion rules are in
SKILL.md §9 — the short version is that an entry earns its place by naming the
**class of situation it recurs in**, and once it would change default behaviour
it gets promoted into the skill body and deleted from here.

**Already promoted into SKILL.md — do not re-log these:** `--` forbidden in XML
comments · `PatchOperationRemove` deletes every match · `MayRequire` checks the
mod not the def · `GameComponent` needs `(Game game)` · `modDependency` does not
imply load order · a failed post-long-event action costs only itself, the queue
continues · compatibility patches must load last · read the `wanter` before
calling an unresolved cross-reference benign · `LoadFolders.xml` makes a mod's def
set depend on the whole mod list · the validator cannot see patch-created nodes
and does not check `Defs/`.

---

### ParentName must name an ABSTRACT def, not a concrete one — and validate_patch.py cannot see this
_2026-08-10 · found in our own mod, one load after auditing it "clean"_

**Symptom:** `XML error: Could not find parent node named "EMP" for node
"DamageDef"`, once per load. The whole DamageDef was **discarded**, so the ion
damage type did not exist, and the weapon's `damageDef` plus its stun hediff both
referenced nothing.

**Cause:** the def said `ParentName="EMP"`. `EMP` is a **concrete** def
(`<defName>EMP</defName>`). `ParentName` resolves only against defs declared with
a `Name=` attribute, i.e. abstract templates. Core's own EMP does the right
thing: `ParentName="StunBase"`, where `StunBase` is
`<DamageDef Name="StunBase" Abstract="True">`.

**Fix:** `ParentName="StunBase"`. When inheriting, copy the parent the *vanilla
equivalent* uses rather than the vanilla def's own name — the def you want to
resemble and the def you can inherit from are usually not the same thing.

**Generalises to — and this is the part that matters:** the audit that passed
this mod checked XML validity and every *internal* defName cross-reference, and
found nothing. Both checks were real and both missed it, because
**`ParentName` is a reference into the GAME's abstract-def namespace, not into
the mod's own.** `validate_patch.py` cannot catch it either: it only inspects
`Patches/`, and this was a `Defs/` file.

So there is a whole class of Defs-file defect no current tool covers:
`ParentName`, `Class=`, `workerClass`, `thingClass` and `graphicClass` all point
outward at names the mod does not own. **Before shipping any Defs file, resolve
every outward-pointing name against the live load set** — `ParentName` against
abstract defs, class names against loaded assemblies. That is the same discipline
as SKILL.md §1, applied to the files you write rather than the ones you patch.

---

### A live def dump answers "does this def exist" — but it contains no abstracts
_2026-08-11 · adding `--live` to validate_patch.py, and immediately mis-firing_

**Symptom:** the new live-index check reported three errors on a patch that was
correct: `'Force_LightsaberBase' does not exist in the LIVE game`. All three
operations were right, and the mod they target works.

**Cause:** `Force_LightsaberBase` is **abstract** — a `Name=` template with no
`defName`. Abstract defs exist only to be inherited from; RimWorld never
registers them in the `DefDatabase`. So a live dump, which enumerates the
DefDatabase, contains **none of them, by construction**. Checking an abstract
against a live index flags every correct patch-the-parent operation as a missing
def — and patching the parent is the *right* technique whenever a value is
inherited (see the entry on inheritance and raw-XML patch ordering).

**Fix:** only check `[defName="X"]` identities against the live index. Skip
`[@Name="X"]` entirely.

**Generalises to:** **a new data source has a shape, and its absences mean
something.** The dump does not contain "everything in the game" — it contains
everything the game *registered*, which excludes abstracts, and (for a partial
dump) everything not requested. Before validating against any index, ask what
that index legitimately omits, or the check will confidently report correct work
as broken. A checker that cries wolf gets switched off, and then it protects
nothing.

Related: the same asymmetry is why `def_diff.py` buckets `offline_abstract`
separately instead of reporting abstracts as "missing at runtime".

---

### An error count is a count of victims, not of causes — abstract bases multiply
_2026-08-10 · confirming the source of 16 identical unresolved-reference lines_

**Symptom:** 16 × `Could not resolve cross-reference: No Verse.SoundDef named
Pawn_Melee_Punch_HitBuilding found to give to Verse.RaceProperties`. Sixteen
looks like a widespread problem across many mods.

**Cause:** **two** lines of XML, in two `Abstract="True"` base ThingDefs
(`AsimovNonEnergyAutomatonBase`, `JDSSWCIS_Droids`). Every concrete race
inheriting a base inherits the dangling reference and fails to resolve it
independently, so one authoring mistake bills once per descendant.

**Fix:** none needed — the engine falls back with *"using undefined sound"*. The
point is the attribution, not the fix.

**Generalises to:** when triaging by volume, remember RimWorld's def inheritance
is a multiplier. **Divide before you panic:** N identical messages naming the same
missing def usually means one mistake in an abstract base with N-ish descendants,
not N mods getting it wrong. Search for the reference in `Abstract="True"` defs
first — it is both the smallest fix and the correct attribution.

The corollary bites the other way too: a *large* count is not automatically
severe, and a *small* count is not automatically safe. Severity comes from the
`wanter` (see SKILL.md §7), not the tally.

---

### A strictly read-only live-bridge call hung the game and cost a 23-minute load
_2026-08-10 · first live use of RimBridgeServer on a 562-mod stack_

**Symptom:** `rimworld/list_debug_action_roots` returned but slowly;
`rimworld/search_debug_actions` never returned. `Player.log` stopped mid-line, the
socket timed out at 60 s, and Windows raised `AppHangB1` and closed RimWorld.
Nothing had been mutated — the calls were pure discovery.

**Cause:** bridge tools execute **on the game's main thread**. Those two build
RimWorld's debug-action node graph, and across 562 mods that build never
completed. A livelock, not a deadlock and not a bad write: CPU stayed pinned and
the log kept growing until the process was killed.

**Fix:** none after the fact. Prevention is to never run enumerating discovery
tools against a game you care about — learn the paths on a throwaway quick-test
colony, then use the known path on the real one. The vanilla surface can also be
obtained fully offline: parsing `[DebugAction]` attributes out of
`Assembly-CSharp.dll` yields all 411 of them with categories and target kinds.

**Generalises to:** **"read-only" is the wrong safety axis for an in-process
bridge.** The question is not *does this mutate state* but *how much work does
this do on the thread that must keep responding.* An enumerating query over a
large plugin set is far more dangerous than a targeted write. Classify tools by
cost, not by side-effect, and treat "list/search/discover everything" as the
expensive category by default.

It also punctures a comforting assumption worth naming: I had constrained the
work to read-only calls and described that as safe. It was safe from corruption
and not safe for the session — two different guarantees that are easy to conflate
when handing someone a risk assessment.

---

### A folklore claim about the engine became our triage rule, and it was wrong
_2026-08-10 · found while deciding whether to disable a mod over it_

**Symptom:** none, which is the problem. For a full day we rated
`Could not execute post-long-event action` as near-top severity, on the belief
that one throw abandons the rest of RimWorld's post-load queue for every mod.

**Cause:** the claim is common RimWorld folklore and the log line *sounds* fatal.
It was written down once, promoted into `SKILL.md` as a default triage rule,
restated in four files, and then cited back as evidence when reasoning about an
unrelated mod. Nobody opened the method.

Parsing the IL settled it in minutes: FAT header with an EH section, a typed
`catch(System.Exception)` over an **18-byte** try containing a single
`Action::Invoke`, and a handler whose `leave` targets the **loop increment**. It
is `for (…) { try { list[i](); } catch { Log.Error(…); } }`. One failed action
costs one action.

**Fix:** retracted across all five files; the real severity is per-action.

**Generalises to:** separate two kinds of claim and hold them to different
standards. An **observation** ("this string appeared in the log") needs only the
log. A claim about **engine behaviour** ("and therefore the engine stops doing X")
needs the IL, the decompiled source, or an authoritative citation — because it
will be used to predict things you have not observed. Ours was load-bearing for a
mod-removal decision and for a public bug report.

Three amplifiers made it worse, and all three recur:
1. **Promotion laundered it.** Moving a note into a "verified lessons" file
   changed nothing about its evidence but changed how much everyone trusted it.
2. **Restatement looked like corroboration.** Four files agreeing was one source
   copied four times.
3. **It was self-confirming.** Every unexplained downstream breakage got
   attributed to the "aborted queue", so the rule kept appearing to earn its keep.

Cheap defence: when a written lesson is about to justify an irreversible or
outward-facing action, re-derive it from primary evidence first. Decompiling one
method is minutes; a wrong bug report is public.

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
`IfModActive` and `IfModNotActive`). With no `LoadFolders.xml`, fall back to the
mod root **and** `<moddir>/<version>` — **both**, not one (see the next entry;
getting this wrong cost us 667 defs). Report matches grouped by mod so a genuine
two-mods-define-this case stays visible.

**Generalises to:** any offline analysis of a game's content directory. The
filesystem is a superset of the load set, usually by a large factor, and the gap
is not random — it is concentrated in exactly the mods that have been around long
enough to accumulate version folders, which are also the popular ones you are
most likely to be patching. **A tool that over-counts is worse than one that does
not count**, because a confident wrong number gets acted on: here it recommended
a change that would have made a correct destructive patch wrong. Before trusting
any "how many things match" figure, ask which population it was computed over.

---

### The version-folder fix over-corrected and hid the mod root, costing 667 defs
_2026-08-10 · found by generalising the animal scan to all def types_

**Symptom:** 28 defs across four mods had `ParentName="AdaptiveStorageBase"`
with no such parent anywhere in the resolved load set. It looked like ~96 defs
were about to fail inheritance in the live game — a serious-sounding finding
that would have sent someone hunting a mod conflict.

**Cause:** the load-set resolver, written to fix the *previous* entry's
over-counting, treated the version folder as **exclusive**: with no
`LoadFolders.xml` it returned `<mod>/<version>` **or** the mod root, never both.
RimWorld loads both. Adaptive Storage Framework declares `AdaptiveStorageBase`
in its **root** `Defs/ThingDefBase.xml` while also shipping a `1.6/` folder, so
the base def was invisible and every dependant dangled. Measured on a 562-mod
stack: **35 active mods, 667 def nodes and 24 PatchOperations** were being
skipped — RIMMSqol (178 defs), Way Better Romance (64), Numbers (40), LWM's Deep
Storage (18).

**Confirmation before believing it:** the live `Player.log` contained **zero**
inheritance/parent-node errors, and all 35 mods demonstrably work. If the root
were genuinely unloaded, these popular mods would be broken for everyone. That
mismatch between "our tool says broken" and "the game says fine" is what
identified the tool as the wrong party.

**Fix:** emit the root **and** the versioned folder, root first so a
version-specific override wins under last-in-wins.

**Generalises to:** two lessons that bite together.

First, **an over-correction is still a correctness bug, and it hides rather than
shouts.** Over-counting produced a loud wrong number; under-counting produced
silence, which is harder to notice — nobody misses defs they never saw. When you
tighten a filter to fix false positives, measure what the tighter filter now
excludes.

Second, **when a static analysis says the game is broken and the game says
otherwise, the analysis is the suspect.** Check the log before reporting. Of the
128 unresolved parents here, only 28 were real; the other 68 carried
`MayRequire="Kura.ExtraStone"` for an inactive mod, so the game correctly skips
them — a documented limitation behaving exactly as documented. Splitting a
finding by cause before reporting it is the difference between a fix and a
wild-goose chase.

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
post-load queue. (That last clause originally read "and took the rest of the
queue with it" — **false**, corrected 2026-08-10; the queue is per-action
try/catch.)

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

### Blanket find-and-replace keeps eating the syntax it lives inside (3 instances)
_2026-08-10 · three separate times in one session_

This trap has now fired three times in a single day, in three different files, on
three different search strings. It is the most reliably recurring mistake in this
log, so it is consolidated here rather than logged three times.

| # | Replace | What it also hit | Result |
|---|---|---|---|
| 1 | `->` to `=>` in a patch header | the `-->` comment terminator | every comment broken |
| 2 | pasted a stack trace containing `--->` | `-->` inside it closed the comment early | file would not parse |
| 3 | `<li>` to `&lt;li&gt;` in About.xml prose | the **real** `<li>1.6</li>` in `<supportedVersions>` | mod metadata unparseable |

**Generalises to:** before any blanket replace in markup, ask *what else in this
file legitimately contains my search string.* Markup is self-similar — the thing
you are escaping is almost always also part of the structure. Two defences that
actually work:

1. **Scope the replace to a region**, not the file. Extract the description /
   comment body, transform it, put it back.
2. **Parse after every write, always.** Instance 3 was written, deployed AND
   committed before anyone noticed, because the parse check ran in a separate
   command that failed independently while the deploy chain carried on.

**Also earned from instance 3:** `validate_patch.py` checks `Patches/` and
nothing else, so a broken `About.xml` sails past it. A malformed About.xml is
worse than a broken patch — RimWorld cannot read the mod's metadata at all.
**Parse every XML in the mod folder as the last step of deploying**, About.xml
included, and make it part of the same command chain so a failure stops the
deploy.

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

**Fix:** none locally; reported upstream (issue #7, open), requesting both the
bundle and a null-check that degrades to "no custom shaders" instead of throwing
into the post-load queue. ⚠️ That issue also claims the throw "aborts the
remainder of the post-load queue" — **that claim is wrong** and needs a
correction comment; see the entry below.

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

---

### Disabling a mod orphaned its add-on's assembly and killed Prepatcher outright

**Symptom:** a dialog before the main menu, and in the log:

```
Prepatcher Error: Fatal error while reloading:
  System.Reflection.ReflectionTypeLoadException
  Could not load type of field
    VSIERationalTraitDevelopment.SocialInteractionsManager_TryAssignThoughtsAfterRaid
    +<>c__DisplayClass1_0:__instance' (1) due to: Could not resolve type with token 0100002a
  at Prepatcher.Process.FreePatcher.FindAllFreePatches (System.Reflection.Assembly)
  at Prepatcher.Process.FreePatcher.RunPatches
  at Prepatcher.Loader.Reload
```

**Cause:** we disabled Vanilla Social Interactions Expanded as a bisect step and
did not check who depended on it. `Stagz.VSIERationalTraitDevelopment` is a
*separate* Workshop mod that hard-depends on VSIE, and it stayed active. Its
assembly still loads, but every type in it references VSIE types that are now
absent, so `Assembly.GetTypes()` throws `ReflectionTypeLoadException`.

Prepatcher enumerates **every** active mod assembly looking for `[FreePatch]`
methods. It calls `GetTypes()` on each one and does not guard the call, so a
single orphaned assembly anywhere in the load set aborts the whole free-patch
pass. The game then continues loading with **unpatched** assemblies, silently,
and any mod that expects a Prepatcher-injected field breaks at runtime instead
of at load. Verified new: the immediately preceding load had `Prepatcher:
Starting...` and zero Prepatcher errors.

**Fix:** disable the orphaned add-on too. It is inert without its parent anyway.

**Rule — dependency checks run in BOTH directions.** Before disabling mod X, ask
not only "what does X need" but "**who needs X**". Only the second question
catches this, and it is the one that gets skipped. The same session had already
produced the mirror-image near-miss: nearly disabling Interaction Bubbles, which
would have taken down SpeakUp, which hard-depends on `Jaxe.Bubbles`.

**How to check, before spending a load** — scan `About.xml` of every *active*
mod (resolve the set with `rimworld_loadset.build_load_set`, never by listing
folders) for the packageId being disabled, and separately scan the DLL bytes on
each mod's *resolved content dirs* for the target assembly's name:

```python
needle = b"VanillaSocialInteractionsExpanded"          # the ASSEMBLY name
for m in mods:
    for cd in m['contentDirs']:                        # version-resolved only
        ad = os.path.join(cd, "Assemblies")
        ...  if needle in open(dll,'rb').read(): FLAG
```

Both halves are needed. The About.xml scan found the culprit here; the byte scan
is what proves nothing *else* is orphaned, and it is the only one that catches an
undeclared dependency.

**Restrict the byte scan to `contentDirs`.** A mod may ship compatibility
assemblies it never loads. `Intimacy - Friends n' Lovers` carries
`Compatibility assemblies/VSIE/Assemblies/VSIECompatibility.dll`, which
references VSIE and is completely harmless because that path is not a loaded
content dir. Scanning the whole mod folder reports it as a second orphan and
sends you to disable a mod that was fine.

**Generalises to:** any framework that reflects over the entire active assembly
set — Prepatcher, and Harmony `PatchAll` scanners. One broken assembly is not
contained to its own mod; it takes out the pass that touched it.

---

### A mod's art can be invisible to a file audit — AssetBundles are readable, and loose files still beat them
_2026-08-11 · found while auditing race art quality_

**Symptom:** a texture-quality audit of every Star Wars race mod had to record
four mods as *"UNVERIFIED — art locked in AssetBundles"*. `find -name '*.png'`
returned nothing for them. The working assumption forming was that bundled art
could be neither inspected nor overridden, which would have meant commissioning
replacement art blind.

**Cause:** RimWorld 1.6 gave AssetBundles first-class support, and authors have
begun shipping art compiled rather than loose to halve download size.

**Fix:** both halves of the fear were wrong.
*Reading:* `pip install UnityPy` opens them. One bundle yielded 554 `Texture2D`
objects with dimensions and internal paths. Assets are stored at
`assets/data/<packageid>/textures/<the ordinary RimWorld path>`, so the path is
recoverable by stripping the prefix. Tooling: `Utils/extract_bundle.py`.
*Overriding:* RimWorld resolves a texture as **loose file in any active mod →
base game resources → bundles**. Bundles are checked LAST, so a loose PNG at the
same path wins *regardless of load order* — overriding a bundle mod is easier
than overriding a loose-file one. (The reverse is the bundle author's problem: a
bundle can never override a base-game texture.)

**Generalises to:** "I can't see it" is a statement about your tools, not about
the file. Before concluding that content is inaccessible, spend ten minutes
looking for the format's standard reader — packed formats almost always have
one. And check the engine's *resolution order* before assuming you cannot
override something; the order is often more favourable than intuition suggests.

---

### Twice now, "the art is bad" has meant "the wrong art is being selected"
_2026-08-11 · Gamorrean, then Wookiee_

**Symptom:** two races looked wrong and both looked like art problems.
Gamorrean read as "a grumpy human with horns". Wookiee rendered at 128×128 where
every other species in the same mod is 512×512.

**Cause:** neither was a missing-art problem.
*Gamorrean:* `PigEars` already existed in Biotech and simply wasn't on the
xenotype; separately, 206 of 318 loaded `HeadTypeDef`s declare no
`requiredGenes`, so a pawn without a head gene rolls from a pool that is
two-thirds modded alien skulls.
*Wookiee:* **two complete, correctly-gated head chains exist** — Outer Rim's at
512×512 and Star Wars Xenotypes' at 128×128. Neither is buggy. The xenotype that
spawns simply carries the gene pointing at the worse one.

**Fix:** a def patch, not a commission. `WookieeHead_Upgrade.xml` swaps one gene
in `BTD_Wookiee`.

**Generalises to:** in a large stack, *presence* of an asset says nothing about
*selection* of it. Before treating an appearance problem as an art problem, dump
which def is actually chosen and what it points at. The def layer is free to
inspect and free to change; art is the most expensive and least reversible input
in the pipeline. Exhaust selection before you commission pixels.

---

### The mod whose entire job is deduplication resolved to the worse asset
_2026-08-11 · Xenotype REMIX: Star Wars_

**Symptom:** Wookiees used 128×128 art despite a 512×512 version being installed
and correctly gated.

**Cause:** `BTD_Wookiee` — from **[BTD] Xenotype REMIX: Star Wars**, adopted
*specifically* to dedupe the Star Wars Xenotypes / Outer Rim overlap — carries
`guy762_Head_wookiee`. Its own `BTD_Data/XenotypeEquivalencies.xml` lists all
three Wookiee xenotypes in one `EquivalentGroup`, so it knew both existed and
picked the lower-resolution one.

**Fix:** local patch. Not a bug report — the author made a judgement call, and
theirs is as legitimate as ours.

**Generalises to:** adopting a "compatibility" or "dedupe" mod resolves a
conflict but **transfers the choice to its author**, silently and across every
def it touches. When you install one, audit *which* side it picked for the
things you care about. Its equivalency data is usually plain XML and tells you
directly. Same shape as a load-order rule: the conflict is gone, but somebody
else decided the outcome.

---

### Absence of a texture folder is not absence of art
_2026-08-11 · Wookiee body_

**Symptom:** a texture audit reported the Wookiee as having "no body art at all"
because no `Textures/Pawn/BodyType/wookiee` folder exists.

**Cause:** the fur *is* the body treatment. `Furskin` is a Biotech `GeneDef`
whose `renderNodeProperties` attach a `PawnRenderNode_Fur` (worker
`PawnRenderNodeWorker_Fur`) to the `Body` tag. Nothing is missing; the art
arrives through the render tree rather than through a per-race folder.

**Fix:** withdraw the finding.

**Generalises to:** since 1.6, graphics reach a pawn by at least three routes —
a race's `graphicPaths`, a `HeadTypeDef`'s `graphicPath`, and a gene's
`renderNodeProperties`. A folder-shaped search only sees the first two. When an
audit reports "no art", confirm against the render tree before believing it,
and state the search method in the finding so the blind spot is visible.

---

### The patch validator cannot evaluate `text()` — but lxml can
_2026-08-11 · authoring the Wookiee swap_

**Symptom:** `validate_patch.py` reported *"xpath uses an XPath feature this
checker cannot evaluate"* for
`/Defs/XenotypeDef[defName="BTD_Wookiee"]/genes/li[text()="guy762_Head_wookiee"]`
and skipped the live hit count — on the two operations that mattered most.

**Cause:** the validator uses `xml.etree.ElementTree`, which supports only a
subset of XPath 1.0. `text()`, `starts-with()`, `contains()` and boolean
predicates are all outside it. The tool deliberately says UNSUPPORTED rather
than guessing, which is correct but leaves real gaps unchecked.

**Fix (this time):** hand-verified with `lxml`, which implements full XPath 1.0 —
the same class of engine as the game's `System.Xml`. It matched 1 node and the
simulated result was exactly the intended gene list.

**Generalises to:** a checker that honestly reports "I cannot check this" is
still a gap, and gaps cluster on the *interesting* cases — nobody needs
`text()` for a simple def edit. **Improvement worth making: have
`validate_patch.py` use `lxml` when it is importable and fall back to
ElementTree otherwise.** That converts most UNSUPPORTED lines into real checks
for a one-line dependency.

---

### Mod-list state on disk is not authoritative while the game is running
_2026-08-11 · told to me more than once before it stuck_

**Symptom:** I repeatedly reported "the removal didn't land — these mods are still
active" after the user had removed and unsubscribed them. Evidence cited each
time: the packageIds still present in `ModsConfig.xml`, and the mod folders still
present under `294100/`. Both readings were accurate. Both conclusions were wrong.

**Cause:** RimWorld holds its active mod list **in memory** while running and
rewrites `ModsConfig.xml` on exit; Steam will not remove an unsubscribed mod's
folder while the game has files open in it. So for the entire duration of a live
session, the on-disk state reflects *the load that is running*, not the user's
subsequent decisions. A manager's edits made mid-session can also be overwritten
when the game closes.

**Fix:** before making any claim about the mod list, establish whether the game is
running. `Player.log`'s mtime versus `ModsConfig.xml`'s mtime is the cheap tell —
if the log is older than the config, a re-sort happened after the load and the
running game does not match the file. Report what the timestamps imply; do not
assert a state.

**Generalises to — and this is the real lesson:** *"verify offline from files"* is
a good rule that quietly assumes **the files are at rest**. Any file a running
process owns is a snapshot of that process's startup, not of the world. Before
treating a file as ground truth, ask **who writes it and when they flush** —
config written on exit, caches written on shutdown, logs written continuously.
The same trap wearing a different hat: a mod-settings file that only rewrites when
its settings window is closed, and a live def dump that describes the mod set at
capture time rather than now.

There is a second, sharper lesson about being told twice. Getting a fact wrong is
ordinary; getting it wrong *again* after correction means it was never written
down. The fix for a repeated error is never more care — it is a durable note in
the place that governs default behaviour, which is why this one is also in
`CLAUDE.md` rather than only here.

---

### Three mods shipped the base game's own assemblies, and one shipped all of it

**Symptom:** Interaction Bubbles never drew a single bubble and its shift-click
settings never opened, while its toggle icon rendered and toggled perfectly. No
exception, no log line, nothing to bisect against. Two dead-end hypotheses and
one wasted 23-minute load went by before the cause turned up somewhere else
entirely.

**What was actually there,** flagged by Dubs Performance Analyzer in a single
line nobody had read:

```
[Analyzer] Mod Tribal Furniture has packaged the base-game Rimworld assemblies
```

`Tribal Furniture` (`Xercaine.Tribal.Furniture`, Workshop 3671245310) shipped
**26 DLLs in `Assemblies/`, of which exactly one — `TribalFurniture.dll`, 25 KB —
was the mod.** The other 25 were the game and the Unity runtime: a
**byte-identical** `Assembly-CSharp.dll` (15,777,280 bytes, same md5 as the
game's), `Assembly-CSharp-firstpass`, twelve `UnityEngine.*` modules,
`Unity.Burst`, `Unity.Collections`, `Unity.Mathematics`, `Unity.TextMeshPro`,
`NAudio`, `NVorbis`, `steamworks.net`. Someone published their whole `bin` output.

RimWorld loads **every** DLL in a mod's `Assemblies` folder.

**Why it can break things invisibly.** Two `Assembly-CSharp` images means the CLR
holds two of every game type, and — the part that bites — **two independent sets
of statics.** `Verse.Find` is nothing but statics, so code bound to the duplicate
sees `Find.CurrentMap` as null. That is not an error and throws nothing; it is
simply never equal to anything. Bubbles gates on `init.Map != Find.CurrentMap` at
capture, `p.Map != Find.CurrentMap` at draw, and `Find.WindowStack.Add(...)` for
its settings dialog — while the two things that *did* work, drawing the icon and
flipping the toggle, touch only `Settings` and `WidgetRow` and never touch `Find`.
One cause, both symptoms, zero diagnostics.

**Sweep for it — this was not a one-off.** Checking every active mod's *resolved
content dirs* against the game's `Managed` folder found **three** offenders:

| mod | stray files |
|---|---|
| `Xercaine.Tribal.Furniture` | 24, incl. a byte-identical `Assembly-CSharp.dll` |
| `petetimessix.researchreinvented.steppingstones` | 2 `UnityEngine.*`, byte-identical |
| `tickleyourpawn.core` | `mscorlib.dll` — **and NOT identical to the game's** |

```python
game = r"...\RimWorld\RimWorldWin64_Data\Managed"
gn = {f.lower() for f in os.listdir(game) if f.endswith(".dll")}
for m in mods:
    for cd in m['contentDirs']:                 # resolved paths only
        ad = os.path.join(cd, "Assemblies")
        hits = [f for f in os.listdir(ad) if f.lower() in gn]   # -> offender
```

**Fix:** move every stray out, keep only the DLLs the mod actually authored.
All three mods had exactly one real assembly each. Relocate rather than delete,
with a manifest recording each file's size and whether it was byte-identical to
the game's copy — Steam may restore them on a validation pass, and you want to
be able to prove nothing unique was taken.

**Generalises to:**

- **Read the analyzer lines.** Dubs Performance Analyzer had diagnosed this in
  plain English and it sat unread in a 38,000-line log while three wrong theories
  were pursued.
- A mod's `Assemblies` folder is a **whitelist you should audit**, not a black
  box. One 25 KB mod dragged 25 MB of duplicate runtime into the process.
- When a mod's code demonstrably *runs* but its *observations of the world* are
  wrong — null maps, empty collections, missing windows, with no exception
  anywhere — suspect split type identity before suspecting the mod's logic.
