## ✅ BUILT AND DEPLOYED 2026-08-26, seat BUILD, in the game-down window

**`jawa/thing_stats`** is written, compiled (0 warnings, 0 errors, no tool removal) and deployed to
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`
with `build.py --gm --apply`. Source:
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchStatTools.cs`, beside `jawa/pawn_stats`.
The deployed DLL's tool-name surface reads **166**, `jawa/thing_stats` among them.

⛔ **That is not the same claim as "the tool works".** RimBridgeServer discovers companions only at
STARTUP, so it does not exist in any running game until the next launch. This item stays open on
`bridge` for exactly that reason.

**What it does, against the spec above:** takes `thing` (one id, or several comma-separated) or
`pawn` + `slot` (`equipment|apparel|inventory`), plus named StatDefs. Every row returns `value`
(`Thing.GetStatValue` — the instance) **beside `defBase`** (`ThingDef.GetStatValueAbstract` with this
thing's stuff — what a def-only reader would have said), plus `delta`, `movedFromDef` and the
`statParts` that can move it. An unknown StatDef is refused **by name with suggestions**; an
unresolved thing id is refused by name, and if the id was really a defName the refusal lists the
live ids carrying that def. 🔴 **A named stat that resolved nowhere returns `success:false`** — the
one thing the first draft got wrong, and the exact failure `BRIDGE_ARG_SHAPES_INCONSISTENT_1` is
filed against: an empty collection with `success:true` cannot be told apart from a true empty result.

### Validation plan — run it at the next load

```
ITEM     jawa/thing_stats — a StatDef evaluated on a live item, with the def-level number beside it
SEE      One answer holding two rows for the same weapon def: a ground copy and a held copy, each
         with value AND defBase, and movedFromDef true wherever a StatPart is in play
ROUTE    python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_stat_and_room.py
         (census must read 166 and list jawa/thing_stats; check 3b reads a held weapon)
         then, for the lightsaber question: jawa/spawn_batch a second copy on the ground, and
         jawa/thing_stats {thing: "<groundId>,<heldId>", stats: "ArmorPenetrationSharp"}
PREDICT  166 jawa/ tools live; a vanilla steel weapon reads movedFromDef=false on Mass and
         true on nothing; a lightsaber's ArmorPenetration* differs between the two ids
CLOSE    One run where both ids come back with value and defBase — NOT chasing every StatPart in
         the mod stack, and NOT grading the lightsaber's number itself (that is
         LIGHTSABER_AP_FROM_HAND_1's own item)
RIDE     batch (no new mod, no def change — it is a companion tool and rides with §23)
LIES     The census is the whole gate: a deployed DLL registers NOTHING until the game restarts,
         so a "tool not found" after a load that predates this deploy is not a failure of the tool.
         And movedFromDef=false is only meaningful once defBase is non-null — a null defBase means
         the base could not be computed, never "nothing moved it".
```

---

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
