# History of the canon-references skill

This file holds evidence. The lessons are in `../SKILL.md`. Do not read a count here as a count of today: run
`python3 src/RimMandrake/Utils/canon_census.py`, or read `design/RimStarWars/canon_references/INDEX.md`. The census
counts a ruling with no `**RULED**` mark as non-conforming. So its ruled count is lower than the count of `INDEX.md`.
The census also counts the blank ruling of `zeer` as non-conforming.

## Counts of the library, by date

| date | entries | `none known` under `## Engine limits` | `## ruling` filled / empty | entries that cite a missing `src/…` or `design/…` path |
|---|---|---|---|---|
| 2026-09-16 | 137 | **108 of 137** | **25 carry a ruling, 112 are empty.** The old text spoke of 112 complete briefs. | **0 of 137 entries cite a missing `src/…` or `design/…` path.** |
| 2026-11-23 | 266 | 165 of 266 | 68 / 198 | 1 of 266 (`wyyyschokk`, corrected the same day) |

- The skill's `description` still says 137. A `description` changes only with the trigger evals of `skill-creator`.
- 2026-11-23: each entry has 4 to 9 `## Must show` lines. The rewrite of 2026-10-09 made the lists longer.
- 2026-11-23: more than half of the 68 filled rulings name an image file. Some of those files are gone. `cancell` and
  `dragonsnake` name a reference of record that a later ruling deleted.
- 2026-11-23: a naive check over the 266 entries reported 133 image names that are not in the entry directory. The
  check read only backticked names that start `wookieepedia_`, `canon_`, `donor_` or `owner_`.

## Dates of the lessons

- The counts in the skill body were measured on 2026-09-16, across all 137 entries.
- The search-API lesson (`searchinfo`, `totalhits`): 2026-09-22.
- The old User-Agent line: fandom.com 403s python-urllib's default User-Agent.
- The `curl` and Fetcher lesson, and the two page-title traps: 2026-09-15.
- The `mirialan` citation was fixed at `252f8ff2e` (2026-09-16). The old Source-URLs line said "already on disk under
  that name… re-verified this pass".
- The Q11a quote stood in the skill cut short: "The top mod without star wars will look precisely the same as the star
  wars enhanced one." The skill now holds the owner's whole clause.

## Text that went stale and was corrected on 2026-11-23

- The skill sent the reader to `CLAUDE.md > What is where` and to `CLAUDE.md` for the library-wide rulings. Those
  rulings are in `design/RimMandrake/standing_rulings.md` §What is where.
- The skill quoted the `useSkinShader: false` annotation as *"needs in-game confirmation of what actually renders."*
  `AGENT_BRIEF.md` words it differently now.
- The skill said that `mon_calamari` points at a bad image held in `rakata/`. The realism sweep of 2026-10-08 deleted
  that image.
- The skill said to search `src/RimStarWars/` for a defName. `RM_Ollathrix` (the wyyyschokk) is under
  `src/RimMandrake/`.
- The skill put the soft cap, the hard cap and the aggression ramp in `RM_CompVerminBreeder`. The caps are in
  `RM_VerminPressureExtension`, and `RM_MapComponent_VerminPopulation` computes the ramp.
- The skill called `RM_MapComponent_StrandingPools.IsReconnected()` the flood-fill. That method now calls
  `RM_PoolKernel.Reconnected()`, which holds the flood-fill.
- The skill's §5 table said that only the owner may depart from canon or write a `## ruling`. Since 2026-11-19 the Conductor may
  do each act outside the owner's five acts (`design/RimMandrake/delegation_policy.md` §2).
