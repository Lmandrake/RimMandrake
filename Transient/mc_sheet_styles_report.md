# MessyConduit review map rebuilt around per-build styles (2026-10-04)

## Status
DONE offline (human_review.py --plan clean, selftest 24/24, run_selftests 174/177 = the 3 pre-existing failures). NOT built live: the main window holds the bridge and runs `python.exe src\RimMandrake\MessyConduit\human_review.py --build --fresh-map`.

## Inputs read
- design §2.3/§3/§4 (B; largest run wins, tie older; Restyle gizmo; Modern colour per run incl. random mix), stage 1-3 reports (probe verbs: AerialProbe place:def:Look:x,z[:rot]:god|build, finishbuild, cplace/cline/crestyle/cdeconstruct/cstyles; HoseProbe census look/rawStyle), test-extension §5.5 (rows 19-24 proposal), human_review.py (29 stations, global --style).

## New station plan
Placement: the style gallery takes the south-east of the south region (where the free area was); the free area moves to the
north band (8,228); old stations keep their exact cells and are renumbered +12 (1-29 -> 13-41).
- S1 block x140-236 z6-52: 1-4 ground cords per look (one compact build each: battery, 3x3 tangle, wall entry, in-line
  switch, plugged lamps, a cut cell = live end + dead end); 5 Modern colour entries (7 runs: random mix, one colour per run,
  Orange, Green, Brown, Yellow, Blue); 6 overhead quartet (one row per look: mast, mast, lamp mast, wall bracket, spans);
  11 hose reels (per look one laid plump + one laid then reeled in).
- S2 block x162-236 z79-111: 7 bridge (before: gap for him; after: the build bridges it), 8 tie (same, equal runs, Scrapper
  older), 9 split (before: marked cell; after: deconstructed), 10 Restyle demo (Scrapper run + switch + mast span, he
  presses the gizmo), 12 older-save set (unstyled conduit + switch + mast span + reel via build_batch).
- M art-slot board (labels; table computed from disk at the paths the code reads), north band beside the free area.
- Styled pieces go through the real designator: AerialProbe `cplace:def:key:x,z:god` (conduit, switch) and
  `place:def:Look:x,z[:rot]:god` (masts, brackets, reels); the global `set:style` is only the default look.

## Old -> new mapping
Old 1-29 -> new 13-41 (same cells, +12); free area F moved south-east -> north band (8,228); new M art board (96,236).
KEYSHEET.md opens with the full table; keysheet.html carries it too. The uncommitted KEYSHEET of the last live build of the
old map was overwritten by --plan (a copy was kept in this session's scratchpad only).

## Verbs used
- conduit/switch: `cplace:PowerConduit|PowerSwitch:<key>:x,z:god` (keys: Scrapper, Industrial, Modern_Mix, Modern_Multi,
  Modern_<Orange|Green|Brown|Yellow|Blue>, Futuristic; switch keys = 4 looks); `cprocess` after each Multi cell so the
  adopt rule sees one colour; `cdeconstruct:x,z` (split after-row); `cstyles:x,z,w,h` read per station.
- anchors/reels: `place:<def>:<Look>:x,z[:rot]:god`; links by `link:id,id`; reels laid by `lay:` and `reelin:x,z`.
- legacy set and old stations: `jawa/build_batch` (no designator, no stored style).

## Selftest / --plan
- selftest_human_review.py 24 checks (4 old renumbered 26->38, 21->33; 20 new): numbering + mapping, real menu keys,
  per-look coverage (1-4, 5 all Modern entries, 6 three anchor kinds x 4 looks, 11 laid + reeled-in per look, 12 nothing
  styled), merge winner from a python twin of ConduitStyles.Components (can fail: swapped sizes flip it), tie is a real tie,
  split gives 2 Industrial halves, restyle demo has no pre-applied action, art board probe + can-fail on an empty dir,
  layout can-fails (station moved onto its neighbour; styled cell on a battery).
- build() dry-run against a stub bridge: 241 cplace, 26 place, 3 'after' actions, 4 reelin, 15 cstyles reads; no crash.

## Open points
- Unproven live: conduit designated UNDER an existing steel wall through cplace (stations 1-4; vanilla allows it, but the
  build records any refusal in notes/styled_refused); bracket placement via `place:...:1:god`; Multi resolving per cell
  (cprocess after each cell so the adopt rule sees the first colour).
- Rock entry is NOT in the per-look stations (cplace cannot designate on natural rock); old station 18 (was 6) shows it in
  the default look only.
- Known code gaps the map shows rather than hides: tangle pieces follow the DEFAULT look (stage 2), clamp not styled,
  span cable falls back in all four looks, no reel coil overlay (all on board M).
- Old station 33 (was 21) expected-refusal line 'cavern pole ... Roofed' was false (that station links Ok since round 4)
  and is deleted from the key sheet.
