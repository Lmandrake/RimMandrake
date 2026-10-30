## spec
`arena who` check d judges a stopped arm's refs from what origin holds now (`git ls-remote origin refs/heads/arena/<arm>/*`), both for the switch-time snapshot and for the later comparison, so a `git push --no-verify <url> HEAD:refs/heads/arena/<arm>/x` that never touches local tracking refs is caught. The reflog method stays on local tracking refs. An unreachable/auth-failing remote raises RemoteUnreachable: who (d) fails (exit bit 8), never passes. A recorded `--allow-offline` switch snapshots local refs and its post-switch who tolerates only that RemoteUnreachable on d: only the remote-refs half, only when the snapshot itself fell back offline (not merely any offline clone in the dirt check), and the events half of d is still computed and reported, so a stopped-arm event after the switch still exits bit 8.

Sandbox consequence: from a shell without the SSH key, `arena who` check d fails (RemoteUnreachable -> bit 8). `who` must therefore run unsandboxed (with the key). No explicit `--offline` mode exists for `who` (only `arena switch --allow-offline`); none is invented here, so a sandboxed who is a fail, never a pass.
## criteria
1. selftest_arena_switch t_who_d_remote_refs: a sneaky URL push makes who exit with bit 8.
2. Unreachable remote makes who (d) fail with RemoteUnreachable.
3. Both forced-failure checks are red when refs_snapshot reverts to local tracking refs.
4. Full selftest_arena_switch passes.
5. t_who_d_offline_partial: offline-snapshot switch + remote gone + stopped-arm event -> bit 8 with events reported; no event -> tolerated; remote gone but snapshot taken online -> not tolerated. Red when the tolerance is the old whole-d forgiveness.
