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
