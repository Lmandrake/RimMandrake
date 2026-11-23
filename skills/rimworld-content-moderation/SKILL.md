---
name: rimworld-content-moderation
description: Deciding what content stays in a RimWorld campaign out of a large mod stack — building contact sheets of real sprites straight from the defs so a keep/cut call is made by looking, cutting with Cherry Picker rather than uninstalling, and the traps that make a cut do nothing or break a pawn. Includes the one nothing warns you about: cutting the last weapon carrying a tag silently disarms every pawn kind whose tags ALL went to zero, so after any cut rebuild the tag -> surviving-item index from the def dump — post-inheritance, post-patch, post-dedup — and only fall back to scanning raw mod XML when no dump matches the current mod list. Use when curating, trimming or cherrypicking items, weapons, apparel, creatures or any graphical asset; when someone asks "which of these do we keep"; after any cut, to find the kinds left with nothing to hold; and before proposing that a mod be removed.
---

# RimWorld content moderation

This skill cuts a large mod stack down to one campaign's worth of content. The job is mostly **deciding**. The decisions
are mostly **visual**. So most of the work is to put the right thing in front of the agent or person who decides.

The evidence, the dates and the old text that was wrong are in `references/history.md`.

## 🔴 First: does a human belong in this review at all? (owner's ruling, 2026-09-01)

"Don't use humans where a screenshot will do." The ladder in `infrastructure/VALIDATION_LADDER.md` binds every review:

- **Machine checks come first:** art presence, def resolution, log errors. A human never hunts magenta (the colour of
  missing art).
- **Opus evaluation** comes next. Opus judges art quality and theme, beyond the grade of the model that built the work.
- **The owner comes last, and ONLY for** gameplay, fun, overall thematic coherence and UI.

If an agent can review a thing, the agent reviews it. A cut decision is the owner's, or the Conductor's as a recorded
act (`design/RimMandrake/delegation_policy.md` §2). No helper makes a cut decision.

**When the owner reviews OUR OWN builds, stage a REVIEW ENVIRONMENT, not a grid.** A review environment is related
content, composed in context on a throwaway map. Examples:

- the animals inside a mock-up of their biome, as a whole ecosystem;
- two dwellings in two faction styles, with the resident race and its equipment;
- beside these, the biome's tile augmentor. "Tile augmentor" is the owner's word for a tile mutator, a world-tile feature
  that changes map generation.

Grids are acceptable, but a grid does not show the interactions that need study. Contact sheets (next section) stay the
right tool for mass keep/cut over EXISTING mod-stack content, where volume rules.

## Build a contact sheet. Do not send a list of defNames.

A contact sheet is a page of many sprites, one sprite in each cell. A spreadsheet answers every question about an item
except the first one: *what does it look like?* Nobody can keep or cut 1,243 animals from names. Each lookup costs a wiki
tab.

**Render the actual sprites, straight from the defs, paginated, grouped by mod.** 1,243 animals took **6.7 seconds**
and produced six PNGs. The cost is small. So never ask anyone to judge from a list.

### Two artifacts, always

| output | why |
|---|---|
| the **sheets** | the reviewer decides on them |
| an **index CSV**, with one row for each placed cell → `defName, mod, texPath, file` | **a picture you cannot act on is decoration.** "Cell 3,7 looks wrong" has to become a defName you can cut |

The run also writes a third output, the **missing-texture CSV**. That CSV is a deliverable too. The CSV lists the things
that have no picture offline. Judge those things in game.

### Row order is the design

Order the rows by **mod**. Then one glance shows the whole contribution of a mod: "this is what Alpha Animals adds, this
is what Beasts of the Rim adds". Without that order, the reviewer needs sixty lookups. Everything else about the layout
is taste. The row order is not.

## Where the sprite actually lives — this is the whole trick

The place of the texture differs by def type. If you read the wrong place, the sheet is empty.

| content | path to the texture |
|---|---|
| **weapons, apparel, buildings, items** | `ThingDef.graphicData.texPath`. The path is **directly on the def.** |
| **animals and pawns** | 🔴 **NOT on the ThingDef.** `graphicData` is null for every animal. Hop `ThingDef` → its `PawnKindDef` → `lifeStages[LAST].bodyGraphicData.texPath` |

⇒ **A weapon or apparel sheet is strictly simpler to build than the animal one.** The weapon sheet removes a hop. Both
sheet tools exist already (see "The tools here").

### Five mechanics that decide whether it works

- **`texPath` has no extension and no side.** `Things/Pawn/Animal/Bear/Bear` may be `Bear_south.png`, `Bear_east.png`,
  or a bare `Bear.png`. Resolve the path. Do not concatenate.
- **Index the textures of each mod from its LOADED content dirs *and* its root.** A mod with `LoadFolders.xml` keeps its
  art under `1.6/Textures/`. If you index only `<mod>/Textures/`, you find nothing and the mod silently renders blank.
- **PatchOperations have not run.** The sheet tools read base XML. If a mod changes a `texPath` by a patch, the change is
  invisible. The sheet then shows the donor's art (the mod that first made the def), not the patched result.
- **Do NOT deduplicate defNames.** A doubled cell means that two mods ship the same thing. Such a cell is a finding. Doubled
  cells showed that *zebra*, *black bear* and *mandrill* shipped twice. If you cut one copy, the other copy stays on
  the map.
- **Vanilla and DLC art is not in loose PNGs.** Vanilla and DLC art is in Unity AssetBundles and `resources.assets`. The sheet tools read
  it from a cache that `src/RimMandrake/Utils/extract_bundle_textures.py` makes. Git ignores the cache, so a fresh clone
  has none. Without the cache, around 40% of animals come out blank, and that is CORRECT. Blank ≠ broken. The details are
  in `skills/reading-rimworld-graphics/SKILL.md`.

## Cut with Cherry Picker, not by uninstalling

Cherry Picker is a mod. Cherry Picker applies a kill list (a config file of `DefType/defName` keys) each time the game loads. To
reverse a cut, edit one line. **An edit of the file does nothing until the next game start.** So no edit needs the game
down, and a decisive cut costs nothing.

- The campaign's kill list is the SHIP profile. `src/RimMandrake/Utils/cherrypicker_swap.py` swaps SHIP and an empty
  REVIEW profile. Use REVIEW to test with no cuts.
- `src/RimMandrake/Utils/cherrypick_build.py` validates a key list offline. Cherry Picker skips most bad keys with no
  message, and one key with no `/` loses every removal in the list.

Removing a *mod* is a different act with a different risk. A mod removal needs a `ModsConfig` change and a game-down window. If
anything referenced the mod, the load logs `Could not resolve cross-reference`. Check the dependencies first. Usually
nothing declares one.

### 🪤 Do not validate Cherry Picker entries against a def dump

🔴 **What "removed" means depends on the def type.** Cherry Picker runs at game startup, after the XML and
the patches are loaded. The dump is captured after Cherry Picker. The proof is in the code of `CherryPicker.dll` and in one load's `Player.log` (2026-11-23).

| def type | what Cherry Picker does | what the dump shows |
|---|---|---|
| `ThingDef`, `PawnKindDef`, `BiomeDef`, `IncidentDef`, `HediffDef`, `FactionDef`, `AbilityDef` and most others | the def stays in the game. Cherry Picker clears or zeroes fields on it (`weaponTags`, `apparel.tags`, `tradeability`, biome commonality, `BiomeDef.implemented`) | a cut that worked is **PRESENT** |
| `GeneDef`, `XenotypeDef`, `BackstoryDef`, `ResearchProjectDef`, `RecipeDef`, `TraitDef`, `HairDef`, `BeardDef`, `TattooDef`, `MemeDef`, `PreceptDef`, `RitualPatternDef`, `DesignationCategoryDef` | the def is deleted | a cut that worked is **ABSENT**, and so is a typo. PRESENT means that the cut did not work, or that the dump comes from a load without the key |

- ⇒ For a type of the first row, the presence of a def in the dump is not evidence about a cut, in either
  direction. The def is present if the cut worked, and if the cut did not work. Only the changed fields are evidence.
- The second row is the list of vanilla types. Cherry Picker also deletes two modded types, `PowerDef` and
  `PsycasterPathDef`.
- 🔑 **An unfiltered census, count or contact sheet silently includes cut content.** From mod XML, that is every cut. From
  the dump, that is every cut of the first row. The
  owner once reviewed an animal sheet that still showed 1,162 of his cuts.
- **Filter any roster against the kill list before you show it to anyone.** `src/RimMandrake/Utils/cherrypicker.py` is the
  one reader of the kill list. Both sheet tools filter through it by default. Print `provenance()`, the line that says
  how many rows you suppressed.
- ✅ **The instrument that CAN answer "did this cut take effect" is `Player.log`.** The log holds
  `[Cherry Picker] The database was processed in … the following defs were removed:`. One `- <DefType>/<defName>,` line
  for each def follows. `cherrypicker.from_log()` reads the lines. A key that
  Cherry Picker skipped has no line.
- 🪤 A cut that failed reads `- FAILED: <key>`, and the header then also holds an error count. `from_log()` stops at the
  first FAILED line and drops the lines after it. `from_log()` also does not read the second block, `These dynamically generated
  defs were also processed`. Grep the log for both.
- A check of a key against a dump is most useful for **newly added** keys. Before the next load, the check confirms the
  spelling. If the key resolves in the dump, the name is spelled right. The dump must match the mod list.
- An old key of the first row that does not resolve is a typo, or its mod is absent. For an old key of the second
  row, the check can never tell you. There, a typo and a successful cut look identical.

The measurement, and the two older explanations that were wrong, are in
`infrastructure/state/facts/dump-is-pre-cherrypicker.md`. The name of that file holds the second wrong one.

## How to run a session

- **Items are the unit. Mods are a consequence.** Never open with "shall we cut this mod". People keep a mod that they
  find silly, to get gear that they want. Renaming is cheap. Cut items. Then ask whether a hollowed-out mod still
  earns its slot.
- **Attribute every row to its mod.** The reviewer needs the mod to look things up. The mod also shows when one name
  belongs to two different mods.
- **Describe a mod from its `About.xml` `<description>`, never from its packageId or name.** A mod inventory once
  described Utility Columns from its packageId (`nephlite.orbitaltradecolumn`) and called it a trade-column mod. Utility
  Columns is a structural-columns building mod. The identity string is not the pitch.
- **Lead with the principle, not the list.** If the reviewer agrees that "real-world firearms are out", one ruling
  disposes of 74 items. The adjudication of 74 rows does not.
- **State the batch size and let the reviewer retune it.** Ask directly whether the reviewer wants bigger or smaller
  rounds.
- **Keep anything with an interesting silhouette or a mechanical hook**, even if the name is wrong. A rename is one
  patch. Cut what is *recognisable from Earth*: a penguin is a penguin under any label.
- **Sort by look and genre fit, not by stats or spawn rate.** Balance and biome assignment are a later pass. That pass
  will be redone anyway. Do not let balance or biome assignment drive a keep/cut call.
- **Anything you are unsure of goes on a hold list**, not into a guess.

## After cutting creatures, sweep the products they made

A cut animal leaves its meat, leather, wool, milk and eggs behind as items with no source in the world. These items
still fill menus, stockpile filters and trade lists. One pass after 168 creature cuts found **271** such orphans.

1. Build a `{product -> set of producing animals}` map. Read `race/meatDef`, `race/leatherDef`, `race/woolDef`,
   `race/milkDef` and the comps (`eggFertilizedDef`, `eggUnfertilizedDef`, `milkDef`, `woolDef`, `resourceDef`).
2. Cut a product only when **every** producer is cut.

🔴 **Three guards. Each guard caught a real false positive:**

- **A plant may make the product.** `DevilstrandCloth` looks orphaned when the devil sheep goes. In fact it is harvested
  from the devilstrand *plant*. Check every `plant/harvestedThingDef` before you cut anything.
- **A recipe may make the product.** Scan `RecipeDef.products` too.
- **The link may be name-only.** `AA_FlamingoPhoenix` has no EggLayer comp at all. Nothing but the shared stem ties it to
  its egg. A name-stem pass catches these. Three conditions apply, or the pass will cut live content:
  - require the stem to be long;
  - strip the mod prefix;
  - confirm that no *surviving* animal shares the stem.

## Before deprecating a mod, audit what else it ships

An empty item list is not an empty mod, and "all its animals are cut" answers only one question. Do the checks below,
in this order. The checks take a couple of minutes. The checks are the difference between a clean removal and a broken
load.

1. **Every def type the mod defines**, not just the one that you reviewed. A creature mod that also ships items,
   buildings, sounds, bodies or damage types does work that you did not audit.
2. **The mod's patch xpaths.** This is the real test. Removal is contained if every xpath names the mod's own prefix.
   Removal is also contained if the xpaths only add the mod's own defs to a shared list. If an xpath reaches into Core or another mod's def, removal reverts a
   functional change.
3. **Whether an assembly loads for the CURRENT game version.** DLLs under old version folders do not load and do not
   matter.
4. **Hard `modDependencies` from other mods.** A `modDependencies` entry is distinct from `loadAfter`, which is harmless. Grep inside the
   `<modDependencies>` block only.

🪤 **An unprefixed defName is the thing to chase.** `WoolCamel` in an animal mod looked like it might make Core's camel
shearable, a real functional change to vanilla. `WoolCamel` belonged to the mod's own camel. Verify. Do not assume either way.

🔴 **A one-hop reference census is not enough — walk donor-of-donor chains too.** One retirement census checked only
direct references to the retired mod. A THIRD mod gated its own content on the presence of the retired mod. Our code consumed
that gated content ungated. The cold load found 4 new cross-reference errors. A direct-reference grep could
never see them.

⚠️ **A dead donor reference does not mean the content is gone.** First check whether we already absorbed the content under
our own prefix. One pass found that 21 "missing" droids were already ours.

⚠️ **A `RSW_<donorName>`-prefix test cannot find a ported species, because the port RENAMES it.** A count by prefix
gave three wrong counts of the same wave in one sitting (105 → 11 → 2 actually owed). The donor→ours mapping is in
`<!-- X -> RSW_Y -->` header comments at the top of the port's own def files. Read those. Never count by prefix.

## 🔴 Biome-cast and ecosystem patches cannot ride a reduced mod list

Self-contained content (a weapon, a creature, a building, a weather event) degrades gracefully on a trimmed mod list. A
preview on a minimal list genuinely previews it. **A biome cast, fauna cast or animal-tolerance patch does not degrade.**
Such a patch wires cross-references into the live set of donor mods. One missing donor then makes a dead map:

- **`BiomeDef.CommonalityOfAnimal` builds its cache with `cachedAnimalCommonalities.Add(wildAnimals[i].animal, ...)`, and
  that line has no null check.** A SINGLE unresolved cross-ref anywhere in a biome's `wildAnimals` list is enough. One null
  throws `ArgumentNullException` the first time anything asks that biome for a commonality. Every mapgen path that touches the
  biome breaks (`BIOME_CAST_REFS_BREAK_MAPGEN_1`, "Biome-cast cross-refs to donor creatures break local mapgen when donor
  is absent").
- **`BiomeDef.ConfigErrors()` throws NRE (a null reference exception) when one list holds two or more unresolved
  `BiomeAnimalRecord` entries.** That check runs in dev mode only. The check reads the animal lists, not `BiomePlantRecord`.
- The plant cache skips an unresolved plant.
- Measured on a reduced list: 399 cross-ref failures, and mapgen died.

⇒ One unconditional `Replace` that mixes many donor mods is a live grenade against any future donor retirement. **Gate
each donor's entries behind their own `MayRequire`.** Then the retirement of one donor cannot orphan another donor's
entries in the same list.

⇒ **FORWARD RISK before you retire any donor mod** (Biomes!, Alpha Animals, GeneticRim, …): FIRST scrub the biome-cast refs
to its creatures. Otherwise local mapgen breaks. Local mapgen makes settlement and quicktest maps, and it runs even under
a frozen world. "All its animals are cut" is not the same audit as "nothing still cross-references it from a
biome cast".

⚠️ **"An animal left this biome" does not imply "this biome now lacks that KIND of animal."** A gap was nearly filed and
built on that inference. The roster still held other animals of the same kind at 6-8x the departed animal's commonality.
Read the REMAINING rows of a fauna roster before you file a gap, not just the row that changed.

🔴 **The removal of an animal's def from the load is not complete until you sweep its `wildAnimals` cross-refs.** Removal
means that the def is deleted from XML, patched out, or its mod leaves the list.

- **A Cherry Picker cut is not such a removal.** The `PawnKindDef` stays, so the entry still resolves. Cherry Picker sets
  the entry's commonality to 0 in `wildAnimals` and `pollutionWildAnimals`. Cherry Picker does not touch
  `coastalWildAnimals`, so a cut animal keeps its weight there. Sweep that list after an animal cut.
- **Unsafe:** a bare dictionary entry, `<CreatureName>value</CreatureName>`, that names the removed def. It throws the same
  `ArgumentNullException` on the next mapgen. The `<li>` form is also wrong: RimWorld discards the whole BiomeDef.
- **Safe:** a `race/wildBiomes` eviction xpath that names the same defName inside a `[defName="..."]` predicate. The safe
  form is easy to confuse with the unsafe form. `PatchOperationRemove` on a missing ThingDef just matches nothing.
- After a removal, grep every biome and ecosystem file for the removed defName, not just the file that you edited. The fault was
  "fixed" more than once, because the sweep missed dangling refs across multiple files.

## Traps that make a cut do nothing, or break the game

- 🔴 **A cut weapon can empty a `weaponTag`. A pawn kind whose only tag resolves to nothing spawns UNARMED, silently.** After
  any weapon cut, diff the tags that you removed against the tags that survive. Then check which `PawnKindDef`s request
  the empty ones (the last section says how).
- 🔴 **A defName can exist as two different def types.** `OuterRim_Geonosian` is both a `XenotypeDef` and a
  `PawnKindDef`. Migrate by node, never by string.
- 🔴 **A mod can inject defs attributed to Core.** 1,073 `HL_` humanlike-animal twins reported as `ludeon.rimworld`. The
  twins were invisible in every per-mod count until someone asked which mod owned a specific row.
- 🔴 **A `FactionDef` cut leaves the faction loaded, and it does nothing to an existing world.** Cherry Picker sets
  `maxConfigurableAtWorldCreation` to -1 and zeroes `startingCountAtWorldCreation` and `requiredCountAtGameStart`.
  - All three are world-creation fields. A faction that is already in the saved world stays.
  - Cherry Picker silently skips a `FactionDef` whose `maxConfigurableAtWorldCreation` is not above 0.
  - `BS_Muspelheim` and `BS_OgreFaction` were listed as `FactionDef/...` cuts, and both still loaded as real
    `FactionDef`s. The same batch's `PawnKindDef`/`XenotypeDef`/`GeneDef`/`AbilityDef` entries read as
    successfully removed.
  - So never rely on a Cherry Picker `FactionDef` cut alone. Read the three fields in a live DefDump, or pair the cut
    with an explicit suppression patch. Such a patch zeroes `startingCountAtWorldCreation`, for example. The patch matters
    most where Cherry Picker skips the def. Our patch is
    `src/RimUtinni/UtinniPatches/Patches/FactionSlate/OnlyOurFactions.xml`.
- **Never infer a def's owning mod from its defName prefix.** Bare, unprefixed names (`Bantha`, `Rat`) ship from mods
  whose prefix appears nowhere in the defName. Read `MayRequire` or the mod's own `About.xml`, not the string.
- **Some mods generate a twin of every def in a class.** If a census returns suspiciously round doubles, look for a
  generator before you cut anything.
- **Mod XML on disk is not the running game.** Some mods change defs at load, dedup passes especially. So a claim from
  disk about what EXISTS is unsafe. The def dump is captured inside the game, after patches and startup code, on one
  mod list and one date.
- 🪤 **Abstract parent defs have no `defName`** and are not content. Abstract parents inflate every count. Abstract parents cannot be cut, because
  Cherry Picker keys on `defName`. One animal census carried **50** of them. Two wore inherited labels that read as real
  creatures. Filter abstract parents out before you present anything to a reviewer.
- **Only the next load proves a cut.** After a large batch, census `Player.log` for `Could not resolve cross-reference`
  and group by the missing defName. 1,308 cuts and three mod removals produced **25 errors across 2 defs**. The log showed
  which one was ours and which one was pre-existing. A guess from the diff cannot show that.

## The tools here

```
src/RimMandrake/Utils/def_inventory.py        load-set resolution, ParentName merging
src/RimMandrake/Utils/animal_inventory.py     -> animals.csv and five more
src/RimMandrake/Utils/animal_contact_sheet.py -> paginated PNGs + index CSV
src/RimMandrake/Utils/thing_contact_sheet.py  the same for weapons, apparel, buildings, items, plants
src/RimMandrake/Utils/cherrypicker.py         the one reader of the kill list
src/RimMandrake/Utils/weapon_tag_audit.py     the pawn kinds with no surviving weapon tag
src/RimMandrake/Utils/apparel_tag_audit.py    the same for apparel
```

The contact sheet is a thin projection over the inventory. The contact sheet owns no load-set resolution and no XML parsing. Build any
new sheet the same way: project over `def_inventory.py`, and do not re-solve inheritance.

⚠️ **Pillow can be absent from a WSL `python3`** (PEP 668 blocks `pip install`). Windows `python.exe` has it. Relative
paths work from the repo root:

```
python.exe src/RimMandrake/Utils/animal_contact_sheet.py --csv <csv> --out <dir>
```

---

## 🔴 A cut item can disarm a pawn kind that never named it, and nothing logs

This failure survives every check that a cut list can run on itself.

A `PawnKindDef` asks for weapons by **tag**, not by defName, for example `weaponTags: NeolithicMeleeDecent`. Cut the last
surviving weapon with that tag, and the tag resolves to an empty set. **A pawn kind whose weapon tags are all empty spawns
bare-handed.** There is no red error, no cross-reference warning and nothing in `Player.log`. The kind is valid, the tag is
valid, and the set is just empty.

Measured in this repo: vanilla `MeleeWeapon_Ikwa` was the only Core weapon with `NeolithicMeleeDecent`. The one other def
in the entire workshop with that tag belonged to an inactive mod. The cut of the ikwa silently disarmed **every pawn kind
that inherits `TribalWarriorBase`**: vanilla tribal warriors, and an authored faction's signature raid. Nobody noticed for
four days. The ikwa is now un-cut (`OWNER_EXCLUDE` in `cherrypick_build.py`).

A kind whose apparel tags all go empty gets nothing from the general apparel pool. `PawnApparelGenerator.CanUsePair`
rejects each item that matches none of the kind's tags. Only required apparel and the free warmth, toxic and vacuum
items stay.

### Measure it from the DEF DUMP, not from the XML

⇒ **After any weapon or apparel cut, rebuild the index of tag → surviving item. Look for tags that went to zero. Then, more
importantly, look for the pawn kinds whose tags ALL went to zero.** `weapon_tag_audit.py` and `apparel_tag_audit.py` find
the kinds. No tool finds the emptied tags from the dump. The count of emptied tags there is always zero. That zero is
not a measurement (see the paragraph on cut weapons in this section). An empty tag is harmless to a kind that has another tag. An empty tag is fatal only to a kind with no surviving alternative.
Single-tag kinds are the ones that break.

🔴 **Read the tags out of the def dump, and gate it on the mod list.** Owner's ruling, 2026-08-19: a dump regenerated
under the full list is *"much more accurate than scanning the XML defs, provided that its version matches the current
modlist."* The reason: the dump is **post-inheritance, post-PatchOperation and post-dedup**, and a raw XML scan is none of
those. A kind can inherit `weaponTags` from an abstract parent, or get them from another mod's patch. The dump shows such
a kind. The scan does not.

⚠️ **The gate is not optional, and the gate is not a date.** Compare the dump's `modCount` and mod set with the live
`ModsConfig.xml` before you believe a single number. A dump captured under a different list describes a different game.
The two audit tools
compare only the count, and they do not refuse when `ModsConfig.xml` is unreadable. So compare the mod sets yourself.

⚠️ **A cut weapon is in the dump with empty `weaponTags`.** Cut apparel has empty `apparel.tags`. So an index built from
the dump holds surviving items only.
A tag whose every carrier was cut is ABSENT from that index, not empty. To learn which cut emptied a tag, read the cut
weapon's tags in its mod's source XML. An empty `weaponTags` list alone does not prove a cut.

**The XML scan is the fallback, not the method.** Use it when no matching dump exists: in a minimal-list window, or
before the next load. The scan is honest about raw file contents and blind to everything the loader does afterwards. So
a "disarmed" verdict from the scan is a hypothesis, not a finding.

🪤 **Do not repeat the claim that `weaponTags` is invisible offline.** The claim is FALSE. The field is in the dump. The
claim circulated in this project as settled fact and reached a skill and two queue items. A note passed the claim on,
and nobody measured the claim. Before you quote a channel as blind, check it.
