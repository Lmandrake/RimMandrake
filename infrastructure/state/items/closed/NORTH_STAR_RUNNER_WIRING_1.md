# NORTH_STAR_RUNNER_WIRING_1 — make the north star actually bind

Filed by BENCH 2026-09-15. Design: `design/RimMandrake/north_star_validation_spec.md`
(read it first — it carries the owner's four rulings of that date and the measured
findings behind them).

## Already built and tested (commit `0e03d1bed`) — do not rebuild

- `modcheck/northstar.py` — parses a walk's `## north star`, returns effective
  state, and gates on a content hash so any edit reverts VALIDATED to DRAFT.
  `bar_for(path)` is the one function a floor check should call: it returns the
  validated ids, or nothing at all for a DRAFT.
- `modcheck/judge.py` — `judge_run(summary, must_show_text, runner=None)` grades
  screenshots against claimed must-show ids via `claude -p`.
  `visual_all_green(results)` is the verdict helper. UNJUDGEABLE is not a pass.
- `floor.uncovered_shows()` and `floor.orphan_shows()`.
- `shows=` on `component()` — optional, so all 18 existing scripts are unaffected.
- `modcheck/selftest_northstar.py` — 22 checks, offline, uses the judge's
  `runner=` injection so it never shells out.

## spec — what is actually owed

1. **`runner.py` consults the visual half.** Today `all_green` (runner.py:205)
   is computed from state verdicts alone. It must additionally require
   `judge.visual_all_green()` over the run's judged results, and the run must
   call `judge.judge_run()` once at the end, after evidence capture.
2. **The visual floor is checked per mod, before the run.** Resolve the mod's
   walk with `northstar.find_walk`, take `northstar.bar_for` as the binding ids,
   and REFUSE the mod when `floor.uncovered_shows()` is non-empty — the same way
   an uncovered settings toggle is treated. Report `floor.orphan_shows()` as a
   lint error naming the ids.
3. **`modcheck validate <mod>`** — a CLI verb calling
   `northstar.record_validation`, owner-authorised (`--owner-said`). It must
   print the must-show lines it is about to bind and require his words, exactly
   as `code_review_status.py mark-clean` refuses to bless silently.
4. **The GREEN definition of spec §5**, including the once-per-mod owner review
   before a mod's FIRST green. Record that review in `modcheck_status.json`
   beside the existing hash — a boolean is not enough; store which run id he
   reviewed.
5. **A hook** that refuses to record GREEN for a mod whose checklist is DRAFT.
   Per the charter, an enforced rule is a hook, not a paragraph.
6. **`must_show_text`** — the judge needs `{id: prose}`, not just ids.
   `northstar.parse` currently returns ids only; add the prose alongside them
   (the regex already captures the line, so this is small).

## verify

```
PROVE   a mod with a VALIDATED checklist whose lines no component claims is
        REFUSED, and a mod whose judge returns any NO or UNJUDGEABLE is not GREEN
EXPECT  selftest_northstar.py still passes, plus new runner-level checks driving
        a fake summary through the real floor + judge with an injected runner
LIES    a green run against a DRAFT checklist; UNJUDGEABLE counted as a pass;
        a mod with no north star section behaving any differently than it does
        today (enforcement is PER MOD, as he validates — an untouched mod must
        be untouched)
```

## criteria

`modcheck run` on a mod with a validated checklist can produce REFUSED (floor),
RED (judge) and GREEN (both halves), each proven by a selftest that shells out to
nothing. The 18 existing scripts still run exactly as before.

## Watch out

- 🔴 **Do not make `shows=` mandatory.** The per-mod rollout is the owner's
  ruling and the reason nothing breaks. A component without `shows` is correct,
  not a defect.
- The judge costs a `claude -p` call per claimed line per run (~18 s measured on
  one image). Judge against the component's LAST screenshot only, which
  `judge.py` already does, and consider batching several lines for one image into
  a single call if runs get slow — but never by asking one vague question
  covering several lines, which is the failure mode the narrow question exists to
  avoid.
- `judge.py` reads the image with the subprocess's own Read tool. Images over
  2000px in either dimension have killed agent sessions before (canon library
  brief); bridge screenshots are well under that, but a fallback
  `system_screenshot.py` capture at desktop resolution may not be. Downscale a
  copy to `/tmp` before judging if a capture is oversized.
