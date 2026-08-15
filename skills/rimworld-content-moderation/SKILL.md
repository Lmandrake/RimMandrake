---
name: rimworld-content-moderation
description: Deciding what content stays in a RimWorld campaign out of a large mod stack — building contact sheets of real sprites straight from the defs so a keep/cut call is made by looking, cutting with Cherry Picker rather than uninstalling, and the traps that make a cut do nothing or break a pawn. Use when curating, trimming or cherrypicking items, weapons, apparel, creatures or any graphical asset; when someone asks "which of these do we keep"; or before proposing that a mod be removed.
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
