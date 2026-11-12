SteveDesktop Whittle clones (~/rm/claude-offline*) have no core.sshCommand, so ./publish retries forever on the read-only default key; run it as GIT_SSH_COMMAND="ssh -i ~/.ssh/deploy_rimmandrake_write -o IdentitiesOnly=yes" ./publish (the key behind the github-rimmandrake-write host alias).
item: SHIP_ALLOY_FORGE_1
