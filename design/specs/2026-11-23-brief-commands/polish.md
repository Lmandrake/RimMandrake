# Polish lines of the fresh reader, 2026-11-23 (a record; nobody works it)

- The `close` line does not show `--live`; `also` does, and the footer says when.
- `census/window.py`: a second run on the same window and `--out` with a wrong `--projects` writes `could_not_look` over a good reading.
- `census/window.py`: a torn line with neither `"assistant"` nor `"tool_result"` in it is not counted as torn (scan3's filter, kept).
- `census/window.py`: `runs` counts a transcript whose turns all repeat another's (as the baseline's 1,908 does).
