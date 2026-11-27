The live DefDump defs.sqlite goes stale at every game load that writes a capture (four captures in three days, 2026-11-26), and every dump_manifest.dump_db reader then answers UNMEASURED. The repair needs no game: measure build from the newest capture on disk (30-70 s). rm-defdump-db.timer now does it every 30 min; read defdump_db_tick.py check before you blame a def check's UNMEASURED on the dump.
item: SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB
home: design/specs/2026-11-26-defdump-db-tick/boundary.md
