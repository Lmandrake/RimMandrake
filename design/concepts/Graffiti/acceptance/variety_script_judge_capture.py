# Acceptance test for RIMMANDRAKE_SCRIPT_GRAFFITI_VARIETY_JUDGE_CAPTURE_TINTS_UNSEEN: validation.py's spree_variety
# captures the lanes for a judge (component variety_judge_names_kinds) and calibrates that judge on a recolour set
# (component control_recolour_set_judged_one), and no longer gates on a def count (variety_three_defs).
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r"\ndef spree_variety\(t\):(.*?)\n(?:@|def )", src, re.S)
body = m.group(1) if m else ""
checks = [bool(m), '"variety_judge_names_kinds"' in body, '"control_recolour_set_judged_one"' in body,
          '"variety_three_defs"' not in body]
print("PASS" if all(checks) else "FAIL %s" % checks); sys.exit(0 if all(checks) else 1)
