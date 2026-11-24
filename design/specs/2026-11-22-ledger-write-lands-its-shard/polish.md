# Polish: a rimflow write lands the paths it wrote (a record; nobody takes lines from it)

- `skills/using-rimflow/SKILL.md` and `references/traps.md` say that the owner flags write OWNER.jsonl, to commit by hand. Skills are edited only in curation sessions.
- `publish.py` `carried_prose_moves` still re-adds a closed item's prose move when a shard is published by hand or by
  the detached finish step. It stays: those publishers did not make the write, so they have no record of it.
- `selftest_no_bare_cuts.py` is red on origin/main with 154 bare cuts in other files (none in this component).
- `maturation.py`'s steward section says "commit and publish it [OWNER.jsonl] too". True; pointing it at `--publish` changes
  the calibrated `maturation_advance` brief hash, so it waits for that brief's next calibration.
- `publish.py` `land_ledger` `blob`: not handled: a `git cat-file` that fails on a shard that exists reads as an empty shard.
  The pre-push `ledger_lint` refuses the commit that would follow.
- `publish.py` `split_pre_existing`: the second `try` block, after `return still, pre`, never runs.
- `publish.py` `warn_owner_shard`: in a held clone, the WARNING can name OWNER.jsonl lines that are already on origin.
- `cli.py` `cmd_implemented`: the refusal of an unpublished sha still prints `git pull --rebase`; `./publish` is the command.
- `cli.py` `_bridge_other_host_locked`: the refusal prints the taker's own `--for` as the holder's.
- `cli.py` `cmd_close --evidence`: a dead path in the evidence gets no warning, as `verify` gives.
