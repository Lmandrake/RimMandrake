The testq worker runs modset_builder and tier_load from its clone pinned at the job's source_sha (the built sha), not from main. A new tier kind therefore resolves only for builds made after it landed; jobs of older builds end INVALID/LOAD. Routing a job to a tier kind must check the built sha's modset_builder, not today's.
item: RIMMANDRAKE_RETIRE_OLD_PIPELINE_REMNANTS_TEN_SLIPPED_INTO_LANES
home: NONE
