# STARWARSRACES_UNDECLARED_GENE_DEPS_1 — five real dependencies are not in About.xml

## Bisection — live, on the bridge, 2026-09-03

Owner approved a live restart bisection. Bridge taken, backed up the live
ModsConfig.xml, built a trimmed test list programmatically (About.xml's 4
*declared* deps + candidates, dependency-closed and load-ordered via
`modset_builder.py`'s own `close_over`/`order`), and restarted RimWorld twice
via the Steam-launch path (`launch-rimworld-via-steam-not-bare-exe`), polling
`Player.log` for `Bridge token:` as the ready signal (~20s each).

**Restart 1** — declared deps + `RedMattis.BetterPrerequisites` +
`RedMattis.BigSmall.Core` (the two the log named): `BigAndSmall.PawnExtension`
and `BetterPrerequisites.GeneExtension` type-not-found errors both **gone**,
and so were the 3 originally-reported cross-refs
(`RSW_Head_hutt`/`RSW_Head_selkath`/`RSW_statgene_predator`) — those are
RimStarWars's OWN gene defs, discarded whole by the missing-type bug, not
content owned by another mod. `RedMattis.BigSmall` (races) and
`RedMattis.Optional` were NOT in this list and nothing missed them.

**Restart 2** — added `LazyFridayStudio.GenesExpandedEyes`: the six
`Eyes_*_Reptile` cross-reference failures (referenced directly by
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`,
confirmed by grep) went to **zero**. Still no `RedMattis.BigSmall` or
`RedMattis.Optional` in the list, and grepping every RSW def file for a
gene/thing name owned by either turned up nothing — RSW never references
their content directly.

**Minimal sufficient set, measured: `RedMattis.BetterPrerequisites`,
`RedMattis.BigSmall.Core`, `LazyFridayStudio.GenesExpandedEyes`.**
`RedMattis.BigSmall` and `RedMattis.Optional` were carry-alongs from the
original live fix, not required — corroborated independently: `About.xml`'s
own `<loadAfter>` already listed exactly these same three RedMattis/LFS
packageIds and neither of the other two, from whoever wired the ordering
during the original live fix.

(One unrelated finding, out of scope: `RSW_statgene_PsyHarmonize` stayed
unresolved throughout — RSW's own gene, not one of the 5 candidates. Left
alone; not filed separately since nobody is blocked on it right now.)

## Fix

Added the 3 measured dependencies to
`src/RimStarWars/StarWarsRaces/About/About.xml`'s `<modDependencies>`
(workshop IDs read from the installed mods themselves, not guessed):
`RedMattis.BetterPrerequisites` (2925432336), `RedMattis.BigSmall.Core`
(2920751126), `LazyFridayStudio.GenesExpandedEyes` (2922457045). Deployed with
`deploy_custom_mods.py --mod StarWarsRaces --apply` (writing the repo file is
not deploying it) and re-verified: `close_over(["mandrake.rsw.starwarsraces"])`
now pulls in all three with zero missing.

`ModsConfig.MINIMAL.xml` does not include StarWarsRaces (checked) so nothing
there needed a change.

## Cleanup

Restored the live `ModsConfig.xml` from the pre-bisection backup (589 active
mods) before closing RimWorld and releasing the bridge — confirmed on disk
after the process exited, since RimWorld does not rewrite this file on exit.

## criteria

`About.xml` declares every mod StarWarsRaces genuinely needs, tested one at a
time. Met — 3 of the original 5 candidates, each individually confirmed live,
not all 5 blindly.
