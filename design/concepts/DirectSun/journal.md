# DirectSun: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

DirectSun entered the pipeline at intake on the owner's card of 2026-11-27 9:25 PM PST: "I'd like it to remain as part
of Direct Sun, as an addition to the obvious shade induced by hard walls. We should also add shadows cast by
mountain-covered squares that are much larger than short walls would, so you get a feel for said mountain on the map
depending on the sun angle. Very cool! So Tree Shade + Direct sun + mountain shade should all receive this design
attention now to bring it to a full modern design with tests, etc." (item
RIMMANDRAKE_ADMIT_DIRECT_SUN_WITH_TREE_AND_MOUNTAIN_SHADE). His words ask for design attention; they start no build.

## The mod as it stands

- **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-27 10:12 PM PST).
- **Stage now:** Stage 1, the Designer, since 2026-11-27 10:12 PM PST (`version/stage_record.json`).
- **Mod:** no shipping folder of its own. The code is in `src/RimMandrake/CreatureBehaviors` (a member of
  `mandrake.rm.biomes`, namespace `RimMandrake.CreatureBehaviors`); the shade-gear defs in
  `src/RimMandrake/EnvironmentalHazards`; the air-heat defs in TheForge, TerminalBiomes and Greentide.
- **Design Version:** 0.1.0, open (`version/VERSION.json`). No locked design. The proposed vision and bars:
  `admission_proposal.md` (a proposal for the Designer and the owner, not a lock).
- **Open question he named (2026-11-26):** merged into Baroque Biomes, or stand-alone. Recorded, not answered.
- **Design input:** `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`,
  `design/RimMandrake/tree_shade_model_2026-10-19.md`, `design/RimMandrake/sun_and_shade_modularity_2026-10-19.md`,
  `design/RimMandrake/shadecraft_lessons_design_2026-10-31.md` (written before the pipeline; input, not settled).
- **Designer item:** RIMMANDRAKE_ADMIT_DIRECT_SUN_WITH_TREE_AND_MOUNTAIN_SHADE.
- **Next:** the Conductor brings the questions to the owner; then the move from intake to the Designer.

## History

### 2026-11-27 9:57 PM PST, admitted to ideas waiting (Intake) (by BENCH)

- 2026-11-27, BENCH: seeded at intake. Measured the same day: 24 core C# files (5812 lines) in Creature Behaviors;
  `selftest_sun_heat.py` 65/65, `selftest_direct_sun.py`, `selftest_tree_crowns.py` and `selftest_shade_lessons.py`
  ALL PASS, `selftest_planet_fixed_sun.py` 72/72; mountain shade has no design and no code (rock casts the lee of a
  wall, height 1). Detail: `admission_proposal.md` §What exists.

### 2026-11-27 10:12 PM PST, stage change: ideas waiting (Intake) to Designer (Stage 1) (by CONDUCTOR)

- Why: his order of 9:25 PM PST 2026-11-27: design attention now for Direct Sun with tree shade and mountain shade; admission page design/concepts/DirectSun/admission_proposal.md (bda9d44fc2); hand act folded into RIMMANDRAKE_BUILD_DESIGN_ONLY_SWITCH_DESIGNER_STOPS_WITH_BUILDS
- Checks passed: order, by, version, hold, intake_closed.
- Was, "Stage now": - **Stage now:** Intake, ideas waiting, since 2026-11-27 9:57 PM PST.
- Was, "Waiting on": - **Waiting on:** the Conductor, who reads `admission_proposal.md` and brings its two questions to the owner; its readiness list (none written yet) and its switch, which is OFF (`./pipe off DirectSun`).
- Record: `version/stage_record.json`.
