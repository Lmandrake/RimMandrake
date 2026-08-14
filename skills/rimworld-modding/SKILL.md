---
name: rimworld-modding
description: Author, patch, validate and debug RimWorld mods — XML PatchOperations, custom Defs, C#/Harmony assemblies, load-order problems, and Player.log triage. Use this whenever the user mentions RimWorld modding, a mod conflict, a Def, a patch, an xpath into Defs, ModsConfig/RimSort load order, a red error in the dev console, or asks to make/fix/analyse anything under a RimWorld Mods folder — even if they just paste a log excerpt and ask "what is this". Also use it before writing any file into a mod folder, because RimWorld's XML has several silent-failure modes that are easy to hit and hard to see.
---

# RimWorld modding

RimWorld's modding surface punishes guessing more than almost anything else you
will work on. Patches fail *silently*, XML comments have a syntax rule most
people don't know, and a single bad Def entry can kill three unrelated mods at
startup with an error that names none of them. Almost every hour lost in this
domain is lost to writing something plausible instead of reading something real.

So the whole method is: **find the ground truth on disk, write the smallest
change that survives a mod being absent, prove it before shipping, and record
what you learned.**

---

## 1. Read the real file first. Always.

Before writing a single line of a patch, open the def you are patching and the
def you are patching *around*. Not the wiki's version of it, not what a doc in
the project says it was last month — the actual XML in the actual mod folder
that is actually loaded right now.

```bash
# where the defs live
RW="C:/Program Files (x86)/Steam/steamapps/common/RimWorld"
WS="C:/Program Files (x86)/Steam/steamapps/workshop/content/294100"

grep -rl 'defName>Armadillo<' "$RW/Data" "$WS" --include=*.xml
```

This costs thirty seconds and it is the difference between a patch that works
and a patch that no-ops forever without telling you. Three specific reasons it
matters more here than elsewhere:

- **A failed PatchOperation is a no-op, not an error you'll notice.** It prints
  one line into a log with thousands of lines. Nothing breaks. The patch just
  never happened. You will believe it worked.
- **Def names are redefined by other mods.** The `Armadillo` you're looking at
  in Core may not be the `Armadillo` that wins. Last loaded def with a given
  `defName` replaces earlier ones entirely.
- **Fields move between versions.** `<wildness>` was valid on `RaceProperties`
  and isn't in 1.6. Mods carrying stale fields log a config error and drop the
  value. Wiki pages and old forum posts lag the game by a version or more.

When you find the ground truth, **quote its file path and the exact snippet in a
comment at the top of the patch**, with a date. Future-you re-reads that comment
instead of re-doing the search.

---

## 2. The game restart is the scarce resource

On a large modded stack a cold load takes **many minutes** — twenty to thirty is
normal past ~500 mods, because every mod's XML is parsed and the texture atlases
are rebuilt. Ask the user what theirs costs and treat that number as the budget
you are spending. It reframes the whole workflow: the goal is not "try it and
see", it is **arrive at the restart already confident, and learn as much as
possible from the one you spend.**

Three habits follow.

**When you are three failed hypotheses deep, stop bisecting downward and build a
MINIMAL load instead.** Cutting to the ~20 mods that can possibly be involved
costs **one** load and answers a better question: *does the feature work at all
in isolation?* **`references/minimal-load.md`** has why it beats bisecting, how to
derive the set rather than guess it, and the two traps inside the reduced set —
read it the moment you notice you are *generating* hypotheses rather than
*testing* a theory.

**Verify everything verifiable offline, first.** A restart should be confirming a
prediction, not conducting an experiment.

**Batch by risk, not by count.** The rule is about *ambiguity*, not quantity:
batch anything whose effects are distinguishable, keep a new C# assembly solo.

**Harvest the whole log, not just your change.** You paid for a full load; a single
yes/no answer is a poor return on it.

**`references/spending-a-load.md` has all three in full — what "verifiable
offline" actually covers, which changes are safe to ride along and which must go
solo, and the running "next restart" queue that makes harvesting cheap.** Open it
when you are planning a load, not every session.

The corollary for how you talk to the user: **do not casually suggest "restart
and see".** Each one costs them real time. Propose a restart when the queue
justifies it, say what the batch contains, and state in advance the specific log
strings that will decide each item.

---

## 3. Pick the implementation tier before you pick the code

Most "how do I do X in RimWorld" questions are really "at which layer does X
belong". Getting this wrong is expensive — people write a C# mod for something a
six-line XML patch does, or try to patch a def for something that only exists at
runtime. Work down this ladder and stop at the first tier that can do the job:

| Tier | Layer | Use when the thing must… | Cost to change later |
|---|---|---|---|
| a | Mod list / settings / scenario | be true before worldgen | free |
| b | XML Def patch | be *true of the game* — stats, spawns, recipes, names | cheap |
| c | C# / Harmony assembly | *behave* differently — new mechanics, new AI | expensive |
| d | Save-game edit | be true of one existing colony, retroactively | one-shot, risky |
| e | Live runtime manipulation (bridge/console) | *change during play* | ephemeral |
| f | External host-side tooling | analyse or generate outside the game | free |

The rule of thumb that keeps this straight: **bake what must be TRUE, script
what must be PLACED, run live only what must CHANGE.** If a value never varies
during a playthrough, it belongs in tier b, full stop. Reaching for C# because
XML feels weak is the single most common overbuild in this domain.

---

## 4. Writing an XML patch

### The shape to default to

Every operation goes inside a `PatchOperationConditional` that tests for the
exact node you are about to touch. This is not ceremony — it is what makes a
patch safe when a mod is absent, when the user updates it, or when the author
fixes the bug upstream. An unconditional patch against a missing node prints a
red error at every launch and trains the user to ignore red errors.

```xml
<Operation Class="PatchOperationConditional">
  <xpath>/Defs/ThingDef[defName="Armadillo"]/race/wildBiomes/Desert</xpath>
  <match Class="PatchOperationRemove">
    <xpath>/Defs/ThingDef[defName="Armadillo"]/race/wildBiomes/Desert</xpath>
  </match>
</Operation>
```

The test xpath and the inner xpath should be **identical** unless you have a
stated reason. If they differ, you are testing for one thing and modifying
another, which is exactly how a patch ends up doing something you didn't intend
in a stack you can't reproduce.

### The four things that bite everyone

**Match the shape of the children already in the node.** RimWorld has two child
shapes and they are not interchangeable. Plain lists use `<li>`. Dictionary-keyed
fields use the *def name as the element name* — `<wildBiomes><Desert>0.3</Desert>`,
`<statBases><MoveSpeed>4.6</MoveSpeed>`,
`<baseWeatherCommonalities><Clear>18</Clear>`. Which one a field uses is a
property of its C# type, so it is identical across every mod, and the only way to
know is to look at what is in the node already.

Getting this backwards is the most destructive mistake in this document: an `<li>`
in a dictionary-keyed field makes the engine **discard the entire parent def** — one
that was working before you touched it. (Why, and the log signature it leaves:
`references/patch-operations.md` §11.)

**`PatchOperationRemove` deletes every match, not the first one.** There is no
"remove one". If a def lists `<TropicalSwamp>` twice and you write the bare
xpath, both disappear and the animal stops spawning there entirely. Use a
positional predicate — `.../TropicalSwamp[2]` — and put the same predicate in the
conditional test so the op self-disables once upstream fixes their file.

**XML comments cannot contain a double hyphen.** `--` anywhere inside `<!-- -->`
is a hard parse error, and it takes the whole file with it, not just the
comment. Separator lines made of dashes and arrows written as `->` are the usual
culprits. Use `===` for rules and `→` or `to` for arrows. Never do a
find-and-replace of `->` across the file either: it corrupts every `-->`
terminator into `-=>`.

**`MayRequire` and `PatchOperationFindMod` check the mod, not the def.**
`MayRequire="VanillaExpanded.VWE"` passes as long as VWE is installed — even if
VWE deleted the def you reference in its latest version. That is a live upstream
bug class, not a hypothetical; it is why unresolved cross-references show up in
stacks where every named mod is present. When you *depend* on a def existing,
guard with `PatchOperationConditional` on the def itself, which tests reality
rather than intent.

The reason this is so common is that **a mod can ship different defs depending on
what else is loaded**, via `LoadFolders.xml` — so the def set is a function of the
whole mod list, and "the mod is installed" tells you nothing about which of its
defs exist. **When a reference goes missing while its owning mod is plainly
present, read that mod's `LoadFolders.xml` before concluding anything**; the
syntax and the real Vanilla-Animals-Expanded/Odyssey case are in
`references/patch-operations.md` §9.

### Which operation

`Add` (child) · `Insert` (sibling) · `Replace` · `Remove` (deletes **every**
match) · `AttributeAdd`/`Set`/`Remove` · `SetName` · `AddModExtension` ·
`Sequence` (stops at first failure) · `Conditional` (`match`/`nomatch`) ·
`FindMod`. `PatchOperationTest` is obsolete — use `Conditional`.

**The full table of what each one takes, plus xpath idioms and inheritance
(`ParentName`/`Abstract`), is in `references/patch-operations.md`.** Read it
when an xpath won't match, or before using any operation above beyond `Add`,
`Replace` and `Conditional`.

---

## 5. Validate before you deploy

Run the bundled validator on any patch file before it goes near the Mods folder.
It catches the silent failures — the ones that cost a full game restart to
discover, which in a large stack is several minutes each time.

```bash
python3 scripts/validate_patch.py path/to/Patch.xml \
    --defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" \
    --defs "C:/Program Files (x86)/Steam/steamapps/workshop/content/294100"
```

The valuable check is the last one: it **runs each xpath against the real Defs on
disk and reports how many nodes it hits**. Zero hits means the patch would silently
do nothing; more hits than expected means a `Remove` is about to take out more than
you think. (Its other five checks: `references/patch-operations.md` §10.)

A patch that validates clean can still be wrong about *intent*, so also confirm
in-game: load, then check the dev console (or `Player.log`) for the patch's own
name. Silence is success.

### Two things it cannot see — know these before trusting a result

It reads defs **unpatched**, so a node another mod creates at runtime is invisible
and **0 matches can be the correct answer**; and it validates `Patches/` only —
**it does not check `Defs/` at all**, so a hand-authored Def with a field that
moved between versions sails straight through. **`references/patch-operations.md`
§10** has both in full, with the WeatherDef that shipped a renamed field. Read it
before you either trust or disbelieve a validator result.

---

## 5b. Load order is a constraint you must ASSERT, not a preference

If your mod patches other mods' defs, it must load after every one of them.
That sounds obvious and is where more time was lost in this project than
anywhere else.

**`ParentName` inheritance is load-order dependent.** A def whose `ParentName`
names an abstract def in a mod that loads *later* does not inherit — at all.
Everything the parent supplied is simply missing, and you get
`XML error: Could not find parent node named "X"` plus a cascade of config
errors about fields you never wrote. Do not assume the engine resolves
inheritance across the whole combined document; it does not.

**The damage escapes your mod**, and none of the stack traces name it. A failed
inheritance breaks *vanilla* code that enumerates all defs of that type — worldgen
included. If worldgen starts throwing, grep the log for `Could not find parent
node` and `Config error in <YourDefPrefix>` before believing it is a vanilla bug.

**Assert the order in code before every launch.** Not by eye, not by trusting the
manager: resolve the load set, compare the index of your mod against each mod it
patches, and fail loudly. One check per mod you reach into.

**`references/load-order.md` holds the three NRE sites that proved it, the
assertion snippet, and why the community rules database must not be hand-edited.**
Open it when an inheritance error appears, when writing the assertion, or before
touching a sorter's rules database.

### Teach the mod manager, or it will keep undoing you

Fixing a scattered order by hand treats the symptom. Write **one `loadAfter` edge
per mod you patch** into the manager's user-rules database (RimSort:
`%LOCALAPPDATA%/RimSort/dbs/userRules.json`) — `loadAfter` is a *constraint* a
topological sort cannot violate, whereas **`loadBottom` is only a hint and creates
no edge at all**. (The full distinction: `references/load-order.md`.)

⚠️ Two traps in the rules file itself. It is keyed by `packageId`, so **renaming
your mod silently orphans every rule** — a stale rule for a dead packageId is
indistinguishable from no rule, which is exactly how this went unnoticed for
days. ❌ **Corrected 2026-08-13 — "the manager rewrites the file on exit, so close
it before editing" is FALSE for RimSort**, and it contradicted this skill's own
trap entry. RimSort saves only when the owner clicks Save; **"close RimSort first"
is never a precondition.** The real hazard is the reverse and it is live: after an
external edit RimSort's in-memory view is stale, so a later Save writes the OLD
list back. Mitigation is one sentence — *"RimSort is open, hit Refresh"*.
🔴 **And read `ModsConfig.xml`'s mtime immediately before writing it.** It moved
twice in twenty minutes on 2026-08-13 while the owner re-sorted. Writing blind
destroys their ordering silently.

---

## 6. Deploying

Author in the project repo, deploy a copy to the game. Never edit in place under
`Mods/` — that copy is disposable, overwritten by the next deploy, and not in
version control.

**The full procedure is `skills/rimworld-deploy/SKILL.md`**: the plan-first
`deploy_custom_mods.py` run, reading the plan before `--apply`, `-` lines and
`--pull`, `DEPLOY_HOLD.txt`, the minimum viable mod folder, why compatibility
patches must be enabled LAST in load order, and the restart that follows.

---

## 6b. 🔴 Inspect the CONSUMER, not the artifact

**A file being correct on disk says nothing about what the game is running.** Every
"it is done" that turned out to be false was reported after reading the artifact and
never asking what last read it.

**The check is one question: _what did the consumer last read, and when?_** The
process start time IS the def-read time — RimWorld reads defs **once, at launch** —
so anything under `Mods/` newer than that StartTime is not loaded. **The three
commands, and two measured cases (a `GenStepDef` and a DLL) both reported done and
both false, are in `references/traps-mods-and-managers.md` §"A def deployed AFTER
launch".** Run them before calling anything live.

⚠️ **Map-generation defs need MORE than a restart: they need a map generated after
it.** Loading a save re-runs no GenStep, so a correct fix is invisible on an old map.

⚠️ **The bridge cannot answer this for you** — `jawa/get_def` returns the def that was
*loaded* and does not expose most fields, so a successful read is not proof the def is
current. **The mtime is the evidence.**

⭐ **Say which one you checked.** "Deployed" is a claim about disk; "live" is a claim
about a process. A report that does not distinguish them will be read as the stronger
of the two.

## 7. Debugging from Player.log

`%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`

Triage by **consequence, not by position in the file**. The ladder, worst first:
static-constructor / `TypeInitializationException` / `ReflectionTypeLoadException`
(the mod is *dead*, not noisy) → `Could not execute post-long-event action` (costs
exactly that one action; the queue continues) → `Could not resolve cross-reference`
(benign **or** fatal — it depends entirely on the `wanter`) →
`Patch operation … failed` (a no-op) → translation and sound errors (cosmetic).

**`references/player-log-triage.md` has each rung in full: the greps, the IL-level
evidence for what each error actually costs, the two shapes of cross-reference
damage, and the judged-safe list you must keep.** Open it whenever you are reading
a log — five "benign" cross-reference lines were the sole cause of a dead mod for
three loads running, and a `ReflectionTypeLoadException` is usually load order
rather than a broken assembly.

---

## 8. C# mods, briefly

Reach for C# only when tier (c) is genuinely required — see §3. When you do,
`references/csharp-and-loading.md` covers Harmony patch types, the entry-point
classes and their required constructor signatures, and `LoadFolders.xml`. Two
constructor rules cause a disproportionate share of "mod does nothing" reports:

- A `GameComponent` needs a **public constructor taking `(Game game)`**. Without
  it, `Game.FillComponents` throws `MissingMethodException` and the component
  silently never exists — worse than a crash, because the feature appears to
  work and simply has no consequences.
- A `Mod` subclass needs `(ModContentPack content)`.

---

## Validation plan — what you owe whoever holds the game

Anything you author and cannot check yourself — a def, a patch, an assembly —
ends with a validation plan **in the same commit**. Not on request: a cold load
costs 23–30 minutes (§2), and without a plan the person holding the game invents
one, and theirs will not carry your prediction.

**1. The observable — what a player SEES when it works.**
🔴 **A positive observation, never "no error".** "No `Patch operation … failed`
line" is an absence, and §7 item 4 says absences are the cheapest thing in that
file. Name the thing on screen: the animal on the wildlife tab, `MoveSpeed` at
4.6 in the stat readout, the recipe in the bill list.

**2. The route — the exact call, click path or spawn that produces it.**
The defName, the dev-mode spawner path, the bridge call with its arguments. ⚠️
**If the route needs a tool that does not exist yet, say so and file it as
blocked on the tool** — do not queue it for a load it cannot survive.

**3. The prediction — written BEFORE the look.**
A number or a specific string: *two* `wildBiomes` children, not "fewer". This is
the field that turns a look into evidence; without it you rationalise the panel.

**4. The threshold — what CLOSES it, and what is explicitly out of scope.**
⭐ **Usually one observation, not a battery.** Name the minutia you are choosing
not to chase — the icon, the translation key, the second biome.

**5. Batch or solo.**
§2's batch-by-risk rule, stated as a field. A validated pure-XML patch with named
log strings rides along; **a new assembly goes solo**, because if the load comes
up wrong nobody can separate the DLL from the three def changes beside it.

**6. What a FALSE PASS looks like.**
The way this particular check lies. Four that cost real cycles here:
- **The conditional never ran.** A `PatchOperationConditional` in a mod that loads
  *before* the mod it patches matches nothing, no-ops, and **prints no log line at
  all** — so "clean log" and "patch applied" are indistinguishable. Load order
  decides whether the check is even meaningful; assert the index (§5b).
- **The consumer is stale.** The file is right and the game never read it —
  RimWorld reads defs **once, at startup**. "Deployed" and "live" are different
  claims (§6b), and the mtime against the process StartTime is the evidence.
- **The instrument cannot see it.** `jawa/get_def` returns `extra: null` for def
  types it does not model, which reads as *the field is absent*. Membership
  questions go to the def dump, never to the probe.
  (`traps-tooling.md` → "`jawa/get_def` returns `extra: null` for def types it does
  not model, and it reads as \"absent\"" · "\"Empty output\" is not a result")
- **A map-gen def checked on an old map.** A `GenStepDef` changes nothing until a
  map is *generated after the load*; loading a save re-runs no GenStep, so a
  correct fix reads as a third failure (§6b; `traps-diagnosis.md` → "The same mod
  stayed dead through two correct fixes, for three different reasons").

### The shape to hand over

```
ITEM     <what is being validated>
SEE      <the positive observation>
ROUTE    <exact call / defName / click path>
PREDICT  <number or string, before the look>
CLOSE    <the bar> — NOT chasing: <the minutia deliberately skipped>
RIDE     batch | solo (<why, if solo>)
LIES     <how this check produces a false pass>
```

Seven lines. If it does not fit, the item is really two items.

Worked, for a `PatchOperationRemove` against a spawn table:

```
ITEM     Armadillo dropped from Desert spawns (Jawa_Patches/Biomes.xml)
SEE      A freshly generated Desert map's wildlife tab lists no Armadillo, and
         the live def dump shows 2 children under race/wildBiomes
ROUTE    Load -> refresh the def dump -> read ThingDef Armadillo -> generate a
         NEW Desert map (an existing save re-runs no GenStep) and open Wildlife
PREDICT  exactly 2 wildBiomes children — was 3 (Desert, AridShrubland,
         TropicalSwamp)
CLOSE    The dump shows 2 — NOT chasing: Armadillos already spawned on old maps
RIDE     batch — pure XML, validated clean, named log string to grep
LIES     Remove deletes EVERY match (§4), so "Desert is gone" is also what a
         too-greedy xpath looks like. Count the survivors, not the removal.
```

---

## 9. Keep this skill learning

This domain's knowledge is almost entirely *earned* — each trap costs a debug
cycle to find and is then cheap forever. That only compounds if it gets written
down, so treat capture as part of finishing the task, not as optional polish.

**The live log is `references/traps-*.md`, indexed by `references/traps.md`.**
Read the **index** at the start of a RimWorld task, then open the one topic file
that matches what you are about to do — patches, tooling, art, the mod stack, or
diagnosis. Reading all five is not the intent and costs ~25k tokens.

**If you are already running, do not reread — take the delta.** A session that has
read the index is stale only by what peers appended since. `python3
src/RimMandrake/Utils/whats_new.py --seat <SEAT>` prints those added headings in a few lines; a
full reread buys the same information for ~25k tokens, which is why it gets
skipped. Run it when the game loads, or any time you want it.

**After any RimWorld task, ask: did anything here surprise me?** If yes, append an
entry to the matching topic file and add its title to the index in the same commit.
⚠️ **But most candidate lessons should be REJECTED** — `references/traps.md` carries
a five-part admission test, and an entry failing any one of them is not a trap.

**The entry format, the admission test, the promote-into-this-file rule, the
forty-entry split threshold and where the canonical copy of a skill lives are all
in `references/traps.md` → "Capture, rejection, promotion".** Open it before you
write an entry — kept in one place so the two cannot drift apart.

---

## Reference files

| File | Read it when |
|---|---|
| `references/traps.md` | **First, and append last.** The *index* of earned lessons — routes to five topic files; open the one you need, never all five. **Entry counts live in its "Which file" table and nowhere else** — they were duplicated here and went stale by 24. |
| ├ `traps-tooling.md` | **If you read only one, read this.** Nearly every entry is a tool that answered a different question than the one asked. |
| ├ `traps-xml-and-defs.md` | Before writing a patch — these cost a game load, not a rerun. |
| ├ `traps-mods-and-managers.md` | A mod is absent, dead, or ignoring its files. |
| ├ `traps-art.md` | Before calling art missing, wrong or broken. |
| └ `traps-diagnosis.md` | Before trusting a diagnosis, or calling into a running game. |
| `references/patch-operations.md` | An xpath won't match; you need the operation table, inheritance, worked examples, `LoadFolders.xml` (§9), the validator's blind spots (§10) or why an `<li>` destroys a def (§11). |
| `references/player-log-triage.md` | **Whenever you are reading a `Player.log`.** The five severity rungs in full, what each error actually costs, and the judged-safe list. |
| `references/load-order.md` | An inheritance error appeared, you are writing the order assertion, or you are about to touch a sorter's rules database. |
| `references/spending-a-load.md` | You are planning a load — what to verify offline, what may ride along in the batch, what to harvest. |
| `references/csharp-and-loading.md` | Before writing any C# — Harmony, entry points, `LoadFolders.xml`. |
| `references/minimal-load.md` | You have decided to cut the stack down to corner a bug. |
| `scripts/validate_patch.py` | Every patch **and every def**, before it goes near the Mods folder. Point it at the mod ROOT: it dispatches on the root element and its banner states what it did and did not scan. |

External, when the references above don't cover it:
[RimWorld Modding Resources hub](https://spdskatr.github.io/RWModdingResources/) ·
[PatchOperations wiki](https://rimworldwiki.com/wiki/Modding_Tutorials/PatchOperations) ·
[Zhentar's xpath guide](https://gist.github.com/Zhentar/4a1b71cea45b9337f70b30a21d868782)
