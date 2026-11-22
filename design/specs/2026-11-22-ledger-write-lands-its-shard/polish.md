# Polish: a rimflow write lands the paths it wrote (a record; nobody takes lines from it)

- `.claude/agents/rm-*.md` (six files) say "Those two flags write OWNER.jsonl ... Commit and publish that file too". True,
  but `--publish` on the write now does it. A curation pass may point them at `--publish`.
- `skills/using-rimflow/SKILL.md` and `references/traps.md` say the same. Skills are edited only in curation sessions.
- `publish.py` `carried_prose_moves` still re-adds a closed item's prose move when a shard is published by hand or by
  the detached finish step. It stays: those publishers did not make the write, so they have no record of it.
- `selftest_no_bare_cuts.py` is red on origin/main with 154 bare cuts in other files (none in this component).
- `maturation.py`'s steward section says "commit and publish it [OWNER.jsonl] too". True; pointing it at `--publish` changes
  the calibrated `maturation_advance` brief hash, so it waits for that brief's next calibration.
