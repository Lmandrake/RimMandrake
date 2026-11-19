# Polish beside boundary.md (no promise broken; not part of passing)

- `SKILL_PATH` has no left boundary: `myskills/x/` or a URL's `.../skills/x/` counts as a skill path (two looks, 2026-11-19).
- A brief that names a skill path only to forbid it ("do not read skills/x/") is not warned: the check reads paths, not
  intent (two looks, 2026-11-19).
