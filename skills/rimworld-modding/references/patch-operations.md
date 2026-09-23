# PatchOperations and xpath — the deep end

Read this when an xpath won't match, when you need something beyond
conditional-wrapped Add/Remove/Replace, or when a patch applies to more or fewer
nodes than you intended.

**Contents**
1. How patching actually runs
2. The document you are querying
3. xpath idioms that matter
4. Multi-node matching and how to control it
5. Def inheritance (`ParentName`, `Abstract`)
6. Operation-by-operation notes
7. Worked examples
8. When *not* to patch

---

## 1. How patching actually runs

RimWorld loads every active mod's `Defs/` into one in-memory XML document, then
walks the active mods **in load order** and applies each mod's `Patches/*.xml`
against that document. Consequences worth internalising:

- **Patches see the result of earlier mods' patches.** Order is everything.
- **A patch cannot see a mod that loads after it.** This is why compatibility
  patch mods go last.
- **A failed operation is reported and skipped.** It does not abort the load, it
  does not abort the file, and it does not visibly break anything. It logs one
  line: `Patch operation Verse.PatchOperationX(...) failed`. In a stack with
  hundreds of mods this line is indistinguishable from ordinary noise, which is
  why conditional-wrapping matters — a conditional that finds nothing is a
  legitimate no-op, so it doesn't log at all, and the log stays meaningful.
- **Duplicate `defName` = last one wins, wholesale.** Not a merge. A mod that
  redefines `Armadillo` replaces Core's def entirely, including fields it never
  mentions.

---

## 2. The document you are querying

The root is `Defs`. Every def file's contents are merged under it, so a def that
lives in `Core/Defs/ThingDefs_Races/Races_Animal.xml` is reached as
`/Defs/ThingDef[defName="Armadillo"]`. **The file path is irrelevant to xpath.**
Only the element structure matters.

Element names are the C# field names, exactly. `race`, `wildBiomes`,
`statBases`, `comps`, `verbs`, `tools`. When you don't know the field name,
don't guess it — read the def, or decompile the class.

List entries are `<li>` elements, *except* where the field is a dictionary-like
`Dictionary<Def, float>`, in which case the key is the element name:

```xml
<race>
  <wildBiomes>
    <Desert>0.3</Desert>          <!-- element name IS the BiomeDef defName -->
    <AridShrubland>0.3</AridShrubland>
  </wildBiomes>
</race>

<statBases>
  <MoveSpeed>4.6</MoveSpeed>      <!-- same pattern: StatDef as element name -->
</statBases>

<tools>
  <li>                            <!-- plain list: <li> -->
    <label>teeth</label>
  </li>
</tools>
```

Getting this wrong in an *xpath* — `wildBiomes/li[...]` — matches nothing and
silently no-ops. Getting it wrong in a `<value>` is far worse: the engine reads
the element name as a def name, so `<li>` makes it search for a def called `li`,
which fails to resolve and **throws away the whole parent def**. You lose content
that was previously working, and the log blames the def that vanished rather than
the patch that removed it.

Which shape a field uses is decided by its C# type — `List<Foo>` versus a
`Dictionary`-style custom loader — so it is the same in every mod that touches
that field. Never infer it from the field's name or from another field nearby;
read the node you are about to write into. Known dictionary-keyed fields include
`wildAnimals`, `wildPlants`, `wildBiomes`, `statBases`, `baseWeatherCommonalities`
and `terrainsByFertility`, but treat that list as a reminder to check rather than
as the answer.

### 🔑 The one-line test, so you never have to trust a list

A `List<Foo>` is dictionary-keyed **exactly when `Foo` declares
`LoadDataFromXmlCustom` and that method reads the NODE NAME as a def reference.**
Open the record class and look:

```csharp
public class BiomeAnimalRecord            // and WeatherCommonalityRecord, identically
{
    public PawnKindDef animal;
    public float commonality;

    public void LoadDataFromXmlCustom(XmlNode xmlRoot)
    {
        DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef(this, "animal", xmlRoot);
        commonality = ParseHelper.FromString<float>(xmlRoot.FirstChild.Value);
    }
}
```

`xmlRoot` **is** the entry, so its NAME is the def and its TEXT is the number:
`<AA_Eyeling>1.2</AA_Eyeling>`. Write `<li><animal>…</animal></li>` instead and
`FirstChild.Value` reads an element rather than text, and the entry misparses.
No `LoadDataFromXmlCustom` → ordinary `<li>` list.

⚠️ **This is worth the thirty seconds because the plausible-sounding warning goes
the other way.** Two separate queue items in this project instructed BUILD to use
the `<li>` form for `wildAnimals` and for `baseWeatherCommonalities` — both
"generalising" from the real `biomeConfigs` / FactionDef trap, which is a
different field. Both would have shipped silently broken XML. **The record class
is the authority; another field's shape is not evidence.**

---

## 3. xpath idioms that matter

```
/Defs/ThingDef[defName="Muffalo"]                    exact def
/Defs/ThingDef[defName="Muffalo"]/statBases/MoveSpeed a field
/Defs/*[defName="Muffalo"]                            any def type with that name
//ThingDef[defName="Muffalo"]                         anywhere (slower, fine)

[defName="A" or defName="B"]                          several defs, one op
[starts-with(defName,"VWE_")]                         prefix families
[contains(defName,"Whip")]                            substring
[@Name="AnimalThingBase"]                             abstract parent by Name
[@Abstract="True"]                                    all abstract defs

/Defs/ThingDef[defName="X"]/race/wildBiomes/Desert[2] the SECOND match only
(/Defs/ThingDef[defName="X"]/comps/li)[1]             first of a node-set
[not(race/wildBiomes)]                                defs LACKING a node
[race/trainability="Advanced"]                        filter by child value
```

Predicates are 1-indexed. `[1]` is the first, not `[0]`.

Note the difference between `foo/bar[2]` and `(foo/bar)[2]`: the first means
"the second `bar` within each `foo`", the second means "the second node of the
whole result set". For the single-def patches you'll usually write they coincide,
but they diverge the moment the leading part of the path matches more than one
element.

**Attributes on values matter too.** `MayRequire` and `MayRequireAnyOf` appear as
attributes and can be selected or removed:

```
/Defs/ThingDef[defName="X"]/comps/li[@MayRequire="ludeon.rimworld.odyssey"]
```

---

## 4. Multi-node matching and how to control it

Most operations act on **every** node the xpath selects. This is a feature for
`Replace`/`AttributeSet` across a family of defs, and a hazard for `Remove`.

- Want all matches? Write the broad xpath and say so in a comment, with the
  count you expect.
- Want one specific match? Add a positional predicate, and **put the same
  predicate in the conditional test** so the operation disables itself the moment
  upstream fixes the duplication.
- Want to know how many you'll hit? Run `scripts/validate_patch.py`, which
  reports the live hit count per xpath against the Defs on disk. Guessing this
  number is how `Remove` ops go wrong.

---

## 5. Def inheritance

```xml
<ThingDef Name="AnimalThingBase" Abstract="True"> ... </ThingDef>
<ThingDef ParentName="AnimalThingBase">
  <defName>Muffalo</defName>
</ThingDef>
```

🔴 **Inheritance is resolved AFTER patches run.** Patches operate on the literal
XML as declared, so you cannot patch a field the child does not itself contain —
`Muffalo/race/baseBodySize` is only patchable if the Muffalo def literally writes
it. Aim at the parent, or at the concrete def where the field is declared.

🔴 **A child's `<li>` list is APPENDED to the parent's, not substituted for it.**
This is the trap that costs a game load, because nothing errors. A def declaring
one `<comps><li>` under a parent with three ends up with **four**. A `FactionDef`
declaring its own `pawnGroupMakers` under `OutlanderFactionBase` also inherits
that abstract's eight — and fields vanilla outlanders under your faction's name.

The opt-out is per-field, on the child's element:

```xml
<pawnGroupMakers Inherit="False">
```

Vanilla writes `Inherit="False"` **314 times**, 9 of them on `pawnGroupMakers`
alone. If you did not write it, you appended.

Three corollaries:

- **Changing a parent to gain fields also inherits its lists.** Re-parenting to
  pick up art or namers silently drags the parent's group makers, comps and
  filters along with them.
- Patching the abstract parent hits every descendant at once, including ones
  from mods you didn't consider. Powerful and easy to overreach with.
- Sometimes the append is what you want — inheriting a vanilla faction's twelve
  group makers and adding a thirteenth is a legitimate, cheap design. Decide
  which you want; do not discover it.

---

## 6. Operation-by-operation notes

### Quick reference — what each operation takes

| Class | Does | Needs |
|---|---|---|
| `PatchOperationAdd` | insert as **child** of target | `xpath`, `value`, opt. `order` |
| `PatchOperationInsert` | insert as **sibling** of target | `xpath`, `value`, opt. `order` |
| `PatchOperationReplace` | swap the node out | `xpath`, `value` |
| `PatchOperationRemove` | delete **all** matches | `xpath` |
| `PatchOperationAttributeAdd` / `Set` / `Remove` | attributes; `Add` won't overwrite | `xpath`, `attribute`, (`value`) |
| `PatchOperationSetName` | rename node, keep contents | `xpath`, `name` |
| `PatchOperationAddModExtension` | attach a DefModExtension | `xpath`, `value` |
| `PatchOperationSequence` | run ops in order, **stop at first failure** | `operations` |
| `PatchOperationConditional` | node exists? → `match` / `nomatch` | `xpath` |
| `PatchOperationFindMod` | mod installed? → `match` / `nomatch` | `mods` |

`PatchOperationTest` is obsolete; use `Conditional`.

**`PatchOperationAdd`** — appends as a *child* of the target. `<order>Prepend</order>`
puts it first instead. If the parent node doesn't exist yet, this fails; add the
parent in a preceding op, or use a `Sequence`.

**`PatchOperationInsert`** — inserts as a *sibling*, default before the target.
Use when position among siblings matters (e.g. ordering `<li>` entries in a
`comps` list where a comp reads state left by an earlier one).

**`PatchOperationReplace`** — the `<value>` replaces the whole selected node,
element name included, so the value must contain the element:
```xml
<value><MoveSpeed>5.2</MoveSpeed></value>
```
A common mistake is supplying only the inner text, which silently produces a
malformed def.

**`PatchOperationRemove`** — deletes every match. See §4.

**`PatchOperationAttributeAdd` / `Set` / `Remove`** — `Add` will not overwrite an
existing attribute; `Set` will. Removing a stale `MayRequire` is a legitimate and
underused way to fix an upstream guard that points at the wrong mod.

**`PatchOperationSetName`** — renames the element, keeps the contents. The tool
for dictionary-keyed fields: moving an animal from one biome to another is a
`SetName` on `wildBiomes/Desert` → `AridShrubland`, not a remove-plus-add.

**`PatchOperationAddModExtension`** — attaches a `DefModExtension`; creates the
`modExtensions` node if absent. `<value>` needs `Class="YourNamespace.YourExt"`.

**`PatchOperationSequence`** — runs `<operations>` in order and **stops at the
first failure**. Good: an atomic multi-step edit where later steps assume earlier
ones. Bad: a grab-bag of unrelated ops, where one early failure silently cancels
everything after it. Keep sequences short and related.

**`PatchOperationConditional`** — `<xpath>` is the test; `<match>` and/or
`<nomatch>` hold operations. This is the default wrapper for anything touching
another mod's content. Nest them when you need two conditions.

**`PatchOperationFindMod`** — tests *installed mods* by packageId or name:
```xml
<Operation Class="PatchOperationFindMod">
  <mods><li>Ludeon.RimWorld.Odyssey</li></mods>
  <match Class="PatchOperationRemove"> ... </match>
</Operation>
```
Prefer `Conditional` on the node itself when you can. `FindMod` tells you a mod
is present; `Conditional` tells you the thing you're about to edit is present,
which is the fact you actually depend on.

🔴 **Return semantics, and they read backwards from every instinct:**

| situation | returns | logs |
|---|---|---|
| none of `<mods>` active | **true** | **nothing** |
| a mod is active, `<match>` succeeds | true | nothing |
| a mod is active, `<match>` fails | **false** | `Patch operation Verse.PatchOperationFindMod(<Name>) failed` |

⇒ **A `FindMod` that FAILS is proof the mod is PRESENT and something inside its
`<match>` broke.** It can never mean the mod is missing. The error prints the
outer wrapper's `ToString()` while the return value came from an inner op, so the
name in the message is the guard, not the defect — read the inner operations.

⚠️ **`<mods>` matches the About.xml `<name>`, not the `packageId`** — and
`<activeMods>` in `ModsConfig.xml` lists `packageId`. Checking the wrong one is
how "that mod isn't installed" gets asserted about a mod that is.

**`PatchOperationTest`** — obsolete. Use `Conditional`.

---

## 7. Worked examples

**Remove a duplicate dictionary key, keeping the first**
```xml
<Operation Class="PatchOperationConditional">
  <xpath>/Defs/ThingDef[defName="Titan"]/race/wildBiomes/TropicalSwamp[2]</xpath>
  <match Class="PatchOperationRemove">
    <xpath>/Defs/ThingDef[defName="Titan"]/race/wildBiomes/TropicalSwamp[2]</xpath>
  </match>
</Operation>
```

**Rename a def's label across a family, only if the family exists**
```xml
<Operation Class="PatchOperationConditional">
  <xpath>/Defs/ThingDef[starts-with(defName,"BoT_")]</xpath>
  <match Class="PatchOperationReplace">
    <xpath>/Defs/ThingDef[defName="BoT_Sandcrawler"]/label</xpath>
    <value><label>sandcrawler</label></value>
  </match>
</Operation>
```

**Add a stat that may not be declared yet** — `Add` needs the parent, so create
it when missing:
```xml
<Operation Class="PatchOperationConditional">
  <xpath>/Defs/ThingDef[defName="X"]/statBases</xpath>
  <match Class="PatchOperationAdd">
    <xpath>/Defs/ThingDef[defName="X"]/statBases</xpath>
    <value><ComfyTemperatureMax>60</ComfyTemperatureMax></value>
  </match>
  <nomatch Class="PatchOperationAdd">
    <xpath>/Defs/ThingDef[defName="X"]</xpath>
    <value><statBases><ComfyTemperatureMax>60</ComfyTemperatureMax></statBases></value>
  </nomatch>
</Operation>
```

---

## 8. When *not* to patch

- **The mod ships a settings toggle for it.** Tier (a) beats tier (b). Check the
  mod's settings before writing XML.
- **You want the def gone entirely.** Cherry Picker-style removal tools handle
  that case more safely than deleting defs other content still cross-references.
  A `Remove` on a def that something else points at converts a tidy-up into a
  cross-reference error.
- **The behaviour lives in code.** No xpath reaches a compiled method. If the
  value you want isn't in XML, it's tier (c).
- **The fix belongs upstream.** Patch locally to unblock, then report it. A local
  patch that silently compensates for someone's bug is a maintenance liability
  that outlives your memory of why it exists — which is why every patch carries a
  dated source comment.

---

## 9. `LoadFolders.xml` — why a mod's def set depends on the whole mod list

The reason that trap is so common is that **a mod can ship different defs
depending on what else is loaded**, via `LoadFolders.xml`:

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

---

## 10. `validate_patch.py` — the full check list, and two things it cannot see

Read this before you trust — or disbelieve — a validator result.

It checks: the file parses; no comment contains `--`; every `Operation` has a
`Class`; ops are conditional-wrapped; the conditional test xpath matches the
inner op's xpath; and — this is the valuable one — it **runs each xpath against
the real Defs on disk and reports how many nodes it hits**. Zero hits means the
patch would silently do nothing. More hits than you expected means a
`Remove` is about to take out more than you think.

🔴 **Pass `--defs` at the Mods folder too, alongside Data and Workshop.**
First-party `mandrake.*` mods live in the game's own `Mods` folder, not in
Workshop content — omitting it makes a real, working cross-mod `ParentName`
inheritance report as "resolves to no def", a false failure that cost a full
validation cycle before it was caught:

```bash
--defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" \
--defs "C:/Program Files (x86)/Steam/steamapps/workshop/content/294100" \
--defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
```

### Two things it cannot see

**It reads the defs as they sit on disk, unpatched.** Other mods' patches have
not run. So a node that another mod *creates* at runtime is invisible, and the
validator calls your perfectly correct xpath a zero-match silent no-op. When you
are patching something a compat patch added, **0 matches is the expected
result** — and it also tells you the fix now depends on load order, because you
must apply after whoever creates the node.

### Bucket the warnings before you triage them — the total is not a backlog

A scoped sweep of `src/Jawa` returns `0 error(s), 1608 warning(s)`. That total sums
four categories that are not commensurable, and bucketing it takes one `grep -c` per
class:

| class | distinguishing phrase | verdict |
|---|---|---|
| the add-if-missing idiom | `inner xpath differs from the conditional test` | **structural** — how the pattern is spelled; the validator's own message calls it intentional |
| a node another mod creates at runtime | `matches 0 nodes` on a compat target | **structural** — a load-order statement, not an error |
| xpath matches more nodes than intended | `matches N nodes` | the only class that can be a defect |
| `iconPath` with no loose file | texture warning | **undecidable offline** — vanilla art is inside Unity bundles |

Of the 1,608, **1,536 were the first class** (1,206 from one file) and zero were
defects. Classes 1 and 2 recur at the same magnitude on every run, so a stable
four-digit total means the number is dominated by structure, not by your changes.
**Report the buckets with a verdict each, never the total** — and write down that the
structural classes were checked, or the next reader re-derives it from the same
warnings and reaches the same non-conclusion.

**It only validates `Patches/`. It does not check `Defs/` at all.** A hand-written
Def with a field that moved between versions sails straight through. That is
exactly how `<exposedThought>` shipped in one of our own WeatherDefs when 1.6 had
renamed it to `<weatherThought>`. Until the tool covers Defs, diff any Def you
author field-by-field against the closest Core def — SKILL.md §1, applied to your
own files.

---

## 11. Why an `<li>` in a dictionary-keyed field destroys the parent def

The rule is in `SKILL.md` §4 — match the shape of the children already in the
node. This is the failure mechanism and its log signature.

Getting this backwards is the most destructive mistake in the skill, because
it does not fail quietly. Add `<li>` into a dictionary-keyed field and the engine
looks for a def literally named `li`, fails to resolve it, and **discards the
entire parent def** — a def that was working fine before you touched it. The only
log evidence is one cross-reference error naming `"li"`, followed much later by
hundreds of unrelated-looking failures from everything that referenced the def
you just destroyed. `validate_patch.py` compares your `<value>` against the live
node's existing children for exactly this reason.

---

## 12. Full paragraphs behind `SKILL.md` §4's compressed rules

Each heading below matches one compressed rule in `SKILL.md` §4. The first line repeats the kept lead; the rest is what moved.

### Field shape: `<li>` vs keyed element — full paragraph

**Take a field's SHAPE from a shipped def, never from a spec or a sample** — a
spec names FIELDS, a def defines SHAPES. RimWorld has two child shapes and they
are not interchangeable: plain lists use `<li>`; dictionary-keyed fields use the
*def name as the element name* — `<wildBiomes><Desert>0.3</Desert>`,
`<statBases><MoveSpeed>4.6</MoveSpeed>`,
`<baseWeatherCommonalities><Clear>18</Clear>`,
`<xenotypeChances><BTD_Nikto MayRequire="btd.xenotyperemix.starwars">0.3</BTD_Nikto>`
— never `<li><xenotype>`. `MayRequire` rides the keyed element unchanged. Which
shape a field uses is a property of its C# type, so it is identical in every mod.

### Why `<li>` in a keyed field discards the parent def — mechanism and log signature

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

### `PatchOperationReplace` against your own mod's def wins silently

**A `PatchOperationReplace` against a def YOUR OWN MOD declares wins silently —
patches run after every def loads, same mod or not.** A generator-written
compat/flora patch overwrote 21 of our own BiomeDefs' `wildPlants` for weeks
because it ran later in load order than the hand-authored defs it was
replacing; the biome shipped 4 stale donor plant names over 9 authored ones and
generated 0 plants on a live map. Nothing in the normal workflow looks for "a
generator patches a def we author" — check for that explicitly whenever a
generated `Patches/` file and a hand-authored `Defs/` file touch the same
defName.

### Match the def's XML element name, not `ThingDef`

**Match the def's XML ELEMENT NAME, not `ThingDef`.** The loader reads the element
name as the C# type, so `/Defs/ThingDef[…]` misses all 51 of VFE Pirates'
`<VFEPirates.WarcasketDef>` pieces — write `/Defs/VFEPirates.WarcasketDef[…]`.
Such a def still lives in `DefDatabase<ThingDef>` and dumps to `ThingDef.json`, so
**only the mod's XML tells you the element name; the def dump never will.**
`/Defs/*[defName="X"]` hits *every* class with that name — `ReduceWill` is both an
`InteractionDef` and a `PrisonerInteractionModeDef` — so use it only when the
class is what varies.

### Patches run before `ParentName` inheritance resolves

**Patches run BEFORE `ParentName` inheritance resolves**, so a patch sees raw XML:
`DA_Taraal`'s `<statBases>`, which it only inherits from `DA_BaseTaraal`, is
simply absent and an `Add` into it fails. Guard on the container, not the leaf — a
`Conditional` on `…/statBases` whose `<nomatch>` adds the whole element. And
because `Sequence` aborts at its first failure, every op after that one is
*untested*, not fine: in one 32-op block, positions 26–32 never ran and the log
said nothing about them.

### `PatchOperationRemove` deletes every match, not the first one

**`PatchOperationRemove` deletes every match, not the first one.** There is no
"remove one". If a def lists `<TropicalSwamp>` twice and you write the bare
xpath, both disappear and the animal stops spawning there entirely. Use a
positional predicate — `.../TropicalSwamp[2]` — and put the same predicate in the
conditional test so the op self-disables once upstream fixes their file.

### `MayRequire` and `PatchOperationFindMod` check the mod, not the def

**`MayRequire` and `PatchOperationFindMod` check the mod, not the def.**
`MayRequire="VanillaExpanded.VWE"` passes as long as VWE is installed — even if
VWE deleted the def you reference in its latest version. That is a live upstream
bug class, not a hypothetical; it is why unresolved cross-references show up in
stacks where every named mod is present. When you *depend* on a def existing,
guard with `PatchOperationConditional` on the def itself, which tests reality
rather than intent.

### `MayRequire` on a bare `<Operation>` does nothing

🔴 **`MayRequire` on a bare `<Operation>` element inside a Patch file does
NOTHING — MEASURED against `LoadedModManager.ApplyPatches()`/`PatchOperation`
source.** Every operation runs unconditionally; `PatchOperation` itself has no
field for it, and the `MayRequire` check only applies to top-level DEF nodes in
the unified XML. Shipping an incident/comp-injection "gated" this way discards
the target's WHOLE def file when the referenced type is absent (a dangling
PawnKindDef this way once NRE'd a downstream mod's own loader and tripped
RimWorld's corrupted-mods reset). **The only real gate on an `<Operation>` is
`PatchOperationFindMod`.** Sweep any bare `MayRequire` on an `<Operation>` you
find; it is silently unguarded (`MAYREQUIRE_OPERATION_INERT_SWEEP_1`).

### `MayRequire` on the def's owning mod is not proof the def loads

🔴 **`MayRequire` on the def's OWNING mod is not proof the def loads.**
`LoadFolders.xml <li IfModActive="...">` can ship a def only when a THIRD mod is
active — invisible to dump `packageId` attribution, since the dump just says
which mod owns it, not which condition gated its folder. A biome `wildAnimals`
reference to such a def null-crashes `CommonalityOfAnimal` the moment the
gating mod is absent even though the owning mod is present. Fix: chain the
gating mod's packageId into your own `MayRequire` too, not just the owning
mod's (`GIDDYUP_NULLKEY_CRASH_1`).

### SKILL.md §4 — the default conditional-wrapped patch shape

```xml
<Operation Class="PatchOperationConditional">
  <xpath>/Defs/ThingDef[defName="Armadillo"]/race/wildBiomes/Desert</xpath>
  <match Class="PatchOperationRemove">
    <xpath>/Defs/ThingDef[defName="Armadillo"]/race/wildBiomes/Desert</xpath>
  </match>
</Operation>
```

### SKILL.md §4 — why the def-set trap is so common (full paragraph)

The reason this is so common is that **a mod can ship different defs depending on
what else is loaded**, via `LoadFolders.xml` — so the def set is a function of the
whole mod list, and "the mod is installed" tells you nothing about which of its
defs exist. **When a reference goes missing while its owning mod is plainly
present, read that mod's `LoadFolders.xml` before concluding anything**; the
syntax and the real Vanilla-Animals-Expanded/Odyssey case are in
`references/patch-operations.md`.
