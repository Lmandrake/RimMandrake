# land.sh - publish by plumbing when `pull --rebase` is refused by peers' unstaged edits

Installed copy: `/home/mandrake/.seat-tmp/land.sh` (this file is the tracked copy).

- `land.sh <sha> <path>...` replays that ONE commit onto origin/main. Every path the commit changes must be
  (or sit under) a listed path. Refuses: no sha, no paths, merge/root commits, a sha already an ancestor
  of origin/main or patch-equivalent to one (git cherry), conflicts.
- `land.sh -m "<msg>" <path>...` builds the commit itself from the working-tree content of the paths in a
  TEMP index seeded from origin/main - the shared HEAD and index are never read.
- Never stash/reset/checkout; never touches peers' unstaged edits. Push is fast-forward only.
- Prints `PUBLISHED <sha>`; pass it to `rimflow close --sha`. Env: LAND_REPO, LAND_REMOTE, LAND_BRANCH.
- Local HEAD still carries the unpublished original; it is not rebased. Tested against a throwaway bare repo.
