# WB-cause-RIMMANDRAKE-JOIN-JETTY-SQUARES-SEAMLESS-STILL-TWO-BLOCKS-20261127-134005

State: done (2026-11-27).

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_TRACE_ARCHSMALL_TIER_SWAP_UNDONE_BEFORE_LAUNCH | REAL (a failure happened) | writer found and guarded; closed | daa3399fa7 (fix), e36f01cf7c (reshape) |

- The writer: `selftest_testq_steve2.py`'s recycled-worker case ran the real `modcheck compose Mock` with
  `RM_GAME_INSTANCE=b`. On Archmagi that copied a clone's `ModsConfig.MINIMAL.xml` (mtime kept) over ArchSmall's
  live list. Caught live at 06:52:21 PST 2026-11-27: a `code_review_status.py check testq.py` run in the
  DRAW_SCRAPPER_JETTIES clone wrote md5 53bbcb40 with mtime 04:14:30, that clone's MINIMAL checkout time, under the
  Pyrelands run. On 2026-11-26, MINIMAL's md5 was a1069dfb, the bytes that came back then.
- Fix: `worker.real_list_cmd`. A test's worker (`TESTQ_SKIP_PULL=1`) with no override runs no compose and no tier
  swap. Its test was red on the parent and is green now. The worker's test files left the live list unchanged.
- The live part of the item (a swap holds over two launches) was replaced by the worker test: it could not decide an
  intermittent writer, and the writer is now known. The Pyrelands run's ArchSmall list was put back on md5 660dbdd1,
  the list it runs.
- Nothing is next. The fresh reader is RIMMANDRAKE_READ_FIX_DAA3399FA7_WITH_FRESH_EYES.
