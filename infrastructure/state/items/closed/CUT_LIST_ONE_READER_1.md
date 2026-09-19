# CUT_LIST_ONE_READER_1 One reader for the Cherry Picker kill list

## spec

`DUMP_DERIVED_SHEETS_SHOW_CUT_1` built `src/RimMandrake/Utils/cherrypicker.py` and moved the two
contact sheets onto it. **Six scripts still open the settings file with their own regex:**

```
src/RimMandrake/Utils/biome_commonality_zeroed.py
src/RimMandrake/Utils/neolithic_floor_roster.py
src/RimMandrake/Utils/preload_check.py
design/Jawa/fauna/allocate_cast.py
design/Jawa/fauna/gen_cast_patch.py
src/RimMandrake/bridgetools/load_session.py
```

⛔ **`cherrypick_build.py` is NOT on that list and must not be moved.** It WRITES the settings
file and owns the ratified-vs-decisions union; it is the producer, not a consumer.

🔑 **Two of them have already hard-coded a count in prose** — `biome_commonality_zeroed.py` says
1,342, `gen_cast_patch.py` says 1,342 — and the list grows every time the owner reviews a
category. A number in a comment is a number that will be wrong.

**The second half, and it is a different file:** `measure count ThingDef` counts what the DUMP
holds, not what the game runs. That is a different question, not a wrong answer — but nothing
labels it, so the answer travels as if it were the population. The instrument lives outside this
repo at `D:\Luke\dev\measuring-large-artifacts` (installed at
`~/.claude/skills/measuring-large-artifacts`); it needs one line saying which question it
answers, in the register-of-instruments style it already uses.

## verify

Grep the repo for `Mod_3521312241` — only `cherrypicker.py` and `cherrypick_build.py` may match.
Then run each moved script and confirm its output is unchanged against a saved before-copy.
⚠️ **Diff the OUTPUT, not the exit code.** These scripts filter populations; a regex that
silently matched fewer keys keeps every count healthy and quietly stops cutting.

## criteria

- [ ] Six scripts import `cherrypicker`; no second parser of the settings file remains.
- [ ] No hard-coded cut count survives in any comment or docstring.
- [ ] `measure` states which question its `ThingDef` count answers.
