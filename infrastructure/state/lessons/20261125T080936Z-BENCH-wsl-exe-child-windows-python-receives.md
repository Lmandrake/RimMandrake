A wsl.exe child of a Windows python receives each name listed in WSLENV that the parent never set as an empty string, not as unset (measured 2026-11-24: RIMFLOW_DRIVER_LOCK='' made game_lock.py read 'no lock path' for ArchBig). Before a WSL tool reads such a variable, drop the empty names of WSLENV (stage_map.py outer does).
item: RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS
home: skills/wsl-windows-plumbing
