---
name: calibrating-binary-formats
description: Decode an opaque binary or packed numeric format by making the producing application print its own value for a record you can name, instead of guessing at the encoding. Covers measuring element width before assuming it, reading a constant value as a sentinel, validating a decode across a whole population rather than one sample, and marking decodes VERIFIED vs HYPOTHESIS so tools refuse to write what nobody has proven. Use when a savegame, blob, packed array, base64/DEFLATE payload or undocumented file reads as nonsense numbers, when you are about to try float16 or an offset hunt, or before writing anything back into a format you did not author.
---

# Never invent an encoding — make the system tell you its own numbers

**The rule in one line: the application that WROTE the bytes can almost always be made
to PRINT what they mean. Find that print before you theorise.**

An hour went into float16 theories on RimWorld's per-tile arrays. One debug-menu call
settled it exactly. That ratio is typical, and it is the whole skill.

---

## 1. The worked example, start to finish

RimWorld stores per-tile world data in a `.rws` savegame as **base64 → raw DEFLATE →
arrays of little-endian unsigned 16-bit ints**. Read naively they are gibberish:

| array | what the raw numbers looked like |
|---|---|
| `tileElevation` | **every ocean tile exactly 7842**; land 8204–9047 |
| `tileTemperature` | 2988–3074, whole planet |
| `tileRainfall` | 233–2584 on land |

**What was tried and was wrong:** `struct.unpack("<e", ...)` (float16) returned all
zeros — a decode that "works" and yields a constant is a decode that is wrong. Then
byte-offset guessing, then scale-factor guessing. Nothing converged, because nothing
was anchored to a known answer.

**What worked, in one call.** The game ships a debug output that prints the value:

```python
r = rb.call("rimworld/execute_debug_action", {"path": "Outputs\\Temperature Data"})
[l["message"] for l in r["effects"]["logs"]]      # -> "Tile avg: 6.7°C"
```

The tile it printed for is **the colony tile, whose id is in the save at
`game/info/startingTile` = 1318** — the one tile you can always name without guessing.
Raw value at index 1318 was **3067**.

```
(3067 - 3000) / 10 = 6.70          the engine said 6.7
```

Bias 3000, scale 10. Done. No theory survived contact with one printed number.

⭐ **`Outputs` has 261 entries** — `Temperature Data`, `Biomes`, `Terrains`,
`World Gen Steps`. The number you need is very often already in one of them.

## 2. 🔴 Then validate across a POPULATION — this is the step people skip

One matching sample proves a *coincidence*. A decode is credible when it produces a
sensible **distribution**, not a sensible point.

Decoded biome mean temperatures came out:

```
Tundra          -1.1 °C
BorealForest     0.4 °C
TemperateForest  6.1 °C
```

**Correctly ordered, plausibly spaced** ⇒ the decode is right. Had Tundra come out
warmer than TemperateForest, the one exact match at tile 1318 would still have been a
fluke and the decode still wrong.

⇒ Pick a grouping the format itself provides (here: biome), decode the whole array,
aggregate, and ask whether the ordering is one physics would produce. **A decode that
cannot be falsified by a population has not been tested.**

## 3. Measure the element WIDTH before you assume it

Nothing about a blob announces its stride. Divide:

```
bytes_per_record = len(raw_decompressed) / known_record_count
```

The tile count is knowable independently (RimWorld: from the world's subdivision, or
from any other per-tile array that decodes cleanly). `len(raw)/count == 2` settles
uint16 versus uint8 versus float32 without a single unpack attempt.

⚠️ **If the division is not an integer, your record count or your container is wrong** —
stop and fix that before touching the encoding. A non-integral stride is the format
telling you there is a header, a trailer, or a second array concatenated on.

## 4. 🔑 A CONSTANT across a whole class is a huge clue

**Every ocean tile's elevation read exactly 7842.** Identical values across a natural
class are never data — they are a **sentinel or a datum line**, and they hand you the
bias.

The test that confirms a bias: does it put the sentinel and the class boundary on
**round numbers**?

```
elevation:  raw - 8192  ->  ocean = -350 m       land minimum = exactly 1 m
```

Land starting at **1 m** and not 3.7 m is not luck. `8192` is also `2^13`, which is what
a programmer picks for a signed-ish midpoint in a uint16. Two independent reasons
pointing at the same constant is real corroboration — unlike two guesses that happen to
agree.

⚠️ Corroboration is not proof. `raw - 8192` is still marked **strongly supported, not
verified** in `D:\Luke\dev\Rimworld\skills\rimworld-world-editing\SKILL.md` §13, because
no engine output was ever made to print an elevation for a named tile. Say which one you
have.

## 5. 🔴 Mark VERIFIED vs HYPOTHESIS, and make tools REFUSE to write the unverified

The status belongs in the code, next to the constant:

```
temperature   (raw - 3000) / 10   -> °C          ✅ VERIFIED against the engine
rainfall      raw                 -> mm/year     ✅ land spans 233-2584
elevation     raw - 8192          -> metres      ⚠️ strongly supported, not proven
pollution     raw / 65535         -> 0..1        ⚠️ HYPOTHESIS
swampiness    raw                 -> 0..1        ⚠️ scale unconfirmed
```

`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\worldmap.py` exposes `get(array, tile)` and
`set(array, tiles, value)` in **physical units**, and **refuses to write any array whose
encoding is unconfirmed**. That refusal is the point of the labelling — a status that
only lives in a comment gets read by nobody at the moment it matters.

🔴 **A wrong decode that still RESOLVES is worse than one that errors.** float16 gave
all zeros, which was obviously broken and cost nothing. A bias that is off by 10 gives
you plausible temperatures forever and poisons every decision downstream — silently.
**Reading is cheap to be wrong about; writing is not. Gate the write.**

## 6. Reading order — the checklist

1. **Container first.** base64? compressed? RimWorld's arrays are base64 then **raw
   DEFLATE** (no zlib/gzip header — `zlib.decompress(b, -15)`). Get plaintext bytes
   before thinking about numbers.
2. **Stride.** `len(raw) / count`. Refuse to continue on a non-integer.
3. **Endianness and signedness.** Try `<H` first; the value range usually decides. A
   whole array under 65535 with no negatives is uint16, not int16.
4. **Anchor.** Find one record whose true value the system will print, and name that
   record from the data itself (`startingTile`, a def name, a row id) — never "probably
   the first one".
5. **Solve bias/scale from the anchor.** Two anchors if you can get them; one anchor
   plus a sentinel is nearly as good.
6. **Validate on the population.** Group, aggregate, check the ordering is physical.
7. **Label and gate.** VERIFIED / HYPOTHESIS in the code, and no writes on HYPOTHESIS.

## 7. Generalises to — anything whose producer can be asked to speak

The RimWorld specifics are incidental. The technique applies wherever there is a program
that already understands the bytes:

| where the number is hiding | examples |
|---|---|
| **debug menu / dev console** | RimWorld `Outputs`, game dev overlays, `about:` pages |
| **logs at verbose level** | the value you want printed for one named record |
| **an export or "copy as" function** | CSV/JSON export of the same records you are decoding |
| **an API over the same store** | read one record through the sanctioned path |
| **the UI itself** | hover a tooltip, screenshot it, read the number off the screen |
| **a second implementation** | another parser, a viewer, a mod that already reads it |

**The anchoring requirement is the same in every case: you need a record you can point
to in BOTH worlds.** The single hardest part of a calibration is usually not the maths —
it is finding an identifier that survives the trip from the file to the UI. Look for it
first, and let it decide which record you calibrate on.

⚠️ **The UI may transform too.** A tooltip showing "6.7 °C" on a machine set to
Fahrenheit would have handed you a wrong bias with total confidence. Check the display
units and the display rounding before treating a screen number as ground truth — "6.7"
is one decimal place, so it constrains the decode to ±0.05, not exactly.

## 8. 🔴 A calibration rots when its SOURCE legitimately grows

A calibration anchored today is not anchored forever. The rimplace known-answer
contract check was correct the day it was written — anchored against the companion
tool's parameter set as it stood then. When the tool later grew a new parameter, the
calibration was not touched in the same change, and the contract check quietly kept
reporting **UNMEASURED** for a full day before anyone connected the two.

⇒ **A calibration and the thing it calibrates are one change, not two.** Whenever a
companion tool, API or format gains a field or parameter, update the calibration
that anchors it in the SAME commit — never as a follow-up. "The calibration still
passes" means nothing until you have checked it still covers the *current* parameter
set, not the one it was written against.
