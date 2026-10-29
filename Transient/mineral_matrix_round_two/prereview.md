# Prereview: mineral matrix round two page

Page: D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-28\page\index.html (151 KB, data.json embedded, also beside it)
Built by page/build_page.py from page/template.html + page/data.json.
Harness: prereview/run.py (Python playwright 1.62, chromium headless shell; needs LD_LIBRARY_PATH=/home/mandrake/.local/lib/pwlibs for libasound).
The page is served inside the artifact skeleton. SheetJS 0.18.5 is the real cdnjs file, routed locally. Google Fonts are blocked, so fallback stacks are what was seen. window.claude is mocked with in-memory db/user/downloads.
Result: 47 of 47 checks pass (prereview/result.json; screenshots prereview/*.png).

## What was checked
- Desktop 1440 px, light and dark: 37 biome rows, 49 mineral columns, 1813 cells. No empty row or column labels. No NaN/undefined/null text. 88 nonzero cells shown, which equals the data.
- Ladder buttons:
  - the first click writes one db record {kind, biome, column, old, new, draft, reset, who, at, v} with who = user id;
  - the cell text and value update and the cell gets the "changed by you" outline;
  - rungs 0.03, 25 and 99 apply;
  - free entry 3.5 applies;
  - "Reset to draft" returns the draft value, writes a reset record and drops the highlight;
  - a saved note shows the note dot.
- Biome header: the band edit writes two band records and the row label shows 12-40%. Another user's record shows the purple outline.
- Filters: only changed, hide empty, class, search.
- Views: by mineral (one card per mineral), other sources, reachability and change log all render clean.
- xlsx via downloads.save, read back with XLSX.read. It has 7 sheets:

  | Sheet | Rows × columns |
  |---|---|
  | Values | 38×54 |
  | Reasons | 91×13 |
  | Bands | 38×11 |
  | Other sources | 5×28 |
  | Homes | 33×6 |
  | Reachability | 54×10 |
  | Change log | 11×8 |

  The edited band is carried into Values. There is no NaN or undefined anywhere.
- Phone 390 px, light and dark: 37 biome cards with the grid hidden. Editing from a chip writes a record, and the "Edit another mineral" select opens the editor. The body never scrolls horizontally in any of the five views.
- No db (null) and no window.claude: the banner says changes stay on this screen, edits still apply locally, and there are no page errors.

## Caught and fixed
1. Desktop body scrolled 1064 px sideways. The outer grid track grew to the table's width. Fixed with minmax(0,1fr) and min-width:0 on the wrappers.
2. Phone body scrolled 62 px. The "All mineral classes" select sized itself to its longest option. Fixed by capping the filter controls' width.
3. The phone editor drawer overflowed the right edge (Close button clipped). It used content-box width plus padding. Fixed with border-box and a single minmax column.
4. In dark mode, high-heat cells (10, 25) had light text on light green. The ink is now a per-theme token. The light heat-5 colour was darkened to give 5.3:1 contrast.
5. The mineral cards showed raw def ids for the second biome (e.g. "FloodedCanyon"). They now show biome labels.
6. Ladder words for 2 and 5, and for 10 and 25, read identically. They now say low and high end.
7. The drawer showed ".3" for the current value. It now shows "0.3".

Harness assumptions corrected, not page bugs: steel is the first column, so its draft is not 0. data.json carries 32 minerals including steel, while the 31 in the D3 count exclude it.

## Not checked
- Real claude.ai runtime (db rules, consent prompts, profile names) and real Google Fonts rendering.
- Keyboard-only walk beyond Enter/Escape handlers.
