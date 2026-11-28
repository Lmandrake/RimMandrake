A vanilla search that walks regions (GenClosest.ClosestThingReachable's RegionwiseBFSWorker, as in Toils_Haul.CheckForGetOpportunityDuplicate) never calls Reachability.CanReach, so a FlowWorks reach veto written as a CanReach postfix does not reach it: a haul was retargeted into a sealed pit. Where such a search picks a target, add CanReach to its validator (RM_Patch_HaulDupeReach, a62c932133).
item: RIMMANDRAKE_ADD_COVERED_PITS_TO_FLOWWORKS_WALK_MAP_HE_ASKED
home: skills/rimworld-modding/references/project-engine-facts.md
