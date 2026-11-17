# Acceptance test for RIMMANDRAKE_SCRIPT_GRAFFITI_SOAK_PER_COLONIST_SUM_HID_ONE: validation.py's scene_lived_in_soak
# asserts the trait mix (site component casts a sensitive and a clean-freak colonist), reads each colonist's negative
# graffiti mood for its SHAPE (soak_each_colonist_returns_to_zero: held on most days of weeks two and three fails), not
# its size against the forced control (soak_each_colonist_below_control was struck by coverage judge
# rm-coverage-judge-1794940039: a capped control lets a small daily debuff pass), requires an unforced story
# (soak_unforced_story_happens), and the colony-sum component soak_mood_sum_stays_small is gone.
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r"\ndef scene_lived_in_soak\(t\):(.*?)\n(?:@|def )", src, re.S)
body = m.group(1) if m else ""
checks = [bool(m), '"soak_each_colonist_returns_to_zero"' in body, '"soak_each_colonist_below_control"' not in body,
          '"soak_unforced_story_happens"' in body, '"soak_mood_sum_stays_small"' not in body,
          "sensitive" in body.lower() and "neurotic" in body.lower()]
print("PASS" if all(checks) else "FAIL %s" % checks); sys.exit(0 if all(checks) else 1)
