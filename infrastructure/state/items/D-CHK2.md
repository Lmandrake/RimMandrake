## spec
Filed by CHECK 2026-08-15, live on the 70-species map. BUILD's fix, in
`gen_races_mod.py` — CHECK does not author src/.

SYMPTOM: a magenta box with a red X where the head should be. Confirmed by
eye on Nikolaus (`RimMandrakeGand`) and Yoko (`RimMandrakeChagrian`); bodies
render fine, neighbouring species render fine, both pawns alive and undowned.

🔴 THE LOG NAMES IT, but NOT under the string you would grep for. The class is
**`Failed to find any textures at <path> while constructing Multi(...)`** — not
"Could not load UnityEngine.Texture2D", which returns ZERO hits. Three entries:
  Failed to find any textures at OuterRim/Genes/Headbone/ChagrianF
  Failed to find any textures at Pawn/HeadType/gand/gand
  Failed to find any textures at Pawn/HeadAttachments/gand/mask_yuun
Every one is missing the `RimMandrakeSW/...` prefix.

ROOT CAUSE: the generator re-namespaces the COMMON path fields (`texPath`,
`graphicPath`, `texPaths`, most `iconPath`) and misses a family of others.
19 defs carry 27 un-namespaced paths, all missing at runtime. The fields it
misses:
  · `texPathFemale`                      (gendered variant - Chagrian, fishmouth, GS_Eyes_Yellow)
  · `<Male>` / `<Female>` inside a `BigAndSmall.PawnExtension` `headPaths`  (gand, selkath)
  · `backgroundPathEndogenes` / `backgroundPathXenogenes`
  · a handful of plain `iconPath`
plus `Pawn/HeadAttachments/gand/mask_yuun` in `Defs/Misc/SW_Support.xml`.

🔑 AND THE SAME MISS COSTS THE ART. The texture copier is driven from that
same path list, so a field it does not rewrite is a texture it never copies:
  gand, selkath heads      path wrong, ART PRESENT (6 files) -> rewrite path only
  ChagrianF                path wrong, ART NOT COPIED        -> rewrite AND copy
  mask_yuun                path wrong, ART NOT COPIED        -> rewrite AND copy
  YellowEyes_Female        path wrong, ART NOT COPIED        -> rewrite AND copy
  OuterRim/GeneIcons/*BG   path wrong, ART NOT COPIED        -> rewrite AND copy
The donors still hold all of it — e.g. `2980427615/Common_Old/Textures/OuterRim/
Genes/Headbone/ChagrianF_east.png`, `2915192253/Textures/Pawn/HeadAttachments/
gand/mask_yuun_east.png` — so nothing is lost, only unmigrated.

⚠️ Gendered fields make this look intermittent: male Chagrians render (their
`texPaths` WERE rewritten), female Chagrians go magenta. Do not test one sex
and call a species clean.

## verify
grep the log for `Failed to find any textures at` after the next load; zero
lines is the pass. Offline: no def field should hold a path starting
`Pawn/`, `OuterRim/`, `UI/` or `Genes/` without the `RimMandrakeSW/` prefix.

## criteria
DECIDE routes; the fix is BUILD's in gen_races_mod.py, then a re-run and redeploy.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
reach the frozen world. Parked, not lost.
