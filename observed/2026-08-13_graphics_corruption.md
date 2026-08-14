
---
## ✅ DIAGNOSED AND FIXED — Camera+, not the GPU. 2026-08-13.

**Cause: `brrainz.cameraplus` (Camera+, load order 88) zoom extension.**

> **`rootSize` under ~11 renders the map flat red.** — BRIDGE, from inside the
> running game, after turning the zoom extension OFF and watching it recover.

**Not a graphics fault at all.** No VRAM exhaustion, no texture-atlas overflow,
no RTX 50-series driver issue, nothing to do with 580 mods.

### What gave it away, and what nearly didn't

The screenshot was read first as GPU corruption and a web search was launched on
that premise. **The disproof was visible in the same image the whole time:**

| corrupted | rendering CORRECTLY |
|---|---|
| terrain, large objects | pawn portraits, minimap, all UI text, notification boxes, grass tufts |

**Uniform corruption does not spare the minimap and the portraits.** And the
palette was not garbage — flat saturated primaries following object silhouettes
is a *rendering mode*, not a broken shader.

The confirming symptom arrived separately: **the owner could zoom in arbitrarily**,
which vanilla clamps. Unlimited zoom + flat colour = one mod in a bad state, not
two faults.

### 📌 The lesson, and it is about method not about Camera+

**A category was chosen before the evidence was examined.** "Rainbow textures on
a 580-mod install" reads as GPU/atlas, so the search went there — and the owner
asking *"does that image look bizarre to you?"* is what forced an actual look.
**Reasoning about the class of a problem is not the same as looking at it**, and
this project has now paid for that distinction three times in one day: a def dump
read instead of runtime, a symbol read instead of a call path, and this.

### ⚠️ Standing operational note

**Do not re-enable Camera+'s zoom extension without turning it off afterwards.**
Anyone inheriting a red map should check `rootSize` before suspecting hardware.
