# LOCAL_IMAGEGEN_TRACK_PARKED_1 — local image generation is PARKED

## What was decided

**Owner ruling, 2026-09-05, relayed verbatim via HESTIA (owner away):**

> "Let's stop the local hardware graphics exploration for now if that's what
> keeps doing this."

It was. Nobody starts ComfyUI, downloads weights, or spawns a local-generation
agent until the owner says otherwise.

**Not covered by this ruling, and continuing normally:** the cloud channels —
Codex CLI `$imagegen` (the current workhorse) and the Gemini CLI + nanobanana
option. The block is specifically on *local compute*, not on making art.

## What was measured

**The kill.** BENCH's systemd scope at 13:09:53 hit usage 10,486,168 kB against a
10,485,760 kB limit with 2G swap full (failcnt 722,407). The kernel OOM-killed a
7.2 GB python child — the Flux model download/handling. The window died anyway,
despite `OOMPolicy=continue`, because `claude` starved in the full cgroup.
FOUNDRY took the same shape of kill the same day. A separate local step in the
god-art pipeline (`rembg_cut.py`, ONNX alpha cutout) was independently spiking to
7+ GB RSS with up to three concurrent, and returned exit 137 four times —
see `GOD_ART_LOCAL_HARDWARE_PARKED_1.md`.

**On disk, complete — nothing needs re-downloading if this is un-parked:**
`~/ComfyUI` 27G · `~/.venvs/comfy` 9.3G (torch 2.11+cu128, CUDA verified
working) · `~/.cache/huggingface` 2.3G. Base model
`flux1-schnell-fp8.safetensors` is COMPLETE at 17,236,328,572 bytes (it finished
at 14:58, *before* the ruling — the "~8GB partial" figure in the original relay
is superseded by this measurement). Custom nodes installed and loading:
`ComfyUI_IPAdapter_plus`, `comfyui_controlnet_aux`, `ComfyUI-layerdiffuse`.
Models present: `ipadapter/ip-adapter_sdxl_vit-h`,
`clip_vision/CLIP-ViT-H-14`, `controlnet/flux-canny-controlnet-v3`.

🔴 **Local generation was NEVER PROVEN.** A scripted test generation was never
executed. All ~39 GB of that install is unvalidated end-to-end — the
recommendation that chose it (`design/Jawa/worldbuilding/graphics_pipeline_recommendation.md`)
rested on research, not on one render this project produced.

**Stale, safe to delete for space:** a leftover `.incomplete` blob in the
ComfyUI checkpoints `.cache`.

## What would have to be true to revisit

All three, not any one:

1. **The owner lifts it in his own words.** This is his ruling; no agent
   un-parks it by inference, and a deadline passing is not a lift.
2. **Heavy ML runs in its OWN bounded systemd scope**, never inside a seat's
   10G cgroup — so a memory balloon kills only itself and cannot starve the
   agent window. This is the technical precondition the kill above establishes;
   resuming without it reproduces the kill.
3. **A single scripted test render succeeds before any batch.** The track was
   parked with zero proof it works at all; the first thing to buy on resume is
   that proof, not a 40-image run.

## Propagation (2026-09-11)

Every live directive that still told someone to run or extend local generation
was corrected:

- `design/Jawa/worldbuilding/graphics_pipeline_recommendation.md` — its "WINNER
  — local on the RTX 5080" call and its "Cheapest test this week ($0): stand up
  ComfyUI…" instruction were the actionable ones; both removed, park stated at
  the top of the doc and in the decision section, cloud channels named as the
  live ones.
- `infrastructure/state/items/MULTIVIEW_FACING_PIPELINE_1.md` (closed) — offered
  "redirect entirely to the 2D Flux/ComfyUI channel" as the owner's alternative;
  corrected, that alternative is parked.
- `GOD_ART_LOCAL_HARDWARE_PARKED_1.md` needed no change — it is already a
  parking record for the same ruling, and its resume steps are already gated on
  the owner lifting it.

## criteria
- [x] Ruling recorded with what was decided, what was measured, and the
      conditions for revisiting.
- [x] Live directives to run local generation neutralized.
- [ ] Open for the owner: whether `rembg_cut.py`'s local ONNX alpha cutout — a
      local-hardware step inside the *shipping* sprite pipeline, and a confirmed
      contributor to the OOM kills — is covered by this park or exempt as
      routine tooling. Not decided here; the tool is untouched.

## Ruling 2026-09-11 — rembg_cut.py is EXEMPT, capped

Owner: the ONNX alpha-cutout (`skills/generating-images/scripts/rembg_cut.py`)
is routine shipping tooling, NOT covered by the park — the Codex cloud channel
keeps its alpha path — but capped to **ONE concurrent run** so it can never
stack to an OOM again (it hit 7+ GB RSS × 3 concurrent in the 2026-09-05
kills). Cap enforcement is code, not prose: filed as
`REMBG_CONCURRENCY_CAP_1` (a flock-style guard in the script itself).
