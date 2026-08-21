## spec
D-CHK2's four magenta cases are fixed, on the owner's ruling 2026-08-19 that the
fix goes ahead despite the 2026-08-15 v2 triage.
30 def paths across `SW_Genes.xml` and `SW_Support.xml` were missing the
`RimMandrakeSW/<DONOR>/` namespace, in exactly the four families D-CHK2 named:
`backgroundPathEndogenes`/`backgroundPathXenogenes` (16), the gand mask `<li>`s
(6), three `texPathFemale` (ChagrianF, YellowEyes_Female, fishyjowls_female) and
the gand/selkath `headPaths` `<Male>`/`<Female>` (4). 42 texture files that had
never been copied were brought across from the donors — the whole ChagrianF
headbone set, all three gand masks, the female yellow eyes, the female selkath
jowls and both gene-icon backgrounds.
🔑 FIXED IN THE OUTPUT, NOT BY A REGENERATE, AND THAT IS NOT A HAND-EDIT THAT
WILL BE LOST: `gen_races_mod.py` already carries the field fix (`texPathFemale`,
`backgroundPath*` in `TEXFIELDS`, `headPaths` in `TEXCONTAINERS`), so a future
run writes exactly these paths. The edit converges with the generator instead of
fighting it. A regenerate is separately blocked — see the DECIDE item.

## verify
done offline, and it is stronger than D-CHK2's own test: **all 329 namespaced
texture paths in the mod were resolved against the files on disk — 0 missing.**
No def field anywhere under `Defs/` now starts `Pawn/`, `OuterRim/` or `Genes/`
without the namespace. Deployed, 26 files.
⚠️ D-CHK2's written test is WRONG and was not used: it says no path may start
`UI/` without the prefix, but `UI/Icons/Xenotypes/Baseliner`,
`UI/Icons/Genes/Gene_Furskin` and a dozen more are VANILLA paths that must stay
bare. Only donor-owned paths get rewritten.

## criteria
`grep -c "Failed to find any textures at" <Player.log>` returns **0** where it
returned 3. Then look at the four cases by eye: Nikolaus (Gand), a Selkath, a
FEMALE Chagrian and a Jawa wearing the yuun mask.
🔴 Gendered fields make this look intermittent — male Chagrians always rendered.
Do not test one sex and call a species clean.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

🔵 NUMERIC HALF PASSES 2026-08-20; the isolated eyeball is still owed.

**result:** ✅ **`grep -c "Failed to find any textures at"` = 2, and NEITHER is a head.**
Both survivors are GrimTerra animal juveniles (`GRIMTERRA_TEXPATH_TYPOS_1` in
BUILD's queue). The three head failures the criterion counted are GONE.
✅ **And the count did not move when provoked.** Spawned 24 pawns across the four
named species — 6 Gand, 6 Selkath, 6 Chagrian, 6 Jawa — covering BOTH sexes
(4 female Chagrian, 5 female Selkath, and males of each). Texture-failure count
before: 2. After: 2. 🔑 That is the right instrument for this item: a magenta
head IS a failed texture lookup, and a failed lookup logs. Zero new lines after
deliberately rendering the gendered cases is the mechanism reporting clean.
⚠️ **STILL OWED, and I am not claiming it: the isolated headshot.** The 69-race
lineup screenshot shows every species rendering with no magenta, but the lineup
spawns one pawn per kind and the gendered concern needs a FEMALE Chagrian framed
on its own. My attempts to frame one put the camera on undiscovered rock — the
`position` a pawn reports and the cell the camera wants did not agree, and I ran
out of patience with it rather than out of evidence.
⇒ closeable by one framed look at a female Chagrian and a female Selkath.
