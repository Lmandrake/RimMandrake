Under machine load ~40 (many parallel detached publishes), a full-tree git checkout or git grep in ./publish tree checks takes over 300 s; hang guards of 120-300 s on whole-tree git calls refuse real publishes. Give whole-tree git calls their own deadline far above a loaded run (publish.py CHECKTREE_GIT_TIMEOUT_S 1800 s, 9c593be76c).
item: RIMMANDRAKE_BUILD_WINDOW_ADAPTERS_TRADE_AND_SETTINGS_FIRST
home: src/RimMandrake/Utils/publish.py
