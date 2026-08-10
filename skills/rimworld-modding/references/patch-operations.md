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

Inheritance is resolved **before** patches run, so by patch time the child def
already carries the parent's fields — you can patch `Muffalo/race/baseBodySize`
even though the literal text of the Muffalo def never mentions it. Two corollaries:

- Patching the abstract parent hits every descendant at once, including ones
  from mods you didn't consider. Powerful and easy to overreach with.
- `Inherit="False"` on a child element blocks inheritance for that field only.

---

## 6. Operation-by-operation notes

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
