In zsh, `git show $c:path/file` fails with "bad substitution" (or silently mangles): `$c:s...` / `:h` / `:t` are zsh history modifiers on the variable. Brace it: `git show "${c}:path"`. A loop that pipes this into sha256sum prints the empty-input hash e3b0c442... for every file, which reads like real (identical) results. Seen 2026-10-24 checking clean-mark hashes.
home: git-efficiency
