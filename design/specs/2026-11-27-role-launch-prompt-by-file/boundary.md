# BOUNDARY: a role run's prompt rides the unit's stdin, never the systemd-run argv, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/role_launch.py` (`launch_argv`: `prompt_file`, `StandardInput=file:`, the `</dev/null`
of the sync and pre-launch steps; `prompt_path`; `launch`). Item `RIMMANDRAKE_FIX_DESIGNER_LAUNCH_ARGUMENT_LIST_TOO_LONG`,
written 2026-11-27. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_role_launch_long_prompt.py`.

Why: at 1:11 AM and 1:15 AM PST on 2026-11-27 the Dispatcher launched the WreckedMachines Designer for stage 3 and both
launches died `OSError: [Errno 7] Argument list too long: 'systemd-run'`. Measured offline: the stage packet
(`designer_stage.packet`) was 131,339 bytes, over Linux `MAX_ARG_STRLEN` (131,072 bytes for one argv string); its
working record (`record.json`, 137,333 bytes on disk) filled 78,876 bytes of it. The packet went to `claude -p` as one
argument, through `systemd-run` and again through `claude_bounded.sh`'s inner `systemd-run --scope`.

## ACCEPTS (the only inputs this is built for)

- **a-role-message.** The message that `role_launch.launch` is given (a prompt, a stage packet, a mend head), of any
  length, for a claude or a codex runner, with or without `pre_launch` steps and a role clone's `./sync`.

## DOES NOT SURVIVE (not promised)

- **a-caller-with-no-prompt-file.** `launch_argv` called without `prompt_file` (a test's path) keeps a message of up to
  `ARGV_PROMPT_MAX` bytes on argv and refuses a longer one with `ValueError`. `launch` always names the file.
- **a-pre-step-that-needs-stdin.** The sync and pre-launch steps read `/dev/null`, as they did before the prompt moved
  to stdin.

## PROMISES (each one is owed a test of the same name)

- **a-long-prompt-rides-stdin-never-argv.** `launch` writes the whole message (the repair line included) to
  `<root>/roles/<unit>.prompt.md`, beside the run's out and err, and the unit reads it as its stdin
  (`StandardInput=file:`). No string of the systemd-run argv is over 131,072 bytes, and none holds the prompt. Run
  through the real sync and pre-launch shell layers, a pre-step that reads stdin leaves the whole text to claude; a
  codex run gets no `--prompt` (agent_runner.py reads stdin). Red on the parent: the longest argv string was 208,375
  bytes for a 208,375-byte message.

## LIMITS

- **ARGV_PROMPT_MAX = 32768 bytes.** Danger: Linux refuses one argv string over 131,072 bytes (E2BIG, measured
  2026-11-27 above). It refuses work only on a call with no `prompt_file`, which no launch makes.

## Measured

- Real `claude -p --output-format json` with a 147,096-byte prompt on stdin from a file answered from the prompt's last
  line (2026-11-27).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
