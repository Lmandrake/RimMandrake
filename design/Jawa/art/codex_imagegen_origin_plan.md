# Claude Code Plan: Use Codex `$imagegen` for RimWorld Graphics

> ⚠️ **SUPERSEDED, 2026-08-12. Kept as the origin record — do not follow it.**
>
> This plan started the work and its *strategy* was right: Claude as
> controller, Codex as image worker, deterministic tools for anything
> measurable. Several of its **mechanical claims were wrong**, and following
> them costs time:
>
> - `codex` is **not on `PATH`**. It lives inside the desktop app under a
>   content-hash directory that moves on every update.
> - `$imagegen` is a **system skill, not a plugin** — it will never show up in
>   `codex plugin list`.
> - The plan assumes transparency can simply be requested. **It cannot.** This
>   install authenticates as `chatgpt` with no `OPENAI_API_KEY`, so both the
>   deterministic CLI and true native transparency are unavailable. Alpha comes
>   only from generating on a chroma key and removing it locally.
> - Generation size is constrained (multiples of 16, ≥655,360 px), which rules
>   out generating a RimWorld facing at its native size.
>
> **The verified, working version of all of this is
> `file:///D:/Luke/dev/Rimworld/skills/generating-images/` and its two
> companions.** Facts live in `references/codex-contract.md`.

## Purpose

Use **Claude Code as the controller** and **Codex as the image-generation worker**.

Target workflow:

- Claude analyzes the task and any existing source images.
- Claude calls `codex exec` with `$imagegen` for image generation or editing.
- Codex writes output files locally.
- Claude inspects the output image.
- Claude iterates if needed.
- Claude uses deterministic tools when exact sizing, alpha, layout, or rotation consistency matters.

---

## Core Rule

For **raster image generation** and **generative image editing**, use **Codex CLI** rather than trying to do the visual synthesis directly.

Use:

```bash
codex exec --sandbox workspace-write '...'
```

When editing an existing image, attach it with:

```bash
-i <image_path>
```

Explicitly tell Codex to use **`$imagegen`** and to **save the result to a specific file path**.

---

## First Test

Run this simple test first:

```bash
codex exec --sandbox workspace-write 'Use $imagegen to create a rusty ancient science-fiction machine on a transparent background. Save the final image as test-machine.png.'
```

Then inspect `test-machine.png`.

If successful, proceed to the RimWorld workflow below.

---

## RimWorld Asset Workflow

### 1. Inspect source assets first

Before generating or editing:

- read image dimensions;
- detect whether alpha is present;
- inspect canvas size;
- inspect number of frames / rotations if applicable;
- inspect whether the asset is a sprite, sprite sheet, icon, object render, or UI asset.

Use deterministic tools where possible to measure and validate these properties.

### 2. Preserve hard constraints

When calling Codex / `$imagegen`, explicitly state:

- preserve canvas size unless instructed otherwise;
- preserve transparency / alpha if required;
- preserve the overall object bounds;
- do not let smoke, wires, hoses, debris, or effects extend outside the asset bounds unless explicitly allowed;
- if multiple rotations/views exist, apply equivalent changes consistently across all views.

### 3. Use generation only for what generation is good at

Use `$imagegen` for:

- material changes;
- rust, corrosion, grime, patchwork repair;
- smoke, sparks, damage, kludged machinery;
- stylistic transformation;
- adding visual detail.

Use deterministic local tools for:

- resizing;
- padding;
- cropping;
- alpha cleanup;
- splitting or assembling sprite sheets;
- duplicating layout structure;
- rotating or arranging already-created views;
- verifying output dimensions and file format.

### 4. Iterate visually

After each output:

- inspect the generated image;
- compare against constraints;
- identify violations;
- send a corrective edit pass if needed.

Do **not** assume first-pass output is correct.

---

## Prompting Rules for Codex

When instructing Codex to call `$imagegen`, always specify:

1. **What image is being edited or generated**
2. **What must change**
3. **What must remain unchanged**
4. **Exact output filename**
5. **Whether transparency must be preserved**
6. **Whether geometry / silhouette / bounds must be preserved**
7. **Any multi-view consistency requirements**

Good prompt structure:

```text
Use $imagegen to edit the attached image.
Make all exposed metal ancient, rusted, and heavily corroded.
Preserve the object silhouette, canvas size, and transparency.
Do not let any hoses, smoke, or debris extend outside the object's existing bounds.
Keep the conveyor belts visually clear and readable.
Save the result as machine-rusted.png.
```

---

## Example: Edit Existing RimWorld Asset

```bash
codex exec --sandbox workspace-write \
  -i "./source/machine.png" \
  'Use $imagegen to edit the attached image. Convert the machine into an ancient, damaged, heavily rusted industrial device. Preserve the overall silhouette, canvas size, and transparent background. Keep all visual additions within the object bounds. Save the result as ./infrastructure/output/machine_rusted.png.'
```

---

## Example: Repair / Upgrade Pass

```bash
codex exec --sandbox workspace-write \
  -i "./infrastructure/output/machine_rusted.png" \
  'Use $imagegen to edit the attached image. Partially repair the machine so it appears functional but still ancient and improvised. Patch holes with mismatched metal, remove excessive support clutter, and keep a few small smoke leaks from cracks. Preserve the canvas size, object bounds, and transparency. Save the result as ./infrastructure/output/machine_repaired.png.'
```

---

## Special Rules for Multi-View / Rotation Assets

If the asset includes several views or 90-degree rotations:

- treat them as the **same object** seen from different directions;
- changes must be equivalent across all views;
- orientation-specific features must rotate correctly;
- do not introduce view-specific clutter that breaks consistency.

If needed:

1. split the sheet into separate view images;
2. edit them carefully and consistently;
3. reassemble them deterministically;
4. verify final layout matches the original sheet format.

---

## Acceptance Checks

After any generation/edit:

- confirm file exists;
- confirm expected filename;
- confirm dimensions match required size;
- confirm transparency exists if required;
- confirm object stays within bounds;
- confirm no accidental cropping;
- confirm no unwanted background;
- confirm repeated views / rotations are consistent;
- confirm the asset is usable in RimWorld context.

If any check fails, repair the asset locally or send a corrective `$imagegen` pass.

---

## Default Working Policy

When asked to create or modify RimWorld graphics:

1. inspect the input asset(s);
2. determine exact technical constraints;
3. call `codex exec --sandbox workspace-write`;
4. require `$imagegen`;
5. save output to a clear local filename;
6. inspect the result;
7. iterate until acceptable;
8. use deterministic tools to enforce final correctness.

---

## Operational Preference

Prefer this chain:

```text
Claude Code -> codex exec -> $imagegen -> output PNG -> Claude inspection -> iterate
```

This is the default image workflow unless the task is purely deterministic and can be completed without generative editing.

---

## Short Instruction to Follow Automatically

For raster image work, use Codex CLI with `$imagegen` as the image worker. Inspect source images first, preserve hard technical constraints, save outputs locally, inspect the results visually, and iterate as needed. Use deterministic tools for sizing, alpha, layout, splitting/assembling sheets, and validation. Use `$imagegen` for visual synthesis and stylistic transformation.