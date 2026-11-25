A wait constant shared by several live parts was shortened for one part, the burn-line control, which now stages the quiet counter. The other parts, the walk's off spells, stage no counter and lost the window they need. Before you retune a shared timing constant, grep its callers. Give each part that has different staging its own named constant.
item: SELFTEST_FIX_PYRELANDS_WALK_BED_RESUME_RRCM
