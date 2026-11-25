# Blind scan hook boundary

Code: `.claude/hooks/block_blind_scan.py`.
Tests: `.claude/hooks/selftest_block_blind_scan.py`.

## ACCEPTS

- A PreToolUse JSON payload naming Bash, with a command string and an optional working directory.
- Static command and path tokens that the measuring-large-artifacts skill can classify.

## DOES NOT SURVIVE

- Dynamically constructed tool names or artifact paths whose values require executing the command.
- Shell grammar beyond the command forms covered by the selftest.

## PROMISES

- **the-four-sibling-forms-are-refused.** A blind scan is refused inside a login shell's `-lc` argument, after a background
  `&`, in a parenthesized subshell, and in `$(...)` or backtick substitutions, including inside double quotes. Ordinary
  scans of unclassified files still pass. Single-quoted and escaped substitution text stays literal. The selftest also
  covers allowed commands with an inline array assignment, a descriptor redirection, and an unclosed substitution.
- **it-fails-open-on-garbage.** Malformed JSON passes without a denial or a nonzero exit.
- **a-quoted-separator-is-not-a-command-of-its-own.** A separator inside a quoted argument stays in that argument.
- **a-failing-skill-import-fails-open.** If the artifact classifier cannot be imported, the command passes.
