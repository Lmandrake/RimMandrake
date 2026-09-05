# MULTIVIEW_FACING_PIPELINE_1 — pose-collision bug fixed and verified; UV-texture path needs an owner decision

Productionize the multi-view-mesh facing pipeline: InstantMesh (4 sprites -> volumetric
mesh) + meshfuse projection; local/free on the 5080; proven 2/3 facings, fix north/south
pose-collision (per-view az bias) + UV-texture path for sharpness (needs nvcc).

## 2026-09-05 (FOUNDRY, continuing a prior session's local GPU work)

**The north/south pose-collision, confirmed exactly.** The alignment gate (in
`Transient/meshfuse_multiview/meshfuse_multiview.py`) does a free 0-360° azimuth
search per view to maximize silhouette IoU against the fused InstantMesh mesh.
Instrumented (the script already logs per-view winners) and ran once before
touching anything:

```
GATE south : best IoU 0.855 @ az=270 el=35
GATE north : best IoU 0.852 @ az=270 el=35   <- identical pose to south
GATE east  : best IoU 0.919 @ az=150 el=22   <- 60° off its own nominal 90°
```

Not a near-miss — an EXACT pose collision. The test object (AutomatedSmelter, a
Wrecked Machines asset) is close to 180°-symmetric in silhouette, so IoU alone
can't distinguish front from back, and the free global search wanders far from
each view's own assigned camera position (east drifted 60°).

**Fix**: replaced the single global 15°-step 0-360° azimuth grid with a
per-view window centered on that view's own `BASE_AZ` (south=0, east=90,
north=180), ±40° in 5° steps. This keeps the alignment gate's actual intent — a
small per-view pose correction — while making a 180°-opposite collision
geometrically impossible (a ±40° window can't reach the opposite view's
position).

**Re-run and visually verified** (fusion+render only, ~100s, the InstantMesh
GPU pass wasn't re-run since the mesh itself doesn't need regenerating):

```
GATE south : best IoU 0.854 @ az=30.0  el=22
GATE east  : best IoU 0.826 @ az=130.0 el=15
GATE north : best IoU 0.772 @ az=210.0 el=22
```

South and north now land on genuinely distinct, ~180°-apart poses. Looked at
the new `Transient/meshfuse_multiview/contact_sheet.png` directly: the fused
south and north cells are now visibly different from each other (south keeps
its front door-slats/red-arc dome; north shows its own top-vent geometry and
side detail) — before the fix, the two fused cells were identical copies.
Fusion coverage rose from 68% to 78% of vertices (south/north no longer
competing for the same projection). One separate, smaller issue noted but NOT
in scope here: the final renders land at the found best-fit azimuth
(30°/130°/210°) rather than canonical 0/90/180, so they read as slightly
oblique rather than dead-on orthographic — pre-existing design choice, not
something this pass changed.

**UV-texture path / `nvcc` — confirmed a real, hard blocker, not attempted.**
`nvcc`/`cicc` (the CUDA compiler frontend) are absent everywhere on this
machine, including the GPU venv — `nvidia-cuda-nvcc-cu12` (the pip wheel
already installed) ships only `ptxas`, not the compiler frontend. Any
pytorch3d/nvdiffrast-based UV-texture rasterizer needs to JIT-compile a `.cu`
file at first use and cannot without it. Fixing this needs NVIDIA's full CUDA
Toolkit installed system-side (not a pip wheel) — a machine-level change, not
attempted this pass per its own scoping.

## criteria
- [x] North/south pose-collision root-caused with real instrumented numbers,
      not guessed.
- [x] Fix applied and re-verified by looking at the actual output, not just
      "it ran" — before/after comparison shown above.
- [ ] **UV-texture path for sharpness — blocked on installing the CUDA
      Toolkit on the shared machine.** Owner decision owed: worth the
      install, or is the current vertex-color bake (already working, just
      lower-res than a proper UV texture) good enough for v1 sprite output?
- [ ] Not yet "productionized" per the item's own word — this is still a
      one-object prototype (AutomatedSmelter only) living in `Transient/`,
      not a repeatable script other assets can run through. Left `doing`.
