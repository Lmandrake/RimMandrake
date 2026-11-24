## refs
file: src/RimMandrake/Utils/stage_review.py
file: design/specs/2026-11-23-stage-review-midday/accept.py

## spec
`stage_review.py` is the helper of the skill `rimworld-live-review`. Three of its flags do less, or more, than they say:

- `--daylight` steps seven chunks of 2000 ticks from any hour and reads no hour. A start at 18 h shoots at 23.6 h. Read the
  hour from `jawa/glow_at` (pass any `cells`) and end between 10 h and 14 h.
- `--clear chunks` destroys category Item over the whole rect. It must destroy chunks only
  (`src/RimMandrake/Utils/rimbench/clear_chunks.py` shows how).
- `--two-pass` sets no weather before its `_clear` shot, so that shot can be in rain. It must set clear weather first.

The clock: a step over 30,000 ticks needs a safe colony (`design/RimMandrake/debug_process.md` § "A long clock advance").
`jawa/time_set_ticks` is refused beside a free colonist without `timeException=true`. Choose one and say why.

## verify
Acceptance test: `python3 design/specs/2026-11-23-stage-review-midday/accept.py` prints PASS, exit 0. On 78750f480b it printed
FAIL for 7 of 8 start hours and for `--clear chunks`, exit 1. It does not cover `--two-pass`: add that case. Then one live
run on a small list: the shot's hour reads 10 to 14.

## criteria
- The three flags do what the helper's `--help` and the skill say.
- The skill's §1 and §5 sentences about these faults are corrected in the same change.
