---
name: rimworld-modding
description: Author, patch, validate and debug RimWorld mods — XML PatchOperations, custom Defs, C#/Harmony assemblies, def inheritance that breaks across load order, and Player.log triage. Use this whenever the user mentions RimWorld modding, a mod conflict, a Def, a patch, an xpath into Defs, a ParentName or abstract def that will not resolve, a red error in the dev console, or asks to make/fix/analyse anything under a RimWorld Mods folder — even if they just paste a log excerpt and ask "what is this". Also use it before writing any file into a mod folder, because RimWorld's XML has several silent-failure modes that are easy to hit and hard to see.
---

# RimWorld modding

Most of the hours lost here were lost because somebody wrote a plausible thing and did not read the real thing. Three facts make this domain different:

- A patch fails *silently*.
- XML comments have a syntax rule that most people do not know (§4).
- One bad Def entry can kill three unrelated mods at startup, with an error that names none of them.

**The method: find the ground truth on disk, write the smallest change that survives a mod being absent, prove the change before you ship it, and record what you learned.**

The words used here:

| word | meaning |
|---|---|
| def | one XML element under `<Defs>` that becomes one game object. Its `defName` is its name |
| patch, xpath | a `PatchOperation` in `Patches/*.xml`; the xpath is the address of the XML nodes that the operation edits |
| no-op | an operation that changes nothing |
| load set | the mods and folders that the game loads, in load order |
| minimal list | a small mod list that loads in seconds; the full list is the owner's whole list |
| def dump | the RimDefDump mod's record of each def in a running game, after all patches |
| bridge | the RimBridge connection that drives a running game (`jawa/...` tools) |

The dates, old figures and retired lines of this file are in [references/history.md](references/history.md).

---

## 1. Read the real file first. Always.

Before you write a line of a patch, open the def that you patch. Also open each def that the patch relies on or works *around*. Open the actual XML in the mod folder that loads now. Do not use the version on a wiki. Do not use what a project doc said last month. The read costs thirty seconds.

→ the grep command: `references/traps-xml-and-defs.md`.

Three reasons make this read matter more here than elsewhere:

- **A failed PatchOperation is a no-op, not an error you'll notice.**
  - The game prints one error in a log of thousands of lines. Nothing else breaks.
  - The patch did not happen, and you will believe that the patch worked.
- **Def names are redefined by other mods.**
  - The `Armadillo` that you see in Core is possibly not the `Armadillo` that wins.
  - Across mods, the last loaded def with a given `defName` replaces the earlier ones entirely.
- **Fields move between versions.**
  - `<wildness>` was valid on `RaceProperties` and is not in 1.6. Wikis lag by a version.
  - Read `XML error: <field> doesn't correspond to any field in type X` as a **version-drift** report, not as a typo. The mod is older than the game.
  - Usually the game drops the value, and the def loads anyway. The count of such lines is the severity: eight lines mean eight races that are wrong in silence.
  - ⚠️ "Loads anyway" is not always true. `<wildness>` or `<leatherLabel>` inside `<race>` can crash the **whole mod load**. The mechanism: `references/traps-xml-and-defs.md`.

When you find the ground truth, **quote its file path and the exact snippet in a comment at the top of the patch**, with a date. Then the next agent reads that comment and does not repeat the search.

### 1b. Three sources of truth, and the one question each answers

Pick the source by the QUESTION, not by habit:

| question | source |
|---|---|
| *How does vanilla implement this? What is the real class/method/signature?* | the **`rimsage`** MCP tools (`search_source`, `read_csharp_symbol`, `search_defs`, `get_def_details`) |
| *What did OUR mod stack actually load?* | the **def dump**: the newest folder in `…\LocalLow\…\DefDump\captures\`, its `defs\*.json`. Check its fingerprint first (`skills/rimworld-deploy/SKILL.md`); get a count from `measure count <DefType>` (if the shell has no `measure`, the `measuring-large-artifacts` skill gives its path) |
| *What is true in the running game right now?* | the **bridge**: see `skills/rimbridge/SKILL.md` |

- 🔴 **`rimsage` indexes vanilla and DLC only. `rimsage` never scans mod folders.**
  - A "not found" from `search_defs` or `get_def_details` is **not** evidence that a def does not exist.
  - Each `OuterRim_`, `BTD_`, `AB_` and `GarryFlowers_` def of our campaign is invisible to `rimsage` by construction.
  - For a def that we author or patch, the def dump is the authority. `rimsage` cannot help there.
- **Use `rimsage` before you choose a Harmony patch target**, and before you write again what vanilla already does. Root `CLAUDE.md` says: "Do not guess a defName, field or namespace."
- ⚠️ **A `merged` def view of `get_def_details` is not the merge of the engine.** The `rimsage` resolver concatenates the parent list and the child list. RimWorld does not always do that. Settle an argument about inheritance with the def dump, not with `get_def_details`.
- ⚠️ **The text inside `DefDump/dump_request.txt` is the capture mode**: `all` or `animals`. The file is not an on/off flag.
  - If the file is empty or holds another word, for example `1`, you get an animals-only capture with no `defs/`. That wastes the dump. Write `all`.
- **For C# that `rimsage` misses, read the decompiled 1.6 tree** at `D:\ClaudeWork\rimmandrake\decomp\rw16` (the `.cs` files are in its `all` folder).
  - Before you trust the tree, compare the md5 of its `Assembly-CSharp.dll` with the installed file. The two were equal on 2026-11-23 (game 1.6.4871).
  - To decompile one type in seconds: `ilspycmd.exe -t <FullTypeName> <RimWorld>\RimWorldWin64_Data\Managed\Assembly-CSharp.dll > out.cs`.
  - `ilspycmd` (v8.2) is `C:\Users\<user>\.dotnet\tools\ilspycmd.exe`. From WSL, the path is `/mnt/c/Users/<user>/.dotnet/tools/ilspycmd.exe`.
  - A static helper can be in `Verse` and not in `Verse.Sound`. Write the output under `D:\ClaudeWork`.
- The study of `rimsage`: `research\RimMandrake\reference\rimsage_rimcp_source_index_mcp.md`. The provenance of the decompile: `research\RimMandrake\reference\rimworld_decompiled_source.md`.

**One negative observation is not a mechanism: read the consuming code before filing the fix.**

- A write can report success while nothing changes, or an expected thing can be absent. Then read the mechanism next. Do not write the finding yet.
- A wrong mechanism gives a finding that agrees with itself, passes review and gets acted on. Four filed findings each died on one direct check:
  - a census read `Defs/` while the content was in `Patches/`;
  - a tool ran at a settled game;
  - `FactionGenerator.InitializeFactions` returns early when the caller passes a faction list;
  - a `def` field is read once at worldgen and never at draw time.
- `mcp__rimsage__search_source` and `mcp__rimsage__read_csharp_symbol` (`typeName` plus optional `memberName`) read the real C# in one call. Before you file an item whose fix depends on "field X does Y", paste the consuming method into the item.
- If a thing occurs only a few percent of the time, a single tile or click cannot settle anything about it.
- When a filed finding is refuted, drop the item in the same action. Do not leave the item in the queue with a header that explains the error. People read the spec before the note, so they act on the false spec.

**The cheapest disproof is a control artifact you never touched.**

- Data that you produced can look corrupted. One case: 181 of 744 authored weights read 0. Then find the nearest instance that you did NOT produce, and look at that instance.
- In that case, a vanilla biome that the project does not patch showed the same zeros. So the pipeline was innocent, and each theory about the pipeline was wasted.
- The control costs one read. A control beats a subagent, because a subagent repeats the theory that it was given.
- If the owner pushes back ("I'm not sure I believe this"), find the mechanism. Do not run the same probe again.

**For animal and def data the three sources are the offline `Defs/` scan, the live dump and `Player.log`, and the join is the deliverable.**

- The offline scan (`src/RimMandrake/Utils/animal_inventory.py`) answers "what did the author write, and where do I patch it". Only this source has provenance (mod, file, xpath).
  - ⚠️ The offline scan selects an animal by the `<race>` element of the def ITSELF. A ThingDef that inherits its whole `<race>` block is dropped in silence (§ animal_inventory.py drops defs that inherit <race>).
- The live dump (`src/RimMandrake/RimDefDump`, a C# startup mod) answers "what exists at runtime", after patches and after overrides.
- `Player.log` shows only what is broken. A full load had ~15 dangling cross-references and ~22 config errors. `Player.log` does not list defs. The huge `[Source: X]/[File: Y]` blocks are the "Possible Matches" hint under each error, not a load trace.
- Join the sources with `src/RimMandrake/Utils/animal_live_diff.py`.
- RimBridge cannot list the whole def database, so RimDefDump exists. Do not argue this again. There is no `list_defs` tool, `run_lua` forbids CLR access, and the vanilla `DebugOutputsEcology` tables render to a dialog, not to the log.
  - `jawa/get_def` and `jawa/get_defs` read only the defs that you name. `jawa/rimdefdump_run` starts a dump of a running game.
- A 0% coverage column is far more likely a dead xpath than an empty field. 1.6 dropped the fields that four columns read (see DEAD XPATHS in `animal_inventory.py`).

---

## 2. The game restart is the scarce resource

- A cold load of the full list takes about 15 to 30 minutes. The measured times are in `skills/rimworld-load-round/SKILL.md` §0.
- **Arrive at the restart already confident.** A restart confirms a prediction. A restart does not conduct an experiment. **"restart and see" is never an answer.**
- **After the second failed hypothesis about one bug, stop.** Cut the mod list down to the mods that can be involved: `references/minimal-load.md`.

### ⛔ HOT RELOAD IS RETIRED — do not call `jawa/hot_reload_defs` (owner's ruling, 2026-09-03)

> *"I recommend we give up on hot reload xml capability as unstable. … let's retire
> that capability as desirable for now and possibly forever."*

Hot reload means that the running game reads its defs again, without a restart. **This ruling supersedes the ruling of 2026-09-01.** The older ruling made hot reload the default for tier-b work (XML defs and patches, §3). The older ruling is dead.

**The replacement is the minimal-list restart, and that restart costs almost nothing.**

- Deploy the XML. Restart on the minimal list. Read the field back.
- The restart took **22 seconds** on the 13-mod list of 2026-08-19. A quicktest world adds ~5 s. The minimal-list restart is now the cycle for tier-b work.
- Hot reload looked worth having only because it saved a load. The minimal list has almost no load to save.

**Why it was retired — measured, on the full 589-mod list, 2026-09-03:**

- The call hung the bridge for about five minutes. Afterwards no pawn of any kind could be generated, and each health flag still read healthy.
- → the full measured incident: `references/spending-a-load.md`.

**What this ruling does NOT change:**

- **`jawa/get_defs` stands.** The batch read of def fields still shows what the running game holds. By default, a list or an object field comes back as a type name. With `deep=true`, the read also returns nested fields, to 3 levels.
- **XML changes still never justify a *full-list* restart.** The answer moved from hot reload to the minimal list, not to a 25-minute load.
- **C#, Harmony and companion-DLL work is untouched.** That work always needed a real load, and still does.

**How to check that this ruling landed:** no run sheet, ladder or skill names `jawa/hot_reload_defs` as a step to take. A doc that still tells you to call it is older than 2026-09-03. This section beats that doc.

**→ `skills/rimworld-load-round/SKILL.md` is the whole subject.** That skill owns:

- the 13-mod minimal list that loads in 22 seconds;
- `modlist_swap.py`;
- how to batch by ambiguity;
- the log strings that you name in advance;
- the harvest of the log.

Read that skill before you call or queue a load.

---

## 3. Pick the implementation tier before you pick the code

Most "how do I do X in RimWorld" questions ask "at which layer does X belong". A wrong layer is expensive. People write a C# mod for a thing that a six-line XML patch does. People also try to patch a def for a thing that exists only at runtime.

Work down this ladder. Stop at the first tier that can do the job:

| Tier | Layer | Use when the thing must… | Cost to change later |
|---|---|---|---|
| a | Mod list / settings / scenario | be true before worldgen | free |
| b | XML Def patch | be *true of the game* — stats, spawns, recipes, names | cheap |
| c | C# / Harmony assembly | *behave* differently — new mechanics, new AI | expensive |
| d | Save-game edit | be true of one existing colony, retroactively | one-shot, risky |
| e | Live runtime manipulation (bridge/console) | *change during play* | ephemeral |
| f | External host-side tooling | analyse or generate outside the game | free |

- **The rule of thumb: bake what must be TRUE, script what must be PLACED, run live only what must CHANGE.**
- If a value never varies during a playthrough, the value belongs in tier b. No exception.
- Do not take C# because XML feels weak. C# in place of XML is the most common overbuild in this domain.

⚠️ **Prove that a comp exists before you scope tier b around the comp:** `grep -rln "CompProperties_<Name>" "$RW/Data"`. `$RW` is the RimWorld folder. Zero hits means that no vanilla def uses a comp of that name.

- Zero hits for a guessed name does not prove that no comp exists. Read the `<comps>` of a vanilla def that has the mechanic.
  - The example: there is no `CompProperties_ShieldBelt` in 1.6, so that grep finds nothing. `Apparel_ShieldBelt` carries `CompProperties_Shield`. That comp reads the stats `EnergyShieldEnergyMax` and `EnergyShieldRechargeRate`.
- If no comp drives the mechanic, a stat drives the mechanic, or code in the `thingClass` does. Read the code to see which one.
- Code in the `thingClass` moves the job to tier c. A new C# assembly rides a game load alone and does not batch. The one exception is the three-assembly waiver (`skills/rimworld-load-round/SKILL.md` §3).

---

## 4. Writing an XML patch

### The shape to default to

Put each operation inside a `PatchOperationConditional` that tests for the exact node that you are about to touch.

- The conditional makes a patch safe in three cases: the mod is absent, the user updates the mod, the author fixes the bug upstream.
- An unconditional patch against a missing node prints a red error at every launch. That trains the user to ignore red errors.
- A conditional that matches nothing logs nothing. So a clean log does not prove that the patch applied (§5).
- Keep the test xpath and the inner xpath **identical**, unless you have a stated reason. Two different xpaths test for one thing and modify another.

→ the same conditional-wrapped example, worked in full: `references/patch-operations.md`.

### The things that bite everyone

**The shape of XML**

- **Take a field's SHAPE from a shipped def, never from a spec or a sample.** A spec names fields; a def defines shapes. A plain list uses `<li>`. A field keyed by def uses the def name as the element name (`<wildBiomes><Desert>0.3</Desert>`). The C# type of the field decides, so the shape is the same in every mod. (A true C# `Dictionary` is a third shape: `<li><key>…</key><value>…</value></li>`.)
- **An `<li>` in a field keyed by def makes the engine discard the entire parent def.** An `<li>` there is the most destructive mistake in this document. The def worked before you touched it, and no log line names the def. The sign is `No Verse.WeatherDef named li found`, under many later errors.
  - `validate_patch.py` catches this in `Patches/`. The validator cannot catch such an `<li>` in a `Defs/` file that you author.
- **A mis-CASED enum value discards the whole target def, exactly like the `<li>` mistake.** The parse is case-sensitive: `water` is not `Water`. The log has at most one line, `Exception loading def from file …`, and no def name. A generator must refuse an unknown or wrongly cased member.
- **Match the def's XML ELEMENT NAME, not `ThingDef`.** The loader reads the element name as the C# type. So `/Defs/ThingDef[…]` misses a `<VFEPirates.WarcasketDef>`. Only the XML of the mod tells you the element name. The def dump never does.
- **XML comments cannot contain a double hyphen.** `--` anywhere inside `<!-- -->` is a hard parse error. The error takes the whole file. Use `===` for rules, and `→` or `to` for arrows. Never replace `->` across a file: that breaks each `-->`.
- **`Graphic_Random`'s `texPath` names a FOLDER, not a file stem.** The path is `Things/.../ScrapNest`, with `ScrapNest_a/b/c.png` inside that folder. The validator can also flag a CORRECT vanilla `texPath` as ERROR. Read the reason before you trust that ERROR.

**How patches act**

- **Patches run BEFORE `ParentName` inheritance resolves**, so a patch sees raw XML. A node that a def only inherits is absent, and an `Add` into that node fails. Guard on the container (`…/statBases`), not on the leaf. Let `<nomatch>` add the whole element.
- **A child's `<li>` list is APPENDED to the parent's list.** To replace the list, write `Inherit="False"` on the child's element (`references/patch-operations.md`).
- **`PatchOperationRemove` deletes every match, not the first one.** There is no "remove one". Use a positional predicate (`.../TropicalSwamp[2]`), and put the same predicate in the test.
- **A `PatchOperationReplace` against a def YOUR OWN MOD declares wins silently.** Patches run after every def loads, in the same mod or not. Check for this when a generated `Patches/` file and a hand-authored `Defs/` file touch the same defName.

**Bulk renames**

- **Migrate by NODE, never by string.** A defName is unique inside one def *type*, not across types. Name the xpath or the parent element that you change. Count the references before and after.
- The same blind find-and-replace also hits a `<texPath>` value that happens to equal the old defName. Nothing resolves a `texPath` at patch time. After a bulk rename, resolve each `texPath` against the files on disk.

**Guards**

- **`MayRequire` and `PatchOperationFindMod` check the mod, not the def.** A mod can delete a def and stay installed. When you *depend* on a def, guard with `PatchOperationConditional` on that def.
- 🔴 **`MayRequire` on a bare `<Operation>` element inside a Patch file does nothing.** Each such operation runs unconditionally. Use `PatchOperationFindMod` (its `<mods>` takes the exact About.xml `<name>`, never the packageId), or a `PatchOperationConditional` on the def.
- 🔴 **`MayRequire` on the def's OWNING mod is not proof the def loads.** `LoadFolders.xml` can ship a def only when a THIRD mod is active. Put the packageId of that third mod in your `MayRequire` too.
- The reason that this is so common: **a mod can ship different defs depending on what else is loaded**, via `LoadFolders.xml`. So the def set is a function of the whole mod list. When a reference is missing while its owning mod is present, read the `LoadFolders.xml` of that mod before you conclude anything.

→ full paragraphs and the incidents behind every rule above: `references/patch-operations.md` and `references/traps-xml-and-defs.md`.

### Which operation

`Add` (child) · `Insert` (sibling) · `Replace` · `Remove` (deletes **every** match) · `AttributeAdd`/`Set`/`Remove` · `SetName` · `AddModExtension` · `Sequence` (stops at first failure) · `Conditional` (`match`/`nomatch`) · `FindMod`.

- `PatchOperationTest` is obsolete. Use `Conditional`.
- **The full table of what each operation takes, plus xpath idioms and inheritance (`ParentName`/`Abstract`), is in `references/patch-operations.md`.** Read that file when an xpath does not match. Read that file also before you use an operation other than `Add`, `Replace` and `Conditional`.

---

## 5. Validate before you deploy

Run the bundled validator on each patch file and each def file before the file goes near the Mods folder. The validator catches the silent failures. Each of those otherwise costs a full game restart to find.

```bash
RWS="/mnt/c/Program Files (x86)/Steam/steamapps"     # WSL paths, for python3
python3 skills/rimworld-modding/scripts/validate_patch.py path/to/Patch.xml \
    --defs "$RWS/common/RimWorld/Data" \
    --defs "$RWS/workshop/content/294100" \
    --defs "$RWS/common/RimWorld/Mods"
```

- With `python.exe`, write Windows paths (`C:/Program Files (x86)/...`). WSL `python3` cannot read a `C:/` path: the validator then prints UNMEASURABLE and gives no verdict.
- Add `--live <DefDump folder>` or `--defnames <file>` to check names against the running game's defs (`skills/rimworld-deploy/SKILL.md`).
- 🔴 **Pass the Mods folder too.** First-party mods are there, not in Workshop content (`references/patch-operations.md` has the failure that this avoids).
- The valuable check **runs each xpath against the real Defs on disk and reports how many nodes the xpath hits**. Zero hits means that the patch does nothing, in silence. More hits than you expect means that a `Remove` is about to take out more than you think. (The other five checks are in `references/patch-operations.md`.)
- A patch that validates clean can still be wrong about *intent*. So also confirm in game: load, then look in the dev console (or `Player.log`) for the id of your mod and the file of the patch. Then read the changed field back with `jawa/get_defs`. A silent log alone proves nothing, because a conditional that matches nothing logs nothing.

### Two things it cannot see

- The validator reads defs **unpatched**. A node that another mod creates at runtime is invisible. So **0 matches can be the correct answer**.
- The validator checks field names in no file. So a hand-authored Def with a field that moved between versions passes.

Both are in `references/patch-operations.md`, with the WeatherDef that shipped a renamed field.

---

## 5b. Load order is a constraint you must ASSERT, not a preference

If your mod patches the defs of other mods, your mod must load after each one of them.

- **`ParentName` resolves only against a `Name=` attribute, never against a `defName`.** A `ParentName` that names no `Name=` gives `Could not find parent node named …`. The def then loads with nothing from that parent. Most named parents are `Abstract="True"`; the engine does not require that.
- **`ParentName` inheritance is load-order dependent.** A def does not inherit from a parent that is declared only in a mod that loads *later*. Everything that the parent supplies is missing.
- **The damage escapes your mod**, and none of the stack traces name your mod. A failed inheritance breaks *vanilla* code that enumerates all defs of that type, worldgen included. If worldgen throws, first search the log for `Could not find parent node` and `Config error in <YourDefPrefix>`.
- **Assert the order in code before every launch.** Do not check by eye, and do not trust the mod manager. Resolve the load set. Compare the index of your mod with each mod that you patch. Fail loudly. Write one check for each mod that you reach into.
- **`references/load-order.md` holds the three NRE sites that proved it, the assertion snippet, and why the community rules database must not be hand-edited.** (An NRE is a null reference exception.) Open that file when an inheritance error appears, when you write the assertion, or before you touch the rules database of a sorter.

Five more rules:

- 🔴 **`ParentName` resolution keys on the `Name=` attribute in a FLAT NAMESPACE NOT scoped by def type.** Give a `ThingDef` and its `PawnKindDef` two different `Name=` values (suffix the second with `_Kind`). In one mod, the second def with the same `Name=` logs an error and is not registered. In one mod or across mods, a child of that name can then inherit the fields of the wrong type. The same `defName` on both is fine.
- 🔴 **A same-mod `Patches/` load-order fix that sorts "after the one file I know adds the duplicate" is not enough.** A THIRD file in the same folder can sort after your fix and break the fix again. Only a filename that sorts after EVERY file in that folder is safe: a `ZZZ_` prefix. Confirm with a fresh capture after the restart.
- 🔴 **`DefDatabase<T>.Add` does not override a repeated `<defName>`.** That method logs a red error and adds a random number to the name of the new def.
  - Ordinary XML defs go through `AddAllInMods`. There, a repeat inside ONE mod logs `has multiple … Skipping`, and the second def is skipped.
  - A repeat ACROSS mods logs NOTHING, and the later def wins. So never look in the log for cross-mod collisions.
  - Compare the actual `<defName>` of each new def with its filename before you stage the batch.
- ⚠️ **`AllLeafSubclasses()` means "nothing currently loaded subclasses this", not "concrete".** An abstract base class of ours with no loaded subclass counts as a leaf. `AlertsReadout` then tries to create the base class and throws. The UI of each map stays broken. Ship a sealed, always-inactive concrete subclass beside such a base.
- ⚠️ **A self-referencing `ResearchProjectDef` prerequisite causes infinite recursion in vanilla `ResearchManager.FinishProject`**, when that project is not yet finished at the call (a scenario, a dev button, a dependent project). The process dies at once, with no exception and no log line. An XML patch that removes the self-reference is not enough if a patch of the donor mod injects the self-reference again. The durable fix is a Harmony prefix on that method that strips the self-reference. Verify with a read of the live def after a fresh cold restart.

→ full paragraphs and the incidents behind every rule above: `references/load-order.md`.

### Teach the mod manager, or it will keep undoing you

If you fix a scattered order by hand, you treat the symptom. The mod manager sorts over your fix again. The durable fix is a rule in the user-rules database of the manager, and **`loadAfter` is the edge you want.**

- **→ `skills/rimworld-start-prep/SKILL.md` owns this**: `userRules.json`, `loadAfter` vs `loadBottom`, Refresh-reads/Save-writes, and why a rule keyed by `packageId` is orphaned by a rename.
- 🔴 You never block on the mod manager. `ModsConfig.xml`, load order and user rules are writable with the game up or down (owner, 2026-08-15). Only **assemblies** wait.
- 🔴 **`<loadAfter>` is an ordering hint and is INVISIBLE to dependency closure.** If a mod SUPPLIES a class or a texture that your mod references, put that mod in `<modDependencies>`. A tool that builds a reduced list walks `<modDependencies>`. Such a tool drops a mod that only `<loadAfter>` names. A missing comp type then discards the whole def that carries the comp, with no error that names the def.

→ mechanism and the incident behind this: `references/load-order.md`.

---

## 6. Deploying

Author in the project repo. Deploy a copy to the game. Never edit in place under `Mods/`. That copy is disposable, is not in version control, and the next deploy overwrites it.

**The full procedure is `skills/rimworld-deploy/SKILL.md`**:

- the plan-first `deploy_custom_mods.py` run, and how to read the plan before `--apply`;
- `-` lines and `--pull`;
- `DEPLOY_HOLD.txt`;
- the minimum viable mod folder;
- which game the deploy writes to (ArchBig is Steam's install; ArchSmall is a second install with its own `Mods` folder).

Enable a compatibility patch LAST in load order, after the mods that it patches. Then restart the game.

🔴 **Deployed is not live.** RimWorld reads defs **once, at launch**. So the start time of the process is the time of the def read. Any file under `Mods/` that is newer is not loaded.

- Before you call anything live, inspect the CONSUMER (the process that reads the file). Run the pre-flight check of the deployed copy against the mod list that the game will load with.
- **`references/deploying-and-liveness.md`** holds:
  - the mtime check;
  - the map-gen defs that need a NEW map;
  - the `MayRequire` gate that outlived its mod;
  - why the `0 errors` of `validate_patch.py` cannot prove independence from a mod that you are about to remove.

---

## 7. Debugging from Player.log

`%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`

Do not `grep` this log first. Run `python3 src/RimMandrake/Utils/harvest_log.py --log <path>`. Triage by **consequence, not by position in the file**. The ladder, worst first:

1. Static-constructor errors, `TypeInitializationException`, `ReflectionTypeLoadException`: the mod is *dead*, not noisy.
2. `Could not execute post-long-event action`: the error costs exactly that one action, and the queue continues. (The triage file names one rare exception.)
3. `Could not resolve cross-reference`: benign **or** fatal. The `wanter` field in the error decides.
4. `Patch operation … failed`: a no-op.
5. Translation and sound errors: cosmetic.

⚠️ **The op named in a patch error is the WRAPPER, not the failure.**

- `PatchOperationFindMod(Asimov) failed` was a broken *inner* `Replace`. Asimov was not missing. `FindMod` returns the inner result, while `ToString()` prints the outer operation. If a mod is truly absent and there is no `<nomatch>`, `FindMod` returns **true** and logs nothing at all. Read the inner operation.
- A field at its C# default (for example `isOrganic`) has no node for `Replace` to find. So `Conditional` is the safe default.

**`references/player-log-triage.md` has each rung in full: the greps, the IL-level evidence for what each error actually costs, the two shapes of cross-reference damage, and the judged-safe list you must keep.**

- Open that file whenever you read a log.
- Five "benign" cross-reference lines were the sole cause of a dead mod for three loads in a row.
- A `ReflectionTypeLoadException` is usually a load-order fault, not a broken assembly.

---

## 8. C# mods, briefly

Use C# only when tier (c) is truly required (§3). Then read `references/csharp-and-loading.md`. That file covers the Harmony patch types, the entry-point classes with their required constructor signatures, and `LoadFolders.xml`. Two constructor rules cause a large share of the "mod does nothing" reports:

- A `GameComponent` needs a **public constructor taking `(Game game)`**. Without that constructor, `Game.FillComponents` catches a `MissingMethodException`, logs one line (`Could not instantiate a GameComponent of type …`) and continues. The component never exists. The missing component is worse than a crash, because the feature appears to work and has no consequences.
- A `Mod` subclass needs `(ModContentPack content)`.

🔴 **Every mod we ship carries a real Mod Settings screen** (owner ruling, 2026-09-12, `MOD_OPTIONS_RETROFIT_1`). The rule applies to each future mod, not only to a retrofit pass. The screen has:

- an on/off switch for each major feature or mechanic;
- tuning where a number is the experience;
- defaults that equal the shipped behaviour;
- a game that still works when every switch is off;
- a label on each toggle that acts only on a newly generated map.

The switch for a mechanic is a plain on/off, default on, with no biome in it (owner's card of 2026-11-21; `design/RimMandrake/standing_rulings.md` §Every mod ships superb Mod Settings). The mechanic works by its physical conditions.

The code is the standard `Mod` + `ModSettings`:

- a settings class holds the fields;
- a `Mod` subclass exposes `DoSettingsWindowContents` and calls `settings.Write()`;
- each gated feature reads its own field, not a hardcoded constant.

⚠️ **`FilthMaker` refuses `Filth_AnimalFilth` on ALL natural terrain** (`placementMask [Terrain]` vs `filthAcceptanceMask [Unnatural]`, on each terrain that inherits `NaturalTerrainBase`). So the filth drop of a comp is a silent no-op outdoors. "the comp ticked with no filth appearing" is not evidence that the comp is broken. One exception: filth made with the flag `FilthSourceFlags.Pawn` is accepted under a roof or in a room.

⚠️ **A wrapper around a subprocess must capture and show BOTH streams on any failure.** A wrapper that reads only `stderr` on a nonzero exit can miss the real error, if the process writes the error to `stdout`. One C# wrapper around an external CLI gave an empty diagnostic on a real auth failure, because that failure went to stdout. Never assume the error channel.

**C# builds work from WSL; do not believe "this WSL machine cannot compile the .csproj".**

- Build with `python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>`. Any subagent brief that touches C# must state this command. The false "can't compile from WSL" claim ships C# that nobody built. That claim is the most common false claim of subagents.
- `winbuild.py` stages the mod on the Windows drive, builds with Windows dotnet, and copies the DLL and its `.srchash` back as a pair. Commit that pair together. The Windows `dotnet.exe` cannot build from a `\\wsl.localhost` path, so do not call `dotnet.exe` on a clone directly.
- There is no Visual Studio, NuGet CLI or .NET Framework targeting pack, and none is needed. The SDK is user-local at `C:\Users\Mandrake\.dotnet\dotnet.exe` (no admin, not on PATH). `C:\Program Files\dotnet` is runtime-only and does not build.
- `net472` targeting comes from the `Microsoft.NETFramework.ReferenceAssemblies` NuGet package.
- Reference the DLLs of the game in `RimWorldWin64_Data\Managed` with `<Private>false</Private>`, so that the build copies nothing into the mod folder.
- Copy `src/RimMandrake/RimDefDump/Source/RimDefDump.csproj` as the working reference.

---

## Handing over something you cannot check yourself

🔴 **First ask whether it needs the game at all.** The default is source: the def, the patch, the C#, the capture, `measure`, an `md5sum`. If you cannot say in one line what source cannot tell you, verify the thing yourself and close the item.

- A live check owes three lines: **the call**, **the expected reading**, and **how a pass could be false**.
- Name a positive observation, never "no error". An absence is the easiest thing to produce by accident.
- Whoever proves the item **closes** the item. Nobody hands the item back. Then that agent searches `infrastructure/state/items/` for what else the proof settled.
- **`references/validation-plan.md`** has the rule and the four false passes.

---

## 9. Keep this skill learning

- **The trap files are `references/traps-*.md`.** Open the one topic file that matches what you are about to do: patches, tooling, art, the mod stack, or diagnosis. Do not read all five. All five cost about 35k tokens.
- **If you are already running, do not reread — take the delta.** `python3 src/RimMandrake/Utils/whats_new.py --seat <SEAT>` prints what changed, in a few lines. Run this command when the game loads.
- **After any RimWorld task, ask: did anything here surprise me?** If yes, file a lesson: `python3 src/RimMandrake/Utils/lessons.py add "…" --home <the topic file>`. Keep the lesson short: what it looked like, what was actually true, what worked.
- ⚠️ **Reject most candidate lessons.** A lesson stays only if the lesson is specific, non-obvious, RimWorld-bound and still true. General software or process advice is not a trap.
- A lesson can change what *this file* says to do by default. Then that lesson belongs here, not in a trap file. Name this file as its `--home`.
- A fresh-context curation session moves the lessons into the skill. Do not edit a skill outside such a session (`skills/README.md`). An edit of `skills/rimworld-modding/` in this repo is the installed text.
- 🔴 **Never number an entry, and never cite one by number, line or heading.** Say "as per the trap file" and stop.

---

## Reference files

| File | Read it when |
|---|---|
| `references/traps.md` | **First.** Routes to the five topic files below and says what qualifies as an entry. Open the one you need, never all five. |
| ├ `traps-tooling.md` | **If you read only one, read this.** Nearly every entry is a tool that answered a different question than the one asked. |
| ├ `traps-xml-and-defs.md` | Before writing a patch — these cost a game load, not a rerun. |
| ├ `traps-mods-and-managers.md` | A mod is absent, dead, or ignoring its files. |
| ├ `traps-art.md` | Before calling art missing, wrong or broken. |
| └ `traps-diagnosis.md` | Before trusting a diagnosis, or calling into a running game. |
| `references/flight.md` | Giving a creature flight, or touching a flyer's def or flying art. |
| `references/project-engine-facts.md` | A comp on a plant, `MayRequire` on a patch, or a `.cs` in a hand-listed csproj. |
| `references/patch-operations.md` | An xpath won't match; you need the operation table, inheritance, worked examples, `LoadFolders.xml` (§9), the validator's blind spots (§10) or why an `<li>` destroys a def (§11). |
| `references/player-log-triage.md` | **Whenever you are reading a `Player.log`.** The five severity rungs in full, what each error actually costs, and the judged-safe list. |
| `references/deploying-and-liveness.md` | A deploy "did not take", or before calling any def live — inspecting the consumer, and the pre-flight against the mod list the game will actually load. |
| `references/load-order.md` | An inheritance error appeared, you are writing the order assertion, or you are about to touch a sorter's rules database. |
| `references/spending-a-load.md` | You are planning a load — what to verify offline, what may ride along in the batch, what to harvest. |
| `references/csharp-and-loading.md` | Before writing any C# — Harmony, entry points, `LoadFolders.xml`. |
| `references/minimal-load.md` | You have decided to cut the stack down to corner a bug. |
| `references/validation-plan.md` | You are writing the plan that ships with the work, or a check came back clean and you want to know how it could have lied. |
| `references/history.md` | You want an old figure, a date, or a line that this file no longer states. |
| `scripts/validate_patch.py` | Every patch **and every def**, before it goes near the Mods folder. Point it at the mod ROOT: it dispatches on the root element and its banner states what it did and did not scan. |

External, when the references above do not cover the question:
[RimWorld Modding Resources hub](https://spdskatr.github.io/RWModdingResources/) ·
[PatchOperations wiki](https://rimworldwiki.com/wiki/Modding_Tutorials/PatchOperations) ·
[Zhentar's xpath guide](https://gist.github.com/Zhentar/4a1b71cea45b9337f70b30a21d868782)

## animal_inventory.py drops defs that inherit <race>

- **`src/RimMandrake/Utils/animal_inventory.py` selects an animal by its OWN `<race>` element.** A ThingDef that inherits its whole `<race>` block from an abstract parent is dropped in silence.
- Two examples are RM_Drommath and RM_Ollareth: both read 'no def in the load set'.
- So any census built on animals.csv undercounts such animals. Select each animal by the name in the biome's roster (its `<wildAnimals>` list). Then read the RESOLVED race of that def (after inheritance).
