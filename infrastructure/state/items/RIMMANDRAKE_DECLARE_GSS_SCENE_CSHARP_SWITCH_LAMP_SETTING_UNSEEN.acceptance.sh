#!/bin/bash
# Acceptance test for RIMMANDRAKE_DECLARE_GSS_SCENE_CSHARP_SWITCH_LAMP_SETTING_UNSEEN. Exit 0 = pass.
out=$(python3 -W ignore src/RimMandrake/rimflow/build_match.py check --mod GimmeSomeSlack 2>/dev/null)
fail=0
for f in GimmeSomeSlackMod.cs Core/SwitchLight.cs Core/SwitchLampArt.cs GssSessionReset.cs; do
  if grep -q "^UNDECLARED  src/RimMandrake/GimmeSomeSlack/Source/$f" <<<"$out"; then echo "FAIL undeclared: $f"; fail=1; else echo "ok   declared or unchanged: $f"; fi
done
grep -q "^build match: read" <<<"$out" || { echo "FAIL: build_match printed no verdict line"; fail=1; }
exit $fail
