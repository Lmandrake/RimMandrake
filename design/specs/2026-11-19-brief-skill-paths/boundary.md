# BOUNDARY: the launch's warning for a brief that names no skill, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`skill_path_warning`, and the line `launch` adds to a launch's text).
Item: `RIMMANDRAKE_NAME_SKILL_PATHS_IN_BRIEFS_AUTOFIRE_IS_OFF`, written 2026-11-19. The owner, 2026-11-19: *"since we're
not seeming enamored of auto firing skills at the moment, it might be very important to pass relevant debug skills to the
subagents we assign to do related work, yes?"* Most project skills are not registered (`skills/README.md`, "Not
registered (read by path)"), so a helper reads a skill only when its brief names the path; `skills/BY_WORK.md` maps
kinds of work to those paths. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_detached_helper.py`.
This page covers only the warning; the rest of `detached_helper.py` has no page yet.

## ACCEPTS (the only inputs this is built for)

- **a-brief-text.** The brief as `launch` receives it (`--brief` or the text of `--brief-file`), before the footer is
  added: the footer is the launcher's own words and names no skill.

## DOES NOT SURVIVE (not promised)

- **a-skill-named-without-its-path.** A brief that says "use the rimbridge skill" with no `skills/<name>/` path is
  warned: the warning reads paths, not skill names, because a helper cannot read a name.
- **a-path-to-a-skill-that-is-gone.** A brief naming `skills/<name>/` is not warned even when that folder does not
  exist; the launch reads no disk for this.

## PROMISES (each one is owed a test of the same name)

- **a-brief-naming-no-skill-gets-one-warning.** A launch that starts, from a brief naming no path with a
  `skills/<name>/` or `skills\<name>\` segment (repo-relative, `~/dev/...`, `/mnt/d/...` or `D:\...` alike), ends its text with exactly one line
  starting `WARNING:` that names `skills/BY_WORK.md`.
- **a-brief-naming-a-skill-gets-no-warning.** A launch from a brief naming such a path prints no `WARNING:` line about
  skills. `skills/BY_WORK.md` alone is not a skill path: a brief that names only the map is still warned.
- **the-warning-refuses-nothing.** The warning never changes a launch's exit code or stops it, and a refused launch's
  text stays exactly the gate's own (no warning is added to it).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
