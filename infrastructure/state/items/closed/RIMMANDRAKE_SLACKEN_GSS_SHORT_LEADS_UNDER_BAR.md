## spec
found-by: T_CORD_GEOMETRY_OFFLINE (`src/RimMandrake/GimmeSomeSlack/Source/SelfTest/CordGeometryChecks.cs`), Maturation Stage 3 of
GimmeSomeSlack 0.1.0 (detached run RIMMANDRAKE_ADVANCE_GIMMESOMESLACK_OFFLINE_BESIDE_THE_PILOT, 2026-11-14). It reads the leaves
`cords_lie_slack` and `no_unforced_sharp_turn` as their oracle text says (per strand: drawn length at least 1.4 times its chord; an
excursion of a cell or more on chords over 4 cells; CordShapeAudit's bend tally reads 0 unforced), on the production CordBuilder
over the 7 oracle scenes.

Reading 2026-11-14 [measured]: 76 strands, ratio min 1.02, 25 under 1.4 (all short leads, chord 2.1 to 3.1 cells: nodal
`junction:5,7|stub_rock:3,7` 1.07, `junction:5,7|junction:5,10` 1.09, downed `junction:5,5|source:3,5` 1.15), 1 of 12 long strands
flat, 7 unforced bends.

Decide which reading is true first:
- (a) MOD: the builder lays short leads near-taut and makes unforced hooks (fix in CordBuilder/CordPlanner; the unforced half is
  likely the defect of RIMMANDRAKE_UNBEND_GSS_LEAD_AT_JUNCTION_BATTERY_TWICE, seen live on the junction-battery lead).
- (b) CRITERION: the 1.4 ratio was never meant for a 2-cell lead. Then the neutral fixer (never the builder) repairs the
  criterion and the owner sees the change; it is a bar edit, so not inside 0.1.0 without him.

The builder must not loosen the test. The check runs only under `--geometry` so T_CORE stays a green gate meanwhile.

Acceptance test: `python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --geometry` exits 0 (its geometry line reads taut 0,
flat 0, unforced bends 0). Watched fail 2026-11-14 on 685c9a1c65 plus this run: 3 geometry FAILs, 4510/4513.
