# Graphics generation channel — review & recommendation

_Research spike, 2026-09-05, BENCH. Owner brief: the current channel is slow &
clumsy; want native transparency, multi-facing consistency (one hero → RimWorld's
facings; Wrecked Machines is the test case), and Remotion to animate background
stills. Local facts measured here; channel/model comparisons from web research
(2025-2026), each tagged where it was only UNCERTAIN._

## Current channel — why it's slow and clumsy (measured)

OpenAI **Codex CLI `$imagegen`** (gpt-image via the ChatGPT login), driven by
`skills/generating-images/scripts/codex_image.py`. Three structural faults:
1. **Transport:** shells a *Windows* Codex binary from WSL, resolves a
   content-hash path that moves on every Codex update, converts every path
   WSL↔Windows, one image per call, no batch.
2. **No native alpha:** ChatGPT-auth Codex can't output transparency, so every
   sprite takes a manual two-step green-screen chroma-key cut (lossy on edges).
3. **No cross-facing identity:** each facing is a *fresh independent generation*;
   `--reference` only conforms canvas/registration, never conditions the pixels.
   This is the root of the Wrecked-Machines drift.

No image API key exists on the machine; `rembg` is not installed. node v22 is.

## Recommendation

**Channel: Google Gemini "Nano Banana Pro" (Gemini 3 Pro Image) + local `rembg`.**
It is the best-in-class *identity-across-angles* engine (up to 8-20 reference
images, strong subject consistency) — which is exactly the multi-facing problem.
Its one gap, no native alpha, is closed by a local `rembg` cutout (no key,
offline), which *also* replaces the current chroma-key step for the whole
pipeline.

🔴 **CORRECTION 2026-09-05 (measured against the live API):** the Gemini free
tier is **`limit: 0` for image generation** — image models (flash AND pro) return
HTTP 429 `RESOURCE_EXHAUSTED` on the free tier. Image gen **requires billing
enabled** on the AI Studio / Google Cloud project. A free key generates TEXT, not
images. So there is no free image channel: gpt-image-2, Gemini, Flux, Ideogram
all bill per image. Gemini stays the recommended pick on *quality* (best
multi-facing), at ~$0.039/image (flash) / ~$0.134 (pro). The channel client
`skills/generating-images/scripts/gemini_image.py` is built and the key is valid
— it works the instant billing is turned on. The no-billing alternative for
rigid wreckage is the local TripoSR 3D-proxy route (GPU, offline, free).

- **Runner-up, single-tool clean:** **gpt-image-2** — native alpha + reference in
  one call, no cutout step at all. Cleaner, but needs an **OpenAI API key +
  billing** (a new account) and its angle-identity is good but below Gemini's.
- **No-Google/No-OpenAI option:** **Flux.1 Kontext via fal.ai** — cheap
  pay-per-call token, strong style preservation, alpha via `rembg`.

## The multi-facing pipeline (the key ask)

**Recommended (MATURE): hero → reference-conditioned facings.**
1. Generate the hero (south, 3/4 top-down) in the chosen channel.
2. One call per facing into Nano Banana Pro, hero as reference, explicit
   orthographic-rotation prompt ("same object, top-down, rotated 90° to face
   east, identical proportions/materials, no perspective change").
3. `rembg` cutout each (one automated step, replaces chroma-key).
4. Mirror east→west in PIL (RimWorld convention) — free, perfectly consistent.
5. Validate silhouette/proportion drift with the existing
   `validate_sprite.py`; re-roll the odd facing (2D synthesis isn't perfect).

🔴 **TESTED 2026-09-05, verdict = not viable from one hero (see
`Transient/triposr_prototype/contact_sheet.png`).** TripoSR ran end-to-end on the
AutomatedSmelter (RTX 5080, torch cu128): silhouette consistency is perfect by
construction, but east/north come back as near-featureless dark slabs — it
reconstructs a thin shell from the single photo and invents no detail for unseen
sides. The current kludged facings are far richer. ⇒ Single-hero 3D-proxy is OUT
for facings; only revisit with multi-view input, or as a silhouette/geometry
guide UNDER a separate reference-conditioned texture pass. This means the
multi-facing goal realistically needs the paid Gemini channel.

**Side-experiment for rigid wreckage (worth it for Wrecked Machines):**
image→3D proxy (**TripoSR** local / open weights, or **Tripo3D** via fal), then
render the exact orthographic facings from the mesh — *geometrically perfect*
angle consistency by construction. Cost: mesh detail/style is below the source
art and needs a style-repaint pass. Rigid machines are the ideal case for it;
organic creatures are not. EXPERIMENTAL on the re-render fidelity.

Zero123++/SV3D/Wonder3D (novel-view diffusion): research-code only, no mature
hosted API found, tuned for studio photos not top-down sprites — skip for now.

## Remotion — animate stills (already working)

Reuse the working install at `D:\Luke\dev\Hearthview\` (Remotion 4.0.520, node
v22, WSL-safe `swangle` renderer, mp4 output). For desert/space backgrounds the
best look is **depth-map parallax + a looping heat-haze/dust overlay**
(Depth-Anything runs locally, no key); **Ken Burns pan/zoom** is the cheap
fallback. A small Remotion project in this repo pointing at our stills.

## What needs the owner (his account/billing) vs. what I can do now

- **His:** which channel key to add — Gemini (free tier, recommended), OpenAI
  (billing), or fal.ai (pay-per-call). This is a credentials/cost decision.
- **No key, I can do now:** install `rembg` (kills the chroma-key clumsiness
  today), and scaffold the Remotion animation project reusing Hearthview.

## First proof once a key is chosen

One Wrecked Machine: hero → 3 facings via the chosen channel + `rembg`, mirrored,
validated — this settles the one open UNCERTAIN (whether the model's
angle-consistency holds for top-down orthographic sprite framing) before we
commit the pipeline.

---

## Channel investment decision (2026-09-05, researched)

**The money-nuance, CONFIRMED:** neither $20 subscription helps our *scripted* pipeline.
- **ChatGPT Plus/Pro:** grant ZERO API credit/discount (OpenAI's own help center). Pro's
  image boost is the consumer chat app, not confirmed to raise Codex's image quota. The
  OpenAI image API (gpt-image-2, now with native transparency) is separate pay-per-call.
- **Google AI Pro ($20):** consumer-app-only, NO API access/credits. Nano Banana Pro is
  ONLY via the separate pay-per-call Gemini API (billing). So "buy $20 Gemini to test" buys
  nothing programmatic — a trap for our use.

**WINNER — local on the RTX 5080 (Flux.1-dev + ComfyUI + IP-Adapter/ControlNet + LayerDiffuse):**
the only option that is simultaneously programmatic, native-alpha (LayerDiffuse), and gives
EXPLICIT control over our two hard needs — IP-Adapter locks the Jawa reference across all
gods; ControlNet drives facings — at $0/image at volume. Flux.1-dev fits 16GB at FP8
(~32s/img; schnell ~7s). (Flux.2 is too big for 16GB — stay on Flux.1.) Reinforced by the
InstantMesh multi-view win, already proven local/free.

**Secondary:** Nano Banana Pro via pay-per-call API (~$0.05-0.10/img) for a few hero god
portraits where its consistency reputation is strongest — pay-per-call, NOT the $20 sub.
**Keep:** Codex channel for one-offs. **Skip:** paid ChatGPT tiers as a volume engine.

**Cheapest test this week ($0):** stand up ComfyUI + Flux.1-dev FP8 + LayerDiffuse +
IP-Adapter, run 10 Jawa-reference sprites across 4 facings, judge identity-lock before any spend.
