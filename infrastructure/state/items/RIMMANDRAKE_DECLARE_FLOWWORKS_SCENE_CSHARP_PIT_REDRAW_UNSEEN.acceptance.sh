#!/bin/bash
# Acceptance test for RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN. Exit 0 = pass.
out=$(python3 -W ignore src/RimMandrake/rimflow/build_match.py check --mod FlowWorks 2>/dev/null)
fail=0
for f in Superdeep/RM_ExcavationWalls.cs Superdeep/RM_UnderLiquid.cs RM_MapComponent_Excavation.cs; do
  if grep -q "^UNDECLARED  src/RimMandrake/FlowWorks/Source/$f" <<<"$out"; then echo "FAIL undeclared: $f"; fail=1; else echo "ok   declared or unchanged: $f"; fi
done
exit $fail
