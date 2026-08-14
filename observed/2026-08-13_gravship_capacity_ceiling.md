# The gravship substructure ceiling is 632.8, and nothing raises it

BRIDGE, 2026-08-13, live on a quicktest map with the v1 ship built (4,057
substructure cells). Every number here was read off the RUNNING game via
`jawa/get_def` or the engine's inspect panel — not off `DefDump`.

## The finding

| source | SubstructureSupport, live |
|---|---|
| `GravEngine` | **632.7954** |
| `GravFieldExtender` | **absent from statBases entirely** |
| `VGE_GravFieldAmplifier` | **absent from statBases entirely** |

Engine panel with 8 extenders built: **`Connected substructure: 4057 / 633`**.
633 is the engine alone. The hull is **6.4x over capacity.**

## What was ruled out, and how

**Distance is not the gate.** Moved an extender from 22.0 tiles to 15.0 —
nowhere near the 34 boundary. Capacity before and after: `4057 / 633`,
unchanged. Not a `<` vs `<=` boundary bug and not placement.

**More engines are not available.** Spawned a second `GravEngine` on the
substructure. The panel reported **"Grav engine disabled: Multiple grav engines
present"** and the overlay showed two readouts, `4057/633` and `0/633`. Two
engines do not sum; they disable each other. Removed it; panel recovered.

**Capacity is not power-dependent.** Control, from two screenshots of the same
ship: at 18:13 `Power output: 4800 W` with `4057 / 633`; at 18:52
`Power output: 0 W` with `4057 / 633`. Same figure across a 4,800 W swing.

## 🔴 The method lesson, which is the reusable part

`GravFieldExtender` shows `SubstructureSupport: 500` in `DefDump/defs/ThingDef.json`
and **nothing** in the running game. `VGE_GravFieldAmplifier` shows `+200` in the
dump and nothing live. Both were quoted as "confirmed in the resolved def" and
both were wrong.

**A def dump records what shipped on disk, never what the game holds after
startup code has run.** The same trap produced the "three live Jawa xenotypes"
claim earlier the same day, which the log disproved (BTD Remix dedups 250 -> 150
at load). Two independent instances in one session.

**For a runtime value, read the runtime.** `jawa/get_def` against the live game,
or the game's own UI. Reserve the dump for "what does this mod ship".

## Consequence

Reach and capacity are different axes. Extenders and amplifiers extend the
FOOTPRINT (visible as pale supported patches in the substructure overlay) and
contribute no budget. Only the engine carries budget, there can be only one, and
it is 632.8. A flightworthy hull is ~633 cells, not 4,057.

`NEXT_RELOAD.md`'s "84.72 against an 85 cap, 0.28 of a cell of margin" is false
precision twice over: the live `maxDistance` is **34**, and the extender it
positions contributes nothing at any distance.

---

## UPDATE — it is a MOD BUG, with a mechanism, and possibly fixable

⚠️ **Correction to my own reasoning above.** Vanilla puts the extender's support
in **`statOffsets`**, not `statBases`, and my first live read only searched
`statBases`. Re-checked the entire def: `SubstructureSupport` appears **zero**
times and there is **no `statOffsets` block at all**, so the conclusion stands —
but the argument as first given was incomplete.

**Vanilla**, `Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Gravship.xml`:

| def | vanilla | live in our game |
|---|---|---|
| `GravFieldExtender` radius | 16.9 | **30.0** |
| `GravFieldExtender` support | **`statOffsets` 250** | **absent entirely** |
| `GravFieldExtender` maxSimultaneous | 6 (documented) | **12** |
| `GravEngine` support | `statBases` 500 | 632.7954 |

**Mechanism.** The live def still reports `modName: Odyssey`, and a grep of the
whole workshop tree finds **no XML anywhere touching `GravFieldExtender`**. So
nothing patches it in XML — the values are rewritten in **C# at startup**, which
is exactly what `NEXT_RELOAD.md` records of Bigger Gravships: it bakes radii
into defs at startup via a Harmony prefix on `DefGenerator.GenerateImpliedDefs`.
It raises the radius and the cap, and the `statOffsets` do not survive.

**So the ceiling is not a design fact, it is a regression:**

- vanilla: 500 + 6 x 250 = **2,000**
- ours: 632.8 + 12 x 0 = **633**

Bigger Gravships made the extender larger and worthless.

**Candidate fix, for OPS/CREATE to rule on, not BRIDGE:** patch `statOffsets`
back onto `GravFieldExtender`. If it survives, 633 + 12 x 250 = **3,633**.
🔴 **Unproven, and it is the entire question** — whether an XML patch survives
BG's startup rewrite or is clobbered by it. Only a load answers that. Do not
scope a hull on 3,633 until it is measured.
