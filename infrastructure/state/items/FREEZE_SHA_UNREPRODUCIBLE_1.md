# FREEZE_SHA_UNREPRODUCIBLE_1
The frozen dump's `modlist_sha` reproduces from nothing; fold `freeze_dump.py` into `refresh.py`

Filed by CHECK, 2026-08-21, off the owner's ruling *"deploy the fix, re-capture, re-freeze."*
⚠️ This does NOT overrule anything BUILD is currently building — it is a defect in the
registry as it already stands, found while checking whether the owner's ruling was
actionable. BUILD owns the dump scheme; CHECK does not redesign it.

## spec

Two defects, both in the freeze mechanism, both measured 2026-08-21 12:55.

### 1. `modlist_sha` is not a checkable claim

`REGISTRY.jsonl`'s `OFFICIAL-2026-08-21` carries `"modlist_sha":"e0f11692cf69e516"`.
**Nothing on this machine produces that number.** Measured against both fingerprints
`refresh.py` computes over the same capture:

| source | value |
|---|---|
| `refresh.dump_fingerprint()` — the mod set the CAPTURE saw | `5ef6eec3daf6c325` |
| `refresh.loadset_fingerprint()` — the CURRENT live load set | `49b83562b10df31c` |
| what the registry froze | `e0f11692cf69e516` |

🔑 **A freeze is a claim about an artifact, and a claim nobody can recompute can only be
believed.** That is the same failure `dumps/README.md` already documents as
`REPLACED`: the registry asserted something about the capture, nobody measured it, and
it was wrong. `capturedUtc` got a detector; `modlist_sha` did not.

⚠️ The `OFFICIAL-2026-08-20` entry is honest about this — it says
`"modlist_sha":"see manifest.json"` rather than inventing a number. The 08-21 entry
regressed by supplying one.

### 2. `refresh.py --freeze` does not exist

`refresh.py:363-364` states: *"⛔ Only the OWNER re-freezes, deliberately. Nothing here
does it automatically, and `--freeze` refuses without an explicit `--by owner`."*
There is **no `--freeze` in its argparse** (`refresh.py:700-712`). So the one act the
whole registry is built around had no command behind it, and the owner would have been
left hand-appending to an append-only JSONL by eye — the exact failure
`~/.claude/CLAUDE.md` names: *"Naming a capability is not handing it over."*

CHECK wrote `src/RimMandrake/Utils/freeze_dump.py` (commit `3f45aaf`) so the owner's
ruling was executable today. It reads `capturedUtc`/`gameVersion`/`modCount` out of
`manifest.json`, takes `modlist_sha` from `refresh.dump_fingerprint()`, sets `supersedes`
itself, refuses any seat but `--by owner`, refuses a no-op when the capture on disk is
already the frozen one, and refuses to append past a malformed registry line.

⛔ **It must not become a second mechanism.** CLAUDE.md is explicit that two tools
answering one question is two answers. Either fold it into `refresh.py` as the `--freeze`
the header already promises, or delete the header's promise and point it at the script.
**BUILD's call which.**

## verify

Offline, no game load.

1. `python3 src/RimMandrake/Utils/freeze_dump.py` — dry run against the current disk.
2. Confirm `refresh.py --help` either grows `--freeze` or its header stops claiming it.
3. `grep modlist_sha infrastructure/state/dumps/REGISTRY.jsonl` — every entry's sha is
   either recomputable or honestly says `see manifest.json`.

## criteria

- ✅ **PASS** when exactly ONE command re-freezes, its `--help` matches the docstring
  that describes it, and the `modlist_sha` it writes is reproducible by a documented
  function a reader can run.
- ❌ **FAIL** if two commands can both append a freeze entry, or if any entry carries a
  sha no code on this machine produces.
- ⛔ **NOT in scope:** re-freezing anything. Only the owner does that, and the current
  capture is correctly frozen until the next load re-captures.
