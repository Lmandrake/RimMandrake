---
name: rimworld-content-moderation
description: Deciding what content stays in a RimWorld campaign out of a large mod stack — building contact sheets of real sprites straight from the defs so a keep/cut call is made by looking, cutting with Cherry Picker rather than uninstalling, and the traps that make a cut do nothing or break a pawn. Includes the one nothing warns you about: cutting the last weapon carrying a tag silently disarms every pawn kind whose tags ALL went to zero, so after any cut rebuild the tag -> surviving-item index from the def dump — post-inheritance, post-patch, post-dedup — and only fall back to scanning raw mod XML when no dump matches the current mod list. Use when curating, trimming or cherrypicking items, weapons, apparel, creatures or any graphical asset; when someone asks "which of these do we keep"; after any cut, to find the kinds left with nothing to hold; and before proposing that a mod be removed.
---

# RimWorld content moderation

Curating a 500+ mod stack down to one campaign's worth of content. The job is
mostly **deciding**, and the decisions are mostly **visual**, so most of the work
is getting the right thing in front of the person deciding.

## Build a contact sheet. Do not send a list of defNames.

A spreadsheet answers every question about an item except the one asked first:
*what does it look like?* Nobody can keep or cut 1,243 animals from names, and
looking each up costs a wiki tab per row.

**Render the actual sprites, straight from the defs, paginated, grouped by mod.**
1,243 animals took **6.7 seconds** and produced six PNGs. It is cheap enough that
there is no excuse for asking someone to judge from a list.

### Two artifacts, always

| output | why |
|---|---|
| the **sheets** | the decision surface |
| an **index CSV** — one row per placed cell → `defName, mod, texPath, file` | **a picture you cannot act on is decoration.** "Cell 3,7 looks wrong" has to become a defName you can cut |

A third falls out and is a deliverable in its own right: the **missing-texture
CSV**, which is the list of things that can only be judged in game.

### Row order is the design

Order rows by **mod**. Then a whole mod's contribution is one glance — "this is
what Alpha Animals adds, this is what Beasts of the Rim adds" — instead of sixty
lookups. Everything else about the layout is taste; this part is not.

## Where the sprite actually lives — this is the whole trick

It differs by def type, and getting it wrong yields an empty sheet:

| content | path to the texture |
|---|---|
| **weapons, apparel, buildings, items** | `ThingDef.graphicData.texPath` — **directly on the def.** Easy. |
| **animals and pawns** | 🔴 **NOT on the ThingDef.** `graphicData` is null for every animal. Hop `ThingDef` → its `PawnKindDef` → `lifeStages[LAST].bodyGraphicData.texPath` |

⇒ **A weapon or apparel sheet is strictly simpler to build than the animal one
that already exists.** If you are generalising, you are removing a hop, not
adding one.

### Five mechanics that decide whether it works

- **`texPath` is extension-less and side-less.** `Things/Pawn/Animal/Bear/Bear`
  may be `Bear_south.png`, `Bear_east.png`, or a bare `Bear.png`. Resolve, do not
  concatenate.
- **Index textures per mod from its LOADED content dirs *and* its root.** A mod
  with `LoadFolders.xml` keeps art under `1.6/Textures/`; indexing only
  `<mod>/Textures/` finds nothing for it and the mod silently renders blank.
- **PatchOperations have not run.** You are reading base XML, so a mod that
  retextures something by patching its `texPath` is invisible. The sheet shows
  the donor's art, not the patched result.
- **Do NOT deduplicate defNames.** A doubled cell means two mods ship the same
  thing — which is a finding. It is how *zebra*, *black bear* and *mandrill* were
  caught shipping twice; cutting one copy would have left the other on the map.
- **Vanilla art is in Unity AssetBundles and cannot be rendered offline.** Around
  40% of animals come out blank and that is CORRECT — they are the vanilla ones
  you already know by sight. Blank ≠ broken.

## Cut with Cherry Picker, not by uninstalling

Cherry Picker removes defs at load from a config file. Every entry is reversible
by editing one line, and **edits are inert until the next game start** — so
nothing here needs the game down, and being decisive costs nothing.

Removing a *mod* is a different act with different risk: a `ModsConfig` change, a
game-down window, and `Could not resolve cross-reference` if anything referenced
it. Check dependencies first; usually nothing declares one.

### 🪤 Do not validate Cherry Picker entries against a def dump

Cherry Picker removes defs **at load**, so the def dump is the *post-removal*
state. **A cut that worked is ABSENT from the dump.**

⇒ Checking config entries against a dump inverts the meaning of the result:
- **does not resolve** → the cut is already in effect. Correct, not broken.
- **resolves** → it has NOT taken effect yet. Either it was added since the game
  started, or it is not working.

So the check is only useful on **newly added** entries, and only to confirm you
spelled the defName right before the next load. It can never tell you an old
entry is a typo, because a typo and a successful cut look identical from here.

## How to run a session

- **Items are the unit. Mods are a consequence.** Never open with "shall we cut
  this mod" — people keep a mod they find silly to get gear they want, and
  renaming is cheap. Cut items; then ask whether a hollowed-out mod still earns
  its slot.
- **Attribute every row to its mod.** The reviewer needs it to look things up,
  and it catches the case where a name belongs to two different mods.
- **Lead with the principle, not the list.** Agreement on "real-world firearms
  are out" disposes of 74 items in one ruling; adjudicating 74 rows does not.
- **State the batch size and let them retune it.** Ask directly whether they want
  bigger or smaller rounds.
- **Keep anything with an interesting silhouette or a mechanical hook**, even if
  the name is wrong — a rename is one patch. Cut what is *recognisable from
  Earth*: a penguin is a penguin under any label.
- **Sort by look and genre fit, not by stats or spawn rate.** Balance and biome
  assignment are a later pass and will be redone anyway; do not let them drive a
  keep/cut call.
- **Anything you are unsure of goes on a hold list**, not into a guess.

## After cutting creatures, sweep the products they made

A cut animal leaves its meat, leather, wool, milk and eggs behind as items with no
source in the world — they still fill menus, stockpile filters and trade lists.
One pass after 168 creature cuts found **271** such orphans.

Build a `{product -> set of producing animals}` map from `race/meatDef`,
`race/leatherDef`, `race/woolDef`, `race/milkDef` and the comps
(`eggFertilizedDef`, `eggUnfertilizedDef`, `milkDef`, `woolDef`, `resourceDef`),
then cut a product only when **every** producer is cut.

🔴 **Three guards, and each one caught a real false positive:**

- **A plant may make it.** `DevilstrandCloth` looks orphaned when the devil sheep
  goes, and is harvested from the devilstrand *plant*. Check every
  `plant/harvestedThingDef` before cutting anything.
- **A recipe may make it.** Scan `RecipeDef.products` too.
- **The link may be name-only.** `AA_FlamingoPhoenix` has no EggLayer comp at all,
  so nothing but the shared stem ties it to its egg. A name-stem pass catches
  these — but require the stem to be long, strip the mod prefix, and confirm no
  *surviving* animal shares it, or the pass will cut live content.

## Before deprecating a mod, audit what else it ships

An empty item list is not an empty mod, and "all its animals are cut" answers only
one question. Check, in this order — it takes a couple of minutes and it is the
difference between a clean removal and a broken load:

1. **Every def type it defines**, not just the one you were reviewing. A creature
   mod that also ships items, buildings, sounds, bodies or damage types is doing
   work you did not audit.
2. **Its patch xpaths.** This is the real test. If every xpath names the mod's own
   prefix, or adds its own defs to a shared list, removal is contained. An xpath
   that reaches into Core or another mod's def is a functional change you would be
   reverting.
3. **Whether an assembly loads for the CURRENT game version.** DLLs under old
   version folders do not load and do not matter.
4. **Hard `modDependencies` from other mods** — distinct from `loadAfter`, which
   is harmless. Grep inside the `<modDependencies>` block only.

🪤 **An unprefixed defName is the thing to chase.** `WoolCamel` in an animal mod
looked like it might make Core's camel shearable — a real functional change to
vanilla. It turned out to belong to the mod's own camel. Verify; do not assume
either way.

## Traps that make a cut do nothing, or break the game

- 🔴 **Cutting a weapon can empty a `weaponTag`, and a pawn kind whose only tag
  resolves to nothing spawns UNARMED, silently.** After any weapon cut, diff the
  tags you removed against the tags that survive, then check which `PawnKindDef`s
  request the empty ones.
- 🔴 **A defName can exist as two different def types.** `OuterRim_Geonosian` is
  both a `XenotypeDef` and a `PawnKindDef`. Migrate by node, never by string.
- 🔴 **A mod can inject defs attributed to Core.** 1,073 `HL_` humanlike-animal
  twins reported as `ludeon.rimworld` and were invisible in every per-mod count
  until someone asked which mod owned a specific row.
- **Some mods generate a twin of every def in a class.** If a census returns
  suspiciously round doubles, look for a generator before cutting anything.
- **A def dump is disk, not runtime.** Mods that mutate defs at load — dedup
  passes especially — make any disk-derived claim about what EXISTS unsafe.
- 🪤 **Abstract parent defs have no `defName`** and are not content. They inflate
  every count and cannot be cut — Cherry Picker keys on `defName`. One animal
  census carried **50** of them, two wearing inherited labels that read as real
  creatures. Filter them out before presenting anything to a reviewer.
- **The cut is only proven by the next load.** After a large batch, census
  `Player.log` for `Could not resolve cross-reference` and group by the missing
  defName. 1,308 cuts and three mod removals produced **25 errors across 2 defs**
  — and reading the log is what distinguished the one that was ours from the one
  that was pre-existing. Guessing which is which from the diff cannot do that.

## The tools here

```
src/RimMandrake/Utils/def_inventory.py        load-set resolution, ParentName merging
src/RimMandrake/Utils/animal_inventory.py     -> animals.csv and five more
src/RimMandrake/Utils/animal_contact_sheet.py -> paginated PNGs + index CSV
```

The contact sheet is a thin projection over the inventory: it owns no load-set
resolution and no XML parsing. Build a weapon or apparel sheet the same way —
project over `def_inventory.py`, do not re-solve inheritance.

⚠️ **Pillow is not installed for WSL `python3`** (PEP 668 blocks `pip install`).
Windows `python.exe` has it, and relative paths work from the repo root:

```
python.exe src/RimMandrake/Utils/animal_contact_sheet.py --csv <csv> --out <dir>
```

---

## 🔴 A cut item can disarm a pawn kind that never named it, and nothing logs

This is the failure mode that survives every check a cut list can run on itself.

A `PawnKindDef` asks for weapons by **tag**, not by defName —
`weaponTags: NeolithicMeleeDecent`. Cut the last surviving weapon carrying that tag
and the tag resolves to an empty set. **A pawn kind whose weapon tag is empty spawns
bare-handed.** No red error, no cross-reference warning, nothing in `Player.log`:
the kind is valid, the tag is valid, the set is just empty.

Measured in this repo: vanilla `MeleeWeapon_Ikwa` is the only Core weapon carrying
`NeolithicMeleeDecent`; the one other def in the entire workshop that carries it
belongs to an inactive mod. Cutting the ikwa silently disarmed **every pawn kind
inheriting `TribalWarriorBase`** — vanilla tribal warriors and an authored faction's
signature raid alike. Nobody noticed for four days.

### Measure it from the DEF DUMP, not from the XML

⇒ **After any weapon or apparel cut, rebuild the tag → surviving-item index and look
for tags that went to zero** — then, more importantly, for the pawn kinds whose tags
ALL went to zero. A tag emptying is harmless to a kind that has another; it is fatal
only to a kind with no surviving alternative, and single-tag kinds are the ones that
break.

🔴 **Read the tags out of the def dump, and gate it on the mod list.** Owner's ruling,
2026-08-19: a dump regenerated under the full list is *"much more accurate than
scanning the XML defs, provided that its version matches the current modlist."* He is
right about why — the dump is **post-inheritance, post-PatchOperation and
post-dedup**, and a raw XML scan is none of those. A kind that inherits `weaponTags`
from an abstract parent, or is handed one by another mod's patch, is invisible to the
scan and present in the dump. Measured: the dump carries `weaponTags` on **696
ThingDefs and 414 PawnKindDefs**.

⚠️ **The gate is not optional and it is not a date.** Compare the dump's `modCount`
and mod set against the live `ModsConfig.xml` before believing a single number. A
dump captured under a different list describes a different game — that is the whole
reason this instruction has a proviso attached.

**The XML scan is the fallback, not the method.** It is what you use when no matching
dump exists — during a minimal-list window, or before the next load. It is honest
about raw file contents and blind to everything the loader does afterwards, so a
"disarmed" verdict from it is a hypothesis, not a finding.

🪤 **Do not repeat the claim that `weaponTags` is invisible offline.** It circulated
in this project as settled fact, reached a skill and two queue items, and is FALSE —
it was inherited from a note rather than measured. The field is in the dump. Check
before you quote a channel as blind.
