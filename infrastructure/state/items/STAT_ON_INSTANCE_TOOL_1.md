## spec

**The bridge can read a def's fields and a thing's inspect text, but it cannot ask the
game what a stat actually evaluates to on a spawned instance.** That gap blocks any
question of the form *"what does this weapon do in THIS pawn's hands"*.

Checked across the whole live tool list, 2026-08-23 02:5x:

| tool | what it returns | why it does not answer |
|---|---|---|
| `jawa/get_defs` | DEF fields, reflectively | static — the value before any StatPart runs |
| `jawa/inspect_string` | the inspect-pane sentences | "Blocked by", "Needs power" — not stat numbers |
| `rimworld/get_selected_pawn_inventory_state` | carried and inventory items | identity, not evaluated stats |
| `jawa/pawn_get` | equipment as `{def, stuff, isPrimary}` | names the weapon, not what it does |

⇒ **One method is missing:** `thing.GetStatValue(statDef)` on a named instance, and the
same for a pawn.

## Why it is worth building

`LIGHTSABER_AP_FROM_HAND_1` is blocked on exactly this, and it is not hypothetical:
`Lightsaber.dll` (workshop 3466124712, 1.6) carries `AdjustedArmorPenetration`,
`GetArmorPenetration`, `StatPart` and `StatPart_EquippedStatOffsetIncrease`. **AP is
adjusted at runtime and the adjustment is tied to equipped context**, so every AP number
in the record — all read from ground-spawned weapons — is unproven for a held one.

🔑 **The class is bigger than one weapon.** Any modded stat with a `StatPart` reads
differently on an instance than on its def, and this project has ~578 mods. A def-only
reader will keep producing confident numbers that are right for an item lying in the
dirt and wrong for one being swung.

## What the tool must do

- Take a `thingId` (or a pawn plus `equipment`/`apparel` slot) and one or more `StatDef`
  defNames; return the evaluated value.
- ⭐ **Return the def-level base beside the evaluated value**, so a caller can see
  whether a StatPart moved it at all. A single number cannot show that, and showing it
  is the whole point.
- ⚠️ **Report an unknown StatDef as a REFUSAL naming it**, never as 0. A stat that does
  not exist and a stat that evaluates to zero must not look alike — that is the failure
  mode this project has hit repeatedly tonight.

⚠️ **Assemblies cannot be deployed while the game runs** (the OS locks them), so this
lands in a game-down window with `build.py --gm --apply`. 🔴 `--gm` or the deploy strips
every player-acting tool.

## verify

- A lightsaber's `ArmorPenetration` read on a ground copy and on the same def equipped
  by a colonist, both reported, with the def base beside each.
- An unknown StatDef name returns a refusal that names it, not a zero.

## criteria

`LIGHTSABER_AP_FROM_HAND_1` can be answered, and no future item has to record a stat as
UNMEASURED because only the def could be read.
