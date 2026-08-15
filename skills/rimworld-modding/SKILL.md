---
name: rimworld-modding
description: Author, patch, validate and debug RimWorld mods — XML PatchOperations, custom Defs, C#/Harmony assemblies, load-order problems, and Player.log triage. Use this whenever the user mentions RimWorld modding, a mod conflict, a Def, a patch, an xpath into Defs, ModsConfig/RimSort load order, a red error in the dev console, or asks to make/fix/analyse anything under a RimWorld Mods folder — even if they just paste a log excerpt and ask "what is this". Also use it before writing any file into a mod folder, because RimWorld's XML has several silent-failure modes that are easy to hit and hard to see.
---

# RimWorld modding

Patches fail *silently*, XML comments have a syntax rule most people don't know,
and a single bad Def entry can kill three unrelated mods at startup with an error
that names none of them. Almost every hour lost here is lost to writing something
plausible instead of reading something real.

The method: **find the ground truth on disk, write the smallest change that
survives a mod being absent, prove it before shipping, and record what you
learned.**

---

## 1. Read the real file first. Always.

Before writing a line of a patch, open the def you are patching and the def you
are patching *around* — the actual XML in the actual mod folder that is loaded
right now, not the wiki's version and not what a project doc said last month.

```bash
# where the defs live
RW="C:/Program Files (x86)/Steam/steamapps/common/RimWorld"
WS="C:/Program Files (x86)/Steam/steamapps/workshop/content/294100"

grep -rl 'defName>Armadillo<' "$RW/Data" "$WS" --include=*.xml
```

This costs thirty seconds. Three specific reasons it matters more here than
elsewhere:

- **A failed PatchOperation is a no-op, not an error you'll notice.** It prints
  one line into a log with thousands of lines. Nothing breaks. The patch just
  never happened. You will believe it worked.
- **Def names are redefined by other mods.** The `Armadillo` you're looking at
  in Core may not be the `Armadillo` that wins. Last loaded def with a given
  `defName` replaces earlier ones entirely.
- **Fields move between versions.** `<wildness>` was valid on `RaceProperties`
  and isn't in 1.6. Read `XML error: <field> doesn't correspond to any field in
  type X` as a **version-drift** report, not a typo: the mod predates the game,
  the value is dropped, the def loads anyway, and the instance count is the
  severity (eight of them = eight races quietly wrong). Wikis lag by a version.

When you find the ground truth, **quote its file path and the exact snippet in a
comment at the top of the patch**, with a date. Future-you re-reads that comment
instead of re-doing the search.

---

## 2. The game restart is the scarce resource

A cold load is **23–30 minutes** past ~500 mods — every mod's XML is parsed and
the texture atlases are rebuilt. **Arrive at the restart already confident.**

- **Verify everything verifiable offline first.** A restart confirms a
  prediction; it does not conduct an experiment.
- **Batch by ambiguity, not by count.** Anything whose effects are
  distinguishable rides along; a new C# assembly goes solo.
- **Harvest the whole log**, not just your change.
- **Never say "restart and see".** Propose a load when the queue justifies it,
  say what the batch contains, and name in advance the log strings that will
  decide each item.
- **Three failed hypotheses deep, stop bisecting and build a MINIMAL load** — the
  ~20 mods that can possibly be involved, one load, answering *does this work at
  all in isolation?*

`references/spending-a-load.md` (planning a load) and `references/minimal-load.md`
(deriving the reduced set) have these in full.

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

⚠️ **Prove a comp exists before scoping tier b around it:** `grep -rln
"CompProperties_<Name>" "$RW/Data"`. Zero hits means the mechanic is stat-driven
or hard-coded in the `thingClass` — there is no `CompProperties_ShieldBelt` in
1.6; `Apparel_ShieldBelt` is plain `Apparel` and the shield is entirely
`EnergyShieldEnergyMax` + `EnergyShieldRechargeRate`. Zero hits moves the job to
tier c, which rides a game load alone instead of batching.

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

Keep the test xpath and the inner xpath **identical** unless you have a stated
reason: differing ones test for one thing and modify another.

### The things that bite everyone

**Take a field's SHAPE from a shipped def, never from a spec or a sample** — a
spec names FIELDS, a def defines SHAPES. RimWorld has two child shapes and they
are not interchangeable: plain lists use `<li>`; dictionary-keyed fields use the
*def name as the element name* — `<wildBiomes><Desert>0.3</Desert>`,
`<statBases><MoveSpeed>4.6</MoveSpeed>`,
`<baseWeatherCommonalities><Clear>18</Clear>`,
`<xenotypeChances><BTD_Nikto MayRequire="btd.xenotyperemix.starwars">0.3</BTD_Nikto>`
— never `<li><xenotype>`. `MayRequire` rides the keyed element unchanged. Which
shape a field uses is a property of its C# type, so it is identical in every mod.

Getting this backwards is the most destructive mistake in this document: an `<li>`
in a dictionary-keyed field makes the engine **discard the entire parent def** — one
that was working before you touched it — and **no log line names the def.** The
tell is the quiet `Could not resolve cross-reference: No Verse.WeatherDef named
li found`, one per patched node, buried under ~950 downstream cross-reference
errors. `validate_patch.py` diffs a `<value>`'s children against the live node, so
it catches this in `Patches/` — it **cannot** catch it in a `Defs/` file you author
outright, which has no existing node to diff against. When a def vanishes
silently, diff it against a sibling in the same folder that survived. (Why:
`references/patch-operations.md`.)

**Match the def's XML ELEMENT NAME, not `ThingDef`.** The loader reads the element
name as the C# type, so `/Defs/ThingDef[…]` misses all 51 of VFE Pirates'
`<VFEPirates.WarcasketDef>` pieces — write `/Defs/VFEPirates.WarcasketDef[…]`.
Such a def still lives in `DefDatabase<ThingDef>` and dumps to `ThingDef.json`, so
**only the mod's XML tells you the element name; the def dump never will.**
`/Defs/*[defName="X"]` hits *every* class with that name — `ReduceWill` is both an
`InteractionDef` and a `PrisonerInteractionModeDef` — so use it only when the
class is what varies.

**Patches run BEFORE `ParentName` inheritance resolves**, so a patch sees raw XML:
`DA_Taraal`'s `<statBases>`, which it only inherits from `DA_BaseTaraal`, is
simply absent and an `Add` into it fails. Guard on the container, not the leaf — a
`Conditional` on `…/statBases` whose `<nomatch>` adds the whole element. And
because `Sequence` aborts at its first failure, every op after that one is
*untested*, not fine: in one 32-op block, positions 26–32 never ran and the log
said nothing about them.

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

**Migrate by NODE, never by string.** defNames are unique within a def *type*, not
across types: `OuterRim_Geonosian` is both a `XenotypeDef` and a `PawnKindDef`, and
a file-wide rename of the xenotype also rewrote three `pawnGroupMakers` entries —
an unresolvable `kind` there is **discarded at load with nothing in the log.** Name
the xpath or parent element you are changing, then count references before and
after: a xenotype swap touches one or two nodes, not eleven.

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
`references/patch-operations.md`.

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
It catches the silent failures, which otherwise cost a full game restart to find.

```bash
python3 scripts/validate_patch.py path/to/Patch.xml \
    --defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" \
    --defs "C:/Program Files (x86)/Steam/steamapps/workshop/content/294100"
```

The valuable check is the last one: it **runs each xpath against the real Defs on
disk and reports how many nodes it hits**. Zero hits means the patch would silently
do nothing; more hits than expected means a `Remove` is about to take out more than
you think. (Its other five checks are in `references/patch-operations.md`.)

A patch that validates clean can still be wrong about *intent*, so also confirm
in-game: load, then check the dev console (or `Player.log`) for the patch's own
name. Silence is success.

### Two things it cannot see

It reads defs **unpatched**, so a node another mod creates at runtime is invisible
and **0 matches can be the correct answer**; and it checks field names in no file,
so a hand-authored Def with a field that moved between versions sails straight
through. Both are in `references/patch-operations.md`, with the WeatherDef that
shipped a renamed field.

---

## 5b. Load order is a constraint you must ASSERT, not a preference

If your mod patches other mods' defs, it must load after every one of them.

**`ParentName` resolves only against `Abstract="True"` defs declared with a
`Name=` attribute — never against a `defName`.** Core's EMP damage def uses
`ParentName="StunBase"` (`<DamageDef Name="StunBase" Abstract="True">`), not
`ParentName="EMP"`; naming a concrete def gives `XML error: Could not find parent
node named "EMP"` and the def is **discarded** whole. So resolve every
outward-pointing name against the live load set before shipping a `Defs/` file:
`ParentName` against `Name=` attributes, and `Class=`/`workerClass`/`thingClass`/
`graphicClass` against loaded assemblies. `validate_patch.py` does both since
2026-08-13; it still checks no field names, types or value ranges.

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
🔴 **Do not block on it either. Owner's ruling, 2026-08-15:** *"You NEVER have to
ask if RimSort is open. It does not autosave, and I will never save without asking.
Nobody blocks on RimSort or game close for config files of any kind."* No mtime
check, no window, no question — `ModsConfig.xml`, load order and user rules are
writable game up or down. Only **assemblies** wait, and only because the OS locks
them while the game runs.

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

**Ask what the consumer last read, and when.** The process start time IS the
def-read time — RimWorld reads defs **once, at launch** — so anything under
`Mods/` newer than that StartTime is not loaded. **The three commands, and two
measured cases (a `GenStepDef` and a DLL) that both reported done and were both
false, are in `references/traps-mods-and-managers.md`.** Run them before calling
anything live.

⚠️ **Map-generation defs need MORE than a restart: they need a map generated after
it.** Loading a save re-runs no GenStep, so a correct fix is invisible on an old map.
The same holds one layer up: `xenotypeSet` is read at **pawn generation**, so a
patch landing after a world exists never fixes that world's colonists — and it
lives on the `PawnKindDef`, not on the `XenotypeDef` of the same name.

⚠️ **The bridge cannot answer this for you** — `jawa/get_def` returns the def that was
*loaded* and does not expose most fields, so a successful read is not proof the def is
current. **The mtime is the evidence.**

⭐ **Say which one you checked.** "Deployed" is a claim about disk; "live" is a claim
about a process. A report that does not distinguish them will be read as the stronger
of the two.

## 6c. Pre-flight: check the DEPLOYED copy against the LIVE mod list

Before a load you cannot repeat, run the check that neither the repo nor the
validator can do — **the game copy against the mod list it will actually load
with**. Both halves are needed; each hides a different failure.

1. **`deploy_custom_mods.py` with no `--apply`**, and read every mod's line. A def
   repointed in the repo and never deployed leaves the GAME holding the old
   reference. Six faction defs sat in exactly that state an hour before a launch.
2. **Resolve every `MayRequire` in the deployed defs against the live list.** 🔴 **A
   rename pass has to move the GATE as well as the name.** `<RimMandrakeGeonosianVariants
   MayRequire="btd.xenotyperemix.starwars">` names our def behind a mod that was
   just switched off, so the node is dropped at load and the faction's
   `xenotypeChances` is silently empty. The defName was right and the gate was a
   corpse. A dead gate on a mod that was NEVER active is fine — that is
   optional-compat working.
3. **Parse `activeMods`; never quote a number you read earlier.** With several
   seats sharing one install the count moved 582 → 580 → 578 → 576 inside an hour.
   `grep -c "<li>"` also over-counts by the 5 `knownExpansions`.

⚠️ **`validate_patch.py` resolves against the CURRENT load set, so `0 errors` cannot
prove independence from a mod you are about to REMOVE** — every stale reference
still resolves while the donor is installed. If you are retiring a mod, the check
is a separate pass that drops each departing packageId and asserts nothing points
there. Ours prints `references that die 0`.

## 7. Debugging from Player.log

`%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`

Triage by **consequence, not by position in the file**. The ladder, worst first:
static-constructor / `TypeInitializationException` / `ReflectionTypeLoadException`
(the mod is *dead*, not noisy) → `Could not execute post-long-event action` (costs
exactly that one action; the queue continues) → `Could not resolve cross-reference`
(benign **or** fatal — it depends entirely on the `wanter`) →
`Patch operation … failed` (a no-op) → translation and sound errors (cosmetic).

⚠️ **The op named in a patch error is the WRAPPER, not the failure.**
`PatchOperationFindMod(Asimov) failed` was a broken *inner* `Replace`, not a
missing Asimov: `FindMod` returns the inner result while `ToString()` prints the
outer, and a genuinely absent mod returns **true** and logs nothing at all. Read
the inner op — and note that a field sitting at its C# default (`isOrganic`) has
no node for `Replace` to find, which is why `Conditional` is the safe default.

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

🔴 **Name a positive observation, never "no error".** "No `Patch operation …
failed` line" is an absence, and §7 ranks absences last. Name the thing on
screen: the animal on the wildlife tab, `MoveSpeed` at 4.6 in the stat readout.

The seven-line handover shape (`ITEM`/`SEE`/`ROUTE`/`PREDICT`/`CLOSE`/`RIDE`/
`LIES`), a worked example, and the four false passes that have cost real cycles
here are in **`references/validation-plan.md`**. Read it when you are writing the
plan, and when a check came back clean and you want to know how it could have
lied to you.

---

## 9. Keep this skill learning

**The live log is `references/traps-*.md`.** Open the one topic file that matches
what you are about to do — patches, tooling, art, the mod stack, or diagnosis.
Reading all five is not the intent and costs ~25k tokens.

**If you are already running, do not reread — take the delta.** `python3
src/RimMandrake/Utils/whats_new.py --seat <SEAT>` prints what peers appended, in a
few lines instead of ~25k tokens. Run it when the game loads.

**After any RimWorld task, ask: did anything here surprise me?** If yes, append it
to the matching topic file, short: what it looked like, what was actually true,
what worked. ⚠️ **Most candidate lessons should be REJECTED** — it goes in only if
it is specific, non-obvious, RimWorld-bound and still true. General software or
process advice is not a trap. If it changes what *this file* says to do by
default, it belongs here instead, and does not get logged at all.

🔴 **Never number an entry, and never cite one by number, line or heading.** Say
"as per the trap file" and stop. Editing an installed skill changes nothing
durable: edit the copy in the user's project, re-package, and say it has been
**delivered** rather than saved.

---

## Reference files

| File | Read it when |
|---|---|
| `references/traps.md` | **First, and append last.** Routes to the five topic files below and says what qualifies as an entry. Open the one you need, never all five. |
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
| `references/validation-plan.md` | You are writing the plan that ships with the work, or a check came back clean and you want to know how it could have lied. |
| `scripts/validate_patch.py` | Every patch **and every def**, before it goes near the Mods folder. Point it at the mod ROOT: it dispatches on the root element and its banner states what it did and did not scan. |

External, when the references above don't cover it:
[RimWorld Modding Resources hub](https://spdskatr.github.io/RWModdingResources/) ·
[PatchOperations wiki](https://rimworldwiki.com/wiki/Modding_Tutorials/PatchOperations) ·
[Zhentar's xpath guide](https://gist.github.com/Zhentar/4a1b71cea45b9337f70b30a21d868782)
