# REFRESH_SQLITE_WRONG_DIR_1 — verify, BUILD, 2026-08-23

## the defect
  game_paths.DEF_DUMP  = DefDump/captures/<newest>/   (the CAPTURE)
  game_paths.DUMP_ROOT = DefDump/                     (holds the captures)
  refresh.py joined DEF_DUMP for defs.sqlite, which lives at the ROOT.
  => a present 788,152,320-byte database reported as 'absent / MISSING',
     sending the reader to 'measure build' for a rebuild he did not need.
  measure's own cli.py:80 says it: 'defs.sqlite stays at the root'.

## before
  DefDump/defs.sqlite        absent                     MISSING   measure build
## after
  DefDump/defs.sqlite        78813 defs, 552 types              current   -

## and the database is NOT poisoned — checked, because it predates tonight
  provenance captured_utc = 2026-08-21T22:44:59Z
  BiomeDef rows = 80, total defs = 78,813
  80 is the healthy value; the broken 05-05-29Z load held 54. So it was built
  from a good capture and nothing queried against it has been misled.
