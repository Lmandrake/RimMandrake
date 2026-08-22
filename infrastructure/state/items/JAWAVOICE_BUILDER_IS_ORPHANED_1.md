## spec
⚠️ **`src/RimMandrake/Utils/build_jawavoice.py` is an orphaned generator standing over 9
committed patch files.** Found 2026-08-21 in the same sweep as
`GENIDEO_REVERTS_DEAD_KINDS_1`.

Two independent breakages:

1. **Its inputs are gone.** `SRC = src/RimMandrake/Utils/_speakup_src_1p6` does not exist
   on disk and is not in git.
2. **Its output path is wrong by one `..`** — `OUT` resolves to
   `src/RimMandrake/src/Jawa/JawaVoice`, a directory that does not exist. It would
   `makedirs` a phantom tree rather than touch the real `src/Jawa/JawaVoice`.

🔑 **The second bug is currently the only thing protecting the nine files.** Anyone who
"fixes" the path without noticing the missing inputs turns a dead script into one that
overwrites hand-maintained XML with nothing.

**Do one of:**
- restore `_speakup_src_1p6`, fix the `OUT` path, and prove a re-run leaves the tree
  clean; or
- **mark the script dead at the top of the file** and leave the path broken, so the next
  reader repairs the right thing.

## verify
Either a re-run produces an empty `git diff` over `src/Jawa/JawaVoice/Patches/`, or the
file's first docstring line says it is dead and why.

## criteria
Nobody can turn this into a working overwrite without first restoring its inputs.
