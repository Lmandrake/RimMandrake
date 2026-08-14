
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

---
## 🎯 EXACT MECHANISM — the extension was not the cause, it was the enabler

**Trigger: `rimworld/set_camera_zoom {"rootSize": 6}`.**

Camera+'s extension widened the zoom range from **11–60 to 0–100**. It did not
break anything by itself — it made `rootSize 6` *reachable*. **Below the engine's
floor of ~11 the world mesh render breaks.** So the fault is a value out of
range, and the mod is only what removed the guard rail.

**Bracketed on one map with nothing else varied:**

| time (local) | rootSize | render | screenshot |
|---|---|---|---|
| 20:50:29 | 12 | clean | 2.83 MB |
| 20:51:15 | **6** | 🔴 **RED** | **0.49 MB** |
| 20:51:44 | 15 | clean | 3.74 MB |
| 20:52:28 | 11 | clean | 2.43 MB |

The trigger call landed 5 s before the first corrupted frame; the correction to
15 landed 2 s before the first clean one.

⭐ **Reusable diagnostic — PNG file size is a free corruption signal.** The broken
frame is **0.49 MB against 2.4–3.7 MB** for clean ones. A flat-colour image
compresses to a fraction. **You can detect this class of failure without looking
at the picture**, which matters when a screenshot is one of many.

## 🔴 FOUR INNOCENT COMPONENTS WERE ACCUSED BEFORE THE REAL CAUSE

In order, on one evening: **eight art mods**, **the GPU / VRAM / texture atlas**,
**another seat's texture prune**, and **Designator Shapes** — each proposed
confidently, each wrong. The actual cause was a parameter we passed ourselves.

📌 **The pattern: when something breaks in a 580-mod stack, the mod list is the
most available explanation and is usually not the answer.** Ask first what *we*
changed in the last minute. Our own bridge traffic is logged, timestamped and
bracketable; a mod interaction is neither.

⚠️ **And it stayed accused after it was solved.** BRIDGE toggled the extension
off, watched it recover and conceded on the record — yet a seat was still
building a case against Designator Shapes afterwards. **Closing a finding loudly
is not optional; an open question keeps consuming seats until someone says it is
shut.**
