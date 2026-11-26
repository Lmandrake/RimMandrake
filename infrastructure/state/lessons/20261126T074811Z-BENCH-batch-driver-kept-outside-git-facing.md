A batch driver kept outside git (facing_backlog drv.py under agent storage) grew its own private size rule (fit every new N/S to east's height) that disagreed with the repo's facing_scale_lint (band up to ~1.4x east; never shrink below MIN_SHRINK 0.65). 26 of 60 view subjects were shrunk below 0.65 and judged as shrunk pictures. A scratch driver must call the repo's rule, not restate it; facing_view_fit.py check-driver now tests that.
item: FACING_NORMVIEW_FIX_SHRINKS_SNAKES_TO_PEAS
home: skills/generating-rimworld-sprites
