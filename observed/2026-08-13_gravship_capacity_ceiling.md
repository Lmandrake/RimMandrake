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

---

## The XML-patch route is DEAD, and a mod already ran the experiment for us

**Do not spend a load testing whether an XML patch survives BG's startup
rewrite. It does not.** Engines Unlimited (`nep.enginesunlimited`, active) ships
exactly that patch and it is clobbered:

| | value |
|---|---|
| Engines Unlimited XML, `workshop/…/3528446690/1.6/Patches/Odyssey_enginecount.xml:8` | `<maxSimultaneous>9000</maxSimultaneous>` |
| **live def, `SmallThruster`** | **20** |
| **live def, `LargeThruster`** | **10** |

20 and 10 are Bigger Gravships' numbers. BG's Harmony prefix on
`DefGenerator.GenerateImpliedDefs` runs **after** all XML patching and is the
last writer, so an XML patch on any def BG touches is silently overwritten.

🔴 **This failure mode is worse than a no-op**: the patch looks applied in every
offline check — the XML is there, the file loads, no error — and is absent only
in the live def. It is the same shape as the `SubstructureSupport: 500` ghost
and the three-Jawa claim, and that is now **three instances in one day of
offline evidence disagreeing with the running game.**

⇒ A `statOffsets` patch on `GravFieldExtender` would be eaten the same way.
Two routes remain, neither BRIDGE's to choose: the BG settings slider
(`BG_gravEngineSupport`, and engine-side settings demonstrably DO reach the live
def — 632.8 and 34 are both in there), or our own Harmony postfix ordered after
BG's prefix, in the companion DLL.

⚠️ And 3,633 was optimistic regardless: support would presumably only count
extenders the engine can see, and ours sit at up to 84.7 against `maxDistance`
34. The realistic figure is 633 + 250 × (extenders inside 34), not 633 + 250×12.

---

## 🟢 RESOLVED — it was a settings value, and it applies LIVE with no restart

**The owner's instinct was right: this was never a hard ceiling.** Sequence,
all live on the running game, no reload:

1. `rimworld/get_mod_settings redmattis.biggergravship` — BG's live settings:

   | setting | value | reaches the def? |
   |---|---|---|
   | `gravEngineSupport` | 632.7954 | ✅ yes |
   | `gravExtenderSupport` | **500.0** | ❌ **no — def has no SubstructureSupport at all** |
   | `gravExtenderMaxDistanceFromEngine` | **85.0** | ❌ **no — def reads 34** |

2. `rimworld/update_mod_settings` with `{"values": {"gravEngineSupport": 4500}}`
   → setting became 4500 in memory and persisted to
   `Config/Mod_3522759531_GravshipSizeSettings.xml`.
   ⚠️ **The def did NOT change yet** — still 632.7954. Writing the setting is
   not applying it.
3. `rimworld/open_mod_settings`, then clicked **"Apply Settings Now!"**
   (`ui-element:10:6:63`). Response: *"UI state did not change"* — which is
   wrong; the def changed.
4. Live `GravEngine` re-read: **`SubstructureSupport: 4500.0`**.
5. Engine panel: **`Connected substructure: 4057 / 4500`** — under capacity.

**So a BG size change needs no game restart.** That removes a ~25-minute load
from every future experiment on ship size. It does need the Apply button; the
settings write alone is inert.

### The extender bug is real and survives Apply

After Apply, `GravFieldExtender` **still** has zero occurrences of
`SubstructureSupport`. BG's own setting says extenders are worth 500 each and
the value never reaches the def — so BG intends 632.8 + 12×500 = 6,632 and
delivers 633. Two of its writes are broken (extender support, and extender
max-distance-from-engine, which gets the engine's 34 instead of its own 85).
**Not our bug and not fixable from the settings window** — the slider is already
set to 500.

### Correction to the "ceiling" framing above

Everything measured above stands as measurement — extenders and amplifiers do
contribute nothing, a second engine does disable the first, capacity is not
power-dependent. What was wrong was the **conclusion** that the ceiling was
therefore fixed at 633. It is a configurable number, it was simply set low, and
the hull never had to shrink.
