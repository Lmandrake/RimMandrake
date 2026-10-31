arena: CARBON_PRESS and COLD_INSPECT hidden checks run a C# build that rsyncs into /mnt/d/ClaudeWork/.../build, read-only in the judge sandbox, so no materialised read can make them pass; they stay dropped until the judge grants a build-output rw path.
home: src/RimMandrake/Utils/arena/arena_vet_reads.py
