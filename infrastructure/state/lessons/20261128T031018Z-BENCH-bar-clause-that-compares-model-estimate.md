A bar clause that compares a model to an estimate can be the only check that catches a kernel mutant: when the Tree shade T2 'within 10 points of the estimate' clause was dropped, the crown mutant 'radius halved' went uncaught (6 of 7). A geometry case caught it again only after it wrote r = k x s / 2 itself instead of reading RM_TreeCrown.Radius. Before you drop an assertion, run the mutator of that kernel.
item: RIMMANDRAKE_RULE_TREE_SHADE_T2_MIASMA_MUD_GROWS_NO_FOREST
home: skills/mutate-your-checker
