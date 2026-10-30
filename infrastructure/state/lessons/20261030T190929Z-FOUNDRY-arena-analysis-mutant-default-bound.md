A module constant used as a function default (def f(control=CONTROL)) is bound at def time: monkeypatching the constant in a mutation test changes nothing, so the mutant survives and the constant is effectively untestable. Default to None and read the constant at call time. Found by selftest_arena_analysis --mutants.
home: NONE
