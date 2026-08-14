
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

## Independent confirmation — PROJECT, 2026-08-13, offline forensics

Ran blind against the GPU/atlas premise, from screenshots, `Player.log`, config
and the web. **It lands on the same verdict**, and the numbers below are what
make it stick without needing the game running.

### 🔬 MEASURED — the corruption window is 17 seconds wide and it healed itself

Every bridge frame in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots`
was scored for mean saturation and for the fraction of pixels sitting on an
RGB-cube corner (`max>200 & min<60`), over the map area only:

| frame | mean sat | corner px | verdict |
|---|---|---|---|
| `rimbridge_20260813_205029.png` | 0.207 | 0.000 | clean |
| **`rimbridge_20260813_205103.png`** | **0.971** | **0.949** | **corrupt** |
| **`…_205115 / 205117 / 205118 / 205120`** | **0.956–0.979** | **0.869–0.898** | **corrupt** |
| `rimbridge_20260813_205144.png` | 0.313 | 0.000 | clean |
| all 38 other frames, 17:56→20:57 | 0.18–0.45 | 0.000 | clean |

**Exactly five frames, 20:51:03 → 20:51:20, bracketed by clean frames of the same
scene 34 s before and 24 s after.** Nothing was restarted in between. **A texture
atlas does not heal in place** — that single fact eliminates the entire
atlas/VRAM/driver family on its own.

### 🔬 MEASURED — the palette is 8 colours, and they are exact

Colour histogram of the map area (excluding UI), `…_205120.png` vs the clean
`…_205144.png` of the same camera position:

| | unique colours | dominant |
|---|---|---|
| corrupt `205120` | **1,901** | **`(255,0,0)` = 78.7%**, then exact `(0,255,255)`, `(0,0,255)`, `(0,255,0)`, `(255,255,0)` |
| clean `205144` | **27,070** | none above 0.5% |

The values are **exactly** on the cube corners, not near them. Real block-
compression failure quantises to *block averages*, which are arbitrary colours —
it does not land 78.7% of a frame on `(255,0,0)` to the bit. This is a mesh/UV
render fault, which is what a sub-floor `rootSize` produces.

Corroborating: `…_205103.png` still carries a smooth gradient in green
(`(0,205,255)`…`(0,227,255)`) with red pinned to 0 and blue pinned to 255 —
**channel clamping, with shading intact underneath.** The textures were never
lost.

### 🔬 MEASURED — the log is clean, and that is evidence, not absence

`Player.log`, 7,267 lines, whole file swept. **Zero hits** for `OutOfMemory`,
`RenderTexture`, `Non-readable`, `mipmap`, `exceeds`, `too large`,
`null texture`, `Unsupported`. The only `VRAM` line is the healthy header
(15,977 MB). The only `atlas` hits are an unrelated XML field error and a mod
named `BMT_SmogPupa`. No GPU-side error of any kind, and no crash — the process
was still logging pawn spawns after the window closed.

Three real content errors exist and **none of them is this** — filed separately,
not causes: an empty-`texPath` `Graphic_Multi` (14×, lines 1564–1614, reproduces
across loads), SWCP's missing `SWCPshaders` AssetBundle (lines 3532–3540), and one
absent animal texture `swanimals/Shyrack/Shyrack_Flying_4_north` (line 6937).

### 🔬 MEASURED — the hypotheses that were killed offline, and how

| hypothesis | killed by | cost |
|---|---|---|
| Texture-atlas / VRAM exhaustion from 580 mods | log sweep: zero atlas/VRAM/memory errors; and it healed with no restart | free |
| RimSort/RimPy DDS "texture optimization" corruption | `find` over the Workshop tree: **one** `.dds` modified in 2 days, and it is a mod's own shipped asset. No mass conversion ever ran. | free |
| RTX 50-series driver / D3D device reset | would not heal in 24 s without a device recreate, and Unity logs nothing at all here | free |
| `-disable-compute-shaders` causing bad CPU-path compression | present since launch; 38 clean frames across 3 hours with the identical flag | free |
| A stuck dev-mode View Settings overlay | session transcripts: the only `set_debug_setting` calls today were two translation-debug flags, both `False`. No view/overlay toggle was ever sent. | free |

**On `-disable-compute-shaders`, since it looked like a clue and is not one.**
It is a supported RimWorld flag that disables the 1.6 compute-shader texture
compressor (auto-disabled on low-VRAM cards anyway); players added it because
1.6 could hang on "Initializing" with DLC enabled. `Prefs.xml` still has
`<textureCompression>True</textureCompression>`, so compression runs on the CPU
path. **Harmless here, and unrelated** — but leave it, it is doing a job.

### 📚 READ ON THE WEB — what the searches actually established

None of it matched, which is the useful result:

- The 1.6 compute-shader compressor and the `-disable-compute-shaders` flag are
  real and documented — <https://rimworldwiki.com/wiki/Version/1.6.4518>
- 1.6 loads `.dds` natively, so RimSort/RimPy/Image Opt texture "optimization"
  now breaks mod textures — <https://steamcommunity.com/sharedfiles/filedetails/?id=3573692536>.
  **Checked and not happening here.**
- RimWorld builds mod textures into atlases at load and spills across VRAM/RAM
  with large mod lists — <https://rimworldwiki.com/wiki/Modding_Tutorials/Textures>
- RTX 5080/5090 instability is real but presents as crashes, black screens and
  flicker — never as a 17-second self-healing recolour —
  <https://www.tomshardware.com/pc-components/gpus/users-report-bricked-or-unstable-rtx-5090-and-5080-cards-root-cause-to-be-determined>
- A D3D device reset invalidates *every* child resource, so recovery needs a full
  device+resource recreate — inconsistent with a 24-second self-heal —
  <https://discussions.unity.com/t/failed-to-present-d3d11-swapchain-due-to-device-reset-removed-list-of-solutions/919068>
- No forum, issue tracker or Steam thread describes this symptom. **The reason is
  that it is not a RimWorld bug — it is only reachable through the bridge.**

### 🧷 The `Shapes` palette in the frame is a second, separate fault

The five corrupt frames uniquely show Designator Shapes' (`merthsoft.designatorshapes`,
Workshop 1235181370) palette open with *"Must designate abandoned claimable
structures or items."* pinned top-left. That is the **armed-designator jam**, from
`select_architect_designator {"designatorId":"Designate_Claim"}` followed by
`apply_architect_designator` with `keepSelected` left at its default `true`.
**Cosmetically co-located, causally unrelated** — already covered at
`D:\Luke\dev\Rimworld\skills\rimbridge\references\traps.md:285`.

### ✅ Cheapest confirmations, in cost order, if it ever recurs

1. **`ls -la` the screenshot.** Flat colour compresses tiny — the corrupt frames
   are ~0.5 MB against 2.4–3.7 MB clean. **Free, instant, decisive.**
2. **`rimworld/get_camera_state`** → read `rootSize`. Below ~11 and you are done.
3. **Re-shoot 30 s later at `rootSize` ≥ 11.** If it heals, it was never the GPU.
4. Only if all three fail: sweep `Player.log` for atlas/VRAM (expect nothing),
   then consider hardware.

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
