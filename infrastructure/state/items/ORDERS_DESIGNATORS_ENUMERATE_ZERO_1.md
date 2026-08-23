## spec

**`rimworld/list_architect_designators` returns ZERO designators for the `Orders`
category**, while returning real designators for the other 41. Measured 2026-08-23 10:4x
by enumerating every category on a live map.

`Orders` is where RimWorld keeps the verbs a player uses constantly — **Open**, Mine,
Chop, Harvest, Haul, Deconstruct, Hunt, Tame, Slaughter, Strip, Claim, Cancel. An empty
list there is not a small gap; it is most of what a colony is told to do.

## How it surfaced

Trying to crack an `AncientCryptosleepCasket` from the bridge for
`RAKATA_ENCOUNTER_UNCHANGED_1`. Four routes were tried and all four refused:

| route | result |
|---|---|
| gizmo on the selected casket | Claim, Deconstruct, Uninstall, Customize… **no Open** |
| context menu with a colonist adjacent | only "Enter cryptosleep casket" |
| architect designator | 🔴 **`Orders` enumerates 0** |
| `jawa/damage` Bomb 500 | 🔴 casket destroyed, **occupant lost** — 10 bombed, zero pawns released |

⇒ The one route that should have worked is the one that reports nothing.

## What to check first

⚠️ **Do not assume the tool is broken until the category NAME is ruled out.** The list
comes back as a label, and `Orders` may be a display label whose internal `defName`
differs, or the tool may key on `DesignationCategoryDef` while `Orders` is assembled
differently. **Try the defName and try a case variant before touching C#.**

🔑 If it is genuinely empty, the fix is worth more than this one casket: with `Orders`
working, the bridge can mine, chop, harvest, haul, hunt, tame and open from a script.
Without it, every one of those needs a gizmo or a context menu that may not exist.

## verify

- `rimworld/list_architect_designators` on `Orders` returns a non-empty list including
  an Open designator.
- `select_architect_designator` + `apply_architect_designator` on a casket cell produces
  a sleeper, and the sleeper is Rakatan.

## criteria

A casket can be opened from the bridge without destroying what is inside it.
