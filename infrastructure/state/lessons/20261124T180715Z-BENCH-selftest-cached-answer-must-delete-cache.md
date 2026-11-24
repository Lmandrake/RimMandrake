A selftest of a cached answer must delete the cache before the case that should miss it: the moving-ref case of selftest_guard_relation.py was green without its fix because an earlier case had kept the right answer. Remove the fix and see red before you trust the case.
item: RIMMANDRAKE_PUT_STEVEDESKTOP_ON_NON_MOD_WORK_ALL_DAY_HE_ASKED
