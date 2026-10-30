# ARENA_SANDBOX_HARDEN_LOOPBACK_STILL_OPEN

## spec
arm_sandbox.py (ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE) hides the filesystem from every arm builder/tester, but the
sandbox shares the network namespace on purpose (the model CLI must reach its API). From inside an arm sandbox the
loopback services stay reachable: RimPulse :8765 (unauthenticated ledger/item pages: item specs can describe the fix),
the account page :8790, and any Windows-host port via the WSL NAT gateway. An arm could curl the ledger and read a task's
item spec or close note. Options: a netns with only an HTTPS egress proxy (slirp4netns/pasta are not installed), or
binding RimPulse to an authenticated socket, or a per-arm token. Measure first: from a sandbox, curl 127.0.0.1:8765.

## criteria
Done when an arm-side probe launched via arm_sandbox.wrap cannot fetch any RimPulse page or other host-local service,
while the model CLI still reaches its API; a selftest proves both.
