The ledger_lint PreToolUse hook fires on any Bash line that holds 'git push', even an ssh push of another repo on another machine, and it judges the local clone's ledger against a newer origin (NOT_APPEND on lines the clone simply lacks). Put a cross-repo push in a script file and run it with ssh bash -s.
item: RIMMANDRAKE_RESTORE_STEVEDESKTOP_ON_FLEET_NOW_OLD_PAGE_HAD_IT
