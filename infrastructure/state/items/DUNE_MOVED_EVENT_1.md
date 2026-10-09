# DUNE_MOVED_EVENT_1 — SS-5: MovingDunes announces "this sand actually moved"; singing dunes and the quake warning listen to it instead of guessing from a requested move

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row SS-5 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Add a change event in MovingDunes raised from RM_DuneKernel.SetDepthHysteretic only when the depth really changed; Stillsand RM_SandSwimRemainder Patch_SlipFace stops firing on the request. Removes false singing; the track-eraser hook (DUNE_TRACK_ERASE_ACCUMULATE_1 / FOOTPRINT_TRACK_GRID_1) subscribes later, not here. No event exists in MovingDunes/Source today.

The row:

| SS-5 | Have MovingDunes announce "this sand actually moved" once, and let the singing dunes / quake warning listen to that, instead of guessing from a requested move the dune engine may then decline. Removes false singing and gives the track eraser its hook for free. | MovingDunes event | M | low | MovingDunes, Stillsand | `RM_SandSwimRemainder.cs:245` `Patch_SlipFace.Prefix` fires on `target` before `RM_DuneKernel.SetDepthHysteretic` (MovingDunes `Kernel/RM_DuneKernel.cs:116`) decides; no change event exists in MovingDunes/Source. Track half is DUNE_TRACK_ERASE_ACCUMULATE_1 / FOOTPRINT_TRACK_GRID_1 (live) — this row is the shared hook + singing fix only. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: MovingDunes and Stillsand build; a selftest shows a declined move raises no event and an accepted one raises exactly one; toggle in Mod Settings.
