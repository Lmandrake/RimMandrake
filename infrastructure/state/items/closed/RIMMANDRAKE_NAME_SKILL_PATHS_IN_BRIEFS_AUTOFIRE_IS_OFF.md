# RIMMANDRAKE_NAME_SKILL_PATHS_IN_BRIEFS_AUTOFIRE_IS_OFF

## spec
With auto-firing skills mostly unregistered, helpers get skills by path: a work-to-skill map, Read-first lists in agent and role definitions, a brief rule, a launch warning. Brief: `D:\ClaudeWork\rimmandrake\conductor\briefs_20261119\skill_paths_in_briefs.md`.

## criteria
A helper assigned debug or build work is told which SKILL.md files to read before it starts.

## verify
Three selftests red on a broken tree and green after; a launch whose brief names no skill prints the WARNING.
