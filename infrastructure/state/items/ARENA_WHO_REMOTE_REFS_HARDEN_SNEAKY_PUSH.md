## spec
`arena who` check d judges a stopped arm's refs from what origin holds now (`git ls-remote origin refs/heads/arena/<arm>/*`), both for the switch-time snapshot and for the later comparison, so a `git push --no-verify <url> HEAD:refs/heads/arena/<arm>/x` that never touches local tracking refs is caught. The reflog method stays on local tracking refs. An unreachable/auth-failing remote raises RemoteUnreachable: who (d) fails (exit bit 8), never passes. A recorded `--allow-offline` switch snapshots local refs and its post-switch who tolerates only that RemoteUnreachable on d.
## criteria
1. selftest_arena_switch t_who_d_remote_refs: a sneaky URL push makes who exit with bit 8.
2. Unreachable remote makes who (d) fail with RemoteUnreachable.
3. Both forced-failure checks are red when refs_snapshot reverts to local tracking refs.
4. Full selftest_arena_switch passes.
