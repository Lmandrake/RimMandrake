A 'rimflow bridge take' run inside 'waitalive.py run' binds the take to the detached job's process, so the lock frees the moment the job ends; set RM_DRIVER_PID=<the claude pid> in the job's environment to bind it to the session (measured 2026-11-26: the first take was lost to another run within seconds).
item: RIMMANDRAKE_LOAD_EDITED_CANONICAL_SAVE_ONCE_618_LINES_CUT_UNLOADED
home: skills/using-rimflow/SKILL.md
