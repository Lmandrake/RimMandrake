# ARTPIPE_METER_WINDOW_REMAP_1

`Detector.note_meters()` reads the wrong meter window since the plan upgrade — the weekly
backstop is dead.

## What is true

MEASURED 2026-09-26 across all 2,388 records of `infrastructure/artpipe/throughput.jsonl`:
the Codex account changed the SHAPE of its rate-limit report when the subscription was
upgraded.

| Period | `primary_window_minutes` | `secondary_window_minutes` |
|---|---|---|
| every record up to 2026-09-26 **10:50** | **300** (5 hours) | **10080** (1 week) |
| every record from 2026-09-26 **11:06** | **10080** (1 week) | **null** |

The 5-hour bucket no longer exists. Corroborated independently: the worker homes refreshed
at 11:04 that day carry `chatgpt_plan_type: prolite`, the stale ones still say `plus`.

`artpiped.py` `Detector.note_meters()` (lines 338-340) maps the two fields **by position**:

```python
weekly = meters.get("secondary_used_percent")   # -> stop_all / refuse_new (95/99/99.8)
five_h = meters.get("primary_used_percent")     # -> n_override=1 / sleep   (90/98)
```

So right now:

- `secondary_used_percent` is `null`, the weekly branch never executes, and `stop_all` /
  `refuse_new` are never recomputed. **The real weekly backstop does not run at all.**
- The weekly percentage arrives in `primary_used_percent` and is judged against the
  FIVE-HOUR thresholds (`FIVE_H_DROP_N1 = 90`, `FIVE_H_SLEEP = 98`), so at 90% weekly the
  daemon will drop to N=1 and at 98% sleep until `primary_resets_at` — coincidentally
  conservative, but not the designed behaviour and not the designed threshold.

## Why it matters

The weekly window is now the ONLY quota window and it is finite: MEASURED ~13.7 jobs per
percentage point, ~1,370 image jobs per week, resetting 2026-10-03 11:04. The daemon is
flying that budget with its backstop disconnected.

## NEXT

Select the window by its declared `*_window_minutes` rather than by field position — treat
whichever window reports 10080 as weekly and whichever reports 300 (if any) as the short
window, and tolerate either being absent. Then re-check `WEEKLY_WARN/REFUSE/STOP` are being
applied to the weekly figure again.

⚠️ Do not "fix" this by swapping the two field names: that would break every historical
record written before 2026-09-26 11:06, and both shapes must parse.
