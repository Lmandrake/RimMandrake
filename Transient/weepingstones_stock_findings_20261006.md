# WeepingStones stock job loop findings 2026-10-06 (static reading only)

## STOCK (stock_releases_species_pawn_into_pen) - mod defect, fixed
RM_JobDriver_StockPoolPen put `FailOnDespawnedNullOrForbidden(A)` at JOB level. ToilFailConditions.DespawnedOrNull requires
thing.Spawned; RM_SkarrinBreedingStock has stackLimit 1, so StartCarryThing moves the whole Thing into the carry tracker,
it despawns, the job ends Incompletable right after pickup and the item is dropped back: "1 stock left, 0 released".
Feed survived the same line only because a food stack > count is split (original stays spawned).
Fix: job-level FailOnDestroyedNullOrForbidden(A) (forbidden check already exempts carried things) + FailOnDespawnedNullOrForbidden
only on the GotoThing toil. Same change in RM_JobDriver_FeedPoolPen (latent for a full-stack carry).
Open: stock_outside_pen should have failed the same way (item re-dropped on pad); settle live.

## NET / CULL - mod defect (target not held), fixed by freeze
Wait toil + FailOnCannotTouch(A, Touch) never follows the target. A wild skarrin / vhorrin wanders or flees out of touch,
job ends Incompletable, target alive: "1 wild left" / "1 vhorrin left". Matches the 2026-10-03 live poke (skarrin flees).
Fix: new first toil calls RM_PoolBreederUtility.HoldStill (StunHandler.StunFor, 900 + wait ticks) on the target.
Design note: this makes netting/culling a stun-then-handle; owner-visible. Settle live: run job_net/job_stock/job_cull.
Unconfirmable statically: handler being attacked (RM_Illoth/BrainWorm bites in surprise logs) would also drop the job; harness side.
