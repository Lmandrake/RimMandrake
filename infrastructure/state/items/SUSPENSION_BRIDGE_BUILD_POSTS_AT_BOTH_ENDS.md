## spec
Child 2 of `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING`. The player-facing **Suspension bridge** at the surface, over dug
ground, with **no walk-under yet** (a deck is a wall from below until `SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD`).
Design: `design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md` §1.1-§1.3, §2, §4; `design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §2, §3 (dug rows), §6, §7, §9.
- Building, not floor terrain (Q1). Player-facing name "Suspension bridge" everywhere (label, settings section, letter,
  readout); never "span" or bare "bridge".
- Custom `Designator_Build` subclass: drag like a wall, 1-3 wide, must start and end on solid surface ground, every
  cell between over a dug hole ≥ 0.5 m; refusals with reasons (`DesignateMultiCell`, `Designator.cs:261`).
- Anchors (1×1) at both ends, built first; deck cells built from the anchors inward; span record in a map component.
- Tiers rope/timber/steel/heavy: length anchor-to-anchor 8/6/10/14, load 150/600/2,000/8,000 kg (playtest starting
  points); **towers** on the hole floor act as mid anchors (built by a pawn standing on the floor).
- Load per span shown in the inspect pane ("Load 640 / 600 kg"); over rating: sag warning and creak at 90%, then the
  **whole span** collapses. HP 0 in any cell also drops the whole span; anchor or tower lost → swing-down from the lost end.
- Collapse: pawns on it descend (existing descent event, fall by metres); items drop; buildings on it destroyed.
  (Hit on pawns below is the underpass item's: nobody is under a deck until then.)
- Railings: per-bridge on/off gizmo (orders work, +50% cost); railed edges never drop anyone; open edges: stagger/blast
  25% and slime slip 10% fall chance, and a deliberate one-way drop. **Railings give no cover.**
- Affordance-lending patch (timber Light; steel Light/Medium; heavy Light/Medium/Heavy). Dig/fill-in refused under a deck.
- Vanilla `Bridge`/`HeavyBridge` refused on any cell the excavation component owns (Q6), message "Use a suspension
  bridge over dug ground".
- Mod Settings rows of `design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §9 that this item makes real; readout line (P8 form) "Suspension bridge (steel) · load …".
- Functional script `src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py` ships with it (debug_process).
Dependencies: `SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT`. Lands on whatever water model is live (P3
`WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` / P4 `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`); no hard gate — the
collapse-into-water row re-runs after P3. Art: placeholder textures until `SUSPENSION_ART_RESKIN_HE_SEES_FIRST`.
ESTIMATE 4 to 5 agent-days + 0.5 day live on the minimal list.

## verify
- L1: selftests on the drag validator (ends on ground, middle all dug, length per tier, width 1-3) and the load sum.
- L2: drag a 6-cell timber bridge across a dry 4 m trench: 2 anchors + 6 deck things exist; a colonist path from one
  bank to the other uses the deck (state read of the path cells).
- L2: drag a 7-cell timber bridge: designator refuses with the length reason; nothing placed.
- L2: load a timber span to 640 kg: inspect string reads "640 / 600"; within the collapse window every deck thing of
  that span is gone and each pawn that was on it is on the trench floor with fall injuries (hediff read).
- L2: deconstruct one anchor: the deck cells disappear in order from that end (tick stamps ascending).
- L2: railings on → a staggered pawn on an edge cell stays on the deck over 20 trials; railings off → some fall.
- L2: a vanilla `Bridge` blueprint on a dug cell is refused (AcceptanceReport false, reason text).
- L2: all settings off → no build button; an existing bridge never breaks from weight.
