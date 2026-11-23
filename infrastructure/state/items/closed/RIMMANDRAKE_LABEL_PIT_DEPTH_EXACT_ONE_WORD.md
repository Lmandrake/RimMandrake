---
state: ready
needs: offline
---

# RIMMANDRAKE_LABEL_PIT_DEPTH_EXACT_ONE_WORD

## spec

Owner live look 2026-11-12 ~18:00 PST (words: D:\ClaudeWork\rimmandrake\conductor\godmode_liquid_20261112\OWNER_WORDS.md):
"Why is there a label of "Canal 1m" at the central northern wall of the pit and "Pit 2m or more" elsewhere? It's supposed
to show the precise depth no matter what, and Pit and Canal are totally interchangeable. Something is very wrong here (fix)."

Binding rulings: a pit is a superdeep cell, not a building; water and depth are true height, no steps (Conductor log 2026-11-12).

Root cause (read 2026-11-12): RM_ExcavationDepth.TerrainFor maps the dug depth to one of FOUR TerrainDefs with baked labels
("canal (0.5 m)", "canal (1 m)", "canal (1.5 m)", "pit (2 m or more)"; every depth past 4 notches shares RM_Channel_Superdeep),
and RM_Patch_MouseoverDepth puts terrain.LabelCap first on the readout line. The liquid-in-pit terrains carry the same
bucket labels ("deep water (2 m or more)" and one per fluid). The north-wall centre cell is the 1 m notch, so it drew the
RM_Channel_Mid label.

Fix: one word, "pit", for a dug square everywhere a player reads it (terrain labels/descriptions, readout, designators, work
givers, job reports, messages); the readout's first part on a dug square is built by RM_Volume.PitLabel from the engine's
true numbers (depthGrid notches, WaterDlAt decilitres, FluidAt kind): "Pit, 2.5 m deep" dry, "Pit, 1.5 m water in 4.0 m"
wet. Exact to 0.1 m. No "or more" in any FlowWorks label. defNames unchanged (saves).

## acceptance test

SelfTest cases PitLabel_* (FlowWorks/Source/SelfTest/PitLabelChecks.cs, run by
`python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only PitLabel_*`):
- every depth 0.5 m .. 125 m (1..250 notches) dry: label == "Pit, <d> m deep" with d to one decimal;
- every depth with 1 notch of water and half-full: "Pit, <w> m <kind> in <d> m";
- the 1 m notch (ramp/north-wall cell) reads "Pit, 1.0 m deep", not "canal";
- every dug/liquid TerrainDef label in Defs/ carries no "or more" and no "canal";
- mutant: a planted "or more" label is refused by the same checker.
Must fail on the base (labels carry "or more"/"canal").
