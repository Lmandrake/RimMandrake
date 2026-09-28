# CONTAGION bedazzle cast — art review sheet

`sheet.html` is a keep/improve/regenerate review of the CONTAGION grotesque cast
(`CONTAGION_BEDAZZLE_SITTING_1`, `infrastructure/artpipe/art_lists/contagion_grotesque_cast.csv`)
— 38 subjects, all validated PASS in the artpipe registry, grouped as **Contagion fauna**
(21 faced creatures shown south/east/north together, plus the 3 Coalescence growth stages),
**Contagion flora** (12 plants) and **Item icons** (cloud repulsor, sunbeam). Folded in as its
own **Desert redo pass** section: the 9 `_b` subjects re-generated the night of 2026-09-27 after
the desert fill-out sitting (`Transient/desert_fillout_art_review/`) marked them
improve/regenerate — each row repeats the original note so the redo can be judged against what
was actually wrong. Every one of the 47 rows is pre-filled `keep`; none were "not ready" (all 38
CSV rows and all 9 redo subjects had a validated-pass render on disk under
`infrastructure/artpipe/_artsrc/`). `decisions.json` is an empty scaffold
(`reviewStatus.state: "prefill"`) — nothing has been ruled on yet.

Images are copied locally into `img/` and referenced by relative path, so the page works
opened straight from disk.

**Open at:** `D:\Luke\dev\Rimworld\Transient\contagion_cast_art_review\sheet.html`

This subagent could not run `assets/serve_sheet.py` to hand over a live tokened URL (no
browser session available here) — the file path above is the fallback the `review-sheets`
skill names for exactly that case. `check_sheet.py` passes with 0 FAIL (1 WARN: the decisions
file has no per-row entries yet, expected for a fresh scaffold nobody has opened).
