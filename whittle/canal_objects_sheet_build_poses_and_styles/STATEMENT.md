# CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES — done statement

Item: "Labelled sheet of every ladder pose, weirs, fords and the four material styles of tank, reel and weir."
Built at 9a463b5bf37c (L0). Owed: A1 (L2), copied from the ledger:

- **A1 (L2):** on a river quicktest map, `objects_sheet.py --prove` reads PROVEN: 12 ladder rows (lowered, raised,
  autoturn on each of four walls) read back their wall's rotation, and every group (`EXPECT` in objects_sheet.py:
  ladders_lowered/raised/autoturn 4 rows each; styles_<kind> one row per look for tank, tall tank, hose reel and
  universal pipe; river_weirs one row per look; river_fords 1 row) has its full rows, all MATCHES, and its labelled
  picture.
  Evidence: `prove.txt` reading `PROVEN`, plus `rows.json`, `index.html` and the `*_labelled.png` pictures from that run
  on SteveDesktop's game A (fetched to `whittle/canal_objects_sheet_build_poses_and_styles/evidence/`), with the
  rimflow `verify --level L2 --result pass` on the built sha citing them.
