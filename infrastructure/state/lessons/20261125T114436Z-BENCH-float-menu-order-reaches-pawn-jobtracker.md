A float-menu order reaches Pawn_JobTracker.StartJob from the job queue: TryTakeOrderedJob enqueues the job and ThinkNode_QueuedJob starts it. So a StartJob hook sees ThinkNode_QueuedJob as the giver of every player order, work orders included. To name the work giver, read the job's workGiverDef when the node is the queue's (JawaBenchCast.Giver, fixed b7cbcd93f2).
item: RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER
home: skills/rimworld-modding/references/project-engine-facts.md
