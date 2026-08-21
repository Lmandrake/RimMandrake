## spec
Carries the live half of **B45 · B46 · B47 · B48 · B49 · B50 · B51** — Hutt
Cartel, Free Droid Enclaves, Wildsteam Clan, Deepwater Compact, Geonosian
Foundry Hive, Ascendant Helix, Junkers. All seven `FactionDef`s are in
`src/Jawa/Jawa_Patches/Defs/FactionDefs/` and deployed.

## verify
done offline against the 578-mod list: **8 files, 0 errors, 1 warning** — the
warning is `iconPath UI/Deities/DeityGeneric`, which is the exact path vanilla
Anomaly's `HoraxCult` uses; the texture lives in a Unity bundle, so no loose-file
checker can see it. Every one of the 45 pawn kinds named across the eight defs
resolves in the live def dump. All four naming/art fields present and non-null on
every faction. `humanlikeFaction` was MISSING on four (Helix · Deepwater ·
Junkers · Wildsteam) and was added — R3 requires it explicitly. No
`combatPower 99999` kind in any `options`, no `minTotalPoints`, no invented
`basicMemberKind`, no `<li>`-shaped `xenotypeChances`.

## criteria
each of the seven appears on the Configure Factions page, generates settlements
at worldgen, and its raids arrive as ITS OWN pawn kinds — not vanilla ones.
🔴 The vanilla-pawn failure is the one to watch: it is what `Inherit="False"` on
`pawnGroupMakers` and on `xenotypeSet` exists to prevent, and it looks like a
working faction until you read the pawn names.
⚠️ Five design values are unresolved and filed to DECIDE as
`five-design-gaps-found-auditing-the-seven-authored-factions-3c81ea`: no
`maxCountAtGameStart` on seven of eight, the Geonosian two-outposts ruling has no
mechanism, the Hutt's `ideoDescription` disagrees with the religions spec, the
Free Droid Enclaves field a biological species against a 0%-biological dossier,
and baseliners generate in five factions. None of them stops this check.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
