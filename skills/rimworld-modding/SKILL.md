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
MINIMAL load instead.** Removing one suspect at a time costs a full load per
guess and only ever tests the guess you already had. Cutting to the ~20 mods
that can possibly be involved costs **one** load and answers a better question:
*does the feature work at all in isolation?* Either answer is progress — a
known-good baseline to bisect upward from, or proof the fault is in the
feature's own mods rather than the stack.

Because it costs about one load, minimising becomes the cheapest option far
earlier than it feels like it should: at the point where you notice you are
*generating* hypotheses rather than *testing* a theory. **The procedure — how to
derive the set rather than guess it, and the two traps inside the reduced set —
is in `references/minimal-load.md`.** Read it when you decide to minimise.

**Verify everything verifiable offline, first.** Defs, About.xml, ModsConfig.xml
and the whole Workshop tree are ordinary files sitting on disk right now. Run
`scripts/validate_patch.py`, parse every XML you touched, confirm the load order
in `ModsConfig.xml` rather than trusting the manager's UI, and cross-check def
references by grepping the mods themselves. Anything you can establish from
files, establish from files. A restart should be confirming a prediction, not
conducting an experiment.

**Batch by risk, not by count.** The one-change-at-a-time rule exists to keep
attribution possible when something breaks — it is about *ambiguity*, not about
quantity, so batch anything whose effects are distinguishable. Config-level
changes (load order, mod settings, un/subscribes) carry near-zero attribution
risk and should always ride along. A pure-XML patch that validated clean and has
named log strings to check is also safe to include, because you know exactly
what evidence would convict it. Keep genuinely ambiguous changes solo: a new C#
assembly, a mod that patches broadly, or two changes that touch the same system.
Say out loud which bucket each pending change is in before proposing a batch.

**Harvest the whole log, not just your change.** After a restart, read the entire
`Player.log` and update the triage list — the mod that just broke unrelatedly,
the new unresolved reference, the count that moved. You paid for a full load; a
single yes/no answer is a poor return on it. Keeping a running "next restart"
queue between loads is what makes this cheap: changes accumulate in a list, and
each load clears the list and refills the evidence.

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

Getting this backwards is the most destructive mistake in this document, because
it does not fail quietly. Add `<li>` into a dictionary-keyed field and the engine
looks for a def literally named `li`, fails to resolve it, and **discards the
entire parent def** — a def that was working fine before you touched it. The only
log evidence is one cross-reference error naming `"li"`, followed much later by
hundreds of unrelated-looking failures from everything that referenced the def
you just destroyed. `validate_patch.py` compares your `<value>` against the live
node's existing children for exactly this reason.

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
what else is loaded**, via `LoadFolders.xml`:

```xml
<v1.6>
  <li>1.6</li>
  <li IfModActive="sarg.alphabiomes">1.6/Mods/AlphaBiomes</li>
  <li IfModNotActive="Ludeon.RimWorld.Odyssey">1.6NotOdyssey</li>
</v1.6>
```

That last line is real: Vanilla Animals Expanded drops its badger, moose, muskox
and porcupine when Odyssey is active, because Odyssey ships its own. So the def
set is a function of the whole mod list, and "the mod is installed" tells you
nothing about which of its defs exist. When a reference goes missing while its
owning mod is plainly present, **read that mod's `LoadFolders.xml` before
concluding anything** — the def may be in a folder your configuration excludes.

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

It checks: the file parses; no comment contains `--`; every `Operation` has a
`Class`; ops are conditional-wrapped; the conditional test xpath matches the
inner op's xpath; and — this is the valuable one — it **runs each xpath against
the real Defs on disk and reports how many nodes it hits**. Zero hits means the
patch would silently do nothing. More hits than you expected means a
`Remove` is about to take out more than you think.

A patch that validates clean can still be wrong about *intent*, so also confirm
in-game: load, then check the dev console (or `Player.log`) for the patch's own
name. Silence is success.

### Two things it cannot see — know these before trusting a result

**It reads the defs as they sit on disk, unpatched.** Other mods' patches have
not run. So a node that another mod *creates* at runtime is invisible, and the
validator calls your perfectly correct xpath a zero-match silent no-op. When you
are patching something a compat patch added, **0 matches is the expected
result** — and it also tells you the fix now depends on load order, because you
must apply after whoever creates the node.

**It only validates `Patches/`. It does not check `Defs/` at all.** A hand-written
Def with a field that moved between versions sails straight through. That is
exactly how `<exposedThought>` shipped in one of our own WeatherDefs when 1.6 had
renamed it to `<weatherThought>`. Until the tool covers Defs, diff any Def you
author field-by-field against the closest Core def — §1, applied to your own
files.

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

**The damage escapes your mod.** A `PawnKindDef` that failed to inherit has no
`race`, so `RaceProperties` is null on it — and vanilla code enumerates *all*
pawnkinds. That produced NREs inside `ThingDef.ResolveIcon`,
`ScenPart_StartingAnimal.PossibleAnimals` and `BiomeDef.CommonalityOfAnimal`,
breaking map generation. **None of those stack traces named a mod.** If worldgen
starts throwing, grep the log for `Could not find parent node` and
`Config error in <YourDefPrefix>` before believing it is a vanilla bug.

**Assert the order in code before every launch.** Not by eye, not by trusting
the manager. Resolve the load set, find the index of your mod and of each mod it
patches, and fail loudly:

```python
low = [m['packageId'].lower() for m in mods]
for mine, target, why in CHECKS:
    assert low.index(mine) > low.index(target), f"{mine} must load after {target}: {why}"
```

Keep one entry per mod you actually reach into. A three-check version passed
while the order was still broken for a fourth mod.

### Teach the mod manager, or it will keep undoing you

RimSort (and similar) re-sort on demand and will silently scatter your mods.
Fixing the resulting order by hand works but treats the symptom. The manager has
a **user rules** database — for RimSort,
`%LOCALAPPDATA%/RimSort/dbs/userRules.json` — and the distinction that matters
is:

- **`loadBottom`** is a *hint*. It asks for "near the end" and creates no edge,
  so nothing prevents another mod landing after you. Several mods claim it and
  it cannot order them among themselves.
- **`loadAfter`** is a *constraint*. A topological sort cannot violate it.

Write one `loadAfter` edge per mod you patch. After that the manager produces the
right order unaided and your assertion becomes a cheap safety net rather than a
repeated repair.

⚠️ Two traps in the rules file itself. It is keyed by `packageId`, so **renaming
your mod silently orphans every rule** — a stale rule for a dead packageId is
indistinguishable from no rule, which is exactly how this went unnoticed for
days. And the manager holds rules in memory and rewrites the file on exit, so
**close it before editing, and reopen to confirm your edit survived.**

Do not hand-edit the *community* rules database: it is a git clone refreshed on
startup, so local changes vanish. Community rules are a pull request to a public
third-party repo, which is the user's call, never yours.

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

## 7. Debugging from Player.log

`%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`

Triage in this order, because it sorts by severity of consequence rather than by
position in the file:

1. **`grep -n "static constructor\|TypeInitializationException\|ReflectionTypeLoadException"`** — these mods are *dead*, not noisy. A mod that
   throws in its static constructor did not load at all, and it will not say so
   again later. In a large stack, failures concentrate here: mods that reflect
   over *other mods'* types at startup are the fragile class.
2. **`Could not execute post-long-event action`** — one queued post-load action
   failed. **It cost exactly that action; the queue continues.** Verified against
   the IL of `Verse.LongEventHandler.ExecuteToExecuteWhenFinished` (1.6.4871):
   the `try` spans 18 bytes around a single `Action::Invoke`, the catch logs via
   `Log.Error`, and its `leave` targets the loop *increment*, not the exit. The
   loop even re-reads `.Count` each pass, so actions queued during execution
   still run.

   Severity is therefore per-action — usually one def's `ResolveIcon` — not
   "everything after this silently didn't happen." Weigh it accordingly before
   blaming unrelated breakage on it, or disabling a mod over it.

   ⚠️ The one real abort path in that method is *outside* the try: the
   per-iteration DeepProfiler block dereferences
   `action.Method.DeclaringType`. An NRE there escapes the loop, skips the final
   `Clear()`, and leaves the re-entry flag set — which bricks the queue
   permanently behind "Already executing." Distinguish the two by the stack: a
   frame for the queued action itself (e.g. `BuildableDef.<PostLoad>b__78_0`)
   means the survivable path.
3. **`Could not resolve cross-reference`** — a def referenced something absent.
   Usually a `MayRequire` guarding the wrong thing (see §4). **Do not file these
   as harmless without reading the `wanter`.** The consequence depends entirely
   on the field that wanted it:

   - **A plain `List<Def>` field** (`wanter=pawnKindDefs`, `thingDefs`, …) drops
     the unresolved entry and degrades gracefully. Genuinely benign.
   - **A record that later becomes a dictionary key** — `BiomeAnimalRecord`,
     `WeatherCommonalityRecord` and their kin — keeps the record and leaves the
     def field **null**. The next consumer to build that dictionary calls
     `Add(null, …)` and throws `ArgumentNullException: key`, which kills whatever
     mod touched it first, in its static constructor, far from here.

   Five such lines, filed as "five spawn-table entries are skipped", were the
   sole cause of a dead mod for three loads running. A large count still means
   content is silently incomplete; a *small* count is not evidence of safety.
4. **`Patch operation ... failed`** — a no-op. Almost always benign, and the most
   common noise category in a big stack.
5. **Translation errors, missing sounds** — cosmetic. The engine says so itself
   ("using undefined sound"). Do not spend time here.

Two behaviours worth keeping:

**Maintain a triage list of errors judged safe**, with the exact log string, the
owning mod, the root cause, and *why* it's harmless. If you can't fill all four,
it isn't safe yet — it's just unexplained. Without this list you re-investigate
the same benign noise every single load.

**Load order can look like a code bug.** A `ReflectionTypeLoadException` naming
another mod's types usually means load order, not a broken assembly: a mod can
declare a `modDependency` and still load *before* it, because dependency ≠
ordering. `loadAfter` is what orders. When it's missing upstream, fix it locally
with a sorter rule rather than touching the mod.

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

**After any RimWorld task, ask: did anything here surprise me?** A patch that
didn't apply, a field that moved, a mod that failed in an unfamiliar shape, an
xpath idiom that took three tries. If yes, append an entry to the matching topic
file, and add its title to the index in the same commit. **The entry format, and
the rule for choosing a file, live in `references/traps.md`** — kept in one place
so the two cannot drift apart.

⚠️ **Most candidate lessons should be REJECTED.** `references/traps.md` carries a
five-part admission test — specific, non-obvious, actionable, domain-bound, still
true — and an entry failing any one of them is not a trap. General software or
process wisdom goes to `DOC_BUDGET.md` or `agents_def.md`; a log full of aphorisms
is worse than no log, because the real entries stop being findable.

If an entry would change what this skill tells you to do *by default*, don't leave
it in the log — **promote it into the body of this file** and delete the log entry.
The log is a staging area, not an archive; when **one topic file** grows past roughly
forty entries, split it rather than append.

> ⚠️ **That threshold went unenforced for eleven entries.** The log was one flat
> file and reached **51**, because *a rule a document states about itself is the
> one nobody is assigned to check.* Split 2026-08-12 into five topic files
> (largest: 17). If you notice a file over forty, you are the one who noticed.

**Where the canonical copy lives.** An installed skill is a read-only cache;
editing it there changes nothing durable. Edit the copy in the user's project,
re-package, and say it has been **delivered** rather than saved — installing it
is theirs to do.

---

## Reference files

| File | Read it when |
|---|---|
| `references/traps.md` | **First, and append last.** The *index* of earned lessons — routes to five topic files. Open the one you need, never all five. |
| ├ `traps-tooling.md` (17) | **If you read only one, read this.** Nearly every entry is a tool that answered a different question than the one asked. |
| ├ `traps-xml-and-defs.md` (13) | Before writing a patch — these cost a game load, not a rerun. |
| ├ `traps-mods-and-managers.md` (10) | A mod is absent, dead, or ignoring its files. |
| ├ `traps-art.md` (7) | Before calling art missing, wrong or broken. |
| └ `traps-diagnosis.md` (4) | Before trusting a diagnosis, or calling into a running game. |
| `references/patch-operations.md` | An xpath won't match; you need the operation table, inheritance or worked examples. |
| `references/csharp-and-loading.md` | Before writing any C# — Harmony, entry points, `LoadFolders.xml`. |
| `references/minimal-load.md` | You have decided to cut the stack down to corner a bug. |
| `scripts/validate_patch.py` | Every patch **and every def**, before it goes near the Mods folder. Point it at the mod ROOT: it dispatches on the root element and its banner states what it did and did not scan. |

External, when the references above don't cover it:
[RimWorld Modding Resources hub](https://spdskatr.github.io/RWModdingResources/) ·
[PatchOperations wiki](https://rimworldwiki.com/wiki/Modding_Tutorials/PatchOperations) ·
[Zhentar's xpath guide](https://gist.github.com/Zhentar/4a1b71cea45b9337f70b30a21d868782)
