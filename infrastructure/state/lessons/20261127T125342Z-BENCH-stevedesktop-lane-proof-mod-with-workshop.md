A SteveDesktop lane proof of a mod with a Workshop dependency ends INVALID LOAD with 'NOT INSTALLED (tier is incomplete)' when that Workshop mod was never copied there (VFE Factory, 2026-11-27). Repair: sync_test_mods.py --only <packageId> --also-mods /mnt/d/ClaudeWork/rimmandrake/instances/b/game/Mods --apply, then ask again. Also: testq.py wait prints 'hung no heartbeat for at least 300s' while a job still deploys and loads; read the done file before judging it hung.
item: RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL
home: infrastructure/stevedesktop/RUNBOOK.md
