A READ-CLEAN mark on src/RimMandrake/Utils/boundary_check.py goes stale within minutes, because every new boundary page adds a row to its PAGES dict (seen 2026-11-27: a mark at 4d724b8e1f was DIRTY 15 min later from one PAGES row). A fresh-reader ticket that names boundary_check.py holds only if you re-mark right before the close; read the diff of the new PAGES rows first. Moving PAGES into a data file would stop the churn.
item: RIMMANDRAKE_READ_FIX_CEAB7B4958_WITH_FRESH_EYES
home: design/specs/2026-11-19-clean-means-promises-tested/polish.md
