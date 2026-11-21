# BOUNDARY: maturation.py's pass tag (each passed mod version gets a git tag), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py`. This page covers only the pass tag: `tag_pass`, the part of `advance`
that calls it on the move his_walk to passed, and the CLI verb `tag-pass`. Item
`RIMMANDRAKE_TAG_EACH_PASSED_MOD_VERSION_PIPELINE_DOES_IT`. The owner, 2026-11-20, about 4:10 PM PST: "Make sure we TAG
each finished version of a mod so we can easily come precisely back to it, please. This should become policy." The rule
is in `design/RimMandrake/standing_rulings.md` §Mod Design Versions. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_maturation_pass_tag.py`, each watched failing on the base `0fe80361702d` (no tag code).

## ACCEPTS (the only inputs these parts are built for)

- **root-is-a-repo-root-with-publish.** `root` is the top of a git clone whose remote `origin` takes pushes, with an
  executable `publish` at the top that commits the named paths, lands them on `origin/main` and prints
  `PUBLISHED <sha>` (the house `./publish`). A selftest fixture gives its own small `publish`.
- **version-is-semver.** The record's `version` is MAJOR.MINOR.PATCH (standing ruling: Mod Design Versions use
  SemVer). The tag name is `mod/<Mod>/v<version>`.

## DOES NOT SURVIVE (not handled)

- **a-pass-commit-rewritten-after-the-tag.** A tag is made on the published commit. A later rewrite of main (a forced
  push) leaves the tag on the old commit. Main is never force-pushed (house rule), and the ledger hook refuses a rewind.
- **a-tag-deleted-on-origin.** Nothing watches origin for a deleted tag. `tag-pass <Mod>` makes and pushes it again.

## PROMISES (each one is owed a test of the same name)

- **pass-lands-and-tags.** The move his_walk to passed, once its files are written, lands them (the pass record, the
  stage record, the journal and the mod's own `ledger/` files that changed) with the root's `publish`, then makes the
  annotated tag `mod/<Mod>/v<version>` on the PUBLISHED commit and pushes it. `advance` gives
  `res["tag"] = {"name", "commit", "pushed": True}` only after `git ls-remote origin` shows the tag on that commit.
- **untagged-pass-is-loud.** When the landing, the tag or the push fails, the move stays made: the pass record is
  written once and never replaced, and his word stands. So the pass step RETRIES, it does not refuse:
  `res["untagged"] = {"name", "step", "why", "retry"}` names the tag, the failed step (`land`, `tag`, `push` or
  `verify`), the cause and the command `maturation.py tag-pass <Mod>`. The CLI prints `PASSED BUT NOT TAGGED` and
  exits 5, never 0. `res["tag"]` is absent.
- **tag-taken-refuses-before-write.** When the tag name already exists in the clone (on any commit), the move to
  passed is refused before any file is written (`res["tag_taken"]`): a name that is taken cannot mark this pass.
- **retry-tags-the-recorded-commit.** `tag_pass(root, mod, version)` with no paths to land finds the commit on
  `origin/main` that added `version/passes/<version>.json`, tags it and pushes the tag. A second run makes no new tag
  and pushes nothing new (`res["already"]`). A pass record that no commit on `origin/main` added is `untagged`, step
  `land`.
- **no-commit-outside-its-own-root.** When `root` is not itself the top of a git clone (a selftest's plain folder, or
  a folder inside some other clone), `tag_pass` commits, tags and pushes nothing: it is `untagged`, step `land`.

Later lists beside this page: `polish.md` (none yet).
