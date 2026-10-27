# LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE

Owner card 2026-10-26 19:06 PDT: "May agents delete our own leftovers when a check proves nothing reads them and
everything is pushed, after archiving or bundling them, and list each in your digest?" -> "Archive then delete, in
digest (Recommended)". Recorded: canon.yml `leftovers_archive_then_delete_delegated`; delegation_policy.md §2.2.
Evidence: delegation_candidates_2026-10-26.md §3 card 4 (18 of 21 cleanup answers were delete/archive).

## Build
One checker (`leftovers.py check <path>`) covering saves, folders (scratch clones, orphan mandrake mod folders),
settings and patches (aimed at retired mods): OURS (mandrake/agent-made) + nothing reads it (references from
repo, deployed mods, ModsConfig as parsed, live settings; a review save he has not judged counts as read) + every
git clone/branch involved is pushed. Then `leftovers.py retire <path>`: archive or git-bundle under
`D:\ClaudeWork\rimmandrake\archive\leftovers\<date>\` (read the base from the environment), verify the archive,
delete, log `--why "delegated: leftovers"` with the archive path, digest line. Refuses anything not ours.
## Verify
Sanity probe: a known-referenced file reads NOT-SAFE; an unpushed clone reads NOT-SAFE; a retire round-trips from
its archive.
