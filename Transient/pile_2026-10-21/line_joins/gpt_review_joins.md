Use a shared ground-plane centreline for every connection. Targets below are **visible widths**, excluding transparent padding. At drawSize 1, multiply cells by 176 or 256 for the two texture sizes.

| Part | Target girth | 176 px/cell | 256 px/cell |
|---|---:|---:|---:|
| Rigid pipe | 0.12–0.14 cell | 21–25 px | 31–36 px |
| Flexible hose | 0.08–0.10 cell | 14–18 px | 20–26 px |
| Ordinary coupling | 0.15–0.18 cell | 26–32 px | 38–46 px |

Use dark-brown/charcoal outlines around **0.006–0.009 cell**: approximately 1–1.5 px at 176, 1.5–2.3 px at 256. Avoid thick black double outlines at joins.

1. **Pipe–pipe runs and end caps**

   **WRONG:** The existing 0.23–0.29-cell pipe is roughly 40–48% of a pawn’s body width and over twice vanilla conduit width. Repeated wide collars make it read as heavy industrial ducting. The end in F is an oversized projecting dome; C has an ambiguous continuation beyond the metal termination.

   **FIX:** Reduce the entire pipe assembly to the target above, including collars. Keep the run’s transverse axis at **0 offset from cell centre**; adjoining tile endpoints meet at **±0.5 cell longitudinally**. Use a shallow elliptical terminal plate, no wider than 0.16 cell, projecting only 0.02–0.03 cell. Render caps only at exposed ends. Show a narrow lit upper edge and restrained south-side shadow.

2. **Pipe-to-hose handoff: C and D**

   **WRONG:** The brown stubs look like torn cloth emerging from metal. In C, the separated brass nozzle and binding create a visibly disconnected handoff. In D, the stub appears to enter the pump without a fitting. Cloth is wider than the rigid pipe.

   **FIX:** Replace every stub with one compact metal reducer, **0.16–0.18 cell wide × 0.12–0.16 cell long**. Centre its bore on the pipe axis, with the fitting midpoint at the shared cell boundary: **±0.5 cell from either adjoining cell centre**. Insert the hose into it with 0.02-cell concealed overlap. Remove the gap and redundant facing nozzle. Bindings should remain below 0.14-cell width.

3. **Hose-to-reel**

   **WRONG:** D/G show a loose hose endpoint beside an isolated reel, without a convincing continuous route. The reel’s side elevation, small visible silhouette and dark square make it resemble an inventory object pasted onto the ground. The 2.8-cell drawing also conflicts with its 2×2 placement.

   **FIX:** Redraw the reel with a visible top and short south face; remove the baked square background. For the 2×2 building, target **1.5–1.8 cells visible width**. Anchor the base footprint at **(0,0)** relative to building centre. Put the hose exit at a defined ground-level port, for example **(−0.75, 0) cell** for a west exit. Route a continuous 0.08–0.10-cell hose into that port; match wound-hose thickness to it.

4. **Reel-to-pump / pump on pipe**

   **WRONG:** The pump’s broad flanges overwhelm the pipe, while the nearby reel and cloth stub fail to establish which port carries liquid. At normal zoom, dense bolts and rings merge into a dark lump.

   **FIX:** Keep the pump visibly substantial: **0.65–0.75 cell body width**—114–132 / 166–192 px. Anchor the liquid manifold at **(0,0)**, with east/west port mouths at **(±0.5,0)**. Taper ports to 0.16–0.18-cell couplings. Connect the reel through an explicit continuous hose and adapter. Use one clear housing, top highlight and short south face; simplify bolts.

5. **Sprinkler head on pipe**

   **WRONG:** The dome/stem silhouette reads as standing beside or above the pipe; its visual centre does not communicate the actual pipe connection. The oversized head compounds the pipe’s bulk.

   **FIX:** Anchor the **stem base**, not the dome or image bounding box, at **(0,0)** on the pipe centreline. Use a **0.20–0.24-cell dome**—35–42 / 51–61 px—and a 0.06–0.08-cell stem. The dome may project **0.06–0.10 cell north** through height; keep the base fixed. Add a small saddle collar so the junction remains visible.

6. **Liquid tap and hose mouth**

   **WRONG:** F presents three disconnected objects. The tall tap and bucket use strong side-elevation cues, while the black hose mouth reads as a large open tunnel.

   **FIX:** Give the tap a compact top-visible valve assembly. Anchor its ground manifold at **(0,0)** and its hose port at **(+0.25,0)**, rotating together. Use a 0.16–0.18-cell threaded fitting and insert the target-width hose directly. Reserve open mouths for genuinely disconnected hoses; use a shallow dark ellipse matching the hose bore. Remove or shrink the bucket.

7. **Tank-to-pipe**

   **WRONG:** A’s pipe visually emerges from behind the tank’s broad support/base without a clear outlet. Its thickness competes with the tank’s structural bands.

   **FIX:** Preserve the tank’s volume, but expose a short outlet neck and 0.18-cell coupling. Anchor the outlet bore on the adjoining pipe centreline: **0 transverse offset**, at the tank’s actual connection boundary. Overlap pipe beneath the fitting by 0.02 cell. Keep supports clear of the outlet silhouette.

Priority order:

1. Halve rigid-pipe girth and thin hoses.
2. Unify connection anchors and eliminate gaps/stubs.
3. Redraw and resize reels.
4. Replace bulbous caps and oversized fittings.
5. Correct sprinkler/tap perspective and simplify small details.