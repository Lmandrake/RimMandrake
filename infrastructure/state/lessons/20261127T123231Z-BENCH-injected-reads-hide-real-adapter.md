A step whose test injects every read (commits=, owed=) never runs its real adapter. The adapter can lose all its data and the suite stays green. Example: work_bundle.reader_step; with --name-only removed from bundle_commits, every bundle reads 'no code' and ends unread. Give each such promise one case that fakes only the act at the far end (the filer) and runs the reads for real, on a throwaway git origin. Then plant a fault in the adapter and see the case go red.
item: RIMMANDRAKE_READ_FIX_291FA34BBB_WITH_FRESH_EYES
home: skills/live-debugging-proof-harness
