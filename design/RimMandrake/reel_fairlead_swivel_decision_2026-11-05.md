# Hose reel: payout guide (fairlead) and supply swivel — decided not needed (2026-11-05)

Item `REEL_FAIRLEAD_DECIDE_AFTER_THE_WALK`. This is the rest of fix 6 in the 2026-10-16 Codex art review
(`git show b5ae71e2a4:Transient/river_hose_art_review_2026-10-16/REVIEW.md`, line 22). Fix 6 asked for:
*"shrink it …, keep the drum visible, and add a tangential payout guide (about 16x10 px fairlead) …
Plus a visible supply swivel on the pump-facing side."* The size and drum part was done by the camera
redraw (`REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON`) and the firehose drum (`HOSE_REEL_REDRAW_FIREHOSE_ON_THE_DRUM`).
The Conductor's triage on 2026-10-29 delegated what remained as an art/design call (delegation_policy §1): a judge decides,
and the item is dropped if no addition is needed.

**Judge:** a fresh Opus `rm-judge` that did not make the art (delegated: art), 2026-11-05.
It looked at a contact sheet of every texture listed below and at the live walkthrough capture
`D:\ClaudeWork\rimmandrake\scratch\br1e_caps\s5_reels_13-16_v.png`, which shows three deployed reels.

VERDICT fairlead: not_needed
VERDICT swivel: not_needed

- **Fairlead (confidence 0.8).** In the live capture, the hose on every reel leaves from a coupling stub
  on the low elbow pipe at the base. It reads as a plumbed outlet, not a dangling coupling. A 16x10 px
  guide shrinks to about 8x5 px at normal zoom (a 2x2 building is about 128 px on screen), which is
  too small to read. It would also move the visible exit away from the point where the code draws the
  hose (`ReelIntakeGeometry`), so the C# would have to change with it.
- **Supply swivel (confidence 0.65).** Every side view already shows the path through the hub: an elbow
  pipe at hub height runs down to a coupling stub, and the Modern look adds a valve handwheel on the
  hub. The north and south views show a hub boss and a feed pipe. The pump joins the reel by being next
  to it in the building network, not by a drawn hose, so a drawn swivel would show nothing the player
  uses. The judge's one caveat: the same stub serves both supply and payout, which only a real plumber
  would notice.

No redraw follows, so no follow-up item is filed for it. The kept reel art stays as installed.

**Side finding (filed):** `REEL_TAIL_VERIFY_RED_DRUM_BEIGE_TAIL`. In the capture, a reel with a red
drum hose had a beige paid-out hose. The capture is from 2026-10-23, before the firehose was deployed,
so this is unproven until someone checks the current Modern hose atlas.

## Textures judged (all present at this commit)

The base (scrap, rust-and-brass) look was judged in the live capture, where it is the copper reel with a tan hose. Its six textures are built the same way: an elbow pipe from the hub runs down to a brass coupling stub.

src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Reel_PumpHookup.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Reel_PumpHookup_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Reel_PumpHookup_south.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Reel_Deployed.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Reel_Deployed_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Reel_Deployed_south.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Industrial/Reel_PumpHookup.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Industrial/Reel_PumpHookup_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Industrial/Reel_PumpHookup_south.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Industrial/Reel_Deployed.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Industrial/Reel_Deployed_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Industrial/Reel_Deployed_south.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_PumpHookup.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_PumpHookup_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_PumpHookup_south.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_Deployed.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_Deployed_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_Deployed_south.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Futuristic/Reel_PumpHookup.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Futuristic/Reel_PumpHookup_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Futuristic/Reel_PumpHookup_south.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Futuristic/Reel_Deployed.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Futuristic/Reel_Deployed_north.png
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/Styles/Futuristic/Reel_Deployed_south.png
