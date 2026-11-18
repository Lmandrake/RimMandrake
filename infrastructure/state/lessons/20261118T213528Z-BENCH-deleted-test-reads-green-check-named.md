A test named as a proof can vanish silently: a later commit deleted a named test function while editing its selftest file, and the file stayed green because a missing test prints nothing. Before trusting or strengthening a proof, grep that each test it names still exists at HEAD; a mutants selftest that names its guarding tests should fail by name when one goes.
item: RIMMANDRAKE_RETIRE_OLD_PIPELINE_REMNANTS_TEN_SLIPPED_INTO_LANES
home: NONE
