When a tier swap looks undone before a launch, read the launch line and list_journal.py show <game> first. Since 20844b58d1 every game_instance launch names the list it loads; LIST CHANGED gives the last modset_builder write (tier, owner, time) and the copy with the same bytes and mtime. An old mtime on a live ModsConfig means a copy that kept its source's mtime (shutil.copy2, atomic_copy), not a fresh write by RimWorld or modset_builder --apply.
item: RIMMANDRAKE_TRACE_ARCHSMALL_TIER_SWAP_UNDONE_BEFORE_LAUNCH
home: skills/rimworld-load-round
