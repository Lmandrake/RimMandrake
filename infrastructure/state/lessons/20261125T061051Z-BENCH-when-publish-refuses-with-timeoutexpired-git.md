When ./publish refuses with TimeoutExpired on a git call (checkout in full_head_tree, or a tree check's git grep), read /proc/pressure/io before suspecting the commit: on SteveDesktop 2026-11-24 fourteen concurrent rm-treecheck trees plus the pool monitor's find scans held it at ~94% full, a 15 s checkout took 119-542 s, and PUBLISH_GIT_TIMEOUT=1500 let the publish through unchanged.
item: RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY
home: skills/clone-landing-commits
